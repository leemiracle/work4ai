# 讲透 NVIDIA/Spatial-IQ

NVIDIA 的 3D 空间智力基准（VLM 空间认知评测+训练闭环），论文 arXiv 2607.22864，图谱 commit `ed1c3a1d`。

## 产物状态

| 产物 | 状态 | 说明 |
|---|---|---|
| deepwiki/ | ✅ 31/31 页 TRUE_100 | 2026-10-26 MCP 通道抓取，全层级对账终判 |
| 图谱 | ✅ 768 节点 / 1365 边 / 8 层 / 9 步 tour | fingerprints 163 文件 @ `ed1c3a1d`，仓内 .understand-anything/knowledge-graph.json |
| onboarding/ONBOARDING.md | ✅ 8 节 | 本轮（2026-11-11）新增 |
| explain/ 3 篇 | ✅ | blocks_render_image 数据线 / NCQ 推理器 / prepare_data 训练线 |
| 勘误 | ✅ 7 条 | 见下，全部 file:line 实证 |

## 勘误（源码实证 vs 常见误解/文档与图谱说法）

1. **「claude/gemini/gpt/kimi 走各自厂商原生 API」——错。** 全部统一打一个 OpenAI 兼容端点（NVIDIA Inference API）：claude runner 注释明写 "Claude Opus 4.6 via Bedrock"（inference/claude/inference_text_claude.py:6），端点由 `INFERENCE_API_BASE` 环境变量注入（:23）；NCQ 注册表里这四家 backend 全是 `nvidia_api`（inference/inference_mcq_NCQ.py:13、:57/:63/:69/:75）。README.md:126-128 的"Set the endpoint via INFERENCE_API_BASE"是权威口径。
2. **「GLM 走智谱云端 API」——错（图谱 L03 描述把 glm 归入 API 组）。** GLM 是本地模型：runner 头注释 "locally hosted GLM (via vLLM OpenAI-compatible server)"（inference/glm/inference_text_glm.py:6），客户端 `OpenAI(base_url=..., api_key="EMPTY")`（:425），NCQ 里 backend=`vllm`、model_id=`glm-edge-v`（inference/inference_mcq_NCQ.py:94）；README.md:131/183 把它列在 Local models 并指向本地权重目录 `weights_glm-4.6v-flash/`，与源码一致。
3. **「NCQ 是统一推理器/选项随机重排器」——半错。** NCQ 实义是 **reduced-option MCQ**：把 5 选项砍成 3/4 选项、答案回映射回原始 A-E 空间（inference/inference_mcq_NCQ.py:6-10），只覆盖 MCQ 任务且注册表仅 7 个模型（:55-95），并非 26 个 runner 的公共底座；真正的公共底座是 inference/view_utils.py:57 的 `find_and_group_views`（26 个 runner 全员 import）。洗牌确实存在（:274）但服务于选项削减，非独立特性。
4. **「27 个 runner」——口径混淆。** 仓内 `inference_*.py` 实数 **26 个**文件（25 个厂商 runner + 1 个 NCQ）；"27"是 analyses/inference_results 的**机器模型配置数**（37 个 eval_raw CSV = 27 机器配置 + 2 人类基线 + 含 3CQ/4CQ 变体与 image 线拆分的多元记录）。
5. **「schema.py 用 6 个 dataclass」——类库搞错（图谱 L08 措辞）。** 是 6 个 **Pydantic BaseModel**（training/schema.py:39/:75/:96/:116/:142/:166），README.md:33 的 "Pydantic-validated dataset manifest" 才是正确口径。
6. **「DAPO-tight 有独立 YAML」——错。** training/configs/ 只有 4 个 YAML（sft/sft_main/grpo/grpo_main）；DAPO-tight 是 grpo_spatialiq_main.yaml 头部注释的配方说明（training/configs/grpo_spatialiq_main.yaml:2，"gemma-4-31B-it on GB200, DAPO-tight recipe"），标签亦打在 tags 里（:190）。
7. **「微调全在 Qwen 上」——不完整。** eval_raw 只有 Qwen 系 sft/dapo 结果，但 main 任务配方换 base 模型：training/configs/sft_spatialiq_main.yaml:15 与 training/configs/grpo_spatialiq_main.yaml:52 均为 `google/gemma-4-31B-it`；标准档才是 Qwen2.5-VL-7B（training/configs/grpo_spatialiq.yaml:51）。

## explain 索引

- explain/01-blocks-render-image.md——Isaac Sim 合成数据生产线（4825 行：back-to-front 掩码真值/资产三形态/异步 S3）
- explain/02-inference-mcq-ncq.md——削减选项 MCQ 推理器（双后端/确定性种子/答案回映射）
- explain/03-prepare-data.md——SFT/GRPO 训练数据组装（10 步 CoT 模板/答案掩码/样本组切分）
