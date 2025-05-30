import asyncio
from pathlib import Path
from containment.mcp.clients.experts.imp import ImpExpert
from containment.mcp.clients.experts.proof.loop import ProofExpert as LoopProofExpert
from containment.structures.enums import ProofMethod
from containment.structures import (
    Polarity,
    Specification,
    VerificationSuccess,
    VerificationResult,
    VerificationFailure,
    ImpFailure,
    Failure,
    HoareTriple,
    ExpertMetadata,
)
from containment.fsio.logs import logs


async def _synthesize_shot(
    model: str,
    specification: Specification,
    *,
    failed_attempts: list[Failure] | None = None,
) -> HoareTriple | ImpFailure:
    """
    Synthesize a Hoare triple from the specification.
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
    return imp_expert.triple


async def _synthesize(
    model: str,
    specification: Specification,
    *,
    failed_attempts: list[Failure] | None = None,
    imp_attempts: int = 5,
) -> HoareTriple:
    """
    Synthesize a hoare triple from the specification, allowing multiple attempts.
    """
    msg_prefix = f"{model}:{specification.name if specification.name is not None else 'user_spec'}:"
    result = None
    for attempt in range(imp_attempts):
        logs.info(
            f"{msg_prefix}: Attempt to synthesize hoare triple: {attempt + 1}/{imp_attempts}"
        )
        result = await _synthesize_shot(
            model, specification, failed_attempts=failed_attempts
        )
        match result:
            case HoareTriple():
                return result
            case ImpFailure():
                logs.warning(
                    f"{msg_prefix} Attempt {attempt + 1} failed: {result.failure_str}"
                )
                if failed_attempts is not None:
                    failed_attempts.append(result)
    msg = f"{msg_prefix}: Failed to synthesize hoare triple after {imp_attempts} attempts."
    if result is not None:
        msg += f" Last failure: {result.failure_str}"
    logs.error(msg)
    raise ValueError(msg)


async def _synthesize_and_prove_loop(
    model: str,
    specification: Specification,
    *,
    proof_loop_budget: int,
    failed_attempts: list[Failure] | None = None,
) -> VerificationResult:
    """
    Synthesize and prove a Hoare triple.
    """
    triple = await _synthesize(model, specification, failed_attempts=failed_attempts)
    proof_expert_pos = LoopProofExpert.connect_and_run(
        model,
        triple,
        polarity=Polarity.POS,
        max_iterations=proof_loop_budget,
    )
    proof_expert_neg = LoopProofExpert.connect_and_run(
        model,
        triple,
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


async def _synthesize_and_prove_search(
    model: str,
    specification: Specification,
    *,
    proof_loop_budget: int = 10,
    failed_attempts: list[Failure] | None = None,
) -> VerificationResult:
    """
    Synthesize and prove a Hoare triple, returning the result.
    """
    triple = await _synthesize(model, specification, failed_attempts=failed_attempts)
    return [
        VerificationFailure(
            triple=triple,
            proof="TODO: not implemented",
            error_message="TODO: not implemented",
            audit_trail=Path.cwd(),  # TODO: implement audit trail
            metadata=ExpertMetadata(model=model, polarity=Polarity.POS),
        )
    ]


async def boundary_loop(
    model: str,
    specification: Specification,
    *,
    proof_loop_budget: int = 10,
    attempt_budget: int = 5,
) -> VerificationResult:
    """
    Run the boundary screener, the boundary's main entrypoint, with a loop scaffold for proof search.

    Return imp code to the caller (representing the outside world) if the proof is successful, allowing up to `attempt_budget` attempts.
    Returns `None` if `attempt_budget` imp programs fail.
    """
    msg_prefix = f"{model}:{specification.name if specification.name is not None else 'user_spec'}-"
    failed_attempts = []
    for attempt in range(attempt_budget):
        msg = f"{msg_prefix}: Attempt to find program provable at specification {specification.name}: {attempt + 1}/{attempt_budget}"
        logs.info(msg)
        result = await _synthesize_and_prove_loop(
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


async def boundary(
    model: str,
    specification: Specification,
    *,
    attempt_budget: int = 5,
    proof_method: ProofMethod = ProofMethod.LOOP,
    proof_loop_budget: int = 10,
) -> VerificationResult:
    """
    Run the boundary screener, the boundary's main entrypoint.

    Return imp code to the caller (representing the outside world) if the proof is successful, allowing up to `attempt_budget` attempts.
    Returns `None` if `attempt_budget` imp programs fail.
    """
    match proof_method:
        case ProofMethod.LOOP:
            return await boundary_loop(
                model,
                specification,
                proof_loop_budget=proof_loop_budget,
                attempt_budget=attempt_budget,
            )
        case ProofMethod.TREE_SEARCH_BASIC:
            raise NotImplementedError("TODO")
