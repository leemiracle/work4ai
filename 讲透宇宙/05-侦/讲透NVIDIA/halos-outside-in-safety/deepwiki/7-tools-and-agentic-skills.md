<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/halos-outside-in-safety · page 7 Tools and Agentic Skills · fetched 2026-11-09 -->

# Tools and Agentic Skills

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [ai-perception/README.md](ai-perception/README.md)
- [skills/README.md](skills/README.md)
- [tools/waypoint-generator/README.md](tools/waypoint-generator/README.md)
- [tools/waypoint-generator/src/App.css](tools/waypoint-generator/src/App.css)
- [tools/waypoint-generator/src/App.jsx](tools/waypoint-generator/src/App.jsx)
- [tools/waypoint-generator/src/components/ExportPanel.jsx](tools/waypoint-generator/src/components/ExportPanel.jsx)
- [tools/waypoint-generator/src/components/WaypointCanvas.jsx](tools/waypoint-generator/src/components/WaypointCanvas.jsx)
- [tools/waypoint-generator/src/components/WaypointList.jsx](tools/waypoint-generator/src/components/WaypointList.jsx)
- [tools/waypoint-generator/src/utils/coordinates.js](tools/waypoint-generator/src/utils/coordinates.js)

</details>



This page provides a high-level overview of the developer-facing tooling ecosystem within the NVIDIA Halos Outside-In Safety (HOISA) repository [`README.md:61-63`](). This tooling suite includes the React/Redux-based Waypoint Generator web app [`tools/waypoint-generator/README.md:1-21`](), the Simulation Regression Reporter (SRR) debug viewer, the Doxygen-to-MDX C API documentation generation pipeline, and automation skills conforming to the `agentskills.io` specification [`skills/README.md:1-3`]().

For detailed implementation guides, architecture specs, and operational workflows, refer to the respective child pages:
- [Waypoint Generator](#7.1)
- [SRR Debug Viewer and C-API Doc Tooling](#7.2)
- [Agentic Deployment Skills](#7.3)

---

## 7.1 Waypoint Generator

The Forklift Waypoint Generator is a web application located in `tools/waypoint-generator/` designed to visually author navigation paths for the simulated forklift [tools/waypoint-generator/README.md:1-6](). Built with React, Redux, and Vite [tools/waypoint-generator/README.md:24](), it allows developers to load warehouse floor plans, configure origin poses, place waypoints with custom headings, and export interpolated trajectory files [tools/waypoint-generator/README.md:9-18]().

The application manages three distinct coordinate systems via `tools/waypoint-generator/src/utils/coordinates.js`: **Pixel** (image space), **World** (Isaac Sim global coordinates in meters), and **Odom** (relative frame offset from the starting origin) [tools/waypoint-generator/src/utils/coordinates.js:4-11](). Calibration parameters such as `scaleFactor` and `translationToGlobalCoordinates` map pixels to physical meters [tools/waypoint-generator/src/utils/coordinates.js:20-21](). The final export schema generates a JSON structure containing map identifiers, origin transforms, discrete waypoints, and dense interpolation `poses` consumed directly by the forklift controller [`tools/waypoint-generator/README.md:90-145]().

For deep dives into the React/Redux store structure, coordinate transformations, map configuration bindings, and output JSON schemas, see [Waypoint Generator](#7.1).

```mermaid
graph TD
    UI["WaypointCanvas.jsx"] -->|Pixel Clicks| COORDS["coordinates.js pixelToWorld"]
    COORDS -->|World Meters| STATE["App.jsx Redux Store"]
    STATE -->|Export Data| EP["ExportPanel.jsx"]
    EP -->|JSON Output| CTRL["robot_controller.py"]

    sub-section-sources
    Sources: [tools/waypoint-generator/src/App.jsx:1-30](), [tools/waypoint-generator/src/components/ExportPanel.jsx:1-87](), [tools/waypoint-generator/src/utils/coordinates.js:1-45]()
```

---

## 7.2 SRR Debug Viewer and C-API Doc Tooling

To support regression analysis and C/C++ integration, the repository includes specialized developer tools under `tools/`. The `srr-debug-viewer` parses recorded simulation metrics, tripwire crossings, and Phase 2 perception events into an interactive visualization interface [`skills/README.md:10-15`](). This allows engineers to inspect safety decision latency, mute/unmute states, and 3D bounding box discrepancies against ground truth recordings.

Additionally, the `tools/c-api` directory houses documentation tooling that executes a Doxygen-to-MDX pipeline, automatically transforming source comments from the `safety-core/` C library headers into structured documentation integrated with the Fern documentation site [`README.md:62-63`]().

For details on the SRR debug viewer data schema and the C-API documentation build workflow, see [SRR Debug Viewer and C-API Doc Tooling](#7.2).

```mermaid
graph TD
    REC["Simulation Recorder"] -->|Kafka Logs & GT| SRR["srr-debug-viewer"]
    DOXY["safety-core/ C Headers"] -->|Doxygen Pipeline| MDX["tools/c-api Markdown Output"]
    MDX -->|Fern Site Sync| DOCS["docs/ Index"]

    sub-section-sources
    Sources: [README.md:61-63](), [skills/README.md:10-15]()
```

---

## 7.3 Agentic Deployment Skills

Automation and lifecycle management are encapsulated as agentic skills stored in `skills/` [`skills/README.md:1-4`](). Conforming to the `agentskills.io` specification, each skill directory contains a `SKILL.md` file detailing its frontmatter metadata (`name`, `description`, `version`) and operational prompts [skills/README.md:1-3](). 

The primary skills include `skills/hoisa-deploy-profile`, which coordinates stack deployment across `base`, `sil`, and `hil` profiles, and `skills/hoisa-generate-regression-report`, which automates Isaac Sim scenario orchestration, log clipping, and metric aggregation [skills/README.md:10-15](). These skills enable coding agents (such as Claude Code or Cursor) to execute multi-container lifecycle operations from natural language requests [skills/README.md:7-8]().

For complete reference documentation, prompt templates, and execution workflows, see [Agentic Deployment Skills](#7.3).

```mermaid
graph TD
    NL["Natural Language Prompt"] -->|Loaded by Agent| SKILL["skills/hoisa-deploy-profile/SKILL.md"]
    SKILL -->|Executes Setup| SCRIPT["deployments/scripts/preflight.py"]
    SCRIPT -->|Compose Stack| COMPOSE["deployments/compose.yaml"]
    COMPOSE -->|Brings Up| VSS["ai-perception/ VSS Blueprint"]
    COMPOSE -->|Brings Up| CORE["safety-core/ nvpss_daemon"]

    sub-section-sources
    Sources: [README.md:89-93](), [skills/README.md:1-15]()
```

---

