import pytest
from containment.structures import Specification, HoareTriple
from containment.fsio.prompts import load_txt, expert_system_prompt


def test_oracle_template_loading():
    """Test oracle system prompt generation."""
    template = load_txt("expert.system.prompt.template", language_instructions="test")
    assert isinstance(template, str)
    assert len(template) > 0

    proof_prompt = expert_system_prompt("loop/proof")
    imp_prompt = expert_system_prompt("imp")
    assert isinstance(proof_prompt, str)
    assert isinstance(imp_prompt, str)
    assert len(proof_prompt) > 0
    assert len(imp_prompt) > 0


@pytest.mark.parametrize("polarity", ["Positive", "Negative"])
def test_lean_file(polarity):
    """Test loading positive lean template file."""
    hoare_triple = HoareTriple(
        specification=Specification(
            precondition="test_prec", postcondition="test_post"
        ),
        command="test_command",
    )
    pos_sorry = load_txt(
        f"loop/{polarity}.lean.template", proof="sorry", **hoare_triple.model_dump()
    )
    assert isinstance(pos_sorry, str)
    assert len(pos_sorry) > 0

    assert hoare_triple.specification.precondition in pos_sorry
    assert hoare_triple.command in pos_sorry
    assert hoare_triple.specification.postcondition in pos_sorry
    assert "sorry" in pos_sorry
