> 来源: [https://deepwiki.com/Tencent/WeKnora/10-development-guide](https://deepwiki.com/Tencent/WeKnora/10-development-guide)
> DeepWiki Tencent/WeKnora

# Development Guide

  Relevant source files 
 - [docs/code-slimming-audit.md](https://github.com/Tencent/WeKnora/blob/10973ed3/docs/code-slimming-audit.md?plain=1)
 - [internal/agent/tools/sandbox_ls.go](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/agent/tools/sandbox_ls.go)
 - [internal/agent/tools/todo_write.go](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/agent/tools/todo_write.go)
 - [internal/application/repository/retriever/milvus/filter.go](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/application/repository/retriever/milvus/filter.go)
 - [internal/application/repository/retriever/weaviate/repository.go](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/application/repository/retriever/weaviate/repository.go)
 - [internal/application/service/fork_bootstrapper_test.go](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/application/service/fork_bootstrapper_test.go)
 - [internal/application/service/wiki_ingest_dedup.go](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/application/service/wiki_ingest_dedup.go)
 
  This guide provides a high-level overview of the development workflow, build system, coding patterns, and tooling for contributors and developers extending WeKnora. It introduces key development modes, outlines the build architecture including CI/CD pipelines, and connects to detailed child pages covering each topic in depth.

 
| Child Page | Purpose |
|---|---|
| Development Environment Setup | Instructions on setting up the local development environment with hot-reloading, IDE integration, and debugging support. |
| Build System and CI/CD | Documentation of Makefile targets, automated build pipelines with GitHub Actions, packaging, and multi-architecture Docker image creation. |
| Code Organization and Patterns | Explanation of codebase directory layout, layered architecture principles, dependency injection approaches, and common design patterns. |
| Testing and Quality Assurance | Overview of testing methodologies, Go and Python test execution, linting configurations, and usage of the QA dataset sampling tool for quality control. |
| CLI Tool | Architecture and usage of the weknora command-line tool, including command hierarchy, output formats, and error handling. Links to specialized CLI child pages. |
| Client SDK and MCP Server | Details of the Go client SDK for API interaction, Python MCP server for tool integration, DeepSeek Harness components, and the WeChat Mini Program client. |
| Documentation Site (website-docs) | Insights into the VitePress-based documentation site, theming components, build and deployment pipeline, and guidance for adding new pages. |

 For production deployment and operational practices, refer to the [Deployment and Operations](https://deepwiki.com/Tencent/WeKnora/9-deployment-and-operations) section.

 
---

 
## Development Modes

 WeKnora supports multiple development modes tailored to different workflows and developer needs, enabled primarily via the `Makefile` and helper scripts.

 
### Local Development Mode

 In this mode, core infrastructure components such as PostgreSQL, Redis, the DocReader gRPC server, and Ollama LLM instance run inside Docker containers. Meanwhile, the WeKnora backend server and frontend run on the developer’s local machine as processes, allowing direct IDE control and enabling hot-reload for rapid iteration. Typical commands include `make dev-start` to launch dependencies and `make dev-app` or `make dev-frontend` for the active servers.

 
```

```

 This setup is optimized for active development, enabling efficient editing, compilation, and immediate feedback.

 Sources: [Makefile54-62](https://github.com/Tencent/WeKnora/blob/10973ed3/Makefile#L54-L62) [scripts/start_all.sh25-33](https://github.com/Tencent/WeKnora/blob/10973ed3/scripts/start_all.sh#L25-L33) [website-docs/01-getting-started/02-installation.md109-118](https://github.com/Tencent/WeKnora/blob/10973ed3/website-docs/01-getting-started/02-installation.md?plain=1#L109-L118)

 
### Lite Mode Development

 Lite mode is intended for lightweight desktop or embedded deployment. It produces a single statically linked binary with embedded frontend assets and uses SQLite (FTS5 + `sqlite-vec`) plus in-memory queues for data storage and processing. This mode simplifies environment dependencies and accelerates startup.

 Developers can build this variant with the `make build-lite` target.

 Sources: [Makefile64-67](https://github.com/Tencent/WeKnora/blob/10973ed3/Makefile#L64-L67) [website-docs/01-getting-started/02-installation.md12-14](https://github.com/Tencent/WeKnora/blob/10973ed3/website-docs/01-getting-started/02-installation.md?plain=1#L12-L14)

 
---

 
## Build System Architecture

 The WeKnora build system is built around a powerful, flexible `Makefile` and complementary scripts, orchestrating compilation, dependency management, Docker image builds, and distribution packaging.

 
### Key Makefile Targets

 
| Target | Purpose | Description / Underlying Command |
|---|---|---|
| build | Standard backend build | Compiles the Go backend server binary using go build |
| build-anydoc | WeKnora build with Rust-based anydoc | Adds Rust-based document parsing engine compilation with specific build tag |
| docker-build-all | Build all production Docker images | Creates multi-architecture images for the app backend, docreader, and frontend UI |
| migrate-up | Database schema migration | Runs migration scripts to update PostgreSQL database schema |
| docs | Generate API documentation | Runs swag init to regenerate OpenAPI Swagger docs |

 The `Makefile` also supports convenient commands for running tests, linting, and local development startup.

 Sources: [Makefile1-228](https://github.com/Tencent/WeKnora/blob/10973ed3/Makefile#L1-L228) [docker/Dockerfile.app63-69](https://github.com/Tencent/WeKnora/blob/10973ed3/docker/Dockerfile.app#L63-L69)

 
### Version Management Injection

 A centralized versioning script `scripts/get_version.sh` extracts semantic version info and injects it during builds. This ensures consistent version strings between binaries, frontend assets, and Docker images.

 
```

```

 This arrangement enables reproducible builds and traceability across components.

 Sources: [scripts/get_version.sh1-20](https://github.com/Tencent/WeKnora/blob/10973ed3/scripts/get_version.sh#L1-L20) [docker/Dockerfile.app36-46](https://github.com/Tencent/WeKnora/blob/10973ed3/docker/Dockerfile.app#L36-L46) [Makefile116-126](https://github.com/Tencent/WeKnora/blob/10973ed3/Makefile#L116-L126)

 
---

 
## CI/CD and Docker Pipeline

 WeKnora leverages GitHub Actions to implement a CI/CD pipeline that supports automated builds, tests, and multi-arch Docker image packaging.

 
### Docker Image Build Stages

 
 - **UI Image:** Builds the frontend assets using Node and packages them into a lightweight Nginx container [.github/workflows/docker-image.yml58-69](https://github.com/Tencent/WeKnora/blob/10973ed3/.github/workflows/docker-image.yml#L58-L69)
 - **App Image:** A multi-stage Docker build using `golang:1.26-bookworm` for compilation and a `debian:12.12-slim` minimal runtime image for the backend [docker/Dockerfile.app2-73](https://github.com/Tencent/WeKnora/blob/10973ed3/docker/Dockerfile.app#L2-L73)
 - **DocReader Image:** Contains the Python-based gRPC document parser server [docker/Dockerfile.docreader4-159](https://github.com/Tencent/WeKnora/blob/10973ed3/docker/Dockerfile.docreader#L4-L159)
 - **Sandbox Images:** Provide isolated execution environments for agent sandboxed skills with architecture-specific variants [.github/workflows/docker-image.yml119-176](https://github.com/Tencent/WeKnora/blob/10973ed3/.github/workflows/docker-image.yml#L119-L176)
 
 These steps produce images tagged by version and platform for release.

 Sources: [docker/Dockerfile.app1-138](https://github.com/Tencent/WeKnora/blob/10973ed3/docker/Dockerfile.app#L1-L138) [.github/workflows/docker-image.yml1-230](https://github.com/Tencent/WeKnora/blob/10973ed3/.github/workflows/docker-image.yml#L1-L230) [scripts/build_images.sh130-250](https://github.com/Tencent/WeKnora/blob/10973ed3/scripts/build_images.sh#L130-L250)

 
---

 
## Testing and Quality Assurance

 Testing and code quality are enforced via multiple strategies and languages.

 
 - **Backend Tests:** Go tests cover core server logic, APIs, and proto-generated interfaces. These run on GitHub Actions for every push or pull request [.github/workflows/app.yml99-104](https://github.com/Tencent/WeKnora/blob/10973ed3/.github/workflows/app.yml#L99-L104)
 - **DocReader Tests:** Python unit tests validate document parsing components and utilities. The DocReader gRPC server is launched in CI for integration testing [.github/workflows/docreader.yml61-62](https://github.com/Tencent/WeKnora/blob/10973ed3/.github/workflows/docreader.yml#L61-L62)
 - **DocReader Go Client Tests:** Ensure Go client connectivity and functionality against a live DocReader server in tests like `TestReadURL` and `TestReadFile` [docreader/client/client_test.go19-95](https://github.com/Tencent/WeKnora/blob/10973ed3/docreader/client/client_test.go#L19-L95)
 - **Linting:** Go code style and correctness are verified using `golangci-lint`, configured to only report new issues on PRs [.github/workflows/go-lint.yml100-104](https://github.com/Tencent/WeKnora/blob/10973ed3/.github/workflows/go-lint.yml#L100-L104) [.golangci.yml](https://github.com/Tencent/WeKnora/blob/10973ed3/.golangci.yml)
 
 Sources: [.github/workflows/app.yml99-104](https://github.com/Tencent/WeKnora/blob/10973ed3/.github/workflows/app.yml#L99-L104) [.github/workflows/docreader.yml38-87](https://github.com/Tencent/WeKnora/blob/10973ed3/.github/workflows/docreader.yml#L38-L87) [docreader/client/client_test.go19-95](https://github.com/Tencent/WeKnora/blob/10973ed3/docreader/client/client_test.go#L19-L95) [.github/workflows/go-lint.yml100-104](https://github.com/Tencent/WeKnora/blob/10973ed3/.github/workflows/go-lint.yml#L100-L104) [.golangci.yml](https://github.com/Tencent/WeKnora/blob/10973ed3/.golangci.yml)

 
---

 
## Development Workflow Summary

 A typical WeKnora development workflow involves:

 
 - **Environment Setup**
 Install required tools and dependencies such as Go, Node.js, and Python (for DocReader). Verify Docker is installed for containerized dependencies.
 - **Infrastructure Start**
 Use the script `scripts/start_all.sh` to launch Docker Compose services including PostgreSQL, Redis, Ollama, and DocReader servers.
 - **Frontend Development**
 Run or build the frontend with either `npm run dev` or helper scripts `scripts/build_frontend_dist.sh` for production asset packaging.
 - **Backend Development**
 Build and run the backend application with `Makefile` commands like `make build` and `make run` for live coding.
 - **Verification**
 Access the Swagger UI generated by `make docs` to interactively explore and test the public API endpoints.
 
 Sources: [Makefile1-228](https://github.com/Tencent/WeKnora/blob/10973ed3/Makefile#L1-L228) [scripts/start_all.sh1-111](https://github.com/Tencent/WeKnora/blob/10973ed3/scripts/start_all.sh#L1-L111) [website-docs/01-getting-started/02-installation.md40-45](https://github.com/Tencent/WeKnora/blob/10973ed3/website-docs/01-getting-started/02-installation.md?plain=1#L40-L45)

 
---

 
## Bridging Natural Language Concepts to Code Entities

 
### Diagram: System Natural Language to Code Entity Mapping

 
```

```

 Sources: [cmd/server/main.go1-50](https://github.com/Tencent/WeKnora/blob/10973ed3/cmd/server/main.go#L1-L50) [docreader/main.py1-40](https://github.com/Tencent/WeKnora/blob/10973ed3/docreader/main.py#L1-L40)

 
### Diagram: Development Build Pipeline Mapping

 
```

```

 Sources: [Makefile1-228](https://github.com/Tencent/WeKnora/blob/10973ed3/Makefile#L1-L228) [scripts/get_version.sh1-20](https://github.com/Tencent/WeKnora/blob/10973ed3/scripts/get_version.sh#L1-L20)

 
---

 
# References

 
 - [.github/workflows/app.yml71-124](https://github.com/Tencent/WeKnora/blob/10973ed3/.github/workflows/app.yml#L71-L124)
 - [.github/workflows/docreader.yml35-105](https://github.com/Tencent/WeKnora/blob/10973ed3/.github/workflows/docreader.yml#L35-L105)
 - [.github/workflows/go-lint.yml80-104](https://github.com/Tencent/WeKnora/blob/10973ed3/.github/workflows/go-lint.yml#L80-L104)
 - [Makefile1-228](https://github.com/Tencent/WeKnora/blob/10973ed3/Makefile#L1-L228)
 - [docreader/client/client_test.go19-95](https://github.com/Tencent/WeKnora/blob/10973ed3/docreader/client/client_test.go#L19-L95)
 - [.golangci.yml](https://github.com/Tencent/WeKnora/blob/10973ed3/.golangci.yml)
 - [scripts/get_version.sh1-20](https://github.com/Tencent/WeKnora/blob/10973ed3/scripts/get_version.sh#L1-L20)
 - [docker/Dockerfile.app2-73](https://github.com/Tencent/WeKnora/blob/10973ed3/docker/Dockerfile.app#L2-L73)
 - [scripts/start_all.sh25-33](https://github.com/Tencent/WeKnora/blob/10973ed3/scripts/start_all.sh#L25-L33)
 - [website-docs/01-getting-started/02-installation.md109-118](https://github.com/Tencent/WeKnora/blob/10973ed3/website-docs/01-getting-started/02-installation.md?plain=1#L109-L118)
 - [website-docs/01-getting-started/02-installation.md12-14](https://github.com/Tencent/WeKnora/blob/10973ed3/website-docs/01-getting-started/02-installation.md?plain=1#L12-L14)
