> 来源: [https://deepwiki.com/TransformerLensOrg/TransformerLens/10-development-and-contributing](https://deepwiki.com/TransformerLensOrg/TransformerLens/10-development-and-contributing)
> DeepWiki TransformerLensOrg/TransformerLens | Last indexed: 16 July 2026 (4ba218

# Development and Contributing

  Relevant source files 
 - [.github/workflows/checks.yml](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/.github/workflows/checks.yml)
 - [.github/workflows/release.yml](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/.github/workflows/release.yml)
 - [AGENTS.md](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/AGENTS.md?plain=1)
 - [README.md](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/README.md?plain=1)
 - [demos/doc_sanitize.cfg](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/demos/doc_sanitize.cfg)
 - [docs/README.md](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/docs/README.md?plain=1)
 - [docs/source/content/contributing.md](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/docs/source/content/contributing.md?plain=1)
 - [docs/source/content/hook_system.md](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/docs/source/content/hook_system.md?plain=1)
 - [docs/source/content/tutorials.md](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/docs/source/content/tutorials.md?plain=1)
 - [makefile](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/makefile)
 - [pyproject.toml](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/pyproject.toml)
 - [transformer_lens/__init__.py](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/transformer_lens/__init__.py)
 - [uv.lock](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/uv.lock)
 
  This document covers the development infrastructure, testing systems, and contribution workflow for the TransformerLens project. As of version 3.0, the project has transitioned to `uv` for package management and introduced the `TransformerBridge` architecture, which requires specific development practices.

 For details on contributing, see [Contributing Guide](https://deepwiki.com/TransformerLensOrg/TransformerLens/10.1-contributing-guide). For information on automated testing, see [CI/CD Pipeline](https://deepwiki.com/TransformerLensOrg/TransformerLens/10.2-cicd-pipeline). For environment setup instructions, see [Development Environment](https://deepwiki.com/TransformerLensOrg/TransformerLens/10.3-development-environment).

 
## Development Ecosystem

 TransformerLens 3.0 uses a modernized toolchain centered around `uv`. The project maintains two parallel systems: the legacy `HookedTransformer` and the new `TransformerBridge`. Contributors are expected to mirror relevant behavioral changes across both systems where applicable.

 
### Development Tools Architecture

 
```

```

 The environment is managed via `uv sync`, which installs dependencies defined in `pyproject.toml` [pyproject.toml1-92](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/pyproject.toml#L1-L92) Formatting and type-checking are enforced through `make` targets [makefile13-22](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/makefile#L13-L22)

 **Sources**: [pyproject.toml1-92](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/pyproject.toml#L1-L92) [makefile1-22](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/makefile#L1-L22) [AGENTS.md9-18](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/AGENTS.md?plain=1#L9-L18) [docs/source/content/contributing.md37-55](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/docs/source/content/contributing.md?plain=1#L37-L55)

 
## CI/CD and Testing Tiers

 The CI/CD pipeline, defined in `.github/workflows/checks.yml`, runs on every push to `main` and `dev*` branches [.github/workflows/checks.yml1-11](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/ .github/workflows/checks.yml#L1-L11) It executes a tiered testing strategy to balance speed and coverage.

 
### Testing Workflow Structure

 
```

```

 
| Tier | Command | Purpose |
|---|---|---|
| Unit | make unit-test | Tests single modules/functions without loading real models makefile23-24 |
| Integration | make integration-test | Cross-component tests using 1-2 cached models makefile26-27 |
| Acceptance | make acceptance-test | End-to-end validation with full model loads makefile29-30 |
| Notebook | make notebook-test | Validates tutorial notebooks using nbval makefile41-64 |

 **Sources**: [.github/workflows/checks.yml1-131](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/.github/workflows/checks.yml#L1-L131) [makefile23-77](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/makefile#L23-L77) [docs/source/content/contributing.md73-96](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/docs/source/content/contributing.md?plain=1#L73-L96)

 
## Code Standards and Quality

 TransformerLens enforces strict code quality via `black`, `isort`, `pycln`, and `mypy`.

 
### Quality Enforcement Pipeline

 
```

```

 `black` is configured with a custom line length of 100 [pyproject.toml122-123](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/pyproject.toml#L122-L123) Type checking with `mypy` is mandatory for all new contributions, and the project prohibits the use of `# type: ignore` [AGENTS.md16](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/AGENTS.md?plain=1#L16-L16)

 **Sources**: [pyproject.toml113-131](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/pyproject.toml#L113-L131) [makefile13-22](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/makefile#L13-L22) [AGENTS.md15-18](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/AGENTS.md?plain=1#L15-L18) [docs/source/content/contributing.md103-115](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/docs/source/content/contributing.md?plain=1#L103-L115)

 
## Documentation and Tutorials

 Documentation is generated using Sphinx and hosted on GitHub Pages. It integrates Python docstrings, Markdown files, and Jupyter notebooks.

 
 - **Build Command**: `uv run build-docs` [makefile82-83](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/makefile#L82-L83)
 - **Live Preview**: `uv run docs-hot-reload` [makefile79-80](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/makefile#L79-L80)
 - **Tutorials**: Maintained as notebooks in the `demos/` directory and verified during CI [makefile41-64](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/makefile#L41-L64)
 
 **Sources**: [docs/README.md1-35](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/docs/README.md?plain=1#L1-L35) [makefile79-84](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/makefile#L79-L84) [docs/source/content/tutorials.md1-40](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/docs/source/content/tutorials.md?plain=1#L1-L40)

 
## Child Pages

 
 - **[Contributing Guide](https://deepwiki.com/TransformerLensOrg/TransformerLens/10.1-contributing-guide)** — Detailed workflow for submitting PRs, mirroring requirements between Bridge and HookedTransformer, and using AI coding agents.
 - **[CI/CD Pipeline](https://deepwiki.com/TransformerLensOrg/TransformerLens/10.2-cicd-pipeline)** — Deep dive into GitHub Actions workflows, test tiers, model caching strategies, and the release process.
 - **[Development Environment](https://deepwiki.com/TransformerLensOrg/TransformerLens/10.3-development-environment)** — Setup guide for `uv`, DevContainers, environment variables (`HF_TOKEN`), and formatting tools.
