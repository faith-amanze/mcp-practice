"""Agent client: the model DECIDES, our code VALIDATES, then our code EXECUTES.

Usage:
    python agent_client.py                      # uses USER_REQUEST below
    python agent_client.py "Explain MCP to a beginner"
    python agent_client.py --bad-tool           # force an unknown tool name
    python agent_client.py --no-topic           # remove the topic argument

If ANTHROPIC_API_KEY is set, Claude makes the decision. Otherwise a simple
keyword router stands in for the model so the practice works offline.
"""
import asyncio
import json
import os
import re
import sys

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Steps 3 and 5: change this line (or pass the request on the command line).
USER_REQUEST = "Explain MCP to a beginner"


# ---------- 1. DECIDE ----------
def decide_with_rules(request: str) -> dict:
    """Stand-in for the model: returns a decision dictionary."""
    text = request.strip()
    lower = text.lower()

    if "checklist" in lower or "revision" in lower or "revise" in lower:
        match = re.search(r"\bfor\s+(.+)$", text, re.IGNORECASE)
        topic = match.group(1).strip(" .?!") if match else text
        return {"tool": "generate_revision_checklist", "arguments": {"topic": topic}}

    match = re.search(r"explain\s+(.+?)(?:\s+to\s+(?:(?:an|a|the)\s+)?(.+))?$", text, re.IGNORECASE)
    topic = match.group(1).strip(" .?!") if match else text
    audience = (match.group(2) or "beginner").strip(" .?!") if match else "beginner"
    return {"tool": "explain_topic", "arguments": {"topic": topic, "audience": audience}}


def decide_with_model(request: str, tools) -> dict:
    """Ask Claude to pick a tool. Returns the decision dictionary."""
    import httpx

    tool_text = json.dumps(
        [{"name": t.name, "description": t.description, "input_schema": t.inputSchema} for t in tools],
        indent=2,
    )
    prompt = (
        "Choose ONE tool for the user's request. Reply with JSON only, shaped like "
        '{"tool": "<name>", "arguments": {...}}.\n\n'
        f"Tools:\n{tool_text}\n\nUser request: {request}"
    )
    response = httpx.post(
        "https://api.anthropic.com/v1/messages",
        headers={
            "x-api-key": os.environ["ANTHROPIC_API_KEY"],
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        },
        json={
            "model": "claude-sonnet-5-5",
            "max_tokens": 300,
            "messages": [{"role": "user", "content": prompt}],
        },
        timeout=30,
    )
    response.raise_for_status()
    text = response.json()["content"][0]["text"]
    text = re.sub(r"^```(?:json)?|```$", "", text.strip(), flags=re.MULTILINE).strip()
    return json.loads(text)


# ---------- 2. VALIDATE ----------
def validate_decision(decision: dict, tools) -> None:
    """Raise ValueError if the decision is not safe to execute."""
    if not isinstance(decision, dict):
        raise ValueError("Decision must be a dictionary.")

    name = decision.get("tool")
    arguments = decision.get("arguments")

    by_name = {t.name: t for t in tools}
    if name not in by_name:
        raise ValueError(f"Unknown tool {name!r}. Allowed tools: {sorted(by_name)}")

    if not isinstance(arguments, dict):
        raise ValueError("'arguments' must be a dictionary.")

    schema = by_name[name].inputSchema
    properties = schema.get("properties", {})
    required = schema.get("required", [])

    missing = [key for key in required if key not in arguments]
    if missing:
        raise ValueError(f"Missing required argument(s) for {name}: {missing}")

    unexpected = [key for key in arguments if key not in properties]
    if unexpected:
        raise ValueError(f"Unexpected argument(s) for {name}: {unexpected}")

    for key, value in arguments.items():
        if properties[key].get("type") == "string" and not isinstance(value, str):
            raise ValueError(f"Argument {key!r} must be a string.")


# ---------- 3. EXECUTE ----------
async def main():
    args = sys.argv[1:]
    flags = {a for a in args if a.startswith("--")}
    request = " ".join(a for a in args if not a.startswith("--")) or USER_REQUEST

    params = StdioServerParameters(command=sys.executable, args=["server.py"])
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = (await session.list_tools()).tools

            print("User request:", request)

            if os.getenv("ANTHROPIC_API_KEY"):
                print("Decision maker: Claude")
                decision = decide_with_model(request, tools)
            else:
                print("Decision maker: keyword router (no ANTHROPIC_API_KEY set)")
                decision = decide_with_rules(request)

            # Steps 7 and 8: tamper with the decision to test validation.
            if "--bad-tool" in flags:
                decision["tool"] = "delete_everything"
            if "--no-topic" in flags:
                decision["arguments"].pop("topic", None)

            print("Decision:", json.dumps(decision))

            try:
                validate_decision(decision, tools)
            except ValueError as error:
                print("REJECTED by validation:", error)
                return

            print("Validation passed. Chosen tool:", decision["tool"])
            result = await session.call_tool(decision["tool"], decision["arguments"])
            print("Result:", json.dumps(result.structuredContent, indent=2))


asyncio.run(main())
