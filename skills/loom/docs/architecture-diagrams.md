# Loom Architecture

## Deployment Modes

Loom supports three deployment modes. Pick the one that matches your team size and workflow.

### Mode 1: Solo Offline (default)

Everything runs on your machine. No server, no network, no auth.

```mermaid
graph LR
    CC[Claude Code] -->|stdio MCP| L[Loom CLI]
    CU[Cursor] -->|stdio MCP| L
    WS[Windsurf] -->|stdio MCP| L
    L --> DB[(.loom/memory.db)]
    L --> EV[(.loom/events.jsonl)]
```

**When to use:** Solo developer, single machine, privacy-first.

| Aspect | Detail |
|--------|--------|
| Setup | `pip install loom && loom init && loom connect claude-code` |
| Auth | None needed |
| Network | None |
| Data location | Local filesystem (`.loom/`) |
| Concurrent users | 1 |
| Multi-workspace | Switch with `cd` — each project has its own `.loom/` |

### Mode 2: Solo Connected (remote gateway)

Loom runs on a server. You access it from any device, any AI tool.

```mermaid
graph LR
    subgraph Your Devices
        CC[Claude Code] -->|stdio or SSE| GW
        CA[Claude.ai] -->|SSE| GW
        PH[Phone] -->|HTTPS| GW
    end

    subgraph Server
        GW[Loom Gateway :8443] --> AUTH[Auth: Bearer Token]
        AUTH --> POL[Policy Engine]
        POL --> DB[(.loom/memory.db)]
        POL --> EV[(.loom/events.jsonl)]
    end
```

**When to use:** Solo developer, multiple devices, access from Claude.ai or ChatGPT.

| Aspect | Detail |
|--------|--------|
| Setup | `loom gateway start` on a VPS + `loom connect --remote` on devices |
| Auth | Single API key (`LOOM_API_KEY`) |
| Network | HTTPS required |
| Data location | Server filesystem |
| Concurrent users | 1 (but from any device) |
| Multi-workspace | One gateway = one workspace. Use multi-workspace mode for multiple projects. |

### Mode 3: Small Team (shared server)

Multiple developers share one Loom server. Each gets their own API key.

```mermaid
graph TD
    subgraph Developers
        A[Alice: Claude Code] -->|SSE + API Key A| GW
        B[Bob: Cursor] -->|SSE + API Key B| GW
        C[Carol: Windsurf] -->|SSE + API Key C| GW
    end

    subgraph Loom Server
        GW[Gateway :8443]
        GW --> AUTH[Team Auth]
        AUTH --> |identify user| POL[Policy Engine]
        POL --> WR[Workspace Router]
        WR --> W1[Project Alpha .loom/]
        WR --> W2[Project Beta .loom/]
        WR --> W3[Project Gamma .loom/]
    end
```

**When to use:** Team of 3-10 developers, shared project memory, audit trail.

| Aspect | Detail |
|--------|--------|
| Setup | `loom team add alice --role admin` + distribute API keys |
| Auth | Per-user API keys with roles (admin/member/viewer) |
| Network | HTTPS required |
| Data location | Server filesystem (one `.loom/` per project) |
| Concurrent users | 3-10 (SQLite WAL) |
| Multi-workspace | `loom workspace register /path/to/project` for each project |

## System Architecture

```mermaid
graph TB
    subgraph Clients
        CC[Claude Code]
        CU[Cursor]
        WS[Windsurf]
        CD[Claude Desktop]
        CA[Claude.ai]
        GPT[ChatGPT]
        CI[CI/CD]
    end

    subgraph Transport
        STDIO[stdio MCP]
        SSE[SSE/HTTP MCP]
        REST[REST API]
    end

    subgraph Loom Gateway
        AUTH[Authentication]
        POL[Policy Engine]
        ROUTE[Workspace Router]
    end

    subgraph Core
        MCP[MCP Server - 8 tools]
        MEM[Memory Store - SQLite+FTS5]
        SES[Session Manager]
        TOK[Write Token]
        EVT[Event Log - JSONL]
    end

    subgraph Storage
        DB[(memory.db)]
        EVTF[(events.jsonl)]
        RT[(runtime.json)]
        WT[(write_token.json)]
        KEYS[(team/keys.json)]
    end

    CC --> STDIO
    CU --> STDIO
    WS --> STDIO

    CD --> SSE
    CA --> SSE
    GPT --> REST
    CI --> REST

    STDIO --> MCP
    SSE --> AUTH
    REST --> AUTH

    AUTH --> POL
    POL --> ROUTE
    ROUTE --> MCP

    MCP --> MEM
    MCP --> SES
    MCP --> TOK
    MCP --> EVT

    MEM --> DB
    EVT --> EVTF
    TOK --> WT
    SES --> DB
```

