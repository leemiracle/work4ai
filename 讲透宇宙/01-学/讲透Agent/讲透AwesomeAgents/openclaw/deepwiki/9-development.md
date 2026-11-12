<!-- source: DeepWiki mcp.deepwiki.com · repo openclaw/openclaw · page 9 Development · fetched 2026-10-26 -->

# Development

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.agents/skills/auto-qa/SKILL.md](.agents/skills/auto-qa/SKILL.md)
- [.agents/skills/auto-qa/references/live-proof-routing.md](.agents/skills/auto-qa/references/live-proof-routing.md)
- [.agents/skills/control-ui-e2e/SKILL.md](.agents/skills/control-ui-e2e/SKILL.md)
- [.agents/skills/crabbox/SKILL.md](.agents/skills/crabbox/SKILL.md)
- [.agents/skills/openclaw-debugging/SKILL.md](.agents/skills/openclaw-debugging/SKILL.md)
- [.agents/skills/openclaw-pr-maintainer/SKILL.md](.agents/skills/openclaw-pr-maintainer/SKILL.md)
- [.agents/skills/openclaw-pr-maintainer/scripts/github-activity.sh](.agents/skills/openclaw-pr-maintainer/scripts/github-activity.sh)
- [.agents/skills/openclaw-repair-sweep/SKILL.md](.agents/skills/openclaw-repair-sweep/SKILL.md)
- [.agents/skills/openclaw-test-performance/SKILL.md](.agents/skills/openclaw-test-performance/SKILL.md)
- [.agents/skills/openclaw-testing/SKILL.md](.agents/skills/openclaw-testing/SKILL.md)
- [.agents/skills/release-openclaw-plugin-testing/SKILL.md](.agents/skills/release-openclaw-plugin-testing/SKILL.md)
- [.agents/skills/test-audit/SKILL.md](.agents/skills/test-audit/SKILL.md)
- [.github/CODEOWNERS](.github/CODEOWNERS)
- [AGENTS.md](AGENTS.md)
- [CONTRIBUTING.md](CONTRIBUTING.md)
- [extensions/memory-wiki/skills/wiki-maintainer/SKILL.md](extensions/memory-wiki/skills/wiki-maintainer/SKILL.md)
- [git-hooks/pre-commit](git-hooks/pre-commit)
- [scripts/AGENTS.md](scripts/AGENTS.md)
- [scripts/README.md](scripts/README.md)
- [scripts/github/dependency-guard.mjs](scripts/github/dependency-guard.mjs)
- [scripts/github/guard-shared.mjs](scripts/github/guard-shared.mjs)
- [scripts/github/security-sensitive-guard.mjs](scripts/github/security-sensitive-guard.mjs)
- [scripts/pr](scripts/pr)
- [scripts/pr-lib/clawsweeper-review-gate.mjs](scripts/pr-lib/clawsweeper-review-gate.mjs)
- [scripts/pr-lib/common.sh](scripts/pr-lib/common.sh)
- [scripts/pr-lib/gates.sh](scripts/pr-lib/gates.sh)
- [scripts/pr-lib/merge-outcome.sh](scripts/pr-lib/merge-outcome.sh)
- [scripts/pr-lib/merge.sh](scripts/pr-lib/merge.sh)
- [scripts/pr-lib/prepare-core.sh](scripts/pr-lib/prepare-core.sh)
- [scripts/pr-lib/process-group-runner.mjs](scripts/pr-lib/process-group-runner.mjs)
- [scripts/pr-lib/push.sh](scripts/pr-lib/push.sh)
- [scripts/pr-lib/review.sh](scripts/pr-lib/review.sh)
- [scripts/pr-lib/worktree.sh](scripts/pr-lib/worktree.sh)
- [src/gateway/server/client-presence.test.ts](src/gateway/server/client-presence.test.ts)
- [src/infra/system-presence.test.ts](src/infra/system-presence.test.ts)
- [src/infra/system-presence.ts](src/infra/system-presence.ts)
- [test/scripts/clawsweeper-review-gate.test.ts](test/scripts/clawsweeper-review-gate.test.ts)
- [test/scripts/dependency-guard-script.test.ts](test/scripts/dependency-guard-script.test.ts)
- [test/scripts/dependency-guard-workflow.test.ts](test/scripts/dependency-guard-workflow.test.ts)
- [test/scripts/github-activity-helper.test.ts](test/scripts/github-activity-helper.test.ts)
- [test/scripts/pr-cross-checkout.test.ts](test/scripts/pr-cross-checkout.test.ts)
- [test/scripts/pr-git-maintenance.test.ts](test/scripts/pr-git-maintenance.test.ts)
- [test/scripts/pr-main-refresh.test-support.ts](test/scripts/pr-main-refresh.test-support.ts)
- [test/scripts/pr-main-refresh.test.ts](test/scripts/pr-main-refresh.test.ts)
- [test/scripts/pr-merge-hosted.test.ts](test/scripts/pr-merge-hosted.test.ts)
- [test/scripts/pr-merge-outcome.test.ts](test/scripts/pr-merge-outcome.test.ts)
- [test/scripts/pr-merge.test.ts](test/scripts/pr-merge.test.ts)
- [test/scripts/pr-metadata.test.ts](test/scripts/pr-metadata.test.ts)
- [test/scripts/pr-operation-lock.test.ts](test/scripts/pr-operation-lock.test.ts)
- [test/scripts/pr-prepare-gates.test.ts](test/scripts/pr-prepare-gates.test.ts)
- [test/scripts/pr-review-artifact-fixture.ts](test/scripts/pr-review-artifact-fixture.ts)
- [test/scripts/pr-review-artifact-validation.test.ts](test/scripts/pr-review-artifact-validation.test.ts)
- [test/scripts/pr-worktree-containment.test.ts](test/scripts/pr-worktree-containment.test.ts)
- [test/scripts/pr-worktree-evidence.test.ts](test/scripts/pr-worktree-evidence.test.ts)
- [test/scripts/pr-wrappers.test.ts](test/scripts/pr-wrappers.test.ts)
- [test/scripts/security-sensitive-guard-script.test.ts](test/scripts/security-sensitive-guard-script.test.ts)
- [test/scripts/security-sensitive-guard-workflow.test.ts](test/scripts/security-sensitive-guard-workflow.test.ts)

