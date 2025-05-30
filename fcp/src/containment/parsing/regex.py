import re
from containment.structures import Language


def parse_program_completion(program_completion: str, tag: Language) -> str | None:
    """Parse the completion and return the program or proof content between tags."""
    # Create regex pattern for the specific tag
    pattern = f"<{tag}>(.*?)</{tag}>"
    match = re.search(pattern, program_completion, re.DOTALL)

    if match:
        return match.group(1).strip()
    return None
