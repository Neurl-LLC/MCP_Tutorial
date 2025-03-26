from mcp.server.fastmcp import FastMCP
from datetime import datetime
from zoneinfo import ZoneInfo

# Create an MCP server
mcp = FastMCP("Tutorial")

@mcp.tool()
def get_time_in_timezone(timezone: str) -> str:
    """
    Given a timezone this tool returns the current time in that time zone
    """
    try:
        tz = ZoneInfo(timezone)
        current_time = datetime.now(tz)
        return current_time.strftime("%Y-%m-%d %H:%M:%S %Z%z")
    except ValueError:
        return "Invalid time zone. Please provide a valid time zone name."

@mcp.resource("info://resource")
def get_resource():
    """ Get a resource from the Server"""
    return f"This is a sample resource from the MCP Server"

@mcp.prompt()
def refactor_prompt(code: str) -> str:
    """Prompt to refactor code"""
    return f"Refactor this code: {code}"


if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport='stdio')