import json
from pathlib import Path
from subprocess import CompletedProcess
from typing import Literal
from containment.structures.basic import Structure

type Language = Literal["imp", "proof"]


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


class ProofLoopMetadata(Structure):
    converged_at_iteration: int = 0
    artifacts_dir: Path | None = None
    model: str

    def incr(self) -> None:
        self.converged_at_iteration += 1

    def chdir(self, cwd: Path) -> None:
        self.artifacts_dir = cwd


class VerificationSuccess(Structure):
    triple: HoareTriple
    proof: str
    audit_trail: Path
    metadata: ProofLoopMetadata


class VerificationFailure(Structure):
    triple: HoareTriple
    proof: str
    error_message: str
    audit_trail: Path
    metadata: ProofLoopMetadata


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
