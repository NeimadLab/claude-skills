---
name: loom
description: "Persistent AI workspace memory — search decisions, log context, generate handoff summaries, and maintain project continuity across sessions and models. Activate when the user mentions project memory, decisions, handoff, context transfer, workspace state, or Loom."
version: 0.1.0
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

## How Loom Works

Loom is an MCP server that gives you persistent, structured project memory. Every decision, goal, risk, and observation is stored in a local SQLite database with full-text search. The memory survives across sessions, across tools (Claude Code, Cursor, Windsurf), and across models.

You have 6 MCP tools available. Use them proactively — don't wait for the user to ask.

## Session Start Protocol

**At the start of every session**, before doing any work:

1. Call `loom_get_handoff_summary` to load context from previous sessions
2. Read the summary — it contains: current goals, recent decisions, open risks, and recommended next actions
3. Acknowledge what you've learned: *"I see we decided to use JWT for auth, and token revocation is still an open risk. Let me continue from there."*

This is the most important habit. It's what makes cross-session and cross-model continuity work.

## Tool Reference

### loom_search_memory

Search project memory before making decisions or answering questions about prior work.

```json
{ "query": "authentication", "type": "decision", "limit": 5 }
```

Parameters:
- `query` (required): full-text search query
- `type` (optional): filter by `decision`, `goal`, `risk`, `note`, `observation`, `artifact`
- `status` (optional): filter by `hypothesis`, `validated`, `obsolete`, `rejected`
- `limit` (optional): max results, default 10

**When to use:** Before making any decision, search first. Avoid contradicting prior decisions. If a related decision exists, reference it.

### loom_log_decision

Record architectural or technical decisions with rationale. This is the most valuable tool — decisions with rationale are what make handoff work.

```json
{
  "decision": "Use PostgreSQL instead of MongoDB",
  "rationale": "Need ACID transactions for payment processing. JSON support covers our document needs.",
  "tags": ["database", "payments"],
  "linked_files": ["src/db/connection.py"]
}
```

**When to use:** Every time the user makes or confirms a technical choice. Always include the rationale — it's the most valuable part.

### loom_write_memory

Store any structured memory entry — goals, risks, observations, notes, artifacts.

```json
{
  "content": "Token revocation not yet implemented",
  "type": "risk",
  "tags": ["auth", "security"]
}
```

Types:
- `decision` — use `loom_log_decision` instead (includes rationale)
- `goal` — current objectives ("Complete auth migration by Friday")
- `risk` — known risks or tech debt ("No rate limiting on API")
- `note` — general observations ("The legacy endpoint uses XML")
- `observation` — patterns or conventions ("Team prefers explicit error types")
- `artifact` — references to deliverables ("API schema at docs/api.yaml")

**When to use:** Log goals at the start of work sessions. Log risks as you discover them. Log observations about project conventions as you learn them.

### loom_get_handoff_summary

Generate a structured transfer packet. The key tool for session onboarding.

```json
{ "depth": "compact" }
```

Returns: current goals, recent decisions (with status), open risks, total memory count, and recent activity.

**When to use:** At the start of every session. Also useful when the user asks "what's the current state?" or "summarize what we've done."

### loom_get_context

Get a compact project overview: type, stack, identity, goals, decisions, risks.

```json
{}
```

**When to use:** When you need quick orientation without the full handoff detail.

### loom_get_state

Get workspace operational state: file counts, runtime identity, event log size, git branch/status.

```json
{}
```

**When to use:** When the user asks about workspace health, or when you need to check if the environment has drifted.

## Memory Status Model

Entries have a trust status:

| Status | Meaning | Your Behavior |
|--------|---------|--------------|
| `hypothesis` | Initial AI-written entry | Treat as suggestion, not fact. Flag uncertainty. |
| `validated` | Human-confirmed | Treat as established fact. Reference with confidence. |
| `obsolete` | Superseded by newer entry | Mention only for historical context. |
| `rejected` | Determined to be wrong | Do not follow. Note if user asks about it. |

All entries you create start as `hypothesis`. Only humans can promote to `validated`.

## Best Practices

### DO
- Call `loom_get_handoff_summary` at the start of every session
- Search memory before making decisions (`loom_search_memory`)
- Log every architectural decision with rationale (`loom_log_decision`)
- Log risks as you discover them (`loom_write_memory` with type `risk`)
- Log goals at the start of work sessions
- Include `tags` and `linked_files` when relevant — they improve search
- Reference prior decisions in your responses: *"Based on our decision to use JWT (logged on March 22)..."*

### DON'T
- Don't create duplicate decisions — search first
- Don't treat `hypothesis` entries as confirmed facts
- Don't ignore open risks — mention them when relevant
- Don't log trivial information — memory should contain decisions, goals, risks, and conventions, not every line of code
- Don't overwrite or contradict validated decisions without discussing with the user first

## Installation

Loom runs as a local CLI + MCP server:

```bash
pip install loom    # or: pip install -e . from source
cd my-project
loom init           # creates .loom/ with memory database
loom connect claude-code  # configures MCP for this tool
```

See `skills/loom/docs/getting-started.md` for full setup instructions.
