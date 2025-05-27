from pathlib import Path
from containment.mcp.clients.basic import MCPClient
from containment.fsio.artifacts import write_artifact
from containment.structures import (
    HoareTriple,
    LakeResponse,
    ExpertMetadata,
    VerificationSuccess,
    VerificationFailure,
    VerificationResult,
)
from containment.fsio.prompts import load_txt, oracle_system_prompt
from containment.netio.oracles import parse_program_completion
from containment.fsio.logs import logs

MAX_CONVERSATION_LENGTH = 20


class ProofExpert(MCPClient):
    """Expert at writing hoare proofs over imp."""

    def __init__(
        self,
        model: str,
        triple: HoareTriple,
        positive: bool,
        *,
        max_iterations: int = 25,
    ) -> None:
        super().__init__()
        self.model = model
        self.triple = triple
        self.positive = positive
        self.max_iterations = max_iterations
        self.max_conversation_length = MAX_CONVERSATION_LENGTH
        self.system_prompt = oracle_system_prompt("proof")
        self.complete = self._mk_complete(self.model, self.system_prompt)
        self.proof = None
        self.verification_result = None
        self.code_dt = []

    @classmethod
    async def connect_and_run(
        cls,
        model: str,
        triple: HoareTriple,
        positive: bool,
        *,
        max_iterations: int = 25,
    ) -> "ProofExpert":
        """
        Async instantiation: connect to the MCP server.
        """
        mcp_client = cls(model, triple, positive, max_iterations=max_iterations)
        mcp_client.verification_result = await mcp_client._connect_to_server_and_run()
        return mcp_client

    def _render_code(self, proof: str | None) -> str:
        """
        Write the proof to a file in the tmpdir.
        """
        polarity = "Positive" if self.positive else "Negative"
        basic = load_txt(
            f"{polarity}.lean.template",
            proof=proof,
            **self.triple.model_dump(),
        )
        self.code_dt.append(basic)
        return basic

    async def _iter(self, stderr: str) -> tuple[Path, LakeResponse]:
        prompt_arguments = {
            "precondition": self.triple.specification.precondition,
            "postcondition": self.triple.specification.postcondition,
            "command": self.triple.command,
            "metavariables": self.triple.specification.metavariables,
            "stderr": stderr,
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
        self.proof = parse_program_completion(
            completion["choices"][0].message.content, "proof"
        )
        tool_arguments = {"lean_code": self._render_code(self.proof)}
        tool_result = await self.session.call_tool(
            "typecheck", arguments=tool_arguments
        )
        cwd = tool_result.content[0].text.strip('"')  # type: ignore
        lake_response = tool_result.content[1].text  # type: ignore
        return Path(cwd), LakeResponse.from_jsons(lake_response)

    async def _prove_loop(self) -> VerificationResult:
        forall_str = (
            f"FORALL {self.triple.specification.metavariables},"
            if self.triple.specification.metavariables
            else ""
        )
        triple_str = f"{forall_str} {self.triple.hidden_code}"
        msg_prefix = f"\t{self.model}:{self.triple.specification.name if self.triple.specification.name is not None else self.triple.specification}-"
        cwd, lake_response = await self._iter("")
        metadata = ExpertMetadata(model=self.model)
        if lake_response.exit_code == 0 and self.proof is not None:
            artifact_dir = write_artifact(cwd, self.triple)
            return VerificationSuccess(
                triple=self.triple,
                proof=self.proof,
                audit_trail=artifact_dir,
                metadata=metadata,
            )
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
                msg = f"{msg_prefix}: Attempt to prove hoare triple {triple_str}: iteration num {iteration}/{self.max_iterations}"
                logs.info(msg)
            self.conversation = self.conversation[-self.max_conversation_length :]
            cwd, lake_response = await self._iter(lake_response.stderr)
            if lake_response.exit_code == 0:
                msg = f"Proof loop converged after {iteration} iterations! for triple {triple_str}"
                logs.info(msg)
                break
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
        if (
            lake_response.exit_code != 0
            and lake_response.stderr
            and self.proof is not None
        ):
            return failures
        if self.proof is None:
            failures.append(
                VerificationFailure(
                    triple=self.triple,
                    proof="sorry <UNREACHABLE?>",
                    error_message="For some reason, the proof field is still None",
                    audit_trail=artifact_dir,
                    metadata=metadata,
                )
            )
            return failures
        return VerificationSuccess(
            triple=self.triple,
            proof=self.proof,
            audit_trail=artifact_dir,
            metadata=metadata,
        )

    async def run(self) -> VerificationResult:
        """
        Run the functionality of client.
        """
        return await self._prove_loop()
