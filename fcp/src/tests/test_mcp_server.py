import pytest
from pathlib import Path
from containment.mcp.server import (
    get_proof_user_prompt,
    get_imp_user_prompt,
    run_lake_exe_check,
)
from containment.mcp.clients.experts.proof import SORRY_CANARY
from containment.structures import Specification, HoareTriple, LakeResponse
from containment.fsio.prompts import load_txt


# TODO: use less fixtures... these strings can just be inlined.
def test_proof_user_prompt(
    sample_precondition: str,
    sample_command: str,
    sample_postcondition: str,
    sample_metavariables: str,
    sample_stderr: str,
):
    """Test the hoare proof user prompt generation."""
    prompt = get_proof_user_prompt(
        precondition=sample_precondition,
        command=sample_command,
        postcondition=sample_postcondition,
        metavariables=sample_metavariables,
        stderr=sample_stderr,
        polarity="Negative",
    )
    assert isinstance(prompt, str)
    assert sample_precondition in prompt
    assert sample_command in prompt
    assert sample_postcondition in prompt


def test_imp_user_prompt(
    sample_precondition: str,
    sample_postcondition: str,
    sample_metavariables: str,
):
    """Test the imp user prompt generation."""
    prompt = get_imp_user_prompt(
        precondition=sample_precondition,
        postcondition=sample_postcondition,
        metavariables=sample_metavariables,
        failed_attempts="",
    )
    assert isinstance(prompt, str)
    assert sample_precondition in prompt
    assert sample_postcondition in prompt


def test_typecheck_tool(temp_lakeproj: Path):
    """Test the typecheck tool functionality."""
    lean_code = """
    def main' : IO Unit := do
      IO.println "Hello, World!"
    """
    response = run_lake_exe_check(lean_code, temp_lakeproj)
    assert isinstance(response, LakeResponse)
    assert hasattr(response, "exit_code")
    assert hasattr(response, "stdout")
    assert hasattr(response, "stderr")
    assert response.exit_code == 0

    assert response.stdout == ""
    assert response.stderr


def test_pos_sorry(sample_hoare_triple: HoareTriple, temp_lakeproj: Path):
    """Test lake tool on positive lean template with sorry filled in."""
    pos_sorry = load_txt(
        "loop/Positive.lean.template",
        proof="sorry",
        **sample_hoare_triple.model_dump(),
    )
    assert isinstance(pos_sorry, str)
    assert "sorry" in pos_sorry
    response = run_lake_exe_check(pos_sorry, temp_lakeproj)
    assert isinstance(response, LakeResponse)
    assert response.exit_code == 0
    assert SORRY_CANARY in response.stderr


@pytest.mark.parametrize("polarity", ["Positive", "Negative"])
def test_fail(sample_hoare_triple: HoareTriple, polarity: str, temp_lakeproj: Path):
    pos_fail = load_txt(
        f"loop/{polarity}.lean.template",
        proof="<NOT A PROOF>",
        **sample_hoare_triple.model_dump(),
    )
    assert isinstance(pos_fail, str)
    response = run_lake_exe_check(pos_fail, temp_lakeproj)
    assert isinstance(response, LakeResponse)
    assert response.exit_code == 1
    assert response.stderr
    assert not response.stdout


@pytest.mark.parametrize("polarity", ["Positive", "Negative"])
def test_experiments_sorry(
    experiment_data: dict, sample_command: str, polarity: str, temp_lakeproj: Path
):
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
            command=sample_command,
        )
        sorry = load_txt(
            f"loop/{polarity}.lean.template", proof="sorry", **hoare_triple.model_dump()
        )
        assert isinstance(sorry, str)
        response = run_lake_exe_check(sorry, temp_lakeproj)
        assert isinstance(response, LakeResponse)
        assert response.exit_code == 0
        assert SORRY_CANARY in response.stderr
        assert not response.stdout


@pytest.mark.parametrize("polarity", ["Positive", "Negative"])
def test_experiments_fail(
    experiment_data: dict, sample_command: str, polarity: str, temp_lakeproj: Path
):
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
            command=sample_command,
        )

        fail = load_txt(
            f"loop/{polarity}.lean.template",
            proof="<NOT A PROOF>",
            **hoare_triple.model_dump(),
        )
        assert isinstance(fail, str)
        response = run_lake_exe_check(fail, temp_lakeproj)
        assert isinstance(response, LakeResponse)
        assert response.exit_code == 1
        assert not response.stdout
