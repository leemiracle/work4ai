<!-- source: DeepWiki mcp.deepwiki.com · repo obra/superpowers · extra page SDD Helper Scripts · fetched 2026-10-26 -->

# SDD Helper Scripts

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docs/superpowers/specs/2026-07-06-sdd-plan-scoped-workspace.md](docs/superpowers/specs/2026-07-06-sdd-plan-scoped-workspace.md)
- [skills/subagent-driven-development/scripts/review-package](skills/subagent-driven-development/scripts/review-package)
- [skills/subagent-driven-development/scripts/sdd-workspace](skills/subagent-driven-development/scripts/sdd-workspace)
- [skills/subagent-driven-development/scripts/task-brief](skills/subagent-driven-development/scripts/task-brief)
- [tests/claude-code/test-sdd-workspace.sh](tests/claude-code/test-sdd-workspace.sh)

</details>



This page provides a detailed reference for the helper scripts used in the Subagent-Driven Development (SDD) workflow: `sdd-workspace`, `task-brief`, and `review-package`. It also describes the `.superpowers/sdd` workspace layout and the tests that validate these components. These scripts are crucial for managing the lifecycle of SDD artifacts, ensuring proper isolation between different development plans, and facilitating the review process.

Sources:
- [docs/superpowers/specs/2026-07-06-sdd-plan-scoped-workspace.md:1-139]()

## SDD Workspace Layout

The SDD workflow utilizes a plan-scoped workspace to store temporary artifacts generated during the development process. This workspace is located at `.superpowers/sdd/` within the repository root. To prevent collisions and ensure isolation, each development plan gets its own dedicated subdirectory within `.superpowers/sdd/`.

The structure is as follows:
```
<repo-root>/
├── .superpowers/
│   └── sdd/
│       ├── .gitignore  (self-ignoring, contains only '*')
│       ├── <plan-slug-A>/
│       │   ├── plan-path  (marker file containing the plan's path)
│       │   ├── progress.md
│       │   ├── task-1-brief.md
│       │   ├── task-1-report.md
│       │   └── review-<base7>..<head7>.diff
│       └── <plan-slug-B>/
│           ├── plan-path
│           └── ...
└── <plan-file-A>.md
└── <plan-file-B>.md
```

The `.gitignore` file at `.superpowers/sdd/.gitignore` contains a single `*` character [skills/subagent-driven-development/scripts/sdd-workspace:81](), making the entire `.superpowers/sdd` directory invisible to `git status` and `git add -A` [tests/claude-code/test-sdd-workspace.sh:101-119](). This prevents accidental commits of temporary SDD artifacts.

Each plan's workspace directory, e.g., `<plan-slug-A>`, contains a `plan-path` marker file [skills/subagent-driven-development/scripts/sdd-workspace:62-67]() that stores the canonical path of the plan file it belongs to. This mechanism helps disambiguate plan slugs if multiple plans share the same basename (e.g., `docs/alpha/plan.md` and `docs/beta/plan.md`) [skills/subagent-driven-development/scripts/sdd-workspace:12-19]().

Sources:
- [docs/superpowers/specs/2026-07-06-sdd-plan-scoped-workspace.md:48-55]()
- [skills/subagent-driven-development/scripts/sdd-workspace:12-19]()
- [skills/subagent-driven-development/scripts/sdd-workspace:24-25]()
- [skills/subagent-driven-development/scripts/sdd-workspace:62-67]()
- [skills/subagent-driven-development/scripts/sdd-workspace:81]()
- [tests/claude-code/test-sdd-workspace.sh:101-119]()

## `sdd-workspace` Script

The `sdd-workspace` script [skills/subagent-driven-development/scripts/sdd-workspace]() is responsible for resolving and ensuring the existence of the plan-scoped workspace directory. It prints the absolute path of the plan's workspace directory to standard output.

### Usage
`sdd-workspace PLAN_FILE` [skills/subagent-driven-development/scripts/sdd-workspace:30]()

### Arguments
- `PLAN_FILE`: The path to the implementation plan file (e.g., `plan-a.md`).

