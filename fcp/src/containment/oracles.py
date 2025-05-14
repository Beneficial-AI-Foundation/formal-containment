"""
Loop scaffold making up the imp and proof oracle.
"""

import os
from typing import Callable, Literal
from pathlib import Path
import dotenv
from anthropic import Anthropic
from containment.structures import HoareTriple, Specification
from containment.parse_xml import parse_xml
from containment.prompts import (
    get_imp_user_prompt,
    get_oracle_system_prompt,
    get_proof_user_prompt,
)

dotenv.load_dotenv(Path.cwd())
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")


def get_oracle_client() -> Anthropic:
    """
    Get the oracle client.
    """
    return Anthropic(api_key=ANTHROPIC_API_KEY)


def mk_complete(
    client: Anthropic, system_prompt: str, cache: bool = True
) -> Callable[[list[dict]], list[dict]]:
    """
    Creates a lambda for sending messages to anthropic, whomst returns a completion.
    """
    sysprompt: dict = {"type": "text", "text": system_prompt}
    if cache:
        sysprompt["cache-control"] = "ephemeral"

    def _complete(messages: list[dict]) -> list[dict]:
        response = client.messages.create(
            model="claude-3-7-sonnet-20250219",
            max_tokens=16384,
            system=[sysprompt],  # type: ignore
            messages=messages,  # type: ignore
        )
        return response.content  # type: ignore

    return _complete


def parse_program_completion(
    program_completion: list, tag: Literal["imp", "proof"]
) -> str | None:
    program_tree = parse_xml(program_completion[0].text)
    program = program_tree.text if program_tree.tag == tag else None
    return program


class Oracle:
    def __init__(self, system_prompt: str):
        self.client = get_oracle_client()
        self.system_prompt = system_prompt
        self.complete = mk_complete(self.client, system_prompt, cache=False)


def imp_oracle(spec: Specification) -> str | None:
    """
    Oracle imp expert.
    """
    system_prompt = get_oracle_system_prompt("imp")
    imp_user_prompt = get_imp_user_prompt(spec)
    oracle = Oracle(system_prompt)
    completion = oracle.complete([{"role": "user", "content": imp_user_prompt}])
    program = parse_program_completion(completion, "imp")
    return program


def proof_oracle(
    conversation_so_far: list,
    triple: HoareTriple,
    stderr: str | None = None,
) -> tuple[str | None, list[dict]]:
    """
    Oracle hoare proof expert.
    """
    system_prompt = get_oracle_system_prompt("proof")
    proof_user_prompt = get_proof_user_prompt(triple, stderr)
    curr_conversation = [{"role": "user", "content": proof_user_prompt}]
    conversation = conversation_so_far + curr_conversation
    oracle = Oracle(system_prompt)
    completion = oracle.complete(conversation)
    proof = parse_program_completion(completion, "proof")
    return proof, conversation
