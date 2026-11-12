<!-- source: DeepWiki mcp.deepwiki.com · repo santifer/career-ops · page 7 Web UI (Next.js) · fetched 2026-10-27 -->

# Web UI (Next.js)

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.claude-plugin/marketplace.json](.claude-plugin/marketplace.json)
- [.claude-plugin/plugin.json](.claude-plugin/plugin.json)
- [.github/plugin/plugin.json](.github/plugin/plugin.json)
- [.release-please-manifest.json](.release-please-manifest.json)
- [CHANGELOG.md](CHANGELOG.md)
- [VERSION](VERSION)
- [package.json](package.json)
- [scaffolder/package.json](scaffolder/package.json)
- [tests/README.md](tests/README.md)
- [tests/web-test-layout.test.mjs](tests/web-test-layout.test.mjs)
- [web/CHANGELOG.md](web/CHANGELOG.md)
- [web/README.md](web/README.md)
- [web/package-lock.json](web/package-lock.json)
- [web/package.json](web/package.json)
- [web/src/app/api/explore/route.ts](web/src/app/api/explore/route.ts)
- [web/src/app/api/whats-new/route.ts](web/src/app/api/whats-new/route.ts)
- [web/src/components/cv/cv-ingest.tsx](web/src/components/cv/cv-ingest.tsx)
- [web/src/components/explore/explore-provider.tsx](web/src/components/explore/explore-provider.tsx)
- [web/src/components/explore/explorer-view.tsx](web/src/components/explore/explorer-view.tsx)
- [web/src/components/home/decision-card.tsx](web/src/components/home/decision-card.tsx)
- [web/src/components/home/first-run-home.tsx](web/src/components/home/first-run-home.tsx)
- [web/src/components/home/follow-up-card.tsx](web/src/components/home/follow-up-card.tsx)
- [web/src/components/home/today-dashboard.tsx](web/src/components/home/today-dashboard.tsx)
- [web/src/components/mobile-nav.tsx](web/src/components/mobile-nav.tsx)
- [web/src/components/pipeline-view.tsx](web/src/components/pipeline-view.tsx)
- [web/src/lib/act-envelope.mjs](web/src/lib/act-envelope.mjs)
- [web/src/lib/explore-error.mjs](web/src/lib/explore-error.mjs)
- [web/src/lib/stream-parse.mjs](web/src/lib/stream-parse.mjs)
- [web/src/lib/whats-new.mjs](web/src/lib/whats-new.mjs)
- [web/tests/lib/act-envelope.test.mjs](web/tests/lib/act-envelope.test.mjs)
- [web/tests/lib/decision-card-cta.test.mjs](web/tests/lib/decision-card-cta.test.mjs)
- [web/tests/lib/explore-error.test.mjs](web/tests/lib/explore-error.test.mjs)
- [web/tests/lib/first-run-copy.test.mjs](web/tests/lib/first-run-copy.test.mjs)
- [web/tests/lib/stream-parse.test.mjs](web/tests/lib/stream-parse.test.mjs)
- [web/tests/lib/whats-new.test.mjs](web/tests/lib/whats-new.test.mjs)

</details>



The `web/` directory contains a local-first Next.js application that provides a graphical interface for the `career-ops` pipeline. It is designed to run alongside the CLI, reading and writing to the same flat-file database (`applications.md`) and configuration files (`profile.yml`, `portals.yml`) [web/package.json:5]().

## Architecture Overview

The Web UI follows a **local-first** philosophy. It does not use a centralized database; instead, it uses the local filesystem as its source of truth.

*   **Read Path:** The UI directly parses the Markdown and YAML files in the root directory to display the current state of the pipeline [web/src/components/pipeline-view.tsx:33-39]().
*   **Write Path:** The UI delegates state changes (e.g., updating an application status) to the core Node.js scripts like `set-status.mjs` via API routes to ensure data integrity and consistent logging [web/CHANGELOG.md:14,41]().
*   **Execution:** Long-running tasks, such as AI evaluations or portal scans, are triggered through the UI but executed by the underlying CLI tools (`claude`, `openrouter-runner.mjs`, etc.) [web/CHANGELOG.md:9,42]().

