<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/Quantum-Calibration-Agent-Blueprint · page 10 Web UI · fetched 2026-10-26 -->

# Web UI

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docs/latest/_static/images/usage/web-ui-overview.png](docs/latest/_static/images/usage/web-ui-overview.png)
- [ui/package-lock.json](ui/package-lock.json)
- [ui/package.json](ui/package.json)
- [ui/pages/_app.tsx](ui/pages/_app.tsx)

</details>



The **Web UI** is the primary graphical interface for the Quantum Calibration Agent (QCA) blueprint. Built with **Next.js**, it provides a browser-based environment for real-time agent interaction, experiment visualization, workflow monitoring, and knowledge base management. It serves as a visual wrapper around the Python backend, transforming streaming agent data into interactive components like chat threads, Plotly charts, and DAG (Directed Acyclic Graph) visualizations.

### Interface Role and Components

The Web UI is structured to support the iterative nature of quantum calibration. It bridges the gap between high-level natural language instructions and low-level experiment execution by providing specialized views for different system states.

| Component Group | Role | Key Technologies |
| :--- | :--- | :--- |
| **Chat** | Real-time SSE streaming with the agent. | `eventsource-parser`, `react-markdown` |
| **Experiments** | Visualization of results and historical data. | `plotly.js`, `react-plotly.js` |
| **Workflows** | Interactive DAG monitoring and node control. | `reactflow`, `dagre` |
| **Knowledge** | Browsing the agent's skills and memory. | `lucide-react`, `react-syntax-highlighter` |
| **Apparatus** | Hardware status and configuration overview. | `recharts`, `lucide-react` |

Sources: [ui/package.json:20-66](), [ui/pages/_app.tsx:18-27]()

### System Interaction Topology

The Web UI does not communicate with the Python backend directly during development. Instead, it utilizes a **Proxy Gateway** to manage traffic and handle the complexities of LangGraph streaming.

**Web UI Communication Flow**

```mermaid
graph TD
    subgraph "Browser (Client Space)"
        [NextJS_Frontend] --> |"HTTP/WS"| [Proxy_Gateway]
    end

    subgraph "Server (Backend Space)"
        [Proxy_Gateway] --> |"localhost:8000"| [FastAPI_Backend]
        [FastAPI_Backend] --> |"Subprocess"| [Experiment_Runner]
        [FastAPI_Backend] --> |"LangGraph"| [Agent_Runtime]
    end

    [NextJS_Frontend] -- "Path: ui/pages/" --> [Proxy_Gateway]
    [Proxy_Gateway] -- "Path: ui/proxy/server.js" --> [FastAPI_Backend]
```

Sources: [ui/package.json:6-8](), [ui/proxy/server.js:1-50]() (referenced via context)

### Frontend Architecture

The frontend is a modern React application using the Next.js Pages router. It leverages a global provider pattern in `_app.tsx` to ensure consistent state across the application, including theme management and data fetching.

*   **Global Providers**: The application is wrapped in `QueryClientProvider` for server-state management, `ThemeProvider` for UI styling, and `appWithTranslation` for internationalization. [ui/pages/_app.tsx:31-53]()
*   **Routing**: Primary views are defined in `ui/pages/`, including the main dashboard (`index.tsx`), workflow management (`workflows.tsx`), and system updates.
*   **Type System**: Shared TypeScript definitions in `ui/types/qcal.ts` ensure type safety for experiment schemas, workflow nodes, and agent messages across all components.

For more details on the component hierarchy and state management, see [Frontend Architecture](#10.1).

### Proxy Gateway

The Proxy Gateway (`ui/proxy/server.js`) is a Node.js-based intermediary used during development. Its primary roles include:

1.  **Request Routing**: Forwarding API requests from the Next.js dev server (port 3099) to the Python FastAPI backend (port 8000). [ui/package.json:6-8]()
2.  **Stream Processing**: Intercepting and processing Server-Sent Events (SSE) from the agent to handle multi-part streaming responses.
3.  **WebSocket Support**: Managing persistent connections for real-time updates.

For details on how the gateway handles LangGraph streams and SSRF validation, see [Proxy Gateway](#10.2).

### Technical Stack Summary

The UI leverages a robust set of dependencies to handle scientific data and agentic workflows:

```mermaid
graph LR
    subgraph "Core UI"
        [NextJS] --> [React_19]
        [React_19] --> [TailwindCSS]
    end

    subgraph "Data & Viz"
        [Plotly_js] --> [Experiment_Plots]
        [ReactFlow] --> [Workflow_DAGs]
        [TanStack_Query] --> [State_Sync]
    end

    subgraph "Agent Integration"
        [EventSource_Parser] --> [SSE_Streams]
        [Tiktoken] --> [Token_Counting]
    end
```

Sources: [ui/package.json:20-66]()

### Related Pages
*   **[Frontend Architecture](#10.1)**: Detailed breakdown of React components, hooks, and the `qcal.ts` type system.
*   **[Proxy Gateway](#10.2)**: Technical specification of the Node.js proxy and the streaming transformation layer.
*   **[Chat and Streaming API](#3.1)**: The backend side of the communication protocol used by the Web UI.

Sources: [ui/package.json:1-115](), [ui/pages/_app.tsx:1-53]()

---

