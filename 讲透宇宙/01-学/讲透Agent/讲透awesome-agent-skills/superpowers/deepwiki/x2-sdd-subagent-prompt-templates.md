<!-- source: DeepWiki mcp.deepwiki.com · repo obra/superpowers · extra page SDD Subagent Prompt Templates · fetched 2026-10-26 -->

# SDD Subagent Prompt Templates

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docs/superpowers/plans/2026-06-09-sdd-task-scoped-review-dispatch.md](docs/superpowers/plans/2026-06-09-sdd-task-scoped-review-dispatch.md)
- [docs/superpowers/specs/2026-06-09-sdd-task-scoped-review-dispatch-design.md](docs/superpowers/specs/2026-06-09-sdd-task-scoped-review-dispatch-design.md)
- [skills/brainstorming/spec-document-reviewer-prompt.md](skills/brainstorming/spec-document-reviewer-prompt.md)
- [skills/subagent-driven-development/SKILL.md](skills/subagent-driven-development/SKILL.md)
- [skills/subagent-driven-development/implementer-prompt.md](skills/subagent-driven-development/implementer-prompt.md)
- [skills/subagent-driven-development/re-review-prompt.md](skills/subagent-driven-development/re-review-prompt.md)
- [skills/subagent-driven-development/task-reviewer-prompt.md](skills/subagent-driven-development/task-reviewer-prompt.md)

</details>



This page details the prompt templates used by subagents in the Subagent-Driven Development (SDD) workflow. It covers `implementer-prompt.md`, `task-reviewer-prompt.md`, and `re-review-prompt.md`, explaining their purpose, structure, and the contract for status reporting and TDD evidence. These templates are crucial for guiding the behavior of AI subagents during the implementation and review phases of a task.

## Implementer Subagent Prompt Template

The `implementer-prompt.md` template [skills/subagent-driven-development/implementer-prompt.md]() is used when dispatching an implementer subagent for a specific task. Its primary goal is to provide clear instructions, context, and expectations for the implementation phase.

### Structure and Purpose

The prompt guides the implementer through the following stages:
1.  **Task Description**: Directs the subagent to read the task brief [skills/subagent-driven-development/implementer-prompt.md:13-14]().
2.  **Context**: Provides scene-setting information, dependencies, and architectural context [skills/subagent-driven-development/implementer-prompt.md:19-20]().
3.  **Pre-work Questions**: Encourages the subagent to ask clarifying questions before starting implementation [skills/subagent-driven-development/implementer-prompt.md:23-30]().
4.  **Job Steps**: Outlines the core responsibilities: implement, test, verify, commit, self-review, and report [skills/subagent-driven-development/implementer-prompt.md:33-40]().
5.  **No Subagent Dispatch**: Explicitly forbids the implementer from spawning other subagents for implementation or review [skills/subagent-driven-development/implementer-prompt.md:50-59]().
6.  **Code Organization Guidelines**: Provides principles for maintaining code quality, following plan structure, and handling large files [skills/subagent-driven-development/implementer-prompt.md:62-73]().
7.  **Escalation Policy**: Defines conditions under which the implementer should stop and escalate, and how to do so [skills/subagent-driven-development/implementer-prompt.md:76-90]().
8.  **Self-Review**: Instructs the implementer to perform a thorough self-review covering completeness, quality, discipline, and testing before reporting [skills/subagent-driven-development/implementer-prompt.md:93-118]().
9.  **Fix Round Instructions**: Details how to handle findings from a task review, including re-running tests and appending fix reports [skills/subagent-driven-development/implementer-prompt.md:120-126]().
10. **Report Format**: Specifies the detailed report content to be written to `[REPORT_FILE]` and the concise status contract for the final message [skills/subagent-driven-development/implementer-prompt.md:129-154]().

### Status Contract and TDD Evidence

