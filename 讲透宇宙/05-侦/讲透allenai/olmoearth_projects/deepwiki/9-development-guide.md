<!-- source: DeepWiki mcp.deepwiki.com · repo allenai/olmoearth_projects · page 9 Development Guide · fetched 2026-10-26 -->

# Development Guide

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/workflows/build-test.yml](.github/workflows/build-test.yml)
- [Dockerfile](Dockerfile)
- [docs/internal.md](docs/internal.md)
- [olmoearth_projects/utils/label_quality/__init__.py](olmoearth_projects/utils/label_quality/__init__.py)
- [olmoearth_run_data/sample/model.yaml](olmoearth_run_data/sample/model.yaml)
- [olmoearth_run_data/satlas_solar_farm/model.yaml](olmoearth_run_data/satlas_solar_farm/model.yaml)
- [pyproject.toml](pyproject.toml)
- [tests/integration/olmoearth_run/test_olmoearth_run.py](tests/integration/olmoearth_run/test_olmoearth_run.py)
- [tests/unit/utils/label_quality/test_wrapper.py](tests/unit/utils/label_quality/test_wrapper.py)
- [uv.lock](uv.lock)

</details>



This guide covers the complete development workflow for contributing to the olmoearth_projects repository, including environment setup, testing procedures, CI/CD processes, and the bifurcated development model between rslearn_projects (research/development) and olmoearth_projects (production/deployment). For information about training models and fine-tuning, see [Model Training](#5). For information about running inference, see [Inference and Deployment](#7).

---

## Development Environment Setup

The repository uses `uv` for fast, reliable Python dependency management and requires Python 3.11 or higher.

### Dependency Management

The project's dependencies are defined in [pyproject.toml:12-21]() and locked in [uv.lock](). The main dependencies include:

| Package | Purpose |
|---------|---------|
| `rslearn[extra]>=0.0.18` | Core training and data processing framework |
| `olmoearth-runner>=0.1.10` | Inference pipeline execution |
| `olmoearth_pretrain` | OlmoEarth encoder models |
| `geopandas>=1.1.1` | Geospatial data manipulation |
| `wandb>=0.21` | Experiment tracking |
| `PyYAML>=6` | Configuration file parsing |

### Local Development Setup

```bash
# Install uv if not already installed
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone the repository
git clone https://github.com/allenai/olmoearth_projects.git
cd olmoearth_projects

# Create virtual environment and install dependencies
uv sync --all-extras

# Activate the virtual environment
source .venv/bin/activate
```

### Development Dependencies

Additional development tools are specified in [pyproject.toml:24-34]() and include:

- **ruff** (>=0.7): Fast Python linter and formatter
- **mypy** (>=1.17.1): Static type checker
- **pytest** (>=8.2): Testing framework
- **pre-commit** (>=4.3.0): Git hook management
- **interrogate** (>=1.7.0): Docstring coverage checker

**Sources**: [pyproject.toml:1-67](), [uv.lock:1-21]()

---

## Development Workflow Architecture

The repository follows a bifurcated development model where code progresses through distinct stages from research to production.

### Workflow Overview Diagram

```mermaid
graph TB
    subgraph "rslearn_projects Repository"
        DEV_CODE["rslp/[project_name]/<br/>Data Curation Scripts<br/>Window Creation Code"]
        DEV_CONFIG["data/[project_name]/<br/>[version_id]/<br/>dataset.json<br/>model.yaml"]
        DEV_DATASET["WEKA Storage<br/>/weka/dfive-default/<br/>rslearn-eai/datasets/"]
        DEV_TRAIN["Fine-tuning Jobs<br/>Beaker/Saturn Cluster<br/>GPU Training"]
        DEV_CHECKPOINT["Model Checkpoints<br/>WEKA Storage<br/>epoch=X-step=Y.ckpt"]
    end
    
    subgraph "olmoearth_projects Repository"
        PROD_CONFIG["olmoearth_run_data/<br/>[project_name]/<br/>model.yaml<br/>dataset.json<br/>olmoearth_run.yaml"]
        PROD_CODE["olmoearth_projects/<br/>[project_name]/<br/>Supporting Code"]
        PROD_GCS["GCS Storage<br/>gs://rslearn-eai/<br/>model_checkpoints/"]
        PROD_INFERENCE["OlmoEarth Studio<br/>Production Inference<br/>olmoearth_run Pipeline"]
    end
    
    DEV_CODE --> DEV_CONFIG
    DEV_CONFIG --> DEV_DATASET
    DEV_DATASET --> DEV_TRAIN
    DEV_TRAIN --> DEV_CHECKPOINT
    
    DEV_CONFIG -->|"Copy configs"| PROD_CONFIG
    DEV_CODE -->|"Copy supporting code"| PROD_CODE
    DEV_CHECKPOINT -->|"Publish for inference"| PROD_GCS
    
    PROD_CONFIG --> PROD_INFERENCE
    PROD_CODE --> PROD_INFERENCE
    PROD_GCS --> PROD_INFERENCE
```

**Sources**: [docs/internal.md:1-56](), Diagram 5 from high-level architecture

### Project Code Organization

When developing a new model or application, code should be organized according to this structure:

**In rslearn_projects (Development Phase)**:
1. Data curation and window creation scripts: `rslp/[project_name]/`
2. Configuration files: `data/[project_name]/[version_id]/`
3. rslearn datasets: `/weka/dfive-default/rslearn-eai/datasets/[project_name]/[version_id]`

**In olmoearth_projects (Deployment Phase)**:
1. Deployment configurations: `olmoearth_run_data/[project_name]/`
2. Supporting code: `olmoearth_projects/[project_name]/`
3. Model checkpoints: `gs://rslearn-eai/model_checkpoints/[project_name]/`

**Sources**: [docs/internal.md:3-29]()

### Development Process Flow

```mermaid
graph LR
    IDEA["New Model<br/>Concept"] --> CURATE["Data Curation<br/>rslp/[project]/"]
    CURATE --> WINDOWS["Window Creation<br/>create_windows_*.py"]
    WINDOWS --> QUALITY["Quality Assessment<br/>check_label_quality"]
    QUALITY --> DATASET["rslearn Dataset<br/>/weka/.../datasets/"]
    DATASET --> TRAIN["Fine-tuning<br/>rslp_finetuning.py"]
    TRAIN --> CHECKPOINT["Checkpoint<br/>/weka/.../checkpoints/"]
    CHECKPOINT --> COPY["Copy to<br/>olmoearth_projects"]
    COPY --> DEPLOY["Deploy to<br/>OlmoEarth Studio"]
```

**Sources**: [docs/internal.md:3-29](), Diagram 5 from high-level architecture

---

## Testing Infrastructure

The repository includes comprehensive unit and integration tests to ensure code quality and functionality.

### Test Organization Structure

```mermaid
graph TB
    subgraph "Test Suite Organization"
        TEST_ROOT["tests/"]
        UNIT["unit/<br/>Fast, Isolated Tests"]
        INTEGRATION["integration/<br/>End-to-End Tests"]
        
        UNIT_LQ["unit/utils/label_quality/<br/>test_wrapper.py<br/>test_spatial_clustering.py<br/>test_spatial_extent.py<br/>test_label_imbalance.py"]
        
        INT_OER["integration/olmoearth_run/<br/>test_olmoearth_run.py<br/>Full Pipeline Tests"]
    end
    
    TEST_ROOT --> UNIT
    TEST_ROOT --> INTEGRATION
    UNIT --> UNIT_LQ
    INTEGRATION --> INT_OER
```

### Unit Tests

Unit tests focus on testing individual components in isolation. They are fast and do not require external resources like GPUs or cloud storage.

**Example: Label Quality Tests**

The label quality utilities have unit tests at [tests/unit/utils/label_quality/test_wrapper.py:1-23]():

```python
# Unit test structure
def test_label_quality_wrapper() -> None:
    # Create test data
    gdf = gpd.GeoDataFrame(...)
    
    # Run the function being tested
    check_label_quality(gdf, checks_to_run=["label_imbalance"])
    
    # Assertions would go here
```

Unit tests verify components like:
- **label_imbalance**: Checks class distribution balance
- **spatial_clustering**: Measures spatial autocorrelation using F1 score
- **spatial_extent**: Analyzes geographic coverage

The `check_label_quality` function at [olmoearth_projects/utils/label_quality/__init__.py:14-61]() orchestrates multiple checks and displays results in a formatted table.

**Running Unit Tests**:
```bash
# Run all unit tests
pytest tests/unit -vv

# Run specific test file
pytest tests/unit/utils/label_quality/test_wrapper.py -vv
```

**Sources**: [tests/unit/utils/label_quality/test_wrapper.py:1-23](), [olmoearth_projects/utils/label_quality/__init__.py:1-61]()

### Integration Tests

Integration tests validate complete workflows, including data loading, model inference, and result generation. These tests may require access to cloud resources and take longer to execute.

**Example: OlmoEarth Run Pipeline Test**

The [tests/integration/olmoearth_run/test_olmoearth_run.py:21-119]() test validates the entire inference pipeline:

```mermaid
graph LR
    SETUP["Test Setup<br/>tmp_path<br/>config_dir"] --> CONFIG["Copy Configs<br/>dataset.json<br/>model.yaml<br/>olmoearth_run.yaml"]
    CONFIG --> CUSTOMIZE["Customize<br/>Request Geometry<br/>Small AOI"]
    CUSTOMIZE --> EXECUTE["olmoearth_run()<br/>Full Pipeline"]
    EXECUTE --> VALIDATE["Validate Output<br/>Check GeoTIFF<br/>Solar Farm %"]
```

The test performs:
1. Creates a small test area centered on a known solar farm
2. Configures the pipeline with single-window processing
3. Executes the full `olmoearth_run` pipeline
4. Validates the output raster contains expected solar farm percentage

**Running Integration Tests**:
```bash
# Run all integration tests (requires GCP credentials)
pytest tests/integration -vv --forked

# Run with pytest-xdist for parallelization
pytest tests/integration -vv --forked -n auto
```

**Sources**: [tests/integration/olmoearth_run/test_olmoearth_run.py:1-119]()

### Test Configuration

Test configuration is defined in [pyproject.toml:60-66]():

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = ["--import-mode=importlib"]
```

The `--forked` flag in integration tests ensures each test runs in an isolated process, preventing memory leaks from model loading.

**Sources**: [pyproject.toml:60-66]()

---

## CI/CD Pipeline

The repository uses GitHub Actions for continuous integration and deployment, automatically building Docker images and running tests on every push and pull request.

### GitHub Actions Workflow

```mermaid
graph TB
    TRIGGER["Trigger<br/>Push to main<br/>Pull Request"] --> BUILD["Build Job<br/>ubuntu-latest"]
    
    subgraph "Build Job Steps"
        CHECKOUT["Checkout Code<br/>actions/checkout@v4"]
        LOGIN["Docker Login<br/>ghcr.io"]
        META["Extract Metadata<br/>Tags & Labels"]
        CLEANUP["Cleanup Disk<br/>Remove Docker Images"]
        BUILD_PUSH["Build & Push<br/>Docker Image"]
        STORE["Store Image Name<br/>Output to test job"]
    end
    
    subgraph "Test Job Steps"
        TEST_CHECKOUT["Checkout Code"]
        TEST_LOGIN["Docker Login"]
        PULL["Pull Built Image"]
        GCP_AUTH["GCP Auth<br/>Service Account"]
        UNIT_TEST["Run Unit Tests<br/>pytest tests/unit"]
        INT_TEST["Run Integration Tests<br/>pytest tests/integration"]
        CLEANUP_TEST["Cleanup<br/>Prune Images"]
    end
    
    BUILD --> CHECKOUT
    CHECKOUT --> LOGIN
    LOGIN --> META
    META --> CLEANUP
    CLEANUP --> BUILD_PUSH
    BUILD_PUSH --> STORE
    
    STORE --> TEST_CHECKOUT
    TEST_CHECKOUT --> TEST_LOGIN
    TEST_LOGIN --> PULL
    PULL --> GCP_AUTH
    GCP_AUTH --> UNIT_TEST
    UNIT_TEST --> INT_TEST
    INT_TEST --> CLEANUP_TEST
```

### Build Job Configuration

The build job is defined in [.github/workflows/build-test.yml:19-75]() and performs:

1. **Checkout**: Clone the repository
2. **Docker Login**: Authenticate to GitHub Container Registry
3. **Metadata Extraction**: Generate tags (SHA, latest)
4. **Disk Cleanup**: Free space for Docker build
5. **Build & Push**: Build image and push to `ghcr.io/allenai/olmoearth_projects`

**Image Tagging Strategy**:
```yaml
tags: |
  type=sha,format=long     # Full commit SHA
  type=sha,format=short    # Short commit SHA
  type=raw,value=latest,enable={{is_default_branch}}
```

The image is tagged with the commit SHA for traceability and `latest` for the main branch.

**Sources**: [.github/workflows/build-test.yml:19-75]()

### Test Job Configuration

The test job is defined in [.github/workflows/build-test.yml:76-122]() and runs on `ubuntu-latest-m` (medium-sized runner) to handle model loading:

**Unit Tests Execution** [.github/workflows/build-test.yml:99-105]():
```bash
docker run --rm \
  -e CI="true" \
  ${{ needs.build.outputs.ghcr_docker_image }} \
  pytest tests/unit -vv
```

**Integration Tests Execution** [.github/workflows/build-test.yml:107-115]():
```bash
docker run --rm \
  -e CI="true" \
  -v ${GOOGLE_GHA_CREDS_PATH}:/tmp/gcp-credentials.json:ro \
  -e GOOGLE_APPLICATION_CREDENTIALS=/tmp/gcp-credentials.json \
  ${{ needs.build.outputs.ghcr_docker_image }} \
  pytest tests/integration -vv --forked
```

The `--forked` flag is critical for integration tests to prevent memory issues when loading large models.

**Sources**: [.github/workflows/build-test.yml:76-122]()

### Concurrency Control

The workflow includes concurrency control at [.github/workflows/build-test.yml:14-16]():

```yaml
concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true
```

This ensures that only one workflow runs per branch at a time, canceling older runs when new commits are pushed.

**Sources**: [.github/workflows/build-test.yml:14-16]()

---

## Docker Environment

The Docker container provides a consistent, reproducible environment for development, testing, and deployment.

### Docker Architecture

```mermaid
graph TB
    BASE["Base Image<br/>pytorch/pytorch:2.7.0<br/>cuda12.8-cudnn9-runtime"] --> GIT["Install Git<br/>Configure GitHub Token"]
    GIT --> UV["Copy uv Binary<br/>ghcr.io/astral-sh/uv"]
    UV --> WORKDIR["Set Working Directory<br/>/olmoearth_projects"]
    WORKDIR --> COPY_LOCK["Copy Dependency Files<br/>pyproject.toml<br/>uv.lock"]
    COPY_LOCK --> SYNC_DEPS["Install Dependencies<br/>uv sync --all-extras<br/>--no-install-project"]
    SYNC_DEPS --> ENV_PATH["Add to PATH<br/>/olmoearth_projects/.venv/bin"]
    ENV_PATH --> COPY_CODE["Copy Source Code<br/>./ → /olmoearth_projects"]
    COPY_CODE --> SYNC_PROJ["Install Project<br/>uv sync --all-extras --locked"]
```

### Dockerfile Structure

The [Dockerfile:1-19]() is optimized for layer caching and build speed:

**Base Image Selection** [Dockerfile:1]():
```dockerfile
FROM pytorch/pytorch:2.7.0-cuda12.8-cudnn9-runtime
```
Uses the official PyTorch image with CUDA 12.8 and cuDNN 9 support for GPU acceleration.

**Git Configuration** [Dockerfile:4-6]():
```dockerfile
ARG GITHUB_TOKEN
RUN git config --global url."https://x-access-token:${GITHUB_TOKEN}@github.com/".insteadOf "https://github.com/"
```
Configures Git to use the provided GitHub token for accessing private repositories (like `olmoearth_pretrain`).

**UV Integration** [Dockerfile:8]():
```dockerfile
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv
```
Copies the `uv` binary from the official image for fast dependency resolution.

**Dependency Installation** [Dockerfile:12-14]():
```dockerfile
COPY pyproject.toml uv.lock /olmoearth_projects/
RUN uv sync --all-extras --no-install-project
```
Installs dependencies first (without the project itself) to maximize Docker layer caching.

**Project Installation** [Dockerfile:16-18]():
```dockerfile
ENV PATH="/olmoearth_projects/.venv/bin:$PATH"
COPY ./ /olmoearth_projects
RUN uv sync --all-extras --locked
```
Copies source code and installs the project with locked dependencies.

**Sources**: [Dockerfile:1-19]()

### Building the Docker Image Locally

```bash
# Build with GitHub token for private repo access
docker build \
  --build-arg GITHUB_TOKEN=<your_token> \
  -t olmoearth_projects:local \
  .

# Run tests in the container
docker run --rm olmoearth_projects:local pytest tests/unit -vv

# Interactive development shell
docker run --rm -it \
  -v $(pwd):/olmoearth_projects \
  olmoearth_projects:local \
  bash
```

### Environment Variables

The Docker container respects several environment variables:

| Variable | Purpose | Example |
|----------|---------|---------|
| `WANDB_MODE` | Control Weights & Biases logging | `disabled` for tests |
| `GOOGLE_APPLICATION_CREDENTIALS` | GCP service account key path | `/tmp/gcp-credentials.json` |
| `CI` | Indicate CI environment | `true` in GitHub Actions |
| `NUM_WORKERS` | PyTorch DataLoader workers | Template in model.yaml |
| `DATASET_PATH` | Path to rslearn dataset | Template in model.yaml |

**Sources**: [Dockerfile:1-19](), [.github/workflows/build-test.yml:99-115]()

---

## Code Quality Standards

The repository enforces code quality through automated tools configured in [pyproject.toml]().

### Linting and Formatting with Ruff

**Ruff Configuration** [pyproject.toml:48-58]():
```toml
[tool.ruff]
fix = true  # Auto-fix issues when possible

[tool.ruff.lint]
extend-select = ["D", "I", "UP"]  # Docstrings, Imports, Upgrades

[tool.ruff.lint.per-file-ignores]
"tests/**" = ["D"]  # Skip docstring checks in tests

[tool.ruff.lint.pydocstyle]
convention = "google"  # Google-style docstrings
```

**Selected Ruff Rules**:
- **D**: Enforce docstrings on public modules, classes, and functions
- **I**: Sort and organize imports
- **UP**: Upgrade syntax for newer Python versions

**Running Ruff**:
```bash
# Check for issues
ruff check .

# Auto-fix issues
ruff check --fix .

# Format code
ruff format .
```

**Sources**: [pyproject.toml:48-58]()

### Type Checking with MyPy

MyPy is configured as a development dependency [pyproject.toml:27]() to catch type errors:

```bash
# Run type checking
mypy olmoearth_projects/
```

### Pre-commit Hooks

Pre-commit hooks are recommended for automated quality checks before commits [pyproject.toml:28]():

```bash
# Install pre-commit hooks
pre-commit install

# Run manually on all files
pre-commit run --all-files
```

### Docstring Coverage

The `interrogate` tool checks docstring coverage [pyproject.toml:26]():

```bash
# Check docstring coverage
interrogate -v olmoearth_projects/
```

**Sources**: [pyproject.toml:24-34]()

---

## Contributing Workflow

### Step-by-Step Contribution Process

1. **Create a Feature Branch**:
   ```bash
   git checkout -b feature/my-new-feature
   ```

2. **Make Changes**:
   - Add code to appropriate directories
   - Include unit tests for new functionality
   - Update documentation as needed

3. **Run Quality Checks**:
   ```bash
   # Format and lint
   ruff format .
   ruff check --fix .
   
   # Type check
   mypy olmoearth_projects/
   
   # Run tests
   pytest tests/unit -vv
   pytest tests/integration -vv --forked
   ```

4. **Commit Changes**:
   ```bash
   git add .
   git commit -m "Add feature: description"
   ```

5. **Push and Create Pull Request**:
   ```bash
   git push origin feature/my-new-feature
   ```
   Then open a pull request on GitHub.

6. **CI/CD Validation**:
   - GitHub Actions will automatically build Docker image
   - Run unit and integration tests
   - Verify all checks pass before merging

### Pull Request Requirements

All pull requests must:
- Pass all CI/CD checks (build, unit tests, integration tests)
- Follow code quality standards (Ruff, MyPy)
- Include tests for new functionality
- Update documentation when adding features

**Sources**: [.github/workflows/build-test.yml:1-122](), [pyproject.toml:48-58]()

---

## Common Development Tasks

### Adding a New Model Application

When adding a new model to the repository:

1. **Development Phase** (in rslearn_projects):
   - Create data curation scripts in `rslp/[project_name]/`
   - Generate training windows with proper spatial splitting
   - Run label quality checks using utilities from [olmoearth_projects/utils/label_quality/]()
   - Create rslearn dataset and store in `/weka/dfive-default/rslearn-eai/datasets/`

2. **Deployment Phase** (in olmoearth_projects):
   - Copy configurations to `olmoearth_run_data/[project_name]/`
   - Add supporting code to `olmoearth_projects/[project_name]/`
   - Publish checkpoint to `gs://rslearn-eai/model_checkpoints/`
   - Document in project README

### Running Local Fine-tuning

While fine-tuning typically happens on GPU clusters via rslearn_projects, you can test configurations locally:

```bash
# Set environment variables
export WANDB_PROJECT=my_project
export WANDB_NAME=local_test
export DATASET_PATH=/path/to/dataset
export TRAINER_DATA_PATH=/tmp/checkpoints

# Run training (with small dataset for testing)
python -m rslearn.train.rslp_finetuning fit \
  --config olmoearth_run_data/[project]/model.yaml
```

### Testing Configuration Changes

Before deploying configuration changes:

1. Create a small test geometry
2. Run the integration test with your config
3. Verify output matches expectations

Example using the test from [tests/integration/olmoearth_run/test_olmoearth_run.py]():

```python
# Customize for your model
checkpoint_path = "path/to/your/checkpoint.ckpt"
config_dir = "olmoearth_run_data/your_project/"
olmoearth_run(config_path=config_dir, checkpoint_path=checkpoint_path)
```

**Sources**: [docs/internal.md:3-29](), [tests/integration/olmoearth_run/test_olmoearth_run.py:1-119]()

---

