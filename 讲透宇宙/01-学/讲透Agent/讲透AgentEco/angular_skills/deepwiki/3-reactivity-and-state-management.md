<!-- source: DeepWiki mcp.deepwiki.com · repo angular/skills · page 3 Reactivity and State Management · fetched 2026-10-27 -->

# Reactivity and State Management

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [angular-developer/references/effects.md](angular-developer/references/effects.md)
- [angular-developer/references/signals-overview.md](angular-developer/references/signals-overview.md)

</details>



Angular's reactivity system is built on **Signals**, a primitive that tracks state and notifies consumers when values change. This system provides fine-grained reactivity, allowing Angular to update only the specific parts of the DOM or state tree that are affected by a change, without relying on heavy zone-based change detection.

### Core Reactivity Model

The reactivity system consists of producers (Signals) and consumers (Templates, Effects, Computations). When a signal is read within a **reactive context**, Angular automatically establishes a dependency relationship.

| Primitive | Purpose | Writable? |
| :--- | :--- | :--- |
| `signal()` | Primary state storage. | Yes |
| `computed()` | Derived, memoized state. | No |
| `linkedSignal()` | Derived state that remains manually writable. | Yes |
| `resource()` | Async state (e.g., HTTP data). | Local mutation supported |
| `effect()` | Side effects for non-signal APIs. | N/A |

### Reactivity Flow and Code Mapping

The following diagram illustrates how state flows from a source `signal` through derivations to the UI or external side effects, mapping these concepts to their specific code entities.

**State Propagation Diagram**
```mermaid
graph TD
    subgraph ["Source State"]
        A["signal()"]
    end

    subgraph ["Derivations"]
        B["computed()"]
        C["linkedSignal()"]
    end

    subgraph ["Consumers"]
        D["Component Template"]
        E["effect()"]
        F["afterRenderEffect()"]
    end

    A --> B
    A --> C
    A --> D
    A --> E
    B --> D
    C --> D
    B --> E
    E --> G["External APIs (localStorage)"]
    F --> H["DOM Manipulation (Canvas/3rd Party)"]
```
Sources: [angular-developer/references/signals-overview.md:1-62](), [angular-developer/references/effects.md:1-13]()

---

### Signals and Computed State
Signals are the foundation of modern Angular. A `signal()` acts as a wrapper around a value [angular-developer/references/signals-overview.md:3-5](). To derive new information from existing signals, `computed()` creates a read-only signal that is lazily evaluated and memoized [angular-developer/references/signals-overview.md:35-41]().

**Key Concepts:**
*   **Reactive Contexts:** Environments like templates or `effect` callbacks where signal reads are tracked [angular-developer/references/signals-overview.md:52-62]().
*   **Untracked Reads:** Using `untracked()` to read a signal value without creating a dependency [angular-developer/references/signals-overview.md:63-66]().
*   **Read-only Exposure:** The `asReadonly()` pattern for services to prevent external state mutation [angular-developer/references/signals-overview.md:25-33]().

For details, see [Signals and Computed State](#3.1).

### linkedSignal and Derived Writable State
While `computed()` is strictly read-only, `linkedSignal()` allows for state that is "linked" to a source signal but can still be manually updated by the user [angular-developer/references/effects.md:15-17](). This is ideal for scenarios like a "Reset to Default" feature or form fields that initialize based on a selection.

For details, see [linkedSignal and Derived Writable State](#3.2).

### Async Reactivity with resource and httpResource
Angular provides `resource()` and `httpResource()` to bring asynchronous operations into the signal world. These primitives manage the lifecycle of an async request, providing signals for `value`, `isLoading`, and `error`.

*   **resource()**: A generic primitive for any async loader [angular-developer/references/effects.md:15-17]().
*   **httpResource()**: A specialized version for HTTP requests that handles automatic cancellation and signal-native data fetching.

For details, see [Async Reactivity with resource and httpResource](#3.3).

### Effects and Side Effects
Effects are used to synchronize signal state with imperative APIs, such as logging, `localStorage`, or 3rd-party libraries [angular-developer/references/effects.md:5-13](). 

**Important Distinctions:**
*   **effect()**: Runs asynchronously during change detection, typically before DOM updates [angular-developer/references/effects.md:20-22]().
*   **afterRenderEffect()**: Specifically designed for DOM manipulation, divided into phases (`earlyRead`, `write`, `read`) to prevent layout thrashing [angular-developer/references/effects.md:43-53]().

**Side Effect Execution Context**
```mermaid
graph LR
    subgraph ["Injection Context (Constructor/Field)"]
        direction TB
        Init["Initialize effect()"]
    end

    subgraph ["Execution Pipeline"]
        direction TB
        CD["Change Detection"]
        Eff["effect() callback"]
        DOM["DOM Update"]
        ARE["afterRenderEffect()"]
    end

    Init -.-> Eff
    CD --> Eff
    Eff --> DOM
    DOM --> ARE
```
Sources: [angular-developer/references/effects.md:29-32](), [angular-developer/references/effects.md:43-47](), [angular-developer/references/effects.md:76-82]()

For details, see [Effects and Side Effects](#3.4).

---

