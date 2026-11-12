<!-- source: DeepWiki mcp.deepwiki.com · repo openai/openai-cs-agents-demo · page 5 Development Environment · fetched 2026-10-26 -->

# Development Environment

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [ui/package.json](ui/package.json)

</details>



This document covers the development environment setup, technology stack, and development workflow for the Customer Service Agents Demo repository. It provides instructions for setting up a local development environment, configuring dependencies, and running the application components.

For information about specific technologies used, see [Technology Stack](#5.1). For step-by-step installation, see [Setup and Configuration](#5.2).

## Technology Stack Overview

The Customer Service Agents Demo uses a modern full-stack architecture with a FastAPI backend and a Next.js frontend.

### Development Environment Architecture

```mermaid
graph TB
    subgraph "Local Development Environment"
        DevMachine["Developer Machine<br/>localhost"]
        
        subgraph "Frontend Development - Port 3000"
            NextJSDev["Next.js Development Server<br/>npm run dev"]
            NodeEnv["Node.js Runtime Environment<br/>node_modules/"]
            TypeScriptComp["TypeScript Compiler<br/>tsc"]
        end
        
        subgraph "Backend Development - Port 8000" 
            UvicornServer["Uvicorn ASGI Server<br/>python -m uvicorn main:app"]
            PythonVenv["Python Virtual Environment<br/>.venv/"]
            FastAPIApp["FastAPI Application<br/>main.py"]
        end
        
        subgraph "External Dependencies"
            OpenAIAPI["OpenAI API<br/>OPENAI_API_KEY"]
            AgentsSDK["OpenAI Agents SDK<br/>pip install openai-agents"]
        end
    end
    
    NextJSDev --> UvicornServer
    FastAPIApp --> OpenAIAPI
    FastAPIApp --> AgentsSDK
    
    DevMachine --> NodeEnv
    DevMachine --> PythonVenv
```

**Sources:** [README.md:7-13](), [README.md:57-79](), [ui/package.json:6-8]()

### Development Technology Stack

| Component | Technology | Purpose | Configuration |
|-----------|------------|---------|---------------|
| **Frontend Framework** | Next.js 15 | React-based UI application | `npm run dev` on port 3000 |
| **Frontend Language** | TypeScript | Type-safe JavaScript development | `tsconfig.json` |
| **Backend Framework** | FastAPI | Python web API framework | `uvicorn main:app` on port 8000 |
| **Backend Runtime** | Python 3.x | Server-side application runtime | Virtual environment in `.venv/` |
| **Agent Framework** | OpenAI Agents SDK | Agent orchestration and management | `pip install -r requirements.txt` |
| **Package Management** | npm + pip | Frontend and backend dependencies | `package.json` and `requirements.txt` |

**Sources:** [README.md:9-13](), [README.md:37-53](), [ui/package.json:13-31]()

## Development Setup Process

### Environment Configuration Flow

```mermaid
flowchart TD
    Start["Start Development Setup"] --> APIKey["Set OPENAI_API_KEY"]
    
    APIKey --> EnvVar["Export environment variable<br/>export OPENAI_API_KEY=your_key"]
    APIKey --> EnvFile["Create .env file<br/>python-backend/.env"]
    
    EnvVar --> BackendSetup["Backend Setup"]
    EnvFile --> BackendSetup
    
    BackendSetup --> CreateVenv["Create Python Virtual Environment<br/>python -m venv .venv"]
    CreateVenv --> ActivateVenv["Activate Virtual Environment<br/>source .venv/bin/activate"]
    ActivateVenv --> InstallPython["Install Python Dependencies<br/>pip install -r requirements.txt"]
    
    Start --> FrontendSetup["Frontend Setup"]
    FrontendSetup --> InstallNode["Install Node Dependencies<br/>npm install"]
    
    InstallPython --> Ready["Development Environment Ready"]
    InstallNode --> Ready
    
    Ready --> RunBackend["Run Backend Only<br/>uvicorn main:app --reload --port 8000"]
    Ready --> RunFullStack["Run Full Stack<br/>npm run dev"]
```

**Sources:** [README.md:17-53](), [ui/package.json:5-12]()

### High-Level Setup Summary

1.  **OpenAI API Key**: Required for the Agents SDK. Can be set via `export` or a `.env` file in `python-backend/`.
2.  **Backend Dependencies**: Requires a Python virtual environment and installation of requirements.
3.  **Frontend Dependencies**: Requires Node.js and `npm install` within the `ui/` directory.

For detailed, step-by-step instructions, see [Setup and Configuration](#5.2).

**Sources:** [README.md:19-53]()

## Running the Application

### Application Startup Options

The development environment supports two primary execution modes:

#### Backend-Only Development
Used for testing the agent logic or API endpoints independently.
```bash
cd python-backend
python -m uvicorn main:app --reload --port 8000
```
**Sources:** [README.md:59-67]()

#### Full-Stack Development
The recommended way to run the demo. This uses the `concurrently` package to launch both servers.
```bash
cd ui
npm run dev
```
This starts the Next.js frontend at `http://localhost:3000` and the Python backend at `http://localhost:8000`.

**Sources:** [README.md:69-79](), [ui/package.json:8]()

### Development Server Communication

```mermaid
graph LR
    subgraph "Development Servers"
        NextJS["Next.js Dev Server<br/>localhost:3000"]
        FastAPI["FastAPI Server<br/>localhost:8000"]
    end
    
    subgraph "File Watching"
        TSWatch["Next.js HMR<br/>Fast Refresh"]
        PyReload["Uvicorn --reload<br/>Watch main.py"]
    end
    
    subgraph "API Communication"
        ChatKitReq["ChatKit Request<br/>/chatkit/state"]
        SSEStream["Server-Sent Events<br/>AgentEvents stream"]
    end
    
    NextJS --> ChatKitReq
    ChatKitReq --> FastAPI
    FastAPI --> SSEStream
    SSEStream --> NextJS
    
    NextJS --> TSWatch
    FastAPI --> PyReload
```

**Sources:** [README.md:55-79](), [ui/package.json:5-12]()

## Customization and Extension

The development environment is designed for experimentation. Developers are encouraged to:

*   **Modify Agent Prompts**: Update the instructions for specialized agents like the `Triage Agent` or `FAQ Agent`.
*   **Extend Tools**: Add new Python functions to the backend and expose them to agents.
*   **Adjust Guardrails**: Modify `guardrails.py` to change how the system handles off-topic or malicious input.
*   **Update UI**: Customize the React components in the `ui/` folder to change the dashboard or chat experience.

For details on the technologies involved in these customizations, see [Technology Stack](#5.1).

**Sources:** [README.md:81-92]()

---

