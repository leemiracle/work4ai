<!-- source: DeepWiki mcp.deepwiki.com · repo openJiuwen-ai/agent-memory · page 5 Agent Memory Platform (Management Console) · fetched 2026-11-02 -->

# Agent Memory Platform (Management Console)

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.gitignore](.gitignore)
- [agent-memory-platform/platform/pom.xml](agent-memory-platform/platform/pom.xml)
- [agent-memory-platform/platform/src/main/resources/application.yml](agent-memory-platform/platform/src/main/resources/application.yml)

</details>



The Agent Memory Platform provides a centralized administrative and management console for the `agent-memory` system. Built as a modular Java Spring Boot application paired with a Vue 3 single-page application frontend, it offers comprehensive control over tenants, operational scopes, dynamic configurations, run-time logs, system audits, and engine operations. It acts as the orchestration layer between operators, developers, and the underlying Python-based `jiuwen_memory` engine [agent-memory-platform/platform/pom.xml:18]().

For detailed breakdowns of the underlying platform subsystems, refer to the child pages:
- [Platform Backend Services](#5.1)
- [Platform Web UI (Vue)](#5.2)

---

## 5.1 Platform Backend Services

The backend of the management console is built on Spring Boot 3.3.5 and structured as a modular monolith [agent-memory-platform/platform/pom.xml:10-18](). It aggregates several functional centers—including authentication, tenant management, scope handling, dynamic configuration, logging, and operational telemetry—under a unified server running on port `9000` [agent-memory-platform/platform/src/main/resources/application.yml:18](). 

Communication with the core Python memory service (defaulting to `http://127.0.0.1:8000`) is mediated by internal HTTP clients such as `MemoryEngineClient`, mapping Java control operations into REST calls [agent-memory-platform/platform/src/main/resources/application.yml:34-35](). Persistence is handled via MyBatis-Plus supporting multiple relational databases (SQLite, MySQL, GaussDB) configured through Spring active profiles [agent-memory-platform/platform/pom.xml:43-72](), [agent-memory-platform/platform/src/main/resources/application.yml:7]().

```mermaid
graph TD
    Client["VueFrontend(:5173)"] -->|HTTPS/REST| SecurityFilter["SpringSecurityFilter"]
    SecurityFilter -->|JWTValid| SpringRouter["SpringMVCController"]
    SpringRouter --> TenantSvc["TenantCenterModule"]
    SpringRouter --> ConfigSvc["ConfigCenterModule"]
    SpringRouter --> OpsSvc["OpsCenterModule"]
    OpsSvc --> EngineClient["MemoryEngineClient"]
    EngineClient -->|HTTP:8516| PythonEngine["MemoryServer(Python)"]

    sub: "Code Entity Space"
    classDef default stroke:#333,fill:none;
```
*Figure 5.1.1: High-level platform backend architecture mapping incoming requests from the frontend through security filters and service modules down to the Python engine client.*

For detailed implementations, security configurations, JWT validation filters, database migrations, and telemetry services, see [Platform Backend Services](#5.1).

Sources: 
- `agent-memory-platform/platform/pom.xml`
- `agent-memory-platform/platform/src/main/resources/application.yml`

---

## 5.2 Platform Web UI (Vue)

The management console frontend is a Vue 3 application that provides operators with graphical dashboards to manage system states. It includes dedicated views for configuration centers, tenant allocations, runtime log inspection, and operational commands. 

The UI communicates with the Spring Boot backend via typed API clients and state stores, backed on the server side by aggregator services that simplify cross-module data retrieval. 

```mermaid
graph TD
    User["Operator"] -->|Browser| VueRouter["VueRouter(:5173)"]
    VueRouter --> ConfigView["ConfigCenterView"]
    VueRouter --> TenantView["TenantManagerView"]
    VueRouter --> OpsView["OpsConsoleView"]
    ConfigView --> ApiClient["PlatformApiClient"]
    TenantView --> ApiClient
    OpsView --> ApiClient
    ApiClient -->|RESTAPI| SpringBoot["PlatformApplication(:9000)"]

    sub: "Code Entity Space"
    classDef default stroke:#333,fill:none;
```
*Figure 5.2.1: Frontend UI routing and API communication paths connecting Vue views via API clients to the platform backend.*

For detailed frontend architecture, component structures, state stores, and layout designs, see [Platform Web UI (Vue)](#5.2).

Sources: 
- `agent-memory-platform/platform/src/main/resources/application.yml`

---

