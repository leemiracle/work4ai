# 10 agent_eval 评测 harness 与 eval_sweep：两条评测线与 LLMJudge

## 角色定位

仓里有两条互补的评测线。**agent_eval/**（仓根，3474 行）测"claude/codex agent 用了 nemo-retriever skill 后答得有没有更好"，双轨——recall 轨（skill vs 无检索 baseline）与 functional 轨（行为 pass/fail）。**tools/evaluation/**（库内，2802 行）是产品层 eval_sweep：配置驱动 QA 批量评测，挂 CLI 隐藏子命令 `retriever eval`。两者共享判分核心 `LLMJudge`——ragas AnswerAccuracy 的去依赖移植。

## 内部结构

**agent_eval 三段式**（`agent_eval/README.md:17-29`）：`extract_queries.py`→`run_agent_eval.py`→`build_report.py`。关键约束：跑 agent 的脚本**零 nemo_retriever import**（拷到干净机器跑 baseline），只有报告脚本允许 import 仓内代码（`README.md:25-29`）。防泄漏三处：抽取产 answer-free queries——无答案/金标页/类别，"refusal 标签不能提示 agent"（`README.md:36-38`）；baseline 用 PATH-shim 挡 `retriever`+settings.json deny+空 HF cache（`README.md:70-71`），claude 适配器再加 `--disable-slash-commands`（`adapters/claude.py:44-48`）；save-root 必须在仓外否则 agent 摸到 `.claude/skills/`——硬 guard（`README.md:229-231`，`run_agent_eval.py:97`）。适配层 `AgentAdapter` ABC 五钩子（`adapters/base.py:35-53`），claude 版直接 `claude --print --output-format json --permission-mode bypassPermissions`（`adapters/claude.py:25-41`）。成本对齐：Claude 直接报 `total_cost_usd`，Codex 不报钱——`_PRICING` 表按 token 推（gpt-5.5 输入 $5/缓存 $0.5/输出 $30 每百万，`README.md:176-187`，表在 `build_report.py:74`）；token 归一化处理口径差（`README.md:189-194`）。

**functional 轨**四脚本（`README.md:252-257`）：203 查询=119 retrieval_answer/60 ingest/24 ingest_plus_answer，6 个 stateful 测试排除（驱动器未建，`README.md:284`）。评分映射（`README.md:279-284`）：retrieval_answer 走 LLM PASS/FAIL rubric；ingest 走程序化闸门——workdir 里 LanceDB 表 rows>0（`eval_functional.py:127` 的 `_count_rows`）且 rubric 确认输出是 ingest 确认而非问答；rubric 刻意只看可观测输出+程序化验证的工件事实，忽略 tracer/job ID/流式进度等结构性不可见信号——"否则 ~80 个 ingest 测试假 FAIL"（`README.md:286-292`）。rubric 指令原话"Decide PASS/FAIL based ONLY on the agent's [observable output]"（`eval_functional.py:56`），判分复用 judge transport 裸调 `judge.complete`（`eval_functional.py:183`）。报告把 run_timeout/judge_error 单列为 non-results 与真逻辑 FAIL 分开（`README.md:403-406`）——宕机不被读成低通过率。

**eval_sweep**：入口 `tools/evaluation/runner.py:42` 的 `run_eval_sweep(config, qa_pairs, results_dir)`——按 config 的 evaluations 列表循环，每个 eval 配一个 generator 模型+一个 judge 模型，构建 `LiteLLMClient.from_kwargs`+`LLMJudge.from_kwargs`（`runner.py:118-134`），跑 N 次写时间戳 JSON。CLI 侧 `retriever eval run <config.yaml>` 懒 import 它（`tools/evaluation/cli.py:235`）。算子化的评分部件：`JudgingOperator`（`tools/evaluation/judging.py:16`）声明 required/output 列（`judging.py:35-37`），ThreadPool 并发判分、单行失败降级为带 error 的 JudgeResult 而非炸整批（`judging.py:83-86`）。程序化计分全在 `scoring.py`：三层架构 Tier1 answer_in_context/Tier2 token_f1（SQuAD 风格，`scoring.py:14`、实现 `:204`）/Tier3 LLM judge，纯计算零 LLM 依赖。

**LLMJudge**（`models/llm/clients/judge.py:217`）：ragas AnswerAccuracy 双判官移植——两个改写判官各打 0/2/4，Judge2 交换 reference/candidate 角色做双向等价检查，归一化取均值（docstring `judge.py:6-24`）。判官 prompt 逐字复刻 ragas（`judge.py:46-72`）；解析器三层降级：剥 `<think>` 思考块（Nemotron reasoning 实测）→剥 code fence→JSON→正则→裸 0/2/4 token（`judge.py:186-199`）。

## 外部连接

**延迟 import 三处实证**（本任务点名的机制）：①`models/llm/__init__.py:65-75` 用模块级 `__getattr__`+`_LAZY_IMPORTS` 字典——types/Protocol 零依赖常驻，`LiteLLMClient`/`LLMJudge` 首次访问才加载，docstring 明示契约"cheap import vs imports litellm on first use"（`__init__.py:9-14`）；②`tools/evaluation/__init__.py:36-46` 同款 `__getattr__`，且 lazy 表里保留旧模块路径别名（`nemo_retriever.evaluation.*`）；③最内层 `litellm.py:143` 的 `import litellm` 在 `complete()` 函数体内，`runner.py:75-77` 的四个评测类也是函数内 import——不装 `[llm]` extra 也能 import 评测类型。其余连接：agent_eval 调外部 `claude`/`codex` CLI 与 judge 端点 integrate.api.nvidia.com（`README.md:158`）；`build_report.py:42` 从 `skill_eval.score` 借 `recall_at_k`；JudgingOperator 挂在 `graph/retriever.py` 的 `RetrieverPipelineBuilder` 流式链上（`.judge(judge)`）；skill_eval（篇 9 的 skill 评测）复用同一 judge 基建。

## 数据流

agent_eval recall 轨：manifest → answer-free queries → 每查询独立 workdir（语料 symlink+GPU 轮询钉卡）→ agent 单轮跑（skill 轨先跑 ingest setup 轮或 `--subprocess-ingest` 直建索引）→ output.json（final_answer+selected_chunks）→ build_report 重读 manifest 对金标 → recall@1/5/10（按各 run 的 page_index_base 归一，baseline 0 起始 vs retriever 1 起始）+judge+retriever 使用率三分类（attempted/succeeded_clean/succeeded_engine）。eval_sweep：eval_sweep.yaml → `run_eval_sweep` → 每 eval 构 generator+judge → QAEvalPipeline 检索→生成→判分 → 结果 JSON+多层汇总打印（`cli.py:33` 的 multi-tier summary）。

## 设计决策

1. **评测脚本与被测物解耦**：runner 零仓内 import、manifest 可重定位、全 CLI flag——"换环境只 repoint 五个路径"（`README.md:464-465`）。
2. **answer-free 防提示泄漏**：标签不进 agent 可见文件，金标在报告期重读 manifest。
3. **程序化闸门优先于 LLM 判分**：ingest 类以 rows>0 硬事实为准，rubric 只补确认——可复现性来自"不判结构性不可见的东西"。
4. **non-results 与 FAIL 分账**：超时/判分器故障单列，防止基础设施事故污染通过率结论。
5. **延迟 import 分层**：类型层常驻、实现层 lazy、依赖层函数内——三层递进让 slim 安装可用性最大化。
6. **judge 复刻而非依赖**：ragas 的 prompt/尺度/双判官语义逐字搬，instructor 约束解码换成"prompt 要求 JSON+宽容解析"。

## 新人提示

- 复跑评测先查三条 gotcha：save-root 在仓外、GPU 钉卡防 OOM、judge 并发 6-8 否则 200 条要数小时（`README.md:228-238`、`:457-458`）。
- Codex 的 `retr_succeeded_clean` 天然偏低（~1s exec-yield 把 retriever query 挪后台，抓不到干净退出码）——看 `succeeded_engine` 才是真相（`README.md:236-238`）。
- 改 judge prompt 后老 report.json 的 judge 分会被缓存复用，需 `--regrade` 强制重判（`README.md:393`）。
- 加新模型定价只改 `build_report.py:74` 的 `_PRICING` 表，不动 adapter。
- 判官模型默认 `nvidia_nim/nemotron-3.5-lightning-30b-a3b`，`<think>` 剥离是针对它的实测补丁——换 reasoning judge 时留意解析层。
