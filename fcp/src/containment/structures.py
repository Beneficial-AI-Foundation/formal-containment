import json
from pathlib import Path
from subprocess import CompletedProcess
from typing import Literal
from pydantic import BaseModel

type Language = Literal["imp", "proof"]


class Structure(BaseModel):
    """
    Base class for all structures.
    """

    @property
    def jsons(self) -> str:
        return json.dumps(self.model_dump())


class Specification(Structure):
    precondition: str
    postcondition: str


class HoareTriple(Structure):
    specification: Specification
    command: str

    def __hash__(self) -> int:
        return hash(
            (
                self.specification.precondition,
                self.command,
                self.specification.postcondition,
            )
        )

    def __str__(self) -> str:
        return f"\\{{ {self.specification.precondition} \\}} {self.command} \\{{ {self.specification.postcondition} \\}}"


class VerificationSuccess(Structure):
    triple: HoareTriple
    proof: str


class VerificationFailure(Structure):
    triple: HoareTriple
    proof: str
    error_message: str


type VerificationResult = VerificationSuccess | VerificationFailure


class LakeResponse(Structure):
    exit_code: int
    stdout: str
    stderr: str

    @classmethod
    def from_subprocess_result(
        cls,
        result: CompletedProcess[str],
    ) -> "LakeResponse":
        return cls(
            exit_code=result.returncode,
            stdout=result.stdout,
            stderr=result.stderr,
        )


class CheckerBase(Structure):
    cwd: Path

    @property
    def basic_path(self) -> Path:
        return self.cwd / "Artifacts" / "Basic.lean"
