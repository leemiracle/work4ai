<!-- source: DeepWiki mcp.deepwiki.com · repo asgeirtj/system_prompts_leaks · extra page Artifacts and Anthropic API Integration · fetched 2026-11-09 -->

# Artifacts and Anthropic API Integration

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [Anthropic/claude-opus-4.6.md](Anthropic/claude-opus-4.6.md)
- [Anthropic/raw/claude-opus-4.6-raw.md](Anthropic/raw/claude-opus-4.6-raw.md)
- [Anthropic/visualize.md](Anthropic/visualize.md)

</details>



This document describes Claude's artifact system, which enables the creation of interactive, rendered content that appears alongside the conversation. It covers the supported artifact file types, the "Claude-in-Claude" capability that embeds the Anthropic API within artifacts to create AI-powered applications, MCP server integration for external tool access, and the persistent storage system using `window.storage`. It also details the specialized "Imagine Visual Creation Suite" for high-fidelity visual assets.

For information about computer use tools and file operations, see [2.1.3 Search, Web Fetch, and Copyright Compliance](). For general tool integration patterns, see [7.1 Tool Integration and Orchestration Patterns]().

## Artifact Types and Rendering

Claude creates artifacts for substantial content that users will want to view, edit, or export. The system prioritizes **single-file artifacts** unless multi-file structures are explicitly requested. [Anthropic/claude-opus-4.6.md:339-342]()

### Supported File Types

Six file extensions receive special rendering in the Claude.ai user interface:

| Extension | Type | Rendering Behavior |
|-----------|------|-------------------|
| `.md` | Markdown | Rendered markdown with formatting |
| `.html` | HTML | Full page render with embedded CSS/JS |
| `.jsx` | React | Interactive React component |
| `.mermaid` | Mermaid | Diagram visualization |
| `.svg` | SVG | Vector graphics display |
| `.pdf` | PDF | Document viewer |

**Sources:** [Anthropic/claude-opus-4.6.md:344-351]()

### Markdown Artifacts

Markdown files are created for standalone written content intended for use outside the conversation. The system distinguishes between **conversational responses** (which stay in chat) and **artifacts** (which are extracted for external use). [Anthropic/claude-opus-4.6.md:355-358]()

**When to create markdown artifacts:**
- Original creative writing. [Anthropic/claude-opus-4.6.md:360-360]()
- Content for eventual export (reports, emails, presentations, blog posts, articles). [Anthropic/claude-opus-4.6.md:361-361]()
- Comprehensive guides. [Anthropic/claude-opus-4.6.md:362-362]()
- Standalone text-heavy documents (longer than 4 paragraphs or 20 lines). [Anthropic/claude-opus-4.6.md:363-363]()

**When NOT to create markdown artifacts:**
- Lists, rankings, or comparisons. [Anthropic/claude-opus-4.6.md:367-367]()
- Plot summaries or story explanations. [Anthropic/claude-opus-4.6.md:368-368]()
- Web search responses or research summaries (stay conversational). [Anthropic/claude-opus-4.6.md:369-369]()
- As accompanying README files when not requested. [Anthropic/claude-opus-4.6.md:370-370]()

**Sources:** [Anthropic/claude-opus-4.6.md:355-372]()

### HTML Artifacts

HTML artifacts bundle all code (HTML, CSS, JavaScript) into a single file. External scripts can be imported from an allowlist of CDNs including `cdnjs.cloudflare.com`, `esm.sh`, `cdn.jsdelivr.net`, and `unpkg.com`. [Anthropic/visualize.md:59-60]()

**Critical restriction:** HTML artifacts must use **JavaScript variables or objects** for data storage, NOT `localStorage` or `sessionStorage`. These browser storage APIs are not supported in the Claude.ai environment and cause artifacts to fail. [Anthropic/claude-opus-4.6.md:402-409]()

**Sources:** [Anthropic/claude-opus-4.6.md:374-376](), [Anthropic/claude-opus-4.6.md:402-409](), [Anthropic/visualize.md:59-60]()

### React Artifacts

React artifacts support three content types: React elements, pure functional components, and functional components with Hooks or component classes. [Anthropic/claude-opus-4.6.md:378-381]()

#### Available Libraries

