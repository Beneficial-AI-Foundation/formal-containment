import tomllib
from pathlib import Path
import asyncio
from containment.structures import Specification, VerificationResult, LLM
from containment.protocol import run as boundary_run

EXPERIMENTS = Path.cwd() / ".." / "experiments"


def load_experiment_data() -> dict[str, list]:
    """
    Load specifications from the experiments directory.
    """
    with open(EXPERIMENTS / "data.toml", "rb") as data:
        return tomllib.load(data)


def load_specifications() -> list[Specification]:
    """
    Load specifications from the experiments directory.
    """
    data = load_experiment_data()
    if "sample" not in data:
        raise ValueError(
            "No specification samples found in the experiment data. Check key in data.toml"
        )
    return [Specification(**specification) for specification in data["sample"]]


def load_models() -> list[LLM]:
    """
    Load models from the experiments directory.
    """
    data = load_experiment_data()
    if "model" not in data:
        raise ValueError("No models found in the experiment data.")
    return [LLM(**model) for model in data["model"]]


def _mk_model_dict() -> dict[str, LLM]:
    """
    Create a dictionary of models from the experiments directory.
    """
    models = load_models()
    return {model.human_name: model for model in models}


INCLUDE_MODELS = ["snt4", "gpt41"]


def experiment_matrix(
    include_models: list[str] = INCLUDE_MODELS,
) -> list[tuple[Specification, LLM]]:
    """
    Load the experiment matrix from the experiments directory.
    """
    specifications = load_specifications()
    models = load_models()
    return [
        (specification, model)
        for specification in specifications
        for model in models
        if model.litellm_id in include_models
    ]


async def run_experiments(
    proof_loop_budget: int,
    attempt_budget: int,
    *,
    include_models: list[str] = INCLUDE_MODELS,
) -> list[VerificationResult | None]:
    """
    Run the experiments on the given specifications in parallel

    Args:
        proof_loop_budget: The number of proof loops to run per imp attempt
        attempt_budget: The number of imp attempts to make
        include_models: The human names of models to include in the experiment run

    Returns:
        A list of VerificationResults or None for each experiment

    TODO: finish configuring-- logs, metadata
    """
    matrix = experiment_matrix(include_models)
    tasks = [
        boundary_run(
            model.litellm_id,
            specification,
            proof_loop_budget=proof_loop_budget,
            attempt_budget=attempt_budget,
        )
        for specification, model in matrix
    ]
    return await asyncio.gather(*tasks)


MODEL_DICT = _mk_model_dict()
