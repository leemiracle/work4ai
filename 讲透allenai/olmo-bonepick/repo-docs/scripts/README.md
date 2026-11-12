# Scripts

Utility scripts for working with bonepick datasets.

## compare_jsonl.py

Compare two JSONL files and find entries where they disagree on a specific field value.

### Features

- Supports compressed (.jsonl.zst, .jsonl.gz) and uncompressed (.jsonl) files
- Uses jq expressions to extract values for comparison
- Matches entries by a text field (default: "text")
- Outputs detailed disagreement records with values from both files
- Shows comprehensive statistics about the comparison

### Usage

Basic usage:
```bash
uv run python3 scripts/compare_jsonl.py file1.jsonl.zst file2.jsonl.zst \
    --value-path '.label' \
    --text-field 'text' \
    --output disagreements.jsonl.zst
```

Interactive mode (browse disagreements one at a time):
```bash
uv run python3 scripts/compare_jsonl.py file1.jsonl.zst file2.jsonl.zst \
    --value-path '.label' \
    --interactive
```

Just show statistics without writing output:
```bash
uv run python3 scripts/compare_jsonl.py file1.jsonl.zst file2.jsonl.zst \
    --value-path '.label' \
    --stats-only
```

Compare nested fields:
```bash
uv run python3 scripts/compare_jsonl.py file1.jsonl.zst file2.jsonl.zst \
    --value-path '.metadata.quality_score' \
    --text-field 'content'
```

### Output Format

When `--output` is specified, disagreements are written as JSONL with the following structure:

```json
{
  "text": "the text content used for matching",
  "value_file1": "value from first file",
  "value_file2": "value from second file",
  "file1_name": "file1.jsonl.zst",
  "file2_name": "file2.jsonl.zst",
  "row_file1": {"full": "row from file1"},
  "row_file2": {"full": "row from file2"}
}
```

### Interactive Mode

Use `--interactive` or `-i` to browse disagreements one at a time:
- Press ENTER to see the next example
- Type `q` + ENTER to quit
- Type `s` + ENTER to skip to the end

This mode shows the full text (up to 500 characters) and the disagreeing values from both files.

### Statistics Output

The script always prints statistics including:
- Number of entries in each file
- Number of common entries (found in both files)
- Number of entries unique to each file
- Number of disagreements
- Disagreement rate (percentage of common entries that disagree)

### Use Cases

1. **Compare model predictions**: Compare annotations from different models
2. **Validate data transformations**: Ensure transformations preserve labels correctly
3. **Quality control**: Find inconsistencies between dataset versions
4. **Annotation comparison**: Compare human annotations with model predictions
