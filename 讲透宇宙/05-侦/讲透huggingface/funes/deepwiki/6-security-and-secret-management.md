<!-- source: DeepWiki mcp.deepwiki.com · repo huggingface/funes · page 6 Security and Secret Management · fetched 2026-10-26 -->

# Security and Secret Management

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [SECURITY.md](SECURITY.md)
- [docs/RATIONALE.md](docs/RATIONALE.md)
- [docs/demo/cross-agents.tape](docs/demo/cross-agents.tape)
- [docs/hub-caching.md](docs/hub-caching.md)
- [docs/landscape.md](docs/landscape.md)
- [src/scan.rs](src/scan.rs)
- [tests/scrub_drops_all.rs](tests/scrub_drops_all.rs)

</details>



Funes is designed to handle highly sensitive data: the verbatim transcripts of your interactions with AI agents. To protect this data, the system implements a multi-layer security model focused on **local-first processing**, **deterministic redaction**, and **fail-closed secret gates**.

The security architecture ensures that credentials never reach the vector index or the Hugging Face Hub, while maintaining a clear trust boundary between the local memory and third-party models.

### Security Architecture Overview

The following diagram illustrates how security measures are integrated into the data lifecycle, from initial indexing to remote synchronization.

**Security Controls in the Data Pipeline**
```mermaid
graph TD
    subgraph "Local Environment"
        [Raw_Transcript] --> [index_command]
        subgraph "Indexing Pipeline"
            [index_command] --> |"redact_turns"| [SecretScanner_Trait]
            [SecretScanner_Trait] --> [Trufflehog_Impl]
            [Trufflehog_Impl] --> |"excise"| [Redacted_Turns]
        end
        [Redacted_Turns] --> [Lance_Dataset]
        
        subgraph "Egress Gate"
            [push_command] --> |"drop_secret_rows"| [SecretScanner_Trait]
            [SecretScanner_Trait] --> |"Fail-Closed"| [HF_Hub_Upload]
        end
    end

    subgraph "External"
        [HF_Hub_Upload] --> [HF_Dataset_Repo]
        [HF_Dataset_Repo] --> |"recall_hits"| [Agent_Context]
    end

    [scrub_command] -.-> |"Retroactive Cleaning"| [Lance_Dataset]
```
**Sources:** [docs/RATIONALE.md:57-82](), [SECURITY.md:28-39](), [src/scan.rs:1-12]()

---

### Core Security Principles

Funes operates under four load-bearing security and privacy principles:

| Principle | Implementation | Code Reference |
| :--- | :--- | :--- |
| **Local-First** | Embeddings, reranking, and indexing happen entirely on the local machine. | [docs/RATIONALE.md:57-61]() |
| **Fail-Closed** | If the `SecretScanner` (Trufflehog) is missing or errors, indexing and pushing are blocked. | [src/scan.rs:11-11](), [src/scan.rs:48-49]() |
| **Data Ownership** | Remote sync uses standard HF Dataset repos owned and gated by the user's `HF_TOKEN`. | [SECURITY.md:23-24](), [docs/RATIONALE.md:63-69]() |
| **Verbatim Ingest** | No LLM summarizes data during ingest, preventing "hallucinated" or distorted memories. | [docs/RATIONALE.md:36-47]() |

**Sources:** [docs/RATIONALE.md:1-82](), [SECURITY.md:15-27]()

---

### Secret Management Layers

Funes utilizes [Trufflehog](https://github.com/trufflesecurity/trufflehog) via the `SecretScanner` trait to identify and neutralize credentials at three distinct stages.

#### 1. Index-Time Redaction
During the `index` command, the `redact_turns` function scans incoming text. Findings are handled based on their encoding: `PLAIN` findings are redacted in-place using `excise`, while encoded findings (e.g., inside Base64) result in the entire block being dropped to prevent reconstruction.
*For details, see [Secret Redaction and Scrubbing](#6.1).*

#### 2. Push-Time Egress Gate
Before data is uploaded to the Hugging Face Hub, the `push` command runs a final `drop_secret_rows` filter. This acts as a safety net to catch secrets that might have bypassed initial redaction or were introduced via manual dataset manipulation.
*For details, see [Secret Redaction and Scrubbing](#6.1).*

#### 3. Retroactive Scrubbing
The `scrub` command allows users to clean an existing local memory. It performs an atomic overwrite of the Lance dataset, removing any rows where secrets are detected. This is essential if a scanner was previously disabled or if new detection patterns are added to Trufflehog.
*For details, see [Secret Redaction and Scrubbing](#6.1).*

**Sources:** [SECURITY.md:28-39](), [src/scan.rs:22-43](), [tests/scrub_drops_all.rs:66-68]()

---

### Trust Boundaries and Prompt Injection

Funes maintains a strict trust boundary between the **Memory Storage** and the **Model Context**.

**Trust Boundary Diagram**
```mermaid
graph LR
    subgraph "Trusted Zone (Local)"
        [Lance_DB]
        [funes_recall]
    end

    subgraph "Untrusted Zone (Third-Party)"
        [Third_Party_Memory]
    end

    subgraph "Execution Zone"
        [Agent_LLM]
    end

    [Lance_DB] --> |"Verbatim Passages"| [funes_recall]
    [Third_Party_Memory] -.-> |"Potential Injection"| [funes_recall]
    [funes_recall] --> |"Injected Context"| [Agent_LLM]
    
    style [Third_Party_Memory] stroke-dasharray: 5 5
```

When an agent calls `recall`, the returned passages are inserted directly into the prompt. If a user binds a third-party memory (a memory they do not own), there is a risk of **Prompt Injection**. A malicious memory could contain passages designed to hijack the agent's instructions. Funes mitigates this via the `wrong-memory guard` and by encouraging per-call usage for untrusted sources.

*For details, see [Trust Model and Prompt Injection Risks](#6.2).*

**Sources:** [SECURITY.md:49-55](), [docs/RATIONALE.md:78-82]()

---

### Child Pages

*   **[Secret Redaction and Scrubbing](#6.1)**
    Deep dive into the `SecretScanner` implementation, the `Trufflehog` binary discovery via `FUNES_TRUFFLEHOG`, the `excise` logic, and the atomic overwrite mechanics of the `scrub` command.
*   **[Trust Model and Prompt Injection Risks](#6.2)**
    Detailed analysis of security boundaries, the risks associated with third-party memories, and the `require_scanner` check that enforces the fail-closed principle during remote synchronization.

---

