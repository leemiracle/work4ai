<!-- source: DeepWiki mcp.deepwiki.com · repo google-deepmind/rgb_stacking · page 5 Testing and Development · fetched 2026-10-26 -->

# Testing and Development

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.gitignore](.gitignore)
- [CONTRIBUTING.md](CONTRIBUTING.md)
- [LICENSE](LICENSE)
- [rgb_stacking/environment_test.py](rgb_stacking/environment_test.py)

</details>



This section outlines the procedures for validating the `rgb_stacking` environment, managing the codebase, and contributing to the project. The development lifecycle is supported by a standardized test suite, a clear contribution workflow involving Google's Contributor License Agreement (CLA), and licensing under the Apache 2.0 standard.

### Core Development Components

The following diagram illustrates the relationship between the testing infrastructure, the source code configuration, and the contribution requirements.

**Development Workflow and Governance**
```mermaid
graph TD
    subgraph "Testing Space"
        ["environment_test.py"] -- "validates" --> ["environment.py"]
        ["environment_test.py"] -- "uses" --> ["dm_env.test_utils.EnvironmentTestMixin"]
    end

    subgraph "Repository Management"
        [".gitignore"] -- "filters" --> ["Build/Cache Artifacts"]
        ["CONTRIBUTING.md"] -- "defines" --> ["PR Process"]
        ["LICENSE"] -- "governs" --> ["Source Code"]
    end

    subgraph "Contributor Requirements"
        ["PR Process"] -- "requires" --> ["Google CLA"]
        ["PR Process"] -- "requires" --> ["Code Review"]
    end
```
Sources: [rgb_stacking/environment_test.py:1-34](), [CONTRIBUTING.md:1-25](), [.gitignore:1-25](), [LICENSE:1-132]()

---

## Running Tests

The reliability of the simulation environment is ensured through automated tests located in `rgb_stacking/environment_test.py`. These tests utilize the `dm_env` testing utilities to verify that the environment adheres to the expected RL interface.

The primary test class, `EnvironmentTest`, inherits from `test_utils.EnvironmentTestMixin` [rgb_stacking/environment_test.py:24-24](). This mixin automatically runs a battery of checks, including:
*   **Spec Validation**: Ensuring action and observation specs match the data returned by the environment.
*   **Lifecycle Checks**: Verifying the `reset()` and `step()` transitions.
*   **Observation Consistency**: Checking that the `ObservationSet` requested (e.g., `ObservationSet.ALL`) is correctly populated [rgb_stacking/environment_test.py:27-29]().

For details on how to execute these tests and extend them for different object triplets or observation configurations, see **[Running Tests](#5.1)**.

Sources: [rgb_stacking/environment_test.py:16-34]()

---

## Contributing and Licensing

The `rgb_stacking` project is open-source and welcomes community contributions. However, all submissions must follow a specific legal and technical workflow to ensure code quality and licensing compliance.

### Contribution Workflow
All changes are managed through GitHub Pull Requests. Key requirements include:
*   **Contributor License Agreement (CLA)**: Contributors must sign the Google CLA to grant permission for redistribution [CONTRIBUTING.md:9-13]().
*   **Code Review**: Every submission, including those from project members, must undergo a formal review [CONTRIBUTING.md:21-24]().

### Licensing
The project employs a dual-license structure:
1.  **Software**: The Python source code and environment logic are licensed under the **Apache License, Version 2.0** [LICENSE:2-4]().
2.  **Assets**: Note that while the code is Apache 2.0, pre-trained policy weights (found in `assets/saved_models/`) are typically governed by separate terms (CC BY 4.0).

For details on the PR process, CLA links, and specific license terms, see **[Contributing and Licensing](#5.2)**.

Sources: [CONTRIBUTING.md:1-25](), [LICENSE:1-132]()

---

## Environment Configuration

The repository includes a `.gitignore` file to maintain a clean development environment by excluding non-essential files from version control.

| Category | Excluded Patterns |
| :--- | :--- |
| **Python Internals** | `__pycache__`, `*.py[cod]`, `*$py.class` |
| **Packaging** | `build/`, `dist/`, `*.egg-info/`, `wheels/` |
| **Virtual Envs** | `.Python`, `lib/`, `lib64/` |

Sources: [.gitignore:1-25]()

---

