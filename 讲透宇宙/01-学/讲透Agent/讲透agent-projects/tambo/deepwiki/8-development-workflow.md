<!-- source: DeepWiki mcp.deepwiki.com · repo tambo-ai/tambo · page 8 Development Workflow · fetched 2026-10-29 -->

# Development Workflow

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/workflows/ci.yml](.github/workflows/ci.yml)
- [.github/workflows/claude.yml](.github/workflows/claude.yml)
- [.github/workflows/cli-non-interactive.yml](.github/workflows/cli-non-interactive.yml)
- [.github/workflows/docker.yml](.github/workflows/docker.yml)
- [.github/workflows/mcp-everything-docker-cloud.yml](.github/workflows/mcp-everything-docker-cloud.yml)
- [.github/workflows/migrate-db.yml](.github/workflows/migrate-db.yml)
- [.github/workflows/release-please-sync-lockfile.yml](.github/workflows/release-please-sync-lockfile.yml)
- [.github/workflows/release-please.yml](.github/workflows/release-please.yml)
- [.github/workflows/stainless-cloud.yml](.github/workflows/stainless-cloud.yml)
- [.github/workflows/template-maintenance.yml](.github/workflows/template-maintenance.yml)
- [CONTRIBUTING.md](CONTRIBUTING.md)

</details>



This page covers the complete development workflow for contributors to the Tambo AI monorepo, including local setup, quality checks, continuous integration, database migrations, and the release process. For deployment and self-hosting instructions, see the OPERATORS.md documentation.

## Overview

The Tambo monorepo uses a fully automated development workflow built on:
- **Turborepo** for monorepo orchestration and caching
- **Conventional Commits** for automated versioning
- **Release Please** for automated releases and changelogs
- **GitHub Actions** for CI/CD automation
- **Drizzle ORM** for database migrations

All quality checks, deployments, and releases are automated through GitHub Actions workflows.

---

## Local Development Setup

### Prerequisites and Tool Management

The repository uses **mise** for version management of Node.js and other tools.

| Tool | Version Source | Notes |
|------|---------------|-------|
| Node.js | `.node-version` | Also synced to `.nvmrc` for nvm compatibility |
| npm | `mise.toml` | Minimum version 11 required |
| Other tools | `mise.toml` | Renovate keeps versions up to date |

**Installation:**

```bash
# Install mise (see https://mise.jdx.dev/getting-started.html)
mise install              # Install/update all tools to correct versions
eval "$(mise activate)"   # For interactive shells
```

For CI/non-interactive shells, use `mise exec -- <command>` instead of activating mise.

**Sources:** [AGENTS.md:54-78](), [CONTRIBUTING.md:11-23]()

---

### Environment Configuration

```mermaid
graph TB
    subgraph "Environment Files Required"
        ApiEnv["apps/api/.env<br/>(from .env.example)"]
        WebEnv["apps/web/.env.local<br/>(from .env.example)"]
        DbEnv["packages/db/.env<br/>(from .env.example)"]
    end
    
    subgraph "Database Options"
        Supabase["Supabase (Recommended)<br/>Port 54322"]
        Docker["Docker PostgreSQL<br/>Port 5433"]
    end
    
    subgraph "Required Secrets"
        DatabaseUrl["DATABASE_URL"]
        ApiKeySecret["API_KEY_SECRET"]
        ProviderKeySecret["PROVIDER_KEY_SECRET"]
        NextAuthSecret["NEXTAUTH_SECRET"]
    end
    
    ApiEnv --> DatabaseUrl
    WebEnv --> DatabaseUrl
    DbEnv --> DatabaseUrl
    
    ApiEnv --> ApiKeySecret
    ApiEnv --> ProviderKeySecret
    WebEnv --> ApiKeySecret
    WebEnv --> ProviderKeySecret
    WebEnv --> NextAuthSecret
    
    Supabase -.->|"postgresql://postgres:postgres@127.0.0.1:54322/postgres"| DatabaseUrl
    Docker -.->|"postgresql://postgres:postgres@localhost:5433/tambo"| DatabaseUrl
```

**Setup Steps:**

```bash
# Copy environment files
cp apps/api/.env.example apps/api/.env
cp apps/web/.env.example apps/web/.env.local
cp packages/db/.env.example packages/db/.env
```

**Database Setup (Choose One):**

