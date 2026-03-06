import pytest
import yaml

from briefcase.layouts import (
    BUILTIN_LAYOUTS,
    list_layouts,
    load_layout,
    render_layout_template,
)


def test_load_builtin_default():
    layout = load_layout("default")
    assert layout is BUILTIN_LAYOUTS["default"]
    assert "src" in layout["dirs"]
    assert "tests" in layout["dirs"]
    assert layout["refs_dir"] == "refs"
    assert "toolset.yaml" in layout["files"]
    assert "AGENT_CONTEXT.md" in layout["files"]


def test_load_builtin_minimal():
    layout = load_layout("minimal")
    assert layout is BUILTIN_LAYOUTS["minimal"]
    assert layout["dirs"] == []
    assert "AGENT_CONTEXT.md" in layout["files"]
    assert "toolset.yaml" not in layout["files"]


def test_unknown_layout_raises():
    with pytest.raises(ValueError, match="Unknown layout"):
        load_layout("nonexistent")


def test_user_defined_overrides_builtin(tmp_path):
    layouts_dir = tmp_path / "layouts"
    layouts_dir.mkdir()
    custom = {"dirs": ["custom"], "refs_dir": "refs", "files": {}}
    (layouts_dir / "default.yaml").write_text(yaml.dump(custom))

    layout = load_layout("default", home=tmp_path)
    assert layout["dirs"] == ["custom"]


def test_user_defined_custom_layout(tmp_path):
    layouts_dir = tmp_path / "layouts"
    layouts_dir.mkdir()
    custom = {"dirs": ["lib"], "refs_dir": "references", "files": {"README.md": "# Hello"}}
    (layouts_dir / "mylay.yaml").write_text(yaml.dump(custom))

    layout = load_layout("mylay", home=tmp_path)
    assert layout["dirs"] == ["lib"]
    assert layout["refs_dir"] == "references"


def test_list_layouts_builtins_only():
    names = list_layouts()
    assert "default" in names
    assert "minimal" in names
    assert names == sorted(names)


def test_list_layouts_union(tmp_path):
    layouts_dir = tmp_path / "layouts"
    layouts_dir.mkdir()
    (layouts_dir / "custom.yaml").write_text(yaml.dump({"dirs": []}))

    names = list_layouts(home=tmp_path)
    assert "default" in names
    assert "minimal" in names
    assert "custom" in names


def test_render_layout_template_project_name():
    tpl = "# {{ project_name }}\nDone."
    result = render_layout_template(tpl, "myproj", [])
    assert result == "# myproj\nDone."


def test_render_layout_template_tools_loop():
    tpl = (
        "Tools:\n"
        "{% for tool in tools %}\n"
        "- {{ tool.name }}: {{ tool.rel_path }}\n"
        "{% endfor %}\n"
    )
    tools = [
        {"name": "foo", "rel_path": "./refs/foo"},
        {"name": "bar", "rel_path": "./refs/bar", "notes": "note"},
    ]
    result = render_layout_template(tpl, "proj", tools)
    assert "- foo: ./refs/foo" in result
    assert "- bar: ./refs/bar" in result


def test_render_layout_template_empty_tools():
    tpl = "{% for tool in tools %}\n- {{ tool.name }}\n{% endfor %}\n"
    result = render_layout_template(tpl, "proj", [])
    assert result.strip() == ""
