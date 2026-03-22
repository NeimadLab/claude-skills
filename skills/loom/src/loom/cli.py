"""Loom command-line interface."""

from __future__ import annotations

import asyncio
import json
import os
import sys
from pathlib import Path

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from loom import __version__
from loom.constants import MCP_CLIENT_CONFIGS, ensure_loom_dir, loom_dir
from loom.events import emit
from loom.models import Event
from loom.runtime import compute_identity, detect_project_type, load_identity, save_identity
from loom.state import doctor_check, get_workspace_state

console = Console()


def _require_workspace() -> Path:
    """Check that we're in an initialized workspace, exit if not."""
    root = Path.cwd()
    if not loom_dir(root).exists():
        console.print("[red]No workspace found.[/] Run `loom init` first.")
        sys.exit(1)
    return root


def _get_active_actor(workspace: Path) -> str:
    """Get the actor name from the active session, or 'cli' if no session."""
    try:
        from loom.sessions import SessionStore

        store = SessionStore(workspace)
        active = store.get_active()
        store.close()
        if active:
            return active["actor"]
    except Exception:
        pass
    return "cli"


@click.group()
@click.version_option(__version__, prog_name="loom")
def main():
    """Loom — Weave context across AI tools."""
    pass


@main.command()
@click.option("--force", is_flag=True, help="Reinitialize even if .loom/ exists")
@click.option(
    "--template", "-t", default=None, help="Apply a domain template (web-backend, cli-tool, etc.)"
)
@click.option(
    "--connect", "-c", default=None, help="Auto-connect an AI tool (claude-code, cursor, windsurf)"
)
@click.option("--non-interactive", is_flag=True, help="Skip interactive prompts")
def init(force: bool, template: str | None, connect: str | None, non_interactive: bool):
    """Initialize Loom workspace in the current directory."""
    root = Path.cwd()
    ld = loom_dir(root)

    if ld.exists() and not force:
        console.print("[yellow]Workspace already initialized.[/] Use --force to reinitialize.")
        return

    ptype = detect_project_type(root)
    if ptype:
        console.print(f"Detected project type: [bold cyan]{ptype}[/]")
    else:
        console.print(
            "[yellow]Could not detect project type.[/] Initializing as generic workspace."
        )

    ensure_loom_dir(root)

    identity = compute_identity(root)
    save_identity(identity, root)
    console.print(f"Runtime identity: [dim]{identity.identity_hash}[/]")

    from loom.memory import MemoryStore

    store = MemoryStore(root)
    store.close()
    console.print("Memory database created.")

    # Add .loom/ to .gitignore
    gitignore = root / ".gitignore"
    if gitignore.exists():
        content = gitignore.read_text()
        if ".loom/" not in content:
            with open(gitignore, "a") as f:
                f.write("\n# Loom workspace state\n.loom/\n")
    else:
        gitignore.write_text("# Loom workspace state\n.loom/\n")

    emit(
        Event(
            event_type="workspace_initialized",
            data={"project_type": ptype or "unknown", "identity": identity.identity_hash},
        ),
        root,
    )

    # ── Template ────────────────────────────────────────────
    if template:
        from loom.templates import apply_template

        result = apply_template(template, root)
        if "error" in result:
            console.print(f"[red]{result['error']}[/]")
        else:
            console.print(
                f"[green]\u2713 Template applied:[/] {template} ({result['entries_added']} entries)"
            )
    elif not non_interactive:
        # Interactive: offer templates
        from loom.templates import list_templates

        templates = list_templates()
        console.print("\n[bold]Available templates:[/]")
        for i, t in enumerate(templates, 1):
            console.print(f"  {i}. {t['name']:20s} {t['description']}")
        console.print("  0. Skip (no template)")

        choice = click.prompt("Apply a template?", type=int, default=0, show_default=True)
        if 1 <= choice <= len(templates):
            from loom.templates import apply_template

            result = apply_template(templates[choice - 1]["name"], root)
            console.print(
                f"[green]\u2713 Template applied:[/] {templates[choice - 1]['name']} "
                f"({result['entries_added']} entries)"
            )

    # ── Auto-import CLAUDE.md if present ────────────────────
    claude_md = root / "CLAUDE.md"
    if claude_md.exists() and (
        non_interactive or click.confirm("Found CLAUDE.md — import into Loom memory?", default=True)
    ):
        from loom.import_export import import_claude_md

        result = import_claude_md(claude_md, root)
        console.print(f"[green]\u2713 Imported {result['imported']} entries[/] from CLAUDE.md")

    # ── Auto-import .cursorrules if present ──────────────────
    cursorrules = root / ".cursorrules"
    if cursorrules.exists() and (
        non_interactive
        or click.confirm("Found .cursorrules — import into Loom memory?", default=True)
    ):
        from loom.import_export import import_cursorrules

        result = import_cursorrules(cursorrules, root)
        console.print(f"[green]\u2713 Imported {result['imported']} entries[/] from .cursorrules")

    # ── Connect AI tool ─────────────────────────────────────
    tool_to_connect = connect
    if not tool_to_connect and not non_interactive:
        tools = ["claude-code", "cursor", "windsurf", "skip"]
        console.print("\n[bold]Connect an AI tool:[/]")
        for i, t in enumerate(tools, 1):
            console.print(f"  {i}. {t}")

        choice = click.prompt("Connect?", type=int, default=1, show_default=True)
        if 1 <= choice <= len(tools) - 1:
            tool_to_connect = tools[choice - 1]

    if tool_to_connect and tool_to_connect != "skip":
        _do_connect(root, tool_to_connect)

    # ── Summary ─────────────────────────────────────────────
    from loom.memory import MemoryStore

    s = MemoryStore(root)
    mem_count = s.count()
    s.close()

    console.print(
        Panel(
            "[bold green]\u2713 Workspace initialized[/]\n\n"
            f"  Project type:    {ptype or 'generic'}\n"
            f"  Identity:        {identity.identity_hash}\n"
            f"  Memory entries:  {mem_count}\n"
            f"  .loom/ created:  {ld}\n"
            + (
                f"\n  Connected to:    [cyan]{tool_to_connect}[/]"
                if tool_to_connect and tool_to_connect != "skip"
                else ""
            ),
            title="Loom",
            border_style="green",
        )
    )