**Option A: Supabase (Recommended)**
```bash
npm install -g supabase
supabase start  # Starts PostgreSQL on port 54322
```

**Option B: Docker PostgreSQL**
```bash
./scripts/cloud/tambo-setup.sh  # Creates docker.env
docker compose --env-file docker.env up postgres -d
# Update DATABASE_URL in all three env files to use port 5433
```

**Initialize Database:**
```bash
npm run db:migrate -w packages/db
```

**Sources:** [CONTRIBUTING.md:25-82](), [AGENTS.md:54-78]()

---

### Development Server Commands

```mermaid
graph LR
    subgraph "Tambo Cloud Platform"
        DevCloud["npm run dev:cloud"]
        Web["apps/web<br/>Port 8260"]
        API["apps/api<br/>Port 8261"]
    end
    
    subgraph "React SDK Framework"
        Dev["npm run dev"]
        Showcase["showcase<br/>Port 8262"]
        Docs["docs<br/>Port 8263"]
    end
    
    DevCloud --> Web
    DevCloud --> API
    Dev --> Showcase
    Dev --> Docs
```

| Command | Starts | Ports |
|---------|--------|-------|
| `npm run dev:cloud` | Tambo Cloud (web + API) | 8260, 8261 |
| `npm run dev` | React SDK (showcase + docs) | 8262, 8263 |
| `npm run dev -w cli` | CLI package only | N/A |
| `npm run dev -w react-sdk` | React SDK package only | N/A |

**Turbo Alternative:**
```bash
turbo dev              # Start all packages
turbo dev --filter=cli # Start specific package
```

**Sources:** [AGENTS.md:303-333](), [CONTRIBUTING.md:84-107]()

---

## Quality Checks and Pre-Commit Workflow

### Required Checks Before Committing

All contributors must run these commands before committing:

```bash
npm run lint           # ESLint across all packages
npm run check-types    # TypeScript type checking
npm test               # Jest unit and integration tests
npm run format         # Prettier code formatting
```

These same checks run automatically in CI and must pass for PRs to be merged.

**Sources:** [AGENTS.md:389-398](), [CONTRIBUTING.md:108-124]()

---

### Testing Infrastructure

```mermaid
graph TB
    subgraph "Test Organization"
        UnitTests["Unit Tests<br/>*.test.ts<br/>Co-located with source"]
        IntegrationTests["Integration Tests<br/>__tests__/<br/>Scenario-based"]
        E2ETests["E2E Tests<br/>apps/api/test/<br/>Supertest + Jest"]
    end
    
    subgraph "Test Execution"
        Jest["Jest Test Runner"]
        Coverage["Coverage Reporting<br/>--coverage flag"]
    end
    
    subgraph "Mock Strategy"
        SystemBoundaries["System Boundaries Only<br/>External APIs, DB, I/O"]
        NoInternalMocks["No Internal Mocking<br/>Real code paths"]
    end
    
    UnitTests --> Jest
    IntegrationTests --> Jest
    E2ETests --> Jest
    
    Jest --> Coverage
    
    Jest --> SystemBoundaries
    Jest --> NoInternalMocks
```

**Test File Conventions:**

| Test Type | Location | Naming |
|-----------|----------|--------|
| Unit tests | Beside source file | `foo.test.ts` (same directory as `foo.ts`) |
| Integration tests | `__tests__/` directory | Descriptive scenario names |
| Fixtures/mocks | `__fixtures__/` or `__mocks__/` | At package source root |

**Test Commands:**

```bash
npm test                    # Run all tests
npm test -- -- --coverage   # With coverage report (note: double --)
npm run test:cov -w apps/api  # Coverage for specific package
npm run test:e2e -w apps/api  # E2E tests only
```

**Sources:** [AGENTS.md:366-388](), [apps/api/README.md:14-76]()

---

## CI/CD Pipeline

### Continuous Integration Workflow

#### CI Job Structure

