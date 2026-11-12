<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/boro · page 2 Review Pipeline · fetched 2026-10-26 -->

# Review Pipeline

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [src/main.rs](src/main.rs)

</details>



The review pipeline in `boro` is a multi-stage agentic workflow designed to provide AI-assisted code review for individual commits. It processes commits sequentially, leveraging a series of specialized stages to identify concerns, validate findings, and generate a comprehensive report. This page provides a high-level overview of the pipeline's structure and its key components, with detailed explanations available in linked child pages.

The core of the review process involves dispatching commit tasks to a pool of workers, each operating in an isolated worktree. This ensures that reviews are independent and do not interfere with each other. The pipeline is designed to be robust, with mechanisms for concurrency control, snapshotting, and detailed reporting of token usage and findings.

## Review Pipeline Overview

The `boro review` command [src/main.rs:214]() initiates a multi-stage agentic code review for each commit within a specified range. The pipeline is structured to progressively refine its understanding of a commit, starting with broad discovery and moving to specialized analysis and validation.

The overall flow can be visualized as follows:

```mermaid
graph TD
    subgraph "Commit Review Pipeline"
        A[Commit Range] --> B(Orchestration & Workers);
        B --> C{Worktree Isolation};
        C --> D[Context Assembly & Prefetch];
        D --> E[Specialist Stages (3-8)];
        E --> F[Findings Validation & Adjudication];
        F --> G[Upstream Follow-up (lore & Fixes:)];
        G --> H[Report Generation];
    end

    style A fill:#ace,stroke:#333,stroke-width:2px
    style B fill:#ace,stroke:#333,stroke-width:2px
    style C fill:#ace,stroke:#333,stroke-width:2px
    style D fill:#ace,stroke:#333,stroke-width:2px
    style E fill:#ace,stroke:#333,stroke-width:2px
    style F fill:#ace,stroke:#333,stroke-width:2px
    style G fill:#ace,stroke:#333,stroke-width:2px
    style H fill:#ace,stroke:#333,stroke-width:2px
```
Sources: [src/main.rs:214]()

## Orchestration and Commit Workers

The review process is managed by an orchestration layer that dispatches individual commit review tasks to a pool of workers. This allows for concurrent processing of multiple commits, improving overall efficiency. Each worker operates within an isolated Git worktree [src/worktree.rs](), preventing cross-contamination between commit reviews. Concurrency is controlled by a semaphore [src/main.rs:40](), and the system tracks snapshots and run totals for each commit.

For details, see [Orchestration and Commit Workers](#2.1).

Sources: [src/main.rs:40](), [src/worktree.rs]()

## Context Assembly and Prefetch

Before the specialized review stages begin, `boro` assembles a comprehensive context for each commit. This involves `build_reference_context` [src/prefetch.rs:100](), which narrows down the relevant subsystem in a "phase-0" step [src/prefetch.rs:100-101](). The `prefetch.rs` module [src/prefetch.rs]() is responsible for gathering necessary information, including validating file locations using `diff_index.rs` [src/diff_index.rs](). This stage also handles the identification and filtering of false-positive digests.

For details, see [Context Assembly and Prefetch](#2.4).

Sources: [src/prefetch.rs:100-101](), [src/prefetch.rs](), [src/diff_index.rs]()

## Specialist Stages and Concern Clustering

The core of the review pipeline involves a series of "specialist stages" (stages 3-8) [src/stages.rs](). These stages are designed to focus on specific types of concerns within the commit. Each stage has a defined instruction body that guides the AI model's analysis. A "fast review pass" [src/main.rs:48-51]() can be enabled for quicker initial assessments. To avoid redundant findings, `boro` employs trigram-based deduplication, implemented in `src/cluster.rs` [src/cluster.rs]().

For details, see [Specialist Stages and Concern Clustering](#2.2).

Sources: [src/stages.rs](), [src/main.rs:48-51](), [src/cluster.rs]()

## Findings Validation and Adjudication

After the specialist stages generate potential findings, a critical validation and adjudication process takes place. This involves comparing new findings against a baseline, and then applying a schema of `KEEP`/`TIGHTEN`/`DROP` to refine the results. `boro` supports different validation modes [src/main.rs:102-122]() and applies specific kernel linkage rules to ensure the accuracy and relevance of the findings.

For details, see [Findings Validation and Adjudication](#2.3).

Sources: [src/main.rs:102-122]()

## Upstream Follow-up (lore and Fixes:)

The pipeline also includes a stage for incorporating upstream context and follow-up information. This involves querying `lei` (from the `public-inbox` package) [README.md:157-158]() for relevant discussions and truncating/stripping mbox headers. Additionally, `boro` performs a lookup for `Fixes:` tags in the upstream master branch and renders this information, providing valuable historical context for the commit under review. The `lore` module [src/lore.rs]() handles the processing of this information.

For details, see [Upstream Follow-up (lore and Fixes:)](#2.5).

Sources: [README.md:157-158](), [src/lore.rs]()

---

