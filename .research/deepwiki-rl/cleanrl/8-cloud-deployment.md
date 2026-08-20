# deepwiki cleanrl §8 cloud-deployment
> 来源: https://deepwiki.com/vwxyzjn/cleanrl/8-cloud-deployment

$/$
$?

/$

DeepWiki

DeepWiki
vwxyzjn/cleanrl

$?

/$

Last indexed:  27 July 2026  (fe8d8a)

  - Overview
  - Getting Started
  - Installation
  - Basic Usage
  - Model Zoo and HuggingFace Integration
  - Core Algorithms
  - PPO (Proximal Policy Optimization)
  - DQN (Deep Q-Network)
  - SAC (Soft Actor-Critic)
  - DDPG and TD3
  - Advanced Algorithms
  - JAX Implementations
  - JAX Algorithm Implementations
  - EnvPool XLA Integration
  - Environment Integrations
  - Classic Control
  - Atari Games
  - MuJoCo and Continuous Control
  - Procgen and Generalization
  - Multi-agent Environments
  - Isaac Gym Integration
  - EnvPool Integration
  - Benchmarking and Evaluation
  - Running Benchmarks
  - Experiment Tracking
  - Hyperparameter Tuning with Optuna
  - Cloud Deployment
  - AWS Batch Setup
  - Docker Containers
  - Testing and CI/CD
  - Development Guide
  - Contributing
  - Glossary

Menu

## Cloud Deployment

Relevant source files

  - .dockerignore

  - .gitpod.Dockerfile

  - .gitpod.yml

  - Dockerfile

  - cloud/main.tf

  - cloud/modules/cleanrl/main.tf

  - cloud/modules/cleanrl/setups.tf

  - cloud/modules/cleanrl/variables.tf

### Purpose and Scope

This document provides an overview of CleanRL's cloud deployment infrastructure, which enables large-scale distributed training and benchmarking of RL algorithms across multiple environments and seeds. Cloud deployment is essential for reproducing the benchmark results published at benchmark.cleanrl.dev and for running experiments that exceed local compute capacity.

The cloud infrastructure consists of two primary components:

  - AWS Batch compute environments provisioned via Terraform for elastic GPU/CPU allocation.

  - Docker containers that encapsulate CleanRL algorithms with all dependencies for reproducible execution.

For detailed instructions on configuring AWS Batch resources, see AWS Batch Setup. For Docker container specifications and development environments, see Docker Containers. For information on how to trigger cloud benchmarks from your local machine, see Running Benchmarks.

Sources: cloud/main.tf1-29 cloud/modules/cleanrl/main.tf1-74

### Cloud Deployment Architecture

CleanRL's cloud deployment uses AWS Batch as the primary orchestration platform, with Terraform managing infrastructure as code. The system supports both cost-optimized spot instances and guaranteed on-demand instances, with automatic fallback strategies.

#### High-Level Infrastructure Overview

```

```

Diagram: CleanRL Cloud Deployment Architecture

This architecture enables cost-efficient large-scale experimentation through:

  - Dual provisioning strategy : Spot instances (configured with spot_bid_percentage = "50" ) with on-demand fallback cloud/main.tf 19

  - Instance diversity : Multiple instance types ranging from ARM-based c6g.medium to GPU-accelerated g4dn.4xlarge cloud/main.tf 20-28

  - Infrastructure as code : All AWS resources managed through Terraform for reproducibility cloud/main.tf 1-15

  - Containerized execution : Docker ensures consistent environments across all instance types using a standard Dockerfile Dockerfile 1-22

Sources: cloud/main.tf17-29 cloud/modules/cleanrl/main.tf1-74 cloud/modules/cleanrl/variables.tf25-36 Dockerfile1-22

### Terraform Module Structure

The cloud infrastructure is organized as a reusable Terraform module that provisions AWS Batch compute environments and job queues. The module creates separate resources for spot and on-demand instances, each with dedicated job queues.

#### Resource Provisioning Pattern

```

```

Diagram: Terraform Resource Dependencies

