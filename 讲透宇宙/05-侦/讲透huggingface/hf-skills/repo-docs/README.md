# hf-skills

Standalone Hugging Face skills installer CLI.

## Why include a Manifest?

The [agentskills.io](https://agentskills.io) spec doesn't require a version in the frontmatter. When version numbers are included, they often aren't updated as the skill changes. A small manifest describing the source commit (local or remote) makes auto-updating simple!

## Commands

```bash
Usage: hf-skills [OPTIONS] COMMAND [ARGS]...

  Browse, install, and manage skills from the Hugging Face skills marketplace.

Options:
  --install-completion  Install completion for the current shell.
  --show-completion     Show completion for the current shell, to copy it or customize the installation.
  -h, --help            Show this message and exit.

Main commands:
  install    Install a registry skill into the selected target directory. [alias: add]
  installed  List installed skills across known directories, or a specific one when narrowed.
  list       List skills available from the configured registry. [alias: ls]
  search     Search registry skills by name or description.
  uninstall  Remove an installed skill, scanning known directories unless narrowed. [alias: remove, rm]
  update     Update installed skills across known directories, or a specific one when narrowed.
  where      Show which local skills directory install/remove/update will use. [alias: target]
```

**IMPORTANT:** Use `--global` to target your home directory.


## Development

```bash
uv sync --dev
uv run ruff format .
uv run ruff check .
uv run ty check
uv run pytest
```

