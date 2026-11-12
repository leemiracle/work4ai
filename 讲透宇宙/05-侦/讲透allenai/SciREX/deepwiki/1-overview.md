<!-- source: DeepWiki mcp.deepwiki.com · repo allenai/SciREX · page 1 Overview · fetched 2026-10-26 -->

# Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [requirements.txt](requirements.txt)

</details>



## Purpose and Scope

This document provides a high-level introduction to the SciREX system, its architecture, and the structure of the codebase. SciREX is a document-level information extraction challenge dataset designed for extracting structured information from scientific papers, including named entities, coreference clusters, and N-ary relations between entities.

For detailed information about specific subsystems:
- Dataset format and schemas: see [Data Format Specification](#2.1)
- Model architectures: see [Model Architecture](#3)
- Training procedures: see [Training](#4)
- Prediction and evaluation: see [Prediction and Evaluation](#5)

---

## What is SciREX?

SciREX (Scientific Information Extraction) is both a dataset and a system for document-level information extraction from scientific papers. The system extracts four types of salient entities (**Method**, **Metric**, **Task**, **Material**) along with their mentions, coreference clusters, and N-ary relations (typically 4-ary tuples connecting Method-Metric-Task-Material entities with an optional Score).

### Key Characteristics

| Aspect | Description |
|--------|-------------|
| **Task Type** | Document-level multi-task information extraction |
| **Input** | Full scientific paper text (sentences and sections) |
| **Output** | NER mentions, salient entity clusters, N-ary relations |
| **Dataset Size** | train/dev/test splits in JSONL format |
| **Base Model** | SciBERT (domain-adapted BERT for scientific text) |
| **Framework** | AllenNLP for training infrastructure |

**Sources:** [README.md:1-28]()

---

## System Architecture

The SciREX system follows a modular pipeline architecture with two parallel training workflows and a sequential prediction workflow.

```mermaid
graph TB
    subgraph Dataset["Dataset Layer"]
        TrainData["train.jsonl<br/>scirex_dataset/"]
        DevData["dev.jsonl"]
        TestData["test.jsonl"]
    end
    
    subgraph DataReaders["Data Readers"]
        ScirexReader["ScirexFullReader<br/>scirex/dataset_readers/scirex_full_reader.py"]
        CorefReaders["Coreference Readers<br/>scirex/dataset_readers/"]
        MultiLabelField["MultiLabelField<br/>scirex/data/fields/multilabel_field.py"]
    end
    
    subgraph Training["Training Pipeline"]
        TrainMain["train_scirex_model.sh<br/>scirex/commands/"]
        TrainCoref["train_pairwise_coreference.sh"]
        ConfigMain["scirex_full.jsonnet<br/>scirex/training_config/"]
        ConfigCoref["pairwise_coreference.jsonnet"]
    end
    
    subgraph Models["Model Components"]
        ScirexModel["ScirexModel<br/>scirex/models/scirex_model.py"]
        CorefModel["PairwiseCoreference<br/>scirex/models/"]
        RelationExtractor["RelationExtractor<br/>scirex/models/relation_extractor.py"]
    end
    
    subgraph Prediction["Prediction Pipeline"]
        PredictScript["predict_scirex_model.sh<br/>scirex/commands/"]
        PredNER["predict_ner.py<br/>scirex/predictors/"]
        PredSalient["predict_salient_mentions.py"]
        PredCoref["predict_pairwise_coreference.py"]
        PredCluster["predict_clusters.py"]
        PredRel["predict_n_ary_relations.py"]
    end
    
    subgraph Evaluation["Evaluation"]
        EvalScript["scirex_relation_evaluate.py<br/>scirex/evaluation_scripts/"]
        Metrics["Precision/Recall/F1"]
    end
    
    subgraph Visualization["Visualization"]
        Browser["index.html<br/>SciREX Browser<br/>scirex_dataset/html/"]
    end
    
    TrainData --> ScirexReader
    ScirexReader --> MultiLabelField
    MultiLabelField --> TrainMain
    MultiLabelField --> TrainCoref
    
    TrainMain --> ConfigMain
    TrainCoref --> ConfigCoref
    ConfigMain --> ScirexModel
    ConfigCoref --> CorefModel
    ScirexModel --> RelationExtractor
    
    ScirexModel --> PredictScript
    CorefModel --> PredictScript
    PredictScript --> PredNER
    PredNER --> PredSalient
    PredNER --> PredCoref
    PredCoref --> PredCluster
    PredCluster --> PredRel
    PredSalient --> PredRel
    
    PredRel --> EvalScript
    TestData --> EvalScript
    EvalScript --> Metrics
    
    TrainData --> Browser
    Metrics --> Browser
```

**Sources:** [README.md:40-57]()

---

## Key Components and Code Mapping

### Data Layer

The dataset consists of three JSONL files containing document-level annotations:

| File | Location | Contents |
|------|----------|----------|
| `train.jsonl` | [scirex_dataset/release_data.tar.gz]() | Training documents with full annotations |
| `dev.jsonl` | [scirex_dataset/release_data.tar.gz]() | Development set for validation |
| `test.jsonl` | [scirex_dataset/release_data.tar.gz]() | Test set for final evaluation |

Each document contains: `doc_id`, `words`, `sentences`, `sections`, `ner`, `coref`, `n_ary_relations`, `method_subrelations`.

**Sources:** [README.md:3-26]()

### Data Processing Components

```mermaid
graph LR
    subgraph Input["Input Format"]
        JSON["Document JSON<br/>{doc_id, words, sentences,<br/>sections, ner, coref,<br/>n_ary_relations}"]
    end
    
    subgraph Processing["Processing Classes"]
        Reader["ScirexFullReader<br/>dataset_readers/<br/>scirex_full_reader.py"]
        Cleaner["clean_json_dict()<br/>merge method_subrelations"]
        Verifier["verify_json_dict()<br/>validate alignment"]
        Resizer["resize_sections()<br/>fit max_length=300"]
    end
    
    subgraph Fields["AllenNLP Fields"]
        TextField["TextField<br/>tokenized text"]
        SpanField["SpanField<br/>entity spans"]
        MultiLabel["MultiLabelField<br/>multi-cluster membership"]
        SequenceLabel["SequenceLabelField<br/>NER tags"]
        Metadata["MetadataField<br/>doc_id, etc"]
    end
    
    JSON --> Reader
    Reader --> Cleaner
    Cleaner --> Verifier
    Verifier --> Resizer
    Resizer --> TextField
    Resizer --> SpanField
    Resizer --> MultiLabel
    Resizer --> SequenceLabel
    Resizer --> Metadata
```

**Sources:** [README.md:8-26]()

### Training Workflow

The system uses a two-phase training approach:

1. **Main Model Training**: Executed via [scirex/commands/train_scirex_model.sh]()
   - Trains `ScirexModel` for multi-task NER, saliency detection, and relation extraction
   - Configuration: [scirex/training_config/scirex_full.jsonnet]()
   - Requires `BERT_BASE_FOLDER` environment variable pointing to SciBERT weights

2. **Coreference Model Training**: Executed via [scirex/commands/train_pairwise_coreference.sh]()
   - Trains pairwise coreference classifier
   - Configuration: [scirex/training_config/pairwise_coreference.jsonnet]()
   - Uses same SciBERT base model

**Sources:** [README.md:40-46]()

### Model Architecture Components

```mermaid
graph TB
    subgraph Embeddings["Embedding Layer"]
        SciBERT["SciBERT<br/>TextFieldEmbedder"]
        ContextEncoder["Context Layer<br/>Seq2SeqEncoder"]
    end
    
    subgraph Tasks["Task Modules in ScirexModel"]
        NER["NER Tagger<br/>token-level classification"]
        Saliency["Saliency Classifier<br/>span-level binary"]
        Relations["N-ary Relation Extractor<br/>tuple extraction"]
    end
    
    subgraph Auxiliary["Auxiliary Models"]
        CorefPairwise["Pairwise Coreference<br/>span pair classification"]
        RelationBinary["RelationExtractor<br/>binary relation classification"]
    end
    
    SciBERT --> ContextEncoder
    ContextEncoder --> NER
    ContextEncoder --> Saliency
    ContextEncoder --> Relations
    
    CorefPairwise -.separate model.-> Relations
```

The `ScirexModel` class implements multi-task learning with three parallel objectives, each with configurable loss weights (`nw`, `lw`, `rw`).

**Sources:** [README.md:40-46]()

### Prediction Pipeline

The prediction system follows a strict sequential dependency chain:

```mermaid
graph LR
    Input["test.jsonl"] --> PredNER["predict_ner.py<br/>Extract NER spans"]
    PredNER --> Out1["ner_predictions.jsonl"]
    PredNER --> PredSalient["predict_salient_mentions.py<br/>Filter salient entities"]
    PredNER --> PredCoref["predict_pairwise_coreference.py<br/>Pairwise coref scores"]
    PredCoref --> PredCluster["predict_clusters.py<br/>Cluster formation"]
    PredCluster --> Out2["cluster_predictions.jsonl"]
    PredCluster --> PredRel["predict_n_ary_relations.py<br/>Extract 4-ary tuples"]
    PredSalient --> PredRel
    PredRel --> Out3["relations_predictions.jsonl"]
```

All five prediction steps are orchestrated by [scirex/commands/predict_scirex_model.sh:1-57]().

**Sources:** [README.md:48-57]()

### Evaluation System

The evaluation script [scirex/evaluation_scripts/scirex_relation_evaluate.py]() performs:

1. **Span Mapping**: Fuzzy matching of predicted spans to gold spans (>0.5 IOU)
2. **Cluster Mapping**: Mapping spans to coreference clusters
3. **Relation Filtering**: Removing relations with entities missing textual mentions (noted at [README.md:28]() as affecting ~50% of relations)
4. **Metric Calculation**: Computing precision, recall, and F1 per entity type

**Sources:** [README.md:28]()

---

## Data Flow Through the System

The following diagram illustrates how data transforms through the complete pipeline:

```mermaid
graph TB
    Raw["Raw JSONL<br/>doc_id, words, sentences,<br/>ner, coref, n_ary_relations"]
    
    subgraph Read["Data Reading"]
        Clean["clean_json_dict<br/>merge method_subrelations"]
        Verify["verify_json_dict<br/>validate spans"]
        Resize["resize_sections<br/>paragraph chunking"]
    end
    
    subgraph Train["Training"]
        Instance["AllenNLP Instance<br/>TextField, SpanField,<br/>MultiLabelField"]
        Model["Model Training<br/>ScirexModel +<br/>Coreference Model"]
        Archive["Model Archives<br/>experiment_scirex_full/<br/>experiment_coreference/"]
    end
    
    subgraph Predict["Prediction"]
        NER["NER Prediction<br/>entity spans + types"]
        Salient["Salient Filtering<br/>cluster membership"]
        Coref["Coreference Resolution<br/>pairwise scores"]
        Cluster["Cluster Formation<br/>coref groups"]
        Relation["Relation Extraction<br/>4-ary tuples"]
    end
    
    subgraph Eval["Evaluation"]
        Map["Span Matching<br/>fuzzy IOU > 0.5"]
        Filter["Relation Filtering<br/>remove missing entities"]
        Metrics["Compute P/R/F1<br/>per entity type"]
    end
    
    Raw --> Clean
    Clean --> Verify
    Verify --> Resize
    Resize --> Instance
    Instance --> Model
    Model --> Archive
    
    Archive --> NER
    NER --> Salient
    NER --> Coref
    Coref --> Cluster
    Cluster --> Relation
    Salient --> Relation
    
    Relation --> Map
    Map --> Filter
    Filter --> Metrics
```

**Sources:** [README.md:1-57]()

---

## Repository Structure

The repository is organized into the following main directories:

| Directory | Purpose |
|-----------|---------|
| `scirex/dataset_readers/` | Data loading and preprocessing classes |
| `scirex/models/` | Neural network model implementations |
| `scirex/predictors/` | Prediction scripts for each task |
| `scirex/evaluation_scripts/` | Evaluation and metric calculation |
| `scirex/training_config/` | Jsonnet configuration files |
| `scirex/commands/` | Shell scripts for training and prediction |
| `scirex/data/fields/` | Custom AllenNLP field types |
| `scirex_dataset/` | Dataset files and browser visualization |

**Sources:** [README.md:1-74]()

---

## Installation and Setup

The system requires Python 3.7 and AllenNLP 0.9.0. Key dependencies:

| Dependency | Version | Purpose |
|------------|---------|---------|
| `allennlp` | 0.9.0 | Training framework |
| `spacy` | 2.1.6 | Text processing |
| `fuzzywuzzy` | 0.17.0 | Entity string matching |
| `scikit-learn` | 0.21.3 | Evaluation metrics |

Setup steps:
1. Create conda environment: `conda create -n scirex python=3.7`
2. Install dependencies: `pip install -r requirements.txt`
3. Download spaCy model: `python -m spacy download en`
4. Set `PYTHONPATH` to repository root
5. Extract dataset: `tar -xvzf scirex_dataset/release_data.tar.gz --directory scirex_dataset`
6. Set `BERT_BASE_FOLDER` environment variable pointing to SciBERT weights

For detailed installation instructions, see [Installation and Setup](#8.2).

**Sources:** [README.md:31-44](), [requirements.txt:1-18]()

---

## External Integrations

The system integrates with:

- **AllenNLP**: Core training and data processing framework
- **SciBERT**: Pre-trained BERT model for scientific text (download from [README.md:44]())
- **DyGIE++**: Alternative information extraction framework with format converters (see [DyGIE++ Integration](#7.1))
- **Semantic Scholar**: Papers referenced via `doc_id` field
- **SciREX Browser**: Web-based visualization at https://allenai.github.io/SciREX/

**Sources:** [README.md:4](), [README.md:44]()

---

## Important Notes

### Relation Evaluation Caveat

Approximately 50% of relations in the dataset contain at least one entity with no textual mentions (they appear only in tables, which are excluded from the dataset). During evaluation, these relations are filtered out at [scirex/evaluation_scripts/scirex_relation_evaluate.py:110](), which artificially reduces precision metrics. This is a known limitation documented in [README.md:28]().

### Citation

For academic use, cite the following paper:
```bibtex
@inproceedings{jain-etal-2020-scirex,
  title={SciREX: A Challenge Dataset for Document-Level Information Extraction},
  author={Sarthak Jain and Madeleine van Zuylen and Hannaneh Hajishirzi and Iz Beltagy},
  booktitle = "Proceedings of the 58th Annual Meeting of the Association for Computational Linguistics",
  month={jul},
  year={2020},
  eprint={2005.00512},
  archivePrefix={arXiv},
  primaryClass={cs.CL}
}
```

**Sources:** [README.md:59-73]()

---

