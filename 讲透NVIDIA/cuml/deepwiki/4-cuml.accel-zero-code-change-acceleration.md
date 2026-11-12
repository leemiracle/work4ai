<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/cuml · page 4 cuml.accel — Zero Code Change Acceleration · fetched 2026-10-26 -->

# cuml.accel — Zero Code Change Acceleration

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [ci/run_cuml_singlegpu_accel_pytests.sh](ci/run_cuml_singlegpu_accel_pytests.sh)
- [docs/source/_static/open-details-on-fragment.js](docs/source/_static/open-details-on-fragment.js)
- [docs/source/cuml-accel/examples/getting_started.ipynb](docs/source/cuml-accel/examples/getting_started.ipynb)
- [docs/source/cuml-accel/examples/plot_kmeans_digits.ipynb](docs/source/cuml-accel/examples/plot_kmeans_digits.ipynb)
- [docs/source/cuml-accel/examples/third-party-apps.rst](docs/source/cuml-accel/examples/third-party-apps.rst)
- [docs/source/cuml-accel/faq.rst](docs/source/cuml-accel/faq.rst)
- [docs/source/cuml-accel/index.rst](docs/source/cuml-accel/index.rst)
- [docs/source/cuml-accel/logging-and-profiling.rst](docs/source/cuml-accel/logging-and-profiling.rst)
- [docs/source/cuml-accel/usage.rst](docs/source/cuml-accel/usage.rst)
- [python/cuml/cuml/accel/__init__.py](python/cuml/cuml/accel/__init__.py)
- [python/cuml/cuml/accel/__main__.py](python/cuml/cuml/accel/__main__.py)
- [python/cuml/cuml/accel/accelerator.py](python/cuml/cuml/accel/accelerator.py)
- [python/cuml/cuml/accel/core.py](python/cuml/cuml/accel/core.py)
- [python/cuml/cuml/accel/estimator_proxy.py](python/cuml/cuml/accel/estimator_proxy.py)
- [python/cuml/cuml/internals/interop.py](python/cuml/cuml/internals/interop.py)
- [python/cuml/cuml_accel_tests/test_accelerator.py](python/cuml/cuml_accel_tests/test_accelerator.py)
- [python/cuml/cuml_accel_tests/test_cli.py](python/cuml/cuml_accel_tests/test_cli.py)
- [python/cuml/cuml_accel_tests/test_core.py](python/cuml/cuml_accel_tests/test_core.py)
- [python/cuml/cuml_accel_tests/test_estimator_proxy.py](python/cuml/cuml_accel_tests/test_estimator_proxy.py)
- [python/cuml/cuml_accel_tests/test_logging.py](python/cuml/cuml_accel_tests/test_logging.py)

</details>



## Purpose and Scope

`cuml.accel` provides zero-code-change GPU acceleration for popular machine learning libraries—specifically scikit-learn, UMAP (`umap-learn`), and HDBSCAN—by intercepting Python module imports and dispatching estimator calls to cuML's GPU backends with transparent CPU fallback [docs/source/cuml-accel/index.rst:4-40](). 

This page serves as a high-level parent overview of the accelerator architecture. For comprehensive technical details, consult the following child pages:
- **4.1 Accelerator Internals: Proxy Estimators and Module Loader** — Detailed breakdown of `ProxyBase`, `ArrayAPIProxyBase`, import hooks in `accelerator.py`, `core.install()`, CLI `__main__`, IPython magics, and profilers.
- **4.2 Overrides and Compatibility Policy** — Family-specific `_overrides/sklearn` modules, `UnsupportedOnGPU` fallback semantics, and documented behavior differences.
- **4.3 Upstream Test Suite Harness and xfail Management** — Execution mechanics for upstream scikit-learn and UMAP test suites under `cuml.accel`, `xfail-list.yaml` management, and result summarization.

---

## High-Level Architecture and Import Interception

When enabled, `cuml.accel` registers custom import hooks via an `Accelerator` instance defined in `python/cuml/cuml/accel/core.py` [python/cuml/cuml/accel/core.py:172-183](). When a user imports modules such as `sklearn.linear_model`, `umap`, or `hdbscan`, the module loader intercepts the import and substitutes accelerated proxy classes (`ProxyBase`) that wrap underlying GPU-accelerated cuML estimators.

