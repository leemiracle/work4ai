<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/bioemu · page 6 Utilities and Helper Functions · fetched 2026-10-26 -->

# Utilities and Helper Functions

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [src/bioemu/seq_io.py](src/bioemu/seq_io.py)
- [src/bioemu/utils.py](src/bioemu/utils.py)
- [tests/test_seq_io.py](tests/test_seq_io.py)
- [tests/test_utils.py](tests/test_utils.py)

</details>



This page documents the utility functions and helper modules in the BioEmu codebase. These utilities provide supporting functionality for the core components of BioEmu, focusing on file management, sequence I/O operations, and environment configuration.

For information about the main workflows and functionality, see [Core Functionality](#3).

## Utility Module Organization

BioEmu includes several dedicated utility modules that provide helper functions used throughout the codebase:

```mermaid
graph TD
    subgraph "Utility Modules"
        utils["utils.py"]
        seq_io["seq_io.py"]
    end

    subgraph "Functionality"
        utils --> |"Provides"| npz["Sample File Management"]
        utils --> |"Provides"| conda["Environment Detection"]
        seq_io --> |"Provides"| fasta["FASTA File Handling"]
        seq_io --> |"Provides"| seq_parse["Sequence Parsing"]
    end

    subgraph "Core Components"
        sample["bioemu.sample"]
        embeds["bioemu.get_embeds"]
        sidechain["bioemu.sidechain_relax"]
    end

    npz -.-> sample
    conda -.-> embeds
    fasta -.-> embeds
    seq_parse -.-> sample
```

Sources: [src/bioemu/utils.py](), [src/bioemu/seq_io.py]()

## Sample Management Utilities

BioEmu includes utilities for managing sampled protein structure files and tracking batches of samples.

### NPZ File Management

The `utils.py` module provides functions for handling NPZ files containing protein structure samples:

```mermaid
flowchart LR
    subgraph "NPZ File Utilities"
        format["format_npz_samples_filename()"]
        count["count_samples_in_output_dir()"]
    end

    input[/"Input: start_id, num_samples"/] --> format
    format --> |"Returns"| filename[/"Formatted filename:\nbatch_0000001_0000010.npz"/]
    
    dir[/"Input: output_dir"/] --> count
    count --> |"Scans files"| parse["Parse batch_*.npz filenames"]
    parse --> |"Extract IDs"| calculate["Calculate sample counts"]
    calculate --> |"Returns"| total[/"Total sample count"/]
```

Sources: [src/bioemu/utils.py:7-22]()

These functions follow specific conventions:

- `format_npz_samples_filename`: Creates standardized filenames for batch sample files using the pattern `batch_{start_id:07d}_{start_id + num_samples:07d}.npz` where IDs are zero-padded to 7 digits.
- `count_samples_in_output_dir`: Counts the total number of samples across all NPZ files in a directory by parsing the numeric portions of filenames.

### Environment Detection

The `get_conda_prefix()` function in `utils.py` helps locate the root Conda folder, which is necessary for certain dependencies:

```mermaid
flowchart TD
    start["get_conda_prefix()"] --> check_root["Check CONDA_ROOT env var"]
    check_root --> has_root{"Exists?"}
    has_root -->|"Yes"| return_root["Return CONDA_ROOT value"]
    
    has_root -->|"No"| check_default["Check CONDA_DEFAULT_ENV"]
    check_default --> is_base{"Is base env?"}
    is_base -->|"Yes"| check_prefix["Get CONDA_PREFIX"]
    is_base -->|"No"| check_prefix1["Get CONDA_PREFIX_1"]
    
    check_prefix --> has_prefix{"Exists?"}
    check_prefix1 --> has_prefix
    
    has_prefix -->|"Yes"| return_prefix["Return prefix value"]
    has_prefix -->|"No"| error["Raise assertion error:\nconda not installed"]
    
    return_root --> finish["Return conda path"]
    return_prefix --> finish
```

Sources: [src/bioemu/utils.py:28-41]()

## Sequence I/O Utilities

The `seq_io.py` module provides utilities for handling protein sequences and FASTA files:

### Sequence Handling Functions

```mermaid
flowchart TD
    subgraph "Public API"
        write_fasta["write_fasta()"]
        read_fasta["read_fasta()"]
        parse_sequence["parse_sequence()"]
    end
    
    subgraph "Helper Functions"
        ensure_records["_ensure_seq_records()"]
    end
    
    subgraph "Input/Output"
        seqs[/"Input: sequences"/]
        path[/"Input: file path"/]
        result[/"Output: sequences"/]
    end
    
    seqs --> write_fasta
    write_fasta --> ensure_records
    ensure_records --> |"Creates directory"| save["Save to FASTA file"]
    
    path --> read_fasta
    read_fasta --> |"Parse FASTA format"| result
    
    input_seq[/"Input: sequence or path"/] --> parse_sequence
    parse_sequence --> is_file{"Is file?"}
    is_file -->|"Yes"| read_fasta
    is_file -->|"No"| return_str["Return as string"]
    read_fasta --> extract["Extract sequence"]
    extract --> result
    return_str --> result
```

Sources: [src/bioemu/seq_io.py:14-52]()

The module provides the following key functionality:

1. **FASTA File Handling**
   - `write_fasta()`: Writes protein sequences to a FASTA file, accepting both raw strings and BioPython `SeqRecord` objects
   - `read_fasta()`: Reads sequences from a FASTA file, returning a list of `SeqRecord` objects

2. **Sequence Parsing**
   - `parse_sequence()`: A versatile function that can extract a protein sequence from:
     - A raw string sequence (returned as-is)
     - A FASTA file path (extracts the first sequence)
     - An a3m file path (extracts the first sequence)
   - Includes error handling for filenames that are too long

3. **Helper Functions**
   - `_ensure_seq_records()`: Internal helper that converts a mixed list of strings and `SeqRecord` objects to a uniform list of `SeqRecord` objects

## Usage in BioEmu Workflows

The utilities are integrated into BioEmu's main workflows in several ways:

```mermaid
flowchart LR
    subgraph "User Input"
        input[/"Amino Acid Sequence\nor FASTA file"/]
    end
    
    subgraph "Sequence Processing"
        parse["parse_sequence()"]
        fasta["write_fasta()"]
    end
    
    subgraph "Sample Generation"
        generate["Generate Samples"]
        format["format_npz_samples_filename()"]
        count["count_samples_in_output_dir()"]
    end
    
    subgraph "Environment Setup"
        conda["get_conda_prefix()"]
        setup["Setup dependencies"]
    end
    
    input --> parse
    parse --> fasta
    fasta --> generate
    
    generate --> format
    format --> save["Save batch samples"]
    
    count --> check["Check completed samples"]
    check --> generate
    
    conda --> setup
    setup --> generate
```

Sources: [src/bioemu/utils.py](), [src/bioemu/seq_io.py]()

## Data Types and Error Handling

### Custom Type Definitions

The codebase defines custom type hints to improve code readability:

```python
StrPath = str | os.PathLike  # Used for file path parameters
```

### Error Handling

The utility functions handle several error cases:

1. **File System Errors**
   - `parse_sequence()` catches `OSError` exceptions that can occur with overly long filenames
   - `write_fasta()` creates parent directories if they don't exist, preventing file write errors

2. **Environment Configuration Errors**
   - `get_conda_prefix()` includes assertions to provide clear error messages when Conda is not properly installed

## Integration with External Libraries

The utility modules integrate with several external libraries:

1. **BioPython**
   - Used in `seq_io.py` for handling FASTA files and sequence records
   - Provides the `SeqRecord` and `Seq` classes for structured sequence representation

2. **Standard Library**
   - `pathlib.Path` for file path handling
   - `os` module for environment variable access and path manipulation

Sources: [src/bioemu/seq_io.py:7-9](), [src/bioemu/utils.py:3-4]()

## Testing

The utility functions are covered by dedicated test modules:

- `tests/test_utils.py`: Tests for NPZ file naming and sample counting
- `tests/test_seq_io.py`: Tests for sequence parsing and FASTA file operations

These tests verify both normal operation and edge cases, such as handling long sequence names and different batch sizes for sample files.

Sources: [tests/test_utils.py](), [tests/test_seq_io.py]()

---

