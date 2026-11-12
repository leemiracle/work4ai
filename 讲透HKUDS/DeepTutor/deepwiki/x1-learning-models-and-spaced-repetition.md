<!-- source: DeepWiki mcp.deepwiki.com · repo HKUDS/DeepTutor · extra page Learning Models and Spaced Repetition · fetched 2026-11-09 -->

# Learning Models and Spaced Repetition

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [deeptutor/api/routers/mastery_path.py](deeptutor/api/routers/mastery_path.py)
- [deeptutor/capabilities/mastery/loop.py](deeptutor/capabilities/mastery/loop.py)
- [deeptutor/capabilities/mastery/prompts/en/mastery_loop.yaml](deeptutor/capabilities/mastery/prompts/en/mastery_loop.yaml)
- [deeptutor/capabilities/mastery/prompts/zh/mastery_loop.yaml](deeptutor/capabilities/mastery/prompts/zh/mastery_loop.yaml)
- [deeptutor/capabilities/mastery/tools.py](deeptutor/capabilities/mastery/tools.py)
- [deeptutor/learning/mastery.py](deeptutor/learning/mastery.py)
- [deeptutor/learning/models.py](deeptutor/learning/models.py)
- [deeptutor/learning/policy.py](deeptutor/learning/policy.py)
- [deeptutor/learning/question_card.py](deeptutor/learning/question_card.py)
- [deeptutor/learning/scheduler.py](deeptutor/learning/scheduler.py)
- [deeptutor/learning/semantic_assessment.py](deeptutor/learning/semantic_assessment.py)
- [deeptutor/learning/service.py](deeptutor/learning/service.py)
- [deeptutor/learning/storage.py](deeptutor/learning/storage.py)
- [deeptutor/learning/teaching.py](deeptutor/learning/teaching.py)
- [deeptutor/learning/tests/test_api_endpoints.py](deeptutor/learning/tests/test_api_endpoints.py)
- [deeptutor/learning/tests/test_guided_mastery_updates.py](deeptutor/learning/tests/test_guided_mastery_updates.py)
- [deeptutor/learning/tests/test_mastery_tools.py](deeptutor/learning/tests/test_mastery_tools.py)
- [deeptutor/learning/tests/test_models.py](deeptutor/learning/tests/test_models.py)
- [deeptutor/learning/tests/test_policy.py](deeptutor/learning/tests/test_policy.py)
- [deeptutor/learning/tests/test_scheduler.py](deeptutor/learning/tests/test_scheduler.py)
- [deeptutor/learning/tests/test_storage.py](deeptutor/learning/tests/test_storage.py)
- [tests/api/test_mastery_path_reviews.py](tests/api/test_mastery_path_reviews.py)
- [tests/capabilities/test_mastery_capability.py](tests/capabilities/test_mastery_capability.py)
- [tests/capabilities/test_mastery_profile_continuity.py](tests/capabilities/test_mastery_profile_continuity.py)
- [tests/capabilities/test_mastery_semantic_assessment.py](tests/capabilities/test_mastery_semantic_assessment.py)
- [tests/capabilities/test_mastery_teaching_compass.py](tests/capabilities/test_mastery_teaching_compass.py)
- [tests/capabilities/test_mastery_teaching_focus.py](tests/capabilities/test_mastery_teaching_focus.py)
- [web/app/(workspace)/learning/page.tsx](web/app/(workspace)/learning/page.tsx)
- [web/lib/learning-api.ts](web/lib/learning-api.ts)

</details>



The Mastery Path learning engine in DeepTutor manages personalized, adaptive learning progress and spaced repetition reviews. It employs a set of core Pydantic models to represent curriculum structure and learner state, a scheduler for spaced repetition intervals, and a transactional SQLite-backed storage layer to guarantee ACID compliance and concurrency safety. This page provides full technical details on these components, their implementation, data flows, and code structures.

