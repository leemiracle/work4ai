> 来源: [https://deepwiki.com/kvcache-ai/ktransformers/11-development](https://deepwiki.com/kvcache-ai/ktransformers/11-development)
> DeepWiki kvcache-ai/ktransformers | Last indexed: 30 April 2026 (02be2b

# Development

  Relevant source files 
 - [.github/CODE_OF_CONDUCT.md](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/.github/CODE_OF_CONDUCT.md?plain=1)
 - [.github/PULL_REQUEST_TEMPLATE.md](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/.github/PULL_REQUEST_TEMPLATE.md?plain=1)
 - [kt-kernel/pytest.ini](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/kt-kernel/pytest.ini)
 - [kt-kernel/scripts/README.md](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/kt-kernel/scripts/README.md?plain=1)
 - [kt-kernel/scripts/convert_gpu_weights.py](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/kt-kernel/scripts/convert_gpu_weights.py)
 - [kt-kernel/test/__init__.py](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/kt-kernel/test/__init__.py)
 - [kt-kernel/test/ci/__init__.py](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/kt-kernel/test/ci/__init__.py)
 - [kt-kernel/test/ci/ci_register.py](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/kt-kernel/test/ci/ci_register.py)
 - [kt-kernel/test/ci/ci_utils.py](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/kt-kernel/test/ci/ci_utils.py)
 - [kt-kernel/test/per_commit/__init__.py](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/kt-kernel/test/per_commit/__init__.py)
 - [kt-kernel/test/per_commit/test_amd_placeholder.py](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/kt-kernel/test/per_commit/test_amd_placeholder.py)
 
  This page provides an overview of KTransformers' development architecture and workflows for contributors. It covers the core extension patterns, Python-C++ interface design, and development practices needed to add new features or backends to the project.

 For detailed guides on specific topics, see:

 
 - C++ operator development: [C++ Extension Development](https://deepwiki.com/kvcache-ai/ktransformers/11.1-c++-extension-development)
 - Testing infrastructure: [Testing Framework](https://deepwiki.com/kvcache-ai/ktransformers/11.2-testing-framework)
 - Release automation: [CI/CD Pipeline](https://deepwiki.com/kvcache-ai/ktransformers/11.3-cicd-pipeline)
 - Contribution process: [Contributing Guidelines](https://deepwiki.com/kvcache-ai/ktransformers/11.4-contributing-guidelines)
 
 
---

 
## Project Architecture for Developers

 KTransformers follows a dual-language architecture where performance-critical kernels are implemented in C++ and exposed to Python via `pybind11`. The system uses a factory pattern to support multiple backend implementations while maintaining a unified Python API.

 
### Module Structure

 
```

```

 **Sources:** [kt-kernel/python/experts.py1-155](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/kt-kernel/python/experts.py#L1-L155) [kt-kernel/python/experts_base.py1-50](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/kt-kernel/python/experts_base.py#L1-L50) [kt-kernel/ext_bindings.cpp1-739](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/kt-kernel/ext_bindings.cpp#L1-L739)

 
---

 
## Python-C++ Interface Design

 The Python-C++ boundary uses `pybind11` with a carefully designed interface that supports asynchronous task submission, NUMA-aware threading, and zero-copy memory access.

 
### Binding Architecture

 
```

```

 **Key Binding Patterns:**

 
| Pattern | Purpose | Implementation |
|---|---|---|
| Task Pattern | Deferred execution on worker threads | kt-kernel/ext_bindings.cpp198-227 |
| Pointer Conversion | Zero-copy tensor access | kt-kernel/ext_bindings.cpp143-153 |
| Shared Ownership | Lifetime management across languages | kt-kernel/ext_bindings.cpp235-240 |
| Property Macros | Pointer property exposure | kt-kernel/ext_bindings.cpp143-153 |

 **Sources:** [kt-kernel/ext_bindings.cpp143-227](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/kt-kernel/ext_bindings.cpp#L143-L227) [kt-kernel/ext_bindings.cpp302-739](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/kt-kernel/ext_bindings.cpp#L302-L739)

 
---

 
## Testing and Quality Assurance

 KTransformers uses a hardware-aware testing framework adapted from SGLang. This system allows developers to register tests for specific backends (CPU, CUDA, AMD) and manage execution with timeouts.

 
### Test Registration System

 Tests are registered using decorators or function calls that the CI registry parses to build a test suite.

 
```

```

 **Key Testing Components:**

 
 - **CI Registry**: Manages hardware-specific test metadata via `CIRegistry` [kt-kernel/test/ci/ci_register.py15-20](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/kt-kernel/test/ci/ci_register.py#L15-L20)
 - **Hardware Mapping**: Maps backends like `CPU`, `CUDA`, and `AMD` to specific registration functions like `register_amd_ci` [kt-kernel/test/ci/ci_register.py34-38](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/kt-kernel/test/ci/ci_register.py#L34-L38)
 - **Timeout Control**: The `run_with_timeout` utility ensures long-running kernels do not hang the CI pipeline [kt-kernel/test/ci/ci_utils.py54-75](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/kt-kernel/test/ci/ci_utils.py#L54-L75)
 - **Test Discovery**: `RegistryVisitor` uses Python's `ast` module to parse test files and collect CI metadata [kt-kernel/test/ci/ci_register.py41-88](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/kt-kernel/test/ci/ci_register.py#L41-L88)
 - **Placeholder Support**: The framework supports placeholders for upcoming backends like AMD/ROCm [kt-kernel/test/per_commit/test_amd_placeholder.py1-37](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/kt-kernel/test/per_commit/test_amd_placeholder.py#L1-L37)
 
 For details, see [Testing Framework](https://deepwiki.com/kvcache-ai/ktransformers/11.2-testing-framework).

 **Sources:** [kt-kernel/test/ci/ci_register.py1-113](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/kt-kernel/test/ci/ci_register.py#L1-L113) [kt-kernel/test/ci/ci_utils.py1-171](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/kt-kernel/test/ci/ci_utils.py#L1-L171) [kt-kernel/test/per_commit/test_amd_placeholder.py1-37](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/kt-kernel/test/per_commit/test_amd_placeholder.py#L1-L37) [kt-kernel/pytest.ini1-28](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/kt-kernel/pytest.ini#L1-L28)

 
---

 
## Factory Pattern and Backend Selection

 The `KTMoEWrapper` class uses `__new__()` to implement a factory pattern that returns different backend implementations based on the `method` parameter.

 
### Factory Implementation

 
```

```

 **Implementation Details:** [kt-kernel/python/experts.py53-120](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/kt-kernel/python/experts.py#L53-L120) shows the factory logic:

 
```

```

 **Sources:** [kt-kernel/python/experts.py53-120](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/kt-kernel/python/experts.py#L53-L120)

 
---

 
## Release and Contribution

 
### CI/CD Pipeline

 The project utilizes GitHub Actions for automated building and testing. The pipeline handles multi-variant wheel building for different CPU architectures and manages Docker image releases. For details, see [CI/CD Pipeline](https://deepwiki.com/kvcache-ai/ktransformers/11.3-cicd-pipeline).

 
### Contributing Guidelines

 Contributors are expected to follow the standard pull request process, including writing new tests for features and adhering to the project's code style. A `PULL_REQUEST_TEMPLATE` is provided to ensure all requirements are met before submission [.github/PULL_REQUEST_TEMPLATE.md1-8](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/.github/PULL_REQUEST_TEMPLATE.md?plain=1#L1-L8)

 The community follows a Code of Conduct to ensure a healthy environment [.github/CODE_OF_CONDUCT.md1-85](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/.github/CODE_OF_CONDUCT.md?plain=1#L1-L85) For details, see [Contributing Guidelines](https://deepwiki.com/kvcache-ai/ktransformers/11.4-contributing-guidelines).

 **Sources:** [.github/PULL_REQUEST_TEMPLATE.md1-8](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/.github/PULL_REQUEST_TEMPLATE.md?plain=1#L1-L8) [.github/CODE_OF_CONDUCT.md1-85](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/.github/CODE_OF_CONDUCT.md?plain=1#L1-L85)
