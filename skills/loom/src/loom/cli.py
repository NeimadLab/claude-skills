"""Loom command-line interface."""

from __future__ import annotations

import asyncio
import json
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


@click.group()
@click.version_option(__version__, prog_name="loom")
def main():
    """Loom — Weave context across AI tools."""
    pass


@main.command()
@click.option("--force", is_flag=True, help="Reinitialize even if .loom/ exists")
def init(force: bool):
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

    # Add .loom/ to .gitignore if not already there
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

    console.print(
        Panel(
            "[bold green]\u2713 Workspace initialized[/]\n\n"
            f"  Project type:  {ptype or 'generic'}\n"
            f"  Identity:      {identity.identity_hash}\n"
            f"  .loom/ created: {ld}\n\n"
            "Next steps:\n"
            "  [dim]loom connect claude-code[/]  \u2014 connect your AI tool\n"
            "  [dim]loom state[/]               \u2014 inspect workspace\n"
            "  [dim]loom doctor[/]              \u2014 run health checks",
            title="Loom",
            border_style="green",
        )
    )


@main.command()
def resume():
    """Resume workspace \u2014 verify identity and restore state."""
    root = _require_workspace()
    stored = load_identity(root)

    if not stored:
        console.print("[red]No runtime manifest found.[/] Run `loom init` first.")
        sys.exit(1)

    live = compute_identity(root)

    if live.identity_hash == stored.identity_hash:
        console.print("[green]\u2713 Runtime identity matches \u2014 no drift detected.[/]")
    else:
        console.print("[yellow]\u26a0 Runtime drift detected[/]")
        console.print(f"  Stored: {stored.identity_hash}")
        console.print(f"  Live:   {live.identity_hash}")
        console.print(
            "  Run [dim]loom doctor[/] for details or [dim]loom init --force[/] to reinitialize."
        )

    state = get_workspace_state(root)
    console.print(f"  Memory entries: {state['memory_entries']}")
    console.print(f"  Events logged:  {state['event_count']}")

    emit(
        Event(
            event_type="workspace_resumed",
            data={"drift": live.identity_hash != stored.identity_hash},
        ),
        root,
    )
    console.print("[green]\u2713 Workspace resumed.[/]")


@main.command()
def doctor():
    """Run workspace health checks."""
    result = doctor_check()
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
def state():
    """Show workspace operational state."""
    root = _require_workspace()
    s = get_workspace_state(root)

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
@click.option("-n", "--limit", default=10, help="Max results")
def search(query: str, type_filter: str | None, status_filter: str | None, limit: int):
    """Search project memory."""
    root = _require_workspace()
    from loom.memory import MemoryStore

    store = MemoryStore(root)
    results = store.search(query, limit=limit, type_filter=type_filter, status_filter=status_filter)
    store.close()

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

    store = MemoryStore(root)
    tag_list = [t.strip() for t in tags.split(",") if t.strip()] if tags else []
    entry = MemoryEntry(
        type=MemoryType.DECISION,
        content=decision,
        rationale=rationale or None,
        tags=tag_list,
        actor="cli",
    )
    store.write(entry)
    store.close()

    emit(
        Event(event_type="decision_logged", actor="cli", data={"entry_id": entry.id}),
        root,
    )
    console.print(f"[green]\u2713 Decision logged:[/] {decision[:60]}")
    console.print(f"  ID: [dim]{entry.id}[/]  Status: [yellow]hypothesis[/]")


# ────────────────────────────────────────────
# NEW: loom events
# ────────────────────────────────────────────


@main.command()
@click.option("-n", "--count", "n", default=20, help="Number of events to show")
def events(n: int):
    """Show recent events from the workspace log."""
    root = _require_workspace()
    from loom.events import tail

    evts = tail(n, root)
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
    config = MCP_CLIENT_CONFIGS.get(client)
    if not config:
        console.print(f"[red]Unknown client: {client}[/]")
        sys.exit(1)

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
    console.print(
        Panel(
            f"[bold green]\u2713 {client} configured for Loom[/]\n\n"
            f"  Config: {config_path}\n"
            f"  Transport: {transport}\n\n"
            f"Restart {client} to activate the connection.",
            title="Loom Connect",
            border_style="green",
        )
    )


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


if __name__ == "__main__":
    main()
