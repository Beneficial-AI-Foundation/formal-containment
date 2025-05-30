import asyncio
from itertools import product
from collections import defaultdict
from typing import Sequence
from containment.structures import (
    Specification,
    VerificationResult,
    VerificationSuccess,
    VerificationFailure,
    ImpFailure,
    LLM,
)
from containment.protocol import boundary
from containment.fsio.artifacts import dump_toml, dump_json
from containment.fsio.logs import logs
from containment.fsio.data import load_models, load_specifications, INCLUDE_MODELS


def _experiment_matrix(
    include_models: list[str] = INCLUDE_MODELS,
) -> list[tuple[Specification, LLM]]:
    """
    Load the experiment matrix from the experiments directory.
    """
    specifications = load_specifications()
    models = load_models()
    return list(
        product(
            specifications,
            [model for model in models if model.human_name in include_models],
        )
    )


def _pp_matrix(matrix: list[tuple[Specification, LLM]]) -> str:
    """
    Pretty print the experiment matrix.
    """
    return "\n".join(
        f"{specification} -> {model.human_name}" for specification, model in matrix
    )


def _results_dict(
    results: list[VerificationResult | BaseException],
) -> dict:
    """
    Create a dictionary of results from the experiment matrix.

    Takes the last failure only, in the case of failures
    """
    result_dict = defaultdict(dict)
    result_dict["_fail"]["_fail"] = []
    for result in results:
        if isinstance(result, VerificationSuccess):
            logs.info(
                f"Experiment succeeded for {result.triple.specification.name} by {result.metadata.model}: {result}"
            )
            result_dict[result.triple.specification.name][result.metadata.model] = (
                result.dictionary
            )
        elif isinstance(result, Sequence):
            if len(result) < 1:
                result_dict["_fail"]["_fail"].append(
                    f"Something went wrong with result: {result}"
                )
                continue
            match result[-1]:
                case VerificationFailure():
                    spec_name = result[-1].triple.specification.name
                case ImpFailure():
                    spec_name = result[-1].specification.name
            logs.info(
                f"Experiment failed for {spec_name} by {result[-1].metadata.model}: {result[-1]}"
            )
            result_dict[spec_name][result[-1].metadata.model] = result[-1].dictionary

        elif isinstance(result, BaseException):
            result_dict["_fail"]["_fail"].append(str(result))
            logs.error(f"Experiment threw an exception: {result}")
        else:
            result_dict["_fail"]["_fail"].append(
                f"Unknown result:: {result}: {type(result)}"
            )
            logs.warning(f"Some unknown result: {result}")
    return dict(result_dict)


async def run_experiments(
    proof_loop_budget: int,
    attempt_budget: int,
    *,
    include_models: list[str] = INCLUDE_MODELS,
    sequential: bool = True,
) -> dict:
    """
    Run the experiments on the given specifications in parallel.

    Writes results to `experiments/artifacts/{timestamp}/experiment_results.toml`
    In addition to the results, the lean code is written also to `artifacts`

    Args:
        proof_loop_budget: The number of proof loops to run per imp attempt
        attempt_budget: The number of imp attempts to make
        include_models: The human names of models to include in the experiment run

    Returns:
        A list of VerificationResults or None for each experiment
    """
    matrix = _experiment_matrix(include_models)
    logs.info(f"Running {len(matrix)} experiments:")
    logs.info(_pp_matrix(matrix))
    tasks = [
        boundary(
            model.litellm_id,
            specification,
            proof_loop_budget=proof_loop_budget,
            attempt_budget=attempt_budget,
        )
        for specification, model in matrix
    ]
    if sequential:
        results = []
        for task in tasks:
            try:
                result = await task
                results.append(result)
            except Exception as exc:
                results.append(exc)
    else:
        results = await asyncio.gather(*tasks, return_exceptions=True)
    results_dict = _results_dict(results)
    dump_toml(results_dict)
    dump_json(results_dict)
    return results_dict
