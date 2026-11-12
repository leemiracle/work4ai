# Attribute Verification Check

This checker verifies whether key attributes in augmented image or video media match the expected values configured in
`checks/cosmos_evaluator.yaml`. It answers the question *"Does this output show the attributes I requested from
Cosmos?"* and can filter outputs whose visible attributes do not match.

## How it works

The attribute verification check evaluates augmented image or video media against expected scene attributes, such as
weather or time of day.

The processing pipeline is:

1. **Question Generation (LLM)**: Generate one multiple-choice verification question for each selected variable. For example:

    ```
    What is the weather like in the video frame?
    A: cloudy
    B: sunny
    C: rainy
    ```

2. **Question Repair**: Normalize fine-grained values to configured options, remove duplicate or confusing choices, and
   ensure the expected value and answer letter agree. Optional fixed questions are then appended.
3. **Evidence Preparation**: Send an image directly, or extract the configured number of evenly spaced video frames.
4. **Question Answering (VLM)**: Ask each question against the prepared evidence and compare the final parsed answer to
   the expected answer. Fixed questions may request a brief explanation.
5. **Pass/Fail Decision**: Pass only when every question receives the expected verdict. Incorrect verdicts and calls
   that fail to produce a verdict are reported separately.

The implementation is split across:

- `processor.py`, which orchestrates question generation, VLM verification, and summary scoring
- `question_generator.py`, which generates multiple-choice questions from configured variables and options
- `vlm_verifier.py`, which prepares image or sampled video evidence and answers questions with the configured VLM
- `run.py`, which provides CLI config loading, execution, and result serialization

## Prerequisites and Compute Requirements

