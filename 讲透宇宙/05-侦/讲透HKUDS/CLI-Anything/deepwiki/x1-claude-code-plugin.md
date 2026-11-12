<!-- source: DeepWiki mcp.deepwiki.com · repo HKUDS/CLI-Anything · extra page Claude Code Plugin · fetched 2026-11-09 -->

# Claude Code Plugin

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [cli-anything-plugin/commands/cli-anything.md](cli-anything-plugin/commands/cli-anything.md)
- [cli-anything-plugin/commands/list.md](cli-anything-plugin/commands/list.md)
- [cli-anything-plugin/commands/refine.md](cli-anything-plugin/commands/refine.md)
- [cli-anything-plugin/commands/test.md](cli-anything-plugin/commands/test.md)
- [cli-anything-plugin/commands/validate.md](cli-anything-plugin/commands/validate.md)
- [krita/agent-harness/KRITA.md](krita/agent-harness/KRITA.md)
- [krita/agent-harness/cli_anything/krita/README.md](krita/agent-harness/cli_anything/krita/README.md)
- [krita/agent-harness/cli_anything/krita/__init__.py](krita/agent-harness/cli_anything/krita/__init__.py)
- [krita/agent-harness/cli_anything/krita/__main__.py](krita/agent-harness/cli_anything/krita/__main__.py)

</details>



This document covers the Claude Code plugin for CLI-Anything, which provides AI agents running in Claude Code with the ability to install via the marketplace (`/plugin marketplace add`, `/plugin install`) and execute the 7-phase CLI generation pipeline.

For information about other platform integrations (OpenCode, Qodercli, OpenClaw, Codex), see [Platform Installation](). For details on the 7-phase generation process that the plugin executes, see [The 7-Phase Generation Pipeline]().

---

## Overview

The Claude Code Plugin is the primary integration mechanism for CLI-Anything. It provides a set of slash commands that Claude Code agents can invoke to:

- **Generate** complete CLI harnesses from software codebases (`/cli-anything`) `[cli-anything-plugin/commands/cli-anything.md:1-13]()`
- **Refine** and expand existing harnesses with iterative gap analysis (`/cli-anything:refine`) `[cli-anything-plugin/commands/refine.md:1-12]()`
- **Test** suites and update `TEST.md` documentation (`/cli-anything:test`) `[cli-anything-plugin/commands/test.md:1-13]()`
- **Validate** harnesses against `HARNESS.md` methodology standards (`/cli-anything:validate`) `[cli-anything-plugin/commands/validate.md:1-13]()`
- **List** and discover installed or generated CLI tools (`/cli-anything:list`) `[cli-anything-plugin/commands/list.md:1-9]()`

Sources: `[cli-anything-plugin/commands/cli-anything.md:1-13]()`, `[cli-anything-plugin/commands/list.md:1-9]`, `[cli-anything-plugin/commands/refine.md:1-12]()`

---

## Installation Methods

### Marketplace Installation

The preferred installation method uses Claude Code's plugin marketplace system to add the repository and install the plugin command suite:

```bash
# Add the marketplace registry
/plugin marketplace add HKUDS/CLI-Anything

# Install the plugin
/plugin install cli-anything
```

### Manual Installation

Users can manually clone the repository into the Claude Code plugins directory and reload:

```bash
cd ~/.claude/plugins
git clone https://github.com/HKUDS/CLI-Anything.git cli-anything
```
After cloning, run `/reload-plugins` within the Claude Code session.

Sources: `[cli-anything-plugin/commands/cli-anything.md:29-86]()`

---

## Plugin Architecture and Code Entity Mapping

The following diagram bridges the Natural Language space (slash commands invoked by users or agents) to the Code Entity space (plugin markdown command definitions and python metadata scanners).

Title: "Natural Language to Code Entity Mapping for Claude Code Plugin"

