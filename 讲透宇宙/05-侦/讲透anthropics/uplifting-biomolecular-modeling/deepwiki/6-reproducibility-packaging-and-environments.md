<!-- source: DeepWiki mcp.deepwiki.com · repo anthropics/uplifting-biomolecular-modeling · page 6 Reproducibility, Packaging and Environments · fetched 2026-10-26 -->

# Reproducibility, Packaging and Environments

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [af2ig/opt/af2ig_opt/stock_cli.py](af2ig/opt/af2ig_opt/stock_cli.py)
- [af2ig/stock/check_pins.py](af2ig/stock/check_pins.py)
- [af3_jax/stock/check_pins.py](af3_jax/stock/check_pins.py)
- [af3_torch/opt/af3_torch_opt/stock_venv.py](af3_torch/opt/af3_torch_opt/stock_venv.py)
- [af3_torch/stock/check_pins.py](af3_torch/stock/check_pins.py)
- [af3_torch/stock/fetch_upstream.py](af3_torch/stock/fetch_upstream.py)
- [boltz2/opt/boltz2_opt/stock_pred.py](boltz2/opt/boltz2_opt/stock_pred.py)
- [boltzgen/environment/requirements.lock](boltzgen/environment/requirements.lock)
- [borzoi/environment/requirements.lock](borzoi/environment/requirements.lock)
- [borzoi/opt/datapath/pipeline_tf/build.py](borzoi/opt/datapath/pipeline_tf/build.py)
- [caliby/environment/requirements.lock](caliby/environment/requirements.lock)
- [chai1/environment/requirements.lock](chai1/environment/requirements.lock)
- [chrombpnet/environment/requirements.lock](chrombpnet/environment/requirements.lock)
- [chrombpnet/opt/chrombpnet_opt/stock_pred_bw.py](chrombpnet/opt/chrombpnet_opt/stock_pred_bw.py)
- [chrombpnet/opt/chrombpnet_opt/weights.py](chrombpnet/opt/chrombpnet_opt/weights.py)
- [chrombpnet/stock/check_pins.py](chrombpnet/stock/check_pins.py)
- [colabfold/environment/requirements.lock](colabfold/environment/requirements.lock)
- [colabfold/stock/check_pins.py](colabfold/stock/check_pins.py)
- [common/opt_core/opt_core/cell_census.py](common/opt_core/opt_core/cell_census.py)
- [common/opt_core/opt_core/mem/peak.py](common/opt_core/opt_core/mem/peak.py)
- [common/opt_core/tests/test_rowpair_e2e_043.py](common/opt_core/tests/test_rowpair_e2e_043.py)
- [e1/environment/requirements.lock](e1/environment/requirements.lock)
- [e1/opt/e1_opt/stock_score.py](e1/opt/e1_opt/stock_score.py)
- [e1/stock/check_pins.py](e1/stock/check_pins.py)
- [ef2inv/environment/requirements.lock](ef2inv/environment/requirements.lock)
- [enformer/stock/check_pins.py](enformer/stock/check_pins.py)
- [flashzoi/stock/check_pins.py](flashzoi/stock/check_pins.py)
- [genie3/environment/requirements.lock](genie3/environment/requirements.lock)
- [openfold3/environment/requirements.lock](openfold3/environment/requirements.lock)
- [openfold3/stock/check_pins.py](openfold3/stock/check_pins.py)
- [openfold3_ob0/environment/requirements.lock](openfold3_ob0/environment/requirements.lock)
- [openfold3_ob0/stock/check_pins.py](openfold3_ob0/stock/check_pins.py)
- [progen2/stock/check_pins.py](progen2/stock/check_pins.py)
- [proteinmpnn/opt/proteinmpnn_opt/weights.py](proteinmpnn/opt/proteinmpnn_opt/weights.py)
- [proteinmpnn/stock/check_pins.py](proteinmpnn/stock/check_pins.py)
- [protenix_v1/environment/requirements.lock](protenix_v1/environment/requirements.lock)
- [pxdesign/opt/pxdesign_opt/cli.py](pxdesign/opt/pxdesign_opt/cli.py)
- [rfdiffusion1/environment/requirements.lock](rfdiffusion1/environment/requirements.lock)
- [rfdiffusion3/environment/requirements.lock](rfdiffusion3/environment/requirements.lock)
- [rosettafold3/environment/requirements.lock](rosettafold3/environment/requirements.lock)

