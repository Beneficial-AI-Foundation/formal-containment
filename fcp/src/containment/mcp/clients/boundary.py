"""The boundary of the box."""

from containment.structures import Specification
from containment.mcp.clients.basic import MCPClient


class Boundary(MCPClient):
    def __init__(self, specification: Specification) -> None:
        super().__init__()
        self.specification = specification
