# Spatial-IQ Onboarding（新人入门指南）

> 图谱基线：768 节点 / 1365 边 / 8 层 / 9 步 tour，fingerprints 163 文件 @ git `ed1c3a1d`。
> 论文：arXiv 2607.22864（NeurIPS 2026 投稿系，README.md:21；`main` 分支复现 camera-ready，投稿版钉在 `neurips26-submission` tag，README.md:303）。

## 1. 项目定位与解决的问题

Spatial-IQ 是 NVIDIA 开源的 **3D 空间智力基准**：用程序化生成的积木场景（blocks world）系统测 VLM 的空间认知——计数、可见性推理、遮挡推断、跨视角比较。三条任务线贯穿全仓（README.md:15）：

- **text（自由问答）**：给单/双视角图，要求输出整数计数答案；
- **mcq（多选）**：给参考图+选项图组，选字母，含 5 选项原生与削减到 3/4 选项的变体；
- **image（图像生成）**：要求模型把答案（物体总数）画进图里，再用 OCR 评分。

仓库是一条完整闭环：**Isaac Sim 合成数据生产线 → 26 个推理 runner → 自动评测 → 论文统计分析 → SFT/RLVR 训练与训练后评测**。注意它不是打包库而是"文档站+脚本集合"——`pyproject.toml` 只服务 Sphinx 文档构建（`.github/workflows/pages.yml:29` 用 `uv sync --frozen` + `uv run sphinx-build`），训练 runner 本体是外部 NeMo-RL 仓（README.md:33）。数据集已发布在 HuggingFace `patrickqrim/spatial-iq`（README.md:21）。

## 2. 总体架构与分层

图谱 8 层对应数据流的五个阶段：

| 层 | 内容 | 代表位置 |
|---|---|---|
| L01 项目根与文档站 | README/docs/uv/Sphinx/Pages 流水线 | README.md:30 目录总表 |
| L02 Isaac Sim 生产线 | 渲染+真值+上传 | data_generation/blocks_render_image.py:574 |
| L03 推理 runner（38 文件） | 10 个厂商/模型目录 + 共享设施 | inference/view_utils.py:57 |
| L04 自动评测与人类基线（13 文件） | text/mcq/image/OCR/human | evaluation/run_evaluation.py:246 |
| L05-L06 论文统计与图表产物 | 2878 行主分析+manifest+40+ 表 | analyses/spatial-IQ_analyses.py:2863 |
| L07 逐题原始数据（38 CSV） | 27 机器模型配置+人类基线的原始作答 | README.md:285 |
| L08 训练与训练评测（15 文件） | schema/数据准备/4 个 NeMo-RL YAML | training/schema.py:39 |

关键分层事实：**推理层被 view_utils.py 单点支撑**——`find_and_group_views()`（inference/view_utils.py:57）按 `sample_NN/view_NN/offset_X_fov_Y_dist_Z/view.png` 目录约定发现并分组视图，被全部 26 个 runner import（含 inference/inference_mcq_NCQ.py:47）。5 个 prompt JSON（`inference/prompt_text_Type1.json` 等）定义三种任务的指令措辞，提示词本身是实验变量。

## 3. 核心子系统深讲

### 3.1 数据生产线（data_generation/blocks_render_image.py，4825 行）

Isaac Sim `SimulationApp` 先启动（data_generation/blocks_render_image.py:36），`omni.replicator.core` 做渲染与注解（:54）。难度分级驱动：5 个难度级×每级多场景×每场景 4 个方位视角（:124，`NUM_VIEWS = len(VIEW_AZIMUTHS_BASE)` :131）。视觉资产三形态可切：程序化 UV cube / 带纹理 factory_box / USD 资产（默认 `soup_can` 罐头，:293、:297、:331），64 色调色板归一化到 UsdPreviewSurface（:219、:285）。RTX 质量开关走环境变量：path tracing（:423）与 DLSS execMode（:435-438）。

真值生成的核心是**back-to-front 排序遮挡掩码**：按相机方位把列/块从后往前画（:733、:761），`_build_mask_back_to_front`（:789）逐块累积可见性，`get_visible_blocks_from_replicator`（:858）在像素级给出可见块集合。GT 按 task 开关逐个落盘（task1-task11，:191-203），主任务 MCQ 真值含正确字母（:1905、:1961）。产物通过异步执行器上传 S3（:518、:525、:547），场景级 `height_map` 写 scene.json（:574-577）。视角变体目录由 `_view_fov_dir` 生成（:603-605）。`summarize_gt_stats.py` 做质控：缩略图拼贴（data_generation/summarize_gt_stats.py:47）与字段分布直方图（:154）。

### 3.2 推理层（inference/）

