import pytest
from pathlib import Path
import tomllib
from containment.mcp.server import (
    get_proof_user_prompt,
    get_imp_user_prompt,
    run_lake_exe_check,
)
from containment.mcp.clients.experts.proof import SORRY_CANARY
from containment.structures import Specification, HoareTriple, LakeResponse
from containment.fsio.prompts import load_txt

# Test data
SAMPLE_PRECONDITION = "x > 0"
SAMPLE_COMMAND = "imp { x := x + 1; }"
SAMPLE_POSTCONDITION = "x > 1"
SAMPLE_METAVARIABLES = ""
SAMPLE_STDERR = ""


@pytest.fixture
def sample_specification():
    return Specification(
        precondition=SAMPLE_PRECONDITION,
        postcondition=SAMPLE_POSTCONDITION,
        metavariables=SAMPLE_METAVARIABLES,
    )


@pytest.fixture
def sample_hoare_triple(sample_specification):
    return HoareTriple(specification=sample_specification, command=SAMPLE_COMMAND)


@pytest.fixture
def experiment_data():
    with open(Path.cwd() / ".." / "experiments" / "data.toml", "rb") as experiment_data:
        experiments = tomllib.load(experiment_data)
    return experiments


def test_proof_user_prompt():
    """Test the hoare proof user prompt generation."""
    prompt = get_proof_user_prompt(
        precondition=SAMPLE_PRECONDITION,
        command=SAMPLE_COMMAND,
        postcondition=SAMPLE_POSTCONDITION,
        metavariables=SAMPLE_METAVARIABLES,
        stderr=SAMPLE_STDERR,
        polarity="Negative",
    )
    assert isinstance(prompt, str)
    assert SAMPLE_PRECONDITION in prompt
    assert SAMPLE_COMMAND in prompt
    assert SAMPLE_POSTCONDITION in prompt


def test_imp_user_prompt():
    """Test the imp user prompt generation."""
    prompt = get_imp_user_prompt(
        precondition=SAMPLE_PRECONDITION,
        postcondition=SAMPLE_POSTCONDITION,
        metavariables=SAMPLE_METAVARIABLES,
        failed_attempts="",
    )
    assert isinstance(prompt, str)
    assert SAMPLE_PRECONDITION in prompt
    assert SAMPLE_POSTCONDITION in prompt


def test_typecheck_tool():
    """Test the typecheck tool functionality."""
    lean_code = """
    def main' : IO Unit := do
      IO.println "Hello, World!"
    """
    cwd, response = run_lake_exe_check(lean_code)
    assert isinstance(cwd, Path)
    assert isinstance(response, LakeResponse)
    assert hasattr(response, "exit_code")
    assert hasattr(response, "stdout")
    assert hasattr(response, "stderr")
    assert response.exit_code == 0

    assert response.stdout == ""
    assert response.stderr


def test_pos_sorry(sample_hoare_triple):
    """Test lake tool on positive lean template with sorry filled in."""
    pos_sorry = load_txt(
        "Positive.lean.template", proof="sorry", **sample_hoare_triple.model_dump()
    )
    assert isinstance(pos_sorry, str)
    assert "sorry" in pos_sorry
    cwd, response = run_lake_exe_check(pos_sorry)
    assert isinstance(cwd, Path)
    assert isinstance(response, LakeResponse)
    assert response.exit_code == 0
    assert SORRY_CANARY in response.stderr


@pytest.mark.parametrize("polarity", ["Positive", "Negative"])
def test_fail(sample_hoare_triple, polarity):
    pos_fail = load_txt(
        f"{polarity}.lean.template",
        proof="<NOT A PROOF>",
        **sample_hoare_triple.model_dump(),
    )
    assert isinstance(pos_fail, str)
    cwd, response = run_lake_exe_check(pos_fail)
    assert isinstance(cwd, Path)
    assert isinstance(response, LakeResponse)
    assert response.exit_code == 1
    assert response.stderr
    assert not response.stdout


@pytest.mark.parametrize("polarity", ["Positive", "Negative"])
def test_experiments_sorry(experiment_data, polarity):
    for sample in experiment_data["sample"]:
        assert isinstance(sample, dict)
        assert "precondition" in sample
        assert "postcondition" in sample
        hoare_triple = HoareTriple(
            specification=Specification(
                precondition=sample["precondition"],
                postcondition=sample["postcondition"],
                metavariables=(
                    sample["metavariables"] if "metavariables" in sample else ""
                ),
            ),
            command=SAMPLE_COMMAND,
        )
        sorry = load_txt(
            f"{polarity}.lean.template", proof="sorry", **hoare_triple.model_dump()
        )
        assert isinstance(sorry, str)
        cwd, response = run_lake_exe_check(sorry)
        assert isinstance(cwd, Path)
        assert isinstance(response, LakeResponse)
        assert response.exit_code == 0
        assert SORRY_CANARY in response.stderr
        assert not response.stdout


@pytest.mark.parametrize("polarity", ["Positive", "Negative"])
def test_experiments_fail(experiment_data, polarity):
    for sample in experiment_data["sample"]:
        assert isinstance(sample, dict)
        assert "precondition" in sample
        assert "postcondition" in sample
        hoare_triple = HoareTriple(
            specification=Specification(
                precondition=sample["precondition"],
                postcondition=sample["postcondition"],
                metavariables=(
                    sample["metavariables"] if "metavariables" in sample else ""
                ),
            ),
            command=SAMPLE_COMMAND,
        )

        fail = load_txt(
            f"{polarity}.lean.template",
            proof="<NOT A PROOF>",
            **hoare_triple.model_dump(),
        )
        assert isinstance(fail, str)
        cwd, response = run_lake_exe_check(fail)
        assert isinstance(cwd, Path)
        assert isinstance(response, LakeResponse)
        assert response.exit_code == 1
        assert not response.stdout
