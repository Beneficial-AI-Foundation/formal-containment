"""The boundary of the box."""

from containment.structures import Specification
from containment.mcp.clients.basic import MCPClient
from containment.mcp.clients.completion import ImpExpert, ProofExpert


class Boundary(MCPClient):
    def __init__(self, specification: Specification) -> None:
        super().__init__()
        self.specification = specification
        self.imp_expert = ImpExpert(specification)
