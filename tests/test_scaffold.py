import pytest

from briefcase.registry import add_tool, ensure_dirs, get_paths
from briefcase.scaffold import create_project


@pytest.fixture(autouse=True)
def tmp_registry(tmp_path, monkeypatch):
    """Set up a temp briefcase home and working directory."""
    home = tmp_path / "briefcase_home"
    ensure_dirs(home=home)
    _, repos_dir, _ = get_paths(home)

    work_dir = tmp_path / "work"
    work_dir.mkdir()
    monkeypatch.chdir(work_dir)

    # Create fake repo dirs
    (repos_dir / "tool1").mkdir()
    (repos_dir / "tool2").mkdir()

    # Register tools
    add_tool("tool1", "https://github.com/org/tool1", notes="Tool one", home=home)
    add_tool("tool2", "https://github.com/org/tool2", home=home)

    return home


def test_create_project_structure(tmp_registry):
    project_dir = create_project("myproj", ["tool1", "tool2"], home=tmp_registry)
    assert (project_dir / "src").is_dir()
    assert (project_dir / "tests").is_dir()
    assert (project_dir / "refs").is_dir()
    assert (project_dir / "toolset.yaml").is_file()
    assert (project_dir / "AGENT_CONTEXT.md").is_file()


def test_symlinks_created(tmp_registry):
    project_dir = create_project("myproj", ["tool1"], home=tmp_registry)
    link = project_dir / "refs" / "tool1"
    assert link.is_symlink()


def test_existing_project_raises(tmp_registry):
    create_project("myproj", ["tool1"], home=tmp_registry)
    with pytest.raises(FileExistsError, match="already exists"):
        create_project("myproj", ["tool1"], home=tmp_registry)


def test_missing_tool_raises(tmp_registry):
    with pytest.raises(ValueError, match="not registered"):
        create_project("myproj", ["nonexistent"], home=tmp_registry)


def test_symlink_with_subpath(tmp_registry):
    _, repos_dir, _ = get_paths(tmp_registry)
    # Create a repo with a subpath
    (repos_dir / "mono" / "packages" / "foo").mkdir(parents=True)
    add_tool("mono", "https://github.com/org/mono", subpath="packages/foo", home=tmp_registry)

    project_dir = create_project("myproj", ["mono"], home=tmp_registry)
    link = project_dir / "refs" / "mono"
    assert link.is_symlink()
    assert str(link.resolve()).endswith("mono/packages/foo")


def test_generated_files_content(tmp_registry):
    project_dir = create_project("myproj", ["tool1"], home=tmp_registry)
    toolset = (project_dir / "toolset.yaml").read_text()
    assert "myproj" in toolset
    assert "tool1" in toolset

    context = (project_dir / "AGENT_CONTEXT.md").read_text()
    assert "# myproj" in context
    assert "tool1" in context
    assert "Do not modify" in context


def test_layout_default_explicit(tmp_registry):
    project_dir = create_project("myproj", ["tool1"], home=tmp_registry, layout="default")
    assert (project_dir / "src").is_dir()
    assert (project_dir / "tests").is_dir()
    assert (project_dir / "refs").is_dir()
    assert (project_dir / "toolset.yaml").is_file()
    assert (project_dir / "AGENT_CONTEXT.md").is_file()


def test_layout_minimal(tmp_registry):
    project_dir = create_project("myproj", ["tool1"], home=tmp_registry, layout="minimal")
    assert (project_dir / "refs").is_dir()
    assert (project_dir / "AGENT_CONTEXT.md").is_file()
    assert "# myproj" in (project_dir / "AGENT_CONTEXT.md").read_text()
    assert "tool1" in (project_dir / "AGENT_CONTEXT.md").read_text()
    # minimal should NOT have src/, tests/, or toolset.yaml
    assert not (project_dir / "src").exists()
    assert not (project_dir / "tests").exists()
    assert not (project_dir / "toolset.yaml").exists()
