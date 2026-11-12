<!-- source: DeepWiki mcp.deepwiki.com · repo openai/gpt-5-coding-examples · page 5 GPT-5 Generation Workflow · fetched 2026-10-26 -->

# GPT-5 Generation Workflow

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)

</details>



This document explains how the example applications in this repository were generated using GPT-5, the different interfaces available for code generation, and how to leverage this repository for creating new applications. It covers the complete workflow from natural language prompts to fully functional applications.

For information about the specific example applications generated through this workflow, see [Example Applications](#3). For technical details about the frameworks and build systems used in the generated code, see [Technical Architecture](#4).

## Generation Process Overview

The applications in this repository demonstrate GPT-5's capability to generate complete, functional applications from zero-shot natural language prompts. Each application was created entirely through a single prompt without any hand-written code modifications.

```mermaid
graph TD
    subgraph "Natural Language Input"
        NL_PROMPT["Natural Language Prompt<br/>Single zero-shot description"]
        REQUIREMENTS["Application Requirements<br/>Features, technology preferences"]
    end
    
    subgraph "GPT-5 Processing"
        MODEL["GPT-5 Model<br/>Code generation engine"]
        ANALYSIS["Requirement Analysis<br/>Technology selection"]
        GENERATION["Code Generation<br/>Complete application scaffold"]
    end
    
    subgraph "Generated Code Entities"
        ASTEROID_FILES["apps/asteroid-game/<br/>Next.js application files"]
        AUDIO_FILE["apps/audio-step-sequencer/<br/>index.html single file"]
        CSA_FILE["apps/artisan-csa/<br/>index.html single file"]
        FRONTEND_APP["front-end/<br/>Explorer Next.js app"]
    end
    
    NL_PROMPT --> MODEL
    REQUIREMENTS --> MODEL
    MODEL --> ANALYSIS
    ANALYSIS --> GENERATION
    GENERATION --> ASTEROID_FILES
    GENERATION --> AUDIO_FILE  
    GENERATION --> CSA_FILE
    GENERATION --> FRONTEND_APP
```

Sources: [README.md:1-62]()

## Interface Options

GPT-5 can be accessed through two primary interfaces, each optimized for different user workflows and technical expertise levels.

| Interface | Target Audience | Execution Environment | Output Format | Live Preview |
|-----------|----------------|----------------------|---------------|--------------|
| Codex CLI | Developers | Terminal + Sandbox | File system structure | Yes |
| ChatGPT | Non-developers | Browser Canvas | Single HTML download | Yes |

### Codex CLI Workflow

The Codex CLI provides a terminal-based development environment that integrates directly with GPT-5 for code generation, execution, and live preview.

```mermaid
graph LR
    subgraph "Developer Workflow"
        CLI_CMD["codex --model gpt-5<br/>--full-auto prompt"]
        SANDBOX["Execution Sandbox<br/>Dependency installation"]
        LIVE_PREVIEW["Live Preview Server<br/>localhost development"]
    end
    
    subgraph "Generated Artifacts"
        PROJECT_STRUCTURE["Project Structure<br/>Multiple files and directories"]
        PACKAGE_JSON["package.json<br/>Dependency specifications"]
        BUILD_CONFIG["Build Configuration<br/>webpack, next.config.js"]
        SOURCE_FILES["Source Files<br/>.js, .tsx, .css, .html"]
    end
    
    CLI_CMD --> SANDBOX
    SANDBOX --> PROJECT_STRUCTURE
    SANDBOX --> PACKAGE_JSON
    SANDBOX --> BUILD_CONFIG
    SANDBOX --> SOURCE_FILES
    SANDBOX --> LIVE_PREVIEW
```

The CLI workflow enables complex multi-file applications like the asteroid game found in [apps/asteroid-game/]().

**Example CLI Command:**
```bash
codex --model gpt-5 --full-auto "Build a simple photobooth application with camera access in a single HTML file"
```

Sources: [README.md:32-46]()

### ChatGPT Workflow  

The ChatGPT interface provides browser-based code generation and preview capabilities, optimized for single-file applications.

```mermaid
graph TD
    subgraph "Non-Developer Workflow"
        CHATGPT_PROMPT["ChatGPT Prompt<br/>Natural language description"]
        CODE_GENERATION["GPT-5 Code Generation<br/>HTML/CSS/JavaScript output"]
        CANVAS_PREVIEW["Canvas Preview<br/>Live browser execution"]
        DOWNLOAD["Download HTML File<br/>Standalone application"]
    end
    
    subgraph "Generated Single File Applications"
        AUDIO_HTML["apps/audio-step-sequencer/index.html<br/>Web Audio API implementation"]
        CSA_HTML["apps/artisan-csa/index.html<br/>Business landing page"]
        CUSTOM_HTML["Custom Application<br/>User-generated content"]
    end
    
    CHATGPT_PROMPT --> CODE_GENERATION
    CODE_GENERATION --> CANVAS_PREVIEW
    CANVAS_PREVIEW --> DOWNLOAD
    DOWNLOAD --> AUDIO_HTML
    DOWNLOAD --> CSA_HTML  
    DOWNLOAD --> CUSTOM_HTML
```

This workflow produces self-contained HTML files like those found in [apps/audio-step-sequencer/index.html]() and [apps/artisan-csa/index.html]().

Sources: [README.md:48-57]()

## Front-End Explorer Integration

The repository includes a Next.js-based explorer application that enables browsing and analysis of the generated examples.

```mermaid
graph TB
    subgraph "front-end/ Explorer App"
        NEXTJS_APP["Next.js Application<br/>localhost:3000 server"]
        EXAMPLE_BROWSER["Example Browser<br/>Interactive gallery"]
        PROMPT_VIEWER["Zero-shot Prompt Viewer<br/>Original generation prompts"]
        REMIX_TOOLS["Remix Tools<br/>Adaptation utilities"]
    end
    
    subgraph "Example Data Sources"
        ASTEROID_DIR["apps/asteroid-game/<br/>Complex Next.js example"]
        AUDIO_DIR["apps/audio-step-sequencer/<br/>Web Audio example"]
        CSA_DIR["apps/artisan-csa/<br/>Business website example"]
    end
    
    NEXTJS_APP --> EXAMPLE_BROWSER
    EXAMPLE_BROWSER --> PROMPT_VIEWER
    PROMPT_VIEWER --> REMIX_TOOLS
    
    EXAMPLE_BROWSER --> ASTEROID_DIR
    EXAMPLE_BROWSER --> AUDIO_DIR  
    EXAMPLE_BROWSER --> CSA_DIR
```

**Setup Commands:**
```bash
cd front-end
npm install
npm run dev
```

Sources: [README.md:7-19]()

## Prompt Structure Analysis

The zero-shot prompts used to generate these applications follow specific patterns that maximize GPT-5's code generation capabilities.

### Single-File Application Prompts

These prompts target complete functionality within a single HTML file, leveraging modern Web APIs:

**Audio Step Sequencer Pattern:**
- Web Audio API integration
- Canvas-based UI components  
- Real-time audio synthesis
- Touch and mouse interaction support

**Artisan CSA Pattern:**
- Business-focused landing page
- Interactive contact forms
- Responsive design implementation
- Local business feature integration

### Multi-File Framework Prompts  

These prompts request complete application scaffolds with modern framework integration:

**Asteroid Game Pattern:**
- Next.js framework specification
- Game loop and entity management
- Audio system integration
- Production-ready build configuration

```mermaid
graph LR
    subgraph "Prompt Components"
        FUNCTIONALITY["Core Functionality<br/>Game mechanics, audio features"]
        TECHNOLOGY["Technology Stack<br/>Framework preferences, APIs"]
        SCOPE["Application Scope<br/>Single file vs multi-file"]
        CONSTRAINTS["Implementation Constraints<br/>Browser compatibility, performance"]
    end
    
    subgraph "Generated Code Architecture" 
        SINGLE_FILE["Single HTML File<br/>apps/audio-step-sequencer/index.html"]
        NEXTJS_STRUCTURE["Next.js Project Structure<br/>apps/asteroid-game/ directory"]
        BUILD_SYSTEM["Build Configuration<br/>webpack.config, package.json"]
        ASSET_OPTIMIZATION["Asset Management<br/>Font loading, CSS optimization"]
    end
    
    FUNCTIONALITY --> SINGLE_FILE
    FUNCTIONALITY --> NEXTJS_STRUCTURE
    TECHNOLOGY --> BUILD_SYSTEM
    SCOPE --> SINGLE_FILE
    SCOPE --> NEXTJS_STRUCTURE
    CONSTRAINTS --> ASSET_OPTIMIZATION
```

Sources: [README.md:1-5](), [README.md:20-31]()

## Iteration and Refinement Process

While the examples in this repository represent single-prompt generations, the workflow supports iterative refinement through both interfaces.

### CLI Iteration Workflow

```mermaid
graph TD
    INITIAL_PROMPT["Initial Prompt<br/>Base application requirements"]
    GENERATED_CODE["Generated Code<br/>Working application baseline"]
    REFINEMENT_PROMPT["Refinement Prompt<br/>Feature additions, bug fixes"]
    UPDATED_CODE["Updated Code<br/>Enhanced application"]
    
    INITIAL_PROMPT --> GENERATED_CODE
    GENERATED_CODE --> REFINEMENT_PROMPT
    REFINEMENT_PROMPT --> UPDATED_CODE
    UPDATED_CODE --> REFINEMENT_PROMPT
```

### ChatGPT Iteration Workflow

```mermaid
graph TD
    BASE_GENERATION["Base Generation<br/>Initial HTML file"]
    CANVAS_TESTING["Canvas Testing<br/>Live preview validation"]
    MODIFICATION_REQUEST["Modification Request<br/>Feature or styling changes"]
    REGENERATION["Code Regeneration<br/>Updated HTML output"]
    
    BASE_GENERATION --> CANVAS_TESTING
    CANVAS_TESTING --> MODIFICATION_REQUEST
    MODIFICATION_REQUEST --> REGENERATION
    REGENERATION --> CANVAS_TESTING
```

Sources: [README.md:29-31]()

## Repository Usage for New Applications

This repository serves as both a reference collection and a starting point for new GPT-5 generated applications.

### Adaptation Workflow

| Step | Action | Result |
|------|--------|---------|
| 1 | Browse examples in [front-end/]() explorer | Identify similar functionality patterns |
| 2 | Copy zero-shot prompt from selected example | Template for adaptation |
| 3 | Customize prompt with new requirements | Personalized application specification |
| 4 | Execute via Codex CLI or ChatGPT | New application generation |
| 5 | Iterate based on results | Refined application output |

### Technology Selection Guidelines

Based on the examples in this repository:

**Choose Single HTML File when:**
- Application scope is self-contained
- Web API integration is primary requirement  
- Deployment simplicity is prioritized
- No server-side functionality needed

**Choose Next.js Framework when:**
- Complex state management required
- Multiple routes or pages needed
- Production optimization important
- Server-side rendering beneficial

Sources: [README.md:19-31](), [README.md:59-61]()