from pathlib import Path
from containment.mcp.clients.basic import MCPClient
from containment.artifacts import write_artifact
from containment.structures import (
    HoareTriple,
    LakeResponse,
    VerificationSuccess,
    VerificationFailure,
    VerificationResult,
)
from containment.prompts import load_txt, oracle_system_prompt
from containment.oracles import parse_program_completion

MAX_CONVERSATION_LENGTH = 12


class ProofExpert(MCPClient):
    """Expert at writing hoare proofs over imp."""

    def __init__(
        self, triple: HoareTriple, positive: bool, *, max_iterations: int = 25
    ) -> None:
        super().__init__()
        self.triple = triple
        self.positive = positive
        self.max_iterations = max_iterations
        self.max_conversation_length = MAX_CONVERSATION_LENGTH
        self.system_prompt = oracle_system_prompt("proof")
        self.complete = self._mk_complete(self.system_prompt)
        self.proof = None
        self.verification_result = None
        self.code_dt = []

    @classmethod
    async def connect_and_run(
        cls, triple: HoareTriple, positive: bool, *, max_iterations: int = 25
    ) -> "ProofExpert":
        """
        Async instantiation: connect to the MCP server.
        """
        mcp_client = cls(triple, positive, max_iterations=max_iterations)
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
        # prompt_arguments = {"triple": self.triple, "stderr": stderr}
        prompt_arguments = {
            "precondition": self.triple.specification.precondition,
            "postcondition": self.triple.specification.postcondition,
            "command": self.triple.command,
            "stderr": stderr,
        }
        user_prompt = await self.session.get_prompt(
            "hoare_proof_user_prompt", arguments=prompt_arguments
        )
        curr_conversation = [
            {
                "role": "user",
                "content": [message.content for message in user_prompt.messages],
            }
        ]
        self.conversation = self.conversation + curr_conversation
        completion = self.complete(self.conversation)
        proof = parse_program_completion(completion, "proof")
        self.proof = proof
        tool_arguments = {"lean_code": self._render_code(proof)}
        tool_result = await self.session.call_tool(
            "typecheck", arguments=tool_arguments
        )
        cwd = tool_result.content[0].text.strip('"')  # type: ignore
        lake_response = tool_result.content[1].text  # type: ignore
        return Path(cwd), LakeResponse.from_jsons(lake_response)

    async def _prove_loop(self) -> VerificationResult | None:
        cwd, lake_response = await self._iter("")
        if lake_response.exit_code == 0 and self.proof is not None:
            return VerificationSuccess(triple=self.triple, proof=self.proof)
        for iteration in range(self.max_iterations):
            if not iteration % 5:
                print(f"iteration num {iteration}/{self.max_iterations}")
            self.conversation = self.conversation[-self.max_conversation_length :]
            cwd, lake_response = await self._iter(lake_response.stderr)
            if lake_response.exit_code == 0:
                break
        write_artifact(cwd, self.triple)
        if (
            lake_response.exit_code != 0
            and lake_response.stderr
            and self.proof is not None
        ):
            return VerificationFailure(
                triple=self.triple, proof=self.proof, error_message=lake_response.stderr
            )
        if self.proof is not None:
            return VerificationSuccess(triple=self.triple, proof=self.proof)
        return None

    async def run(self) -> VerificationResult | None:
        """
        Run the functionality of client.
        """
        return await self._prove_loop()