The module creates resources in this order:

  - IAM setup : Three roles ( ecs_instance_role , aws_batch_service_role , aws_spot_fleet_service_role ) with appropriate policies cloud/modules/cleanrl/setups.tf 1-75

  - Network setup : Default VPC with security group aws_batch_compute_environment_security_group allowing egress cloud/modules/cleanrl/setups.tf 77-96

  - Compute environments : One per instance type for spot and on-demand cloud/modules/cleanrl/main.tf 5-63

  - Job queues : Linked to corresponding compute environments cloud/modules/cleanrl/main.tf 27-73

Sources: cloud/modules/cleanrl/main.tf1-74 cloud/modules/cleanrl/setups.tf1-96 cloud/modules/cleanrl/variables.tf1-37

### Instance Type Configuration

CleanRL's default configuration provisions several instance types optimized for different workloads. The Terraform module uses a `count` parameter to create parallel resources for each instance type.

#### Instance Type Matrix

| Instance Type | vCPUs | Memory | GPU | Primary Use Case |
| g4dn.4xlarge | 16 | 64 GB | NVIDIA T4 | Multi-GPU training, Atari with CNN cloud/main.tf 21 |
| g4dn.xlarge | 4 | 16 GB | NVIDIA T4 | Single-GPU training, MuJoCo cloud/main.tf 22 |
| r5ad.large | 2 | 16 GB | None | Memory-intensive CPU tasks cloud/main.tf 23 |
| c5a.large | 2 | 4 GB | None | Compute-optimized CPU tasks cloud/main.tf 24 |
| c6g.medium | 1 | 2 GB | None (ARM) | Lightweight testing, classic control cloud/main.tf 26 |
| m6gd.medium | 1 | 4 GB | None (ARM) | ARM-based development cloud/main.tf 27 |

Each instance type receives two compute environments (spot and on-demand) and two job queues, resulting in 12 total job queues for the default configuration cloud/modules/cleanrl/main.tf1-74

Sources: cloud/main.tf20-28 cloud/modules/cleanrl/variables.tf25-36

### Docker and Environment Setup

The codebase includes comprehensive support for containerized execution and remote development environments.

#### Docker Containerization

The primary `Dockerfile` uses `nvidia/cuda:11.4.2-runtime-ubuntu20.04` as a base Dockerfile1 It installs essential system dependencies like `xvfb`, `ffmpeg`, and `python-opengl` for rendering environment frames Dockerfile6 Python dependencies are managed using `uv` for high-performance installation Dockerfile11-14

#### Gitpod Integration

For developers who prefer cloud-based IDEs, CleanRL provides a `.gitpod.yml` and `.gitpod.Dockerfile`  .gitpod.yml1-27 This setup includes:

  - VNC Support : Uses workspace-full-vnc for rendering GUI-based environments .gitpod.Dockerfile 1

  - Automated Setup : Runs uv pip install . on initialization .gitpod.yml 5

  - MuJoCo Dependencies : Pre-installs system libraries required for mujoco_py .gitpod.Dockerfile 16-20

For detailed specifications on the Docker build process and entrypoints, see Docker Containers.

Sources: Dockerfile1-22  .gitpod.Dockerfile1-21  .gitpod.yml1-27 .dockerignore1-10

### Cost Optimization and Scaling

The cloud infrastructure implements several strategies to minimize costs:

  - Spot Instances : Leverages AWS Spot instances with a configurable spot_bid_percentage (default 50%) cloud/modules/cleanrl/variables.tf 19-23

  - Auto-scaling : Compute environments are configured with min_vcpus = 0 and max_vcpus = 2000 , ensuring resources are only provisioned during active training cloud/modules/cleanrl/variables.tf 1-5

  - Allocation Strategies : Supports BEST_FIT and SPOT_CAPACITY_OPTIMIZED to ensure jobs are placed on the most cost-effective or available hardware cloud/modules/cleanrl/variables.tf 7-17

For a deep dive into configuring these AWS resources, see AWS Batch Setup.

Sources: cloud/modules/cleanrl/main.tf41-63 cloud/modules/cleanrl/variables.tf1-23



#### On this page

  - Cloud Deployment
  - Purpose and Scope
  - Cloud Deployment Architecture
  - High-Level Infrastructure Overview
  - Terraform Module Structure
  - Resource Provisioning Pattern
  - Instance Type Configuration
  - Instance Type Matrix
  - Docker and Environment Setup
  - Docker Containerization
  - Gitpod Integration
  - Cost Optimization and Scaling

$!/$$/$
