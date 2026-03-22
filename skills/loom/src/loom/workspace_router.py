"""Multi-workspace router — serve multiple projects from one gateway.

Manages a registry of workspaces and routes requests to the correct one
based on workspace ID in the request path or header.

Architecture:
    Client → Gateway → Router → Workspace A (.loom/)
                              → Workspace B (.loom/)
                              → Workspace C (.loom/)

Each workspace has its own memory.db, events.jsonl, sessions, and policies.
The router adds a thin layer that selects which workspace handles a request.
"""

from __future__ import annotations

import json
from pathlib import Path

from loom.constants import loom_dir

REGISTRY_FILE = "workspaces.json"


class WorkspaceRouter:
    """Manage and route between multiple workspaces."""

    def __init__(self, config_dir: Path | None = None):
        """Initialize the router.

        Args:
            config_dir: Directory to store the workspace registry.
                        Defaults to ~/.loom/ (global config).
        """
        self.config_dir = config_dir or Path.home() / ".loom"
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self._registry_path = self.config_dir / REGISTRY_FILE

    def _load_registry(self) -> dict:
        """Load workspace registry. Returns {workspace_id: {path, name, ...}}."""
        if not self._registry_path.exists():
            return {}
        return json.loads(self._registry_path.read_text())

    def _save_registry(self, registry: dict) -> None:
        """Save workspace registry."""
        self._registry_path.write_text(json.dumps(registry, indent=2) + "\n")

    def register(self, workspace_path: Path, name: str | None = None) -> dict:
        """Register a workspace with the router.

        Args:
            workspace_path: Absolute path to the project directory containing .loom/
            name: Human-friendly name (defaults to directory name)

        Returns: {id, name, path, status}
        """
        ws = workspace_path.resolve()
        ld = loom_dir(ws)

        if not ld.exists():
            return {"error": f"No .loom/ found at {ws}. Run `loom init` first."}

        registry = self._load_registry()

        # Generate ID from path hash (deterministic)
        import hashlib

        ws_id = hashlib.sha256(str(ws).encode()).hexdigest()[:12]
        ws_name = name or ws.name

        registry[ws_id] = {
            "path": str(ws),
            "name": ws_name,
            "registered_at": _now(),
        }

        self._save_registry(registry)

        return {"id": ws_id, "name": ws_name, "path": str(ws), "status": "registered"}

    def unregister(self, workspace_id: str) -> bool:
        """Remove a workspace from the router."""
        registry = self._load_registry()
        if workspace_id not in registry:
            return False
        del registry[workspace_id]
        self._save_registry(registry)
        return True

    def list_workspaces(self) -> list[dict]:
        """List all registered workspaces with status."""
        registry = self._load_registry()
        result = []

        for ws_id, info in registry.items():
            ws_path = Path(info["path"])
            ld = loom_dir(ws_path)
            healthy = ld.exists() and (ld / "memory.db").exists()

            result.append(
                {
                    "id": ws_id,
                    "name": info["name"],
                    "path": info["path"],
                    "healthy": healthy,
                    "registered_at": info.get("registered_at", "unknown"),
                }
            )

        return result

    def resolve(self, workspace_id: str) -> Path | None:
        """Resolve a workspace ID to its path. Returns None if not found."""
        registry = self._load_registry()
        info = registry.get(workspace_id)
        if not info:
            return None

        ws_path = Path(info["path"])
        if not loom_dir(ws_path).exists():
            return None

        return ws_path

    def resolve_by_name(self, name: str) -> Path | None:
        """Resolve a workspace by name (first match)."""
        registry = self._load_registry()
        for info in registry.values():
            if info["name"].lower() == name.lower():
                ws_path = Path(info["path"])
                if loom_dir(ws_path).exists():
                    return ws_path
        return None

    def get_default(self) -> Path | None:
        """Get the default workspace (first registered, or CWD if it has .loom/)."""
        # Check CWD first
        cwd = Path.cwd()
        if loom_dir(cwd).exists():
            return cwd

        # Otherwise first registered
        registry = self._load_registry()
        for info in registry.values():
            ws_path = Path(info["path"])
            if loom_dir(ws_path).exists():
                return ws_path

        return None


def _now() -> str:
    """Current UTC timestamp."""
    from datetime import UTC, datetime

    return datetime.now(UTC).isoformat()


def create_multi_workspace_app(config_dir: Path | None = None):
    """Create a Starlette app that routes to multiple workspaces.

    Routes:
        GET  /health                          → global health
        GET  /workspaces                      → list registered workspaces
        POST /workspaces/register             → register a workspace
        *    /w/{workspace_id}/api/*           → workspace-specific REST API
        *    /w/{workspace_id}/mcp             → workspace-specific MCP SSE
        *    /w/{workspace_id}/mcp/messages    → workspace-specific MCP messages
    """
    from starlette.applications import Starlette
    from starlette.requests import Request
    from starlette.responses import JSONResponse
    from starlette.routing import Route

    router = WorkspaceRouter(config_dir)

    async def health(request: Request) -> JSONResponse:
        """Global health check."""
        workspaces = router.list_workspaces()
        return JSONResponse(
            {
                "status": "ok",
                "version": "0.3.0",
                "mode": "multi-workspace",
                "workspaces": len(workspaces),
                "healthy": sum(1 for w in workspaces if w["healthy"]),
            }
        )

    async def list_ws(request: Request) -> JSONResponse:
        """List all registered workspaces."""
        return JSONResponse(router.list_workspaces())

    async def register_ws(request: Request) -> JSONResponse:
        """Register a workspace."""
        body = await request.json()
        path = Path(body.get("path", ""))
        name = body.get("name")
        result = router.register(path, name)
        status = 200 if "id" in result else 400
        return JSONResponse(result, status_code=status)

    async def workspace_proxy(request: Request) -> JSONResponse:
        """Route request to the correct workspace's gateway."""
        ws_id = request.path_params.get("workspace_id", "")
        ws_path = router.resolve(ws_id)

        if not ws_path:
            return JSONResponse(
                {"error": f"Workspace not found: {ws_id}"},
                status_code=404,
            )

        # Delegate to the workspace's gateway app
        from loom.gateway import create_app

        app = create_app(ws_path)

        # Rewrite path: /w/{id}/api/search → /api/search
        sub_path = request.url.path.split(f"/w/{ws_id}", 1)[-1]

        # Create a sub-request scope
        from starlette.testclient import TestClient

        client = TestClient(app)

        if request.method == "GET":
            resp = client.get(sub_path, headers=dict(request.headers))
        elif request.method == "POST":
            body = await request.body()
            resp = client.post(
                sub_path,
                content=body,
                headers=dict(request.headers),
            )
        else:
            return JSONResponse({"error": "Method not allowed"}, status_code=405)

        return JSONResponse(resp.json(), status_code=resp.status_code)

    routes = [
        Route("/health", health, methods=["GET"]),
        Route("/workspaces", list_ws, methods=["GET"]),
        Route("/workspaces/register", register_ws, methods=["POST"]),
        Route("/w/{workspace_id:path}", workspace_proxy, methods=["GET", "POST"]),
    ]

    return Starlette(routes=routes)
