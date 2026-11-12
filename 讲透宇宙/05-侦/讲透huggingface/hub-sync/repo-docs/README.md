# hub-sync action

A GitHub Action that syncs your repository to Hugging Face Hub 🤗

Uses the official HF CLI via `uvx` to deploy to Spaces, Models, or Datasets.

## Quick Start

Add your HF token as a GitHub secret (`HF_TOKEN`), then:

```yaml
name: Sync GitHub to Hugging Face Hub
on:
  push:
    branches: [main]

jobs:
  sync:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6
      - uses: huggingface/hub-sync@v0.3.0
        with:
          github_repo_id: ${{ github.repository }}
          huggingface_repo_id: username/repo-name
          hf_token: ${{ secrets.HF_TOKEN }}
```

## Usage

### All Options

```yaml
- uses: huggingface/hub-sync@v0.3.0
  with:
    # Required
    github_repo_id: ${{ github.repository }}
    huggingface_repo_id: username/repo-name
    hf_token: ${{ secrets.HF_TOKEN }}
    
    # Optional
    repo_type: space              # space | model | dataset (default: space)
    space_sdk: gradio             # gradio | streamlit | docker | static (default: gradio)
    private: false                # Create as private (default: false)
    subdirectory: ''              # Sync only this folder (default: '' = root)
    exclude: |                    # Extra patterns to skip, one per line
      *.env
      node_modules/
    include: |                    # Allowlist, if set, only these are uploaded
      *.py
    delete_removed: true          # Remove Hub files outside the upload set (default: true)
    hf_version: ''                # Pin the hf CLI version (default: '' = latest)
```

### Filtering what gets synced

Three patterns are always excluded and cannot be turned off:

- `.git*` at the root — covers `.git/`, `.gitignore`, `.gitattributes`, `.github/`
- `*/.git/` at any depth — a submodule's git directory
- `*/.github/` at any depth — nested CI config

Nested dotfiles still sync, so `templates/.gitignore` and `docs/.gitkeep` reach the Hub.

`exclude` adds to that list. `include` is an allowlist: set it and only matching files upload. Blank lines and `#` comments are ignored.

Patterns are `fnmatch` globs. Gitignore syntax does not apply. `*` crosses directory boundaries, so `data/*` matches `data/sub/deep.json` and `**` is never needed. A trailing slash matches a directory's contents, so `node_modules/` works. Matching is case-sensitive on every platform.

> [!WARNING]
> By default the action mirrors, so a filtered-out file is **deleted from the Hub** if it is already there. Excluding a path removes the Hub copy too. If the Hub repo holds files written by something else — a training job, a separate upload — set `delete_removed: false` to upload without deleting anything.

## Features

- **Automatic exclusions** — root git metadata plus nested `.git/` and `.github/` directories, and cannot be disabled
- **User-defined patterns** — add your own `exclude` rules or an `include` allowlist
- **True mirroring** — deletes removed files from HF, or set `delete_removed: false` to only ever add
- **Subdirectory support** — suitable for monorepos
- **Source-aware commit messages** — synced commits identify the originating GitHub repository
