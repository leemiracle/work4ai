# STTS: Unified Spatio-Temporal Token Scoring for Efficient Video VLMs

[**arXiv**](https://arxiv.org/abs/2603.18004) | [Molmo2-4B-Lite-30%](https://storage.googleapis.com/oe-training-public/Molmo2-STTS/Molmo2-4B-Lite-0.3.tar) | [Molmo2-4B-Lite-50%](https://storage.googleapis.com/oe-training-public/Molmo2-STTS/Molmo2-4B-Lite-0.5.tar)

Welcome to the official repository for the paper: **Unified Spatio-Temporal Token Scoring for Efficient Video VLMs**. 

This guide will help you understand and implement STTS. While our implementation is built on top of [Molmo2](https://github.com/allenai/molmo2), the STTS mechanism is highly portable to any Vision-Language Model (VLM) architecture. We highly encourage you to adapt this code to fit your own custom codebase!


## Setup

Our codebase relies entirely on the Molmo2 environment. To get started:

1. Visit the official [Molmo2 repository](https://github.com/allenai/molmo2).
2. Follow their provided setup instructions to configure your environment.

> **Note:** STTS does not require any additional dependencies or packages beyond what is needed for Molmo2.


## Training

The core STTS algorithm is implemented within `olmo/nn/temporal_image_vit.py`. Other files included, such as `olmo/nn/temporal_vision_backbone.py` and `olmo/models/temporal_video_olmo`, are required for the handling the token pruning and packing procedure as the token reduction propagates from the ViT to the LLM.

### Example: Single-Node Training (8 GPUs)

Below is a sample bash command to train STTS on a single node with 8 GPUs. To enable multi-node training, please refer back to the Molmo2 repository documentation.

```bash
torchrun --nproc-per-node 8 \
    launch_scripts/train_image_video_sft.py /path/to/pretrained/model all-v5-video-academic-only \
    --wandb.allow_resume=False \
    --global_batch_size 64 \
    --device_batch_size=2 \
    --max_duration=6250 \
    --seq_len 9686 \
    --packing \
    --model.mm_preprocessor.max_frames=64 \
    --model.mm_preprocessor.max_subtitle_tokens=null \
    --model.mm_preprocessor.use_frame_special_tokens=True \
    --model.vision_backbone.vit.sdpa_backend=efficient \
    --model.vision_backbone.compile_vit=null \
    --model.vision_backbone.compile_connector=null \
    --data.num_workers=4 \
    --save_folder=/path/to/save/folder \
    --use_temporal_video_olmo \
    --model.mm_preprocessor.topk=0.5 \
    --model.vision_backbone.vit.topk=0.5 \
    --model.vision_backbone.vit.prune_at=3 \
    --model.vision_backbone.vit.prune_method=scorer
```

### Key STTS Parameters

The following arguments are specific to configuring STTS as described in our paper:

* **`/path/to/pretrained/model`**: We fine-tune all STTS variants using [this](https://storage.googleapis.com/oe-training-public/Molmo2-STTS/Molmo2-4B-Lite-Pretrain.tar) checkpoint. Even though this checkpoint is pretrained with Qwen3-4B instead of Qwen3-4B-Instruct (what Molmo2 uses), it provides minimal performance difference (as demonstrated by our paper).
* **`all-v5-video-academic-only`**: The data mixture we use, representing the video-QA subset of Molmo2-Data. Ensure you have downloaded the required data following the Molmo2 guidelines.
* **`--use_temporal_video_olmo`**: A mandatory flag required to enable the STTS architecture.
* **`--model.mm_preprocessor.topk=0.5`**: Defines the $k$% pruning ratio conducted by STTS (e.g., `0.5` removes 50% of all vision tokens from the input). *Note: Our code currently only supports 3x3 pooling.*
* **`--model.vision_backbone.vit.topk=0.5`**: Must match the `mm_preprocessor.topk` value above.
* **`--model.vision_backbone.vit.prune_at=3`**: Designates the layer to inject the STTS scorer after (referred to as $l$ in the paper).
* **`--model.vision_backbone.vit.prune_method=scorer`**: Determines the pruning method. Supported options include:
* `scorer`: STTS pruning (our method).
* `easy`: Heuristic-based neighbor-frame cosine similarity sort and prune.
* `random`: Random token pruning.

For other customizable parameters, please review the `TemporalVitConfig` class inside `olmo/nn/temporal_image_vit.py`.

## Evaluation

To evaluate the model, you can run the following sample command:

```bash
torchrun --nproc-per-node 8 launch_scripts/eval_molmo2.py /path/to/save/folder \
    --device_batch_size=2 \
    --mode=video
```

The evaluation process operates largely the same as Molmo2. You can specify different evaluation subsets using the `--mode` flag (e.g., `--mode=video` for video-QA only, `--mode=video_pointing` for pointing tasks, etc.).


## Citation

If you find this work useful in your research, please consider citing our paper:

```bibtex
@misc{zhang2026stts,
      title={Unified Spatio-Temporal Token Scoring for Efficient Video VLMs}, 
      author={Jianrui Zhang and Yue Yang and Rohun Tripathi and Winson Han and Ranjay Krishna and Christopher Clark and Yong Jae Lee and Sangho Lee},
      year={2026},
      eprint={2603.18004},
      archivePrefix={arXiv},
      primaryClass={cs.CV}
}
```
