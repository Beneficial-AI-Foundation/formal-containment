from containment.structures import HoareTriple, LakeResponse, CheckerBase
from containment.io.prompts import load_txt
from containment.io.tools import lake_exe_check


class Checker(CheckerBase):
    """Running lake tool in given tmpdir."""

    def write_code(self, lean_code: str) -> None:
        """Write the lean code to a file in the tempdir."""
        with open(self.basic_path, "w") as basic_dot_lean:
            basic_dot_lean.write(lean_code)
        return None

    def write_proof(
        self, triple: HoareTriple, proof: str | None, positive: bool
    ) -> None:
        """
        Write the proof to a file in the tmpdir.
        """
        polarity = "Positive" if positive else "Negative"
        basic = load_txt(
            f"{polarity}.lean.template",
            proof=proof,
            **triple.model_dump(),
        )
        self.write_code(basic)
        return None

    def run(
        self, triple: HoareTriple, proof: str | None = None, positive: bool = True
    ) -> LakeResponse:
        """
        Run the lake tool and return the response. (None option for proof is just for testing).

        Args:
            triple: The Hoare triple to prove
            proof: The proof to write to the file
            positive: The polarity flag (to affirm vs deny the hoare triple)

        Returns:
            LakeResponse: The result of the lake tool
        """
        self.write_proof(triple, proof, positive)
        result = lake_exe_check(self.cwd)
        return result

    def run_code(self, lean_code: str) -> LakeResponse:
        """Run the lake tool and return the response."""
        self.write_code(lean_code)
        return lake_exe_check(self.cwd)