The implementer's final report adheres to a strict status contract:
-   **Status**: `DONE | DONE_WITH_CONCERNS | BLOCKED | NEEDS_CONTEXT` [skills/subagent-driven-development/implementer-prompt.md:142]().
-   **Commits created**: Short SHA and subject [skills/subagent-driven-development/implementer-prompt.md:143]().
-   **One-line test summary**: e.g., "14/14 passing, output pristine" [skills/subagent-driven-development/implementer-prompt.md:144]().
-   **Concerns**: If any [skills/subagent-driven-development/implementer-prompt.md:145]().
-   **Report file path**: Path to the detailed report [skills/subagent-driven-development/implementer-prompt.md:146]().

If Test-Driven Development (TDD) is required for the task, the report must include explicit TDD evidence:
-   **RED**: Command run, relevant failing output before implementation, and why the failure was expected [skills/subagent-driven-development/implementer-prompt.md:134-135]().
-   **GREEN**: Command run and relevant passing output after implementation [skills/subagent-driven-development/implementer-prompt.md:136]().

This evidence ensures that tests were written before the code and that they correctly validate the implemented functionality.

```mermaid
graph TD
    A[Controller Dispatches Implementer] --> B{Implementer Reads Task Brief};
    B --> C{Questions?};
    C -- Yes --> D[Ask Questions];
    D --> E[Receive Context];
    C -- No --> E;
    E --> F[Implement Task];
    F --> G[Write Tests (TDD if required)];
    G --> H[Verify Implementation];
    H --> I[Commit Work];
    I --> J[Self-Review];
    J --> K{Issues Found?};
    K -- Yes --> F;
    K -- No --> L[Write Detailed Report to REPORT_FILE];
    L --> M[Report Status Contract to Controller];
    M -- Status: DONE --> N[Task Complete];
    M -- Status: DONE_WITH_CONCERNS --> O[Task Complete with Concerns];
    M -- Status: BLOCKED/NEEDS_CONTEXT --> P[Escalate to Controller];

    subgraph Implementer's Report (REPORT_FILE)
        LR[What Implemented] --> LR1[What Tested & Results];
        LR1 --> LR2[TDD Evidence (RED/GREEN)];
        LR2 --> LR3[Files Changed];
        LR3 --> LR4[Self-Review Findings];
        LR4 --> LR5[Issues/Concerns];
    end

    subgraph Implementer's Final Message (Status Contract)
        FM[Status] --> FM1[Commits Created];
        FM1 --> FM2[Test Summary];
        FM2 --> FM3[Concerns];
        FM3 --> FM4[Report File Path];
    end
```
**Diagram: Implementer Subagent Workflow and Reporting**
Sources:
- [skills/subagent-driven-development/implementer-prompt.md]()

## Task Reviewer Prompt Template

The `task-reviewer-prompt.md` template [skills/subagent-driven-development/task-reviewer-prompt.md]() is used to dispatch a subagent responsible for reviewing a single task's implementation. This review is a critical gate, focusing on both spec compliance and code quality.

### Structure and Purpose

The task reviewer prompt guides the subagent through a structured review process:
1.  **Purpose**: Clearly states the goal: verify spec compliance and code quality for one task [skills/subagent-driven-development/task-reviewer-prompt.md:7-8]().
2.  **What Was Requested**: Directs the reviewer to the task brief and global constraints [skills/subagent-driven-development/task-reviewer-prompt.md:22-27]().
3.  **What the Implementer Claims**: Points to the implementer's report, with a strong caution not to trust it blindly [skills/subagent-driven-development/task-reviewer-prompt.md:30-31]().
4.  **Diff Under Review**: Provides `BASE_SHA`, `HEAD_SHA`, and the `DIFF_FILE`, emphasizing a single read of the diff and limited scope outside it [skills/subagent-driven-development/task-reviewer-prompt.md:34-53]().
5.  **No Subagent Dispatch**: Explicitly forbids the reviewer from spawning other subagents for review [skills/subagent-driven-development/task-reviewer-prompt.md:56-63]().
6.  **Do Not Trust the Report**: Reinforces skepticism towards the implementer's claims and rationales [skills/subagent-driven-development/task-reviewer-prompt.md:66-72]().
7.  **Tests**: Instructs the reviewer not to re-run tests unless specific doubts arise, and to focus on the implementer's reported TDD evidence [skills/subagent-driven-development/task-reviewer-prompt.md:75-93]().
8.  **Part 1: Spec Compliance**: Details checks for missing, extra, or misunderstood requirements, including file-by-file verification for batched dispatches [skills/subagent-driven-development/task-reviewer-prompt.md:96-114]().
9.  **Part 2: Code Quality**: Covers aspects like separation of concerns, error handling, DRY principles, edge cases, test quality, and code structure [skills/subagent-driven-development/task-reviewer-prompt.md:117-134]().
10. **Report Format**: Specifies that the final message is the report itself, starting directly with the spec-compliance verdict, with file:line references for findings [skills/subagent-driven-development/task-reviewer-prompt.md:137-143]().
11. **Calibration**: Guides the reviewer on categorizing issues by severity (Important, Minor) [skills/subagent-driven-development/task-reviewer-prompt.md:146-153]().

