<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/cuda-q-academic · page 6 Quantum Applications to Finance · fetched 2026-10-26 -->

# Quantum Applications to Finance

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [quantum-applications-to-finance/01_quantum_walks.ipynb](quantum-applications-to-finance/01_quantum_walks.ipynb)
- [quantum-applications-to-finance/02_quantum_walks.ipynb](quantum-applications-to-finance/02_quantum_walks.ipynb)
- [quantum-applications-to-finance/solutions/02_solutions.ipynb](quantum-applications-to-finance/solutions/02_solutions.ipynb)
- [quick-start-to-quantum/03_quick_start_to_quantum.ipynb](quick-start-to-quantum/03_quick_start_to_quantum.ipynb)
- [quick-start-to-quantum/04_quick_start_to_quantum.ipynb](quick-start-to-quantum/04_quick_start_to_quantum.ipynb)

</details>



This document covers the quantum computing applications to financial modeling implemented in the CUDA-Q Academic repository. The system demonstrates how quantum walks can be used to generate and load probability distributions relevant to financial markets, with particular focus on discrete time quantum walks (DTQW), split step quantum walks (SSQW), and multi-split step quantum walks (mSSQW) for risk modeling and asset pricing.

For foundational quantum computing concepts, see [Quick Start to Quantum Computing](#2). For quantum algorithms beyond finance applications, see [Quantum Algorithms](#3).

## System Architecture

The quantum finance module is organized around progressive complexity levels of quantum walk implementations, from basic educational examples to sophisticated variational algorithms for probability distribution loading.

```mermaid
graph TB
    subgraph "Educational Foundation"
        DTQW["01_quantum_walks.ipynb<br/>Discrete Time Quantum Walks"]
        BASICS["CUDA-Q Basics<br/>Quantum Kernels & Gates"]
    end
    
    subgraph "Advanced Applications"
        SSQW["02_quantum_walks.ipynb<br/>Split Step Quantum Walks"]
        mSSQW["Multi-Split Step Quantum Walks<br/>Variational Optimization"]
    end
    
    subgraph "Core Components"
        KERNELS["@cudaq.kernel Functions<br/>inc, dec, SSQW_one_step"]
        BOUNDARY["Boundary Handlers<br/>no_INC_at_right_endpoint<br/>no_DEC_at_left_endpoint"]
        HELPERS["Helper Functions<br/>plot_walk_results<br/>reset_coin_and_endpoint"]
    end
    
    subgraph "Financial Models"
        LOGNORMAL["Log-Normal Distribution<br/>Asset Price Modeling"]
        RISK["Risk Distribution Loading<br/>Loan Default Probability"]
    end
    
    DTQW --> SSQW
    BASICS --> DTQW
    SSQW --> mSSQW
    KERNELS --> DTQW
    KERNELS --> SSQW
    BOUNDARY --> SSQW
    HELPERS --> DTQW
    HELPERS --> SSQW
    mSSQW --> LOGNORMAL
    mSSQW --> RISK
```

**Sources:** [quantum-applications-to-finance/01_quantum_walks.ipynb:1-223](), [quantum-applications-to-finance/02_quantum_walks.ipynb:1-133]()

## Quantum Walk Types and Implementations

### Discrete Time Quantum Walk (DTQW)

The basic quantum walk implementation uses a coin qubit to determine movement direction and walker qubits to track position on a line segment.

```mermaid
graph LR
    subgraph "DTQW Components"
        COIN["coin_qubit<br/>Direction Control"]
        WALKER["walker_qubits<br/>Position Register"]
        INC["inc() kernel<br/>Position +1"]
        DEC["dec() kernel<br/>Position -1"]
    end
    
    subgraph "Operations"
        COINFLIP["Coin Operations<br/>h(), x(), u3()"]
        CONDITIONAL["Conditional Movement<br/>cudaq.control()"]
    end
    
    COIN --> COINFLIP
    WALKER --> INC
    WALKER --> DEC
    COINFLIP --> CONDITIONAL
    CONDITIONAL --> INC
    CONDITIONAL --> DEC
```

**Sources:** [quantum-applications-to-finance/01_quantum_walks.ipynb:94-165]()

### Split Step Quantum Walk (SSQW)

SSQW generalizes DTQW by applying two coin operations per step, allowing more flexible probability distribution generation.

```mermaid
graph TD
    subgraph "SSQW_one_step Process"
        F1["First Coin Operation F1<br/>x() or h()"]
        BOUND1["Boundary Check<br/>no_INC_at_right_endpoint"]
        INCR["Controlled Increment<br/>cudaq.control(inc)"]
        RESET1["reset_coin_and_endpoint"]
        F2["Second Coin Operation F2<br/>h() or custom gate"]
        BOUND2["Boundary Check<br/>no_DEC_at_left_endpoint"]
        DECR["Controlled Decrement<br/>cudaq.control(dec)"]
        RESET2["reset_coin_and_endpoint"]
    end
    
    F1 --> BOUND1
    BOUND1 --> INCR
    INCR --> RESET1
    RESET1 --> F2
    F2 --> BOUND2
    BOUND2 --> DECR
    DECR --> RESET2
```

**Sources:** [quantum-applications-to-finance/02_quantum_walks.ipynb:88-132]()

## Financial Applications

### Log-Normal Distribution Loading

The system addresses the challenge of loading classical probability distributions into quantum states for financial modeling. The log-normal distribution is particularly important for asset pricing models.

```mermaid
graph TB
    subgraph "Financial Context"
        ASSET["Asset Price Model<br/>S_T = log-normal distribution"]
        FORMULA["log(S_T) ~ N((r - σ²/2)T + log(S₀), σ²T)"]
        PARAMS["Parameters:<br/>S₀: Initial price<br/>r: Risk-free rate<br/>σ: Volatility<br/>T: Time to maturity"]
    end
    
    subgraph "Quantum Implementation"
        mSSQW_KERNEL["mSSQW Kernel<br/>Variational Parameters"]
        OPTIMIZATION["scipy.optimize.minimize<br/>Classical Optimizer"]
        COST["Cost Function<br/>Target Distribution Matching"]
    end
    
    subgraph "Technical Components"
        OBSERVE["cudaq.observe<br/>Expectation Value Computation"]
        HAMILTONIAN["position_hamiltonian<br/>cudaq.spin.z operators"]
    end
    
    ASSET --> FORMULA
    FORMULA --> PARAMS
    PARAMS --> mSSQW_KERNEL
    mSSQW_KERNEL --> OPTIMIZATION
    OPTIMIZATION --> COST
    COST --> OBSERVE
    OBSERVE --> HAMILTONIAN
```

**Sources:** [quantum-applications-to-finance/02_quantum_walks.ipynb:235-259]()

### Risk Distribution Modeling

The framework enables modeling of individual loan risk distributions, accounting for uncertainties in modeling and macroeconomic factors.

| Application | Quantum Walk Type | Key Parameters | Financial Relevance |
|-------------|------------------|----------------|-------------------|
| Asset Pricing | mSSQW | θ, φ, λ (coin operations) | Log-normal spot price modeling |
| Loan Risk | mSSQW | Variational gates | Default/prepayment distributions |
| Market Data | SSQW/mSSQW | Multiple coin ops | Asymmetric return distributions |
| Extreme Events | Quantum interference | Amplitude amplitudes | Better tail risk representation |

**Sources:** [quantum-applications-to-finance/02_quantum_walks.ipynb:235-241]()

## Core Implementation Components

### Quantum Kernels

The system defines several key quantum kernels for different walk operations:

```mermaid
graph LR
    subgraph "Position Operators"
        INC_KERNEL["@cudaq.kernel<br/>inc(qubits: cudaq.qview)<br/>Maps |x⟩ to |x+1⟩ mod 16"]
        DEC_KERNEL["@cudaq.kernel<br/>dec(qubits: cudaq.qview)<br/>Maps |x⟩ to |x-1⟩ mod 16"]
    end
    
    subgraph "Boundary Control"
        NO_INC["no_INC_at_right_endpoint<br/>Prevents |1111⟩ → |0000⟩"]
        NO_DEC["no_DEC_at_left_endpoint<br/>Prevents |0000⟩ → |1111⟩"]
    end
    
    subgraph "Composite Operations"
        SSQW_STEP["SSQW_one_step<br/>Complete walk step"]
        MEASUREMENT["SSQW_with_measurement<br/>Full algorithm with sampling"]
    end
    
    INC_KERNEL --> SSQW_STEP
    DEC_KERNEL --> SSQW_STEP
    NO_INC --> SSQW_STEP
    NO_DEC --> SSQW_STEP
    SSQW_STEP --> MEASUREMENT
```

**Sources:** [quantum-applications-to-finance/02_quantum_walks.ipynb:143-165](), [quantum-applications-to-finance/01_quantum_walks.ipynb:106-126]()

### Variational Optimization Workflow

The multi-Split Step Quantum Walk uses classical optimization to find quantum parameters that generate target probability distributions.

```mermaid
graph TD
    subgraph "Variational Algorithm Loop"
        INIT["Initialize Parameters<br/>θ, φ, λ for u3 gates"]
        EXECUTE["Execute mSSQW Kernel<br/>Generate quantum state"]
        MEASURE["Compute Expectation<br/>cudaq.observe(kernel, hamiltonian)"]
        COST_CALC["Calculate Cost<br/>MSE vs target distribution"]
        OPTIMIZE["Classical Optimizer<br/>scipy.optimize.minimize"]
        UPDATE["Update Parameters"]
        CONVERGE{"Converged?"}
    end
    
    INIT --> EXECUTE
    EXECUTE --> MEASURE
    MEASURE --> COST_CALC
    COST_CALC --> OPTIMIZE
    OPTIMIZE --> UPDATE
    UPDATE --> CONVERGE
    CONVERGE -->|No| EXECUTE
    CONVERGE -->|Yes| RESULT["Optimal Distribution"]
```

**Sources:** [quantum-applications-to-finance/02_quantum_walks.ipynb:1-259]()

## Execution and Visualization

### Sampling and State Analysis

The system provides multiple methods for extracting information from quantum walk states:

| Method | Function | Purpose | Output |
|--------|----------|---------|---------|
| Sampling | `cudaq.sample()` | Statistical measurement | Histogram of outcomes |
| State Vector | `cudaq.get_state()` | Complete quantum state | Complex amplitudes |
| Expectation | `cudaq.observe()` | Average values | Real-valued expectation |
| Visualization | `plot_walk_results()` | Result analysis | Probability histograms |

**Sources:** [quantum-applications-to-finance/01_quantum_walks.ipynb:178-222](), [quantum-applications-to-finance/02_quantum_walks.ipynb:179-222]()

### Hamiltonian Construction

The system uses Pauli operators to construct Hamiltonians for expectation value computation:

```python
position_hamiltonian = 7.5*cudaq.spin.i(0) - 4*cudaq.spin.z(0) - 2*cudaq.spin.z(1) - cudaq.spin.z(2) - 0.5*cudaq.spin.z(3)
```

This Hamiltonian enables computation of position expectation values for 4-qubit walker states, where each computational basis state `|j⟩` has eigenvalue `j`.

**Sources:** [quick-start-to-quantum/04_quick_start_to_quantum.ipynb:250-256]()

## Educational Progression

The module follows a structured learning path from classical concepts to advanced quantum algorithms:

1. **Classical Random Walks** - Foundation understanding of stochastic processes
2. **CUDA-Q Basics** - Quantum kernel programming, gates, and measurement
3. **DTQW Implementation** - Basic quantum walk with coin and walker qubits
4. **SSQW Generalization** - Multiple coin operations per step
5. **mSSQW Optimization** - Variational algorithms for distribution loading
6. **Financial Applications** - Log-normal distributions and risk modeling

This progression enables learners to understand both the quantum computing foundations and practical financial applications.

**Sources:** [quantum-applications-to-finance/01_quantum_walks.ipynb:41-56](), [quantum-applications-to-finance/02_quantum_walks.ipynb:45-55]()

---

