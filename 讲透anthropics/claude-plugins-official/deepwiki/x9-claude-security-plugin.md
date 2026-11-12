<!-- source: DeepWiki mcp.deepwiki.com · repo anthropics/claude-plugins-official · extra page claude-security Plugin · fetched 2026-10-26 -->

# claude-security Plugin

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [plugins/claude-security/.claude-plugin/plugin.json](plugins/claude-security/.claude-plugin/plugin.json)
- [plugins/claude-security/README.md](plugins/claude-security/README.md)
- [plugins/claude-security/agents/claude-security.md](plugins/claude-security/agents/claude-security.md)
- [plugins/claude-security/agents/explore.md](plugins/claude-security/agents/explore.md)
- [plugins/claude-security/agents/patch-generator.md](plugins/claude-security/agents/patch-generator.md)
- [plugins/claude-security/agents/patch-verifier.md](plugins/claude-security/agents/patch-verifier.md)
- [plugins/claude-security/agents/scan-researcher.md](plugins/claude-security/agents/scan-researcher.md)
- [plugins/claude-security/scripts/lib/finding.py](plugins/claude-security/scripts/lib/finding.py)
- [plugins/claude-security/scripts/lib/plugin.py](plugins/claude-security/scripts/lib/plugin.py)
- [plugins/claude-security/scripts/lib/sarif.py](plugins/claude-security/scripts/lib/sarif.py)
- [plugins/claude-security/scripts/lib/secret.py](plugins/claude-security/scripts/lib/secret.py)
- [plugins/claude-security/scripts/lib/strictjson.py](plugins/claude-security/scripts/lib/strictjson.py)
- [plugins/claude-security/scripts/patch_artifacts.py](plugins/claude-security/scripts/patch_artifacts.py)
- [plugins/claude-security/scripts/render_report.py](plugins/claude-security/scripts/render_report.py)
- [plugins/claude-security/scripts/write_scan_meta.py](plugins/claude-security/scripts/write_scan_meta.py)
- [plugins/claude-security/skills/claude-security/SKILL.md](plugins/claude-security/skills/claude-security/SKILL.md)
- [plugins/claude-security/skills/claude-security/jobs/scan-changes.md](plugins/claude-security/skills/claude-security/jobs/scan-changes.md)
- [plugins/claude-security/skills/claude-security/jobs/scan-codebase.md](plugins/claude-security/skills/claude-security/jobs/scan-codebase.md)
- [plugins/claude-security/skills/claude-security/jobs/suggest-patches.md](plugins/claude-security/skills/claude-security/jobs/suggest-patches.md)
- [plugins/claude-security/skills/claude-security/specs/report-spec.md](plugins/claude-security/skills/claude-security/specs/report-spec.md)
- [plugins/claude-security/workflows/scan.js](plugins/claude-security/workflows/scan.js)

</details>



The `claude-security` plugin is an agentic security scanning, verification, and automated patching system designed to execute deep vulnerability research within a Claude Code session [plugins/claude-security/.claude-plugin/plugin.json:1-4](). It orchestrates a multi-agent pipeline mirroring human security teams to map codebases, build threat models, hunt for vulnerabilities, verify findings through an adversarial panel, and generate targeted, verified patch files [plugins/claude-security/README.md:1-5]().

Sources: [plugins/claude-security/.claude-plugin/plugin.json:1-4](), [plugins/claude-security/README.md:1-5]()

## Overview and Trust Model

The plugin operates directly within the user's Claude Code session using local repository permissions (`.git/config`, `.claude/` settings, and `CLAUDE.md`) [plugins/claude-security/README.md:13-18](). 

### The Trusted-Code Model
*   **No Isolation Layer:** Scans run under the user's standard permissions without a built-in sandbox [plugins/claude-security/README.md:13-18]().
*   **Adversarial Defense:** Source code, comments, and docstrings are treated as untrusted data. Instructions embedded in code (e.g., "skip verification") are classified as prompt injection attacks, logged as findings, and ignored by researchers [plugins/claude-security/agents/scan-researcher.md:45-51]().
*   **Sandbox Recommendation:** For untrusted third-party repositories or dependencies, users are advised to run sessions inside `sandbox-runtime` [plugins/claude-security/README.md:13-18]().

