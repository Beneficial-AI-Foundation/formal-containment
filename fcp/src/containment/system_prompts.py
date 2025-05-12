from jinja2 import Environment, FileSystemLoader
from pathlib import Path

# Set up Jinja2 environment
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


def get_oracle_system_prompt(language_instructions: str) -> str:
    """
    Get the system prompt for the oracle.

    Args:


    Returns:
        The complete system prompt for the oracle
    """
    with open(template_dir / language_instructions, "r") as f:
        language_instructions = f.read()
    return load_prompt(
        "oracle.system.prompt", language_instructions=language_instructions
    )
