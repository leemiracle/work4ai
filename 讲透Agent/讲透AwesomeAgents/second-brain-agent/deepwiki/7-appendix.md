<!-- source: DeepWiki mcp.deepwiki.com · repo flepied/second-brain-agent · page 7 Appendix · fetched 2026-10-26 -->

# Appendix

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.gitignore](.gitignore)

</details>



This appendix provides additional reference information for the Second Brain Agent system, including licensing details, project structure overview, and miscellaneous files that support the main functionality. For information about core system components, see the main documentation sections [1](#1) through [6](#6).

## Licensing

The Second Brain Agent is distributed under the GNU General Public License version 3 (GPL-3.0). This is a copyleft license that ensures the software remains free and open source.

### License Summary

| Aspect | Details |
|--------|---------|
| License Type | GNU General Public License v3.0 |
| Permissions | Commercial use, modification, distribution, private use |
| Conditions | Source code must be disclosed, license and copyright notice must be included, state changes must be documented |
| Limitations | No warranty, no liability |

The full license text is available in the project root and establishes the legal framework for using, modifying, and distributing the software.

**Sources:** [LICENSE:1-675]()

## Project Structure Overview

The following diagram illustrates the high-level organization of files and directories in the Second Brain Agent codebase:

### Project File Organization

```mermaid
graph TB
    ROOT["/"]
    
    subgraph "Core Python Modules"
        LIB["lib.py"]
        EXTRACTORS["extractors.py"] 
        TMD["transform_md.py"]
        TTXT["transform_txt.py"]
        SBA["second_brain_agent.py"]
        MCP["mcp_server.py"]
    end
    
    subgraph "CLI Utilities"
        SIM["similarity.py"]
        QA["qa.py"]
        SC["smart_connections.py"]
    end
    
    subgraph "Infrastructure Scripts"
        MONITOR["monitor.sh"]
        INTEGRATION["integration-test.sh"]
        COMPOSE["compose.yaml"]
    end
    
    subgraph "Configuration Files"
        PYPROJECT["pyproject.toml"]
        GITIGNORE[".gitignore"]
        ENVFILE[".env"]
        LICENSE_FILE["LICENSE"]
    end
    
    subgraph "Service Definitions"
        SERVICES["*.service files"]
    end
    
    ROOT --> LIB
    ROOT --> EXTRACTORS
    ROOT --> TMD
    ROOT --> TTXT
    ROOT --> SBA
    ROOT --> MCP
    ROOT --> SIM
    ROOT --> QA
    ROOT --> SC
    ROOT --> MONITOR
    ROOT --> INTEGRATION
    ROOT --> COMPOSE
    ROOT --> PYPROJECT
    ROOT --> GITIGNORE
    ROOT --> ENVFILE
    ROOT --> LICENSE_FILE
    ROOT --> SERVICES
```

**Sources:** [.gitignore:1-5](), [LICENSE:1-675]()

## Configuration and Metadata Files

### Git Configuration

The project uses Git for version control with a standard `.gitignore` configuration that excludes:

| Pattern | Purpose |
|---------|---------|
| `__pycache__` | Python bytecode cache directories |
| `.venv` | Virtual environment directory |
| `.env` | Environment variables file containing secrets |
| `*.service` | Generated systemd service files |

### Dependency Management

The project uses Poetry for Python dependency management, with configuration specified in `pyproject.toml`. This includes:

- Project metadata and version information
- Python dependencies for core functionality
- Development dependencies for testing and code quality
- Build system configuration

**Sources:** [.gitignore:1-5]()

## System Entry Points and Utilities

The following diagram maps the various entry points and utilities to their specific code implementations:

### Code Entry Points Mapping

```mermaid
graph LR
    subgraph "Web Interface"
        STREAMLIT_CMD["streamlit run"] --> SBA_PY["second_brain_agent.py"]
        SBA_PY --> AGENT_CLASS["Agent class"]
    end
    
    subgraph "CLI Tools"
        PYTHON_SIM["python similarity.py"] --> SIM_PY["similarity.py"]
        PYTHON_QA["python qa.py"] --> QA_PY["qa.py"] 
        PYTHON_SC["python smart_connections.py"] --> SC_PY["smart_connections.py"]
    end
    
    subgraph "Server Processes"
        MCP_SERVER["mcp server"] --> MCP_PY["mcp_server.py"]
        MCP_PY --> MCP_HANDLERS["get_documents, search_documents"]
    end
    
    subgraph "Processing Scripts"
        BASH_MONITOR["./monitor.sh"] --> MONITOR_SH["monitor.sh"]
        PYTHON_TMD["python transform_md.py"] --> TMD_PY["transform_md.py"]
        PYTHON_TTXT["python transform_txt.py"] --> TTXT_PY["transform_txt.py"]
    end
    
    subgraph "Testing"
        PYTEST["pytest"] --> TEST_FILES["test_*.py"]
        BASH_INTEGRATION["./integration-test.sh"] --> INTEGRATION_SH["integration-test.sh"]
    end
    
    AGENT_CLASS --> LIB_AGENT["lib.Agent"]
    SIM_PY --> CHROMADB_DIRECT["ChromaDB direct access"]
    QA_PY --> LIB_AGENT
    SC_PY --> LIB_AGENT
    TMD_PY --> TRANSFORM_FUNCS["extract_text_from_*"]
    TTXT_PY --> CHUNK_FUNCS["chunk_text, store_embeddings"]
```

**Sources:** [.gitignore:4]()

## File Patterns and Exclusions

The project maintains clean version control through strategic file exclusions:

### Generated and Temporary Files

```mermaid
graph TB
    subgraph "Python Runtime"
        PYCACHE["__pycache__/"]
        PYFILES["*.pyc, *.pyo"]
    end
    
    subgraph "Environment"
        VENV[".venv/"]
        ENVFILE[".env"]
    end
    
    subgraph "System Services"
        SERVICES["*.service"]
        GENERATED["Generated from templates"]
    end
    
    subgraph "Version Control"
        GITIGNORE[".gitignore"]
        EXCLUSIONS["Excluded patterns"]
    end
    
    GITIGNORE --> PYCACHE
    GITIGNORE --> VENV
    GITIGNORE --> ENVFILE
    GITIGNORE --> SERVICES
    
    PYCACHE --> PYFILES
    SERVICES --> GENERATED
    GITIGNORE --> EXCLUSIONS
```

This ensures that sensitive configuration data, generated files, and environment-specific artifacts are not committed to version control.

**Sources:** [.gitignore:1-5]()

## Legal and Compliance Information

### GPL-3.0 License Compliance

The GNU General Public License v3.0 requires specific compliance measures:

| Requirement | Implementation |
|-------------|----------------|
| Source Code Availability | All source code is publicly available in the GitHub repository |
| License Notice | Full license text included in [LICENSE:1-675]() |
| Copyright Notice | Copyright notices preserved in all source files |
| Modification Documentation | Git history provides complete modification tracking |
| Distribution Terms | All redistributions must include license and source code |

### Third-Party Dependencies

The system integrates with various external services and libraries, each with their own licensing terms:

- OpenAI API (commercial terms)
- Hugging Face models (various open source licenses)
- AssemblyAI (commercial terms)
- ChromaDB (Apache 2.0 license)
- Python ecosystem packages (various open source licenses)

Users must ensure compliance with all applicable licenses when deploying the system.

**Sources:** [LICENSE:1-675]()