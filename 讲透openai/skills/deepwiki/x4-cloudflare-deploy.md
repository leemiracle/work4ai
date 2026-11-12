<!-- source: DeepWiki mcp.deepwiki.com · repo openai/skills · extra page Cloudflare Deploy · fetched 2026-10-30 -->

# Cloudflare Deploy

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [skills/.curated/cloudflare-deploy/SKILL.md](skills/.curated/cloudflare-deploy/SKILL.md)
- [skills/.curated/netlify-deploy/SKILL.md](skills/.curated/netlify-deploy/SKILL.md)
- [skills/.curated/render-deploy/SKILL.md](skills/.curated/render-deploy/SKILL.md)

</details>



This page documents the `cloudflare-deploy` skill, which provides deployment capabilities for Cloudflare's platform services including Workers, Pages, and related infrastructure. The skill uses the `wrangler` CLI to interact with Cloudflare's API and provides decision trees to help users select the appropriate Cloudflare product for their use case.

For other deployment platforms, see [Netlify Deploy](5.5.1), [Vercel Deploy](5.5.2), and [Render Deploy](5.5.4).

## Skill Purpose and Scope

The `cloudflare-deploy` skill activates when users want to deploy, host, publish, or set up projects on the Cloudflare platform. It serves as a unified entry point to Cloudflare's extensive product catalog, guiding users through product selection, authentication, and deployment workflows [skills/.curated/cloudflare-deploy/SKILL.md:1-8]().

The skill operates as a hub-and-spoke architecture: the main `SKILL.md` provides decision trees and product routing, while detailed implementation instructions are stored in product-specific reference files under `references/` [skills/.curated/cloudflare-deploy/SKILL.md:112-213]().

Sources: [skills/.curated/cloudflare-deploy/SKILL.md:1-10]()

## Architecture Overview

### Skill Structure

```mermaid
graph TB
    SkillEntry["cloudflare-deploy/SKILL.md<br/>Entry point + routing"]
    
    subgraph "Decision_Trees"
        ComputeTree["Compute Decision Tree<br/>Workers, Pages, DO, etc."]
        StorageTree["Storage Decision Tree<br/>KV, D1, R2, etc."]
        AITree["AI Decision Tree<br/>Workers AI, Vectorize"]
        NetworkTree["Networking Decision Tree<br/>Tunnel, Spectrum"]
        SecurityTree["Security Decision Tree<br/>WAF, Bot Management"]
        MediaTree["Media Decision Tree<br/>Images, Stream"]
    end
    
    subgraph "Authentication_Layer"
        WranglerAuth["npx wrangler whoami<br/>Auth verification"]
        LoginFlow["wrangler login<br/>OAuth flow"]
        APIToken["CLOUDFLARE_API_TOKEN<br/>CI/CD auth"]
    end
    
    subgraph "Product_References"
        WorkersRef["references/workers/<br/>Serverless functions"]
        PagesRef["references/pages/<br/>Static sites + SSR"]
        KVRef["references/kv/<br/>Key-value storage"]
        D1Ref["references/d1/<br/>SQLite database"]
        AIRef["references/workers-ai/<br/>AI inference"]
        TunnelRef["references/tunnel/<br/>Local exposure"]
    end
    
    subgraph "Deployment_Commands"
        WranglerDeploy["wrangler deploy<br/>Worker deployment"]
        PagesDeploy["wrangler pages deploy<br/>Pages deployment"]
        NPMDeploy["npm run deploy<br/>Framework-specific"]
    end
    
    SkillEntry --> ComputeTree
    SkillEntry --> StorageTree
    SkillEntry --> AITree
    SkillEntry --> NetworkTree
    SkillEntry --> SecurityTree
    SkillEntry --> MediaTree
    
    ComputeTree --> WorkersRef
    ComputeTree --> PagesRef
    StorageTree --> KVRef
    StorageTree --> D1Ref
    AITree --> AIRef
    NetworkTree --> TunnelRef
    
    SkillEntry --> WranglerAuth
    WranglerAuth --> LoginFlow
    WranglerAuth --> APIToken
    
    WorkersRef --> WranglerDeploy
    PagesRef --> PagesDeploy
    WorkersRef --> NPMDeploy
```

