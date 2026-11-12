<!-- source: DeepWiki mcp.deepwiki.com · repo Imbad0202/academic-research-skills · page 11 CI/CD and Quality Infrastructure · fetched 2026-10-30 -->

# CI/CD and Quality Infrastructure

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/workflows/pytest.yml](.github/workflows/pytest.yml)
- [docs/design/2026-04-20-v3.4-prisma-trAIce-raise-readcheck-design.md](docs/design/2026-04-20-v3.4-prisma-trAIce-raise-readcheck-design.md)
- [docs/design/2026-04-22-ars-v3.7.3-reading-check-probe-design.md](docs/design/2026-04-22-ars-v3.7.3-reading-check-probe-design.md)
- [docs/design/2026-04-23-ars-v3.6.2-sprint-contract-design.md](docs/design/2026-04-23-ars-v3.6.2-sprint-contract-design.md)
- [docs/design/2026-04-26-ars-v3.6.5-consumer-integration-design.md](docs/design/2026-04-26-ars-v3.6.5-consumer-integration-design.md)
- [docs/design/2026-04-27-ars-v3.6.5.2-claude-ai-method-4a-scope-implementation-brief.md](docs/design/2026-04-27-ars-v3.6.5.2-claude-ai-method-4a-scope-implementation-brief.md)
- [docs/design/2026-04-27-ars-v3.6.6-generator-evaluator-contract-design.md](docs/design/2026-04-27-ars-v3.6.6-generator-evaluator-contract-design.md)
- [docs/design/2026-05-14-ai-disclosure-impl-spec.md](docs/design/2026-05-14-ai-disclosure-impl-spec.md)
- [docs/design/2026-05-15-issue-103-claim-alignment-audit-decision.md](docs/design/2026-05-15-issue-103-claim-alignment-audit-decision.md)
- [docs/design/2026-05-15-issue-103-claim-alignment-audit-spec.md](docs/design/2026-05-15-issue-103-claim-alignment-audit-spec.md)
- [docs/design/2026-05-18-ars-v3.9.2-phase-boundary-spec.md](docs/design/2026-05-18-ars-v3.9.2-phase-boundary-spec.md)
- [scripts/adapters/tests/test_check_corpus_consumer_protocol.py](scripts/adapters/tests/test_check_corpus_consumer_protocol.py)
- [scripts/check_corpus_consumer_protocol.py](scripts/check_corpus_consumer_protocol.py)
- [scripts/test_check_spec_consistency.py](scripts/test_check_spec_consistency.py)

</details>



The Academic Research Skills (ARS) system maintains high architectural integrity and prevents prompt drift through a multi-layered CI/CD and Quality Infrastructure. This framework ensures that agents in the ecosystem adhere to strict data contracts, versioning rules, and performance budgets. The infrastructure is divided into automated consistency checks, a comprehensive test suite, and a specialized audit system for cross-model verification.

