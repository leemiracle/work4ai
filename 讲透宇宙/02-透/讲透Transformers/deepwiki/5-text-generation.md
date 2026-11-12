> 来源: [https://deepwiki.com/huggingface/transformers/5-text-generation](https://deepwiki.com/huggingface/transformers/5-text-generation)
> DeepWiki huggingface/transformers | Last indexed: 3 September 2026 (8f5420

# Text Generation

  Relevant source files 
 - [benchmark_v2/benchmark_scripts/continuous_batching_overall.py](https://github.com/huggingface/transformers/blob/8f542025/benchmark_v2/benchmark_scripts/continuous_batching_overall.py)
 - [docs/source/en/internal/generation_utils.md](https://github.com/huggingface/transformers/blob/8f542025/docs/source/en/internal/generation_utils.md?plain=1)
 - [docs/source/en/main_classes/text_generation.md](https://github.com/huggingface/transformers/blob/8f542025/docs/source/en/main_classes/text_generation.md?plain=1)
 - [docs/source/ko/internal/generation_utils.md](https://github.com/huggingface/transformers/blob/8f542025/docs/source/ko/internal/generation_utils.md?plain=1)
 - [examples/pytorch/continuous_batching.py](https://github.com/huggingface/transformers/blob/8f542025/examples/pytorch/continuous_batching.py)
 - [src/transformers/cache_utils.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/cache_utils.py)
 - [src/transformers/generation/__init__.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/generation/__init__.py)
 - [src/transformers/generation/candidate_generator.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/generation/candidate_generator.py)
 - [src/transformers/generation/configuration_utils.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/generation/configuration_utils.py)
 - [src/transformers/generation/continuous_batching/cache.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/generation/continuous_batching/cache.py)
 - [src/transformers/generation/continuous_batching/cache_manager.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/generation/continuous_batching/cache_manager.py)
 - [src/transformers/generation/continuous_batching/continuous_api.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/generation/continuous_batching/continuous_api.py)
 - [src/transformers/generation/continuous_batching/initialization.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/generation/continuous_batching/initialization.py)
 - [src/transformers/generation/continuous_batching/input_outputs.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/generation/continuous_batching/input_outputs.py)
 - [src/transformers/generation/continuous_batching/model_runner.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/generation/continuous_batching/model_runner.py)
 - [src/transformers/generation/continuous_batching/requests.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/generation/continuous_batching/requests.py)
 - [src/transformers/generation/continuous_batching/scheduler.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/generation/continuous_batching/scheduler.py)
 - [src/transformers/generation/continuous_batching/utils.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/generation/continuous_batching/utils.py)
 - [src/transformers/generation/logits_process.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/generation/logits_process.py)
 - [src/transformers/generation/utils.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/generation/utils.py)
 - [src/transformers/generation/watermarking.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/generation/watermarking.py)
 - [src/transformers/integrations/eager_paged.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/integrations/eager_paged.py)
 - [src/transformers/integrations/executorch.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/integrations/executorch.py)
 - [src/transformers/integrations/flash_paged.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/integrations/flash_paged.py)
 - [src/transformers/integrations/sdpa_paged.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/integrations/sdpa_paged.py)
 - [src/transformers/masking_utils.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/masking_utils.py)
 - [tests/generation/test_candidate_generator.py](https://github.com/huggingface/transformers/blob/8f542025/tests/generation/test_candidate_generator.py)
 - [tests/generation/test_continuous_batching.py](https://github.com/huggingface/transformers/blob/8f542025/tests/generation/test_continuous_batching.py)
 - [tests/generation/test_logits_process.py](https://github.com/huggingface/transformers/blob/8f542025/tests/generation/test_logits_process.py)
 - [tests/generation/test_utils.py](https://github.com/huggingface/transformers/blob/8f542025/tests/generation/test_utils.py)
 - [tests/utils/test_cache_utils.py](https://github.com/huggingface/transformers/blob/8f542025/tests/utils/test_cache_utils.py)
 - [tests/utils/test_masking_utils.py](https://github.com/huggingface/transformers/blob/8f542025/tests/utils/test_masking_utils.py)
 
  The text generation subsystem in `transformers` provides a high-level API for autoregressive decoding across various modalities, including text-decoder, text-to-text, speech-to-text, and vision-to-text models. It is centered around the `GenerationMixin` class, which orchestrates the complex interaction between model forward passes, KV caching, logits processing, and stopping criteria.

 
### System Overview

 The generation process is initiated via the `generate()` method, which serves as the primary entry point. Based on the configuration provided in `GenerationConfig`, the system selects a decoding strategy (e.g., greedy search, multinomial sampling, or beam search) and manages the iterative generation of tokens. The system also supports advanced features like speculative decoding via `CandidateGenerator` and high-throughput inference via `ContinuousMixin`.

 **Sources:** [src/transformers/generation/utils.py2417-2450](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/generation/utils.py#L2417-L2450) [src/transformers/generation/configuration_utils.py100-110](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/generation/configuration_utils.py#L100-L110)

 
#### Generation Workflow

 The following diagram illustrates how the natural language generation request is mapped to internal code entities and the iterative loop.

 **Text Generation Execution Flow**

 
```

```

 **Sources:** [src/transformers/generation/utils.py137-148](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/generation/utils.py#L137-L148) [src/transformers/generation/configuration_utils.py82-98](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/generation/configuration_utils.py#L82-L98)

 
---

 
### Core Components

 
#### 1. GenerationMixin & Decoding Strategies

 The `GenerationMixin` is the base class providing the `generate()` method to `PreTrainedModel`. It handles the logic for different `GenerationMode` types. The mapping `GENERATION_MODES_MAPPING` directs the request to specific internal methods like `_sample` or `_beam_search`. It also supports speculative decoding through `CandidateGenerator` implementations such as `AssistedCandidateGenerator` or `PromptLookupCandidateGenerator`.

 For details, see [GenerationMixin & Decoding Strategies](https://deepwiki.com/huggingface/transformers/5.1-generationmixin-and-decoding-strategies).

 **Sources:** [src/transformers/generation/utils.py137-148](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/generation/utils.py#L137-L148) [src/transformers/generation/candidate_generator.py39-42](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/generation/candidate_generator.py#L39-L42) [src/transformers/generation/configuration_utils.py82-98](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/generation/configuration_utils.py#L82-L98)

 
#### 2. KV Cache Implementations

 To avoid redundant computations during autoregressive generation, the system utilizes Key-Value (KV) caching. The `Cache` abstract base class defines the interface for storing and updating these tensors.

 
 - **DynamicCache:** The default implementation that grows dynamically. [src/transformers/cache_utils.py113-117](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/cache_utils.py#L113-L117)
 - **StaticCache:** Pre-allocates memory for a fixed maximum length, enabling optimizations like `torch.compile`. [src/transformers/cache_utils.py243-247](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/cache_utils.py#L243-L247)
 - **QuantizedCache:** Reduces memory footprint by quantizing stored KV pairs (e.g., using HQQ or Quanto). [src/transformers/cache_utils.py884-888](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/cache_utils.py#L884-L888)
 - **EncoderDecoderCache:** A wrapper for models with separate encoder and decoder KV states. [src/transformers/cache_utils.py1770-1775](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/cache_utils.py#L1770-L1775)
 
 For details, see [KV Cache Implementations](https://deepwiki.com/huggingface/transformers/5.2-kv-cache-implementations).

 **Sources:** [src/transformers/cache_utils.py27-111](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/cache_utils.py#L27-L111) [src/transformers/cache_utils.py113-117](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/cache_utils.py#L113-L117) [src/transformers/cache_utils.py243-247](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/cache_utils.py#L243-L247)

 
#### 3. Logits Processors & Stopping Criteria

 The generation loop is customized using two primary lists of callables:

 
 - **LogitsProcessorList:** A collection of `LogitsProcessor` objects that modify the model's output scores (e.g., `TemperatureLogitsWarper`, `TopKLogitsWarper`, `RepetitionPenaltyLogitsProcessor`). [src/transformers/generation/logits_process.py63-68](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/generation/logits_process.py#L63-L68)
 - **StoppingCriteriaList:** A collection of `StoppingCriteria` objects that determine when the generation should terminate (e.g., `MaxLengthCriteria`, `EosTokenCriteria`, `StopStringCriteria`). [src/transformers/generation/stopping_criteria.py105-113](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/generation/stopping_criteria.py#L105-L113)
 
 For details, see [Logits Processors, Stopping Criteria & Watermarking](https://deepwiki.com/huggingface/transformers/5.3-logits-processors-stopping-criteria-and-watermarking).

 **Sources:** [src/transformers/generation/logits_process.py63-68](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/generation/logits_process.py#L63-L68) [src/transformers/generation/stopping_criteria.py105-113](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/generation/stopping_criteria.py#L105-L113)

 
#### 4. Continuous Batching

 For high-throughput inference scenarios, the library supports continuous batching via the `ContinuousMixin`. This architecture uses a `Scheduler` (e.g., `FIFOScheduler`) and a `PagedAttentionCache` to manage multiple requests concurrently, allowing new requests to join the batch at any time.

 For details, see [Continuous Batching](https://deepwiki.com/huggingface/transformers/5.4-continuous-batching).

 **Sources:** [src/transformers/generation/utils.py76](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/generation/utils.py#L76-L76) [src/transformers/generation/continuous_batching/continuous_api.py84-90](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/generation/continuous_batching/continuous_api.py#L84-L90) [src/transformers/generation/continuous_batching/scheduler.py27-35](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/generation/continuous_batching/scheduler.py#L27-L35)

 
---

 
### Logic Mapping: Input to Code

 This diagram bridges the conceptual "Decoding Parameters" to the internal classes and processors that implement them.

 **Parameter to Logic Mapping**

 
```

```

 **Sources:** [src/transformers/generation/configuration_utils.py100-160](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/generation/configuration_utils.py#L100-L160) [src/transformers/generation/utils.py137-148](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/generation/utils.py#L137-L148) [src/transformers/generation/candidate_generator.py80-85](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/generation/candidate_generator.py#L80-L85)

 
### Summary Table of Components

 
| Component | Code Entity | Role |
|---|---|---|
| Orchestrator | GenerationMixin | Iterates the generation loop and manages state. |
| Configuration | GenerationConfig | Holds hyperparameters and strategy flags. |
| Cache Manager | Cache / DynamicCache | Manages KV tensors to speed up inference. |
| Speculative Decoding | CandidateGenerator | Generates draft tokens to be verified by the main model. |
| Logits Modifier | LogitsProcessorList | Applies filters and warpers to the vocabulary scores. |
| Termination | StoppingCriteriaList | Checks for stop tokens, length, or time limits. |
| Batching API | ContinuousBatchingAPI | Orchestrates high-throughput, multi-request inference. |

 **Sources:** [src/transformers/generation/utils.py169-185](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/generation/utils.py#L169-L185) [src/transformers/cache_utils.py243](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/cache_utils.py#L243-L243) [src/transformers/generation/candidate_generator.py39-42](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/generation/candidate_generator.py#L39-L42) [src/transformers/generation/continuous_batching/continuous_api.py138-146](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/generation/continuous_batching/continuous_api.py#L138-L146)