## Data Flow

### Decision Lifecycle

```mermaid
stateDiagram-v2
    [*] --> hypothesis: AI logs decision
    hypothesis --> validated: Human promotes
    hypothesis --> rejected: Human rejects
    hypothesis --> obsolete: Memory decay (TTL)
    validated --> obsolete: Superseded
    rejected --> [*]: Retained for audit
    obsolete --> [*]: Retained for audit
```

### Session Flow

```mermaid
sequenceDiagram
    participant A as Claude Code
    participant L as Loom
    participant B as Cursor

    A->>L: open_session(actor="claude-code")
    A->>L: log_decision("Use JWT")
    A->>L: log_decision("Use PostgreSQL")
    A->>L: write_memory(type="risk", "No rate limiting")
    A->>L: close_session(summary="Auth architecture done")

    Note over L: Context persists in memory.db

    B->>L: open_session(actor="cursor")
    B->>L: get_handoff_summary()
    L-->>B: {decisions: ["JWT", "PostgreSQL"], risks: ["No rate limiting"]}
    B->>L: log_decision("Use Alembic for migrations")
    B->>L: close_session(summary="Migration setup")
```

### Multi-Workspace Request Routing

```mermaid
graph LR
    REQ[Request: /w/abc123/api/search] --> GW[Gateway]
    GW --> AUTH[Auth Check]
    AUTH --> ROUTE[Router: resolve abc123]
    ROUTE --> |abc123 = /home/dev/project-alpha| WS[Workspace: project-alpha]
    WS --> STORE[MemoryStore: project-alpha/.loom/memory.db]
    STORE --> RESP[Response: search results]
```

## Security Model

```mermaid
graph TD
    REQ[Incoming Request] --> TLS{HTTPS?}
    TLS -->|No| REJECT[403 Reject]
    TLS -->|Yes| AUTH{Valid API Key?}
    AUTH -->|No| UNAUTH[401 Unauthorized]
    AUTH -->|Yes| ROLE{Check Role}
    ROLE -->|viewer + write| DENY[403 Forbidden]
    ROLE -->|member + admin| POL{Policy Check}
    POL -->|deny rule| BLOCK[Blocked by policy]
    POL -->|allow| TOK{Write Token?}
    TOK -->|write + no token| QUEUE[Queue / Retry]
    TOK -->|read or has token| EXEC[Execute]
    EXEC --> AUDIT[Log to events.jsonl]
```

## Scaling Limits

| Dimension | Solo | Small Team | Needs Migration |
|-----------|------|------------|-----------------|
| Users | 1 | 3-10 | >20 → PostgreSQL |
| Memory entries | <10K | <10K | >100K → archiving |
| Search latency | <0.1ms p95 | <1ms p95 | >10ms → index tuning |
| Workspaces | 1 per CLI | 1-10 per server | >10 → separate instances |
| Storage | Local SSD | Server SSD | >10GB → S3/NFS |
| Auth | None / single key | Per-user keys | SSO → V2.0 |
| Audit | events.jsonl | events.jsonl | Signed log → V2.0 |

## Migration Path

```
V0.x (current)          V1.0                    V2.0
─────────────           ────                    ────
SQLite + files    →     SQLite + contracts  →   PostgreSQL option
File-based auth   →     API key + roles     →   OAuth2 / SSO
Single-process    →     Gateway + policy    →   Connection pooling
events.jsonl      →     events.jsonl + hash →   Signed audit log
Manual sync       →     Git-based sync      →   Real-time replication
```