Sources: [plugins/claude-security/README.md:13-18](), [plugins/claude-security/agents/scan-researcher.md:45-51]()

## System Architecture

The orchestrator agent (`claude-security:claude-security`) coordinates jobs by executing workflows implemented in JavaScript (`workflows/scan.js`) and dispatching specialized subagents [plugins/claude-security/agents/claude-security.md:3-15](), [plugins/claude-security/workflows/scan.js:1-4]().

### Diagram: Natural Language Space to Code Entity Space (Scanning Pipeline)
This diagram bridges high-level user security requests to the concrete script and workflow modules executing them.

```mermaid
graph TD
    User[""User Request (Natural Language)""] --> Lead[""Agent: claude-security (plugins/claude-security/agents/claude-security.md)""]
    Lead --> Menu[""Skill: claude-security (plugins/claude-security/skills/claude-security/SKILL.md)""]
    
    subgraph "Job Dispatchers"
        Menu --> CB[""Job: scan-codebase (plugins/claude-security/skills/claude-security/jobs/scan-codebase.md)""]
        Menu --> CH[""Job: scan-changes (plugins/claude-security/skills/claude-security/jobs/scan-changes.md)""]
        Menu --> SP[""Job: suggest-patches (plugins/claude-security/skills/claude-security/jobs/suggest-patches.md)""]
    end

    CB --> Workflow[""Workflow Runtime: scan.js (plugins/claude-security/workflows/scan.js)""]
    CH --> Workflow

    Workflow --> Inv[""Agent: scan-inventory (plugins/claude-security/agents/scan-inventory.md)""]
    Workflow --> Res[""Agent: scan-researcher (plugins/claude-security/agents/scan-researcher.md)""]
    Workflow --> Ver[""Agent: scan-verifier (plugins/claude-security/agents/scan-verifier.md)""]
    
    SP --> PatchGen[""Agent: patch-generator (plugins/claude-security/agents/patch-generator.md)""]
    PatchGen --> PatchVer[""Agent: patch-verifier (plugins/claude-security/agents/patch-verifier.md)""]
```
Sources: [plugins/claude-security/agents/claude-security.md:3-15](), [plugins/claude-security/workflows/scan.js:1-4](), [plugins/claude-security/agents/scan-researcher.md:1-8]()

## Scan Jobs and Effort Tiers

The plugin supports three core jobs invoked via slash commands or natural language [plugins/claude-security/README.md:29-38]():
1.  **Scan codebase:** Analyzes the entire repository or scoped sub-directories [plugins/claude-security/skills/claude-security/jobs/scan-codebase.md:1-5]().
2.  **Scan changes:** Reviews a branch diff, pull request diff, or specific commit against its parent [plugins/claude-security/skills/claude-security/jobs/scan-changes.md:1-5]().
3.  **Suggest patches:** Turns confirmed report findings into targeted `.patch` files [plugins/claude-security/skills/claude-security/jobs/suggest-patches.md:1-4]().

Effort tiers (`low`, `medium`, `high`) are validated in `workflows/scan.js` to control resource allocation, component matrix depth, and breadth sweeps [plugins/claude-security/workflows/scan.js:9-11](), [plugins/claude-security/skills/claude-security/jobs/scan-codebase.md:19-28]().

| Effort Tier | Inventory & Scope | Researchers | Verification Panel |
| :--- | :--- | :--- | :--- |
| `low` | Skipped (Fast triage) | 1 researcher over repository | 3-lens panel (2-of-3 quorum) [plugins/claude-security/skills/claude-security/jobs/scan-codebase.md:23-23]() |
| `medium` | Component partition (~25 files/component, max 24) | 1 researcher per component × category | 3-lens panel (2-of-3 quorum) [plugins/claude-security/skills/claude-security/jobs/scan-codebase.md:24-24]() |
| `high` | Component partition (max 48 components) | 2 researchers per cell, 2 breadth sweeps | 3-lens panel (2-of-3 quorum) [plugins/claude-security/skills/claude-security/jobs/scan-codebase.md:25-29]() |

Sources: [plugins/claude-security/README.md:29-38](), [plugins/claude-security/workflows/scan.js:9-11](), [plugins/claude-security/skills/claude-security/jobs/scan-codebase.md:19-29]()

## Report Format and Artifact Generation

