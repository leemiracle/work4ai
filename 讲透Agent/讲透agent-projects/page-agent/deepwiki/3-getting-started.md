<!-- source: DeepWiki mcp.deepwiki.com · repo alibaba/page-agent · page 3 Getting Started · fetched 2026-10-29 -->

# Getting Started

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [docs/README-zh.md](docs/README-zh.md)
- [packages/website/src/constants.ts](packages/website/src/constants.ts)
- [packages/website/src/pages/docs/advanced/custom-ui/page.tsx](packages/website/src/pages/docs/advanced/custom-ui/page.tsx)
- [packages/website/src/pages/docs/advanced/page-agent/page.tsx](packages/website/src/pages/docs/advanced/page-agent/page.tsx)
- [packages/website/src/pages/docs/features/custom-tools/page.tsx](packages/website/src/pages/docs/features/custom-tools/page.tsx)
- [packages/website/src/pages/docs/introduction/limitations/page.tsx](packages/website/src/pages/docs/introduction/limitations/page.tsx)
- [packages/website/src/pages/docs/introduction/overview/page.tsx](packages/website/src/pages/docs/introduction/overview/page.tsx)
- [packages/website/src/pages/docs/introduction/quick-start/page.tsx](packages/website/src/pages/docs/introduction/quick-start/page.tsx)

</details>



This page guides you through installing PageAgent and executing your first AI-powered web automation task. PageAgent can be integrated via CDN script tag, NPM package, or browser extension, depending on your use case.

