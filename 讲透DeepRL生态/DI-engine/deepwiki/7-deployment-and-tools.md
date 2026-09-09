> 来源: [https://deepwiki.com/opendilab/DI-engine/7-deployment-and-tools](https://deepwiki.com/opendilab/DI-engine/7-deployment-and-tools)
> DeepWiki opendilab/DI-engine | Last indexed: 20 April 2025 (c290a6

# Deployment and Tools

  Relevant source files 
 - [.github/workflows/algo_test.yml](https://github.com/opendilab/DI-engine/blob/c290a673/.github/workflows/algo_test.yml)
 - [.github/workflows/badge.yml](https://github.com/opendilab/DI-engine/blob/c290a673/.github/workflows/badge.yml)
 - [.github/workflows/deploy.yml](https://github.com/opendilab/DI-engine/blob/c290a673/.github/workflows/deploy.yml)
 - [.github/workflows/doc.yml](https://github.com/opendilab/DI-engine/blob/c290a673/.github/workflows/doc.yml)
 - [.github/workflows/envpool_test.yml](https://github.com/opendilab/DI-engine/blob/c290a673/.github/workflows/envpool_test.yml)
 - [.github/workflows/platform_test.yml](https://github.com/opendilab/DI-engine/blob/c290a673/.github/workflows/platform_test.yml)
 - [.github/workflows/release.yml](https://github.com/opendilab/DI-engine/blob/c290a673/.github/workflows/release.yml)
 - [.github/workflows/release_conda.yml](https://github.com/opendilab/DI-engine/blob/c290a673/.github/workflows/release_conda.yml)
 - [.github/workflows/style.yml](https://github.com/opendilab/DI-engine/blob/c290a673/.github/workflows/style.yml)
 - [.github/workflows/unit_test.yml](https://github.com/opendilab/DI-engine/blob/c290a673/.github/workflows/unit_test.yml)
 - [cloc.sh](https://github.com/opendilab/DI-engine/blob/c290a673/cloc.sh)
 - [conda/conda_build_config.yaml](https://github.com/opendilab/DI-engine/blob/c290a673/conda/conda_build_config.yaml)
 - [ding/framework/middleware/tests/test_trainer.py](https://github.com/opendilab/DI-engine/blob/c290a673/ding/framework/middleware/tests/test_trainer.py)
 - [ding/utils/render_helper.py](https://github.com/opendilab/DI-engine/blob/c290a673/ding/utils/render_helper.py)
 - [dizoo/atari/config/serial/pong/pong_dqn_render_config.py](https://github.com/opendilab/DI-engine/blob/c290a673/dizoo/atari/config/serial/pong/pong_dqn_render_config.py)
 - [dizoo/dmc2gym/__init__.py](https://github.com/opendilab/DI-engine/blob/c290a673/dizoo/dmc2gym/__init__.py)
 - [dizoo/dmc2gym/entry/dmc2gym_save_replay_example.py](https://github.com/opendilab/DI-engine/blob/c290a673/dizoo/dmc2gym/entry/dmc2gym_save_replay_example.py)
 - [dizoo/dmc2gym/envs/__init__.py](https://github.com/opendilab/DI-engine/blob/c290a673/dizoo/dmc2gym/envs/__init__.py)
 - [dizoo/dmc2gym/envs/dmc2gym_env.py](https://github.com/opendilab/DI-engine/blob/c290a673/dizoo/dmc2gym/envs/dmc2gym_env.py)
 - [dizoo/dmc2gym/envs/test_dmc2gym_env.py](https://github.com/opendilab/DI-engine/blob/c290a673/dizoo/dmc2gym/envs/test_dmc2gym_env.py)
 - [dizoo/image_classification/imagenet.png](https://github.com/opendilab/DI-engine/blob/c290a673/dizoo/image_classification/imagenet.png)
 - [docker/Dockerfile.base](https://github.com/opendilab/DI-engine/blob/c290a673/docker/Dockerfile.base)
 - [docker/Dockerfile.env](https://github.com/opendilab/DI-engine/blob/c290a673/docker/Dockerfile.env)
 - [docker/Dockerfile.rpc](https://github.com/opendilab/DI-engine/blob/c290a673/docker/Dockerfile.rpc)
 
  
## Purpose and Scope

 This document covers the deployment options and tooling ecosystem for DI-engine, explaining how to package, distribute, and deploy reinforcement learning environments and algorithms using Docker containers, CI/CD pipelines, and various deployment targets. It also describes utilities for rendering and recording training sessions. For information on the core architecture of DI-engine, see [Core Architecture](https://deepwiki.com/opendilab/DI-engine/2-core-architecture).

 
## Docker Containerization

 DI-engine provides a comprehensive Docker containerization system for creating reproducible environments across various platforms and deployment scenarios.

 
### Container Architecture

 
```

```

 Sources: [docker/Dockerfile.base](https://github.com/opendilab/DI-engine/blob/c290a673/docker/Dockerfile.base) [docker/Dockerfile.env](https://github.com/opendilab/DI-engine/blob/c290a673/docker/Dockerfile.env) [docker/Dockerfile.rpc](https://github.com/opendilab/DI-engine/blob/c290a673/docker/Dockerfile.rpc) [.github/workflows/deploy.yml](https://github.com/opendilab/DI-engine/blob/c290a673/.github/workflows/deploy.yml)

 
### Base Images

 The base image (`opendilab/ding:nightly`) is built on PyTorch 1.12.1 with CUDA 11.3 support and includes all core DI-engine dependencies. A separate documentation image (`opendilab/ding:nightly-doc`) is available for documentation building.

 The base image is defined in [docker/Dockerfile.base](https://github.com/opendilab/DI-engine/blob/c290a673/docker/Dockerfile.base) with the following key characteristics:

 
 - Built on PyTorch 1.12.1 CUDA 11.3 cuDNN8 runtime
 - Includes system dependencies for graphics rendering and development
 - Pre-installs DI-engine with fast and test dependencies
 
 
### Environment-Specific Images

 DI-engine provides specialized Docker images for different simulation environments, each extending the base image with environment-specific dependencies:

 
| Image | Environment | Key Features |
|---|---|---|
| opendilab/ding:nightly-atari | Atari games | Includes AutoROM for automatic ROM installation |
| opendilab/ding:nightly-mujoco | MuJoCo physics simulation | Pre-installed MuJoCo 2.1.0, OpenGL support |
| opendilab/ding:nightly-smac | StarCraft Multi-Agent Challenge | StarCraftII 4.10.0, SMAC environment |
| opendilab/ding:nightly-grf | Google Research Football | GFootball simulator, rendering support |
| opendilab/ding:nightly-dmc2gym | DeepMind Control Suite | DMC environment with gym wrapper |
| opendilab/ding:nightly-metaworld | Meta-World | Robotic manipulation benchmarks |
| opendilab/ding:nightly-cityflow | CityFlow | Traffic simulation environment |
| opendilab/ding:nightly-evogym | Evolution Gym | Co-optimization of robot design and control |
| opendilab/ding:nightly-d4rl | D4RL | Datasets for offline RL |

 Sources: [docker/Dockerfile.env](https://github.com/opendilab/DI-engine/blob/c290a673/docker/Dockerfile.env) [.github/workflows/deploy.yml](https://github.com/opendilab/DI-engine/blob/c290a673/.github/workflows/deploy.yml)

 
## CI/CD Pipeline

 DI-engine implements a comprehensive CI/CD pipeline using GitHub Actions to automate testing, building, and deployment processes.

 
### CI/CD Architecture

 
```

```

 Sources: [.github/workflows/unit_test.yml](https://github.com/opendilab/DI-engine/blob/c290a673/.github/workflows/unit_test.yml) [.github/workflows/algo_test.yml](https://github.com/opendilab/DI-engine/blob/c290a673/.github/workflows/algo_test.yml) [.github/workflows/platform_test.yml](https://github.com/opendilab/DI-engine/blob/c290a673/.github/workflows/platform_test.yml) [.github/workflows/envpool_test.yml](https://github.com/opendilab/DI-engine/blob/c290a673/.github/workflows/envpool_test.yml) [.github/workflows/style.yml](https://github.com/opendilab/DI-engine/blob/c290a673/.github/workflows/style.yml) [.github/workflows/doc.yml](https://github.com/opendilab/DI-engine/blob/c290a673/.github/workflows/doc.yml) [.github/workflows/deploy.yml](https://github.com/opendilab/DI-engine/blob/c290a673/.github/workflows/deploy.yml) [.github/workflows/release.yml](https://github.com/opendilab/DI-engine/blob/c290a673/.github/workflows/release.yml) [.github/workflows/release_conda.yml](https://github.com/opendilab/DI-engine/blob/c290a673/.github/workflows/release_conda.yml) [.github/workflows/badge.yml](https://github.com/opendilab/DI-engine/blob/c290a673/.github/workflows/badge.yml)

 
### GitHub Actions Workflows

 DI-engine uses several GitHub Actions workflows to automate different parts of the CI/CD process:

 
| Workflow | Purpose | Trigger |
|---|---|---|
| style.yml | Check code style with flake8 and yapf | Push, Pull Request |
| unit_test.yml | Run unit tests and upload coverage | Push, Pull Request |
| algo_test.yml | Test RL algorithms | Changes to policy, model, or RL utils |
| platform_test.yml | Test on macOS and Windows | Push, Pull Request |
| envpool_test.yml | Test EnvPool integration | Push, Pull Request |
| doc.yml | Build and deploy documentation | Push to main or doc branches |
| deploy.yml | Build and push Docker images | Push to main or deploy/docker branches |
| release.yml | Publish package to PyPI | Tag creation |
| release_conda.yml | Publish package to Conda | Tag creation or commit message with "conda" |
| badge.yml | Update repository badges | Push to main, badge, or doc branches |

 Sources: [.github/workflows/](https://github.com/opendilab/DI-engine/blob/c290a673/.github/workflows/)

 
### Docker Image Deployment

 The Docker image deployment workflow (`deploy.yml`) builds multiple Docker images:

 
 - Base image (`opendilab/ding:nightly`)
 - Documentation image (`opendilab/ding:nightly-doc`)
 - Environment-specific images (atari, mujoco, etc.)
 
 The workflow builds images using Docker BuildX for cross-platform compatibility and pushes them to Docker Hub.

 Sources: [.github/workflows/deploy.yml](https://github.com/opendilab/DI-engine/blob/c290a673/.github/workflows/deploy.yml)

 
### Package Deployment

 DI-engine can be deployed as both PyPI and Conda packages:

 
 - **PyPI Deployment**: The `release.yml` workflow builds sdist and wheel packages and publishes them to PyPI when a new tag is created.
 - **Conda Deployment**: The `release_conda.yml` workflow builds Conda packages and publishes them to Anaconda.org when a new tag is created or a commit message contains "conda".
 
 Sources: [.github/workflows/release.yml](https://github.com/opendilab/DI-engine/blob/c290a673/.github/workflows/release.yml) [.github/workflows/release_conda.yml](https://github.com/opendilab/DI-engine/blob/c290a673/.github/workflows/release_conda.yml) [conda/conda_build_config.yaml](https://github.com/opendilab/DI-engine/blob/c290a673/conda/conda_build_config.yaml)

 
## Testing Infrastructure

 DI-engine has an extensive testing infrastructure to ensure code quality and functionality:

 
### Test Types

 
| Test Type | Purpose | Configuration |
|---|---|---|
| Unit Tests | Test individual components | Running with specific Python versions (3.8, 3.9, 3.10) |
| Algorithm Tests | Test RL algorithms | Triggered by changes to policy, model, or RL utils |
| Environment Tests | Test environment integrations | EnvPool and specific environment tests |
| Platform Tests | Test cross-platform compatibility | macOS and Windows testing |
| Benchmark Tests | Performance benchmarking | Included as part of unit test workflow |

 Sources: [.github/workflows/unit_test.yml](https://github.com/opendilab/DI-engine/blob/c290a673/.github/workflows/unit_test.yml) [.github/workflows/algo_test.yml](https://github.com/opendilab/DI-engine/blob/c290a673/.github/workflows/algo_test.yml) [.github/workflows/platform_test.yml](https://github.com/opendilab/DI-engine/blob/c290a673/.github/workflows/platform_test.yml) [.github/workflows/envpool_test.yml](https://github.com/opendilab/DI-engine/blob/c290a673/.github/workflows/envpool_test.yml)

 
### K8s Integration

 DI-engine includes Kubernetes integration tools for distributed training and deployment. These are installed as part of the test environment setup:

 
```

```

 Sources: [.github/workflows/unit_test.yml29](https://github.com/opendilab/DI-engine/blob/c290a673/.github/workflows/unit_test.yml#L29-L29)

 
## Environment Recording and Rendering

 DI-engine provides tools for recording environment interactions as videos and rendering environments for visualization.

 
### Recording Architecture

 
```

```

 Sources: [ding/utils/render_helper.py](https://github.com/opendilab/DI-engine/blob/c290a673/ding/utils/render_helper.py) [dizoo/dmc2gym/envs/dmc2gym_env.py](https://github.com/opendilab/DI-engine/blob/c290a673/dizoo/dmc2gym/envs/dmc2gym_env.py)

 
### Enable Replay Saving

 The `enable_save_replay` method on environment classes allows recording interactions to video:

 
```

```

 This configuration is demonstrated in [dizoo/dmc2gym/entry/dmc2gym_save_replay_example.py](https://github.com/opendilab/DI-engine/blob/c290a673/dizoo/dmc2gym/entry/dmc2gym_save_replay_example.py) and [dizoo/atari/config/serial/pong/pong_dqn_render_config.py](https://github.com/opendilab/DI-engine/blob/c290a673/dizoo/atari/config/serial/pong/pong_dqn_render_config.py)

 For specific environments like DMC2Gym, video recording is implemented using Gym's `RecordVideo` wrapper:

 
```

```

 Sources: [dizoo/dmc2gym/envs/dmc2gym_env.py181-187](https://github.com/opendilab/DI-engine/blob/c290a673/dizoo/dmc2gym/envs/dmc2gym_env.py#L181-L187)

 
### Rendering Utilities

 The `render_helper.py` module provides utilities for rendering environments:

 
 - `render(env)`: Renders a DI-engine environment's current frame
 - `render_env(env)`: Renders a raw gym environment's current frame
 - `fps(env_manager)`: Gets the frames per second for an environment
 
 These utilities handle different environment types automatically, including MuJoCo environments that require special rendering setup.

 Sources: [ding/utils/render_helper.py](https://github.com/opendilab/DI-engine/blob/c290a673/ding/utils/render_helper.py)

 
## Documentation Tools

 DI-engine includes a dedicated documentation build system and Docker image.

 
### Documentation Build

 Documentation is built using Sphinx and deployed to GitHub Pages. The process is automated through the `doc.yml` GitHub Actions workflow, which:

 
 - Clones the DI-engine-docs repository
 - Installs documentation dependencies
 - Builds the HTML documentation
 - Deploys to GitHub Pages
 
 The documentation Docker image (`opendilab/ding:nightly-doc`) includes all tools necessary for building documentation.

 Sources: [docker/Dockerfile.base30-72](https://github.com/opendilab/DI-engine/blob/c290a673/docker/Dockerfile.base#L30-L72) [.github/workflows/doc.yml](https://github.com/opendilab/DI-engine/blob/c290a673/.github/workflows/doc.yml)

 
## Repository Metrics

 DI-engine includes tools for calculating and displaying repository metrics as badges, including:

 
 - Lines of code
 - Comment percentage
 
 These metrics are calculated using the `cloc.sh` script and updated automatically by the `badge.yml` workflow.

 Sources: [cloc.sh](https://github.com/opendilab/DI-engine/blob/c290a673/cloc.sh) [.github/workflows/badge.yml](https://github.com/opendilab/DI-engine/blob/c290a673/.github/workflows/badge.yml)
