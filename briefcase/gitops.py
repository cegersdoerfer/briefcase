import re
import subprocess
from pathlib import Path


def parse_github_url(url: str) -> tuple[str, str | None]:
    """Parse a GitHub URL, extracting any subpath from /tree/<branch>/... patterns.

    Returns (clone_url, subpath) where subpath is None if no /tree/ pattern found.
    """
    m = re.match(r"(https://github\.com/[^/]+/[^/]+)/tree/[^/]+(?:/(.+))?", url)
    if m:
        subpath = m.group(2).rstrip("/") if m.group(2) else None
        return m.group(1), subpath
    return url, None


def clone_repo(url: str, dest_path: Path) -> None:
    if dest_path.exists():
        raise FileExistsError(f"Destination already exists: {dest_path}")
    result = subprocess.run(
        ["git", "clone", url, str(dest_path)],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"git clone failed:\n{result.stderr.strip()}")


def pull_repo(repo_path: Path) -> None:
    if not repo_path.exists():
        raise FileNotFoundError(f"Repo path does not exist: {repo_path}")
    result = subprocess.run(
        ["git", "pull", "--ff-only"],
        capture_output=True,
        text=True,
        cwd=str(repo_path),
    )
    if result.returncode != 0:
        raise RuntimeError(f"git pull failed in {repo_path}:\n{result.stderr.strip()}")
