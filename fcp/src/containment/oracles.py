"""
Loop scaffold making up the imp and proof oracle.
"""

import os
from typing import Callable
import dotenv
from anthropic import Anthropic
from containment.structures import Specification, HoareTriple
from containment.prompts import get_oracle_system_prompt, get_imp_user_prompt

dotenv.load_dotenv("..")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")


def get_oracle_client() -> Anthropic:
    """
    Get the oracle client.
    """
    return Anthropic(api_key=ANTHROPIC_API_KEY)


def complete(
    client: Anthropic, system_prompt: str, cache: bool = True
) -> Callable[[list[dict]], list[dict]]:
    """
    Creates a lambda for sending messages to anthropic, whomst returns a completion
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


class Oracle:
    def __init__(self, system_prompt: str):
        self.client = get_oracle_client()
        self.system_prompt = system_prompt
        self.complete = complete(self.client, self.system_prompt, cache=False)


class Loop:
    def __init__(self, oracle: Oracle, tool: list[str] | Callable[[str], list[str]]):
        self.oracle = oracle
        self.tool = tool  # the executable (to be used with subprocess.run)

    # TODO: implement stateful loop that feeds error message from tool use back into oracle


def imp_oracle(spec: Specification) -> list[dict]:
    """
    Oracle for the imp loop.
    """
    system_prompt = get_oracle_system_prompt("imp")
    imp_user_prompt = get_imp_user_prompt(spec)
    oracle = Oracle(system_prompt)
    return oracle.complete([{"role": "user", "content": imp_user_prompt}])


def proof_oracle(spec: HoareTriple) -> list[dict]:
    """
    Oracle for the proof loop.
    """
    system_prompt = get_oracle_system_prompt("proof")
    # proof_user_prompt = get_proof_user_prompt(spec)
    _oracle = Oracle(system_prompt)
    # return oracle.complete([{"role": "user", "content": proof_user_prompt}])
    return []