Claude supports a specific set of libraries for React artifacts:
- `lucide-react@0.263.1` (Icons)
- `recharts` (Charts)
- `shadcn/ui` (UI components)
- `three.js` (r128) - Note: `THREE.CapsuleGeometry` is NOT available. [Anthropic/claude-opus-4.6.md:391-391]()
- `tone` (Audio synthesis)
- `mammoth` (DOCX processing)
- `tensorflow` (Machine learning)

**Sources:** [Anthropic/claude-opus-4.6.md:383-400]()

**Critical styling constraint:** React artifacts use **Tailwind's core utility classes only**. There is no Tailwind compiler available, so only pre-defined classes from Tailwind's base stylesheet work. [Anthropic/claude-opus-4.6.md:395-397]()

### Storage Restrictions

Artifact Data Flow
```mermaid
graph TB
    subgraph "Supported_Storage"
        ["React_state_useState_useReducer"]
        ["JavaScript_variables_objects"]
        ["window.storage_API"]
    end
    
    subgraph "Prohibited_Storage"
        ["localStorage_Error"]
        ["sessionStorage_Error"]
        ["ANY_browser_storage_APIs"]
    end
    
    ["Artifact_Code"] --> ["React_state_useState_useReducer"]
    ["Artifact_Code"] --> ["JavaScript_variables_objects"]
    ["Artifact_Code"] --> ["window.storage_API"]
    
    ["Artifact_Code"] -.->|"NEVER_use"| ["localStorage_Error"]
    ["Artifact_Code"] -.->|"NEVER_use"| ["sessionStorage_Error"]
    ["Artifact_Code"] -.->|"NEVER_use"| ["ANY_browser_storage_APIs"]
```

**Sources:** [Anthropic/claude-opus-4.6.md:402-409]()

## Claude-in-Claude: Embedded API Access

The "Claude-in-Claude" capability allows artifacts to make requests to the Anthropic API's `/v1/messages` endpoint. This enables artifacts to become intelligent, interactive applications powered by Claude Sonnet 4. [Anthropic/claude-opus-4.6.md:530-534]()

### Architecture Diagram: Claude-in-Claude System

Claude-in-Claude Infrastructure
```mermaid
graph TB
    subgraph "User_Browser"
        ["User"]
        ["Artifact_UI_React_HTML"]
    end
    
    subgraph "Anthropic_Infrastructure"
        ["Anthropic_API_Endpoint_v1_messages"]
        ["claude-sonnet-4-20250514"]
    end
    
    subgraph "MCP_Ecosystem"
        ["asana-mcp"]
        ["slack-mcp"]
        ["User_connectors"]
    end
    
    subgraph "External_Services"
        ["Asana"]
        ["Slack"]
        ["Gmail"]
    end
    
    ["User"] -->|"Interacts"| ["Artifact_UI_React_HTML"]
    ["Artifact_UI_React_HTML"] -->|"fetch()"| ["Anthropic_API_Endpoint_v1_messages"]
    ["Anthropic_API_Endpoint_v1_messages"] -->|"Routes_to"| ["claude-sonnet-4-20250514"]
    
    ["Artifact_UI_React_HTML"] -->|"mcp_servers_parameter"| ["asana-mcp"]
    ["Artifact_UI_React_HTML"] -->|"mcp_servers_parameter"| ["slack-mcp"]
    
    ["claude-sonnet-4-20250514"] -->|"Uses_tools"| ["asana-mcp"]
    ["claude-sonnet-4-20250514"] -->|"Uses_tools"| ["slack-mcp"]
    
    ["asana-mcp"] -->|"Integrates"| ["Asana"]
    ["slack-mcp"] -->|"Integrates"| ["Slack"]
```

**Sources:** [Anthropic/claude-opus-4.6.md:530-534](), [Anthropic/claude-opus-4.6.md:580-598]()

### API Request Format

The standard API call structure uses `fetch` without requiring an API key:

```javascript
const response = await fetch("https://api.anthropic.com/v1/messages", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    model: "claude-sonnet-4-20250514", // Always use Sonnet 4
    max_tokens: 1000,                   // Always set to 1000
    messages: [{ role: "user", content: "Your prompt here" }],
  })
});
```

**Sources:** [Anthropic/claude-opus-4.6.md:536-545]()

## MCP Server Integration

Model Context Protocol (MCP) servers extend artifact capabilities by providing access to external services. Artifacts can include MCP servers in API calls via the `mcp_servers` parameter. [Anthropic/claude-opus-4.6.md:580-584]()

### MCP Integration Diagram

