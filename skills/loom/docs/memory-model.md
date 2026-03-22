# Memory Model

## Overview

Project memory stores structured knowledge that models can query to understand what happened before they arrived. It is the layer that makes cross-model handoff possible — without it, every new session starts from zero.

Memory is **consultative, never authoritative**. If memory contradicts the filesystem or Git, the filesystem and Git win. Memory accelerates understanding and provides context — it does not override canonical state.

## Storage Engine

- **Database:** SQLite embedded (`.loom/memory.db`), one per workspace
- **Search:** FTS5 full-text index on `content` and `tags` fields
- **Concurrency:** WAL mode for concurrent reads during writes
- **Optional (V0.4+):** sqlite-vss for vector similarity search, only if FTS5 proves insufficient

## Schema

```sql
CREATE TABLE memory (
  id             TEXT PRIMARY KEY,   -- ULID (sortable, unique)
  type           TEXT NOT NULL,      -- decision | artifact | goal | risk | note | observation
  status         TEXT NOT NULL,      -- hypothesis | validated | obsolete | rejected
  content        TEXT NOT NULL,      -- Free-text description
  rationale      TEXT,               -- Why this decision was made (decisions only)
  actor          TEXT,               -- Who created this entry (model name or user)
  session_id     TEXT,               -- Which session created this
  timestamp      TEXT NOT NULL,      -- ISO 8601
  linked_files   TEXT,               -- JSON array of file paths
  linked_commits TEXT,               -- JSON array of commit SHAs
  tags           TEXT,               -- JSON array of searchable tags
  created_at     TEXT NOT NULL,
  updated_at     TEXT NOT NULL
);

CREATE VIRTUAL TABLE memory_fts USING fts5(content, tags, content=memory);
```

## Record Types

| Type | Purpose | Example |
|------|---------|---------|
| `decision` | Architectural or technical choice | "Use JWT instead of session cookies for auth" |
| `artifact` | Reference to a deliverable | "API schema published at docs/api.yaml" |
| `goal` | Current objective | "Complete auth migration by Friday" |
| `risk` | Known risk or concern | "Rate limiting not implemented for remote gateway" |
| `note` | General observation | "The legacy endpoint uses XML, not JSON" |
| `observation` | Pattern or convention learned | "Team prefers explicit error types over string messages" |

## Status Transitions

```
                ┌──────────┐
                │hypothesis│ ← Initial AI-written entry
                └────┬─────┘
                     │
            ┌────────┼────────┐
            ▼                 ▼
      ┌──────────┐     ┌──────────┐
      │validated │     │ rejected │ ← Wrong or harmful
      └────┬─────┘     └──────────┘
           │
           ▼
      ┌──────────┐
      │ obsolete │ ← Superseded by newer decision
      └──────────┘
```

- **hypothesis:** Initial entry written by an AI model. Lower trust. Consultative only.
- **validated:** Promoted by a human or confirmed by evidence. Higher trust.
- **obsolete:** Superseded by a newer decision. Retained for history.
- **rejected:** Determined to be wrong or harmful. Retained with reason. Never silently deleted.

## Memory Classes

| Class | Scope | Retention | Trust Level | Use |
|-------|-------|-----------|-------------|-----|
| **Project memory** | Shared across all sessions | Permanent (until invalidated) | Higher, especially validated | Decisions, goals, artifacts, conventions |
| **Session memory** | Private to one actor/session | Expires with session close | Lower | Scratchpad, intermediate reasoning, temp notes |

## Handoff Summary

`get_handoff_summary()` generates a structured transfer packet for model onboarding:

```json
{
  "current_goal": "Refactor auth to use JWT with refresh token rotation",
  "recent_decisions": [
    { "id": "01HXY...", "content": "Use RS256 for JWT signing", "status": "validated" },
    { "id": "01HXZ...", "content": "Store refresh tokens in Redis", "status": "hypothesis" }
  ],
  "changed_files": ["src/auth/jwt.ts", "src/middleware/auth.ts", "tests/auth.test.ts"],
  "open_risks": [
    { "content": "Token revocation not yet implemented", "status": "hypothesis" }
  ],
  "unresolved_questions": ["Should we support multiple active refresh tokens per user?"],
  "recommended_next_actions": ["Implement token revocation endpoint", "Add E2E tests for refresh flow"],
  "tech_stack": "TypeScript, FastAPI, PostgreSQL, Redis"
}
```

## Import / Export

Loom memory is not a lock-in. Users can migrate in and out:

- **`loom import CLAUDE.md`** — parse existing project instructions into memory entries (type=note, status=validated)
- **`loom import .cursorrules`** — parse Cursor rules into memory entries
- **`loom export claude-md`** — generate a CLAUDE.md from validated decisions and conventions
- **`loom export markdown`** — export all memory as a readable markdown document
