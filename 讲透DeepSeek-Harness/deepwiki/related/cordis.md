> 来源: [https://deepwiki.com/cordiverse/cordis](https://deepwiki.com/cordiverse/cordis)
> DeepWiki cordiverse/cordis

# Overview

  Relevant source files 
 - [.github/workflows/build.yml](https://github.com/cordiverse/cordis/blob/00278924/.github/workflows/build.yml)
 - [README.md](https://github.com/cordiverse/cordis/blob/00278924/README.md?plain=1)
 - [package.json](https://github.com/cordiverse/cordis/blob/00278924/package.json)
 - [packages/core/README.md](https://github.com/cordiverse/cordis/blob/00278924/packages/core/README.md?plain=1)
 - [packages/core/package.json](https://github.com/cordiverse/cordis/blob/00278924/packages/core/package.json)
 
  
## Purpose and Scope

 This document provides a high-level introduction to Cordis, a meta-framework for modern JavaScript applications. It explains the core purpose, high-level architecture, and implementation details of the framework's foundation. Cordis is designed to provide a robust environment for building modular applications through a plugin-centric architecture, dependency injection, and comprehensive lifecycle management.

 Sources: [packages/core/package.json2-3](https://github.com/cordiverse/cordis/blob/00278924/packages/core/package.json#L2-L3) [package.json1-10](https://github.com/cordiverse/cordis/blob/00278924/package.json#L1-L10)

 
## What is Cordis

 Cordis is a meta-framework of **Spatiotemporal Composability** [README.md5-9](https://github.com/cordiverse/cordis/blob/00278924/README.md?plain=1#L5-L9) It facilitates the development of modular applications by providing a centralized orchestration layer. It manages the lifecycle of components (plugins), coordinates their interactions via a service-based dependency injection system, and provides a unified event bus for communication.

 The framework is distributed primarily through the `cordis` package [packages/core/package.json2](https://github.com/cordiverse/cordis/blob/00278924/packages/core/package.json#L2-L2) which acts as the main entry point for applications, and `@cordisjs/core`, which contains the fundamental logic.

 
| Feature | Description |
|---|---|
| Context-Based Orchestration | Uses a Context object as the primary interface for all framework operations. |
| Plugin System | Supports dynamic loading and management of plugins with full lifecycle tracking. |
| Service Pattern | Provides a Service base class for creating reusable, injectable components. |
| Lifecycle Management | Manages resource cleanup and state transitions through a "Fiber" system. |

 Sources: [packages/core/package.json1-9](https://github.com/cordiverse/cordis/blob/00278924/packages/core/package.json#L1-L9) [package.json1-10](https://github.com/cordiverse/cordis/blob/00278924/package.json#L1-L10) [README.md5-9](https://github.com/cordiverse/cordis/blob/00278924/README.md?plain=1#L5-L9)

 
## High-Level Architecture

 The Cordis architecture is centered around the `Context` class, which serves as the container for services and plugins. The system follows a hierarchical structure where contexts can be branched, isolated, or intercepted to create scoped environments.

 
### System Architecture Diagram

 This diagram bridges the natural language concepts of the framework to the specific code entities defined in the core package.

 
```

```

 Sources: [packages/core/package.json33-48](https://github.com/cordiverse/cordis/blob/00278924/packages/core/package.json#L33-L48) [packages/core/package.json7-17](https://github.com/cordiverse/cordis/blob/00278924/packages/core/package.json#L7-L17)

 
### Data and Control Flow

 When an application starts, the `Context` initializes its core services. Plugins are registered via the `Registry`, which creates a `Runtime` for each plugin. Dependencies between plugins and services are resolved by the `Reflect` service using property interception.

 
```

```

 Sources: [packages/core/package.json7-17](https://github.com/cordiverse/cordis/blob/00278924/packages/core/package.json#L7-L17) [packages/core/package.json33-44](https://github.com/cordiverse/cordis/blob/00278924/packages/core/package.json#L33-L44)

 
## Implementation Details

 
### The Context and Service Pattern

 The core of Cordis is the `Context` class. It acts as a proxy-like container where services are attached as properties. The `Service` class allows developers to define named units of functionality that other plugins can depend on.

 
### Dependency Injection

 Cordis uses a "demand-driven" dependency injection model. Instead of passing dependencies in constructors, plugins declare their requirements. The framework's `ReflectService` manages these declarations, ensuring that a plugin's logic only executes when its required services are available.

 
### Monorepo Organization

 Cordis is managed as a monorepo using Yarn workspaces [package.json7-10](https://github.com/cordiverse/cordis/blob/00278924/package.json#L7-L10) The `packages/` directory contains the core framework and its standard plugins.

 
| Path | Role |
|---|---|
| packages/core | The engine of the framework, containing the Context and Service logic. |
| external/* | Third-party or auxiliary packages integrated into the workspace. |
| package.json | Root configuration for yakumo build tools and vitest testing. |

 Sources: [package.json7-10](https://github.com/cordiverse/cordis/blob/00278924/package.json#L7-L10) [package.json14-19](https://github.com/cordiverse/cordis/blob/00278924/package.json#L14-L19) [packages/core/package.json1-17](https://github.com/cordiverse/cordis/blob/00278924/packages/core/package.json#L1-L17)

 
## Development Infrastructure

 Cordis uses a specialized toolchain for building and testing across its packages, orchestrated primarily via `yakumo`:

 
 - **Yakumo**: A workspace-aware task runner used for building (`yarn yakumo esbuild`, `yarn yakumo tsc`) and publishing [package.json14-15](https://github.com/cordiverse/cordis/blob/00278924/package.json#L14-L15) It is invoked via `node` with `tsx` and `@cordisjs/unyaml` for configuration handling [package.json14](https://github.com/cordiverse/cordis/blob/00278924/package.json#L14-L14)
 - **Vitest**: The primary testing framework, integrated with `yakumo-vitest` for workspace-wide execution [package.json16-36](https://github.com/cordiverse/cordis/blob/00278924/package.json#L16-L36)
 - **TSX**: Used to execute TypeScript files directly during development and within the `yakumo` script environment [package.json29](https://github.com/cordiverse/cordis/blob/00278924/package.json#L29-L29)
 - **CI/CD**: GitHub Actions handle linting, building (specifically ensuring `core` builds first), and testing on multiple Node.js versions (24, 26) [.github/workflows/build.yml43-62](https://github.com/cordiverse/cordis/blob/00278924/.github/workflows/build.yml#L43-L62)
 
 Sources: [package.json12-20](https://github.com/cordiverse/cordis/blob/00278924/package.json#L12-L20) [package.json21-37](https://github.com/cordiverse/cordis/blob/00278924/package.json#L21-L37) [.github/workflows/build.yml43-46](https://github.com/cordiverse/cordis/blob/00278924/.github/workflows/build.yml#L43-L46) [.github/workflows/build.yml56-76](https://github.com/cordiverse/cordis/blob/00278924/.github/workflows/build.yml#L56-L76)