### System Relationship Diagram

This diagram illustrates how the Web UI interacts with the core system entities.

```mermaid
graph TD
    subgraph "Web UI (Next.js)"
        [PipelineView] --> [api/status]
        [ExplorerView] --> [api/explore]
        [TodayDashboard] --> [api/report]
    end

    subgraph "Core Scripts (Node.js)"
        [api/status] -- "exec" --> [set-status.mjs]
        [api/explore] -- "exec" --> [scan.mjs]
        [api/explore] -- "exec" --> [scan-ats-full.mjs]
        [api/report] -- "read" --> [reports/ directory]
    end

    subgraph "Data Layer (Markdown/YAML)"
        [set-status.mjs] -- "write" --> [applications.md]
        [set-status.mjs] -- "log" --> [status-log.tsv]
        [scan.mjs] -- "write" --> [pipeline.md]
        [ExplorerView] -- "read" --> [portals.yml]
    end
```
**Sources:** [web/src/components/pipeline-view.tsx:14-27](), [web/CHANGELOG.md:14,32,41](), [web/package.json:37-41]().

## Key Functional Areas

### Pipeline & Inbox
The `PipelineView` is the central hub for tracking applications. It features a tabbed interface that separates the **Inbox** (newly discovered postings in `pipeline.md`) from the **Tracker** (active applications in `applications.md`) [web/src/components/pipeline-view.tsx:14-27]().
*   **Source of Truth:** The URL parameters (`tab`, `q`, `min`, `sort`) serve as the single source of truth for the view state, allowing deep linking and AI-driven navigation [web/src/components/pipeline-view.tsx:44-53]().
*   **Triage:** The `InboxTriage` component allows users to quickly evaluate, skip, or discard new leads [web/src/components/pipeline-view.tsx:11,185]().

### Discovery (Explore)
The `ExplorerView` provides a UI for the `scan.mjs` and `scan-ats-full.mjs` scripts. It allows users to trigger broad "Reverse ATS" scans and AI-assisted discovery across configured portals [web/CHANGELOG.md:8,12]().
*   **AI Discovery:** Integrates with `api/explore/ai` to perform semantic searches for roles matching the user's profile.
*   **Cost Tracking:** Displays a `CostBadge` to show token usage for AI-driven discovery tasks.

### Today Dashboard
The `TodayDashboard` acts as an action queue, highlighting urgent tasks such as overdue follow-ups, pending applications, and recent employer responses [web/CHANGELOG.md:15]().
*   **Decision Cards:** Presents specific actions (e.g., "Apply to X", "Follow up with Y") based on the current pipeline state.
*   **Analytics Tiles:** Displays funnel metrics (conversion rates from Applied to Interview, etc.) derived from the `status-log.tsv` [web/CHANGELOG.md:34]().

## Technical Stack

| Component | Technology |
| :--- | :--- |
| **Framework** | Next.js 15+ (App Router) [web/package.json:22]() |
| **Runtime** | Node.js >= 22.0.0 [web/package.json:14]() |
| **Styling** | Tailwind CSS 4.0, Lucide Icons [web/package.json:21,31]() |
| **Components** | React 19, Radix UI (via Shadcn) [web/package.json:24]() |
| **Content** | React Markdown, Remark GFM [web/package.json:26-27]() |

## Detailed Subsystems

For deeper technical details on the implementation of the Web UI, refer to the following child pages:

### [Web API Routes & Core Libraries](#7.1)
Covers the Next.js API layer, including SSRF protection (`origin-guard.mjs`), Server-Sent Events (SSE) for streaming AI responses (`stream-parse.mjs`), and the shared logic for interacting with the CLI scripts.

### [Web UI Components & Pages](#7.2)
Detailed breakdown of individual React components, the `ExploreProvider` state management, company logo resolution strategies, and the integration of the PDF generation engine within the UI.

**Sources:** [web/package.json:1-44](), [web/src/components/pipeline-view.tsx:1-185](), [web/CHANGELOG.md:1-50]().

---

