<!-- source: DeepWiki mcp.deepwiki.com · repo AgentsMesh/AgentsMesh · page 7 Development Environment · fetched 2026-10-26 -->

# Development Environment

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.claude/skills/worktree/SKILL.md](.claude/skills/worktree/SKILL.md)
- [CLAUDE.md](CLAUDE.md)
- [deploy/dev/.gitignore](deploy/dev/.gitignore)
- [deploy/dev/backend.Dockerfile](deploy/dev/backend.Dockerfile)
- [deploy/dev/dev.sh](deploy/dev/dev.sh)
- [deploy/dev/docker-compose.yml](deploy/dev/docker-compose.yml)
- [deploy/dev/gitea/init-gitea.sh](deploy/dev/gitea/init-gitea.sh)
- [deploy/dev/init-seed.sh](deploy/dev/init-seed.sh)
- [deploy/dev/nginx/conf.d/default.conf](deploy/dev/nginx/conf.d/default.conf)
- [deploy/dev/nginx/nginx.conf](deploy/dev/nginx/nginx.conf)
- [deploy/dev/runner-entrypoint.sh](deploy/dev/runner-entrypoint.sh)
- [deploy/dev/runner-ssh/id_ed25519.pub](deploy/dev/runner-ssh/id_ed25519.pub)
- [deploy/dev/runner.Dockerfile](deploy/dev/runner.Dockerfile)
- [deploy/dev/seed/seed.sql](deploy/dev/seed/seed.sql)
- [deploy/dev/traefik/dynamic/grpc.yml](deploy/dev/traefik/dynamic/grpc.yml)
- [deploy/dev/web.Dockerfile](deploy/dev/web.Dockerfile)
- [relay/.air.toml](relay/.air.toml)
- [runner/.gitignore](runner/.gitignore)
- [runner/internal/config/config_grpc_test.go](runner/internal/config/config_grpc_test.go)
- [runner/internal/envpath/envpath_test.go](runner/internal/envpath/envpath_test.go)
- [web/src/components/ui/block-editor.tsx](web/src/components/ui/block-editor.tsx)
- [web/src/lib/api/base.ts](web/src/lib/api/base.ts)

</details>



This page covers the local development environment setup for AgentsMesh: the `dev.sh` one-click script, how it configures and starts all services, worktree port isolation, seed data, and common workflows.

