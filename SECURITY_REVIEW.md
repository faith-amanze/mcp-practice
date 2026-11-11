# MCP Server Security Review

Review of `server.py` (the practice MCP server). The server runs over stdio and exposes five tools and one resource.

## 1-4. Tool classification

| Tool | Risk level | Read-only or action | Requires approval |
|---|---|---|---|
| `add_numbers` | Low | Read-only | No |
| `multiply_numbers` | Low | Read-only | No |
| `estimate_study_time` | Low | Read-only | No |
| `explain_topic` | Low | Read-only | No |
| `generate_revision_checklist` | Low | Read-only | No |
| `project://status` (resource) | Low | Read-only | No |

**Read-only tools:** all of them. Each takes input, computes a result, and returns it without changing anything.

**Action tools:** none. No tool writes files, sends messages, uses the network, or changes anything outside the process, so none requires approval.

**Watch point:** `estimate_study_time`, `explain_topic`, and `generate_revision_checklist` echo the `topic` text back in their output. If a topic ever came from untrusted content (such as a web page), that text would flow back into the model's context. The risk is low here, but it is why `explain_topic` limits topic length.

## 5. Validation added (`explain_topic`)

Before doing any work, the tool checks that:

- the topic is not empty,
- the topic is at most 100 characters,
- the audience is `beginner`, `intermediate`, or `advanced` (case and extra spaces are ignored).

Anything else returns a friendly error, for example:

```
'wizard' isn't a valid audience. Please use one of: beginner, intermediate, advanced.
```

## 6. Structured error response (`generate_revision_checklist`)

An empty topic returns an error with a machine-readable code, a human-readable message, and a hint:

```json
{
  "ok": false,
  "error": {
    "code": "EMPTY_TOPIC",
    "message": "No topic was provided.",
    "hint": "Pass a topic such as 'FastAPI' or 'Python basics'."
  }
}
```

A program can check `error.code` reliably, which is much harder with free-text errors.

## 7. Remote transport security rule

**Any MCP server reachable over a network must require authentication and use HTTPS (TLS). Never expose an unauthenticated server on a public address.**

This server uses stdio, so only the program that launches it can talk to it, and the rule does not apply yet. It starts to matter as soon as the server is served over HTTP.

## 8. A tool that should not be allowed in a beginner MCP server

**`run_shell_command(command: str)`**, which runs any command on the machine.

Safe and unsafe input cannot be told apart, because any command could be harmful. A single mistaken or manipulated call (for example, a prompt injection hidden in text the model read) could delete files or leak data. Beginner servers should stick to narrow tools that do one specific thing with validated inputs.
