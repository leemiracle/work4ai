<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/deepops · page 5 CI/CD and Testing · fetched 2026-10-26 -->

# CI/CD and Testing

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [workloads/jenkins/Jenkinsfile](workloads/jenkins/Jenkinsfile)
- [workloads/jenkins/Jenkinsfile-matrix](workloads/jenkins/Jenkinsfile-matrix)
- [workloads/jenkins/Jenkinsfile-multi-nightly](workloads/jenkins/Jenkinsfile-multi-nightly)
- [workloads/jenkins/Jenkinsfile-nightly](workloads/jenkins/Jenkinsfile-nightly)
- [workloads/jenkins/scripts/jenkins-common.sh](workloads/jenkins/scripts/jenkins-common.sh)
- [workloads/jenkins/scripts/test-dcgm-metrics.sh](workloads/jenkins/scripts/test-dcgm-metrics.sh)
- [workloads/jenkins/scripts/test-deepops-registry-mirror.sh](workloads/jenkins/scripts/test-deepops-registry-mirror.sh)
- [workloads/jenkins/scripts/test-dle-deployment.sh](workloads/jenkins/scripts/test-dle-deployment.sh)
- [workloads/jenkins/scripts/test-monitoring.sh](workloads/jenkins/scripts/test-monitoring.sh)
- [workloads/jenkins/scripts/vagrant-startup.sh](workloads/jenkins/scripts/vagrant-startup.sh)

</details>



This page documents the continuous integration, continuous deployment (CI/CD), and testing framework used in DeepOps. It explains the testing architecture, automated test suites, and how the system validates both Kubernetes and Slurm deployments across different configurations.