Scans generate timestamped directories (`CLAUDE-SECURITY-<timestamp>/`) containing structured machine-readable and human-readable outputs produced by `scripts/render_report.py` [plugins/claude-security/README.md:55-60](), [plugins/claude-security/scripts/render_report.py:2-12]().

### Artifact Structure
*   **`CLAUDE-SECURITY-RESULTS.md`**: Human-readable report detailing coverage, metrics, severity scores (CRITICAL, HIGH, MEDIUM, LOW mapped to CVSS v4.0 qualitative scales), exploit scenarios, and recommendations [plugins/claude-security/README.md:57-57]().
*   **`CLAUDE-SECURITY-RESULTS.jsonl`**: Machine-readable records where each object includes a stable `claudeSecurityPluginFindingId` [plugins/claude-security/README.md:58-58](), [plugins/claude-security/scripts/lib/finding.py:26-53]().
*   **`CLAUDE-SECURITY-RESULTS.sarif`**: SARIF 2.1.0 compliant log generated by `scripts/lib/sarif.py` for integration with GitHub code scanning and IDE viewers [plugins/claude-security/README.md:59-59](), [plugins/claude-security/scripts/lib/sarif.py:1-65]().
*   **`CLAUDE-SECURITY-REVISION-<sha12>.json`**: Revision stamp capturing commit metadata, dirty tree flags (`-dirty`), and verification rigor [plugins/claude-security/README.md:60-60]().

Sources: [plugins/claude-security/README.md:55-60](), [plugins/claude-security/scripts/render_report.py:2-12](), [plugins/claude-security/scripts/lib/sarif.py:1-65]()

## Patch Generation and Multi-Agent Verification Pipeline

The `suggest-patches` job translates findings into verified fixes [plugins/claude-security/skills/claude-security/jobs/suggest-patches.md:1-4](). Every candidate patch undergoes isolated implementation and rigorous multi-agent scrutiny before delivery.

### Diagram: Natural Language Space to Code Entity Space (Patch Verification Pipeline)
This diagram maps patch suggestion commands to underlying workspace operations and verifier claims.

```mermaid
graph LR
    UserReq[""User Request (suggest-patches)""] --> Job[""Job Recipe: suggest-patches.md (plugins/claude-security/skills/claude-security/jobs/suggest-patches.md)""]
    Job --> Gen[""Agent: patch-generator (plugins/claude-security/agents/patch-generator.md)""]
    
    subgraph "Workspace Execution"
        Gen --> Scratch[""Scratch Workspace Checkout (PATCH BASE)""]
        Scratch --> Staged[""Staged Diff (git diff --cached)""]
    end

    Staged --> Ver[""Agent: patch-verifier (plugins/claude-security/agents/patch-verifier.md)""]

    subgraph "Verification Claims"
        Ver --> C1[""TARGETED (Strict hunk-finding alignment)""]
        Ver --> C2[""NO_NEW_VULNERABILITY (Fresh researcher pass)""]
        Ver --> C3[""BEHAVIOUR_UNCHANGED (Test execution & review)""]
    end

    C1 & C2 & C3 --> Decision{All Confident?}
    Decision -- Yes --> PatchFile[""Output: patches/FX.patch""]
    Decision -- No --> Reject[""Objection Sent to Generator""]
```
Sources: [plugins/claude-security/skills/claude-security/jobs/suggest-patches.md:1-4](), [plugins/claude-security/agents/patch-generator.md:1-13](), [plugins/claude-security/agents/patch-verifier.md:12-44]()

### The Three Verifier Claims
The `patch-verifier` subagent enforces strict criteria before a patch is accepted:
1.  **TARGETED:** Every hunk directly addresses the finding without scope creep [plugins/claude-security/agents/patch-verifier.md:34-34]().
2.  **NO_NEW_VULNERABILITY:** An independent researcher inspects the staged diff to ensure no secondary weakness is introduced [plugins/claude-security/agents/patch-verifier.md:35-35]().
3.  **BEHAVIOUR_UNCHANGED:** Project test suites are executed within the scratch workspace, confirming functionality remains intact [plugins/claude-security/agents/patch-verifier.md:36-36]().

Sources: [plugins/claude-security/skills/claude-security/jobs/suggest-patches.md:1-4](), [plugins/claude-security/agents/patch-verifier.md:12-44]()

---