def _do_connect(root: Path, client: str, remote: str | None = None):
    """Internal helper to connect an AI tool (shared by init and connect commands)."""
    config = MCP_CLIENT_CONFIGS.get(client)
    if not config:
        console.print(f"[red]Unknown client: {client}[/]")
        return

    if remote:
        mcp_entry = {
            "type": "sse",
            "url": remote.rstrip("/") + "/mcp",
            "headers": {"Authorization": "Bearer YOUR_API_KEY"},
        }
    else:
        mcp_entry = {"command": "loom", "args": ["mcp", "serve"]}

    config_path = None
    for candidate in config["path_candidates"]:
        p = Path(candidate).expanduser()
        if p.exists():
            config_path = p
            break
    if config_path is None:
        config_path = Path(config["path_candidates"][0]).expanduser()

    existing = json.loads(config_path.read_text()) if config_path.exists() else {}
    servers = existing.get(config["key"], {})
    servers["loom"] = mcp_entry
    existing[config["key"]] = servers

    config_path.parent.mkdir(parents=True, exist_ok=True)
    config_path.write_text(json.dumps(existing, indent=2) + "\n")

    transport = "SSE (remote)" if remote else "stdio (local)"
    console.print(f"  [green]\u2713[/] {client} configured ({transport})")


@main.command()
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
def resume(as_json: bool):
    """Resume workspace — verify identity, restore caches, refresh state."""
    root = _require_workspace()
    stored = load_identity(root)

    if not stored:
        if as_json:
            click.echo(json.dumps({"error": "No runtime manifest found"}))
        else:
            console.print("[red]No runtime manifest found.[/] Run `loom init` first.")
        sys.exit(1)

    live = compute_identity(root)
    drift = live.identity_hash != stored.identity_hash

    from loom.docker import restore_caches

    cache_report = restore_caches(root)
    ws_state = get_workspace_state(root)

    emit(
        Event(
            event_type="workspace_resumed",
            data={"drift": drift, "caches_restored": cache_report.get("volumes_restored", 0)},
        ),
        root,
    )

    if as_json:
        click.echo(
            json.dumps(
                {
                    "drift": drift,
                    "stored_identity": stored.identity_hash,
                    "live_identity": live.identity_hash,
                    "docker": cache_report,
                    "memory_entries": ws_state["memory_entries"],
                    "event_count": ws_state["event_count"],
                },
                indent=2,
                default=str,
            )
        )
        return

    if not drift:
        console.print("[green]\u2713 Runtime identity matches \u2014 no drift detected.[/]")
    else:
        console.print("[yellow]\u26a0 Runtime drift detected[/]")
        console.print(f"  Stored: {stored.identity_hash}")
        console.print(f"  Live:   {live.identity_hash}")
        console.print(
            "  Run [dim]loom doctor[/] for details or [dim]loom init --force[/] to reinitialize."
        )

    if cache_report["docker_available"]:
        if cache_report["volumes_restored"] > 0:
            console.print(
                f"  Docker caches: [green]{cache_report['volumes_restored']} volume(s) restored[/]"
            )
        if cache_report["volumes_created"] > 0:
            console.print(
                f"  Docker caches: [cyan]{cache_report['volumes_created']} volume(s) created[/]"
            )
    else:
        console.print("  Docker: [dim]not available (cache restore skipped)[/]")

    console.print(f"  Memory entries: {ws_state['memory_entries']}")
    console.print(f"  Events logged:  {ws_state['event_count']}")
    console.print("[green]\u2713 Workspace resumed.[/]")


@main.command()
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
def doctor(as_json: bool):
    """Run workspace health checks."""
    result = doctor_check()

    if as_json:
        click.echo(json.dumps(result, indent=2))
        if not result["healthy"]:
            sys.exit(1)
        return

    table = Table(title="Loom Doctor", show_header=True)
    table.add_column("Check", style="bold")
    table.add_column("Status", justify="center")
    table.add_column("Detail")

    for c in result["checks"]:
        status = "[green]\u2713[/]" if c["ok"] else "[red]\u2717[/]"
        table.add_row(c["name"], status, c["detail"])

    console.print(table)
    console.print(f"\n[{'green' if result['healthy'] else 'red'}]{result['summary']}[/]")
    if not result["healthy"]:
        sys.exit(1)


