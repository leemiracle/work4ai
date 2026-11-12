<!-- source: DeepWiki mcp.deepwiki.com · repo huggingface/funes · page 4 Remote Synchronization (Hugging Face Hub) · fetched 2026-10-26 -->

# Remote Synchronization (Hugging Face Hub)

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docs/push.md](docs/push.md)
- [src/hub.rs](src/hub.rs)
- [src/lib.rs](src/lib.rs)
- [src/main.rs](src/main.rs)

</details>



Funes treats the Hugging Face (HF) Hub as a versioned, append-only object store for distributing agent memory. While `funes` is designed to be local-first, the Hub integration allows users to synchronize their memory across multiple machines, share knowledge with teammates, or consume public memory datasets.

Synchronization is built on the **Lance** dataset format, which `funes` manages via the Hugging Face transport layer. This allows for efficient delta-based updates where only new memory chunks are uploaded or downloaded.

### High-Level Synchronization Flow

The synchronization process bridges the local indexing pipeline with the remote Hub repository. The following diagram illustrates how local code entities interact with the HF Hub:

**Memory Distribution Architecture**
```mermaid
graph TD
    subgraph "Local Environment"
        [Local_Lance_Dataset] --> ["src/commands/push.rs"]
        ["src/commands/push.rs"] -- "calculates delta" --> [Push_Logic]
        [Push_Logic] -- "calls" --> ["src/hub.rs"]
    end

    subgraph "Hugging Face Hub"
        ["src/hub.rs"] -- "HFClient (HTTPS)" --> [HF_Dataset_Repo]
        [HF_Dataset_Repo] -- "hf:// URI" --> [Remote_Memory]
    end

    subgraph "Retrieval"
        ["src/commands/recall.rs"] -- "read-through cache" --> ["src/hub.rs"]
        ["src/hub.rs"] -- "fetch_store" --> [Remote_Memory]
    end
```
**Sources:** [src/lib.rs:15-19](), [src/hub.rs:1-3](), [docs/push.md:3-11]()

---

### Core Concepts

#### The `hf://` URI and Shorthand
Funes identifies remote memories using a specific URI scheme: `hf://datasets/<owner>/<name>[/<prefix>]`. For convenience, the CLI also supports a shorthand `<org>/<repo>` which is automatically expanded.
*   **Parsing Logic:** `parse_hf` decomposes these URIs into owner, repository name, and optional path prefixes [src/hub.rs:17-26]().
*   **Shorthand Detection:** `is_remote_shorthand` identifies strings containing a `/` that do not start with filesystem markers like `.` or `~` [src/hub.rs:11-13]().

#### Hub Transport Layer
The `hub.rs` module serves as the transport abstraction. It handles:
*   **Authentication:** Manages tokens via the `HF_TOKEN` environment variable or the local `huggingface-cli` login cache [src/hub.rs:95-100]().
*   **Repository Lifecycle:** Idempotent creation of private dataset repositories via `create_dataset_repo` [src/hub.rs:73-86]().
*   **Reachability:** Probing whether the Hub is accessible or if the system should degrade to local-only mode [src/hub.rs:30-36]().

For details on the transport implementation, see [Hub Transport and Remote Memory](#4.2).

**Sources:** [src/hub.rs:1-118](), [src/lib.rs:15-16]()

---

### The Push Pipeline

The `push` command is the primary mechanism for distributing memory. It is designed to be safe, incremental, and "fail-closed" regarding sensitive data.

**Push Logic and Secret Gate**
```mermaid
graph LR
    [Local_Chunks] --> [Delta_Calc]
    [Delta_Calc] -- "local_ids - remote_ids" --> [Pending_Rows]
    [Pending_Rows] --> ["SecretScanner (Trufflehog)"]
    ["SecretScanner (Trufflehog)"] -- "Clean" --> [HF_Upload]
    ["SecretScanner (Trufflehog)"] -- "Sensitive Found" --> [Hold_Back_Warning]
    [HF_Upload] --> [Update_README_md]
```
**Sources:** [docs/push.md:46-58](), [src/commands/push.rs]()

#### Key Features of the Pipeline:
1.  **Delta Calculation:** Funes only uploads chunks that do not exist on the remote, minimizing bandwidth [docs/push.md:15-16]().
2.  **The Secret Gate:** An egress filter that uses Trufflehog to scan rows before they leave the machine. It reconstructs full blocks to ensure secrets split across chunks are detected [docs/push.md:46-51]().
3.  **Wrong-Memory Guard:** A safety check that prevents pushing to a repository that shares no history with the local index, protecting against accidental overwrites [docs/push.md:28-31]().
4.  **Dataset Cards:** Funes automatically generates and updates `README.md` files on the Hub, providing live statistics and usage instructions [docs/push.md:18-22]().

For details on the push mechanics, see [Push Pipeline](#4.1).

**Sources:** [docs/push.md:13-67](), [src/main.rs:83-103]()

---

### Remote Memory Retrieval

Remote memories are not "downloaded" in the traditional sense. Instead, funes uses a read-through cache mechanism:
*   **Lazy Loading:** The `recall` command can target a remote memory via the `--memory` flag [src/main.rs:55]().
*   **Object Store Wrappers:** The `fetch_store` and `capture_store` wrappers in the memory layer allow Lance to treat the HF Hub as a backing filesystem [src/lib.rs:17-18]().
*   **Offline Resilience:** If the Hub is unreachable, funes can automatically fall back to the local index if a copy exists [src/hub.rs:28-36]().

**Sources:** [src/lib.rs:15-19](), [src/hub.rs:28-36](), [docs/push.md:9-11]()

---

