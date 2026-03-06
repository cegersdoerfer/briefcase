Toolreg CLI — Concise Implementation Plan

Goal

Build a minimal CLI that lets users maintain a shared local registry of reusable GitHub repos and quickly scaffold new coding-agent projects that expose selected repos locally via refs/ symlinks.

MVP Scope

Implement only these commands:
	•	toolreg add <name> <repo_url>
	•	toolreg list
	•	toolreg new <project_name> --tool <name>...
	•	toolreg update <name> and toolreg update --all

Primary User Workflow
	1.	Add reusable tools once into a shared registry.
	2.	Create a new project that symlinks selected tools into refs/.
	3.	Hand the project directory to a coding agent.
	4.	Agent reads AGENT_CONTEXT.md and toolset.yaml before implementation.

Functional Requirements

1. Global registry

Maintain a global home directory:

~/.toolreg/
  repos/
  registry.yaml

registry.yaml should store, per tool:
	•	name
	•	repo_url
	•	local_path
	•	optional notes
	•	optional tags

2. Add command

toolreg add <name> <repo_url> should:
	•	create ~/.toolreg/ and ~/.toolreg/repos/ if missing
	•	clone the repo into ~/.toolreg/repos/<name>
	•	write/update the tool entry in registry.yaml
	•	fail clearly if the destination already exists

3. List command

toolreg list should:
	•	read registry.yaml
	•	print each tool with name and local path
	•	optionally include notes/tags if present

4. New project command

toolreg new <project_name> --tool <name>... should:
	•	create a new project directory
	•	create subdirectories: src/, tests/, refs/
	•	create symlinks in refs/ to each selected registered repo
	•	generate toolset.yaml
	•	generate AGENT_CONTEXT.md
	•	fail clearly if the project directory already exists
	•	fail clearly if a requested tool is not registered

5. Update command

toolreg update <name> should:
	•	run git pull --ff-only in the selected repo

toolreg update --all should:
	•	iterate all registered repos
	•	run git pull --ff-only for each
	•	report per-repo success/failure

Generated Project Files

toolset.yaml

Include:
	•	project name
	•	list of selected tools
	•	local relative path for each tool, e.g. ./refs/fastapi
	•	short purpose/notes if available
	•	fixed rules:
	•	do not modify ./refs
	•	implement new code under ./src
	•	add tests under ./tests

AGENT_CONTEXT.md

Include:
	•	instruction to implement in src/
	•	explanation that referenced tools are in refs/
	•	list of referenced tools and their purposes
	•	instruction not to modify anything under refs/
	•	instruction to use referenced repos for examples and API understanding

Technical Design

Language and libraries

Use Python.
Recommended libraries:
	•	typer for CLI
	•	pyyaml for registry and manifest files
	•	rich for readable terminal output
	•	standard library pathlib for paths
	•	standard library subprocess for Git commands

Internal modules

Suggested structure:

toolreg/
  pyproject.toml
  README.md
  toolreg/
    cli.py
    registry.py
    gitops.py
    scaffold.py
    templates.py

Responsibilities:
	•	cli.py: command definitions and argument parsing
	•	registry.py: create/load/save registry, CRUD helpers
	•	gitops.py: Git clone/pull wrappers with error handling
	•	scaffold.py: project creation and symlink logic
	•	templates.py: render toolset.yaml and AGENT_CONTEXT.md

Error Handling Requirements

Handle these cases cleanly:
	•	repo already exists when adding
	•	invalid or unreachable Git URL
	•	requested tool is missing from registry
	•	project directory already exists
	•	symlink creation failure
	•	git pull failure during update
	•	malformed registry.yaml

Errors should be human-readable and actionable.

Platform Assumptions

Target macOS/Linux first.
Use filesystem symlinks for refs/.
Windows support can be deferred unless explicitly needed.

Non-Goals for MVP

Do not implement yet:
	•	repo summarization
	•	vector search or embeddings
	•	dependency installation
	•	patching shared repos
	•	worktree management
	•	template ecosystems beyond a minimal scaffold
	•	automatic agent execution

Implementation Order
	1.	Build registry read/write layer.
	2.	Build Git clone/pull wrappers.
	3.	Implement add and list.
	4.	Implement project scaffold creation for new.
	5.	Generate toolset.yaml and AGENT_CONTEXT.md.
	6.	Implement update and update --all.
	7.	Add polish: better terminal output, clearer errors, basic tests.

Acceptance Criteria

The MVP is complete when the following works end-to-end:

toolreg add fastapi https://github.com/fastapi/fastapi
toolreg add litellm https://github.com/BerriAI/litellm
toolreg list
toolreg new my-app --tool fastapi --tool litellm

And my-app/ contains:

my-app/
  src/
  tests/
  refs/
    fastapi -> ~/.toolreg/repos/fastapi
    litellm -> ~/.toolreg/repos/litellm
  toolset.yaml
  AGENT_CONTEXT.md

Recommended Phase 2

After MVP is stable, add:
	•	per-tool notes editing
	•	support for project config input files
	•	commit SHA snapshot recording in toolset.yaml
	•	validation/doctor command
	•	optional richer scaffold templates
