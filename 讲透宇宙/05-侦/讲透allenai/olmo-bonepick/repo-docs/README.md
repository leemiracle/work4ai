
<p align="center">
  <img src="https://github.com/allenai/olmo-bonepick/blob/main/assets/logo.png?raw=true" alt="Olmo Bonepick library logo" width="500"/>
</p>

`bonepick` is a CLI tool for training efficient text quality classifiers that run on CPU. It supports [**Model2Vec**][1] (static embeddings) and [**FastText**][2] classifiers, with built-in tools for data preparation, LLM-based annotation, batch annotation via async APIs, calibration evaluation, and model distillation.

## Installation

From PyPI:

```
pip install bonepick
```

From source:

```shell
git clone https://github.com/allenai/olmo-bonepick.git
cd olmo-bonepick
uv sync .
```

### Optional Dependencies

The `annotate` extra provides tools for using LLM APIs to label data:

```shell
uv sync --extra annotate
```

This enables the `annotate-dataset`, `batch-annotate-submit`, `batch-annotate-retrieve`, `list-prompts`, `annotation-agreement`, and `label-distribution` commands for automated data annotation using LLM providers via the `lm-deluge` library.

The `distill` extra provides tools for distilling Sentence Transformer models to Model2Vec:

```shell
uv sync --extra distill
```

Install both at once:

```shell
uv sync --extra annotate --extra distill
```

## Data Format

Datasets are stored as compressed JSONL files (`.jsonl.zst`, `.jsonl.gz`, or `.jsonl`) in `train/` and `test/` subdirectories. Each row must have a text field and a label field.

```
dataset/
├── train/
│   ├── shard_0.jsonl.zst
│   └── shard_100000.jsonl.zst
└── test/
    └── shard_0.jsonl.zst
```

## Data Preparation Pipeline

### 1. Import from HuggingFace

Download a HuggingFace dataset to local JSONL format:

```shell
uv run bonepick import-hf-dataset \
    -n HuggingFaceFW/fineweb-edu-llama3-annotations \
    -o data/fineweb-edu-llama3-annotations \
    --test-split 0.1
```

### 2. Transform Labels (Optional)

Use jq expressions to reshape fields. Common use case: binarize multi-class labels.

```shell
# Binarize scores: 0-1 → 0 (low quality), 2-5 → 1 (high quality)
uv run bonepick transform-dataset \
    --input-dir data/fineweb-edu-llama3-annotations \
    --output-dir data/fineweb-edu-binary \
    -l '{score: (if .score < 2 then 0 else 1 end)}'

# Or use string labels
uv run bonepick transform-dataset \
    --input-dir data/fineweb-edu-llama3-annotations \
    --output-dir data/fineweb-edu-binary \
    -l '{score: (if .score < 2 then "neg" else "pos" end)}'
```

### 3. Balance Dataset (Optional)

Balance the dataset so each label has equal representation. Useful when one class significantly outnumbers others:

```shell
uv run bonepick balance-dataset \
    --input-dir data/fineweb-edu-binary \
    --output-dir data/fineweb-edu-binary-balanced \
    --seed 42
```

Supports multiple input directories:

```shell
uv run bonepick balance-dataset \
    -i data/dataset1 \
    -i data/dataset2 \
    -o data/combined-balanced \
    --seed 42
```

### 3a. Sample Dataset (Optional)

Create a smaller random sample of a dataset. Useful for quick experiments or when you need a subset:

```shell
# Sample 10% of the dataset
uv run bonepick sample-dataset \
    -i data/fineweb-edu-binary \
    -o data/fineweb-edu-sample \
    --sampling-rate 0.1

# Or specify a target size
uv run bonepick sample-dataset \
    -i data/fineweb-edu-binary \
    -o data/fineweb-edu-sample \
    --target-size 500MB

# Supports multiple input directories
uv run bonepick sample-dataset \
    -i data/dataset1 \
    -i data/dataset2 \
    -o data/combined-sample \
    --target-size 1GB
```

### 3b. Reshard Dataset (Optional)

Combine multiple small files into a specified number of larger files with roughly equal sizes. Useful for reducing I/O overhead and creating evenly-sized shards:

```shell
# Reshard into 10 output files
uv run bonepick reshard-dataset \
    -d data/fineweb-edu-binary \
    -o data/fineweb-edu-resharded \
    -n 10

# Create train/test splits during resharding
uv run bonepick reshard-dataset \
    -d data/raw-dataset \
    -o data/split-dataset \
    -n 10 \
    --test-split-frac 0.1

# Create train/valid/test splits
uv run bonepick reshard-dataset \
    -d data/raw-dataset \
    -o data/split-dataset \
    -n 10 \
    --test-split-frac 0.1 \
    --valid-split-frac 0.05

# Use more processes for faster resharding
uv run bonepick reshard-dataset \
    -d data/large-dataset \
    -o data/resharded \
    -n 20 \
    -p 8
```

