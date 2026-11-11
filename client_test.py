"""Direct MCP client test. No AI model involved."""
import asyncio
import sys

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def main():
    params = StdioServerParameters(command=sys.executable, args=["server.py"])
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            tools = await session.list_tools()
            names = [t.name for t in tools.tools]
            print("Tools:", names)
            assert "explain_topic" in names
            assert "generate_revision_checklist" in names

            explained = await session.call_tool(
                "explain_topic", {"topic": "MCP", "audience": "beginner"}
            )
            print("\nexplain_topic:", explained.structuredContent)
            assert explained.structuredContent["ok"] is True

            checklist = await session.call_tool(
                "generate_revision_checklist", {"topic": "FastAPI"}
            )
            print("\ngenerate_revision_checklist:", checklist.structuredContent)
            assert checklist.structuredContent["ok"] is True

            # Safety review checks: validation and structured errors
            bad_audience = await session.call_tool(
                "explain_topic", {"topic": "MCP", "audience": "wizard"}
            )
            print("\nexplain_topic (bad audience):", bad_audience.structuredContent)
            assert bad_audience.structuredContent["ok"] is False

            too_long = await session.call_tool(
                "explain_topic", {"topic": "x" * 101, "audience": "beginner"}
            )
            print("\nexplain_topic (topic too long):", too_long.structuredContent)
            assert too_long.structuredContent["ok"] is False

            empty = await session.call_tool("generate_revision_checklist", {"topic": "   "})
            print("\ngenerate_revision_checklist (empty topic):", empty.structuredContent)
            assert empty.structuredContent["error"]["code"] == "EMPTY_TOPIC"

            print("\nServer works without the AI model.")


asyncio.run(main())
