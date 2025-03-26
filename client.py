from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Create server parameters for stdio connection
server_params = StdioServerParameters(
    command="python",
    args=["server.py"],
)

async def run():
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize the connection
            await session.initialize()

            # List available prompts
            prompts = await session.list_prompts()
            print(prompts)
            
            # List available resources
            resources = await session.list_resources()
            print(resources)

            # List available tools
            tools = await session.list_tools()
            print(tools)

            # Get a prompt
            prompt = await session.get_prompt(
                "refactor_prompt", arguments={"code": "print('Hello World')"}
            )
            print(prompt)

            # Read a resource
            content = await session.read_resource("info://resource")
            print(content)

            # Call a tool
            result = await session.call_tool(
                "get_time_in_timezone", arguments={"timezone": "America/New_York"}
            )
            print(result)

if __name__ == "__main__":
    import asyncio

    asyncio.run(run())