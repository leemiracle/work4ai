<!-- source: DeepWiki mcp.deepwiki.com · repo libingzheren/Jev-Mem · page 4 System-One Controller (Jev) · fetched 2026-10-13 -->

# System-One Controller (Jev)

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [memory/jev_mem_policies.py](memory/jev_mem_policies.py)
- [memory/jev_questions.py](memory/jev_questions.py)

</details>



This page provides a high-level overview of the System-One Controller, referred to as "Jev" within the Jev-Mem codebase. Jev acts as a lightweight, fast, and reactive layer responsible for making immediate decisions based on current observations and memory state. It encompasses policies for memory admission, typing, and relation judgment, as well as the retrieval control mechanisms. This controller also defines the question schema used for these decisions and provides a client for interacting with the underlying decision-making system.

The System-One Controller is designed to operate quickly, often making probabilistic assessments that guide the more deliberate System-Two processes. It leverages a structured question protocol to elicit specific judgments from an underlying model, which can be either a live provider or a mock for testing and development.

## Write and Read Policies

The `jev_mem_policies.py` and `jev_mem_retrieval.py` modules define the core policies that govern how memories are processed and retrieved. These policies include:

*   **Admission Control**: Determining whether an observation should be stored in memory, based on factors like future utility, importance, novelty, and redundancy. This is handled by the `MemoryAdmission` dataclass and the `assess_observation` method in `WritePolicy` [memory/jev_mem_policies.py:12-23, 108-124]().
*   **Memory Typing**: Classifying observations into categories such as episodic, semantic, procedural, and preference memory. The `MemoryTypeScores` dataclass captures these classifications [memory/jev_mem_policies.py:26-31]().
*   **Relation Judgment**: Assessing potential relationships between new observations and existing memories, such as semantic similarity, causality, or entity identity. The `relations` method in `WritePolicy` is responsible for this [memory/jev_mem_policies.py:125-149]().
*   **Budget Allocation**: While not explicitly detailed on this page, policies can implicitly influence resource allocation by prioritizing certain types of memories or relations.
*   **Evidence Assessment**: Evaluating the relevance and quality of retrieved information.

These policies are implemented using structured questions defined in `jev_questions.py`, which are then evaluated by the Jev client.

For details, see [Write and Read Policies](#4.1).

Sources:
* [memory/jev_mem_policies.py:12-23]()
* [memory/jev_mem_policies.py:26-31]()
* [memory/jev_mem_policies.py:108-124]()
* [memory/jev_mem_policies.py:125-149]()

## Noul/Choice Question Protocol and Client

The `jev_questions.py` module defines the structured decision-making protocol used by Jev. This protocol relies on two primary types from the `typesafe_sdk`: `Noul` and `Choice`.

*   **Noul**: Represents a "Natural Language Output Unit" and is used for probabilistic assessments of propositions (e.g., "should store," "is important"). It takes instructions and criteria for "yes" and "no" outcomes [memory/jev_questions.py:10-13](). Examples include `admission_questions` and `memory_type_questions` [memory/jev_questions.py:19-41, 44-63]().
*   **Choice**: Allows for selecting one option from a predefined set of choices, often used for more complex categorizations or actions.

The `jev_client.py` module (not fully shown in the provided snippets but referenced) provides the interface for interacting with the underlying model that answers these `Noul` and `Choice` questions. This client can be configured to use a live LLM provider or a mock implementation for testing and development purposes, as seen in the `mock_values` parameter in `WritePolicy` methods [memory/jev_mem_policies.py:104-106, 115-118, 132-133]().

The following diagram illustrates the high-level interaction between the `WritePolicy` and the `jev_questions` for memory admission:

```mermaid
graph TD
    subgraph "System-One Controller (Jev)"
        A["WritePolicy.assess_observation(content, duplicate, recent_memories)"] --> B{jev_client.evaluate("observation", ...)}
        B --> C["jev_questions.observation_questions()"]
        C --> D["jev_questions.admission_questions()"]
        C --> E["jev_questions.memory_type_questions()"]
        D --> F["Noul(should_store)"]
        D --> G["Noul(future_utility)"]
        D --> H["Noul(importance)"]
        D --> I["Noul(novelty)"]
        D --> J["Noul(redundancy)"]
        E --> K["Noul(episodic)"]
        E --> L["Noul(semantic)"]
        E --> M["Noul(procedural)"]
        E --> N["Noul(preference)"]
        B -- "Result.values" --> O["MemoryAdmission(**result.values)"]
        B -- "Result.values" --> P["MemoryTypeScores(**result.values)"]
        O & P --> Q["Return (admission, memory_type)"]
    end

    style A fill:#f9f,stroke:#333,stroke-width:2px
    style B fill:#ccf,stroke:#333,stroke-width:2px
    style C fill:#ccf,stroke:#333,stroke-width:2px
    style D fill:#ccf,stroke:#333,stroke-width:2px
    style E fill:#ccf,stroke:#333,stroke-width:2px
    style F fill:#ccf,stroke:#333,stroke-width:2px
    style G fill:#ccf,stroke:#333,stroke-width:2px
    style H fill:#ccf,stroke:#333,stroke-width:2px
    style I fill:#ccf,stroke:#333,stroke-width:2px
    style J fill:#ccf,stroke:#333,stroke-width:2px
    style K fill:#ccf,stroke:#333,stroke-width:2px
    style L fill:#ccf,stroke:#333,stroke-width:2px
    style M fill:#ccf,stroke:#333,stroke-width:2px
    style N fill:#ccf,stroke:#333,stroke-width:2px
    style O fill:#f9f,stroke:#333,stroke-width:2px
    style P fill:#f9f,stroke:#333,stroke-width:2px
    style Q fill:#f9f,stroke:#333,stroke-width:2px
```
Title: Jev Admission and Typing Flow

Sources:
* [memory/jev_mem_policies.py:104-106]()
* [memory/jev_mem_policies.py:115-118]()
* [memory/jev_mem_policies.py:132-133]()
* [memory/jev_questions.py:10-13]()
* [memory/jev_questions.py:19-41]()
* [memory/jev_questions.py:44-63]()

For details, see [Noul/Choice Question Protocol and Client](#4.2).

---

