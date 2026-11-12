> 标题：LoCoMo 基准评测入口——benchmark runner 精讲 · 源文件：jev_mem/benchmarks/locomo.py（877 行）· 图谱标签：基准与数据集层 / 一级枢纽

## 角色定位

整个 Jev-Mem"产出数字"的地方：LoCoMo benchmark 官方入口。`pyproject.toml:30` 注册 console script `jev-mem-eval = "jev_mem.benchmarks.locomo:main"`，`jev_mem/cli.py:40` 也经 `python -m jev_mem.benchmarks.locomo` 转发。一次完整运行 = 加载数据集→构建（或复用缓存）记忆图→跑问答→四指标评分→分层落盘。

文件头（jev_mem/benchmarks/locomo.py:2-11）交代架构演变："The core logic has been moved to proper modules under memory/ folder"——现在只剩编排壳：构建委托 `MemoryBuilder`、检索委托 `QueryEngine`、评测委托 `TestHarness`+`Evaluator`、重评分委托 `score_only_mode`。它有两副面孔（locomo.py:440 打印标题）：`jev_active` 时是 "Jev-Mem LoCoMo benchmark"，否则 "MAGMA baseline"——同一 runner 服务实验组与对照组。还实现了严格可复现机制：缓存按模型+embedding+config 指纹自动分仓、`validate_reuse_memory` 做配置一致性校验、结果文件带全套配置快照。

## 内部结构

- `validate_reuse_memory`（locomo.py:38）：复用缓存守门员——检查 graph.json/vectors/keyword_index.json 三件套（locomo.py:42-44）与配置文件（locomo.py:46-47）、老缓存补默认（locomo.py:49-51）、13 个构建字段逐一 JSON 比对（locomo.py:54-59），不一致抛 ValueError（locomo.py:60-61）
- `score_only_mode`（locomo.py:64-359）：免检索重评——加载旧结果（locomo.py:120-124）、逐题重跑 evaluate_answer（locomo.py:129-146）、重算四指标与分类分表（locomo.py:148-233）、写 rescored 结果（locomo.py:235-262）、多样本聚合（locomo.py:317-357）
- `main`（locomo.py:361-874）：
  - argparse 23 参数（locomo.py:363-404）：dataset/sample/model/embedding-model/score-only/reuse-memory/ablation 与 jev-mem 系列等，覆盖全部实验轴
  - Jev 配置组装（locomo.py:406-427）：flag 覆盖进 `JevMemConfig`（locomo.py:418），`--reuse-memory` 前置校验（locomo.py:420-427：单样本、开 read、非 rebuild/score-only）
  - 实验指纹（locomo.py:428-432）：`sha256(json.dumps(config))[:12]` 拼进缓存后缀——不同配置的图自动隔离
  - 样本主循环（locomo.py:486-777）：缓存目录三级命名（locomo.py:493-510，默认 `locomo_trg_cache_{model}/sample{id}{_openai}`）→`MemoryBuilder`（locomo.py:518-524）→三分支取记忆：reuse 含维度与样本归属两道校验 / cache 命中 / 全新构建记秒数（locomo.py:533-569）→`QueryEngine`（locomo.py:589-597）→`Evaluator`+`TestHarness`（locomo.py:600-606）→best-of-N（locomo.py:609-617）→分类过滤（locomo.py:619-628，五类 Multi-hop/Temporal/Open-domain/Single-hop/Adversarial 见 locomo.py:456）→并行/串行跑题（locomo.py:631-634）→指标计算（locomo.py:636-707）→结果落盘（locomo.py:709-763，`results_{model}/` 全快照）
  - 多样本聚合（locomo.py:779-872）：均值表+跨样本分类聚合（locomo.py:813-839）+aggregate JSON（locomo.py:849-871）
- `__main__` 入口（locomo.py:876-877）

## 外部连接

import（locomo.py:29-35）：`jev_mem.datasets.locomo.load_locomo_dataset`、`memory.cache_compat.memory_config_path`、`MemoryBuilder`、`QueryEngine` 四样顶层依赖。惰性导入：`JevMemConfig`（locomo.py:408）、`TestHarness`+`Evaluator`（locomo.py:433-434）、`BestOfNSelector`（locomo.py:610）、score_only 分支的 `LLMController`+tqdm（locomo.py:73-74）。dotenv（locomo.py:27）读 OPENAI_API_KEY。被引：pyproject 的 entry point、`jev_mem/cli.py`、README/docs、`tests/test_backend_cache.py`、`tests/test_project_layout.py`。图谱基准层枢纽。

