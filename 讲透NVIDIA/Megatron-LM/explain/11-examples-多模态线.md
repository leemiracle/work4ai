# 11 Examples 多模态线：mimo 异构训练、NVLM 转换器、评测脚本族与 modelopt conf 体系

## 一、角色定位

`examples/` 是 Megatron-LM 的"活文档"。本篇四块：`examples/mimo/`（异构多模态 VLM/AVLM 参考实现，自带独立训练循环）、`examples/multimodal/`（LLaVA 系经典线：数据、模型、转换器、15 基准评测）、`examples/post_training/modelopt/`（ModelOpt 后训练家族，conf 按厂商组织）、`nvlm/` 子线（InternViT×各家 LLM 配方）。共同展示"核心库只给积木、编排全在 examples"的分层哲学。

## 二、内部结构

**mimo 异构多模态**：`pretrain_mimo.py` 入口（train.py/avlm_inference.py 配套）。`training/` 十文件（args/batch/builder/data/distributed/encoder_prefetch/grad_sync/runtime/step/topology）构成**自研训练循环**，不走 megatron/training 标准路径——异构并行（vision encoder 与 LLM 用不同 DP/TP 网格）要改的钩子太多，干脆整个循环自带。`model_providers/` 四 provider（llava_vlm/llava_avlm/mock/nemotron_moe_vlm）加三种编码器（hf_clip/hf_whisper/radio）；`nemotron_moe_vlm.py:57` 注册 provider 参数，:166-168 硬性要求 `calculate_per_token_loss=True`（"异构循环按真实 LM token 数缩放两类梯度"）。异构拓扑由 `utils/hetero.py:10` 的 `get_grid_dim_size(HyperCommGrid)` 反推；`builder.py:130-142` 提供 use_megatron_fsdp/use_torch_fsdp2 双开关接 08 篇 FSDP。冒烟入口 `run_hetero_nemotron_20l_mock_train.sh`：8 rank、20 层 Nemotron6-MoE VLM、hybrid-layer-pattern `"MEMEM*EMEMEM*EMEMEM*"`、128 专家 top-6。

**modelopt 后训练 conf 体系**：`conf/arguments.sh` 是汇聚锚——**arguments.sh:105 的 `source "${SCRIPT_DIR}/conf/${MLM_MODEL_CFG}.sh"`** 按环境变量动态加载模型 conf，SANDBOX_ROOT 存在时改从沙箱路径（:107）；train.sh:5 先 source 它再叠 `--modelopt-enabled --export-te-mcore-model` 通用参数。conf 家族按厂商目录：deepseek-ai（R1/V2-Lite）、meta-llama（3.1/3.2/Llama-4 双 MoE）、nvidia（Nemotron-H 47B/56B、Nano 9B、Nemotron-3 三档）、openai（gpt-oss-120b）、Qwen（6 个）、moonshotai。**moonshotai 大小写双名分工**是最易踩的坑：大写 `Kimi-K2-Instruct.sh` 承载完整 MODEL_ARGS 架构参数（61 层、hidden 7168、MLA kv-lora-rank 512/q-lora-rank 1536、384 专家 sigmoid router top-8、shared-expert overlap）；小写 `kimi_k2_instruct.sh` 是转换布局（HF→TP=8/ETP=1/EP=64）；`kimi_k2_instruct_export.sh` 是导出布局（PP=16，层分布 3,[4]×14,2，经 `--decoder-first/last-pipeline-num-layers` 表达）。同一模型三份 conf 三种角色，文件名即接口。

**NVLM/InternViT 转换器群**：`examples/multimodal/model_converter/` 五件套（clip 163 行/siglip 154/internvit 162/radio 314/vision_model_tester 125）。`internvit_converter.py:8` 的 `convert()` 是硬编码模板：hidden_size=3200/num_heads=25/dim=128 写死（:18-20），双循环构造 QKV interleaving 置换表（:24-26，把 HF 的 [q|k|v] 拼接序重排成 head-interleaved）后按 TP 切片写 mcore 格式——换 ViT 版本必须改常数。`examples/multimodal/nvlm/` 是配方目录：yi_34b/qwen20_72b×internvit_6b 的 pretrain/sft/生成脚本、qwen2p5_7b 视频/siglip 变体、pp_checkpoint_converter.py、nvlm_prompts.json。

