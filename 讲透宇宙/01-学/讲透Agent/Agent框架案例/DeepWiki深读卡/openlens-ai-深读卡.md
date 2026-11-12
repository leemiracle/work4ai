# openlens-ai 深读卡 —— LangGraph 五 Agent 端到端自动科研：问题+数据集进，LaTeX 论文出

> **定位**：OpenLens AI 是面向健康信息学（health informatics）的全自动科研 Agent 系统：输入一个研究问题与医学数据集，自动完成文献综述→数据分析→实验编码→LaTeX 论文生成的端到端流水线。基于 LangGraph 编排 5 个专职 Agent，代码执行走 OpenHands Docker 沙盒；主包为 `curie/`（打包名 curie_ai，README 中以 `openlens_ai/` 前缀引用，Curie 系自动科研系统改造痕迹明显——推断）。
> **本地**：`repos/openlens-ai`（jarrycyx/openlens-ai）｜**深读**：deepwiki 28 子页归档 `deepwiki/openlens-ai/full.md`（2026-08-21）

## 一、组件栈（DeepWiki 蒸馏）

| 层 | 职责 | 关键实体 |
|---|---|---|
| 入口/编排 | LangGraph 图构建与条件路由、Web UI | `build_graph.py`、`state.py` SharedState、MemorySaver checkpointer、`start_app.py`(Streamlit) |
| Agent 层 | 5 个专职科研 Agent | SupervisorAgent / LiteratureReviewer / DataAnalyzer / Coder / LaTeXWriter |
| 提示层 | 每 Agent 细分 prompt 模板库 | `supervisor_plan/alter`、`coder(_validator/_concluder/_router)`、latex 十件套（rigor/literature_check/figure_check 等） |
| 工具层 | 文献检索/网搜/代码执行/产物写入 | Search(Read)Arxiv/MedRxivTool、TavilySearch、OpenHandsTool、Plan(Report)WriterTool、LatexWriterTool |
| 质量层 | 多模态质检与检索重排 | GLM-4.1v-9b-thinking（图表/PDF 质评）、bge-reranker-v2-m3 |
| 执行沙盒 | Docker 隔离代码执行 | vendored `modules/OpenHands` 运行时、`agent-med-cpu` 容器、OPENHANDS_MAX_ITER=100 |
| 模型基建 | LLM 路由/部署/压测 | `llm_router/`：LiteLLM proxy(:8077)、`deploy_model_vllm.py`、`api_perf.py` |
| 评估层 | 医学问题集并行评测 | `exp/eval/`：openlens_eval_dataset v1/v2、五维质量打分、parallel_test、断点续传 |

## 二、核心机制

1. **文件产物即检查点的阶段路由**（来源：System Architecture / Multi-Agent System / Experiment Tracking）：Supervisor 先查 `plan.md` 存在与否决定"新建计划 vs 修改计划"，Data Analyzer 查 `data_show.md`，每 Agent 配 `*_router()` 条件边——路由条件不靠自由文本判断而靠磁盘产物存在性，天然支持断点续跑（thread_id + node call stack 完成度分析双保险）。
2. **生成→验证→VLM 质检闭环**（来源：Coder Agent / LaTeX Writer）：Coder 走 coding→validation→VLM 图表质评→concluder；LaTeX Writer 按节顺序生成（abstract_intro→related_works→methods→experiments）后经 `latex_validator` + VLM PDF 质评，再进 rigor/literature_check/figure_check 多维润色环，`MAX_LATEX_POLISH_ROUND=2` 限轮防死循环——用视觉模型做"看图/看版式"的多模态质检，区别于纯文本 validator。
3. **双角色文献 Agent + 防偷懒下限**（来源：Literature Reviewer Agent）：两阶段操作模型 `search_llm`（搜索循环，设最少工具调用次数下限，防止不查就写）与 `write_llm`（成稿）；arXiv/medRxiv 双学术库 + Tavily 兜底 + BGE 重排。
4. **自托管模型基建与评测闭环**（来源：LLM Router Infrastructure / Evaluation Framework）：LiteLLM 多 key 余额校验+负载均衡、vLLM 多 GPU tensor-parallel 部署、api_perf 延迟/吞吐压测；评测侧用医学研究问题集 CSV 并行跑批 + LLM 五维打分（结果落 CSV）——科研 Agent 自带"模型运维+回归评测"全套，工程完整度高。

## 三、与讲透系列的对位

| openlens-ai 概念 | 讲透系列对应概念 |
|---|---|
| SharedState TypedDict + `*_router()` 条件边 | 讲透Agent：ReAct 循环 / LangGraph 编排模式 |
| OpenHandsTool → Docker `agent-med-cpu` | 讲透Agent：安全沙盒 |
| plan.md / literature_report / data_report 落盘产物 | 讲透Agent：记忆机制（外部文件记忆/产物记忆） |
| Supervisor 规划 + 4 个执行者分工 | 讲透多Agent协作：Supervisor 编排模式 |
| VLM 质评 + latex polish 限轮循环 | 讲透学习型Agent：反思-自我改进循环 |
| search_llm/write_llm 分角色 + 模板库 | 上下文工程（按角色切分 prompt） |

## 四、关键入口

```python
curie/build_graph.py          # LangGraph 主入口：--question --dataset-path --thread-id 三参数起跑
curie/state.py                # SharedState TypedDict：research_question/current_subtask/messages/各阶段报告
curie/agents/supervisor.py    # SupervisorAgent：研究计划生成与 Agent 间协调（plan.md 读写字检查）
curie/agents/coder.py         # CoderAgent：实验编码→OpenHands 执行→VLM 验证→结论生成
curie/agents/latex_writer.py  # LaTeXWriterAgent：按节写作 + 质量润色循环（含 VLM PDF 质评）
curie/tools/                  # OpenHandsTool、Search/ReadArxiv(MedRxiv)Tool、TavilySearch、Plan/ReportWriterTool
llm_router/create_yaml.py     # LiteLLM 配置生成：多 key 余额校验 + 负载均衡
exp/eval/parallel_test.py     # 医学问题集并行评测 + 五维质量打分 + 断点续传
# 注：README 源码引用前缀为 openlens_ai/，仓库主包目录名为 curie/，同库两称
```

## 五、深读子页地图（28 页精选 6）

1. **Multi-Agent System**（P6）——五 Agent 全景执行流图 + 全部 prompt 模板清单，信息密度最高，先读这页
2. **System Architecture**（P2）——SharedState schema、阶段路由表、外部服务依赖全景
3. **Coder Agent**（P10）——"生成→沙盒执行→VLM 质评"闭环的标准范本
4. **LaTeX Writer Agent**（P11）——按节生成 + 多维润色的论文流水线设计（配 P8 文献 Agent 两阶段模型）
5. **LLM Router Infrastructure**（P12-15）——LiteLLM/vLLM 自托管模型路由、部署与压测三连页
6. **Evaluation Datasets**（P17）——医学研究问题集的难度/类型分层设计（v1→v2 演进）

## 六、与"我们"的关系（一句话）

对学 Agent 的人，这是把 LangGraph 编排、安全沙盒、外部文件记忆、VLM 质检、模型路由、回归评测垂直组装成"端到端 AI Scientist"的生产级全栈样例——讲透系列核心概念的一次总装演习。

---
生成：2026-08-21 · deepwiki 28 页全归档