```mermaid
flowchart TB
    Trigger["Push to main/develop<br/>or Pull Request"]
    
    subgraph "Parallel CI Jobs"
        LintJob["lint job"]
        TestJob["test job"]
        E2EJob["e2e job"]
        BuildJob["build job"]
    end
    
    subgraph "lint job steps"
        L1["actions/checkout@v6"]
        L2[".github/actions/setup-tools"]
        L3["Check incorrect domains<br/>(git grep tambo.ai/tambo.com)"]
        L4["npm run prettier-check"]
        L5["npm run lint"]
        L6["npm run check-types"]
        L7["Validate docs.tambo.co links"]
    end
    
    subgraph "test job steps"
        T1["actions/checkout@v6"]
        T2[".github/actions/setup-tools"]
        T3["npm run test -- -- --coverage"]
        T4["Upload to Codecov"]
    end
    
    subgraph "e2e job steps"
        E1["actions/checkout@v6"]
        E2[".github/actions/setup-tools"]
        E3["npm run test:e2e -w @tambo-ai-cloud/api"]
    end
    
    subgraph "build job steps"
        B1["actions/checkout@v6"]
        B2[".github/actions/setup-tools"]
        B3["npm run build<br/>(with dummy env vars)"]
    end
    
    StatusJob["status job<br/>(workflow-check.yml)"]
    
    Trigger --> LintJob
    Trigger --> TestJob
    Trigger --> E2EJob
    Trigger --> BuildJob
    
    LintJob --> L1 --> L2 --> L3 --> L4 --> L5 --> L6 --> L7
    TestJob --> T1 --> T2 --> T3 --> T4
    E2EJob --> E1 --> E2 --> E3
    BuildJob --> B1 --> B2 --> B3
    
    LintJob --> StatusJob
    TestJob --> StatusJob
    E2EJob --> StatusJob
    BuildJob --> StatusJob
```

**CI Job Details:**

| Job | Purpose | Key Steps | Exit Conditions |
|-----|---------|-----------|-----------------|
| `lint` | Code quality & type safety | Domain check, Prettier, ESLint, TypeScript, link validation | Blocks if linting/type errors found |
| `test` | Unit & integration tests | Jest tests with coverage, Codecov upload | Blocks if tests fail |
| `e2e` | End-to-end API tests | Supertest-based API tests in apps/api/test | Blocks if E2E tests fail |
| `build` | Build verification | Full Turbo build with production settings | Blocks if build fails |
| `status` | Aggregate check | Validates all jobs passed using workflow-check.yml | Reports overall status |

**Concurrency Control:**
```yaml
concurrency:
  group: ${{ github.workflow }}-${{ github.ref_name }}
  cancel-in-progress: true
```
This cancels in-progress CI runs when new commits are pushed to the same branch.

**Turbo Remote Caching:**
- Uses `TURBO_TEAM` and `TURBO_TOKEN` environment variables
- Shares build artifacts across CI runs and developers
- Significantly speeds up repeated builds

**Build Dummy Environment Variables:**
```yaml
DATABASE_URL: "postgresql://dummy-user:dummy-password@dummy-host:5432/dummy-database"
API_KEY_SECRET: "dummy-api-key-secret"
PROVIDER_KEY_SECRET: "dummy-provider-key-secret"
NEXTAUTH_SECRET: "dummy-nextauth-secret"
NEXTAUTH_URL: "http://localhost:8260"
SKIP_ENV_VALIDATION: "true"
```
These allow the build to complete without real credentials.

**Sources:** [.github/workflows/ci.yml:1-172]()

---

### Conventional Commits Validation

All PR titles must follow the Conventional Commits format:

```
<type>(scope): <description>
```

**Workflow:** `conventional-commits.yml`

**Allowed Types:**

| Type | Description | Release Impact |
|------|-------------|----------------|
| `feat` | New feature | Minor version bump |
| `fix` | Bug fix | Patch version bump |
| `perf` | Performance improvement | Patch version bump |
| `deps` | Dependency update | Patch version bump |
| `docs` | Documentation only | No release |
| `style` | Code style changes | No release |
| `chore` | Maintenance tasks | No release |
| `refactor` | Code refactoring | No release |
| `test` | Test changes | No release |
| `build` | Build system changes | No release |
| `ci` | CI configuration changes | No release |
| `revert` | Revert previous commit | Depends on original |

**Breaking Changes:** Add `!` after scope: `feat(api)!: change authentication`

**Common Scopes:** `api`, `web`, `core`, `db`, `react-sdk`, `cli`, `showcase`, `docs`

**Example PR Titles:**
```
feat(api): add transcript export
fix(web): prevent duplicate project creation
chore(db): reorganize migration files
docs(react-sdk): update component registration guide
```

