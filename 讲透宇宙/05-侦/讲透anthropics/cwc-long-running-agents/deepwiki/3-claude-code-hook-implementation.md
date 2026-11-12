<!-- source: DeepWiki mcp.deepwiki.com · repo anthropics/cwc-long-running-agents · page 3 Claude Code Hook Implementation · fetched 2026-10-26 -->

# Claude Code Hook Implementation

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [claude-code-config/.claude/settings.json](claude-code-config/.claude/settings.json)

</details>



## Purpose and Scope

This section provides a high-level overview of how the harness primitives are wired into native Claude Code event hooks. Claude Code hooks intercept agent actions (`PreToolUse` and session completion (`Stop`)) to enforce quality contracts, security controls, and workflow handoffs. The configuration is managed centrally via `claude-code-config/.claude/settings.json` [claude-code-config/.claude/settings.json:1-32](). 

As a parent page, this document outlines the overarching architecture of the hook wiring, shell/JSON conventions, and configuration patterns. For line-level implementation details, refer to the child pages:
- For hook matcher rules and environment overrides, see [Hook Wiring in settings.json](#3.1).
- For script-level stdin/stdout behavior, exit codes, and failure modes, see [Hook Script Reference](#3.2).
- For evidence tracking, results file schema, and security limitations, see [Extending and Customizing the Gate](#3.3).

```mermaid
graph TD
    A["Natural Language Space: Agent Tool Call"] --> B["Code Entity Space: PreToolUse Matchers"]
    B --> C["claude-code-config/.claude/settings.json"]
    C --> D["kill-switch.sh"]
    C --> E["steer.sh"]
    C --> F["track-read.sh"]
    C --> G["verify-gate.sh"]
    
    sub: "Stop Event"
    H["Natural Language Space: Session Stop"] --> I["Code Entity Space: Stop Matcher"]
    I --> J["claude-code-config/.claude/settings.json"]
    J --> K["commit-on-stop.sh"]
```
Sources: [claude-code-config/.claude/settings.json:1-32]()

---

## 3.1 Hook Wiring in settings.json

The hook infrastructure leverages Claude Code's native configuration system to intercept tool invocations and lifecycle events. In `claude-code-config/.claude/settings.json`, hooks are divided into `PreToolUse` and `Stop` categories [claude-code-config/.claude/settings.json:2-30]().

`PreToolUse` hooks use matchers like `*` for global governance (kill switches and steering channels), `Read` to log evidence gathering via `track-read.sh`, and `Write|Edit` to enforce the default-FAIL contract via `verify-gate.sh` [claude-code-config/.claude/settings.json:3-23](). The `Stop` hook invokes `commit-on-stop.sh` to ensure state is captured when a session terminates [claude-code-config/.claude/settings.json:24-30]().

For detailed configuration patterns, environment variable overrides, and matcher precedence, see [Hook Wiring in settings.json](#3.1).

```mermaid
graph TD
    sub: "Hook Registration Flow"
    EV["Claude Code Event"] --> PTU["PreToolUse Matcher"]
    PTU -->|"matcher: *"| KS[".claude/hooks/kill-switch.sh"]
    PTU -->|"matcher: *"| ST[".claude/hooks/steer.sh"]
    PTU -->|"matcher: Read"| TR[".claude/hooks/track-read.sh"]
    PTU -->|"matcher: Write|Edit"| VG[".claude/hooks/verify-gate.sh"]
    
    EV --> STP["Stop Hook"]
    STP --> CS[".claude/hooks/commit-on-stop.sh"]
```
Sources: [claude-code-config/.claude/settings.json:1-32]()

---

## 3.2 Hook Script Architecture and Shell/JSON Conventions

All hook scripts share common conventions for consuming stdin payloads from Claude Code, interacting with environment variables, and producing structured JSON responses or standard exit codes. 

When a hook executes, Claude Code injects contextual payloads over `stdin` containing tool inputs, session metadata, or invocation arguments. The hook scripts process these inputs using standard POSIX shell utilities and Python helpers, validating evidence states or checking ephemeral control files.

For a line-level walkthrough of each script, stdin data structures, exit code behaviors, and failure recovery protocols, see [Hook Script Reference](#3.2).

Sources: [claude-code-config/.claude/settings.json:1-32]()

---

## 3.3 Gate Extension and Security Boundaries

The verification gate relies on tracking file reads and test execution results to prevent blind edits. By monitoring which files have been examined prior to modification, the system enforces rigor. However, native hook enforcement has distinct security boundaries and bypass vectors (such as direct Bash tool file modifications or case sensitivity edge cases).

Customizing these gates involves adapting test result schemas (`test-results.json`), modifying path matchers, or extending evidence collection scripts.

For instructions on extending criteria, managing results file shapes, and understanding security limitations, see [Extending and Customizing the Gate](#3.3).

Sources: [claude-code-config/.claude/settings.json:1-32]()

---

