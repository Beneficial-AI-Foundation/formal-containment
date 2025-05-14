from dataclasses import dataclass
from enum import Enum
from subprocess import CompletedProcess


class VerificationResult(Enum):
    PASS = "pass"
    FAIL = "fail"


@dataclass
class Specification:
    precondition: str
    postcondition: str


@dataclass
class HoareTriple:
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


@dataclass
class VerificationResponse:
    result: VerificationResult
    triple: HoareTriple
    error_message: str | None = None


@dataclass
class ToolResponse:
    exit_code: int
    stdout: str
    stderr: str

    @classmethod
    def from_subprocess_result(
        cls,
        result: CompletedProcess[str],
    ) -> "ToolResponse":
        return cls(
            exit_code=result.returncode,
            stdout=result.stdout,
            stderr=result.stderr,
        )
