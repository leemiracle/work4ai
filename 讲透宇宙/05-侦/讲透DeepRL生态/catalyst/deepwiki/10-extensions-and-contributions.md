> 来源: [https://deepwiki.com/catalyst-team/catalyst/10-extensions-and-contributions](https://deepwiki.com/catalyst-team/catalyst/10-extensions-and-contributions)
> DeepWiki catalyst-team/catalyst | Last indexed: 21 April 2025 (e99f90

# Extensions and Contributions

  Relevant source files 
 - [.github/FUNDING.yml](https://github.com/catalyst-team/catalyst/blob/e99f9065/.github/FUNDING.yml)
 - [.github/ISSUE_TEMPLATE/bug_report.md](https://github.com/catalyst-team/catalyst/blob/e99f9065/.github/ISSUE_TEMPLATE/bug_report.md?plain=1)
 - [.github/ISSUE_TEMPLATE/documentation.md](https://github.com/catalyst-team/catalyst/blob/e99f9065/.github/ISSUE_TEMPLATE/documentation.md?plain=1)
 - [.github/ISSUE_TEMPLATE/feature_request.md](https://github.com/catalyst-team/catalyst/blob/e99f9065/.github/ISSUE_TEMPLATE/feature_request.md?plain=1)
 - [.github/ISSUE_TEMPLATE/question.md](https://github.com/catalyst-team/catalyst/blob/e99f9065/.github/ISSUE_TEMPLATE/question.md?plain=1)
 - [.github/PULL_REQUEST_TEMPLATE.md](https://github.com/catalyst-team/catalyst/blob/e99f9065/.github/PULL_REQUEST_TEMPLATE.md?plain=1)
 - [.github/workflows/codestyle.yml](https://github.com/catalyst-team/catalyst/blob/e99f9065/.github/workflows/codestyle.yml)
 - [.github/workflows/deploy_publish.yml](https://github.com/catalyst-team/catalyst/blob/e99f9065/.github/workflows/deploy_publish.yml)
 - [.github/workflows/deploy_push.yml](https://github.com/catalyst-team/catalyst/blob/e99f9065/.github/workflows/deploy_push.yml)
 - [.github/workflows/dl_cpu.yml](https://github.com/catalyst-team/catalyst/blob/e99f9065/.github/workflows/dl_cpu.yml)
 - [.github/workflows/dl_cpu_minimal.yml](https://github.com/catalyst-team/catalyst/blob/e99f9065/.github/workflows/dl_cpu_minimal.yml)
 - [.github/workflows/greetings.yml](https://github.com/catalyst-team/catalyst/blob/e99f9065/.github/workflows/greetings.yml)
 - [.github/workflows/integrations.yml](https://github.com/catalyst-team/catalyst/blob/e99f9065/.github/workflows/integrations.yml)
 - [.pre-commit-config.yaml](https://github.com/catalyst-team/catalyst/blob/e99f9065/.pre-commit-config.yaml)
 - [CONTRIBUTING.md](https://github.com/catalyst-team/catalyst/blob/e99f9065/CONTRIBUTING.md?plain=1)
 - [bin/workflows/check_settings.sh](https://github.com/catalyst-team/catalyst/blob/e99f9065/bin/workflows/check_settings.sh)
 - [catalyst/contrib/losses/__init__.py](https://github.com/catalyst-team/catalyst/blob/e99f9065/catalyst/contrib/losses/__init__.py)
 - [catalyst/contrib/losses/smoothing_dice.py](https://github.com/catalyst-team/catalyst/blob/e99f9065/catalyst/contrib/losses/smoothing_dice.py)
 - [catalyst/settings.py](https://github.com/catalyst-team/catalyst/blob/e99f9065/catalyst/settings.py)
 - [docs/api/contrib.rst](https://github.com/catalyst-team/catalyst/blob/e99f9065/docs/api/contrib.rst)
 - [requirements/requirements-cv.txt](https://github.com/catalyst-team/catalyst/blob/e99f9065/requirements/requirements-cv.txt)
 - [requirements/requirements-dev.txt](https://github.com/catalyst-team/catalyst/blob/e99f9065/requirements/requirements-dev.txt)
 - [requirements/requirements-optuna.txt](https://github.com/catalyst-team/catalyst/blob/e99f9065/requirements/requirements-optuna.txt)
 - [setup.py](https://github.com/catalyst-team/catalyst/blob/e99f9065/setup.py)
 
  This page provides a comprehensive guide for extending Catalyst's functionality through custom components and for contributing to the Catalyst project. It covers the contrib module structure, creating custom extensions, the contribution workflow, and extension dependency management.

 For information about specific implementation details of existing components, see [Core Concepts](https://deepwiki.com/catalyst-team/catalyst/1.2-core-concepts).

 
## Contrib Module Structure

 The contrib module in Catalyst is a collection of community-contributed extensions that expand the framework's capabilities beyond its core functionality. These extensions provide additional layers, losses, datasets, optimizers, and other components useful for various deep learning tasks.

 
```

```

 Sources: [docs/api/contrib.rst1-490](https://github.com/catalyst-team/catalyst/blob/e99f9065/docs/api/contrib.rst#L1-L490) [catalyst/contrib/losses/__init__.py1-54](https://github.com/catalyst-team/catalyst/blob/e99f9065/catalyst/contrib/losses/__init__.py#L1-L54)

 The contrib module is organized by component types, allowing users to easily find and use extensions for specific needs. Each submodule in contrib follows a consistent interface with the core Catalyst components, ensuring seamless integration.

 
### Using Contrib Components

 Using contrib components in your code is straightforward. First, ensure you have installed the necessary dependencies (see [Extension Dependency Management](https://github.com/catalyst-team/catalyst/blob/e99f9065/Extension Dependency Management)), then import the specific component you need:

 
```

```

 Many contrib components require additional dependencies beyond Catalyst's core requirements. These are organized into optional dependency groups in the package setup.

 Sources: [setup.py41-62](https://github.com/catalyst-team/catalyst/blob/e99f9065/setup.py#L41-L62) [catalyst/settings.py1-547](https://github.com/catalyst-team/catalyst/blob/e99f9065/catalyst/settings.py#L1-L547)

 
## Creating Custom Extensions

 Catalyst's modular architecture makes it easy to extend with custom components. The most common extensions are custom callbacks, metrics, and losses.

 
### Custom Callback Development

 Callbacks are the primary way to extend Catalyst's training loop behavior. To create a custom callback:

 
 - Inherit from the `Callback` base class
 - Override specific event methods to implement desired functionality
 - Register your callback with the runner
 
 
```

```

 
### Custom Metric Development

 To create a custom metric:

 
 - Inherit from appropriate metric base class (`BatchMetric`, `LoaderMetric`, or `FunctionalMetric`)
 - Implement the required methods for computation
 - Use with a MetricCallback or directly in your training code
 
 
### Custom Loss Development

 Custom losses can be created by inheriting from `torch.nn.Module` and implementing the forward method. The example below demonstrates a custom loss implementation similar to those in the contrib module:

 
```

```

 When creating custom extensions, follow the same code style and documentation standards as the core Catalyst components to ensure consistency and ease of use.

 Sources: [catalyst/contrib/losses/smoothing_dice.py1-95](https://github.com/catalyst-team/catalyst/blob/e99f9065/catalyst/contrib/losses/smoothing_dice.py#L1-L95)

 
## Contributing to Catalyst

 Contributing to Catalyst involves more than just writing code. The workflow includes setting up the environment, adhering to code standards, writing tests and documentation, and following the pull request process.

 
```

```

 Sources: [CONTRIBUTING.md1-187](https://github.com/catalyst-team/catalyst/blob/e99f9065/CONTRIBUTING.md?plain=1#L1-L187) [.github/PULL_REQUEST_TEMPLATE.md1-45](https://github.com/catalyst-team/catalyst/blob/e99f9065/.github/PULL_REQUEST_TEMPLATE.md?plain=1#L1-L45)

 
### Setting Up the Development Environment

 To set up a development environment for Catalyst:

 
 - Install Python 3.7.0 or higher
 - Create a virtual environment (recommended)
 - Install development dependencies: 
```

```
 - For comprehensive development, install additional dependencies: 
```

```
 - Set up the pre-commit hook: 
```

```
 
 Sources: [CONTRIBUTING.md62-93](https://github.com/catalyst-team/catalyst/blob/e99f9065/CONTRIBUTING.md?plain=1#L62-L93)

 
### Coding Standards and Testing

 Catalyst maintains strict coding standards to ensure consistency and quality:

 
 - **Code Style**: Catalyst uses a custom [code style package](https://github.com/catalyst-team/catalyst/blob/e99f9065/code style package) and pre-commit hooks to enforce formatting

 
```

```
 - **Documentation Style**: Google docstring format is required for all new code

 
```

```
 - **Testing**: All new features and bugfixes must include tests

 
```

```
 - **GitHub CI**: Ensure your code passes all CI checks before submitting a PR
 
 Sources: [CONTRIBUTING.md98-144](https://github.com/catalyst-team/catalyst/blob/e99f9065/CONTRIBUTING.md?plain=1#L98-L144) [.github/workflows/codestyle.yml1-152](https://github.com/catalyst-team/catalyst/blob/e99f9065/.github/workflows/codestyle.yml#L1-L152) [.github/workflows/dl_cpu.yml1-116](https://github.com/catalyst-team/catalyst/blob/e99f9065/.github/workflows/dl_cpu.yml#L1-L116)

 
### Pull Request Process

 To contribute changes to Catalyst:

 
 - For new features:

 
 - Make an issue with your feature description
 - Discuss the design and implementation details
 - Implement the feature once approved
 - For bugfixes:

 
 - Find an existing issue or create one
 - Comment to indicate you'll work on the fix
 - Implement the fix
 - Submit a PR following the template, ensuring:

 
 - Tests are included
 - Documentation is updated
 - CHANGELOG.md is updated
 - CI/CD checks pass
 
 Sources: [CONTRIBUTING.md32-60](https://github.com/catalyst-team/catalyst/blob/e99f9065/CONTRIBUTING.md?plain=1#L32-L60) [.github/PULL_REQUEST_TEMPLATE.md1-45](https://github.com/catalyst-team/catalyst/blob/e99f9065/.github/PULL_REQUEST_TEMPLATE.md?plain=1#L1-L45)

 
## Extension Dependency Management

 Catalyst uses a sophisticated system to manage optional dependencies for its extensions, allowing users to install only what they need.

 
```

```

 Sources: [catalyst/settings.py1-547](https://github.com/catalyst-team/catalyst/blob/e99f9065/catalyst/settings.py#L1-L547) [setup.py1-136](https://github.com/catalyst-team/catalyst/blob/e99f9065/setup.py#L1-L136) [bin/workflows/check_settings.sh1-224](https://github.com/catalyst-team/catalyst/blob/e99f9065/bin/workflows/check_settings.sh#L1-L224)

 
### Dependency Groups

 Catalyst organizes optional dependencies into logical groups that can be installed separately:

 
| Extension Group | Description | Installation Command |
|---|---|---|
| cv | Computer vision components | pip install catalyst[cv] |
| ml | Machine learning utilities | pip install catalyst[ml] |
| optuna | Integration with Optuna | pip install catalyst[optuna] |
| mlflow | MLflow logger | pip install catalyst[mlflow] |
| neptune | Neptune logger | pip install catalyst[neptune] |
| wandb | Weights & Biases logger | pip install catalyst[wandb] |
| comet | Comet.ml logger | pip install catalyst[comet] |
| all | CV, ML and Optuna components | pip install catalyst[all] |

 When creating extensions that require additional dependencies, it's best to use Catalyst's settings system to check for their availability:

 
```

```

 This approach ensures that users get clear error messages when missing dependencies and know exactly how to install them.

 Sources: [setup.py41-62](https://github.com/catalyst-team/catalyst/blob/e99f9065/setup.py#L41-L62) [catalyst/settings.py186-346](https://github.com/catalyst-team/catalyst/blob/e99f9065/catalyst/settings.py#L186-L346)

 
### Configuration Methods

 Catalyst provides three ways to configure extension requirements:

 
 - **Installation-time**: Install specific extension groups

 
```

```
 - **Configuration file**: Create a `.catalyst` file in your project directory

 
```
[catalyst]
cv_required = true
optuna_required = true
```
 - **Environment variables**: Set environment variables before running your code

 
```

```
 
 This flexible configuration system makes it easy to manage dependencies in different environments, from development to production.

 Sources: [catalyst/settings.py347-372](https://github.com/catalyst-team/catalyst/blob/e99f9065/catalyst/settings.py#L347-L372) [bin/workflows/check_settings.sh19-38](https://github.com/catalyst-team/catalyst/blob/e99f9065/bin/workflows/check_settings.sh#L19-L38)

 
## Further Resources

 For more detailed information on contributing to Catalyst:

 
 - Review the full [CONTRIBUTING.md](https://github.com/catalyst-team/catalyst/blob/e99f9065/CONTRIBUTING.md?plain=1) guidelines
 - Check the [minimal examples section](https://github.com/catalyst-team/catalyst/blob/e99f9065/minimal examples section) for implementation patterns
 - Join the [Catalyst Slack](https://join.slack.com/t/catalyst-team-core/shared_invite/zt-d9miirnn-z86oKDzFMKlMG4fgFdZafw) for discussion and help
 - Review PRs in the [Contrib Module](https://github.com/catalyst-team/catalyst/blob/e99f9065/Contrib Module) for examples of extension implementations
 
 Remember that the best contributions follow Catalyst's design philosophy of being modular, flexible, and well-documented.

 Sources: [CONTRIBUTING.md15-30](https://github.com/catalyst-team/catalyst/blob/e99f9065/CONTRIBUTING.md?plain=1#L15-L30) [.github/PULL_REQUEST_TEMPLATE.md1-45](https://github.com/catalyst-team/catalyst/blob/e99f9065/.github/PULL_REQUEST_TEMPLATE.md?plain=1#L1-L45)