The command uses a greedy bin packing algorithm to ensure output files have roughly equal sizes. It supports multiple input directories via repeated `-d` flags, and can optionally create train/test/valid splits with `--test-split-frac` and `--valid-split-frac`.

### 4a. Normalize Text (for Model2Vec)

Apply text normalization before training Model2Vec classifiers:

```shell
uv run bonepick normalize-dataset \
    --input-dir data/fineweb-edu-binary \
    --output-dir data/fineweb-edu-binary-normalized \
    -n plsfix
```

Available normalizers: `whitespace`, `plsfix`, `tokenizer`, `ultrafine`, `ultrafine_commits`, `hyperfine`, `hyperfine_code`, `potion`, `potion_code`

### 4b. Convert to FastText Format (for FastText)

Convert JSONL to FastText's `__label__<label> <text>` format:

```shell
uv run bonepick convert-to-fasttext \
    --input-dir data/fineweb-edu-binary \
    --output-dir data/fasttext-fineweb-edu-binary \
    -n ultrafine
```

#### Auto-binning Numeric Labels

For datasets with continuous or many discrete numeric labels, use `--auto N` to automatically bin labels into N equal-count (quantile-based) bins:

```shell
# Bin numeric scores into 5 quantile-based bins
uv run bonepick convert-to-fasttext \
    --input-dir data/scored-dataset \
    --output-dir data/fasttext-binned \
    --label-expression '.score' \
    --auto 5 \
    -n ultrafine
```

This performs a two-pass operation:
1. **Pass 1**: Reads all training labels to compute quantile boundaries
2. **Pass 2**: Converts data using the computed bins

The output shows bin edges and sample distribution:
```
Bin edges and labels (equal-count/quantile bins):
    bin_0: [0.0000, 11.0000)
    bin_1: [11.0000, 13.0000)
    bin_2: [13.0000] (single-value bin)
    bin_3: (13.0000, 15.0000)
    bin_4: [15.0000, 19.0000)
```

Single-value bins (where many samples share the same value) are supported and displayed with `[value]` notation. The bin mapping is saved in the output `report.yaml` for reference.

### 5. Count Tokens (Optional)

Count the total number of tokens in a dataset using a specified tokenizer. Useful for understanding dataset size and token distribution:

```shell
# Count tokens using default tokenizer (bundled dolma2 tokenizer)
uv run bonepick count-tokens \
    -d data/fineweb-edu-binary

# Use a custom tokenizer
uv run bonepick count-tokens \
    -d data/fineweb-edu-binary \
    -t microsoft/deberta-base

# Custom field extraction with JQ expression
uv run bonepick count-tokens \
    -d data/custom-dataset \
    -i ".content"

# Count tokens across multiple datasets
uv run bonepick count-tokens \
    -d data/dataset1 \
    -d data/dataset2 \
    -d data/dataset3

# Use more processes for faster counting
uv run bonepick count-tokens \
    -d data/large-dataset \
    -p 16
```

The command outputs:
- Total files processed
- Total token count
- Total dataset size in bytes
- Average tokens per file
- Average tokens per byte

## Training

### Model2Vec Classifier

Trains a classifier head on top of frozen Model2Vec static embeddings:

```shell
uv run bonepick train-model2vec \
    -d data/fineweb-edu-binary-normalized \
    -o models/model2vec-classifier
```

Key options:
- `-m/--model-name`: Model2Vec model to use (default: `minishlab/potion-base-32M`)
- `--learning-rate`: Learning rate (default: 1e-3)
- `--max-epochs`: Maximum training epochs (default: -1 for unlimited)
- `--early-stopping-patience`: Epochs without improvement before stopping (default: 5)
- `--loss-class-weight`: Class weighting strategy: `balanced`, `uniform`, `sqrt` (default: `uniform`)
- `--regression`: Train a regressor instead of classifier
- `--normalizer`: Apply a normalizer during training
- `--max-length`: Maximum text length

### FastText Classifier

Trains a FastText classifier (requires `fasttext` binary in PATH):

```shell
uv run bonepick train-fasttext \
    -d data/fasttext-fineweb-edu-binary \
    -o models/fasttext-classifier
```

### Training on Multiple Datasets

All training commands support combining data from multiple directories using repeated `-d` flags:

```shell
# Combine multiple datasets for training
uv run bonepick train-model2vec \
    -d data/dataset1-normalized \
    -d data/dataset2-normalized \
    -d data/dataset3-normalized \
    -o models/combined-classifier
```

Data from all directories is concatenated before training. Each directory must have `train/` and `test/` subdirectories.

## Evaluation

Both evaluation commands compute detailed classification metrics using probability predictions (`predict_proba` for Model2Vec, `predict-prob` for FastText). Results include precision, recall, F1-score, and AUC for each class, plus macro averages.

### Model2Vec Evaluation

```shell
uv run bonepick eval-model2vec \
    -d data/fineweb-edu-binary-normalized \
    -m models/contrastive-classifier \
    --text-field text \
    --label-field score
```

### FastText Evaluation

```shell
uv run bonepick eval-fasttext \
    -d data/fasttext-fineweb-edu-binary \
    -m models/fasttext-classifier \
    --text-field text \
    --label-field score
```

### Multi-Dataset Evaluation

Evaluate on multiple datasets simultaneously. Results are computed on the combined test sets:

```shell
uv run bonepick eval-model2vec \
    -d data/dataset1-normalized \
    -d data/dataset2-normalized \
    -d data/dataset3-normalized \
    -m models/combined-classifier
```

### Output Format

Results are saved as YAML files in the model directory with the naming pattern `results_<dataset_signature>.yaml`:

```yaml
dataset_dir:
  - data/fineweb-edu-binary-normalized
model_dir: models/model2vec-classifier
overall_results:
  macro_precision: 0.8734
  macro_recall: 0.8621
  macro_f1: 0.8677
  macro_auc: 0.9245
per_class_metrics:
  - class_name: '0'
    precision: 0.8512
    recall: 0.8823
    f1: 0.8665
    support: 1523
    auc: 0.9245
  - class_name: '1'
    precision: 0.8956
    recall: 0.8419
    f1: 0.8679
    support: 1477
    auc: 0.9245
```

### Metrics Explained

- **Precision**: Of all predictions for a class, how many were correct
- **Recall**: Of all actual instances of a class, how many were predicted correctly
- **F1**: Harmonic mean of precision and recall
- **AUC**: Area Under the ROC Curve (one-vs-rest for multi-class)
- **Macro averages**: Unweighted mean across all classes
- **Support**: Number of true instances for each class in the test set

### Custom Field Names

Both evaluation commands support custom field names if your dataset uses different column names:

```shell
uv run bonepick eval-model2vec \
    -d data/custom-dataset \
    -m models/my-classifier \
    --text-field document \
    --label-field quality_score
```

## Calibration Evaluation

Evaluate and train calibration models for prediction quality assessment.

### Evaluate Calibration

Evaluate scalar predictions (0-1) against ordinal gold labels. Computes AUC, rank correlation, regression, and calibration metrics:

```shell
# Evaluate predictions from a single dataset
uv run bonepick eval-calibration \
    -d ./annotated_data \
    -p '.metadata.classifier.quality_score' \
    -l '.annotation.rating'

# Evaluate from multiple directories with output file
uv run bonepick eval-calibration \
    -d ./data1 -d ./data2 \
    -p '.prediction' \
    -l '.label' \
    -o results.yaml
```

Metrics computed:
- **AUC**: Macro, weighted, and ordinal (adjacent pairs) using Mann-Whitney U
- **Correlation**: Spearman, Kendall's Tau-b, Pearson
- **Regression**: MSE, RMSE, MAE, R-squared (labels normalized to 0-1)
- **Calibration**: Expected Calibration Error with bin analysis

### Train Calibration Model

Learn weights for prediction components to approximate gold labels. Useful for understanding how different model prediction dimensions relate to human annotations:

```shell
# Train linear model mapping prediction components to gold ratings
uv run bonepick train-calibration \
    -d ./annotated_data \
    -p '.prediction.components' \
    -l '.annotation.rating' \
    -m linear

# Train log-linear model with output file
uv run bonepick train-calibration \
    -d ./data \
    -p '.model_scores' \
    -l '.gold_label' \
    -m log-linear \
    -o calibration_weights.yaml
```

Model types:
- **linear**: `score = clamp(sum(w_i * pred_i) + bias, 0, 1)`
- **log-linear**: `score = sigmoid(sum(w_i * pred_i) + bias)`

The prediction expression must return a dict of `{component_name: value}`. Outputs include learned weights, fit metrics (R-squared, RMSE, MAE), and a ready-to-use jq expression.

## Data Annotation (Optional)

