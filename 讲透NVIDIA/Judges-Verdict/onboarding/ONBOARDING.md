# Judges-Verdict 新人导览（ONBOARDING）

> 仓：/usr-data/data2/repos/agent-repos/NVIDIA/Judges-Verdict（commit dfbcd5ee）
> 图谱：44 节点 / 83 边 / 9 层 / 12 步 tour，校验 0 issues；行号锚均经源码核实（2026-11-08）

## 1. 项目定位与核心价值

Judge's Verdict 是 NVIDIA 开源的 **LLM-as-Judge 评测框架**——评的不是普通模型，而是"裁判模型"本身：用一批 LLM 对同一份生成答案打分，量化每个裁判与人类标注的一致性（配套数据集 `nvidia/judges-verdict` 已发布 HuggingFace）。差异化在 `llm_judge_benchmark/utils/litellm_ragas_wrapper.py`——**完全绕开 LangChain 的 LiteLLM 直连 RAGAS 适配器**（litellm_ragas_wrapper.py:6 直言 "bypasses LangChain entirely"），凭 LiteLLM 统一路由让 26 家供应商裁判（GPT 全系、Claude、Nemotron、Gemma、gpt-oss、本地 vLLM）进同一张评测表。主配置收录 26 个裁判（全部 framework: litellm），每个默认跑 3 个 trial。

## 2. 总体架构

三大组件（docs/Architecture_Overview.md 口径）：

- **配置管理器**：`judge_config_manager.py` 定义 ServingFramework 枚举（litellm/oneapi/nvdev，judge_config_manager.py:21-26）与 JudgeModelConfig 数据类；`judge_config.py` 模块级实例化 Manager 并暴露 6 个便捷函数（judge_config.py:17）做门面。
- **评分引擎**：`scoring/llm_judge_scoring.py` 把评测 JSON 转 RAGAS 数据集，逐裁判跑 AnswerAccuracy（llm_judge_scoring.py:263），每 trial 写 checkpoint 支持断点续跑。
- **LiteLLM 适配层**：用 litellm completion API 手工实现 RAGAS 最小接口。

数据流一条线：HuggingFace `nvidia/judges-verdict` → `scripts/data_prep.py`（train 丢 annotations；test 三路分拣，coral/dc767 外联 join）→ `data/evaluation.json` → 评分引擎 → `results/{裁判名}/trial{N}.json`。双框架分派点在 llm_judge_scoring.py:145-158：LiteLLM 走直连包装、其余走 LangChain 包装。

## 3. 核心模块地图

| 模块 | 职责 | 关键锚 |
|---|---|---|
| judge_config_manager.py | YAML 配置心脏 | 枚举:21-26；15 字段:29-48；四路径搜索:148-153 |
| judge_config.py | 门面，6 查询函数 | 模块级实例化:17；get_default_judges:25 |
| scoring/llm_judge_scoring.py | 评分主链路+CLI | run_judge_evaluations:83；main:292 |
| utils/litellm_ragas_wrapper.py | RAGAS↔LiteLLM 适配 | RagasLiteLLMWrapper:28；工厂:176 |
| scripts/data_prep.py | ETL | coral join:87-140；dc767 join:143-188 |


JudgeModelConfig 两个"路由"方法值得记：`get_api_key()`（judge_config_manager.py:69-104）按模型前缀选环境变量——`local/` 前缀返回字面量 "EMPTY"（judge_config_manager.py:82）、`nvidia_nim/`→NVIDIA_NIM_API_KEY（:85）、未知前缀默认 OPENAI_API_KEY（:93）；`get_effective_base_url()`（judge_config_manager.py:106-121）为 OneAPI 拼内部代理 URL（:118-119），NVIDIA NIM 读 NVIDIA_NIM_API_BASE（:112-115）。

## 4. 数据流 / 控制流

评分主链路（run_judge_evaluations，llm_judge_scoring.py:83-289）：

1. **造评测集**：load_evaluation_data 把 question/gt_answer/gen_answer 重命名为 RAGAS 惯用列（映射表 llm_judge_scoring.py:45-50），process_evaluations 去重（:65），create_ragas_dataset 逐行构造 SingleTurnSample（:71-79）。
2. **逐裁判循环**：建 `results/{judge}/`，**扫描已有 trial 文件找断点**（llm_judge_scoring.py:126-127），满 max_trials 即跳过（:130-132）。
3. **造 LLM**：LiteLLM 调 create_ragas_litellm_wrapper（llm_judge_scoring.py:147-156），否则 create_langchain_llm（:161）。
4. **trial 循环**：每 trial 先保存/恢复包装器原方法（llm_judge_scoring.py:186-203，防上轮补丁污染），对 o1 系打温度豁免补丁（:206-221），再包一层通用闭包 patch（:236-251），RAGAS evaluate 后**结果立即写 trial{N}.json**（:283-284）——断点续跑的落点。

