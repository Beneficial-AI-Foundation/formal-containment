"""Imp expert."""

from containment.mcp.clients.basic import MCPClient
from containment.structures import (
    HoareTriple,
    Polarity,
    ExpertMetadata,
    Specification,
    ImpFailure,
    Failure,
)
from containment.fsio.logs import logs
from containment.fsio.prompts import expert_system_prompt
from containment.parsing.regex import parse_program_completion


class ImpExpert(MCPClient):
    def __init__(
        self,
        model: str,
        spec: Specification,
        failed_attempts: list[Failure] | None = None,
    ) -> None:
        super().__init__()
        self.model = model
        self.spec = spec
        if failed_attempts is None:
            self.failed_attempts = []
        else:
            self.failed_attempts = failed_attempts
        self.system_prompt = expert_system_prompt("imp")
        self.complete = self._mk_complete(self.model, self.system_prompt)
        self.triple = None
        self.failure = None

    @classmethod
    async def connect_and_run(
        cls,
        model: str,
        spec: Specification,
        failed_attempts: list[Failure] | None = None,
    ) -> "ImpExpert":
        """
        Async instantiation: connect to the MCP server.

        Invariant: exactly one of `triple`, `failure` is None
        """
        mcp_client = cls(model, spec, failed_attempts)
        result = await mcp_client._connect_to_server_and_run()
        match result:
            case HoareTriple():
                mcp_client.triple = result
            case ImpFailure():
                mcp_client.failure = result
        return mcp_client

    async def _complete_triple(self) -> HoareTriple | ImpFailure:
        failed_attempts = (
            "\n".join(
                f"<failed_attempt>{failed_attempt.failure_str}</failed_attempt>"
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
                    "content": [
                        message.content.model_dump() for message in user_prompt.messages
                    ],
                }
            ]
        )
        message_content = completion["choices"][0].message.content
        program = parse_program_completion(message_content, "imp")
        if program is None:
            msg = f"{self.spec.name},{self.model}: No program found. XML parse error, probably"
            logs.info(msg)
            return ImpFailure(
                specification=self.spec,
                attempted_completion=message_content,
                failed_attempts=self.failed_attempts,
                metadata=ExpertMetadata(model=self.model, polarity=Polarity.POS),
                error_message=msg,
            )
        triple = HoareTriple(specification=self.spec, command=program)
        triple.add_tokens_spent_on_command(completion["usage"]["total_tokens"])
        return triple

    async def run(self) -> HoareTriple | ImpFailure:
        """
        Run the functionality of client.
        """
        return await self._complete_triple()
