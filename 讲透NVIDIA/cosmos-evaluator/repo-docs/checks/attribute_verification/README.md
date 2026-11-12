# Attribute Verification

This module verifies whether key attributes in augmented image or video media match the expected values configured in
`cosmos_evaluator.yaml`. It generates multiple-choice questions with an LLM and answers them with a VLM.

## Architecture

The system is built with a modular design consisting of several core components:

### Modules

- **`processor.py`**: `AttributeVerificationProcessor` - Orchestrates question generation, VLM verification, and summary scoring.
- **`question_generator.py`**: `LLMQuestionGenerator` - Generates one or more multiple-choice verification questions from configured variables/options.
- **`vlm_verifier.py`**: `VLMVerifier` - Answers questions against an image or sampled video frames.
- **`run.py`**: CLI entry point that wires argument parsing, configuration, and results.

### Entry Point

- **`run.py`**: Main entry point with command line interface and configuration management.

## Usage

### Prerequisites

- Create a new `.env` file in the `checks/attribute_verification` directory based on `.env.example`.
- Ensure your multistorage credentials can access the target `--augmented-video-path`.
- Set `LLM_API_KEY` for question generation and `VLM_API_KEY` for visual verification when the configured endpoints
  require authentication. A custom endpoint may instead name its credential with `api_key_env`; the legacy shared
  `BUILD_NVIDIA_API_KEY` remains a compatibility fallback.

### Command Line Interface

```bash
usage: run.py [-h] [--clip-id CLIP_ID] --augmented-video-path AUGMENTED_VIDEO_PATH [--config CONFIG] [--config-dir CONFIG_DIR] [--verbose {DEBUG,INFO,WARNING,ERROR}] [--env-file ENV_FILE] [--output-dir OUTPUT_DIR]

Attribute Verification Tool

options:
  -h, --help            show this help message and exit
  --clip-id CLIP_ID     Clip ID for processing
  --augmented-video-path AUGMENTED_VIDEO_PATH
                        Path to the augmented image or video
  --config CONFIG       Configuration file name (without .yaml extension) (default: cosmos_evaluator)
  --config-dir CONFIG_DIR
                        Path to the configuration directory
  --verbose {DEBUG,INFO,WARNING,ERROR}
                        Set logging level (DEBUG, INFO, WARNING, ERROR) (default: INFO)
  --env-file ENV_FILE   Path to the .env file to load (default: checks/attribute_verification/.env)
  --output-dir OUTPUT_DIR
                        Path to the output directory (default: outputs)
```

### Example Command

```bash
dazel run --auto_output_filter=none //checks/attribute_verification:run -- --augmented-video-path s3://omniverse-metropolis-sdg-dev-us-west-2/common/cosmos_evaluator/test_inputs/attribute_verification/sunny_morning.mp4
```

## Features

- **Modular Design**: Clear separation between question generation, verification, and orchestration.
- **Configuration Management**: Uses `cosmos_evaluator.yaml` for selected variables, options, prompts, and model settings.
- **Comprehensive Logging**: Progress and per-check diagnostics with configurable verbosity.
- **Curated or generated choices**: Constrains answers to configured options, or lets the LLM create distractors.
- **Fixed questions and reasoning**: Supports additional configured MCQs with optional brief explanations.
- **Image and multi-frame video evidence**: Sends images directly or evenly samples configured frames from a video.
- **Structured Results**: Separates incorrect verdicts from checks that could not obtain a VLM verdict.

## Processing Pipeline

1. **Input Validation**: Validate that the augmented media URI exists and is accessible.
2. **Config Loading**: Load `metropolis.attribute_verification` configuration from `cosmos_evaluator.yaml`.
3. **Question Generation (LLM)**: Generate and repair questions for non-excluded variables, then append valid fixed questions.
4. **Question Answering (VLM)**: Ask each question against the image or sampled video frames.
5. **Summary Computation**: Aggregate `passed_checks`, `failed_checks`, and `errored_checks` and compute overall pass/fail.
6. **Result Serialization**: Write JSON results to `{clip_id}.attribute_verification.results.json`.

## Output

- **Overall Pass/Fail**: `true` if all checks pass, otherwise `false`.
- **Summary**: Total, passed, failed, and errored checks. A run with no valid questions fails with `no_questions`.
- **Per-check Details**: Variable/value, question/options, expected and VLM answers, optional reasoning, and optional error.
- **JSON Results**: Saved to `{clip_id}.attribute_verification.results.json`.

### Console Output Example

```text
Validating augmented video path: s3://omniverse-metropolis-sdg-dev-us-west-2/common/cosmos_evaluator/test_inputs/attribute_verification/sunny_morning.mp4
Error processing sample: The provided LLM endpoint was not found. Please check the LLM endpoint and model.
```

When configured successfully, the CLI also prints:

- `Check complete, results saved to: ...`
- `Passed: <bool>`
- `Total checks: <int>`
- `Passed checks: <int>`
- `Failed checks: <int>`
- `Errored checks: <int>`
- A `Checks:` section with one line per verified variable.

### JSON Results Format

```json
{
  "clip_id": "f260297f-ec80-4673-9f5d-d7786da8f0dc",
  "passed": true,
  "summary": {
    "total_checks": 2,
    "passed_checks": 2,
    "failed_checks": 0,
    "errored_checks": 0,
    "reason": null
  },
  "checks": [
    {
      "variable": "weather",
      "value": "sunny",
      "question": "What is the weather in this video?",
      "options": {
        "A": "sunny",
        "B": "rainy"
      },
      "expected_answer": "A",
      "request_reasoning": false,
      "vlm_answer": "A",
      "vlm_reasoning": null,
      "passed": true,
      "error": null
    }
  ],
  "duration_seconds": 1.25
}
```

## Troubleshooting

### Common Issues

1. **LLM endpoint not found (404)**: Verify LLM endpoint/model settings in config and environment.
2. **Unauthorized/invalid API key**: Verify credentials for the configured LLM/VLM endpoints.
3. **Video URI cannot be accessed**: Ensure storage credentials are set and the `--augmented-video-path` exists.
4. **Missing `.env` file**: Either create `checks/attribute_verification/.env` or pass `--env-file` explicitly.