</details>



This page provides a high-level overview of guidelines for contributing to OpenClaw, the repository organization, and typical development workflows. OpenClaw is structured as a multi-platform TypeScript monorepo leveraging modern tooling and strict architectural boundaries to facilitate scalable, maintainable, and extensible development.

---

## Contributing

OpenClaw employs a collaborative model welcoming contributions such as bug fixes and improvements following established workflows and guidelines defined in `CONTRIBUTING.md` and `AGENTS.md`.

Key points to note:

- **Pull Request Workflow:** All PRs must include concrete validation evidence [AGENTS.md:16](). Maintainers use a specialized `scripts/pr` wrapper to manage the lifecycle of PRs, ensuring code trust boundaries are respected [scripts/pr:12-14]().
- **Code Ownership:** `CODEOWNERS` routes reviewers but does not itself enforce approval; maintainers must verify live branch protection rules [AGENTS.md:19]().
- **Real Behavior Proof:** OpenClaw mandates that verdicts need source, tests, and dependency contract proof; diff-only reviews are insufficient [AGENTS.md:12]().
- **Repair Doctrine:** The repository follows a strict "Repair Doctrine" where root-cause investigation is the default. Refactors that leave code better than it was found are preferred over narrow workarounds [AGENTS.md:24-34]().
- **Codex Hard Gate:** For any behavior involving the Codex runtime, acting agents must personally inspect the sibling `../codex` source for exact protocol behavior before rendering a verdict or code change [AGENTS.md:14]().
- **CI/CD Guards:** The system uses `scripts/pr-lib/clawsweeper-review-gate.mjs` to validate maintainer review comments and head SHAs before landing [scripts/pr-lib/merge.sh:92-112]().

