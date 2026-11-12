<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/cuda-q-academic · page 1 Overview · fetched 2026-10-26 -->

# Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [Guide-to-cuda-q-backends.ipynb](Guide-to-cuda-q-backends.ipynb)
- [README.md](README.md)
- [Sample-Syllabus.md](Sample-Syllabus.md)
- [qaoa-for-max-cut/00_StartHere.ipynb](qaoa-for-max-cut/00_StartHere.ipynb)

</details>



This document provides a comprehensive overview of the CUDA-Q Academic repository, which serves as NVIDIA's educational platform for quantum computing training. The repository contains interactive Jupyter notebooks and supporting materials designed to prepare quantum computing professionals by combining high-performance computing with quantum computing skills, developed in collaboration with universities and tested in real classroom settings.

For specific implementation details of individual modules, see [Quick Start to Quantum Computing](#2), [Quantum Algorithms](#3), [QAOA](#4), [Quantum Error Correction](#5), and [Quantum Applications to Finance](#6). For technical documentation of the underlying CUDA-Q framework, see [CUDA-Q Programming Framework](#7).

## Repository Architecture

CUDA-Q Academic follows a modular educational architecture with clear progression paths and technical infrastructure supporting multiple deployment options.

### Educational Module Structure

```mermaid
graph TB
    subgraph "Foundation Layer"
        QS["quick-start-to-quantum/"]
        QS_LAB1["Lab 1: Single Qubits"]
        QS_LAB2["Lab 2: Multi-Qubits"] 
        QS_LAB3["Lab 3: Variational Programs"]
        QS_LAB4["Lab 4: Hybrid Programs"]
    end
    
    subgraph "Application Layer"
        QIS["qis-examples/"]
        QAOA["qaoa-for-max-cut/"]
        QEC["qec101/"]
        FIN["quantum-applications-to-finance/"]
    end
    
    subgraph "Supporting Infrastructure"
        GUIDE["Guide-to-cuda-q-backends.ipynb"]
        SYLLABUS["Sample-Syllabus.md"]
        WIDGETS["widgets/"]
        REQ["requirements.txt"]
        DOCKER["Dockerfile"]
    end
    
    QS --> QS_LAB1
    QS --> QS_LAB2  
    QS --> QS_LAB3
    QS --> QS_LAB4
    
    QS_LAB4 --> QIS
    QS_LAB4 --> QAOA
    QS_LAB3 --> QEC
    QS_LAB3 --> FIN
    
    GUIDE --> QS
    GUIDE --> QAOA
    SYLLABUS --> QS
    WIDGETS --> QS
    REQ --> QS
    DOCKER --> QAOA
```

Sources: [README.md:1-51](), [Sample-Syllabus.md:1-67]()

### Learning Progression Flow

```mermaid
graph TD
    subgraph "Prerequisites"
        PYTHON["Python Programming"]
        JUPYTER["Jupyter Notebooks"]
        MATH["Complex Numbers, Linear Algebra, Statistics"]
    end
    
    subgraph "Core CUDA-Q Concepts"
        KERNEL["@cudaq.kernel decorator"]
        SAMPLE["cudaq.sample()"]
        OBSERVE["cudaq.observe()"]
        TARGETS["Backend Targets"]
    end
    
    subgraph "Quantum Fundamentals"
        QUBITS["Single & Multi-Qubits"]
        GATES["Quantum Gates"]
        ENTANGLE["Entanglement"]
        MEASURE["Measurement"]
    end
    
    subgraph "Advanced Applications"
        VQE["Variational Quantum Eigensolver"]
        QAOA_ALG["QAOA Algorithm"]
        QEC_CODES["Error Correction Codes"]
        FINANCE_APPS["Financial Applications"]
    end
    
    PYTHON --> KERNEL
    JUPYTER --> KERNEL
    MATH --> QUBITS
    
    KERNEL --> SAMPLE
    KERNEL --> OBSERVE
    KERNEL --> TARGETS
    
    SAMPLE --> QUBITS
    OBSERVE --> GATES
    TARGETS --> ENTANGLE
    
    QUBITS --> VQE
    GATES --> QAOA_ALG
    ENTANGLE --> QEC_CODES
    MEASURE --> FINANCE_APPS
```

Sources: [README.md:20-21](), [README.md:26-28](), [README.md:35-37](), [README.md:49-50]()

## Technical Framework Integration

The repository leverages the CUDA-Q programming model to provide a unified interface from educational concepts to high-performance quantum computing backends.

### CUDA-Q Programming Model

```mermaid
graph TB
    subgraph "Educational Interface"
        NOTEBOOKS["Jupyter Notebooks"]
        EXERCISES["Interactive Exercises"]
        VISUALIZATIONS["Quantum State Visualizations"]
    end
    
    subgraph "CUDA-Q Core"
        KERNEL_DEC["@cudaq.kernel"]
        QVECTOR["cudaq.qvector()"]
        GATES_API["h(), x(), cnot(), etc."]
        SAMPLE_API["cudaq.sample()"]
        OBSERVE_API["cudaq.observe()"]
        SPIN_OPS["cudaq.spin operators"]
    end
    
    subgraph "Backend Targets"
        QPP_CPU["qpp-cpu"]
        NVIDIA_GPU["nvidia"]
        NVIDIA_MQPU["nvidia-mqpu"]
        REMOTE_MQPU["remote-mqpu"]
    end
    
    subgraph "Hardware Acceleration"
        CUSTATEVEC["cuStateVec"]
        CUTENSOR["cuTensor"]
        CUTENSORNET["cuTensorNet"]
        MPI["MPI Distribution"]
    end
    
    NOTEBOOKS --> KERNEL_DEC
    EXERCISES --> QVECTOR
    VISUALIZATIONS --> GATES_API
    
    KERNEL_DEC --> SAMPLE_API
    QVECTOR --> OBSERVE_API
    GATES_API --> SPIN_OPS
    
    SAMPLE_API --> QPP_CPU
    OBSERVE_API --> NVIDIA_GPU
    SPIN_OPS --> NVIDIA_MQPU
    KERNEL_DEC --> REMOTE_MQPU
    
    NVIDIA_GPU --> CUSTATEVEC
    NVIDIA_MQPU --> CUTENSOR
    REMOTE_MQPU --> CUTENSORNET
    NVIDIA_MQPU --> MPI
```

Sources: [Guide-to-cuda-q-backends.ipynb:88-129](), [Guide-to-cuda-q-backends.ipynb:200-235]()

## Core Educational Modules

### Module Classification by Complexity

| Module | Prerequisites | Hardware Requirements | Key CUDA-Q Features |
|--------|--------------|----------------------|-------------------|
| `quick-start-to-quantum/` | Python, Math basics | CPU | `@cudaq.kernel`, `cudaq.sample()` |
| `qis-examples/` | Quick Start completion | CPU | `cudaq.observe()`, Hamiltonian construction |
| `qaoa-for-max-cut/` | Quick Start, NetworkX | GPU recommended | `cudaq.vqe()`, optimization |
| `qec101/` | Quick Start completion | CPU | Noise models, error mitigation |
| `quantum-applications-to-finance/` | Quick Start completion | CPU | Quantum walks, financial modeling |

Sources: [README.md:17-51](), [qaoa-for-max-cut/00_StartHere.ipynb:60-62]()

### Backend Configuration Options

```mermaid
graph LR
    subgraph "Single Processor"
        CPU_SIM["cudaq.set_target('qpp-cpu')"]
        GPU_SIM["cudaq.set_target('nvidia')"]
        GPU_FP64["cudaq.set_target('nvidia', option='fp64')"]
    end
    
    subgraph "Multi-Processor"
        MGPU["cudaq.set_target('nvidia', option='mgpu')"]
        MQPU["cudaq.set_target('nvidia-mqpu')"]
        REMOTE["cudaq.set_target('remote-mqpu')"]
    end
    
    subgraph "Execution Patterns"
        SAMPLING["Circuit Sampling"]
        HAM_BATCH["Hamiltonian Batching"]
        CIRCUIT_CUT["Circuit Cutting"]
    end
    
    CPU_SIM --> SAMPLING
    GPU_SIM --> SAMPLING
    GPU_FP64 --> HAM_BATCH
    
    MGPU --> CIRCUIT_CUT
    MQPU --> HAM_BATCH
    REMOTE --> CIRCUIT_CUT
```

Sources: [Guide-to-cuda-q-backends.ipynb:242-257](), [Guide-to-cuda-q-backends.ipynb:328-370]()

## Deployment Architecture

The repository supports multiple deployment strategies to accommodate different educational environments and resource constraints.

### Platform Integration Options

```mermaid
graph TB
    subgraph "Local Development"
        DOCKER_LOCAL["Docker + requirements.txt"]
        CONDA_ENV["Conda Environment"]
        PIP_INSTALL["pip install cuda-quantum"]
    end
    
    subgraph "Cloud Platforms"
        QBRAID["qBraid Lab"]
        COCALC["CoCalc"]
        COLAB["Google Colab"]
    end
    
    subgraph "Institutional"
        HPC_CLUSTERS["HPC Clusters"]
        GPU_NODES["GPU Compute Nodes"]
        MPI_ENV["MPI Environments"]
    end
    
    subgraph "Content Access"
        JUPYTER_NB["Jupyter Notebooks"]
        INTERACTIVE_WIDGETS["Interactive Widgets"]
        ASSESSMENT_TOOLS["Assessment Materials"]
    end
    
    DOCKER_LOCAL --> JUPYTER_NB
    CONDA_ENV --> JUPYTER_NB
    PIP_INSTALL --> JUPYTER_NB
    
    QBRAID --> INTERACTIVE_WIDGETS
    COCALC --> INTERACTIVE_WIDGETS
    COLAB --> INTERACTIVE_WIDGETS
    
    HPC_CLUSTERS --> ASSESSMENT_TOOLS
    GPU_NODES --> ASSESSMENT_TOOLS
    MPI_ENV --> ASSESSMENT_TOOLS
    
    JUPYTER_NB --> ASSESSMENT_TOOLS
    INTERACTIVE_WIDGETS --> ASSESSMENT_TOOLS
```

Sources: [README.md:6-7](), [qaoa-for-max-cut/00_StartHere.ipynb:85-87](), [qaoa-for-max-cut/00_StartHere.ipynb:134-135]()

### Resource Requirements by Module

```mermaid
graph TD
    subgraph "CPU-Only Modules"
        QS_CPU["quick-start-to-quantum/"]
        QIS_CPU["qis-examples/"]  
        QEC_BASIC["qec101/ (basic concepts)"]
        FIN_BASIC["quantum-applications-to-finance/ (intro)"]
    end
    
    subgraph "GPU-Recommended"
        QAOA_GPU["qaoa-for-max-cut/ (Labs 2-3)"]
        QEC_NOISE["qec101/ (noisy simulation)"]
        FIN_ADV["quantum-applications-to-finance/ (advanced)"]
    end
    
    subgraph "Multi-GPU/HPC"
        QAOA_DIST["qaoa-for-max-cut/ (distributed)"]
        QAOA_ASSESS["qaoa-for-max-cut/ (Lab 4 assessment)"]
    end
    
    QS_CPU --> QAOA_GPU
    QIS_CPU --> QEC_NOISE
    QEC_BASIC --> QEC_NOISE
    FIN_BASIC --> FIN_ADV
    
    QAOA_GPU --> QAOA_DIST
    QAOA_GPU --> QAOA_ASSESS
```

Sources: [qaoa-for-max-cut/00_StartHere.ipynb:124-135](), [README.md:31-51]()

## Educational Standards Alignment

CUDA-Q Academic aligns with established quantum computing educational frameworks and competency standards.

### Curriculum Integration Framework

```mermaid
graph LR
    subgraph "Educational Standards"
        QIS_PATHWAYS["QIS Learning Pathways"]
        EU_FRAMEWORK["European QT Competence Framework"]
        HPC_COMPETENCIES["HPC Competencies"]
        TEXTBOOK_ALIGN["Textbook Alignment"]
    end
    
    subgraph "CUDA-Q Academic Content"
        SAMPLE_SYLLABUS["Sample-Syllabus.md"]
        MODULE_STRUCTURE["Modular Learning Path"]
        ASSESSMENT_MATERIALS["Assessment Exercises"]
        PRACTICAL_EXAMPLES["Hands-on Examples"]
    end
    
    subgraph "Implementation Tools"
        JUPYTER_INTEGRATION["Jupyter Notebook Integration"]
        VISUALIZATION_TOOLS["Interactive Visualizations"]
        BACKEND_FLEXIBILITY["Multiple Backend Support"]
        HYBRID_PROGRAMMING["Quantum-Classical Hybrid Examples"]
    end
    
    QIS_PATHWAYS --> SAMPLE_SYLLABUS
    EU_FRAMEWORK --> MODULE_STRUCTURE
    HPC_COMPETENCIES --> ASSESSMENT_MATERIALS
    TEXTBOOK_ALIGN --> PRACTICAL_EXAMPLES
    
    SAMPLE_SYLLABUS --> JUPYTER_INTEGRATION
    MODULE_STRUCTURE --> VISUALIZATION_TOOLS
    ASSESSMENT_MATERIALS --> BACKEND_FLEXIBILITY
    PRACTICAL_EXAMPLES --> HYBRID_PROGRAMMING
```

Sources: [Sample-Syllabus.md:14-18](), [Sample-Syllabus.md:21-67]()

This overview establishes the foundation for understanding CUDA-Q Academic's role as a comprehensive quantum computing education platform. For detailed information about specific modules and their implementations, refer to the respective sections listed at the beginning of this document.

---

