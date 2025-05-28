from containment.structures import Specification, HoareTriple
from containment.fsio.prompts import load_txt, oracle_system_prompt


def test_oracle_template_loading():
    """Test oracle system prompt generation."""
    template = load_txt("oracle.system.prompt.template", language_instructions="test")
    assert isinstance(template, str)
    assert len(template) > 0

    proof_prompt = oracle_system_prompt("proof")
    imp_prompt = oracle_system_prompt("imp")
    assert isinstance(proof_prompt, str)
    assert isinstance(imp_prompt, str)
    assert len(proof_prompt) > 0
    assert len(imp_prompt) > 0


def test_pos_lean_file():
    """Test loading positive lean template file."""
    hoare_triple = HoareTriple(
        specification=Specification(
            precondition="test_prec", postcondition="test_post"
        ),
        command="test_command",
    )
    pos_sorry = load_txt(
        "Positive.lean.template", proof="sorry", **hoare_triple.model_dump()
    )
    assert isinstance(pos_sorry, str)
    assert len(pos_sorry) > 0

    assert hoare_triple.specification.precondition in pos_sorry
    assert hoare_triple.command in pos_sorry
    assert hoare_triple.specification.postcondition in pos_sorry
    assert "sorry" in pos_sorry


def test_neg_lean_file():
    """Test loading negative lean template file."""
    hoare_triple = HoareTriple(
        specification=Specification(
            precondition="test_prec", postcondition="test_post"
        ),
        command="test_command",
    )
    neg_sorry = load_txt(
        "Negative.lean.template", proof="sorry", **hoare_triple.model_dump()
    )
    assert isinstance(neg_sorry, str)
    assert len(neg_sorry) > 0

    assert hoare_triple.specification.precondition in neg_sorry
    assert hoare_triple.command in neg_sorry
    assert hoare_triple.specification.postcondition in neg_sorry
    assert "sorry" in neg_sorry
