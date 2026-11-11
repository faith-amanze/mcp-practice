# Why the model should not execute tools directly

The model only proposes a tool call; our code decides whether to run it.

- **Models make mistakes.** It can invent a tool name, drop a required argument,
  or pass the wrong type. Validation catches this before anything runs.
- **Tools have real effects.** A tool might send email, change files, or spend
  money. A wrong or manipulated call should never execute unchecked.
- **Prompt injection.** Text the model reads (a web page, a document) can try to
  trick it into calling tools. Our code is the safety layer that still says no.
- **Control and auditing.** When our code executes, we can log every call,
  enforce permissions, rate-limit, or ask the user for approval.
- **Predictability.** Keeping decide, validate, and execute as separate steps
  makes failures easy to find and fix.
