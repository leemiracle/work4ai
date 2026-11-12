# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Run CLI commands
uv run bonepick <command>
uv run bonepick --help

# Run tests
uv run pytest
uv run pytest tests/test_indent_utils.py  # single file
uv run pytest -k "test_name"              # single test

# Format code
uv run ruff format .

# Commit (Claude must add co-author)
git commit -m "message

Co-Authored-By: Claude <model> <noreply@anthropic.com>"
```

**Important**: Claude must always add co-author trailer to commits, including the model name (e.g., `Claude Opus 4.6`).

## Executing commands

**IMPORTANT**: Always prefer `uv run` rather than using Python executable. This is a uv-first repo.

## Architecture

CLI tool for training efficient text quality classifiers (Model2Vec and FastText) on text data, with LLM-based annotation and calibration evaluation tools.

### Module Structure

```
src/bonepick/
├── __init__.py        # Command registration hub (all commands added to cli here)
├── cli.py             # Click CLI setup + custom param types
├── logger.py          # Logging initialization (file + stderr handlers)
├── version.py         # Package version string
├── data/
│   ├── commands.py    # Data pipeline CLI commands
│   ├── utils.py       # DatasetSplit, DatasetTuple, ChunkedDataset, file I/O helpers
│   ├── normalizers.py # Text normalizer registry
│   ├── expressions.py # JQ expression utilities + calibration jq generation
│   ├── indentation.py # Space-to-tab indentation detection/conversion (for code normalizers)
│   ├── tokenizers.py  # Parallel tokenization utilities
│   └── tokenizers_config/  # Bundled tokenizer JSON configs
│       ├── dolma2_tokenizer.json
│       └── ultra_fineweb_tokenizer.json
├── model2vec/
│   ├── commands.py    # train/eval/distill commands
│   └── utils.py       # StaticModelForClassification, StaticModelForRegression
├── fasttext/
│   ├── commands.py    # train/eval/infer commands
│   └── utils.py       # FastText binary helpers
├── evals/
│   ├── commands.py    # eval-calibration, train-calibration commands
│   ├── utils.py       # Shared metrics computation (AUC, correlation, regression, calibration)
│   ├── display.py     # Rich-based CLI display for evaluation results
│   └── modeling.py    # Calibration model fitting (Ridge, L-BFGS-B)
└── annotate/          # Optional LLM annotation (requires --extra annotate)
    ├── annotate_loop.py     # annotate-dataset, list-prompts commands
    ├── analysis_loop.py     # annotation-agreement, label-distribution commands
    ├── batch_loop.py        # batch-annotate-submit, batch-annotate-retrieve commands
    ├── prompts.py           # BasePrompt, BaseSystemPrompt, BaseAnnotationPrompt base classes
    ├── annotate_utils.py    # DataclassType protocol
    ├── deluge_utils.py      # SqliteInvalidableCache, lm-deluge monkey patching
    ├── pydantic_utils.py    # dataclass_to_json_schema converter
    └── prompt_collections/  # 63+ annotation task prompts, 3 system prompts
        ├── code_rubrics.py
        ├── content_rubrics.py
        ├── sft_filtering.py
        └── stack_edu_rubrics.py
```

### Code Style

- **CLI pattern**: Each command is a `@click.command()` function in a `commands.py` file, registered in `__init__.py`
- **Custom Click types**: Use `PathParamType`, `FloatOrIntParamType`, `ByteSizeParamType`, `PCADimTypeParamType` from `cli.py`
- **Parallel processing**: Use `ProcessPoolExecutor`/`ThreadPoolExecutor` with `as_completed()` pattern
- **File I/O**: Use `smart_open` for transparent compression (.zst, .gz) support
- **JSON**: Use `msgspec.json.Encoder/Decoder` for fast serialization
- **JQ expressions**: Use `compile_jq()` from `data/expressions.py` for field transforms
- **Options pattern**: Use `multiple=True` for options that accept multiple values (e.g., `-d/--dataset-dir`)

### Data Pipeline

1. `import-hf-dataset` - Downloads HuggingFace datasets to local JSONL
2. `transform-dataset` - Applies jq expressions to reshape fields
3. `balance-dataset` - Balances datasets by label
4. `sample-dataset` - Random sampling by rate or target size
5. `reshard-dataset` - Combines files into evenly-sized shards (supports train/test/valid split creation)
6. `normalize-dataset` - Text normalization
7. `convert-to-fasttext` - Converts JSONL to FastText format
8. `count-tokens` - Token counting with specified tokenizer

### Data Format

- Compressed JSONL (`.jsonl.zst`, `.jsonl.gz`, `.jsonl`) in `train/` and `test/` subdirectories
- Each row needs `text` and `label` fields (configurable via `--text-field`, `--label-field`)
- Multiple `-d/--dataset-dir` options supported for combining datasets

### Key Data Structures

- `DatasetSplit`: Holds parallel `text` and `label` lists for a single split
- `DatasetTuple`: Contains `train`, `valid`, `test` splits with signature hashing
- `ChunkedDataset`: Chunked dataset abstraction for large datasets

## Normalizers

`whitespace`, `plsfix`, `tokenizer`, `ultrafine`, `ultrafine_commits`, `hyperfine`, `hyperfine_code`, `potion`, `potion_code`

Note: normalizer names use **underscores** (e.g., `hyperfine_code`, not `hyperfine-code`).

## Testing

- Test data: `tests/data/`
- Test output: `tests/output/` (gitignored)

## Tips

- For Model2Vec: normalize BEFORE training
- For FastText: normalize during `convert-to-fasttext`
