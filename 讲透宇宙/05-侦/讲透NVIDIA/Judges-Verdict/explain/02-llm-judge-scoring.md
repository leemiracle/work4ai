# 02 · llm_judge_scoring.py —— 评分引擎主链路与 trial 断点续跑

## 角色定位

`llm_judge_benchmark/scoring/llm_judge_scoring.py`（414 行）是框架的执行心脏兼 CLI 入口（pyproject.toml 注册命令 `llm-judge-score`）：把 data/evaluation.json 变成 RAGAS 数据集，按 YAML 配置逐裁判各跑最多 3 个 trial 的 AnswerAccuracy 评测，落盘 results/{裁判}/trial{N}.json。

## 内部结构

四个纯函数 + 两个主函数：

- `load_evaluation_data`（llm_judge_scoring.py:35-59）：读 JSON 转 DataFrame，把 question/gt_answer/gen_answer 映射成 RAGAS 惯用列名（映射表 llm_judge_scoring.py:45-50）。
- `process_evaluations`（llm_judge_scoring.py:62-66）：四列 drop_duplicates，唯一问答对只评一次。
- `create_ragas_dataset`（llm_judge_scoring.py:69-80）：逐行构造 SingleTurnSample，只带 user_input/reference/response 三字段。
- `run_judge_evaluations`（llm_judge_scoring.py:83-289）：核心循环，见"数据流"。
- `main`（llm_judge_scoring.py:292）：argparse 五参数（llm_judge_scoring.py:296-317）；先实例化 Manager 收集实际在用的框架（llm_judge_scoring.py:328-338），按框架分组预检环境变量（litellm 查四项，llm_judge_scoring.py:344-353），缺失只警告；--judges 缺省取全部配置模型（llm_judge_scoring.py:373-377）。

## 外部连接

上游吃 scripts/data_prep.py 产的 evaluation.json。配置全经 JudgeConfigManager（llm_judge_scoring.py:106-109、:135）。LLM 侧双路：LITELLM 框架走 create_ragas_litellm_wrapper（llm_judge_scoring.py:147-156），其余走 create_langchain_llm + LangchainLLMWrapper（llm_judge_scoring.py:161-162/:182-183）。RAGAS 侧三件套：AnswerAccuracy()（llm_judge_scoring.py:263）、RunConfig(max_workers=num_workers)（llm_judge_scoring.py:260，并发度来自 YAML）、evaluate()（llm_judge_scoring.py:276）。

## 数据流

裁判循环（llm_judge_scoring.py:112 外层 tqdm）：

1. **目录与断点**：建 results/{judge}/；`while os.path.exists(trial{N}.json)` 扫出 next_trial（llm_judge_scoring.py:126-127）；超过 max_trials 直接 skip（:130-132）——**checkpoint 的全部秘密就是文件名探测**，重跑同命令天然续跑。
2. **造 LLM**：模型不在配置则 continue（llm_judge_scoring.py:137-140）；失败隔离粒度是裁判级（:169-171）。
3. **trial 循环**（llm_judge_scoring.py:178）：每 trial——
   - **原方法保存/恢复**：首个 trial 把 generate/agenerate_text 原方法存到 _original_* 属性（llm_judge_scoring.py:186-197），后续每 trial 开头恢复（:199-203）——防补丁无限叠加；
   - **o1 温度补丁**：裁判名含 "o1" 时（llm_judge_scoring.py:206）换上丢弃 temperature 的 patched 方法（:208-221）；
   - **通用闭包 patch**（llm_judge_scoring.py:236-251）：恒等转发，历史地层；
   - **评测执行**：evaluate().to_pandas()（llm_judge_scoring.py:276），**立即**写 checkpoint（:283-284）。

## 设计决策

- **trial 即 checkpoint、文件名即状态**：续跑语义完全由 results/ 目录内容定义——崩溃后重跑同一命令即恢复，全文件最值得抄的决策。
- 评分参数全来自 YAML（llm_judge_scoring.py:255）——配置单一事实源。
- o1 补丁用"改对象方法"而非传参，避免侵入 RAGAS/LangChain 上游；代价是保存/恢复仪式（llm_judge_scoring.py:186-203）不可省，漏一步就是隐蔽参数丢失。

## 新人提示

先 `llm-judge-score --judges <一个便宜模型>` 小规模验证：裁判名必须与 YAML 键名逐字一致（llm_judge_scoring.py:12-14）。删掉 trial3.json 重跑可体验续跑。结果按裁判×trial 聚合即得一致性统计；max_trials 只控上限，已存在的 trial 永不重算（llm_judge_scoring.py:126-132）。

——锚核对于 2026-11-08，commit dfbcd5ee。
