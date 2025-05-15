from pathlib import Path
from containment.artifacts import write_artifact
from containment.lake import Checker
from containment.oracles import Oracle, proof_oracle
from containment.prompts import get_oracle_system_prompt
from containment.structures import HoareTriple, ToolResponse
from containment.tools import temp_lakeproj_init

UP = ".."
LAKE_DIR = Path.cwd() / UP / "imp"
PROOF_SYSTEM_PROMPT = get_oracle_system_prompt("proof")
MAX_CONVERSATION_LENGTH = 16


class Loop:
    """
    Loop class for running a tool and feeding the result back into the oracle.

    Prover of hoare triples.
    """

    def __init__(
        self,
        system_prompt: str,
        max_iterations: int,
        max_conversation_length: int = MAX_CONVERSATION_LENGTH,
    ):
        self.oracle = Oracle(system_prompt)
        self.max_iterations = max_iterations
        self.max_conversation_length = max_conversation_length
        self.lake_dir = LAKE_DIR
        self.tmpdir = temp_lakeproj_init()
        self.conversation = []

    def _iter(self, triple: HoareTriple, stderr: str | None) -> ToolResponse:
        """Iteration of the loop."""

        proof, self.conversation = proof_oracle(self.conversation, triple, stderr)
        checker = Checker(self.tmpdir)
        return checker.run(triple, proof)

    def _loop_init(self, triple: HoareTriple) -> ToolResponse:
        """0th iteration of the loop."""
        return self._iter(triple, None)

    def run(self, triple: HoareTriple) -> ToolResponse:
        """Continue the loop until lake succeeds or max iterations are reached."""
        lake_response = self._loop_init(triple)
        if lake_response.exit_code == 0:
            return lake_response
        for iteration in range(self.max_iterations):
            if iteration % 5 == 0:
                print(f"iteration num {iteration}/{self.max_iterations}")
            self.conversation = self.conversation[-self.max_conversation_length :]
            lake_response = self._iter(triple, lake_response.stderr)
            if lake_response.exit_code == 0:
                break
        write_artifact(self.tmpdir, triple)
        return lake_response


def proof_loop(max_iterations: int = 25) -> Loop:
    """
    Create a proof loop with the given max iterations.
    """
    loop = Loop(PROOF_SYSTEM_PROMPT, max_iterations)
    return loop
