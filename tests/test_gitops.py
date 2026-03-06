from briefcase.gitops import parse_github_url


def test_parse_github_url_with_tree_path():
    url = "https://github.com/badlogic/pi-mono/tree/main/packages/coding-agent"
    clone_url, subpath = parse_github_url(url)
    assert clone_url == "https://github.com/badlogic/pi-mono"
    assert subpath == "packages/coding-agent"


def test_parse_github_url_plain_repo():
    url = "https://github.com/org/repo"
    clone_url, subpath = parse_github_url(url)
    assert clone_url == "https://github.com/org/repo"
    assert subpath is None


def test_parse_github_url_trailing_slash():
    url = "https://github.com/org/repo/tree/main/sub/path/"
    clone_url, subpath = parse_github_url(url)
    assert clone_url == "https://github.com/org/repo"
    assert subpath == "sub/path"


def test_parse_github_url_non_main_branch():
    url = "https://github.com/org/repo/tree/develop/src/lib"
    clone_url, subpath = parse_github_url(url)
    assert clone_url == "https://github.com/org/repo"
    assert subpath == "src/lib"


def test_parse_github_url_non_github():
    url = "https://gitlab.com/org/repo"
    clone_url, subpath = parse_github_url(url)
    assert clone_url == url
    assert subpath is None


def test_parse_github_url_with_blob_path():
    url = "https://github.com/badlogic/pi-mono/blob/main/packages/agent/src/agent-loop.ts"
    clone_url, subpath = parse_github_url(url)
    assert clone_url == "https://github.com/badlogic/pi-mono"
    assert subpath == "packages/agent/src/agent-loop.ts"


def test_parse_github_url_tree_branch_only():
    url = "https://github.com/badlogic/pi-mono/tree/main"
    clone_url, subpath = parse_github_url(url)
    assert clone_url == "https://github.com/badlogic/pi-mono"
    assert subpath is None
