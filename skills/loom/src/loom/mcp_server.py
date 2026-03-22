"""MCP server exposing Loom memory and state tools.

The tool handlers are implemented as plain async functions in `handlers`
so they can be tested without the MCP transport layer.
"""

from __future__ import annotations

import json
from pathlib import Path

from mcp.server import Server
from mcp.types import TextContent, Tool

from loom import events as event_log
from loom.memory import MemoryStore
from loom.models import Event, MemoryEntry, MemoryType
from loom.state import get_workspace_state

# ────────────────────────────────────────────
# Tool definitions (schema only, no logic)
# ────────────────────────────────────────────

TOOLS = [
    Tool(
        name="loom_search_memory",
        description=(
            "Search project memory for decisions, notes, goals, risks. "
            "Returns relevant entries ranked by recency."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query"},
                "type": {
                    "type": "string",
                    "enum": ["decision", "artifact", "goal", "risk", "note", "observation"],
                },
                "status": {
                    "type": "string",
                    "enum": ["hypothesis", "validated", "obsolete", "rejected"],
                },
                "limit": {"type": "integer", "default": 10},
            },
            "required": ["query"],
        },
    ),
    Tool(
        name="loom_write_memory",
        description=(
            "Store a structured memory entry in project memory. "
            "Types: decision, note, goal, risk, observation."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "content": {"type": "string", "description": "Memory content"},
                "type": {
                    "type": "string",
                    "enum": ["decision", "artifact", "goal", "risk", "note", "observation"],
                    "default": "note",
                },
                "tags": {"type": "array", "items": {"type": "string"}, "default": []},
                "linked_files": {"type": "array", "items": {"type": "string"}, "default": []},
            },
            "required": ["content"],
        },
    ),
    Tool(
        name="loom_log_decision",
        description=(
            "Record an architectural or technical decision with rationale. "
            "Stored as type=decision, status=hypothesis."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "decision": {"type": "string", "description": "What was decided"},
                "rationale": {"type": "string", "description": "Why"},
                "tags": {"type": "array", "items": {"type": "string"}, "default": []},
                "linked_files": {"type": "array", "items": {"type": "string"}, "default": []},
            },
            "required": ["decision", "rationale"],
        },
    ),
    Tool(
        name="loom_get_handoff_summary",
        description=(
            "Generate a structured handoff summary for model onboarding. "
            "Includes: decisions, goals, risks, changed context."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "depth": {
                    "type": "string",
                    "enum": ["compact", "full"],
                    "default": "compact",
                },
            },
        },
    ),
    Tool(
        name="loom_get_context",
        description="Get compact project context: type, stack, decisions, goals, risks.",
        inputSchema={"type": "object", "properties": {}},
    ),
    Tool(
        name="loom_get_state",
        description="Get workspace operational state: files, identity, events, git status.",
        inputSchema={"type": "object", "properties": {}},
    ),
]

# ────────────────────────────────────────────
# Handlers (testable without MCP transport)
# ────────────────────────────────────────────


def handle_search_memory(store: MemoryStore, arguments: dict) -> dict:
    """Handle loom_search_memory tool call."""
    return store.search(
        query=arguments.get("query", ""),
        limit=arguments.get("limit", 10),
        type_filter=arguments.get("type"),
        status_filter=arguments.get("status"),
    )


def handle_write_memory(store: MemoryStore, arguments: dict, workspace: Path) -> dict:
    """Handle loom_write_memory tool call."""
    entry = MemoryEntry(
        type=MemoryType(arguments.get("type", "note")),
        content=arguments["content"],
        tags=arguments.get("tags", []),
        linked_files=arguments.get("linked_files", []),
        actor="mcp-client",
    )
    store.write(entry)
    event_log.emit(
        Event(
            event_type="memory_written",
            actor="mcp-client",
            data={"entry_id": entry.id, "type": entry.type.value},
        ),
        workspace,
    )
    return {"id": entry.id, "status": "written"}


def handle_log_decision(store: MemoryStore, arguments: dict, workspace: Path) -> dict:
    """Handle loom_log_decision tool call."""
    entry = MemoryEntry(
        type=MemoryType.DECISION,
        content=arguments["decision"],
        rationale=arguments.get("rationale"),
        tags=arguments.get("tags", []),
        linked_files=arguments.get("linked_files", []),
        actor="mcp-client",
    )
    store.write(entry)
    event_log.emit(
        Event(
            event_type="decision_logged",
            actor="mcp-client",
            data={"entry_id": entry.id, "decision": entry.content[:100]},
        ),
        workspace,
    )
    return {"id": entry.id, "status": "logged"}


def handle_get_handoff_summary(store: MemoryStore, arguments: dict) -> dict:
    """Handle loom_get_handoff_summary tool call."""
    depth = arguments.get("depth", "compact")
    n = 5 if depth == "compact" else 20
    decisions = store.search("", limit=n, type_filter="decision")
    goals = store.search("", limit=3, type_filter="goal")
    risks = store.search("", limit=3, type_filter="risk")
    recent = store.recent(n)
    return {
        "current_goals": [g["content"] for g in goals],
        "recent_decisions": [{"content": d["content"], "status": d["status"]} for d in decisions],
        "open_risks": [r["content"] for r in risks],
        "total_memory_entries": store.count(),
        "recent_activity": [{"type": e["type"], "content": e["content"][:80]} for e in recent],
    }


def handle_get_context(store: MemoryStore, workspace: Path) -> dict:
    """Handle loom_get_context tool call."""
    state = get_workspace_state(workspace)
    decisions = store.search("", limit=10, type_filter="decision")
    goals = store.search("", limit=5, type_filter="goal")
    risks = store.search("", limit=5, type_filter="risk")
    return {
        "project_type": state.get("project_type", "unknown"),
        "runtime_identity": state.get("runtime_identity"),
        "git_branch": state.get("git_branch"),
        "memory_entries": state.get("memory_entries", 0),
        "active_goals": [g["content"] for g in goals],
        "recent_decisions": [d["content"] for d in decisions[:5]],
        "known_risks": [r["content"] for r in risks],
    }


# ────────────────────────────────────────────
# MCP Server (wires handlers to transport)
# ────────────────────────────────────────────


def create_server(workspace: Path | None = None) -> Server:
    """Create and configure the Loom MCP server."""
    server = Server("loom")
    ws = workspace or Path(".")

    @server.list_tools()
    async def list_tools() -> list[Tool]:
        """Return all available Loom MCP tools."""
        return TOOLS

    @server.call_tool()
    async def call_tool(name: str, arguments: dict) -> list[TextContent]:
        """Dispatch an MCP tool call to the appropriate handler."""
        store = MemoryStore(ws)
        try:
            if name == "loom_search_memory":
                result = handle_search_memory(store, arguments)
            elif name == "loom_write_memory":
                result = handle_write_memory(store, arguments, ws)
            elif name == "loom_log_decision":
                result = handle_log_decision(store, arguments, ws)
            elif name == "loom_get_handoff_summary":
                result = handle_get_handoff_summary(store, arguments)
            elif name == "loom_get_context":
                result = handle_get_context(store, ws)
            elif name == "loom_get_state":
                result = get_workspace_state(ws)
            else:
                result = {"error": f"Unknown tool: {name}"}
            return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
        finally:
            store.close()

    return server


async def run_stdio(workspace: Path | None = None) -> None:
    """Run the MCP server over stdio transport."""
    from mcp.server.stdio import stdio_server

    server = create_server(workspace)
    async with stdio_server() as (read, write):
        init_options = server.create_initialization_options()
        await server.run(read, write, init_options)