MCP Connectivity
```mermaid
graph LR
    subgraph "Artifact_Logic"
        ["fetch_v1_messages"]
        ["mcp_servers_config"]
    end
    
    subgraph "MCP_Endpoints"
        ["asana_mcp_sse"]
        ["slack_mcp_url"]
        ["excalidraw_mcp_url"]
    end
    
    ["fetch_v1_messages"] --> ["mcp_servers_config"]
    ["mcp_servers_config"] --> ["asana_mcp_sse"]
    ["mcp_servers_config"] --> ["slack_mcp_url"]
```

**Sources:** [Anthropic/claude-opus-4.6.md:580-598]()

## Persistent Storage System

Artifacts can store and retrieve data that persists across sessions using the `window.storage` API. [Anthropic/claude-opus-4.6.md:811-813]()

### Storage API Methods

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `get(key, shared?)` | `key: string`, `shared?: boolean` | `{key, value, shared} \| null` | Retrieve a value |
| `set(key, value, shared?)` | `key: string`, `value: string`, `shared?: boolean` | `{key, value, shared} \| null` | Store a value |
| `delete(key, shared?)` | `key: string`, `shared?: boolean` | `{key, deleted, shared} \| null` | Delete a value |
| `list(prefix?, shared?)` | `prefix?: string`, `shared?: boolean` | `{keys, prefix?, shared} \| null` | List keys |

**Sources:** [Anthropic/claude-opus-4.6.md:815-820]()

### Key Design Patterns

Use **hierarchical keys under 200 characters**: `table_name:record_id`. [Anthropic/claude-opus-4.6.md:838-840]()

**Key restrictions:**
- Cannot contain whitespace. [Anthropic/claude-opus-4.6.md:841-841]()
- Cannot contain path separators (`/` or `\`). [Anthropic/claude-opus-4.6.md:842-842]()
- Cannot contain quotes (`'` or `"`). [Anthropic/claude-opus-4.6.md:843-843]()

**Sources:** [Anthropic/claude-opus-4.6.md:838-843]()

## Imagine Visual Creation Suite (Visualize)

The `visualize.md` instructions define a "Core Design System" for specialized visual modules including diagrams, mockups, interactives, charts, art, and data visualizations. [Anthropic/visualize.md:1-5]()

### Core Modules

| Module | Purpose | Key Constraints |
|--------|---------|-----------------|
| `diagram` | Flowcharts, architectures | Minimal colors, readable labels |
| `mockup` | UI/UX wireframes | High fidelity, standard components |
| `interactive` | Functional tools | `sendPrompt()` integration |
| `chart` | Statistical data | `recharts` usage, accessible |
| `art` | Creative SVG/HTML | Thematic consistency |
| `data_viz` | Complex datasets | Interactive filtering, tooltips |

**Sources:** [Anthropic/visualize.md:3-10]()

### Design Philosophy and Implementation

Claude's visualization suite follows a strict minimalist aesthetic designed to blend with the host interface.

- **Philosophy**: Seamless, Flat, and Compact. [Anthropic/visualize.md:25-28]()
- **Text vs Visuals**: All explanatory text must be OUTSIDE the tool call. The tool output should contain ONLY the visual element. [Anthropic/visualize.md:29-29]()
- **Typography**: Default font is Anthropic Sans. Headings use `font-weight: 500`. Never use weight 600 or 700. [Anthropic/visualize.md:45-46]()
- **Dark Mode**: Mandatory support. Every color must work in both light and dark modes. [Anthropic/visualize.md:70-75]()
- **Interactive Controls**: Artifacts can use `sendPrompt(text)` to send messages to the chat as if the user typed it, enabling interactive feedback loops. [Anthropic/visualize.md:77-77]()

### Complexity and Limits

To ensure performance and readability, the suite enforces hard limits on visual complexity:
- **Box subtitles**: ≤5 words. [Anthropic/visualize.md:13-13]()
- **Colors**: ≤2 ramps per diagram. [Anthropic/visualize.md:14-14]()
- **Horizontal tier**: ≤4 boxes at full width (~140px each). [Anthropic/visualize.md:15-15]()
- **Icon sizing**: Explicitly set `font-size: 16px` for emoji or `width: 16px; height: 16px` for SVG icons. [Anthropic/visualize.md:56-56]()

**Sources:** [Anthropic/visualize.md:12-68]()

---

