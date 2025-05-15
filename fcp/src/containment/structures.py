from dataclasses import dataclass, asdict
from subprocess import CompletedProcess


@dataclass
class Specification:
    precondition: str
    postcondition: str

    @property
    def dictionary(self) -> dict:
        return asdict(self)


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

    @property
    def dictionary(self) -> dict:
        return asdict(self)


@dataclass
class VerificationSuccess:
    triple: HoareTriple


@dataclass
class VerificationFailure:
    triple: HoareTriple
    error_message: str


type VerificationResult = VerificationSuccess | VerificationFailure


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
