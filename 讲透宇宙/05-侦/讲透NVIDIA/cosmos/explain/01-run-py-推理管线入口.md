# 01 · run.py：评测栈总入口与推理管线调度

## 一、角色定位

`run.py` 位于 `evaluation/cosmos3/reasoner/vlmevalkit/`（NVIDIA Cosmos 仓 vendored 的 VLMEvalKit fork），是整个 reasoner 评测栈的唯一人肉入口：一条命令完成"模型×数据集"的笛卡尔积调度——按数据集构建 prompt、分派给模型（本地或 API）、断点续跑、调 judge 判分、汇总报告。仓内 README 的评测示例与 scripts/ 下的批量脚本最终都收敛到它。同目录的 `run_api.py` 是 API 专用变体，`setup.py` + `requirements/` 定义可复现环境。它不实现任何模型或数据集逻辑，只做编排：模型来自 `vlmeval/config.py` 的 `supported_VLM` 注册表，数据集来自 `vlmeval/dataset/__init__.py` 的 `build_dataset` 工厂，推理循环下沉到 `vlmeval/inference*.py` 三条管线。

## 二、内部结构

**进程与 GPU 切分（run.py:15-46）**：`get_gpu_list()`（run.py:15）不依赖 torch，直接读 `CUDA_VISIBLE_DEVICES` 或管道 `nvidia-smi --list-gpus | wc -l` 计数。模块加载期就读取 `RANK/WORLD_SIZE/LOCAL_WORLD_SIZE/LOCAL_RANK` 四个 torchrun 注入的环境变量（run.py:28-31），当 `LOCAL_WORLD_SIZE>1` 时按 `GPU_PER_PROC = NGPU // LOCAL_WORLD_SIZE` 把 GPU 切片写回 `CUDA_VISIBLE_DEVICES`（run.py:34-42）——这是单机多卡跑多模型实例（每进程独占若干卡）的关键，而非张量并行。

**两个配置驱动的构造器**：`build_model_from_config`（run.py:61）支持 `--config` JSON 里 `"class"` 字段指定类名，在 `vlmeval.api`/`vlmeval.vlm` 命名空间里 getattr 动态解析（run.py:72-75）；构造前 `os.environ.pop('WORLD_SIZE')`（run.py:64），建完再还原（run.py:79-80）——因为新版 transformers 的 `device_map='auto'` 看到 WORLD_SIZE 会自作主张启用 TP，与 VLMEvalKit 的"torchrun 多实例"模型冲突。`build_dataset_from_config`（run.py:84）用 `inspect.signature` 做参数过滤：若类构造器接受 `dataset` 形参则自动注入数据集名（run.py:96-97）；无 `**kwargs` 的类只传合法参数（run.py:98-104）。

**CLI（run.py:110-214）**：双入口——`--data`+`--model` 名字列表，或 `--config` JSON 文件（互斥，run.py:231）。关键 flag：`--work-dir` 默认 `./outputs`（可被 `MMEVAL_ROOT` 环境变量覆盖，run.py:238-239）；`--mode` 三态 `all/infer/eval`（run.py:191）；`--reuse` 复用历史预测文件、`--ignore` 跳过失败样本（run.py:203-205）；`--retry/--api-nproc/--judge-nproc/--judge-args/--judge` 控制 API 与 judge 行为。

**main 主循环（run.py:227-546）**：外层遍历模型（run.py:277），内层遍历数据集（run.py:297），每个组合的目录骨架是 `outputs/{model_name}/T{日期}_G{git前8位}/`（`eval_id`，run.py:241-242、283）。推理分派按数据集能力三选一（run.py:346-377）：

- `dataset.MODALITY == 'VIDEO'` → `infer_data_job_video`（run.py:349，inference_video.py:231 定义）
- `dataset.TYPE == 'MT'`（多轮对话）→ `infer_data_job_mt`（run.py:359，inference_mt.py:173）
- 其余（图像单轮）→ `infer_data_job`（run.py:369，inference.py:200）

评测只在 `RANK == 0` 执行（run.py:457），核心一行 `eval_results = dataset.evaluate(result_file, **judge_kwargs)`（run.py:502）；judge 模型由一条按数据集名硬编码的巨型 if-elif 链决定（run.py:393-443），如 MCQ 默认 `chatgpt-0125`（run.py:406）、MathVista 系用 `gpt-4o-mini`（run.py:414-415）。

## 三、外部连接

