<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/cuda-q-academic · page 2 Quick Start to Quantum Computing · fetched 2026-10-26 -->

# Quick Start to Quantum Computing

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [qec101/01_QEC_Intro.ipynb](qec101/01_QEC_Intro.ipynb)
- [quick-start-to-quantum/01_quick_start_to_quantum.ipynb](quick-start-to-quantum/01_quick_start_to_quantum.ipynb)
- [quick-start-to-quantum/02_quick_start_to_quantum.ipynb](quick-start-to-quantum/02_quick_start_to_quantum.ipynb)

</details>



## Purpose and Scope

This document covers the foundational quantum computing module within CUDA-Q Academic, designed to introduce learners to quantum programming concepts using NVIDIA's CUDA-Q platform. The module provides hands-on experience with quantum circuits, single and multi-qubit operations, and the CUDA-Q programming framework through interactive Jupyter notebooks.

For quantum error correction concepts, see [Quantum Error Correction](#5). For advanced quantum algorithms, see [Quantum Algorithms](#3) and [QAOA](#4). For quantum applications in finance, see [Quantum Applications to Finance](#6).

## Module Structure and Learning Progression

The Quick Start module follows a structured three-step quantum programming template across two comprehensive labs:

```mermaid
graph TD
    Start["Learning Journey"] --> Lab1["Lab 1: Single Qubits"]
    Lab1 --> Lab2["Lab 2: Multi-Qubits & Entanglement"]
    Lab2 --> Advanced["Advanced Modules"]
    
    Lab1 --> Encode1["Encode Information"]
    Lab1 --> Manipulate1["Manipulate States"]
    Lab1 --> Extract1["Extract Information"]
    
    Lab2 --> Encode2["Multi-Qubit Encoding"]
    Lab2 --> Manipulate2["Entanglement & CNOT"]
    Lab2 --> Extract2["Statevector Analysis"]
    
    Advanced --> QEC["QEC 101"]
    Advanced --> Algorithms["Quantum Algorithms"]
    Advanced --> Finance["Finance Applications"]
```

**Diagram: Quick Start Module Learning Progression**

Sources: [quick-start-to-quantum/01_quick_start_to_quantum.ipynb:40-68](), [quick-start-to-quantum/02_quick_start_to_quantum.ipynb:40-80]()

## CUDA-Q Programming Framework

### Core Programming Constructs

The module introduces essential CUDA-Q programming patterns through practical implementation:

```mermaid
graph TB
    subgraph "CUDA-Q Core Components"
        Kernel["@cudaq.kernel decorator"]
        QVector["cudaq.qvector initialization"]
        QBit["cudaq.qubit individual qubits"]
        Gates["Quantum Gates"]
        State["State Extraction"]
    end
    
    subgraph "Quantum Gates"
        X["x gate (bit flip)"]
        H["h gate (Hadamard)"]
        Y["y gate"]
        Z["z gate"]
        CNOT["x.ctrl (CNOT)"]
    end
    
    subgraph "State Operations"
        GetState["get_state()"]
        Sample["sample()"]
        Amplitudes["get_state.amplitudes()"]
    end
    
    Kernel --> QVector
    Kernel --> QBit
    QVector --> Gates
    QBit --> Gates
    Gates --> State
    State --> GetState
    State --> Sample
    State --> Amplitudes
```

**Diagram: CUDA-Q Programming Framework Architecture**

Sources: [quick-start-to-quantum/01_quick_start_to_quantum.ipynb:60-67](), [quick-start-to-quantum/02_quick_start_to_quantum.ipynb:74-79]()

### Kernel Definition and Usage

The foundational programming pattern uses the `@cudaq.kernel` decorator:

| Component | Syntax | Purpose |
|-----------|--------|---------|
| Kernel Declaration | `@cudaq.kernel` | Defines quantum program entry point |
| Qubit Allocation | `cudaq.qvector(n)` | Creates n-qubit register |
| Single Qubit | `cudaq.qubit` | Individual qubit parameter |
| Gate Application | `x(qubit)`, `h(qubit)` | Applies quantum operations |
| State Extraction | `cudaq.get_state(kernel)` | Retrieves quantum state |
| Measurement | `cudaq.sample(kernel, shots_count=n)` | Performs measurements |

Sources: [quick-start-to-quantum/01_quick_start_to_quantum.ipynb:324-327](), [quick-start-to-quantum/02_quick_start_to_quantum.ipynb:263-281]()

## Lab 1: Single Qubit Operations

### Quantum State Representation

Lab 1 establishes the fundamental concepts of quantum state representation using the Bloch sphere visualization and mathematical notation:

```mermaid
graph LR
    subgraph "Classical Bits"
        CB0["Bit: 0"]
        CB1["Bit: 1"]
        Vector0["Vector: Up"]
        Vector1["Vector: Down"]
    end
    
    subgraph "Quantum Qubits"
        QB["Qubit: |ψ⟩"]
        Alpha["α|0⟩ + β|1⟩"]
        Bloch["Bloch Sphere"]
        Infinite["Infinite States"]
    end
    
    subgraph "CUDA-Q Implementation"
        Kernel["@cudaq.kernel"]
        QVector["cudaq.qvector(c)"]
        MinusState["minus_state()"]
        Visualization["add_to_bloch_sphere()"]
    end
    
    CB0 --> Vector0
    CB1 --> Vector1
    QB --> Alpha
    Alpha --> Bloch
    Bloch --> Infinite
    
    QB --> Kernel
    Kernel --> QVector
    Kernel --> MinusState
    Bloch --> Visualization
```

**Diagram: Classical vs Quantum State Representation in CUDA-Q**

Sources: [quick-start-to-quantum/01_quick_start_to_quantum.ipynb:163-198](), [quick-start-to-quantum/01_quick_start_to_quantum.ipynb:315-327]()

### Interactive Visualization System

The module incorporates interactive widgets for enhanced learning:

```mermaid
graph TD
    subgraph "Visualization Components"
        BlochRotation["bloch_sphere_rotation.py"]
        StateViz["bloch_sphere_state_visualization.py"]
        Interactive["Interactive Widgets"]
    end
    
    subgraph "Widget Functions"
        CreateWidget["create_rotation_widget()"]
        StateWidget["create_state_widget()"]
        Display["display(widget)"]
    end
    
    subgraph "Mathematical Representation"
        Theta["θ parameter"]
        Phi["φ parameter"]
        Amplitudes["cos(θ/2)|0⟩ + sin(θ/2)e^{iφ}|1⟩"]
    end
    
    BlochRotation --> CreateWidget
    StateViz --> StateWidget
    CreateWidget --> Display
    StateWidget --> Display
    
    Theta --> Amplitudes
    Phi --> Amplitudes
    Interactive --> Amplitudes
```

**Diagram: Interactive Visualization System Architecture**

Sources: [quick-start-to-quantum/01_quick_start_to_quantum.ipynb:210-217](), [quick-start-to-quantum/01_quick_start_to_quantum.ipynb:257-265]()

## Lab 2: Multi-Qubit Systems and Entanglement

### Computational Basis States

Lab 2 introduces multi-qubit systems using computational basis state notation:

| System Size | Basis States | Notation | CUDA-Q Implementation |
|-------------|-------------|----------|----------------------|
| 1 qubit | 2 states | \|0⟩, \|1⟩ | `cudaq.qvector(1)` |
| 2 qubits | 4 states | \|00⟩, \|01⟩, \|10⟩, \|11⟩ | `cudaq.qvector(2)` |
| n qubits | 2^n states | \|b_{n-1}...b_1b_0⟩ | `cudaq.qvector(n)` |

Sources: [quick-start-to-quantum/02_quick_start_to_quantum.ipynb:163-182]()

### Kernel Composition and Subroutines

The module demonstrates advanced programming patterns using kernel composition:

```mermaid
graph TB
    subgraph "Main Kernel"
        MainKernel["nested_quantum_program(num_qubits: int)"]
        QVectorAlloc["qvector = cudaq.qvector(num_qubits)"]
    end
    
    subgraph "Subroutine Kernels"
        MinusKernel["minus(qubit: cudaq.qubit)"]
        XGateKernel["xgate(qubits: cudaq.qvector)"]
        InitializeKernel["initialize(qubits: cudaq.qview, state: list[int])"]
    end
    
    subgraph "Gate Operations"
        XGate["x(qubit)"]
        HGate["h(qubit)"]
        CtrlGate["x.ctrl(control, target)"]
    end
    
    MainKernel --> QVectorAlloc
    QVectorAlloc --> MinusKernel
    QVectorAlloc --> XGateKernel
    MinusKernel --> XGate
    MinusKernel --> HGate
    XGateKernel --> XGate
    InitializeKernel --> CtrlGate
```

**Diagram: Kernel Composition Architecture**

Sources: [quick-start-to-quantum/02_quick_start_to_quantum.ipynb:396-441](), [quick-start-to-quantum/02_quick_start_to_quantum.ipynb:709-731]()

### CNOT Gate Implementation

Multi-qubit entangling operations use the controlled-X (CNOT) gate:

```mermaid
graph LR
    subgraph "CNOT Gate Syntax"
        SingleCtrl["x.ctrl(control_qubit, target_qubit)"]
        MultiCtrl["x.ctrl(control_qubits_list, target_qubit)"]
    end
    
    subgraph "Circuit Representation"
        ControlQubit["Control: ●"]
        TargetQubit["Target: ⊕"]
        Wire["Connecting Wire"]
    end
    
    subgraph "Implementation Example"
        ApplyCNOT["apply_cnot(control: cudaq.qubit, target: cudaq.qubit)"]
        XCtrl["x.ctrl(control, target)"]
    end
    
    SingleCtrl --> ControlQubit
    MultiCtrl --> ControlQubit
    ControlQubit --> TargetQubit
    TargetQubit --> Wire
    
    ApplyCNOT --> XCtrl
    XCtrl --> SingleCtrl
```

**Diagram: CNOT Gate Implementation and Syntax**

Sources: [quick-start-to-quantum/02_quick_start_to_quantum.ipynb:680-713](), [quick-start-to-quantum/02_quick_start_to_quantum.ipynb:709-737]()

## State Extraction and Analysis

### Statevector Operations

The module provides comprehensive state analysis capabilities:

```mermaid
graph TD
    subgraph "State Extraction Methods"
        GetState["cudaq.get_state(kernel)"]
        Sample["cudaq.sample(kernel, shots_count=n)"]
        Amplitudes["state.amplitudes([[1,0], [1,1]])"]
    end
    
    subgraph "State Representation"
        Vector["Statevector Array"]
        Coefficients["Complex Amplitudes"]
        Probabilities["|amplitude|² = probability"]
    end
    
    subgraph "Analysis Functions"
        MostProbable["result.most_probable()"]
        Distribution["Quasi-probability Distribution"]
        Precision["np.round(amplitudes, precision)"]
    end
    
    GetState --> Vector
    Vector --> Coefficients
    Coefficients --> Probabilities
    
    Sample --> Distribution
    Distribution --> MostProbable
    
    GetState --> Amplitudes
    Amplitudes --> Precision
```

**Diagram: State Extraction and Analysis Framework**

Sources: [quick-start-to-quantum/01_quick_start_to_quantum.ipynb:312-322](), [quick-start-to-quantum/02_quick_start_to_quantum.ipynb:294-322]()

## Installation and Environment Setup

### Required Dependencies

The module requires several Python packages for full functionality:

| Package | Purpose | Installation |
|---------|---------|--------------|
| `cudaq` | CUDA-Q quantum programming | `pip install cudaq` |
| `qutip` | Quantum toolbox utilities | `pip install qutip>=5` |
| `ipywidgets` | Interactive notebook widgets | `pip install ipywidgets` |
| `matplotlib` | Plotting and visualization | `pip install matplotlib>=3.5` |
| `numpy` | Numerical computing | Standard with most Python distributions |

Sources: [quick-start-to-quantum/01_quick_start_to_quantum.ipynb:99-119](), [quick-start-to-quantum/02_quick_start_to_quantum.ipynb:107-113]()

### Platform Compatibility

The notebooks support multiple deployment platforms:

```mermaid
graph LR
    subgraph "Deployment Options"
        GoogleColab["Google Colab"]
        JupyterLocal["Local Jupyter"]
        VSCode["VSCode Jupyter"]
    end
    
    subgraph "Setup Requirements"
        CPURuntime["CPU Runtime"]
        KernelRestart["Kernel Restart After Install"]
        PackageInstall["Package Installation"]
    end
    
    GoogleColab --> CPURuntime
    JupyterLocal --> PackageInstall
    VSCode --> KernelRestart
    CPURuntime --> PackageInstall
    PackageInstall --> KernelRestart
```

**Diagram: Platform Deployment Options**

Sources: [quick-start-to-quantum/01_quick_start_to_quantum.ipynb:86-90](), [quick-start-to-quantum/02_quick_start_to_quantum.ipynb:107-114]()

## Key Learning Outcomes

### Terminology and Concepts

Students completing this module will understand:

- **Quantum State**: Superposition of computational basis states
- **Probability Amplitudes**: Complex coefficients in quantum states  
- **Measurement**: Probabilistic collapse to classical outcomes
- **Entanglement**: Non-separable multi-qubit correlations
- **Kernel**: CUDA-Q quantum program definition
- **Statevector**: Complete quantum state representation

### Programming Competencies

- Defining quantum programs using `@cudaq.kernel`
- Implementing single and multi-qubit operations
- Creating reusable quantum subroutines
- Extracting and analyzing quantum states
- Using interactive visualization tools
- Understanding circuit diagram representations

Sources: [quick-start-to-quantum/01_quick_start_to_quantum.ipynb:49-67](), [quick-start-to-quantum/02_quick_start_to_quantum.ipynb:64-79]()

## Integration with Advanced Topics

The Quick Start module serves as the foundation for more specialized quantum computing topics covered in other CUDA-Q Academic modules, providing essential programming skills and conceptual understanding required for quantum algorithms, error correction, and domain-specific applications.

Sources: [quick-start-to-quantum/01_quick_start_to_quantum.ipynb:1-68](), [quick-start-to-quantum/02_quick_start_to_quantum.ipynb:1-133]()

---

