# restgpt 深读卡 —— 把 LLM 接上真实 REST API 的"规划-选接口-执行解析"三段式 Agent

> **定位**：RestGPT 是北大 Song Yifan 等人 2023 年提出的自主 Agent（arXiv 2306.06624），用迭代式 coarse-to-fine 规划让 LLM 通过真实 RESTful API 操控电影数据库（TMDB）与音乐播放器（Spotify）。核心差异化在于不靠预定义工具函数，而是直接消化 OpenAPI 文档、组织 HTTP 参数、并**生成 Python 代码解析 JSON 响应**；随论文发布的 RestBench（人工标注 gold solution path）成为 API-Agent 方向的常用基准。
> **本地**：`repos/restgpt`（Yifan-Song793/RestGPT）｜**深读**：deepwiki 19 子页归档 `deepwiki/restgpt/full.md`（2026-08-21）

## 一、组件栈（DeepWiki 蒸馏）

| 层 | 职责 | 关键实体 |
|---|---|---|
| 编排层 | 主循环：迭代控制、历史管理、终局判断 | `RestGPT(Chain)`（LangChain）、`_should_continue/_should_end`、`max_iterations=15` |
| 规划层 | 生成当前步自然语言子任务（粗粒度） | `Planner`、PLANNER_PROMPT、planner_history |
| 接口选择层 | 子任务 → 具体 API 调用计划（细粒度） | `APISelector`、`ReducedOpenAPISpec` |
| 调用层 | 按 OpenAPI 文档组织参数、发 HTTP 请求 | `Caller`、`RequestsWrapper`、`_get_response` |
| 解析层 | 从 JSON 响应抽取下一步所需信息 | `ResponseParser`（代码生成）、`SimpleResponseParser`（LLM 直读）、`PythonREPL` |
| 场景/规格层 | 外部世界定义 | TMDB（54 API）/ Spotify（40 API）、`datasets/{tmdb,spotify}.json` |
| 评测层 | RestBench 基准 | 人工标注 instruction + gold solution path，`run_tmdb.py`/`run_spotify.py` |

## 二、核心机制

1. **迭代式 coarse-to-fine 在线规划**（来源：System Architecture / Planner）：不一次性展开全计划，而是每轮由 Planner 只产出一个自然语言子任务，API Selector 把它细化成 API 调用计划，执行结果回灌 planner_history 决定下一步——"感知-规划-行动"闭环，天然处理前序调用结果依赖后序参数的链式任务。创新点：把"规划"拆成粗（子任务）细（API 计划）两级，避免 LLM 一步跳到 API 细节时参数幻觉。
2. **Caller 直接消化 OpenAPI 文档组织参数**（来源：Caller / Executor）：不写工具封装，LLM 依据 `ReducedOpenAPISpec` 的端点文档自行确定 HTTP 方法、路径参数、query/body，经 `RequestsWrapper` 发出真实请求；失败可迭代重试（内部同样 `max_iterations=15`）。创新点：对任意 REST API 的"零封装"接入范式——换场景只换 spec 文件。
3. **Parser 用代码生成解析响应 + 三级降级**（来源：Parser / Executor）：优先让 LLM 按响应 schema 写 Python 抽取代码在 `PythonREPL` 中执行；失败则简化 JSON 重试；再失败降级为 `SimpleResponseParser` 让 LLM 直接读响应给自然语言摘要。创新点：用"写代码"替代"逐 token 读长 JSON"，精确过滤大响应、防止上下文爆炸。
4. **RestBench 基准驱动**（来源：Evaluation Framework (RestBench)）：TMDB 100 条 / Spotify 57 条真实指令，人工标注 gold solution path（平均路径长 2.3/2.6），把"Agent 是否选对 API 序列"变成可判定问题——后来的 API-Agent 与 tool-learning 工作常引其设定。

## 三、与讲透系列的对位

| RestGPT 概念 | 讲透Agent/多Agent协作/学习型Agent 对应概念 |
|---|---|
| Planner 每轮"子任务→观察→再规划" | ReAct 循环（Thought/Action/Observation 的 scratchpad 结构同源） |
| API Selector + Caller 按 OpenAPI 组织参数 | 工具调用（从"函数签名"泛化到"API 文档"的工具选择与参数填充） |
| planner_history / scratchpad | 记忆机制（纯短期工作记忆，无长期记忆） |
| Planner→Selector→Executor 固定管线 | 编排模式（pipeline 式硬编排，区别于自由 Agent 循环） |
| PythonREPL 执行生成代码 | 安全沙盒（仅 exec 隔离 globals，弱沙盒——讲透系列可当反面教材对比） |
| 代码解析压缩 API 响应再回灌 | 上下文工程（观察结果的裁剪与结构化回写） |

## 四、关键入口

```python
repos/restgpt/
├── run.py                      # 交互入口：选 scenario + 输入 instruction
├── model/rest_gpt.py:22        # RestGPT(Chain) 主编排：L96-131 迭代控制与 _call 主循环
├── model/planner.py:88         # Planner(Chain)：粗粒度自然语言子任务生成
├── model/api_selector.py:110   # APISelector(Chain)：子任务→API 调用计划
├── model/caller.py:112         # Caller(Chain)：L197 _get_response 组织参数发真实 HTTP
├── model/parser.py:177         # ResponseParser 代码生成解析；:156 PythonREPL；:333 Simple 降级
├── datasets/{tmdb,spotify}.json # Reduced OpenAPI 规格（换场景=换此文件）
└── run_tmdb.py / run_spotify.py # RestBench 评测脚本；init_spotify.py 初始化/清空 Spotify 环境
```

## 五、深读子页地图（19 页精选 5）

1. **System Architecture**——四级组件 + 迭代控制逻辑的完整 mermaid 流程，10 分钟看懂主循环。
2. **Executor**（含 Caller/Parser 思想）——本仓库最精华：代码生成解析与三级降级链路。
3. **Planner**——粗到细规划的 prompt 设计、in-context 示例与 scratchpad 构造。
4. **API Interfaces**——Reduced OpenAPI 规格如何被选择与消费，多步 API 链式调用实例。
5. **Evaluation Framework (RestBench)**——数据集结构、gold path 标注方式与评测跑法。

## 六、与"我们"的关系（一句话）

对学 Agent 的人，这个仓库的独特价值是展示了"不给工具函数、只给 API 文档"时 LLM Agent 的最完整最小实现——三级管线每级都是 LangChain Chain 子类、几百行可通读，是讲透Agent 系列 ReAct/工具调用/上下文工程三个概念的天然真实世界对照样本。

---
生成：2026-08-21 · deepwiki 19 页全归档
