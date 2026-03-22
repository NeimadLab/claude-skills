---
name: loom
description: "Persistent AI workspace memory — search decisions, log context, track sessions, manage handoffs, and maintain project continuity across AI tools. Activate when the user mentions project memory, decisions, handoff, context transfer, workspace state, sessions, or Loom."
version: 0.4.0
---

# Loom — Persistent AI Workspace Memory

## Trigger

Activate when the user:
- Asks to remember, log, or record a decision, goal, risk, or observation
- Asks about previous decisions, project context, or "what did we decide about X?"
- Mentions "handoff", "continue where we left off", "pick up from last time"
- Asks to search project memory or workspace history
- Mentions "Loom", "workspace memory", or "project brain"
- Starts a new session and needs to be onboarded on prior context
- Asks to check workspace health, state, or runtime identity
- Asks about session history or who worked on what

## How Loom Works

Loom is an MCP server that gives you persistent, structured project memory. Every decision, goal, risk, and observation is stored in a local SQLite database with full-text search. The memory survives across sessions, across tools (Claude Code, Cursor, Windsurf), and across models.

You have 8 MCP tools available. Use them proactively — don't wait for the user to ask.

## Session Start Protocol

**At the start of every session**, before doing any work:

1. Call `loom_open_session` with your actor name and model
2. Call `loom_get_handoff_summary` to load context from previous sessions
3. Read the summary — it contains: current goals, recent decisions, open risks
4. Acknowledge what you've learned: *"I see from previous work that we decided to use JWT for auth, and token revocation is still an open risk."*

**At the end of every session:**

1. Call `loom_close_session` with a brief summary of what was accomplished
2. This creates a clean handoff point for the next session

## Tool Reference

### loom_open_session

Open a session to track which AI tool is working. Call at the start of every interaction.

```json
{ "actor": "claude-code", "model_name": "claude-opus-4" }
```

### loom_close_session

Close the current session when finishing work.

```json
{ "summary": "Set up backend architecture: FastAPI + PostgreSQL + JWT auth" }
```

### loom_search_memory

Search project memory before making decisions or answering questions about prior work.

```json
{ "query": "authentication", "type": "decision", "limit": 5 }
```

Parameters:
- `query` (required): full-text search query
- `type` (optional): `decision`, `goal`, `risk`, `note`, `observation`, `artifact`
- `status` (optional): `hypothesis`, `validated`, `obsolete`, `rejected`
- `limit` (optional): max results, default 10

**When to use:** Before making any decision, search first. Avoid contradicting prior decisions.

### loom_log_decision

Record architectural or technical decisions with rationale.

```json
{
  "decision": "Use PostgreSQL instead of MongoDB",
  "rationale": "Need ACID transactions for payment processing.",
  "tags": ["database", "payments"]
}
```

**When to use:** Every time the user makes or confirms a technical choice. Always include the rationale.

### loom_write_memory

Store any structured memory entry — goals, risks, observations, notes, artifacts.

```json
{ "content": "Token revocation not yet implemented", "type": "risk", "tags": ["auth"] }
```

Types: `decision` (use log_decision instead), `goal`, `risk`, `note`, `observation`, `artifact`

### loom_get_handoff_summary

Generate a structured transfer packet for session onboarding.

```json
{ "depth": "compact" }
```

Returns: current goals, recent decisions (with status), open risks, total memory count.

**When to use:** At the start of every session. Also when the user asks "what's the current state?"

### loom_get_context

Get a compact project overview: type, stack, identity, goals, decisions, risks.

```json
{}
```

### loom_get_state

Get workspace operational state: file counts, runtime identity, event log size, git status.

```json
{}
```

## Memory Status Model

| Status | Meaning | Your Behavior |
|--------|---------|--------------|
| `hypothesis` | AI-written, not confirmed | Treat as suggestion. Flag uncertainty. |
| `validated` | Human-confirmed | Treat as established fact. |
| `obsolete` | Superseded | Mention only for historical context. |
| `rejected` | Determined wrong | Do not follow. |

All entries you create start as `hypothesis`. Only humans promote to `validated`.

## Best Practices

### DO
- Call `loom_open_session` at start, `loom_close_session` at end
- Call `loom_get_handoff_summary` before starting work
- Search memory before making decisions
- Log every architectural decision with rationale
- Log risks as you discover them
- Include `tags` and `linked_files` when relevant
- Reference prior decisions: *"Based on our decision to use JWT (validated)..."*

### DON'T
- Don't skip the session protocol
- Don't create duplicate decisions — search first
- Don't treat `hypothesis` entries as confirmed facts
- Don't ignore open risks
- Don't log trivial information
- Don't overwrite validated decisions without discussing with the user

## Installation

```bash
pip install loom        # or: pip install -e . from source
cd my-project
loom init               # creates .loom/ with memory database
loom connect claude-code  # configures MCP for this tool
```

For remote access: `loom gateway start --port 8443`

See `skills/loom/docs/getting-started.md` for full setup instructions.
