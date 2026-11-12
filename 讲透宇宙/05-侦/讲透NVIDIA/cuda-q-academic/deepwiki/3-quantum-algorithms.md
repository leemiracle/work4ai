<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/cuda-q-academic · page 3 Quantum Algorithms · fetched 2026-10-26 -->

# Quantum Algorithms

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [qis-examples/grovers.ipynb](qis-examples/grovers.ipynb)
- [qis-examples/solutions/grovers-solution.ipynb](qis-examples/solutions/grovers-solution.ipynb)

</details>



This page covers the implementation and theory of quantum algorithms within the CUDA-Q Academic framework, with primary focus on Grover's algorithm for quantum database search. The material demonstrates fundamental quantum algorithmic concepts including superposition preparation, oracle construction, amplitude amplification, and measurement-based solution extraction using CUDA-Q programming constructs.

For quantum error correction algorithms, see [Quantum Error Correction](#5). For variational quantum algorithms and optimization approaches, see [Quantum Approximate Optimization Algorithm (QAOA)](#4).

## Overview

Quantum algorithms leverage quantum mechanical phenomena like superposition and interference to solve computational problems with potential speedup over classical approaches. The implementation focuses on Grover's algorithm, which provides quadratic speedup for unstructured search problems, reducing the search complexity from O(N) to O(√N) oracle queries.

**Algorithm Structure**

```mermaid
graph TD
    A["Preparation: equal_superposition()"] --> B["Oracle: phase_oracle()"]
    B --> C["Diffusion: grover_diffusion_operator()"]
    C --> D{"Iteration Count < Optimal?"}
    D -->|Yes| B
    D -->|No| E["Measurement"]
    E --> F["Extract Solution"]
    
    subgraph "CUDA-Q Implementation"
        G["@cudaq.kernel decorators"]
        H["cudaq.qvector quantum registers"]
        I["Gate operations: h, x, z.ctrl"]
        J["State analysis: cudaq.get_state()"]
        K["Sampling: cudaq.sample()"]
    end
```

Sources: [qis-examples/grovers.ipynb:196-211]()

## Theoretical Foundation

### Good and Bad State Decomposition

The algorithm operates on a decomposition of the computational space into marked ("good") and unmarked ("bad") states:

- **Good State**: |G⟩ = (1/√t) Σ_{i:f(i)=1} |i⟩ 
- **Bad State**: |B⟩ = (1/√(N-t)) Σ_{i:f(i)=0} |i⟩
- **Initial Superposition**: |ξ⟩ = sin(θ)|G⟩ + cos(θ)|B⟩

Where θ = arcsin(√(t/N)), t is the number of marked states, and N = 2^n is the total number of states.

```mermaid
graph LR
    subgraph "2D Quantum State Space"
        A["Bad State |B⟩"] -->|"cos(θ)"| C["Initial State |ξ⟩"]
        B["Good State |G⟩"] -->|"sin(θ)"| C
        C -->|"Grover Iteration"| D["Rotated State"]
        D -->|"After m iterations"| E["Near |G⟩"]
    end
    
    subgraph "Geometric Operations"
        F["reflection_over_B"]
        G["reflection_over_xi"] 
        F --> G
        G --> H["2θ rotation"]
    end
```

Sources: [qis-examples/grovers.ipynb:364-384](), [qis-examples/grovers.ipynb:478-522]()

## Implementation Components

### Preparation Phase

The `equal_superposition()` function initializes n qubits in uniform superposition:

```mermaid
graph TD
    A["Qubits in |0⟩^⊗n"] --> B["equal_superposition(qubits)"]
    B --> C["H gates applied to all qubits"]
    C --> D["State |ξ⟩ = (1/√N) Σ|i⟩"]
    
    subgraph "CUDA-Q Implementation"
        E["@cudaq.kernel decorator"]
        F["cudaq.qview parameter"]
        G["h(qubits_in_zero_state)"]
    end
```

Sources: [qis-examples/grovers.ipynb:240-244]()

### Oracle Construction

Phase oracles implement the marking function f(x) by flipping phases of marked states:

| Oracle Function | Target State | Implementation |
|----------------|--------------|----------------|
| `U9()` | \|1001⟩ | Uses controlled-Z with auxiliary qubit |
| `U15()` | \|1111⟩ | Multi-controlled Z gate |
| `phase_oracle()` | Both marked states | Composition of U9 and U15 |

**Oracle Architecture**

```mermaid
graph TD
    A["marking_function()"] --> B["Boolean function f(x)"]
    B --> C["Phase oracle implementation"]
    
    subgraph "Phase Oracle Components"
        D["U9: flips |1001⟩ phase"]
        E["U15: flips |1111⟩ phase"] 
        F["aux_qubit in |−⟩ state"]
        G["Phase kickback mechanism"]
        
        D --> H["phase_oracle()"]
        E --> H
        F --> D
        F --> E
        G --> D
        G --> E
    end
```

Sources: [qis-examples/grovers.ipynb:656-720](), [qis-examples/grovers.ipynb:752-787]()

### Amplitude Amplification

The Grover diffusion operator performs amplitude amplification through reflection operations:

**Diffusion Operator Components**

```mermaid
graph TD
    subgraph "Diffusion Operator Sequence"
        A["State after oracle"] --> B["H gates"]
        B --> C["X gates"] 
        C --> D["Multi-controlled Z"]
        D --> E["X gates"]
        E --> F["H gates"]
        F --> G["Amplified state"]
    end
    
    subgraph "Mathematical Operations"
        H["Reflection over |0000⟩"]
        I["Conjugation by H^⊗n"]
        J["Reflection over |ξ⟩"]
        
        H --> I
        I --> J
    end
```

Sources: [qis-examples/grovers.ipynb:820-900]()

## Algorithm Execution Flow

### Iteration Control

The optimal number of Grover iterations is m = ⌊π/(4θ)⌋, where the algorithm rotates the state vector by 2θ per iteration:

```mermaid
graph TD
    A["Calculate θ = arcsin(√(t/N))"] --> B["Compute m = ⌊π/(4θ)⌋"]
    B --> C["Initialize iteration counter"]
    C --> D["Apply phase_oracle()"]
    D --> E["Apply grover_diffusion_operator()"]
    E --> F["Increment counter"]
    F --> G{"Counter < m?"}
    G -->|Yes| D
    G -->|No| H["Measure qubits"]
    H --> I["Extract marked states"]
```

Sources: [qis-examples/grovers.ipynb:196-211]()

### State Analysis and Verification

**Measurement and Validation Framework**

```mermaid
graph LR
    subgraph "State Analysis Tools"
        A["cudaq.get_state()"] --> B["Amplitude extraction"]
        C["cudaq.sample()"] --> D["Probability distribution"]
        E["overlap() method"] --> F["State comparison"]
        G["plot_results()"] --> H["Visualization"]
    end
    
    subgraph "Validation Methods"
        I["check_phase()"] --> J["Phase verification"]
        K["marking_function()"] --> L["Solution validation"]
        M["Histogram analysis"] --> N["Success probability"]
    end
```

Sources: [qis-examples/grovers.ipynb:288-346](), [qis-examples/grovers.ipynb:700-720]()

## Example Implementation

For a 4-qubit system with marked states `1001` and `1111`:

| Parameter | Value | Description |
|-----------|--------|-------------|
| n | 4 | Number of qubits |
| N | 16 | Total states (2^n) |
| t | 2 | Marked states |
| θ | arcsin(√(2/16)) = π/12 | Rotation angle |
| m | ⌊π/(4×π/12)⌋ = 3 | Optimal iterations |

The implementation demonstrates ~94% success probability after optimal iterations, with marked states showing significantly higher measurement frequencies compared to unmarked states.

Sources: [qis-examples/grovers.ipynb:130-184](), [qis-examples/grovers.ipynb:395-402]()

## Integration with CUDA-Q Framework

The quantum algorithm implementations utilize core CUDA-Q programming constructs:

- `@cudaq.kernel` decorators for quantum function definitions
- `cudaq.qvector` and `cudaq.qubit` for quantum register management  
- Gate operations (`h`, `x`, `z.ctrl`) for quantum transformations
- `cudaq.sample()` and `cudaq.get_state()` for result extraction
- Auxiliary qubit management for phase oracle implementation

Sources: [qis-examples/grovers.ipynb:88-92](), [qis-examples/grovers.ipynb:240-244]()

---

