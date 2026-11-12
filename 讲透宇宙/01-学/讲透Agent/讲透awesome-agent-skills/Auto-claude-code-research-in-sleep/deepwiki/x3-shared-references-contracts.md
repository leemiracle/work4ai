<!-- source: DeepWiki mcp.deepwiki.com · repo wanshuiyin/Auto-claude-code-research-in-sleep · extra page Shared References & Contracts · fetched 2026-10-26 -->

# Shared References & Contracts

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [skills/paper-write/templates/IEEEtran.bst](skills/paper-write/templates/IEEEtran.bst)
- [skills/paper-write/templates/IEEEtran.cls](skills/paper-write/templates/IEEEtran.cls)
- [skills/paper-write/templates/ieee_conference.tex](skills/paper-write/templates/ieee_conference.tex)
- [skills/paper-write/templates/ieee_journal.tex](skills/paper-write/templates/ieee_journal.tex)
- [skills/shared-references/acceptance-gate.md](skills/shared-references/acceptance-gate.md)
- [skills/shared-references/assurance-contract.md](skills/shared-references/assurance-contract.md)
- [skills/shared-references/effort-contract.md](skills/shared-references/effort-contract.md)
- [skills/shared-references/evidence-precheck.md](skills/shared-references/evidence-precheck.md)
- [skills/shared-references/external-cadence.md](skills/shared-references/external-cadence.md)
- [skills/shared-references/fan-out-pattern.md](skills/shared-references/fan-out-pattern.md)
- [skills/shared-references/injection-hygiene.md](skills/shared-references/injection-hygiene.md)
- [skills/shared-references/venue-checklists.md](skills/shared-references/venue-checklists.md)
- [skills/skills-codex/shared-references/acceptance-gate.md](skills/skills-codex/shared-references/acceptance-gate.md)
- [skills/skills-codex/shared-references/assurance-contract.md](skills/skills-codex/shared-references/assurance-contract.md)
- [skills/skills-codex/shared-references/effort-contract.md](skills/skills-codex/shared-references/effort-contract.md)
- [skills/skills-codex/shared-references/external-cadence.md](skills/skills-codex/shared-references/external-cadence.md)
- [skills/skills-codex/shared-references/injection-hygiene.md](skills/skills-codex/shared-references/injection-hygiene.md)
- [skills/skills-codex/shared-references/review-tracing.md](skills/skills-codex/shared-references/review-tracing.md)
- [tests/test_evidence_check.py](tests/test_evidence_check.py)
- [tests/test_idea_creator_query_pack_scan.py](tests/test_idea_creator_query_pack_scan.py)
- [tests/test_threat_scan.py](tests/test_threat_scan.py)
- [tests/test_verify_paper_audits.py](tests/test_verify_paper_audits.py)
- [tools/evidence_check.py](tools/evidence_check.py)
- [tools/threat_scan.py](tools/threat_scan.py)
- [tools/verify_paper_audits.sh](tools/verify_paper_audits.sh)

</details>



This leaf page documents the foundational system contracts, shared behavioral references, and deterministic gate architectures located in `skills/shared-references/`. These references govern cross-model interaction, audit strictness, threat scanning, state tracking, and execution governance across all 74+ composable ARIS skills.

Sources: `skills/shared-references/acceptance-gate.md:1-25`, `skills/shared-references/effort-contract.md:1-15` [skills/shared-references/acceptance-gate.md:1-25]()

---

## 1. Acceptance Gates & Model Sovereignty

The ARIS architecture enforces a strict separation between execution (generation/action) and acquittal (evaluation/stop decisions). The acceptance gate contract governs how autonomous loops (`/auto-review-loop`, `/dse-loop`, `/experiment-bridge`) terminate.

### Type-A vs. Type-B Gates
Autonomous stop/accept conditions are classified into two disjoint categories:
*   **Type-A (Execution / Objective):** Machine-checkable signals of what happened, requiring no subjective taste. Examples include `exit code == 0`, file existence (`paper/main.pdf`), queue exhaustion, or test suite passes (`pytest`). Claude may self-judge Type-A gates.
*   **Type-B (Quality / Correctness / Acceptance):** Judgments of merit, novelty, or sufficiency (e.g., "the paper is good", "the proof is valid", "the claim is supported"). Claude is **strictly prohibited** from self-judging Type-B gates. These must be routed to a heterogeneous model family (default `codex` via MCP, `oracle-pro`, or verified non-Claude backends).

```
                 ┌──────────────────────────────────────────────┐
                 │         Autonomous Loop Termination          │
                 └──────────────────────┬───────────────────────┘
                                        │
                        Is it an objective execution check?
                                   /           \
                                 Yes            No
                                 /                \
                       ┌────────▼───────┐        ┌▼─────────────────────────┐
                       │    Type-A      │        │          Type-B          │
                       │ (Same-Family   │        │   (Cross-Model Jury)     │
                       │  Self-Check OK)│        │   tools/verify_paper_audits.sh │
                       └────────────────┘        └──────────────────────────┘
```
**Diagram 1:** *Bridge from Natural Language Stop Conditions to Code Entity Space (`tools/verify_paper_audits.sh` and gate validation classes).*

