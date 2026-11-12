<!-- source: DeepWiki mcp.deepwiki.com · repo openai/skills · extra page Vercel Deploy · fetched 2026-10-30 -->

# Vercel Deploy

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [skills/.curated/vercel-deploy/SKILL.md](skills/.curated/vercel-deploy/SKILL.md)
- [skills/.curated/vercel-deploy/agents/openai.yaml](skills/.curated/vercel-deploy/agents/openai.yaml)
- [skills/.curated/vercel-deploy/assets/vercel.png](skills/.curated/vercel-deploy/assets/vercel.png)
- [skills/.curated/vercel-deploy/scripts/deploy.sh](skills/.curated/vercel-deploy/scripts/deploy.sh)

</details>



## Purpose and Scope

This document details the `vercel-deploy` skill, which enables zero-configuration deployment of applications and websites to the Vercel platform. The skill provides two primary paths: a native Vercel CLI-based workflow for environments with existing credentials, and a specialized fallback script-based deployment path for sandboxed or unauthenticated environments.

For other cloud deployment options, see [Netlify Deploy [5.5.1]](), [Cloudflare Deploy [5.5.3]](), and [Render Deploy [5.5.4]]().

---

## Deployment Strategies

The skill implements a hierarchical execution strategy to ensure deployment success regardless of the local environment's authentication state.

### 1. CLI-Based Deployment (Preferred)
If the Vercel CLI is present, the skill attempts a direct deployment. This method is preferred as it utilizes the user's local configuration and existing project links.

- **Check**: `command -v vercel` [skills/.curated/vercel-deploy/SKILL.md:18-22]()
- **Command**: `vercel deploy [path] -y` [skills/.curated/vercel-deploy/SKILL.md:24-27]()
- **Timeout**: A 10-minute (600,000ms) timeout is enforced to accommodate remote builds [skills/.curated/vercel-deploy/SKILL.md:29-29]().

### 2. Fallback Script-Based Deployment
If the CLI is missing or returns an authentication error ("No existing credentials found"), the skill executes a specialized deployment script [skills/.curated/vercel-deploy/SKILL.md:31-35]().

- **Script Path**: `scripts/deploy.sh` [skills/.curated/vercel-deploy/scripts/deploy.sh:1-5]()
- **Mechanism**: Packages the project into a tarball and uploads it to a claimable deployment endpoint `https://codex-deploy-skills.vercel.sh/api/deploy` [skills/.curated/vercel-deploy/scripts/deploy.sh:9-9]().
- **Output**: Returns JSON containing a `previewUrl` and a `claimUrl` [skills/.curated/vercel-deploy/SKILL.md:50-52]().

---

## Implementation Details: `deploy.sh`

The fallback script handles complex logic for framework detection and project staging to ensure Vercel can build the project correctly without manual intervention.

### Framework Detection
The `detect_framework` function parses `package.json` to identify the specific technology stack. This allows the deployment API to apply the correct build settings.

| Framework Category | Detection Logic (Dependencies) | Internal Identifier |
|--------------------|--------------------------------|---------------------|
| Meta-frameworks    | `next`, `blitz`, `gatsby`, `astro` | `nextjs`, `blitzjs`, etc. |
| Modern SSR         | `@remix-run/`, `@tanstack/start` | `remix`, `tanstack-start` |
| SPAs               | `react-scripts`, `vue`, `svelte` | `create-react-app`, etc. |
| Static/SSG         | `vitepress`, `docusaurus`, `hexo` | `vitepress`, `docusaurus-2` |
| Backend/API        | `express`, `nestjs`, `hono` | `express`, `nestjs`, etc. |

**Sources**: [skills/.curated/vercel-deploy/scripts/deploy.sh:12-162]()

### Data Flow and Staging
The script creates a clean deployment package by staging files in a temporary directory, ensuring sensitive data and heavy artifacts are excluded.