* **LLM and VLM endpoints**: A VLM endpoint is required. An LLM endpoint is also required when generating questions
  from `selected_variables`; a run containing only `extra_questions` skips question generation. See
  [Model Setup](#model-setup) for details.
* **S3 Bucket and Credentials**: S3 can store input media for the attribute verification checker. Set up the attribute
  verification `.env` file with this information if needed by following the
  [Getting Started Guide](../getting_started.md#attribute-verification-check).
* **Checker Compute Requirements**: The checker container on its own is lightweight and CPU-only. Any linux machine will be able to run this checker.
* **LLM and VLM Compute Requirements**: Any locally deployed LLM or VLM will require a GPU to run. The compute requirements may vary depending on which LLM or VLM is deployed, with specific compute requirements found on the `Model Card` for the model on the [build.nvidia.com](https://build.nvidia.com) website. The default LLM and VLM for this checker require the following resources:
  - `qwen/qwen3-next-80b-a3b-instruct` (default LLM):
    * NVIDIA Ampere: A100
    * NVIDIA Blackwell: B200, B100
    * NVIDIA Hopper: H100, H200
    * See the [Model Card](https://build.nvidia.com/qwen/qwen3-next-80b-a3b-instruct/modelcard) for more information
  - `qwen/qwen3.5-397b-a17b` (default VLM):
    * NVIDIA Ampere: A100
    * NVIDIA Blackwell: B100, B200, GB200
    * NVIDIA Hopper: H100, H20
    * See the [Model Card](https://build.nvidia.com/qwen/qwen3.5-397b-a17b/modelcard) for more information

  Compute is not required if connecting to an external LLM or VLM.


## Inputs

The check requires:

* **Augmented media**: the Cosmos-augmented image or video being evaluated
* **Selected variables**: A dictionary with the expected attribute values to verify, such as `weather: sunny`. Each item in the dictionary corresponds to a separate check for the VLM to execute.
* **Variable options**: the allowed answer choices for each variable.

When providing augmented media, it is simplest to use remote URIs such as `s3://...` when testing locally.

For CLI usage, the media path is provided by the legacy `--augmented-video-path` argument, and the expected attributes
come from the configuration file rather than CLI flags.

### Guidance on Constructing Inputs for Good Results

1. The default `frames: 1` behavior uses only the first video frame. Increase `frames` for attributes or events that may
   appear later; sampled frames are evenly distributed across the clip and sent together in chronological order.
2. Use a frame count supported by the VLM endpoint's image limits. For a static attribute, one clear frame is usually
   more efficient and just as accurate.
3. It is recommended to limit the selected variables to be a targeted list of 2-4 attributes. Using a large number of attributes may cause the checker to fail more often (since more checks are needed to pass), or may overload the VLM or LLM endpoints.
4. Variable options should be easy to distinguish from each other. For example, asking the checker to distinguish between `morning`, `noon`, `midday`, and `afternoon` for a `time of day` attribute will result in many inaccuracies, since it is hard to tell the difference between these times of day based on a video alone.

## Configuration

Configuration lives in `checks/cosmos_evaluator.yaml` under `metropolis.attribute_verification`.

This file acts as both the default configuration file for the CLI, as well as provides the default configuration values for the service container.

An explanation of each config value is below:
* **enabled**: Enables or disables the checker in shared configuration. Default: `true`.
* **selected_variables**: Mapping of attribute names to the expected value for the clip. Each entry produces one verification question. Default: `weather: sunny`, `time_of_day: morning`.
* **variable_options**: Mapping of attribute names to the full allowed option list that the LLM must use when building answer choices.
* **exclude_variables**: Attribute names to remove from both selected variables and option pools before generation.
* **extra_questions**: Optional fixed MCQs. Each entry contains `question`, an `options` mapping, `correct_answer`, and
  optional `variable`, `value`, and `request_reasoning` fields.
* **question_generation.generate_options**: Let the LLM invent distinct distractors instead of using
  `variable_options`; the configured selected value remains the ground-truth answer. Default: `false`.
* **question_generation.llm.endpoint**: OpenAI-compatible endpoint used for LLM question generation. Default: `https://integrate.api.nvidia.com/v1` (Use this endpoint when connecting to [build.nvidia.com](https://build.nvidia.com)).
* **question_generation.llm.model**: LLM model used to generate questions. Default: `qwen/qwen3-next-80b-a3b-instruct`.
* **question_generation.llm.api_key_env**: Optional environment-variable name containing this endpoint's API key.
* **question_generation.parameters.frequency_penalty**: Frequency penalty passed to the LLM request. Default: `0.0`.
* **question_generation.parameters.max_tokens**: Maximum number of output tokens for question generation. Default: `2048`.
* **question_generation.parameters.presence_penalty**: Presence penalty passed to the LLM request. Default: `0.0`.
* **question_generation.parameters.retry**: Number of retry attempts for retryable LLM failures. Default: `1`.
* **question_generation.parameters.stream**: Whether the fallback non-structured LLM request should stream tokens. Default: `true`.
* **question_generation.parameters.temperature**: Sampling temperature for question generation. Default: `0.2`.
* **question_generation.parameters.top_p**: Top-p sampling value for question generation. Default: `0.95`.
* **question_generation.system_prompt**: System prompt instructing the LLM to generate a simple JSON multiple-choice question answerable from a single frame.
* **vlm_verification.vlm.endpoint**: OpenAI-compatible endpoint used for VLM verification. Default: `https://integrate.api.nvidia.com/v1` (Use this endpoint when connecting to [build.nvidia.com](https://build.nvidia.com)).
* **vlm_verification.vlm.model**: VLM model used to answer the generated questions. Default: `qwen/qwen3.5-397b-a17b`.
* **vlm_verification.vlm.api_key_env**: Optional environment-variable name containing this endpoint's API key.
* **vlm_verification.frames**: Number of evenly spaced frames sent for a video. Images are sent directly. Default: `1`.
* **vlm_verification.parameters.frequency_penalty**: Frequency penalty passed to the VLM request. Default: `0.0`.
* **vlm_verification.parameters.max_tokens**: Maximum number of output tokens for the VLM answer. Default: `10`.
* **vlm_verification.parameters.retry**: Number of retry attempts for retryable VLM failures. Default: `1`.
* **vlm_verification.parameters.stream**: Whether the VLM response should stream. Default: `false`.
* **vlm_verification.parameters.temperature**: Sampling temperature for VLM answering. Default: `0.0`.
* **vlm_verification.parameters.top_p**: Top-p sampling value for VLM answering. Default: `1.0`.
* **vlm_verification.system_prompt**: System prompt instructing the VLM to answer with only a single option letter.

The service request also accepts an optional `verbose` value of `DEBUG`, `INFO`, `WARNING`, or `ERROR`.

For example, this override excludes a generated attribute, adds a fixed question with reasoning, and evaluates six
frames distributed across a video:

```yaml
exclude_variables:
  - time_of_day
extra_questions:
  - variable: safety_cones
    value: present
    question: Are safety cones visible anywhere in the scene?
    options:
      A: present
      B: absent
    correct_answer: A
    request_reasoning: true
question_generation:
  generate_options: true
vlm_verification:
  frames: 6
```

## Model Setup

The checker makes two model calls:

1. **An LLM call** to generate one multiple-choice question per configured variable.
2. **A VLM call per question** using the image directly or the configured number of sampled video frames.

The models and endpoints for both the VLM and the LLM are configured in `checks/cosmos_evaluator.yaml`. The recommended
credential setup keeps the two roles explicit in `checks/attribute_verification/.env`:

```dotenv
LLM_API_KEY=<key-for-question-generation>
VLM_API_KEY=<key-for-visual-verification>
```

The same credential may be assigned to both variables when both endpoints accept it. Credentials are resolved from the
endpoint's optional `api_key_env`, then the role-specific `LLM_API_KEY` or `VLM_API_KEY`. The legacy
`BUILD_NVIDIA_API_KEY` is retained only as a compatibility fallback. For a custom `api_key_env`, inject the named
variable into the checker process or container; never put the secret itself in YAML.

By default, the checked-in configuration uses:

* **LLM endpoint**: `https://integrate.api.nvidia.com/v1` ([build.nvidia.com](https://build.nvidia.com))
* **LLM model**: `qwen/qwen3-next-80b-a3b-instruct`
* **VLM endpoint**: `https://integrate.api.nvidia.com/v1` ([build.nvidia.com](https://build.nvidia.com))
* **VLM model**: `qwen/qwen3.5-397b-a17b`

See the [Setting up your LLM and VLM API key](../getting_started.md#setting-up-your-llm-and-vlm-api-key) for details on retrieving an API key for the [build.nvidia.com](https://build.nvidia.com) endpoints.

You can change these defaults in `checks/cosmos_evaluator.yaml`, or override them per request through the service `config` payload. Any endpoint that is compatible with the OpenAI API can be used in place of the default [build.nvidia.com](https://build.nvidia.com), including locally-deployed endpoints. The VLM and LLM models may also be replaced with other models, but please keep in mind that the checker performance may degrade if using models other than the provided defaults. The less powerful the model, the less accurate the checker will be.

## Local CLI Testing

### Run the Checker

> Note: Before running this command, ensure that you have already gone through the steps from the [Getting Started](../getting_started.md) and [Customization](../customization.md) guides. Both the environment setup and the build system setup must be complete before this command will work.

Before running the checker locally, ensure that the selected attributes match the ones you want to check for. Please update `checks/cosmos_evaluator.yaml` to configure these attributes.

From the `cosmos-evaluator` (repo root) directory, run this command:

```bash
dazel run //checks/attribute_verification:run -- \
  --augmented-video-path s3://<bucket_name>/path/to/augmented.mp4
```

The documented CLI supports these options:

- **--augmented-video-path** (required): URI to the augmented image or video being evaluated. The option name is
  retained for compatibility.
- **--clip-id** (optional): Clip identifier for the run. If omitted, the CLI generates a UUID automatically.
- **--config** (optional): Configuration file name to load, without the `.yaml` extension. Defaults to `cosmos_evaluator`.
- **--config-dir** (optional): Optional path to the directory containing the configuration file.
- **--verbose** (optional): Logging level for the run. Supported values are `DEBUG`, `INFO`, `WARNING`, and `ERROR`. Defaults to `INFO`.
- **--env-file** (optional): Path to the `.env` file to load before processing. Defaults to `checks/attribute_verification/.env`.
- **--output-dir** (optional): Directory where the JSON results file is written. Defaults to `outputs`.

### Interpret the Output

The checker produces:

* An **overall pass/fail** result, where `passed = true` only if every check passes.
* A **summary** with `total_checks`, `passed_checks`, `failed_checks`, and `errored_checks`. Incorrect model answers are
  failures; endpoint or media-processing errors and unparseable VLM verdicts (`vlm_answer == "UNKNOWN"`) are errors. If
  no valid question remains, the result fails with `reason: "no_questions"`.
* A console summary with the saved output path, overall result, and one line per checked variable.
* A JSON results file named `{clip_id}.attribute_verification.results.json` under `--output-dir`.

The JSON results will look like this:

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

Higher-quality runs show agreement between the configured expected attributes and the VLM's answers. Failed checks indicate that the model judged one or more expected attributes to be absent or mismatched.

## Building and Running the Service Container

The attribute verification service wraps `AttributeVerificationProcessor` behind a standardized REST API for containerized deployment.

The service exposes these endpoints:

- `GET /health` for health and version status
- `GET /config` to retrieve the default attribute verification configuration
- `POST /process` to process one clip and return per-check verification results

The `POST /process` request body includes:

* **clip_id** (required): This can be set to any arbitrary string, and is used to identify the input media in the results.
* **augmented_video_url** (required): Remote path (or local/mounted path) for the augmented image or video. The field
  name is retained for compatibility.
* **config** (optional): Dictionary with any config values which should be altered from the default value. Defaults to `{}`.
* **verbose** (optional): Logging level for the run. Supported values are `DEBUG`, `INFO`, `WARNING`, and `ERROR`. Defaults to `INFO`.

### Build and Run the Container

First, build the container:

```bash
dazel build //services/attribute_verification:image
```

Next, load the built container into the local docker instance:

```bash
dazel run //services/attribute_verification:image_load
```

Finally, run the loaded container:

```bash
docker run --env-file=checks/attribute_verification/.env -p 8080:8080 attribute-verification-checker:1.1.0
```
