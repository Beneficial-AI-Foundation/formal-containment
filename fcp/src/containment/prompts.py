from pathlib import Path
from dataclasses import asdict
from jinja2 import Environment, FileSystemLoader
from containment.structures import Specification, HoareTriple

template_dir = (
    Path(__file__).parent.parent.parent.parent / "txt"
)  # Go up to monorepo root
env = Environment(loader=FileSystemLoader(template_dir))


def load_prompt(template_name: str, **kwargs) -> str:
    """
    Load and render a prompt template from the txt directory in the monorepo root.

    Args:

        **kwargs: Variables to pass to the template

    Returns:
        Rendered prompt string
    """
    template = env.get_template(template_name)
    return template.render(**kwargs)


def get_oracle_system_prompt(language: str) -> str:
    """
    Get the system prompt for the oracle.

    Args:


    Returns:
        The complete system prompt for the oracle
    """
    with open(template_dir / f"{language}.system.prompt", "r") as f:
        language_instructions = f.read()
    return load_prompt(
        "oracle.system.prompt.template", language_instructions=language_instructions
    )


def get_imp_user_prompt(spec: Specification) -> str:
    """
    Get the user prompt for the imp oracle.
    """
    return load_prompt("imp.user.prompt.template", **asdict(spec))


def get_proof_user_prompt(triple: HoareTriple) -> str:
    """
    Get the user prompt for the proof oracle.
    """

    return load_prompt("proof.user.init.prompt.template", **asdict(triple))
