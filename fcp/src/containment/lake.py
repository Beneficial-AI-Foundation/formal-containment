from pathlib import Path
from containment.structures import HoareTriple, ToolResponse
from containment.prompts import load_template
from containment.tools import lake_exe_check


class Checker:
    def __init__(self, cwd: Path):
        self.cwd = cwd
        self.basic_path = cwd / "Artifacts" / "Basic.lean"

    def write_proof(
        self, triple: HoareTriple, proof: str | None, positive: bool
    ) -> None:
        """
        Write the proof to a file in the tmpdir.
        """
        polarity = "Positive" if positive else "Negative"
        basic = load_template(
            f"{polarity}.lean.template",
            proof=proof,
            **triple.dictionary,
        )
        with open(self.basic_path, "w") as basic_dot_lean:
            basic_dot_lean.write(basic)

    def run(
        self, triple: HoareTriple, proof: str | None = None, positive: bool = True
    ) -> ToolResponse:
        """
        Run the lake tool and return the result. (None option for proof is just for testing).

        Args:
            triple: The Hoare triple to prove
            proof: The proof to write to the file

        Returns:
            ToolResponse: The result of the lake tool
        """
        self.write_proof(triple, proof, positive)
        result = lake_exe_check(self.cwd)
        return result
