# ADR-002: SQLite for Project Memory

## Status
Accepted

## Context
Project memory needs persistent, queryable, and searchable storage. Options considered: PostgreSQL (too heavy for local), JSON files (no query support), SQLite (embedded, zero-config).

## Decision
Use SQLite as the memory storage engine with FTS5 for full-text search. One `.loom/memory.db` per workspace. WAL mode for concurrent reads. Optional sqlite-vss for vector search if FTS5 proves insufficient (V0.4+).

## Consequences
- **Easier:** Zero configuration. Works everywhere. Battle-tested. Fast for local workloads.
- **Harder:** Not suitable for high-concurrency multi-writer scenarios (fine for V0.x one-writer model). Remote topology may need migration to PostgreSQL/Turso for serverless deployment.