</details>



This page provides a high-level overview of the mechanisms employed to ensure the byte-reproducibility of the inference optimization kits. This includes how dependencies are pinned, model weights are managed, build processes are defined, and execution environments are configured. The goal is to guarantee that a given kit, when run with its specified environment and inputs, will produce identical outputs across different executions and systems.

The core of reproducibility lies in meticulously defining and verifying every component of the kit's stack, from the Python interpreter and installed packages to the exact bytes of upstream code and model weights. This page introduces the key concepts and components involved, with detailed explanations provided in its child pages.

## Pin Verification and Weights

Reproducibility starts with precise pinning of all dependencies and data. Each kit includes a `PINS.json` file that acts as a manifest, detailing the exact versions and cryptographic hashes of critical components. These components include the Python interpreter, installed Python packages, the upstream stock code, and model weights.

The `stock/check_pins.py` script, present in each kit, is central to verifying these pins. It compares the current environment's components against the `PINS.json` specification. For instance, it checks the Python interpreter's version, the versions and member hashes of key Python packages like `torch`, `transformers`, and `tokenizers` [progen2/stock/check_pins.py:52-87](), and the SHA256 digests of the stock files [progen2/stock/check_pins.py:110-121](). For kits that use external model weights, `check_pins.py` also verifies their integrity by comparing their SHA256 hashes against the pinned values [progen2/stock/check_pins.py:117-121]().

Model weights are often large and are managed separately. The `fetch_upstream.py` script (e.g., [af3_torch/stock/fetch_upstream.py]()) handles the acquisition of these weights, ensuring they match the pinned digests. The `weights.py` modules within `opt/` directories (e.g., [chrombpnet/opt/chrombpnet_opt/weights.py](), [proteinmpnn/opt/proteinmpnn_opt/weights.py]()) provide mechanisms for loading and potentially memoizing these weights, further contributing to consistent behavior.

For complex kits like `af3_torch`, which combine components from multiple Python environments (e.g., a JAX venv and a PyTorch venv), a "stock venv" is composed on the fly. This process overlays one environment's distributions onto another, ensuring that the resulting environment precisely matches the pinned configuration for running the stock upstream code [af3_torch/opt/af3_torch_opt/stock_venv.py:1-15]().

