from typing import Callable
from mcp import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client
from containment.oracles import get_oracle_client, mk_complete


class MCPClient:
    SERVER_PARAMETERS = StdioServerParameters(
        command="uv",
        args=["run mcp-server"],
        env=None,  # Optional environment variables
    )

    async def __init__(self) -> None:
        self.conversation = []
        self.client = get_oracle_client()
        await self.connect_to_server()

    def mk_complete(self, system_prompt: str) -> Callable[[list[dict]], list[dict]]:
        return mk_complete(self.client, system_prompt, cache=False)

    async def connect_to_server(self):
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
