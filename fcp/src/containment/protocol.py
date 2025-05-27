from containment.mcp.clients.experts.imp import ImpExpert
from containment.mcp.clients.experts.proof import ProofExpert
from containment.structures import (
    Specification,
    VerificationFailure,
    VerificationSuccess,
    VerificationResult,
)
from containment.fsio.logs import logs


async def _synthesize_and_prove(
    model: str,
    specification: Specification,
    *,
    proof_loop_budget: int = 10,
    failed_attempts: list[str] | None = None,
) -> VerificationResult | None:
    """
    Synthesize and prove a Hoare triple.
    """
    imp_expert = await ImpExpert.connect_and_run(
        model, specification, failed_attempts=failed_attempts
    )
    if imp_expert.triple is None:
        return None
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
) -> VerificationResult | None:
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
            case None:
                logs.warning(f"{msg_prefix}: Problem in `imp` synthesis.")
            case VerificationSuccess():
                return result
            case VerificationFailure():
                failed_attempts.append(result.triple.command)
                msg = f"{msg_prefix}: Failed attempt {attempt + 1}/{attempt_budget} with error: {result.error_message}"
                logs.info(msg)
    return None
