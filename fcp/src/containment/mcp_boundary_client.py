"""The boundary of the box"""

from mcp.client.stdio import StdioServerParameters, stdio_client

server_parameters = StdioServerParameters(
    command="uv",
    args=["run mcp-server"],
    env=None,  # Optional environment variables
)

__all__ = ["stdio_client"]
