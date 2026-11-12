<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/boro · page 5 Apply, Build and Test Workflows · fetched 2026-10-26 -->

# Apply, Build and Test Workflows

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [resources/test-picker.md](resources/test-picker.md)
- [resources/test-plan-picker.md](resources/test-plan-picker.md)
- [src/apply.rs](src/apply.rs)
- [src/git.rs](src/git.rs)
- [src/kconfig.rs](src/kconfig.rs)
- [src/output.rs](src/output.rs)
- [src/test_boot.rs](src/test_boot.rs)
- [src/tools.rs](src/tools.rs)

</details>



This page provides a high-level overview of `boro`'s non-review execution workflows: applying backports with automated conflict resolution, building kernels, and running automated boot and verification tests using `virtme-ng`. 

While the review pipeline analyzes code statically, these workflows handle active manipulation of the working tree, dependency configuration, compilation, and isolated virtual machine execution.

```mermaid
graph TD
    User["User Command"] -->|"boro apply"| ApplyModule["Apply Workflow\nsrc/apply.rs"]
    User -->|"boro test"| TestModule["Test Workflow\nsrc/test_boot.rs"]
    ApplyModule --> GitOps["Git Operations\nsrc/git.rs"]
    TestModule --> KConfig["KConfig Gen\nsrc/kconfig.rs"]
    TestModule --> VngRunner["virtme-ng Harness\nsrc/test_boot.rs"]
    
    subgraph CodeEntitySpace ["Code Entity Space"]
        ApplyModule
        TestModule
        GitOps
        KConfig
        VngRunner
    end
    
    Sources: src/apply.rs:20-95, src/test_boot.rs:146-203, src/git.rs:8-14, src/kconfig.rs:33-40
```

---

## 5.1. Patch Apply and Conflict Resolution

The `boro apply` command automates the cherry-picking of upstream patches into target trees where code drift often causes `git` diff3 conflicts. Instead of failing immediately or requiring manual intervention for every hunk, `boro` engages a suggest-and-validate loop powered by large language models to resolve conflicts idiomatically while preserving target-tree-specific adaptations.

Following a successful apply or auto-resolution, a mandatory post-apply review stage inspects the entire modified commit diff to detect "backport gaps"—references to types, macros, or fields introduced upstream in commits absent from the target tree.

For details, see [Patch Apply and Conflict Resolution](#5.1).

Sources: `src/apply.rs:20-95`

---

## 5.2. Build and Boot Testing with virtme-ng

The `boro test` command exercises patches inside an isolated virtual machine using `virtme-ng` (`vng`). Before compilation, `boro` analyzes the patch diff to generate a targeted Kconfig fragment (`src/kconfig.rs`), ensuring that gated subsystems affected by the patch are actually compiled into the test kernel.

An AI test picker (`resources/test-picker.md`) or test plan generator (`resources/test-plan-picker.md`) selects a high-signal test command or falls back safely to `dmesg` inspection. The runner enforces strict timeouts to prevent hangs during VM execution, capturing standard output and error streams for subsequent triage.

```mermaid
graph TD
    Patch["Commit Patch"] --> KGen["KConfig Generator\nsrc/kconfig.rs"]
    Patch --> Picker["Test Picker\nresources/test-picker.md"]
    KGen --> VngBuild["vng -b Build\nsrc/test_boot.rs"]
    Picker --> VngRun["vng -r VM Execution\nsrc/test_boot.rs"]
    VngBuild --> VngRun
    VngRun --> Triage["Model Triage & Findings\nsrc/test_boot.rs"]

    subgraph CodeEntitySpace ["Code Entity Space"]
        KGen
        VngBuild
        VngRun
        Triage
    end

    Sources: src/kconfig.rs:33-40, src/test_boot.rs:146-203, resources/test-picker.md:1-38
```

For details, see [Build and Boot Testing with virtme-ng](#5.2).

Sources: `src/test_boot.rs:146-203`, `resources/test-picker.md:1-38`, `src/kconfig.rs:33-40`

---

## 5.3. Git, Worktrees and Process Execution

All apply, build, and test workflows rely on a robust set of repository management and subprocess utilities. These helpers normalize commit ranges, query revision histories, and manage worktree isolation to guarantee that concurrent worker threads do not interfere with each other's working directories or git states.

Subprocess execution wrappers handle output capture, exit-status validation, and resource cleanups across tool invocations such as `git`, `vng`, and external diagnostic binaries.

For details, see [Git, Worktrees and Process Execution](#5.3).

Sources: `src/git.rs:8-14`

---

