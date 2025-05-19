"""Imp expert."""

from containment.mcp.clients.basic import MCPClient
from containment.structures import (
    HoareTriple,
    Specification,
)
from containment.prompts import oracle_system_prompt
from containment.oracles import parse_program_completion


class ImpExpert(MCPClient):
    def __init__(self, spec: Specification) -> None:
        super().__init__()
        self.spec = spec
        self.system_prompt = oracle_system_prompt("imp")
        self.complete = self._mk_complete(self.system_prompt)
        self.triple = None

    @classmethod
    async def connect_and_run(cls, spec: Specification) -> "ImpExpert":
        """
        Async instantiation: connect to the MCP server.
        """
        mcp_client = cls(spec)
        mcp_client.triple = await mcp_client._connect_to_server_and_run()
        return mcp_client

    async def _complete_triple(self) -> HoareTriple:
        prompt_arguments = {
            "precondition": self.spec.precondition,
            "postcondition": self.spec.postcondition,
        }
        user_prompt = await self.session.get_prompt(
            "imp_user_prompt", arguments=prompt_arguments
        )
        completion = self.complete(
            [
                {
                    "role": "user",
                    "content": [message.content for message in user_prompt.messages],
                }
            ]
        )
        # completion = self.complete(user_prompt)
        program = parse_program_completion(completion, "imp")
        if program is None:
            raise ValueError("No program found. XML parse error probably")
        return HoareTriple(specification=self.spec, command=program)

    async def run(self) -> HoareTriple:
        """
        Run the functionality of client.
        """
        return await self._complete_triple()
