import asyncio
import sys

from pydantic import AnyUrl
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def main():
    params = StdioServerParameters(command=sys.executable, args=["server.py"])
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            # Step 2: confirm add_numbers is listed
            tools = await session.list_tools()
            names = [t.name for t in tools.tools]
            print("Tools:", names)
            assert "add_numbers" in names

            # Step 3: arguments changed to a=10, b=7
            add = await session.call_tool("add_numbers", {"a": 10, "b": 7})
            print("add_numbers:", add.content[0].text)  # 17

            # Step 4: call the new tool
            mul = await session.call_tool("multiply_numbers", {"a": 10, "b": 7})
            print("multiply_numbers:", mul.content[0].text)  # 70

            # Practice 2: test estimate_study_time
            for topic, level in [("Python basics", "easy"),
                                 ("Calculus", "HARD"),
                                 ("Statistics", "impossible")]:
                res = await session.call_tool(
                    "estimate_study_time", {"topic": topic, "difficulty": level}
                )
                print(f"estimate_study_time({topic!r}, {level!r}):", res.structuredContent)

            # Step 5: list and read the resource
            resources = await session.list_resources()
            print("Resources:", [str(r.uri) for r in resources.resources])
            status = await session.read_resource(AnyUrl("project://status"))
            print("Status:", status.contents[0].text)


asyncio.run(main())
