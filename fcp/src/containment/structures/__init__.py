import json
from pathlib import Path
from subprocess import CompletedProcess
from typing import Literal, Self, Sequence
from containment.structures.basic import Structure
from containment.structures.enums import Polarity

type Language = Literal["imp", "loop/proof", "proof"]


class Specification(Structure):
    precondition: str
    postcondition: str
    metavariables: str = ""  # invariant: space separated lean identifiers
    name: str | None = None


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

    @property
    def hidden_code(self) -> str:
        """An alternative str method that hides the command"""
        return f"\\{{ {self.specification.precondition} \\}} {hash(self.command)} \\{{ {self.specification.postcondition} \\}}"


class LLM(Structure):
    human_name: str
    provider: str
    model_pin: str

    @property
    def litellm_id(self) -> str:
        return str(Path(self.provider) / self.model_pin)

    def __str__(self) -> str:
        return self.litellm_id


class ExpertMetadata(Structure):
    iteration: int = 0
    model: str
    polarity: Polarity
    success: bool = False

    def incr(self) -> None:
        self.iteration += 1

    def successful(self) -> None:
        self.success = True


class VerificationSuccess(Structure):
    triple: HoareTriple
    proof: str
    audit_trail: Path
    metadata: ExpertMetadata


class VerificationFailure(Structure):
    triple: HoareTriple
    proof: str
    error_message: str
    audit_trail: Path
    metadata: ExpertMetadata

    @property
    def failure_str(self) -> str:
        return self.triple.command


class ImpFailure(Structure):
    specification: Specification
    attempted_completion: str
    metadata: ExpertMetadata
    failed_attempts: list[VerificationFailure | Self] | None = None
    error_message: str | None = None

    @property
    def failure_str(self) -> str:
        return self.attempted_completion


type Failure = VerificationFailure | ImpFailure
type Success = VerificationSuccess
type VerificationResult = Success | Sequence[Failure]


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
