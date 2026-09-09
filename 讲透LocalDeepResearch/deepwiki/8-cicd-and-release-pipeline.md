> 来源: [https://deepwiki.com/LearningCircuit/local-deep-research/8-cicd-and-release-pipeline](https://deepwiki.com/LearningCircuit/local-deep-research/8-cicd-and-release-pipeline)
> DeepWiki LearningCircuit/local-deep-research | Last indexed: 6 May 2026 (4a6a90

# CI/CD and Release Pipeline

  Relevant source files 
 - [.github/release.yml](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/.github/release.yml)
 - [.github/workflows/README.md](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/.github/workflows/README.md?plain=1)
 - [.github/workflows/advanced-search-reminder.yml](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/.github/workflows/advanced-search-reminder.yml)
 - [.github/workflows/ai-code-reviewer.yml](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/.github/workflows/ai-code-reviewer.yml)
 - [.github/workflows/backwards-compatibility.yml](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/.github/workflows/backwards-compatibility.yml)
 - [.github/workflows/bearer.yml](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/.github/workflows/bearer.yml)
 - [.github/workflows/check-env-vars.yml](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/.github/workflows/check-env-vars.yml)
 - [.github/workflows/checkov.yml](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/.github/workflows/checkov.yml)
 - [.github/workflows/claude-code-review.yml](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/.github/workflows/claude-code-review.yml)
 - [.github/workflows/codeql.yml](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/.github/workflows/codeql.yml)
 - [.github/workflows/container-security.yml](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/.github/workflows/container-security.yml)
 - [.github/workflows/danger-zone-alert.yml](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/.github/workflows/danger-zone-alert.yml)
 - [.github/workflows/devskim.yml](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/.github/workflows/devskim.yml)
 - [.github/workflows/docker-multiarch-test.yml](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/.github/workflows/docker-multiarch-test.yml)
 - [.github/workflows/docker-publish.yml](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/.github/workflows/docker-publish.yml)
 - [.github/workflows/docker-tests.yml](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/.github/workflows/docker-tests.yml)
 - [.github/workflows/dockle.yml](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/.github/workflows/dockle.yml)
 - [.github/workflows/e2e-research-test.yml](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/.github/workflows/e2e-research-test.yml)
 - [.github/workflows/file-whitelist-check.yml](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/.github/workflows/file-whitelist-check.yml)
 - [.github/workflows/fuzz.yml](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/.github/workflows/fuzz.yml)
 - [.github/workflows/gitleaks.yml](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/.github/workflows/gitleaks.yml)
 - [.github/workflows/grype.yml](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/.github/workflows/grype.yml)
 - [.github/workflows/hadolint.yml](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/.github/workflows/hadolint.yml)
 - [.github/workflows/label-fixed-in-dev.yml](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/.github/workflows/label-fixed-in-dev.yml)
 - [.github/workflows/mypy-type-check.yml](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/.github/workflows/mypy-type-check.yml)
 - [.github/workflows/npm-audit.yml](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/.github/workflows/npm-audit.yml)
 - [.github/workflows/nuclei.yml](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/.github/workflows/nuclei.yml)
 - [.github/workflows/ossf-scorecard.yml](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/.github/workflows/ossf-scorecard.yml)
 - [.github/workflows/owasp-zap-scan.yml](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/.github/workflows/owasp-zap-scan.yml)
 - [.github/workflows/playwright-webkit-tests.yml](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/.github/workflows/playwright-webkit-tests.yml)
 - [.github/workflows/pre-commit.yml](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/.github/workflows/pre-commit.yml)
 - [.github/workflows/publish.yml](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/.github/workflows/publish.yml)
 - [.github/workflows/puppeteer-e2e-tests.yml](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/.github/workflows/puppeteer-e2e-tests.yml)
 - [.github/workflows/release-gate.yml](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/.github/workflows/release-gate.yml)
 - [.github/workflows/release.yml](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/.github/workflows/release.yml)
 - [.github/workflows/responsive-ui-tests-enhanced.yml](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/.github/workflows/responsive-ui-tests-enhanced.yml)
 - [.github/workflows/retirejs.yml](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/.github/workflows/retirejs.yml)
 - [.github/workflows/sbom.yml](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/.github/workflows/sbom.yml)
 - [.github/workflows/security-file-write-check.yml](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/.github/workflows/security-file-write-check.yml)
 - [.github/workflows/security-headers-validation.yml](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/.github/workflows/security-headers-validation.yml)
 - [.github/workflows/security-tests.yml](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/.github/workflows/security-tests.yml)
 - [.github/workflows/semgrep.yml](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/.github/workflows/semgrep.yml)
 - [.github/workflows/sync-main-to-dev.yml](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/.github/workflows/sync-main-to-dev.yml)
 - [.github/workflows/update-dependencies.yml](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/.github/workflows/update-dependencies.yml)
 - [.github/workflows/update-npm-dependencies.yml](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/.github/workflows/update-npm-dependencies.yml)
 - [.github/workflows/update-precommit-hooks.yml](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/.github/workflows/update-precommit-hooks.yml)
 - [.github/workflows/validate-image-pinning.yml](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/.github/workflows/validate-image-pinning.yml)
 - [.github/workflows/version_check.yml](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/.github/workflows/version_check.yml)
 - [.github/workflows/zizmor-security.yml](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/.github/workflows/zizmor-security.yml)
 
  This page covers the GitHub Actions workflow ecosystem for Local Deep Research: how code flows from a pull request through quality gates to a published release. It describes the orchestration workflow, gate structure, version management, Docker publishing, PyPI publishing, and automated maintenance schedules.

 For details on individual security scanning tools (Bandit, CodeQL, OWASP ZAP, etc.) referenced here, see [Security Scanning Infrastructure](https://deepwiki.com/LearningCircuit/local-deep-research/8.2-security-scanning-infrastructure). For information on the test suite itself, see [Continuous Integration Workflows](https://deepwiki.com/LearningCircuit/local-deep-research/8.1-continuous-integration-workflows).

 
---

 
## Workflow Architecture

 All workflows live in `.github/workflows/`. The ecosystem follows a hub-and-spoke model: `release.yml` is the orchestrator, and it calls specialized reusable workflows (`workflow_call`) via aggregator gates.

 **Diagram: Release Pipeline Overview**

 
```

```

 Sources: [.github/workflows/release.yml1-180](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/.github/workflows/release.yml#L1-L180) [.github/workflows/release.yml197-451](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/.github/workflows/release.yml#L197-L451)

 
---

 
## Version Management

 The version source of truth is `src/local_deep_research/__version__.py`. The `package.json` version is kept in sync automatically.

 
### Auto-Bump Workflow

 `version_check.yml` triggers on every push to `main` that modifies source files, and opens a PR against `main` with the bumped version. It uses the `pdm-bump` plugin.

 
| Input | Bump type |
|---|---|
| Automatic (push to main) | patch |
| workflow_dispatch with minor | minor |
| workflow_dispatch with major | major |

 The job skips itself when the triggering commit already contains `chore: auto-bump version` to prevent infinite loops [.github/workflows/version_check.yml:42].

 After bumping, `package.json` is updated with `jq` to keep the NPM version field in sync [.github/workflows/version_check.yml:119-121].

 
### Release Trigger Logic

 The `version-check` job in `release.yml` reads `__version__.py`, extracts the version, and checks whether a GitHub release for that tag already exists using `gh release view`. If it does, `should_release=false` is set and no further jobs run. Tag pushes and `workflow_dispatch` bypass this check and always proceed [.github/workflows/release.yml:57-79].

 
```

```

 Sources: [.github/workflows/version_check.yml1-180](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/.github/workflows/version_check.yml#L1-L180) [.github/workflows/release.yml28-79](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/.github/workflows/release.yml#L28-L79)

 
---

 
## Gate Structure

 The `build` job's `if` condition explicitly lists which gates are blocking. Failure in any required gate prevents the release from proceeding.

 
```

```

 [.github/workflows/release.yml:197-202]

 
| Gate job | Workflow called | Blocking? |
|---|---|---|
| release-gate | release-gate.yml | Yes |
| ci-gate | ci-gate.yml | Yes |
| e2e-test-gate | puppeteer-e2e-tests.yml | Yes |
| compat-test-gate | backwards-compatibility.yml | Yes |
| test-gate | playwright-webkit-tests.yml | No (advisory) |
| responsive-test-gate | responsive-ui-tests-enhanced.yml | No (advisory) |
| vulture-gate | vulture-dead-code.yml | No (advisory) |

 Advisory gates run in parallel but their failure does not prevent the release. This is intentional for tests that detect cosmetic rendering differences (like `responsive-ui-tests-enhanced.yml`) where fixes are not urgent [.github/workflows/release.yml:120-133].

 Sources: [.github/workflows/release.yml93-197](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/.github/workflows/release.yml#L93-L197) [.github/workflows/responsive-ui-tests-enhanced.yml1-11](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/.github/workflows/responsive-ui-tests-enhanced.yml#L1-L11)

 
---

 
## Security Gate (`release-gate.yml`)

 `release-gate.yml` is a reusable workflow aggregator. It calls 17+ individual security scan workflows and then checks the GitHub Code Scanning API for open alerts.

 **Diagram: Security Gate Job Graph**

 
```

```

 The `owasp-zap-scan.yml` workflow executes both baseline and API scans against a live instance of the `local_deep_research.web.app` server [.github/workflows/owasp-zap-scan.yml:56-85]. Similarly, `zizmor-security.yml` audits the security posture of the GitHub Actions themselves [.github/workflows/zizmor-security.yml:35-41].

 For details on security infrastructure, see [Security Scanning Infrastructure](https://deepwiki.com/LearningCircuit/local-deep-research/8.2-security-scanning-infrastructure).

 Sources: [.github/workflows/owasp-zap-scan.yml1-203](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/.github/workflows/owasp-zap-scan.yml#L1-L203) [.github/workflows/zizmor-security.yml1-66](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/.github/workflows/zizmor-security.yml#L1-L66)

 
---

 
## Build Job: SBOM and Supply Chain Artifacts

 If all required gates pass, the `build` job in `release.yml` runs to generate supply chain security artifacts:

 
 - **SBOM generation** — Trivy generates SBOM files (SPDX/CycloneDX).
 - **Sigstore signing** — Cosign signs artifacts using keyless signing (GitHub OIDC).
 - **SLSA hash generation** — SHA256 hashes of all artifacts are passed to the `provenance` job.
 
 The `provenance` job calls `slsa-framework/slsa-github-generator` at SLSA level 3 to produce `provenance.intoto.jsonl` [.github/workflows/release.yml:384-393]. The `create-release` job assembles all artifacts and calls `gh release create` with auto-generated release notes [.github/workflows/release.yml:395-406].

 Sources: [.github/workflows/release.yml265-393](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/.github/workflows/release.yml#L265-L393)

 
---

 
## Publishing Trigger Model

 Publishing to Docker Hub and PyPI is **not** triggered by creating a GitHub release through the UI. It is triggered exclusively by `repository_dispatch` events sent from `trigger-workflows` in `release.yml`. This design prevents bypassing the security gate [.github/workflows/release.yml:89-91].

 
```

```

 [.github/workflows/release.yml:408-440]

 
---

 
## Docker Publishing (`docker-publish.yml`)

 The Docker pipeline builds multi-arch images (AMD64 and ARM64) and performs a final security scan before manifest creation.

 **Diagram: Docker Publish Job Sequence**

 
```

```

 The `security-scan` job uses Trivy to check for fixable HIGH/CRITICAL vulnerabilities and uploads a SARIF report to the GitHub Security tab [.github/workflows/docker-publish.yml:147-175].

 For details, see [Docker Image Publishing](https://deepwiki.com/LearningCircuit/local-deep-research/8.4-docker-image-publishing).

 Sources: [.github/workflows/docker-publish.yml1-393](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/.github/workflows/docker-publish.yml#L1-L393)

 
---

 
## PyPI Publishing (`publish.yml`)

 The PyPI publishing workflow uses an isolated three-job structure to ensure frontend assets are correctly bundled.

 **Diagram: PyPI Publish Job Chain**

 
```

```

 The `build-frontend` job executes the Vite build and verifies the `manifest.json` location at `src/local_deep_research/web/static/dist/.vite/manifest.json` [.github/workflows/publish.yml:73-95]. The `build-package` job downloads these assets before running `pdm build` to ensure the wheel contains the UI [.github/workflows/publish.yml:141-148].

 For details, see [PyPI Package Publishing](https://deepwiki.com/LearningCircuit/local-deep-research/8.5-pypi-package-publishing).

 Sources: [.github/workflows/publish.yml1-466](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/.github/workflows/publish.yml#L1-L466)

 
---

 
## Automated Maintenance

 Workflows run on schedules to keep dependencies and security metadata current.

 
| Workflow | File | Schedule | Purpose |
|---|---|---|---|
| Update PDM dependencies | update-dependencies.yml | Wednesday 08:00 UTC | Bump Python deps in pdm.lock |
| Update NPM dependencies | update-npm-dependencies.yml | Thursday 08:00 UTC | Bump JS deps in package-lock.json |
| Update pre-commit hooks | update-precommit-hooks.yml | Friday 08:00 UTC | Bump hook versions |
| Zizmor Security Scan | zizmor-security.yml | Monday 09:00 UTC | Weekly GitHub Actions security audit [.github/workflows/zizmor-security.yml:8] |
| File Whitelist Check | file-whitelist-check.yml | On PR | Ensures no unauthorized file types enter the repo [.github/workflows/file-whitelist-check.yml:46-47] |

 For details, see [Automated Dependency Maintenance](https://deepwiki.com/LearningCircuit/local-deep-research/8.6-automated-dependency-maintenance).

 
---

 
## Security Design Principles

 The pipeline is designed so that the release process is immutable and verified:

 
 - **No Manual Publishing**: Publishing jobs are triggered **only** via `repository_dispatch`. They have no `workflow_dispatch` trigger [.github/workflows/docker-publish.yml:3-9], [.github/workflows/publish.yml:3-9].
 - **Commit Pinning**: All GitHub Actions are pinned to exact commit SHAs (e.g., `actions/checkout@de0fac2e4500dabe0009e67214ff5f5447ce83dd`) to prevent supply chain attacks.
 - **Runner Hardening**: All jobs use `step-security/harden-runner` with `egress-policy: audit` to log and control outbound network calls [.github/workflows/release.yml:36].
 - **Least Privilege**: Minimal top-level `permissions: {}` is declared on each workflow, with jobs defining only the specific permissions they need [.github/workflows/release.yml:11].
 - **Path Filtering**: Workflows like `docker-tests.yml` use `dorny/paths-filter` to optimize resource usage by only running jobs relevant to the changed files [.github/workflows/docker-tests.yml:57-91].
 
 Sources: [.github/workflows/release.yml1-20](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/.github/workflows/release.yml#L1-L20) [.github/workflows/docker-publish.yml1-11](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/.github/workflows/docker-publish.yml#L1-L11) [.github/workflows/publish.yml1-11](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/.github/workflows/publish.yml#L1-L11) [.github/workflows/docker-tests.yml39-92](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/.github/workflows/docker-tests.yml#L39-L92)