**multimodal 评测脚本族**（`evaluation/`，18 文件 15 基准）：中枢两个复用源——`get_input_output_paths`（evaluate_mmmu.py:21）与 `compute_vqa_accuracy`（evaluate_vqav2.py:94）。前者做**分片合并**：单文件输出 `-merged.json`；目录模式构造 `EvaluationConfig(task, partition_id="*")` 交 run_text_generation 的 `get_output_path(dp_rank="*")` 生成通配 pattern 后 glob 全部分片（evaluate_mmmu.py:25-36），合并按 sample_id 去重（:69）——推理端按 (partition, dp_rank) 分片写出，评测端盲合并。`compute_vqa_accuracy` 内置**四种判分策略**：ChartQA 宽松精度（数值 ±5% 内记对，非数值精确匹配，:110-127）；VQAv2/TextVQA 的 `min(1.0, num_match/3)` 三标注者规则（:129-131）；SPDocVQA/InfoVQA 的 ANLS（阈值 0.5，:132-134）；AI2D/RealworldQA/MotionBench 单真值精确匹配（:135-138）。MMMU 特殊：官方仓库无 API，evaluate_mmmu.py:96-106 subprocess 调 `examples/multimodal/MMMU/mmmu/main_eval_only.py` 再正则抠 'Overall' acc。复用链：evaluate_ai2d.py:4、evaluate_infovqa.py:4、evaluate_textvqa.py:5、evaluate_video_motionbench.py:6 全从中枢 import。`evaluation_datasets.py`（1698 行）管基准注册与提示词。

## 三、外部连接

mimo 向下依赖 `megatron/core/hyper_comm_grid.py` 与 FSDP 子树；`examples/multimodal/model.py:194` 的 vision_model_type 分派（pixtral-vit/qwen-vl/kimi-vit 等）连着 10 篇 tokenizer 与 mimo 编码器。modelopt 线向下调 TensorRT-LLM ModelOpt（prune/eagle3/finetune/generation_server 各脚本），向上接蒸馏与量化导出。评测线依赖 `run_text_generation.py`+`config.py`（EvaluationConfig :499，partition_id :517）的输出约定；nvlm 的 pp_checkpoint_converter 与 09 篇总线共享思想但独立实现。

## 四、数据流

mimo 异构训练：energon dataloader → task encoder → vision encoder 与 LLM 各自并行网格前向 → grad_sync 跨网格聚合 → step 按 per-token loss 归一。multimodal 经典线：HF ViT checkpoint → model_converter（置换+TP 切片）→ mcore vision tower → combine_lm_vision_checkpoints.sh 与 LLM 权重合成 → pretrain/sft → run_text_generation 按 (partition, dp_rank) 分片产出 jsonl → 评测盲合并 → 四策略或 MMMU subprocess 判分。modelopt 流：设 `MLM_MODEL_CFG=moonshotai/Kimi-K2-Instruct` → arguments.sh:105 source 大写 conf 拿架构 → 训练/蒸馏 → 小写 conf 转布局 → export conf 定 PP 层分布 → TE-mcore 导出。

## 五、设计决策

1. **mimo 自带循环而非魔改标准循环**：异构并行钩子太多，复制 ~2000 行循环比在 megatron/training 加 if 分支便宜——examples 层承担"实验性"的代价。
2. **conf 按"文件名即 API"组织**：大小写区分角色（架构/转换/导出）虽易误读，但三份纯数据文件零代码可组合；动态 source 是唯一汇聚点。
3. **判分策略内置**：四策略写死在中枢函数，加基准 cost 是改一个 elif——评测口径集中一处。
4. **分片合并用通配约定**：推理端文件名带 partition/dp_rank，评测端 "*" glob 盲收——两端只共享命名约定，无中心账本。
5. **转换器硬编码超参**：internvit_converter 是"参考实现"与"通用工具"的边界示范——通用化请走 09 篇 schema 路线。

## 六、新人提示

- Kimi-K2 三份 conf 别拿错：训练/蒸馏用大写，转 TP/EP 布局用小写，导出 PP 布局用 _export；改架构不改转换 conf 会在加载时形状对不上。
- mimo nemotron provider 不开 `--calculate-per-token-loss` 直接 ValueError（nemotron_moe_vlm.py:168），这是异构梯度缩放硬前提。
- 跑评测前确认推理输出目录符合 partition/dp_rank 命名约定，否则 glob 空集、merged 文件为空 dict 而非报错。
- internvit_converter 只认 InternViT-6B（3200/25/128）；换版本先改 :18-20 三常数再跑 vision_model_tester.py 验证。
- ChartQA ±5% 判分含 rstrip("%")（evaluate_vqav2.py:117-118）："55%" 与 55 判等，但 "0.55" vs "55%" 走数值分支判错——排查精度异常先看这。
- mimo 无 README，文档性最强入口是 run_hetero_nemotron_20l_mock_train.sh 注释与 mock provider——从 mock 跑通再换真数据。
