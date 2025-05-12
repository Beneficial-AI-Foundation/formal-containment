from dataclasses import dataclass
from enum import Enum


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


@dataclass
class VerificationResponse:
    result: VerificationResult
    triple: HoareTriple
    error_message: str | None = None
