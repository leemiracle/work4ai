<!-- source: DeepWiki mcp.deepwiki.com · repo google-deepmind/narrativeqa · page 4 Utilities and Tools · fetched 2026-10-26 -->

# Utilities and Tools

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [compare.sh](compare.sh)
- [download_stories.sh](download_stories.sh)

</details>



This page documents the scripts and utilities provided for dataset management and validation in the NarrativeQA repository. These tools handle the acquisition of story content from external sources and verification of data integrity.

The utilities are designed to be run as standalone bash scripts and handle the operational aspects of working with the dataset. For detailed technical documentation of individual scripts, see [Content Download Script](#4.1) and [Validation Script](#4.2). For information about the data files these utilities work with, see [Dataset Reference](#3).

## Overview

The NarrativeQA repository provides two primary utility scripts for dataset management:

| Script | Purpose | Input | Output |
|--------|---------|-------|--------|
| `download_stories.sh` | Downloads story content from external URLs | `documents.csv` | Downloaded files in `tmp/` directory |
| `compare.sh` | Validates downloaded file sizes | `documents.csv`, `tmp/` files | Size difference reports |

## Utility Architecture

**Utility Data Flow Pipeline**
```mermaid
graph TD
    documents_csv["documents.csv"]
    download_script["download_stories.sh"]
    tmp_directory["tmp/ directory"]
    compare_script["compare.sh"]
    id_url_csv["id_url.csv"]
    
    documents_csv -->|"parses fields 1,3,4,5"| download_script
    download_script -->|"creates intermediate file"| id_url_csv
    download_script -->|"wget downloads"| tmp_directory
    tmp_directory -->|"stores {id}.content files"| compare_script
    id_url_csv -->|"reads for validation"| compare_script
    
    subgraph tmp_files["Downloaded Content"]
        content_files["{id}.content files"]
        log_files["{id}.log files"]
    end
    
    tmp_directory --> content_files
    tmp_directory --> log_files
```

Sources: [download_stories.sh:20-21](), [download_stories.sh:26](), [compare.sh:29]()

## Script Execution Flow

**Typical Usage Sequence**
```mermaid
sequenceDiagram
    participant User
    participant download_stories_sh as "download_stories.sh"
    participant documents_csv as "documents.csv"
    participant external_sources as "External Sources"
    participant tmp_dir as "tmp/ directory"
    participant compare_sh as "compare.sh"
    
    User->>download_stories_sh: Execute script
    download_stories_sh->>documents_csv: Parse CSV fields
    download_stories_sh->>download_stories_sh: Create id_url.csv
    
    loop "For each document"
        download_stories_sh->>tmp_dir: Check if file exists
        alt "File missing or too small"
            download_stories_sh->>external_sources: wget download
            external_sources-->>download_stories_sh: Return content
            download_stories_sh->>tmp_dir: Save as {id}.content
        end
        alt "Gutenberg source"
            download_stories_sh->>download_stories_sh: Apply 2-second delay
        end
        alt "Gzipped content"
            download_stories_sh->>download_stories_sh: Decompress file
        end
    end
    
    User->>compare_sh: Execute validation
    compare_sh->>documents_csv: Read expected file sizes
    compare_sh->>tmp_dir: Check actual file sizes
    compare_sh-->>User: Report discrepancies
```

Sources: [download_stories.sh:24-49](), [compare.sh:28-43]()

## File Processing Logic

**Download Script Decision Tree**
```mermaid
flowchart TD
    start["Process document ID"]
    check_file["Check if {id}.content exists"]
    check_size["Get file size"]
    size_ok{"Size > 19000 bytes?"}
    file_exists{"File exists?"}
    download["wget download from URL"]
    gutenberg_check{"kind == 'gutenberg'?"}
    sleep_delay["sleep 2 seconds"]
    check_gzip["Check file type"]
    is_gzip{"Gzipped content?"}
    decompress["Move to .gz and gunzip"]
    next_file["Process next file"]
    
    start --> check_file
    check_file --> file_exists
    file_exists -->|"No"| download
    file_exists -->|"Yes"| check_size
    check_size --> size_ok
    size_ok -->|"No"| download
    size_ok -->|"Yes"| next_file
    
    download --> gutenberg_check
    gutenberg_check -->|"Yes"| sleep_delay
    gutenberg_check -->|"No"| check_gzip
    sleep_delay --> check_gzip
    check_gzip --> is_gzip
    is_gzip -->|"Yes"| decompress
    is_gzip -->|"No"| next_file
    decompress --> next_file
```

Sources: [download_stories.sh:27-48]()

## Error Handling and Recovery

The utilities implement several error handling mechanisms:

### Download Script Recovery
- **File existence check**: Verifies files exist before processing [download_stories.sh:27-31]()
- **Size validation**: Re-downloads files smaller than 19,000 bytes [download_stories.sh:35]()
- **Rate limiting**: Applies 2-second delays for Project Gutenberg sources [download_stories.sh:37-39]()
- **Automatic decompression**: Detects and handles gzipped content [download_stories.sh:43-48]()

### Validation Script Output
- **Missing file detection**: Reports files that should exist but don't [compare.sh:30-33]()
- **Size difference calculation**: Computes absolute and percentage differences [compare.sh:39-42]()
- **Sorted reporting**: Orders results by percentage difference for easy review [compare.sh:43]()

## Data Dependencies

**Script Input/Output Relationships**
```mermaid
graph LR
    subgraph inputs["Input Files"]
        documents_csv["documents.csv"]
    end
    
    subgraph processing["Processing Files"]
        id_url_csv["id_url.csv"]
        content_files["tmp/{id}.content"]
        log_files["tmp/{id}.log"]
    end
    
    subgraph outputs["Output Reports"]
        size_reports["Size difference reports"]
        error_logs["Download error logs"]
    end
    
    documents_csv -->|"fields: id,kind,url,file_size"| id_url_csv
    id_url_csv --> content_files
    id_url_csv --> log_files
    content_files --> size_reports
    log_files --> error_logs
    
    documents_csv -.->|"expected sizes"| size_reports
```

Sources: [download_stories.sh:21](), [download_stories.sh:26](), [download_stories.sh:40](), [compare.sh:28-43]()

## Operational Characteristics

### Performance Considerations
- **Sequential processing**: Downloads are processed one at a time to respect rate limits
- **Resume capability**: Script can be re-run safely, only downloading missing or incomplete files
- **Memory efficient**: Processes files individually without loading entire dataset into memory

### Resource Requirements
- **Network access**: Required for downloading external story content
- **Disk space**: Temporary storage needed for ~1,500+ story files
- **Processing time**: Variable depending on network speed and number of missing files

Sources: [download_stories.sh:24-49](), [compare.sh:28-43]()

---