### Reviewer Verdicts and Findings

The task reviewer provides two main verdicts:
-   **Spec Compliance**: Assesses if the implementation matches requirements (Missing, Extra, Misunderstood) [skills/subagent-driven-development/task-reviewer-prompt.md:96-103]().
-   **Code Quality**: Evaluates the build quality, test effectiveness, and code structure [skills/subagent-driven-development/task-reviewer-prompt.md:117-134]().

Findings are categorized by severity:
-   **Important**: Incorrect/fragile behavior, missed requirements, maintainability damage (e.g., verbatim duplication, swallowed errors, assertion-free tests) [skills/subagent-driven-development/task-reviewer-prompt.md:148-152]().
-   **Minor**: Polish suggestions, broader coverage recommendations [skills/subagent-driven-development/task-reviewer-prompt.md:152]().

The design of this prompt evolved through several cost iterations to optimize for efficiency and quality, merging spec and quality reviews into a single subagent dispatch [docs/superpowers/specs/2026-06-09-sdd-task-scoped-review-dispatch-design.md:55-58]().

```mermaid
graph TD
    A[Controller Dispatches Task Reviewer] --> B{Reviewer Reads Task Brief & Global Constraints};
    B --> C{Reviewer Reads Implementer's Report (Skeptically)};
    C --> D[Reviewer Reads Diff File Once];
    D --> E{Part 1: Spec Compliance Check};
    E -- Findings --> F[Report Spec Compliance Findings (Missing, Extra, Misunderstood)];
    E -- No Findings --> G[Spec Compliance Approved];
    F --> H{Part 2: Code Quality Check};
    G --> H;
    H -- Findings --> I[Report Code Quality Findings (Code, Tests, Structure)];
    H -- No Findings --> J[Code Quality Approved];
    I --> K[Categorize Findings by Severity (Important, Minor)];
    J --> K;
    K --> L[Final Report: Spec Verdict + Quality Verdict + Findings (file:line)];

    subgraph Reviewer's Scope
        RS1[Task Brief]
        RS2[Global Constraints]
        RS3[Implementer's Report]
        RS4[Diff File (BASE_SHA..HEAD_SHA)]
    end

    subgraph Reviewer's Output
        RO1[Spec Compliance Verdict]
        RO2[Code Quality Verdict]
        RO3[Findings (file:line, severity)]
    end

    RS1 --> B; RS2 --> B; RS3 --> C; RS4 --> D;
    L --> RO1; L --> RO2; L --> RO3;
```
**Diagram: Task Reviewer Subagent Workflow**
Sources:
- [skills/subagent-driven-development/task-reviewer-prompt.md]()
- [docs/superpowers/specs/2026-06-09-sdd-task-scoped-review-dispatch-design.md]()

## Re-Review Prompt Template

The `re-review-prompt.md` template [skills/subagent-driven-development/re-review-prompt.md]() is used when dispatching a subagent to re-review a task after a fix round. Its purpose is narrowly scoped: verify that previous findings have been addressed and that the fix itself did not introduce new issues.

