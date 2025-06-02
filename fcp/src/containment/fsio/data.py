from pathlib import Path
import tomllib
from containment.structures import Specification, LLM

EXPERIMENTS = Path.cwd() / ".." / "experiments"


def _load_experiment_data() -> dict[str, list]:
    """
    Load specifications from the experiments directory.
    """
    with open(EXPERIMENTS / "data.toml", "rb") as data:
        return tomllib.load(data)


def load_specifications() -> list[Specification]:
    """
    Load specifications from the experiments directory.
    """
    data = _load_experiment_data()
    if "sample" not in data:
        raise ValueError(
            "No specification samples found in the experiment data. Check key in data.toml"
        )
    return [Specification(**specification) for specification in data["sample"]]


def load_models() -> list[LLM]:
    """
    Load models from the experiments directory.
    """
    data = _load_experiment_data()
    if "model" not in data:
        raise ValueError("No models found in the experiment data.")
    return [LLM(**model) for model in data["model"]]


def _mk_model_dict() -> dict[str, LLM]:
    """
    Create a dictionary of models from the experiments directory.
    """
    models = load_models()
    return {model.human_name: model for model in models}


MODEL_DICT = _mk_model_dict()
