<!-- source: DeepWiki mcp.deepwiki.com · repo huggingface/hf_transfer · page 3 Core API · fetched 2026-10-26 -->

# Core API

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [src/lib.rs](src/lib.rs)

</details>



This page provides a comprehensive overview of the primary functions exposed by the hf_transfer library. The Core API consists of two main functions that enable high-performance file transfers through parallel processing and robust error handling.

For information about the overall architecture of hf_transfer, see [Architecture](#2).

## Overview of Core Functions

The hf_transfer library exposes two primary Python functions for file transfer operations:

1. `download`: High-performance parallel download of files from remote sources
2. `multipart_upload`: Efficient chunked upload to remote storage services

Both functions leverage Rust's performance capabilities and Tokio's asynchronous runtime to significantly improve transfer speeds compared to traditional Python implementations.

```mermaid
graph TD
    subgraph "Python API Layer"
        download["download()"]
        multipart_upload["multipart_upload()"]
    end
    
    subgraph "Internal Rust Implementation"
        download_async["download_async()"]
        upload_async["upload_async()"]
        download_chunk["download_chunk()"]
        upload_chunk["upload_chunk()"]
        exponential_backoff["exponential_backoff()"]
    end
    
    download --> download_async
    multipart_upload --> upload_async
    
    download_async --> download_chunk
    download_async --> exponential_backoff
    upload_async --> upload_chunk
    upload_async --> exponential_backoff
```

Sources: [src/lib.rs:35-140](). [src/lib.rs:363-450]()

## Function: download

The `download` function enables efficient downloading of files by splitting the download into multiple chunks processed in parallel.

### Signature

```python
def download(
    url: str,
    filename: str,
    max_files: int,
    chunk_size: int,
    parallel_failures: int = 0,
    max_retries: int = 0,
    headers: Optional[Dict[str, str]] = None,
    callback: Optional[Callable[[int], None]] = None
) -> None
```

### Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `url` | `str` | The URL of the file to download |
| `filename` | `str` | Local path where the file should be saved |
| `max_files` | `int` | Maximum number of open file handles, determining the maximum parallelism |
| `chunk_size` | `int` | Size of each download chunk in bytes |
| `parallel_failures` | `int` | Maximum number of chunk failures allowed in parallel (must be ≤ `max_files`) |
| `max_retries` | `int` | Maximum number of retry attempts per chunk |
| `headers` | `Optional[Dict[str, str]]` | Optional HTTP headers to include in requests |
| `callback` | `Optional[Callable[[int], None]]` | Optional callback function called with bytes transferred |

### Implementation Details

The function operates by:

1. Creating a multi-threaded Tokio runtime
2. Determining the file size via a range request
3. Splitting the download into chunks based on the specified `chunk_size`
4. Creating a semaphore to limit concurrent downloads to `max_files`
5. Spawning tasks for each chunk that download and write to the target file
6. Implementing retry logic with exponential backoff if specified

```mermaid
sequenceDiagram
    participant "Python" as P
    participant "download()" as D
    participant "download_async()" as DA
    participant "download_chunk()" as DC
    participant "Remote Server" as S
    participant "Local File" as F
    
    P->>+D: Call with url, filename, params
    D->>+DA: Execute in Tokio runtime
    DA->>S: HEAD request to get file size
    S-->>DA: Return content length
    
    DA->>DA: Calculate chunks
    
    par Chunks processed in parallel
        DA->>+DC: Process chunk 1
        DC->>S: Request range for chunk 1
        S-->>DC: Return chunk 1 data
        DC->>F: Write chunk 1 to file
        DC-->>-DA: Return success/error
        
        DA->>+DC: Process chunk 2
        DC->>S: Request range for chunk 2
        S-->>DC: Return chunk 2 data
        DC->>F: Write chunk 2 to file
        DC-->>-DA: Return success/error
        
        DA->>+DC: Process chunk N
        DC->>S: Request range for chunk N
        S-->>DC: Return chunk N data
        DC->>F: Write chunk N to file
        DC-->>-DA: Return success/error
    end
    
    alt Chunk error occurs
        DA->>DA: Apply exponential backoff
        DA->>+DC: Retry chunk
        DC-->>-DA: Return success/error
    end
    
    DA-->>-D: Return overall result
    D-->>-P: Return success or raise exception
```

Sources: [src/lib.rs:36-88](), [src/lib.rs:151-295](), [src/lib.rs:334-361]()

## Function: multipart_upload

The `multipart_upload` function enables efficient uploads by splitting the file into chunks and uploading them in parallel.

### Signature

```python
def multipart_upload(
    file_path: str,
    parts_urls: List[str],
    chunk_size: int,
    max_files: int,
    parallel_failures: int = 0,
    max_retries: int = 0,
    callback: Optional[Callable[[int], None]] = None
) -> List[Dict[str, str]]
```

### Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `file_path` | `str` | Path to the local file to upload |
| `parts_urls` | `List[str]` | List of pre-signed URLs for each part of the multipart upload |
| `chunk_size` | `int` | Size of each upload chunk in bytes |
| `max_files` | `int` | Maximum number of open file handles, determining the maximum parallelism |
| `parallel_failures` | `int` | Maximum number of chunk failures allowed in parallel (must be ≤ `max_files`) |
| `max_retries` | `int` | Maximum number of retry attempts per chunk |
| `callback` | `Optional[Callable[[int], None]]` | Optional callback function called with bytes transferred |

### Return Value

List of dictionaries containing the HTTP response headers from each part upload, used for completing multipart uploads.

### Implementation Details

The function operates by:

1. Creating a multi-threaded Tokio runtime
2. Splitting the file into chunks of `chunk_size` bytes
3. Creating a semaphore to limit concurrent uploads to `max_files`
4. Spawning tasks for each chunk that read from the file and upload to the corresponding pre-signed URL
5. Implementing retry logic with exponential backoff if specified
6. Collecting headers from the responses to each part upload

```mermaid
sequenceDiagram
    participant "Python" as P
    participant "multipart_upload()" as MU
    participant "upload_async()" as UA
    participant "upload_chunk()" as UC
    participant "Local File" as F
    participant "Remote Server" as S
    
    P->>+MU: Call with file_path, part_urls, params
    MU->>+UA: Execute in Tokio runtime
    
    par Chunks processed in parallel
        UA->>+UC: Process part 1
        UC->>F: Read chunk 1
        F-->>UC: Return chunk 1 data
        UC->>S: Upload chunk 1
        S-->>UC: Return response headers
        UC-->>-UA: Return headers/error
        
        UA->>+UC: Process part 2
        UC->>F: Read chunk 2
        F-->>UC: Return chunk 2 data
        UC->>S: Upload chunk 2
        S-->>UC: Return response headers
        UC-->>-UA: Return headers/error
        
        UA->>+UC: Process part N
        UC->>F: Read chunk N
        F-->>UC: Return chunk N data
        UC->>S: Upload chunk N
        S-->>UC: Return response headers
        UC-->>-UA: Return headers/error
    end
    
    alt Chunk error occurs
        UA->>UA: Apply exponential backoff
        UA->>+UC: Retry chunk
        UC-->>-UA: Return headers/error
    end
    
    UA->>UA: Collect response headers
    UA-->>-MU: Return headers array
    MU-->>-P: Return headers or raise exception
```

Sources: [src/lib.rs:101-140](), [src/lib.rs:363-450](), [src/lib.rs:452-482]()

## Error Handling and Retry Mechanism

Both `download` and `multipart_upload` implement robust error handling with an exponential backoff retry mechanism. This makes transfers resilient to transient network issues.

### Retry Configuration

To enable the retry mechanism, both `parallel_failures` and `max_retries` must be set:

- `parallel_failures`: Limits how many chunks can be in a failed/retrying state simultaneously
- `max_retries`: Maximum number of retry attempts before failing the entire operation

### Exponential Backoff Implementation

The retry mechanism uses an exponential backoff strategy with jitter to avoid thundering herd problems:

```mermaid
graph TD
    subgraph "Retry Logic"
        failure["Chunk Transfer Failure"]
        check_max_retries["Check if max_retries reached"]
        check_parallel["Check parallel_failures limit"]
        backoff["Calculate backoff with jitter"]
        wait["Sleep for calculated duration"]
        retry["Retry chunk transfer"]
        fail["Fail with error"]
    end
    
    failure --> check_max_retries
    check_max_retries -->|"retry count >= max_retries"| fail
    check_max_retries -->|"retry count < max_retries"| check_parallel
    
    check_parallel -->|"limit reached"| fail
    check_parallel -->|"under limit"| backoff
    
    backoff --> wait
    wait --> retry
    retry -->|"success"| success["Continue"]
    retry -->|"failure"| failure
```

The backoff duration is calculated using this formula:
```
wait_time = (BASE_WAIT_TIME + retry_count² + random_jitter(0-500ms)).min(MAX_WAIT_TIME)
```

Where:
- `BASE_WAIT_TIME` = 300ms
- `MAX_WAIT_TIME` = 10,000ms (10 seconds)

This provides a balance between quick retries for transient failures and avoiding overwhelming the server with retry requests.

Sources: [src/lib.rs:26-28](), [src/lib.rs:142-148](), [src/lib.rs:248-270](), [src/lib.rs:393-416]()

## Thread Control

The number of worker threads used by the Tokio runtime can be tuned by setting the `TOKIO_WORKER_THREADS` environment variable. This allows for fine-grained control over the parallelism model based on the specific environment where hf_transfer is running.

Sources: [src/lib.rs:33-34](), [src/lib.rs:59-62](), [src/lib.rs:125-128]()

## Integration with Python

Both API functions are exposed to Python using PyO3 bindings. They are registered with the Python module in the `pymodule` declaration at [src/lib.rs:484-491]().

For information on how to use these functions with the huggingface_hub library, see [Integration with huggingface_hub](#4.1).

---

