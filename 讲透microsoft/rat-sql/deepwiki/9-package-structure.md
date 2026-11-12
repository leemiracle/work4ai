<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/rat-sql · page 9 Package Structure · fetched 2026-10-26 -->

# Package Structure

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [ratsql/__init__.py](ratsql/__init__.py)
- [ratsql/commands/__init__.py](ratsql/commands/__init__.py)

</details>



This document provides a comprehensive overview of the RAT-SQL repository package structure and organization. It explains the main packages, their relationships, and how they map to the system functionality described in the [System Architecture](#3) document. Understanding this package structure will help developers navigate the codebase effectively and locate relevant components when modifying or extending the system.

## Overview

RAT-SQL is organized as a Python package with a modular structure that separates the different functional components of the text-to-SQL system. The main package is `ratsql`, which contains several subpackages organized by functionality.

```mermaid
graph TD
    subgraph "Repository Root"
        run["run.py - Main Entry Point"]
        experiments["experiments/ - Configuration Files"]
        ratsql["ratsql/ - Main Package"]
        third_party["third_party/ - External Dependencies"]
    end
    
    subgraph "ratsql Package"
        commands["commands/ - CLI Commands"]
        models["models/ - Neural Models"]
        datasets["datasets/ - Dataset Processing"]
        utils["utils/ - Utilities"]
        preprocessors["preprocessors/ - Data Preparation"]
        resources["resources/ - Static Resources"]
    end
    
    run -->|uses| ratsql
    experiments -->|configures| run
    
    ratsql --> commands
    ratsql --> models
    ratsql --> datasets
    ratsql --> utils
    ratsql --> preprocessors
    ratsql --> resources
```

Sources: [README.md:78-86](), [ratsql/__init__.py](), [ratsql/commands/__init__.py]()

## Main Package Structure

The `ratsql` package is the core of the system and contains the following main subpackages:

| Package | Description |
|---------|-------------|
| `commands` | Contains the command handlers for preprocessing, training, evaluation, and inference operations |
| `models` | Houses the model architecture components, including encoders and decoders |
| `datasets` | Manages dataset loading, processing, and conversions for Spider and WikiSQL |
| `utils` | General utility functions and helpers used throughout the codebase |
| `preprocessors` | Data preprocessing logic for transforming raw inputs into model-ready formats |
| `resources` | Static resources and configuration files used by the system |

## Command Package Structure

The command package implements the main operations exposed through the CLI interface. Each command corresponds to a specific operation in the pipeline.

```mermaid
graph TD
    subgraph "commands Package"
        init["__init__.py"]
        preprocess["preprocess.py"]
        train["train.py"]
        infer["infer.py"]
        eval["eval.py"]
    end
    
    subgraph "CLI Interface"
        run["run.py"]
        run -->|"run.py preprocess"| preprocess
        run -->|"run.py train"| train
        run -->|"run.py eval"| infer
        run -->|"run.py eval"| eval
    end
    
    preprocess -->|produces| preprocessed[("Preprocessed Data")]
    train -->|reads| preprocessed
    train -->|produces| model[("Model Checkpoints")]
    infer -->|uses| model
    infer -->|produces| predictions[("SQL Predictions")]
    eval -->|evaluates| predictions
```

Sources: [ratsql/commands/__init__.py](), [README.md:83-86]()

## Model Package Structure

The models package contains the neural network architecture components, including the encoder and decoder variants.

```mermaid
graph TD
    subgraph "models Package"
        base["base.py - Base Model Classes"]
        nl2code["nl2code/ - Decoder Implementation"]
        spider["spider/ - Spider Encoders"]
        spider_enc["spider/spider_enc.py - Base Spider Encoder"]
        spider_enc_v2["spider/spider_enc_v2.py - GloVe Encoder"]
        spider_bert["spider/spider_bert_enc.py - BERT Encoder"]
    end
    
    subgraph "Model Interface"
        model_interface["Model Interface"]
        model_interface --> spider_enc
        model_interface --> nl2code
    end
    
    base --> spider_enc
    spider_enc --> spider_enc_v2
    spider_enc --> spider_bert
    
    subgraph "Decoder Implementation"
        nl2code_base["nl2code/decoder.py - NL2Code Decoder"]
        nl2code_train["nl2code/train.py - Training Logic"]
        nl2code_infer["nl2code/infer.py - Inference Logic"]
    end
    
    nl2code --> nl2code_base
    nl2code --> nl2code_train
    nl2code --> nl2code_infer
```

Sources: [README.md:88-92]()

## Dataset Package Structure

The dataset package handles the loading, processing, and manipulation of the Spider and WikiSQL datasets.

```mermaid
graph TD
    subgraph "datasets Package"
        spider_data["spider/ - Spider Dataset Handling"]
        wikisql_data["wikisql/ - WikiSQL Dataset Handling"]
        dataset["dataset.py - Base Dataset Classes"]
    end
    
    subgraph "Spider Dataset Processing"
        spider_vocab["spider/vocab.py - Vocabulary Building"]
        spider_process["spider/process_sql.py - SQL Processing"]
        spider_load["spider/load_spider.py - Data Loading"]
    end
    
    subgraph "WikiSQL Dataset Processing"
        wikisql_vocab["wikisql/vocab.py - Vocabulary Building"]
        wikisql_process["wikisql/process_sql.py - SQL Processing"]
        wikisql_load["wikisql/load_wikisql.py - Data Loading"]
    end
    
    dataset --> spider_data
    dataset --> wikisql_data
    
    spider_data --> spider_vocab
    spider_data --> spider_process
    spider_data --> spider_load
    
    wikisql_data --> wikisql_vocab
    wikisql_data --> wikisql_process
    wikisql_data --> wikisql_load
```

Sources: [README.md:30-53]()

## Runtime Data Flow Between Packages

This diagram illustrates how data flows between different packages during the execution of RAT-SQL processing pipeline:

```mermaid
flowchart LR
    subgraph "External Data"
        spider[("Spider Dataset")]
        wikisql[("WikiSQL Dataset")]
    end
    
    subgraph "ratsql Packages"
        direction TB
        preproc["preprocessors"]
        dataset_pkg["datasets"]
        models_pkg["models"]
        commands_pkg["commands"]
        utils_pkg["utils"]
    end
    
    subgraph "Processing Flow"
        preprocess_cmd["commands.preprocess"]
        train_cmd["commands.train"]
        infer_cmd["commands.infer"]
        eval_cmd["commands.eval"]
    end
    
    spider --> dataset_pkg
    wikisql --> dataset_pkg
    
    dataset_pkg --> preproc
    preproc --> preprocess_cmd
    
    preprocess_cmd --> |"Processed Data"| train_cmd
    train_cmd --> |"Model Checkpoint"| infer_cmd
    infer_cmd --> |"SQL Predictions"| eval_cmd
    
    models_pkg --> train_cmd
    models_pkg --> infer_cmd
    
    utils_pkg --> preprocess_cmd
    utils_pkg --> train_cmd
    utils_pkg --> infer_cmd
    utils_pkg --> eval_cmd
```

Sources: [README.md:83-86]()

## Configuration Files Organization

The configuration system in RAT-SQL uses JSONNET files to define experiment settings and model architectures. These files are organized in the `experiments` directory.

```mermaid
graph TD
    subgraph "experiments/ Directory"
        spider_glove["spider-glove-run.jsonnet"]
        spider_bert["spider-bert-run.jsonnet"]
        wikisql_glove["wikisql-glove-run.jsonnet"]
    end
    
    subgraph "Model Configurations"
        nl2code_glove["nl2code-glove.jsonnet"]
        nl2code_bert["nl2code-bert.jsonnet"]
        nl2code_base["nl2code-base.libsonnet"]
    end
    
    subgraph "run.py Interface"
        run["run.py"]
    end
    
    spider_glove -->|references| nl2code_glove
    spider_bert -->|references| nl2code_bert
    wikisql_glove -->|references| nl2code_base
    
    nl2code_glove -->|inherits from| nl2code_base
    nl2code_bert -->|inherits from| nl2code_base
    
    run -->|loads| spider_glove
    run -->|loads| spider_bert
    run -->|loads| wikisql_glove
```

Sources: [README.md:88-92]()

## Code-to-Entity Mapping

This diagram maps the main code entities (classes and modules) to their corresponding system components, bridging the gap between the natural language descriptions and the actual code implementation:

```mermaid
graph TD
    subgraph "Natural Language Space"
        nl_encoder["Encoder Component"]
        nl_decoder["Decoder Component"]
        nl_preprocess["Preprocessing Pipeline"]
        nl_train["Training System"]
    end
    
    subgraph "Code Entity Space"
        SpiderEncoderV2["SpiderEncoderV2 (models.spider.spider_enc_v2)"]
        SpiderEncoderBert["SpiderEncoderBert (models.spider.spider_bert_enc)"]
        NL2CodeDecoder["NL2CodeDecoder (models.nl2code.decoder)"]
        Preprocessor["BatchPreproc (preprocessors.spider)"]
        Trainer["TrainModel (commands.train)"]
    end
    
    nl_encoder --> SpiderEncoderV2
    nl_encoder --> SpiderEncoderBert
    nl_decoder --> NL2CodeDecoder
    nl_preprocess --> Preprocessor
    nl_train --> Trainer
```

Sources: [README.md:90-92]()

## File Organization for RAT-SQL Components

This diagram shows how the different RAT-SQL components map to specific files in the repository structure:

```mermaid
graph TD
    subgraph "RAT-SQL Components"
        component_cli["Command-Line Interface"]
        component_encoder["Encoder Architecture"]
        component_decoder["Decoder Architecture"]
        component_dataset["Dataset Processing"]
        component_train["Training System"]
        component_eval["Evaluation System"]
    end
    
    subgraph "Repository Files"
        file_run["run.py"]
        file_spider_enc["ratsql/models/spider/spider_enc.py"]
        file_spider_encv2["ratsql/models/spider/spider_enc_v2.py"]
        file_spider_bert["ratsql/models/spider/spider_bert_enc.py"]
        file_nl2code["ratsql/models/nl2code/decoder.py"]
        file_spider_ds["ratsql/datasets/spider/"]
        file_wikisql_ds["ratsql/datasets/wikisql/"]
        file_train["ratsql/commands/train.py"]
        file_eval["ratsql/commands/eval.py"]
    end
    
    component_cli --> file_run
    component_encoder --> file_spider_enc
    component_encoder --> file_spider_encv2
    component_encoder --> file_spider_bert
    component_decoder --> file_nl2code
    component_dataset --> file_spider_ds
    component_dataset --> file_wikisql_ds
    component_train --> file_train
    component_eval --> file_eval
```

Sources: [README.md:83-92]()

## Package Dependencies

This diagram illustrates the dependencies between the main packages in RAT-SQL:

```mermaid
graph LR
    subgraph "External Dependencies"
        pytorch["PyTorch"]
        corenlp["Stanford CoreNLP"]
        bert["BERT Models"]
        nltk["NLTK"]
    end
    
    subgraph "RAT-SQL Packages"
        commands["ratsql.commands"]
        models["ratsql.models"]
        datasets["ratsql.datasets"]
        utils["ratsql.utils"]
        preprocessors["ratsql.preprocessors"]
    end
    
    pytorch --> models
    corenlp --> preprocessors
    bert --> models
    nltk --> preprocessors
    
    models --> commands
    datasets --> commands
    datasets --> preprocessors
    preprocessors --> commands
    utils --> commands
    utils --> models
    utils --> datasets
    utils --> preprocessors
```

Sources: [README.md:74-75]()

## Summary

The RAT-SQL package structure follows a modular design that separates concerns based on functionality. The `ratsql` package contains subpackages for commands, models, datasets, utilities, and preprocessing. This organization facilitates maintenance, extension, and customization of the system. The package structure maps directly to the system architecture described in the [System Architecture](#3) document, with clear separation between the preprocessing, training, and evaluation components.

---

