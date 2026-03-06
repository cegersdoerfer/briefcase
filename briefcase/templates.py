import yaml


def render_toolset_yaml(project_name: str, tools: list[dict]) -> str:
    data = {
        "project": project_name,
        "tools": [
            {
                "name": t["name"],
                "path": t["rel_path"],
                **({"notes": t["notes"]} if t.get("notes") else {}),
            }
            for t in tools
        ],
        "rules": [
            "Do not modify anything under ./refs/",
            "Implement new code under ./src/",
            "Add tests under ./tests/",
            "Use referenced repos for examples and API understanding.",
        ],
    }
    return yaml.dump(data, default_flow_style=False, sort_keys=False)


def render_agent_context(project_name: str, tools: list[dict]) -> str:
    lines = [
        f"# {project_name}",
        "",
        "## Instructions",
        "",
        "- Implement all new code under `./src/`.",
        "- Add tests under `./tests/`.",
        "- Referenced tool repos are symlinked in `./refs/`. Use them for examples and API understanding.",
        "- **Do not modify anything under `./refs/`.**",
        "",
        "## Referenced Tools",
        "",
    ]
    for t in tools:
        line = f"- **{t['name']}** — `{t['rel_path']}`"
        if t.get("notes"):
            line += f" — {t['notes']}"
        lines.append(line)
    lines.append("")
    return "\n".join(lines)
