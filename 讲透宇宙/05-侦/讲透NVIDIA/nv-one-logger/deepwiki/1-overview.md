<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/nv-one-logger · page 1 Overview · fetched 2026-10-26 -->

# Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)

</details>



## Purpose and Scope

This document provides an overview of the `nv-one-logger` monorepo, a comprehensive logging and telemetry system designed for machine learning and general application telemetry. The system provides a foundational core library with specialized extensions for different domains and backend integrations. This overview covers the monorepo architecture, component relationships, and how the different packages work together to provide a flexible telemetry solution.

For specific implementation details of individual packages, see [Core Package (one_logger_core)](#2), [Training Telemetry Package](#3), [Backend Integrations](#4), and [Application Integrations](#5). For development and deployment procedures, see [Development and Deployment](#6).

## Monorepo Architecture

The `nv-one-logger` system is organized as a monorepo containing five independent Python packages that share common development practices while maintaining separate CI/CD pipelines and release cycles. Each package serves a specific architectural role within the larger telemetry ecosystem.

### Package Structure and Dependencies

```mermaid
graph TB
    subgraph "nv_one_logger namespace"
        subgraph "Foundation Layer"
            Core["one_logger_core<br/>nv_one_logger.api<br/>nv_one_logger.core<br/>nv_one_logger.exporter<br/>nv_one_logger.recorder"]
        end
        
        subgraph "Domain Layer"
            Training["one_logger_training_telemetry<br/>nv_one_logger.training_telemetry.api"]
        end
        
        subgraph "Backend Layer"
            OTEL["one_logger_otel<br/>nv_one_logger.otel.exporter"]
            WandB["one_logger_wandb<br/>nv_one_logger.wandb.exporter"]
        end
        
        subgraph "Application Layer"
            PTL["one_logger_pytorch_lightning_integration<br/>nv_one_logger.training_telemetry.integration"]
        end
    end
    
    Core --> Training
    Core --> OTEL
    Core --> WandB
    Training --> PTL
    
    Training -.-> Core
    OTEL -.-> Core
    WandB -.-> Core
    PTL -.-> Training
```

**Sources:** [README.md:1-106]()

### Component Relationships and Data Flow

The following diagram shows the key classes and modules that enable data flow between components:

```mermaid
graph LR
    subgraph "User Applications"
        UserApp["Application Code"]
        MLApp["ML Training Code"]
        PTLApp["PyTorch Lightning App"]
    end
    
    subgraph "API Layer"
        TimedSpan["timed_span<br/>(context manager)"]
        OneLoggerProvider["OneLoggerProvider<br/>.configure()"]
        TrainingProvider["TrainingTelemetryProvider"]
        PTLCallbacks["TimeEventCallback<br/>OneLoggerPTLTrainer<br/>hook_trainer_cls"]
    end
    
    subgraph "Core Processing"
        Span["core.span.Span"]
        Events["core.events"]
        Attributes["core.attributes"]
        Recorder["recorder implementations"]
    end
    
    subgraph "Export Backends"
        FileExporter["exporter.file_exporter<br/>FileExporter"]
        LoggerExporter["exporter.logger_exporter<br/>LoggerExporter"]
        OTELExporter["otel.exporter<br/>OpenTelemetryExporter"]
        WandBExporter["wandb.exporter<br/>WandBExporter"]
    end
    
    UserApp --> TimedSpan
    MLApp --> TrainingProvider
    PTLApp --> PTLCallbacks
    
    TimedSpan --> OneLoggerProvider
    TrainingProvider --> OneLoggerProvider
    PTLCallbacks --> TrainingProvider
    
    OneLoggerProvider --> Recorder
    Recorder --> Span
    Span --> Events
    Span --> Attributes
    
    Recorder --> FileExporter
    Recorder --> LoggerExporter
    Recorder --> OTELExporter
    Recorder --> WandBExporter
```

**Sources:** [README.md:14-46](), [README.md:63-100]()

## Package Overview

The monorepo contains five packages organized by architectural responsibility:

| Package | Purpose | Key Modules | Dependencies |
|---------|---------|-------------|--------------|
| `one_logger_core` | Foundation logging functionality | `api`, `core`, `exporter`, `recorder` | None (base layer) |
| `one_logger_training_telemetry` | ML training telemetry specialization | `training_telemetry.api` | `one_logger_core` |
| `one_logger_otel` | OpenTelemetry integration | `otel.exporter` | `one_logger_core` |
| `one_logger_wandb` | Weights & Biases integration | `wandb.exporter` | `one_logger_core` |
| `one_logger_pytorch_lightning_integration` | PyTorch Lightning callbacks | `training_telemetry.integration` | `one_logger_training_telemetry` |

**Sources:** [README.md:63-100]()

### Development Structure

Each package follows a consistent development structure that enables independent evolution while maintaining shared practices:

```mermaid
graph TB
    subgraph "Common Structure"
        subgraph "Package Layout"
            SrcDir["src/nv_one_logger/<package>/"]
            TestsDir["tests/"]
            PyProject["pyproject.toml<br/>(Poetry configuration)"]
            Makefile["Makefile<br/>(Development automation)"]
        end
        
        subgraph "CI/CD Independence"
            Pipeline["GitLab CI Pipeline<br/>Package-specific jobs"]
            StagingRepo["Artifactory Staging<br/>hwinf-mlwfo-staging-pypi"]
            ProdRepo["Artifactory Production<br/>hwinf-mlwfo-pypi"]
        end
    end
    
    SrcDir --> Pipeline
    TestsDir --> Pipeline
    PyProject --> Pipeline
    Pipeline --> StagingRepo
    Pipeline --> ProdRepo
```

**Sources:** [README.md:52-60]()

### Namespace Organization

All packages share the `nv_one_logger` Python namespace, allowing for consistent imports and logical organization:

- **Core APIs**: `from nv_one_logger.api import timed_span, OneLoggerProvider`
- **Training APIs**: `from nv_one_logger.training_telemetry.api import TrainingTelemetryProvider`
- **Backend Exporters**: `from nv_one_logger.otel.exporter import OpenTelemetryExporter`
- **Integration Callbacks**: `from nv_one_logger.training_telemetry.integration import TimeEventCallback`

This namespace design enables users to import functionality from different packages seamlessly while maintaining clear package boundaries and dependencies.

**Sources:** [README.md:14-46](), [README.md:55]()

## Key Architectural Patterns

The system employs several key patterns that enable flexibility and maintainability:

1. **Layered Dependencies**: Foundation → Domain → Backend/Application layers prevent circular dependencies
2. **Extensible Exporters**: Base exporter classes in `one_logger_core` enable custom backend implementations
3. **Configuration Management**: Declarative configuration through `ExporterConfigManager` supports multiple configuration sources
4. **Independent Deployment**: Each package has its own CI/CD pipeline enabling independent release cycles
5. **Shared Namespace**: Common `nv_one_logger` namespace provides consistent user experience across packages

**Sources:** [README.md:5-8]()

---