For details, see [Pin Verification and Weights](#6.1).

### Pinning and Verification Flow

```mermaid
graph TD
    A[Kit Directory] --> B(PINS.json);
    B --> C{check_pins.py};
    C --> D[Python Interpreter Version];
    C --> E[Python Package Versions/Hashes];
    C --> F[Stock Code File Hashes];
    C --> G[Model Weights Hashes];
    D -- "sys.version_info" --> H[Current Interpreter];
    E -- "importlib.metadata" --> I[Installed Packages];
    F -- "sha256_file()" --> J[Stock Files on Disk];
    G -- "sha256_file()" --> K[Model Weights on Disk];
    H -- "Compare" --> D;
    I -- "Compare" --> E;
    J -- "Compare" --> F;
    K -- "Compare" --> G;
    C -- "Reports discrepancies" --> L[Stderr/JSON Output];
    C -- "Exit Code 0 on success" --> M[Success];
    C -- "Exit Code 3 on failure" --> N[Failure];

    subgraph "PINS.json Contents"
        B_sub1["pins.python"]
        B_sub2["pins.<package_name>"]
        B_sub3["stock_files.files"]
        B_sub4["weights.<size>.files"]
    end

    subgraph "check_pins.py Functions"
        C_sub1[check_interpreter()]
        C_sub2[check_packages()]
        C_sub3[check_stock_files()]
        C_sub4[check_weights()]
    end

    B --> B_sub1;
    B --> B_sub2;
    B --> B_sub3;
    B --> B_sub4;

    C --> C_sub1;
    C --> C_sub2;
    C --> C_sub3;
    C --> C_sub4;

    C_sub1 --> D;
    C_sub2 --> E;
    C_sub3 --> F;
    C_sub4 --> G;
```
Sources: [progen2/stock/check_pins.py:1-242](), [colabfold/stock/check_pins.py:1-212](), [af3_torch/stock/check_pins.py:1-154](), [openfold3_ob0/stock/check_pins.py:1-161](), [af3_torch/opt/af3_torch_opt/stock_venv.py:1-177]()

## Environments, Containers and GPU Configs

The execution environment is critical for reproducibility. Each kit defines its dependencies in `environment/requirements.lock` files (e.g., [caliby/environment/requirements.lock](), [protenix_v1/environment/requirements.lock](), [rfdiffusion3/environment/requirements.lock](), [openfold3/environment/requirements.lock]()). These files are generated using `pip freeze` or similar tools and list every Python package and its exact version, including direct and transitive dependencies. Some kits also specify `git+https` URLs with commit hashes for upstream packages [caliby/environment/requirements.lock:25,33,144]().

Containerization is used to encapsulate these environments. `Dockerfile` or `apptainer.def` files (not shown in provided snippets, but implied by context) build images based on these `requirements.lock` files, ensuring a consistent operating system, system libraries, and Python environment. These container definitions often install packages with `--no-deps` to strictly adhere to the lock file [caliby/environment/requirements.lock:10-11](), [protenix_v1/environment/requirements.lock:11-13](), [rfdiffusion3/environment/requirements.lock:4-6]().

GPU-specific configurations are managed through `configs/{a100,h100,h200}.env` files. These files define environment variables and settings tailored to different NVIDIA GPU architectures, influencing aspects like CUDA versions, cuDNN, and other performance-critical libraries. The `_build_backend.py` script (not shown) and `pyproject.toml` files (not shown) handle the packaging and build processes, ensuring that any compiled components (e.g., custom CUDA kernels) are built against the correct environment and GPU architecture.

For details, see [Environments, Containers and GPU Configs](#6.2).

### Environment Definition and Build Process

```mermaid
graph TD
    A[Kit Directory] --> B(environment/requirements.lock);
    B --> C(Dockerfile / apptainer.def);
    C --> D[Container Image];
    D --> E[Runtime Environment];

    B_sub1["# Python interpreter version"]
    B_sub2["# System OS/CUDA base"]
    B_sub3["Package==Version"]
    B_sub4["Package @ git+https://..."]

    B --> B_sub1;
    B --> B_sub2;
    B --> B_sub3;
    B --> B_sub4;

    C --> F[configs/{a100,h100,h200}.env];
    F --> E;

    G[_build_backend.py] --> D;
    H[pyproject.toml] --> G;
```
Sources: [caliby/environment/requirements.lock:1-212](), [protenix_v1/environment/requirements.lock:1-146](), [rfdiffusion3/environment/requirements.lock:1-141](), [openfold3/environment/requirements.lock:1-124]()

## Licensing and Third-Party Notices

Maintaining legal compliance is an integral part of reproducibility and distribution. The repository includes a top-level `LICENSE` and `NOTICE` file, which apply to the overall codebase. Each individual kit also contains its own `LICENSE` file, detailing the specific licensing terms for that kit's components.

Furthermore, the `third_party_licenses/` directory (not shown) contains inventories of licenses for all third-party dependencies, including vendored kernels and forks of upstream projects. This ensures clear provenance and compliance with open-source licenses, providing transparency regarding the origin and licensing of all code and data within each kit.

For details, see [Licensing and Third-Party Notices](#6.3).
Sources: (No specific file citations provided for this section, relying on general repository structure and common practices for open-source projects.)

---