- **API 模型**（claude/gemini/gpt/kimi/nemotron，README.md:113）：只依赖 `requests`，打同一个 OpenAI 兼容端点（`INFERENCE_API_BASE`，inference/claude/inference_text_claude.py:23），Claude 注释明写"NVIDIA Inference API (Claude Opus 4.6 via Bedrock)"（:6）；key 池存 `inference/api_keys.txt` 按行号选（:26）。Nemotron 关思考链（inference/nemotron/inference_text_nemotron.py:7-9）。
- **本地模型**（qwen/qwen3b/glm/hunyuan/vla0，README.md:131）：qwen 系与 glm 走本地 vLLM OpenAI 兼容 server（inference/glm/inference_text_glm.py:6、:425），hunyuan 用 `AutoModelForCausalLM` 多卡分片本地加载（inference/hunyuan/inference_image_hunyuan.py:218）。
- **NCQ 削减选项推理器**（inference/inference_mcq_NCQ.py，755 行）：砍掉错误选项只留 N 个（默认 3），答案回映射到原始 A-E 空间（:6-10 docstring）；模型注册表 7 项分 `nvidia_api`/`vllm` 双后端（:55-95，:327、:382）；确定性种子驱动选项选择与洗牌（:200、:229、:273-274）。

### 3.3 评测层（evaluation/）

`run_evaluation.py` 按 mode 分派 text/mcq/mcq3options/mcq4options（evaluation/run_evaluation.py:246、:252-256）。text 核心 `evaluation_text.py`（672 行）：整数抽取（:160）、逐 view 评分（:293）、层级聚合（:415）。image 评分对预测图做掩码重定向后的剪影 IoU（evaluation/evaluation_image.py:143，少于 2 块记 NaN :157，task1-10 全走剪影 :280）。OCR 线三后端 Tesseract/PaddleOCR/Qwen-VLM（evaluation/main_ocr/evaluate_main_ocr.py:222、:238、:279），2/3 共识投票（:9、:331、:366），优先级 `qwen_vlm > paddle > tesseract`（:328）。人类基线三脚本之一 `evaluation_human_mcq.py` 加载人工字母作答（:166、:183）。

### 3.4 论文统计（analyses/）

`spatial-IQ_analyses.py`（2878 行、83 个函数）是论文图表唯一生成源，`main()` 在 :2863；按文件名模式自动发现模型（README.md:285-286）。`hierarchy_dependency.py`（814 行）补统计检验：BH-FDR 多重校正（analyses/hierarchy_dependency.py:146）、固定效应相关（:176）、置换检验（:221）、场景内提升表（:282）、捆绑耦合表（:328）。每个图表的路径与参数登记在 `analyses/analyses_results/paper_output_manifest.json`（478 行），复现论文从 manifest 反查。

### 3.5 训练线（training/ + training_evaluation/）

数据契约是 6 个 Pydantic 模型：GtAnswers/GtMasks/McqTask/ViewSample/SceneSample/SpatialIQDataset（training/schema.py:39、:75、:96、:116、:142、:166）。`prepare_data.py` 按样本组切 train/val（:102），CoT 模式用 10 步分解模板把 task1-9 子答案串成 `<think>` 链再 `<answer>` 收尾（:56-70），`--cot-mask-final-answer` 把最终答案替换为占位符防泄漏（:136-139、:226）。4 个 NeMo-RL YAML：SFT/GRPO 各有标准版与 main 版；标准版 Qwen2.5-VL-7B（training/configs/sft_spatialiq.yaml:16、training/configs/grpo_spatialiq.yaml:51，GRPO 8 prompt×8 generation、500 步上限 :3-4、:7），main 版 Gemma-4-31B + DAPO-tight 配方（training/configs/sft_spatialiq_main.yaml:15、training/configs/grpo_spatialiq_main.yaml:2、:52）。CoT 系统提示词要求答案进 `<answer>` 标签（training/prompts/spatialiq_cot.txt:1）。`verify_cpu.py` 11 个冒烟测试覆盖依赖→数据→SFT/GRPO processor（training/verify_cpu.py:32、:184、:214）。训练后评测走 VLMEvalKit（README.md:34、training_evaluation/setup.sh）。

## 4. 关键数据流

```
Isaac Sim 渲染 ──view.png + gt.json──▶ 26 个 runner（API/本地）
                                          │ pred 文本/字母/图像 → inference_results/
                                          ▼
                          run_evaluation.py ──text/mcq/image 分派──▶ eval_raw_<slug>.csv
                                          ▼
              analyses/inference_results/（37 个 CSV：27 机器配置+人类）
                                          ▼
        spatial-IQ_analyses.py + hierarchy_dependency.py ──▶ tables/ + manifest
                                          ▼（另一支）
   training/prepare_data.py ──JSONL──▶ NeMo-RL（SFT/GRPO）──DCP ckpt──▶
   convert_all.sh → convert_dcp_to_hf.sh → convert_hfdcp_to_hf.py（FQN 重命名+FSDP 行分片重组，
   inference/qwen_finetuned/convert_hfdcp_to_hf.py:15、:65）──▶ HF 权重 ──▶ vLLM 复评
```

