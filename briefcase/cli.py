from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

from briefcase.gitops import clone_repo, parse_github_url, pull_repo
from briefcase.registry import add_tool, ensure_dirs, get_paths, get_tool, list_tools, remove_tool
from briefcase.scaffold import create_project

app = typer.Typer(help="Manage a local registry of reusable GitHub repos and scaffold coding-agent projects.")
console = Console()

_home: Path | None = None


@app.callback()
def main(
    home: Optional[Path] = typer.Option(
        None,
        envvar="BRIEFCASE_HOME",
        help="Override the briefcase home directory (default: ~/.briefcase).",
    ),
) -> None:
    """Configure global options."""
    global _home
    _home = home


@app.command()
def add(
    name: str,
    repo_url: str,
    path: Optional[str] = typer.Option(None, "--path", help="Subpath within the repo (for monorepos)."),
) -> None:
    """Register a GitHub repo and clone it locally."""
    ensure_dirs(_home)
    try:
        clone_url, detected_subpath = parse_github_url(repo_url)
        subpath = path or detected_subpath
        _, repos_dir, _ = get_paths(_home)
        dest = repos_dir / name
        with console.status(f"Cloning {clone_url}..."):
            clone_repo(clone_url, dest)
        with console.status(f"Registering '{name}'..."):
            add_tool(name, clone_url, subpath=subpath, home=_home)
        console.print(f"[green]Added '{name}' from {clone_url}[/green]")
    except (FileExistsError, ValueError, RuntimeError) as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


@app.command("list")
def list_cmd() -> None:
    """List all registered tools."""
    tools = list_tools(home=_home)
    if not tools:
        console.print("No tools registered yet. Use [bold]briefcase add[/bold] to get started.")
        return
    table = Table(title="Registered Tools")
    table.add_column("Name", style="cyan")
    table.add_column("Repo URL")
    table.add_column("Local Path", style="dim")
    table.add_column("Notes", style="italic")
    for t in tools:
        table.add_row(t["name"], t.get("repo_url", ""), t.get("local_path", ""), t.get("notes", ""))
    console.print(table)


@app.command()
def remove(
    name: str,
) -> None:
    """Remove a registered tool and delete its cloned repo."""
    try:
        with console.status(f"Removing '{name}'..."):
            remove_tool(name, home=_home)
        console.print(f"[green]Removed '{name}'[/green]")
    except KeyError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


@app.command()
def new(
    project_name: str,
    tools: list[str] = typer.Option([], "--tools", help="Tool name(s) to include in the project."),
    layout: Optional[str] = typer.Option(None, "--layout", help="Project layout to use (default: from config or 'default')."),
) -> None:
    """Scaffold a new coding-agent project with symlinked tool references."""
    if not tools:
        registered = list_tools(home=_home)
        if not registered:
            console.print("[red]Error:[/red] No tools registered. Use [bold]briefcase add[/bold] first.")
            raise typer.Exit(1)
        from simple_term_menu import TerminalMenu
        tool_names = [t["name"] for t in registered]
        menu = TerminalMenu(
            tool_names,
            title="Select tools to include (Space to select, Enter to confirm):",
            multi_select=True,
            show_multi_select_hint=True,
        )
        menu.show()
        selected = menu.chosen_menu_entries
        if not selected:
            console.print("No tools selected. Aborting.")
            raise typer.Exit(0)
        tools = list(selected)
    try:
        project_dir = create_project(project_name, tools, home=_home, layout=layout)
        console.print(f"[green]Created project '{project_name}' at {project_dir}[/green]")
    except (FileExistsError, ValueError) as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


@app.command()
def update(
    name: Optional[str] = typer.Argument(None, help="Tool name to update."),
    all_tools: bool = typer.Option(False, "--all", help="Update all registered tools."),
) -> None:
    """Pull latest changes for registered tool(s)."""
    if not name and not all_tools:
        console.print("[red]Error:[/red] Provide a tool name or use --all.")
        raise typer.Exit(1)

    if all_tools:
        tools = list_tools(home=_home)
        if not tools:
            console.print("No tools registered.")
            return
        for t in tools:
            _update_one(t["name"])
    else:
        _update_one(name)


def _update_one(name: str) -> None:
    tool = get_tool(name, home=_home)
    if tool is None:
        console.print(f"[red]Error:[/red] Tool '{name}' not found in registry.")
        raise typer.Exit(1)
    _, repos_dir, _ = get_paths(_home)
    repo_path = repos_dir / name
    try:
        with console.status(f"Pulling latest for '{name}'..."):
            pull_repo(repo_path)
        console.print(f"[green]Updated '{name}'[/green]")
    except (FileNotFoundError, RuntimeError) as e:
        console.print(f"[yellow]Warning:[/yellow] Failed to update '{name}': {e}")
