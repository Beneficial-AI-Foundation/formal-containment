from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from containment.structures import Specification, HoareTriple, Language

TEMPLATE_DIR = Path.cwd() / ".." / "txt"
env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))


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


def oracle_system_prompt(language: Language) -> str:
    """
    Get the system prompt for the oracle.

    Args:
        language: The language of the oracle

    Returns:
        The complete system prompt for the oracle
    """
    language_instructions = load_template(f"{language}.system.prompt")
    # with open(TEMPLATE_DIR / f"{language}.system.prompt", "r") as f:
    #    language_instructions = f.read()
    return load_template(
        "oracle.system.prompt.template", language_instructions=language_instructions
    )


def imp_user_prompt(spec: Specification) -> str:
    """
    Get the user prompt for the imp oracle.
    """
    return load_template("imp.user.prompt.template", **spec.model_dump())


def proof_user_template(stage: str) -> str:
    return f"proof.user.{stage}.prompt.template"


def proof_user_prompt(triple: HoareTriple, stderr: str | None = None) -> str:
    """
    Get the user prompt for the proof oracle.

    TODO: handle polarity
    """

    if stderr is not None:
        return load_template(
            proof_user_template("continuous"), stderr=stderr, **triple.model_dump()
        )
    return load_template(proof_user_template("init"), **triple.model_dump())