Sources: `deeptutor/learning/models.py:1-209](), `deeptutor/learning/storage.py:1-50](), `deeptutor/learning/scheduler.py:1-35]()

---

## Core Data Models

All learning-related domain models are defined as Pydantic `BaseModel` subclasses in `deeptutor/learning/models.py`. These models encapsulate knowledge points, modules, learner progress, interactions, error records, and spaced repetition states.

### Enumerations and Legacy Compatibility

- **`KnowledgeType`**: Enumerates types of knowledge elements (`memory`, `concept`, `procedure`, `design`). Legacy string mappings in `_KNOWLEDGE_TYPE_LEGACY` support backward compatibility [deeptutor/learning/models.py:10-35]().
- **`ErrorType`**: Categorizes learner errors into structural, deviation, application, and metacognitive types, with legacy mapping support [deeptutor/learning/models.py:17-47]().
- **`LearningStage`**: Defines mastery path lifecycle stages: `DIAGNOSTIC`, `EXPLAIN`, `FEYNMAN_CHECK`, `PRACTICE`, `ERROR_DIAGNOSIS`, `REVIEW`, and `COMPLETED`. Legacy stage names are remapped via `_STAGE_LEGACY` [deeptutor/learning/models.py:51-78]().
- **`InteractionStatus`**: Manages interaction lifecycles (`REGISTERED`, `AWAITING_INPUT`, `ANSWERED`, `GRADED`, `ABANDONED`) [deeptutor/learning/storage.py:54-78]().

### Primary Pydantic Classes

| Class Name | File Location | Description |
|------------|--------------|-------------|
| `KnowledgePoint` | `deeptutor/learning/models.py:80-97]()` | Granular learning objective with `id`, `name`, `type`, `module_id`, `prerequisite_ids`, and source metadata. |
| `LearningModule` | `deeptutor/learning/models.py:98-113]()` | Container grouping knowledge points with `order`, `pass_threshold`, and `objective` summary. |
| `LearningProgress` | `deeptutor/learning/models.py` | Aggregate root storing modules, mastery levels, repetition states, error records, and review queues. |
| `QuizAttempt` | `deeptutor/learning/models.py:123-148]()` | Records individual quiz attempts with correctness, result state, user answer, error classification, and void flags. |
| `ErrorRecord` | `deeptutor/learning/models.py:158-171]()` | Tracks persistent learning errors linked to knowledge points, retry history, and status. |
| `LearningEvidence` | `deeptutor/learning/models.py:173-201]()` | Durable review/assessment event used to recompute retention state. |
| `RepetitionState` | `deeptutor/learning/models.py:202-215]()` | Encapsulates spaced repetition scheduling parameters (interval index, stability, difficulty, due dates). |
| `MasteryInteraction` | `deeptutor/learning/storage.py:35-36]()` | Durably stores questions and answers for idempotency and lifecycle tracking. |

Sources: `deeptutor/learning/models.py:10-215](), `deeptutor/learning/storage.py:31-45]()

---

## Spaced Repetition Scheduler

The spaced repetition system adapts review timing based on knowledge type and learner performance, implemented via `SpacedRepetitionScheduler` in `deeptutor/learning/scheduler.py`.

### Interval Sequences by Knowledge Type

Each `KnowledgeType` maps to a predefined sequence of review intervals in days (or seconds in debug mode):

| Knowledge Type | Default Interval Sequence (Days) |
|----------------|----------------------------------|
| `KnowledgeType.MEMORY` | `[0, 1, 3, 7, 14, 30, 60]` [deeptutor/learning/scheduler.py:18]() |
| `KnowledgeType.CONCEPT` | `[3, 7, 14, 30]` [deeptutor/learning/scheduler.py:19]() |
| `KnowledgeType.PROCEDURE` | `[3, 7, 14]` [deeptutor/learning/scheduler.py:20]() |
| `KnowledgeType.DESIGN` | `[14, 28]` [deeptutor/learning/scheduler.py:21]() |

Sources: `deeptutor/learning/scheduler.py:17-22]()

### Scheduling Mechanics and Retention Tuning

- **`validate_desired_retention`**: Ensures desired retention bounds are strictly maintained between `0.7` and `0.99`, defaulting to `0.9` [deeptutor/learning/scheduler.py:57-82]().
- **Stability & Interval Conversion**: The scheduler computes stability and intervals using exponential forgetting models (`_stability_from_interval`, `_interval_from_stability`) [deeptutor/learning/scheduler.py:178-188]().
- **Review Queue Construction**: `build_review_queue` generates due tasks sorted by forgetting risk, overdue duration, and type priority (`review_sort_key`) [deeptutor/learning/scheduler.py:118-145]().

