# Loom Features

Complete feature reference. Everything Loom can do, organized by category.

## Memory

Persistent, structured project memory that survives across sessions and tools.

| Feature | CLI | MCP Tool | JSON |
|---------|-----|----------|------|
| Search memory | `loom search "auth"` | `loom_search_memory` | `--json` |
| Log decision | `loom log "Use JWT" -r "Stateless"` | `loom_log_decision` | — |
| Write any entry | — | `loom_write_memory` | — |
| Promote to validated | `loom promote <id>` | — | — |
| Reject entry | `loom reject <id> -r "reason"` | — | — |
| Get handoff summary | — | `loom_get_handoff_summary` | — |
| Get project context | `loom context` | `loom_get_context` | `--json` `--save` |

**Entry types:** decision, goal, risk, note, observation, artifact
**Status model:** hypothesis → validated → obsolete / rejected
**Storage:** SQLite + FTS5 full-text search. p95 search latency <0.1ms on 500 entries.

## Sessions

Track which AI tool is working, when, and what it accomplished.

| Feature | CLI | MCP Tool | JSON |
|---------|-----|----------|------|
| Open session | `loom session open claude-code --model claude-opus-4` | `loom_open_session` | `--json` |
| Close session | `loom session close -s "summary"` | `loom_close_session` | `--json` |
| List sessions | `loom session list` | — | `--json` |
| Cleanup stale | `loom session cleanup --max-age 24` | — | — |

**Actor tracking:** Every memory entry is linked to the actor that created it.
**Session history:** Full audit trail of who worked when and what they did.

## Write Token

Single-writer exclusion. Prevents concurrent write conflicts.

| Feature | CLI | JSON |
|---------|-----|------|
| Acquire token | `loom token acquire <session_id> <actor> --lease 15` | `--json` |
| Release token | `loom token release <session_id>` | `--json` |
| Check status | `loom token status` | `--json` |

**Lease-based:** Tokens auto-expire after configurable duration (default 15 min).
**Force reclaim:** `--force` takes the token from a stale holder.

## Import / Export

Migration path for existing workflows. On-ramp for new users.

| Feature | CLI |
|---------|-----|
| Import CLAUDE.md | `loom import CLAUDE.md` |
| Import .cursorrules | `loom import .cursorrules` |
| Export as CLAUDE.md | `loom export claude-md -o CLAUDE.md` |
| Export as markdown | `loom export markdown -o dump.md` |

**Smart detection:** Auto-detects decisions, goals, risks, conventions from markdown.
**Roundtrip safe:** Import → edit in Loom → export back to CLAUDE.md.

## Workspace Management

Initialize, monitor, and restore workspaces.

| Feature | CLI | JSON |
|---------|-----|------|
| Initialize | `loom init` | — |
| Resume (verify + restore) | `loom resume` | `--json` |
| Health checks | `loom doctor` | `--json` |
| Workspace state | `loom state` | `--json` |
| View events | `loom events -n 20` | `--json` |
| Connect AI tool | `loom connect claude-code` | — |

**Project detection:** Python, Node, Rust, Go (from lockfiles and manifests).
**Runtime identity:** SHA-256 hash of lockfiles — detects environment drift.
**Docker restore:** `loom resume` restores cache volumes if Docker is available.

## Remote Gateway

Access Loom from anywhere — Claude.ai, ChatGPT, phone, CI/CD.

| Feature | CLI |
|---------|-----|
| Start gateway | `loom gateway start --port 8443` |
| Generate API key | `loom gateway keygen` |
| Generate devcontainer | `loom gateway devcontainer` |

**Transports:** stdio (local), SSE/HTTP (remote), REST API (ChatGPT/CI)
**REST endpoints:** `/api/search`, `/api/log-decision`, `/api/handoff`, `/api/context`, `/api/write-memory`
**MCP-over-HTTP:** `/mcp/messages` (JSON-RPC)
**Auth:** Bearer token via `LOOM_API_KEY`

## Policy Engine

Governance layer. Control what AI tools can do in your workspace.

| Feature | CLI | JSON |
|---------|-----|------|
| Install default policy | `loom policy install` | — |
| Check tool permission | `loom policy check loom_write_memory` | `--json` |

**Rules:** YAML-based, per-action (read_memory, write_memory, execute, read_secret)
**Conditions:** `path_match`, `command_match`, `alias_match`
**Decisions:** allow, deny, approve (with logged reasons)
**Gateway integration:** Policy evaluated before every tool call on the gateway.