**Sources:** [.github/workflows/conventional-commits.yml:1-24](), [AGENTS.md:406-428](), [CONTRIBUTING.md:199-209]()

---

## Database Migrations

### Migration Development Workflow

```mermaid
flowchart TB
    SchemaChange["Edit packages/db/src/schema.ts"]
    
    subgraph "Local Development"
        Generate["npm run db:generate -w packages/db<br/>(drizzle-kit generate)"]
        Review["Review generated SQL<br/>in packages/db/migrations/"]
        Migrate["npm run db:migrate -w packages/db<br/>(drizzle-kit migrate)"]
        Studio["npm run db:studio -w packages/db<br/>(drizzle-kit studio)"]
    end
    
    subgraph "Version Control"
        Commit["Commit schema.ts + migration SQL"]
        PR["Create Pull Request"]
    end
    
    SchemaChange --> Generate
    Generate --> Review
    Review --> Migrate
    Migrate --> Studio
    Studio --> Commit
    Commit --> PR
```

**Database Commands:**

| Command | Purpose | Underlying Tool | Working Directory |
|---------|---------|-----------------|-------------------|
| `npm run db:generate -w packages/db` | Generate migration from schema changes | `drizzle-kit generate` | packages/db |
| `npm run db:migrate -w packages/db` | Apply migrations to database | `drizzle-kit migrate` | packages/db |
| `npm run db:check -w packages/db` | Check migration status | `drizzle-kit check` | packages/db |
| `npm run db:studio -w packages/db` | Open Drizzle Studio (visual DB editor) | `drizzle-kit studio` | packages/db |
| `npm run db:push -w packages/db` | Push schema directly to DB (dev only) | `drizzle-kit push` | packages/db |

**Schema File Locations:**
- Main schema: `packages/db/src/schema.ts`
- Generated migrations: `packages/db/migrations/*.sql`
- Drizzle config: `packages/db/drizzle.config.ts`

**Important Rules:**
- Never hand-edit migration SQL files in `packages/db/migrations/`
- Always use `npm run db:generate` to create migrations from schema changes
- Commit both `schema.ts` and generated migration files together
- Test migrations locally before pushing
- Migration files are timestamped (e.g., `0000_migration_name.sql`)

**Sources:** [AGENTS.md:280-294](), [CONTRIBUTING.md:120-124]()

---

### Automated Migration Deployment

#### Migration Detection and Execution

```mermaid
sequenceDiagram
    participant PR as "Pull Request"
    participant CI as "CI Workflow"
    participant Main as "main branch"
    participant MigrateDB as "migrate-db.yml"
    participant GitHubAPI as "GitHub API"
    participant DB as "Production Database"
    
    PR->>CI: Push changes
    CI->>CI: Run lint, test, e2e, build
    CI->>Main: Merge (if all jobs pass)
    
    Main->>MigrateDB: Trigger on workflow_run success
    
    MigrateDB->>GitHubAPI: Fetch previous workflow runs
    GitHubAPI-->>MigrateDB: Previous run HEAD_SHA
    
    MigrateDB->>MigrateDB: git diff BASE_SHA..HEAD_SHA -- packages/db
    
    alt packages/db has changes
        MigrateDB->>MigrateDB: actions/checkout@v6
        MigrateDB->>MigrateDB: .github/actions/setup-tools
        MigrateDB->>DB: npm run db:migrate -w packages/db
        MigrateDB->>MigrateDB: ✓ Migration complete
    else No changes in packages/db
        MigrateDB->>MigrateDB: Skip migration (changed=false)
    end
```

**Migration Workflow Configuration:**

| Setting | Value | Purpose |
|---------|-------|---------|
| Trigger | `workflow_run` on CI completion | Runs after CI passes on main |
| Watch path | `packages/db` | Only migrations when DB changes |
| Detection method | `git diff` between workflow runs | Precise change tracking |
| Database secret | `secrets.DATABASE_URL` | Production database connection |

**Change Detection Algorithm:**

The workflow uses a sophisticated diff-based detection system:

1. **Fetch Previous Run:**
   ```bash
   # API call to get previous workflow run
   curl -H "Authorization: Bearer ${GITHUB_TOKEN}" \
     "https://api.github.com/repos/${GITHUB_REPOSITORY}/actions/workflows/${WORKFLOW_ID}/runs?branch=main&per_page=20"
   
   # Extract previous HEAD_SHA using jq
   BASE_SHA=$(jq -r '.workflow_runs | sort_by(.run_started_at) | ...')
   ```

