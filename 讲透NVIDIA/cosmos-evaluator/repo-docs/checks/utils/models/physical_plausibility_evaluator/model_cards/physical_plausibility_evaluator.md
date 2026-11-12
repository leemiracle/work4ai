# physical_plausibility_evaluator

## Model Overview

### Description or Model Summary:

`physical_plausibility_evaluator` scores video acceptability using a frozen video encoder and a trained binary
classifier. It supports synthetic-video quality screening without a reference video. Users can train or adapt the
classifier and calibrate its decision threshold for their own definition of acceptable video. The pretrained classifier
uses human quality labels for Cosmos-generated FineVideo samples. See the [checker guide][guide] for setup.

This model is ready for commercial or non-commercial use.

### License/Terms of Use:

[OpenMDW-1.1][openmdw] <br>

The pinned V-JEPA source is primarily [MIT-licensed][upstream-license], with [Apache-2.0 exceptions][upstream-terms].
Upstream components retain their own terms; this license does not relicense the frozen backbone. <br>

V-JEPA 2.1 weights will not be bundled or redistributed with this release. Users obtain the pinned backbone separately
from Meta through the [setup instructions][guide]. The trained bundle is currently in the private [Hugging Face
repository][weights]; it contains the classifier, normalization, calibration thresholds and provenance. <br>

### Deployment Geography:

Global. <br>

### Use Case: <br>

Developers and researchers assessing and filtering individual videos using task-specific acceptability criteria.
The model produces scores and decisions, not generated media. A passing decision does not certify physical correctness
or suitability for safety-critical use. <br>

### Release Date: <br>

Build.Nvidia.com: Not Applicable. <br>
GitHub: Planned 10/20/2026 via [Cosmos Evaluator][release-repository]. <br>
Hugging Face: Planned 10/20/2026 via [nvidia/physical-plausibility-evaluator][weights]. <br>
NGC: Not Applicable. <br>
Other: Not Applicable. <br>

The planned release is part of Cosmos Data Factory. The Hugging Face repository is currently private. <br>

## References(s):

- [V-JEPA source repository][vjepa], [pinned source license][upstream-license] and [license exceptions][upstream-terms].
  Users obtain the frozen backbone separately under its upstream terms. <br>
- [FineVideo source dataset at the recorded revision][finevideo]. <br>
- [Checker guide][guide] and [training/adaptation notebook][notebook]. <br>

## Model Architecture:

**Architecture Type:** Transformer encoder with learned attention pooling and a binary linear classifier.

**Network Architecture:** Frozen V-JEPA 2.1 ViT-L/16 encoder (`vjepa2_1_vitl_dist_vitG_384.pt`), feature normalization,
learned attention pooling and a linear binary classifier. A sigmoid provides the bad-class score; a calibrated threshold
determines the decision.

**This model was developed based on:** Meta V-JEPA 2.1; encoder weights remain frozen.

**Number of model parameters:** Approximately **3.0 × 10^8** frozen encoder parameters and **2,049** trainable
parameters in the attention query and linear classifier.

The query pools normalized space-time tokens into a 1,024-dimensional vector; the linear head produces one bad logit.
Feature mean and scale are fitted on training data and then held fixed. Padding-coverage weights enter attention as a
multiplicative prior; fully padded tokens are excluded. Source revision and checkpoint hashes are [pinned][encoder].

## Input(s): <br>

**Input Type(s):** Video. <br>

**Input Format(s):** <br>

- Video: .mp4 (H.264/AVC), decoded to RGB frames by FFmpeg. Other containers/codecs depend on the decoder. <br>

**Input Parameters:**

- Video: Three-Dimensional (3D): time, height and width, with three RGB channels. <br>

**Other Properties Related to Input:** Sample 64 distinct frames uniformly across the video, including both endpoints;
reject videos with fewer than 64 decodable frames. Resize with preserved aspect ratio, pad to 384 × 384 pixels, and
normalize using ImageNet channel statistics. Audio and alpha channels are not used; no reference video is required.
Decoded frames use 8-bit RGB. The normalized encoder input is `[batch, 3, 64, 384, 384]`; encoder tokens are
`[batch, 32, 24, 24, 1024]` before padding removal.
<br>

## Output(s)

**Output Type(s):** Numerical scores and a categorical good/bad decision. <br>

**Output Format(s):** <br>

