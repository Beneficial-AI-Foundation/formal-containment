"""
Functions for LLM completion.
"""

import os
from pathlib import Path
from typing import Callable
import dotenv
from litellm import completion

dotenv.load_dotenv(Path.cwd() / ".." / ".env")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

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
            {
                "role": "developer" if model.startswith("openai") else "system",
                "content": system_prompt,
            },
        ] + messages
        return completion(model=model, messages=messages, stream=False)  # type: ignore

    return _complete
