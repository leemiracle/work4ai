# mlintern Claude Plugin

Use `ml-intern` from inside Claude Code.

[ML Intern](https://github.com/huggingface/ml-intern) is an open-source ML engineer agent from Hugging Face that can research, write, and run ML workflows such as fine-tuning, evaluation, and shipping models. This plugin makes it easy to invoke that workflow from Claude Code.

## Experimental

This plugin is experimental and may change frequently. Expect rough edges.

## What this plugin provides

- `/mlintern:setup` to verify local setup
- `/mlintern:run "fine-tune a model"` to run an ML Intern task
- `/mlintern:run --background "..."` to run in background
- `/mlintern:run --model anthropic/claude-opus-4-6 "..."` to pick a model
- `/mlintern:run --status [job-id]` to check running/recent jobs
- `/mlintern:run --result [job-id]` to fetch final output
- `/mlintern:run --cancel [job-id]` to cancel a running job

## Requirements

- Node.js 18+ (if you are already using Claude Code, you should already have this)
- `ml-intern` installed and available on PATH
- Auth configured for `ml-intern` (HF token and any model provider keys you use)

By default, many `ml-intern` setups use an Anthropic model, so setting `ANTHROPIC_API_KEY` is the most reliable first step:

```bash
export ANTHROPIC_API_KEY=sk-...
```

If you prefer Hugging Face-hosted models, pass `--model huggingface/<model-id>` and ensure your HF auth is available (`HF_TOKEN` or `hf auth login`).

The plugin install step itself does not currently install `ml-intern` for you. That keeps plugin install predictable across environments, but means `ml-intern` still needs to be installed separately on your machine.

## Install in Claude Code

The `/plugin ...` .

Install `ml-intern` first (skip if already installed):

```bash
git clone git@github.com:huggingface/ml-intern.git
cd ml-intern
uv sync
uv tool install -e .
```

Then install this Claude plugin (the commands below are Claude Code slash commands and should be run inside an active Claude Code session, not your regular shell terminal):

```bash
/plugin marketplace add huggingface/mlintern-plugin
/plugin install mlintern@huggingface-mlintern
/reload-plugins
/mlintern:setup
```

## Run it!

Now, in your Claude Code session, you can do:

```bash
/mlintern:run --background "Fine-tune a small Whisper model for Arabic speech recognition \
 on a GPU under 5 dollars and compare the fine-tuned model's metrics to the original model."
/mlintern:run --model huggingface/openai/gpt-oss-120b "Summarize the best Arabic ASR datasets."
/mlintern:run --status
/mlintern:run --result
```