The annotation features require the `annotate` extra dependencies (`uv sync --extra annotate`).

### List Available Prompts

```shell
# List available task prompts
uv run bonepick list-prompts task

# List available system prompts
uv run bonepick list-prompts system
```

### Annotate Dataset with LLM

Use LLM APIs to automatically label or annotate your dataset:

```shell
uv run bonepick annotate-dataset \
    -d data/unlabeled-dataset \
    -o data/annotated-dataset \
    -m gpt-5.2 \
    -T <task-prompt-name> \
    -i ".text" \
    --max-requests-per-minute 100
```

Key options:
- `-d/--dataset-dir`: Input dataset directory (can specify multiple)
- `-o/--output-dir`: Output directory for annotated data
- `-m/--model-name`: Model to use (default: gpt-5.2)
- `-T/--annotation-task-prompt`: Name of annotation task prompt (required)
- `-S/--annotation-system-prompt`: Name of system prompt (optional)
- `-i/--input-field-expression`: jq expression to extract input text (default: `.text`)
- `-f/--input-field-format`: Input format: `text` or `conversation` (default: text)
- `-r/--reasoning-effort`: Reasoning effort level: `minimal`, `low`, `medium`, `high`, `xhigh`, `none`
- `-e/--service-tier`: Service tier: `auto`, `default`, `flex`, `priority` (optional)
- `-c/--cache-location`: Cache location for LLM responses
- `--reprocess-all-rows/--process-missing-rows`: Reprocess behavior
- `--max-requests-per-minute`, `--max-tokens-per-minute`, `--max-concurrent-requests`: Rate limiting
- `--max-text-length`, `--max-new-tokens`: Length constraints
- `--limit-rows`: Maximum rows to annotate

### Batch Annotation

For large-scale annotation jobs, use the batch API workflow which submits requests asynchronously and retrieves results later:

```shell
# Step 1: Submit batch job
uv run bonepick batch-annotate-submit \
    -d data/unlabeled-dataset \
    -b data/batch-job \
    -m gpt-5.2 \
    -T <task-prompt-name> \
    -i ".text"

# Step 2: Retrieve results (waits for batch completion)
uv run bonepick batch-annotate-retrieve \
    -b data/batch-job \
    -o data/annotated-dataset
```

The submit step creates a batch directory with a manifest and compressed rows file, then submits prompts via the provider's batch API (OpenAI or Anthropic). The retrieve step waits for completion and merges results back with the original data.

Key options for `batch-annotate-submit`:
- `-d/--dataset-dir`: Input dataset directory (can specify multiple)
- `-b/--batch-dir`: Batch output directory for job state
- `-m/--model-name`: Model to use (default: gpt-5.2)
- `-T/--annotation-task-prompt`: Name of annotation task prompt (required)
- `-S/--annotation-system-prompt`: Name of system prompt (optional)
- `--annotation-batch-size`: Max items per API batch (default: 50000)
- `--reprocess-all-rows/--process-missing-rows`: Reprocess behavior
- `--limit-rows`: Maximum rows to annotate

### Compare Annotation Agreement

Compare annotations between two datasets to measure inter-annotator agreement:

```shell
uv run bonepick annotation-agreement \
    --dataset-dir data/annotator1 \
    --dataset-dir data/annotator2 \
    --label-expression '.label' \
    --key-expression '.id'
```

This command computes agreement metrics between two annotation datasets, useful for:
- Measuring inter-annotator reliability between human annotators
- Comparing human annotations vs LLM annotations
- Validating annotation quality across different annotation rounds

Key options:
- `--dataset-dir`: Paths to the dataset directories (specify multiple times, required)
- `--label-expression`: JQ expression to extract the label/annotation (e.g., `.label`, `.annotation.category`)
- `--key-expression`: JQ expression to extract a unique identifier (e.g., `.id`, `.text`)
- `--show-confusion-matrix/--no-confusion-matrix`: Show confusion matrix (default: true)
- `--show-disagreements/--no-disagreements`: Show examples where annotators disagreed (default: false)
- `--max-disagreements`: Maximum disagreement examples to show (default: 10)
- `--ordinal/--no-ordinal`: Treat labels as ordinal (ordered) values (default: false)

Example with nested fields:

```shell
uv run bonepick annotation-agreement \
    --dataset-dir data/human-annotations \
    --dataset-dir data/llm-annotations \
    --label-expression '.annotation.quality_score' \
    --key-expression '.metadata.document_id' \
    --show-disagreements \
    --max-disagreements 20
```

#### Ordinal Labels

For numeric labels where order matters (e.g., rating scales 1-5), use `--ordinal` to compute metrics that account for the distance between ratings:

