# 11 · SFT 与蒸馏训练配方群：TOML 三档 × launch 脚本 × cosmos-framework 外部边界

## ① 角色定位

cookbooks 的训练面分布在三个 finetune/distill 目录，同一范式：**launch shell（本地准备+torchrun）+ 结构化 TOML（运行级旋钮）+ 注册在 cosmos-framework 的 experiment（配方语义）**。训练实现零本地代码（除蒸馏的 config 生成器）——README:60-66 明说"SFT here is a multi-GPU torchrun job, so these cookbooks ship as launch scripts + this README rather than a one-click notebook"。三组：**reasoner/finetune/**（VLM 对话 SFT：LLaVA-OneVision + VideoPhy-2 三档）、**generator/action/finetune/**（DROID/LIBERO/RoboCasa 策略）、**generator/audiovisual/**（vision SFT 三档 + DMD2 蒸馏）。分档：nano=Qwen3-VL-8B 系，super=Qwen3-VL-32B 全量微调，edge=2B Nemotron-2B-Dense-VL（SigLIP2 塔冻结）。硬件基线 8×H100 80GB（Edge 4 卡也放得下）。

## ② 内部结构

**launch 脚本三段式**（`launch_sft_videophy2_super.sh`，40 行）：①准备段全幂等——数据集在即跳（:24-26）、checkpoint 在即跳（:30-32 合并 Super LM 到 Qwen3-VL-32B 视觉塔）；②注入 `VIDEOPHYSICS_ROOT`（:36）与 `PYTORCH_ALLOC_CONF=expandable_segments:True`（:18，32B 防溢出）；③`torchrun -m cosmos_framework.scripts.train --sft-toml=... -- model.config...safetensors_path=...`（:38-40，`--` 后是 hydra 覆写）。**一条反直觉注释**（:16-17）：故意不清 LD_LIBRARY_PATH——torchcodec 解码要沿它 dlopen CUDA NPP+FFmpeg（对比推理线清理它）。

**videophy2_sft_super.toml**（104 行）字段分层：`[job]` :25-31；`[model]` :33-35 `attn_implementation="cosmos"`+bf16；`[model.parallelism]` :45-49 `data_parallel_shard_degree=-1`（FSDP 全分片自动）；`[optimizer]` :61-66 lr 1e-6；`[scheduler]` :71-77 cosine cycle 50；`[trainer]` :79-83 FSDP+grad_accum 8+max_iter 50；`[checkpoint]` :93-96 `load_path="???"`（hydra 必填占位）；`[dataloader_train]` :98-103 注释明示 PATH_REMAPS 路由。edge 档差异：`attn_implementation="flash_attention_2"`（:37），:35-36 注释给两个事实——`cosmos` 适配器 Qwen3-VL 专用会拒绝 Edge 掩码；**flash_attention_2 比 sdpa 快约 14% 且 loss 曲线一致**，sdpa 是无 flash-attn 的可移植回退。

**action finetune**——DROID 参考形状（README:16）：HSDP 32×8=256 ranks（GB200 64 节点×4）、全局 batch 8192、lr 2e-4、`loss_scale=10`、10000 iters；TOML 头注（:4-10）钉死分工哲学："this file pins the run-level scalars... remaining recipe knobs live in the registered experiment"。单 8 卡冒烟用 `EXTRA_TAIL_OVERRIDES` 压 max_iter/replicate_degree（README:102-116），正确缩放法：**保持全局 batch 用 grad_accum_iter=32 补**而非缩 batch。RoboCasa 是**首个带移动底盘**的 embodiment（15D 契约，`base_encoding="raw"` 直传）。**`vision_sft_super.toml` 是 LoRA 范本**：:19-22 `lora_enabled/rank 16/alpha 32/targets="q_proj_moe_gen,..."`（MoT 生成路径四投影）；:53 `keys_to_select=["lora_"]`；:82 `keys_to_skip_loading` 含 `"lora_"` 让适配器新初始化。README 警告：FFN 目标必须写全限定 `mlp_moe_gen.up_proj`，裸 `up_proj` 会把理解塔一起适配。

**distill/**——DMD2 短程冒烟（README:7-11 明示"functional recipe, not production reproduction"，6 个迭代验证加载/损失/断点续训/学生导出/推理全链）。`launch_distillation_t2i.sh` 仅 17 行定义 5 个变量后 source `common.sh`（228 行：钉 BridgeData2 revision :10、拓扑硬校验 :52-53、`wait_for_file` 跨节点等共享文件）；**真正组配置的是 `build_distillation_config.py`**（454 行，pydantic `extra="forbid"`），从 framework 公开 API import 30+ 符号组装 DMD2RFModel/DistillationTrainer——TOML 只存配方旋钮（t2i：`t_list` :38 即四步、双优化器 lr 2e-6/4e-7 :41/:45、`num_video_frames=1` :61）。

## ③ 外部连接

- **cosmos-framework 是单一边界**：训练全走 `cosmos_framework.scripts.train`；experiment 注册、数据准备/转换、导出（`export_model`→HF safetensors）全在上游仓。TOML 注释里的字段迁移备注（"was [model.parallelism].precision"）说明本仓配置跟踪上游 schema 演进。
- **上游文档**：reasoner finetune README:62-64 链 cosmos-framework 的 training.md/sft_config.md 等——GitHub 上游仓 docs，非本仓路径（见⑥坑 2）。
- **HF 资产**：数据侧 videophy2_train/Cosmos3-DROID/LIBERO_LeRobot_v3/BridgeData2-Subset（revision 钉死）/RoboCasa；模型侧 Cosmos3 系+Wan2.2 VAE+蒸馏 teacher。
- **推理线回环**：训练产物经 `export_model` 直接进推理 cookbook（README:56；action 线同构，finetune README:293）。

## ④ 数据流

典型 SFT 全流：launch 探测式准备（数据集→VAE→DCP 转换，产物在即跳）→ torchrun 拉起 N 份 train 脚本 → 每 rank 读同一 TOML（按 experiment 名找回注册配方）→ hydra `--` 覆写注入本地路径 → FSDP/HSDP 训练 → `outputs/train/<...>/checkpoints/iter_<N>/`（DCP）→ `export_model` 转 HF safetensors → 推理 cookbook 消费。蒸馏线多一跳：`common.sh` 先跑 `build_distillation_config.py` 织完整 config，每节点各执行同一 launcher、由 NODE_RANK/MASTER_ADDR 组网（无 Slurm/K8s 层）。

## ⑤ 设计决策

1. **TOML 只钉"run-level scalars"**，配方语义留注册 experiment——换数据/规模只改 TOML 小节；代价是查某旋钮要去上游仓。
2. **档位梯度复用数据流**：videophy2 三档 TOML 共享 dataset+dataflow，只动 backbone/并行度/注意力实现。
3. **幂等准备**：下载/转换以产物存在性为闸，重跑零浪费。
4. **蒸馏用 Python 生成配置而非纯 TOML**：DMD2 需要 lazy config/回调编排/双优化器的命令式结构，pydantic `extra="forbid"` 保证拼错键立刻炸。
5. **诚实标注配方等级**：distill README 显式声明"不承诺生产质量样本、不复现 NVIDIA 训练结果"；DROID/LIBERO 相反钉参考形状声称可复现。

## ⑥ 新人提示（坑与勘误）

1. **TOML dotted key 陷阱（本仓源码级钉版）**：videophy2_sft_super.toml:67-69 注释——toml→hydra 覆写把 dict key 里的"."解析为嵌套，`model.visual` 这类**键名本身含点**的配置（如 per-part LR 倍率）TOML 表达不了，注释原话"Edit the experiment"——必须去上游 experiment Python 改；`--` 后覆写同受此约束。
2. **`docs/action_policy_libero_sft.md` 是断链**：action_policy_libero_10_nano.toml:7 与 action_policy_libero_all_nano.toml:10 写"See docs/..."，但全仓无此文件、本仓 docs/ 只有 reference/models.md——应指 cosmos-framework 上游文档；action README 其它 docs 引用均以完整 GitHub URL 出现，唯这两处是局部相对路径。
3. **`load_path="???"` 不是可留空默认值**：是 hydra 必填占位（:95），不通过 launch `--` 传入本地 checkpoint 路径，config 解析直接失败。
4. **Edge 档别抄 nano 的 `attn_implementation="cosmos"`**：cosmos 适配器 Qwen3-VL-only，Edge 掩码会被拒（edge TOML:34-37）；装了 flash-attn 用 flash_attention_2（快 ~14%），没装回落 sdpa。
5. **LoRA 四处联改缺一不可**：`lora_enabled/rank/alpha/targets`+`keys_to_select`+`keys_to_skip_loading`+关 EMA/compile；只开 lora_enabled 会全参训练。
6. **蒸馏 4 节点配置要三处联动**：NNODES=4、改 common.sh:52 拓扑校验、TOML `data_parallel_shard_degree=32→16`——README 强调"coordinated changes"，故意不发 4 节点 TOML。
7. **训练线别清 LD_LIBRARY_PATH**：与推理/评测线相反（super launch:16-17），torchcodec 解码依赖它找 NPP/FFmpeg。