@main.command()
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
def state(as_json: bool):
    """Show workspace operational state."""
    root = _require_workspace()
    s = get_workspace_state(root)

    if as_json:
        click.echo(json.dumps(s, indent=2, default=str))
        return

    console.print(
        Panel(
            f"  Project type:     [cyan]{s['project_type'] or 'unknown'}[/]\n"
            f"  Runtime identity: [dim]{s['runtime_identity'] or 'none'}[/]\n"
            f"  Identity drift:   {s['identity_drift'] or 'unknown'}\n"
            f"  Memory entries:   {s['memory_entries']}\n"
            f"  Events logged:    {s['event_count']}\n"
            f"  Git branch:       {s['git_branch'] or 'N/A'}\n"
            f"  Git dirty:        {s['git_dirty'] if s['git_dirty'] is not None else 'N/A'}\n"
            f"  File count:       {s['file_count']}",
            title="Workspace State",
            border_style="blue",
        )
    )


# ────────────────────────────────────────────
# NEW: loom search
# ────────────────────────────────────────────


@main.command()
@click.argument("query")
@click.option(
    "-t", "--type", "type_filter", default=None, help="Filter: decision|goal|risk|note|observation"
)
@click.option(
    "-s",
    "--status",
    "status_filter",
    default=None,
    help="Filter: hypothesis|validated|obsolete|rejected",
)
@click.option("-a", "--actor", "actor_filter", default=None, help="Filter by actor name")
@click.option("-n", "--limit", default=10, help="Max results")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
def search(
    query: str,
    type_filter: str | None,
    status_filter: str | None,
    actor_filter: str | None,
    limit: int,
    as_json: bool,
):
    """Search project memory."""
    root = _require_workspace()
    from loom.memory import MemoryStore

    store = MemoryStore(root)
    results = store.search(
        query,
        limit=limit,
        type_filter=type_filter,
        status_filter=status_filter,
        actor_filter=actor_filter,
    )
    store.close()

    if as_json:
        click.echo(json.dumps(results, indent=2, default=str))
        return

    if not results:
        console.print(f"[dim]No results for '{query}'.[/]")
        return

    table = Table(title=f"Memory search: {query}", show_header=True)
    table.add_column("Type", style="cyan", width=10)
    table.add_column("Status", width=10)
    table.add_column("Content")
    table.add_column("When", style="dim", width=12)

    for r in results:
        status_style = {
            "hypothesis": "yellow",
            "validated": "green",
            "obsolete": "dim",
            "rejected": "red",
        }.get(r["status"], "")
        table.add_row(
            r["type"],
            f"[{status_style}]{r['status']}[/]",
            r["content"][:80] + ("..." if len(r["content"]) > 80 else ""),
            r["timestamp"][:10],
        )

    console.print(table)
    console.print(f"[dim]{len(results)} result(s)[/]")


# ────────────────────────────────────────────
# NEW: loom log
# ────────────────────────────────────────────


@main.command()
@click.argument("decision")
@click.option("-r", "--rationale", default="", help="Why this was decided")
@click.option("--tags", default="", help="Comma-separated tags")
def log(decision: str, rationale: str, tags: str):
    """Log a decision to project memory."""
    root = _require_workspace()
    from loom.memory import MemoryStore
    from loom.models import MemoryEntry, MemoryType

    actor = _get_active_actor(root)
    store = MemoryStore(root)
    tag_list = [t.strip() for t in tags.split(",") if t.strip()] if tags else []
    entry = MemoryEntry(
        type=MemoryType.DECISION,
        content=decision,
        rationale=rationale or None,
        tags=tag_list,
        actor=actor,
    )
    store.write(entry)
    store.close()

    emit(
        Event(event_type="decision_logged", actor=actor, data={"entry_id": entry.id}),
        root,
    )
    console.print(f"[green]\u2713 Decision logged:[/] {decision[:60]}")
    console.print(f"  ID: [dim]{entry.id}[/]  Status: [yellow]hypothesis[/]")


# ────────────────────────────────────────────
# NEW: loom events
# ────────────────────────────────────────────


@main.command()
@click.option("-n", "--count", "n", default=20, help="Number of events to show")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
def events(n: int, as_json: bool):
    """Show recent events from the workspace log."""
    root = _require_workspace()
    from loom.events import tail

    evts = tail(n, root)

    if as_json:
        click.echo(json.dumps(evts, indent=2, default=str))
        return

    if not evts:
        console.print("[dim]No events yet.[/]")
        return

    table = Table(title="Recent Events", show_header=True)
    table.add_column("Time", style="dim", width=20)
    table.add_column("Event", style="cyan")
    table.add_column("Actor", width=12)
    table.add_column("Data")

    for e in reversed(evts):  # oldest first
        data_str = json.dumps(e.get("data", {}), separators=(",", ":"))
        if len(data_str) > 50:
            data_str = data_str[:47] + "..."
        table.add_row(
            e.get("timestamp", "")[:19],
            e.get("event_type", ""),
            e.get("actor") or "-",
            data_str,
        )

    console.print(table)


# ────────────────────────────────────────────
# loom connect
# ────────────────────────────────────────────


@main.command()
@click.argument("client", type=click.Choice(["claude-code", "cursor", "windsurf"]))
@click.option("--remote", default=None, help="Remote Loom server URL")
def connect(client: str, remote: str | None):
    """Generate and install MCP configuration for an AI tool."""
    root = Path.cwd()
    _do_connect(root, client, remote)
    console.print(f"\n  Restart [bold]{client}[/] to activate the connection.")


# ────────────────────────────────────────────
# loom status (the one-liner)
# ────────────────────────────────────────────


