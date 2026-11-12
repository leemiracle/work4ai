# 07 · cosmos_eval：一键跑全套的评测编排入口

## ① 角色定位

`evaluation/cosmos3/reasoner/vlmevalkit/cosmos_eval/` 是 fork 顶层的"评测编排层"：不含任何推理或打分逻辑，只做三件事——**组装配置、并发驱动 stock `run.py`、读出分数**。README 原话："No extra evaluation logic lives in the kit — the kit only composes the inputs and reads the outputs"。它是把 NVIDIA 内部评测流水线公开可复现化的产物：`models/cosmos.json` 记录内部跑分的确切采样参数，`data/metropolis/*.json` 记录基准入口参数，`manifest.json` 记录 CLI 并发旗标，三者拼出内部配方，`run_all.py` 组装配跑。本批发布 Metropolis "smart infra" 基准——`AETCBench_all`（官方 TAR）+ 8 个 `VANTAGE_*` 共 9 个；**数据集尚未公开**（挑战赛进行中），当前是参考配方。

## ② 内部结构

**run_all.py（279 行，stdlib-only）**：`load_model_layer()` :60 读 `models/<model>.json`（缺失时列出已有层名退出）；`_render_env()` :76-84 递归做 `${VAR}` 环境变量替换；`compose()` :87-97 核心"哑合并"——`model_conf = {class} | defaults | benchmarks[bench]` 三层 update，注释特意声明"no routing/schema logic here"（:13）；`build_config()` :100-105 组出 `{"model": {...}, "data": {bench: ...}}` 文档；`select_benches()` :113-133 把 manifest key（形如 `metropolis/VANTAGE_SOT`）拆 domain/bench 并编稳定序号（:132）；`_bench_workdir()` :136-140 给 ConcatDataset 基准用**不含基准名**的 `_concat_NN` 目录（见⑥）；`_run_cmd()` :148-158 拼 `run.py --config --work-dir --api-nproc/--judge-nproc --verbose --save-eval-results`；`run_one()` :161-192 单基准全流程——compose/import 配置写盘 → `subprocess.run`（cwd=VLMEVALKIT_ROOT，日志重定向 run.log，:184-185）→ `parse_score.report()` 取分（:189）；`main()` :217-275 ThreadPoolExecutor 并发（默认 `--concurrency 2`，:222），支持 `--export-configs`（占位符原样导出，:237-244）/`--import-configs`（导入配置仍会 `_render_env`，:172-175）/`--dry-run`，任一基准失败最终 `SystemExit(1)`（:274-275）。

**parse_score.py（787 行）**：文件头 :10-18 声明是内部 `vlmeval_metric/score_parser.py`+`eval_data.py` 的 **VERBATIM VENDORED PORT**，维护者 CI 门禁对同一 eval JSON 断言两实现输出一致——"Do not hand-edit"。`load_eval_summary_with_metadata()` :51-75 兼容 `*.dict.eval.json` 与 `*.df.eval.json`（DataFrame 三段式）两种产物；`normalize_score()` :95-102 用"值 ≤1.0 即 0-1 制"启发式统一 0-100（注释点名 AI2D/MMBench 存 0-1、CountBenchQA 存 0-100）；`_detect_format()` :115-138 探测 A 平面标量/B 多 split 数组/C 索引行列表/D 裸数值四格式，`parse_scores()` :267-288 分发；**`SCORE_OVERRIDES` :295-377 是 50+ 条按基准覆写的取分规则**，知识密度峰值：6 个异常检测基准（TailgatingVerification :301 至 ITSCollision :306）统一取 macro avg F1（注释：类别严重偏斜下 accuracy 被多数类美化，macro-F1 才诚实）；`MetropolisDVC`/`VANTAGE_DVC` 取嵌套 `overall.SODA_c`（:307-308）；`VANTAGE_SOT` 取 `Overall`（:341）；`AETCBench_all` 取 `weighted_mean`（:358）；`SCORE_OVERRIDE_PREFIXES` :381-394 让 `MVBench_8frame` 类变体名共享逻辑；`extract_overall_score()` :597-629 精确名→前缀→通用兜底，全败返回 0.0；`find_eval_output()` :716-719 取 `*/*/*.eval.json` 中 mtime 最新；`report()` :745-762 是给 run_all 的编程接口，`main()` :765-783 独立 CLI（`--work-dir`/`--eval-json` 互斥必填，:767）。

