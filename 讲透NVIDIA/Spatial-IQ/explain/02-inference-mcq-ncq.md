# explain 02 · inference/inference_mcq_NCQ.py——削减选项 MCQ 推理器

## 角色定位

755 行的 MCQ 专用推理器。NCQ 指 **reduced-option（削减选项）选择题**：把原生 5 选项（A-E）砍成 N 选项（默认 3），正确项必在其中，模型作答后**回映射到原始 A-E 字母空间**，标准评测脚本零改动可评（docstring 自述，inference/inference_mcq_NCQ.py:6-10）。它治的是"5 选 1 错误选项互相干扰"的测量噪声——`claude3CQ` 等 slug（inference/inference_mcq_NCQ.py:26-28）即其产物。

## 内部结构

三层组织。**模型注册表** `MODEL_CONFIGS`（inference/inference_mcq_NCQ.py:55）7 个条目按 backend 二分：claude/gemini/gpt/kimi 走 `nvidia_api`（:57/:63/:69/:75，经 NVIDIA Inference API），qwen/qwen3b/glm 走 `vllm`（inference/inference_mcq_NCQ.py:82、:88、:94 本地 server）。**双后端调用** `_nvidia_api_call`（:327）与 `_vllm_api_call`（:382）并列，CLI choices 锁死注册表（inference/inference_mcq_NCQ.py:636）。**选项削减核心** `_select_n_options`（:229）：从 4 个错误项挑 N-1 个，支持按 choice_types 约束"必含某类干扰项"（:237-246）；拼回正确项后 `rng.shuffle(kept)` 洗牌（:273-274），映射表 `new_to_orig`（:275）记新字母→原字母，`_map_answer_back`（:279）从模型输出抠单字母查表回原始空间。

## 外部连接

视图发现复用 view_utils（inference/inference_mcq_NCQ.py:47），与 25 个厂商 runner 同一目录约定；内置 DEFINITIONS_BLOCK 空间概念定义（inference/inference_mcq_NCQ.py:101）与精度测试指令 `_CI_MCQ`（inference/inference_mcq_NCQ.py:110）；输出进 `inference_results/`（:51），评测用 `--pred-slug <model>3CQ` 直接消费（:27）；key 池 `api_keys.txt` 按行号选（:50），与 API 厂商 runner 同规（inference/claude/inference_text_claude.py:26）。

## 数据流

逐任务循环：读 GT 正确字母与 choice_types → `_deterministic_seed(view_dir, task_name, num_options)`（inference/inference_mcq_NCQ.py:200）造种子 → 驱动 `_select_n_options`（:229）选保留项+洗牌 → 按新字母顺序送后端（:327 或 :382）→ 模型答新字母 → `_map_answer_back`（:279）回原始 A-E → 写 pred 文件。同 view/任务/选项数复现同一种子（main 任务亦然 inference/inference_mcq_NCQ.py:573），消融可重复。

## 设计决策

1. **回映射而非改评测**：复杂度全吸收进推理侧（inference/inference_mcq_NCQ.py:279），评测/统计链路无需感知选项被削减——接口防腐。
2. **确定性随机**：种子由数据路径+任务名+选项数派生（:200），换机器重跑得同一套削减题。
3. **类型约束采样**：干扰项类型可控（:237-246），支撑难度归因实验。
4. **单文件双后端**：不引 SDK，nvidia_api/vllm 均裸 HTTP（:327、:382），与仓内"API 客户端只依赖 requests"约定一致（README.md:115）。

## 新人提示

先读 inference/inference_mcq_NCQ.py:6-28 docstring（自含使用手册）再读注册表（:55）分清双后端；调试选项逻辑直接对 `_select_n_options`（:229）写单测——纯函数、只依赖 rng。加新模型只需注册表补一条+两后端其一适配。注意 3CQ/4CQ 评测 slug 约定（:27-28），漏后缀会按 5 选项 GT 对不上答案。