2. **Compare Commits:**
   ```bash
   git diff --quiet "$BASE_SHA" "$HEAD_SHA" -- packages/db
   # Exit 0: no changes, Exit 1: changes detected
   ```

3. **Execute Migration:**
   ```bash
   npm run db:migrate -w packages/db
   # Applies all pending migrations to DATABASE_URL
   ```

**Failsafe Behaviors:**

| Scenario | Behavior | Reasoning |
|----------|----------|-----------|
| First workflow run | Check if packages/db exists at HEAD | Initial migration on new setup |
| GitHub API failure | Default to `changed=true` | Err on side of running migration |
| Git diff failure | Default to `changed=true` | Prevent missing migrations |
| Dependabot actor | Skip entirely | Dependency updates don't need migrations |
| Upstream CI failed | Skip entirely | Don't migrate on broken code |

**Sources:** [.github/workflows/migrate-db.yml:1-142]()

---

## Release Process

### Release Please Workflow

```mermaid
flowchart TB
    subgraph "Continuous Release Process"
        Commits["Conventional Commits<br/>merged to main"]
        
        RP["release-please.yml<br/>Analyzes commits"]
        
        ReleasePR["Release PR Created/Updated<br/>- Updates CHANGELOG.md<br/>- Bumps package.json versions<br/>- Groups related changes"]
        
        Review["Manual Review<br/>& Approval"]
        
        Merge["Merge Release PR"]
    end
    
    subgraph "Automated Publishing"
        NPM["NPM Packages<br/>@tambo-ai/react<br/>tambo (CLI)<br/>create-tambo-app"]
        
        Deploy["Deployments<br/>apps/web → deploy-web<br/>apps/api → deploy-api<br/>docs → deploy-docs<br/>showcase → deploy-showcase"]
        
        Sentry["Sentry Release<br/>Create & finalize"]
    end
    
    Commits --> RP
    RP --> ReleasePR
    ReleasePR --> Review
    Review --> Merge
    
    Merge --> NPM
    Merge --> Deploy
    Merge --> Sentry
```

**Release Please Configuration:**

- **Manifest File:** `.release-please-manifest.json`
- **Config File:** `release-please-config.json`
- **Token:** `RELEASE_PLEASE_TOKEN` (for writing PRs)

**Release Targets:**

| Package/App | Release Type | Destination |
|-------------|--------------|-------------|
| `react-sdk` | NPM publish | https://www.npmjs.com/package/@tambo-ai/react |
| `cli` | NPM publish | https://www.npmjs.com/package/tambo |
| `create-tambo-app` | NPM publish | https://www.npmjs.com/package/create-tambo-app |
| `apps/web` | Deployment | Merge `main` → `deploy-web` (Vercel watches) |
| `apps/api` | Deployment | Merge `main` → `deploy-api` (Railway watches) |
| `docs` | Deployment | Merge `main` → `deploy-docs` |
| `showcase` | Deployment | Merge `main` → `deploy-showcase` |

**Sources:** [.github/workflows/release-please.yml:1-234](), [RELEASING.md:1-95]()

---

### NPM Package Publishing

#### Package Publishing Jobs

```mermaid
flowchart TB
    subgraph "Release Please Job"
        RP["release-please job<br/>(googleapis/release-please-action@v4)"]
        Outputs["Job Outputs:<br/>react-sdk--release_created<br/>cli--release_created<br/>create-tambo-app--release_created<br/>packages/react-ui-base--release_created"]
    end
    
    subgraph "NPM Publishing Jobs (Parallel)"
        ReactJob["publish-react-sdk job"]
        CliJob["publish-cli job"]
        CreateJob["publish-create-tambo-app job"]
        UIBaseJob["publish-react-ui-base job"]
    end
    
    subgraph "Publishing Steps (per job)"
        S1["actions/checkout@v6<br/>(fetch-depth: 0)"]
        S2[".github/actions/setup-tools"]
        S3["actions/setup-node@v6<br/>(registry-url: npmjs.org)"]
        S4["npx turbo build --filter={package}"]
        S5["npm publish --access public"]
    end
    
    RP --> Outputs
    
    Outputs -->|"if: react-sdk--release_created == 'true'"| ReactJob
    Outputs -->|"if: cli--release_created == 'true'"| CliJob
    Outputs -->|"if: create-tambo-app--release_created == 'true'"| CreateJob
    Outputs -->|"if: packages/react-ui-base--release_created == 'true'"| UIBaseJob
    
    ReactJob --> S1
    S1 --> S2 --> S3 --> S4 --> S5
```

