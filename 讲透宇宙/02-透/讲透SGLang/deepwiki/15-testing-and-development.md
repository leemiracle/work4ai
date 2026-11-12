> 来源: [https://deepwiki.com/sgl-project/sglang/15-testing-and-development](https://deepwiki.com/sgl-project/sglang/15-testing-and-development)
> DeepWiki sgl-project/sglang | Last indexed: 27 Aug 2026 (94183a)

# Testing and Development

  Relevant source files 
 - [.claude/skills/ci-workflow-guide/SKILL.md](https://github.com/sgl-project/sglang/blob/94183a8d/.claude/skills/ci-workflow-guide/SKILL.md?plain=1)
 - [.codespellrc](https://github.com/sgl-project/sglang/blob/94183a8d/.codespellrc)
 - [.github/CI_PERMISSIONS.json](https://github.com/sgl-project/sglang/blob/94183a8d/.github/CI_PERMISSIONS.json)
 - [.github/CODEOWNERS](https://github.com/sgl-project/sglang/blob/94183a8d/.github/CODEOWNERS)
 - [.github/FOLDER_README.md](https://github.com/sgl-project/sglang/blob/94183a8d/.github/FOLDER_README.md?plain=1)
 - [.github/update_ci_permission.py](https://github.com/sgl-project/sglang/blob/94183a8d/.github/update_ci_permission.py)
 - [.github/workflows/amd-aiter-scout.yml](https://github.com/sgl-project/sglang/blob/94183a8d/.github/workflows/amd-aiter-scout.yml)
 - [.github/workflows/amd-ci-job-monitor.yml](https://github.com/sgl-project/sglang/blob/94183a8d/.github/workflows/amd-ci-job-monitor.yml)
 - [.github/workflows/auto-tune.yml](https://github.com/sgl-project/sglang/blob/94183a8d/.github/workflows/auto-tune.yml)
 - [.github/workflows/bot-bump-sglang-version.yml](https://github.com/sgl-project/sglang/blob/94183a8d/.github/workflows/bot-bump-sglang-version.yml)
 - [.github/workflows/ci-failure-monitor.yml](https://github.com/sgl-project/sglang/blob/94183a8d/.github/workflows/ci-failure-monitor.yml)
 - [.github/workflows/nightly-test-amd-rocm720.yml](https://github.com/sgl-project/sglang/blob/94183a8d/.github/workflows/nightly-test-amd-rocm720.yml)
 - [.github/workflows/nightly-test-amd.yml](https://github.com/sgl-project/sglang/blob/94183a8d/.github/workflows/nightly-test-amd.yml)
 - [.github/workflows/pr-test-amd-extra.yml](https://github.com/sgl-project/sglang/blob/94183a8d/.github/workflows/pr-test-amd-extra.yml)
 - [.github/workflows/pr-test-amd-rocm720.yml](https://github.com/sgl-project/sglang/blob/94183a8d/.github/workflows/pr-test-amd-rocm720.yml)
 - [.github/workflows/pr-test-amd.yml](https://github.com/sgl-project/sglang/blob/94183a8d/.github/workflows/pr-test-amd.yml)
 - [.github/workflows/pr-test.yml](https://github.com/sgl-project/sglang/blob/94183a8d/.github/workflows/pr-test.yml)
 - [.github/workflows/release-branch-cut.yml](https://github.com/sgl-project/sglang/blob/94183a8d/.github/workflows/release-branch-cut.yml)
 - [.github/workflows/rerun-test.yml](https://github.com/sgl-project/sglang/blob/94183a8d/.github/workflows/rerun-test.yml)
 - [.github/workflows/runner-utilization.yml](https://github.com/sgl-project/sglang/blob/94183a8d/.github/workflows/runner-utilization.yml)
 - [.github/workflows/slash-command-handler.yml](https://github.com/sgl-project/sglang/blob/94183a8d/.github/workflows/slash-command-handler.yml)
 - [.pre-commit-config.yaml](https://github.com/sgl-project/sglang/blob/94183a8d/.pre-commit-config.yaml)
 - [docs/docs/developer_guide/contribution_guide.mdx](https://github.com/sgl-project/sglang/blob/94183a8d/docs/docs/developer_guide/contribution_guide.mdx?plain=1)
 - [docs/docs/developer_guide/evaluating_new_models.mdx](https://github.com/sgl-project/sglang/blob/94183a8d/docs/docs/developer_guide/evaluating_new_models.mdx?plain=1)
 - [docs/docs/hardware-platforms/ascend-npus/development/contribution_guide.mdx](https://github.com/sgl-project/sglang/blob/94183a8d/docs/docs/hardware-platforms/ascend-npus/development/contribution_guide.mdx?plain=1)
 - [docs/docs/references/nightly_precision_regression.mdx](https://github.com/sgl-project/sglang/blob/94183a8d/docs/docs/references/nightly_precision_regression.mdx?plain=1)
 - [python/sglang/test/precision_baseline_store.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/test/precision_baseline_store.py)
 - [scripts/ci/amd/ensure_vram_clear.sh](https://github.com/sgl-project/sglang/blob/94183a8d/scripts/ci/amd/ensure_vram_clear.sh)
 - [scripts/ci/utils/query_job_status.py](https://github.com/sgl-project/sglang/blob/94183a8d/scripts/ci/utils/query_job_status.py)
 - [scripts/ci/utils/runner_utilization_report.py](https://github.com/sgl-project/sglang/blob/94183a8d/scripts/ci/utils/runner_utilization_report.py)
 - [scripts/ci/utils/slash_command_handler.py](https://github.com/sgl-project/sglang/blob/94183a8d/scripts/ci/utils/slash_command_handler.py)
 - [scripts/ci/utils/test_runner_utilization_report.py](https://github.com/sgl-project/sglang/blob/94183a8d/scripts/ci/utils/test_runner_utilization_report.py)
 - [scripts/ci_monitor/README.md](https://github.com/sgl-project/sglang/blob/94183a8d/scripts/ci_monitor/README.md?plain=1)
 - [scripts/ci_monitor/ci_failures_analysis.py](https://github.com/sgl-project/sglang/blob/94183a8d/scripts/ci_monitor/ci_failures_analysis.py)
 - [scripts/ci_monitor/test_ci_failures_analysis.py](https://github.com/sgl-project/sglang/blob/94183a8d/scripts/ci_monitor/test_ci_failures_analysis.py)
 - [test/registered/amd/perf/mi35x/test_minimax_m3_perf_mi35x.py](https://github.com/sgl-project/sglang/blob/94183a8d/test/registered/amd/perf/mi35x/test_minimax_m3_perf_mi35x.py)
 - [test/registered/amd/test_deepseek_v4_flash_fp8_mi30x.py](https://github.com/sgl-project/sglang/blob/94183a8d/test/registered/amd/test_deepseek_v4_flash_fp8_mi30x.py)
 - [test/registered/debug_utils/test_nightly_precision_regression.py](https://github.com/sgl-project/sglang/blob/94183a8d/test/registered/debug_utils/test_nightly_precision_regression.py)
 - [test/registered/unit/test_precision_baseline_store.py](https://github.com/sgl-project/sglang/blob/94183a8d/test/registered/unit/test_precision_baseline_store.py)
 - [test/run_suite.py](https://github.com/sgl-project/sglang/blob/94183a8d/test/run_suite.py)
 
  This document covers SGLang's testing infrastructure, CI/CD workflows, benchmarking tools, and development practices. It explains how tests are organized, executed across multiple hardware platforms, and integrated into the pull request review process.

 For information about contributing code and formatting requirements, see the contribution guide in `docs/developer_guide/contribution_guide.mdx` [docs/developer_guide/contribution_guide.mdx1-133](https://github.com/sgl-project/sglang/blob/94183a8d/docs/developer_guide/contribution_guide.mdx?plain=1#L1-L133) For deployment-specific topics, see [Installation and Deployment](https://deepwiki.com/sgl-project/sglang/2-installation-and-deployment).

 
---

 
## Test Suite Organization

 SGLang uses a registry-based test system where tests are registered via decorators and executed by `test/run_suite.py` [test/run_suite.py1-230](https://github.com/sgl-project/sglang/blob/94183a8d/test/run_suite.py#L1-L230) The registry system provides a declarative API for organizing tests by hardware backend, suite name, and nightly/per-commit classification.

 
### Test Registration System

 Tests are registered using platform-specific decorator functions that map to `HWBackend` enum values [test/run_suite.py18-26](https://github.com/sgl-project/sglang/blob/94183a8d/test/run_suite.py#L18-L26) The `CIRegistry` class stores metadata such as the filename, backend, and estimated execution time [test/run_suite.py10-15](https://github.com/sgl-project/sglang/blob/94183a8d/test/run_suite.py#L10-L15)

 **Test Discovery and Collection Flow**

 
```

```

 Sources: [test/run_suite.py10-15](https://github.com/sgl-project/sglang/blob/94183a8d/test/run_suite.py#L10-L15) [test/run_suite.py197-206](https://github.com/sgl-project/sglang/blob/94183a8d/test/run_suite.py#L197-L206) [test/run_suite.py222-230](https://github.com/sgl-project/sglang/blob/94183a8d/test/run_suite.py#L222-L230)

 
### Suite Organization by Hardware Backend

 The `PER_COMMIT_SUITES` and `NIGHTLY_SUITES` dictionaries define valid suite names per hardware platform.

 
| Hardware | Per-Commit Suites (Examples) | Nightly Suites (Examples) |
|---|---|---|
| CUDA | base-a-test-1-gpu-small, base-b-test-4-gpu-b200 | nightly-test-1-gpu-large, nightly-test-8-gpu-b200 |
| AMD | stage-a-test-1-gpu-small-amd, stage-c-test-4-gpu-amd | nightly-amd, nightly-amd-accuracy-8-gpu-mi35x-kimi-k3 |
| CPU | base-a-test-cpu, base-b-test-cpu | (none) |
| NPU | base-a-test-1-npu-a2, base-b-test-16-npu-a3 | nightly-1-npu-a3, nightly-16-npu-a3 |
| XPU | stage-a-test-1-gpu-xpu | nightly-xpu-1-gpu |

 Sources: [test/run_suite.py32-119](https://github.com/sgl-project/sglang/blob/94183a8d/test/run_suite.py#L32-L119) [test/run_suite.py122-185](https://github.com/sgl-project/sglang/blob/94183a8d/test/run_suite.py#L122-L185)

 
---

 
## CI/CD Workflow Architecture

 SGLang's CI system uses GitHub Actions with multi-stage execution and hardware-specific runners to manage test execution across NVIDIA CUDA, AMD ROCm, Intel CPU/Xeon, Intel XPU, and Huawei NPU platforms.

 
### Multi-Stage Test Execution

 The primary CUDA workflow (`.github/workflows/pr-test.yml`) executes tests in stages:

 
 - **Check Changes**: Detects which packages (`main_package`, `sgl_kernel`, `jit_kernel`) need testing [.github/workflows/pr-test.yml74-81](https://github.com/sgl-project/sglang/blob/94183a8d/.github/workflows/pr-test.yml#L74-L81)
 - **Wait Jobs**: Enforces sequential execution for PRs via `wait-for-jobs` to prevent runner exhaustion [.github/workflows/pr-test.yml97-125](https://github.com/sgl-project/sglang/blob/94183a8d/.github/workflows/pr-test.yml#L97-L125)
 - **Hardware Specifics**: AMD runs utilize `pr-test-amd.yml` [.github/workflows/pr-test-amd.yml1-126](https://github.com/sgl-project/sglang/blob/94183a8d/.github/workflows/pr-test-amd.yml#L1-L126) and specialized ROCm 7.2 workflows [.github/workflows/pr-test-amd-rocm720.yml1-152](https://github.com/sgl-project/sglang/blob/94183a8d/.github/workflows/pr-test-amd-rocm720.yml#L1-L152) Nightly AMD testing is covered in `nightly-test-amd-rocm720.yml` [.github/workflows/nightly-test-amd-rocm720.yml1-152](https://github.com/sgl-project/sglang/blob/94183a8d/.github/workflows/nightly-test-amd-rocm720.yml#L1-L152)
 
 
### Slash Command Handler and Rerun Utilities

 SGLang supports developer-triggered reruns via GitHub comments (e.g., `/rerun-test`). The `slash_command_handler.py` script manages these dispatches, including a `_check_rebase_gate` to ensure PRs are up to date with `main` before wasting runner time [scripts/ci/utils/slash_command_handler.py37-151](https://github.com/sgl-project/sglang/blob/94183a8d/scripts/ci/utils/slash_command_handler.py#L37-L151) Permissions are controlled via `.github/CI_PERMISSIONS.json` [.github/CI_PERMISSIONS.json1-230](https://github.com/sgl-project/sglang/blob/94183a8d/.github/CI_PERMISSIONS.json#L1-L230)

 **CI Entity Relationship Diagram**

 
```

```

 Sources: [scripts/ci/utils/slash_command_handler.py37-151](https://github.com/sgl-project/sglang/blob/94183a8d/scripts/ci/utils/slash_command_handler.py#L37-L151) [.github/workflows/rerun-test.yml1-81](https://github.com/sgl-project/sglang/blob/94183a8d/.github/workflows/rerun-test.yml#L1-L81) [.github/CI_PERMISSIONS.json1-10](https://github.com/sgl-project/sglang/blob/94183a8d/.github/CI_PERMISSIONS.json#L1-L10)

 
---

 
## Benchmarking and Performance Testing

 SGLang provides comprehensive tools for measuring throughput and latency across various scenarios.

 
 - **Online Serving Benchmark**: `sglang.benchmark.serving` measures TTFT, ITL, and throughput under dynamic request rates.
 - **Single Batch Benchmark**: `sglang.benchmark.one_batch` measures the latency of running a single static batch without a server.
 - **Kernel Benchmarks**: `jit-kernel-benchmark-test-amd` measures performance of custom JIT operations [test/run_suite.py49](https://github.com/sgl-project/sglang/blob/94183a8d/test/run_suite.py#L49-L49)
 
 Sources: [test/run_suite.py49](https://github.com/sgl-project/sglang/blob/94183a8d/test/run_suite.py#L49-L49) [test/run_suite.py79](https://github.com/sgl-project/sglang/blob/94183a8d/test/run_suite.py#L79-L79) [test/run_suite.py173](https://github.com/sgl-project/sglang/blob/94183a8d/test/run_suite.py#L173-L173)

 
---

 
## Development Tools and Debugging

 SGLang includes specialized tools for deep-dive debugging of model outputs and tensor-level behavior.

 
### Tensor Dumper and Comparator

 Developers can dump intermediate tensors during the forward pass for comparison.

 
 - **Nightly Precision Regression**: Specific nightly suites perform automated hidden state comparisons to ensure accuracy remains stable across releases [scripts/ci/utils/slash_command_handler.py30-31](https://github.com/sgl-project/sglang/blob/94183a8d/scripts/ci/utils/slash_command_handler.py#L30-L31)
 - **Precision Baseline Store**: Managed via `test_nightly_precision_regression.py` [scripts/ci/utils/slash_command_handler.py30](https://github.com/sgl-project/sglang/blob/94183a8d/scripts/ci/utils/slash_command_handler.py#L30-L30)
 
 
### CI and Debugging Utilities

 
 - **CUDA Coredumps**: Automated generation of CUDA coredumps on failure via `SGLANG_CUDA_COREDUMP="1"` [.github/workflows/pr-test.yml59](https://github.com/sgl-project/sglang/blob/94183a8d/.github/workflows/pr-test.yml#L59-L59)
 - **VRAM Management**: Scripts like `ensure_vram_clear.sh` are used on AMD runners to prevent VRAM fragmentation across test jobs [.github/workflows/nightly-test-amd.yml152](https://github.com/sgl-project/sglang/blob/94183a8d/.github/workflows/nightly-test-amd.yml#L152-L152)
 - **Failure Analysis**: The `ci_failures_analysis.py` script monitors for consecutive failures and infrastructure-related issues [scripts/ci_monitor/ci_failures_analysis.py75-100](https://github.com/sgl-project/sglang/blob/94183a8d/scripts/ci_monitor/ci_failures_analysis.py#L75-L100)
 
 Sources: [.github/workflows/pr-test.yml58-65](https://github.com/sgl-project/sglang/blob/94183a8d/.github/workflows/pr-test.yml#L58-L65) [scripts/ci/utils/slash_command_handler.py30-31](https://github.com/sgl-project/sglang/blob/94183a8d/scripts/ci/utils/slash_command_handler.py#L30-L31) [scripts/ci_monitor/ci_failures_analysis.py75-100](https://github.com/sgl-project/sglang/blob/94183a8d/scripts/ci_monitor/ci_failures_analysis.py#L75-L100)

 
---

 
## Child Pages

 
 - [Test Infrastructure and CI/CD](https://deepwiki.com/sgl-project/sglang/15.1-test-infrastructure-and-cicd) — Explain test orchestration, CI registry system, GitHub Actions workflows, and CI monitoring.
 - [Benchmarking and Performance Measurement](https://deepwiki.com/sgl-project/sglang/15.2-benchmarking-and-performance-measurement) — Document benchmarking tools, `bench_serving`, `bench_one_batch`, and performance testing infrastructure.
 - [Test Runners and Model Comparison](https://deepwiki.com/sgl-project/sglang/15.3-test-runners-and-model-comparison) — Explain `HFRunner` vs `SRTRunner`, test utilities, output comparison, and evaluation scripts.
 - [Development Tools and Debugging](https://deepwiki.com/sgl-project/sglang/15.4-development-tools-and-debugging) — Cover tensor dumper, dump comparator, debug utilities, CUDA coredump handling, nightly precision regression testing, offline mode for CI, and where to find internal playbooks (`scripts/` and `.claude/`).
