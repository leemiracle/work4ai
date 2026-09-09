> 来源: [https://deepwiki.com/LearningCircuit/local-deep-research/7-development-guide](https://deepwiki.com/LearningCircuit/local-deep-research/7-development-guide)
> DeepWiki LearningCircuit/local-deep-research | Last indexed: 6 May 2026 (4a6a90

# Development Guide

  Relevant source files 
 - [.file-whitelist.txt](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/.file-whitelist.txt)
 - [.github/CODEOWNERS](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/.github/CODEOWNERS)
 - [.github/scripts/file-whitelist-check.sh](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/.github/scripts/file-whitelist-check.sh)
 - [.gitignore](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/.gitignore)
 - [.gitleaks.toml](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/.gitleaks.toml)
 - [.gitleaksignore](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/.gitleaksignore)
 - [.pre-commit-config.yaml](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/.pre-commit-config.yaml)
 - [.pre-commit-hooks/check-absolute-module-paths.py](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/.pre-commit-hooks/check-absolute-module-paths.py)
 - [.pre-commit-hooks/check-pathlib-usage.py](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/.pre-commit-hooks/check-pathlib-usage.py)
 - [.pre-commit-hooks/check-session-context-manager.py](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/.pre-commit-hooks/check-session-context-manager.py)
 - [.pre-commit-hooks/file-whitelist-check.sh](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/.pre-commit-hooks/file-whitelist-check.sh)
 - [.pre-commit-hooks/recommend-release-notes.py](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/.pre-commit-hooks/recommend-release-notes.py)
 - [CONTRIBUTING.md](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/CONTRIBUTING.md?plain=1)
 - [README.md](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/README.md?plain=1)
 - [changelog.d/3670.breaking.1.md](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/changelog.d/3670.breaking.1.md?plain=1)
 - [changelog.d/3670.breaking.md](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/changelog.d/3670.breaking.md?plain=1)
 - [changelog.d/3670.feature.md](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/changelog.d/3670.feature.md?plain=1)
 - [changelog.d/3773.feature.md](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/changelog.d/3773.feature.md?plain=1)
 - [changelog.d/README.md](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/changelog.d/README.md?plain=1)
 - [docker-compose.gpu.override.yml](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/docker-compose.gpu.override.yml)
 - [docs/CI_CD_INFRASTRUCTURE.md](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/docs/CI_CD_INFRASTRUCTURE.md?plain=1)
 - [docs/RELEASE_GUIDE.md](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/docs/RELEASE_GUIDE.md?plain=1)
 - [docs/SECURITY_REVIEW_PROCESS.md](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/docs/SECURITY_REVIEW_PROCESS.md?plain=1)
 - [docs/SQLCIPHER_INSTALL.md](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/docs/SQLCIPHER_INSTALL.md?plain=1)
 - [docs/decisions/0001-remove-detect-secrets.md](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/docs/decisions/0001-remove-detect-secrets.md?plain=1)
 - [docs/developing.md](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/docs/developing.md?plain=1)
 - [docs/docker-compose-guide.md](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/docs/docker-compose-guide.md?plain=1)
 - [docs/install-pip.md](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/docs/install-pip.md?plain=1)
 - [docs/installation.md](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/docs/installation.md?plain=1)
 - [examples/benchmarks/browsecomp/run_browsecomp_fixed_v2.py](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/examples/benchmarks/browsecomp/run_browsecomp_fixed_v2.py)
 - [examples/benchmarks/gemini/run_gemini_benchmark_fixed.py](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/examples/benchmarks/gemini/run_gemini_benchmark_fixed.py)
 - [examples/benchmarks/scripts/run_benchmark_with_claude_grading.py](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/examples/benchmarks/scripts/run_benchmark_with_claude_grading.py)
 - [examples/optimization/llm_multi_benchmark.py](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/examples/optimization/llm_multi_benchmark.py)
 - [pdm.lock](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/pdm.lock)
 - [pyproject.toml](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/pyproject.toml)
 - [src/local_deep_research/database/sqlcipher_compat.py](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/src/local_deep_research/database/sqlcipher_compat.py)
 - [src/local_deep_research/web/static/js/services/api.js](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/src/local_deep_research/web/static/js/services/api.js)
 - [tests/api_tests/fix_search_engines.py](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/tests/api_tests/fix_search_engines.py)
 - [tests/api_tests/migrate_research_mode.py](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/tests/api_tests/migrate_research_mode.py)
 - [tests/api_tests/populate_search_engines.py](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/tests/api_tests/populate_search_engines.py)
 - [tests/api_tests/run_basic_api_tests.py](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/tests/api_tests/run_basic_api_tests.py)
 - [tests/conftest.py](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/tests/conftest.py)
 - [tests/infrastructure_tests/test_csrf_api.test.js](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/tests/infrastructure_tests/test_csrf_api.test.js)
 - [tests/security/test_absolute_module_paths_hook.py](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/tests/security/test_absolute_module_paths_hook.py)
 - [tests/test_settings_manager.py](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/tests/test_settings_manager.py)
 - [tests/ui_tests/test_direct_uuid_insert.py](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/tests/ui_tests/test_direct_uuid_insert.py)
 - [tests/ui_tests/test_mixed_id_handling.py](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/tests/ui_tests/test_mixed_id_handling.py)
 - [tests/ui_tests/test_trace_error.py](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/tests/ui_tests/test_trace_error.py)
 - [tests/ui_tests/test_uuid_fresh_db.py](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/tests/ui_tests/test_uuid_fresh_db.py)
 - [tests/ui_tests/test_uuid_research.py](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/tests/ui_tests/test_uuid_research.py)
 
  This document provides comprehensive guidance for contributors to Local Deep Research. It covers development environment setup, code quality standards, testing infrastructure, and security review processes.

 **Scope**: This page focuses on the practical aspects of developing and contributing code. For architectural design patterns and system internals, see [Architecture](https://deepwiki.com/LearningCircuit/local-deep-research/3-architecture). For CI/CD pipeline details, see [CI/CD and Release Pipeline](https://deepwiki.com/LearningCircuit/local-deep-research/8-cicd-and-release-pipeline). For production deployment configuration, see [Deployment Strategies](https://deepwiki.com/LearningCircuit/local-deep-research/9-deployment-strategies).

 
---

 
## Development Environment Setup

 
### Prerequisites

 Local Deep Research requires the following tools for development:

 
| Tool | Version | Purpose |
|---|---|---|
| Python | 3.12+ | Backend runtime and service logic [pyproject.toml10] |
| Node.js | Latest | Frontend build tooling and UI tests [.pre-commit-config.yaml37-47] |
| PDM | Latest | Python dependency and virtualenv management [pyproject.toml1-3] |
| SQLCipher | System library | AES-256 database encryption [docs/SQLCIPHER_INSTALL.md1-15] |

 
### Initial Setup Workflow

 The following diagram maps the setup process to the underlying tools and scripts.

 **Development Onboarding Flow**

 
```

```

 **Sources**: [tests/conftest.py22-25](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/tests/conftest.py#L22-L25) [.pre-commit-config.yaml1-45](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/.pre-commit-config.yaml#L1-L45)

 
### Backend Setup with PDM

 PDM is the Python dependency manager used by this project. It provides deterministic builds via `pdm.lock` and manages virtual environments automatically [[pyproject.toml143-150](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/[pyproject.toml#L143-L150)].

 
```

```

 Always commit `pdm.lock` alongside `pyproject.toml` changes to ensure reproducible builds [[pyproject.toml52](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/[pyproject.toml#L52-L52)]. The repository uses a whitelist approach in `.gitignore` to ensure only critical project files are tracked [[.gitignore1-61](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/[.gitignore#L1-L61)].

 **Sources**: [pyproject.toml143-150](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/pyproject.toml#L143-L150) [.gitignore1-61](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/.gitignore#L1-L61) [pdm.lock1-10](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/pdm.lock#L1-L10)

 
### Frontend Setup

 The frontend uses Vite for development and build tooling. Assets are served via Flask but managed through `package.json`. CSRF protection is required for all API communication via `getCsrfToken` [[src/local_deep_research/web/static/js/services/api.js17-20](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/[src/local_deep_research/web/static/js/services/api.js#L17-L20)].

 
```

```

 **Sources**: [.pre-commit-config.yaml37-47](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/.pre-commit-config.yaml#L37-L47) [src/local_deep_research/web/static/js/services/api.js1-11](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/src/local_deep_research/web/static/js/services/api.js#L1-L11)

 
---

 
## Project Structure and File Organization

 
### Repository Layout

 The project follows a standard Python package structure with a frontend integrated into the web module.

 
```

```

 **Sources**: [.github/CODEOWNERS1-30](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/.github/CODEOWNERS#L1-L30) [.gitignore1-100](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/.gitignore#L1-L100) [pyproject.toml110-123](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/pyproject.toml#L110-L123)

 
### Critical Path Owners

 Specific modules require maintainer approval due to their impact on security or data integrity.

 
 - **Security/Auth**: `src/local_deep_research/web/auth/` [[.github/CODEOWNERS24](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/[.github/CODEOWNERS#L24-L24)]
 - **Database**: `src/local_deep_research/database/` [[.github/CODEOWNERS20](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/[.github/CODEOWNERS#L20-L20)]
 - **CI/CD & Pre-commit**: `.github/workflows/` and `.pre-commit-hooks/` [[.github/CODEOWNERS34-35](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/[.github/CODEOWNERS#L34-L35)]
 
 
---

 
## Code Quality and Static Analysis

 
### Pre-commit Hook Infrastructure

 The repository enforces quality via 26+ hooks configured in `.pre-commit-config.yaml`.

 
| Hook ID | Tool/Script | Purpose |
|---|---|---|
| gitleaks | Gitleaks | Secret scanning (API keys, tokens) [.pre-commit-config.yaml24-30] |
| ruff | Ruff | Python linting and auto-fixing [.pre-commit-config.yaml53-54] |
| check-env-vars | check-env-vars.py | Ensure env vars use SettingsManager [.pre-commit-config.yaml73-78] |
| check-ldr-db-usage | check-ldr-db.py | Prevent shared ldr.db usage [.pre-commit-config.yaml92-98] |
| check-pathlib-usage | check-pathlib-usage.py | Enforce pathlib.Path over os.path [.pre-commit-config.yaml141-147] |
| check-datetime-timezone | check_datetime_timezone.py | Enforce UtcDateTime in models/migrations [.pre-commit-config.yaml120-125] |
| file-whitelist-check | file-whitelist-check.sh | Restrict binary and large file commits [.pre-commit-hooks/file-whitelist-check.sh1-20] |

 **Sources**: [.pre-commit-config.yaml1-168](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/.pre-commit-config.yaml#L1-L168) [.pre-commit-hooks/file-whitelist-check.sh1-50](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/.pre-commit-hooks/file-whitelist-check.sh#L1-L50) [scripts/pre_commit/check_datetime_timezone.py1-10](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/scripts/pre_commit/check_datetime_timezone.py#L1-L10)

 
### Python Coding Standards

 Custom checks enforce specific architectural patterns:

 
 - **Logging**: Use `loguru` instead of standard `logging` [[.pre-commit-config.yaml66-72](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/[.pre-commit-config.yaml#L66-L72)].
 - **SQL**: Prevent raw SQL usage in favor of SQLAlchemy ORM [[.pre-commit-config.yaml66-72](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/[.pre-commit-config.yaml#L66-L72)].
 - **UTC Datetime**: All `DateTime` columns must use `UtcDateTime` from `sqlalchemy_utc` [[.pre-commit-config.yaml120-125](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/[.pre-commit-config.yaml#L120-L125)].
 - **Settings**: All environment variables must be accessed through `SettingsManager` [[.pre-commit-config.yaml73-78](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/[.pre-commit-config.yaml#L73-L78)].
 
 
---

 
## Testing Infrastructure

 
### Test Execution

 The project maintains a comprehensive test suite across Python and JavaScript.

 **Testing Entity Map**

 
```

```

 
 - **Backend**: Executed via `pytest` [[pyproject.toml180-190](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/[pyproject.toml#L180-L190)].
 - **Mocking**: Tests utilize a robust set of mock fixtures for external services like arXiv, PubMed, and LLM providers [[tests/conftest.py28-42](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/[tests/conftest.py#L28-L42)].
 - **Isolation**: Singletons like `SocketIOService` and `BackgroundJobScheduler` are reset between tests using the `reset_all_singletons` fixture [[tests/conftest.py57-130](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/[tests/conftest.py#L57-L130)].
 - **Timeout**: Database operations are limited to 5 seconds in tests to prevent hanging [[tests/conftest.py133-145](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/[tests/conftest.py#L133-L145)].
 
 **Sources**: [tests/conftest.py1-205](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/tests/conftest.py#L1-L205) [pyproject.toml180-190](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/pyproject.toml#L180-L190) [.pre-commit-config.yaml156-163](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/.pre-commit-config.yaml#L156-L163)

 
---

 
## Security Best Practices

 
### Secret Scanning

 `gitleaks` is the primary tool for secret detection [[.gitleaks.toml3-8](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/[.gitleaks.toml#L3-L8)]. It uses regex-based rules for GitHub PATs, Google API keys, and SQLCipher keys [[.gitleaks.toml15-55](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/[.gitleaks.toml#L15-L55)]. Known false positives are managed in `.gitleaksignore` [[.gitleaksignore1-16](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/[.gitleaksignore#L1-L16)].

 
### File Whitelist Policy

 A strict whitelist approach is used for the repository to prevent accidental commitment of research data, databases, or large binaries [[.gitignore1-10](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/[.gitignore#L1-L10)].

 
 - **Large Files**: Blocked if > 1MB [[.pre-commit-hooks/file-whitelist-check.sh47-50](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/[.pre-commit-hooks/file-whitelist-check.sh#L47-L50)].
 - **Binary Files**: Only explicitly allowed file types (e.g., favicons, error sounds) are permitted [[.gitignore284-286](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/[.gitignore#L284-L286)].
 - **Entropy Check**: Custom checks look for high-entropy strings (potential keys) in non-test files [[.github/scripts/file-whitelist-check.sh193-208](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/[.github/scripts/file-whitelist-check.sh#L193-L208)].
 
 
### Security Review Gates

 The release process enforces security gates before any artifact is published [[.github/CODEOWNERS10](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/[.github/CODEOWNERS#L10-L10)]. This includes strict reviews of database migrations [[.github/CODEOWNERS15-17](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/[.github/CODEOWNERS#L15-L17)] and authentication logic [[.github/CODEOWNERS23-25](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/[.github/CODEOWNERS#L23-L25)].

 **Sources**: [.pre-commit-config.yaml1-168](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/.pre-commit-config.yaml#L1-L168) [.gitleaks.toml1-160](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/.gitleaks.toml#L1-L160) [.github/scripts/file-whitelist-check.sh1-220](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/.github/scripts/file-whitelist-check.sh#L1-L220)

 
---

 
## Child Pages

 For detailed information on specific development topics, see the following child pages:

 
 - [Project Structure](https://deepwiki.com/LearningCircuit/local-deep-research/7.1-project-structure) — Repository organization, module layout, and the 26 custom pre-commit hooks.
 - [Testing Infrastructure](https://deepwiki.com/LearningCircuit/local-deep-research/7.2-testing-infrastructure) — Detailed pytest setup, Playwright/Puppeteer UI tests, and test data management.
 - [Code Quality and Static Analysis](https://deepwiki.com/LearningCircuit/local-deep-research/7.3-code-quality-and-static-analysis) — Linting rules (Ruff, ESLint), type checking (Mypy), and custom project-specific hooks.
 - [Security Best Practices](https://deepwiki.com/LearningCircuit/local-deep-research/7.4-security-best-practices) — Secret scanning with Gitleaks, file whitelisting, and the release security gate process.
