> 来源: [https://deepwiki.com/huggingface/transformers/10-pipelines](https://deepwiki.com/huggingface/transformers/10-pipelines)
> DeepWiki huggingface/transformers | Last indexed: 3 September 2026 (8f5420

# Pipelines

  Relevant source files 
 - [docs/source/en/tasks/zero_shot_object_detection.md](https://github.com/huggingface/transformers/blob/8f542025/docs/source/en/tasks/zero_shot_object_detection.md?plain=1)
 - [pyproject.toml](https://github.com/huggingface/transformers/blob/8f542025/pyproject.toml)
 - [src/transformers/_typing.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/_typing.py)
 - [src/transformers/pipelines/__init__.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/pipelines/__init__.py)
 - [src/transformers/pipelines/any_to_any.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/pipelines/any_to_any.py)
 - [src/transformers/pipelines/audio_classification.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/pipelines/audio_classification.py)
 - [src/transformers/pipelines/base.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/pipelines/base.py)
 - [src/transformers/pipelines/depth_estimation.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/pipelines/depth_estimation.py)
 - [src/transformers/pipelines/feature_extraction.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/pipelines/feature_extraction.py)
 - [src/transformers/pipelines/image_classification.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/pipelines/image_classification.py)
 - [src/transformers/pipelines/image_segmentation.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/pipelines/image_segmentation.py)
 - [src/transformers/pipelines/image_text_to_text.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/pipelines/image_text_to_text.py)
 - [src/transformers/pipelines/mask_generation.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/pipelines/mask_generation.py)
 - [src/transformers/pipelines/object_detection.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/pipelines/object_detection.py)
 - [src/transformers/pipelines/text_generation.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/pipelines/text_generation.py)
 - [src/transformers/pipelines/video_classification.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/pipelines/video_classification.py)
 - [src/transformers/pipelines/zero_shot_audio_classification.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/pipelines/zero_shot_audio_classification.py)
 - [src/transformers/pipelines/zero_shot_image_classification.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/pipelines/zero_shot_image_classification.py)
 - [tests/pipelines/test_pipelines_any_to_any.py](https://github.com/huggingface/transformers/blob/8f542025/tests/pipelines/test_pipelines_any_to_any.py)
 - [tests/pipelines/test_pipelines_audio_classification.py](https://github.com/huggingface/transformers/blob/8f542025/tests/pipelines/test_pipelines_audio_classification.py)
 - [tests/pipelines/test_pipelines_common.py](https://github.com/huggingface/transformers/blob/8f542025/tests/pipelines/test_pipelines_common.py)
 - [tests/pipelines/test_pipelines_depth_estimation.py](https://github.com/huggingface/transformers/blob/8f542025/tests/pipelines/test_pipelines_depth_estimation.py)
 - [tests/pipelines/test_pipelines_image_classification.py](https://github.com/huggingface/transformers/blob/8f542025/tests/pipelines/test_pipelines_image_classification.py)
 - [tests/pipelines/test_pipelines_image_segmentation.py](https://github.com/huggingface/transformers/blob/8f542025/tests/pipelines/test_pipelines_image_segmentation.py)
 - [tests/pipelines/test_pipelines_image_text_to_text.py](https://github.com/huggingface/transformers/blob/8f542025/tests/pipelines/test_pipelines_image_text_to_text.py)
 - [tests/pipelines/test_pipelines_mask_generation.py](https://github.com/huggingface/transformers/blob/8f542025/tests/pipelines/test_pipelines_mask_generation.py)
 - [tests/pipelines/test_pipelines_object_detection.py](https://github.com/huggingface/transformers/blob/8f542025/tests/pipelines/test_pipelines_object_detection.py)
 - [tests/pipelines/test_pipelines_text_generation.py](https://github.com/huggingface/transformers/blob/8f542025/tests/pipelines/test_pipelines_text_generation.py)
 - [tests/pipelines/test_pipelines_video_classification.py](https://github.com/huggingface/transformers/blob/8f542025/tests/pipelines/test_pipelines_video_classification.py)
 - [tests/pipelines/test_pipelines_zero_shot_image_classification.py](https://github.com/huggingface/transformers/blob/8f542025/tests/pipelines/test_pipelines_zero_shot_image_classification.py)
 - [tests/test_pipeline_mixin.py](https://github.com/huggingface/transformers/blob/8f542025/tests/test_pipeline_mixin.py)
 - [utils/check_types.py](https://github.com/huggingface/transformers/blob/8f542025/utils/check_types.py)
 
  The `pipeline()` API is the highest-level abstraction in the Transformers library, designed to provide zero-code inference capabilities for a vast array of machine learning tasks. It orchestrates the entire inference lifecycle—from raw input preprocessing to model execution and output post-processing—abstracting away the complexities of specific model architectures and data modalities.

 
### Core Architecture

 The foundation of this system is the `Pipeline` base class defined in [src/transformers/pipelines/base.py58](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/pipelines/base.py#L58-L58) Every task-specific pipeline inherits from this class and implements a standard lifecycle:

 
 - **Preprocessing**: Converting raw inputs (text, images, audio) into model-ready tensors via `preprocess`.
 - **Inference**: Running the forward pass of the model via `forward`.
 - **Post-processing**: Converting raw logits or tensors back into human-readable formats via `postprocess`.
 - **Batching/Streaming**: Handling data iteration via `DataLoader` for efficient processing [src/transformers/pipelines/base.py60-65](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/pipelines/base.py#L60-L65)
 
 The `pipeline()` factory function handles task routing by looking up the requested task in the `SUPPORTED_TASKS` registry [src/transformers/pipelines/__init__.py141](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/pipelines/__init__.py#L141-L141) This registry maps task strings (e.g., `"text-classification"`) to their implementation classes, default models, and required `AutoModel` classes [src/transformers/pipelines/__init__.py141-172](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/pipelines/__init__.py#L141-L172)

 
#### Pipeline Initialization & Routing

 The following diagram illustrates how the `pipeline()` function resolves a user request into a concrete `Pipeline` instance.

 **Diagram: Pipeline Initialization & Routing**

 
```

```

 **Sources:** [src/transformers/pipelines/__init__.py136-172](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/pipelines/__init__.py#L136-L172) [src/transformers/pipelines/base.py58-69](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/pipelines/base.py#L58-L69) [src/transformers/pipelines/base.py124-180](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/pipelines/base.py#L124-L180)

 
---

 
### Task Support and Modalities

 The pipeline API supports a diverse set of modalities, each handled by specialized subclasses. The system is extensible, allowing for custom pipelines via the `PipelineRegistry` [src/transformers/pipelines/base.py61](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/pipelines/base.py#L61-L61)

 
#### Text and Conversational Tasks

 Text-based pipelines primarily utilize `PreTrainedTokenizer` for input handling [src/transformers/pipelines/base.py38](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/pipelines/base.py#L38-L38) Key tasks include:

 
 - **Text Generation**: Using `TextGenerationPipeline` for autoregressive models like GPT-2 or Llama [src/transformers/pipelines/text_generation.py23](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/pipelines/text_generation.py#L23-L23) It supports both raw text and `Chat` objects for conversational modes [src/transformers/pipelines/text_generation.py27-28](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/pipelines/text_generation.py#L27-L28)
 - **Classification**: Sentiment analysis and NER via `TextClassificationPipeline` and `TokenClassificationPipeline` [src/transformers/pipelines/__init__.py77-85](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/pipelines/__init__.py#L77-L85)
 - **Any-to-Any**: A unified interface for multimodal inputs and outputs [src/transformers/pipelines/__init__.py50](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/pipelines/__init__.py#L50-L50)
 
 For details on chat templating, tool-call parsing, and streaming, see [Text & Conversational Pipelines](https://deepwiki.com/huggingface/transformers/10.1-text-and-conversational-pipelines).

 
#### Vision, Audio, and Multimodal Tasks

 These pipelines rely on `BaseImageProcessor`, `BaseVideoProcessor`, or `FeatureExtractionMixin` to handle non-textual data [src/transformers/pipelines/base.py34-37](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/pipelines/base.py#L34-L37)

 
 - **Audio**: `AutomaticSpeechRecognitionPipeline` supports Whisper and CTC-based models [src/transformers/pipelines/__init__.py148-153](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/pipelines/__init__.py#L148-L153)
 - **Vision**: Includes `ImageClassificationPipeline`, `ObjectDetectionPipeline`, and `DepthEstimationPipeline` [src/transformers/pipelines/__init__.py65-75](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/pipelines/__init__.py#L65-L75)
 - **Multimodal**: `ImageTextToTextPipeline` generates text from combined image and text prompts, supporting conversational message formats [src/transformers/pipelines/image_text_to_text.py53-64](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/pipelines/image_text_to_text.py#L53-L64)
 
 For details on signal processing and vision-specific outputs, see [Vision, Audio & Multimodal Pipelines](https://deepwiki.com/huggingface/transformers/10.2-vision-audio-and-multimodal-pipelines).

 
---

 
### Internal Execution Flow

 The `Pipeline` class manages the transition between data states. It utilizes a `pad_collate_fn` to handle batching when `batch_size > 1` is specified, ensuring that heterogeneous input lengths (like `input_ids` or `pixel_values`) are correctly padded using the tokenizer's or feature extractor's settings [src/transformers/pipelines/base.py124-180](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/pipelines/base.py#L124-L180)

 **Diagram: Data Transformation Flow**

 
```

```

 **Sources:** [src/transformers/pipelines/base.py34-38](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/pipelines/base.py#L34-L38) [src/transformers/pipelines/base.py124-180](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/pipelines/base.py#L124-L180) [src/transformers/pipelines/text_generation.py86-90](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/pipelines/text_generation.py#L86-L90)

 
### Integration with PEFT

 Pipelines seamlessly support models with adapters. When a model is loaded via `pipeline()`, the environment checks for PEFT availability [src/transformers/pipelines/__init__.py44](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/pipelines/__init__.py#L44-L44) If the model identifier points to a PEFT adapter, the underlying `load_model` utility handles the integration of the adapter weights into the base architecture.

 **Sources:** [src/transformers/pipelines/__init__.py44](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/pipelines/__init__.py#L44-L44) [src/transformers/pipelines/base.py63-64](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/pipelines/base.py#L63-L64)
