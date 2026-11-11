from typing import Any

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("practice")

# Safety review: every tool below is pure computation. None reads files, writes
# files, uses the network, or changes anything outside this process.
# Each tool is marked: risk level | read-only or action | approval needed.


def error_response(code: str, message: str, hint: str | None = None) -> dict[str, Any]:
    """Structured error: a machine-readable code, a human message, an optional hint."""
    error: dict[str, Any] = {"code": code, "message": message}
    if hint:
        error["hint"] = hint
    return {"ok": False, "error": error}


# risk: low | read-only | approval: no
@mcp.tool()
def add_numbers(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b


# risk: low | read-only | approval: no
@mcp.tool()
def multiply_numbers(a: int, b: int) -> int:
    """Multiply two numbers."""
    return a * b


# Practice 2: study time estimator
STUDY_HOURS = {"easy": 2, "medium": 5, "hard": 10}


# risk: low | read-only | approval: no
@mcp.tool()
def estimate_study_time(topic: str, difficulty: str) -> dict[str, Any]:
    """Estimate study hours for a topic. Difficulty must be easy, medium, or hard."""
    level = difficulty.strip().lower()

    if level not in STUDY_HOURS:
        return {
            "ok": False,
            "error": (
                f"'{difficulty}' isn't a valid difficulty. "
                "Please use one of: easy, medium, hard."
            ),
        }

    hours = STUDY_HOURS[level]
    return {
        "ok": True,
        "topic": topic,
        "difficulty": level,
        "estimated_hours": hours,
        "message": f"Plan about {hours} hours to study {topic} at {level} level.",
    }


# Practice 3: tools the agent can choose between
EXPLANATIONS = {
    "mcp": (
        "MCP (Model Context Protocol) is a standard way for AI apps to connect "
        "to tools and data. Think of it like USB for AI: one plug shape, many "
        "devices. A server offers tools and resources, and a client discovers "
        "and uses them."
    ),
    "fastapi": (
        "FastAPI is a Python framework for building web APIs quickly. You write "
        "normal Python functions, add type hints, and FastAPI handles "
        "validation, docs, and JSON for you."
    ),
}

# Practice 4, task 5: validation rules for explain_topic
ALLOWED_AUDIENCES = ("beginner", "intermediate", "advanced")
MAX_TOPIC_LENGTH = 100


# risk: low | read-only | approval: no
@mcp.tool()
def explain_topic(topic: str, audience: str = "beginner") -> dict[str, Any]:
    """Explain a topic in plain language. Audience: beginner, intermediate, or advanced."""
    # Validation 1: topic must not be empty
    if not topic.strip():
        return {"ok": False, "error": "Please tell me which topic to explain."}

    # Validation 2: topic must not be absurdly long
    if len(topic) > MAX_TOPIC_LENGTH:
        return {
            "ok": False,
            "error": f"That topic is too long. Please keep it under {MAX_TOPIC_LENGTH} characters.",
        }

    # Validation 3: audience must be one of the allowed values
    level = audience.strip().lower()
    if level not in ALLOWED_AUDIENCES:
        return {
            "ok": False,
            "error": (
                f"'{audience}' isn't a valid audience. "
                f"Please use one of: {', '.join(ALLOWED_AUDIENCES)}."
            ),
        }

    explanation = EXPLANATIONS.get(
        topic.strip().lower(),
        f"{topic} is best learned step by step: start with the problem it "
        "solves, learn its core terms, then try one small example.",
    )
    return {"ok": True, "topic": topic, "audience": level, "explanation": explanation}


# risk: low | read-only | approval: no
@mcp.tool()
def generate_revision_checklist(topic: str) -> dict[str, Any]:
    """Create a revision checklist for a topic."""
    # Practice 4, task 6: structured error response
    if not topic.strip():
        return error_response(
            code="EMPTY_TOPIC",
            message="No topic was provided.",
            hint="Pass a topic such as 'FastAPI' or 'Python basics'.",
        )

    return {
        "ok": True,
        "topic": topic,
        "checklist": [
            f"Explain what {topic} is and the problem it solves in one sentence.",
            f"List the core concepts and key terms of {topic}.",
            f"Build or run one small working example of {topic}.",
            f"Write down 3 common mistakes with {topic} and how to avoid them.",
            f"Answer practice questions on {topic} without looking at notes.",
            f"Teach {topic} to someone else, or write a short summary.",
        ],
    }


# risk: low | read-only | approval: no
@mcp.resource("project://status")
def project_status() -> str:
    """Current project status."""
    return "Project status: on track"


if __name__ == "__main__":
    mcp.run()