### Structure and Purpose

The re-reviewer prompt guides the subagent through a focused verification process:
1.  **Purpose**: Verify each finding was addressed and the fix introduced no new breakage [skills/subagent-driven-development/re-review-prompt.md:7-8]().
2.  **The Task**: Directs the reviewer to the task brief for context [skills/subagent-driven-development/re-review-prompt.md:22-23]().
3.  **Findings Under Verification**: Provides the verbatim list of findings from the previous review [skills/subagent-driven-development/re-review-prompt.md:26-27]().
4.  **The Fix**: Points to the implementer's report (which includes appended fix reports) and the fix diff details (`FIX_BASE_SHA`, `HEAD_SHA`, `DIFF_FILE`) [skills/subagent-driven-development/re-review-prompt.md:30-42]().
5.  **No Subagent Dispatch**: Explicitly forbids spawning other subagents [skills/subagent-driven-development/re-review-prompt.md:45-54]().
6.  **Scope**: Emphasizes that the scope is limited to the findings list and the fix diff. Issues outside the fix diff are noted as "Out-of-Scope Observations" and do not block the task [skills/subagent-driven-development/re-review-prompt.md:57-63]().
7.  **Tests**: Instructs the reviewer to confirm the implementer's reported test results for the fix, but not to re-run tests unless specific doubts arise [skills/subagent-driven-development/re-review-prompt.md:66-72]().
8.  **Output Format**: Specifies the report structure: per-finding verdicts, new breakage in the fix diff, out-of-scope observations, and a final round verdict [skills/subagent-driven-development/re-review-prompt.md:75-101]().

### Re-Reviewer Verdicts

The re-reviewer provides the following verdicts:
-   **Finding Verdicts**: For each original finding, states `ADDRESSED` or `NOT ADDRESSED`, with file:line evidence [skills/subagent-driven-development/re-review-prompt.md:81-85]().
-   **New Breakage in the Fix Diff**: Reports any new issues introduced by the fix, with severity (Critical/Important/Minor) [skills/subagent-driven-development/re-review-prompt.md:88-90]().
-   **Out-of-Scope Observations**: Notes any issues found outside the fix diff, which are non-blocking [skills/subagent-driven-development/re-review-prompt.md:93-95]().
-   **Fix Round Verdict**: A summary verdict indicating if all findings were addressed with no new critical/important breakage, or if findings remain open [skills/subagent-driven-development/re-review-prompt.md:98-100]().

```mermaid
graph TD
    A[Controller Dispatches Re-Reviewer] --> B{Re-Reviewer Reads Task Brief};
    B --> C{Re-Reviewer Reads Previous Findings List};
    C --> D{Re-Reviewer Reads Implementer's Fix Report};
    D --> E[Re-Reviewer Reads Fix Diff (FIX_BASE_SHA..HEAD_SHA)];
    E --> F{Verify Each Finding: ADDRESSED / NOT ADDRESSED};
    F --> G{Inspect Fix Diff for New Breakage};
    G --> H{Identify Out-of-Scope Observations};
    H --> I[Generate Report];

    subgraph Re-Reviewer's Scope
        RRS1[Task Brief]
        RRS2[Previous Findings]
        RRS3[Implementer's Fix Report]
        RRS4[Fix Diff (FIX_BASE_SHA..HEAD_SHA)]
    end

    subgraph Re-Reviewer's Output
        RRO1[Per-Finding Verdicts]
        RRO2[New Breakage in Fix Diff (severity)]
        RRO3[Out-of-Scope Observations]
        RRO4[Fix Round Verdict]
    end

    RRS1 --> B; RRS2 --> C; RRS3 --> D; RRS4 --> E;
    I --> RRO1; I --> RRO2; I --> RRO3; I --> RRO4;
```
**Diagram: Re-Reviewer Subagent Workflow**
Sources:
- [skills/subagent-driven-development/re-review-prompt.md]()

---