**Publishing Job Configuration:**

| Package | Job Name | Turbo Filter | Working Directory | NPM Package Name | Tag |
|---------|----------|--------------|-------------------|------------------|-----|
| React SDK | `publish-react-sdk` | `@tambo-ai/react` | `./react-sdk` | `@tambo-ai/react` | `latest` |
| CLI | `publish-cli` | `tambo` | `./cli` | `tambo` | `latest` |
| Create Tambo App | `publish-create-tambo-app` | `create-tambo-app` | `./create-tambo-app` | `create-tambo-app` | `latest` |
| React UI Base | `publish-react-ui-base` | `@tambo-ai/react-ui-base` | `./packages/react-ui-base` | `@tambo-ai/react-ui-base` | `next` |

**OIDC Authentication:**

The workflow uses OpenID Connect for secure npm publishing without long-lived tokens:

```yaml
permissions:
  contents: read
  id-token: write  # Required for OIDC publishing to NPM
```

**Build and Publish Commands:**

```bash
# React SDK
npx turbo build --filter=@tambo-ai/react
cd react-sdk && npm publish --access public

# CLI
npx turbo build --filter=tambo
cd cli && npm publish --access public

# Create Tambo App
npx turbo build --filter=create-tambo-app
cd create-tambo-app && npm publish --access public

# React UI Base (with 'next' tag)
npx turbo build --filter=@tambo-ai/react-ui-base
cd packages/react-ui-base && npm publish --access public --tag next
```

**Package Registry:**
All packages publish to https://registry.npmjs.org with public access.

**Sources:** [.github/workflows/release-please.yml:42-153]()

---

### Application Deployment

```mermaid
sequenceDiagram
    participant RP as Release Please
    participant Workflow as release-please.yml
    participant DeployBranch as deploy-* branches
    participant Platform as Vercel/Railway
    
    RP->>Workflow: apps/web release created
    Workflow->>Workflow: Checkout & setup Git
    Workflow->>DeployBranch: Merge main → deploy-web
    DeployBranch->>Platform: Automatic deployment trigger
    
    RP->>Workflow: apps/api release created
    Workflow->>Workflow: Checkout & setup Git
    Workflow->>DeployBranch: Merge main → deploy-api
    DeployBranch->>Platform: Automatic deployment trigger
```

**Deployment Strategy:**

Applications are deployed by merging `main` into deployment-specific branches:

| Application | Deploy Branch | Platform | Monitoring |
|-------------|---------------|----------|------------|
| apps/web | `deploy-web` | Vercel | https://vercel.com/tambo-ai/tambo-landing/deployments |
| apps/api | `deploy-api` | Railway (Production) | https://railway.com/project/f6706075-78e8-4b8f-93ff-a07ef6da36d9 |
| docs | `deploy-docs` | Vercel | N/A |
| showcase | `deploy-showcase` | Vercel | N/A |

**Process:**
1. Release Please detects changes in app directory
2. Creates release PR with version bump
3. When merged, triggers deployment job
4. Deployment job merges `main` into `deploy-*` branch
5. Platform (Vercel/Railway) watches `deploy-*` branch and deploys automatically

**Sentry Integration:**
- Release workflow creates Sentry release after deployment
- Links commits to release for error tracking
- Uses `sentry-cli` to propose version, set commits, and finalize

**Sources:** [.github/workflows/release-please.yml:123-234](), [RELEASING.md:28-44]()

---

### Template Maintenance Automation

