<p align="center">
  <img src="assets/briefcase.png" alt="briefcase logo" width="200">
</p>

# briefcase

**Pack your agent's briefcase with the right repos before it starts work.**

Coding agents write better code when they can read real examples — but wiring up reference repos for every new project is tedious. Briefcase maintains a local registry of GitHub repos and scaffolds new projects with symlinked references, generated context files, and everything an agent needs to hit the ground running.

## Install

```
pip install agent-briefcase
```

Or install from source:

```
git clone https://github.com/cegersdoerfer/briefcase.git
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

### Remove a repo

```
briefcase remove <name>
```

Removes the tool from the registry and deletes its cloned repo from `~/.briefcase/repos/`.

### Update a repo (git pull)

```
briefcase update <name>
briefcase update --all
```

### Scaffold a new project

```
briefcase new myproject --tools foo bar
```

When `--tools` is omitted, an interactive menu lets you pick from registered tools:

```
briefcase new myproject
```

Creates a project directory with this layout (using the `default` layout):

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

### Project layouts

The `--layout` flag selects a project layout:

```
briefcase new myproject --tools foo --layout minimal
```

Built-in layouts:

| Layout    | Directories    | Files                            |
|-----------|---------------|----------------------------------|
| `default` | src, tests    | toolset.yaml, AGENT_CONTEXT.md   |
| `minimal` | (none)        | AGENT_CONTEXT.md                 |

Both layouts create a `refs/` directory for tool symlinks.

#### Custom layouts

Place a YAML file in `~/.briefcase/layouts/` to define a custom layout:

```yaml
# ~/.briefcase/layouts/mylay.yaml
dirs: [lib]
refs_dir: refs
files:
  AGENT_CONTEXT.md: |
    # {{ project_name }}
    {% for tool in tools %}
    - **{{ tool.name }}** — `{{ tool.rel_path }}`
    {% endfor %}
```

Template variables: `{{ project_name }}`, `{{ tool.name }}`, `{{ tool.rel_path }}`, `{{ tool.notes }}`.

A same-named file in `~/.briefcase/layouts/` overrides a built-in layout.

#### Default layout config

Set a global default in `~/.briefcase/config.yaml`:

```yaml
default_layout: minimal
```

The `--layout` CLI flag takes precedence over the config file.

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