```shell
uv run bonepick annotation-agreement \
    --dataset-dir data/rater1 \
    --dataset-dir data/rater2 \
    --label-expression '.score' \
    --key-expression '.id' \
    --ordinal
```

With `--ordinal`, the command computes:
- **Weighted Kappa (quadratic)**: Penalizes distant disagreements more heavily (13 vs 14 is less severe than 13 vs 30)
- **Mean Absolute Error (MAE)**: Average absolute difference between ratings
- **Root Mean Squared Error (RMSE)**: Emphasizes larger disagreements
- **Pearson Correlation**: Measures linear relationship between raters
- **Difference Histogram**: Visual distribution of rating differences

The command outputs:
- **Dataset coverage**: Samples in each dataset, common samples, unique samples
- **Agreement rate**: Percentage of matching labels
- **Cohen's Kappa**: Accounts for chance agreement (0.00-0.20: slight, 0.21-0.40: fair, 0.41-0.60: moderate, 0.61-0.80: substantial, 0.81-1.00: almost perfect)
- **Label distribution**: Comparison of label frequencies between datasets
- **Confusion matrix**: Shows which labels are confused with each other
- **Disagreement examples**: Optional display of specific cases where annotators disagreed

## Model Distillation

Distill a Sentence Transformer model to a lightweight Model2Vec static embedding model:

```shell
uv run bonepick distill-model2vec \
    -m sentence-transformers/all-MiniLM-L6-v2 \
    -o models/distilled-model \
    -d 256 \
    --quantize-to float16
```

Key options:
- `-m/--model-name-or-path`: HuggingFace model name or local path (required)
- `-o/--output-dir`: Output directory (required)
- `-v/--vocabulary-path`: Custom vocabulary file (one token per line)
- `-d/--pca-dims`: PCA dimensions for dimensionality reduction (default: 256, or `auto`)
- `-s/--sif-coefficient`: SIF (Smooth Inverse Frequency) coefficient (default: 1e-4)
- `-t/--token-remove-pattern`: Regex pattern for tokens to remove (default: `\[unused\d+\]`)
- `-r/--trust-remote-code`: Allow remote code execution
- `-q/--quantize-to`: Quantization type: `float16`, `float32`, `float64`, `int8` (default: float16)
- `-k/--vocabulary-quantization`: Vocabulary quantization factor
- `-p/--pooling`: Pooling strategy: `mean`, `last`, `first`, `pooler` (default: mean)

## CLI Reference

```shell
uv run bonepick --help
uv run bonepick <command> --help
```

### Data Pipeline Commands

| Command | Description |
|---------|-------------|
| `import-hf-dataset` | Download HuggingFace dataset to local JSONL |
| `transform-dataset` | Apply jq transforms to reshape fields |
| `balance-dataset` | Balance dataset so each label has equal representation |
| `sample-dataset` | Create a random sample of a dataset by rate or target size |
| `reshard-dataset` | Combine multiple files into specified number of evenly-sized files |
| `normalize-dataset` | Normalize text (for Model2Vec) |
| `convert-to-fasttext` | Convert JSONL to FastText format |
| `count-tokens` | Count tokens in dataset directories using a tokenizer |

### Training Commands

| Command | Description |
|---------|-------------|
| `train-model2vec` | Train Model2Vec classifier or regressor |
| `train-fasttext` | Train FastText classifier |
| `distill-model2vec` | Distill Sentence Transformer to Model2Vec |

### Evaluation Commands

| Command | Description |
|---------|-------------|
| `eval-model2vec` | Evaluate Model2Vec classifier |
| `eval-fasttext` | Evaluate FastText classifier |
| `infer-fasttext` | Run FastText inference on JSONL files |
| `eval-calibration` | Evaluate predictions against ordinal labels (AUC, correlation, calibration) |
| `train-calibration` | Train calibration model mapping prediction components to gold labels |

### Annotation Commands (Requires `annotate` extra)

| Command | Description |
|---------|-------------|
| `annotate-dataset` | Annotate dataset using LLM APIs |
| `batch-annotate-submit` | Submit batch annotation job to LLM batch API |
| `batch-annotate-retrieve` | Retrieve batch annotation results and merge with original data |
| `list-prompts` | List available annotation prompts |
| `annotation-agreement` | Compare annotations between two datasets and compute agreement metrics |
| `label-distribution` | Show label distribution in a dataset |

### Utility Commands

| Command | Description |
|---------|-------------|
| `version` | Print package version |

[1]: https://github.com/MinishLab/model2vec
[2]: https://fasttext.cc