### Implementation Details

The script performs the following steps:
1. **Argument Validation**: Checks if exactly one argument (`PLAN_FILE`) is provided and if the file exists [skills/subagent-driven-development/scripts/sdd-workspace:33-39]().
2. **Slug Generation**: Extracts a "slug" from the `PLAN_FILE` by taking its basename and removing the `.md` extension [skills/subagent-driven-development/scripts/sdd-workspace:41]().
3. **Repository Root Determination**: Uses `git rev-parse --show-toplevel` to find the absolute path of the Git repository root [skills/subagent-driven-development/scripts/sdd-workspace:45]().
4. **Plan Path Normalization**: Normalizes the `PLAN_FILE` path to a canonical form. If the plan is within the repository, it's stored as a repo-relative path; otherwise, it's an absolute path. This normalized path is used as the `plan_id` [skills/subagent-driven-development/scripts/sdd-workspace:50-56]().
5. **Workspace Directory Resolution**:
    - It first attempts to use `$base/$slug` as the workspace directory [skills/subagent-driven-development/scripts/sdd-workspace:70]().
    - The `owns()` function [skills/subagent-driven-development/scripts/sdd-workspace:60-67]() checks if a given directory is owned by the current plan. A directory is owned if:
        - It contains a `plan-path` file whose content matches the current `plan_id`.
        - It does not contain a `plan-path` file (in which case it's claimed by writing the `plan_id` into a new `plan-path` file).
    - If the initial slug-based directory is not owned by the current plan, it attempts to disambiguate by appending the parent directory name of the plan file (e.g., `$base/$slug-$parent`) [skills/subagent-driven-development/scripts/sdd-workspace:71-72]().
    - If still not owned, it further disambiguates by appending a counter (e.g., `$base/$slug-$parent-2`, `$base/$slug-$parent-3`, etc.) [skills/subagent-driven-development/scripts/sdd-workspace:73-76]().
6. **`.gitignore` Creation**: Ensures a `.gitignore` file exists at `.superpowers/sdd/.gitignore` with content `*` to ignore all contents of the SDD workspace from Git [skills/subagent-driven-development/scripts/sdd-workspace:81]().
7. **Output**: Prints the absolute path of the resolved workspace directory [skills/subagent-driven-development/scripts/sdd-workspace:82]().

### `sdd-workspace` Data Flow
```mermaid
graph TD
    A[Call sdd-workspace PLAN_FILE] --> B{Validate PLAN_FILE};
    B -- Valid --> C[Extract slug from PLAN_FILE];
    B -- Invalid --> E[Exit 2: Usage Error];
    C --> D[Get Git Repo Root];
    D --> F[Normalize PLAN_FILE path to plan_id];
    F --> G[Attempt workspace dir: $base/$slug];
    G --> H{Call owns($dir)};
    H -- Owned --> I[Ensure .gitignore at .superpowers/sdd/];
    H -- Not Owned --> J[Attempt workspace dir: $base/$slug-$parent];
    J --> K{Call owns($dir)};
    K -- Not Owned --> L[Attempt workspace dir: $base/$slug-$parent-$n (loop)];
    L -- Owned --> I;
    K -- Owned --> I;
    I --> M[Print absolute path of resolved workspace dir];
```

Sources:
- [skills/subagent-driven-development/scripts/sdd-workspace:33-39]()
- [skills/subagent-driven-development/scripts/sdd-workspace:41]()
- [skills/subagent-driven-development/scripts/sdd-workspace:45]()
- [skills/subagent-driven-development/scripts/sdd-workspace:50-56]()
- [skills/subagent-driven-development/scripts/sdd-workspace:60-67]()
- [skills/subagent-driven-development/scripts/sdd-workspace:70]()
- [skills/subagent-driven-development/scripts/sdd-workspace:71-72]()
- [skills/subagent-driven-development/scripts/sdd-workspace:73-76]()
- [skills/subagent-driven-development/scripts/sdd-workspace:81]()
- [skills/subagent-driven-development/scripts/sdd-workspace:82]()

## `task-brief` Script

The `task-brief` script [skills/subagent-driven-development/scripts/task-brief]() extracts the full text of a specific task from an implementation plan and writes it to a file within the plan's SDD workspace. This allows the implementer subagent to read the task brief directly without needing it to be passed through the controller's context.

### Usage
`task-brief PLAN_FILE TASK_NUMBER [OUTFILE]` [skills/subagent-driven-development/scripts/task-brief:12]()

### Arguments
- `PLAN_FILE`: The path to the implementation plan file.
- `TASK_NUMBER`: The number of the task to extract.
- `OUTFILE` (optional): The path to write the task brief. If not provided, it defaults to `<repo-root>/.superpowers/sdd/<plan-basename>/task-<N>-brief.md` [skills/subagent-driven-development/scripts/task-brief:27]().

### Implementation Details

The script performs the following steps:
1. **Argument Validation**: Checks if `PLAN_FILE` and `TASK_NUMBER` are provided and if `PLAN_FILE` exists [skills/subagent-driven-development/scripts/task-brief:14-19]().
2. **Output File Determination**:
    - If `OUTFILE` is provided, it uses that path [skills/subagent-driven-development/scripts/task-brief:21-22]().
    - Otherwise, it calls `sdd-workspace` to get the plan's workspace directory and constructs the default output path: `$dir/task-${n}-brief.md` [skills/subagent-driven-development/scripts/task-brief:24-27]().
3. **Task Extraction**: Uses `awk` to parse the `PLAN_FILE`. It identifies task headings (e.g., `## Task 1: ...`) and extracts all lines belonging to the specified `TASK_NUMBER`, respecting code fences (` ``` `) [skills/subagent-driven-development/scripts/task-brief:30-36]().
4. **Output Validation**: Checks if the extracted `OUTFILE` is non-empty. If the task is not found, it prints an error and exits with code 3 [skills/subagent-driven-development/scripts/task-brief:38-41]().
5. **Confirmation**: Prints the path of the written file and the number of lines [skills/subagent-driven-development/scripts/task-brief:43]().

### `task-brief` Data Flow
```mermaid
graph TD
    A[Call task-brief PLAN_FILE TASK_NUMBER [OUTFILE]] --> B{Validate Arguments};
    B -- Valid --> C{OUTFILE provided?};
    C -- Yes --> D[Set OUTFILE to provided path];
    C -- No --> E[Call sdd-workspace PLAN_FILE];
    E --> F[Construct default OUTFILE path: $dir/task-$N-brief.md];
    D --> G[Extract Task N from PLAN_FILE using awk];
    F --> G;
    G --> H[Write extracted content to OUTFILE];
    H --> I{Check if OUTFILE is empty};
    I -- Empty --> J[Exit 3: Task not found];
    I -- Not Empty --> K[Print confirmation message];
```

Sources:
- [skills/subagent-driven-development/scripts/task-brief:12]()
- [skills/subagent-driven-development/scripts/task-brief:14-19]()
- [skills/subagent-driven-development/scripts/task-brief:21-22]()
- [skills/subagent-driven-development/scripts/task-brief:24-27]()
- [skills/subagent-driven-development/scripts/task-brief:30-36]()
- [skills/subagent-driven-development/scripts/task-brief:38-41]()
- [skills/subagent-driven-development/scripts/task-brief:43]()

## `review-package` Script

The `review-package` script [skills/subagent-driven-development/scripts/review-package]() generates a comprehensive review package for a given Git commit range. This package includes a commit list, a file statistics summary, and a detailed diff, all written to a file within the plan's SDD workspace. This ensures the reviewer has all necessary information in one place.

### Usage
`review-package PLAN_FILE BASE HEAD [OUTFILE]` [skills/subagent-driven-development/scripts/review-package:13]()

### Arguments
- `PLAN_FILE`: The path to the implementation plan file. This is a new mandatory argument to ensure plan-scoped workspace usage [docs/superpowers/specs/2026-07-06-sdd-plan-scoped-workspace.md:66]().
- `BASE`: The Git reference for the base of the commit range (e.g., `HEAD~1`).
- `HEAD`: The Git reference for the head of the commit range (e.g., `HEAD`).
- `OUTFILE` (optional): The path to write the review package. If not provided, it defaults to `<repo-root>/.superpowers/sdd/<plan-basename>/review-<base7>..<head7>.diff` [skills/subagent-driven-development/scripts/review-package:8]().

### Implementation Details

The script performs the following steps:
1. **Argument Validation**: Checks if 3 or 4 arguments are provided and if `PLAN_FILE` exists [skills/subagent-driven-development/scripts/review-package:12-20](). It also validates `BASE` and `HEAD` as valid Git references [skills/subagent-driven-development/scripts/review-package:22-23]().
2. **Range Guards**:
    - Verifies that `BASE` is an ancestor of `HEAD` using `git merge-base --is-ancestor` [skills/subagent-driven-development/scripts/review-package:27](). If not, it exits with code 3.
    - Checks that the commit range `BASE..HEAD` is not empty using `git rev-list --count` [skills/subagent-driven-development/scripts/review-package:28](). If empty, it exits with code 3.
3. **Output File Determination**:
    - If `OUTFILE` is provided, it uses that path [skills/subagent-driven-development/scripts/review-package:30-31]().
    - Otherwise, it calls `sdd-workspace` to get the plan's workspace directory and constructs the default output path: `$dir/review-$(git rev-parse --short "$base")..$(git rev-parse --short "$head").diff` [skills/subagent-driven-development/scripts/review-package:33-36](). The filename includes short hashes of `BASE` and `HEAD` to ensure distinct files for re-reviews [skills/subagent-driven-development/scripts/review-package:8-9]().
4. **Package Generation**:
    - Writes a header indicating the commit range [skills/subagent-driven-development/scripts/review-package:40-41]().
    - Appends a list of commits using `git log --oneline` [skills/subagent-driven-development/scripts/review-package:43]().
    - Appends a file change statistics summary using `git diff --stat` [skills/subagent-driven-development/scripts/review-package:46]().
    - Appends the detailed diff with 10 lines of context using `git diff -U10` [skills/subagent-driven-development/scripts/review-package:49]().
    - All output is redirected to the determined `OUTFILE` [skills/subagent-driven-development/scripts/review-package:50]().
5. **Confirmation**: Prints the path of the written file, the number of commits, and the file size [skills/subagent-driven-development/scripts/review-package:52-53]().

### `review-package` Data Flow
```mermaid
graph TD
    A[Call review-package PLAN_FILE BASE HEAD [OUTFILE]] --> B{Validate Arguments};
    B -- Valid --> C{Validate Git Refs BASE, HEAD};
    C -- Valid --> D{Check BASE is ancestor of HEAD};
    D -- Not Ancestor --> E[Exit 3: Invalid Range];
    D -- Ancestor --> F{Check Commit Range is Not Empty};
    F -- Empty --> E;
    F -- Not Empty --> G{OUTFILE provided?};
    G -- Yes --> H[Set OUTFILE to provided path];
    G -- No --> I[Call sdd-workspace PLAN_FILE];
    I --> J[Construct default OUTFILE path: $dir/review-<base7>..<head7>.diff];
    H --> K[Generate Review Package Content];
    J --> K;
    K --> L[Write content to OUTFILE];
    L --> M[Print confirmation message];
```

Sources:
- [docs/superpowers/specs/2026-07-06-sdd-plan-scoped-workspace.md:66]()
- [skills/subagent-driven-development/scripts/review-package:8-9]()
- [skills/subagent-driven-development/scripts/review-package:13]()
- [skills/subagent-driven-development/scripts/review-package:12-20]()
- [skills/subagent-driven-development/scripts/review-package:22-23]()
- [skills/subagent-driven-development/scripts/review-package:27]()
- [skills/subagent-driven-development/scripts/review-package:28]()
- [skills/subagent-driven-development/scripts/review-package:30-31]()
- [skills/subagent-driven-development/scripts/review-package:33-36]()
- [skills/subagent-driven-development/scripts/review-package:40-41]()
- [skills/subagent-driven-development/scripts/review-package:43]()
- [skills/subagent-driven-development/scripts/review-package:46]()
- [skills/subagent-driven-development/scripts/review-package:49]()
- [skills/subagent-driven-development/scripts/review-package:50]()
- [skills/subagent-driven-development/scripts/review-package:52-53]()

## Helper Script Tests

The functionality of these SDD helper scripts is validated by the `test-sdd-workspace.sh` script [tests/claude-code/test-sdd-workspace.sh](). This test suite ensures that the workspace resolution, artifact placement, and Git integration (or lack thereof) behave as expected.

### Key Test Cases

The `test-sdd-workspace.sh` script covers the following scenarios:

-   **`sdd-workspace` Argument Validation**:
    -   Errors when called without a `PLAN_FILE` argument [tests/claude-code/test-sdd-workspace.sh:54-62]().
    -   Errors when called with a non-existent `PLAN_FILE` [tests/claude-code/test-sdd-workspace.sh:64-71]().
-   **Per-Plan Workspace Resolution**:
    -   Confirms that `sdd-workspace` prints the correct path: `<repo-root>/.superpowers/sdd/<plan-basename>` [tests/claude-code/test-sdd-workspace.sh:74-82]().
    -   Verifies that two different plan files resolve to two distinct workspace directories [tests/claude-code/test-sdd-workspace.sh:84-91]().
-   **Git Integration (Self-Ignoring)**:
    -   Checks that a `.gitignore` file with `*` content is created at `.superpowers/sdd/` [tests/claude-code/test-sdd-workspace.sh:93-97]().
    -   Ensures that artifacts within the SDD workspace are invisible to `git status` [tests/claude-code/test-sdd-workspace.sh:99-109]().
    -   Confirms that `git add -A` does not stage files within the SDD workspace [tests/claude-code/test-sdd-workspace.sh:111-119]().
-   **`task-brief` Artifact Placement**:
    -   Verifies that `task-brief` writes its output file (e.g., `task-1-brief.md`) into the correct plan-scoped workspace directory [tests/claude-code/test-sdd-workspace.sh:121-130]().
-   **`review-package` Artifact Placement and Validation**:
    -   Confirms that `review-package` writes its output file (e.g., `review-<base7>..<head7>.diff`) into the correct plan-scoped workspace directory [tests/claude-code/test-sdd-workspace.sh:138-148]().
    -   Errors when `review-package` is called without a `PLAN_FILE` argument [tests/claude-code/test-sdd-workspace.sh:150-157]().
    -   Verifies that `review-package` honors an explicitly provided `OUTFILE` [tests/claude-code/test-sdd-workspace.sh:159-166]().
    -   Tests range guards:
        -   Rejects a `BASE` that is not an ancestor of `HEAD` [tests/claude-code/test-sdd-workspace.sh:168-180]().
        -   Rejects an empty commit range (`BASE..HEAD`) [tests/claude-code/test-sdd-workspace.sh:182-186]().

Sources:
- [tests/claude-code/test-sdd-workspace.sh:54-62]()
- [tests/claude-code/test-sdd-workspace.sh:64-71]()
- [tests/claude-code/test-sdd-workspace.sh:74-82]()
- [tests/claude-code/test-sdd-workspace.sh:84-91]()
- [tests/claude-code/test-sdd-workspace.sh:93-97]()
- [tests/claude-code/test-sdd-workspace.sh:99-109]()
- [tests/claude-code/test-sdd-workspace.sh:111-119]()
- [tests/claude-code/test-sdd-workspace.sh:121-130]()
- [tests/claude-code/test-sdd-workspace.sh:138-148]()
- [tests/claude-code/test-sdd-workspace.sh:150-157]()
- [tests/claude-code/test-sdd-workspace.sh:159-166]()
- [tests/claude-code/test-sdd-workspace.sh:168-180]()
- [tests/claude-code/test-sdd-workspace.sh:182-186]()
- [tests/claude-code/test-sdd-workspace.sh]()

---