For detailed installation instructions, see [Installation Methods](#3.1). For a step-by-step walkthrough, see [Quick Start Guide](#3.2). For LLM provider configuration, see [LLM Provider Setup](#3.3).

## Prerequisites

PageAgent requires:

| Requirement | Details |
|------------|---------|
| **LLM API Access** | OpenAI-compatible API endpoint with tool calling support (see [LLM Provider Setup](#3.3)) |
| **Modern Browser** | Chrome, Firefox, Safari, or Edge with ES6+ support |
| **Client-Side JavaScript** | No server-side components required (runs entirely in the browser) |

Note that for production use, you should configure an LLM API key via environment variables or a backend proxy. The demo CDN uses a free testing API for evaluation purposes only [README.md:67-67]().

Sources: [README.md:53-91](), [packages/website/src/pages/docs/introduction/quick-start/page.tsx:23-56]()

## Installation Methods Overview

PageAgent provides three primary installation methods to suit different development environments:

**Installation Method Selection**

```mermaid
graph TB
    [START] --> [CDN]
    [START] --> [NPM]
    [START] --> [EXT]
    
    [CDN] -- "dist/iife/page-agent.demo.js" --> [CDN_USE]
    [NPM] -- "npm install page-agent" --> [NPM_USE]
    [EXT] -- "Chrome Extension" --> [EXT_USE]

    [CDN_USE]["Quick testing<br/>Static HTML pages<br/>No build tooling"]
    [NPM_USE]["Production apps<br/>React/Vue/Angular<br/>Build system integration"]
    [EXT_USE]["Multi-page tasks<br/>Cross-tab automation<br/>User-side tools"]
```

| Method | Distribution Artifact | Global Access | Use Case |
|--------|----------------------|---------------|----------|
| **CDN** | `page-agent.demo.js` | `window.PageAgent` | Fast testing, static demos |
| **NPM** | `page-agent` package | ES Module Import | Production SaaS integration |
| **Extension** | Chrome Extension | Side Panel / Hub | Cross-tab automation |

For detailed installation instructions for each method, see [Installation Methods](#3.1).

Sources: [README.md:53-91](), [packages/website/src/pages/docs/introduction/quick-start/page.tsx:22-99](), [packages/website/src/pages/docs/introduction/limitations/page.tsx:24-83]()

## Quick Example: CDN Demo

The fastest way to try PageAgent is via the demo CDN, which includes a pre-configured testing LLM.

```html
<!-- Demo CDN with free testing LLM (evaluation only) -->
<script 
    src="https://cdn.jsdelivr.net/npm/page-agent@1.12.2/dist/iife/page-agent.demo.js" 
    crossorigin="anonymous"
></script>
```

This automatically initializes a `PageAgent` instance and shows the UI panel. The demo uses a free testing API [packages/website/src/constants.ts:9-9]() with the model `qwen3.5-flash` [packages/website/src/constants.ts:8-8]().

**Warning**: The demo CDN is for technical evaluation only. By using it, you agree to the [testing API terms](https://github.com/alibaba/page-agent/blob/main/docs/terms-and-privacy.md). Do not use in production or with sensitive data [README.md:67-67]().

| Mirror | URL |
|--------|-----|
| Global | [https://cdn.jsdelivr.net/npm/page-agent@1.12.2/dist/iife/page-agent.demo.js](https://cdn.jsdelivr.net/npm/page-agent@1.12.2/dist/iife/page-agent.demo.js) |
| China | [https://registry.npmmirror.com/page-agent/1.12.2/files/dist/iife/page-agent.demo.js](https://registry.npmmirror.com/page-agent/1.12.2/files/dist/iife/page-agent.demo.js) |

Sources: [README.md:53-71](), [packages/website/src/constants.ts:1-11](), [packages/website/src/pages/docs/introduction/quick-start/page.tsx:23-85]()

## Quick Example: NPM Package

For production applications, install via NPM and configure your own LLM:

```bash
npm install page-agent
```

```javascript
import { PageAgent } from 'page-agent'

const agent = new PageAgent({
    model: 'qwen3.5-plus',
    baseURL: 'https://dashscope.aliyuncs.com/compatible-mode/v1',
    apiKey: 'YOUR_API_KEY',
    language: 'en-US',
})

await agent.execute('Click the login button')
```

**Class Instantiation Flow**

```mermaid
graph TB
    [IMPORT] -- "Import from 'page-agent'" --> [CONSTRUCTOR]
    [CONSTRUCTOR] -- "Init PageAgent" --> [CORE]
    [CORE] -- "Extends" --> [PageAgentCore]
    
    subgraph "Internal Components"
        [PageAgentCore] --> [LLM]
        [PageAgentCore] --> [PageController]
    end

    [CONSTRUCTOR] --> [PanelUI]

    [IMPORT]["packages/page-agent/src/index.ts"]
    [CONSTRUCTOR]["packages/page-agent/src/PageAgent.ts"]
    [PageAgentCore]["packages/core/src/PageAgentCore.ts"]
    [LLM]["packages/llms/src/LLM.ts"]
    [PageController]["packages/page-controller/src/PageController.ts"]
    [PanelUI]["packages/ui/src/Panel.tsx"]
```

The `PageAgent` class extends `PageAgentCore` and adds the `panel` UI property [packages/website/src/pages/docs/advanced/page-agent/page.tsx:80-85](). It automatically creates a `PageController` for DOM extraction and element actions [packages/website/src/pages/docs/advanced/page-agent/page.tsx:32-35]().

Sources: [README.md:72-89](), [packages/website/src/pages/docs/introduction/quick-start/page.tsx:89-114](), [packages/website/src/pages/docs/advanced/page-agent/page.tsx:16-18]()

## Executing Tasks

The `PageAgent` instance provides two execution modes: programmatic and interactive.

**Execution Modes**

```mermaid
graph LR
    [User] -- "Natural Language" --> [PageAgent]
    
    subgraph "Execution Paths"
        [PageAgent] -- "agent.execute(task)" --> [Programmatic]
        [PageAgent] -- "agent.panel.show()" --> [Interactive]
    end

    [Programmatic] --> [ReActLoop]
    [Interactive] --> [UI_Panel]
    [UI_Panel] -- "User clicks Run" --> [ReActLoop]

    [ReActLoop]["packages/core/src/PageAgentCore.ts<br/>(Observe-Think-Act)"]
    [UI_Panel]["packages/ui/src/Panel.tsx<br/>(Human-in-the-loop)"]
```

**Programmatic Execution**
```javascript
// Execute task from code
const result = await agent.execute('Click the login button')
```

**Interactive Panel Execution**
```javascript
// Show UI panel for user input
agent.panel.show()
```

The `execute()` method implements the Re-act loop (observe page state, invoke LLM for decision, execute action, repeat). The `PageAgentCore` logic is fully decoupled from the UI through events like `statuschange`, `historychange`, and `activity` [packages/website/src/pages/docs/advanced/custom-ui/page.tsx:125-154]().

Sources: [README.md:88-88](), [packages/website/src/pages/docs/introduction/quick-start/page.tsx:116-130](), [packages/website/src/pages/docs/advanced/page-agent/page.tsx:151-164](), [packages/website/src/pages/docs/advanced/custom-ui/page.tsx:15-17]()

## Next Steps

After completing basic setup and your first execution:

1.  **Configure LLMs**: Learn how to set up OpenAI, Claude, or local Ollama in [LLM Provider Setup](#3.3).
2.  **Explore Installation**: Deep dive into the Chrome Extension or NPM configuration in [Installation Methods](#3.1).
3.  **Custom Tools**: Extend the agent's capabilities by writing your own tools using the `tool()` helper and Zod schemas [packages/website/src/pages/docs/features/custom-tools/page.tsx:46-86](). See [Custom Tools System](#9).
4.  **Architecture**: Understand how the DOM is processed via text-based manipulation without screenshots [packages/website/src/pages/docs/introduction/limitations/page.tsx:136-154](). See [Page Controller System](#5).

Sources: [README.md:1-125](), [packages/website/src/pages/docs/introduction/quick-start/page.tsx:1-134](), [packages/website/src/pages/docs/features/custom-tools/page.tsx:1-114]()

---

