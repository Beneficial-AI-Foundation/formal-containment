"""Imp expert."""

from containment.mcp.clients.basic import MCPClient
from containment.structures import (
    HoareTriple,
    Specification,
)
from containment.io.prompts import oracle_system_prompt
from containment.oracles import parse_program_completion


class ImpExpert(MCPClient):
    def __init__(
        self, spec: Specification, failed_attempts: list[str] | None = None
    ) -> None:
        super().__init__()
        self.spec = spec
        if failed_attempts is None:
            self.failed_attempts = []
        else:
            self.failed_attempts = failed_attempts
        self.system_prompt = oracle_system_prompt("imp")
        self.complete = self._mk_complete(self.system_prompt)
        self.triple = None

    @classmethod
    async def connect_and_run(
        cls, spec: Specification, failed_attempts: list[str] | None = None
    ) -> "ImpExpert":
        """
        Async instantiation: connect to the MCP server.
        """
        mcp_client = cls(spec, failed_attempts)
        mcp_client.triple = await mcp_client._connect_to_server_and_run()
        return mcp_client

    async def _complete_triple(self) -> HoareTriple:
        failed_attempts = (
            "\n".join(
                f"<failed_attempt>{failed_attempt}</failed_attempt>"
                for failed_attempt in self.failed_attempts
            )
            if self.failed_attempts is not None
            else ""
        )
        prompt_arguments = {
            "precondition": self.spec.precondition,
            "postcondition": self.spec.postcondition,
            "metavariables": self.spec.metavariables,
            "failed_attempts": failed_attempts,
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
        program = parse_program_completion(completion, "imp")
        if program is None:
            raise ValueError("No program found. XML parse error probably")
        return HoareTriple(specification=self.spec, command=program)

    async def run(self) -> HoareTriple:
        """
        Run the functionality of client.
        """
        return await self._complete_triple()
