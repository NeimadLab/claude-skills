"""HTTP/SSE gateway for remote MCP access with authentication.

Exposes the same MCP tools over SSE transport for remote AI clients
(Claude.ai, ChatGPT, Gemini, CI/CD pipelines).
Also provides REST API endpoints for non-MCP clients.
"""

from __future__ import annotations

import json
import logging
import os
import secrets
from pathlib import Path

from loom.events import emit
from loom.mcp_server import (
    handle_close_session,
    handle_get_context,
    handle_get_handoff_summary,
    handle_get_state,
    handle_log_decision,
    handle_open_session,
    handle_search_memory,
    handle_write_memory,
)
from loom.memory import MemoryStore
from loom.models import Event

logger = logging.getLogger("loom.gateway")


def _get_api_key() -> str | None:
    """Read API key from environment."""
    return os.environ.get("LOOM_API_KEY")


def _authenticate(request) -> bool:
    """Validate Bearer token from request headers."""
    expected = _get_api_key()
    if not expected:
        logger.warning("LOOM_API_KEY not set — gateway is unauthenticated!")
        return True  # No key = open access (dev mode)

    auth = request.headers.get("authorization", "")
    if not auth.startswith("Bearer "):
        return False
    token = auth[7:]
    return secrets.compare_digest(token, expected)


def generate_api_key() -> str:
    """Generate a secure random API key."""
    return secrets.token_hex(32)


def create_app(workspace: Path | None = None):
    """Create the Starlette ASGI app with MCP SSE + REST endpoints."""
    from starlette.applications import Starlette
    from starlette.middleware import Middleware
    from starlette.requests import Request
    from starlette.responses import JSONResponse
    from starlette.routing import Route

    ws = workspace or Path.cwd()

    # ── Auth middleware ──────────────────────────────────────
    async def auth_middleware(request: Request, call_next):
        # Skip auth for health check
        if request.url.path == "/health":
            return await call_next(request)

        if not _authenticate(request):
            ip = request.client.host if request.client else "unknown"
            emit(
                Event(
                    event_type="auth_failed",
                    data={
                        "path": str(request.url.path),
                        "ip": ip,
                    },
                ),
                ws,
            )
            return JSONResponse({"error": "Unauthorized"}, status_code=401)

        return await call_next(request)

    # ── REST endpoints (for ChatGPT Custom GPTs etc.) ───────
    async def health(request: Request) -> JSONResponse:
        """Health check endpoint."""
        return JSONResponse({"status": "ok", "version": "0.2.0"})

    async def api_search(request: Request) -> JSONResponse:
        """Search project memory."""
        body = await request.json()
        store = MemoryStore(ws)
        try:
            result = handle_search_memory(store, body)
            _log_api_call("search_memory", request, ws)
            return JSONResponse(result)
        finally:
            store.close()

    async def api_log_decision(request: Request) -> JSONResponse:
        """Log a decision."""
        body = await request.json()
        store = MemoryStore(ws)
        try:
            result = handle_log_decision(store, body, ws)
            _log_api_call("log_decision", request, ws)
            return JSONResponse(result)
        finally:
            store.close()

    async def api_handoff(request: Request) -> JSONResponse:
        """Get handoff summary."""
        store = MemoryStore(ws)
        try:
            result = handle_get_handoff_summary(store, {"depth": "compact"})
            _log_api_call("get_handoff_summary", request, ws)
            return JSONResponse(result)
        finally:
            store.close()

    async def api_context(request: Request) -> JSONResponse:
        """Get project context."""
        store = MemoryStore(ws)
        try:
            result = handle_get_context(store, ws)
            _log_api_call("get_context", request, ws)
            return JSONResponse(result)
        finally:
            store.close()

    async def api_write_memory(request: Request) -> JSONResponse:
        """Write a memory entry."""
        body = await request.json()
        store = MemoryStore(ws)
        try:
            result = handle_write_memory(store, body, ws)
            _log_api_call("write_memory", request, ws)
            return JSONResponse(result)
        finally:
            store.close()

    # ── MCP over SSE ────────────────────────────────────────
    async def mcp_sse(request: Request):
        """MCP-over-SSE endpoint. Streams MCP protocol messages."""
        from sse_starlette.sse import EventSourceResponse

        # For now, expose a simplified SSE stream that handles
        # JSON-RPC tool calls. Full MCP SDK SSE integration
        # will replace this in v0.3.1.
        async def event_generator():
            # Send initial capabilities
            yield {
                "event": "endpoint",
                "data": json.dumps(
                    {
                        "uri": f"http://{request.headers.get('host', 'localhost')}/mcp/messages",
                    }
                ),
            }

        return EventSourceResponse(event_generator())

    async def mcp_messages(request: Request) -> JSONResponse:
        """Handle MCP JSON-RPC messages over HTTP POST."""
        body = await request.json()
        method = body.get("method", "")
        params = body.get("params", {})
        req_id = body.get("id")

        store = MemoryStore(ws)
        try:
            if method == "initialize":
                result = {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {"tools": {}},
                    "serverInfo": {"name": "loom", "version": "0.2.0"},
                }
            elif method == "tools/list":
                from loom.mcp_server import TOOLS

                result = {"tools": [_tool_to_dict(t) for t in TOOLS]}
            elif method == "tools/call":
                tool_name = params.get("name", "")
                arguments = params.get("arguments", {})
                handler_result = _dispatch_tool(tool_name, arguments, store, ws)
                result = {
                    "content": [{"type": "text", "text": json.dumps(handler_result)}],
                    "isError": False,
                }
                _log_api_call(tool_name, request, ws)
            else:
                result = {"error": f"Unknown method: {method}"}

            response = {"jsonrpc": "2.0", "id": req_id, "result": result}
            return JSONResponse(response)
        finally:
            store.close()

    # ── Routes ──────────────────────────────────────────────
    routes = [
        Route("/health", health, methods=["GET"]),
        Route("/api/search", api_search, methods=["POST"]),
        Route("/api/log-decision", api_log_decision, methods=["POST"]),
        Route("/api/handoff", api_handoff, methods=["GET"]),
        Route("/api/context", api_context, methods=["GET"]),
        Route("/api/write-memory", api_write_memory, methods=["POST"]),
        Route("/mcp", mcp_sse, methods=["GET"]),
        Route("/mcp/messages", mcp_messages, methods=["POST"]),
    ]

    from starlette.middleware.base import BaseHTTPMiddleware

    app = Starlette(
        routes=routes,
        middleware=[Middleware(BaseHTTPMiddleware, dispatch=auth_middleware)],
    )

    return app