## Recovery & Maintenance

Keep your workspace healthy and your data safe.

| Feature | CLI | JSON |
|---------|-----|------|
| Integrity check + repair | `loom repair` | `--json` |
| Rebuild from event log | `loom rebuild` | `--json` |
| Memory decay | `loom decay --ttl 30` | `--json` |
| Dry run decay | `loom decay --ttl 30 --dry-run` | `--json` |

**Integrity checks:** .loom/ dir, memory.db, FTS5 sync, events.jsonl, runtime.json, write token, sessions.
**Auto-repair:** Cleans expired tokens, closes stale sessions, rebuilds FTS5 index.
**State rebuild:** Nuclear recovery — reconstruct memory.db from events.jsonl alone.
**Memory decay:** Auto-obsolete unvalidated `hypothesis` entries older than TTL days.

## Team Mode

Multi-user access for small teams (3-10 developers).

| Feature | CLI | JSON |
|---------|-----|------|
| Add team member | `loom team add alice --role member` | `--json` |
| List team | `loom team list` | `--json` |
| Remove member | `loom team remove <user_id>` | — |
| Show limits | `loom team limits` | — |

**Roles:** admin (full access), member (read + write), viewer (read only)
**Per-user API keys:** Each team member gets their own key. Actions attributed to the user.
**Solo ↔ Team:** Add a user to switch from solo to team mode. Remove all to go back.

### Team Limits (transparent)

| Dimension | Works Well | Caution | Needs V2.0 |
|-----------|-----------|---------|------------|
| Concurrent users | 3-10 | 10-20 | >20 |
| Memory entries | <10K | 10K-100K | >100K |
| Workspaces | 1-10 | - | >10 |
| Auth | API keys | - | SSO/OAuth |
| Roles | admin/member/viewer | - | Custom RBAC |

## Multi-Workspace

Serve multiple projects from one gateway.

| Feature | CLI | JSON |
|---------|-----|------|
| Register workspace | `loom workspace register /path/to/project -n "Alpha"` | `--json` |
| List workspaces | `loom workspace list` | `--json` |
| Remove workspace | `loom workspace remove <id>` | — |
| Start multi-ws gateway | `loom workspace serve --port 8443` | — |

**Routing:** Each workspace gets its own URL prefix: `/w/{workspace_id}/api/...`
**Isolation:** Each project has its own .loom/, memory.db, sessions, and policies.
**Health monitoring:** `loom workspace list` shows health status of each workspace.

## Benchmarks

Measure and verify Loom performance.

| Feature | CLI | JSON |
|---------|-----|------|
| Run benchmarks | `loom benchmark` | `--json` |

**Measures:** init time, write throughput, search latency (p50/p95/p99), handoff generation, event emit.
**Performance targets:**

| Operation | p50 | p95 |
|-----------|-----|-----|
| Init (cold start) | <20ms | <35ms |
| Memory write | <1.5ms | <2ms |
| FTS5 search (500 entries) | <0.1ms | <0.2ms |
| Handoff summary (50 entries) | <0.5ms | <1ms |
| Event emit | <0.3ms | <0.5ms |

## MCP Tools (8 total)

| Tool | Purpose |
|------|---------|
| `loom_search_memory` | Full-text search across all memory entries |
| `loom_write_memory` | Store a structured memory entry |
| `loom_log_decision` | Log a decision with rationale |
| `loom_get_handoff_summary` | Generate transfer packet for session onboarding |
| `loom_get_context` | Compact project overview |
| `loom_get_state` | Workspace operational state |
| `loom_open_session` | Start tracking an AI tool session |
| `loom_close_session` | End session with summary |

## Supported AI Tools

| Tool | Transport | Setup |
|------|-----------|-------|
| Claude Code | stdio (local) or SSE (remote) | `loom connect claude-code` |
| Cursor | stdio (local) | `loom connect cursor` |
| Windsurf | stdio (local) | `loom connect windsurf` |
| Claude Desktop | stdio (local) | Manual config |
| Claude.ai | SSE (remote) | Gateway + MCP integration |
| ChatGPT | REST API (remote) | Gateway + Custom GPT Actions |
| Gemini | SSE (remote) | Gateway + Extensions |
| CI/CD | REST API or CLI | Gateway + `loom log` in pipeline |