- Numerical scores and decision: JSON from the CLI and service. <br>

**Output Parameters:**

- Numerical scores: Scalar (0D), one value per score per video. <br>
- Decision: One good/bad label per video. <br>

**Other Properties Related to Output:**

- `bad_logit`: Raw classifier output; larger values indicate stronger evidence for the bad class. <br>
- `bad_score = sigmoid(bad_logit)` and `plausibility_score = 1 - bad_score`: Scores in `[0, 1]`, not guaranteed
  calibrated probabilities. `prediction` and `passed` record the thresholded decision. <br>
- The default `cap: 0.3` selects the saved logit threshold calibrated to a validation good-rejection cap of 30%. It is
  not a score cutoff of 0.3, a maximum-accuracy setting, or a guarantee on new data. At or above the cutoff, the video
  is rejected. Explicit score-threshold overrides are supported; see the [checker guide][guide]. <br>
- No spatial or temporal defect-localization output is provided. <br>

Our AI models are designed and/or optimized to run on NVIDIA GPU-accelerated systems. <br>
Encoder and classifier execution use PyTorch/CUDA. Decoding and resizing use CPU. <br>

## Software Integration:

**Runtime Engine(s):** PyTorch; the integration pins PyTorch 2.10.0 with CUDA 12.8. FFmpeg decodes video.

**Supported Hardware Microarchitecture Compatibility:** NVIDIA Hopper H100, the tested configuration. Other GPU
architectures are not certified by this card.

**Supported Operating System(s):** Linux.

The model can be integrated through the CLI or REST API. Its `.pt` bundle is loaded with `weights_only=True` and
schema/feature-contract validation. These integrity checks do not establish robustness or privacy. See the
[checker guide][guide] for setup and deployment.

Integration requires additional testing with use-case-specific data. Following the V-model methodology, iterative unit
and system validation should assess functional requirements, misuse and safety risks before deployment.

## Model Version(s):

`finevideo-attention-linear-v1`: FineVideo-trained attention query and linear classifier, with normalization and
calibration thresholds. The [checker guide][guide] records the immutable revision, file and checksum. The model-card
name remains `physical_plausibility_evaluator`; this identifier names the existing checkpoint artifact.

No ongoing model retraining or maintenance is planned.

## Training, Testing, and Evaluation Datasets:

The dataset will not be released; the held-out FineVideo benchmark results may be shared. The following describes the
classifier dataset; the encoder was pretrained separately by Meta.

## Training Dataset:

### Data Modality:

Video, with human binary quality labels. Source images and captions condition video generation; the classifier does not
train on caption text or audio.

### Training Data Size:

**Video Training Data Size:** Less than 10,000 hours: 2,991 training videos, approximately 7.7 hours.

**Data Collection Method by dataset:** Synthetic videos generated from FineVideo frame/caption conditioning.

**Labeling Method by dataset:** Manually labeled; three quality levels mapped to binary acceptable/unacceptable labels.

**Properties:**

The dataset was generated with Cosmos 3 image-to-video, around mid-July 2026.
Preparation selected 5,000 unique sources from [FineVideo][finevideo] at revision
`84c74091e1c6ee7a5dffabfafb5c9033e4718883`, stratified by content category and dynamism. Selection applied landscape
resolution, age-restriction, visual-caption, temporal-coverage, audiovisual-correlation and limited text filters.
The second decoded frame of a timestamp-selected source clip was resized to 1280 by 720 pixels and paired with its
FineVideo activity description, with whitespace normalization only. Frame/caption alignment was not verified across
the full dataset.

One video was generated per source: 1280 by 720 pixels, 93 frames at 10 FPS (9.3 seconds).
Human annotators assigned three quality levels: major artifacts/nonphysical behavior; usable with minor artifacts and a
correctly described main event; or no artifacts. Annotation QC excluded 13 of 5,000 outputs, leaving 4,987 videos.
The classifier maps quality level 1 to bad (`0`, 3,491 videos) and levels 2–3 to good (`1`, 1,496 videos).

The selected classifier uses Adam with learning rate `0.003` and explicit L2 coefficients `0.001` for both query and
classifier weights. Training uses class-balanced binary cross-entropy; gradients update only the query and classifier.
User adaptation options are scratch training, warm-start fine-tuning with fixed source normalization, or threshold-only
calibration. The [training notebook][notebook] documents these distinct workflows.

