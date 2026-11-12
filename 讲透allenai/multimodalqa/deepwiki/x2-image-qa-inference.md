<!-- source: DeepWiki mcp.deepwiki.com · repo allenai/multimodalqa · extra page Image QA Inference · fetched 2026-10-26 -->

# Image QA Inference

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [baselines/image_qa/inference.py](baselines/image_qa/inference.py)

</details>



## Purpose and Scope

This document describes the inference system for the VilBERT-based Image QA model, focusing on how predictions are generated at test time. The inference system loads trained model checkpoints, processes questions and images, and produces answers using different strategies based on question type and inference mode.

For information about training the Image QA model, see [Image QA Training](#5.1.3). For details about the underlying model architecture, see [Image QA Model Architecture](#5.1.2). For dataset preparation and feature extraction, see [Image QA Dataset Preparation](#5.1.1).

**Sources:** [baselines/image_qa/inference.py:1-253]()

---

## Inference Architecture Overview

The image QA inference system is implemented in the `InferenceModel` class, which orchestrates model loading, feature extraction, prediction, and answer selection. The system supports three inference modes (`implicit_decomp`, `auto_routing`, `context_only`) and handles both single-hop and multi-hop questions with bridge entities.

```mermaid
graph TB
    subgraph "Initialization"
        INIT["InferenceModel.__init__"]
        INIT --> LOAD_TOK["Load BertTokenizer<br/>bert-base-uncased"]
        INIT --> LOAD_VOCAB["Load Vocabulary<br/>idx2answer, answer2idx"]
        INIT --> LOAD_MODEL["Load VilbertForMQA<br/>from checkpoint"]
        INIT --> LOAD_DOCS["Load Image Metadata<br/>MMQA_images.jsonl"]
        INIT --> FEAT_EXT["FeatureExtractor or<br/>img_features_dir"]
    end
    
    subgraph "Prediction Flow"
        PRED["predict()"]
        PRED --> PREP["Prepare raw_inputs<br/>questions, img_ids, img_names"]
        PREP --> CHECK_BRIDGE{"Multi-hop with<br/>bridge entities?"}
        CHECK_BRIDGE -->|Yes| FILTER["Filter images by<br/>bridge_entities"]
        CHECK_BRIDGE -->|No| LOAD_FEAT["Load/Extract Features"]
        FILTER --> LOAD_FEAT
        LOAD_FEAT --> GET_ANS["get_answers()"]
    end
    
    subgraph "Answer Computation"
        GET_ANS --> PROCESS["process_raw_inputs<br/>tokenize & prepare"]
        PROCESS --> COLLATE["collate()<br/>batch data"]
        COLLATE --> FORWARD["model.forward()<br/>get logits"]
        FORWARD --> STRATEGY{"Question Type<br/>Strategy"}
        STRATEGY -->|QUESTIONS_WITH_VOCAB_ANSWERS| VOCAB_ANS["Select min DISTRACTOR_TOK<br/>then max other vocab"]
        STRATEGY -->|SINGLE_CORRECT_ANS| SINGLE_ANS["Select max IS_ANSWER_TOK"]
        STRATEGY -->|Multiple Entities| MULTI_ANS["Select IS_ANSWER_TOK > IS_NOT_ANSWER_TOK"]
        VOCAB_ANS --> RETURN["Return predicted_answers"]
        SINGLE_ANS --> RETURN
        MULTI_ANS --> RETURN
    end
    
    LOAD_MODEL --> PRED
    LOAD_VOCAB --> PRED
    LOAD_DOCS --> PRED
    FEAT_EXT --> PRED
```

**Diagram: End-to-End Inference Pipeline from Initialization to Answer Selection**

**Sources:** [baselines/image_qa/inference.py:161-233](), [baselines/image_qa/inference.py:37-159]()

---

## InferenceModel Class

The `InferenceModel` class encapsulates all components required for inference, including model weights, tokenizer, vocabulary, and feature extraction.

### Initialization Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `checkpoint_path` | str | Path to trained model checkpoint (`.pt` file) |
| `vilbert_dir` | str | Directory containing VilBERT pre-trained weights |
| `img_info_path` | str | Path to `MMQA_images.jsonl` containing image metadata |
| `vocab_path` | str | Path to pickled vocabulary (`vocab.pickle`) |
| `device` | str | PyTorch device (e.g., `'cuda:0'`, `'cpu'`) |
| `mode` | str | Inference mode: `'auto_routing'`, `'implicit_decomp'`, or `'context_only'` |
| `img_features_dir` | str (optional) | Directory with pre-extracted image features |
| `use_distractors` | bool | Whether to use distractor images during inference |

### Initialization Process

The initialization process [baselines/image_qa/inference.py:162-195]() performs the following steps:

1. **Tokenizer Setup**: Loads `bert-base-uncased` tokenizer and sets pad token ID
2. **Image Metadata Loading**: Reads `MMQA_images.jsonl` into a dictionary keyed by image ID
3. **Vocabulary Loading**: Unpickles `idx2answer` and `answer2idx` mappings
4. **Model Instantiation**: Creates `VilbertForMQA` with pre-trained VilBERT weights
5. **Checkpoint Loading**: Loads fine-tuned weights from checkpoint if provided
6. **Model Preparation**: Sets model to evaluation mode and moves to device
7. **Feature Extractor**: Initializes either `FeatureExtractor` (for on-the-fly extraction) or uses pre-computed features directory

```mermaid
graph LR
    subgraph "InferenceModel Components"
        MODEL["self.model<br/>VilbertForMQA"]
        TOK["self.tokenizer<br/>BertTokenizer"]
        VOCAB["self.idx2answer<br/>self.answer2idx"]
        DOCS["self.img_docs<br/>dict[id → metadata]"]
        FEAT["self.feature_extractor<br/>or img_features_dir"]
        MODE["self.mode<br/>inference strategy"]
        DEV["self.device<br/>cuda or cpu"]
    end
    
    MODEL --> PRED_METHOD["predict()"]
    TOK --> PRED_METHOD
    VOCAB --> PRED_METHOD
    DOCS --> PRED_METHOD
    FEAT --> PRED_METHOD
    MODE --> PRED_METHOD
    DEV --> PRED_METHOD
```

**Diagram: InferenceModel Class Attributes and Dependencies**

**Sources:** [baselines/image_qa/inference.py:161-195]()

---

## Prediction Workflow

The `predict` method [baselines/image_qa/inference.py:197-232]() is the main entry point for generating predictions on a single question.

### Method Signature

```python
def predict(self, question, img_ids_or_paths, question_type, bridge_entities=None)
```

### Parameters

- **`question`** (str): The question text
- **`img_ids_or_paths`** (list): List of image IDs (strings) or file paths
- **`question_type`** (str): One of the 16 question types (e.g., `'ImageQ'`, `'Compose(ImageQ,TextQ)'`)
- **`bridge_entities`** (list, optional): List of bridge entity names for multi-hop questions

### Input Processing

```mermaid
graph TD
    START["predict() called"]
    START --> CHECK_HOP{"question_type in<br/>IMAGE_AS_SECOND_HOP_QUESTION_TYPES<br/>and mode not auto_routing/context_only?"}
    CHECK_HOP -->|Yes| ASSERT_BRIDGE["Assert bridge_entities provided<br/>Must be list"]
    CHECK_HOP -->|No| BUILD_INPUTS["Build raw_inputs dict"]
    ASSERT_BRIDGE --> BUILD_INPUTS
    
    BUILD_INPUTS --> INIT_DICT["Initialize raw_inputs:<br/>question_id, question_type, question<br/>img_ids, img_names, img_features lists"]
    INIT_DICT --> LOOP["For each img_id_or_path"]
    
    LOOP --> CHECK_EXTRACTOR{"self.feature_extractor<br/>is not None?"}
    CHECK_EXTRACTOR -->|Yes| EXTRACT["Extract features on-the-fly<br/>img_path → img_features"]
    CHECK_EXTRACTOR -->|No| LOAD_PICKLE["Load pre-computed features<br/>img_features_dir/img_id.pickle"]
    
    EXTRACT --> GET_NAME1["Get img_name from path"]
    LOAD_PICKLE --> GET_NAME2["Get img_name from img_docs"]
    
    GET_NAME1 --> APPEND["Append to raw_inputs"]
    GET_NAME2 --> APPEND
    APPEND --> LOOP
    
    LOOP --> CALL_GET_ANS["Call get_answers()<br/>Returns predicted_answers"]
    CALL_GET_ANS --> RETURN["Return predicted_answers"]
```

**Diagram: predict() Method Workflow**

The method constructs a `raw_inputs` dictionary containing:
- `question_id`: Empty string (not used in inference)
- `question_type`: The provided question type
- `question`: The question text
- `img_ids`: List of image IDs
- `img_names`: List of human-readable image names (titles)
- `img_features`: List of extracted feature dictionaries

**Sources:** [baselines/image_qa/inference.py:197-232]()

---

## Answer Computation Strategies

The `get_answers` function [baselines/image_qa/inference.py:37-159]() implements different answer selection strategies based on question type. It processes the raw inputs, runs forward pass, and applies type-specific logic to extract answers from model logits.

### Pre-processing: Filtering by Bridge Entities and Distractors

Before computing predictions, the function filters images based on the inference mode and question type:

```mermaid
graph TD
    START["get_answers() called"]
    START --> CLEAN_BRIDGE{"bridge_entities<br/>provided?"}
    CLEAN_BRIDGE -->|Yes| LEV["Use levenshtein_distance<br/>to match bridge entities<br/>to img_names"]
    CLEAN_BRIDGE -->|No| CHECK_DIST
    LEV --> CHECK_DIST["Check use_distractors flag"]
    
    CHECK_DIST --> DIST_LOGIC{"use_distractors?"}
    DIST_LOGIC -->|No| FILTER_DIST["Filter bad_indexes:<br/>Remove DISTRACTOR_TOK images<br/>Or images not in question"]
    DIST_LOGIC -->|Yes| CHECK_MODE{"mode in implicit_decomp<br/>and question in<br/>IMAGE_AS_SECOND_HOP?"}
    
    FILTER_DIST --> BUILD_RAW
    CHECK_MODE -->|Yes| FILTER_BRIDGE["Filter bad_indexes:<br/>Keep only bridge_entities"]
    CHECK_MODE -->|No| BUILD_RAW["Build raw_inputs list"]
    FILTER_BRIDGE --> BUILD_RAW
    
    BUILD_RAW --> PROCESS["process_raw_inputs()<br/>for each raw_input"]
    PROCESS --> COLLATE["collate() into batched_data"]
    COLLATE --> FORWARD["model.forward()<br/>get logits"]
```

**Diagram: Pre-processing and Filtering Logic**

**Sources:** [baselines/image_qa/inference.py:40-94]()

### Strategy 1: Vocabulary-Based Answers

For questions in `QUESTIONS_WITH_VOCAB_ANSWERS` [baselines/image_qa/inference.py:127-138]():

1. Compute probability of `DISTRACTOR_TOK` for each image
2. Select image with minimum `DISTRACTOR_TOK` probability
3. For that image's logits, suppress `DISTRACTOR_TOK`, `IS_ANSWER_TOK`, `IS_NOT_ANSWER_TOK`
4. Return vocabulary item with highest remaining logit

**Example Question Types**: Questions where the answer is a specific term from the vocabulary (e.g., colors, shapes)

### Strategy 2: Single Correct Image

For questions in `QUESTION_TYPES_WITH_SINGLE_CORRECT_ANS` [baselines/image_qa/inference.py:139-144]():

1. Compute probability of `IS_ANSWER_TOK` for each image
2. Return the image name with highest `IS_ANSWER_TOK` probability

**Example Question Types**: `ImageQ`, where exactly one image is correct

### Strategy 3: Multiple Entity Answers

For all other question types [baselines/image_qa/inference.py:145-154]():

1. For each image, compare `IS_ANSWER_TOK` vs `IS_NOT_ANSWER_TOK` logits
2. Return all image names where `IS_ANSWER_TOK` > `IS_NOT_ANSWER_TOK`

**Example Question Types**: `ImageListQ`, `Intersect(ImageListQ,TextQ)`, where multiple images can be correct

### Answer Strategy Comparison

| Strategy | Question Types | Selection Logic | Return Type |
|----------|---------------|-----------------|-------------|
| Vocabulary | `QUESTIONS_WITH_VOCAB_ANSWERS` | Min `DISTRACTOR_TOK`, then max vocab logit | Single vocabulary term |
| Single Image | `QUESTION_TYPES_WITH_SINGLE_CORRECT_ANS` | Max `IS_ANSWER_TOK` probability | Single image name |
| Multiple Entities | All others | `IS_ANSWER_TOK` > `IS_NOT_ANSWER_TOK` | List of image names |

**Sources:** [baselines/image_qa/inference.py:127-154]()

---

## Multi-Hop Reasoning with Bridge Entities

Multi-hop questions in the `IMAGE_AS_SECOND_HOP_QUESTION_TYPES` category require bridge entities from the first hop to guide the second hop prediction.

### Bridge Entity Matching

When bridge entities are provided [baselines/image_qa/inference.py:40-44](), the system:

1. Uses Levenshtein distance to fuzzy-match bridge entity strings to image names
2. Selects the closest matching image name for each bridge entity
3. Creates a deduplicated set of matched image names

```mermaid
graph LR
    BRIDGE_IN["bridge_entities<br/>['Entity A', 'Entity B']"]
    IMG_NAMES["raw_data['img_names']<br/>['Image_A', 'Image_B', ...]"]
    
    BRIDGE_IN --> LEV_FUNC["get_closest()<br/>uses levenshtein_distance"]
    IMG_NAMES --> LEV_FUNC
    
    LEV_FUNC --> MATCHED["clean_bridge_entities<br/>{'Image_A', 'Image_B'}"]
    MATCHED --> FILTER["Filter raw_inputs<br/>to only matched images"]
    FILTER --> INFERENCE["Run inference on<br/>filtered images"]
```

**Diagram: Bridge Entity Fuzzy Matching Process**

### Multi-Hop Filtering Logic

For multi-hop questions in `implicit_decomp` mode [baselines/image_qa/inference.py:59-62]():

```
if question_type in IMAGE_AS_SECOND_HOP_QUESTION_TYPES and mode not in ['auto_routing', 'context_only']:
    assert bridge_entities is not None
    assert isinstance(bridge_entities, list)
    bad_indexes = [idx for idx, img_name in enumerate(raw_data['img_names']) if img_name not in bridge_entities]
```

This filters the candidate images to only those that match the bridge entities from the first hop, ensuring the second hop focuses on the correct context.

**Sources:** [baselines/image_qa/inference.py:20-36](), [baselines/image_qa/inference.py:40-62](), [baselines/image_qa/inference.py:198-201]()

---

## Usage Example

The script includes a self-contained example demonstrating typical usage [baselines/image_qa/inference.py:235-252]():

```python
mode = 'implicit_decomp'
checkpoint_filename = 'checkpoints/my_model.pt'
vocab_filename = '../../dataset/cache/vocab.pickle'
vilbert_dir = "../../deps/vilbert-multi-task"
img_info_path = '../../dataset/MMQA_images.jsonl'
img_features_dir = '../../dataset/img_features'
device = 'cuda:1'

question = "What shape is in the center of Viduthalal Chiruthaigal Katchi?"
question_type = "ImageQ"
img_ids_or_paths = ['e7a17bf9eb43fbe95843f682a03b0eb3']

inference_model = InferenceModel(
    checkpoint_filename, vilbert_dir, img_info_path, 
    vocab_filename, device, mode, img_features_dir)
    
pred = inference_model.predict(question, img_ids_or_paths, question_type)
```

### Integration with Pipeline

The `InferenceModel` is typically instantiated by the main pipeline orchestrator (see [Pipeline Implementation](#6.1)) which:

1. Loads the appropriate checkpoint based on inference mode
2. Processes questions from the dataset
3. Routes questions to the image QA model based on question type classification
4. Handles multi-hop decomposition and bridge entity passing
5. Collects predictions for evaluation

**Sources:** [baselines/image_qa/inference.py:235-252]()

---

## Key Design Decisions

### Separation of Feature Extraction

The inference model supports two modes for image features:
- **Pre-computed features** (`img_features_dir`): Fast, used in production pipeline
- **On-the-fly extraction** (`FeatureExtractor`): Flexible for new images, but slower

This design allows batch processing with cached features while maintaining flexibility for interactive use.

### Mode-Specific Logic

The `mode` parameter affects:
- Whether bridge entities are required for multi-hop questions
- Which images are included in the candidate set
- How the model processes questions (with/without decomposition)

This enables systematic comparison of different reasoning strategies using the same underlying model.

### Answer Type Handling

The three answer selection strategies correspond to different semantic question types:
- **Vocabulary answers**: Classifying image properties (colors, shapes, etc.)
- **Single entity**: Selecting the correct image from candidates
- **Multiple entities**: Finding all matching images (intersection, list operations)

This type-aware prediction logic ensures the model output format matches the expected answer format.

**Sources:** [baselines/image_qa/inference.py:1-253]()

---

