# 03 train/ 训练线：torchrun 自研 SFT 与 LLaMA-Factory 双轨

## 角色定位

`train/` 有两条并行训练轨：**自研轨**是 `sft.sh`（torchrun 拉起）+ `sft.py`（trl.SFTTrainer + FSDP），自己控制模板拼接与 loss 掩码；**LLaMA-Factory 轨**是 9 行薄入口 `train.py` + 一族 YAML 超参，由 accelerate + DeepSpeed 启动。readme.md:164 明说分工：默认走自研轨，换更多模型族可"choose to use llamafactory...or modify the code in train/sft.py"。

## 内部结构

**`train.py` 是全仓最短可执行文件**：L1 导入 `run_exp`，`main()` 只有一行调用——超参全外置 YAML，经 `accelerate launch train/train.py train/training_args.yaml` 注入（readme.md:180）。

**`sft.py`（141 行）是自研轨核心**：`TrainingConfig` dataclass（L18-27）定模型名（默认 Llama-3.1-8B-Instruct）、block_size 32768、训练文件、留作 DAgger 的 dagger 开关（L27）。`train()` 流程：HfArgumentParser 合并 trl.SFTConfig（L36-37）；模型名含 "70B" 走 device_map=auto 分支（L43-52）；读 JSON 后**按模型族手工拼对话模板**（L66-76 四分支），拼接的是 `item['predict']`：直接消费蒸馏产物里的教师思维链。loss 掩码用 `DataCollatorForCompletionOnlyLM`（L116-121，Mistral 分支用 token 序列模板并切前两 token，L108-114）；各族 pad_token 都选永不被使用的 token（L96/101/105）。

**`sft.sh`（42 行）torchrun 链**：L16-17 `torchrun --nproc-per-node 8 train/sft.py`，micro_batch 1 × 梯度累积 8（L10-11），FSDP `"full_shard auto_wrap"` + `train/fsdp_config_llama.json`（L26-27），bf16 + cosine。

**fsdp 三胞胎**：`fsdp_config_{llama,qwen,mistral}.json` 各一行，分别为 `LlamaDecoderLayer`/`Qwen2DecoderLayer`/`MistralDecoderLayer`——换基模只改 `--fsdp_config` 指向。

**training_args 系列**：`training_args.yaml` 全参 SFT（pubmed、lr 1e-5、5 epoch），超参与 sft.sh 一一对应——同一实验的两套启动方式；`training_args_lora.yaml` PEFT 版（rank 64/alpha 128/loraplus 16，L13-17），配 `merge_lora.yaml` 合并 adapter；`training_args_mm.yaml` 多模态版（Qwen2.5-VL-7B + lr 5e-5）。

## 外部连接

自研轨依赖 trl/transformers/torch 纯栈；LLaMA-Factory 轨依赖 llamafactory 0.9.2 + `train/accelerate_config.yaml`（DeepSpeed ZeRO-3、优化器与参数双 CPU offload、8 进程 bf16，L3-17）。`data/dataset_info.json` 承上启下：YAML 的 `dataset: pubmed` 经注册表解析到 `train_pubmed.json`。

## 数据流

自研轨：蒸馏后的 `data/train_pubmed.json`（含 predict）→ sft.py 拼模板 → collator 只对 assistant 段算 loss → `saves/pubmed-llama`（sft.sh:37）→ 交给 vllm_infer_text.py 当模型路径。LLaMA-Factory 轨：YAML → run_exp → DeepSpeed checkpoint → 多模态线还要跑 `zero_to_fp32.py` 转换（demo:23）。

## 设计决策（含批判）

**双轨并存**是论文刚需：自研轨精确控制"只在教师推理段算 loss"，LLaMA-Factory 轨白得 LoRA/多模态/KTO 生态；代价是两份超参要人肉同步。**两处笔误**：`sft.sh:19` 的 `--train_file_path="data/train_pubmed"` 缺 `.json` 后缀，直接跑会在 sft.py:57 的 `open()` 处 FileNotFoundError——demo:26 同参数却带后缀，可见是后改丢的；`training_args_mm.yaml:19` 的 `output_dir: saves//mmrait-qwenvl` 双斜杠无害但不整洁。模板在 sft.py 与两个 vllm 脚本三处各写一份，又一隐形契约。

## 新人提示

1. 跑自研轨先看 sft.sh:19 后缀坑；正确姿势是照 demo 脚本抄命令，别直接 `bash train/sft.sh`。
2. LLaMA-Factory 轨报 "dataset not found" 查两处：dataset 名是否在 `data/dataset_info.json` 注册、文件是否已被 process/ 生成。
3. 多模态线的 `accelerate_config_mm.yaml` 不存在（见 06 篇），需自建或复用 `accelerate_config.yaml`。
4. sft.py 的 70B 分支（L43-52）用 device_map=auto 而非 FSDP，触发条件是模型名含 "70B"。
