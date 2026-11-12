# Asta Resource Repository

A lightweight document metadata index for AI coding agents. Track documents, papers, and resources with tags and summaries—no databases, just a git-friendly YAML file.

## What It Does

This tool helps you and your AI agents keep track of documents by storing **metadata only** (URLs, summaries, tags) in a simple `.asta/documents/index.yaml` file. Think of it as a smart bookmark manager that AI agents can use.

**Key Features:**
- 📋 **Metadata only**: URLs, summaries, tags—no content storage
- 🔧 **CLI + Skill**: Full document management via command line and Claude Code skill
- ⚡ **Zero setup**: No databases, no Docker, no external services
- 📝 **Git-friendly**: Human-readable YAML diffs
- 🔍 **Searchable**: Multiple search modes (simple, keyword, semantic, hybrid)
- 🏷️ **Taggable**: Organize with custom tags
- 🚀 **Portable**: Copy `.asta/` folder anywhere
- 💾 **Smart caching**: Automatic content caching with SHA256 verification

## Installation

**Prerequisites**: Python 3.10+ and [uv](https://docs.astral.sh/uv/) package manager

**Install with uv:**

```bash
uv tool install git+https://github.com/allenai/asta-resource-repo.git
```

This installs the `asta-documents` CLI globally.

## Skill Installation

The [asta-documents](skills/asta-documents/SKILL.md) skill provides agent instructions for using the `asta-documents` CLI.

**Claude Code:**
```bash
curl -o ~/.claude/skills/asta-documents.md https://raw.githubusercontent.com/allenai/asta-resource-repo/main/skills/asta-documents/SKILL.md
```

**skills.sh:**
```bash
npx skills add add allenai/asta-resource-repo/skills
```

## Command Line Usage
- 
See the **Asta-Documents Skill**: [skills/asta-documents/SKILL.md](skills/asta-documents/SKILL.md)

## Development

Want to contribute or modify the code? See:
- **[CLAUDE.md](CLAUDE.md)** - Architecture and development guide
- **[BEADS.md](BEADS.md)** - Issue tracking with Beads

## License

Apache 2.0 License. See [LICENSE](LICENSE) for details.
