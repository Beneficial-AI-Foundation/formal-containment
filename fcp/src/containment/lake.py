from dataclasses import asdict
from pathlib import Path
from containment.structures import HoareTriple, ToolResponse
from containment.prompts import load_template
from containment.tools import lake_exe_check


class Checker:
    def __init__(self, cwd: Path):
        self.cwd = cwd
        self.basic_path = cwd / "Artifacts" / "Basic.lean"

    def write_proof(self, triple: HoareTriple, proof: str | None) -> None:
        """
        Write the proof to a file in the tmpdir.
        """
        basic = load_template(
            "Positive.lean.template",
            proof=proof,
            **asdict(triple),
        )
        with open(self.basic_path, "w") as thefile:
            thefile.write(basic)

    def run(self, triple: HoareTriple, proof: str | None = None) -> ToolResponse:
        """
        Run the lake tool and return the result. (None option for proof is just for testing).

        Args:
            triple: The Hoare triple to prove
            proof: The proof to write to the file

        Returns:
            ToolResponse: The result of the lake tool
        """
        self.write_proof(triple, proof)
        result = lake_exe_check(self.cwd)
        return result
