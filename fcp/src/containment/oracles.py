"""
Functions for LLM completion.
"""

import os
from pathlib import Path
from typing import Callable
import dotenv
from anthropic import Anthropic
from containment.structures import HoareTriple, Specification, Language
from containment.parse_xml import parse_xml
from containment.prompts import (
    imp_user_prompt,
    oracle_system_prompt,
    proof_user_prompt,
)

dotenv.load_dotenv(Path.cwd() / ".." / ".env")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

ORACLE_CONFIG_MODEL = "claude-3-7-sonnet-20250219"
ORACLE_CONFIG_MAX_TOKENS = 2**14


def get_oracle_client() -> Anthropic:
    """
    Get the oracle/completion client.
    """
    return Anthropic(api_key=ANTHROPIC_API_KEY)


def mk_complete(
    client: Anthropic,
    system_prompt: str,
    *,
    cache: bool = True,
    available_tools: list[dict] | None = None,
) -> Callable[[list[dict]], list[dict]]:
    """
    Creates a lambda for sending messages to anthropic, whomst returns a completion.
    """
    sysprompt = {"type": "text", "text": system_prompt}
    if cache:
        sysprompt["cache-control"] = "ephemeral"

    if available_tools is None:
        available_tools = []

    def _complete(messages: list[dict]) -> list[dict]:
        response = client.messages.create(
            model=ORACLE_CONFIG_MODEL,
            max_tokens=ORACLE_CONFIG_MAX_TOKENS,
            system=[sysprompt],  # type: ignore
            messages=messages,  # type: ignore
            tools=available_tools,  # type: ignore
        )
        return response.content  # type: ignore

    return _complete


def parse_program_completion(program_completion: list, tag: Language) -> str | None:
    program_tree = parse_xml(program_completion[0].text)
    program = program_tree.text if program_tree.tag == tag else None
    return program


def imp_oracle(spec: Specification) -> str | None:
    """
    Expert imp programmer.
    """
    failed_attempts = ""
    client = get_oracle_client()
    system_prompt = oracle_system_prompt("imp")
    user_prompt = imp_user_prompt(spec, failed_attempts=failed_attempts)
    complete = mk_complete(client, system_prompt, cache=False)
    completion = complete([{"role": "user", "content": user_prompt}])
    program = parse_program_completion(completion, "imp")
    return program


def proof_oracle(
    conversation_so_far: list[dict],
    triple: HoareTriple,
    stderr: str | None = None,
) -> tuple[str | None, list[dict]]:
    """
    Expert hoare proof synthesizer.
    """
    system_prompt = oracle_system_prompt("proof")
    user_prompt = proof_user_prompt(triple, stderr)
    client = get_oracle_client()
    curr_conversation = [{"role": "user", "content": user_prompt}]
    conversation = conversation_so_far + curr_conversation
    complete = mk_complete(client, system_prompt, cache=False)
    completion = complete(conversation)
    proof = parse_program_completion(completion, "proof")
    return proof, conversation