@main.command()
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
def status(as_json: bool):
    """One-liner workspace overview: state + doctor + session + token."""
    root = _require_workspace()

    ws_state = get_workspace_state(root)

    from loom import write_token
    from loom.sessions import SessionStore

    tok = write_token.status(root)

    try:
        ss = SessionStore(root)
        active_session = ss.get_active()
        session_count = len(ss.list_sessions(100))
        ss.close()
    except Exception:
        active_session = None
        session_count = 0

    result = doctor_check()

    from loom.team import is_team_mode

    team = is_team_mode(root)

    if as_json:
        click.echo(
            json.dumps(
                {
                    "state": ws_state,
                    "doctor": result,
                    "session": {
                        "active": active_session,
                        "total": session_count,
                    },
                    "write_token": tok,
                    "team_mode": team,
                },
                indent=2,
                default=str,
            )
        )
        return

    # Compact one-screen summary
    healthy = result["healthy"]
    health_icon = "[green]\u2713[/]" if healthy else "[red]\u2717[/]"
    health_detail = f"{sum(1 for c in result['checks'] if c['ok'])}/{len(result['checks'])} checks"

    session_text = (
        f"[green]{active_session['actor']}[/] ({active_session.get('model_name', '?')})"
        if active_session
        else "[dim]none[/]"
    )

    token_text = (
        f"[yellow]held by {tok['actor']}[/] ({tok.get('remaining_seconds', 0)}s)"
        if tok.get("held")
        else "[green]free[/]"
    )

    mode_text = "[cyan]team[/]" if team else "solo"

    console.print(
        Panel(
            f"  Project:   [cyan]{ws_state.get('project_type', '?')}[/]  "
            f"  Identity: [dim]{(ws_state.get('runtime_identity') or '?')[:12]}[/]  "
            f"  Branch: {ws_state.get('git_branch') or 'N/A'}\n"
            f"  Health:    {health_icon} {health_detail}  "
            f"  Memory: [bold]{ws_state.get('memory_entries', 0)}[/] entries  "
            f"  Events: {ws_state.get('event_count', 0)}\n"
            f"  Session:   {session_text}  "
            f"  Token: {token_text}  "
            f"  Mode: {mode_text}"
            + (f"  Sessions: {session_count} total" if session_count > 0 else ""),
            title="Loom Status",
            border_style="blue",
        )
    )


# ────────────────────────────────────────────
# loom templates
# ────────────────────────────────────────────


@main.group(name="templates")
def templates_group():
    """Project templates for domain-specific onboarding."""
    pass


@templates_group.command(name="list")
def templates_list():
    """List available project templates."""
    from loom.templates import list_templates

    templates = list_templates()
    table = Table(title="Available Templates", show_header=True)
    table.add_column("Name", style="cyan")
    table.add_column("Description")
    table.add_column("Entries", justify="right")

    for t in templates:
        table.add_row(t["name"], t["description"], str(t["entries"]))
    console.print(table)


@templates_group.command(name="apply")
@click.argument("name")
def templates_apply(name: str):
    """Apply a template to the current workspace."""
    root = _require_workspace()
    from loom.templates import apply_template

    result = apply_template(name, root)
    if "error" in result:
        console.print(f"[red]{result['error']}[/]")
        return
    console.print(f"[green]\u2713 Template applied:[/] {name} ({result['entries_added']} entries)")


# ────────────────────────────────────────────
# loom context
# ────────────────────────────────────────────


@main.command()
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
@click.option("--save", is_flag=True, help="Save to .loom/context.md")
def context(as_json: bool, save: bool):
    """Show compact project context for session onboarding."""
    root = _require_workspace()
    from loom.mcp_server import handle_get_context
    from loom.memory import MemoryStore

    store = MemoryStore(root)
    ctx = handle_get_context(store, root)
    store.close()

    if as_json:
        click.echo(json.dumps(ctx, indent=2, default=str))
        return

    if save:
        from loom.constants import loom_dir

        lines = [
            f"# Project Context ({ctx.get('project_type', 'unknown')})",
            "",
            f"**Runtime:** {ctx.get('runtime_identity', 'N/A')}",
            f"**Branch:** {ctx.get('git_branch', 'N/A')}",
            f"**Memory entries:** {ctx.get('memory_entries', 0)}",
            "",
        ]
        if ctx.get("active_goals"):
            lines.append("## Active Goals")
            for g in ctx["active_goals"]:
                lines.append(f"- {g}")
            lines.append("")
        if ctx.get("recent_decisions"):
            lines.append("## Recent Decisions")
            for d in ctx["recent_decisions"]:
                lines.append(f"- {d}")
            lines.append("")
        if ctx.get("known_risks"):
            lines.append("## Known Risks")
            for r in ctx["known_risks"]:
                lines.append(f"- {r}")
            lines.append("")

        out = loom_dir(root) / "context.md"
        out.write_text("\n".join(lines))
        console.print(f"[green]\u2713 Saved to[/] {out}")
        return

    console.print(
        Panel(
            f"  Project:     [cyan]{ctx.get('project_type', 'unknown')}[/]\n"
            f"  Identity:    [dim]{ctx.get('runtime_identity', 'N/A')}[/]\n"
            f"  Branch:      {ctx.get('git_branch', 'N/A')}\n"
            f"  Memory:      {ctx.get('memory_entries', 0)} entries\n\n"
            + (
                "  [bold]Goals:[/]\n"
                + "".join(f"    \u2022 {g}\n" for g in ctx.get("active_goals", []))
                if ctx.get("active_goals")
                else ""
            )
            + (
                "  [bold]Decisions:[/]\n"
                + "".join(f"    \u2022 {d}\n" for d in ctx.get("recent_decisions", []))
                if ctx.get("recent_decisions")
                else ""
            )
            + (
                "  [bold]Risks:[/]\n"
                + "".join(f"    \u26a0 {r}\n" for r in ctx.get("known_risks", []))
                if ctx.get("known_risks")
                else ""
            ),
            title="Project Context",
            border_style="cyan",
        )
    )