**三份 JSON**：`manifest.json` 9 条目全在 `metropolis/` 域，run 旗标统一 `{api_nproc: 8, judge_nproc: 4}`；`models/cosmos.json`：`class: CosmosReason2`、defaults `temperature 0/seed 1/retry 10/max_tokens 8192/timeout 600`，benchmarks 按基准覆写——`VANTAGE_2DPointing` max_tokens 降到 512、`VANTAGE_DVC` 提到 16384+`total_pixels 8388608`、EventVerification/Temporal/VQA 统一 `total_pixels 16777216`、`VANTAGE_SOT` 挂完整 `response_format.json_schema`（7 个 frame 各为 4 元数组或 null 的 strict schema，直接让端点输出结构化 JSON）；`data/metropolis/VANTAGE_SOT.json` 仅 4 行：class/dataset/max_pixels 921600/nframe 8。

## ③ 外部连接

- **被驱动方**：`../run.py`（stock VLMEvalKit 入口，run_all.py:44 以 `RUN_PY` 定位），每基准一次子进程。
- **上游依赖**：`class: CosmosReason2` 指向 fork 内 vlmeval wrapper 层（本系列 04/05 篇）；`model_family: "cr"` 写进 dataset_conf 供数据集侧识别。
- **环境变量契约**（docstring :17-19）：`COSMOS_API_BASE`/`COSMOS_MODEL`/`COSMOS_API_KEY` 给受测端点，`OPENAI_API_BASE`/`OPENAI_API_KEY` 给 gpt-4o 判官——两套凭据必须同配。
- `cosmos_eval/.gitignore` 补丁：仓库根忽略 `*json` 与 `data/`，这里用 `!*.json`/`!data/**` 把本目录资产重新纳入版本控制。

## ④ 数据流

单基准生命周期：`manifest[key]` → select_benches 拆 domain/bench → `load_data_conf`+`load_model_layer` → `compose` 三层合并 → `build_config(render=True)` 展开 `${VAR}` → 写 `_configs/<bench>.json` → 子进程 `run.py --config` → `find_eval_output` 挑最新 `*.eval.json` → `load_scores` 注入 `__columns__` → `extract_overall_score`（先查 SCORE_OVERRIDES）→ 结果汇入 `_print_summary`。失败两通道：子进程非零退出（status=error，指 run.log）与 eval 产物缺失（status=no-eval），都不中断其它基准，但让 main 最终 exit 1。

## ⑤ 设计决策

1. **哑合并优于智能路由**：compose 拒绝任何 schema/路由逻辑，复杂度推给内部生成工具，公开层只消费——复现行为与内部严格一致且易审计。
2. **配置三层分离**（dataset/model/run 旗标）：换模型家族只动 `models/<family>.json`、调并发只动 manifest，互不污染。
3. **环境变量晚绑定**：`${VAR}` 占位符原样进 git，跑时才替换；`--export-configs` 导出保留占位符（:243），可离线审阅再 import 回跑。
4. **parse_score 双实现锁死**：vendored port+CI 同输入断言一致（:17-18），以少量重复换"公开分数=内部分数"的硬保证。
5. **评分覆写表而非每基准一个解析器**：50+ 基准差异收敛为一张 lambda 表+前缀表，新基准加一行即可。

## ⑥ 新人提示（坑与勘误）

1. **ConcatDataset 基准的工作目录陷阱**（run_all.py:46-52）：Astro2D 类基准按子数据集评测时 `eval_file.replace(dataset_name, sub_name)` 会替换路径里**所有**出现的基准名——work-dir 含基准名时子结果指向永不创建的兄弟目录直接 FileNotFoundError。`_CONCAT_BENCHES = {"VANTAGE_Astro2D"}`（:52）因此给无名目录。自增基准清单须同步维护此集合。
2. **docstring 引用的 `gen_oss_configs.py` 与 `vlmeval_metric/` 不在本仓**：run_all.py:12-13 与 parse_score.py:10-15 都提到，全仓检索不存在——内部工具引用，公开仓只有消费端；按 :17-18"Do not hand-edit"，改取分逻辑应去 upstream。
3. **normalize_score 的 1.0 启发式有理论误伤面**：0-100 制下真考出 ≤1.00 分会被再乘 100。实践概率极低（ODinW13 注释 :585-589 专门论证 mAP 恒在 [0,1] 不会双重缩放），但读分须知此假设。
4. **默认并发只有 2**：对外部端点瞬时压力 = concurrency × api_nproc（manifest 覆盖了 `_run_cmd` 默认的 16 而为 8），调参先算这个乘积。
5. **`--dataset` 显式传名更稳**：`_infer_dataset_name` 的"去模型前缀"推断（:731-742）在带下划线模型名上会切错。
