<!-- source: DeepWiki mcp.deepwiki.com · repo google-deepmind/optax · page 3 Optimizers · fetched 2026-10-26 -->

# Optimizers

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [optax/_src/alias.py](optax/_src/alias.py)
- [optax/_src/transform.py](optax/_src/transform.py)

</details>



This page provides a high-level overview of the optimization algorithms available across the Optax library, ranging from standard first-order optimizers to advanced adaptive, second-order, and experimental methods. Optax implements optimizers as composable gradient transformations that consume parameter gradients and state, returning updated parameters and state.

For complete implementation details, specific hyperparameters, and practical use cases, refer to the child pages:
- [Standard Optimizers](#3.1)
- [Adaptive and Second-Order Optimizers](#3.2)
- [Contributed Optimizers](#3.3)

---

## 3.1. Standard Optimizers

Standard optimizers form the baseline for the vast majority of deep learning tasks. These include stochastic gradient descent (`sgd`), adaptive moment estimation (`adam`), decoupled weight decay variants (`adamw`), root mean square propagation (`rmsprop`), and cumulative gradient approaches (`adagrad`). In Optax, these algorithms are assembled by chaining foundational components such as momentum trackers, scaling transforms, and learning rate multipliers [optax/_src/alias.py:36-157]().

For detailed documentation on implementation specifics, parameter configurations, and concrete use cases, see [Standard Optimizers](#3.1).

Sources: [optax/_src/alias.py:36-157]()

---

## 3.2. Adaptive and Second-Order Optimizers

Beyond standard first-order methods, Optax provides sophisticated optimization algorithms designed for high-dimensional models, large batch sizes, or complex curvature. This category encompasses memory-efficient second-moment factorizations (`adafactor`), quasi-Newton second-order approaches (`lbfgs`), layer-wise adaptive rate scaling (`lars`, `lamb`), and resilient step size mechanisms.

```mermaid
flowchart TD
    subgraph "AdaptiveAndSecondOrderSpace ["Adaptive and Second-Order Optimizers"]"
        A["optax._src.alias.adafactor"]
        B["optax._src.alias.lbfgs"]
        C["optax._src.alias.lamb"]
        D["optax._src.alias.lars"]
    end
    
    subgraph "CoreTransformations ["Underlying Transforms"]"
        E["optax._src.factorized"]
        F["optax._src.linesearch"]
    end
    
    A --> E
    B --> F
```
*Figure 1: Mapping natural language concepts of adaptive and second-order methods to their respective code entities.*

For comprehensive breakdowns of factorized second moments, quasi-Newton optimization histories, and line search integrations, see [Adaptive and Second-Order Optimizers](#3.2).

Sources: [optax/_src/alias.py](), [optax/_src/factorized.py]()

---

## 3.3. Contributed Optimizers

The `optax.contrib` module houses specialized, research-oriented, and experimental optimizers that explore novel architectural and algorithmic paradigms outside the core Optax package. These methods address specialized training challenges such as dual-momentum tracking, orthogonalized weight updates, sharpness-aware minimization, and schedule-free convergence.

```mermaid
flowchart TD
    subgraph "ContribSpace ["optax.contrib Module"]"
        A["optax.contrib.ademamix"]
        B["optax.contrib.adopt"]
        C["optax.contrib.muon"]
        D["optax.contrib.sophia"]
        E["optax.contrib.sam"]
    end
    
    subgraph "Categories ["Optimization Paradigms"]"
        F["DualMomentum"]
        G["Orthogonalization"]
        H["HessianApproximation"]
        I["MinimaSharpness"]
    end
    
    A --> F
    C --> G
    D --> H
    E --> I
```
*Figure 2: Mapping contributed optimizer algorithms to their module locations and paradigms.*

For deep dives into individual contributed optimizers, consult the subsections below and the main child page:
- [AdEMAMix and Momentum Variants](#3.3.1)
- [ADOPT and Muon Optimizers](#3.3.2)
- [Other Contrib Optimizers](#3.3.3)

For the full reference on all experimental modules, see [Contributed Optimizers](#3.3).

Sources: [optax/contrib/__init__.py]()

### 3.3.1. AdEMAMix and Momentum Variants

The AdEMAMix optimizer family introduces dual-momentum architectures to standard adaptive training. By tracking multiple exponential moving averages of past gradients with different decay schedules, AdEMAMix decouples fast adaptation from long-term trend retention. 

For implementation specifics and simplified variants, see [Contributed Optimizers](#3.3).

Sources: [optax/contrib/__init__.py]()

### 3.3.2. ADOPT and Muon Optimizers

This category covers advanced training algorithms such as ADOPT, which refines traditional adaptive momentum for enhanced stability, and Muon, which applies Newton-Schulz orthogonalization to matrix-valued parameters. Muon requires precise dimension specifications to properly format weight matrices for orthogonal updates.

For algorithmic proofs and code structure, see [Contributed Optimizers](#3.3).

Sources: [optax/contrib/__init__.py]()

### 3.3.3. Other Contrib Optimizers

Optax's contribution library also features a wide array of specialized optimizers and wrappers, including Sophia (Stochastic second-order), MADGRAD, Prodigy, Momo, D-Adaptation, DoG, COCOB, GaLore, ACProp, schedule-free methods, and optimization wrappers like SAM (Sharpness-Aware Minimization), Mechanize, complex-valued variants, and reduce-on-plateau handlers.

For a complete catalog and architectural guides, see [Contributed Optimizers](#3.3).

Sources: [optax/contrib/__init__.py]()

---

