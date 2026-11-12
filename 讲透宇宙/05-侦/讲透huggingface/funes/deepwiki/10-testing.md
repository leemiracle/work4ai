<!-- source: DeepWiki mcp.deepwiki.com · repo huggingface/funes · page 10 Testing · fetched 2026-10-26 -->

# Testing

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [tests/index_recall.rs](tests/index_recall.rs)
- [tests/reindex_incremental.rs](tests/reindex_incremental.rs)
- [tests/remote_recall.rs](tests/remote_recall.rs)
- [tests/remove.rs](tests/remove.rs)
- [tests/support/mod.rs](tests/support/mod.rs)

</details>



The `funes` test suite is designed to ensure the integrity of the agent-memory contract, the security of the data synchronization pipeline, and the correctness of the hybrid retrieval system. It spans unit tests for core logic, fixture-based integration tests using real model weights, and gated remote tests against the Hugging Face Hub.

### Test Strategy Overview

The testing architecture prioritizes end-to-end correctness by executing the real `BGE` embedder and `Lance` indexing pipeline against temporary environments.

| Test Category | Description | Primary Location |
|:---|:---|:---|
| **Unit Tests** | Logic verification for chunking, CIDs, and parsing. | `src/` (inline) |
| **Integration Tests** | E2E flows: Index → Recall, Push → Pull, Hook Installation. | `tests/*.rs` |
| **Fixture Tests** | Validating parsers against static session snapshots. | `tests/parse_real_sessions.rs` |
| **Remote Tests** | Gated tests requiring `HF_FUNES_TEST_TOKEN` for Hub sync. | `tests/remote_recall.rs` |

---

### Test Environment and Support

Integration tests utilize a `support` module to isolate the execution environment. This includes creating `fake_cli` binaries to intercept calls to agent CLIs (like `claude` or `codex`) and redirecting `$FUNES_HOME` to temporary directories to prevent interference with local developer setups.

**Test Support Flow**
```mermaid
graph TD
    subgraph "Test Execution"
        [test_runner] --> [tempfile::tempdir]
        [tempfile::tempdir] --> [ENV: FUNES_HOME]
        [test_runner] --> [support::fake_cli]
        [support::fake_cli] --> [ENV: PATH]
    end

    subgraph "Verification"
        [funes_binary] -- "executes" --> [fake_cli]
        [fake_cli] -- "logs to" --> [cli.log]
        [test_runner] -- "asserts" --> [cli.log]
    end
```
Sources: [tests/support/mod.rs:6-30](), [tests/index_recall.rs:29-33](), [tests/remove.rs:11-21]()

---

### Integration Tests: Indexing and Recall

These tests verify the core "read surface" of `funes`. They ensure that when a transcript is indexed, the resulting `Lance` dataset can be queried via vector search and full-text search (FTS), and that session provenance (e.g., `workdir`, `session_id`) is preserved.

*   **`index_recall.rs`**: Exercises `run_index` [tests/index_recall.rs:36-38]() followed by `recall`, `scan`, `sessions`, and `status`. It verifies that type filters (e.g., `tool_use`) correctly restrict results [tests/index_recall.rs:70-82]().
*   **`reindex_incremental.rs`**: Ensures that appending turns to an existing session and re-indexing converges to the same state as indexing from scratch, preventing data duplication [tests/reindex_incremental.rs:32-68]().
*   **`remote_recall.rs`**: A gated test that opens a stable fixture on the HF Hub using `hf://` and performs a hybrid recall to find a `UNIQUEMARKERXYZZY` [tests/remote_recall.rs:11-52]().

For details, see [Integration Tests: Indexing and Recall](#10.1).

---

### Integration Tests: Push and Remote

These tests cover the synchronization lifecycle between local memory and the Hugging Face Hub. They focus on the delta calculation (local vs. remote IDs) and the integrity of the `Dataset Card` (README.md).

*   **`push_round_trip.rs`**: Validates the full flow of creating a remote repository, pushing initial chunks, and appending new ones.
*   **`store_lock.rs`**: Tests the `MemoryLock` concurrency model to ensure multiple processes don't corrupt the local Lance dataset during synchronization.
*   **`push_card.rs`**: Verifies that the metadata in the `README.md` on the Hub correctly reflects the memory's provenance and harness types.

For details, see [Integration Tests: Push and Remote](#10.2).

---

### Integration Tests: Security and Agent Hooks

Security tests verify the "Secret Gate" and redaction capabilities, while hook tests ensure that `funes` can correctly inject itself into various agent environments without breaking existing user configurations.

*   **Secret Detection**: Tests like `redact_on_index` and `scrub_drops_all` verify that `Trufflehog` integration correctly identifies and removes sensitive keys during both indexing and the `scrub` command.
*   **Agent Integration**: Tests in `remove.rs` and `add_*.rs` verify that installing or removing `funes` from agents like Claude, Codex, or Hermes is idempotent and preserves unrelated user hooks [tests/remove.rs:39-83]().

**Agent Hook Verification**
```mermaid
graph LR
    subgraph "Agent Config Space"
        [hooks.json]
        [config.yaml]
        [shell-hooks-allowlist.json]
    end

    subgraph "Code Entities"
        [funes::agents::claude]
        [funes::agents::codex]
        [funes::agents::hermes]
    end

    [tests/remove.rs] -- "verifies removal of" --> [funes-index.sh]
    [tests/remove.rs] -- "verifies removal of" --> [funes-push.sh]
    [funes::agents::hermes] -- "modifies" --> [config.yaml]
    [funes::agents::codex] -- "modifies" --> [hooks.json]
```
Sources: [tests/remove.rs:98-121](), [tests/remove.rs:51-66](), [tests/remove.rs:1-3]()

For details, see [Integration Tests: Security and Agent Hooks](#10.3).

---

