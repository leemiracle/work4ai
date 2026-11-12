<!-- source: DeepWiki mcp.deepwiki.com · repo araffin/rl-baselines-zoo · page 5 Development and Deployment · fetched 2026-10-30 -->

# Development and Deployment

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.dockerignore](.dockerignore)
- [tests/test_train.py](tests/test_train.py)

</details>



This section covers the infrastructure and tooling for developing, testing, and deploying the RL Baselines Zoo training system. It includes containerization with Docker, automated testing frameworks, and development workflow tools that ensure code quality and reproducible environments.

For specific Docker configuration details, see [Docker Setup and Containerization](#5.1). For testing implementation details, see [Testing Framework](#5.2). For build tools and repository configuration, see [Development Tools and Configuration](#5.3).

## Development Infrastructure Overview

The RL Baselines Zoo provides a comprehensive development infrastructure that supports both local development and production deployment scenarios. The system is designed around three core pillars: containerization for environment consistency, automated testing for quality assurance, and development tools for workflow automation.

### Development Infrastructure Components

```mermaid
graph TB
    subgraph "Containerization Layer"
        A["docker/Dockerfile"]
        B["docker/Dockerfile.cpu"] 
        C["docker/Dockerfile.gpu"]
        D["scripts/build_docker.sh"]
        E[".dockerignore"]
    end
    
    subgraph "Testing Framework"
        F["tests/test_train.py"]
        G["tests/test_enjoy.py"]
        H["tests/test_hyperparams_opt.py"]
        I[".travis.yml"]
        J["scripts/run_tests_travis.sh"]
    end
    
    subgraph "Build and Development Tools"
        K["Makefile"]
        L["requirements.txt"]
        M[".coveragerc"]
        N[".gitignore"]
        O["setup.py"]
    end
    
    subgraph "Core Application Targets"
        P["train.py"]
        Q["enjoy.py"]
        R["hyperparams_opt.py"]
        S["utils/benchmark.py"]
    end
    
    A --> E
    B --> E
    C --> E
    D --> A
    D --> B
    D --> C
    
    F --> P
    G --> Q
    H --> R
    
    I --> J
    J --> F
    J --> G
    J --> H
    
    K --> F
    K --> G
    K --> H
    K --> L
    
    A --> P
    B --> P
    C --> P
    
    style I fill:#f9f9f9
    style A fill:#f9f9f9
    style F fill:#f9f9f9
```

Sources: [tests/test_train.py:1-62](), [.dockerignore:1-13]()

## Testing Architecture

The testing framework validates core functionality across different algorithms and environments using `pytest`. The test suite covers training workflows, model evaluation, and hyperparameter optimization processes.

### Test Execution Flow

```mermaid
flowchart TD
    A["pytest"] --> B["test_train.py"]
    A --> C["test_enjoy.py"] 
    A --> D["test_hyperparams_opt.py"]
    
    B --> E["test_train()"]
    B --> F["test_continue_training()"]
    
    E --> G["ALGOS = ('ppo2', 'a2c', 'acer', 'acktr', 'dqn', 'trpo')"]
    E --> H["ENV_IDS = ('CartPole-v1', 'BreakoutNoFrameskip-v4')"]
    E --> I["N_STEPS = 100"]
    
    G --> J["experiments dict generation"]
    H --> J
    
    J --> K["@pytest.mark.parametrize"]
    K --> L["subprocess.call(['python', 'train.py'] + args)"]
    
    F --> M["Continue training test with -i flag"]
    M --> N["trained_agents/a2c/MountainCar-v0.pkl"]
    
    L --> O["_assert_eq(return_code, 0)"]
    
    style K fill:#f9f9f9
    style L fill:#f9f9f9
    style O fill:#f9f9f9
```

Sources: [tests/test_train.py:8-62]()

### Test Configuration Matrix

The testing system uses a parametrized approach to validate multiple algorithm-environment combinations:

| Test Category | Algorithms | Environments | Purpose |
|---------------|------------|--------------|---------|
| Core Algorithms | `ppo2`, `a2c`, `acer`, `acktr`, `dqn`, `trpo` | `CartPole-v1`, `BreakoutNoFrameskip-v4` | Basic training validation |
| Continuous Control | `ddpg` | `MountainCarContinuous-v0` | DDPG-specific testing |
| SAC Algorithm | `sac` | `Pendulum-v0` | SAC-specific testing |
| Complex Environments | `ppo2` | `BipedalWalkerHardcore-v3` | VecNormalize and frame-stack testing |
| Continue Training | `a2c` | `MountainCar-v0` | Model loading and continuation |

Sources: [tests/test_train.py:14-30]()

## Docker Containerization System

The containerization system provides isolated, reproducible environments for training and evaluation. The Docker setup supports both CPU and GPU configurations with appropriate base images and dependency management.

### Docker Build Configuration

```mermaid
graph LR
    A["scripts/build_docker.sh"] --> B["docker/Dockerfile"]
    A --> C["docker/Dockerfile.cpu"]
    A --> D["docker/Dockerfile.gpu"]
    
    E[".dockerignore"] --> B
    E --> C
    E --> D
    
    F["requirements.txt"] --> B
    F --> C
    F --> D
    
    B --> G["Base Container Image"]
    C --> H["CPU-Optimized Image"]
    D --> I["GPU-Enabled Image"]
    
    J["scripts/run_docker_cpu.sh"] --> H
    K["scripts/run_docker_gpu.sh"] --> I
    
    style A fill:#f9f9f9
    style E fill:#f9f9f9
```

Sources: [.dockerignore:1-13]()

### Docker Exclusion Patterns

The `.dockerignore` file defines which files and directories are excluded from Docker build contexts to optimize build performance and container size:

```
__pycache__/         # Python bytecode cache
logs/                # Training logs
.pytest_cache/       # Test cache
.coverage            # Coverage reports
trained_agents/      # Pre-trained models
.git/                # Git repository data
```

Sources: [.dockerignore:1-13]()

## Development Workflow Integration

The development infrastructure integrates with continuous integration systems and provides automated validation of code changes. The workflow ensures that all core functionality remains operational across different environments and configurations.

### CI/CD Pipeline Structure

```mermaid
flowchart TB
    A["Git Push/Pull Request"] --> B[".travis.yml"]
    B --> C["scripts/run_tests_travis.sh"]
    
    C --> D["Environment Setup"]
    D --> E["Dependency Installation"]
    E --> F["Test Execution"]
    
    F --> G["test_train.py"]
    F --> H["test_enjoy.py"] 
    F --> I["test_hyperparams_opt.py"]
    
    G --> J["Algorithm Coverage Check"]
    H --> K["Evaluation Validation"]
    I --> L["Optimization Testing"]
    
    J --> M["Coverage Report"]
    K --> M
    L --> M
    
    M --> N["Build Status"]
    
    style B fill:#f9f9f9
    style C fill:#f9f9f9
    style M fill:#f9f9f9
```

Sources: [tests/test_train.py:36-47]()

## Quality Assurance Mechanisms

The development infrastructure incorporates multiple quality assurance mechanisms including test parametrization, return code validation, and environment cleanup procedures.

### Test Validation Process

The testing framework uses subprocess calls to validate the actual command-line interface of the training system:

```python
return_code = subprocess.call(['python', 'train.py'] + args)
_assert_eq(return_code, 0)
```

This approach ensures that the testing validates the complete end-to-end workflow as users would experience it, rather than just testing individual functions in isolation.

Sources: [tests/test_train.py:46-47](), [tests/test_train.py:8-9]()

The test environment cleanup ensures consistent test execution by removing previous test artifacts before each test run, maintaining isolated test conditions across different algorithm and environment combinations.

Sources: [tests/test_train.py:31-33]()

---

