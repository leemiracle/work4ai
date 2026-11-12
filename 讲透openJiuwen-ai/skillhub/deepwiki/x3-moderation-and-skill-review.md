<!-- source: DeepWiki mcp.deepwiki.com · repo openJiuwen-ai/skillhub · extra page Moderation and Skill Review · fetched 2026-11-02 -->

# Moderation and Skill Review

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [CHANGELOG.md](CHANGELOG.md)
- [docs/zh/SUMMARY.md](docs/zh/SUMMARY.md)
- [frontend/src/components/Publish/PublishDrawer.tsx](frontend/src/components/Publish/PublishDrawer.tsx)
- [frontend/src/utils/pluginType.ts](frontend/src/utils/pluginType.ts)
- [frontend/src/utils/publishFieldLabels.ts](frontend/src/utils/publishFieldLabels.ts)
- [marketplace/plugins_market/core/audit_events.py](marketplace/plugins_market/core/audit_events.py)
- [marketplace/plugins_market/core/audit_failed.py](marketplace/plugins_market/core/audit_failed.py)
- [marketplace/plugins_market/core/middleware/request_id.py](marketplace/plugins_market/core/middleware/request_id.py)
- [marketplace/plugins_market/core/moderation.py](marketplace/plugins_market/core/moderation.py)
- [marketplace/plugins_market/routers/audit.py](marketplace/plugins_market/routers/audit.py)
- [marketplace/plugins_market/services/skill_review.py](marketplace/plugins_market/services/skill_review.py)
- [marketplace/plugins_market/tests/test_m3_agent_moderation_flow.py](marketplace/plugins_market/tests/test_m3_agent_moderation_flow.py)
- [marketplace/plugins_market/tests/test_moderated_market_asset_types.py](marketplace/plugins_market/tests/test_moderated_market_asset_types.py)
- [marketplace/skill_review/engines/rule/patterns.py](marketplace/skill_review/engines/rule/patterns.py)
- [marketplace/skill_review/runtime/package_access/zip_access.py](marketplace/skill_review/runtime/package_access/zip_access.py)
- [marketplace/skill_review/tests/test_zip_package_access.py](marketplace/skill_review/tests/test_zip_package_access.py)
- [marketplace/tests/test_skill_review_incremental_checks.py](marketplace/tests/test_skill_review_incremental_checks.py)

</details>



## Purpose and Scope
This page documents the moderation subsystem, pending review queues, self-moderation policies, automated `skill_review` engines, and package safety validation pipelines within the openJiuwen Agentic Hub (`plugins_market` and `skill_review`). It details how assets transition through publishing states, how admin workflows handle moderation queues, and how automated rule and semantic engines inspect package contents for security risks.

---

## 1. Moderation Statuses and Asset Taxonomies

The marketplace enforces publishing gates and visibility controls using a structured moderation status taxonomy and classification set. 

### Moderation Status Constants
Assets and versions maintain explicit moderation statuses defined in `marketplace/plugins_market/core/moderation.py`:
* `MODERATION_PENDING` (`"PENDING"`): Awaiting administrator or automated review [marketplace/plugins_market/core/moderation.py:14]().
* `MODERATION_APPROVED` (`"APPROVED"`): Passed inspection and publicly visible [marketplace/plugins_market/core/moderation.py:15]() [marketplace/plugins_market/core/moderation.py:76-77]().
* `MODERATION_REJECTED` (`"REJECTED"`): Blocked due to policy or security violations [marketplace/plugins_market/core/moderation.py:16]().

### Asset Type Classifications
Plugin types are grouped into categories determining whether they undergo moderation:
* `SKILL_LIKE_PLUGIN_TYPES`: Includes `skill` and `swarmskill` (normalized from `teamskills`) [marketplace/plugins_market/core/moderation.py:18-19]() [marketplace/plugins_market/core/moderation.py:35-37]().
* `AGENT_ASSET_PLUGIN_TYPES`: Wrapped agent types including `agent-plugin`, `agent-template`, and `agent-mcp` [marketplace/plugins_market/core/moderation.py:22-28]().
* `MODERATED_MARKET_ASSET_TYPES`: The union of skill-like types and agent asset types. Legacy types like `tools`, `mcp-stdio`, and `restful-api` bypass moderation and are auto-approved [marketplace/plugins_market/core/moderation.py:30-32]().