For hardware validation procedures, see [Burn-in Testing](#5.2).

## 1. CI/CD Architecture Overview

DeepOps employs Jenkins as its primary CI/CD platform. The system runs multiple test pipelines that validate different deployment configurations and components of the framework.

```mermaid
flowchart TD
    subgraph "CI/CD System Architecture"
        Jenkins["Jenkins Server"]
        
        subgraph "Pipeline Types"
            MainPipeline["Main Pipeline<br>(Jenkinsfile)"]
            NightlyPipeline["Nightly Pipeline<br>(Jenkinsfile-nightly)"]
            MultiNightly["Multi-Node Pipeline<br>(Jenkinsfile-multi-nightly)"]
            MatrixPipeline["Matrix Pipeline<br>(Jenkinsfile-matrix)"]
        end
        
        subgraph "Testing Environment"
            VirtualEnv["Virtual Environment<br>(Vagrant)"]
            TestScripts["Test Scripts<br>(jenkins/scripts)"]
        end
        
        subgraph "Test Categories"
            K8sTests["Kubernetes Tests"]
            SlurmTests["Slurm Tests"]
            GPUTests["GPU Validation Tests"]
            MonitoringTests["Monitoring Tests"]
            NetworkingTests["Networking Tests"]
            StorageTests["Storage Tests"]
        end
    end
    
    Jenkins --> MainPipeline
    Jenkins --> NightlyPipeline
    Jenkins --> MultiNightly
    Jenkins --> MatrixPipeline
    
    MainPipeline --> VirtualEnv
    NightlyPipeline --> VirtualEnv
    MultiNightly --> VirtualEnv
    MatrixPipeline --> VirtualEnv
    
    VirtualEnv --> TestScripts
    TestScripts --> K8sTests
    TestScripts --> SlurmTests
    TestScripts --> GPUTests
    TestScripts --> MonitoringTests
    TestScripts --> NetworkingTests
    TestScripts --> StorageTests
```

Sources: [workloads/jenkins/Jenkinsfile:1-147](), [workloads/jenkins/Jenkinsfile-nightly:1-251](), [workloads/jenkins/Jenkinsfile-multi-nightly:1-251](), [workloads/jenkins/Jenkinsfile-matrix:1-258]()

## 2. Jenkins Pipeline Structure

DeepOps utilizes several Jenkins pipeline configurations to handle different testing scenarios:

### 2.1 Main Pipeline (Jenkinsfile)

The standard pipeline performs basic validation tests on a single-GPU configuration. It tests both Kubernetes and Slurm deployments with default settings.

### 2.2 Nightly Pipeline (Jenkinsfile-nightly)

Runs an extensive test suite nightly with a single GPU:
- Kubernetes deployment with GPU Operator
- Slurm deployment
- All services and add-ons (monitoring, dashboards, etc.)

### 2.3 Multi-Node Nightly Pipeline (Jenkinsfile-multi-nightly)

Similar to the nightly pipeline but uses two GPUs to test multi-node scenarios.

### 2.4 Matrix Pipeline (Jenkinsfile-matrix)

Allows customized test configurations by specifying combinations of:
- Operating systems (Ubuntu/CentOS)
- OS versions (18.04, 20.04, 7, 8)
- Deployment platforms (Kubernetes/Slurm)
- Container managers (containerd/docker)
- Full/single-node installations
- GPU Operator configurations

```mermaid
flowchart LR
    subgraph "Pipeline Variables"
        OS["OS Type<br>centos/ubuntu"]
        OSVersion["OS Version<br>18.04/20.04/7/8"]
        DeployType["Deployment Platform<br>slurm/k8s"]
        GPUOp["GPU Operator<br>true/false"]
        ContainerMgr["Container Manager<br>containerd/docker"]
        Installation["Installation Type<br>single-node/multi-node"]
    end
    
    subgraph "Pipeline Stages"
        Setup["Setup Stage<br>Repository & Environment"]
        Deploy["Deployment Stage<br>K8s or Slurm"]
        Services["Services Stage<br>Deploy Add-ons"]
        Tests["Test Stage<br>Run Validation Tests"]
        Cleanup["Cleanup Stage<br>Tear Down Environment"]
    end
    
    OS --> Setup
    OSVersion --> Setup
    DeployType --> Deploy
    GPUOp --> Deploy
    ContainerMgr --> Deploy
    Installation --> Setup
    
    Setup --> Deploy
    Deploy --> Services
    Services --> Tests
    Tests --> Cleanup
```

Sources: [workloads/jenkins/Jenkinsfile-matrix:9-54](), [workloads/jenkins/Jenkinsfile-matrix:85-224]()

## 3. Test Script Architecture

The testing system utilizes a collection of shell scripts located in `workloads/jenkins/scripts/` that perform specific validation tasks. These scripts share common utilities and environment variables through `jenkins-common.sh`.

```mermaid
flowchart TD
    subgraph "Test Script Architecture"
        JenkinsCommon["jenkins-common.sh<br>(Common Utilities)"]
        
        subgraph "Environment Setup"
            VagrantStartup["vagrant-startup.sh<br>(Create Virtual Environment)"]
            MungeFiles["munge-files.sh<br>(Configure Test Files)"]
        end
        
        subgraph "Kubernetes Tests"
            ClusterUp["test-cluster-up.sh<br>(Deploy K8s)"]
            K8sDebug["get-k8s-debug.sh<br>(Collect K8s Status)"]
            GPUJob["run-gpu-job.sh<br>(Test GPU Workload)"]
            IngressTest["verify-ingress-config.sh"]
            LocalRegistry["test-local-registry.sh"]
            DLExample["test-dle-deployment.sh<br>(ML Workload)"]
        end
        
        subgraph "Slurm Tests"
            SlurmSetup["test-setup-slurm.sh<br>(Deploy Slurm)"]
            SlurmDebug["get-slurm-debug.sh<br>(Collect Slurm Status)"]
            SlurmJob["test-slurm-job.sh<br>(Basic Job)"]
            NFSTest["test-slurm-nfs-mount.sh<br>(Storage)"]
            MPITest["test-mpi-job.sh<br>(MPI)"]
            EnrootTest["test-slurm-enroot-job.sh<br>(Containers)"]
            SlurmGPU["test-slurm-gpu.sh<br>(GPU Access)"]
        end
        
        subgraph "Common Tests"
            Monitoring["test-monitoring.sh<br>(Prometheus/Grafana)"]
            Dashboard["test-dashboard.sh<br>(K8s Dashboard)"]
            DCGMMetrics["test-dcgm-metrics.sh<br>(GPU Metrics)"]
            RSyslogTests["test-rsyslog-k8s.sh/slurm.sh<br>(Log Forwarding)"]
        end
    end
    
    JenkinsCommon --> VagrantStartup
    JenkinsCommon --> MungeFiles
    JenkinsCommon --> ClusterUp
    JenkinsCommon --> SlurmSetup
    JenkinsCommon --> Monitoring
    
    VagrantStartup --> ClusterUp
    VagrantStartup --> SlurmSetup
    
    ClusterUp --> K8sDebug
    ClusterUp --> GPUJob
    ClusterUp --> IngressTest
    ClusterUp --> LocalRegistry
    ClusterUp --> DLExample
    ClusterUp --> Monitoring
    ClusterUp --> Dashboard
    
    SlurmSetup --> SlurmDebug
    SlurmSetup --> SlurmJob
    SlurmSetup --> NFSTest
    SlurmSetup --> MPITest
    SlurmSetup --> EnrootTest
    SlurmSetup --> SlurmGPU
    SlurmSetup --> DCGMMetrics
```

Sources: [workloads/jenkins/scripts/jenkins-common.sh:1-56](), [workloads/jenkins/scripts/vagrant-startup.sh:1-10](), [workloads/jenkins/scripts/test-monitoring.sh:1-149](), [workloads/jenkins/scripts/test-dcgm-metrics.sh:1-48](), [workloads/jenkins/scripts/test-dle-deployment.sh:1-42]()

## 4. Test Categories

The DeepOps CI/CD system validates several critical areas of functionality:

### 4.1 Kubernetes Deployment Tests

Tests that validate the deployment and functionality of Kubernetes clusters:

- Basic cluster deployment and stability
- GPU Operator functionality
- Container runtime validation (containerd/docker)
- GPU accessibility from pods
- Networking components (Ingress)
- Storage systems

### 4.2 Slurm Deployment Tests

Tests focused on validating Slurm HPC clusters:

- Basic cluster deployment and functionality
- Job submission and execution
- GPU accessibility from jobs
- MPI workloads
- Container integration (Enroot)
- NFS mounting and shared storage

### 4.3 Monitoring and Observability Tests

Tests for monitoring infrastructure:

- Prometheus and Grafana deployment
- DCGM metrics for GPU monitoring
- Alert Manager functionality
- Dashboard accessibility
- Log forwarding with rsyslog

The monitoring test suite validates both the deployment of the monitoring stack and the collection of GPU-specific metrics through DCGM.

```
# Example DCGM metrics validated in tests
DCGM_FI_DEV_GPU_TEMP
DCGM_FI_DEV_POWER_USAGE
DCGM_FI_DEV_GPU_UTIL
DCGM_FI_DEV_MEM_COPY_UTIL
DCGM_FI_DEV_MEM_CLOCK
DCGM_FI_DEV_SM_CLOCK
```

Sources: [workloads/jenkins/scripts/test-monitoring.sh:10-148](), [workloads/jenkins/scripts/test-dcgm-metrics.sh:40-48]()

### 4.4 Deep Learning Examples Tests

Tests that deploy and validate Deep Learning Examples:

- Jupyter notebook accessibility
- PyTorch model deployment
- End-to-end ML workflow validation

Sources: [workloads/jenkins/scripts/test-dle-deployment.sh:9-42]()

## 5. Virtual Testing Environment

DeepOps uses Vagrant to create virtual testing environments that simulate multi-node clusters. This provides a consistent, reproducible environment for testing deployments.

### 5.1 Vagrant Configuration

The testing environment typically consists of:

- One management node (for Kubernetes control plane or Slurm controller)
- One or more GPU nodes (with virtual or passthrough GPUs)
- In multi-node tests, additional compute nodes

```mermaid
flowchart TD
    subgraph "Virtual Testing Environment"
        Vagrant["Vagrant Controller"]
        
        subgraph "Single-Node Configuration"
            MGMT01["virtual-mgmt01<br>10.0.0.2X"]
            GPU01["virtual-gpu01<br>10.0.0.6X"]
        end
        
        subgraph "Multi-Node Configuration"
            MGMT01m["virtual-mgmt01<br>10.0.0.2X"]
            MGMT02["virtual-mgmt02<br>10.0.0.3X"]
            MGMT03["virtual-mgmt03<br>10.0.0.4X"]
            GPU01m["virtual-gpu01<br>10.0.0.6X"]
            GPU02["virtual-gpu02<br>10.0.0.7X"]
        end
    end
    
    Vagrant --> MGMT01
    Vagrant --> GPU01
    
    Vagrant --> MGMT01m
    Vagrant --> MGMT02
    Vagrant --> MGMT03
    Vagrant --> GPU01m
    Vagrant --> GPU02
```

Sources: [workloads/jenkins/scripts/vagrant-startup.sh:1-10](), [workloads/jenkins/scripts/jenkins-common.sh:17-42]()

### 5.2 GPU Resource Management

The Jenkins environment locks GPU resources using the `lock` directive to ensure tests have exclusive access to physical GPUs. The number of GPUs allocated depends on the test type:

- Standard tests use 1 GPU
- Multi-node tests use 2 GPUs

```
# Example from Jenkinsfile showing GPU resource locking
lock(resource: null, label: 'gpu', quantity: 1, variable: 'GPUDATA') {
  // Test tasks run here with exclusive GPU access
}
```

Sources: [workloads/jenkins/Jenkinsfile:18-136](), [workloads/jenkins/Jenkinsfile-multi-nightly:23-239]()

## 6. Test Execution Workflow

The typical test workflow follows this sequence:

1. **Environment Setup**
   - Reset repository to clean state
   - Configure test-specific parameters
   - Start Vagrant virtual environment

2. **Deployment**
   - Deploy Kubernetes or Slurm cluster
   - Install required components (GPU drivers, containers)
   - Verify cluster status

3. **Component Testing**
   - Test basic functionality (jobs, pods)
   - Test GPU access
   - Test additional services (NFS, MPI, etc.)

4. **Monitoring Testing**
   - Deploy monitoring stack
   - Verify metrics collection
   - Test dashboard access

5. **Cleanup**
   - Tear down environment
   - Remove test configurations

The diagram below illustrates the full test execution workflow:

```mermaid
sequenceDiagram
    participant Jenkins as "Jenkins Server"
    participant Repo as "DeepOps Repository"
    participant Vagrant as "Vagrant Environment"
    participant K8s as "Kubernetes Cluster"
    participant Slurm as "Slurm Cluster"
    participant Monitor as "Monitoring Stack"
    
    Jenkins->>Repo: Clone repository
    Jenkins->>Repo: Reset to clean state
    Jenkins->>Repo: Munge configuration files
    Jenkins->>Vagrant: Start virtual environment
    
    alt Kubernetes Deployment
        Jenkins->>K8s: Deploy K8s cluster
        Jenkins->>K8s: Install GPU Operator
        Jenkins->>K8s: Verify GPU pods
        Jenkins->>K8s: Test registry & ingress
        Jenkins->>K8s: Deploy DL examples
    else Slurm Deployment
        Jenkins->>Slurm: Deploy Slurm cluster
        Jenkins->>Slurm: Test basic jobs
        Jenkins->>Slurm: Test GPU jobs
        Jenkins->>Slurm: Test MPI & Enroot
        Jenkins->>Slurm: Test NFS mounts
    end
    
    Jenkins->>Monitor: Deploy Prometheus & Grafana
    Jenkins->>Monitor: Verify DCGM metrics
    Jenkins->>Monitor: Test dashboard access
    
    Jenkins->>Vagrant: Tear down environment
```

Sources: [workloads/jenkins/Jenkinsfile-nightly:16-239](), [workloads/jenkins/Jenkinsfile:16-136]()

## 7. Test Matrix Configuration

The matrix pipeline enables testing across multiple configurations by defining a matrix of deployment options:

| Parameter | Available Options |
|-----------|------------------|
| OS Type | ubuntu, centos |
| OS Version | 18.04, 20.04, 7, 8 |
| Deployment | k8s, slurm |
| Container Manager | containerd, docker |
| GPU Operator | true, false |
| Installation Type | single-node, multi-node |

Each combination is tested independently, providing comprehensive coverage of deployment scenarios.

Sources: [workloads/jenkins/Jenkinsfile-matrix:12-54]()

## 8. Adding New Tests

To add new tests to the CI/CD system:

1. Create a new test script in `workloads/jenkins/scripts/`
2. Source the `jenkins-common.sh` file for common utilities
3. Add the test to the appropriate Jenkins pipeline file
4. Use timeouts to prevent hanging tests
5. Include proper error handling and debugging output

Tests should be modular, focusing on validating specific functionality with clear success/failure criteria.

---