# ────────────────────────────────────────────
# loom session
# ────────────────────────────────────────────


@main.group()
def session():
    """Session management (track which AI tool is working)."""
    pass


@session.command(name="open")
@click.argument("actor")
@click.option("--model", default=None, help="Model name (e.g. claude-opus-4, gpt-4o)")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
def session_open(actor: str, model: str | None, as_json: bool):
    """Open a new session for an actor."""
    root = _require_workspace()
    from loom.sessions import SessionStore

    store = SessionStore(root)
    result = store.open_session(actor, model)
    store.close()

    if as_json:
        click.echo(json.dumps(result, indent=2))
        return

    console.print(
        f"[green]\u2713 Session opened[/]\n"
        f"  ID:    [dim]{result['id']}[/]\n"
        f"  Actor: [cyan]{actor}[/]\n"
        f"  Model: {model or 'unspecified'}"
    )


@session.command(name="close")
@click.option("--summary", "-s", default=None, help="Session summary")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
def session_close(summary: str | None, as_json: bool):
    """Close the active session."""
    root = _require_workspace()
    from loom.sessions import SessionStore

    store = SessionStore(root)
    active = store.get_active()
    if not active:
        if as_json:
            click.echo(json.dumps({"error": "No active session"}))
        else:
            console.print("[yellow]No active session to close.[/]")
        store.close()
        return

    result = store.close_session(active["id"], summary)
    store.close()

    if as_json:
        click.echo(json.dumps(result, indent=2))
        return

    console.print(
        f"[green]\u2713 Session closed[/]\n"
        f"  ID:      [dim]{result['id']}[/]\n"
        f"  Ended:   {result['ended_at'][:19]}"
    )


@session.command(name="list")
@click.option("-n", "--limit", default=10, help="Max sessions to show")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
def session_list(limit: int, as_json: bool):
    """List recent sessions."""
    root = _require_workspace()
    from loom.sessions import SessionStore

    store = SessionStore(root)
    sessions = store.list_sessions(limit)
    store.close()

    if as_json:
        click.echo(json.dumps(sessions, indent=2))
        return

    if not sessions:
        console.print("[dim]No sessions recorded yet.[/]")
        return

    table = Table(title="Sessions", show_header=True)
    table.add_column("Actor", style="cyan", width=14)
    table.add_column("Model", width=14)
    table.add_column("Status", width=8)
    table.add_column("Started", style="dim", width=17)
    table.add_column("ID", style="dim", width=12)

    for s in sessions:
        status_style = "green" if s["status"] == "active" else "dim"
        table.add_row(
            s["actor"],
            s.get("model_name") or "-",
            f"[{status_style}]{s['status']}[/]",
            s["started_at"][:16],
            s["id"][:12] + "...",
        )
    console.print(table)


@session.command(name="cleanup")
@click.option("--max-age", default=24, help="Max session age in hours before auto-close")
def session_cleanup(max_age: int):
    """Close stale sessions that have been active too long."""
    root = _require_workspace()
    from loom.sessions import SessionStore

    store = SessionStore(root)
    closed = store.cleanup_stale(max_age)
    store.close()
    console.print(f"[green]\u2713 Cleaned up {closed} stale session(s)[/]")


# ────────────────────────────────────────────
# loom token
# ────────────────────────────────────────────


@main.group()
def token():
    """Write token management (single-writer exclusion)."""
    pass


@token.command(name="acquire")
@click.argument("session_id")
@click.argument("actor")
@click.option("--lease", default=15, help="Lease duration in minutes")
@click.option("--force", is_flag=True, help="Force acquire even if held by another")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
def token_acquire(session_id: str, actor: str, lease: int, force: bool, as_json: bool):
    """Acquire the write token for a session."""
    root = _require_workspace()
    from loom import write_token

    result = write_token.acquire(session_id, actor, root, lease, force)

    if as_json:
        click.echo(json.dumps(result, indent=2))
        return

    if result["acquired"]:
        console.print(
            f"[green]\u2713 Write token acquired[/]\n"
            f"  Actor:   [cyan]{actor}[/]\n"
            f"  Lease:   {lease} min\n"
            f"  Expires: {result['expires_at'][:19]}"
        )
    else:
        console.print(
            f"[red]\u2717 Write token held by {result.get('holder', 'unknown')}[/]\n"
            f"  Expires: {result.get('expires_at', 'N/A')[:19]}\n"
            f"  Use --force to reclaim."
        )


@token.command(name="release")
@click.argument("session_id")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
def token_release(session_id: str, as_json: bool):
    """Release the write token."""
    root = _require_workspace()
    from loom import write_token

    result = write_token.release(session_id, root)

    if as_json:
        click.echo(json.dumps(result, indent=2))
        return

    if result["released"]:
        console.print("[green]\u2713 Write token released[/]")
    else:
        console.print(f"[yellow]\u26a0 {result.get('reason', 'unknown error')}[/]")


