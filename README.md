# briefcase

A CLI for maintaining a local registry of GitHub repos and scaffolding coding-agent projects that reference them.

## Install

```
pip install -e .
```

Requires Python 3.10+ and git.

## Usage

### Register a repo

```
briefcase add <name> <repo-url>
```

Clones the repo into `~/.briefcase/repos/<name>` and records it in the registry.

### List registered repos

```
briefcase list
```

### Update a repo (git pull)

```
briefcase update <name>
briefcase update --all
```

### Scaffold a new project

```
briefcase new myproject --tool foo --tool bar
```

Creates a project directory with this layout:

```
myproject/
  src/           # your code goes here
  tests/
  refs/
    foo -> ~/.briefcase/repos/foo   # symlink, read-only reference
    bar -> ~/.briefcase/repos/bar
  toolset.yaml
  AGENT_CONTEXT.md
```

The generated `AGENT_CONTEXT.md` and `toolset.yaml` give a coding agent the context it needs to use the referenced repos.

### Custom home directory

Override the default `~/.briefcase` location:

```
briefcase --home /path/to/registry list
BRIEFCASE_HOME=/path/to/registry briefcase list
```

`--home` takes precedence over the `BRIEFCASE_HOME` env var.

## Development

```
pip install -e ".[dev]"
.venv/bin/python -m pytest
```
