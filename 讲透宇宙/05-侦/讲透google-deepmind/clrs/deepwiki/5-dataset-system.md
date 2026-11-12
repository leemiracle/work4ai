<!-- source: DeepWiki mcp.deepwiki.com · repo google-deepmind/clrs · page 5 Dataset System · fetched 2026-10-26 -->

# Dataset System

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [clrs/__init__.py](clrs/__init__.py)
- [clrs/_src/dataset.py](clrs/_src/dataset.py)
- [clrs/_src/dataset_test.py](clrs/_src/dataset_test.py)

</details>



The Dataset System in the CLRS benchmark is responsible for creating, managing, and processing algorithmic data for training and evaluation. It provides utilities for handling both full-trajectory algorithm execution traces and fixed-length chunks for more efficient training with neural networks.

For information about data chunking specifically, see [Data Chunking](#5.1).

## Architecture Overview

**Dataset System Architecture**
```mermaid
graph TD
    subgraph "Dataset System Components"
        CLRSDs["CLRSDataset Class"] -->|implements| TFDsBuilder["TensorFlow GeneratorBasedBuilder"]
        CLRSDs -->|generates| AlgExamples["Algorithm Examples"]
        CLRSDs -->|uses| BuilderCfg["BuilderConfig<br/>(algorithm_split)"]
        
        CreateDs["create_dataset()"] -->|creates| FullTrajectory["Full-trajectory<br/>Datasets"]
        CreateChunkDs["create_chunked_dataset()"] -->|creates| ChunkedDs["Chunked<br/>Datasets"]
        
        CreateChunkDs -->|uses| Chunkify["chunkify()"]
        Chunkify -->|transforms| FullTrajectory
        Chunkify -->|produces| ChunkedDs
        
        Preprocess["_preprocess()"] -->|converts| RawData["Raw Data"]
        Preprocess -->|produces| DataPoints["DataPoint Objects"]
        
        CreateDs -->|uses| Preprocess
        CreateChunkDs -->|uses| Preprocess
    end
    
    subgraph "External Interfaces"
        TFDs["TensorFlow Datasets"] <-->|data access| CLRSDs
        AlgoSpecs["Algorithm Specifications"] -->|defines data structure| Preprocess
        Samplers["Algorithm Samplers"] -->|generates| RawData
    end
```

Sources: [clrs/_src/dataset.py:58-138](), [clrs/_src/dataset.py:153-178](), [clrs/_src/dataset.py:181-189](), [clrs/_src/dataset.py:211-330]()

## Core Components

### CLRSDataset Class

The core of the dataset system is the `CLRSDataset` class, which implements TensorFlow's `GeneratorBasedBuilder` interface. This class enables seamless integration with TensorFlow's dataset ecosystem while providing specialized functionality for algorithmic reasoning tasks.

**CLRSDataset Inheritance and Structure**
```mermaid
classDiagram
    class CLRSDataset {
        VERSION = "1.0.0"
        BUILDER_CONFIGS = DEFAULT_BUILDER_CONFIGS
        _instantiated_dataset
        _instantiated_dataset_name
        _instantiated_dataset_split
        _create_data(single_sample)
        _info() -> DatasetInfo
        _split_generators(dl_manager) -> dict
        _generate_examples() -> (id, data)
    }
    
    class CLRSConfig {
        name: str
        split: str
    }
    
    class GeneratorBasedBuilder {
        info: DatasetInfo
        download_and_prepare()
        as_dataset()
    }
    
    GeneratorBasedBuilder <|-- CLRSDataset : extends
    CLRSConfig --|> CLRSDataset : configures
```

Sources: [clrs/_src/dataset.py:39-52](), [clrs/_src/dataset.py:58-138]()

The `CLRSDataset` class handles:
- Generating algorithm-specific data points
- Supporting different split configurations (train/val/test)
- Providing consistent dataset interfaces through TensorFlow Datasets
- Managing the creation and access to algorithm execution trajectories

### Dataset Creation Functions

The system provides two main functions for creating datasets:

#### 1. create_dataset

The `create_dataset` function creates datasets with full-trajectory samples:

```python
def create_dataset(folder, algorithm, split, batch_size):
    """Create dataset with full-trajectory samples."""
    # Returns (processed_dataset, num_samples, specs)
```

#### 2. create_chunked_dataset

The `create_chunked_dataset` function creates datasets with fixed-length chunks:

```python
def create_chunked_dataset(folder, algorithm, split, batch_size, chunk_length):
    """Create dataset with fixed-length chunks."""
    # Returns (chunked_dataset, specs)
```

**Dataset Creation Flow**
```mermaid
flowchart LR
    subgraph "Input Parameters"
        folder["folder"]
        algorithm["algorithm"]
        split["split"]
        batchSize["batch_size"]
        chunkLength["chunk_length"]
    end
    
    subgraph "Dataset Creation Pipeline"
        loadDS["tfds.load()"]
        repeat["dataset.repeat()"]
        batch["dataset.batch()"]
        preprocess["_preprocess()"]
        chunkify["chunkify()"]
    end
    
    subgraph "Output"
        processedDS["Processed Dataset"]
        numSamples["Number of Samples"]
        specs["Algorithm Specifications"]
    end
    
    folder & algorithm & split --> loadDS
    loadDS --> repeat
    repeat --> batch
    batchSize --> batch
    batch --> preprocess
    algorithm --> preprocess
    
    %% For create_dataset
    preprocess --> processedDS
    
    %% For create_chunked_dataset
    preprocess --> chunkify
    chunkLength --> chunkify
    chunkify --> processedDS
    
    processedDS & numSamples & specs --> result["Return Value"]
```

Sources: [clrs/_src/dataset.py:181-189](), [clrs/_src/dataset.py:323-330]()

## Data Processing

### Preprocessing

The `_preprocess` function converts raw data into structured `DataPoint` objects:

```python
def _preprocess(data_point, algorithm=None):
    """Convert sampled inputs into DataPoints."""
    # Sorts data into inputs, outputs, and hints
    # Creates DataPoint objects
    # Returns Feedback object
```

**Data Preprocessing Flow**
```mermaid
flowchart LR
    subgraph "Input"
        rawData["data_point"]
        algorithm["algorithm"]
    end
    
    subgraph "Preprocessing Steps"
        extractFields["Extract Fields from Names"]
        sortData["Sort Data by Type<br/>(input/hint/output)"]
        createDataPoints["Create DataPoint Objects"]
        createFeedback["Create Feedback Object"]
    end
    
    subgraph "Reference Data"
        specs["SPECS[algorithm]"]
    end
    
    subgraph "Output"
        processedData["samplers.Feedback Object"]
    end
    
    rawData --> extractFields
    algorithm --> specs
    specs --> sortData
    extractFields --> sortData
    sortData --> createDataPoints
    createDataPoints --> createFeedback
    createFeedback --> processedData
```

Sources: [clrs/_src/dataset.py:153-178]()

During preprocessing:
1. Data is sorted into inputs, outputs, and hints based on naming conventions
2. The algorithm's specifications determine the stage, location, and type of each data point
3. `DataPoint` objects are created for each component
4. A `Feedback` object is returned containing the processed data

## Data Chunking

The chunking mechanism is a critical component of the Dataset System that handles variable-length algorithm execution traces.

### Chunking Mechanism

The `chunkify` function converts full-trajectory samples into fixed-length chunks:

```python
def chunkify(dataset: Iterator[samplers.Feedback], chunk_length: int):
    """Generator of fixed-length chunks from full-trajectory samples."""
    # Yields fixed-length chunks of data
```

**Chunking Process**
```mermaid
flowchart TD
    subgraph "Input"
        fullDataset["Full-trajectory Dataset"]
        chunkLength["chunk_length parameter"]
    end
    
    subgraph "Chunking Process"
        createEmptyChunk["Create Empty Chunk"]
        getBatches["Get Data Batches to Fill Chunk"]
        fillChunk["Fill Chunk (one batch element at a time)"]
        markBoundaries["Mark Sample Boundaries (is_first/is_last)"]
        cleanUp["Clean Up Processed Batches"]
        yieldChunk["Yield Chunked Feedback"]
    end
    
    fullDataset & chunkLength --> chunkify["chunkify() function"]
    chunkify --> createEmptyChunk
    createEmptyChunk --> getBatches
    getBatches --> fillChunk
    fillChunk --> markBoundaries
    markBoundaries --> cleanUp
    cleanUp --> yieldChunk
    yieldChunk --> createEmptyChunk
    
    subgraph "Output"
        chunkedDataset["Fixed-length Chunked Dataset"]
    end
    
    yieldChunk --> chunkedDataset
    
    subgraph "Helper Functions"
        copyIO["_copy_io() function"]
        copyHint["_copy_hint() function"]
    end
    
    fillChunk -->|uses| copyIO
    fillChunk -->|uses| copyHint
```

Sources: [clrs/_src/dataset.py:211-320](), [clrs/_src/dataset.py:192-208]()

The chunking mechanism:
- Takes full-sample dataset and chunk_length as input
- Yields fixed-time-length chunks of data
- Uses marking tensors (`is_first` and `is_last`) to track sample boundaries
- Efficiently handles batches with samples of different lengths
- Uses helper functions `_copy_hint` and `_copy_io` to copy data to chunks

### Sample Boundaries in Chunked Data

The chunking system tracks sample boundaries using two binary indicator matrices:
- `is_first`: Marks the beginning of each sample
- `is_last`: Marks the end of each sample

For example, with `chunk_length=6` and `batch_size=2`, if one sample has length 3 and another has length 5:

| is_first | is_last |
|----------|---------|
| [1, 1]   | [0, 0]  |
| [0, 0]   | [0, 0]  |
| [0, 0]   | [1, 0]  |
| [1, 0]   | [0, 0]  |
| [0, 0]   | [0, 1]  |
| [0, 1]   | [0, 0]  |

This allows the model to recognize where samples begin and end within the batch.

Sources: [clrs/_src/dataset.py:230-235]()

## API and Integration

The Dataset System integrates with the rest of the CLRS benchmark through several exported functions:

**API and Integration Points**
```mermaid
flowchart TD
    subgraph "Dataset System API"
        CLRSDs["CLRSDataset Class"]
        createDs["create_dataset()"]
        createChunkDs["create_chunked_dataset()"]
        chunkify["chunkify()"]
        getFolder["get_clrs_folder()"]
        getURL["get_dataset_gcp_url()"]
    end
    
    subgraph "Integration Points"
        runFile["run.py"]
        samplers["samplers.py"]
        clrsText["clrs_text.py"]
    end
    
    %% Dataset System to Integration Points
    createDs -->|used by| runFile
    createChunkDs -->|used by| runFile
    CLRSDs -->|provides data for| samplers
    getURL -->|used by| runFile
    getFolder -->|used by| runFile
    
    %% Integration with CLRS-Text
    CLRSDs -->|provides data for| clrsText
    
    subgraph "External Systems"
        tfds["TensorFlow Datasets"]
        huggingFace["Hugging Face"]
    end
    
    CLRSDs -->|extends| tfds
    clrsText -->|interfaces with| huggingFace
```

Sources: [clrs/__init__.py:26-31](), [clrs/_src/dataset.py:145-150]()

## Function Reference

Here's a reference of key functions in the Dataset System:

| Function | Purpose | Parameters |
|----------|---------|------------|
| `CLRSDataset` | TensorFlow dataset implementation | - |
| `create_dataset` | Creates full-trajectory datasets | folder, algorithm, split, batch_size |
| `create_chunked_dataset` | Creates chunked datasets | folder, algorithm, split, batch_size, chunk_length |
| `chunkify` | Converts to fixed-length chunks | dataset, chunk_length |
| `get_clrs_folder` | Returns dataset folder name | - |
| `get_dataset_gcp_url` | Returns dataset download URL | - |

Sources: [clrs/__init__.py:64-94](), [clrs/_src/dataset.py:58-330]()

## Summary

The Dataset System is a flexible component of the CLRS benchmark that enables:

1. Creation of algorithm-specific datasets through the `CLRSDataset` class
2. Processing of raw algorithm data into structured `DataPoint` objects
3. Generation of both full-trajectory and chunked datasets for training
4. Efficient handling of variable-length algorithm executions through the chunking mechanism

This system forms a critical bridge between the algorithm implementation and the neural network models, providing the data structures and interfaces needed for effective algorithmic reasoning.

Sources: [clrs/_src/dataset.py:16-330]()

---

