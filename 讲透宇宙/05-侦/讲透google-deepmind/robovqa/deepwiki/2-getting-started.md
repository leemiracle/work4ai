<!-- source: DeepWiki mcp.deepwiki.com · repo google-deepmind/robovqa · page 2 Getting Started · fetched 2026-10-26 -->

# Getting Started

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [data_loading_and_eval.ipynb](data_loading_and_eval.ipynb)

</details>



This document provides step-by-step instructions for using the RoboVQA repository to interact with the RoboVQA dataset. This repository contains example code for loading, visualizing, and evaluating against the dataset, not the full RoboVQA model implementation.

For comprehensive details about the dataset format and processing pipeline, see [Core Implementation](#3). For information about contributing to the project, see [Development Guide](#4).

## Purpose and Scope

The RoboVQA repository serves as a demonstration interface for the RoboVQA dataset, which contains multimodal long-horizon reasoning data for robotics applications. The primary workflow involves:

1. Accessing the pre-configured Google Colab environment
2. Loading TFRecord data from Google Cloud Storage
3. Visualizing image sequences and text content
4. Running evaluation pipelines with BLEU score metrics

## Prerequisites

| Requirement | Description |
|-------------|-------------|
| Google Account | Required for Google Colab access |
| Internet Connection | Needed to access Google Cloud Storage dataset |
| Browser | Chrome, Firefox, or Safari for Colab compatibility |

No local installation or setup is required - the entire workflow runs in Google Colab.

## Quick Start Workflow

### Repository Entry Point

The primary entry point is through the repository's main documentation:

```mermaid
graph TD
    A[README.md] --> B["Open In Colab Badge"]
    B --> C[data_loading_and_eval.ipynb]
    C --> D["Google Colab Environment"]
    D --> E["Interactive Dataset Exploration"]
    
    A --> F["Project Links"]
    F --> G["robovqa.github.io"]
    F --> H["arXiv:2311.00899"]
```

**User Journey**: Navigate to repository → Click "Open In Colab" badge → Execute notebook cells sequentially

Sources: [README.md:1-46](), [data_loading_and_eval.ipynb:1-541]()

### Core Execution Flow

The main workflow executes through the Jupyter notebook with these key steps:

```mermaid
graph TD
    A[data_loading_and_eval.ipynb] --> B["Cell 1: Display Utils"]
    B --> C["Cell 2: Task Utils"]
    C --> D["Cell 3: Dataset Loading"]
    D --> E["Cell 4: TF Dataset Creation"]
    E --> F["Cell 5: Example Visualization"]
    F --> G["Cell 6: Evaluation Setup"]
    G --> H["Cell 7: BLEU Score Evaluation"]
    
    B --> B1["display_image()"]
    B --> B2["as_gif()"]
    
    C --> C1["Task class"]
    C --> C2["Tasks class"]
    C --> C3["fetch_question_answer()"]
    
    D --> D1["tf.io.gfile.glob()"]
    D --> D2["gs://anon_robovqa/tfrecord/train/train*"]
    
    E --> E1["tf.data.TFRecordDataset"]
    E --> E2["tf.train.SequenceExample"]
    
    G --> G1["mock_call_model()"]
    G --> G2["run_eval()"]
    G --> G3["sacrebleu.sentence_bleu()"]
```

**Execution Method**: Run cells sequentially from top to bottom in the Colab environment

Sources: [data_loading_and_eval.ipynb:58-541]()

## Data Loading Pipeline

### Google Cloud Storage Access

The dataset is stored in Google Cloud Storage and accessed through TensorFlow's file system utilities:

```mermaid
graph LR
    A["tf.io.gfile.glob"] --> B["gs://anon_robovqa/tfrecord/train/train*"]
    B --> C["tf.data.TFRecordDataset"]
    C --> D["dataset.as_numpy_iterator()"]
    D --> E["tf.train.SequenceExample"]
    E --> F["example.ParseFromString()"]
    
    F --> G["Feature Lists"]
    G --> H["images"]
    G --> I["texts"]
    
    H --> J["tf.image.decode_jpeg()"]
    I --> K["decode('utf-8')"]
```

**Data Access Pattern**: Glob pattern → TFRecord dataset → Numpy iterator → Protocol buffer parsing

Sources: [data_loading_and_eval.ipynb:385-427]()

### Text Processing Architecture

The text processing system handles conversational dialogue with specialized tagging:

```mermaid
graph TD
    A["Raw Text Content"] --> B["Tasks()"]
    B --> C["Tasks.text_to_dict()"]
    C --> D["Task()"]
    D --> E["Task.get_splits()"]
    
    E --> F["PRED_STARTS"]
    E --> G["NOPRED_STARTS"]
    E --> H["PRED_START/PRED_END"]
    E --> I["PRED_ANSWER_BINARY_START/END"]
    
    F --> F1["'Robot:', 'Thought:', 'Action:'"]
    G --> G1["'User:', 'System:'"]
    H --> H1["'<PRED>', '</PRED>'"]
    I --> I1["'<PRED:ANSWER:BINARY>', '</PRED:ANSWER:BINARY>'"]
    
    D --> J["fetch_question_answer()"]
    J --> K["Question-Answer Pairs"]
```

**Processing Flow**: Raw text → Tasks container → Individual Task objects → Tag-based splitting → Q/A extraction

Sources: [data_loading_and_eval.ipynb:99-374]()

## Visualization and Display

### Image Sequence Handling

The system provides utilities for displaying both single images and image sequences:

| Function | Purpose | Input | Output |
|----------|---------|--------|--------|
| `display_image()` | Main display function | List of numpy arrays | GIF animation or static image |
| `as_gif()` | GIF creation | List of PIL Images | GIF bytes |

```mermaid
graph LR
    A["JPEG Bytes"] --> B["tf.image.decode_jpeg()"]
    B --> C["Numpy Arrays"]
    C --> D["display_image()"]
    
    D --> E{"len(images) > 1?"}
    E -->|Yes| F["as_gif()"]
    E -->|No| G["plt.imshow()"]
    
    F --> H["PIL.Image.fromarray()"]
    H --> I["save as GIF"]
    I --> J["display.Image()"]
    
    G --> K["plt.show()"]
```

**Display Logic**: Multiple images → GIF animation, Single image → Static matplotlib display

Sources: [data_loading_and_eval.ipynb:66-87]()

### Text Output Formatting

The `display_text()` function processes conversational text and extracts structured question-answer pairs:

```mermaid
graph TD
    A["display_text()"] --> B["fetch_question_answer()"]
    B --> C["Tasks(text)"]
    C --> D["tasks.tasks_dict.items()"]
    D --> E["Task(task)"]
    E --> F["t.get_splits('A:')"]
    F --> G["(question, answer) pairs"]
    G --> H["print formatted output"]
    
    H --> I["'Task %d (type: %s): %s %s'"]
```

**Output Format**: `Task {index} (type: {task_type}): {question} {answer}`

Sources: [data_loading_and_eval.ipynb:356-374]()

## Evaluation Pipeline

### Mock Model Interface

The evaluation system provides a template for model integration:

```mermaid
graph TD
    A["mock_call_model()"] --> B["Input: images, question"]
    B --> C["Return: 'This is a mock answer!'"]
    
    D["run_eval()"] --> E["get_eval_example()"]
    E --> F["Load validation TFRecords"]
    F --> G["gs://anon_robovqa/tfrecord/val/val*"]
    
    D --> H["fetch_question_answer()"]
    H --> I["Extract Q/A pairs"]
    I --> J["call_model(images, question)"]
    J --> K["sacrebleu.sentence_bleu()"]
    K --> L["BLEU score output"]
```

**Evaluation Flow**: Load validation data → Extract Q/A pairs → Call model → Calculate BLEU scores

Sources: [data_loading_and_eval.ipynb:462-503]()

### BLEU Score Calculation

The system uses the `sacrebleu` library for evaluation metrics:

| Component | Purpose | Input | Output |
|-----------|---------|--------|--------|
| `sacrebleu.sentence_bleu()` | BLEU score calculation | Reference answer, predicted answer | BLEU score percentage |
| `run_eval()` | End-to-end evaluation | Model function | Formatted evaluation results |

**Integration Point**: Replace `mock_call_model()` with your actual model implementation

Sources: [data_loading_and_eval.ipynb:448-503]()

## Next Steps

1. **Dataset Exploration**: Execute all cells in the notebook to see example data
2. **Model Integration**: Replace `mock_call_model()` with your model implementation
3. **Custom Evaluation**: Modify the evaluation pipeline for your specific use case
4. **Data Processing**: Adapt the `Task` and `Tasks` classes for custom text processing needs

For detailed implementation information, see [Core Implementation](#3). For contribution guidelines, see [Development Guide](#4).

Sources: [README.md:1-46](), [data_loading_and_eval.ipynb:1-541]()

---

