# data-to-paper 深读卡 —— 从原始数据自主产出可追溯科研论文的 Agent 流水线

> **定位**：多 Agent 端到端驱动完整科研流程（数据探索→文献→假设→分析→图表→论文→PDF），产出"每个数字都能回溯到产生它的代码行"的 backward-traceable 论文。Technion Kishony lab 出品、有配套方法论文，与 AI-Scientist 同属"AI 科学家"赛道但独锚定**科学可复现性（grounded chain of evidence）**。支持 autopilot 全自动 / copilot 人工引导双模式。
> **本地**：`repos/data-to-paper`（Technion-Kishony-lab/data-to-paper）｜**深读**：deepwiki 23 子页归档 `deepwiki/data-to-paper/full.md`（2026-08-21）

## 一、组件栈（DeepWiki 蒸馏）

| 层 | 职责 | 关键实体 |
|---|---|---|
| 科研编排层 | 假设检验型研究工作流（探索→假设→分析→写作→PDF） | `steps_runner`、`hypothesis_testing/coding/`、`writing_steps` |
| 会话层 | 多 LLM 会话管理与结构化输出提取 | `ConversationManager`、`ConversationAction`、`ResetToTag` |
| 代码执行层 | AI 生成代码的沙盒执行与调试闭环 | `CodeRunner`、`DebuggerConverser`、`MultiRunContext`/`RunIssue` |
| 统计护栏层 | 运行时拦截 statsmodels/scipy/sklearn 防统计谬误 | `OverrideStatisticsPackages`、`SetRandomSeeds`、`PValue` |
| 数据层 | DataFrame 追踪、校验、溯源元数据 | `InfoDataFrame`、`TrackDataFrames`、`check_analysis_df` |
| 文档生成层 | 表/图→LaTeX→PDF 编译与引文管理 | `LatexDocument`、`df_to_latex/figure`、Crossref 引文 |
| 人机交互层 | copilot 模式的研究者监督 GUI | `PysideApp`、Panel 系统 |

## 二、核心机制

1. **证据链接地（grounded chain of evidence）**〔Overview / Architecture Overview〕：差异化核心——论文正文里每个数值都经 `PValue` 对象与 DataFrame 溯源元数据绑定到具体代码行，形成"假设→代码→数值→文本"闭环；不同于一般写作 Agent 的整段自由生成，幻觉数字在机制上无处遁形。
2. **统计包运行时 override**〔Code Execution System / Statistical Package Overrides〕：护栏不打在 prompt 层而打在 Python 运行时——上下文管理器拦截统计库：p-value 自动打标防编造、禁止对同一模型重复 `fit()`、限制 sklearn 搜索迭代次数、强制随机种子保复现。比"提示 LLM 别 p-hacking"硬一个数量级，是同类框架罕见的机制级反学术不端设计。
3. **DebuggerConverser 调试闭环**〔Debugging System〕：执行失败→`RunIssue` 分类（语法/执行/运行时问题 + forgive 宽恕机制计数）→错误回喂 LLM 改代码→重执行，直到成功或超时；沙盒同时禁危险函数/模块、白名单写文件、`OutputFileRequirements` 校验产物格式。
4. **会话回卷 + 强类型提取**〔Conversation Management / Data Type Extraction〕：LLM 输出一律走 PythonValue/LaTeX/QuotedText/MultipleChoice 严格提取；提取失败用 `ResetToTag` 回卷会话重试并可换更强模型，`InfoDataFrame` 侧还强制"改过的 DataFrame 必须落盘"。

## 三、与讲透系列的对位

| 该框架概念 | 讲透系列对应概念 |
|---|---|
| CodeRunner 沙盒（禁函数/禁导入/文件白名单/超时） | 讲透Agent · 安全沙盒 |
| DebuggerConverser 执行→报错→改码循环 | 讲透Agent · ReAct 循环（观察错误→行动→再观察） |
| steps_runner 探索→假设→分析→写作流水线 | 讲透多Agent协作 · 流水线式编排模式 |
| ResetToTag 会话回卷 + 结构化提取契约 | 讲透Agent · 上下文工程（上下文回滚/输出 schema） |
| OverrideStatisticsPackages 运行时拦截 | 讲透Agent · 工具调用护栏（机制级校验优于提示级约束） |
| InfoDataFrame 溯源元数据 | 讲透Agent · 记忆机制（审计轨迹/来源追踪） |

## 四、关键入口

```python
src/data_to_paper/run_gpt_code/code_runner.py            # CodeRunner：沙盒核心（禁用函数/导入、写文件白名单、超时）
src/data_to_paper/run_gpt_code/overrides/contexts.py     # OverrideStatisticsPackages：全套统计护栏入口
src/data_to_paper/run_gpt_code/overrides/pvalue.py       # PValue 对象：证据链接地载体（数值↔代码行绑定）
src/data_to_paper/research_types/hypothesis_testing/steps_runner.py  # 科研主流程编排（各阶段 agent 装配）
src/data_to_paper/research_types/hypothesis_testing/coding/          # 各阶段 coding agent：exploration/preprocessing/analysis/displayitems
src/data_to_paper/conversation/conversation_manager.py   # ConversationManager：会话创建/追加/回卷（ResetToTag）
src/data_to_paper/base_steps/result_converser.py         # Converser 基类：LLM 请求→提取→校验→重试循环
src/data_to_paper/latex/latex_doc.py                     # LatexDocument：LaTeX 组装、PDF 编译、可追溯表格/图
```

## 五、深读子页地图（23 页精选 6）

1. **Architecture Overview**（L674）—— 六系统全景 + 数据/控制流时序图，最佳切入页
2. **Code Execution System**（L1059）—— CodeRunner 安全机制与调试闭环细节
3. **Statistical Package Overrides**（L1997）—— p-value 打标与反 p-hacking 护栏深读（核心创新所在）
4. **DataFrame Tracking**（L2281）—— DataFrame 修改追踪/强制落盘/防原地篡改
5. **Conversation Management**（L5187）—— ConversationAction 设计与会话回卷
6. **Data Type Extraction**（L5544）—— 四类强类型提取、失败重试与模型升级策略

## 六、与"我们"的关系（一句话）

它示范了"不靠提示词、靠运行时 override + 溯源对象把 LLM 钉死在事实上"的完整工程范式——这套 grounded 证据链技术可直接迁移到任何要求高可信产出的 Agent 场景（报表、法律、科研辅助）。

---
生成：2026-08-21 · deepwiki 23 页全归档