@token.command(name="status")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
def token_status(as_json: bool):
    """Show current write token status."""
    root = _require_workspace()
    from loom import write_token

    result = write_token.status(root)

    if as_json:
        click.echo(json.dumps(result, indent=2))
        return

    if result["held"]:
        console.print(
            f"[yellow]\u26a0 Write token held[/]\n"
            f"  Actor:     [cyan]{result['actor']}[/]\n"
            f"  Session:   [dim]{result['session_id'][:12]}...[/]\n"
            f"  Remaining: {result['remaining_seconds']}s"
        )
    else:
        console.print("[green]\u2713 Write token is free[/]")


# ────────────────────────────────────────────
# loom mcp serve
# ────────────────────────────────────────────


@main.group()
def mcp():
    """MCP server commands."""
    pass


@mcp.command()
def serve():
    """Run Loom MCP server over stdio."""
    from loom.mcp_server import run_stdio

    asyncio.run(run_stdio())


# ────────────────────────────────────────────
# loom import / loom export
# ────────────────────────────────────────────


@main.command(name="import")
@click.argument("file", type=click.Path(exists=True))
def import_cmd(file: str):
    """Import CLAUDE.md or .cursorrules into Loom memory."""
    root = _require_workspace()
    from loom.import_export import import_file

    file_path = Path(file)
    result = import_file(file_path, root)
    console.print(
        f"[green]\u2713 Imported {result['imported']} entries[/] "
        f"from [cyan]{result['source']}[/] (format: {result['format']})"
    )


@main.command(name="export")
@click.argument("format", type=click.Choice(["claude-md", "markdown"]))
@click.option("-o", "--output", default=None, help="Output file path")
def export_cmd(format: str, output: str | None):
    """Export Loom memory as CLAUDE.md or markdown."""
    root = _require_workspace()
    from loom.import_export import export_claude_md, export_markdown

    out_path = Path(output) if output else None

    if format == "claude-md":
        content = export_claude_md(root, out_path)
        dest = out_path or (root / "CLAUDE.md")
    else:
        content = export_markdown(root, out_path)
        dest = out_path or Path("/dev/stdout")

    if format == "markdown" and not output:
        console.print(content)
    else:
        console.print(f"[green]\u2713 Exported to[/] [cyan]{dest}[/]")


# ────────────────────────────────────────────
# loom promote / loom reject
# ────────────────────────────────────────────


@main.command()
@click.argument("entry_id")
def promote(entry_id: str):
    """Promote a memory entry: hypothesis → validated."""
    root = _require_workspace()
    from loom.memory import MemoryStore

    store = MemoryStore(root)
    entry = store.get(entry_id)
    if not entry:
        console.print(f"[red]Entry not found:[/] {entry_id}")
        sys.exit(1)

    if entry["status"] != "hypothesis":
        console.print(
            f"[yellow]Cannot promote:[/] entry is '{entry['status']}', "
            f"only 'hypothesis' can be promoted."
        )
        sys.exit(1)

    store.update_status(entry_id, "validated")
    store.close()

    emit(
        Event(
            event_type="memory_promoted",
            actor="cli",
            data={"entry_id": entry_id, "from": "hypothesis", "to": "validated"},
        ),
        root,
    )
    console.print(f"[green]\u2713 Promoted to validated:[/] {entry['content'][:60]}")


@main.command()
@click.argument("entry_id")
@click.option("--reason", "-r", required=True, help="Why this entry is rejected")
def reject(entry_id: str, reason: str):
    """Reject a memory entry: hypothesis → rejected."""
    root = _require_workspace()
    from loom.memory import MemoryStore

    store = MemoryStore(root)
    entry = store.get(entry_id)
    if not entry:
        console.print(f"[red]Entry not found:[/] {entry_id}")
        sys.exit(1)

    if entry["status"] not in ("hypothesis", "validated"):
        console.print(f"[yellow]Cannot reject:[/] entry is '{entry['status']}'.")
        sys.exit(1)

    store.update_status(entry_id, "rejected")
    store.close()

    emit(
        Event(
            event_type="memory_rejected",
            actor="cli",
            data={"entry_id": entry_id, "reason": reason},
        ),
        root,
    )
    console.print(f"[green]\u2713 Rejected:[/] {entry['content'][:60]}\n  Reason: {reason}")


# ────────────────────────────────────────────
# loom gateway (remote access)
# ────────────────────────────────────────────


@main.group()
def gateway():
    """Remote gateway commands (SSE/HTTP server)."""
    pass


@gateway.command()
@click.option("--host", default="0.0.0.0", help="Bind address")
@click.option("--port", default=8443, help="Port")
def start(host: str, port: int):
    """Start the remote gateway server (SSE + REST API)."""
    from loom.gateway import run_gateway

    api_key = os.environ.get("LOOM_API_KEY")
    if not api_key:
        console.print(
            "[yellow]\u26a0 LOOM_API_KEY not set[/] \u2014 gateway will run "
            "without authentication.\n"
            "  Set it with: [dim]export LOOM_API_KEY=$(loom gateway keygen)[/]"
        )

    console.print(
        Panel(
            f"[bold cyan]Loom Gateway starting[/]\n\n"
            f"  Host:       {host}\n"
            f"  Port:       {port}\n"
            f"  Auth:       {'[green]API key[/]' if api_key else '[yellow]NONE[/]'}\n"
            f"  MCP SSE:    http://{host}:{port}/mcp\n"
            f"  REST API:   http://{host}:{port}/api/\n"
            f"  Health:     http://{host}:{port}/health",
            title="Gateway",
            border_style="cyan",
        )
    )

    run_gateway(workspace=Path.cwd(), host=host, port=port)


