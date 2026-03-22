# Testing Strategy

## Philosophy

Loom must test both implementation correctness and product claims. A green unit suite alone does not prove that workspace resume, cross-model handoff, or crash recovery actually work. The testing strategy explicitly ties test types to product hypotheses.

## Test Types

| Type | What It Proves | Speed | When Run | Failure = |
|------|---------------|:-----:|----------|-----------|
| **Unit** | Isolated logic works (parsers, hash functions, policy evaluator) | Fast (<60s) | Every PR | Merge blocked |
| **Integration** | Subsystems interact correctly (memory + state, gateway + policy) | Medium (~5 min) | Every PR | Merge blocked |
| **E2E** | Product scenarios work end-to-end in a real container | Slow (~15 min) | PR + release | Merge blocked (smoke), release blocked (full) |
| **Contract** | Public MCP tool surface matches documented schema | Fast (<30s) | Every PR | Merge blocked |
| **Benchmark** | Performance claims hold (resume time, search latency) | Slow (~10 min) | Release only | Release note warning |
| **Compatibility** | Works across OS + tool combinations | Slow (~30 min) | Release only | Compatibility matrix update |

## Key Scenarios

Each scenario maps to a product claim that Loom makes:

1. **Same-actor resume:** `loom init` → work → close terminal → `loom resume` → verify state is intact and environment is functional. *Proves: "Never start from scratch again."*

2. **Cross-model handoff:** Claude Code writes 5 decisions → user switches to Cursor → Cursor reads handoff summary and continues work. *Proves: "Switch models, keep the thread."*

3. **Crash recovery:** Kill Loom process mid-session → `loom resume` → verify integrity, reclaim stale session, no data loss. *Proves: resilience and trust in the state model.*

4. **Remote gateway:** Authenticate via API key → write memory via HTTPS → verify audit trail → verify policy enforcement on denied action. *Proves: "Your workspace, accessible from anywhere."*

5. **Policy enforcement:** Attempt a denied action (e.g., `read_secret` from remote) → verify blocked → verify logged → verify user-friendly error message. *Proves: governance actually works.*

6. **State rebuild:** Delete `.loom/memory.db` → run `loom rebuild` → verify memory reconstructed from events + Git. *Proves: reconstructible .loom/.*

## Benchmark Targets

| Metric | Target | Measurement Method |
|--------|--------|-------------------|
| Cold start (`loom init`) | < 30s | Timed E2E on clean project |
| Warm resume (`loom resume`) | < 10s | Timed E2E after container rebuild |
| Memory search (1000 entries) | < 100ms (p95) | Benchmark suite with synthetic data |
| Handoff summary generation | < 2s | Benchmark suite |
| State rebuild from events | < 60s | Benchmark suite with 10K events |
| Policy evaluation | < 5ms (p99) | Microbenchmark |

## Fixture Strategy

Test fixtures live in `tests/fixtures/` and include:

- **Sample projects:** minimal Python and Node.js projects with lockfiles
- **Memory databases:** pre-populated SQLite files with known content
- **Event logs:** JSONL files with specific event sequences
- **Policy files:** YAML configs for testing allow/deny/approve paths
- **MCP request/response pairs:** JSON files for contract tests

## CI Integration

Tests run in GitHub Actions with matrix builds (Linux + macOS). Docker-in-Docker is available for E2E tests. See `.github/workflows/ci.yml` for the pipeline configuration.
