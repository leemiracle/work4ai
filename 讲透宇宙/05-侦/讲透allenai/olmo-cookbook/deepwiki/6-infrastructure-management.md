<!-- source: DeepWiki mcp.deepwiki.com · repo allenai/olmo-cookbook · page 6 Infrastructure Management · fetched 2026-10-26 -->

# Infrastructure Management

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [src/cookbook/cli/pmr.py](src/cookbook/cli/pmr.py)

</details>



This document covers the infrastructure management system provided by the `poormanray` CLI, which enables distributed computing by managing fleets of EC2 instances. The system provides a simplified alternative to Ray for distributed data processing, with built-in support for various data processing toolkits.

For information about training configuration and orchestration, see [Training System](#5). For evaluation execution environments, see [Evaluation System](#4).

## Overview

The infrastructure management system, implemented primarily in [src/cookbook/cli/pmr.py:1-2070](), provides comprehensive EC2 instance lifecycle management through the `poormanray` CLI. This system enables users to create, configure, and manage clusters of EC2 instances for distributed processing tasks, with special support for AI/ML workloads.

```mermaid
graph TB
    subgraph "poormanray CLI Commands"
        CREATE["create<br/>Creates EC2 instances"]
        LIST["list<br/>Lists instances"]
        TERMINATE["terminate<br/>Terminates instances"]
        RUN["run<br/>Executes commands"]
        MAP["map<br/>Distributes scripts"]
        SETUP["setup<br/>Configures AWS credentials"]
    end
    
    subgraph "Core Classes"
        INSTANCEINFO["InstanceInfo<br/>EC2 instance representation"]
        SESSION["Session<br/>SSH connection management"]
        CLIENTUTILS["ClientUtils<br/>AWS client utilities"]
    end
    
    subgraph "AWS Infrastructure"
        EC2["EC2 Instances"]
        SSM["Systems Manager"]
        AMI["Amazon Machine Images"]
    end
    
    CREATE --> INSTANCEINFO
    LIST --> INSTANCEINFO
    TERMINATE --> INSTANCEINFO
    RUN --> SESSION
    MAP --> SESSION
    
    INSTANCEINFO --> EC2
    SESSION --> EC2
    CLIENTUTILS --> SSM
    CLIENTUTILS --> AMI
```

**Sources:** [src/cookbook/cli/pmr.py:1-81](), [src/cookbook/cli/pmr.py:2055-2066]()

## Core Data Structures

### InstanceInfo Class

The `InstanceInfo` class serves as the primary representation of EC2 instances throughout the system:

```mermaid
classDiagram
    class InstanceInfo {
        +str instance_id
        +str instance_type
        +str image_id
        +InstanceStatus state
        +str public_ip_address
        +str name
        +dict tags
        +str region
        +datetime created_at
        +from_instance() InstanceInfo
        +describe_instances() List[InstanceInfo]
        +create_instance() InstanceInfo
        +terminate() bool
        +pause() bool
        +resume() bool
    }
    
    class InstanceStatus {
        <<enumeration>>
        PENDING
        RUNNING
        SHUTTING_DOWN
        TERMINATED
        STOPPING
        STOPPED
        +active() List[InstanceStatus]
        +unterminated() List[InstanceStatus]
    }
    
    class Session {
        +str instance_id
        +str private_key_path
        +str user
        +InstanceInfo instance
        +connect() SSHClient
        +run() SessionContent
        +run_in_screen() SessionContent
    }
    
    InstanceInfo --> InstanceStatus
    Session --> InstanceInfo
```

**Sources:** [src/cookbook/cli/pmr.py:415-876](), [src/cookbook/cli/pmr.py:357-376](), [src/cookbook/cli/pmr.py:879-1019]()

### Instance Management Operations

The system provides comprehensive instance lifecycle management through a set of class methods and CLI commands:

| Operation | Method | CLI Command | Purpose |
|-----------|--------|-------------|---------|
| Creation | `InstanceInfo.create_instance()` | `create` | Launch new instances with specified configurations |
| Discovery | `InstanceInfo.describe_instances()` | `list` | Query and filter existing instances |
| Termination | `instance.terminate()` | `terminate` | Permanently destroy instances |
| Pause | `instance.pause()` | `pause` | Stop instances (preserving state) |
| Resume | `instance.resume()` | `resume` | Restart stopped instances |

**Sources:** [src/cookbook/cli/pmr.py:769-876](), [src/cookbook/cli/pmr.py:536-746]()

## SSH Session Management

The `Session` class provides SSH-based command execution capabilities with support for both interactive and detached execution modes:

```mermaid
graph LR
    subgraph "Session Execution Modes"
        SINGLE["run_single()<br/>Direct SSH execution"]
        SCREEN["run_in_screen()<br/>Screen session execution"]
    end
    
    subgraph "Command Types"
        COMMAND["Direct Commands<br/>String commands"]
        SCRIPT["Script Files<br/>Base64 encoded transfer"]
    end
    
    subgraph "Execution Context"
        ATTACHED["Attached Mode<br/>Real-time output"]
        DETACHED["Detached Mode<br/>Background execution"]
    end
    
    COMMAND --> SINGLE
    COMMAND --> SCREEN
    SCRIPT --> SINGLE
    SCRIPT --> SCREEN
    
    SINGLE --> ATTACHED
    SCREEN --> ATTACHED
    SCREEN --> DETACHED
```

**Sources:** [src/cookbook/cli/pmr.py:920-1018](), [src/cookbook/cli/pmr.py:1108-1136]()

## Toolkit Installation Systems

The infrastructure management system includes built-in support for several specialized toolkits:

### Setup Scripts and Installation

```mermaid
graph TB
    subgraph "Toolkit Setup Scripts"
        D2TK["D2TK_SETUP<br/>Dolma2 toolkit installation"]
        DOLMA_PYTHON["DOLMA_PYTHON_SETUP<br/>Python environment setup"]
        DECON["make_decon_python_setup()<br/>DECON toolkit with PMR variables"]
    end
    
    subgraph "Setup Commands"
        SETUP_D2TK["setup-d2tk<br/>Install Dolma2 toolkit"]
        SETUP_DOLMA["setup-dolma-python<br/>Setup Python environment"]
        SETUP_DECON["setup-decon<br/>Install DECON toolkit"]
    end
    
    subgraph "Installation Components"
        RAID["RAID Configuration<br/>Instance store setup"]
        PYTHON["Python 3.12<br/>Package management"]
        TOOLS["Development Tools<br/>gcc, cmake, rust"]
        S5CMD["s5cmd<br/>S3 transfer tool"]
    end
    
    D2TK --> SETUP_D2TK
    DOLMA_PYTHON --> SETUP_DOLMA
    DECON --> SETUP_DECON
    
    SETUP_D2TK --> RAID
    SETUP_D2TK --> TOOLS
    SETUP_DOLMA --> PYTHON
    SETUP_DOLMA --> S5CMD
    SETUP_DECON --> PYTHON
    SETUP_DECON --> TOOLS
```

**Sources:** [src/cookbook/cli/pmr.py:168-330](), [src/cookbook/cli/pmr.py:1719-1921]()

### DECON Environment Setup

The DECON setup includes special handling for distributed processing environments:

```python
# PMR environment variables are automatically set for distributed processing
PMR_HOST_INDEX={host_index}
PMR_HOST_COUNT={host_count}
```

**Sources:** [src/cookbook/cli/pmr.py:239-258](), [src/cookbook/cli/pmr.py:1839-1921]()

## Distributed Script Execution

The `map` command provides sophisticated script distribution capabilities across instance fleets:

```mermaid
sequenceDiagram
    participant CLI as "map command"
    participant INSTANCES as "Instance Fleet"
    participant SCRIPTS as "Script Collection"
    
    CLI->>INSTANCES: Query available instances
    CLI->>SCRIPTS: Load and shuffle scripts
    CLI->>CLI: Calculate distribution ratio
    
    loop For each instance
        CLI->>INSTANCES: Create job UUID directory
        CLI->>INSTANCES: Transfer assigned scripts (base64)
        CLI->>INSTANCES: Generate run_all.sh script
    end
    
    loop For each instance
        CLI->>INSTANCES: Execute run_all.sh in detached mode
    end
    
    Note over INSTANCES: Scripts execute in parallel across fleet
```

**Sources:** [src/cookbook/cli/pmr.py:1923-2053]()

### Script Distribution Algorithm

The system uses a proportional distribution algorithm to evenly spread scripts across instances:

```python
ratio = len(script) / len(instances)
start_idx = round(ratio * i)
end_idx = round(ratio * (i + 1))
instance_scripts = script[start_idx:end_idx]
```

**Sources:** [src/cookbook/cli/pmr.py:1980-1985]()

## AWS Integration

The infrastructure management system integrates deeply with AWS services through boto3 clients:

```mermaid
graph LR
    subgraph "Client Management"
        CLIENTUTILS["ClientUtils"]
        EC2CLIENT["EC2Client"]
        SSMCLIENT["SSMClient"]
    end
    
    subgraph "AWS Services"
        EC2SERVICE["EC2 Service<br/>Instance management"]
        SSMSERVICE["SSM Service<br/>Parameter store"]
        AMI_LOOKUP["AMI Lookup<br/>Latest Amazon Linux"]
    end
    
    subgraph "Resource Management"
        VPC["VPC Discovery"]
        KEYPAIRS["Key Pair Management"]
        SECURITY["Security Groups"]
    end
    
    CLIENTUTILS --> EC2CLIENT
    CLIENTUTILS --> SSMCLIENT
    EC2CLIENT --> EC2SERVICE
    SSMCLIENT --> SSMSERVICE
    SSMCLIENT --> AMI_LOOKUP
    
    EC2SERVICE --> VPC
    EC2SERVICE --> KEYPAIRS
    EC2SERVICE --> SECURITY
```

**Sources:** [src/cookbook/cli/pmr.py:333-354](), [src/cookbook/cli/pmr.py:748-767](), [src/cookbook/cli/pmr.py:1021-1106]()

## CLI Command Structure

The poormanray CLI follows a consistent pattern with common options across all commands:

```mermaid
graph TB
    subgraph "Common CLI Options"
        NAME["--name<br/>Cluster identifier"]
        REGION["--region<br/>AWS region"]
        INSTANCE_TYPE["--instance-type<br/>EC2 instance type"]
        SSH_KEY["--ssh-key-path<br/>SSH authentication"]
        DETACH["--detach<br/>Background execution"]
    end
    
    subgraph "Instance Lifecycle Commands"
        CREATE_CMD["create<br/>Launch instances"]
        LIST_CMD["list<br/>Query instances"]
        PAUSE_CMD["pause<br/>Stop instances"]
        RESUME_CMD["resume<br/>Start instances"]
        TERMINATE_CMD["terminate<br/>Destroy instances"]
    end
    
    subgraph "Execution Commands"
        RUN_CMD["run<br/>Execute commands"]
        MAP_CMD["map<br/>Distribute scripts"]
        SETUP_CMD["setup<br/>Configure credentials"]
    end
    
    NAME --> CREATE_CMD
    NAME --> LIST_CMD
    NAME --> RUN_CMD
    NAME --> MAP_CMD
    REGION --> CREATE_CMD
    REGION --> LIST_CMD
    SSH_KEY --> RUN_CMD
    SSH_KEY --> MAP_CMD
```

**Sources:** [src/cookbook/cli/pmr.py:1143-1251](), [src/cookbook/cli/pmr.py:2055-2066]()

The system uses a decorator pattern to apply common options across commands, ensuring consistency and reducing code duplication through the `common_cli_options` function.

**Sources:** [src/cookbook/cli/pmr.py:1146-1251]()

---

