# Customizing the Cosmos Evaluator

This section of the documentation describes how to set up the build system, lint, and unit test. After following these steps, you will have everything you need to begin running the code from source.

## Build Setup

Cosmos Evaluator uses **Dazel** — Bazel running inside Docker — for hermetic, reproducible builds. Follow these steps to set up Dazel on your machine.

### Linux Setup

```bash
# Clone the repository
git clone https://github.com/NVIDIA/cosmos-evaluator.git
cd cosmos-evaluator

# Source the build environment
source tools/env_setup.sh

# Verify the build works
dazel build //...
```

### macOS Setup

macOS requires Colima with specific settings due to filesystem compatibility requirements:

```bash
# Clone the repository
git clone https://github.com/NVIDIA/cosmos-evaluator.git
cd cosmos-evaluator

# Install Colima
brew install colima docker

# Start Colima with QEMU and 9p mount (both required)
colima start --cpu 4 --memory 8 --disk 60 --vm-type qemu --mount-type 9p

```

Create a `user.dazelrc` file at the repository root for macOS compatibility:

```python
# user.dazelrc — macOS overrides
import subprocess

# Fix group detection (getent not available on macOS)
DAZEL_DOCKER_RUN_FLAGS += ["-e", "GROUP_ID=1000"]

# Disable GPU (not available on macOS)
DAZEL_DOCKER_RUN_FLAGS = [f for f in DAZEL_DOCKER_RUN_FLAGS if '--gpus' not in f]
```

Then build:

```bash
source tools/env_setup.sh
dazel build //...    # ~5 min first build, ~4 sec cached
```

> **Note:** GPU-dependent features (Objects check's SegFormer/CWIP models and Physical Plausibility's default configuration) require a Linux machine with an NVIDIA GPU. macOS can run the Hallucination and Attribute Verification checks and non-GPU code paths.


## Linting and Formatting

If you are making a local change and would like to run the linter:

```bash
# Auto-fix lint and formatting issues
dazel fix

# Check for violations without fixing
dazel lint
```

## Running Unit Tests

```bash
# All tests
dazel test //...

# Specific module tests (tests live in each package's tests/ subpackage)
dazel test //checks/objects/single_view/tests:all
dazel test //checks/hallucination/tests:all
dazel test //checks/attribute_verification/tests:all
dazel test //checks/physical_plausibility/tests:all
dazel test //services/objects/single_view/tests:all
dazel test //services/hallucination/tests:all
dazel test //services/attribute_verification/tests:all
dazel test //services/physical_plausibility/tests:all
```

## Project Structure

```bash
cosmos-evaluator/
├── checks/                         # Evaluation modules
│   ├── attribute_verification/     # Attribute verification check
│   ├── cosmos_evaluator.yaml       # Central configuration
│   ├── hallucination/              # Hallucination check
│   ├── objects/single_view/        # Object correspondence check
│   ├── physical_plausibility/      # Physical plausibility check
│   ├── sample_data/                # Sample fixtures used by tests/docs
│   └── utils/                      # Shared utilities (video I/O, data loading, transforms)
├── database/                       # PostgreSQL container + shared DB utilities
├── docs/                           # This documentation
├── services/                       # REST API microservices
│   ├── arbitrator/                 # Orchestration coordinator service
│   ├── attribute_verification/     # Attribute verification service
│   ├── database/                   # Database REST API service
│   ├── framework/                  # Base classes and protocols
│   ├── hallucination/              # Hallucination service
│   ├── objects/single_view/        # Single-view objects service
│   └── physical_plausibility/      # Physical plausibility service
├── tools/                          # Build infra (dazel, lint, format, env_setup.sh)
├── utils/                          # Cross-cutting utilities (bazel, environment, s3)
├── third_party                     # External dependencies
```

## Configuration

Check defaults live in `checks/cosmos_evaluator.yaml`, keyed per check (e.g. `av.objects_single_view`); edit it, or
select an alternate file with a runner's `--config <name>` flag. A non-empty `config` sent by a REST caller
**replaces** these defaults entirely — if you specify one it must be the **full** configuration (no partial configs,
no assumed defaults), so each run is self-describing. Omitting `config`, or sending `null` or an empty `{}`, is
treated identically and uses the image defaults. See each check's README / `docs/checks/` page for its specific knobs.

## Next Steps

Dive into one of the existing checkers, or create your own!

- [Hallucination Check Guide](checks/hallucination.md) — Details on the hallucination checker
- [Objects Check Guide](checks/objects.md) — Details on the objects checker
- [Attribute Verification Check Guide](checks/attribute_verification.md) — Details on the attribute verification checker
- [Physical Plausibility Check Guide](checks/physical_plausibility.md) — Details on the physical plausibility checker
- [Custom Checker Tutorial](tutorials/custom_checker.md) — Build your own check from scratch
- [Service Framework Guide](services/framework.md) — Building and deploying a microservice around your custom check
- [Orchestration Layer Guide](services/orchestration.md) — Coordinate multiple checkers with the Arbitrator and Database REST API
