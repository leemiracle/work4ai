<!-- source: DeepWiki mcp.deepwiki.com · repo conorluddy/ios-simulator-skill · page 3 Core Concepts · fetched 2026-10-26 -->

# Core Concepts

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [CLAUDE.md](CLAUDE.md)
- [README.md](README.md)

</details>



This document explains the fundamental architectural concepts and design patterns that underpin the `ios-simulator-skill` system. These concepts apply consistently across all 22 scripts and shared utilities.

For detailed implementation of specific script categories, see [Script Categories Overview](#4). For contributor guidance on applying these patterns, see [Architecture Patterns and Best Practices](#12.4).

---

## Semantic Navigation via Accessibility APIs

The skill uses **semantic navigation** through iOS accessibility APIs rather than pixel-based coordinate systems. This architectural decision provides resilience against UI changes, screen size variations, and dynamic layouts.

### Traditional Pixel-Based Approach (Fragile)

```bash
# Brittle - breaks when UI changes
idb ui tap 320 400
```

### Semantic Approach (Robust)

```bash
# Resilient - finds by meaning
python scripts/navigator.py --find-text "Login" --tap
```

**Diagram: Semantic Navigation Flow**

```mermaid
graph TB
    subgraph "Natural Language Space"
        [REQ] --> "Find and tap 'Login' button"
    end
    
    subgraph "Code Entity Space (navigator.py)"
        [PARSE] --> "ArgumentParser --find-text 'Login' --tap"
        [NAV_CLASS] --> "ElementNavigator class __init__"
        [FIND] --> "find_element() search_term='Login'"
    end
    
    subgraph "AccessibilityTreeQuerying"
        [IDB_CMD] --> "subprocess.run() idb ui describe-all --json"
        [JSON_PARSE] --> "json.loads(stdout)"
        [TREE] --> "elements: List[Dict] type, label, frame"
    end
    
    subgraph "ElementMatching"
        [FILTER] --> "_filter_elements() fuzzy text matching"
        [MATCH] --> "matched_element: Dict {'type': 'Button', 'label': 'Login'}"
    end
    
    subgraph "CoordinateCalculation"
        [FRAME] --> "frame: Dict {'x': 50, 'y': 400, 'w': 100, 'h': 44}"
        [CENTER] --> "calculate_center() x=100, y=422"
    end
    
    subgraph "ActionExecution"
        [TAP_CMD] --> "subprocess.run() idb ui tap 100 422"
        [SUCCESS] --> "Return: (True, 'Tapped Login')"
    end
    
    [REQ] --> [PARSE]
    [PARSE] --> [NAV_CLASS]
    [NAV_CLASS] --> [FIND]
    [FIND] --> [IDB_CMD]
    [IDB_CMD] --> [JSON_PARSE]
    [JSON_PARSE] --> [TREE]
    [TREE] --> [FILTER]
    [FILTER] --> [MATCH]
    [MATCH] --> [FRAME]
    [FRAME] --> [CENTER]
    [CENTER] --> [TAP_CMD]
    [TAP_CMD] --> [SUCCESS]
```

Sources: [README.md:67-79](), [ios-simulator-skill/skills/ios-simulator-skill/scripts/navigator.py](), [CLAUDE.md:203-209]()

The system performs **fuzzy matching** by default to handle minor text variations. For detailed navigation capabilities, see [Semantic Navigation via Accessibility APIs](#3.1).

---

## External Tools: simctl and idb

The skill wraps two primary command-line tools: Apple's `xcrun simctl` and Facebook's `idb`. Scripts abstract these tools behind semantic interfaces.

**Diagram: Tool Selection and Invocation**

```mermaid
graph LR
    subgraph "ScriptLayer"
        [SCRIPT] --> "Any Script (e.g., simctl_boot.py)"
        [CHECK] --> "check_idb_available() from idb_utils"
    end
    
    subgraph "ToolDecisionLogic"
        [IDB_CHECK] --> "IDB installed? shutil.which('idb')"
        [FEATURE_REQ] --> "Requires interactive UI features?"
    end
    
    subgraph "AppleTools (simctl)"
        [SIMCTL] --> "xcrun simctl subprocess.run()"
        [SIMCTL_OPS] --> "boot, shutdown, create, delete, privacy, status_bar"
    end
    
    subgraph "FacebookIDB (idb)"
        [IDB] --> "idb subprocess.run()"
        [IDB_OPS] --> "ui describe-all, ui tap, ui swipe, ui text"
    end
    
    [SCRIPT] --> [CHECK]
    [CHECK] --> [IDB_CHECK]
    [IDB_CHECK] -->|No| [SIMCTL]
    [IDB_CHECK] -->|Yes| [FEATURE_REQ]
    [FEATURE_REQ] -->|No| [SIMCTL]
    [FEATURE_REQ] -->|Yes| [IDB]
    
    [SIMCTL] --> [SIMCTL_OPS]
    [IDB] --> [IDB_OPS]
```

Sources: [CLAUDE.md:7-12](), [ios-simulator-skill/skills/ios-simulator-skill/scripts/common/idb_utils.py]()

### Tool Responsibilities
- **simctl**: Used for lifecycle management (boot/shutdown), simulator creation, and system-level settings like privacy permissions or status bar overrides. [ios-simulator-skill/skills/ios-simulator-skill/scripts/simctl_boot.py](), [ios-simulator-skill/skills/ios-simulator-skill/scripts/privacy_manager.py]().
- **idb**: Used for UI-level interactions including querying the accessibility tree and simulating gestures. [ios-simulator-skill/skills/ios-simulator-skill/scripts/navigator.py](), [ios-simulator-skill/skills/ios-simulator-skill/scripts/gesture.py]().

For detailed tool usage, see [External Tools: simctl and idb](#3.2).

---

## Progressive Disclosure and Token Efficiency

The skill achieves a **96% token reduction** compared to raw tool output through a progressive disclosure pattern. Scripts return minimal summaries by default, caching full details for later retrieval.

### ProgressiveCache System
The `ProgressiveCache` class at [ios-simulator-skill/skills/ios-simulator-skill/scripts/common/cache_utils.py:162-163]() implements TTL-based caching. When a command (like a build) generates large output, the skill saves the full log to disk and provides a `cache_id`.

```python
# Default Summary Output (Low Token Cost)
"Build: SUCCESS (0 errors, 3 warnings) [xcresult-20251018-143052]"
```

For detailed metrics and cache retrieval flags, see [Progressive Disclosure and Token Efficiency](#3.3).

Sources: [ios-simulator-skill/skills/ios-simulator-skill/scripts/common/cache_utils.py](), [CLAUDE.md:174-182](), [README.md:49-65]()

---

## Output Modes and Formatting

All scripts support three output modes optimized for different consumers: AI agents, human developers, and CI/CD pipelines.

| Mode | Flag | Purpose | Token Impact |
|------|------|---------|--------------|
| **Default** | (none) | Minimal summary for AI agents | 5-10 tokens |
| **Verbose** | `--verbose` | Full details for debugging | 400+ tokens |
| **JSON** | `--json` | Machine-parseable for automation | 20-30 tokens |

Scripts implement this using a consistent `execute()` method that returns a `(success, message)` tuple. [CLAUDE.md:66-68]().

For formatting examples, see [Output Modes and Formatting](#3.4).

Sources: [CLAUDE.md:90-105](), [ios-simulator-skill/skills/ios-simulator-skill/scripts/simctl_boot.py]()

---

## Device Targeting and Auto-Detection

Scripts automatically detect the target simulator, eliminating the need to repeatedly provide UDIDs.

- **Auto-UDID Detection**: If no UDID is provided, `resolve_device_identifier()` in [ios-simulator-skill/skills/ios-simulator-skill/scripts/common/device_utils.py:151-152]() identifies the single booted simulator.
- **Fuzzy Name Resolution**: Users can provide names like "iPhone 16" instead of full UDIDs.
- **Batch Operations**: Many scripts support `--all` or `--type` (e.g., `python scripts/simctl_boot.py --type iPhone`). [CLAUDE.md:107-114]().

For logic details, see [Device Targeting and Auto-Detection](#3.5).

Sources: [ios-simulator-skill/skills/ios-simulator-skill/scripts/common/device_utils.py](), [CLAUDE.md:78-88](), [README.md:136-137]()

---

## Class-Based Script Architecture

All scripts follow a standardized class-based design pattern to ensure testability and reusability.

1. **Initialization**: The class `__init__` handles configuration and device resolution.
2. **Execution**: The `execute()` method contains the core logic and returns a `(bool, str)` tuple representing success and the formatted message. [CLAUDE.md:66-68]().
3. **Main**: The `main()` function handles CLI argument parsing and process exit codes. [CLAUDE.md:70-76]().

```python
# Standard Pattern [CLAUDE.md:57-76]
class DeviceManager:
    def __init__(self, udid: str | None = None):
        self.udid = udid

    def execute(self, **kwargs) -> tuple[bool, str]:
        # Return (success, message) tuple
        pass
```

For architectural standards, see [Class-Based Script Architecture](#3.6).

Sources: [CLAUDE.md:57-76](), [ios-simulator-skill/skills/ios-simulator-skill/scripts/simctl_boot.py]()

---

