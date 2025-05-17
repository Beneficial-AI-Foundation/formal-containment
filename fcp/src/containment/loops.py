from pathlib import Path
from containment.artifacts import write_artifact
from containment.lake import Checker
from containment.oracles import proof_oracle
from containment.structures import (
    HoareTriple,
    LakeResponse,
    VerificationSuccess,
    VerificationFailure,
    VerificationResult,
)
from containment.tools import temp_lakeproj_init

UP = ".."
IMP_DIR = Path.cwd() / UP / "imp"
MAX_CONVERSATION_LENGTH = 16


class Loop:
    """
    Loop class for running a tool and feeding the result back into the oracle.

    Prover of hoare triples.
    """

    def __init__(
        self,
        max_iterations: int,
        max_conversation_length: int = MAX_CONVERSATION_LENGTH,
    ):
        self.max_iterations = max_iterations
        self.max_conversation_length = max_conversation_length
        self.lake_dir = IMP_DIR
        self.tmpdir = temp_lakeproj_init()
        self.conversation = []
        self.proof = None

    def _iter(
        self, triple: HoareTriple, stderr: str | None, positive: bool
    ) -> LakeResponse:
        """Iteration of the loop."""

        self.proof, self.conversation = proof_oracle(self.conversation, triple, stderr)
        checker = Checker(cwd=self.tmpdir)
        return checker.run(triple, self.proof, positive)

    def run(self, triple: HoareTriple, *, positive: bool) -> VerificationResult | None:
        """Continue the loop until lake succeeds or max iterations are reached."""
        lake_response = self._iter(triple, None, positive)
        if lake_response.exit_code == 0 and self.proof is not None:
            return VerificationSuccess(triple=triple, proof=self.proof)
        for iteration in range(self.max_iterations):
            if iteration % 5 == 0:
                print(f"iteration num {iteration}/{self.max_iterations}")
            self.conversation = self.conversation[-self.max_conversation_length :]
            lake_response = self._iter(triple, lake_response.stderr, positive)
            if lake_response.exit_code == 0:
                break
        write_artifact(self.tmpdir, triple)
        if (
            lake_response.exit_code != 0
            and lake_response.stderr
            and self.proof is not None
        ):
            return VerificationFailure(
                triple=triple, proof=self.proof, error_message=lake_response.stderr
            )
        if self.proof is not None:
            return VerificationSuccess(triple=triple, proof=self.proof)
        return None


def proof_loop(max_iterations: int = 25) -> Loop:
    """
    Create a proof loop with the given max iterations.
    """
    return Loop(max_iterations)
