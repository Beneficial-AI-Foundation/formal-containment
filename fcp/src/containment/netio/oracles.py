"""
Functions for LLM completion.
"""

import os
from pathlib import Path
from typing import Callable
import dotenv
from containment.structures import Language
from containment.netio.parse_xml import parse_xml

# from containment.io.logs import logs
from litellm import completion

dotenv.load_dotenv(Path.cwd() / ".." / ".env")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

ANTHROPIC_PREFIX = Path("anthropic")
OPENAI_PREFIX = Path("openai")

SONNET_PIN = "claude-3-7-sonnet-20250219"
SONNET_3_7 = str(ANTHROPIC_PREFIX / SONNET_PIN)
GPT_PIN = "gpt-4.1-2025-04-14"
GPT_4_1 = str(OPENAI_PREFIX / GPT_PIN)
ORACLE_CONFIG_MAX_TOKENS = 2**14


def mk_complete(
    model: str,
    system_prompt: str,
) -> Callable[[list[dict]], dict]:
    """
    Creates a lambda for sending messages to anthropic, whomst returns a completion.
    """

    # logs.info(f"Anthropic system prompt: {sysprompt}")
    def _complete(messages: list[dict]) -> dict:
        messages = [
            {"role": "system", "content": system_prompt},
        ] + messages
        return completion(model=model, messages=messages, stream=False)  # type: ignore

    return _complete


def parse_program_completion(program_completion: str, tag: Language) -> str | None:
    """Call the XML parser on the completion and return the program."""
    program_tree = parse_xml(program_completion)
    program = program_tree.text if program_tree.tag == tag else None
    return program