For details on each individual Docker Compose service (images, volumes, health checks), see [Docker Compose Services](#7.1). For the local runner binary build process and Gitea initialization, see [Local Runner and Gitea Setup](#7.2).

---

## Overview

The development environment lives entirely under `deploy/dev/`. The entry point is a single script, `deploy/dev/dev.sh`, which handles all first-time setup and idempotent restarts. It starts Docker backend services while the web frontend runs on the host for faster Turbopack iteration.

**Key design decisions:**
- Multiple git worktrees can run simultaneously with isolated port ranges.
- The frontend (`web/`) runs locally via `pnpm dev --turbopack`, not in Docker.
- All URLs (API, WebSocket, OAuth callbacks) derive from a single `PRIMARY_DOMAIN` variable.
- Hot reload is enabled for backend, runner, and relay via [Air](https://github.com/air-verse/air).

---

## Prerequisites

| Tool | Minimum Version | Purpose |
|------|----------------|---------|
| Docker Desktop | 4.x | All backend services |
| `pnpm` | 8.x | Frontend dependency management |
| `git` | 2.x | Worktree support |
| `openssl` | 3.x | Dev SSL cert generation |
| `ssh-keygen` | bundled with OpenSSH | Gitea deploy key generation |

---

## Quick Start

```bash
cd deploy/dev
./dev.sh               # First-time setup and start
./dev.sh --clean       # Stop all services and remove volumes
./dev.sh --reset-runners  # Kill stale runner processes and restart containers
```

After `./dev.sh` completes, the environment is ready:

| Service | Address | Notes |
|---------|---------|-------|
| Frontend | `http://localhost:<WEB_PORT>` | Next.js, Turbopack, local process |
| API | `http://localhost:<HTTP_PORT>/api` | Via Traefik |
| Relay (WebSocket) | `ws://localhost:<HTTP_PORT>/relay` | Via Traefik |
| gRPC (mTLS) | `grpcs://localhost:<GRPC_PORT>` | TLS passthrough via Traefik |
| Gitea | `http://localhost:<GITEA_HTTP_PORT>` | `gitea-admin` / `gitea-admin-123` |
| Traefik Dashboard | `http://localhost:<TRAEFIK_DASHBOARD_PORT>` | |
| Adminer | `http://localhost:<ADMINER_PORT>` | |
| MinIO Console | `http://localhost:<MINIO_CONSOLE_PORT>` | |

Test accounts (seeded automatically):
- **User**: `dev@agentsmesh.local` / `devpass123`
- **Admin**: `admin@agentsmesh.local` / `adminpass123`

Sources: [deploy/dev/dev.sh:626-655](), [CLAUDE.md:33-48]()

---

## Initialization Flow

The `main()` function in `dev.sh` runs the following steps in order:

**`dev.sh` Initialization Sequence**

```mermaid
flowchart TD
    A["main()"] --> B["generate_ssl_certs()"]
    B --> C["generate_ai_cli_configs()"]
    C --> D["generate_env()"]
    D --> E["generate_traefik_config()"]
    E --> F["generate_web_env()"]
    F --> G["docker compose up -d --build"]
    G --> H["wait_for_service(postgres)"]
    H --> I["run_migrations()"]
    I --> J["init_seed(pg_container)"]
    J --> K["generate_runner_ssh_key()"]
    K --> L["init_gitea()"]
    L --> M["setup_gitea_ssh_config()"]
    M --> N["chown /workspace (runner container)"]
    N --> O["start_frontend()"]
    O --> P["build_runner_local()"]
    P --> Q["show_result()"]

    B -->|"ssl/ca.crt already exists"| skip1["skip"]
    D -->|".env matches current project"| skip2["preserve existing ports"]
    J -->|"dev@agentsmesh.local exists"| skip3["skip"]
    P -->|"source hash unchanged"| skip4["skip build"]
```

Sources: [deploy/dev/dev.sh:804-893]()

---

### Step Details

#### Step 1–2: SSL Certs and AI CLI Configs

`generate_ssl_certs()` calls `generate-dev-certs.sh` to produce a CA keypair at `deploy/dev/ssl/ca.crt` and `ca.key`. These are used for mTLS between the backend and runners.

`generate_ai_cli_configs()` writes pre-configured settings for Claude Code (`settings.json`), OpenAI Codex (`config.toml`), and Gemini CLI (`settings.json`) to `deploy/dev/ai-cli-configs/`. These are copied into the runner container image by [deploy/dev/runner.Dockerfile:98-100]().

Sources: [deploy/dev/dev.sh:72-127]()

#### Step 3: `.env` Generation and Port Allocation

`generate_env()` computes a port offset from the current worktree name. Ports are spaced 50 apart per worktree, giving a range that supports up to 500 concurrent worktrees.

```
HTTP_PORT   = 10000 + offset * 50
GRPC_PORT   = 10001 + offset * 50
POSTGRES_PORT = 10002 + offset * 50
...
GITEA_SSH_PORT = 10010 + offset * 50
```

The `main` worktree always gets offset `0` (ports starting at `10000`). Other worktrees get a deterministic offset from an MD5 hash of the branch name.

If `.env` already exists for the current `COMPOSE_PROJECT_NAME`, `generate_env()` preserves the existing ports to keep runner configurations stable.

Sources: [deploy/dev/dev.sh:42-244]()

**Port Allocation Scheme**

```mermaid
flowchart LR
    subgraph "Worktree: main (offset=0)"
        H0["HTTP_PORT=10000"]
        G0["GRPC_PORT=10001"]
        P0["POSTGRES_PORT=10002"]
        R0["REDIS_PORT=10003"]
        W0["WEB_PORT=10007"]
    end
    subgraph "Worktree: feature-xyz (offset=N)"
        HN["HTTP_PORT=10000+N*50"]
        GN["GRPC_PORT=10001+N*50"]
        PN["POSTGRES_PORT=10002+N*50"]
        RN["REDIS_PORT=10003+N*50"]
        WN["WEB_PORT=10007+N*50"]
    end
```

Sources: [deploy/dev/dev.sh:185-220]()

#### Step 4–5: Traefik and Web `.env.local`

`generate_traefik_config()` writes `deploy/dev/traefik/traefik.yml` with the Docker Compose project name embedded so Traefik only discovers containers from the current worktree's project. This prevents cross-worktree routing conflicts.

`generate_web_env()` writes `web/.env.local` with:
- `PRIMARY_DOMAIN=localhost:<HTTP_PORT>`
- `NEXT_PUBLIC_WS_URL=ws://127.0.0.1:<HTTP_PORT>` (direct; Next.js rewrites don't support WebSocket proxy)
- `API_PROXY_TARGET=http://127.0.0.1:<HTTP_PORT>` (server-side proxy target)

Sources: [deploy/dev/dev.sh:129-283]()

#### Step 6–8: Docker Services, Migrations, and Seed Data

`docker compose up -d --build` starts all services defined in `docker-compose.yml`. The backend container image includes `golang-migrate`, and `run_migrations()` executes it inside the running container:

```bash
docker exec <backend_container> migrate \
  -path /app/migrations \
  -database "postgres://agentsmesh:agentsmesh_dev@postgres:5432/agentsmesh?sslmode=disable" \
  up
```

`init_seed()` checks whether `dev@agentsmesh.local` already exists before applying `deploy/dev/seed/seed.sql`.

Sources: [deploy/dev/dev.sh:301-409](), [deploy/dev/seed/seed.sql:1-289]()

#### Steps 9–9.6: Gitea, SSH Keys

`generate_runner_ssh_key()` creates an ed25519 keypair at `deploy/dev/runner-ssh/id_ed25519` if absent. The private key is gitignored.

`init_gitea()` calls `deploy/dev/gitea/init-gitea.sh`, which:
1. Creates the `gitea-admin` user via the Gitea CLI.
2. Creates the `dev-org` organization.
3. Creates and seeds `demo-webapp` and `demo-api` repositories from `deploy/dev/gitea/repos/`.
4. Registers the runner's public key as a deploy key on both repos.

`setup_gitea_ssh_config()` injects a `Host gitea` block into `~/.ssh/config`, mapping `gitea` → `127.0.0.1:<GITEA_SSH_PORT>`. This lets local runners clone `git@gitea:org/repo.git` URLs from outside Docker. The block is managed (removed and rewritten on each run) to stay in sync with port changes.

Sources: [deploy/dev/dev.sh:437-497](), [deploy/dev/gitea/init-gitea.sh:1-244]()

#### Step 10–11.5: Frontend and Runner Binary

`start_frontend()` runs `pnpm dev --turbopack --port <WEB_PORT>` in the background, logging to `deploy/dev/web.log`. It detects stale Next.js lock files and clears the Turbopack cache before restarting.

`build_runner_local()` compiles the runner binary for `darwin/arm64` inside a Docker container (using `golang:1.25-alpine`) so no local Go installation is required. The output is installed to `~/.local/bin/agentsmesh-runner`. A source hash (based on `git rev-parse HEAD:runner HEAD:proto` plus uncommitted diffs) is cached in `runner/.local-build-hash`; the build is skipped when source is unchanged.

Sources: [deploy/dev/dev.sh:658-802]()

---

## Docker Service Architecture

**Docker Compose Network Topology**

```mermaid
flowchart TB
    Browser["Browser"]
    LocalFrontend["Next.js\n(local host process)\nWEB_PORT"]
    LocalRunner["agentsmesh-runner\n(local binary)\n~/.local/bin/"]

    subgraph "Docker Network: agentsmesh-<worktree>_default"
        Traefik["traefik\nHTTP_PORT -> :80\nGRPC_PORT -> :9443\nDASHBOARD_PORT -> :8080"]
        Backend["backend\n:8080\nAir hot reload"]
        Runner["runner\n:9090\nAir hot reload"]
        Relay["relay\n:8090\nAir hot reload"]
        Postgres["postgres\n:5432"]
        Redis["redis\n:6379"]
        MinIO["minio\n:9000 (API)\n:9001 (Console)"]
        Gitea["gitea\n:3000 (HTTP)\n:22 (SSH)"]
        Adminer["adminer\n:8080"]
    end

    Browser -->|"HTTP /api"| Traefik
    Browser -->|"ws /relay"| Traefik
    LocalFrontend -->|"API_PROXY_TARGET (server-side)"| Traefik
    LocalFrontend -->|"NEXT_PUBLIC_WS_URL (direct WS)"| Traefik
    LocalRunner -->|"grpcs GRPC_PORT"| Traefik

    Traefik -->|"/api PathPrefix"| Backend
    Traefik -->|"/relay PathPrefix + strip"| Relay
    Traefik -->|"TCP TLS passthrough :9443"| Backend

    Backend --> Postgres
    Backend --> Redis
    Backend --> MinIO
    Backend -->|"internal HTTP"| Relay

    Runner -->|"gRPC mTLS traefik:9443"| Traefik
    Runner -->|"SSH git@gitea"| Gitea
    Runner -->|"REST http://backend:8080"| Backend
```

Sources: [deploy/dev/docker-compose.yml:1-420](), [deploy/dev/traefik/dynamic/grpc.yml:1-20]()

---

## Seed Data

The seed script `deploy/dev/seed/seed.sql` is idempotent (uses `WHERE NOT EXISTS`). It creates:

| Entity | Value |
|--------|-------|
| User | `dev@agentsmesh.local` / `devpass123` |
| Admin | `admin@agentsmesh.local` / `adminpass123` |
| Organization | `dev-org` (slug), Pro plan, active |
| Runner | node_id `dev-runner`, org `dev-org` |
| Runner token | `dev-runner-token` (pre-hashed bcrypt) |
| Tickets | `DEV-1`, `DEV-2` |
| Git provider | Local Gitea at `http://gitea:3000` |
| Repositories | `dev-org/demo-webapp`, `dev-org/demo-api` |

The runner Docker container's `runner-entrypoint.sh` generates its own mTLS client cert from the CA at startup and writes a `config.yaml` to `/home/runner/.agentsmesh/config.yaml`. The cert CN matches the `node_id` (`dev-runner`) and the org (`dev-org`).

Sources: [deploy/dev/seed/seed.sql:1-289](), [deploy/dev/runner-entrypoint.sh:255-301]()

---

## Hot Reload

All three Go services use [Air](https://github.com/air-verse/air) for automatic rebuild on file changes. Source code directories are bind-mounted into the containers.

| Service | Config | Watch scope |
|---------|--------|-------------|
| Backend | `backend/.air.toml` | `backend/` |
| Runner | `runner/.air.toml` | `runner/` |
| Relay | `relay/.air.toml` | `relay/` |

The relay Air config sets `kill_delay = "5s"` to ensure the old process releases port `8090` before the new binary attempts to bind it.

The frontend uses Next.js Turbopack fast refresh running on the host. If a stale `.next/dev/lock` file is detected, `start_frontend()` clears both the lock and the Turbopack cache before restarting.

Sources: [relay/.air.toml:1-52](), [deploy/dev/dev.sh:657-729](), [deploy/dev/docker-compose.yml:215-224]()

---

## Common Workflows

### Viewing Logs

```bash
# Frontend
tail -f deploy/dev/web.log

# Backend (in deploy/dev directory)
docker compose logs -f backend

# Runner
docker compose logs -f runner

# All services
docker compose logs -f
```

### Running Database Migrations

Migrations are run automatically by `dev.sh`. To run manually inside the backend container:

```bash
docker exec <COMPOSE_PROJECT_NAME>-backend-1 migrate \
  -path /app/migrations \
  -database "postgres://agentsmesh:agentsmesh_dev@postgres:5432/agentsmesh?sslmode=disable" \
  up
```

To create a new migration file (requires `golang-migrate` installed locally):

```bash
brew install golang-migrate
migrate create -ext sql -dir backend/migrations -seq add_new_feature
```

### Using a Local Runner Binary

After `dev.sh` builds and installs the runner to `~/.local/bin/agentsmesh-runner`, register and start it:

```bash
agentsmesh-runner register \
  --server http://localhost:<HTTP_PORT> \
  --token <TOKEN>

agentsmesh-runner run
```

The `--reset-runners` flag in `dev.sh` stops stale local runner processes and restarts the Docker runner and relay containers:

```bash
./dev.sh --reset-runners
```

### Working with Multiple Worktrees

Each git worktree gets an isolated `COMPOSE_PROJECT_NAME` (`agentsmesh-<worktree-name>`) and a unique port range. Worktrees can run simultaneously without conflicts.

```bash
# Create a worktree
git worktree add -b feature/my-feature ../AgentsMesh-Worktrees/feature-my-feature origin/main
cd ../AgentsMesh-Worktrees/feature-my-feature

# Start its own environment
cd deploy/dev && ./dev.sh
```

The `.env` file stores the computed port offset. If `.env` already exists for the project name, existing ports are preserved on subsequent `dev.sh` runs.

Sources: [deploy/dev/dev.sh:42-68](), [deploy/dev/dev.sh:171-245](), [deploy/dev/dev.sh:499-594](), [.claude/skills/worktree/SKILL.md:1-118]()

### Full Teardown

```bash
cd deploy/dev
./dev.sh --clean
```

This stops all containers, removes volumes, and deletes `.env`. Note that this also removes all database data, MinIO data, and Gitea data. Re-running `./dev.sh` will re-initialize everything from scratch.

Sources: [deploy/dev/dev.sh:596-623]()

---

## Environment Variables Reference

The generated `deploy/dev/.env` and `web/.env.local` share a unified domain configuration pattern. All service URLs are derived from two variables:

| Variable | Dev Default | Description |
|----------|-------------|-------------|
| `PRIMARY_DOMAIN` | `localhost:<HTTP_PORT>` | Base domain for all URLs |
| `USE_HTTPS` | `false` | Protocol scheme (`http` vs `https`) |
| `HTTP_PORT` | `10000` (main) | Traefik HTTP listener host port |
| `GRPC_PORT` | `10001` (main) | Traefik gRPC passthrough host port |
| `POSTGRES_PASSWORD` | `agentsmesh_dev` | Shared between backend and init scripts |
| `JWT_SECRET` | `dev-jwt-secret-...` | Must match between backend and relay |
| `INTERNAL_API_SECRET` | `dev-internal-secret` | Used by relay to call backend internal API |
| `ANTHROPIC_AUTH_TOKEN` | *(empty)* | Optional: fill in to use Claude Code |

The `COMPOSE_PROJECT_NAME` variable (set to `agentsmesh-<worktree>`) is the isolation key for all Docker resources: containers, networks, and volumes all receive this prefix.

Sources: [deploy/dev/dev.sh:195-243](), [deploy/dev/dev.sh:254-283](), [deploy/dev/docker-compose.yml:120-215]()

---

