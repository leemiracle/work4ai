<!-- source: DeepWiki mcp.deepwiki.com · repo google-deepmind/alphatensor_quantum · page 6 Synthetic Demonstrations · fetched 2026-10-26 -->

# Synthetic Demonstrations

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [src/demonstrations.py](src/demonstrations.py)
- [src/demonstrations_test.py](src/demonstrations_test.py)

</details>



This page documents the synthetic demonstration generation system used to create training data for the AlphaTensor-Quantum reinforcement learning agent. The system generates random tensor decomposition sequences that incorporate quantum circuit optimization patterns known as gadgets, providing structured training examples that help the agent learn efficient decomposition strategies.

For information about the core tensor and factor operations used in demonstrations, see [Mathematical Foundations](#4). For details about how demonstrations are integrated into the training pipeline, see [Agent System](#3.1).

## System Overview

The synthetic demonstrations system creates artificial training examples that simulate optimal quantum circuit decomposition sequences. Each demonstration consists of a target tensor and a sequence of rank-one factors that decompose it, along with metadata indicating where beneficial gadget patterns occur.

```mermaid
flowchart TD
    subgraph "Demonstration Generation Pipeline"
        Config["DemonstrationsParams<br/>Configuration"]
        RandomFactors["_generate_random_factors<br/>Initial Factor Generation"]
        GadgetSampling["_sample_num_gadgets_per_type<br/>Gadget Type Selection"]
        ToffoliGen["_generate_toffoli_gadget<br/>7-Factor Toffoli Patterns"]
        CSGen["_generate_cs_gadget<br/>3-Factor CS Patterns"]
        GadgetOverwrite["_overwrite_factors_with_gadgets<br/>Pattern Insertion"]
        TensorReconstruct["Tensor Reconstruction<br/>einsum('ru,rv,rw->uvw')"]
        DemoOutput["Demonstration<br/>Output Structure"]
    end
    
    subgraph "Action-Value Extraction"
        ActionExtract["get_action_and_value<br/>Training Pair Generation"]
        FactorIndex["action_factor_to_index<br/>Factor to Action Mapping"]
        ValueCalc["Value Calculation<br/>Future Reward Sum"]
        GadgetReward["Gadget Reward Bonus<br/>TOFFOLI_REWARD_SAVING<br/>CS_REWARD_SAVING"]
    end
    
    Config --> RandomFactors
    Config --> GadgetSampling
    RandomFactors --> GadgetOverwrite
    GadgetSampling --> ToffoliGen
    GadgetSampling --> CSGen
    ToffoliGen --> GadgetOverwrite
    CSGen --> GadgetOverwrite
    GadgetOverwrite --> TensorReconstruct
    TensorReconstruct --> DemoOutput
    
    DemoOutput --> ActionExtract
    ActionExtract --> FactorIndex
    ActionExtract --> ValueCalc
    ValueCalc --> GadgetReward
    
    classDef generation fill:#f9f9f9
    classDef extraction fill:#e8f4f8
    
    class Config,RandomFactors,GadgetSampling,ToffoliGen,CSGen,GadgetOverwrite,TensorReconstruct,DemoOutput generation
    class ActionExtract,FactorIndex,ValueCalc,GadgetReward extraction
```

**Sources:** [src/demonstrations.py:473-563](), [src/demonstrations.py:566-610]()

## Demonstration Data Structure

The `Demonstration` class represents a complete synthetic training example containing all necessary information for training the RL agent.

| Field | Type | Purpose |
|-------|------|---------|
| `tensor` | `Array[*batch, size, size, size]` | Target 3D tensor to decompose |
| `num_factors` | `Array[*batch]` | Number of valid factors in sequence |
| `factors` | `Array[*batch, max_factors, size]` | Factor sequence (zero-padded) |
| `factors_complete_toffoli_gadget` | `Array[*batch, max_factors]` | Boolean flags for Toffoli gadget completion |
| `factors_complete_cs_gadget` | `Array[*batch, max_factors]` | Boolean flags for CS gadget completion |

```mermaid
graph TD
    subgraph "Demonstration Structure"
        Demo["Demonstration<br/>NamedTuple"]
        Tensor["tensor<br/>3D Array GF(2)"]
        NumFactors["num_factors<br/>Scalar Integer"]
        Factors["factors<br/>2D Array (padded)"]
        ToffoliFlags["factors_complete_toffoli_gadget<br/>Boolean Array"]
        CSFlags["factors_complete_cs_gadget<br/>Boolean Array"]
    end
    
    subgraph "Validation Properties"
        ZeroPadding["Zero Padding<br/>factors[num_factors:] = 0"]
        TensorRecon["Tensor Reconstruction<br/>tensor = einsum(factors, factors, factors) % 2"]
        GadgetConsistency["Gadget Consistency<br/>Only last factor of gadget marked True"]
    end
    
    Demo --> Tensor
    Demo --> NumFactors
    Demo --> Factors
    Demo --> ToffoliFlags
    Demo --> CSFlags
    
    Factors --> ZeroPadding
    Tensor --> TensorRecon
    ToffoliFlags --> GadgetConsistency
    CSFlags --> GadgetConsistency
```

**Sources:** [src/demonstrations.py:30-50](), [src/demonstrations_test.py:39-69]()

## Synthetic Data Generation Process

The `generate_synthetic_demonstrations` function orchestrates the creation of complete demonstrations through a multi-stage process controlled by configuration parameters.

### Factor Generation

Initial factors are generated randomly with configurable sparsity, ensuring no all-zero factors exist:

```mermaid
flowchart TD
    subgraph "Random Factor Generation"
        InitZeros["Initialize Zero Factors<br/>zeros(num_factors, size)"]
        SampleRandom["Sample Bernoulli<br/>p = 1 - prob_zero_factor_entry"]
        CheckZeros["Check All-Zero Factors<br/>any(all(factors == 0, axis=-1))"]
        ResampleLoop["Resample Loop<br/>_resample_factors"]
    end
    
    subgraph "Gadget-Specific Generation"
        LinearIndep3["_generate_three_linearly_independent_factors<br/>For Toffoli Gadgets"]
        LinearIndep2["_generate_two_linearly_independent_factors<br/>For CS Gadgets"]
        ToffoliConstruct["Toffoli Construction<br/>[a, b, c, a+b, a+c, a+b+c, b+c]"]
        CSConstruct["CS Construction<br/>[a, b, a+b]"]
    end
    
    InitZeros --> SampleRandom
    SampleRandom --> CheckZeros
    CheckZeros -->|"Has Zeros"| ResampleLoop
    ResampleLoop --> CheckZeros
    CheckZeros -->|"No Zeros"| LinearIndep3
    
    LinearIndep3 --> ToffoliConstruct
    LinearIndep2 --> CSConstruct
```

**Sources:** [src/demonstrations.py:98-117](), [src/demonstrations.py:176-194](), [src/demonstrations.py:197-208]()

### Configuration Parameters

The generation process is controlled by `DemonstrationsParams`:

| Parameter | Purpose | Effect |
|-----------|---------|---------|
| `min_num_factors` | Minimum demonstration length | Controls training sequence diversity |
| `max_num_factors` | Maximum demonstration length | Limits computational overhead |
| `prob_zero_factor_entry` | Factor sparsity probability | Controls factor density |
| `prob_include_gadget` | Gadget inclusion probability | Balances gadget vs. random training |
| `prob_toffoli_gadget` | Toffoli vs. CS gadget ratio | Controls gadget type distribution |
| `max_num_gadgets` | Maximum gadgets per demonstration | Limits gadget density |

**Sources:** [src/demonstrations.py:480-527](), [src/config.py]()

## Gadget Integration

Gadgets are quantum circuit optimization patterns that provide efficiency benefits. The system incorporates two types: Toffoli gadgets (7 factors) and CS gadgets (3 factors).

### Gadget Insertion Process

```mermaid
sequenceDiagram
    participant Config as "Configuration"
    participant Sampler as "_sample_num_gadgets_per_type"
    participant Overwriter as "_overwrite_factors_with_gadgets"
    participant ToffoliGen as "_generate_toffoli_gadget"
    participant CSGen as "_generate_cs_gadget"
    
    Config->>Sampler: num_gadgets, prob_toffoli_gadget
    Sampler->>Sampler: Sample gadget counts within factor budget
    Sampler-->>Overwriter: num_toffoli_gadgets, num_cs_gadgets
    
    loop For each gadget to insert
        Overwriter->>Overwriter: Sample insertion position
        Overwriter->>Overwriter: Choose gadget type (Toffoli vs CS)
        alt Toffoli gadget
            Overwriter->>ToffoliGen: Generate 7-factor pattern
            ToffoliGen-->>Overwriter: [a, b, c, a+b, a+c, a+b+c, b+c]
            Overwriter->>Overwriter: Mark factor 6 as gadget completion
        else CS gadget
            Overwriter->>CSGen: Generate 3-factor pattern
            CSGen-->>Overwriter: [a, b, a+b]
            Overwriter->>Overwriter: Mark factor 2 as gadget completion
        end
        Overwriter->>Overwriter: Update insertion index
    end
```

**Sources:** [src/demonstrations.py:230-291](), [src/demonstrations.py:320-469]()

### Gadget Positioning Algorithm

The system uses a sophisticated algorithm to position gadgets uniformly throughout demonstrations while respecting factor budget constraints:

```mermaid
graph TD
    subgraph "Gadget Positioning"
        CalcBudget["Calculate Factor Budget<br/>7 * num_toffoli + 3 * num_cs"]
        SampleIndices["Sample Insertion Indices<br/>Uniform without replacement"]
        ProbDistribution["Probability Distribution<br/>P(i) = C(n-i+start-1, k-1) / C(n, k)"]
        InsertOrder["Insert in Index Order<br/>Prevents overlaps"]
    end
    
    subgraph "Budget Enforcement"
        CheckBudget["Check Budget Constraint<br/>total_factors <= num_factors"]
        DecrementGadgets["Decrement Gadget Count<br/>If budget exceeded"]
        ResampleTypes["Resample Gadget Types<br/>Until budget satisfied"]
    end
    
    CalcBudget --> CheckBudget
    CheckBudget -->|"Exceeds Budget"| DecrementGadgets
    DecrementGadgets --> ResampleTypes
    ResampleTypes --> CheckBudget
    CheckBudget -->|"Within Budget"| SampleIndices
    SampleIndices --> ProbDistribution
    ProbDistribution --> InsertOrder
```

**Sources:** [src/demonstrations.py:253-290](), [src/demonstrations.py:360-390]()

## Action-Value Extraction

The `get_action_and_value` function converts demonstrations into training pairs for the RL agent, mapping factors to action indices and computing discounted future rewards.

### Value Calculation

Values represent the sum of future rewards from a given position, incorporating gadget completion bonuses:

```mermaid
flowchart LR
    subgraph "Value Computation"
        MoveIndex["move_index<br/>Current Position"]
        BaseValue["Base Value<br/>move_index - num_factors"]
        GadgetScan["Scan Future Factors<br/>fori_loop(move_index, num_factors)"]
        ToffoliBonus["Toffoli Bonus<br/>+TOFFOLI_REWARD_SAVING"]
        CSBonus["CS Bonus<br/>+CS_REWARD_SAVING"]
        FinalValue["Final Value<br/>Sum of base + bonuses"]
    end
    
    subgraph "Action Mapping"
        FactorExtract["Extract Factor<br/>factors[move_index]"]
        ActionIndex["action_factor_to_index<br/>Binary to Integer"]
    end
    
    MoveIndex --> BaseValue
    MoveIndex --> FactorExtract
    BaseValue --> GadgetScan
    GadgetScan --> ToffoliBonus
    GadgetScan --> CSBonus
    ToffoliBonus --> FinalValue
    CSBonus --> FinalValue
    FactorExtract --> ActionIndex
```

**Sources:** [src/demonstrations.py:566-610](), [src/factors.py]()

### Reward Structure

| Event | Reward | Purpose |
|-------|--------|---------|
| Each factor applied | -1.0 | Encourages shorter decompositions |
| Toffoli gadget completion | `+TOFFOLI_REWARD_SAVING` | Rewards 4-T-gate savings |
| CS gadget completion | `+CS_REWARD_SAVING` | Rewards 1-T-gate savings |

**Sources:** [src/demonstrations.py:591-600](), [src/factors.py]()

## Configuration and Usage

Synthetic demonstrations are primarily used during agent initialization and training to provide structured examples alongside exploration-based learning.

### Integration with Training Pipeline

```mermaid
graph TD
    subgraph "Training Integration"
        AgentInit["Agent Initialization<br/>agent.py"]
        DemoConfig["DemonstrationsParams<br/>From config.py"]  
        DemoGen["generate_synthetic_demonstrations<br/>Batched generation"]
        ActionValue["get_action_and_value<br/>Training pair extraction"]
        TrainingData["Training Dataset<br/>Actions + Values"]
        NetworkUpdate["Network Parameter Update<br/>Policy + Value losses"]
    end
    
    AgentInit --> DemoConfig
    DemoConfig --> DemoGen
    DemoGen --> ActionValue  
    ActionValue --> TrainingData
    TrainingData --> NetworkUpdate
    NetworkUpdate --> AgentInit
```

**Sources:** [src/demonstrations.py:472](), [src/agent.py](), [src/config.py]()

The synthetic demonstrations system provides a crucial bootstrap mechanism for training, ensuring the agent learns from structured examples that incorporate domain knowledge about quantum circuit optimization patterns while maintaining the flexibility to discover novel decomposition strategies through reinforcement learning.

---

