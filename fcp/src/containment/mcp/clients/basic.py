from typing import Any, Callable
from abc import abstractmethod
from mcp import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client
from containment.oracles import mk_complete
from containment.structures.mcp import MCPClientBase


class MCPClient(MCPClientBase):
    """Subclasses are MCP clients connected to the server defined in `..server`"""

    SERVER_PARAMETERS = StdioServerParameters(
        command="uv",
        args=["run", "mcp-server"],
        env=None,  # Optional environment variables
    )

    def _mk_complete(self, system_prompt: str) -> Callable[[list[dict]], list[dict]]:
        return mk_complete(self.client, system_prompt, cache=False)

    async def _connect_to_server_and_run(self):
        async with stdio_client(self.SERVER_PARAMETERS) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()

                response = await session.list_tools()
                self.available_tools = response.tools

                response = await session.list_resource_templates()
                self.available_resources = response.resourceTemplates

                response = await session.list_prompts()
                self.available_prompts = response.prompts

                self.session = session
                return await self.run()

    @abstractmethod
    async def run(self) -> Any:
        """
        Run the client's functionality.
        """
