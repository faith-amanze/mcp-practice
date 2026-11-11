# mcp-practice

A practice project for learning the Model Context Protocol (MCP): building a small server with tools and a resource, testing it with a client, and putting a validation layer between an "agent" and the tools it calls.

## What's inside

| File | Purpose |
|---|---|
| `server.py` | The MCP server: five tools and one resource |
| `client.py` | Basic client that lists and calls the tools and reads the resource |
| `client_test.py` | Tests the server directly, with no AI model involved |
| `agent_client.py` | Agent loop: decide, then validate, then execute |
| `SECURITY_REVIEW.md` | Risk classification and safety notes for the tools |
| `NOTES.md` | Why a model should not execute tools directly |

## Tools and resource

| Name | Type | What it does |
|---|---|---|
| `add_numbers` | Tool | Adds two integers |
| `multiply_numbers` | Tool | Multiplies two integers |
| `estimate_study_time` | Tool | Estimates study hours for a topic (`easy`, `medium`, or `hard`) |
| `explain_topic` | Tool | Explains a topic for a `beginner`, `intermediate`, or `advanced` audience |
| `generate_revision_checklist` | Tool | Builds a revision checklist for a topic |
| `project://status` | Resource | Returns a short project status message |

All tools are read-only: they compute a result and return it without changing anything.

## Setup

Requires Python 3.10 or newer.

```bash
python -m venv venv
```

Activate the virtual environment:

- Windows (PowerShell): `venv\Scripts\Activate.ps1`
- macOS / Linux: `source venv/bin/activate`

Then install the dependency:

```bash
pip install -r requirements.txt
```

The version is pinned to `mcp<2` because MCP 2.x renamed `FastMCP`, which this code uses.

## Run it

The clients start the server themselves over stdio, so you don't need to run `server.py` separately.

```bash
python client.py          # tools and resource demo
python client_test.py     # direct test, no AI model
python agent_client.py    # agent loop with validation
```

Try different requests and failure cases with the agent:

```bash
python agent_client.py "Make a revision checklist for FastAPI"
python agent_client.py --bad-tool      # forces an unknown tool name; validation rejects it
python agent_client.py --no-topic      # removes a required argument; validation rejects it
```

## How the agent works

1. **Decide:** something proposes a tool call, such as `{"tool": "explain_topic", "arguments": {"topic": "MCP"}}`. By default a simple keyword router does this, so no API key is needed.
2. **Validate:** the code checks that the tool exists and that the arguments match its schema.
3. **Execute:** only a validated call is run.

To use Claude as the decision maker instead, set an `ANTHROPIC_API_KEY` environment variable. This path is optional and billed separately through the Anthropic API.

## Safety

See [SECURITY_REVIEW.md](SECURITY_REVIEW.md) for the risk classification of each tool, the validation and structured-error examples, and notes on remote transport security.
