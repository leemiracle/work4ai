<!-- source: DeepWiki mcp.deepwiki.com · repo anthropics/cwc-workshops · page 5 Eval-Driven Agent Development Workshop · fetched 2026-10-26 -->

# Eval-Driven Agent Development Workshop

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [eval-driven-agent-development/CLAUDE.md](eval-driven-agent-development/CLAUDE.md)
- [eval-driven-agent-development/README.md](eval-driven-agent-development/README.md)

</details>



The **Eval-Driven Agent Development Workshop** is a hands-on guide to building and optimizing a **Claude Managed Agent (CMA)** capable of generating professional PowerPoint presentations (`.pptx`). The core philosophy of the workshop is that agentic behavior should not be tuned by "vibes," but by a rigorous, two-layer evaluation system that measures every iteration of the agent's system prompt and toolset.

Participants progress through six evolutionary stages of the agent—from a "naive" baseline to a sophisticated version with visual awareness and a self-correction QA loop—while using a programmatic and LLM-based grader to quantify improvements in layout, typography, and content coherence.

## Workshop Architecture

The workshop environment consists of a local TypeScript runner that orchestrates cloud-based Managed Agent sessions and a local Dockerized rendering engine for visual evaluation.

### Component Relationship
The following diagram illustrates how the local eval runner interacts with the Claude Managed Agents infrastructure and the local grading tools.

**CMA Eval-Driven Development Flow**
```mermaid
graph TD
    subgraph "Local Environment"
        [eval-runner.ts] --> [create-slides.ts]
        [eval-runner.ts] --> [render.ts]
        [eval-runner.ts] --> [graders.ts]
        [render.ts] --> ["Docker (cwc-pptx-render)"]
        [graders.ts] --> [parse-pptx.ts]
    end

    subgraph "Anthropic Cloud (CMA)"
        [create-slides.ts] -- "ant beta:agents" --> ["Agent (agent.yaml)"]
        ["Agent (agent.yaml)"] -- "Executes" --> ["Environment (environment.yaml)"]
        ["Environment (environment.yaml)"] -- "Produces" --> [presentation.pptx]
    end

    [presentation.pptx] -- "Download" --> [eval-runner.ts]
    ["Docker (cwc-pptx-render)"] -- "Output" --> [slide-JPGs]
    [slide-JPGs] -- "Visual Check" --> [graders.ts]
```
Sources: [eval-driven-agent-development/README.md:71-85](), [eval-driven-agent-development/CLAUDE.md:13-17]()

## Agent Iteration Path

The workshop guides developers through six specific variants of the agent, located in `resources/agents/` (and the `solutions/` directory). Each step addresses a specific failure mode identified by the evaluation harness.

| Variant | Focus | Key Change |
| :--- | :--- | :--- |
| **00-naive** | Baseline | Basic prompt to generate a `.pptx` file. |
| **01-visual** | Visuals | Adding image generation or placeholder logic. |
| **02-typography** | Design | Constraining font sizes and families for readability. |
| **03-palette** | Branding | Enforcing color schemes and professional themes. |
| **04-density** | Layout | Preventing "wall of text" slides via structural constraints. |
| **05-qa-loop** | Reliability | Implementing a multi-turn self-correction step. |

For details on how these agents are configured and deployed, see [PPTX Workshop: Agent Pipeline and Tooling](#5.2).

Sources: [eval-driven-agent-development/README.md:74-76](), [eval-driven-agent-development/CLAUDE.md:13-14]()

## The Two-Layer Grader System

To move beyond manual inspection, the workshop utilizes a robust grading system defined in `src/graders.ts`. This system combines two distinct approaches to ensure the generated slide decks meet both structural and aesthetic requirements:

1.  **Programmatic Graders**: Use `parse-pptx.ts` to extract raw XML data from the `.pptx` file. They check for objective metrics like slide count, font sizes, and text density.
2.  **LLM-as-Judge Graders**: Use Claude to inspect JPG renders of the slides (generated via a Dockerized LibreOffice instance in `render.ts`). These graders evaluate subjective qualities like color harmony, image relevance, and title-body coherence.

For a deep dive into the grading logic and how to add custom metrics, see [PPTX Workshop: Grader System](#5.1).

Sources: [eval-driven-agent-development/src/graders.ts:1-20](), [eval-driven-agent-development/README.md:60-65]()

## Core Workflow

The development cycle is driven by the `ant` CLI and a set of `npm` scripts that automate the "Build -> Run -> Grade" loop.

### Command Reference
| Action | Command | File Reference |
| :--- | :--- | :--- |
| **Provision Agent** | `ant beta:agents create < resources/agent.yaml` | [CLAUDE.md:21-25]() |
| **Run Agent** | `npm run create-slides -- <task_name>` | [src/create-slides.ts]() |
| **Render Slides** | `npm run render -- <task_name>` | [src/render.ts]() |
| **Evaluate** | `npm run eval -- <task_name>` | [src/eval-runner.ts]() |
| **Set Baseline** | `npm run eval -- --all --baseline` | [README.md:64-65]() |

### Data Mapping: Code Entities to Workshop Concepts
This diagram maps the conceptual "Natural Language" requirements to the specific TypeScript files and CLI resources that implement them.

**Code Entity Mapping**
```mermaid
graph LR
    subgraph "Natural Language Space"
        A["'Create a slide deck'"]
        B["'Is the font too small?'"]
        C["'Does it look professional?'"]
    end

    subgraph "Code Entity Space"
        A --> [tasks.json]
        A --> [create-slides.ts]
        B --> [parse-pptx.ts]
        B --> [graders.ts]
        C --> [render.ts]
        C --> [graders.ts]
    end

    subgraph "CMA Resource Space"
        [agent.yaml] -- "Defines" --> [AgentResource]
        [environment.yaml] -- "Defines" --> [EnvResource]
    end

    [create-slides.ts] -- "Uses" --> [AgentResource]
```
Sources: [eval-driven-agent-development/README.md:71-85](), [eval-driven-agent-development/CLAUDE.md:19-39]()

---

