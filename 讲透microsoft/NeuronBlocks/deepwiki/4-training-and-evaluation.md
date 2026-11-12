<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/NeuronBlocks · page 4 Training and Evaluation · fetched 2026-10-26 -->

# Training and Evaluation

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [LearningMachine.py](LearningMachine.py)
- [Model.py](Model.py)
- [block_zoo/Embedding.py](block_zoo/Embedding.py)
- [predict.py](predict.py)
- [test.py](test.py)
- [train.py](train.py)

</details>



This document provides a comprehensive overview of the training and evaluation system in NeuronBlocks, covering the end-to-end workflow from data preparation to model testing. The system is designed around a centralized `LearningMachine` class that orchestrates training, validation, and testing processes across different NLP task types.

For detailed information about specific components, see [Training Pipeline](#4.1), [Testing and Prediction](#4.2), [Data Processing](#4.3), and [Evaluation Metrics](#4.4). For model architecture details, see [Core Architecture](#3).

## System Overview

The training and evaluation system consists of three main entry points (`train.py`, `test.py`, `predict.py`) that all leverage the core `LearningMachine` class for model operations. The system supports caching, distributed training, and multiple problem types including classification, sequence tagging, regression, and machine reading comprehension.

### Core Components Architecture

```mermaid
graph TB
    subgraph "Entry Points"
        TRAIN_PY["train.py<br/>Main Training Script"]
        TEST_PY["test.py<br/>Model Testing Script"]
        PREDICT_PY["predict.py<br/>Prediction Script"]
    end
    
    subgraph "Core Classes"
        LM["LearningMachine<br/>Training/Testing Orchestrator"]
        MODEL["Model<br/>Neural Network Builder"]
        PROBLEM["Problem<br/>Data Processor"]
        MODELCONF["ModelConf<br/>Configuration Manager"]
    end
    
    subgraph "Support Systems"
        CACHE["Cache<br/>Data/Model Caching"]
        EVALUATOR["Evaluator<br/>Metrics Calculator"]
        LOSS["Loss<br/>Loss Functions"]
        OPTIMIZER["PyTorch Optimizers<br/>SGD/Adam/etc"]
    end
    
    subgraph "Data Flow"
        RAW_DATA["Raw TSV/JSON Data"]
        ENCODED_DATA["Encoded Tensors"]
        TRAINED_MODEL["Saved Model Files"]
        PREDICTIONS["Prediction Output"]
    end
    
    TRAIN_PY --> LM
    TEST_PY --> LM
    PREDICT_PY --> LM
    
    LM --> MODEL
    LM --> PROBLEM
    LM --> EVALUATOR
    LM --> LOSS
    
    TRAIN_PY --> CACHE
    TRAIN_PY --> OPTIMIZER
    
    MODELCONF --> LM
    MODELCONF --> MODEL
    MODELCONF --> PROBLEM
    
    RAW_DATA --> PROBLEM
    PROBLEM --> ENCODED_DATA
    ENCODED_DATA --> MODEL
    MODEL --> TRAINED_MODEL
    MODEL --> PREDICTIONS
    
    CACHE --> PROBLEM
    CACHE --> ENCODED_DATA
```

Sources: [train.py:1-390](), [LearningMachine.py:31-92](), [test.py:17-58](), [predict.py:15-71]()

## Training Workflow

The training process follows a structured pipeline that handles data preparation, model initialization, iterative training with validation, and model persistence. The workflow supports both fresh training and fine-tuning from pretrained models.

### Training Pipeline Flow

```mermaid
flowchart TD
    START["python train.py --conf_path config.json"] --> INIT_CONF["ModelConf('train', conf_path)"]
    INIT_CONF --> INIT_PROBLEM["Problem('train', problem_type)"]
    
    INIT_PROBLEM --> CHECK_FINETUNE{"`conf.pretrained_model_path?`"}
    CHECK_FINETUNE -->|Yes| LOAD_SAVED_PROBLEM["problem.load_problem(saved_problem_path)"]
    CHECK_FINETUNE -->|No| CACHE_CHECK
    
    LOAD_SAVED_PROBLEM --> CACHE_CHECK{"`conf.use_cache?`"}
    CACHE_CHECK -->|Yes| CACHE_VERIFY["Cache._check_dictionary()<br/>Cache._check_encoding()"]
    CACHE_CHECK -->|No| BUILD_VOCAB
    
    CACHE_VERIFY --> CACHE_VALID{"`Cache Valid?`"}
    CACHE_VALID -->|Yes| CACHE_LOAD["cache.load(conf, problem, emb_matrix)"]
    CACHE_VALID -->|No| BUILD_VOCAB["problem.build(data_path_list)<br/>Build vocabulary & embeddings"]
    
    CACHE_LOAD --> INIT_LEARNING_MACHINE
    BUILD_VOCAB --> SAVE_CACHE["cache.save(conf, params, problem)"]
    SAVE_CACHE --> INIT_LEARNING_MACHINE["LearningMachine('train', conf, problem)"]
    
    INIT_LEARNING_MACHINE --> LOAD_PRETRAINED{"`pretrained_model_path?`"}
    LOAD_PRETRAINED -->|Yes| LOAD_MODEL["lm.load_model(pretrained_model_path)"]
    LOAD_PRETRAINED -->|No| INIT_OPTIMIZER
    LOAD_MODEL --> INIT_OPTIMIZER["optimizer = eval(optimizer_name)"]
    
    INIT_OPTIMIZER --> INIT_LOSS["loss_fn = Loss(**loss_conf)"]
    INIT_LOSS --> TRAIN_LOOP["lm.train(optimizer, loss_fn)"]
    
    TRAIN_LOOP --> FINAL_TEST["lm.test(loss_fn, test_path)"]
    FINAL_TEST --> END["Training Complete"]
```

Sources: [train.py:228-338](), [train.py:108-128](), [LearningMachine.py:93-338]()

### Cache System Architecture

The caching system optimizes training by storing preprocessed data and embeddings to avoid redundant computation across training runs.

```mermaid
graph LR
    subgraph "Cache Types"
        DICT_CACHE["Dictionary Cache<br/>problem.pkl<br/>emb_matrix.pkl"]
        ENC_CACHE["Encoding Cache<br/>train_data_md5/<br/>encoded tensors"]
    end
    
    subgraph "Cache Validation"
        CONF_CHECK["Configuration Check<br/>_verify_conf()"]
        MD5_CHECK["MD5 Integrity Check<br/>md5([file_paths])"]
        INDEX_CHECK["Index File Validation<br/>encoding_cache_index"]
    end
    
    subgraph "Cache Operations"
        CHECK["cache.check(conf, params)"]
        LOAD["cache.load(conf, problem)"]
        SAVE["cache.save(conf, params)"]
        RENEW["_renew_cache()"]
    end
    
    CHECK --> CONF_CHECK
    CHECK --> MD5_CHECK
    CHECK --> INDEX_CHECK
    
    CONF_CHECK --> DICT_CACHE
    MD5_CHECK --> ENC_CACHE
    
    CHECK --> LOAD
    CHECK --> RENEW
    LOAD --> DICT_CACHE
    LOAD --> ENC_CACHE
    SAVE --> DICT_CACHE
    SAVE --> ENC_CACHE
```

Sources: [train.py:25-227](), [train.py:108-128](), [train.py:200-227]()

## LearningMachine Core Operations

The `LearningMachine` class serves as the central orchestrator for all model operations, handling different problem types and providing unified interfaces for training, testing, and prediction.

### LearningMachine Method Structure

| Method | Purpose | Key Parameters | Problem Types Supported |
|--------|---------|---------------|------------------------|
| `__init__` | Initialize learning machine | `phase`, `conf`, `problem`, `vocab_info` | All |
| `train` | Execute training loop | `optimizer`, `loss_fn` | All |
| `test` | Evaluate model on test data | `loss_fn`, `test_data_path` | All |
| `evaluate` | Internal evaluation method | `data`, `evaluator`, `loss_fn` | All |
| `predict` | Generate predictions | `data_path`, `output_path` | All |
| `interactive` | Interactive prediction mode | `samples`, `file_columns` | All |

Sources: [LearningMachine.py:31-89](), [LearningMachine.py:93-338](), [LearningMachine.py:339-360]()

### Training Loop Implementation

```mermaid
sequenceDiagram
    participant TL as "Training Loop"
    participant DG as "Data Generator"
    participant Model as "Neural Model"
    participant Loss as "Loss Function"
    participant Eval as "Evaluator"
    participant LRS as "LRScheduler"
    
    TL->>DG: _get_training_data_generator()
    loop Each Data Part
        DG->>TL: train_data, train_length, train_target
        loop Each Batch
            TL->>Model: model(inputs_desc, length_desc)
            Model->>TL: logits
            TL->>Loss: loss_fn(logits_flat, target_batches)
            Loss->>TL: loss
            TL->>Model: loss.backward()
            TL->>Model: optimizer.step()
            
            alt Validation Step
                TL->>Eval: evaluate(valid_data)
                Eval->>TL: metrics_result
                alt Best Model
                    TL->>TL: Save model checkpoint
                end
            end
        end
    end
    TL->>LRS: lr_scheduler.step()
```

Sources: [LearningMachine.py:124-338](), [LearningMachine.py:146-336]()

## Problem Type Support

The system supports multiple NLP task types with specialized handling for each:

### Problem Type Configuration

| Problem Type | Class Constant | Prediction Output | Metrics |
|-------------|---------------|------------------|---------|
| Classification | `ProblemTypes.classification` | Class probabilities | `accuracy`, `auc`, `f1` |
| Sequence Tagging | `ProblemTypes.sequence_tagging` | Tag sequences | `seq_tag_f1`, `accuracy` |
| Regression | `ProblemTypes.regression` | Continuous values | `mse`, `rmse` |
| MRC | `ProblemTypes.mrc` | Text spans | `mrc_em`, `mrc_f1` |

Sources: [LearningMachine.py:76-88](), [LearningMachine.py:182-265]()

## Testing and Prediction

The testing system reuses the same `LearningMachine` infrastructure but operates in evaluation mode with different data flow patterns.

### Test vs Predict Workflow

```mermaid
graph TB
    subgraph "test.py Workflow"
        TEST_START["test.py --conf_path config.json"] --> TEST_CONF["ModelConf('test', conf_path)"]
        TEST_CONF --> TEST_PROBLEM["Problem('test', ...)"]
        TEST_PROBLEM --> TEST_LOAD_PROBLEM["problem.load_problem(saved_problem_path)"]
        TEST_LOAD_PROBLEM --> TEST_LM["LearningMachine('test', ...)"]
        TEST_LM --> TEST_LOAD_MODEL["lm.load_model(previous_model_path)"]
        TEST_LOAD_MODEL --> TEST_EXECUTE["lm.test(loss_fn, test_path)"]
    end
    
    subgraph "predict.py Workflow"
        PRED_START["predict.py --conf_path config.json"] --> PRED_CONF["ModelConf('predict', conf_path)"]
        PRED_CONF --> PRED_PROBLEM["Problem('predict', ...)"]
        PRED_PROBLEM --> PRED_LOAD_PROBLEM["problem.load_problem(saved_problem_path)"]
        PRED_LOAD_PROBLEM --> PRED_LM["LearningMachine('predict', ...)"]
        PRED_LM --> PRED_LOAD_MODEL["lm.load_model(previous_model_path)"]
        PRED_LOAD_MODEL --> PRED_MODE{"`predict_mode`"}
        PRED_MODE -->|batch| PRED_BATCH["lm.predict(data_path, output_path)"]
        PRED_MODE -->|interactive| PRED_INTERACTIVE["lm.interactive(samples)"]
    end
```

Sources: [test.py:17-58](), [predict.py:15-71](), [predict.py:37-70]()

## GPU and Distributed Training Support

The system supports GPU acceleration and multi-GPU distributed training through PyTorch's `DataParallel`:

```mermaid
graph LR
    subgraph "GPU Configuration"
        USE_GPU["conf.use_gpu"] --> CHECK_GPU{"`torch.cuda.is_available()`"}
        CHECK_GPU -->|True| SINGLE_GPU["Single GPU Mode"]
        CHECK_GPU -->|True| MULTI_GPU["Multi-GPU DataParallel"]
        CHECK_GPU -->|False| CPU_MODE["CPU Mode"]
    end
    
    subgraph "Model Wrapping"
        SINGLE_GPU --> MODEL_GPU["model.cuda()"]
        MULTI_GPU --> DATA_PARALLEL["nn.DataParallel(model)"]
        DATA_PARALLEL --> TRANSFER_GPU["transfer_to_gpu(model)"]
    end
    
    subgraph "Batch Size Scaling"
        MULTI_GPU --> SCALE_BATCH["batch_num *= torch.cuda.device_count()"]
        SCALE_BATCH --> SCALE_LOGGING["logging *= device_count()"]
    end
```

Sources: [LearningMachine.py:36-48](), [LearningMachine.py:140-144](), [Model.py:405-420]()

## Integration Points

This training and evaluation system integrates with several other NeuronBlocks components:

- **Configuration System**: Uses `ModelConf` for parameter management (see [Configuration System](#3.3))
- **Block Zoo**: Leverages neural building blocks for model construction (see [Block Zoo](#3.1))
- **Data Processing**: Depends on `Problem` class for data handling (see [Data Processing](#4.3))
- **Model Architecture**: Uses `Model` class for neural network construction (see [Core Architecture](#3))

The system provides a complete training-to-deployment pipeline that handles the complexity of modern deep learning workflows while maintaining flexibility for different NLP tasks and deployment scenarios.

Sources: [train.py:1-390](), [LearningMachine.py:1-897](), [test.py:1-77](), [predict.py:1-91]()

---

