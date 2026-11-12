> 来源: [https://deepwiki.com/huggingface/transformers/15-cicd-testing-and-infrastructure](https://deepwiki.com/huggingface/transformers/15-cicd-testing-and-infrastructure)
> DeepWiki huggingface/transformers | Last indexed: 3 September 2026 (8f5420

# CI/CD, Testing & Infrastructure

  Relevant source files 
 - [.circleci/config.yml](https://github.com/huggingface/transformers/blob/8f542025/.circleci/config.yml)
 - [.circleci/config.yml.bak](https://github.com/huggingface/transformers/blob/8f542025/.circleci/config.yml.bak)
 - [.circleci/create_circleci_config.py](https://github.com/huggingface/transformers/blob/8f542025/.circleci/create_circleci_config.py)
 - [.github/scripts/codeowners_for_review_action](https://github.com/huggingface/transformers/blob/8f542025/.github/scripts/codeowners_for_review_action)
 - [.github/workflows/add-model-like.yml](https://github.com/huggingface/transformers/blob/8f542025/.github/workflows/add-model-like.yml)
 - [.github/workflows/assign-reviewers.yml](https://github.com/huggingface/transformers/blob/8f542025/.github/workflows/assign-reviewers.yml)
 - [.github/workflows/benchmark_v2_mi300_caller.yml](https://github.com/huggingface/transformers/blob/8f542025/.github/workflows/benchmark_v2_mi300_caller.yml)
 - [.github/workflows/build-ci-docker-images.yml](https://github.com/huggingface/transformers/blob/8f542025/.github/workflows/build-ci-docker-images.yml)
 - [.github/workflows/build-docker-images.yml](https://github.com/huggingface/transformers/blob/8f542025/.github/workflows/build-docker-images.yml)
 - [.github/workflows/build-nightly-ci-docker-images.yml](https://github.com/huggingface/transformers/blob/8f542025/.github/workflows/build-nightly-ci-docker-images.yml)
 - [.github/workflows/build-past-ci-docker-images.yml](https://github.com/huggingface/transformers/blob/8f542025/.github/workflows/build-past-ci-docker-images.yml)
 - [.github/workflows/check-workflow-permissions.yml](https://github.com/huggingface/transformers/blob/8f542025/.github/workflows/check-workflow-permissions.yml)
 - [.github/workflows/check_failed_tests.yml](https://github.com/huggingface/transformers/blob/8f542025/.github/workflows/check_failed_tests.yml)
 - [.github/workflows/check_tiny_models.yml](https://github.com/huggingface/transformers/blob/8f542025/.github/workflows/check_tiny_models.yml)
 - [.github/workflows/circleci-failure-summary-comment.yml.bak](https://github.com/huggingface/transformers/blob/8f542025/.github/workflows/circleci-failure-summary-comment.yml.bak)
 - [.github/workflows/codeql.yml](https://github.com/huggingface/transformers/blob/8f542025/.github/workflows/codeql.yml)
 - [.github/workflows/collated-reports.yml](https://github.com/huggingface/transformers/blob/8f542025/.github/workflows/collated-reports.yml)
 - [.github/workflows/doctest_job.yml](https://github.com/huggingface/transformers/blob/8f542025/.github/workflows/doctest_job.yml)
 - [.github/workflows/doctests.yml](https://github.com/huggingface/transformers/blob/8f542025/.github/workflows/doctests.yml)
 - [.github/workflows/extras-smoke-test.yml](https://github.com/huggingface/transformers/blob/8f542025/.github/workflows/extras-smoke-test.yml)
 - [.github/workflows/get-pr-info.yml](https://github.com/huggingface/transformers/blob/8f542025/.github/workflows/get-pr-info.yml)
 - [.github/workflows/get-pr-number.yml](https://github.com/huggingface/transformers/blob/8f542025/.github/workflows/get-pr-number.yml)
 - [.github/workflows/model_jobs_intel_gaudi.yml](https://github.com/huggingface/transformers/blob/8f542025/.github/workflows/model_jobs_intel_gaudi.yml)
 - [.github/workflows/new_model_pr_merged_notification.yml](https://github.com/huggingface/transformers/blob/8f542025/.github/workflows/new_model_pr_merged_notification.yml)
 - [.github/workflows/pr-repo-consistency-bot.yml](https://github.com/huggingface/transformers/blob/8f542025/.github/workflows/pr-repo-consistency-bot.yml)
 - [.github/workflows/pr_build_doc_with_comment.yml](https://github.com/huggingface/transformers/blob/8f542025/.github/workflows/pr_build_doc_with_comment.yml)
 - [.github/workflows/pr_slow_ci_suggestion.yml](https://github.com/huggingface/transformers/blob/8f542025/.github/workflows/pr_slow_ci_suggestion.yml)
 - [.github/workflows/push-important-models.yml](https://github.com/huggingface/transformers/blob/8f542025/.github/workflows/push-important-models.yml)
 - [.github/workflows/release-conda.yml](https://github.com/huggingface/transformers/blob/8f542025/.github/workflows/release-conda.yml)
 - [.github/workflows/release.yml](https://github.com/huggingface/transformers/blob/8f542025/.github/workflows/release.yml)
 - [.github/workflows/self-comment-ci.yml](https://github.com/huggingface/transformers/blob/8f542025/.github/workflows/self-comment-ci.yml)
 - [.github/workflows/self-nightly-caller.yml](https://github.com/huggingface/transformers/blob/8f542025/.github/workflows/self-nightly-caller.yml)
 - [.github/workflows/self-scheduled-amd-mi250-caller.yml](https://github.com/huggingface/transformers/blob/8f542025/.github/workflows/self-scheduled-amd-mi250-caller.yml)
 - [.github/workflows/self-scheduled-amd-mi300-caller.yml](https://github.com/huggingface/transformers/blob/8f542025/.github/workflows/self-scheduled-amd-mi300-caller.yml)
 - [.github/workflows/self-scheduled-caller.yml](https://github.com/huggingface/transformers/blob/8f542025/.github/workflows/self-scheduled-caller.yml)
 - [.github/workflows/self-scheduled-flash-attn-caller.yml](https://github.com/huggingface/transformers/blob/8f542025/.github/workflows/self-scheduled-flash-attn-caller.yml)
 - [.github/workflows/self-scheduled-intel-gaudi.yml](https://github.com/huggingface/transformers/blob/8f542025/.github/workflows/self-scheduled-intel-gaudi.yml)
 - [.github/workflows/self-scheduled-intel-gaudi3-caller.yml](https://github.com/huggingface/transformers/blob/8f542025/.github/workflows/self-scheduled-intel-gaudi3-caller.yml)
 - [.github/workflows/slack-report.yml](https://github.com/huggingface/transformers/blob/8f542025/.github/workflows/slack-report.yml)
 - [.github/workflows/ssh-runner.yml](https://github.com/huggingface/transformers/blob/8f542025/.github/workflows/ssh-runner.yml)
 - [.github/workflows/stale.yml](https://github.com/huggingface/transformers/blob/8f542025/.github/workflows/stale.yml)
 - [.github/workflows/trl-ci-bot.yml](https://github.com/huggingface/transformers/blob/8f542025/.github/workflows/trl-ci-bot.yml)
 - [.github/workflows/trufflehog.yml](https://github.com/huggingface/transformers/blob/8f542025/.github/workflows/trufflehog.yml)
 - [.github/workflows/update_metdata.yml](https://github.com/huggingface/transformers/blob/8f542025/.github/workflows/update_metdata.yml)
 - [.gitignore](https://github.com/huggingface/transformers/blob/8f542025/.gitignore)
 - [Makefile](https://github.com/huggingface/transformers/blob/8f542025/Makefile)
 - [conftest.py](https://github.com/huggingface/transformers/blob/8f542025/conftest.py)
 - [docker/transformers-all-latest-gpu/Dockerfile](https://github.com/huggingface/transformers/blob/8f542025/docker/transformers-all-latest-gpu/Dockerfile)
 - [docker/transformers-pytorch-amd-gpu/Dockerfile](https://github.com/huggingface/transformers/blob/8f542025/docker/transformers-pytorch-amd-gpu/Dockerfile)
 - [docker/transformers-pytorch-deepspeed-amd-gpu/Dockerfile](https://github.com/huggingface/transformers/blob/8f542025/docker/transformers-pytorch-deepspeed-amd-gpu/Dockerfile)
 - [docker/transformers-pytorch-deepspeed-latest-gpu/Dockerfile](https://github.com/huggingface/transformers/blob/8f542025/docker/transformers-pytorch-deepspeed-latest-gpu/Dockerfile)
 - [docker/transformers-pytorch-deepspeed-nightly-gpu/Dockerfile](https://github.com/huggingface/transformers/blob/8f542025/docker/transformers-pytorch-deepspeed-nightly-gpu/Dockerfile)
 - [docker/transformers-pytorch-gpu/Dockerfile](https://github.com/huggingface/transformers/blob/8f542025/docker/transformers-pytorch-gpu/Dockerfile)
 - [docker/transformers-quantization-latest-gpu/Dockerfile](https://github.com/huggingface/transformers/blob/8f542025/docker/transformers-quantization-latest-gpu/Dockerfile)
 - [docs/source/en/pr_checks.md](https://github.com/huggingface/transformers/blob/8f542025/docs/source/en/pr_checks.md?plain=1)
 - [setup.py](https://github.com/huggingface/transformers/blob/8f542025/setup.py)
 - [src/transformers/data/processors/squad.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/data/processors/squad.py)
 - [src/transformers/dependency_versions_table.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/dependency_versions_table.py)
 - [src/transformers/safetensors_conversion.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/safetensors_conversion.py)
 - [tests/conftest_tests/test_cache_fallback.py](https://github.com/huggingface/transformers/blob/8f542025/tests/conftest_tests/test_cache_fallback.py)
 - [tests/models/phimoe/test_modeling_phimoe.py](https://github.com/huggingface/transformers/blob/8f542025/tests/models/phimoe/test_modeling_phimoe.py)
 - [tests/repo_utils/test_checkers.py](https://github.com/huggingface/transformers/blob/8f542025/tests/repo_utils/test_checkers.py)
 - [tests/repo_utils/test_split_model_tests.py](https://github.com/huggingface/transformers/blob/8f542025/tests/repo_utils/test_split_model_tests.py)
 - [tests/repo_utils/test_tests_fetcher.py](https://github.com/huggingface/transformers/blob/8f542025/tests/repo_utils/test_tests_fetcher.py)
 - [tests/utils/test_get_previous_daily_ci.py](https://github.com/huggingface/transformers/blob/8f542025/tests/utils/test_get_previous_daily_ci.py)
 - [tests/utils/test_testing_utils.py](https://github.com/huggingface/transformers/blob/8f542025/tests/utils/test_testing_utils.py)
 - [utils/check_bad_commit.py](https://github.com/huggingface/transformers/blob/8f542025/utils/check_bad_commit.py)
 - [utils/check_inits.py](https://github.com/huggingface/transformers/blob/8f542025/utils/check_inits.py)
 - [utils/check_reviewers.py](https://github.com/huggingface/transformers/blob/8f542025/utils/check_reviewers.py)
 - [utils/checkers-requirements.txt](https://github.com/huggingface/transformers/blob/8f542025/utils/checkers-requirements.txt)
 - [utils/checkers.py](https://github.com/huggingface/transformers/blob/8f542025/utils/checkers.py)
 - [utils/collated_reports.py](https://github.com/huggingface/transformers/blob/8f542025/utils/collated_reports.py)
 - [utils/compare_test_runs.py](https://github.com/huggingface/transformers/blob/8f542025/utils/compare_test_runs.py)
 - [utils/get_pr_run_slow_jobs.py](https://github.com/huggingface/transformers/blob/8f542025/utils/get_pr_run_slow_jobs.py)
 - [utils/get_previous_daily_ci.py](https://github.com/huggingface/transformers/blob/8f542025/utils/get_previous_daily_ci.py)
 - [utils/notification_service.py](https://github.com/huggingface/transformers/blob/8f542025/utils/notification_service.py)
 - [utils/pr_slow_ci_models.py](https://github.com/huggingface/transformers/blob/8f542025/utils/pr_slow_ci_models.py)
 - [utils/process_bad_commit_report.py](https://github.com/huggingface/transformers/blob/8f542025/utils/process_bad_commit_report.py)
 - [utils/split_model_tests.py](https://github.com/huggingface/transformers/blob/8f542025/utils/split_model_tests.py)
 - [utils/tests_fetcher.py](https://github.com/huggingface/transformers/blob/8f542025/utils/tests_fetcher.py)
 
  This section provides a high-level overview of the automation pipelines, testing frameworks, and infrastructure components that ensure the stability and quality of the `transformers` library. The system is designed to handle a massive suite of tests across diverse hardware (CPU, NVIDIA GPU, AMD GPU, Intel Gaudi) and software environments.

 
## System Architecture Overview

 The infrastructure bridges the gap between code changes in a Pull Request (PR) and the execution of thousands of tests. It utilizes a combination of **CircleCI** for core logic and **GitHub Actions** for specialized hardware, Docker image builds, and reporting.

 
### CI/CD Workflow Diagram

 
```

```

 **Sources:** [.circleci/config.yml1-100](https://github.com/huggingface/transformers/blob/8f542025/.circleci/config.yml#L1-L100) [.circleci/create_circleci_config.py93-145](https://github.com/huggingface/transformers/blob/8f542025/.circleci/create_circleci_config.py#L93-L145) [utils/tests_fetcher.py18-29](https://github.com/huggingface/transformers/blob/8f542025/utils/tests_fetcher.py#L18-L29) [.github/workflows/build-docker-images.yml1-15](https://github.com/huggingface/transformers/blob/8f542025/.github/workflows/build-docker-images.yml#L1-L15) [.github/workflows/self-comment-ci.yml1-32](https://github.com/huggingface/transformers/blob/8f542025/.github/workflows/self-comment-ci.yml#L1-L32)

 
## Core Components

 
### 1. CircleCI Pipeline & Test Selection

 The primary CI engine uses a dynamic configuration pattern to manage the library's vast test suite. Instead of a static list of jobs, it runs a "setup" workflow that analyzes the repository diff.

 
 - **Dynamic Configuration:** The `CircleCIJob` dataclass in `create_circleci_config.py` defines the schema for generated jobs, including environment variables like `TRANSFORMERS_IS_CI` and `PYTEST_TIMEOUT` [.circleci/create_circleci_config.py93-168](https://github.com/huggingface/transformers/blob/8f542025/.circleci/create_circleci_config.py#L93-L168)
 - **Intelligent Fetching:** `tests_fetcher.py` analyzes the `git` diff to identify impacted models. If "core files" like `modeling_utils.py` or `setup.py` are modified, it triggers a full CI run [utils/tests_fetcher.py71-84](https://github.com/huggingface/transformers/blob/8f542025/utils/tests_fetcher.py#L71-L84)
 - **Test Environment:** The `conftest.py` file provides global fixtures and logic, such as a read-only cache fallback mechanism (`_with_tmpdir_cache_fallback`) to handle CI environments where the filesystem is locked [conftest.py109-156](https://github.com/huggingface/transformers/blob/8f542025/conftest.py#L109-L156)
 
 For details, see [CircleCI Pipeline & Test Selection](https://deepwiki.com/huggingface/transformers/15.1-circleci-pipeline-and-test-selection).

 
### 2. GitHub Actions Workflows

 GitHub Actions (GHA) handles specialized tasks, scheduled builds, and maintenance utilities.

 
 - **Docker Automation:** `build-docker-images.yml` runs daily to build and push images for PyTorch, DeepSpeed, and AMD ROCm to DockerHub [.github/workflows/build-docker-images.yml1-15](https://github.com/huggingface/transformers/blob/8f542025/.github/workflows/build-docker-images.yml#L1-L15)
 - **Slow CI Triggering:** Maintainers can trigger comprehensive slow tests on PRs by commenting `run-slow`, handled by `self-comment-ci.yml` and `pr_slow_ci_models.py` [.github/workflows/self-comment-ci.yml31-95](https://github.com/huggingface/transformers/blob/8f542025/.github/workflows/self-comment-ci.yml#L31-L95)
 - **Reporting:** The `notification_service.py` utility parses test results and sends detailed summaries to Slack, distinguishing between modeling, trainer, and pipeline failures [utils/notification_service.py36-188](https://github.com/huggingface/transformers/blob/8f542025/utils/notification_service.py#L36-L188)
 - **Bisecting:** `check_bad_commit.py` automates finding the exact commit that introduced a test failure using `git bisect` [utils/check_bad_commit.py28-137](https://github.com/huggingface/transformers/blob/8f542025/utils/check_bad_commit.py#L28-L137)
 
 For details, see [GitHub Actions Workflows](https://deepwiki.com/huggingface/transformers/15.2-github-actions-workflows).

 
### 3. Docker Infrastructure

 The library maintains specialized Dockerfiles in the `docker/` directory to provide consistent environments for various backends.

 
 - **NVIDIA GPU Stack:** The `transformers-all-latest-gpu` image includes a full stack of `torch`, `torchvision`, `torchaudio`, and `torchcodec` pinned to compatible versions [docker/transformers-all-latest-gpu/Dockerfile12-78](https://github.com/huggingface/transformers/blob/8f542025/docker/transformers-all-latest-gpu/Dockerfile#L12-L78)
 - **Quantization:** The `transformers-quantization-latest-gpu` image installs a wide array of backends including `bitsandbytes`, `hqq`, `auto-round`, and `compressed-tensors` [docker/transformers-quantization-latest-gpu/Dockerfile58-83](https://github.com/huggingface/transformers/blob/8f542025/docker/transformers-quantization-latest-gpu/Dockerfile#L58-L83)
 - **AMD ROCm:** `transformers-pytorch-amd-gpu` builds a ROCm-compatible environment, including specialized wheels for `flash-attn` and `torchcodec` [docker/transformers-pytorch-amd-gpu/Dockerfile50-56](https://github.com/huggingface/transformers/blob/8f542025/docker/transformers-pytorch-amd-gpu/Dockerfile#L50-L56)
 
 For details, see [Docker Images](https://deepwiki.com/huggingface/transformers/15.3-docker-images).

 
### 4. Benchmarking Framework

 The library includes a framework for tracking performance regressions and hardware utilization, integrated into the `Makefile`.

 
 - **Execution:** Benchmarks are triggered via `make benchmark`, which executes `benchmark/benchmark.py` [Makefile74-75](https://github.com/huggingface/transformers/blob/8f542025/Makefile#L74-L75)
 - **Continuous Batching:** Specialized benchmarks in `benchmark_v2` evaluate high-throughput serving performance using scripts like `continuous_batching_overall.py`.
 
 For details, see [Benchmarking Framework](https://deepwiki.com/huggingface/transformers/15.4-benchmarking-framework).

 
## Dependency & Consistency Management

 Dependencies are centrally defined in `setup.py` and synchronized throughout the repository using the `Makefile`.

 
| Command | Utility | Purpose |
|---|---|---|
| make check-code-quality | utils/checkers.py | Runs ruff linting and transformers-mlinter setup.py126-129 Makefile50-51 |
| make check-repository-consistency | utils/checkers.py | Validates auto_mappings, inits, and docstrings Makefile54-55 |
| make fix-repo | utils/checkers.py | Automatically updates dependency_versions_table.py from setup.py setup.py71-72 Makefile62-63 |

 **Sources:** [setup.py72-164](https://github.com/huggingface/transformers/blob/8f542025/setup.py#L72-L164) [src/transformers/dependency_versions_table.py4-91](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/dependency_versions_table.py#L4-L91) [Makefile13-36](https://github.com/huggingface/transformers/blob/8f542025/Makefile#L13-L36) [utils/checkers.py1-20](https://github.com/huggingface/transformers/blob/8f542025/utils/checkers.py#L1-L20)
