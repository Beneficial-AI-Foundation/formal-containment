from pathlib import Path
from typing import Literal
from jinja2 import Environment, FileSystemLoader
from containment.structures import Specification, HoareTriple

template_dir = (
    # Path(__file__).parent.parent.parent.parent / "txt"
    Path.cwd() / ".." / "txt"
)  # Go up to monorepo root
env = Environment(loader=FileSystemLoader(template_dir))


def load_template(template_name: str, **kwargs) -> str:
    """
    Load and render a prompt template from the txt directory in the monorepo root.

    Args:
        **kwargs: Variables to pass to the template

    Returns:
        Rendered prompt string
    """
    template = env.get_template(template_name)
    return template.render(**kwargs)


def get_oracle_system_prompt(language: Literal["imp", "proof"]) -> str:
    """
    Get the system prompt for the oracle.

    Args:
        language: The language of the oracle

    Returns:
        The complete system prompt for the oracle
    """
    with open(template_dir / f"{language}.system.prompt", "r") as f:
        language_instructions = f.read()
    return load_template(
        "oracle.system.prompt.template", language_instructions=language_instructions
    )


def get_imp_user_prompt(spec: Specification) -> str:
    """
    Get the user prompt for the imp oracle.
    """
    return load_template("imp.user.prompt.template", **spec.dictionary)


def proof_user_template(stage: str) -> str:
    return f"proof.user.{stage}.prompt.template"


def get_proof_user_prompt(triple: HoareTriple, stderr: str | None = None) -> str:
    """
    Get the user prompt for the proof oracle.
    """

    if stderr is not None:
        return load_template(
            proof_user_template("continuous"), stderr=stderr, **triple.dictionary
        )
    return load_template(proof_user_template("init"), **triple.dictionary)