Sources: [skills/.curated/cloudflare-deploy/SKILL.md:1-213]()

## Prerequisites and Sandboxing

The skill requires escalated sandbox permissions for network operations. Deployments may fail with timeout, DNS, or connection errors under default sandbox settings. Users should be prompted to rerun with `sandbox_permissions=require_escalated` if deployment network calls are blocked [skills/.curated/cloudflare-deploy/SKILL.md:12-13]().

Deployments typically take several minutes to complete. The skill should use appropriate timeout values and inform users of expected duration [skills/.curated/cloudflare-deploy/SKILL.md:13]().

Sources: [skills/.curated/cloudflare-deploy/SKILL.md:10-13]()

## Authentication Workflow

### Authentication Verification

Before any deployment operation (`wrangler deploy`, `wrangler pages deploy`, or `npm run deploy`), the skill verifies authentication status using:

```bash
npx wrangler whoami
```

This command returns the authenticated account details if successful, or an error if not authenticated [skills/.curated/cloudflare-deploy/SKILL.md:19-21]().

Sources: [skills/.curated/cloudflare-deploy/SKILL.md:15-21]()

### Authentication Methods

```mermaid
sequenceDiagram
    participant Skill as "cloudflare-deploy"
    participant Wrangler as "wrangler CLI"
    participant CF as "Cloudflare API"
    participant Browser as "Browser"
    participant CI as "CI/CD Environment"
    
    Skill->>Wrangler: "npx wrangler whoami"
    
    alt "Already Authenticated"
        Wrangler->>CF: "Verify token"
        CF-->>Wrangler: "Account details"
        Wrangler-->>Skill: "Show account info"
        Skill->>Skill: "Proceed to deployment"
    else "Not Authenticated (Local)"
        Wrangler-->>Skill: "Not authenticated error"
        Skill->>Wrangler: "npx wrangler login"
        Wrangler->>Browser: "Open OAuth flow"
        Browser->>CF: "User authenticates"
        CF-->>Browser: "Auth success"
        Browser-->>Wrangler: "Token stored"
        Wrangler-->>Skill: "Authentication complete"
    else "Not Authenticated (CI/CD)"
        Wrangler-->>Skill: "Not authenticated error"
        Skill->>CI: "Check CLOUDFLARE_API_TOKEN env var"
        CI-->>Skill: "Token value"
        Skill->>Wrangler: "Use token from env"
        Wrangler->>CF: "Authenticate with token"
        CF-->>Wrangler: "Auth success"
    end
```

The skill supports two authentication methods [skills/.curated/cloudflare-deploy/SKILL.md:23-25]():

1. **Interactive/Local**: `wrangler login` triggers a one-time OAuth flow via browser.
2. **CI/CD**: `CLOUDFLARE_API_TOKEN` environment variable for automated pipelines.

Detailed authentication instructions are stored in the `references/wrangler/auth.md` reference file [skills/.curated/cloudflare-deploy/SKILL.md:23]().

Sources: [skills/.curated/cloudflare-deploy/SKILL.md:15-25]()

## Product Selection Decision Trees

The skill uses decision trees to route users to appropriate Cloudflare products based on their requirements. The trees are structured by functional category: compute, storage, AI, networking, security, and media.

### Compute Decision Tree