Sources: `skills/shared-references/acceptance-gate.md:33-100`, `tools/verify_paper_audits.sh:1-40` [skills/shared-references/acceptance-gate.md:33-100]()

---

## 2. Effort & Assurance Contracts

The execution workload and audit rigor are decoupled into two orthogonal configuration axes: `effort` and `assurance`.

### The Two-Axis Configuration Model
*   **`effort` (`lite`, `balanced`, `max`, `beast`):** Controls compute depth, iteration counts, candidate breadth, and token budget. It scales numbers of papers read, ideas generated, and experimental seeds.
*   **`assurance` (`draft`, `submission`):** Controls whether audit phases are advisory (silent skip allowed) or load-bearing (mandatory verdicts required).

| Effort Level | Implied Assurance | Primary Target |
| :--- | :--- | :--- |
| `lite` | `draft` | Budget-constrained exploration (~0.4x tokens) |
| `balanced` | `draft` | Default ARIS behavior (1x tokens) |
| `max` | `submission` | Deep research runs (~2.5x tokens; audits mandatory) |
| `beast` | `submission` | Submission sprints (~5-8x tokens; verifier enforced) |

Sources: `skills/shared-references/effort-contract.md:29-65`, `skills/shared-references/assurance-contract.md:9-44` [skills/shared-references/effort-contract.md:29-65]()

### The External Verifier: `verify_paper_audits.sh`
At `assurance: submission`, paper compilation and finalization invoke the external verifier script `tools/verify_paper_audits.sh` to validate mandatory audit artifacts (`PROOF_AUDIT.json`, `PAPER_CLAIM_AUDIT.json`, `CITATION_AUDIT.json`, `KILL_ARGUMENT.json`).

```
             ┌────────────────────────────────────────────────────────┐
             │               paper-writing Phase 6                    │
             └───────────────────────────┬────────────────────────────┘
                                         │ invokes
                                         ▼
             ┌────────────────────────────────────────────────────────┐
             │       tools/verify_paper_audits.sh                     │
             │  - Validates JSON schemas & required fields            │
             │  - Recomputes SHA256 hashes (audited_input_hashes)     │
             │  - Checks review_independence and verdicts             │
             └───────────────────────────┬────────────────────────────┘
                                         │
                         Exits 0 (Pass)  OR  Exits 1 (Block)
```
**Diagram 2:** *External Verifier Execution Flow connecting natural language writing phases to shell verification (`tools/verify_paper_audits.sh`).*

Sources: `tools/verify_paper_audits.sh:1-35`, `skills/shared-references/assurance-contract.md:87-125` [tools/verify_paper_audits.sh:1-35]()

---

## 3. Injection Hygiene & Threat Scanning

ARIS re-injects external data (fetched paper abstracts, research wiki nodes/edges, community pull-request assets, and `MEMORY.md`) back into agent contexts. To prevent prompt injection and context hijacking, ARIS implements a two-layer scanning architecture.

### Two-Layer Defense Architecture
1.  **Layer 1 (`tools/threat_scan.py`):** Deterministic, regex-based pre-filter. It operates with zero model inference, failing open to novelty while aggressively blocking known-bad patterns (exfiltration URLs, privilege escalation commands, role-hijacks).
2.  **Layer 2 (Cross-Model Jury):** Semantic validation by a heterogeneous model family (`codex` or overlay backends).

Scopes are classified into `all`, `context` (warnings on fetched abstracts), and `strict` (quarantine/blocking on user-mediated writes like wiki edges and query packs).

Sources: `skills/shared-references/injection-hygiene.md:13-42`, `tests/test_idea_creator_query_pack_scan.py:1-40` [skills/shared-references/injection-hygiene.md:13-42]()

---

## 4. Review Tracing & External Cadence

### Review Tracing Protocol
Every reviewer call that performs critiquing, scoring, or claim verification writes a structured trace record under `.aris/traces/<skill-name>/<date>_run<NN>/`. These trace directories contain:
*   `run.meta.json`: Run identity, executor model, review independence status.
*   `NNN-<purpose>.request.json`: Full prompt, reasoning effort, and referenced file lists.
*   `NNN-<purpose>.response.md`: Verbatim reviewer output.
*   `NNN-<purpose>.meta.json`: Execution duration, agent/thread ID, and HTTP status.

Sources: `skills/skills-codex/shared-references/review-tracing.md:35-97` [skills/skills-codex/shared-references/review-tracing.md:35-97]()

### External Cadence Principle
External schedulers (`/loop`, `/schedule`, `CronCreate`) decide *when* an agent wakes up, but **never** *who* judges the work or *whether* an artifact is accepted. Cadence can drive execution flow, but acquittal remains strictly delegated to cross-model review. Wrapping internal semantic feedback loops (`/auto-review-loop`) in external timers introduces thread discontinuity and redundant context consumption.

Sources: `skills/shared-references/external-cadence.md:1-55` [skills/shared-references/external-cadence.md:1-55]()

---

