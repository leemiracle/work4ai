> 来源: [https://deepwiki.com/hill-a/stable-baselines/7-development-and-testing](https://deepwiki.com/hill-a/stable-baselines/7-development-and-testing)
> DeepWiki hill-a/stable-baselines | Last indexed: 22 June 2025 (45beb2

# Development and Testing

  Relevant source files 
 - [.travis.yml](https://github.com/hill-a/stable-baselines/blob/45beb246/.travis.yml)
 - [Dockerfile](https://github.com/hill-a/stable-baselines/blob/45beb246/Dockerfile)
 - [Makefile](https://github.com/hill-a/stable-baselines/blob/45beb246/Makefile)
 - [docs/guide/install.rst](https://github.com/hill-a/stable-baselines/blob/45beb246/docs/guide/install.rst)
 - [scripts/build_docker.sh](https://github.com/hill-a/stable-baselines/blob/45beb246/scripts/build_docker.sh)
 - [scripts/run_docker_cpu.sh](https://github.com/hill-a/stable-baselines/blob/45beb246/scripts/run_docker_cpu.sh)
 - [scripts/run_docker_gpu.sh](https://github.com/hill-a/stable-baselines/blob/45beb246/scripts/run_docker_gpu.sh)
 - [stable_baselines/gail/model.py](https://github.com/hill-a/stable-baselines/blob/45beb246/stable_baselines/gail/model.py)
 - [stable_baselines/her/her.py](https://github.com/hill-a/stable-baselines/blob/45beb246/stable_baselines/her/her.py)
 - [tests/test_atari.py](https://github.com/hill-a/stable-baselines/blob/45beb246/tests/test_atari.py)
 - [tests/test_continuous.py](https://github.com/hill-a/stable-baselines/blob/45beb246/tests/test_continuous.py)
 - [tests/test_identity.py](https://github.com/hill-a/stable-baselines/blob/45beb246/tests/test_identity.py)
 - [tests/test_lstm_policy.py](https://github.com/hill-a/stable-baselines/blob/45beb246/tests/test_lstm_policy.py)
 - [tests/test_save.py](https://github.com/hill-a/stable-baselines/blob/45beb246/tests/test_save.py)
 
  This document covers the development workflow, testing infrastructure, and continuous integration system for stable-baselines. It explains how the project ensures code quality through comprehensive testing, automated validation, and containerized development environments.

 For information about the actual algorithms being tested, see [Core Algorithms](https://deepwiki.com/hill-a/stable-baselines/3-core-algorithms). For details about policy networks used in tests, see [Policy Networks](https://deepwiki.com/hill-a/stable-baselines/4-policy-networks). For environment management during testing, see [Environment Management](https://deepwiki.com/hill-a/stable-baselines/5-environment-management).

 
## Testing Architecture

 The stable-baselines testing system is built around specialized test environments and comprehensive validation suites that verify algorithm implementations across different scenarios.

 
### Core Testing Infrastructure

 
```

```

 The testing architecture uses purpose-built environments to validate different aspects of algorithm functionality. The `IdentityEnv` class provides a simple learning task where algorithms must learn to output the observation as the action, serving as a basic sanity check for all implementations.

 Sources: [tests/test_identity.py1-137](https://github.com/hill-a/stable-baselines/blob/45beb246/tests/test_identity.py#L1-L137) [tests/test_continuous.py1-173](https://github.com/hill-a/stable-baselines/blob/45beb246/tests/test_continuous.py#L1-L173) [stable_baselines/common/identity_env.py6-12](https://github.com/hill-a/stable-baselines/blob/45beb246/stable_baselines/common/identity_env.py#L6-L12)

 
### Algorithm Validation Pipeline

 
```

```

 Each algorithm undergoes systematic validation through the `LEARN_FUNC_DICT` configuration, which defines algorithm-specific hyperparameters optimized for the identity learning task. The validation requires achieving a reward threshold of 90 across 20 evaluation episodes.

 Sources: [tests/test_identity.py12-71](https://github.com/hill-a/stable-baselines/blob/45beb246/tests/test_identity.py#L12-L71) [tests/test_identity.py85-88](https://github.com/hill-a/stable-baselines/blob/45beb246/tests/test_identity.py#L85-L88) [tests/test_continuous.py117-136](https://github.com/hill-a/stable-baselines/blob/45beb246/tests/test_continuous.py#L117-L136)

 
## Continuous Integration System

 The project uses Travis CI with Docker-based testing to ensure consistent validation across different environments and algorithm combinations.

 
### CI/CD Pipeline Architecture

 
```

```

 The CI system splits tests into parallel jobs based on filename patterns to avoid memory issues and reduce wall-clock time. Each job runs in an isolated Docker container with pre-installed dependencies.

 Sources: [.travis.yml1-53](https://github.com/hill-a/stable-baselines/blob/45beb246/.travis.yml#L1-L53) [scripts/run_tests_travis.sh19](https://github.com/hill-a/stable-baselines/blob/45beb246/scripts/run_tests_travis.sh#L19-L19)

 
### Docker Development Environment

 
| Component | CPU Image | GPU Image |
|---|---|---|
| Base Image | ubuntu:16.04 | nvidia/cuda:9.0-cudnn7-runtime-ubuntu16.04 |
| Tag | stablebaselines/stable-baselines-cpu | stablebaselines/stable-baselines |
| Dependencies | OpenMPI, CMake, Python 3.5+ | CUDA 9.0, cuDNN 7 + CPU deps |
| Installation | pip install -e .[mpi,tests,docs] | Same as CPU |
| Usage | run_docker_cpu.sh | run_docker_gpu.sh |

 The Docker setup provides consistent development environments with all dependencies pre-installed. The images include development tools, testing frameworks, and documentation builders.

 Sources: [Dockerfile1-48](https://github.com/hill-a/stable-baselines/blob/45beb246/Dockerfile#L1-L48) [scripts/build_docker.sh1-23](https://github.com/hill-a/stable-baselines/blob/45beb246/scripts/build_docker.sh#L1-L23) [scripts/run_docker_cpu.sh1-12](https://github.com/hill-a/stable-baselines/blob/45beb246/scripts/run_docker_cpu.sh#L1-L12) [scripts/run_docker_gpu.sh1-20](https://github.com/hill-a/stable-baselines/blob/45beb246/scripts/run_docker_gpu.sh#L1-L20)

 
## Test Categories and Coverage

 
### Algorithm-Specific Test Suites

 
```

```

 Each test category targets specific algorithm capabilities:

 
 - **Identity tests** verify basic learning on simple tasks
 - **Continuous tests** validate action space handling and exploration
 - **Save/load tests** ensure model persistence across formats
 - **LSTM tests** confirm memory-dependent learning
 
 Sources: [tests/test_identity.py74-89](https://github.com/hill-a/stable-baselines/blob/45beb246/tests/test_identity.py#L74-L89) [tests/test_continuous.py109-136](https://github.com/hill-a/stable-baselines/blob/45beb246/tests/test_continuous.py#L109-L136) [tests/test_save.py38-136](https://github.com/hill-a/stable-baselines/blob/45beb246/tests/test_save.py#L38-L136) [tests/test_lstm_policy.py102-133](https://github.com/hill-a/stable-baselines/blob/45beb246/tests/test_lstm_policy.py#L102-L133)

 
## Development Workflow

 
### Build and Test Commands

 The project provides standardized commands through `Makefile` for common development tasks:

 
| Command | Script | Purpose |
|---|---|---|
| make pytest | ./scripts/run_tests.sh | Run test suite with coverage |
| make type | pytype -j auto | Type checking validation |
| make doc | cd docs && make html | Build documentation |
| make docker-cpu | ./scripts/build_docker.sh | Build CPU Docker image |
| make docker-gpu | USE_GPU=True ./scripts/build_docker.sh | Build GPU Docker image |

 
### Test Execution Patterns

 The testing system uses pytest markers to categorize and control test execution:

 
 - `@pytest.mark.slow` - Long-running algorithm training tests
 - `@pytest.mark.expensive` - Resource-intensive validation tests
 - `@pytest.mark.parametrize` - Parameterized tests across algorithms/policies
 
 Tests automatically handle resource cleanup through try/finally blocks and explicit memory management with `del model, env` statements to prevent memory leaks during continuous integration.

 Sources: [Makefile1-42](https://github.com/hill-a/stable-baselines/blob/45beb246/Makefile#L1-L42) [tests/test_identity.py74](https://github.com/hill-a/stable-baselines/blob/45beb246/tests/test_identity.py#L74-L74) [tests/test_lstm_policy.py101](https://github.com/hill-a/stable-baselines/blob/45beb246/tests/test_lstm_policy.py#L101-L101) [tests/test_continuous.py34](https://github.com/hill-a/stable-baselines/blob/45beb246/tests/test_continuous.py#L34-L34)