The retained inventory totals approximately 12.9 hours. Source preparation, generation, annotation and split provenance
are documented internally. The dataset and detailed generation settings are not publicly released.
No personal data was used in the selected FineVideo source frames/captions, generated videos or annotations. This
statement concerns the classifier dataset, not Meta's encoder pretraining; see the [privacy subcard][privacy].

### Testing Dataset:

**Data Collection Method by dataset:** Synthetic; same generation process as training.

**Labeling Method by dataset:** Manually labeled; same quality-to-binary mapping as training.

**Properties:** 998 held-out test videos from the same 4,987-video inventory. The quality-stratified 60/20/20
train/validation/test split uses seed `20260915` and separates identical-video groups, but does not establish
scene-disjointness. Test videos do not fit normalization, classifier parameters or thresholds.

### Evaluation Dataset:

**Benchmark Score:** On 998 held-out Cosmos-generated FineVideo test videos (698 bad, 300 good), the pretrained
classifier achieves bad-class ROC AUC **0.8258**. At the default validation good-rejection cap of **30%**, bad recall
is **80.52%** (562/698) and actual good-video rejection is **31.33%** (94/300). These results use the saved
validation-calibrated logit threshold **0.5438173**; test labels did not select the threshold.

**Data Collection Method by dataset:** Synthetic; same generation process as training.

**Labeling Method by dataset:** Manually labeled; same quality-to-binary mapping as training.

**Properties:** 998 validation videos select the classifier configuration/checkpoint by ROC AUC and calibrate
thresholds.
Final benchmark evaluation uses the separate 998 test videos described above. Metrics are bad-class ROC AUC, bad recall
and good-video rejection; a validation rejection cap is not a guarantee on test data.

## Inference:

**Acceleration Engine:** PyTorch with CUDA. This release does not provide a TensorRT or TensorRT-LLM engine.

**Test Hardware Set-Up:** NVIDIA Hopper H100.

Encoder inference uses BF16 autocast with FP32 weights; cached tokens use FP16. Feature normalization, attention pooling
and classification use FP32. GPU memory requirements depend on batch size and retained tokens.

## Ethical Considerations:

NVIDIA believes Trustworthy AI is a shared responsibility and has established policies and practices for a wide array
of AI applications. Developers should work with their model team to ensure the model meets relevant industry and
use-case requirements and addresses unforeseen misuse.

Ensure you have proper rights and permissions for all input video content, including content involving people, personal
health information or intellectual property. This classifier produces scores and decisions; it does not generate or
anonymize media.

Users are responsible for model inputs and outputs and for safe integration, including appropriate review and safety
mechanisms before deployment. A passing score does not certify physical correctness and must not be the sole basis for
safety-critical decisions. See the [bias][bias], [explainability][explainability], [privacy][privacy] and
[safety/security][safety] subcards for limitations.

Please report model quality, risk, security vulnerabilities or NVIDIA AI Concerns
[here](https://www.nvidia.com/en-us/support/submit-security-vulnerability/).

[openmdw]: https://openmdw.ai/license/1-1/
[weights]: https://huggingface.co/nvidia/physical-plausibility-evaluator
[guide]: ../../../../../docs/checks/physical_plausibility.md
[notebook]: ../../../../../docs/tutorials/train_physical_plausibility_checker.ipynb
[encoder]: ../../../../physical_plausibility/model.py
[vjepa]: https://github.com/facebookresearch/vjepa2
[upstream-license]: https://github.com/facebookresearch/vjepa2/blob/204698b45b3712590f06245fbfba32d3be539812/LICENSE
[upstream-terms]: https://github.com/facebookresearch/vjepa2/blob/204698b45b3712590f06245fbfba32d3be539812/README.md#license
[bias]: physical_plausibility_evaluator_subcards/bias.md
[explainability]: physical_plausibility_evaluator_subcards/explainability.md
[privacy]: physical_plausibility_evaluator_subcards/privacy.md
[safety]: physical_plausibility_evaluator_subcards/safety_security.md
[release-repository]: https://github.com/nvidia-cosmos/cosmos-evaluator

[finevideo]: https://huggingface.co/datasets/HuggingFaceFV/finevideo/tree/84c74091e1c6ee7a5dffabfafb5c9033e4718883