上游依赖 `vlmeval.config.supported_VLM`（run.py:49）、`vlmeval.dataset.build_dataset`（run.py:50）、三条 inference 管线（run.py:52-54）、`vlmeval.smp` 的工具函数群（run.py:55-56，含 `prepare_reuse_files` 断点续跑）与 `vlmeval.utils.result_transfer` 的 MMMU/MMT-Bench 官方提交格式转换（run.py:57）。下游产物是 `outputs/{model}/{eval_id}/{model}_{dataset}.tsv` 预测文件与 `.eval.json` 评测结果（run.py:510-523），并在 `outputs/{model}/` 顶层建符号链接指向最新一轮（run.py:529-538）。

## 四、数据流

一次 `--data MMBench_DEV_EN_V11 --model Qwen2.5-VL-7B` 的旅程：parse_args → main 读环境变量切 GPU →（非 config 模式）把 `--retry/--verbose` 注入 `supported_VLM` 的 partial.keywords（run.py:251-258）→ 双循环进入组合 → `build_dataset` 下载数据集 TSV → RANK 0 先行 `prepare_reuse_files`（run.py:334-338）→ **`model = model_name`（run.py:343-344，此时模型仍只是字符串）** → `infer_data_job` 内部检查已有预测、未完成时才真正 `supported_VLM[model_name](**kwargs)` 实例化（inference.py:134，惰性构建；已完成则直接返回不加载模型，inference.py:105-116）→ 循环 `model.generate(message=struct)` 落盘 → RANK 0 组装 judge_kwargs → `dataset.evaluate` → 结果打印/tabulate 并可选存 JSON → 符号链接。任何组合抛异常都被 `except Exception` 吞掉记日志后 continue（run.py:540-543），保证一次批量评测不因单点失败全灭。

## 五、设计决策

1. **模型延迟实例化**（run.py:343-344 + inference.py:134）：模型在主循环里先以名字字符串传递，进推理函数确认"确有未完成样本"后才构造。这让 `--mode eval`、已完成的组合复用、以及 rank 0 先建数据集的编排都不必预载模型，7B 级模型可省十几 GB 显存。
2. **GPU 按进程切片而非张量并行**（run.py:34-42）：fork 沿用上游"单机多实例并行跑多模型"的吞吐优先哲学；TP 交给 wrapper 内部的 vLLM/lmdeploy 自己决定（如 qwen2_vl/model.py:273-283 按 GPU 数选 tp_size）。
3. **judge 硬编码链**（run.py:393-443）：不用配置文件而用 if-elif，换来零配置开箱即用——代价是新增数据集要改入口文件，属于典型的"评测脚本优先"取舍。
4. **`--config` 与命令行双轨**（run.py:230-234）：config 模式支持同名模型多参数变体（同模型不同 temperature/img_detail 各建一条，run.py:132-145 示例），并绕过 CLI 的全局 retry 注入。
5. **eval_id 内嵌 git commit**（run.py:241-242）：预测目录名携带代码版本，天然支持"同模型不同代码版本重跑"的可追溯对比。

## 六、新人提示（坑/勘误）

- **`LOCAL_RANK` 默认值是 1 不是 0**（run.py:31）：`os.environ.get("LOCAL_RANK", 1)`——单独 `python run.py` 起跑时 LOCAL_RANK=1、LOCAL_WORLD_SIZE=1，不触发 GPU 切分分支所以无实害，但任何"默认 rank 应为 0"的直觉在这里是错的，别拿它抄进自己的脚本。
- **judge 选择链里有元组 bug**（run.py:439）：`judge_kwargs['model'] = 'gpt-4.1',` 行尾多一个逗号，赋值成 `('gpt-4.1',)` 元组；下游 `build_judge` 若按字符串处理会走异常路径。MMReason 数据集实际会踩中。
- **`--reuse` 不设不等于干净重跑**：旧文件会被 `prepare_reuse_files` 移进 `bak_{时间戳}_{数据集}` 备份目录（smp/file.py:493-505），不会删；排查"为什么目录越跑越大"先看 bak_*。
- **FWD_API=1 是危险开关**（run.py:261-268）：把所有 API 模型强行替换成 `GPT4V` 类，用于端点兼容性测试，评测结果勿当真。
- **MMBench TEST split 只能官方服务器判分**（run.py:487-493，`MMBenchOfficialServer` 判据在 smp/file.py:94-116：本地 TSV 的 answer 列是否全非 NaN）；MMMU_TEST/MMT-Bench_ALL 也只转提交文件不本地判分（run.py:459-469）。
- **EVAL_PROXY 只包住评测段**（run.py:496-499、526-527）：judge 调用走代理、模型推理不走；推理期的网络行为不受此影响。
