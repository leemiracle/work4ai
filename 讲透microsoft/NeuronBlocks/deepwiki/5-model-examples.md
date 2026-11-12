<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/NeuronBlocks · page 5 Model Examples · fetched 2026-10-26 -->

# Model Examples

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [block_zoo/embedding/CNNCharEmbedding.py](block_zoo/embedding/CNNCharEmbedding.py)
- [dataset/get_glove.sh](dataset/get_glove.sh)
- [dataset/get_glove_6B.sh](dataset/get_glove_6B.sh)
- [model_zoo/advanced/conf.json](model_zoo/advanced/conf.json)
- [model_zoo/nlp_tasks/slot_tagging/conf_slot_tagging.json](model_zoo/nlp_tasks/slot_tagging/conf_slot_tagging.json)
- [register_block.py](register_block.py)
- [settings.py](settings.py)
- [tools/calculate_auc.py](tools/calculate_auc.py)

</details>



This document provides practical examples of implementing different NLP tasks using the NeuronBlocks toolkit. It demonstrates how to configure and build models for various problem types including classification, sequence tagging, text matching, and advanced multi-modal scenarios.

For detailed information about the underlying components used in these examples, see [Core Architecture](#3), [Block Zoo](#3.1), and [Model Zoo](#3.2). For training and evaluation procedures, see [Training and Evaluation](#4).

## Overview of Model Categories

NeuronBlocks supports four primary problem types defined in `ProblemTypes` enum, each with specific model architectures and evaluation metrics:

```mermaid
graph TD
    subgraph "ProblemTypes Enum"
        CLASSIFICATION["ProblemTypes.classification<br/>Text Classification Tasks"]
        SEQUENCE["ProblemTypes.sequence_tagging<br/>NER, Slot Filing"]
        REGRESSION["ProblemTypes.regression<br/>Scoring Tasks"]
        MRC["ProblemTypes.mrc<br/>Reading Comprehension"]
    end
    
    subgraph "Configuration Files"
        ADV_CONF["model_zoo/advanced/conf.json<br/>Multi-modal Classification"]
        SLOT_CONF["model_zoo/nlp_tasks/slot_tagging/<br/>conf_slot_tagging.json"]
        TASK_CONFIGS["Task-specific Configurations<br/>In model_zoo directory"]
    end
    
    subgraph "Evaluation Metrics"
        CLASS_METRICS["Classification Metrics<br/>auc, accuracy, f1, macro_f1"]
        SEQ_METRICS["Sequence Metrics<br/>seq_tag_f1, seq_tag_accuracy"]
        REGR_METRICS["Regression Metrics<br/>MSE, RMSE"]
        MRC_METRICS["MRC Metrics<br/>f1, em"]
    end
    
    CLASSIFICATION --> ADV_CONF
    SEQUENCE --> SLOT_CONF
    CLASSIFICATION --> CLASS_METRICS
    SEQUENCE --> SEQ_METRICS
    REGRESSION --> REGR_METRICS
    MRC --> MRC_METRICS
    
    ADV_CONF --> TASK_CONFIGS
    SLOT_CONF --> TASK_CONFIGS
```

Sources: [settings.py:18-32](), [model_zoo/advanced/conf.json](), [model_zoo/nlp_tasks/slot_tagging/conf_slot_tagging.json]()

## Text Classification and Matching Example

The advanced configuration demonstrates a sophisticated text matching model that can be adapted for classification tasks. It showcases multiple embedding types, attention mechanisms, and layer combinations.

### Architecture Overview

```mermaid
graph TD
    subgraph "Input Processing"
        QUESTION_TEXT["question_text<br/>Input Column"]
        ANSWER_TEXT["answer_text<br/>Input Column"] 
        QUESTION_POSTAG["question_postag<br/>POS Tags"]
        ANSWER_POSTAG["answer_postag<br/>POS Tags"]
        CHAR_INPUTS["Character-level Inputs<br/>question_char, answer_char"]
    end
    
    subgraph "Embedding Layer"
        WORD_EMB["Word Embedding<br/>dim: 300, fix_weight: true"]
        POSTAG_EMB["POS Tag Embedding<br/>dim: 20"]
        CHAR_EMB["CNNCharEmbedding<br/>dim: [30,20,100]"]
    end
    
    subgraph "Question Processing Pipeline"
        Q_BILSTM["question_1: BiLSTM<br/>hidden_dim: 64"]
        Q_LAYERNORM["question_2: LayerNorm"]
        Q_LINEAR["question_3: Linear<br/>hidden_dim: 128, PReLU"]
        Q_POOL["question_4: Pooling<br/>mean pooling"]
    end
    
    subgraph "Answer Processing Pipeline"
        A_BILSTMATT["answer_1: BiLSTMAtt<br/>hidden_dim: 64"]
        A_LINEAR["answer_2: Linear<br/>hidden_dim: 128, batch_norm"]
        A_DROPOUT["answer_3: Dropout<br/>dropout: 0.5"]
        A_POOL["answer_4: Pooling<br/>Reuse question_4 layer"]
    end
    
    subgraph "Output Processing"
        COMBINATION["Combination Layer<br/>operations: origin, difference, dot_multiply"]
        OUTPUT_LINEAR["Output Linear<br/>hidden_dim: [128, 2]"]
        CROSSENTROPY["CrossEntropyLoss<br/>size_average: true"]
    end
    
    QUESTION_TEXT --> WORD_EMB
    ANSWER_TEXT --> WORD_EMB
    QUESTION_POSTAG --> POSTAG_EMB
    ANSWER_POSTAG --> POSTAG_EMB
    CHAR_INPUTS --> CHAR_EMB
    
    WORD_EMB --> Q_BILSTM
    POSTAG_EMB --> Q_BILSTM
    CHAR_EMB --> Q_BILSTM
    
    Q_BILSTM --> Q_LAYERNORM
    Q_LAYERNORM --> Q_LINEAR
    Q_LINEAR --> Q_POOL
    
    WORD_EMB --> A_BILSTMATT
    POSTAG_EMB --> A_BILSTMATT
    CHAR_EMB --> A_BILSTMATT
    
    A_BILSTMATT --> A_LINEAR
    A_LINEAR --> A_DROPOUT
    A_DROPOUT --> A_POOL
    
    Q_POOL --> COMBINATION
    A_POOL --> COMBINATION
    COMBINATION --> OUTPUT_LINEAR
    OUTPUT_LINEAR --> CROSSENTROPY
```

Sources: [model_zoo/advanced/conf.json:77-202]()

### Key Configuration Patterns

The advanced example demonstrates several important configuration patterns:

| Component | Configuration | Purpose |
|-----------|---------------|---------|
| `CNNCharEmbedding` | `dim: [30, 20, 100]`, `window_size: [3,3,5]` | Multi-scale character representation |
| `BiLSTMAtt` | `hidden_dim: 64` | Attention-enhanced recurrent processing |
| `LayerNorm` | Applied after BiLSTM | Stabilizes training |
| `Combination` | `operations: ["origin", "difference", "dot_multiply"]` | Feature interaction modeling |
| `Pooling` | `pool_type: "mean"`, `pool_axis: 1` | Sequence-to-vector conversion |

The model processes questions and answers through separate but parallel pipelines, then combines their representations using multiple operations before final classification.

Sources: [model_zoo/advanced/conf.json:78-101](), [model_zoo/advanced/conf.json:170-177]()

## Sequence Tagging Example

The slot tagging configuration demonstrates a typical sequence labeling architecture for named entity recognition using the BIOES tagging scheme.

### Sequence Tagging Architecture

```mermaid
graph TD
    subgraph "Input Configuration"
        SEQUENCE_COL["sequence<br/>file_header: 0"]
        TAG_COL["tag<br/>file_header: 1"]
        BIOES_SCHEME["tagging_scheme: BIOES<br/>TaggingSchemes enum"]
    end
    
    subgraph "Model Architecture"
        WORD_EMBEDDING["Embedding Layer<br/>word dim: 100"]
        EMB_DROPOUT["emb_dropout<br/>Dropout: 0.5"]
        BI_LSTM["sentence_BiLSTM<br/>BiLSTM hidden_dim: 100"]
        LSTM_DROPOUT["lstm_dropout<br/>Dropout: 0.5"]
        OUTPUT_LINEAR["Output Linear<br/>hidden_dim: [-1]"]
    end
    
    subgraph "Loss and Metrics"
        CE_LOSS["CrossEntropyLoss<br/>ignore_index: 0, size_average: false"]
        SEQ_METRICS["seq_tag_f1<br/>seq_tag_accuracy"]
    end
    
    subgraph "Training Configuration"
        SGD_OPT["SGD Optimizer<br/>lr: 0.015, weight_decay: 1e-8"]
        LR_DECAY["lr_decay: 0.95<br/>minimum_lr: 0.00001"]
        BATCH_CONFIG["batch_size: 10<br/>max_epoch: 2"]
    end
    
    SEQUENCE_COL --> WORD_EMBEDDING
    BIOES_SCHEME --> TAG_COL
    
    WORD_EMBEDDING --> EMB_DROPOUT
    EMB_DROPOUT --> BI_LSTM  
    BI_LSTM --> LSTM_DROPOUT
    LSTM_DROPOUT --> OUTPUT_LINEAR
    
    OUTPUT_LINEAR --> CE_LOSS
    TAG_COL --> CE_LOSS
    CE_LOSS --> SEQ_METRICS
    
    SGD_OPT --> BATCH_CONFIG
    LR_DECAY --> BATCH_CONFIG
```

Sources: [model_zoo/nlp_tasks/slot_tagging/conf_slot_tagging.json:1-119]()

### Sequence Tagging Configuration Details

The slot tagging example uses several key configuration patterns specific to sequence labeling:

```json
{
  "dataset_type": "sequence_tagging",
  "tagging_scheme": "BIOES",
  "add_start_end_for_seq": false,
  "file_header": {
    "sequence": 0,
    "tag": 1
  }
}
```

The architecture uses a straightforward BiLSTM with dropout regularization, designed for token-level classification. The `ignore_index: 0` in `CrossEntropyLoss` handles padding tokens, while `size_average: false` ensures proper loss calculation for variable-length sequences.

Sources: [model_zoo/nlp_tasks/slot_tagging/conf_slot_tagging.json:6-19](), [model_zoo/nlp_tasks/slot_tagging/conf_slot_tagging.json:106-118]()

## Character-Level Embedding Integration

The `CNNCharEmbedding` component demonstrates how to incorporate character-level information into word representations, particularly useful for handling out-of-vocabulary words and morphologically rich languages.

### CNNCharEmbedding Processing Flow

```mermaid
graph TD
    subgraph "Character Input Processing"
        CHAR_INPUT["Character Input<br/>[batch_size, seq_len, char_num_in_words]"]
        RESHAPE1["Reshape<br/>[batch_size, seq_len * char_num_in_words]"]
        CHAR_LOOKUP["char_embeddings lookup<br/>embedding_matrix_dim: 50"]
        RESHAPE2["Reshape<br/>[batch_size * seq_len, char_num_in_words, embedding_dim]"]
    end
    
    subgraph "CNN Processing"
        UNSQUEEZE["Add Channel Dimension<br/>[batch_size * seq_len, 1, char_num, embedding_dim]"]
        CONV2D_1["Conv2d Layer 1<br/>window_size[0], output_channel[0]"]
        CONV2D_2["Conv2d Layer 2<br/>window_size[1], output_channel[1]"]
        CONV2D_3["Conv2d Layer 3<br/>window_size[2], output_channel[2]"]
    end
    
    subgraph "Pooling and Output"
        MAXPOOL1["Max Pool 1D<br/>Kernel size: conv_output.size(2)"]
        CONCAT["Concatenate Outputs<br/>torch.cat(outputs, 2)"]
        FINAL_RESHAPE["Final Reshape<br/>[batch_size, seq_len, total_output_dim]"]
    end
    
    CHAR_INPUT --> RESHAPE1
    RESHAPE1 --> CHAR_LOOKUP
    CHAR_LOOKUP --> RESHAPE2
    RESHAPE2 --> UNSQUEEZE
    
    UNSQUEEZE --> CONV2D_1
    UNSQUEEZE --> CONV2D_2
    UNSQUEEZE --> CONV2D_3
    
    CONV2D_1 --> MAXPOOL1
    CONV2D_2 --> MAXPOOL1
    CONV2D_3 --> MAXPOOL1
    
    MAXPOOL1 --> CONCAT
    CONCAT --> FINAL_RESHAPE
```

The `CNNCharEmbedding` class in `block_zoo/embedding/CNNCharEmbedding.py` implements multi-scale character convolutions with configurable window sizes and output dimensions, allowing the model to capture character patterns at different granularities.

Sources: [block_zoo/embedding/CNNCharEmbedding.py:93-132](), [model_zoo/advanced/conf.json:91-101]()

## Data Pipeline and Evaluation Integration

Model examples integrate with NeuronBlocks' data processing and evaluation systems through standardized configuration patterns and evaluation utilities.

### Model-to-Evaluation Pipeline

```mermaid
graph LR
    subgraph "Model Configuration"
        MODEL_INPUTS["model_inputs<br/>question, answer"]
        TARGET["target<br/>label"]
        PREDICT_FIELDS["predict_fields<br/>prediction, confidence"]
    end
    
    subgraph "Training Process"
        TRAIN_PY["train.py<br/>Training Orchestrator"]
        LEARNING_MACHINE["LearningMachine<br/>Training Logic"]
        MODEL_SAVE["Model Checkpoints<br/>model.nb files"]
    end
    
    subgraph "Evaluation Tools"
        CALC_AUC["calculate_auc.py<br/>AUC calculation utility"]
        METRICS_EVAL["Built-in Metrics<br/>accuracy, f1, seq_tag_f1"]
        PREDICT_OUTPUT["Prediction Output<br/>predict.tsv files"]
    end
    
    subgraph "Cache System"
        CACHE_DIR["cache_dir<br/>.cache.* directories"]
        VOCAB_CACHE["Vocabulary Caching<br/>Preprocessing optimization"]
        DATA_ENCODING["Data Encoding Cache<br/>cencoding_* files"]
    end
    
    MODEL_INPUTS --> TRAIN_PY
    TARGET --> TRAIN_PY
    TRAIN_PY --> LEARNING_MACHINE
    LEARNING_MACHINE --> MODEL_SAVE
    
    MODEL_SAVE --> PREDICT_OUTPUT
    PREDICT_FIELDS --> PREDICT_OUTPUT
    PREDICT_OUTPUT --> CALC_AUC
    PREDICT_OUTPUT --> METRICS_EVAL
    
    TRAIN_PY --> CACHE_DIR
    CACHE_DIR --> VOCAB_CACHE
    VOCAB_CACHE --> DATA_ENCODING
```

The evaluation pipeline supports multiple output formats and metrics. The `calculate_auc.py` utility provides external AUC calculation for binary classification tasks, while built-in metrics handle multi-class and sequence tagging scenarios.

Sources: [tools/calculate_auc.py:27-34](), [model_zoo/advanced/conf.json:45-47](), [settings.py:24-32]()

## Extension and Registration Patterns

Model examples can be extended with custom blocks using the registration system, enabling contribution of new neural network components.

### Block Registration Workflow

```mermaid
graph TD
    subgraph "Block Development"
        CUSTOM_BLOCK["CustomBlock.py<br/>User Implementation"]
        CUSTOM_CONF["CustomBlockConf<br/>Configuration Class"]
        BLOCK_ZOO_DIR["block_zoo/<subdir>/<br/>Block Location"]
    end
    
    subgraph "Registration Process"
        REGISTER_PY["register_block.py<br/>Registration Utility"]
        GET_BLOCK_PATH["get_block_path()<br/>Find block file"]
        WRITE_FILE["write_file()<br/>Update __init__.py"]
        IMPORT_LINE["Import Statement<br/>from .subdir import CustomBlock, CustomBlockConf"]
    end
    
    subgraph "Integration"
        INIT_FILES["__init__.py Files<br/>Block discovery"]
        MODEL_CONFIG["Model Configuration<br/>JSON architecture"]
        AUTOTEST["Automated Testing<br/>Quality assurance"]
    end
    
    CUSTOM_BLOCK --> BLOCK_ZOO_DIR
    CUSTOM_CONF --> BLOCK_ZOO_DIR
    BLOCK_ZOO_DIR --> REGISTER_PY
    
    REGISTER_PY --> GET_BLOCK_PATH
    GET_BLOCK_PATH --> WRITE_FILE
    WRITE_FILE --> IMPORT_LINE
    
    IMPORT_LINE --> INIT_FILES
    INIT_FILES --> MODEL_CONFIG
    MODEL_CONFIG --> AUTOTEST
```

The `register_block.py` utility automates the process of making custom blocks discoverable by the NeuronBlocks framework, ensuring proper import statements are added to the appropriate `__init__.py` files throughout the block zoo hierarchy.

Sources: [register_block.py:8-55]()

---