## 数据流

端到端一次 `jev-mem-eval --sample 1 --model gpt-4o-mini --jev-mem`：

1. 配置：`--jev-mem` 置 write/read 双开（locomo.py:410-411）→指纹如 `jev_mem_3f2a9c1b8d07`→缓存目录 `locomo_trg_cache_gpt_4o_mini/sample1/jev_mem_3f2a...`（locomo.py:514）
2. 数据：`load_locomo_dataset`（locomo.py:475）→sample 含对话轮与 qa 列表（每题带 category 1-5）
3. 构建：缓存未命中走 `builder.build_memory(sample)`（locomo.py:555）——逐轮入库建图（可能被 admission 拒绝，locomo.py:565 打印 stored/rejected）→`builder.save()`；二次运行直接 `builder.load()`（locomo.py:549）
4. 检索+答题：`tester.test_questions_parallel(sample, 50, n_workers=3)`（locomo.py:632）——每题调 query_engine.query 拿上下文、LLM 生成、Evaluator 评分
5. 聚合：逐题 question/expected/predicted/category/metrics/llm_judge_score→locomo.py:636-707 算指标→locomo.py:731-761 写 JSON（stats 连 memory_stats 图统计一起快照）

`--score-only` 旁路（locomo.py:471-472）：跳过 2-4 步直接读旧结果重评分——换 judge 模型时省下全部构建检索成本。`--reuse-memory` 旁路：只跳构建（locomo.py:534-545），检索实验在冻结图上做，locomo.py:539-544 两道校验（向量维度匹配、图属于当前样本）防跨实验污染。

## 设计决策

**配置指纹分仓**（locomo.py:428-432+514）是实验管理核心：任何 write 侧参数变化（admission 阈值、决策后端、consolidation 间隔）都产生新缓存目录，杜绝"改配置读旧图"的静默污染。`validate_reuse_memory` 的 13 字段白名单比对（locomo.py:54-58）进一步保证显式复用语义一致——locomo.py:51 的 setdefault 是老缓存迁移兼容层。

**模型归一化命名**（locomo.py:496 等四处）：`gpt-4o-mini`→`gpt_4o_mini` 让目录名合法，同一逻辑重复四次未提取。**去 Cat5 双口径**（locomo.py:161-169、651-660）：Adversarial 类（问记忆里没有的事，期望答不知道）拉低常规指标，所有报告给 with/without 两套——LoCoMo 社区惯例口径。**best-of-N 三种选优**（locomo.py:391-395、609-617）：每题跑 N 次按 llm_judge/voting/f1 挑最好；批判地看这是刷分机制，消融对比必须两侧同配置。

**一处实锤 bug**：`score_only_mode` 的 locomo.py:266 `wrong_answers = [r for r in test_results if ...]`——`test_results` 在该函数内**从未定义**（正确变量是 updated_results），走到必 NameError。该分支无测试覆盖，属休眠地雷：跑 `--score-only` 且存在低分题即炸。locomo.py:279-358 引用其产物同受连坐；主流程 main（locomo.py:636-707）的同名统计是健康版本——复制分化后只修了主流程的典型痕迹。

## 新人提示

先读 main 的 argparse 块（locomo.py:363-404）——23 个参数就是全仓实验轴清单，每个 flag 对应论文一张表。顺着 locomo.py:486-777 样本循环读，重点三处：locomo.py:533-569 缓存三分支（实验如何免重建）、locomo.py:518-597 组件装配（memory/query/eval 三层如何拼）、locomo.py:636-707 指标计算（结果 JSON 每个数字的口径）。

四个常见坑：改了 write 侧配置看不到行为变化——八成缓存命中（locomo.py:546），要么 `--rebuild` 要么认新指纹目录；`--reuse-memory` 报配置不一致——那是 locomo.py:54-59 白名单在保护，想强制请改回一致配置；结果目录叫 `results_gpt_4o_mini/` 而非模型原名——locomo.py:496 归一化所致；`--score-only` 遇低分题崩溃——locomo.py:266 的 NameError，修该行或避免触发。默认并行 3 worker（locomo.py:389-390），调 OpenAI 限流时加 `--no-parallel` 串行排查。
