<!-- source: DeepWiki mcp.deepwiki.com · repo aaronjmars/MiroShark · page 8 Infrastructure & Deployment · fetched 2026-10-26 -->

# Infrastructure & Deployment

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.dockerignore](.dockerignore)
- [.github/workflows/docker-image.yml](.github/workflows/docker-image.yml)
- [Dockerfile](Dockerfile)
- [backend/app/utils/logger.py](backend/app/utils/logger.py)
- [backend/run.py](backend/run.py)
- [docker-compose.yml](docker-compose.yml)
- [frontend/package-lock.json](frontend/package-lock.json)
- [frontend/package.json](frontend/package.json)
- [frontend/src/store/pendingUpload.js](frontend/src/store/pendingUpload.js)

</details>



This section outlines the deployment strategies, containerization architecture, and continuous integration pipeline for MiroShark. The system is designed to be portable, supporting both local development environments and containerized production-ready deployments via Docker.

## Deployment Overview

MiroShark follows a three-tier architecture comprising a Vue 3 frontend, a Flask backend, and a Neo4j graph database. Deployment is orchestrated to ensure that all services, including the local LLM provider (Ollama), are correctly networked and configured.

### System Component Architecture

The following diagram illustrates how the infrastructure components map to the codebase and their communication paths.

**Infrastructure to Code Entity Map**

```mermaid
graph TD
    subgraph "External/Infrastructure"
        "N4J"["Neo4j Container (Port 7687/7474)"]
        "OLM"["Ollama Container (Port 11434)"]
    end

    subgraph "MiroShark Service"
        "BEND"["Flask Backend (Port 5001)"]
        "FEND"["Vue 3 Frontend (Port 3000)"]
        "LOGS"["RotatingFileHandler (logs/*.log)"]
    end

    "FEND" -- "REST API" --> "BEND"
    "BEND" -- "Bolt Protocol" --> "N4J"
    "BEND" -- "OpenAI-Compatible API" --> "OLM"
    "BEND" -- "Writes to" --> "LOGS"

    style "BEND" stroke-dasharray: 5 5
    style "FEND" stroke-dasharray: 5 5
```
**Sources:** [docker-compose.yml:1-48](), [backend/run.py:40-45](), [backend/app/utils/logger.py:66-75]()

## Deployment Options

MiroShark supports two primary deployment modes:

1.  **Docker Compose (Recommended):** A fully containerized setup that manages the MiroShark application, Neo4j database, and Ollama instance. This ensures environment parity and simplifies dependency management. For details, see [Docker & Production Deployment](#8.1).
2.  **Local Development:** Running the components natively. The backend requires Python 3.11+ and `uv` for dependency management [Dockerfile:1-9](), while the frontend requires Node.js (>= 18) [Dockerfile:3-5]().

### Configuration & Validation
The backend validates its environment variables upon startup via `Config.validate()` [backend/run.py:28-34](). Key configuration parameters include `NEO4J_URI`, `LLM_BASE_URL`, and `EMBEDDING_MODEL` [docker-compose.yml:28-38]().

## Containerization & CI/CD

The project utilizes a multi-stage `Dockerfile` and GitHub Actions for automated image builds.

### Docker Architecture
The main `miroshark` image is a unified container that handles both frontend and backend tasks in development mode using `npm run dev` [Dockerfile:29](). It leverages `uv` for fast, frozen Python dependency installation [Dockerfile:21]().

**Container Dependency Graph**

```mermaid
graph LR
    "GitHub_Actions"["docker-image.yml"] -- "Pushes to" --> "GHCR"["ghcr.io/aaronjmars/miroshark"]
    "Docker_Compose"["docker-compose.yml"] -- "Pulls" --> "GHCR"
    "Docker_Compose" -- "Starts" --> "miroshark_service"["MiroShark Service"]
    "miroshark_service" -- "Depends On" --> "neo4j_service"["Neo4j Service"]
    "miroshark_service" -- "Depends On" --> "ollama_service"["Ollama Service"]
```
**Sources:** [.github/workflows/docker-image.yml:1-50](), [docker-compose.yml:42-44]()

For a deep dive into the Docker configuration and the Nginx setup for production, see [Docker & Production Deployment](#8.1).

## Testing & Artifacts

The system produces specific artifacts during pipeline execution and end-to-end tests. These artifacts are stored in structured directories and serve as "checkpoints" for the graph build and simulation processes.

### Pipeline Artifacts
The pipeline generates several JSON and DB files, such as:
*   `01_ontology.json`: The schema generated from source documents.
*   `02_graph_data.json`: The extracted entities and relationships.
*   `actions.jsonl`: A log of every agent action during a simulation.
*   `trajectory.json`: Metrics tracking opinion convergence and polarization.

These artifacts allow developers to validate specific stages of the pipeline (e.g., verifying the ontology before running a full simulation). For a full breakdown of these files, see [Test Fixtures & Pipeline Test Outputs](#8.2).

## Logging & Observability

MiroShark implements a unified logging system via `setup_logger` [backend/app/utils/logger.py:30-88]().
*   **Console Output:** Concise logs at `INFO` level and above [backend/app/utils/logger.py:80-82]().
*   **File Output:** Detailed `DEBUG` logs stored in the `logs/` directory with a 10MB rotation policy [backend/app/utils/logger.py:67-75]().
*   **Windows Compatibility:** The system explicitly reconfigures `stdout` and `stderr` to use UTF-8 encoding to prevent crashes on Windows consoles [backend/run.py:8-16](), [backend/app/utils/logger.py:13-23]().

**Sources:** [backend/run.py:8-16](), [backend/app/utils/logger.py:1-126]()

---
### Child Pages
- [Docker & Production Deployment](#8.1)
- [Test Fixtures & Pipeline Test Outputs](#8.2)

---

