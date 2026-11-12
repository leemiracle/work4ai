<!-- source: DeepWiki mcp.deepwiki.com · repo google-deepmind/ithaca · page 5 Inference System · fetched 2026-10-26 -->

# Inference System

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [colabs/ithaca_inference.ipynb](colabs/ithaca_inference.ipynb)
- [inference_example.py](inference_example.py)
- [ithaca/eval/inference.py](ithaca/eval/inference.py)

</details>



This document describes the Ithaca inference system, which uses trained models to perform two tasks on ancient Greek inscriptions: **attribution** (predicting date and geographical origin) and **restoration** (filling in missing characters). The inference system is designed to be lightweight and deployable without training infrastructure dependencies.

For information about training models, see [Training System](#4). For details about the model architecture, see [Model Architecture](#3).

## Overview

The inference system provides a clean separation between model deployment and training. It operates on pre-trained model checkpoints and exposes functionality through three interfaces:

**Sources:** [ithaca/eval/inference.py:1-269](), [inference_example.py:1-130](), [colabs/ithaca_inference.ipynb:1-100]()

### System Architecture

```mermaid
graph TB
    subgraph "Checkpoint Storage"
        PKL["checkpoint.pkl<br/>Serialized Model State"]
    end
    
    subgraph "Core Inference Module"
        PREP["_prepare_text()<br/>Text preprocessing"]
        ATTR["attribute()<br/>Date & region prediction"]
        REST["restore()<br/>Character restoration"]
        LOAD["load_checkpoint()<br/>Deserialize model"]
    end
    
    subgraph "Supporting Utilities"
        EVAL["ithaca.util.eval<br/>beam_search, saliency maps"]
        TEXT["ithaca.util.text<br/>text_to_idx, strip_accents"]
        ALPHA["GreekAlphabet<br/>Vocabulary mappings"]
    end
    
    subgraph "User Interfaces"
        CLI["inference_example.py<br/>Command-line tool"]
        COLAB["ithaca_inference.ipynb<br/>Interactive notebook"]
        API["Direct API<br/>Python imports"]
    end
    
    subgraph "Output Structures"
        ATTR_RES["AttributionResults<br/>locations, year_scores, saliency"]
        REST_RES["RestorationResults<br/>predictions, saliency"]
    end
    
    PKL --> LOAD
    LOAD --> ATTR
    LOAD --> REST
    
    PREP --> ATTR
    PREP --> REST
    
    EVAL --> ATTR
    EVAL --> REST
    TEXT --> PREP
    ALPHA --> PREP
    
    CLI --> ATTR
    CLI --> REST
    COLAB --> ATTR
    COLAB --> REST
    API --> ATTR
    API --> REST
    
    ATTR --> ATTR_RES
    REST --> REST_RES
```

**Sources:** [ithaca/eval/inference.py:14-21](), [inference_example.py:40-74]()

## Core Components

### Entry Points

The inference module provides two main functions in `ithaca.eval.inference`:

| Function | Purpose | Input | Output |
|----------|---------|-------|--------|
| `attribute()` | Predict date and geographical origin | Text string | `AttributionResults` |
| `restore()` | Fill missing characters (marked with `?`) | Text with `?` placeholders | `RestorationResults` |

Both functions require a `forward` callable, which is the model's apply function bound to trained parameters.

**Sources:** [ithaca/eval/inference.py:186-224](), [ithaca/eval/inference.py:226-268]()

### Key Constants

[ithaca/eval/inference.py:130-140]() defines critical inference parameters:

| Constant | Value | Purpose |
|----------|-------|---------|
| `MIN_TEXT_LEN` | 50 | Minimum input text length |
| `TEXT_LEN` | 768 | Fixed model sequence length |
| `DATE_MIN` | -800 | Earliest year (800 BCE) |
| `DATE_MAX` | 800 | Latest year (800 CE) |
| `DATE_INTERVAL` | 10 | Date binning interval (decades) |
| `RESTORATION_BEAM_WIDTH` | 20 | Number of beam search candidates |
| `ALPHABET_MISSING_RESTORE` | `'?'` | Character marking restoration target |

**Sources:** [ithaca/eval/inference.py:130-140]()

### Data Structures

```mermaid
graph TB
    subgraph "Attribution Output"
        ATTR_RES["AttributionResults<br/>(NamedTuple)"]
        ATTR_RES --> INPUT_TEXT["input_text: str"]
        ATTR_RES --> LOCATIONS["locations: List[LocationPrediction]"]
        ATTR_RES --> YEAR_SCORES["year_scores: List[float]<br/>160 decade probabilities"]
        ATTR_RES --> DATE_SAL["date_saliency: List[float]<br/>Per-character importance"]
        ATTR_RES --> LOC_SAL["location_saliency: List[float]<br/>Per-character importance"]
        
        LOCATIONS --> LOC_PRED["LocationPrediction<br/>location_id: int<br/>score: float"]
    end
    
    subgraph "Restoration Output"
        REST_RES["RestorationResults<br/>(NamedTuple)"]
        REST_RES --> INPUT_TEXT2["input_text: str"]
        REST_RES --> TOP_PRED["top_prediction: str"]
        REST_RES --> RESTORED["restored: List[int]<br/>Restored char indices"]
        REST_RES --> PREDS["predictions: List[Restoration]<br/>Top 20 beam search results"]
        REST_RES --> PRED_SAL["prediction_saliency:<br/>List[RestorationCharSaliency]"]
        
        PREDS --> RESTORATION["Restoration<br/>text: str<br/>score: float"]
        PRED_SAL --> CHAR_SAL["RestorationCharSaliency<br/>text: str<br/>restored_idx: int<br/>saliency: List[float]"]
    end
```

**Sources:** [ithaca/eval/inference.py:35-128]()

## Text Preprocessing

The `_prepare_text()` function [ithaca/eval/inference.py:142-183]() performs critical input preparation:

### Preprocessing Pipeline

```mermaid
graph LR
    INPUT["Raw Input Text"] --> STRIP["Strip whitespace<br/>re.sub(r'\s+', ' ')"]
    STRIP --> ACCENTS["Remove accents<br/>strip_accents()"]
    ACCENTS --> VALIDATE["Validate length<br/>50 ≤ len < 767"]
    VALIDATE --> SOS["Add SOS token<br/>alphabet.sos + text"]
    SOS --> REPLACE["Replace '?' with<br/>alphabet.missing"]
    REPLACE --> PAD["Pad to 768<br/>+ alphabet.pad"]
    PAD --> INDICES["Convert to indices<br/>text_to_idx()<br/>text_to_word_idx()"]
    INDICES --> OUTPUT["Model-ready arrays"]
```

The function returns an 8-tuple:
1. `text` - Cleaned text (no SOS/padding)
2. `text_sos` - With start-of-sequence token
3. `text_padded` - Padded to `TEXT_LEN`
4. `text_char` - Character indices (shape: 1 × 768)
5. `text_word` - Word indices (shape: 1 × 768)
6. `text_len` - Actual text length (list of 1 element)
7. `padding` - Binary mask (1 for real tokens, 0 for padding)
8. `restore_mask_idx` - Indices of `?` characters to restore

**Sources:** [ithaca/eval/inference.py:142-183](), [ithaca/util/text.py]()

## Checkpoint Loading

The `load_checkpoint()` function in [inference_example.py:40-73]() demonstrates how to deserialize a trained model:

```mermaid
graph TB
    PICKLE["checkpoint.pkl<br/>Pickled dict"] --> LOAD["pickle.load()"]
    
    LOAD --> PARAMS["checkpoint['params']<br/>JAX arrays"]
    LOAD --> MODEL_CFG["checkpoint['model_config']<br/>Model constructor args"]
    LOAD --> REGION["checkpoint['region_map']<br/>ID ↔ name mappings"]
    LOAD --> VOCAB["checkpoint['alphabet']<br/>idx2word, word2idx"]
    
    PARAMS --> JAX_PUT["jax.device_put()<br/>Move to accelerator"]
    MODEL_CFG --> CONSTRUCT["Model(**model_config)<br/>Reconstruct architecture"]
    
    JAX_PUT --> FORWARD["functools.partial(<br/>model.apply, params)<br/>Create forward function"]
    CONSTRUCT --> FORWARD
    
    VOCAB --> ALPHA["GreekAlphabet()<br/>Populate vocabularies"]
    
    FORWARD --> OUTPUT["Ready for inference"]
    REGION --> OUTPUT
    ALPHA --> OUTPUT
```

The checkpoint contains:
- `params`: Trained model parameters (JAX pytrees)
- `model_config`: Dictionary of model hyperparameters
- `alphabet`: Vocabulary mappings (`idx2word`, `word2idx`)
- `region_map`: Geographical region metadata

**Sources:** [inference_example.py:40-73]()

## Attribution

The `attribute()` function [ithaca/eval/inference.py:186-224]() predicts when and where an inscription was written.

### Attribution Flow

```mermaid
graph TB
    INPUT["Input text string"] --> PREP["_prepare_text()<br/>Clean & tokenize"]
    PREP --> RNG["jax.random.PRNGKey(SEED)<br/>Fixed random seed"]
    
    RNG --> FORWARD["forward(<br/>text_char, text_word,<br/>is_training=False)"]
    PREP --> FORWARD
    
    FORWARD --> DATE_LOG["date_logits<br/>Raw date predictions"]
    FORWARD --> REGION_LOG["subregion_logits<br/>Raw region predictions"]
    
    DATE_LOG --> DATE_SOFT["softmax(date_logits)<br/>160 decade probabilities"]
    REGION_LOG --> REGION_SOFT["softmax(subregion_logits)<br/>84 region probabilities"]
    
    REGION_SOFT --> LOC_LIST["Sort by score<br/>List[LocationPrediction]"]
    
    FORWARD --> SALIENCY["compute_attribution_saliency_maps()<br/>Gradient-based importance"]
    
    DATE_SOFT --> RESULT["AttributionResults"]
    LOC_LIST --> RESULT
    SALIENCY --> RESULT
```

### Date Predictions

The model outputs 160 values representing probability distribution over decades from 800 BCE to 800 CE:

- Index 0: 800-790 BCE
- Index 1: 790-780 BCE
- ...
- Index 159: 790-800 CE

The `year_scores` field contains these probabilities after softmax normalization.

### Region Predictions

The model classifies among 84 ancient world subregions. The `locations` field contains `LocationPrediction` objects sorted by decreasing probability:

```python
LocationPrediction(location_id=42, score=0.723)  # Highest probability
LocationPrediction(location_id=15, score=0.134)  # Second highest
...
```

Region IDs map to names via `region_map['sub']['ids_inv']` and `region_map['sub']['names_inv']`.

**Sources:** [ithaca/eval/inference.py:186-224](), [colabs/ithaca_inference.ipynb:291-292]()

## Restoration

The `restore()` function [ithaca/eval/inference.py:226-268]() fills in missing characters marked with `?` in the input text.

### Restoration Flow

```mermaid
graph TB
    INPUT["Text with '?' markers"] --> VALIDATE["Check for at least<br/>one '?' character"]
    VALIDATE --> PREP["_prepare_text()<br/>Convert '?' to alphabet.missing"]
    
    PREP --> MASK["restore_mask_idx<br/>Positions to restore"]
    PREP --> TEXT_PAD["text_padded<br/>Preprocessed text"]
    
    TEXT_PAD --> BEAM["beam_search_batch_2d()<br/>Non-sequential beam search"]
    MASK --> BEAM
    
    BEAM --> CANDIDATES["20 restoration candidates<br/>with log probabilities"]
    
    CANDIDATES --> CONVERT["Convert logprob to score<br/>math.exp(logprob)"]
    CONVERT --> STRIP["Strip SOS & padding<br/>for visualization"]
    
    TEXT_PAD --> GREEDY["sequential_restoration_saliency()<br/>Greedy prediction saliency"]
    MASK --> GREEDY
    
    STRIP --> RESULT["RestorationResults"]
    GREEDY --> RESULT
```

### Non-Sequential Beam Search

The restoration uses **non-sequential beam search** [ithaca/util/eval.py]() which:

1. Starts with highest-confidence character prediction
2. Iteratively fills in remaining `?` positions by confidence
3. Maintains top-k hypotheses at each step
4. Returns 20 final candidates ranked by joint probability

This differs from left-to-right sequential generation, allowing the model to first predict characters it is most confident about.

### Restoration Output

The `predictions` field contains 20 `Restoration` objects:

```python
Restoration(text="εδοξεν τηι βουληι...", score=0.661)  # Top hypothesis
Restoration(text="εδοξεν τηι βουληι...", score=0.001)  # Alternative
...
```

Scores sum to approximately 1.0 across all candidates (normalized probabilities).

**Sources:** [ithaca/eval/inference.py:226-268](), [colabs/ithaca_inference.ipynb:425-557]()

## Saliency Maps

Both `attribute()` and `restore()` compute **saliency maps** - per-character importance scores showing which input characters most influenced each prediction.

### Attribution Saliency

[ithaca/eval/inference.py:213-215]() computes two saliency maps via `compute_attribution_saliency_maps()`:

- `date_saliency`: Which characters influenced date prediction
- `location_saliency`: Which characters influenced region prediction

Each is a list of floats (length = input text length), with values in [0, 1] representing relative importance.

### Restoration Saliency

[ithaca/eval/inference.py:255-257]() computes saliency for each restored character via `sequential_restoration_saliency()`. The `prediction_saliency` field contains one `RestorationCharSaliency` entry per restored position, showing which input characters influenced that specific character prediction.

### Visualization

The Colab notebook [colabs/ithaca_inference.ipynb:302-339]() provides visualization helpers:

```python
def generate_saliency(text, saliency, snippet=False):
    """Generates HTML with background color intensity proportional to saliency."""
    snippet_html = SALIENCY_SNIPPET_TEMPLATE.render(
        pairs=list(zip(text, saliency)))
    # Purple shading: rgba(171,71,188, score)
```

Higher saliency scores result in darker purple highlighting.

**Sources:** [ithaca/eval/inference.py:213-223](), [ithaca/eval/inference.py:255-257](), [colabs/ithaca_inference.ipynb:302-339]()

## User Interfaces

### Programmatic API

Direct Python imports for custom applications:

```python
from ithaca.eval import inference
from ithaca.models.model import Model
from ithaca.util.alphabet import GreekAlphabet

# Load checkpoint (see load_checkpoint example above)
# ...

# Attribution
attribution_results = inference.attribute(
    text=input_text,
    forward=forward,
    params=params,
    alphabet=alphabet,
    region_map=region_map,
    vocab_char_size=vocab_char_size,
    vocab_word_size=vocab_word_size
)

# Restoration
restoration_results = inference.restore(
    text=input_text,
    forward=forward,
    params=params,
    alphabet=alphabet,
    vocab_char_size=vocab_char_size,
    vocab_word_size=vocab_word_size
)
```

**Sources:** [ithaca/eval/inference.py:186-268]()

### Command-Line Interface

[inference_example.py:1-130]() provides a CLI tool:

```bash
# Direct text input
python inference_example.py \
    --input="εδοξεν τηι βουληι..." \
    --checkpoint_path=checkpoint.pkl \
    --attribute_json=attribution.json \
    --restore_json=restoration.json

# File input
python inference_example.py \
    --input_file=inscription.txt \
    --checkpoint_path=checkpoint.pkl
```

**Command-line Flags:**

| Flag | Required | Default | Description |
|------|----------|---------|-------------|
| `--input` | One of input/input_file | - | Direct text string |
| `--input_file` | One of input/input_file | - | Path to text file |
| `--checkpoint_path` | No | `checkpoint.pkl` | Checkpoint location |
| `--attribute_json` | No | - | Save attribution JSON to path |
| `--restore_json` | No | - | Save restoration JSON to path |

If JSON paths are not specified, results print to stdout.

**Sources:** [inference_example.py:28-126]()

### Interactive Notebook

[colabs/ithaca_inference.ipynb:1-1500]() provides a Google Colab notebook with:

1. **Setup cells**: Install dependencies and download checkpoint
2. **Input cell**: Text input field (50-750 characters)
3. **Restoration section**: 
   - Top-20 hypotheses table (scrollable)
   - Per-character saliency visualization
4. **Attribution section**:
   - Bar chart of top-10 regions
   - Interactive map with folium
   - Date distribution plot (800 BCE - 800 CE)
   - Date and location saliency maps

The notebook includes helper functions:

```python
def get_subregion_name(id, region_map):
    """Maps region ID to human-readable name."""
    
def bce_ad(d):
    """Formats year as '430 BCE' or '120 AD'."""
    
def generate_saliency(text, saliency, snippet=False):
    """Generates HTML saliency visualization."""
```

**Input Conventions:**
- `-` (dash): Missing characters to skip (not predicted)
- `?` (question mark): Missing characters to predict
- Text length: 50-750 characters

**Sources:** [colabs/ithaca_inference.ipynb:20-1500]()

## Interface Comparison

```mermaid
graph TB
    subgraph "Use Cases"
        UC1["Research:<br/>Interactive exploration"]
        UC2["Integration:<br/>Pipeline component"]
        UC3["Batch Processing:<br/>Many inscriptions"]
    end
    
    subgraph "Interface Options"
        COLAB["Colab Notebook<br/>ithaca_inference.ipynb"]
        API["Python API<br/>inference.attribute/restore"]
        CLI["CLI Tool<br/>inference_example.py"]
    end
    
    UC1 --> COLAB
    UC2 --> API
    UC3 --> CLI
    UC3 --> API
    
    COLAB --> VIS["Visualizations:<br/>Maps, charts, saliency"]
    API --> PROG["Programmatic:<br/>JSON output, custom pipelines"]
    CLI --> BATCH["Batch-friendly:<br/>File I/O, shell scripts"]
```

| Interface | Best For | Pros | Cons |
|-----------|----------|------|------|
| Colab Notebook | Exploratory research | Rich visualizations, interactive | Manual, one-at-a-time |
| Python API | Custom applications | Full control, embeddable | Requires Python integration |
| CLI | Batch processing | Shell scriptable, I/O redirection | Limited visualization |

**Sources:** [colabs/ithaca_inference.ipynb:104-136](), [inference_example.py:76-126](), [ithaca/eval/inference.py:14-21]()

## JSON Output Format

Both `AttributionResults` and `RestorationResults` provide `.json()` methods [ithaca/eval/inference.py:72-73](), [ithaca/eval/inference.py:126-127]() for serialization:

### Attribution JSON

```json
{
  "input_text": "εδοξεν τηι βουληι...",
  "locations": [
    {"location_id": 42, "score": 0.723},
    {"location_id": 15, "score": 0.134}
  ],
  "year_scores": [0.001, 0.002, ..., 0.018],
  "date_saliency": [0.12, 0.45, ..., 0.03],
  "location_saliency": [0.08, 0.52, ..., 0.11]
}
```

### Restoration JSON

```json
{
  "input_text": "εδοξεν τηι ?????...",
  "top_prediction": "εδοξεν τηι βουληι...",
  "restored": [11, 12, 13, 14, 15],
  "predictions": [
    {"text": "εδοξεν τηι βουληι...", "score": 0.661},
    {"text": "εδοξεν τηι βουλης...", "score": 0.001}
  ],
  "prediction_saliency": [
    {
      "text": "εδοξεν τηι β????...",
      "restored_idx": 11,
      "saliency": [0.12, 0.03, ...]
    }
  ]
}
```

**Sources:** [ithaca/eval/inference.py:63-73](), [ithaca/eval/inference.py:112-127]()

## Error Handling

The inference system validates inputs and raises clear errors:

| Condition | Exception | Message |
|-----------|-----------|---------|
| Text too short | `ValueError` | "Input text too short." (< 50 chars) |
| Text too long | `ValueError` | "Input text too long." (≥ 767 chars) |
| No `?` in restore | `ValueError` | "At least one character must be missing." |
| Missing checkpoint | `FileNotFoundError` | Standard Python file error |

**Sources:** [ithaca/eval/inference.py:162-166](), [ithaca/eval/inference.py:230-231](), [inference_example.py:88-91]()

---