For details on GitHub Actions workflows, prompt linting, and version consistency, see [Spec Consistency CI and Prompt Linting](#11.1). For details on the cross-model audit infrastructure, see [Audit Artifact System](#11.2). For details on requirements, pytest manifests, and local validation scripts, see [Developer Environment and Test Suite](#11.3).

## High-Level Infrastructure Overview

The quality stack bridges the gap between Natural Language (agent prompts) and Code (validators and schemas). It ensures that changes to markdown-based agent prompts do not violate underlying system invariants.

### Quality Infrastructure Components

| Component | Purpose | Key Code Entities |
|:---|:---|:---|
| **Spec Consistency CI** | Validates agent prompts against schemas and versioning rules. | [.github/workflows/spec-consistency.yml:1-5]() |
| **Pytest Suite** | Unit and integration tests for script-based validators and adapters. | [.github/workflows/pytest.yml:1-10]() |
| **Script Validators** | Specialized Python tools that enforce specific architectural patterns. | `scripts/check_spec_consistency.py`, `scripts/check_version_consistency.py` |
| **Audit Artifact System** | Cross-model verification infrastructure for deliverable quality. | `shared/contracts/passport/claim_audit_result.schema.json` |

### System Quality Flow

The following diagram illustrates how the CI/CD infrastructure bridges the "Natural Language Space" of agent prompts with the "Code Entity Space" of validators and schemas.

**Diagram: ARS Quality Bridge**
```mermaid
graph TD
    subgraph "Natural-Language-Space"
        ["pipeline_orchestrator_agent.md"]
        ["formatter_agent.md"]
        ["bibliography_agent.md"]
    end

    subgraph "Validation-Layer-Python"
        ["check_spec_consistency.py"]
        ["check_version_consistency.py"]
        ["check_394_submission_policy.py"]
        ["test_v3_6_7_phase_6_6.py"]
    end

    subgraph "Infrastructure-GHA-Schemas"
        ["spec-consistency.yml"]
        ["claim_audit_result.schema.json"]
        ["terminal_policies.schema.json"]
    end

    ["pipeline_orchestrator_agent.md"] -- "Line Budget/Phase IDs" --> ["test_v3_6_7_phase_6_6.py"]
    ["formatter_agent.md"] -- "Refusal Rules" --> ["check_394_submission_policy.py"]
    ["check_spec_consistency.py"] -- "Enforces" --> ["pipeline_orchestrator_agent.md"]
    ["spec-consistency.yml"] -- "Triggers" --> ["check_spec_consistency.py"]
    ["spec-consistency.yml"] -- "Triggers" --> ["check_version_consistency.py"]
    ["test_v3_6_7_phase_6_6.py"] -- "References" --> ["claim_audit_result.schema.json"]
    ["check_394_submission_policy.py"] -- "Validates" --> ["terminal_policies.schema.json"]
```
Sources: [.github/workflows/spec-consistency.yml:1-85](), [scripts/test_v3_6_7_phase_6_6.py:1-30](), [scripts/check_394_submission_policy.py:1-30]()

---

## Spec Consistency CI and Prompt Linting

The core of the ARS quality gate is the `spec-consistency` workflow. Unlike traditional CI that only checks code, this workflow lints agent markdown files to ensure they remain synchronized with design specifications and line-budget constraints.

For full documentation on GitHub Actions workflows, `check_spec_consistency.py`, prompt drift prevention, and release-governance workflows, see **[Spec Consistency CI and Prompt Linting](#11.1)**.

Sources: [.github/workflows/spec-consistency.yml:46-76](), [scripts/check_version_consistency.py:2-40](), [scripts/test_v3_6_7_phase_6_6.py:69-82]()

---

## Audit Artifact System

The Audit Artifact System is a cross-model infrastructure designed to verify the faithfulness and integrity of research outputs. It acts as a hard gate within the pipeline, particularly between Stage 4 and Stage 5, validating claim-reference alignment against retrieved reference text.

For details on artifact bundles, invariant families, audit schemas, and audit records, see **[Audit Artifact System](#11.2)**.

Sources: [docs/design/2026-05-15-issue-103-claim-alignment-audit-decision.md:28-31](), [docs/design/2026-05-15-issue-103-claim-alignment-audit-spec.md:44-71](), [academic-paper/agents/formatter_agent.md:118-130]()

---

## Script Validators and Pytest Suite

The system uses a suite of Python-based validators and pytest configurations to manage complex integrations and enforce architectural boundaries across all components.

### Validator Responsibilities

| Validator Script | Responsibility |
|:---|:---|
| `scripts/check_394_submission_policy.py` | Enforces submission-package terminality across schema, orchestrator, and formatter [scripts/check_394_submission_policy.py:2-9](). |
| `scripts/check_version_consistency.py` | Validates outward-facing agent-counts and release-note minimum lengths [scripts/check_version_consistency.py:29-37](). |
| `scripts/check_spec_consistency.py` | Validates relative markdown link grammar and version block parity [scripts/test_check_spec_consistency.py:18-37](). |

**Diagram: Version and Policy Validation**
This diagram shows how CI execution targets code entities and configuration schemas.

```mermaid
graph LR
    subgraph "CI-Runner"
        ["spec-consistency.yml"]
    end

    subgraph "Validators"
        ["check_version_consistency.py"]
        ["check_394_submission_policy.py"]
        ["run_ci_pytest_manifest.py"]
    end

    subgraph "Target-Entities"
        ["CLAUDE.md"]
        ["CHANGELOG.md"]
        ["terminal_policies.schema.json"]
        ["_ci_pytest_manifest.toml"]
    end

    ["spec-consistency.yml"] -- "Executes" --> ["check_version_consistency.py"]
    ["spec-consistency.yml"] -- "Executes" --> ["check_394_submission_policy.py"]
    ["spec-consistency.yml"] -- "Executes" --> ["run_ci_pytest_manifest.py"]

    ["check_version_consistency.py"] -- "Syncs" --> ["CLAUDE.md"]
    ["check_version_consistency.py"] -- "Syncs" --> ["CHANGELOG.md"]
    ["check_394_submission_policy.py"] -- "Validates" --> ["terminal_policies.schema.json"]
    ["run_ci_pytest_manifest.py"] -- "Consumes" --> ["_ci_pytest_manifest.toml"]
```
Sources: [.github/workflows/pytest.yml:1-62](), [.github/workflows/spec-consistency.yml:46-157](), [scripts/check_version_consistency.py:2-38](), [scripts/check_394_submission_policy.py:10-30]()

For complete instructions on running pytest suites, dev environment setup, and script validators locally, see **[Developer Environment and Test Suite](#11.3)**.

---