图像生成模型的评分是两段式：先剪影重叠（evaluation/evaluation_image.py:143），main 任务再走 OCR 共识重抽总数（README.md:88）。

## 5. 构建 / 运行 / 入口

- **文档站**：`uv sync --frozen && uv run sphinx-build -b html docs _site`（.github/workflows/pages.yml:29-32），Pages 双 job 部署（:38、:50）。
- **数据生成**：见 `data_generation/README_blocks_render_image.md`（285 行），输出结构+ S3 配置。
- **推理**：API 模型只需 `pip install -r inference/gemini/requirements.txt` + `inference/api_keys.txt`（README.md:117-123）；本地模型起 vLLM server 后 `--base-url http://127.0.0.1:8000/v1`（README.md:143）。
- **评测**：`python evaluation/run_evaluation.py folders.txt --pred-slug <slug> --mode <mode>`；OCR 线先 `setup_ocr.sh` 再用 `.venv-ocr` 跑（README.md:251-256）。
- **训练**：`prepare_data.py` 出 JSONL → 填 YAML 的 `train_data_path` 覆盖位（training/configs/grpo_spatialiq.yaml:137）→ 交给 NeMo-RL。

## 6. 设计决策与权衡

1. **合成数据而非真实照片**：渲染管线保证真值完美（像素级可见性掩码 data_generation/blocks_render_image.py:858），代价是领域差距——论文用人类基线校准（L07 的 eval_raw_human_*.csv）。
2. **API 单端点抽象**：所有商用模型走一个 OpenAI 兼容端点而非各自 SDK（inference/claude/inference_text_claude.py:23），26 个 runner 才能高度平行、三行换模型 ID。
3. **NCQ 削减选项而非改题**：把 5 选 1 削成 3/4 选 1 并回映射原字母空间（inference/inference_mcq_NCQ.py:229-279），标准评测脚本零改动即可评 `*3CQ/*4CQ` 变体——用确定性种子保证可复现（:200）。
4. **CoT 答案掩码**：SFT 教推理格式但不泄漏最终答案（training/prepare_data.py:136-139），把"记住答案"的捷径堵死，GRPO 阶段再让奖励引导推理。
5. **评分防模型偏置**：OCR 三后端共识 + 优先级链（evaluation/main_ocr/evaluate_main_ocr.py:328），hunyuan 单独 main 脚本绕开扩散模型"忠实复现输入"的偏置（inference/hunyuan/inference_image_hunyuan_main.py:9-11）。

## 7. 已核实勘误（详见 README.md 勘误节）

- claude/gemini/gpt/kimi 并非走各家原生 API，统一走 NVIDIA Inference API（inference/claude/inference_text_claude.py:6；inference/inference_mcq_NCQ.py:13）；
- GLM 是本地 vLLM 模型不是智谱云端 API（inference/glm/inference_text_glm.py:6、:425）；
- NCQ 的语义是"削减选项"不是"统一推理器"，且只覆盖 7 个模型注册（inference/inference_mcq_NCQ.py:6-10、:55）；
- schema.py 是 Pydantic BaseModel 而非 dataclass（training/schema.py:39）；
- DAPO-tight 不是独立 YAML，是 grpo_spatialiq_main.yaml 内的配方注释（training/configs/grpo_spatialiq_main.yaml:2）。

## 8. 新人上手路线

1. 读 README.md:15-34 任务与目录总表 → docs/index.md 任务卡；
2. 跑 `python training/verify_cpu.py` 过 11 个冒烟测试，零 GPU 建立环境信心（training/verify_cpu.py:32）；
3. 读 inference/view_utils.py:57-73 理解视图发现约定，再读一家 API runner（claude text）+ 一家本地 runner（glm）对照双形态；
4. 用 inference_results/ 现成预测跑 evaluation/run_evaluation.py 走通评分；
5. 进 data_generation/ 理解 GT 结构（gt.json 的 task1-task11 + height_map），这是理解一切任务的钥匙（data_generation/blocks_render_image.py:191-203）；
6. 需要复现论文图表时，从 paper_output_manifest.json 反查生成参数；
7. 训练兴趣者从 training/schema.py:39 的六个模型读数据契约，再读 prepare_data.py 的 CoT 模板（:56）与 GRPO YAML。
