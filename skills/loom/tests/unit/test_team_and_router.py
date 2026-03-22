"""Tests for team auth and multi-workspace router."""

from pathlib import Path

from loom.memory import MemoryStore


def _init(tmp_path: Path) -> Path:
    (tmp_path / ".loom").mkdir()
    MemoryStore(tmp_path).close()  # init db
    return tmp_path


# ── Team Auth ─────────────────────────────────────────────────


class TestTeamAuth:
    def test_add_user(self, tmp_path):
        ws = _init(tmp_path)
        from loom.team import add_user

        result = add_user("alice", "admin", ws)
        assert result["name"] == "alice"
        assert result["role"] == "admin"
        assert len(result["api_key"]) == 64

    def test_list_users(self, tmp_path):
        ws = _init(tmp_path)
        from loom.team import add_user, list_users

        add_user("alice", "admin", ws)
        add_user("bob", "member", ws)

        users = list_users(ws)
        assert len(users) == 2
        names = {u["name"] for u in users}
        assert names == {"alice", "bob"}

    def test_remove_user(self, tmp_path):
        ws = _init(tmp_path)
        from loom.team import add_user, list_users, remove_user

        result = add_user("alice", "admin", ws)
        assert remove_user(result["user_id"], ws) is True
        assert len(list_users(ws)) == 0

    def test_remove_nonexistent(self, tmp_path):
        ws = _init(tmp_path)
        from loom.team import remove_user

        assert remove_user("fake-id", ws) is False

    def test_authenticate_valid_key(self, tmp_path):
        ws = _init(tmp_path)
        from loom.team import add_user, authenticate

        result = add_user("alice", "admin", ws)
        user = authenticate(result["api_key"], ws)
        assert user is not None
        assert user["name"] == "alice"

    def test_authenticate_invalid_key(self, tmp_path):
        ws = _init(tmp_path)
        from loom.team import add_user, authenticate

        add_user("alice", "admin", ws)
        user = authenticate("invalid-key", ws)
        assert user is None

    def test_solo_mode_no_keys(self, tmp_path):
        ws = _init(tmp_path)
        from loom.team import authenticate, is_team_mode

        assert is_team_mode(ws) is False
        assert authenticate("any-key", ws) is None

    def test_team_mode_with_keys(self, tmp_path):
        ws = _init(tmp_path)
        from loom.team import add_user, is_team_mode

        add_user("alice", "admin", ws)
        assert is_team_mode(ws) is True

    def test_permissions(self, tmp_path):
        from loom.team import check_permission

        admin = {"role": "admin"}
        member = {"role": "member"}
        viewer = {"role": "viewer"}

        assert check_permission(admin, "admin") is True
        assert check_permission(admin, "write") is True
        assert check_permission(member, "write") is True
        assert check_permission(member, "admin") is False
        assert check_permission(viewer, "read") is True
        assert check_permission(viewer, "write") is False
        assert check_permission(None, "write") is True  # solo mode


# ── Workspace Router ──────────────────────────────────────────


class TestWorkspaceRouter:
    def test_register_workspace(self, tmp_path):
        ws = _init(tmp_path)
        from loom.workspace_router import WorkspaceRouter

        router = WorkspaceRouter(tmp_path / "config")
        result = router.register(ws, "alpha")
        assert result["name"] == "alpha"
        assert "id" in result

    def test_list_workspaces(self, tmp_path):
        ws1 = tmp_path / "proj1"
        ws1.mkdir()
        _init(ws1)
        ws2 = tmp_path / "proj2"
        ws2.mkdir()
        _init(ws2)

        from loom.workspace_router import WorkspaceRouter

        router = WorkspaceRouter(tmp_path / "config")
        router.register(ws1, "Alpha")
        router.register(ws2, "Beta")

        workspaces = router.list_workspaces()
        assert len(workspaces) == 2
        names = {w["name"] for w in workspaces}
        assert names == {"Alpha", "Beta"}

    def test_resolve_workspace(self, tmp_path):
        ws = _init(tmp_path)
        from loom.workspace_router import WorkspaceRouter

        router = WorkspaceRouter(tmp_path / "config")
        result = router.register(ws)
        resolved = router.resolve(result["id"])
        assert resolved == ws.resolve()

    def test_resolve_nonexistent(self, tmp_path):
        from loom.workspace_router import WorkspaceRouter

        router = WorkspaceRouter(tmp_path / "config")
        assert router.resolve("fake-id") is None

    def test_unregister(self, tmp_path):
        ws = _init(tmp_path)
        from loom.workspace_router import WorkspaceRouter

        router = WorkspaceRouter(tmp_path / "config")
        result = router.register(ws)
        assert router.unregister(result["id"]) is True
        assert len(router.list_workspaces()) == 0

    def test_register_no_loom_dir(self, tmp_path):
        bare = tmp_path / "no-loom"
        bare.mkdir()

        from loom.workspace_router import WorkspaceRouter

        router = WorkspaceRouter(tmp_path / "config")
        result = router.register(bare)
        assert "error" in result

    def test_health_status(self, tmp_path):
        ws = _init(tmp_path)
        from loom.workspace_router import WorkspaceRouter

        router = WorkspaceRouter(tmp_path / "config")
        router.register(ws, "healthy-project")

        workspaces = router.list_workspaces()
        assert workspaces[0]["healthy"] is True

    def test_resolve_by_name(self, tmp_path):
        ws = _init(tmp_path)
        from loom.workspace_router import WorkspaceRouter

        router = WorkspaceRouter(tmp_path / "config")
        router.register(ws, "My Project")

        resolved = router.resolve_by_name("my project")
        assert resolved == ws.resolve()
