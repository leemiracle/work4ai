# hf-claude

extension for `hf` to launch Claude Code with [Hugging Face Inference Providers](https://huggingface.co/docs/inference-providers/en/index)

It lets you pick:
- model (from `https://router.huggingface.co/v1/models`)
- provider (`auto` or a concrete provider for the selected model)

Then it runs `claude --model <model[:provider]>` with the required env vars preconfigured.

## Requirements

- Claude Code CLI installed
- `curl`, `jq`, `bash`
- [`fzf`](https://github.com/junegunn/fzf#installation) *(optional)* — enables fuzzy model/provider search; without it the launcher falls back to an arrow-key menu (↑/↓ to move, Enter to select)
- A Hugging Face token, via either:

```bash
curl -LsSf https://hf.co/cli/install.sh | bash
hf auth login        
# or
export HF_TOKEN='hf_...'
```

## Install

```bash
hf extensions install hf-claude
# add --force to reinstall the extension
```

## Run

```bash
hf claude
# or
hf extensions exec claude
```

Forward extra args to Claude Code:

```bash
hf claude --help
hf extensions exec claude -- --help
```

## Billing to an organization

To bill inference usage to a Hugging Face organization instead of your personal
account, pass `--bill-to` (you must have Write privileges in the org):

```bash
hf claude --bill-to your-org-name
```

This sets the router's `X-HF-Bill-To` header (via `ANTHROPIC_CUSTOM_HEADERS`) on
every request. You can also set it via the `HF_BILL_TO` environment variable:

```bash
export HF_BILL_TO=your-org-name
hf claude
```