```mermaid
graph TD
    ComputeEntry["Need to run code?"]
    
    ComputeEntry --> ServerlessEdge["Serverless functions at edge"]
    ComputeEntry --> FullStack["Full-stack web app with Git deploys"]
    ComputeEntry --> Stateful["Stateful coordination/real-time"]
    ComputeEntry --> LongRunning["Long-running multi-step jobs"]
    ComputeEntry --> Containers["Run containers"]
    ComputeEntry --> MultiTenant["Multi-tenant customers deploy code"]
    ComputeEntry --> Cron["Scheduled tasks cron"]
    ComputeEntry --> EdgeLogic["Lightweight edge logic HTTP modification"]
    ComputeEntry --> Observability["Process Worker execution events"]
    ComputeEntry --> Latency["Optimize latency to backend"]
    
    ServerlessEdge --> WorkersRef["references/workers/"]
    FullStack --> PagesRef["references/pages/"]
    Stateful --> DORef["references/durable-objects/"]
    LongRunning --> WorkflowsRef["references/workflows/"]
    Containers --> ContainersRef["references/containers/"]
    MultiTenant --> PlatformsRef["references/workers-for-platforms/"]
    Cron --> CronRef["references/cron-triggers/"]
    EdgeLogic --> SnippetsRef["references/snippets/"]
    Observability --> TailRef["references/tail-workers/"]
    Latency --> SmartPlaceRef["references/smart-placement/"]
```

Sources: [skills/.curated/cloudflare-deploy/SKILL.md:27-43]()

### Storage Decision Tree

```mermaid
graph TD
    StorageEntry["Need storage?"]
    
    StorageEntry --> KVStore["Key-value config, sessions, cache"]
    StorageEntry --> RelationalSQL["Relational SQL"]
    StorageEntry --> ObjectStorage["Object/file storage S3-compatible"]
    StorageEntry --> MessageQueue["Message queue async processing"]
    StorageEntry --> VectorDB["Vector embeddings AI/search"]
    StorageEntry --> EntityState["Strongly-consistent per-entity state"]
    StorageEntry --> SecretsManage["Secrets management"]
    StorageEntry --> StreamETL["Streaming ETL to R2"]
    StorageEntry --> PersistCache["Persistent cache long-term retention"]
    
    KVStore --> KVRef["references/kv/"]
    RelationalSQL --> SQLiteChoice["SQLite or Postgres/MySQL?"]
    SQLiteChoice --> D1Ref["references/d1/<br/>SQLite"]
    SQLiteChoice --> HyperdriveRef["references/hyperdrive/<br/>Existing Postgres/MySQL"]
    ObjectStorage --> R2Ref["references/r2/"]
    MessageQueue --> QueuesRef["references/queues/"]
    VectorDB --> VectorizeRef["references/vectorize/"]
    EntityState --> DOStorageRef["references/durable-objects/<br/>DO storage"]
    SecretsManage --> SecretsRef["references/secrets-store/"]
    StreamETL --> PipelinesRef["references/pipelines/"]
    PersistCache --> CacheReserveRef["references/cache-reserve/"]
```

Sources: [skills/.curated/cloudflare-deploy/SKILL.md:45-58]()

### AI/ML Decision Tree

```mermaid
graph TD
    AIEntry["Need AI?"]
    
    AIEntry --> Inference["Run inference LLMs, embeddings, images"]
    AIEntry --> VectorRAG["Vector database for RAG/search"]
    AIEntry --> Agents["Build stateful AI agents"]
    AIEntry --> Gateway["Gateway for any AI provider caching, routing"]
    AIEntry --> SearchWidget["AI-powered search widget"]
    
    Inference --> WorkersAIRef["references/workers-ai/"]
    VectorRAG --> VectorizeRef2["references/vectorize/"]
    Agents --> AgentsSDKRef["references/agents-sdk/"]
    Gateway --> AIGatewayRef["references/ai-gateway/"]
    SearchWidget --> AISearchRef["references/ai-search/"]
```

Sources: [skills/.curated/cloudflare-deploy/SKILL.md:60-69]()

## Product Catalog

The skill maintains a comprehensive index of Cloudflare products organized by category. Each entry maps to a reference directory containing detailed deployment instructions.

### Compute & Runtime Products

