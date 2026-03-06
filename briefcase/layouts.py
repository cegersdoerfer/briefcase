import re
from pathlib import Path

import yaml

from briefcase.templates import render_agent_context, render_toolset_yaml

BUILTIN_LAYOUTS: dict[str, dict] = {
    "default": {
        "dirs": ["src", "tests"],
        "refs_dir": "refs",
        "files": {
            "toolset.yaml": render_toolset_yaml,
            "AGENT_CONTEXT.md": render_agent_context,
        },
    },
    "minimal": {
        "dirs": [],
        "refs_dir": "refs",
        "files": {
            "AGENT_CONTEXT.md": (
                "# {{ project_name }}\n"
                "\n"
                "## Referenced Tools\n"
                "\n"
                "{% for tool in tools %}\n"
                "- **{{ tool.name }}** — `{{ tool.rel_path }}`\n"
                "{% endfor %}\n"
            ),
        },
    },
}


def render_layout_template(template_str: str, project_name: str, tools: list[dict]) -> str:
    """Render a layout template string with variable substitution."""
    result = template_str.replace("{{ project_name }}", project_name)

    # Expand {% for tool in tools %}...{% endfor %} blocks
    pattern = r"\{%\s*for\s+tool\s+in\s+tools\s*%\}\n?(.*?)\{%\s*endfor\s*%\}\n?"
    def expand_loop(match: re.Match) -> str:
        body = match.group(1)
        lines = []
        for tool in tools:
            rendered = body
            rendered = rendered.replace("{{ tool.name }}", tool["name"])
            rendered = rendered.replace("{{ tool.rel_path }}", tool["rel_path"])
            rendered = rendered.replace("{{ tool.notes }}", tool.get("notes") or "")
            lines.append(rendered)
        return "".join(lines)

    result = re.sub(pattern, expand_loop, result, flags=re.DOTALL)
    return result


def load_layout(name: str, home: Path | None = None) -> dict:
    """Load a layout by name. User-defined layouts in {home}/layouts/ take priority."""
    if home is not None:
        user_file = home / "layouts" / f"{name}.yaml"
        if user_file.exists():
            data = yaml.safe_load(user_file.read_text())
            if not isinstance(data, dict):
                raise ValueError(f"Invalid layout file: {user_file}")
            return data

    if name in BUILTIN_LAYOUTS:
        return BUILTIN_LAYOUTS[name]

    raise ValueError(f"Unknown layout: '{name}'. Available: {', '.join(list_layouts(home))}")


def list_layouts(home: Path | None = None) -> list[str]:
    """Return sorted union of built-in and user-defined layout names."""
    names = set(BUILTIN_LAYOUTS.keys())
    if home is not None:
        layouts_dir = home / "layouts"
        if layouts_dir.is_dir():
            for f in layouts_dir.glob("*.yaml"):
                names.add(f.stem)
    return sorted(names)
