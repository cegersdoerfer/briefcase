from pathlib import Path

from briefcase.registry import get_paths, get_tool
from briefcase.templates import render_agent_context, render_toolset_yaml


def create_project(project_name: str, tool_names: list[str], home: Path | None = None) -> Path:
    _, repos_dir, _ = get_paths(home)
    project_dir = Path.cwd() / project_name

    if project_dir.exists():
        raise FileExistsError(f"Project directory already exists: {project_dir}")

    # Validate all tools exist before creating anything
    tools_info = []
    for name in tool_names:
        tool = get_tool(name, home=home)
        if tool is None:
            raise ValueError(f"Tool '{name}' is not registered. Run 'briefcase add' first.")
        tools_info.append(tool)

    # Create directory structure
    (project_dir / "src").mkdir(parents=True)
    (project_dir / "tests").mkdir()
    refs_dir = project_dir / "refs"
    refs_dir.mkdir()

    # Create symlinks and build template data
    template_tools = []
    for tool in tools_info:
        link = refs_dir / tool["name"]
        target = repos_dir / tool["name"]
        link.symlink_to(target)
        template_tools.append({
            "name": tool["name"],
            "rel_path": f"./refs/{tool['name']}",
            "notes": tool.get("notes"),
        })

    # Write generated files
    (project_dir / "toolset.yaml").write_text(render_toolset_yaml(project_name, template_tools))
    (project_dir / "AGENT_CONTEXT.md").write_text(render_agent_context(project_name, template_tools))

    return project_dir