```mermaid
graph TB
    subgraph "NaturalLanguageSpace"
        NL_GEN["/cli-anything command"]
        NL_LIST["/cli-anything:list command"]
        NL_VAL["/cli-anything:validate command"]
    end

    subgraph "CodeEntitySpace"
        CMD_MAIN["cli-anything-plugin/commands/cli-anything.md"]
        CMD_LIST["cli-anything-plugin/commands/list.md"]
        CMD_VAL["cli-anything-plugin/commands/validate.md"]
        META_DIST["importlib.metadata.distributions()"]
        GLOB_SCAN["glob.glob()"]
    end

    NL_GEN --> CMD_MAIN
    NL_LIST --> CMD_LIST
    NL_VAL --> CMD_VAL
    CMD_LIST --> META_DIST
    CMD_LIST --> GLOB_SCAN
```

### Directory Structure

```mermaid
graph TB
    subgraph "cli-anything-plugin/"
        subgraph "commands/"
            CMD_MAIN["cli-anything.md"]
            CMD_REFINE["refine.md"]
            CMD_TEST["test.md"]
            CMD_VALIDATE["validate.md"]
            CMD_LIST["list.md"]
        end
        
        HARNESS["HARNESS.md"]
        SKILL_GEN["skill_generator.py"]
    end
    
    subgraph "Generated_Harness"
        direction LR
        AH["agent-harness/"]
        SETUP["setup.py"]
        CA["cli_anything/"]
        SW["<software>/"]
        CORE["core/"]
        UTILS["utils/"]
        TESTS["tests/"]
        
        AH --> SETUP
        AH --> CA
        CA --> SW
        SW --> CORE
        SW --> UTILS
        SW --> TESTS
    end

    CMD_MAIN -- "orchestrates" --> AH
    CMD_VAL -- "checks" --> CA
    CMD_LIST -- "scans" --> CA
```

Sources: `[cli-anything-plugin/commands/cli-anything.md:87-108]`, `[cli-anything-plugin/commands/list.md:21-115]()`

---

## Command Execution Flow

Title: "Command Execution Flow and Backend Inspection"

```mermaid
sequenceDiagram
    participant Agent as "ClaudeCodeAgent"
    participant CMD as "cli-anything.md"
    participant List as "list.md"
    participant FS as "FileSystem"
    participant Py as "PythonRuntime"
    
    Agent->>CMD: "/cli-anything https://github.com/blender/blender"
    CMD->>FS: "Clone repository & setup agent-harness"
    CMD->>Py: "pip install -e ."
    
    Agent->>List: "/cli-anything:list --json"
    List->>Py: "importlib.metadata.distributions()"
    Py-->>List: "Filter cli-anything-* distributions"
    List->>FS: "glob.glob(agent-harness/cli_anything/*/__init__.py)"
    List-->>Agent: "JSON tool list output"
```

Sources: `[cli-anything-plugin/commands/cli-anything.md:29-86]`, `[cli-anything-plugin/commands/list.md:21-115]()`

---

## Plugin Commands Reference

### `/cli-anything:list`
Scans the system for both installed PyPI packages (`cli-anything-*`) via `importlib.metadata` and local generated harnesses via `glob` pattern matching `[cli-anything-plugin/commands/list.md:21-115]()`.

- **Deduplication:** Merges installed and generated records, preferring `installed` status while retaining the local `source` path `[cli-anything-plugin/commands/list.md:117-122]()`.
- **Depth Control:** Supports `--depth <n>` for recursive filesystem scanning `[cli-anything-plugin/commands/list.md:13-14]()`.

### `/cli-anything:validate`
Enforces standards from `HARNESS.md`, verifying PEP 420 namespace compliance, Click command groups, `--json` flag support, and `_resolve_cli` subprocess test harnesses `[cli-anything-plugin/commands/validate.md:27-86]()`.

Sources: `[cli-anything-plugin/commands/list.md:13-122]`, `[cli-anything-plugin/commands/validate.md:27-86]()`

---

## Summary

The Claude Code plugin provides robust marketplace integration (`/plugin marketplace add`, `/plugin install`) and command dispatching (`/cli-anything`, `/cli-anything:list`, `/cli-anything:validate`) to automate the creation of agent-native CLI tools `[cli-anything-plugin/commands/cli-anything.md:1-13]`, `[cli-anything-plugin/commands/list.md:1-9]()`.

Sources: `[cli-anything-plugin/commands/cli-anything.md:1-13]`, `[cli-anything-plugin/commands/list.md:1-9]()`

---

