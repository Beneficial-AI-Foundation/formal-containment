from containment.oracles import get_oracle_client


class MCPClientBase:
    """
    Base class for the Model Context Protocol (MCP) client.
    """

    def __init__(self) -> None:
        self.conversation = []
        self.client = get_oracle_client()