```mermaid
graph TD
    subgraph "Local Filesystem"
        [ProjectDir]
        [PkgJson]
    end

    subgraph "deploy.sh Execution"
        ["detect_framework()"]
        ["mktemp -d"]
        ["tar -cf - . --exclude='node_modules'"]
        ["Static HTML Index Fix"]
        ["tar -czf project.tgz"]
    end

    subgraph "Remote API"
        ["DEPLOY_ENDPOINT"]
    end

    [ProjectDir] --> ["detect_framework()"]
    [ProjectDir] --> ["tar -cf - . --exclude='node_modules'"]
    ["tar -cf - . --exclude='node_modules'"] --> ["mktemp -d"]
    ["mktemp -d"] --> ["Static HTML Index Fix"]
    ["Static HTML Index Fix"] --> ["tar -czf project.tgz"]
    ["tar -czf project.tgz"] --> ["DEPLOY_ENDPOINT"]
```
**Diagram: Vercel Deploy Script Data Flow**

**Sources**: [skills/.curated/vercel-deploy/scripts/deploy.sh:9-9](), [skills/.curated/vercel-deploy/scripts/deploy.sh:165-231]()

---

## Skill Interface Configuration

The `vercel-deploy` skill defines its user-facing interface through the `openai.yaml` configuration file.

### Interface Metadata
| Field | Value | Purpose |
|-------|-------|---------|
| `display_name` | "Vercel Deploy" | User-facing name [skills/.curated/vercel-deploy/agents/openai.yaml:2]() |
| `short_description` | "Deploy apps and agents with zero configuration..." | Brief summary [skills/.curated/vercel-deploy/agents/openai.yaml:3]() |
| `default_prompt` | "Create a Vercel deployment for this project and share the URL." | Default action prompt [skills/.curated/vercel-deploy/agents/openai.yaml:6]() |

### Security and Permissions
The skill documentation specifies how to handle sandboxed environments:
- **Default**: No escalated permissions for CLI checks [skills/.curated/vercel-deploy/SKILL.md:12-13]().
- **Escalation**: If network calls are blocked (timeouts/DNS errors), the deploy command should be rerun with `sandbox_permissions=require_escalated` [skills/.curated/vercel-deploy/SKILL.md:69-72]().

---

## Code Entity Mapping

The following diagrams map the logical deployment concepts and data processing to specific code entities within the skill directory.

### Intent to Entity Mapping
```mermaid
graph LR
    subgraph "Natural Language Intent"
        ["'Deploy my app'"]
        ["'Push to production'"]
    end

    subgraph "Code Entity Space"
        ["SKILL.md"]
        ["scripts/deploy.sh"]
        ["agents/openai.yaml"]
        
        subgraph "Functions in deploy.sh"
            ["detect_framework()"]
            ["cleanup()"]
            ["has_dep_exact()"]
        end
    end

    ["'Deploy my app'"] --> ["SKILL.md"]
    ["'Push to production'"] -->|"--prod"| ["SKILL.md"]
    ["SKILL.md"] -->|Fallback| ["scripts/deploy.sh"]
    ["scripts/deploy.sh"] --> ["detect_framework()"]
    ["detect_framework()"] --> ["has_dep_exact()"]
    ["agents/openai.yaml"] -->|Interface| ["'Deploy my app'"]
```
**Diagram: Vercel Deploy Intent to Code Mapping**

### Deployment Logic Flow
```mermaid
graph TD
    subgraph "Skill Logic"
        ["SKILL.md"]
    end

    subgraph "CLI Flow"
        ["command -v vercel"]
        ["vercel deploy -y"]
    end

    subgraph "Script Flow (deploy.sh)"
        ["detect_framework()"]
        ["has_dep_exact()"]
        ["has_dep_prefix()"]
        ["cleanup()"]
    end

    ["SKILL.md"] --> ["command -v vercel"]
    ["command -v vercel"] -- "Found" --> ["vercel deploy -y"]
    ["command -v vercel"] -- "Missing/Auth Error" --> ["detect_framework()"]
    ["detect_framework()"] --> ["has_dep_exact()"]
    ["detect_framework()"] --> ["has_dep_prefix()"]
    ["detect_framework()"] --> ["cleanup()"]
```
**Diagram: Deployment Execution Paths**

**Sources**: [skills/.curated/vercel-deploy/SKILL.md:1-8](), [skills/.curated/vercel-deploy/scripts/deploy.sh:12-12](), [skills/.curated/vercel-deploy/scripts/deploy.sh:25-27](), [skills/.curated/vercel-deploy/scripts/deploy.sh:29-31](), [skills/.curated/vercel-deploy/scripts/deploy.sh:173-178](), [skills/.curated/vercel-deploy/agents/openai.yaml:1-7]()

---

