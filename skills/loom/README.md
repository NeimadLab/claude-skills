<div align="center">

# Loom

**Weave context across AI tools. Resume work, not setup.**

*A loom weaves separate threads into one fabric — Loom weaves your AI workspace context into one persistent, inspectable, transferable substrate.*

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Phase](https://img.shields.io/badge/Phase-0.2_Handoff-3498DB.svg)](ROADMAP.md)
[![MCP](https://img.shields.io/badge/Protocol-MCP-8B5CF6.svg)](docs/gateway-model.md)

[Problem](#the-problem) · [Solution](#the-solution) · [Quick Start](#quick-start) · [Architecture](docs/architecture.md) · [Roadmap](ROADMAP.md) · [Contributing](CONTRIBUTING.md)

</div>

---

## The Problem

Every AI coding tool loses your work in four ways:

| Friction | What Happens | Time Lost |
|----------|-------------|-----------|
| **Context amnesia** | Claude compacts mid-task. Cursor forgets across tabs. Windsurf degrades in long sessions. | Every session |
| **Environment rebuild** | New session = cold start. Packages reinstall. Config rediscovered. State reconstructed. | 5–15 min/restart |
| **Cross-model blindness** | Claude Code doesn't know what Cursor did. Cursor doesn't know what Claude.ai decided. | Every tool switch |
| **Zero governance** | No audit trail. No approval workflow. No secret protection. Every shell command is ungoverned. | Permanent risk |

No single tool solves all four. Claude Code has CLAUDE.md but no cross-model transfer. Nucleus MCP has shared memory but no runtime persistence. DevContainers have isolation but no governance. **Loom unifies them.**

---

## The Solution

Loom is the workspace layer that makes AI-assisted development **persistent**, **transferable across models**, and **governed by explicit policies**.

```
┌───────────────────────────────────────────────────────────────┐
│  CLIENTS: Claude Code  Cursor  Windsurf  Claude.ai  ChatGPT  │
│           (stdio)     (stdio)  (stdio)   (SSE)      (SSE)    │
└───────────────────────┬───────────────────────────────────────┘
                        ▼
┌───────────────────────────────────────────────────────────────┐
│   P4: MCP GATEWAY  (Auth + Policy + Routing + Audit)         │
└───────────────────────────────────────────────────────────────┘
            ▼                  ▼                  ▼
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│ P2: PROJECT     │  │ P3: STATE       │  │ P1: RUNTIME     │
│ MEMORY          │  │ INDEX           │  │ SHELL           │
│ SQLite + FTS5   │  │ Git + JSONL     │  │ Docker+Volumes  │
└─────────────────┘  └─────────────────┘  └─────────────────┘
                        ▼
┌───────────────────────────────────────────────────────────────┐
│  WORKSPACE: Filesystem + Git + .loom/ (canonical truth)       │
└───────────────────────────────────────────────────────────────┘
```

---

## Quick Start

```bash
# Install from source (v0.2.0)
git clone https://github.com/NeimadLab/loom.git
cd loom
pip install -e .

# Initialize your project
cd ~/my-project
loom init

# Connect your AI tool
loom connect claude-code   # or: cursor, windsurf

# Resume after interruption
loom resume

# Check workspace health
loom doctor

# View workspace state
loom state
```

> **Current status:** V0.1-alpha. CLI works. MCP memory server works over stdio.
> Runtime persistence (Docker volumes) and remote gateway are planned for V0.1 and V0.3 respectively.
> See [ROADMAP.md](ROADMAP.md) for what's next.

---

## What It Looks Like

### `loom init` on a Python project
```
$ cd my-fastapi-app
$ loom init

Detected project type: python
Runtime identity: 7f3a2b1c9e04d8f2

╭──────────────────────── Loom ────────────────────────╮
│ ✓ Workspace initialized                             │
│                                                      │
│   Project type:  python                              │
│   Identity:      7f3a2b1c9e04d8f2                    │
│   .loom/ created: /home/dev/my-fastapi-app/.loom       │
│                                                      │
│ Next steps:                                          │
│   loom connect claude-code  — connect your AI tool    │
│   loom state               — inspect workspace        │
│   loom doctor              — run health checks        │
╰──────────────────────────────────────────────────────╯
```

### `loom doctor` health checks
```
$ loom doctor

                    Loom Doctor
┏━━━━━━━━━━━━━━━━━━┳━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Check            ┃ Status ┃ Detail                  ┃
┡━━━━━━━━━━━━━━━━━━╇━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ .loom/ directory  │   ✓    │ Present                 │
│ Runtime manifest │   ✓    │ Present                 │
│ Memory database  │   ✓    │ 28672 bytes             │
│ Event log        │   ✓    │ 12 events               │
│ Runtime identity │   ✓    │ No drift                │
│ Git repository   │   ✓    │ Clean                   │
│ Docker           │   ✓    │ Running                 │
└──────────────────┴────────┴─────────────────────────┘

7/7 checks passed
```

### Cross-model handoff via MCP
```
# Claude Code opens a session and works:
loom_open_session(actor="claude-code", model_name="claude-opus-4")
loom_log_decision(
    decision="Use JWT with RS256 for authentication",
    rationale="Stateless, scalable, works with our API gateway"
)
loom_close_session(summary="Set up auth architecture")

# User switches to Cursor. Cursor opens its own session:
loom_open_session(actor="cursor", model_name="gpt-4o")
loom_get_handoff_summary()
# → { "recent_decisions": [{"content": "Use JWT with RS256", "status": "hypothesis"}],
#     "current_goals": ["Complete auth migration"],
#     "open_risks": ["Token revocation not implemented"] }

# Cursor sees Claude Code's decisions. Context survived the switch.
```

### Import/export CLAUDE.md
```
$ loom import CLAUDE.md
✓ Imported 12 entries from CLAUDE.md (format: claude-md)

$ loom export claude-md -o CLAUDE.md
✓ Exported to CLAUDE.md
```

See [`examples/python-project/`](examples/python-project/) for a full initialized workspace.


---

## Why Not Just Use X?

| Tool | What It Covers | What It Doesn't | Loom Adds |
|------|---------------|-----------------|----------|
| **Claude Code CLAUDE.md** | Persistent instructions, auto-memory | No cross-model, no runtime, no gateway | Cross-model memory, runtime persistence, governance |
| **Nucleus MCP** | Shared memory across tools | No runtime, no governance | Runtime shell, policy engine, remote access |
| **DevContainers** | Reproducible environments | No memory, no handoff | Project memory, handoff summaries, state index |
| **mem0 / OpenMemory** | Semantic memory, vector search | No workspace, no governance | Full workspace substrate, policy-gated access |
| **LangGraph / CrewAI** | Multi-agent orchestration | Cloud-first, not for local dev | Local-first, workspace-native, model-agnostic |

---

## Three Deployment Topologies

| Topology | How | Best For |
|----------|-----|----------|
| **Local** | CLI + MCP via stdio. Data stays on your laptop. | Solo dev. Air-gapped. Maximum sovereignty. |
| **Remote** | MCP gateway over HTTPS. Claude.ai, ChatGPT connect as clients. | Cloud AI tools. Team workspaces. Mobile access. |
| **Hybrid** | Local runtime + remote memory. Sync between devices. | Fast local dev + persistent cloud memory. |

---

## Roadmap

| Phase | Name | Status |
|-------|------|:------:|
| **V0.1** | [Foundations](docs/product-evolution.md#v01--foundations) — Resume + Memory + Doctor | ✅ Done |
| **V0.2** | [Sequential Handoff](docs/product-evolution.md#v02--sequential-model-handoff) — Sessions, tokens, import/export, gateway | ✅ Done |
| **V0.3** | [Hardening](docs/product-evolution.md#v03--controlled-gateway--remote-access) — Policy engine, recovery, benchmarks | ⬜ Next |
| **V1.0** | [Stable Substrate](docs/product-evolution.md#v10--stable-technical-substrate) — Contracts, PyPI, hybrid topology | ⬜ Planned |
| **V2.0** | [Parallel Tracks](docs/product-evolution.md#v20--parallel-work-streams) — Multi-agent via Git worktrees | ⬜ Future |
| **V3.0** | [Orchestrated Intelligence](docs/product-evolution.md#v30--coordinated-actor-ecosystem) — Role-based actor coordination | ⬜ Future |

Full details → [ROADMAP.md](ROADMAP.md) · Product evolution → [docs/product-evolution.md](docs/product-evolution.md)

---

## Documentation

### Getting Started

| Guide | Description |
|-------|-------------|
| **[Getting Started](docs/getting-started.md)** | Zero to working workspace in 5 minutes |
| **[Local Setup](docs/setup-local.md)** | Complete local installation and configuration |
| **[Cloud Setup](docs/setup-cloud.md)** | Deploy on VPS, Fly.io, Railway, or AWS/GCP/Azure |

### Connect Your AI Tool

| Tool | Guide | Transport |
|------|-------|-----------|
| **Claude Code** | [Connect →](docs/connect-claude-code.md) | stdio (local) or SSE (remote) |
| **Cursor** | [Connect →](docs/connect-cursor.md) | stdio (local) |
| **Windsurf** | [Connect →](docs/connect-windsurf.md) | stdio (local) |
| **Claude Desktop** | [Connect →](docs/connect-claude-desktop.md) | stdio (local) |
| **Claude.ai** (browser) | [Connect →](docs/setup-cloud.md#claudeai-browser) | SSE (remote) |
| **ChatGPT** (custom GPT) | [Connect →](docs/setup-cloud.md#chatgpt-custom-gpt-with-actions) | REST API (remote) |
| **Gemini** | [Connect →](docs/setup-cloud.md#gemini-google-ai-studio) | SSE (remote) |
| **CI/CD** | [Connect →](docs/setup-cloud.md#cicd-pipelines-github-actions-gitlab-ci) | CLI or REST API |

### Reference

| Document | Description |
|----------|-------------|
| [MCP Tool Reference](docs/mcp-tool-reference.md) | All 6 MCP tools with parameters and examples |
| [Architecture](docs/architecture.md) | Five pillars, state model, invariants |
| [Memory Model](docs/memory-model.md) | How structured memory works |
| [Security Model](docs/security-model.md) | Threat model, policies, action classes |
| [Product Charter](docs/product-charter.md) | Mission, principles, why "Loom" |

---

## Repository Structure

```
loom/
├── src/loom/              ← Core source code
│   ├── cli/              ← CLI commands (init, resume, doctor...)
│   ├── mcp/              ← MCP server implementation
│   ├── memory/           ← SQLite memory layer
│   ├── state/            ← Inventory, events, state index
│   ├── gateway/          ← Policy engine, auth, gateway service
│   └── runtime/          ← Container lifecycle, identity
├── docs/                 ← Architecture, models, guides
├── rfcs/                 ← Proposals for significant changes
├── adrs/                 ← Architectural Decision Records
├── templates/            ← DevContainer, policy, MCP configs
├── deploy/               ← Docker, Fly.io deployment configs
├── tests/                ← Unit, integration, e2e, contract, benchmark
├── scripts/              ← Dev, release, benchmark utilities
├── ROADMAP.md            ← Now / Next / Later / Not Planned
├── CONTRIBUTING.md       ← How to contribute
├── GOVERNANCE.md         ← Decision process
└── SECURITY.md           ← Vulnerability reporting
```

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

**Quick paths:**
- 🐛 Found a bug → [Open an issue](.github/ISSUE_TEMPLATE/bug-report.yml)
- 💡 Feature idea → [Start a Discussion](../../discussions)
- 📖 Improve docs → PRs always welcome
- 🔧 Contribute code → see [Contributing Code](docs/contributing-code.md)

## License

MIT — see [LICENSE](LICENSE).
