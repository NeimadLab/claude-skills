# Function & Skill Catalog

44 functions organized by subsystem. Each function has: role, phase, implementation guidance, exposure model, and dependencies.

## Workspace & Runtime (Phase 0.1–0.2)

| Function | Role | Phase | Exposed |
|----------|------|:-----:|:-------:|
| `init_workspace()` | Create .loom/ scaffold, detect project type, generate devcontainer.json | 0.1 | CLI |
| `detect_runtime_identity()` | Compute deterministic hash from lockfiles, tool versions, base image | 0.1 | Internal |
| `snapshot_runtime()` | Capture restorable runtime state and cache references | 0.1 | Internal |
| `restore_env()` | Recreate runtime from manifests. Emit diff on mismatch. | 0.1 | Internal |
| `doctor_check()` | Run health checks. Machine-readable + human summary. | 0.1 | Model |
| `repair_workspace()` | Apply safe automated fixes. Approval on destructive ops. | 0.1 | CLI |
| `run_isolated_test()` | Run project tests in controlled runtime. Capture results. | 0.1 | Model (V0.3+) |
| `build_artifact()` | Build deliverables under controlled runtime. | 0.2 | Model (V0.3+) |

## Inventory & State (Phase 0.1–0.4)

| Function | Role | Phase | Exposed |
|----------|------|:-----:|:-------:|
| `refresh_inventory()` | Update file index in SQLite. Scoped, incremental. | 0.1 | Internal |
| `list_workspace_state()` | Return concise operational snapshot. | 0.1 | Model |
| `scan_services()` | Detect local services (containers, ports, DBs). | 0.3 | Model |
| `diff_workspace_state()` | Show changes since previous baseline. | 0.2 | Model |
| `rebuild_state()` | Reconstruct .loom/ from repo + events. Tolerate partial loss. | 0.4 | CLI |

## Memory & Handoff (Phase 0.2–0.4)

| Function | Role | Phase | Exposed |
|----------|------|:-----:|:-------:|
| `write_memory_entry()` | Store typed memory record (decision/artifact/goal/risk/note). | 0.2 | MCP |
| `search_memory()` | Full-text + metadata search. FTS5, optional vector (V0.4+). | 0.2 | MCP |
| `log_decision()` | Specialized decision record with rationale and status. | 0.2 | MCP |
| `promote_decision_status()` | Transition: hypothesis → validated → obsolete. | 0.4 | MCP |
| `invalidate_memory_entry()` | Retire stale memory. Soft-delete with reason. | 0.4 | MCP |
| `get_handoff_summary()` | Structured transfer packet: goal, decisions, files, risks, next actions. | 0.2 | MCP |

## Sessions, Actors & Coordination (Phase 0.2–2.0)

| Function | Role | Phase | Exposed |
|----------|------|:-----:|:-------:|
| `open_session()` | Start bounded session with identity, scope, lease. | 0.2 | MCP |
| `close_session()` | End session. Emit summary. Release write token. | 0.2 | MCP |
| `attach_actor()` | Associate model/user identity with session. | 0.2 | Internal |
| `acquire_write_token()` | Grant exclusive write authority. Lease-based. | 0.2 | MCP |
| `release_write_token()` | Release or expire write authority. | 0.2 | MCP |
| `create_worktree()` | Git worktree isolation for parallel work. | 2.0 | MCP |
| `merge_worktree()` | Test-gated merge with traceability. | 2.0 | MCP |

## Gateway & Policy (Phase 0.3)

| Function | Role | Phase | Exposed |
|----------|------|:-----:|:-------:|
| `start_gateway()` | Start MCP gateway (stdio + optional SSE/HTTPS). | 0.3 | CLI |
| `stop_gateway()` | Stop gateway. Close sessions. Revoke tokens. | 0.3 | CLI |
| `attach_remote_model()` | Bind remote model session via gateway. | 0.3 | Auto |
| `policy_check()` | Evaluate action against YAML policy rules. | 0.3 | Internal |
| `request_approval()` | Prompt user with command preview, diff, risk level. | 0.3 | Internal |
| `execute_tool_call()` | Dispatch MCP tool call with eventing and policy. | 0.3 | Internal |
| `read_secret()` | Access secrets via named aliases. Whitelist-only. | 0.3 | Model (local) |
| `install_dependency()` | Controlled package install. Approval-gated. | 0.3 | Model |

## Observability & Packaging (Phase 0.1–1.0)

| Function | Role | Phase | Exposed |
|----------|------|:-----:|:-------:|
| `tail_events()` | Read recent events. Filter by type, actor, session. | 0.1 | Model |
| `export_context_bundle()` | Package state for debugging or handoff. | 0.4 | CLI |
| `package_release_notes()` | Generate release notes from decisions + commits. | 1.0 | CLI |
| `benchmark_resume()` | Measure resume, handoff, rebuild latency. | 1.0 | CLI |

## New Functions

| Function | Role | Phase | Exposed |
|----------|------|:-----:|:-------:|
| `loom_connect(client)` | Generate MCP config for a specific AI tool. | 0.1 | CLI |
| `loom_context()` | Generate compact project onboarding file. | 0.2 | MCP |
| `loom_import(source)` | Import CLAUDE.md / .cursorrules into Loom memory. | 0.2 | CLI |
| `loom_export(target)` | Export Loom memory as CLAUDE.md / .cursorrules. | 0.2 | CLI |
| `loom_set_project(id)` | Switch active project on multi-project instance. | 0.3 | MCP |
| `loom_benchmark()` | Run full benchmark suite. Produce report. | 1.0 | CLI |

See the [Project Bible](project-bible-v3.md) for the original detailed implementation guidance per function. The actual implementation is in `src/loom/`.
