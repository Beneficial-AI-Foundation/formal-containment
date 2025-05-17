"""The boundary of the box."""

from containment.structures import Specification
from containment.mcp.clients.basic import MCPClient
from containment.mcp.clients.completion import ImpExpert, ProofExpert


class Boundary(MCPClient):
    async def __init__(self, precondition: str, postcondition: str) -> None:
        await super().__init__()
        self.precondition = precondition
        self.postcondition = postcondition

        self.specification = Specification(
            precondition=precondition, postcondition=postcondition
        )