```mermaid
graph TD
    UserScript["User Code\n\"from sklearn.linear_model import LogisticRegression\""] --> ImportSystem["Python Import System"]
    ImportSystem --> AccelHook["cuml.accel.core.ACCEL\n\"Accelerator(exclude=_exclude_from_acceleration)\""]
    
    AccelHook --> CheckModule{"Module in _OVERRIDES?"}
    CheckModule -- Yes --> LoadOverride["Load Override Module\n\"cuml.accel._overrides.sklearn.linear_model\""]
    CheckModule -- No --> LoadStandard["Load Standard CPU Module"]
    
    LoadOverride --> ProxyClass["ProxyEstimator\n\"ProxyBase\" subclass"]
    ProxyClass --> GPUBackend["cuML GPU Estimator\n\"InteropMixin\""]
    
    Sources["Sources: python/cuml/cuml/accel/core.py:153-183, python/cuml/cuml/accel/estimator_proxy.py:174-180"]
```

Sources: `python/cuml/cuml/accel/core.py:153-183`, `python/cuml/cuml/accel/estimator_proxy.py:174-180`

---

## Dispatch Mechanism and CPU Fallback

Estimators managed by `cuml.accel` maintain hyperparameters and metadata through a paired CPU estimator instance while delegating heavy computational tasks (such as `fit`, `predict`, and `transform`) to GPU implementations [python/cuml/cuml/accel/estimator_proxy.py:180](). 

If an unsupported hyperparameter, data format, or edge case is encountered, the GPU implementation raises `UnsupportedOnGPU`. The proxy layer transparently catches this exception, synchronizes state, and falls back to the native CPU estimator execution path without interrupting the user workflow [docs/source/cuml-accel/index.rst:37-43]().

```mermaid
graph TD
    MethodCall["User calls \"model.fit(X, y)\""] --> ProxyMethod["ProxyBase Method Dispatch"]
    ProxyMethod --> TryGPU{"GPU Implementation\n\"_gpu_class\" available & supported?"}
    
    TryGPU -- Yes --> ExecGPU["Execute on GPU\n(cuML libcuml / RAFT)"]
    ExecGPU --> CheckSuccess{"Succeeds?"}
    CheckSuccess -- Yes --> ReturnGPU["Return GPU Results"]
    CheckSuccess -- No / Unsupported --> Fallback["Raise \"UnsupportedOnGPU\""]
    
    TryGPU -- No --> Fallback
    
    Fallback --> ExecCPU["Execute on CPU\n(\"_cpu_class\" model)"]
    ExecCPU --> ReturnCPU["Return CPU Results"]
    
    Sources["Sources: python/cuml/cuml/accel/estimator_proxy.py:174-180, python/cuml/cuml/internals/interop.py:17-105"]
```

Sources: `python/cuml/cuml/accel/estimator_proxy.py:174-180`, `python/cuml/cuml/internals/interop.py:17-105`

---

## Activation Methods

`cuml.accel` supports multiple activation entry points to accommodate scripts, interactive notebooks, and automated testing pipelines:

1. **Command-Line Interface (CLI)**: Invoke scripts or modules using the accelerator runner wrapper [python/cuml/cuml/accel/__main__.py:21-48]().
   ```bash
   python -m cuml.accel myscript.py
   python -m cuml.accel -m mymodule --option
   ```
2. **Jupyter / IPython Magics**: Load the extension at the start of a notebook session [python/cuml/cuml/accel/__init__.py:8]().
   ```ipython
   %load_ext cuml.accel
   ```
3. **Programmatic Installation**: Enable acceleration explicitly inside Python code [python/cuml/cuml/core.py]().
   ```python
   import cuml.accel
   cuml.accel.install(log_level="info")
   ```
4. **Environment Variable**: Automatically enable acceleration via environment configuration [python/cuml/cuml_accel_tests/test_cli.py:180-198]().
   ```bash
   export CUML_ACCEL_ENABLED=true
   ```

Sources: `python/cuml/cuml/accel/__main__.py:21-48`, `python/cuml/cuml/accel/__init__.py:6-9`, `python/cuml/cuml/accel/core.py:212-217`, `python/cuml/cuml_accel_tests/test_cli.py:180-198`

---

## Child Pages

For further technical depth, refer to the child documentation modules:
- [Accelerator Internals: Proxy Estimators and Module Loader](#4.1)
- [Overrides and Compatibility Policy](#4.2)
- [Upstream Test Suite Harness and xfail Management](#4.3)

Sources: `docs/source/cuml-accel/index.rst:62-72`

---