```mermaid
graph TD
    subcode["Code Entity Space: marketplace/plugins_market/core/moderation.py"]
        A["MODERATION_PENDING"] --> B["MarketAssetDB.moderation_status"]
        C["MODERATION_APPROVED"] --> B
        D["MODERATION_REJECTED"] --> B
        E["SKILL_LIKE_PLUGIN_TYPES"] --> H["is_moderated_market_asset_type()"]
        F["AGENT_ASSET_PLUGIN_TYPES"] --> H
        G["MODERATED_MARKET_ASSET_TYPES"] --> H
    end

    subgraph "Natural Language Space"
        NL1["Pending Review State"] --> NL2["Public Visibility Gate"]
        NL3["Skill & Agent Types"] --> NL4["Mandatory Inspection"]
    end

    NL1 -.-> A
    NL2 -.-> C
    NL3 -.-> E
    NL4 -.-> H

    classDef default fill:#fff,stroke:#000,stroke-width:1px;
```
*Title: Moderation Constants to Code Mapping*

Sources:
- `marketplace/plugins_market/core/moderation.py:1-78`

---

## 2. Pending Queue and Self-Moderation Rules

### Self-Moderation and Admin Bypass
When a user publishes an asset, `_moderation_for_publish()` evaluates whether the publisher requires moderation or qualifies for auto-approval. System administrators (`is_system_admin=True`) automatically bypass moderation, receiving `MODERATION_APPROVED` status. Regular users publishing moderated asset types (`agent-plugin`, `agent-mcp`, `agent-template`, `skill`, `swarmskill`) are placed into `MODERATION_PENDING` [marketplace/plugins_market/tests/test_moderated_market_asset_types.py:76-95]().

### Pending Queue Queries
The moderation backend exposes pending queues via `MarketAssetRepository.list_plugins()`. For agent assets, pending queues operate at the version row level rather than solely relying on the main asset record. This ensures that when an approved asset publishes a new version requiring review, it correctly appears in the pending review queue [marketplace/plugins_market/tests/test_m3_agent_moderation_flow.py:144-189]().

```mermaid
graph TD
    subcode["Code Entity Space: _moderation_for_publish() & MarketAssetRepository"]
        P1["Publish Request"] --> P2{"is_system_admin?"}
        P2 -- Yes --> P3["MODERATION_APPROVED"]
        P2 -- No --> P4{"is_moderated_market_asset_type()"}
        P4 -- Yes --> P5["MODERATION_PENDING"]
        P4 -- No --> P3
        P5 --> P6["MarketAssetRepository.list_plugins()"]
        P6 --> P7["Version-Level Filtering"]
    end

    subgraph "Natural Language Space"
        N1["User Submission"] --> N2["Admin Auto-Pass Check"]
        N2 --> N3["Queue Assignment"]
    end

    N1 -.-> P1
    N2 -.-> P2
    N3 -.-> P5

    classDef default fill:#fff,stroke:#000,stroke-width:1px;
```
*Title: Publish Moderation Decision Flow*

Sources:
- `marketplace/plugins_market/core/moderation.py:35-78`
- `marketplace/plugins_market/tests/test_moderated_market_asset_types.py:76-95`
- `marketplace/plugins_market/tests/test_m3_agent_moderation_flow.py:144-189`

---

## 3. Automated Skill Review Engine and Package Safety

Automated skill inspection is handled by the `skill_review` subsystem, combining static pattern matching with safe archive extraction.

### Package Extraction and Zip Safety
Before executing checks, ZIP archives are processed by `ZipPackageAccess` and `_index_safe_entries()` in `marketplace/skill_review/runtime/package_access/zip_access.py`. This mechanism prevents path traversal attacks, absolute paths, and zip bomb collisions by raising a `ZipPathCollisionError` if multiple archive members normalize to identical paths [marketplace/skill_review/runtime/package_access/zip_access.py:15-33]().