def _dispatch_tool(name: str, arguments: dict, store: MemoryStore, workspace: Path) -> dict:
    """Route a tool call to the right handler."""
    handlers = {
        "loom_search_memory": lambda: handle_search_memory(store, arguments),
        "loom_write_memory": lambda: handle_write_memory(store, arguments, workspace),
        "loom_log_decision": lambda: handle_log_decision(store, arguments, workspace),
        "loom_get_handoff_summary": lambda: handle_get_handoff_summary(store, arguments),
        "loom_get_context": lambda: handle_get_context(store, workspace),
        "loom_get_state": lambda: handle_get_state(workspace),
        "loom_open_session": lambda: handle_open_session(arguments, workspace),
        "loom_close_session": lambda: handle_close_session(arguments, workspace),
    }
    handler = handlers.get(name)
    if handler:
        return handler()
    return {"error": f"Unknown tool: {name}"}


def _tool_to_dict(tool) -> dict:
    """Convert an MCP Tool object to a JSON-serializable dict."""
    return {
        "name": tool.name,
        "description": tool.description,
        "inputSchema": tool.inputSchema,
    }


def _log_api_call(tool_name: str, request, workspace: Path) -> None:
    """Log an API call to the event log."""
    emit(
        Event(
            event_type="gateway_tool_call",
            actor="remote",
            data={
                "tool": tool_name,
                "ip": request.client.host if request.client else "unknown",
                "method": request.method,
            },
        ),
        workspace,
    )


def run_gateway(workspace: Path | None = None, host: str = "0.0.0.0", port: int = 8443) -> None:
    """Run the gateway server."""
    import uvicorn

    app = create_app(workspace)

    api_key = _get_api_key()
    if api_key:
        logger.info("Gateway starting with API key authentication")
    else:
        logger.warning("Gateway starting WITHOUT authentication (set LOOM_API_KEY)")

    emit(
        Event(
            event_type="gateway_started",
            data={"host": host, "port": port, "authenticated": bool(api_key)},
        ),
        workspace or Path.cwd(),
    )

    uvicorn.run(app, host=host, port=port, log_level="info")
