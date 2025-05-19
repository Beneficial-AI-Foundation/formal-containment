"""The boundary of the box."""

from typing import Any
from containment.structures import Specification
from containment.mcp.clients.basic import MCPClient


class Boundary(MCPClient):
    def __init__(self, specification: Specification) -> None:
        super().__init__()
        self.specification = specification

    def run(self) -> Any:
        """
        Run the boundary of the box.
        """
        raise NotImplementedError("TODO")
