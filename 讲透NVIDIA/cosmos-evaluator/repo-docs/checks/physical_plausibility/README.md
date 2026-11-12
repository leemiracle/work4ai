# Physical Plausibility Check

This check evaluates motion in a generated video using a frozen V-JEPA 2.1 encoder, learned attention pooling, and a
linear classifier. It returns a plausibility score and a pass/fail result without a reference video or annotations.

## Intended use and limitations

The Physical Plausibility Evaluator helps screen generated videos for visual artifacts and implausible behavior. It
supports automated filtering, but does not guarantee that an accepted video is physically correct or free of artifacts.

**Pretrained model and training domain.** The provided checkpoint was trained on human-labeled videos generated with
Cosmos using seed images and descriptions from FineVideo. Training labels distinguish videos with major artifacts or
nonphysical behavior from videos judged good or usable with minor artifacts. Consequently, an accepted video may still
contain minor defects.

**Accuracy and generalization.** The checker can miss problematic videos and reject acceptable ones. Performance may
vary across environments, camera viewpoints, video-generation models, and quality criteria. Small or brief defects can
be difficult to detect. Performance measured on the training domain should not be assumed to apply to a new dataset.

**Using the checker on your data.** Before using its decisions for filtering, evaluate the checkpoint on a
representative labeled sample of your videos. Calibrate the decision threshold to your requirements: catching more
problematic videos generally increases the number of acceptable videos rejected. The supplied threshold reflects the
original calibration data and may need adjustment for your application.

If performance remains insufficient after calibration, finetune the checker or train a new classification head using
your own labels. V-JEPA remains pretrained and frozen during these workflows. Use the existing [training and calibration
tutorial](../../docs/tutorials/train_physical_plausibility_checker.ipynb) for instructions.

The checker's score indicates the model's preference for the bad-video class; it should not be interpreted as a
calibrated probability of a physical error.

## Architecture

Core modules:

- **`processor.py`**: Loads the classifier bundle and computes scores and pass/fail results.
- **`model.py`**: Loads the pinned video encoder and samples 64 distinct frames per video.
- **`features.py`**: Preprocesses frames with aspect-preserving 384 × 384 letterboxing.
- **`attention.py`**: Implements attention pooling, checkpoint validation, and saved thresholds.
- **`run.py`**: CLI entry point for config loading, execution, and result serialization.

## Usage

See the [Physical Plausibility Check guide](../../docs/checks/physical_plausibility.md) for prerequisites, model setup,
configuration, CLI usage, and result interpretation.

The default configuration requires an NVIDIA GPU and uses the pretrained classifier from the public Hugging Face
[physical-plausibility-evaluator repository](https://huggingface.co/nvidia/physical-plausibility-evaluator). The default
classifier does not require `HF_TOKEN`. Alternatively, supply a compatible local or remote bundle with
`--checkpoint-uri` or the YAML `checkpoint_uri` setting.

```bash
dazel run //checks/physical_plausibility:run -- \
  --video-path /absolute/path/to/video.mp4 \
  --checkpoint-uri /models/checker.pt \
  --output-dir outputs
```

The video must contain at least 64 frames. Higher `plausibility_score` values indicate more plausible motion; lower
`bad_score` values indicate more plausible motion. Scores reflect training labels and are not guaranteed calibrated
probabilities.

## Training and Calibration

The [training notebook](../../docs/tutorials/train_physical_plausibility_checker.ipynb) covers dataset preparation,
scratch training, pretrained fine-tuning, threshold-only calibration, and held-out evaluation. Scratch training does not
require a pretrained classifier. Fine-tuning updates the attention query and classifier while preserving source
normalization; the encoder remains frozen.
