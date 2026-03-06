import pytest

from briefcase.registry import add_tool, ensure_dirs, get_tool, list_tools, load_registry, remove_tool


@pytest.fixture(autouse=True)
def tmp_registry(tmp_path):
    """Use a temp directory as the briefcase home."""
    ensure_dirs(home=tmp_path)
    return tmp_path


@pytest.fixture()
def home(tmp_path):
    return tmp_path


def test_load_empty_registry(home):
    assert load_registry(home=home) == {}


def test_add_and_get_tool(home):
    add_tool("foo", "https://github.com/org/foo", notes="a lib", home=home)
    tool = get_tool("foo", home=home)
    assert tool is not None
    assert tool["name"] == "foo"
    assert tool["repo_url"] == "https://github.com/org/foo"
    assert tool["notes"] == "a lib"


def test_add_duplicate_raises(home):
    add_tool("bar", "https://github.com/org/bar", home=home)
    with pytest.raises(ValueError, match="already exists"):
        add_tool("bar", "https://github.com/org/bar", home=home)


def test_list_tools(home):
    add_tool("a", "https://github.com/org/a", home=home)
    add_tool("b", "https://github.com/org/b", home=home)
    tools = list_tools(home=home)
    names = [t["name"] for t in tools]
    assert names == ["a", "b"]


def test_get_missing_tool(home):
    assert get_tool("nonexistent", home=home) is None


def test_round_trip_preserves_data(home):
    add_tool("x", "https://github.com/org/x", notes="note", tags=["t1", "t2"], home=home)
    tool = get_tool("x", home=home)
    assert tool["tags"] == ["t1", "t2"]
    assert tool["notes"] == "note"


def test_remove_tool(home):
    add_tool("foo", "https://github.com/org/foo", home=home)
    # Create a fake repo dir to verify it gets deleted
    repo_dir = home / "repos" / "foo"
    repo_dir.mkdir(parents=True, exist_ok=True)
    (repo_dir / "README.md").write_text("hello")

    remove_tool("foo", home=home)

    assert get_tool("foo", home=home) is None
    assert not repo_dir.exists()


def test_remove_nonexistent_tool_raises(home):
    with pytest.raises(KeyError, match="not found"):
        remove_tool("ghost", home=home)


def test_subpath_round_trip(home):
    add_tool("mono", "https://github.com/org/mono", subpath="packages/foo", home=home)
    tool = get_tool("mono", home=home)
    assert tool is not None
    assert tool["subpath"] == "packages/foo"
    assert tool["local_path"].endswith("mono/packages/foo")
