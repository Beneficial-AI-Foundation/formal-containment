from containment.mcp.clients.experts.imp import ImpExpert
from containment.mcp.clients.experts.proof import ProofExpert
from containment.structures import (
    Specification,
    VerificationSuccess,
    VerificationResult,
    Failure,
)
from containment.fsio.logs import logs


async def _synthesize_and_prove(
    model: str,
    specification: Specification,
    *,
    proof_loop_budget: int,
    failed_attempts: list[Failure] | None = None,
) -> VerificationResult:
    """
    Synthesize and prove a Hoare triple.
    """
    imp_expert = await ImpExpert.connect_and_run(
        model, specification, failed_attempts=failed_attempts
    )
    if imp_expert.triple is None:
        if imp_expert.failure is None:
            raise ValueError(
                "Unreachable. `triple` is None but `failure` is also None, which should not happen."
            )
        return imp_expert.failure
    proof_expert = await ProofExpert.connect_and_run(
        model, imp_expert.triple, positive=True, max_iterations=proof_loop_budget
    )
    if proof_expert.verification_result is None:
        raise ValueError(
            "Unreachable. `verification_result` is initialized to None but is always set to the right type in `.connect_and_run`"
        )
    return proof_expert.verification_result


async def run(
    model: str,
    specification: Specification,
    *,
    proof_loop_budget: int = 10,
    attempt_budget: int = 5,
) -> VerificationResult:
    """
    Run the boundary screener, the boundary's main entrypoint.

    Return imp code to the caller (representing the outside world) if the proof is successful, allowing up to `attempt_budget` attempts.
    Returns `None` if `attempt_budget` imp programs fail.
    """
    msg_prefix = f"{model}:{specification.name if specification.name is not None else 'user_spec'}-"
    failed_attempts = []
    for attempt in range(attempt_budget):
        msg = f"{msg_prefix}: Attempt to find program provable at specification {specification.name}: {attempt + 1}/{attempt_budget}"
        logs.info(msg)
        result = await _synthesize_and_prove(
            model,
            specification,
            proof_loop_budget=proof_loop_budget,
            failed_attempts=failed_attempts,
        )
        match result:
            case list():
                failed_attempts.extend(result)
            case VerificationSuccess():
                return result
    return failed_attempts
