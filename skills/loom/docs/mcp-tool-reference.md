
# MCP Tool Reference

Complete reference for all 6 Loom MCP tools. These tools are available to any MCP-compatible AI client connected to Loom.

## loom_search_memory

Search project memory for decisions, notes, goals, risks, and observations.

**Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|:--------:|---------|-------------|
| `query` | string | ✅ | — | Full-text search query |
| `type` | string | | all | Filter: `decision`, `artifact`, `goal`, `risk`, `note`, `observation` |
| `status` | string | | all | Filter: `hypothesis`, `validated`, `obsolete`, `rejected` |
| `limit` | integer | | 10 | Maximum results to return |

**Returns:** JSON array of memory entries, ranked by recency.

**Example:**
```json
// Input
{ "query": "authentication", "type": "decision", "limit": 5 }

// Output
[
  {
    "id": "019d12f8...",
    "type": "decision",
    "status": "validated",
    "content": "Use JWT with RS256 for authentication",
    "rationale": "Stateless, scalable, works with API gateway",
    "actor": "claude-code",
    "timestamp": "2026-03-22T10:00:00Z",
    "tags": "[\"auth\", \"security\"]"
  }
]
```

**Tips:**
- Search with an empty query (`""`) to list all entries (respects type/status filters)
- Special characters are automatically sanitized for FTS5 compatibility
- Results are ordered by timestamp descending (most recent first)

---

## loom_write_memory

Store a structured memory entry in project memory.

**Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|:--------:|---------|-------------|
| `content` | string | ✅ | — | The memory content |
| `type` | string | | `note` | One of: `decision`, `artifact`, `goal`, `risk`, `note`, `observation` |
| `tags` | string[] | | `[]` | Searchable tags |
| `linked_files` | string[] | | `[]` | Related file paths |

**Returns:** `{ "id": "...", "status": "written" }`

**Example:**
```json
// Input
{
  "content": "API returns paginated responses with cursor-based pagination",
  "type": "observation",
  "tags": ["api", "pagination"]
}
```

---

## loom_log_decision

Record an architectural or technical decision with rationale. This is a convenience wrapper that creates a memory entry with `type=decision` and `status=hypothesis`.

**Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|:--------:|---------|-------------|
| `decision` | string | ✅ | — | What was decided |
| `rationale` | string | ✅ | — | Why this was decided |
| `tags` | string[] | | `[]` | Searchable tags |
| `linked_files` | string[] | | `[]` | Related file paths |

**Returns:** `{ "id": "...", "status": "logged" }`

**Example:**
```json
// Input
{
  "decision": "Use PostgreSQL instead of MongoDB",
  "rationale": "Need ACID transactions for payment processing. JSON support covers our document needs.",
  "tags": ["database", "payments"],
  "linked_files": ["src/db/connection.py"]
}
```

**Tips:**
- Always include a rationale — it's the most valuable part for future handoff
- New decisions start as `hypothesis` — humans can promote to `validated` via CLI
- Search for existing decisions before logging a new one to avoid contradictions

---

## loom_get_handoff_summary

Generate a structured transfer packet for another model or session to resume work. This is the key tool for cross-model handoff.

**Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|:--------:|---------|-------------|
| `depth` | string | | `compact` | `compact` (5 recent) or `full` (20 recent) |

**Returns:** Structured JSON summary.

**Example output:**
```json
{
  "current_goals": ["Complete auth migration by end of sprint"],
  "recent_decisions": [
    { "content": "Use JWT with RS256 for auth", "status": "validated" },
    { "content": "Store refresh tokens in Redis", "status": "hypothesis" }
  ],
  "open_risks": ["Token revocation not yet implemented"],
  "total_memory_entries": 23,
  "recent_activity": [
    { "type": "decision", "content": "Use JWT with RS256 for auth" },
    { "type": "risk", "content": "Token revocation not yet implemented" }
  ]
}
```

**Best practice:** Call this tool at the **start of every new session** to onboard the model with full context from previous work.

---

## loom_get_context

Get a compact project context package. Lighter than a handoff summary — designed for quick orientation.

**Parameters:** None.

**Returns:**
```json
{
  "project_type": "python",
  "runtime_identity": "7f3a2b1c9e04d8f2",
  "git_branch": "main",
  "memory_entries": 23,
  "active_goals": ["Complete auth migration"],
  "recent_decisions": ["Use JWT with RS256", "PostgreSQL for database"],
  "known_risks": ["Token revocation not implemented"]
}
```

---

## loom_get_state

Get workspace operational state: file counts, runtime identity, event log stats, git status.

**Parameters:** None.

**Returns:**
```json
{
  "workspace": "/home/dev/my-project",
  "loom_initialized": true,
  "project_type": "python",
  "runtime_identity": "7f3a2b1c9e04d8f2",
  "identity_drift": "none",
  "memory_entries": 23,
  "event_count": 47,
  "recent_events": [...],
  "git_branch": "main",
  "git_dirty": false,
  "file_count": 142
}
```

---

## Type and Status Reference

### Memory Types

| Type | When to Use |
|------|------------|
| `decision` | Architectural or technical choice (use `loom_log_decision` for this) |
| `goal` | Current objective or milestone |
| `risk` | Known risk, concern, or tech debt |
| `note` | General observation or information |
| `observation` | Pattern, convention, or learned behavior |
| `artifact` | Reference to a deliverable (API doc, schema, report) |

### Status Values

| Status | Meaning | Trust Level |
|--------|---------|:-----------:|
| `hypothesis` | Initial AI-written entry | Low — consultative |
| `validated` | Human-confirmed or evidence-backed | High |
| `obsolete` | Superseded by newer entry | Historical |
| `rejected` | Determined to be wrong | Retained for audit |