For in-depth contribution instructions, PR processes, labeling system, and code review practices, see the **[Contributing](#9.1)** subpage.

**Sources:** [AGENTS.md:12-41](), [scripts/pr:12-28](), [scripts/pr-lib/merge.sh:92-123]()

---

## Project Structure

OpenClaw is architected as a monorepo supporting integrated development and clear separation of concerns across multiple platforms.

### Core Repository Layout

| Directory | Purpose |
| :--- | :--- |
| `src/` | Core TypeScript source: agents, gateway, and runtime logic. |
| `extensions/` | Internal plugin packages (referred to as "plugins" in UI/Docs) [AGENTS.md:20](). |
| `apps/` | Platform-specific native client apps (iOS, macOS, Android, Linux) [AGENTS.md:21](). |
| `scripts/` | Local tooling, PR wrappers, and generated-artifact helpers [scripts/AGENTS.md:3](). |
| `skills/` | Bundled skill library including `SKILL.md` definitions [.agents/skills/openclaw-pr-maintainer/SKILL.md:3-9](). |
| `qa/` | Scenario pack assets and repository-backed QA resources. |
| `.agents/` | Specialized agent skills for repository maintenance (e.g., `openclaw-pr-maintainer`) [.agents/skills/openclaw-pr-maintainer/SKILL.md:1-5](). |
| `.local/` | Reserved namespace for ephemeral artifacts, transition journals, and merge audits [scripts/pr-lib/worktree.sh:78-79](). |

### Monorepo Management Highlights

- **pnpm Workspaces:** The repository uses `pnpm` for dependency management. If pnpm would reconcile a shared install during execution, developers are encouraged to use `node scripts/run-vitest.mjs` to bypass preflights [.agents/skills/openclaw-testing/SKILL.md:124-126]().
- **Wrapper Trust Boundary:** The `scripts/pr` script classifies subcommands into `advisory` (can run local code) and `landing` (requires origin-main code) to maintain security during the merge process [scripts/pr:17-28]().
- **Pathfinder Rule:** Touched code must be left better than found; unrelated issues discovered mid-task should be fixed if small or recorded as follow-ups [AGENTS.md:34]().

For a full explanation of repository layout, package organization, and monorepo management conventions, please see **[Project Structure](#9.2)**.

**Sources:** [AGENTS.md:20-21](), [scripts/AGENTS.md:1-28](), [scripts/pr:17-28](), [scripts/pr-lib/worktree.sh:132-133]()

---

## Development Workflow

OpenClaw emphasizes an efficient developer experience, utilizing scoped testing, remote execution for heavy suites, and automated release gates.

### Typical Local Development Cycle

1.  **Hydration:** Run `pnpm install` to resolve workspace dependencies. If it fails, report the first actionable error [AGENTS.md:18]().
2.  **Testing:** Use `scripts/run-vitest.mjs` for local test execution [scripts/AGENTS.md:8](). Confirmed bugs require a failing reproduction before editing [AGENTS.md:38]().
3.  **PR Preparation:** Use `scripts/pr review-init` and `prepare-gates` to validate changes against the required test plan [scripts/pr:23]().
4.  **Remote Proof:** For heavy suites or untrusted fork code, use `crabbox` backends (AWS or Blacksmith Testbox) to run tests in isolated environments [.agents/skills/openclaw-testing/SKILL.md:27-30]().
5.  **Merge Verification:** The `merge-run` command performs a final verification, including a `merge-crabbox-parent-audit` to detect intervening main movement [scripts/pr-lib/merge.sh:29-85]().

### Bridging Natural Language Commands to Code Entities

```mermaid
title "PR Maintenance and Git Workflow Mapping"
graph TD
  subgraph "Developer_Intent"
    INIT_REVIEW["scripts/pr review-init"]
    RUN_GATES["scripts/pr prepare-gates"]
    MERGE_PR["scripts/pr merge-run"]
    RECOVER_LOCK["scripts/pr lock-recover"]
  end

  subgraph "Code_Implementation"
    PR_WRAPPER["scripts/pr"]
    WORKTREE_LIB["scripts/pr-lib/worktree.sh"]
    GATES_LIB["scripts/pr-lib/gates.sh"]
    MERGE_LIB["scripts/pr-lib/merge.sh"]
  end

  subgraph "Entity_Logic"
    LOCK_MECHANISM["scripts/pr-lib/operation-lock.sh"]
    TRANSITION_JOURNAL[".local/review-transition.json"]
    OUTCOME_REF["refs/openclaw/pr-merge-outcomes/"]
  end

  INIT_REVIEW --> PR_WRAPPER
  PR_WRAPPER --> WORKTREE_LIB
  WORKTREE_LIB --> TRANSITION_JOURNAL
  RUN_GATES --> GATES_LIB
  MERGE_PR --> MERGE_LIB
  MERGE_LIB --> OUTCOME_REF
  RECOVER_LOCK --> LOCK_MECHANISM
```
**Sources:** [scripts/pr:23](), [scripts/pr-lib/worktree.sh:133-145](), [scripts/pr-lib/merge-outcome.sh:24-32](), [test/scripts/pr-operation-lock.test.ts:58-62]()

### Remote Execution Architecture

```mermaid
title "Crabbox Remote Execution Flow"
graph TD
  subgraph "Trigger"
    GATE_REQ["OPENCLAW_PR_GATES_REMOTE=testbox"]
  end

  subgraph "Harness"
    CRAB_WRAPPER["scripts/crabbox-wrapper.mjs"]
    BOOTSTRAP["scripts/crabbox-untrusted-bootstrap.sh"]
  end

  subgraph "Remote_Target"
    AWS_CBX["Crabbox AWS Instance"]
    BS_TBX["Blacksmith Testbox"]
  end

  GATE_REQ --> CRAB_WRAPPER
  CRAB_WRAPPER --> BOOTSTRAP
  BOOTSTRAP --> AWS_CBX
  BOOTSTRAP --> BS_TBX
```
**Sources:** [scripts/AGENTS.md:24-25](), [.agents/skills/openclaw-testing/SKILL.md:86-87]()

For exhaustive details on local development setup, hot module reloading, debugging, and Windows-specific considerations (such as `exec/process` tool boundaries), see **[Development Workflow](#9.3)**.

---

This high-level overview outlines how contributing guidelines, project structure, and development workflows integrate cohesively in the OpenClaw codebase. For greater technical depth and procedural details, refer to the linked child pages below:

- **[Contributing](#9.1)** — Contribution guidelines, PR workflow, label taxonomy, and code review.
- **[Project Structure](#9.2)** — Detailed repo layout, monorepo management, and package organization.
- **[Development Workflow](#9.3)** — Developer setup, local runtime, testing practices, and CI/CD integration.

**Sources:** [AGENTS.md:1-41](), [scripts/AGENTS.md:1-28](), [scripts/pr:1-129]()

---

