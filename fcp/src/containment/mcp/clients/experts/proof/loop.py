from pathlib import Path
from containment.fsio.tools import temp_lakeproj_init
from containment.mcp.clients.basic import MCPClient
from containment.mcp.clients.experts.proof import SORRY_CANARY
from containment.fsio.artifacts import write_artifact
from containment.structures import (
    HoareTriple,
    LakeResponse,
    Polarity,
    ExpertMetadata,
    VerificationSuccess,
    VerificationFailure,
    VerificationResult,
)
from containment.fsio.prompts import load_txt, expert_system_prompt
from containment.parsing.regex import parse_program_completion
from containment.fsio.logs import logs

MAX_CONVERSATION_LENGTH = 32


def filter_conversation_length(
    conversation: list[dict], max_conversation_length: int = MAX_CONVERSATION_LENGTH
) -> list[dict]:
    """
    Filter the conversation to the last MAX_CONVERSATION_LENGTH messages, maintaining the 0th message.
    """
    if not conversation:
        return []
    system_message = conversation[0]
    tail = conversation[1:]
    if not tail:
        return [system_message]
    if len(tail) >= max_conversation_length:
        tail = tail[-max_conversation_length:]
    return [system_message] + tail


class ProofExpert(MCPClient):
    """Expert at writing hoare proofs over imp, via a minimal scaffold."""

    def __init__(
        self,
        model: str,
        triple: HoareTriple,
        polarity: Polarity,
        *,
        max_iterations: int = 25,
    ) -> None:
        super().__init__()
        self.model = model
        self.triple = triple
        self.polarity = polarity
        self.max_iterations = max_iterations
        self.max_conversation_length = MAX_CONVERSATION_LENGTH
        self.system_prompt = expert_system_prompt("loop/proof")
        self.complete = self._mk_complete(model, self.system_prompt)
        self.proof = None
        self.verification_result = None
        self.code_dt = []
        self.tokens_spent = 0

    @classmethod
    async def connect_and_run(
        cls,
        model: str,
        triple: HoareTriple,
        polarity: Polarity,
        *,
        max_iterations: int = 25,
    ) -> "ProofExpert":
        """
        Async instantiation: connect to the MCP server.
        """
        mcp_client = cls(model, triple, polarity, max_iterations=max_iterations)
        mcp_client.verification_result = await mcp_client._connect_to_server_and_run()
        return mcp_client

    def _render_code(self, proof: str | None) -> str:
        """
        Write the proof to a file in the tmpdir.
        """
        basic = load_txt(
            f"loop/{self.polarity.value}.lean.template",
            proof=proof,
            **self.triple.model_dump(),
        )
        self.code_dt.append(basic)
        return basic

    async def _iter(self, stderr: str, cwd: Path) -> LakeResponse:
        prompt_arguments = {
            "precondition": self.triple.specification.precondition,
            "postcondition": self.triple.specification.postcondition,
            "command": self.triple.command,
            "metavariables": self.triple.specification.metavariables,
            "stderr": stderr,
            "polarity": self.polarity.value,
        }
        user_prompt = await self.session.get_prompt(
            "hoare_proof_user_prompt", arguments=prompt_arguments
        )
        curr_conversation = [
            {
                "role": "user",
                "content": [
                    message.content.model_dump() for message in user_prompt.messages
                ],
            }
        ]
        self.conversation = self.conversation + curr_conversation
        completion = self.complete(self.conversation)
        proof_content = completion["choices"][0].message.content
        self.tokens_spent += completion["usage"]["total_tokens"]
        self.conversation.append({"role": "assistant", "content": proof_content})
        self.proof = parse_program_completion(proof_content, "proof")
        tool_arguments = {"lean_code": self._render_code(self.proof), "cwd": str(cwd)}
        tool_result = await self.session.call_tool(
            "typecheck", arguments=tool_arguments
        )
        lake_response_str = tool_result.content[0].text  # type: ignore
        return LakeResponse.from_jsons_clean(lake_response_str)

    async def _prove_loop(self) -> VerificationResult:
        forall_str = (
            f"FORALL {self.triple.specification.metavariables},"
            if self.triple.specification.metavariables
            else ""
        )
        triple_str = f"{forall_str} {self.triple.hidden_code}"
        msg_prefix = f"\t{self.model}:{self.triple.specification.name if self.triple.specification.name is not None else self.triple.specification}-"
        cwd = temp_lakeproj_init()
        lake_response = await self._iter("", cwd)
        metadata = ExpertMetadata(model=self.model, polarity=self.polarity)
        metadata.set_tokens_spent(self.tokens_spent)
        if lake_response.exit_code == 0 and self.proof is not None:
            if SORRY_CANARY not in lake_response.stderr:
                artifact_dir = write_artifact(cwd, self.triple)
                metadata.successful()
                return VerificationSuccess(
                    triple=self.triple,
                    proof=self.proof,
                    audit_trail=artifact_dir / f"{hash(self.triple)}.lean",
                    metadata=metadata,
                )
            msg = f"{msg_prefix}: Proof for {self.polarity.value} hoare triple {triple_str} has a sorry."
            logs.info(msg)
        failures = [
            VerificationFailure(
                triple=self.triple,
                proof=self.proof if self.proof is not None else "<UNREACHABLE>",
                error_message=lake_response.stderr,
                audit_trail=cwd,
                metadata=metadata,
            )
        ]
        for iteration in range(1, self.max_iterations + 1):
            metadata.incr()
            if not iteration % 3:
                msg = f"{msg_prefix}: Attempt to prove {self.polarity.value} hoare triple {triple_str}: iteration num {iteration}/{self.max_iterations}"
                logs.info(msg)
            self.conversation = filter_conversation_length(self.conversation)
            lake_response = await self._iter(lake_response.stderr, cwd=cwd)
            if (
                lake_response.exit_code == 0
                and SORRY_CANARY not in lake_response.stderr
            ):
                msg = f"{msg_prefix}: Proof loop converged after {iteration} iterations! for triple {triple_str}"
                logs.info(msg)
                break
            metadata.set_tokens_spent(self.tokens_spent)
            failures.append(
                VerificationFailure(
                    triple=self.triple,
                    proof=self.proof if self.proof is not None else "<UNREACHABLE>",
                    error_message=lake_response.stderr,
                    audit_trail=cwd,
                    metadata=metadata,
                )
            )

        artifact_dir = write_artifact(cwd, self.triple)
        if lake_response.exit_code != 0 and self.proof is not None:
            return failures
        if self.proof is None:
            failures.append(
                VerificationFailure(
                    triple=self.triple,
                    proof="sorry <UNREACHABLE?>",
                    error_message=lake_response.stderr,
                    audit_trail=artifact_dir / f"{hash(self.triple)}.lean",
                    metadata=metadata,
                )
            )
            return failures
        metadata.successful()
        return VerificationSuccess(
            triple=self.triple,
            proof=self.proof,
            audit_trail=artifact_dir / f"{hash(self.triple)}.lean",
            metadata=metadata,
        )

    async def run(self) -> VerificationResult:
        """
        Run the functionality of client.
        """
        return await self._prove_loop()
