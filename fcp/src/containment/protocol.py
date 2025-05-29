import asyncio
from containment.mcp.clients.experts.imp import ImpExpert
from containment.mcp.clients.experts.proof.loop import ProofExpert as LoopProofExpert
from containment.structures import (
    Polarity,
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
    proof_expert_pos = LoopProofExpert.connect_and_run(
        model,
        imp_expert.triple,
        polarity=Polarity.POS,
        max_iterations=proof_loop_budget,
    )
    proof_expert_neg = LoopProofExpert.connect_and_run(
        model,
        imp_expert.triple,
        polarity=Polarity.NEG,
        max_iterations=proof_loop_budget,
    )

    done, pending = await asyncio.wait(
        [
            asyncio.create_task(expert)
            for expert in [proof_expert_pos, proof_expert_neg]
        ],
        return_when=asyncio.FIRST_COMPLETED,
    )
    for task in pending:
        task.cancel()
    proof_expert = done.pop().result()
    if proof_expert.verification_result is None:
        raise ValueError(
            "Unreachable. `verification_result` is initialized to None but is always set to the right type in `.connect_and_run`"
        )
    return proof_expert.verification_result


async def boundary(
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
                if result.metadata.polarity == Polarity.POS:
                    msg = f"{msg_prefix}: proof in the positive polarity found, code is safe!"
                    logs.info(msg)
                    return result
                else:
                    msg = f"{msg_prefix}: proof in the negative polarity found, code is unsafe!"
                    continue
    return failed_attempts
