> 来源: [https://deepwiki.com/TransformerLensOrg/TransformerLens/9-model-registry-and-benchmarking](https://deepwiki.com/TransformerLensOrg/TransformerLens/9-model-registry-and-benchmarking)
> DeepWiki TransformerLensOrg/TransformerLens | Last indexed: 16 July 2026 (4ba218

# Model Registry and Benchmarking

  Relevant source files 
 - [transformer_lens/benchmarks/main_benchmark.py](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/transformer_lens/benchmarks/main_benchmark.py)
 - [transformer_lens/factories/architecture_adapter_factory.py](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/transformer_lens/factories/architecture_adapter_factory.py)
 - [transformer_lens/model_bridge/generalized_components/__init__.py](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/transformer_lens/model_bridge/generalized_components/__init__.py)
 - [transformer_lens/model_bridge/sources/transformers.py](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/transformer_lens/model_bridge/sources/transformers.py)
 - [transformer_lens/model_bridge/supported_architectures/__init__.py](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/transformer_lens/model_bridge/supported_architectures/__init__.py)
 - [transformer_lens/tools/model_registry/__init__.py](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/transformer_lens/tools/model_registry/__init__.py)
 - [transformer_lens/tools/model_registry/data/architecture_gaps.json](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/transformer_lens/tools/model_registry/data/architecture_gaps.json)
 - [transformer_lens/tools/model_registry/data/supported_models.json](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/transformer_lens/tools/model_registry/data/supported_models.json)
 - [transformer_lens/tools/model_registry/data/verification_history.json](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/transformer_lens/tools/model_registry/data/verification_history.json)
 - [transformer_lens/tools/model_registry/generate_report.py](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/transformer_lens/tools/model_registry/generate_report.py)
 - [transformer_lens/tools/model_registry/hf_scraper.py](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/transformer_lens/tools/model_registry/hf_scraper.py)
 - [transformer_lens/tools/model_registry/verify_models.py](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/transformer_lens/tools/model_registry/verify_models.py)
 - [transformer_lens/utilities/architectures.py](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/transformer_lens/utilities/architectures.py)
 
  The Model Registry and Benchmarking system provides a rigorous framework for verifying that models loaded via `TransformerBridge` maintain numerical parity and functional integrity compared to their HuggingFace reference implementations. This system ensures that the 50+ supported architectures in TransformerLens are reliable for mechanistic interpretability research.

 
### System Overview

 The system consists of three main pillars:

 
 - **The Registry**: A data-driven inventory of compatible models and their verification status.
 - **The Scraper**: An automated tool for discovering new compatible models on the HuggingFace Hub.
 - **The Benchmark Suite**: A multi-phase verification pipeline that tests everything from logit parity to activation hook shapes.
 
 
### Code Entity Relationship

 The following diagram illustrates how the natural language concepts of "Registry" and "Benchmarking" map to specific code entities within the `transformer_lens` package.

 **Registry and Verification Architecture**

 
```

```

 Sources: [transformer_lens/tools/model_registry/__init__.py1-17](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/transformer_lens/tools/model_registry/__init__.py#L1-L17) [transformer_lens/benchmarks/main_benchmark.py1-12](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/transformer_lens/benchmarks/main_benchmark.py#L1-L12) [transformer_lens/tools/model_registry/verify_models.py1-24](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/transformer_lens/tools/model_registry/verify_models.py#L1-L24)

 
---

 
## Model Registry

 The Model Registry is the source of truth for model support in TransformerLens. It tracks over 12,000 models across 65+ architectures, providing metadata on whether a model has been fully verified, is known to be broken, or is too large for standard testing environments.

 
### Key Components

 
 - **`supported_models.json`**: The primary database containing model IDs, architecture IDs, and verification scores (Phases 1-8). [transformer_lens/tools/model_registry/data/supported_models.json1-26](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/transformer_lens/tools/model_registry/data/supported_models.json#L1-L26)
 - **`architecture_gaps.json`**: Tracks popular HuggingFace architectures that do not yet have a `ArchitectureAdapter` in TransformerLens, helping prioritize development. [transformer_lens/tools/model_registry/data/architecture_gaps.json1-30](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/transformer_lens/tools/model_registry/data/architecture_gaps.json#L1-L30)
 - **Verification Statuses**: 
 - `0`: Unverified
 - `1`: Verified (Passed parity checks)
 - `2`: Skipped (e.g., OOM or incompatible quantization)
 - `3`: Failed (Numerical divergence detected)
 
 For details on how to check model support or contribute to the registry, see **[Model Registry](https://deepwiki.com/TransformerLensOrg/TransformerLens/9.1-model-registry)**.

 Sources: [transformer_lens/tools/model_registry/api.py1-24](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/transformer_lens/tools/model_registry/api.py#L1-L24) [transformer_lens/tools/model_registry/registry_io.py46-57](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/transformer_lens/tools/model_registry/registry_io.py#L46-L57)

 
---

 
## Benchmarking and Verification

 The benchmarking system is designed to catch regressions and ensure that `TransformerBridge` (v3) provides the same internal activations as the original models. It uses a phased approach to minimize compute while maximizing coverage.

 
### Benchmark Phases (P1-P8)

 The suite is divided into specific phases to isolate different failure modes:

 
| Phase | Name | Description |
|---|---|---|
| P1 | HF vs Bridge | Compares raw HuggingFace output against TransformerBridge (unprocessed). |
| P2 | Bridge vs Hooked | Compares TransformerBridge against legacy HookedTransformer. |
| P3 | Full Processing | Tests compatibility mode with weight processing (folding/centering). |
| P4 | Text Quality | Measures perplexity via GPT-2 Medium to ensure no weights were corrupted. |
| P7 | Multimodal | Specialized tests for vision-language models (e.g., LLaVA). |
| P8 | Audio | Specialized tests for audio models (e.g., HuBERT). |

 **Verification Flow**

 
```

```

 Sources: [transformer_lens/benchmarks/main_benchmark.py5-12](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/transformer_lens/benchmarks/main_benchmark.py#L5-L12) [transformer_lens/tools/model_registry/verify_models.py112-124](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/transformer_lens/tools/model_registry/verify_models.py#L112-L124) [transformer_lens/benchmarks/forward_pass.py36-40](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/transformer_lens/benchmarks/forward_pass.py#L36-L40)

 
### Key Tools

 
 - **`run_benchmark_suite`**: The high-level entry point for testing a single model. [transformer_lens/benchmarks/main_benchmark.py172-180](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/transformer_lens/benchmarks/main_benchmark.py#L172-L180)
 - **`verify_models.py`**: A batch processing script that iterates through the registry, handles memory management, and updates the JSON data. [transformer_lens/tools/model_registry/verify_models.py1-24](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/transformer_lens/tools/model_registry/verify_models.py#L1-L24)
 
 For details on running these tools and interpreting numerical parity results, see **[Benchmarking and Verification](https://deepwiki.com/TransformerLensOrg/TransformerLens/9.2-benchmarking-and-verification)**.

 Sources: [transformer_lens/benchmarks/main_benchmark.py1-12](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/transformer_lens/benchmarks/main_benchmark.py#L1-L12) [transformer_lens/tools/model_registry/verify_models.py141-150](https://github.com/TransformerLensOrg/TransformerLens/blob/4ba2187b/transformer_lens/tools/model_registry/verify_models.py#L141-L150)
