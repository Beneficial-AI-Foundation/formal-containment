from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from containment.structures import Specification, HoareTriple, Language

TEMPLATE_DIR = Path.cwd() / ".." / "txt"


def load_txt(template_name: str | Path, **kwargs) -> str:
    """
    Load and render a prompt template from the txt directory in the monorepo root.

    Args:
        **kwargs: Variables to pass to the template

    Returns:
        Rendered prompt string
    """
    if isinstance(template_name, str) and template_name.endswith(".template"):
        env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
        template = env.get_template(template_name)
        return template.render(**kwargs)
    with open(TEMPLATE_DIR / template_name, "r") as template_file:
        return template_file.read()


def oracle_system_prompt(language: Language) -> str:
    """
    Get the system prompt for the oracle.

    Args:
        language: The language of the oracle

    Returns:
        The complete system prompt for the oracle
    """
    language_instructions = load_txt(f"{language}.system.prompt")
    return load_txt(
        "oracle.system.prompt.template", language_instructions=language_instructions
    )


def imp_user_prompt(spec: Specification, failed_attempts: str) -> str:
    """
    Get the user prompt for the imp oracle.
    """
    return load_txt(
        "imp.user.prompt.template", failed_attempts=failed_attempts, **spec.model_dump()
    )


def proof_user_prompt(
    triple: HoareTriple, stderr: str | None = None, positive: bool = True
) -> str:
    """
    Get the user prompt for the proof oracle.
    """
    return load_txt(
        "proof.user.prompt.template",
        **triple.model_dump(),
        stderr=stderr,
        positive=positive,
    )
