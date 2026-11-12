<!-- source: DeepWiki mcp.deepwiki.com · repo HKUDS/AgentSpace · page 8 Deployment & Infrastructure · fetched 2026-11-09 -->

# Deployment & Infrastructure

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.env.example](.env.example)
- [README.md](README.md)
- [apps/web/app/api/daemon/package/route.ts](apps/web/app/api/daemon/package/route.ts)

</details>



AgentSpace is designed to be flexible, supporting environments ranging from local development machines to distributed cloud infrastructures. The deployment model is governed by the `AGENT_SPACE_DEPLOYMENT_MODE` environment variable, which determines how the system handles database connections and file storage [.env.example:4-4]().

## Deployment Modes

AgentSpace provides two primary deployment paths to balance control and ease of use.

| Mode | Database | Attachment Storage | Best For |
| :--- | :--- | :--- | :--- |
| `self_hosted` | Local PostgreSQL | Local Filesystem | Teams requiring full data sovereignty and local CLI execution. |
| `cloud` | Neon (Serverless) | Cloudflare R2 | Scalable production environments and distributed teams. |

### Self-Hosted Deployment
In `self_hosted` mode, the system expects a standard PostgreSQL instance and a local directory for storing workspace attachments [.env.example:7-11](). This mode is ideal for internal networks where the agent daemon and web server reside on the same infrastructure.

For details, see [Self-Hosted Deployment](#8.1).

### Cloud Deployment
`cloud` mode utilizes serverless infrastructure to minimize maintenance. It leverages **Neon** for PostgreSQL, providing features like instant database branching for testing, and **Cloudflare R2** for S3-compatible object storage [.env.example:16-40]().

For details, see [Cloud Deployment (Neon + Cloudflare R2)](#8.2).

## Infrastructure Overview

The infrastructure bridges the "Natural Language Space" (where users interact with agents) and the "Code Entity Space" (where services and daemons execute logic).

### System Component Architecture

This diagram illustrates how the deployment components interact across the network boundary.

```mermaid
graph TD
    subgraph "External_Services"
        ["Google_OAuth"]
        ["Neon_Postgres"]
        ["Cloudflare_R2"]
    end

    subgraph "Production_Server"
        ["Nginx_Reverse_Proxy"]
        ["Web_App_Service"]
        ["PostgreSQL_Local"]
    end

    subgraph "Execution_Host"
        ["Daemon_Service"]
        ["Sandbox_Environment"]
    end

    ["Nginx_Reverse_Proxy"] --> ["Web_App_Service"]
    ["Web_App_Service"] --> ["PostgreSQL_Local"]
    ["Web_App_Service"] --> ["Neon_Postgres"]
    ["Web_App_Service"] --> ["Cloudflare_R2"]
    
    ["Daemon_Service"] -- "Polling /api/daemon/*" --> ["Nginx_Reverse_Proxy"]
    ["Daemon_Service"] --> ["Sandbox_Environment"]
```
**Sources:** [.env.example:4-40](), [apps/web/app/api/daemon/package/route.ts:7-21]()

### Code Entity Mapping: Deployment & Storage

This diagram maps infrastructure concepts to specific code entities and environment configurations used during deployment.

```mermaid
graph LR
    subgraph "Environment_Config"
        ["AGENT_SPACE_DEPLOYMENT_MODE"]
        ["SELF_HOSTED_DATABASE_URL"]
        ["NEON_DATABASE_URL"]
        ["CLOUDFLARE_R2_BUCKET"]
    end

    subgraph "Web_Server_Entities"
        ["buildDaemonPackageTarball"]
        ["requireDaemonAuth"]
        ["api/attachments/route.ts"]
    end

    subgraph "Storage_Abstraction"
        ["LocalRoot"]
        ["R2Client"]
        ["SignedURLs"]
    end

    ["AGENT_SPACE_DEPLOYMENT_MODE"] -- "self_hosted" --> ["LocalRoot"]
    ["AGENT_SPACE_DEPLOYMENT_MODE"] -- "cloud" --> ["R2Client"]
    ["NEON_DATABASE_URL"] --> ["Neon_Postgres"]
    ["CLOUDFLARE_R2_BUCKET"] --> ["SignedURLs"]
    ["buildDaemonPackageTarball"] -- "Generates" --> ["Daemon_Deployment_Artifact"]
```
**Sources:** [.env.example:4-49](), [apps/web/app/api/daemon/package/route.ts:1-13]()

## Testing Infrastructure

AgentSpace utilizes a robust testing pipeline centered around **Playwright** for End-to-End (E2E) verification. A key feature of the infrastructure is the integration with the **Neon API**, which allows the test suite to programmatically create isolated database branches for every test run [.env.example:23-30](). This ensures that E2E tests (such as workspace navigation and task dispatch) run against a clean, production-like schema without affecting the main database.

For details, see [Testing Infrastructure](#8.3).

## Key Configuration Requirements

Regardless of the deployment mode, several security and integration keys must be provisioned:
*   **Encryption Keys**: `NEXT_SERVER_ACTIONS_ENCRYPTION_KEY` and `AGENT_SPACE_GOOGLE_WORKSPACE_TOKEN_ENCRYPTION_KEY` are required to secure server-side operations and sensitive OAuth tokens [.env.example:62-79]().
*   **OAuth Credentials**: Google Client IDs and Secrets are necessary for user authentication and Google Workspace integrations [.env.example:68-76]().
*   **Signed URLs**: The `ATTACHMENT_SIGNED_URL_TTL_SECONDS` setting controls the lifespan of temporary access links for files stored in R2 or local storage [.env.example:47-47]().

**Sources:**
- [.env.example:1-82]()
- [apps/web/app/api/daemon/package/route.ts:1-21]()
- [README.md:68-78]()

---

