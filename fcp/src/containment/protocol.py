from containment.mcp.clients.experts.imp import ImpExpert
from containment.mcp.clients.experts.proof import ProofExpert
from containment.structures import (
    Specification,
    VerificationFailure,
    VerificationSuccess,
    VerificationResult,
)


async def _synthesize_and_prove(
    specification: Specification,
    *,
    proof_loop_budget: int = 10,
    failed_attempts: list[str] | None = None,
) -> VerificationResult:
    """
    Synthesize and prove a Hoare triple.
    """
    imp_expert = await ImpExpert.connect_and_run(
        specification, failed_attempts=failed_attempts
    )
    if imp_expert.triple is None:
        raise ValueError("Problem in imp expert synthesis.")
    proof_expert = await ProofExpert.connect_and_run(
        imp_expert.triple, positive=True, max_iterations=proof_loop_budget
    )
    if proof_expert.verification_result is None:
        raise ValueError("Problem in proof expert verification.")
    return proof_expert.verification_result


async def run(
    specification: Specification,
    *,
    proof_loop_budget: int = 10,
    attempt_budget: int = 5,
) -> VerificationResult | None:
    """
    Run the boundary screener, the boundary's main entrypoint.

    Return imp code to the caller (representing the outside world) if the proof is successful, allowing up to `attempt_budget` attempts.
    Returns `None` if `attempt_budget` imp programs fail.
    """
    failed_attempts = []
    for attempt in range(attempt_budget):
        print(
            f"Attempt to find program provable at specification {specification}: {attempt + 1}/{attempt_budget}"
        )

        result = await _synthesize_and_prove(
            specification,
            proof_loop_budget=proof_loop_budget,
            failed_attempts=failed_attempts,
        )
        match result:
            case VerificationSuccess():
                return result
            case VerificationFailure():
                failed_attempts.append(result.triple.command)
        print(
            f"Failed attempt {attempt + 1}/{attempt_budget} with error: {result.error_message}"
        )
