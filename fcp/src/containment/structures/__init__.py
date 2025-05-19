import json
from pathlib import Path
from subprocess import CompletedProcess
from typing import Literal
from containment.structures.basic import Structure

type Language = Literal["imp", "proof"]


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

    @classmethod
    def from_jsons(cls, result: str) -> "LakeResponse":
        """The MCP server json RPC will return a str that json decodes into the arguments for LakeResponse"""
        return cls(**json.loads(result))


class CheckerBase(Structure):
    cwd: Path

    @property
    def basic_path(self) -> Path:
        return self.cwd / "Artifacts" / "Basic.lean"
