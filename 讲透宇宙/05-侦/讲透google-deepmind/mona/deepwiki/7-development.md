<!-- source: DeepWiki mcp.deepwiki.com · repo google-deepmind/mona · page 7 Development · fetched 2026-10-26 -->

# Development

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.gitignore](.gitignore)
- [CONTRIBUTING.md](CONTRIBUTING.md)
- [LICENSE](LICENSE)

</details>



This page provides information for developers who want to contribute to or extend the MONA research system. It covers development setup, project structure, contribution workflows, and extension points for researchers implementing new MONA experiments.

For information about running existing experiments, see [Getting Started](#2). For details about the build system architecture, see [Build System](#6.1).

## Development Environment

The MONA system uses Bazel for build management and follows Google's development practices for open source projects. The development environment supports both tabular value iteration experiments and neural network-based PPO experiments.

### Repository Structure for Developers

```mermaid
graph TB
    subgraph "Source Organization"
        SRC["src/"]
        PROTO["proto/"]
        IPYNB["ipynb/"]
        DATA_DIR["data/"]
    end
    
    subgraph "Core Development Files"
        MAIN["src/main.py"]
        ENV_CORE["src/block_push_env.py"]
        ENV_GYM["src/block_push_gym_env.py"]
        STATES["src/state.py"]
        FILE_HANDLER["src/file_handler.py"]
        RUNNER["src/runner.py"]
    end
    
    subgraph "Build Configuration"
        BUILD_ROOT["BUILD.bazel"]
        MODULE_DEF["MODULE.bazel"] 
        REQUIREMENTS["requirements.txt"]
        GITIGNORE[".gitignore"]
    end
    
    subgraph "Protocol Definitions"
        ROLLOUT_PROTO["proto/rollout.proto"]
        PROTO_BUILD["proto/BUILD.bazel"]
    end
    
    subgraph "Experimental Interfaces"
        PPO_NOTEBOOK["ipynb/ppo.ipynb"]
        ANALYSIS_NOTEBOOK["ipynb/analysis.ipynb"]
    end
    
    SRC --> MAIN
    SRC --> ENV_CORE
    SRC --> ENV_GYM
    SRC --> STATES
    SRC --> FILE_HANDLER
    SRC --> RUNNER
    
    PROTO --> ROLLOUT_PROTO
    PROTO --> PROTO_BUILD
    
    IPYNB --> PPO_NOTEBOOK
    IPYNB --> ANALYSIS_NOTEBOOK
    
    BUILD_ROOT --> MODULE_DEF
    MODULE_DEF --> REQUIREMENTS
```

*Sources: [.gitignore:1-25](), [CONTRIBUTING.md:1-26](), directory structure from system analysis*

### Development Workflow

The development workflow follows standard GitHub practices with additional requirements for Google's Contributor License Agreement:

```mermaid
graph LR
    subgraph "Contribution Process"
        CLA["Contributor License Agreement<br/>cla.developers.google.com"]
        FORK["Fork Repository"]
        BRANCH["Create Feature Branch"]
        DEVELOP["Implement Changes"]
    end
    
    subgraph "Code Quality"
        BUILD["bazel build //..."]
        TEST["bazel test //..."]
        LINT["Code Review Checks"]
    end
    
    subgraph "Submission"
        PR["GitHub Pull Request"]
        REVIEW["Code Review Process"]
        MERGE["Merge to Main"]
    end
    
    CLA --> FORK
    FORK --> BRANCH
    BRANCH --> DEVELOP
    
    DEVELOP --> BUILD
    BUILD --> TEST
    TEST --> LINT
    
    LINT --> PR
    PR --> REVIEW
    REVIEW --> MERGE
```

*Sources: [CONTRIBUTING.md:4-10](), [CONTRIBUTING.md:15-20](), [CONTRIBUTING.md:22-25]()*

## Code Organization for Extension

### Core Extension Points

The MONA system provides several key extension points for researchers:

| Component | File Path | Extension Purpose |
|-----------|-----------|------------------|
| Environment Logic | `src/block_push_env.py` | Add new gridworld mechanics |
| State Representation | `src/state.py` | Modify state encoding |
| Approval Functions | `src/main.py` | Implement new approval strategies |
| Data Persistence | `proto/rollout.proto` | Add experimental metrics |
| Neural Networks | `ipynb/ppo.ipynb` | Integrate new RL algorithms |

### Build System Integration

```mermaid
graph TD
    subgraph "Bazel Build Targets"
        MAIN_TARGET["//src:main"]
        ENV_TARGET["//src:block_push_env"]
        PROTO_TARGET["//proto:rollout_py_pb2"]
        TEST_TARGETS["//src:*_test"]
    end
    
    subgraph "Python Dependencies" 
        BAZEL_DEPS["rules_python<br/>protobuf<br/>numpy<br/>gymnasium"]
        PIP_DEPS["requirements.txt<br/>stable-baselines3<br/>matplotlib"]
    end
    
    subgraph "Generated Code"
        PROTO_PY["rollout_pb2.py"]
        PROTO_GRPC["Generated Protocol Buffers"]
    end
    
    PROTO_TARGET --> PROTO_PY
    PROTO_TARGET --> PROTO_GRPC
    
    MAIN_TARGET --> ENV_TARGET
    ENV_TARGET --> PROTO_TARGET
    
    BAZEL_DEPS --> MAIN_TARGET
    PIP_DEPS --> BAZEL_DEPS
```

*Sources: Build system analysis, [MODULE.bazel]() reference, [requirements.txt]() reference*

## Contributing Guidelines

### Licensing Requirements

All contributions must comply with the Apache 2.0 license terms and include the Contributor License Agreement:

- **License**: Apache License 2.0 with standard copyright notice
- **CLA Required**: Submit at https://cla.developers.google.com/
- **Copyright Retention**: Contributors retain copyright while granting usage rights
- **Patent Grant**: Includes patent license grant for contributions

*Sources: [LICENSE:1-203](), [CONTRIBUTING.md:4-13]()*

### Code Review Process

- **All submissions require review**: Including contributions from project members
- **GitHub Pull Requests**: Standard GitHub PR workflow for code reviews  
- **Community Guidelines**: Follow Google's Open Source Community Guidelines
- **Review Standards**: Focus on code quality, test coverage, and documentation

*Sources: [CONTRIBUTING.md:15-20](), [CONTRIBUTING.md:22-25]()*

### Development Standards

The codebase follows these development standards:

```mermaid
graph LR
    subgraph "Code Standards"
        PYTHON["Python 3.x"]
        BAZEL["Bazel Build"]
        PROTO["Protocol Buffers"]
        TYPING["Type Annotations"]
    end
    
    subgraph "File Organization"
        GITIGNORE_RULES[".gitignore Rules<br/>__pycache__/<br/>*.pyc<br/>build/<br/>dist/"]
        MODULE_STRUCTURE["Modular Design<br/>src/<br/>proto/<br/>ipynb/"]
    end
    
    subgraph "Testing"
        UNIT_TESTS["Unit Tests"]
        INTEGRATION_TESTS["Integration Tests"]
        BAZEL_TEST["bazel test //..."]
    end
    
    PYTHON --> BAZEL
    BAZEL --> PROTO
    PROTO --> TYPING
    
    GITIGNORE_RULES --> MODULE_STRUCTURE
    MODULE_STRUCTURE --> UNIT_TESTS
    UNIT_TESTS --> INTEGRATION_TESTS
    INTEGRATION_TESTS --> BAZEL_TEST
```

*Sources: [.gitignore:1-25](), [CONTRIBUTING.md](), development practices inferred from codebase structure*

## Research Extension Points

### Adding New Experimental Methods

Researchers can extend the MONA framework by:

1. **New RL Algorithms**: Extend the PPO notebook approach in `ipynb/ppo.ipynb`
2. **Modified Environments**: Extend `BlockPushEnv` class in `src/block_push_env.py` 
3. **Alternative Approval Functions**: Modify approval logic in `src/main.py`
4. **New Metrics**: Extend `rollout.proto` message definitions
5. **Analysis Tools**: Add visualization methods to `ipynb/analysis.ipynb`

### Data Format Extensions

To add new experimental data:

1. Modify protocol buffer definitions in `proto/rollout.proto`
2. Regenerate Python bindings using Bazel
3. Update file handler logic in `src/file_handler.py`
4. Add analysis support in the analysis notebook

*Sources: System architecture analysis, experimental framework design from codebase structure*

## License Information

This project is released under the Apache License 2.0. Key points for developers:

- **Open Source**: Free to use, modify, and distribute
- **Patent Grant**: Includes patent license for contributions
- **Attribution Required**: Must include license notice in distributions  
- **No Warranty**: Software provided "as is" without warranties
- **Contributor Protection**: CLA protects both contributors and project

For complete license terms, see [LICENSE:1-203]().

*Sources: [LICENSE:1-203](), [CONTRIBUTING.md:4-13]()*

---