CLI 入口 main()（llm_judge_scoring.py:292）五参数（--evaluation-file/--output-dir/--judges/--max-trials/--config-file，:296-317），注册为 `llm-judge-score` 命令；main 先按在用框架预检环境变量（:344-361），缺 key 只警告，--judges 缺省取全部配置模型（:373-377）。

## 5. 环境与运行方式

- Python >=3.12,<4.0（pyproject.toml:12），Poetry 或 pip 双安装；关键锁定 ragas ~0.3.3、litellm ~1.76.2（pyproject.toml:14-21）。
- 备数据：`python scripts/data_prep.py` 生成 data/evaluation.json；CORAL 钉死 HuggingFace revision（data_prep.py:55）、dc767 CSV 钉死 GitHub nv-ingest 固定 commit（data_prep.py:226）——可复现性靠两处 commit 锚。
- 跑评测：`llm-judge-score --judges gpt-4o claude-sonnet-4`；裁判名即输出目录名（llm_judge_scoring.py:12-14）。环境变量按框架配：litellm 需 OPENAI/ANTHROPIC/NVIDIA_NIM key+BASE（llm_judge_scoring.py:344-353），nvdev/oneapi 需 NVIDIA_API_KEY/ONE_API_KEY（:355-361）。

## 6. 设计决策与权衡

- **LiteLLM 优先、LangChain 兜底**：官方路线收窄到 LiteLLM（README 明示），LangChain 路径（ChatNVIDIA/ChatOpenAI，judge_config_manager.py:255/:295）留给 nvdev/oneapi 内部框架；LiteLLM 分支在工厂里直接 NotImplementedError（judge_config_manager.py:300-303）强制走直连。
- **o1/o3 温度补丁三处重复**：judge_config_manager.py:276（构造时不传）、litellm_ragas_wrapper.py:94（completion 时不传）、llm_judge_scoring.py:206（运行时 patch）三层各自为战，改动易漏。
- **defaults 只补缺不覆盖**：YAML defaults 合并仅当模型条目缺键才下放（judge_config_manager.py:184-186），逐模型定制 num_workers（实际 1-32）不被冲掉。

## 7. 已知问题与勘误

- **utils/__init__.py:7 的 `__all__ = ["llm_score_utils"]` 是陈旧声明**：仓内不存在 llm_score_utils 模块，真实实现是 litellm_ragas_wrapper.py；星号导入实际导空（无害但误导）。
- **两个 notebook 均为 119 字节 0 cells 空壳**（notebooks/01_Quick_Start_Example.ipynb、02_Analyze_Results.ipynb）——README 提到的结果分析无代码支撑，只能手读 results/{judge}/trial{N}.json。
- **补丁地层可读性差**：llm_judge_scoring.py:206 o1 补丁用 `"o1" in judge` 子串匹配（未来 "gpt-o4" 类命名会漏、o3 只在 manager/wrapper 层处理），与 :236 通用 patch（仅恒等转发）功能重叠，靠 :199-203 恢复原方法防无限叠加。
- **.flake8 被图谱 scanner 误归为代码文件**（实为 120 字符行宽的 flake8 配置）——工具口径问题非仓缺陷。另注意 data_prep.py:31/:49 在 ImportError 时 `os.system(pip install)` 自装依赖，有供应链风险。

## 8. 新人上手路线

1. 读 README + docs/Architecture_Overview.md 建立三组件认知。
2. 通读 judge_config_manager.py（319 行）：从 ServingFramework（judge_config_manager.py:21）到 create_langchain_llm（:233），这是全仓词汇表。
3. 对照 config/judge_config_litellm_example.yaml 配一个裁判（4 模型最小集，含本地 vLLM 样例 local_qwen-0.5b：base_url localhost:8000 + api_key EMPTY）。
4. 跑通 data_prep.py → 用 example 配置跑 2 个裁判，观察 results/{judge}/trial1..3.json 与断点续跑（删一个 trial 重跑即见）。
5. 精读 run_judge_evaluations（llm_judge_scoring.py:83-289）：trial 循环、o1 补丁、checkpoint 是全部执行语义；再读 generate（litellm_ragas_wrapper.py:69-149）理解"RAGAS 最小接口"。
6. 进阶：修 utils/__init__.py:7 陈旧 __all__；给 notebooks 补分析逻辑。

——本导览由 understand-anything 图谱流水线生成，图谱在仓内 `.understand-anything/knowledge-graph.json`。