@gateway.command()
def keygen():
    """Generate a secure API key for gateway authentication."""
    from loom.gateway import generate_api_key

    key = generate_api_key()
    console.print(f"[green]\u2713 API key generated:[/]\n\n  {key}\n")
    console.print(
        "[dim]Set it as environment variable:[/]\n"
        f"  export LOOM_API_KEY={key}\n\n"
        "[dim]Or in your .env file:[/]\n"
        f"  LOOM_API_KEY={key}"
    )


@gateway.command()
def devcontainer():
    """Generate a devcontainer.json with Loom cache volumes."""
    root = _require_workspace()
    from loom.docker import generate_devcontainer

    dc_path = generate_devcontainer(root)
    console.print(f"[green]\u2713 Generated:[/] {dc_path}")


# ────────────────────────────────────────────
# loom policy
# ────────────────────────────────────────────


@main.group()
def policy():
    """Policy engine commands."""
    pass


@policy.command(name="install")
def policy_install():
    """Install the default policy file into the workspace."""
    root = _require_workspace()
    from loom.policy import install_default_policy

    dest = install_default_policy(root)
    console.print(f"[green]\u2713 Policy installed:[/] {dest}")
    console.print("[dim]Edit the file to customize rules.[/]")


@policy.command(name="check")
@click.argument("tool_name")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
def policy_check(tool_name: str, as_json: bool):
    """Check what the policy would decide for a tool call."""
    root = _require_workspace()
    from loom.policy import evaluate

    result = evaluate(tool_name, {}, root)

    if as_json:
        click.echo(json.dumps(result, indent=2))
        return

    style = {"allow": "green", "deny": "red", "approve": "yellow"}.get(result["decision"], "")
    console.print(
        f"  Tool:     [cyan]{tool_name}[/]\n"
        f"  Decision: [{style}]{result['decision']}[/]\n"
        f"  Reason:   {result['reason']}"
    )


# ────────────────────────────────────────────
# loom repair / rebuild / decay
# ────────────────────────────────────────────


@main.command()
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
def repair(as_json: bool):
    """Repair workspace: clean stale tokens, sessions, rebuild FTS5."""
    root = _require_workspace()
    from loom.recovery import integrity_check
    from loom.recovery import repair as do_repair

    report = integrity_check(root)
    fix_report = do_repair(root)

    if as_json:
        click.echo(json.dumps({"integrity": report, "repairs": fix_report}, indent=2, default=str))
        return

    # Show integrity checks
    table = Table(title="Integrity Check", show_header=True)
    table.add_column("Check", style="bold")
    table.add_column("Status", justify="center")
    table.add_column("Detail")
    for c in report["checks"]:
        status = "[green]\u2713[/]" if c["ok"] else "[red]\u2717[/]"
        table.add_row(c["name"], status, c["detail"])
    console.print(table)

    if fix_report["repaired"] > 0:
        console.print(f"\n[green]\u2713 Repaired {fix_report['repaired']} issue(s):[/]")
        for d in fix_report["details"]:
            console.print(f"  \u2022 {d}")
    else:
        console.print("\n[green]\u2713 No repairs needed.[/]")


@main.command()
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
def rebuild(as_json: bool):
    """Reconstruct memory.db from events.jsonl (nuclear recovery option)."""
    root = _require_workspace()
    from loom.recovery import rebuild_from_events

    console.print("[yellow]Rebuilding memory from events.jsonl...[/]")
    result = rebuild_from_events(root)

    if as_json:
        click.echo(json.dumps(result, indent=2))
        return

    if "error" in result:
        console.print(f"[red]\u2717 {result['error']}[/]")
        sys.exit(1)

    console.print(
        f"[green]\u2713 Rebuilt {result['rebuilt']} entries[/] ({result['skipped']} skipped)"
    )
    if result["skipped"] > 0:
        console.print("[dim]Skipped entries had missing or unrecoverable data.[/]")


@main.command()
@click.option("--ttl", default=30, help="Days before hypothesis entries are auto-obsoleted")
@click.option("--dry-run", is_flag=True, help="Show what would decay without changing anything")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
def decay(ttl: int, dry_run: bool, as_json: bool):
    """Auto-obsolete unvalidated hypothesis entries older than TTL."""
    root = _require_workspace()
    from loom.recovery import decay_memories

    result = decay_memories(root, ttl_days=ttl, dry_run=dry_run)

    if as_json:
        click.echo(json.dumps(result, indent=2, default=str))
        return

    if dry_run:
        console.print(f"[yellow]Dry run:[/] {result['would_decay']} entries would be decayed")
        for e in result.get("entries", []):
            console.print(f"  \u2022 [dim]{e['id'][:12]}[/] {e['content']}")
    else:
        console.print(f"[green]\u2713 Decayed {result['decayed']} entries[/] (TTL: {ttl} days)")


# ────────────────────────────────────────────
# loom benchmark
# ────────────────────────────────────────────


@main.command()
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
def benchmark(as_json: bool):
    """Run performance benchmarks."""
    from loom.benchmark import format_report, run_benchmarks

    if not as_json:
        console.print("[cyan]Running benchmarks...[/]\n")

    results = run_benchmarks()

    if as_json:
        click.echo(json.dumps(results, indent=2))
        return

    console.print(format_report(results))


# ────────────────────────────────────────────
# loom team
# ────────────────────────────────────────────


