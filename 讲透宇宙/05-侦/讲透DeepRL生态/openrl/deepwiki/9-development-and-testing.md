> 来源: [https://deepwiki.com/OpenRL-Lab/openrl/9-development-and-testing](https://deepwiki.com/OpenRL-Lab/openrl/9-development-and-testing)
> DeepWiki OpenRL-Lab/openrl | Last indexed: 28 April 2025 (4c92aa

# Development and Testing

  Relevant source files 
 - [.github/ISSUE_TEMPLATE/bug_report.yml](https://github.com/OpenRL-Lab/openrl/blob/4c92aa44/.github/ISSUE_TEMPLATE/bug_report.yml)
 - [.github/ISSUE_TEMPLATE/documentation.yml](https://github.com/OpenRL-Lab/openrl/blob/4c92aa44/.github/ISSUE_TEMPLATE/documentation.yml)
 - [.github/ISSUE_TEMPLATE/feature_request.yml](https://github.com/OpenRL-Lab/openrl/blob/4c92aa44/.github/ISSUE_TEMPLATE/feature_request.yml)
 - [.github/workflows/unit_test.yml](https://github.com/OpenRL-Lab/openrl/blob/4c92aa44/.github/workflows/unit_test.yml)
 - [Project.md](https://github.com/OpenRL-Lab/openrl/blob/4c92aa44/Project.md?plain=1)
 - [openrl/supports/opendata/utils/opendata_utils.py](https://github.com/OpenRL-Lab/openrl/blob/4c92aa44/openrl/supports/opendata/utils/opendata_utils.py)
 - [tests/test_env/test_mpe_env.py](https://github.com/OpenRL-Lab/openrl/blob/4c92aa44/tests/test_env/test_mpe_env.py)
 - [tests/test_examples/test_train_cartpole.py](https://github.com/OpenRL-Lab/openrl/blob/4c92aa44/tests/test_examples/test_train_cartpole.py)
 - [tests/test_examples/test_train_mpe.py](https://github.com/OpenRL-Lab/openrl/blob/4c92aa44/tests/test_examples/test_train_mpe.py)
 
  This document provides a comprehensive guide for developers who want to contribute to the OpenRL framework and test their changes. It covers the development workflow, testing infrastructure, and how to write effective tests for OpenRL components. For specific details about the testing framework implementation, see [Testing Framework](https://deepwiki.com/OpenRL-Lab/openrl/9.1-testing-framework). For information about research projects built with OpenRL, see [Research Projects](https://deepwiki.com/OpenRL-Lab/openrl/9.2-research-projects).

 
## Development Workflow

 
### Setting Up Development Environment

 To start developing with OpenRL, you need to set up a proper development environment:

 
```

```

 
### Contribution Process

 The diagram below illustrates the standard contribution workflow for OpenRL:

 
```

```

 Sources: [.github/workflows/unit_test.yml1-43](https://github.com/OpenRL-Lab/openrl/blob/4c92aa44/.github/workflows/unit_test.yml#L1-L43)

 
### Issue Reporting

 OpenRL provides structured templates for reporting issues:

 
 - **Bug Reports**: Use the bug report template to provide reproduction steps, error messages, and system information.
 - **Feature Requests**: Use the feature request template to describe and motivate new features.
 - **Documentation Issues**: Use the documentation template to report documentation problems.
 
 Sources: [.github/ISSUE_TEMPLATE/bug_report.yml1-62](https://github.com/OpenRL-Lab/openrl/blob/4c92aa44/.github/ISSUE_TEMPLATE/bug_report.yml#L1-L62) [.github/ISSUE_TEMPLATE/feature_request.yml1-32](https://github.com/OpenRL-Lab/openrl/blob/4c92aa44/.github/ISSUE_TEMPLATE/feature_request.yml#L1-L32) [.github/ISSUE_TEMPLATE/documentation.yml1-21](https://github.com/OpenRL-Lab/openrl/blob/4c92aa44/.github/ISSUE_TEMPLATE/documentation.yml#L1-L21)

 
## Testing Framework

 
### Testing Directory Structure

 OpenRL's test suite is organized hierarchically by component type:

 
```

```

 Sources: [tests/test_env/test_mpe_env.py1-62](https://github.com/OpenRL-Lab/openrl/blob/4c92aa44/tests/test_env/test_mpe_env.py#L1-L62) [tests/test_examples/test_train_mpe.py1-54](https://github.com/OpenRL-Lab/openrl/blob/4c92aa44/tests/test_examples/test_train_mpe.py#L1-L54) [tests/test_examples/test_train_cartpole.py1-59](https://github.com/OpenRL-Lab/openrl/blob/4c92aa44/tests/test_examples/test_train_cartpole.py#L1-L59)

 
### Test Execution

 Tests are executed using pytest with various options:

 
```

```

 
### Continuous Integration

 OpenRL uses GitHub Actions for continuous integration. The workflow is defined in the unit_test.yml file and runs automatically on pull requests.

 
```

```

 The CI workflow:

 
 - Runs on Python 3.8 and 3.11
 - Installs OpenRL with test dependencies
 - Executes tests with pytest
 - Generates and uploads coverage reports
 
 Sources: [.github/workflows/unit_test.yml1-43](https://github.com/OpenRL-Lab/openrl/blob/4c92aa44/.github/workflows/unit_test.yml#L1-L43)

 
## Writing Tests for OpenRL

 
### Test Structure and Markers

 Tests in OpenRL use pytest markers for categorization. The most common marker is `@pytest.mark.unittest`:

 
```

```

 
### Using Fixtures

 Fixtures provide reusable test components and parameter configurations:

 
```

```

 Sources: [tests/test_examples/test_train_mpe.py15-25](https://github.com/OpenRL-Lab/openrl/blob/4c92aa44/tests/test_examples/test_train_mpe.py#L15-L25) [tests/test_examples/test_train_cartpole.py30-36](https://github.com/OpenRL-Lab/openrl/blob/4c92aa44/tests/test_examples/test_train_cartpole.py#L30-L36)

 
### Testing Environments

 Environment tests typically follow this pattern:

 
```

```

 A typical environment test:

 
 - Creates an environment with `make()`
 - Resets the environment
 - Performs random actions
 - Verifies environment properties
 - Closes the environment
 
 Sources: [tests/test_env/test_mpe_env.py27-35](https://github.com/OpenRL-Lab/openrl/blob/4c92aa44/tests/test_env/test_mpe_env.py#L27-L35)

 
### Testing Agents and Training

 Agent tests verify training and inference functionality:

 
```

```

 A typical agent test:

 
 - Creates an environment
 - Initializes a network and agent
 - Trains for a small number of steps
 - Evaluates agent performance
 - Asserts performance meets a threshold
 
 Sources: [tests/test_examples/test_train_cartpole.py40-54](https://github.com/OpenRL-Lab/openrl/blob/4c92aa44/tests/test_examples/test_train_cartpole.py#L40-L54) [tests/test_examples/test_train_mpe.py28-50](https://github.com/OpenRL-Lab/openrl/blob/4c92aa44/tests/test_examples/test_train_mpe.py#L28-L50)

 
## Research Projects

 OpenRL has been used in several research projects. For a detailed list, see [Research Projects](https://deepwiki.com/OpenRL-Lab/openrl/9.2-research-projects). Major projects include:

 
| Project | Description | Paper |
|---|---|---|
| MQE | Multi-agent Quadruped Environment for MARL | MQE: Unleashing the Power of Interaction with Multi-agent Quadruped Environment |
| LLMArena | Framework for evaluating LLM capabilities in dynamic multi-agent environments | LLMArena: Assessing Capabilities of Large Language Models in Dynamic Multi-Agent Environments |
| TiZero | RL agent for Google Research Football | TiZero: Mastering Multi-Agent Football with Curriculum Learning and Self-Play |
| DGPO | Framework for discovering multiple strategies | DGPO: Discovering Multiple Strategies with Diversity-Guided Policy Optimization |

 Sources: [Project.md1-43](https://github.com/OpenRL-Lab/openrl/blob/4c92aa44/Project.md?plain=1#L1-L43)

 
## Best Practices for Development and Testing

 
 - **Write Tests First**: Consider writing tests before implementing new features to ensure they meet requirements.
 - **Keep Tests Fast**: Minimize training steps and environment interactions to keep test execution time short.
 - **Test Edge Cases**: Test error handling, boundary conditions, and invalid inputs.
 - **Use Appropriate Markers**: Use markers to categorize tests for selective execution.
 - **Maintain Test Independence**: Each test should be independent and not rely on state from other tests.
 - **Follow Test Naming Conventions**: Name tests with `test_` prefix followed by a descriptive name.
 - **Verify Main APIs**: Ensure core APIs like `make()`, `Agent.train()`, and `Agent.act()` are thoroughly tested.
 - **Use CI for Verification**: Rely on the CI pipeline to catch issues across different Python versions.
 
 Sources: [tests/test_examples/test_train_cartpole.py40-54](https://github.com/OpenRL-Lab/openrl/blob/4c92aa44/tests/test_examples/test_train_cartpole.py#L40-L54) [tests/test_env/test_mpe_env.py27-35](https://github.com/OpenRL-Lab/openrl/blob/4c92aa44/tests/test_env/test_mpe_env.py#L27-L35)
