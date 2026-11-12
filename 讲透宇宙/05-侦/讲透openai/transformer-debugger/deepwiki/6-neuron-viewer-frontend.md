<!-- source: DeepWiki mcp.deepwiki.com · repo openai/transformer-debugger · page 6 Neuron Viewer Frontend · fetched 2026-10-26 -->

# Neuron Viewer Frontend

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [neuron_viewer/README.md](neuron_viewer/README.md)
- [neuron_viewer/package-lock.json](neuron_viewer/package-lock.json)
- [neuron_viewer/src/welcome.tsx](neuron_viewer/src/welcome.tsx)

</details>



The **Neuron Viewer** is a React-based application that provides a graphical interface for exploring transformer model internals. It serves two primary functions: visualizing static activation data for specific model components (neurons, attention heads, and autoencoder latents) and providing an interactive environment called the **Transformer Debugger (TDB)** for real-time model steering and analysis.

The frontend is built with React, TypeScript, and Tailwind CSS, using [Parcel](https://parceljs.org) as the build tool [neuron_viewer/package-lock.json:38-38](). It communicates with the [Activation Server](5.-Activation-Server) to fetch model weights, activations, and generated explanations.

### Application Structure

The application is divided into two main functional areas:

1.  **Transformer Debugger (TDB):** An interactive tool for "debugging" model behavior on specific prompts. It allows users to view activations, ablate nodes, and trace influences across layers. For details, see [Transformer Debugger UI](#6.1).
2.  **Node Pages:** Static-style pages that display comprehensive information about a specific model node (e.g., MLP Neuron 5 in Layer 10), including dataset examples and LLM-generated explanations. For details, see [Neuron Viewer Pages and Panes](#6.2).

### System Integration and Data Flow

The frontend does not perform model inference or heavy data processing locally. Instead, it acts as a thin client for the Activation Server.

#### Backend Connectivity
The frontend connects to the backend using an auto-generated TypeScript client [neuron_viewer/README.md:42-42](). Network requests are abstracted into a `requests` layer:
*   **Inference Requests:** Handled via `src/requests/inferenceRequests.ts` for TDB operations [neuron_viewer/src/welcome.tsx:6-6]().
*   **Read Requests:** Handled via `src/requests/readRequests.ts` for fetching metadata and pre-computed activation records [neuron_viewer/src/welcome.tsx:5-5]().

#### Natural Language to Code Mapping
The following diagram illustrates how UI concepts map to the underlying codebase entities.

**UI to Code Entity Mapping**
```mermaid
graph TD
    subgraph "UI View Layer"
        "Welcome[Welcome.tsx]" -- "Navigates to" --> "NodePage[NodePage.tsx]"
        "Welcome[Welcome.tsx]" -- "Links to" --> "TDB[TransformerDebugger.tsx]"
    end

    subgraph "State & Routing"
        "Router[App.tsx]" -- "URL Pattern" --> "NodeParams[/:model/:nodeType/:layer/:index]"
        "Router[App.tsx]" -- "URL Pattern" --> "TdbParams[/:model/tdb_alpha]"
    end

    subgraph "Data Fetching Layer"
        "TDB[TransformerDebugger.tsx]" --> "InfReq[inferenceRequests.ts]"
        "NodePage[NodePage.tsx]" --> "ReadReq[readRequests.ts]"
        "InfReq[inferenceRequests.ts]" --> "Client[src/client/index.ts]"
        "ReadReq[readRequests.ts]" --> "Client[src/client/index.ts]"
    end

    "Client[src/client/index.ts]" -- "HTTP/JSON" --> "FastAPI[Activation Server]"
```
Sources: [neuron_viewer/src/welcome.tsx:1-61](), [neuron_viewer/README.md:40-46]()

### Routing and Entry Points

The application uses `react-router-dom` to manage navigation [neuron_viewer/package-lock.json:26-26](). The primary entry point is the `Welcome` component, which dynamically discovers available models and datasets from the backend [neuron_viewer/src/welcome.tsx:18-52]().

| Route Pattern | Component | Description |
| :--- | :--- | :--- |
| `/` | `Welcome` | Landing page; lists available datasets and links to TDB [neuron_viewer/src/welcome.tsx:8-8](). |
| `/:model/:nodeType/:layer/:index` | `NodePage` | Visualizes a specific neuron or latent [neuron_viewer/src/welcome.tsx:60-60](). |
| `/:model/tdb_alpha` | `TransformerDebugger` | The interactive debugger interface [neuron_viewer/src/welcome.tsx:36-42](). |

### Technology Stack

The frontend utilizes several key libraries for its interface:
*   **NextUI & Tailwind CSS:** For the component library and styling [neuron_viewer/package-lock.json:13-13]().
*   **Ag-Grid:** Used for high-performance data tables in TDB [neuron_viewer/package-lock.json:17-18]().
*   **Framer Motion:** For UI transitions and animations [neuron_viewer/package-lock.json:21-21]().
*   **Observable Plot:** For rendering activation charts and histograms [neuron_viewer/package-lock.json:30-30]().

**Frontend Communication Architecture**
```mermaid
graph LR
    subgraph "Neuron Viewer (React)"
        direction TB
        "UI_Components[src/panes/]" 
        "TDB_Logic[src/TransformerDebugger/]"
        "Request_Lib[src/requests/]"
        "Generated_Client[src/client/]"
    end

    subgraph "External"
        "Server[Activation Server]"
        "Env[NEURON_VIEWER_ACTIVATION_SERVER_URL]"
    end

    "UI_Components[src/panes/]" --> "Request_Lib[src/requests/]"
    "TDB_Logic[src/TransformerDebugger/]" --> "Request_Lib[src/requests/]"
    "Request_Lib[src/requests/]" --> "Generated_Client[src/client/]"
    "Generated_Client[src/client/]" -- "Axios" --> "Server[Activation Server]"
    "Env[NEURON_VIEWER_ACTIVATION_SERVER_URL]" -. "Configures" .-> "Generated_Client[src/client/]"
```
Sources: [neuron_viewer/README.md:40-55](), [neuron_viewer/package-lock.json:19-19]()

### Development and Deployment

The frontend is served locally using Parcel's development server. It expects the Activation Server to be running (typically on port 8000) to function correctly [neuron_viewer/README.md:7-24]().

*   **Setup:** `npm install` [neuron_viewer/README.md:12-12]()
*   **Run:** `npm start` [neuron_viewer/README.md:18-18]()
*   **Build:** `npm run build` [neuron_viewer/README.md:62-62]()

For details on the specific views, see:
*   [Transformer Debugger UI](#6.1)
*   [Neuron Viewer Pages and Panes](#6.2)

Sources: [neuron_viewer/package-lock.json:1-43](), [neuron_viewer/src/welcome.tsx:1-125](), [neuron_viewer/README.md:1-64]()

---