### Rule Engine Patterns
The static analysis engine executes built-in regex rules defined in `DEFAULT_RULE_PATTERNS` (`marketplace/skill_review/engines/rule/patterns.py`) [marketplace/skill_review/engines/rule/patterns.py:47-181](). Each `RulePattern` specifies:
* `pattern_id`: Unique identifier (e.g. `private_key_block`, `well_known_api_key`, `prompt_override`) [marketplace/skill_review/engines/rule/patterns.py:12]().
* `regex`: Compiled case-insensitive regular expression [marketplace/skill_review/engines/rule/patterns.py:13]().
* `section_key`: Target domain section (`data_asset`, `instruction`, `execution`) [marketplace/skill_review/engines/rule/patterns.py:14]().
* `severity` & `confidence`: Risk weighting parameters (`high`, `medium`, `low`) [marketplace/skill_review/engines/rule/patterns.py:16-17]().

```mermaid
graph TD
    subcode["Code Entity Space: skill_review Engine & Zip Access"]
        Z1["ZipFile Archive"] --> Z2["_index_safe_entries()"]
        Z2 -->|Collision Detected| Z3["ZipPathCollisionError"]
        Z2 -->|Safe Path| Z4["ZipPackageAccess.list_files()"]
        Z4 --> R1["DEFAULT_RULE_PATTERNS"]
        R1 --> R2["compile_rule()"]
        R2 --> R3["RulePattern Matching"]
    end

    subgraph "Natural Language Space"
        NL1["Upload Archive"] --> NL2["Path Safety Validation"]
        NL2 --> NL3["Static Content Scanning"]
    end

    NL1 -.-> Z1
    NL2 -.-> Z2
    NL3 -.-> R3

    classDef default fill:#fff,stroke:#000,stroke-width:1px;
```
*Title: Package Access and Rule Review Pipeline*

Sources:
- `marketplace/skill_review/runtime/package_access/zip_access.py:15-78`
- `marketplace/skill_review/engines/rule/patterns.py:10-181`

---

## 4. Review Lifecycle, Reports, and Writeback

### Review Statuses and Execution Lifecycle
Review tasks are managed through `initialize_skill_review()` and run asynchronously or synchronously depending on the trigger [marketplace/plugins_market/services/skill_review.py:115-160](). The review record progresses through distinct lifecycle states:
* `REVIEW_STATUS_QUEUED` (`"queued"`): Initialized and waiting for execution [marketplace/plugins_market/services/skill_review.py:50]() [marketplace/plugins_market/services/skill_review.py:136]().
* `REVIEW_STATUS_RUNNING` (`"running"`): Actively executing rule and semantic checkers [marketplace/plugins_market/services/skill_review.py:51]().
* `REVIEW_STATUS_PASSED` (`"passed"`): Successfully evaluated with no blocking violations [marketplace/plugins_market/services/skill_review.py:52]().
* `REVIEW_STATUS_FAILED` (`"failed"`): Review completed but identified security findings exceeding thresholds [marketplace/plugins_market/services/skill_review.py:53]().
* `REVIEW_STATUS_SYSTEM_FAILED` (`"system_failed"`): Execution aborted due to timeouts, service unavailability, or invalid model responses [marketplace/plugins_market/services/skill_review.py:54]() [marketplace/plugins_market/services/skill_review.py:163-180]().

### Semantic Review and Fallbacks
Optional AI semantic review layers run after static rule checks, producing semantic summaries and risk conclusions [marketplace/plugins_market/services/skill_review.py:188-197]. If the AI service encounters failures, fallback messages such as `USER_FACING_SEMANTIC_FALLBACK` ensure the publishing pipeline remains functional based on static rules [marketplace/plugins_market/services/skill_review.py:69-72]().

### Writeback Resilience and Audit Logging
Database writebacks for review reports implement exponential backoff with jitter (`REVIEW_WRITEBACK_RETRY_BACKOFF_SECONDS`) to handle MySQL concurrent lock conflicts (`RETRYABLE_REVIEW_WRITEBACK_MYSQL_ERROR_CODES` like `1205` and `1213`) [marketplace/plugins_market/services/skill_review.py:61-63](). All moderation and review state changes emit structured audit records via `audit_log` and notify administrators through `notify_review_admins_new_skill_submission` [marketplace/plugins_market/routers/audit.py:23-36]() [marketplace/plugins_market/services/skill_review.py:12-42]().

Sources:
- `marketplace/plugins_market/services/skill_review.py:39-197`
- `marketplace/plugins_market/routers/audit.py:23-56`

---

