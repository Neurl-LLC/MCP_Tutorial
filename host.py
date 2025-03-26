import asyncio
import sys
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from anthropic import Anthropic

anthropic = Anthropic()


async def list_available_tools(session):
    """Retrieve and format the list of available tools."""
    try:
        tool_list = await session.list_tools()
        return [{
            "name": tool.name,
            "description": tool.description,
            "input_schema": tool.inputSchema
        } for tool in tool_list.tools]
    except Exception as e:
        print(f"Error fetching tool list: {e}")
        return []


async def get_claude_response(messages, tools):
    """Fetch a response from Claude AI."""
    try:
        return anthropic.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1000,
            messages=messages,
            tools=tools
        )
    except Exception as e:
        print(f"Error fetching Claude response: {e}")
        return None


async def handle_tool_use(session, content):
    """Execute a tool call and return the result."""
    try:
        result = await session.call_tool(content.name, content.input)
        return {
            "tool_use_id": content.id,
            "content": result.content[0].text if result.content else "No response from tool."
        }
    except Exception as e:
        print(f"Error executing tool {content.name}: {e}")
        return {"tool_use_id": content.id, "content": "Error executing tool."}


async def chat(session):
    """Run the interactive chat loop."""
    messages = []
    tools = await list_available_tools(session)

    while True:
        user_input = input("\nProvide your prompt (or type 'exit' to quit): ").strip()
        if user_input.lower() == "exit":
            print("Exiting chat.")
            break

        messages.append({"role": "user", "content": user_input})

        response = await get_claude_response(messages, tools)
        if not response or not response.content:
            print("Error: No response from Claude.")
            continue

        final_text = []
        assistant_message_content = []

        for content in response.content:
            if content.type == "text":
                final_text.append(content.text)
                assistant_message_content.append(content)
            elif content.type == "tool_use":
                tool_result = await handle_tool_use(session, content)
                assistant_message_content.append(content)
                messages.append({"role": "assistant", "content": assistant_message_content})
                messages.append({"role": "user", "content": [{"type": "tool_result", **tool_result}]})

                # Get new response from Claude after tool execution
                response = await get_claude_response(messages, tools)
                if response and response.content:
                    messages.append({"role": "assistant", "content": response.content[0].text})
                    final_text.append(response.content[0].text)

        print("\nAssistant:", "\n".join(final_text))


async def run(server_params):
    """Establish connection and start the host session."""
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            await chat(session)


async def main():
    """Parse command-line arguments and start the server connection."""
    if len(sys.argv) < 2:
        print("Usage: python client.py <server_command> [args...]")
        sys.exit(1)

    server_params = StdioServerParameters(
        command=sys.argv[1],
        args=sys.argv[2:]
    )

    await run(server_params)



if __name__ == "__main__":
    asyncio.run(main())