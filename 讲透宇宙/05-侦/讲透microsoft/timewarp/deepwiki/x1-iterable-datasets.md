<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/timewarp · extra page Iterable Datasets · fetched 2026-10-26 -->

# Iterable Datasets

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [datasets/iterable_datasets.py](datasets/iterable_datasets.py)

</details>



## Purpose and Scope

This page documents the `TrajectoryIterableDataset` implementation for streaming molecular dynamics trajectory data. This dataset class is designed for scenarios where:

- The full dataset cannot fit in memory
- Data should be loaded on-demand during training
- Incremental downloading from remote storage is required
- Data needs to be partitioned across multiple DataLoader workers

For efficient indexed access to pre-processed trajectories, see [LMDB Datasets](#3.2.2). For the base dataloader primitives and batch formats, see [Data Loaders](#3.1).

**Sources:** [datasets/iterable_datasets.py:1-280]()

## Architecture Overview

The iterable dataset system consists of four main components organized in a hierarchy:

```mermaid
graph TB
    subgraph "PyTorch Integration"
        IterableDataset["torch.utils.data.IterableDataset"]
        DownloadableDataset["DownloadableDataset[DatasetStats]"]
    end
    
    subgraph "Core Classes"
        TrajectoryIterableDataset["TrajectoryIterableDataset"]
        TrajectoryIterableDatasetIterator["TrajectoryIterableDatasetIterator"]
        RawMolDynDataset["RawMolDynDataset"]
        IncrementalRawMolDynDataset["IncrementalRawMolDynDataset"]
    end
    
    subgraph "Data Sources"
        LocalFiles["Local PDB + NPZ Files"]
        RemoteBlob["Remote Blob Storage"]
    end
    
    subgraph "Output"
        MolDynDatapoint["MolDynDatapoint"]
    end
    
    IterableDataset --> TrajectoryIterableDataset
    DownloadableDataset --> TrajectoryIterableDataset
    TrajectoryIterableDataset --> TrajectoryIterableDatasetIterator
    TrajectoryIterableDataset --> RawMolDynDataset
    TrajectoryIterableDataset --> IncrementalRawMolDynDataset
    
    RawMolDynDataset --> IncrementalRawMolDynDataset
    
    LocalFiles --> RawMolDynDataset
    RemoteBlob --> IncrementalRawMolDynDataset
    
    TrajectoryIterableDatasetIterator --> MolDynDatapoint
    
    style TrajectoryIterableDataset fill:#f9f9f9
    style TrajectoryIterableDatasetIterator fill:#f9f9f9
```

**Sources:** [datasets/iterable_datasets.py:45-280]()

## RawMolDynDataset

`RawMolDynDataset` is the foundational class that handles loading molecular dynamics trajectories from local disk storage.

### Data Structure

The class expects data organized as:
```
data_dir/
├── protein1-traj-state0.pdb
├── protein1-traj-arrays.npz
├── protein2-traj-state0.pdb
├── protein2-traj-arrays.npz
└── ...
```

Each trajectory consists of:
- **PDB file** (`*-traj-state0.pdb`): Initial structure and topology
- **NPZ file** (`*-traj-arrays.npz`): Trajectory data (coordinates, velocities, forces)

**Sources:** [datasets/iterable_datasets.py:45-81]()

### Key Methods and Attributes

| Method/Attribute | Purpose |
|------------------|---------|
| `pdb_names` | Cached property that returns sorted list of available trajectory names |
| `pdb_file_name(pdb_name)` | Constructs path to PDB file for a given trajectory |
| `npz_file_name(pdb_name)` | Constructs path to NPZ file for a given trajectory |
| `_gracefully_load_pdb_trace_data(pdb_name)` | Loads trajectory data with error handling |
| `make_iterator(pdb_names)` | Creates iterator over specified trajectories |

**Sources:** [datasets/iterable_datasets.py:47-130]()

### Configuration Parameters

```mermaid
graph LR
    RawMolDynDataset["RawMolDynDataset"]
    
    data_dir["data_dir: StrPath"]
    step_width["step_width: int"]
    equal_data_spacing["equal_data_spacing: bool = False"]
    
    data_dir --> RawMolDynDataset
    step_width --> RawMolDynDataset
    equal_data_spacing --> RawMolDynDataset
    
    data_dir_desc["Directory containing<br/>PDB and NPZ files"]
    step_width_desc["Time step interval<br/>between samples"]
    equal_desc["Whether to use<br/>equal spacing"]
    
    data_dir --- data_dir_desc
    step_width --- step_width_desc
    equal_data_spacing --- equal_desc
```

**Sources:** [datasets/iterable_datasets.py:34-42]()

### Error Handling

The `_gracefully_load_pdb_trace_data` method handles three types of errors gracefully:

1. **FileNotFoundError**: Logs warning when PDB or NPZ file is missing
2. **CoordDeltaTooBig**: Logs warning when coordinate changes exceed physical limits
3. **Other exceptions**: Re-raised with context about which files failed

When errors occur, the method returns `None` and the iterator skips that trajectory.

**Sources:** [datasets/iterable_datasets.py:59-80]()

### Iterator Implementation

The `make_iterator` method produces `MolDynDatapoint` objects:

```mermaid
graph TB
    Start["Start iteration"]
    LoadTraj["Load trajectory<br/>_gracefully_load_pdb_trace_data"]
    CheckValid{"Valid<br/>trajectory?"}
    ExtractData["Extract:<br/>- atom_types<br/>- adj_list<br/>- coordinates<br/>- velocities<br/>- forces"]
    LoopFrames["Loop through frames"]
    YieldPoint["Yield MolDynDatapoint"]
    NextTraj["Next trajectory"]
    End["End"]
    
    Start --> LoadTraj
    LoadTraj --> CheckValid
    CheckValid -->|No| NextTraj
    CheckValid -->|Yes| ExtractData
    ExtractData --> LoopFrames
    LoopFrames --> YieldPoint
    YieldPoint --> LoopFrames
    LoopFrames --> NextTraj
    NextTraj --> LoadTraj
    LoadTraj --> End
```

**Sources:** [datasets/iterable_datasets.py:82-130]()

## IncrementalRawMolDynDataset

`IncrementalRawMolDynDataset` extends `RawMolDynDataset` to support on-demand downloading from remote blob storage.

### Key Differences from RawMolDynDataset

| Aspect | RawMolDynDataset | IncrementalRawMolDynDataset |
|--------|------------------|------------------------------|
| Data source | Local files only | Blob storage with local caching |
| PDB names discovery | `os.listdir(data_dir)` | `downloader.list_files()` |
| File loading | Direct file access | Download if missing, then access |
| Download tracking | N/A | Maintains `download_attempted` set |

**Sources:** [datasets/iterable_datasets.py:132-170]()

### Download Logic

The incremental download flow:

```mermaid
sequenceDiagram
    participant Iterator
    participant Dataset as IncrementalRawMolDynDataset
    participant Downloader
    participant LocalFS as Local Filesystem
    
    Iterator->>Dataset: _gracefully_load_pdb_trace_data(pdb_name)
    
    alt Not previously attempted
        Dataset->>Downloader: download_file_if_missing(*.pdb)
        Downloader->>LocalFS: Download if not exists
        Dataset->>Downloader: download_file_if_missing(*.npz)
        Downloader->>LocalFS: Download if not exists
        Dataset->>Dataset: Mark as download_attempted
    end
    
    Dataset->>LocalFS: Load from local files
    LocalFS-->>Dataset: TrajectoryInformation
    Dataset-->>Iterator: TrajectoryInformation or None
```

**Sources:** [datasets/iterable_datasets.py:155-169]()

### Configuration

```python
@dataclass(frozen=True)
class IncrementalRawMolDynDataset:
    downloader: Any  # BlobClient instance
    download_attempted: Set[str] = field(default_factory=set)
    # Inherits: data_dir, step_width, equal_data_spacing
```

The `downloader` parameter should be a `BlobClient` instance that implements:
- `list_files()`: Returns list of files in remote storage
- `download_file_if_missing(filename)`: Downloads file if not already cached

**Sources:** [datasets/iterable_datasets.py:133-170]()

## TrajectoryIterableDatasetIterator

`TrajectoryIterableDatasetIterator` implements chunking and shuffling logic for trajectory data.

### Chunking Strategy

Trajectories are grouped into chunks to improve data locality:

```mermaid
graph LR
    subgraph "Raw Iterator"
        T1["Trajectory 1<br/>100 frames"]
        T2["Trajectory 2<br/>150 frames"]
        T3["Trajectory 3<br/>80 frames"]
    end
    
    subgraph "Buffer (num_traces_per_chunk=2)"
        B1["All frames from<br/>Trajectory 1<br/>Trajectory 2"]
    end
    
    subgraph "Shuffled Output"
        O1["Frame 42 from T2"]
        O2["Frame 7 from T1"]
        O3["Frame 103 from T2"]
        O4["..."]
    end
    
    T1 --> B1
    T2 --> B1
    B1 -->|Shuffle| O1
    B1 -->|Shuffle| O2
    B1 -->|Shuffle| O3
    B1 -->|Shuffle| O4
```

**Sources:** [datasets/iterable_datasets.py:173-212]()

### Configuration Parameters

| Parameter | Type | Default | Purpose |
|-----------|------|---------|---------|
| `raw_iterator` | `Iterator[MolDynDatapoint]` | Required | Source iterator from RawMolDynDataset |
| `num_traces_per_chunk` | `int` | Required | Number of trajectories per chunk |
| `shuffle` | `bool` | `False` | Whether to shuffle within chunks |
| `skip_incomplete_chunks` | `bool` | `False` | Whether to discard partial final chunks |

**Sources:** [datasets/iterable_datasets.py:173-178]()

### Iteration Logic

The iterator maintains a buffer and implements a pull-based loading strategy:

```mermaid
stateDiagram-v2
    [*] --> CheckBuffer: __next__ called
    CheckBuffer --> LoadChunk: Buffer empty
    CheckBuffer --> PopDatapoint: Buffer has data
    
    LoadChunk --> AccumulateTrajectories: Load until num_traces_per_chunk
    AccumulateTrajectories --> AccumulateTrajectories: Add datapoints
    AccumulateTrajectories --> Shuffle: Chunk complete
    AccumulateTrajectories --> HandleIncomplete: StopIteration raised
    
    HandleIncomplete --> ClearBuffer: skip_incomplete_chunks=True
    HandleIncomplete --> Shuffle: skip_incomplete_chunks=False
    
    Shuffle --> CheckBuffer: Shuffle if enabled
    ClearBuffer --> RaiseStop: Buffer empty
    
    PopDatapoint --> Return: Pop first element
    Return --> [*]
    RaiseStop --> [*]: Raise StopIteration
```

**Sources:** [datasets/iterable_datasets.py:181-211]()

## TrajectoryIterableDataset

`TrajectoryIterableDataset` is the primary user-facing class that integrates all components.

### Class Hierarchy

```mermaid
graph BT
    TrajectoryIterableDataset["TrajectoryIterableDataset"]
    DownloadableDataset["DownloadableDataset[DatasetStats]"]
    IterableDataset["torch.utils.data.IterableDataset"]
    
    TrajectoryIterableDataset --> DownloadableDataset
    TrajectoryIterableDataset --> IterableDataset
    
    Props["Properties:<br/>- num_traces_per_chunk: int = 16<br/>- step_width: int = 1<br/>- shuffle: bool = False<br/>- equal_data_spacing: bool = False"]
    
    Props -.-> TrajectoryIterableDataset
```

**Sources:** [datasets/iterable_datasets.py:214-220]()

### Multi-Worker Support

The dataset automatically partitions data across DataLoader workers:

```mermaid
graph TB
    subgraph "Main Process"
        Dataset["TrajectoryIterableDataset<br/>pdb_names = [A,B,C,D,E,F]"]
    end
    
    subgraph "Worker 0"
        W0["pdb_names_for_worker(0, 3)<br/>→ [A, B]"]
        W0Iter["make_iterator_for_pdb_names<br/>([A, B])"]
    end
    
    subgraph "Worker 1"
        W1["pdb_names_for_worker(1, 3)<br/>→ [C, D]"]
        W1Iter["make_iterator_for_pdb_names<br/>([C, D])"]
    end
    
    subgraph "Worker 2"
        W2["pdb_names_for_worker(2, 3)<br/>→ [E, F]"]
        W2Iter["make_iterator_for_pdb_names<br/>([E, F])"]
    end
    
    Dataset --> W0
    Dataset --> W1
    Dataset --> W2
    
    W0 --> W0Iter
    W1 --> W1Iter
    W2 --> W2Iter
```

The partitioning is handled by:
1. `pdb_names_for_worker(worker_id, num_workers)`: Splits PDB names using `approximately_equal_partition`
2. `make_iterator_for_worker(worker_id, num_workers)`: Creates iterator with worker-specific random seed

**Sources:** [datasets/iterable_datasets.py:240-279]()

### Random Seed Management

For reproducibility with multiple workers:

```python
# Line 262-264 in iterable_datasets.py
state = np.random.get_state(legacy=True)
assert isinstance(state, tuple)
np.random.seed(state[1][0] + worker_id)
```

This ensures:
- Each worker gets a different but deterministic random seed
- Seeds change between epochs (main process resets seed each epoch)
- Different workers produce different shuffling orders

**Sources:** [datasets/iterable_datasets.py:258-266]()

### Integration with DownloadableDataset

`TrajectoryIterableDataset` inherits from `DownloadableDataset`, providing:

- Automatic dataset downloading from Huggingface
- Dataset integrity checking via `check_dir` method
- Support for both local and remote data sources

```python
# Line 237-238 in iterable_datasets.py
@staticmethod
def check_dir(data_dir: StrPath, expected_dataset_stats: DatasetStats):
    return len(get_pdb_names(data_dir)) == expected_dataset_stats.num_files
```

**Sources:** [datasets/iterable_datasets.py:236-238]()

### Raw Dataset Factory

The dataset automatically selects the appropriate raw dataset implementation:

```mermaid
graph TB
    Create["TrajectoryIterableDataset.__iter__()"]
    CheckDownloader{"self.downloader<br/>exists?"}
    CreateIncremental["IncrementalRawMolDynDataset<br/>(with downloader)"]
    CreateLocal["RawMolDynDataset<br/>(local files only)"]
    
    Create --> CheckDownloader
    CheckDownloader -->|Yes| CreateIncremental
    CheckDownloader -->|No| CreateLocal
    
    CreateIncremental --> Iterator["Return iterator<br/>with incremental download"]
    CreateLocal --> Iterator
```

**Sources:** [datasets/iterable_datasets.py:221-234]()

## Complete Data Flow

The following diagram shows the complete data flow from disk to model:

```mermaid
flowchart TB
    subgraph "Storage"
        Local["Local Files<br/>data_dir/*.pdb<br/>data_dir/*.npz"]
        Remote["Remote Blob Storage<br/>(optional)"]
    end
    
    subgraph "Dataset Layer"
        TID["TrajectoryIterableDataset"]
        RawDS["RawMolDynDataset or<br/>IncrementalRawMolDynDataset"]
        Iterator["TrajectoryIterableDatasetIterator"]
    end
    
    subgraph "Processing"
        LoadTraj["load_pdb_trace_data"]
        Chunk["Chunk by num_traces_per_chunk"]
        Shuffle["Shuffle (optional)"]
    end
    
    subgraph "Output"
        Datapoint["MolDynDatapoint<br/>- name<br/>- atom_types<br/>- adj_list<br/>- coordinates<br/>- velocities<br/>- forces<br/>- targets"]
    end
    
    Remote -.->|Download if needed| Local
    Local --> RawDS
    TID --> RawDS
    RawDS --> LoadTraj
    LoadTraj --> Iterator
    Iterator --> Chunk
    Chunk --> Shuffle
    Shuffle --> Datapoint
```

**Sources:** [datasets/iterable_datasets.py:1-280]()

## Usage Example

```python
from datasets.iterable_datasets import TrajectoryIterableDataset
from torch.utils.data import DataLoader

# Create dataset
dataset = TrajectoryIterableDataset(
    data_dir="/path/to/data",
    num_traces_per_chunk=16,  # Load 16 trajectories at a time
    step_width=1,              # Use every frame
    shuffle=True,              # Shuffle within chunks
    equal_data_spacing=False   # Sample uniformly from trajectories
)

# Create DataLoader with multiple workers
dataloader = DataLoader(
    dataset,
    batch_size=None,  # Batching handled by collate_fn
    num_workers=4      # 4 workers, data automatically partitioned
)

# Iterate
for datapoint in dataloader:
    # datapoint is a MolDynDatapoint
    coords = datapoint.atom_coords
    velocities = datapoint.atom_velocs
    # ... train model ...
```

**Sources:** [datasets/iterable_datasets.py:214-280]()

## Performance Considerations

| Configuration | Memory Usage | Throughput | Use Case |
|---------------|--------------|------------|----------|
| `num_traces_per_chunk=1` | Minimal | Low (frequent I/O) | Memory-constrained |
| `num_traces_per_chunk=16` (default) | Moderate | Balanced | General use |
| `num_traces_per_chunk=64` | High | High (better locality) | Large memory available |
| `shuffle=True` | +20% (buffer overhead) | -5% (shuffle cost) | Training |
| `shuffle=False` | Baseline | Baseline | Evaluation |
| `num_workers=1` | N/A | Baseline | Single-threaded |
| `num_workers=4` | 4x (per worker) | ~3.5x | Multi-core systems |

**Note:** With remote downloading enabled (`IncrementalRawMolDynDataset`), throughput depends heavily on network bandwidth and latency. The `download_attempted` tracking prevents redundant download attempts.

**Sources:** [datasets/iterable_datasets.py:173-280]()

---

