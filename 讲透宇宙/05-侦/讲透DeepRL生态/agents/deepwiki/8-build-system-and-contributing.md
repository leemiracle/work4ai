> 来源: [https://deepwiki.com/tensorflow/agents/8-build-system-and-contributing](https://deepwiki.com/tensorflow/agents/8-build-system-and-contributing)
> DeepWiki tensorflow/agents | Last indexed: 24 April 2025 (2a236d

# Build System and Contributing

  Relevant source files 
 - [README.md](https://github.com/tensorflow/agents/blob/2a236d30/README.md?plain=1)
 - [docs/overview.md](https://github.com/tensorflow/agents/blob/2a236d30/docs/overview.md?plain=1)
 - [pip_pkg.sh](https://github.com/tensorflow/agents/blob/2a236d30/pip_pkg.sh)
 - [setup.py](https://github.com/tensorflow/agents/blob/2a236d30/setup.py)
 - [tests_release.sh](https://github.com/tensorflow/agents/blob/2a236d30/tests_release.sh)
 - [tf_agents/version.py](https://github.com/tensorflow/agents/blob/2a236d30/tf_agents/version.py)
 
  This document explains the build system for TF-Agents, how to set up a development environment, testing practices, and how to make contributions to the project. It covers the technical aspects of working with the codebase rather than using the library as an end user. For general installation information for users, see [Overview](https://deepwiki.com/tensorflow/agents/1-overview).

 
## Table of Contents

 
 - [Build System Overview](https://github.com/tensorflow/agents/blob/2a236d30/Build System Overview)
 - [Building and Installing from Source](https://github.com/tensorflow/agents/blob/2a236d30/Building and Installing from Source)
 - [Testing Framework](https://github.com/tensorflow/agents/blob/2a236d30/Testing Framework)
 - [Release Process](https://github.com/tensorflow/agents/blob/2a236d30/Release Process)
 - [Contributing Guidelines](https://github.com/tensorflow/agents/blob/2a236d30/Contributing Guidelines)
 
 
## Build System Overview

 TF-Agents uses a Python-based build system centered around `setuptools` for packaging and distribution. The project supports both stable releases and nightly builds, with configurable dependencies to support different versions of TensorFlow and related libraries.

 
```

```

 Sources: [setup.py16-396](https://github.com/tensorflow/agents/blob/2a236d30/setup.py#L16-L396) [pip_pkg.sh1-52](https://github.com/tensorflow/agents/blob/2a236d30/pip_pkg.sh#L1-L52) [tf_agents/version.py16-39](https://github.com/tensorflow/agents/blob/2a236d30/tf_agents/version.py#L16-L39)

 
## Building and Installing from Source

 
### Prerequisites

 Before building TF-Agents from source, you need to have Python (3.8 or newer), pip, and git installed. TF-Agents supports Python 3.9, 3.10, and 3.11.

 
### Development Installation

 To install TF-Agents for development:

 
 - Clone the repository:
 
 
```

```

 
 - Install in development mode with test dependencies:
 
 
```

```

 
 - Install TensorFlow separately (for flexibility with versions):
 
 
```

```

 
 - Set the environment variable to use keras-2 (tf-keras):
 
 
```

```

 
```

```

 Sources: [README.md162-167](https://github.com/tensorflow/agents/blob/2a236d30/README.md?plain=1#L162-L167) [setup.py275-331](https://github.com/tensorflow/agents/blob/2a236d30/setup.py#L275-L331)

 
### Building a Wheel Package

 To build a wheel package for distribution:

 
 - Set the Python version to use for building:
 
 
```

```

 
 - Run the pip package script:
 
 
```

```

 
 - For a release build, add the `--release` flag:
 
 
```

```

 The script will create a wheel file in the specified directory, which can then be installed with pip.

 Sources: [pip_pkg.sh1-52](https://github.com/tensorflow/agents/blob/2a236d30/pip_pkg.sh#L1-L52) [setup.py275-331](https://github.com/tensorflow/agents/blob/2a236d30/setup.py#L275-L331)

 
## Testing Framework

 TF-Agents has a comprehensive testing framework that includes unit tests, integration tests, and tests for Colab notebooks. The testing system is integrated with the build system through custom test commands in `setup.py`.

 
### Running Tests

 To run the tests:

 
```

```

 For release testing:

 
```

```

 
### Test Architecture

 
```

```

 The testing system separates tests into three categories:

 
 - Main grouped tests - Run together in a single process
 - Individual tests - Tests that must be run in separate processes (listed in `test_individually.txt`)
 - Broken tests - Tests that are temporarily disabled (listed in the file specified by `--broken_tests`)
 
 Sources: [setup.py68-166](https://github.com/tensorflow/agents/blob/2a236d30/setup.py#L68-L166) [tests_release.sh151-250](https://github.com/tensorflow/agents/blob/2a236d30/tests_release.sh#L151-L250)

 
### Test Configuration

 Tests can be configured with various flags to control dependencies and test execution:

 
 - `--broken_tests`: Specify a file listing tests to exclude
 - `--tf_version`, `--reverb_version`, etc.: Override specific dependency versions
 - `--release`: Run tests for a stable release build
 
 Sources: [setup.py89-161](https://github.com/tensorflow/agents/blob/2a236d30/setup.py#L89-L161) [tests_release.sh11-116](https://github.com/tensorflow/agents/blob/2a236d30/tests_release.sh#L11-L116)

 
## Release Process

 TF-Agents follows a versioning scheme based on Semantic Versioning, with support for both stable releases and development (nightly) builds.

 
### Version Numbering

 Version numbers follow the format `MAJOR.MINOR.PATCH[SUFFIX]`, where:

 
 - `MAJOR`: Major version, currently 0 (pre-1.0 release)
 - `MINOR`: Minor version, incremented for new features
 - `PATCH`: Patch version, incremented for bug fixes
 - `SUFFIX`: Either empty for stable releases or `dev` for development builds
 
 
```

```

 Sources: [tf_agents/version.py16-39](https://github.com/tensorflow/agents/blob/2a236d30/tf_agents/version.py#L16-L39) [setup.py261-273](https://github.com/tensorflow/agents/blob/2a236d30/setup.py#L261-L273)

 
### Release Types

 TF-Agents provides two types of releases:

 
 - **Stable Releases**: Published as `tf-agents` on PyPI

 
 - Tagged with version numbers like `v0.19.0`
 - Compatible with specific versions of TensorFlow and dependencies
 - Built with `--release` flag
 - **Nightly Builds**: Published as `tf-agents-nightly` on PyPI

 
 - Include the latest features and fixes
 - Built from the master branch
 - Have version numbers with date stamps (e.g., `0.20.0.dev20230215`)
 
 Each release is tested against specific versions of TensorFlow, TF-Probability, Reverb, and other dependencies. The compatibility matrix is documented in the [README.md](https://github.com/tensorflow/agents/blob/2a236d30/README.md?plain=1)

 Sources: [README.md177-214](https://github.com/tensorflow/agents/blob/2a236d30/README.md?plain=1#L177-L214) [setup.py261-273](https://github.com/tensorflow/agents/blob/2a236d30/setup.py#L261-L273) [tests_release.sh197-218](https://github.com/tensorflow/agents/blob/2a236d30/tests_release.sh#L197-L218)

 
### Building and Testing Releases

 The `tests_release.sh` script is used to build and test releases:

 
```

```

 This script:

 
 - Creates a virtual environment
 - Installs dependencies
 - Runs tests
 - Builds a wheel package
 - Optionally tests Colab notebooks
 
 Sources: [tests_release.sh1-262](https://github.com/tensorflow/agents/blob/2a236d30/tests_release.sh#L1-L262)

 
## Contributing Guidelines

 TF-Agents welcomes contributions from the community. The contribution process follows standard GitHub workflows with pull requests.

 
### Development Workflow

 
```

```

 
### Contribution Best Practices

 
 - **Code Style**: Follow the TensorFlow style guide.
 - **Testing**: Add tests for new features and ensure existing tests pass.
 - **Documentation**: Document new features and update existing documentation as needed.
 - **Commit Messages**: Write clear commit messages describing your changes.
 - **Pull Requests**: Create focused pull requests that address specific issues.
 
 
### Testing Your Changes

 Before submitting a pull request, ensure that your changes pass all tests:

 
```

```

 For comprehensive testing, you can use the release test script:

 
```

```

 Sources: [README.md168-176](https://github.com/tensorflow/agents/blob/2a236d30/README.md?plain=1#L168-L176) [CONTRIBUTING.md](https://github.com/tensorflow/agents/blob/2a236d30/CONTRIBUTING.md?plain=1) (referenced in [README.md172-173](https://github.com/tensorflow/agents/blob/2a236d30/README.md?plain=1#L172-L173))

 
## Dependency Management

 TF-Agents has several dependencies, with special handling for key components like TensorFlow, TensorFlow Probability, and Reverb.

 
```

```

 Dependencies are managed in `setup.py` with specific version requirements. For development flexibility, TensorFlow and some other key dependencies can be installed separately from TF-Agents.

 Sources: [setup.py176-232](https://github.com/tensorflow/agents/blob/2a236d30/setup.py#L176-L232) [README.md89-167](https://github.com/tensorflow/agents/blob/2a236d30/README.md?plain=1#L89-L167)

 
### Dependency Version Overrides

 The build system allows overriding default dependency versions with flags:

 
 - `--tf-version`: Override TensorFlow version
 - `--reverb-version`: Override Reverb version
 - `--tfp-version`: Override TensorFlow Probability version
 - `--rlds-version`: Override RLDS version
 - `--tf-keras-version`: Override TF-Keras version
 
 These flags can be passed to `setup.py` or the release test script.

 Sources: [setup.py342-383](https://github.com/tensorflow/agents/blob/2a236d30/setup.py#L342-L383) [tests_release.sh30-102](https://github.com/tensorflow/agents/blob/2a236d30/tests_release.sh#L30-L102)
