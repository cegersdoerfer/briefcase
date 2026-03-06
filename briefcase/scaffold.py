from pathlib import Path

from briefcase.config import get_default_layout
from briefcase.layouts import load_layout, render_layout_template
from briefcase.registry import get_paths, get_tool


def create_project(
    project_name: str,
    tool_names: list[str],
    home: Path | None = None,
    layout: str | None = None,
) -> Path:
    _, repos_dir, _ = get_paths(home)
    project_dir = Path.cwd() / project_name

    if project_dir.exists():
        raise FileExistsError(f"Project directory already exists: {project_dir}")

    # Resolve layout
    layout_name = layout if layout is not None else get_default_layout(home)
    layout_spec = load_layout(layout_name, home)

    # Validate all tools exist before creating anything
    tools_info = []
    for name in tool_names:
        tool = get_tool(name, home=home)
        if tool is None:
            raise ValueError(f"Tool '{name}' is not registered. Run 'briefcase add' first.")
        tools_info.append(tool)

    # Create directory structure from layout
    project_dir.mkdir(parents=True)
    for d in layout_spec.get("dirs", []):
        (project_dir / d).mkdir(parents=True, exist_ok=True)

    refs_dir_name = layout_spec.get("refs_dir", "refs")
    refs_dir = project_dir / refs_dir_name
    refs_dir.mkdir(parents=True, exist_ok=True)

    # Create symlinks and build template data
    template_tools = []
    for tool in tools_info:
        link = refs_dir / tool["name"]
        subpath = tool.get("subpath")
        target = repos_dir / tool["name"] / subpath if subpath else repos_dir / tool["name"]
        link.symlink_to(target)
        template_tools.append({
            "name": tool["name"],
            "rel_path": f"./{refs_dir_name}/{tool['name']}",
            "notes": tool.get("notes"),
        })

    # Write generated files
    for filename, content in layout_spec.get("files", {}).items():
        if callable(content):
            text = content(project_name, template_tools)
        else:
            text = render_layout_template(content, project_name, template_tools)
        (project_dir / filename).write_text(text)

    return project_dir