```mermaid
flowchart TB
    RP["Release Please Workflow<br/>Completes Successfully"]
    
    Detect["template-maintenance.yml<br/>Detect Releases"]
    
    HasRelease{"New Release?"}
    
    subgraph "For Each Template Repo"
        Clone["Clone template repo<br/>(tambo-ai/tambo-template)"]
        Branch["Create upgrade branch<br/>(tambo-upgrade-{tag})"]
        PreCapture["Capture pre-upgrade state<br/>(package.json, versions)"]
        Upgrade["npx -y tambo@latest upgrade<br/>--yes --silent"]
        PostCapture["Capture post-upgrade state<br/>Generate diff"]
        CreatePR["Create Pull Request<br/>with upgrade summary"]
    end
    
    RP --> Detect
    Detect --> HasRelease
    
    HasRelease -->|Yes| Clone
    HasRelease -->|No| Skip["Skip"]
    
    Clone --> Branch
    Branch --> PreCapture
    PreCapture --> Upgrade
    Upgrade --> PostCapture
    PostCapture --> CreatePR
```

**Template Upgrade Workflow:**

When new versions of `@tambo-ai/react`, `tambo`, or other packages are released, the template repositories are automatically upgraded.

**Process:**
1. Triggered after successful Release Please workflow
2. Detects which packages were released
3. Clones template repository (currently `tambo-ai/tambo-template`)
4. Creates upgrade branch named `tambo-upgrade-{release-tag}`
5. Runs `npx -y tambo@latest upgrade --yes --silent`
6. Captures before/after state and generates diff
7. Creates PR in template repo with upgrade details

**Template Repos:**
- `tambo-ai/tambo-template` - Standard template
- Additional templates can be added to the matrix

**Authentication:**
- Uses `TAMBO_UPGRADE_PAT` secret for cross-repo access
- Falls back to `GITHUB_TOKEN` if PAT not available

**Sources:** [.github/workflows/template-maintenance.yml:1-142]()

---

## Development Best Practices

### Pre-Commit Checklist

Before creating a PR, ensure:

- [ ] Conventional Commit title format: `<type>(scope): description`
- [ ] All quality checks pass: `npm run lint && npm run check-types && npm test`
- [ ] Code formatted: `npm run format`
- [ ] Tests added/updated for new functionality
- [ ] Documentation updated if user-facing changes
- [ ] Database migrations generated if schema changed
- [ ] No secrets committed (use environment variables)

**Sources:** [CONTRIBUTING.md:212-218](), [AGENTS.md:389-398]()

---

### Cross-Package Development

When working across multiple packages:

| Scenario | Actions Required |
|----------|------------------|
| **react-sdk changes** | 1. Run tests<br/>2. Rebuild package<br/>3. Test in showcase app<br/>4. Verify docs examples |
| **cli changes** | 1. Test component generation<br/>2. Verify registry updates<br/>3. Components auto-sync to showcase |
| **showcase changes** | Edit CLI registry files (auto-syncs to showcase)<br/>**Never edit showcase components directly** |
| **docs changes** | Ensure examples match current API<br/>Duplicate CLI component changes to docs package |

**Workspace Commands:**
```bash
npm run dev -w cli           # Work on CLI package
npm run build -w react-sdk   # Build React SDK
npm test -w apps/api         # Test API package
```

**Sources:** [AGENTS.md:351-359]()

---

### Tool Version Management

**Changing Tool Versions:**

1. Update the authoritative version file:
   - Node.js: Update both `.node-version` AND `.nvmrc`
   - Other tools: Update `mise.toml`

2. Run `mise install` to apply changes locally

3. Verify all checks pass:
   ```bash
   npm run lint && npm run check-types && npm test
   ```

4. Open PR with version file changes

**Local Overrides:**

Create `.mise.local.toml` (gitignored) for local-only changes. Only use for additive or patch-level changes—never override Node.js major version or use incompatible versions.

**Sources:** [AGENTS.md:69-77]()

---

## Related Documentation

| Document | Purpose |
|----------|---------|
| [CONTRIBUTING.md](https://github.com/tambo-ai/tambo/blob/main/CONTRIBUTING.md) | Contributor setup and PR workflow |
| [AGENTS.md](https://github.com/tambo-ai/tambo/blob/main/AGENTS.md) | Coding standards and architecture |
| [RELEASING.md](https://github.com/tambo-ai/tambo/blob/main/RELEASING.md) | Detailed release workflow |
| [OPERATORS.md](https://github.com/tambo-ai/tambo/blob/main/OPERATORS.md) | Self-hosting and deployment |

**Sources:** [CONTRIBUTING.md:220-227](), [CLAUDE.md:1-33]()

---

