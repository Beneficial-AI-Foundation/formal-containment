import re
from containment.structures import Language


def parse_program_completion(program_completion: str, tag: Language) -> str | None:
    """Parse the completion and return the program or proof content between tags."""
    # Create regex pattern for the specific tag
    pattern = f"<{tag}>(.*?)</{tag}>"
    mtch = re.search(pattern, program_completion, re.DOTALL)

    if mtch:
        return mtch.group(1).strip()
    return None