| Product | Reference Path | Primary Use Case |
|---------|----------------|------------------|
| Workers | `references/workers/` | Serverless edge functions [skills/.curated/cloudflare-deploy/SKILL.md:117]() |
| Pages | `references/pages/` | Static sites with Git integration [skills/.curated/cloudflare-deploy/SKILL.md:118]() |
| Durable Objects | `references/durable-objects/` | Stateful coordination primitives [skills/.curated/cloudflare-deploy/SKILL.md:120]() |
| Workflows | `references/workflows/` | Long-running multi-step jobs [skills/.curated/cloudflare-deploy/SKILL.md:121]() |

Sources: [skills/.curated/cloudflare-deploy/SKILL.md:115-127]()

### Storage & Data Products

| Product | Reference Path | Storage Type |
|---------|----------------|--------------|
| KV | `references/kv/` | Key-value store [skills/.curated/cloudflare-deploy/SKILL.md:132]() |
| D1 | `references/d1/` | SQLite database [skills/.curated/cloudflare-deploy/SKILL.md:133]() |
| R2 | `references/r2/` | S3-compatible object storage [skills/.curated/cloudflare-deploy/SKILL.md:134]() |
| Queues | `references/queues/` | Message queuing [skills/.curated/cloudflare-deploy/SKILL.md:135]() |

Sources: [skills/.curated/cloudflare-deploy/SKILL.md:130-141]()

## Deployment Workflow

### General Deployment Pattern

```mermaid
sequenceDiagram
    participant User as "User"
    participant Skill as "cloudflare-deploy"
    participant DecisionTree as "Decision Trees"
    participant Ref as "Product Reference"
    participant Wrangler as "wrangler CLI"
    participant CF as "Cloudflare API"
    
    User->>Skill: "Request deployment"
    Skill->>Wrangler: "npx wrangler whoami"
    
    alt "Not Authenticated"
        Wrangler-->>Skill: "Auth error"
        Skill->>Skill: "Load references/wrangler/auth.md"
        Skill->>User: "Guide through wrangler login"
        User->>Wrangler: "npx wrangler login"
        Wrangler->>CF: "OAuth flow"
        CF-->>Wrangler: "Token stored"
    end
    
    Skill->>DecisionTree: "Route by requirements"
    DecisionTree->>Ref: "Load product reference"
    Ref-->>Skill: "Deployment instructions"
    
    Skill->>Wrangler: "Execute deployment command"
    Note over Wrangler: "wrangler deploy or<br/>wrangler pages deploy or<br/>npm run deploy"
    
    Wrangler->>CF: "Upload assets/code"
    CF->>CF: "Build and deploy"
    CF-->>Wrangler: "Deployment URL"
    Wrangler-->>Skill: "Success + URL"
    Skill-->>User: "Report deployment URL"
```

Sources: [skills/.curated/cloudflare-deploy/SKILL.md:15-213]()

## Troubleshooting

### Escalated Network Access

When deployment commands fail due to network issues (timeouts, DNS errors, connection resets), the skill should prompt users to rerun with escalated sandbox permissions [skills/.curated/cloudflare-deploy/SKILL.md:216-218](). This typically occurs when sandbox networking blocks outbound requests to Cloudflare's API.

The recommended user-facing guidance:
```
The deploy needs escalated network access to deploy to Cloudflare. I can rerun the command with escalated permissions—want me to proceed?
```
Sources: [skills/.curated/cloudflare-deploy/SKILL.md:216-222]()

### Integration with Other Deployment Skills

The `cloudflare-deploy` skill is part of a broader deployment tools suite:

- **[Netlify Deploy](5.5.1)**: Alternative for JAMstack sites with Netlify-specific features using `npx netlify` [skills/.curated/netlify-deploy/SKILL.md:2-3]().
- **[Render Deploy](5.5.4)**: Full-stack applications with databases and background workers using `render.yaml` Blueprints or Direct Creation [skills/.curated/render-deploy/SKILL.md:2-12]().

Sources: [skills/.curated/cloudflare-deploy/SKILL.md:1-10](), [skills/.curated/netlify-deploy/SKILL.md:1-10](), [skills/.curated/render-deploy/SKILL.md:1-15]()

---

