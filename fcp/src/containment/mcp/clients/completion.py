"""Completions as an MCP client. This is the AI that is getting locked in the box."""

from pathlib import Path
from containment.mcp.clients.basic import MCPClient
from containment.artifacts import write_artifact
from containment.structures import (
    HoareTriple,
    LakeResponse,
    Specification,
    VerificationSuccess,
    VerificationFailure,
    VerificationResult,
)
from containment.prompts import load_template, oracle_system_prompt
from containment.oracles import parse_program_completion

MAX_CONVERSATION_LENGTH = 16


class ImpExpert(MCPClient):
    async def __init__(self, spec: Specification) -> None:
        await super().__init__()
        self.spec = spec
        self.system_prompt = oracle_system_prompt("imp")
        self.complete = self.mk_complete(self.system_prompt)

    async def complete_triple(self) -> HoareTriple:
        prompt_arguments = {"spec": self.spec.jsons}
        user_prompt = await self.session.get_prompt(
            "imp_user_prompt", arguments=prompt_arguments
        )
        completion = self.complete([{"role": "user", "content": user_prompt}])
        program = parse_program_completion(completion, "imp")
        if program is None:
            raise ValueError("No program found. XML parse error probably")
        return HoareTriple(specification=self.spec, command=program)


class ProofExpert(MCPClient):
    """Expert at writing hoare proofs over imp."""

    async def __init__(
        self, triple: HoareTriple, positive: bool, *, max_iterations: int = 25
    ) -> None:
        await super().__init__()
        self.triple = triple
        self.positive = positive
        self.max_iterations = max_iterations
        self.max_conversation_length = MAX_CONVERSATION_LENGTH
        self.system_prompt = oracle_system_prompt("proof")
        self.complete = self.mk_complete(self.system_prompt)
        self.proof = None

    def render_code(self, proof: str | None) -> str:
        """
        Write the proof to a file in the tmpdir.
        """
        polarity = "Positive" if self.positive else "Negative"
        basic = load_template(
            f"{polarity}.lean.template",
            proof=proof,
            **self.triple.model_dump(),
        )
        return basic

    async def _iter(self, stderr: str | None) -> tuple[Path, LakeResponse]:
        prompt_arguments = {"triple": self.triple, "stderr": stderr}
        user_prompt = await self.session.get_prompt(
            "hoare_proof_user_prompt", arguments=prompt_arguments
        )
        curr_conversation = [{"role": "user", "content": user_prompt}]
        self.conversation = self.conversation + curr_conversation
        completion = self.complete(self.conversation)
        proof = parse_program_completion(completion, "proof")
        self.proof = proof
        tool_arguments = {"lean_code": self.render_code(proof)}
        (cwd, lake_result), is_error = await self.session.call_tool(
            "typecheck", arguments=tool_arguments
        )
        return Path(cwd), lake_result.content[0]

    async def run(self) -> VerificationResult | None:
        cwd, lake_response = await self._iter(None)
        if lake_response == 0 and self.proof is not None:
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