@main.group()
def team():
    """Team management (multi-user access)."""
    pass


@team.command(name="add")
@click.argument("name")
@click.option("--role", type=click.Choice(["admin", "member", "viewer"]), default="member")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
def team_add(name: str, role: str, as_json: bool):
    """Add a team member and generate their API key."""
    root = _require_workspace()
    from loom.team import add_user

    result = add_user(name, role, root)

    if as_json:
        click.echo(json.dumps(result, indent=2))
        return

    console.print(
        f"[green]\u2713 User added:[/] {name} ({role})\n\n"
        f"  API Key: [bold]{result['api_key']}[/]\n"
        f"  User ID: [dim]{result['user_id']}[/]\n\n"
        "[yellow]Save this key — it cannot be shown again.[/]"
    )


@team.command(name="list")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
def team_list(as_json: bool):
    """List team members."""
    root = _require_workspace()
    from loom.team import list_users

    users = list_users(root)

    if as_json:
        click.echo(json.dumps(users, indent=2))
        return

    if not users:
        console.print("[dim]No team members. Running in solo mode.[/]")
        console.print("[dim]Use `loom team add <name>` to enable team mode.[/]")
        return

    table = Table(title="Team Members", show_header=True)
    table.add_column("Name", style="cyan")
    table.add_column("Role")
    table.add_column("Key Prefix", style="dim")
    table.add_column("User ID", style="dim", width=12)

    for u in users:
        table.add_row(u["name"], u["role"], u["key_prefix"], u["user_id"])
    console.print(table)


@team.command(name="remove")
@click.argument("user_id")
def team_remove(user_id: str):
    """Remove a team member by user ID."""
    root = _require_workspace()
    from loom.team import remove_user

    if remove_user(user_id, root):
        console.print("[green]\u2713 User removed[/]")
    else:
        console.print(f"[red]User not found: {user_id}[/]")


@team.command(name="limits")
def team_limits():
    """Show team mode limits and scaling guidance."""
    from loom.team import TEAM_LIMITS

    console.print(TEAM_LIMITS)


# ────────────────────────────────────────────
# loom workspace (multi-workspace router)
# ────────────────────────────────────────────


@main.group()
def workspace():
    """Multi-workspace management (serve multiple projects)."""
    pass


@workspace.command(name="register")
@click.argument("path", type=click.Path(exists=True))
@click.option("--name", "-n", default=None, help="Workspace name")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
def ws_register(path: str, name: str | None, as_json: bool):
    """Register a workspace with the multi-project router."""
    from loom.workspace_router import WorkspaceRouter

    router = WorkspaceRouter()
    result = router.register(Path(path), name)

    if as_json:
        click.echo(json.dumps(result, indent=2))
        return

    if "error" in result:
        console.print(f"[red]{result['error']}[/]")
        return

    console.print(
        f"[green]\u2713 Workspace registered:[/] {result['name']}\n"
        f"  ID:   [dim]{result['id']}[/]\n"
        f"  Path: {result['path']}"
    )


@workspace.command(name="list")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
def ws_list(as_json: bool):
    """List all registered workspaces."""
    from loom.workspace_router import WorkspaceRouter

    router = WorkspaceRouter()
    workspaces = router.list_workspaces()

    if as_json:
        click.echo(json.dumps(workspaces, indent=2))
        return

    if not workspaces:
        console.print("[dim]No workspaces registered.[/]")
        console.print("[dim]Use `loom workspace register /path/to/project` to add one.[/]")
        return

    table = Table(title="Workspaces", show_header=True)
    table.add_column("Name", style="cyan")
    table.add_column("ID", style="dim", width=14)
    table.add_column("Path")
    table.add_column("Health", justify="center")

    for w in workspaces:
        health = "[green]\u2713[/]" if w["healthy"] else "[red]\u2717[/]"
        table.add_row(w["name"], w["id"], w["path"], health)
    console.print(table)


@workspace.command(name="remove")
@click.argument("workspace_id")
def ws_remove(workspace_id: str):
    """Unregister a workspace (does not delete files)."""
    from loom.workspace_router import WorkspaceRouter

    router = WorkspaceRouter()
    if router.unregister(workspace_id):
        console.print("[green]\u2713 Workspace unregistered[/]")
    else:
        console.print(f"[red]Workspace not found: {workspace_id}[/]")


@workspace.command(name="serve")
@click.option("--host", default="0.0.0.0", help="Bind address")
@click.option("--port", default=8443, help="Port")
def ws_serve(host: str, port: int):
    """Start the multi-workspace gateway server."""
    import uvicorn

    from loom.workspace_router import WorkspaceRouter, create_multi_workspace_app

    router = WorkspaceRouter()
    workspaces = router.list_workspaces()

    console.print(
        Panel(
            f"[bold cyan]Multi-Workspace Gateway[/]\n\n"
            f"  Host:       {host}\n"
            f"  Port:       {port}\n"
            f"  Workspaces: {len(workspaces)}\n\n"
            + "".join(
                f"  [{('green' if w['healthy'] else 'red')}]\u2022[/] {w['name']} → /w/{w['id']}/\n"
                for w in workspaces
            )
            + f"\n  Health: http://{host}:{port}/health\n"
            f"  List:   http://{host}:{port}/workspaces",
            title="Gateway",
            border_style="cyan",
        )
    )

    app = create_multi_workspace_app()
    uvicorn.run(app, host=host, port=port, log_level="info")


if __name__ == "__main__":
    main()
