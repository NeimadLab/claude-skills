"""Tests for project templates and status command."""

import json
import subprocess
from pathlib import Path

from loom.memory import MemoryStore


def _init(tmp_path: Path) -> Path:
    (tmp_path / ".loom").mkdir()
    MemoryStore(tmp_path).close()
    return tmp_path


def loom(*args: str, cwd: Path, check: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(["loom", *args], cwd=str(cwd), capture_output=True, text=True, timeout=15)


# ── Templates ─────────────────────────────────────────────────


class TestTemplates:
    def test_list_templates(self):
        from loom.templates import list_templates

        templates = list_templates()
        assert len(templates) >= 5
        names = {t["name"] for t in templates}
        assert "web-backend" in names
        assert "cli-tool" in names
        assert "data-pipeline" in names

    def test_apply_template(self, tmp_path):
        ws = _init(tmp_path)
        from loom.templates import apply_template

        result = apply_template("web-backend", ws)
        assert result["entries_added"] >= 5
        assert result["template"] == "web-backend"

        store = MemoryStore(ws)
        entries = store.search("API")
        assert len(entries) >= 1
        # Template entries are validated
        assert all(e["status"] == "validated" for e in entries)
        store.close()

    def test_apply_unknown_template(self, tmp_path):
        ws = _init(tmp_path)
        from loom.templates import apply_template

        result = apply_template("nonexistent", ws)
        assert "error" in result

    def test_apply_cli_tool_template(self, tmp_path):
        ws = _init(tmp_path)
        from loom.templates import apply_template

        result = apply_template("cli-tool", ws)
        assert result["entries_added"] >= 4

        store = MemoryStore(ws)
        entries = store.search("exit codes")
        assert len(entries) >= 1
        store.close()

    def test_template_entries_are_tagged(self, tmp_path):
        ws = _init(tmp_path)
        from loom.templates import apply_template

        apply_template("infra-devops", ws)

        store = MemoryStore(ws)
        entries = store.recent(20)
        # All entries should have the template name as a tag
        for e in entries:
            assert "infra-devops" in e.get("tags", ""), f"Missing tag in: {e['content'][:40]}"
        store.close()


# ── CLI: templates list ───────────────────────────────────────


class TestTemplatesCLI:
    def test_templates_list(self, tmp_path):
        r = loom("templates", "list", cwd=tmp_path)
        assert r.returncode == 0
        assert "web-backend" in r.stdout

    def test_templates_apply(self, tmp_path):
        (tmp_path / "pyproject.toml").write_text("[project]\n")
        loom("init", "--non-interactive", cwd=tmp_path)
        r = loom("templates", "apply", "web-backend", cwd=tmp_path)
        assert r.returncode == 0
        assert "Template applied" in r.stdout


# ── CLI: status ───────────────────────────────────────────────


class TestStatusCLI:
    def test_status_json(self, tmp_path):
        (tmp_path / "pyproject.toml").write_text("[project]\n")
        loom("init", "--non-interactive", cwd=tmp_path)

        r = loom("status", "--json", cwd=tmp_path)
        assert r.returncode == 0
        data = json.loads(r.stdout)
        assert "state" in data
        assert "doctor" in data
        assert "session" in data
        assert "write_token" in data
        assert "team_mode" in data

    def test_status_rich(self, tmp_path):
        (tmp_path / "pyproject.toml").write_text("[project]\n")
        loom("init", "--non-interactive", cwd=tmp_path)

        r = loom("status", cwd=tmp_path)
        assert r.returncode == 0
        assert "Loom Status" in r.stdout

    def test_status_shows_session(self, tmp_path):
        (tmp_path / "pyproject.toml").write_text("[project]\n")
        loom("init", "--non-interactive", cwd=tmp_path)
        loom("session", "open", "claude-code", cwd=tmp_path)

        r = loom("status", "--json", cwd=tmp_path)
        data = json.loads(r.stdout)
        assert data["session"]["active"] is not None
        assert data["session"]["active"]["actor"] == "claude-code"


# ── CLI: init non-interactive with template ───────────────────


class TestInitInteractive:
    def test_init_non_interactive(self, tmp_path):
        (tmp_path / "pyproject.toml").write_text("[project]\n")
        r = loom("init", "--non-interactive", cwd=tmp_path)
        assert r.returncode == 0
        assert "Workspace initialized" in r.stdout

    def test_init_with_template(self, tmp_path):
        (tmp_path / "pyproject.toml").write_text("[project]\n")
        r = loom("init", "--non-interactive", "-t", "web-backend", cwd=tmp_path)
        assert r.returncode == 0
        assert "Template applied" in r.stdout

    def test_init_auto_imports_claude_md(self, tmp_path):
        (tmp_path / "pyproject.toml").write_text("[project]\n")
        (tmp_path / "CLAUDE.md").write_text("- Use FastAPI for the backend\n- Always write tests\n")
        r = loom("init", "--non-interactive", cwd=tmp_path)
        assert r.returncode == 0
        assert "Imported" in r.stdout

    def test_init_auto_imports_cursorrules(self, tmp_path):
        (tmp_path / "package.json").write_text('{"name":"test"}')
        (tmp_path / ".cursorrules").write_text("Always use TypeScript strict mode\n")
        r = loom("init", "--non-interactive", cwd=tmp_path)
        assert r.returncode == 0
        assert "Imported" in r.stdout or "cursorrules" in r.stdout.lower()
