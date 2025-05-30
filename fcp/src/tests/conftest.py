import pytest
from pathlib import Path
import tomllib
from containment.structures import Specification, HoareTriple

# Test data
SAMPLE_PRECONDITION = "x > 0"
SAMPLE_COMMAND = "imp { x := x + 1; }"
SAMPLE_POSTCONDITION = "x > 1"
SAMPLE_METAVARIABLES = ""
SAMPLE_STDERR = ""


@pytest.fixture
def sample_precondition() -> str:
    return SAMPLE_PRECONDITION


@pytest.fixture
def sample_command() -> str:
    return SAMPLE_COMMAND


@pytest.fixture
def sample_postcondition() -> str:
    return SAMPLE_POSTCONDITION


@pytest.fixture
def sample_metavariables() -> str:
    return SAMPLE_METAVARIABLES


@pytest.fixture
def sample_stderr() -> str:
    return SAMPLE_STDERR


@pytest.fixture
def sample_specification(
    sample_precondition: str, sample_postcondition: str, sample_metavariables: str = ""
) -> Specification:
    return Specification(
        precondition=sample_precondition,
        postcondition=sample_postcondition,
        metavariables=sample_metavariables,
    )


@pytest.fixture
def sample_hoare_triple(sample_specification: Specification, sample_command: str):
    return HoareTriple(specification=sample_specification, command=sample_command)


@pytest.fixture
def experiment_data():
    with open(Path.cwd() / ".." / "experiments" / "data.toml", "rb") as experiment_data:
        experiments = tomllib.load(experiment_data)
    return experiments