Sources: `deeptutor/learning/scheduler.py:57-194]()

---

## Mastery Calculation Policy

Mastery quantification is handled via recency-weighted grading rules integrated through `LearningService` [deeptutor/learning/service.py:8-9]() and companion policy modules [deeptutor/learning/policy.py](). 

- Correct answers increment the mastery score while respecting confidence limits.
- Partial correctness, hints usage, and error records factor into the composite mastery computation.
- Objectives must clear explicit gates defined in `gate_threshold` before advancement is permitted [deeptutor/capabilities/mastery/tools.py:69-81]()

Sources: `deeptutor/learning/service.py:8-10](), `deeptutor/capabilities/mastery/tools.py:69-81]()

---

## Storage Transactions and Data Migration

Durable learner progress is managed by `LearningStore` and `LearningTransaction` in `deeptutor/learning/storage.py`, utilizing workspace-scoped SQLite databases with real compare-and-swap (CAS) revision checks [deeptutor/learning/storage.py:1-13]().

### Transactional Unit of Work (`LearningTransaction`)

- **Atomicity**: `LearningTransaction` bundles state mutation, interaction row updates, and event emission into a single SQLite transaction [deeptutor/learning/storage.py:109-128]().
- **Concurrency Control**: Stale aggregates attempting to overwrite changes trigger a `LearningConflictError` based on revision mismatches [deeptutor/learning/storage.py:85-96]().
- **Lease Management**: `PathLeaseConflictError` prevents concurrent mutation races across multiple tutoring sessions [deeptutor/learning/storage.py:98-106]().

### Legacy Migration

On store initialization, legacy JSON files (`<path-id>.json`) are lazily imported, mapped into the SQLite aggregate schema, committed, and archived under `.legacy/` [deeptutor/learning/storage.py:9-13]().

Sources: `deeptutor/learning/storage.py:1-193]()

---

## Data Flow and Architecture Diagrams

### Diagram: Model Composition and Persistence Architecture
This diagram bridges natural language concepts (`LearningProgress`, `LearningTransaction`) to code entities in `deeptutor/learning/models.py` and `deeptutor/learning/storage.py`.

```mermaid
title "Model Composition and SQLite Persistence"
graph TD
    LP["LearningProgress (deeptutor/learning/models.py)"] --> LM["LearningModule"]
    LM --> KP["KnowledgePoint"]
    LP --> ER["ErrorRecord"]
    LP --> RS["RepetitionState"]
    LP --> PQ["PendingQuestion"]
    
    LS["LearningStore (deeptutor/learning/storage.py)"] --> LTX["LearningTransaction"]
    LTX --> LP
    LTX --> DB[("mastery.sqlite3 (Workspace DB)")]
```

Sources: `deeptutor/learning/models.py:80-215](), `deeptutor/learning/storage.py:109-130]()

### Diagram: Spaced Repetition and Grading Pipeline
This diagram traces the flow from incoming client actions through the `LearningService` and scheduler classes to the SQLite persistence backend.

```mermaid
title "Grading and Spaced Repetition Pipeline Flow"
graph TD
    Client["Client / WebSocket (unified_ws.py)"] --> Svc["LearningService (deeptutor/learning/service.py)"]
    Svc --> Mst["compute_mastery (mastery.py)"]
    Svc --> Sch["SpacedRepetitionScheduler (scheduler.py)"]
    Sch --> RS["RepetitionState"]
    Svc --> Store["LearningStore.mutate (storage.py)"]
    Store --> DB[("mastery.sqlite3")]
```

Sources: `deeptutor/learning/service.py:1-36](), `deeptutor/learning/scheduler.py:147-194](), `deeptutor/learning/storage.py:1-50]()

---

### Summary

- Pydantic models in `deeptutor/learning/models.py` define the core curriculum and learner state.
- `SpacedRepetitionScheduler` schedules review intervals based on knowledge types and retention targets.
- `LearningStore` and `LearningTransaction` enforce ACID compliance, concurrency leases, and CAS checks over SQLite.
- Legacy progress formats migrate seamlessly upon initialization.

Sources: `deeptutor/learning/models.py:1-215](), `deeptutor/learning/scheduler.py:1-194](), `deeptutor/learning/storage.py:1-193]()

---

