from containment.oracles import get_oracle_client


class MCPClientBase:
    """
    Base class for the Model Context Protocol (MCP) client.
    """

    conversation = []
    client = get_oracle_client()
