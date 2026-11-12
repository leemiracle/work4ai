# deepanalyze 深读卡 —— 人大高瓴自主数据分析 Agent：把 ReAct 循环训进 8B 权重而非编排层

> **定位**：人大 RUC-DataLab 出品的自主数据分析 Agent 系统（self-evolving 框架，论文《DeepAnalyze: Autonomous Data Science》arXiv:2510.16872）。核心差异化：不靠通用 LLM + prompt 编排，而是从 DeepSeek-R1-0528-Qwen3-8B 训出专用 DeepAnalyze-8B——Action Tag 协议作为特殊 token 内化进词表，经"单技能 SFT → 多技能冷启动 → RL"三阶段课程训练；模型、500K 数据集、训练与服务代码全开源。
> **本地**：`repos/deepanalyze`（ruc-datalab/DeepAnalyze）｜**深读**：deepwiki 50 子页归档 `deepwiki/deepanalyze/full.md`（2026-08-21）

## 一、组件栈（DeepWiki 蒸馏）

| 层 | 职责 | 关键实体 |
|---|---|---|
| 模型层 | DeepAnalyze-8B（vLLM :8000 服务，4/8bit 量化可跑 16GB 卡） | `add_vocab.py`、`quantize.py`、stop_token_ids |
| API 层 | FastAPI OpenAI 兼容服务 :8200，chat/files/models/threads/admin 五路由 | `API/main.py`、`chat_api.py`、`models.py`(Pydantic) |
| 执行沙盒 | `<Code>` 子进程执行：cwd=thread 工作区、120s 超时、无头 matplotlib | `execute_code_safe_async()`、`Chinese_matplot_str` |
| 工作区/状态 | thread-{uuid} 目录隔离，上传件拷入、产物落 `generated/`、跨轮持久 | `storage.py`(InMemoryStore)、`WorkspaceTracker` |
| 文件服务 | HTTP 文件服务器 :8100，下载 URL 以 `<File>` 注入响应 | `render_file_block()`、`build_download_url()` |
| 前端层 | 5 种界面：WebUI(React :4000)/CLI/JupyterUI(MCP)/Gradio/Python SDK | `demo/*`、`DeepAnalyzeVLLM`（SDK 绕过 API 直连 vLLM） |
| 训练层 | 三阶段课程：单技能 SFT → 多技能冷启动 → RL | ms-swift、SkyRL、`scripts/*.sh`、DataScience-Instruct-500K |

## 二、核心机制

1. **Action Tag 协议训进词表（创新本质）**（来源：Training Pipeline / Action Tags Reference）：同类框架用 system prompt 约定输出格式，DeepAnalyze 则由 `add_vocab.py` 把 `<Analyze>/<Understand>/<Code>/<Execute>/<Answer>/<File>` 添加为特殊 token 再训练，协议遵守靠权重保证——每轮恰好输出一个动作标签，vLLM 以 tag 边界 stop_token_ids 截断，`<Execute>/<File>` 只由系统生成、模型永不输出。
2. **服务器端感知-行动循环**（来源：Code Execution and Agentic Loop）：流式累积响应 → 检测 `<Code>` → 正则抽取（兼容 markdown fence）→ 注入中文字体配置 → asyncio 子进程执行（`MPLBACKEND=Agg`、去 DISPLAY、120s 超时 kill）→ stdout/stderr 以 `role:"execute"` 回注消息数组续流，直到 `</Answer>` 终止；未闭合 `<Code>` 自动补全，`[Timeout]/[Error]` 文本回注供模型自我修正——一条实现于 API 层的完整 ReAct 循环。
3. **文件系统 diff 作为"眼睛"**（来源：Workspace and File Tracking / Action Tags Reference）：`WorkspaceTracker` 在每次执行前后对工作区做 stat 快照（size + mtime_ns），diff 出新增/修改文件移入 `generated/` 并生成 `<File>` markdown 块（图片自动内嵌预览、附 :8100 下载链接）——把 ReAct 的观察空间从 stdout 扩展到文件系统副作用，产物自动进入下一轮上下文。
4. **self-evolving = 训练出来的自主性**（来源：Training Pipeline）：500K 数据集分 SFT portion（数据清洗/EDA/建模/可视化/报告）与 RL portion（奖励=任务完成、代码执行成功、产物质量、多步推理连贯）；Stage3 用 SkyRL 做策略优化，让模型学会探索-试错-自纠，而非仅模仿示范——大多数 agent 仓库止步编排层，这里把 agentic 能力下沉到了模型权重。

## 三、与讲透系列的对位

| DeepAnalyze 概念 | 讲透系列对应概念 |
|---|---|
| `<Analyze>→<Code>→<Execute>` 循环直至 `</Answer>` | 讲透Agent：ReAct 循环（推理+行动+观察，终止条件显式化） |
| `role:"execute"` 结果回注 messages | 讲透Agent：工具调用结果注入 / 上下文工程（观察写入消息流） |
| thread-{uuid} 工作区跨轮持久 + InMemoryStore | 讲透Agent：记忆机制（工作区即外部状态记忆，thread 即会话） |
| 子进程 + cwd 隔离 + 超时 + 无头环境 | 讲透Agent：安全沙盒（进程级隔离，弱于容器/e2b，胜在轻量） |
| 三阶段课程 SFT→冷启动→RL | 讲透学习型Agent：自进化（进化发生在权重而非编排层） |

## 四、关键入口

```python
API/chat_api.py             # agentic 循环核心：generate_stream_with_execution() + 终止规则表
API/utils.py                # extract_code_from_segment / execute_code_safe_async / WorkspaceTracker / 报告生成
API/storage.py              # thread 生命周期：建区/拷文件/generated/ 收集/过期清理
deepanalyze/add_vocab.py    # 向 DeepSeek-R1-0528-Qwen3-8B 词表添加 Action Tag 特殊 token
scripts/single.sh           # Stage1 单技能 SFT（ms-swift + LoRA）
scripts/multi_coldstart.sh  # Stage2 多技能冷启动联合 SFT
scripts/multi_rl.sh         # Stage3 RL 优化（SkyRL，产出 DeepAnalyze-8B）
demo/deepanalyze_general/deepanalyze_general.py  # Python SDK DeepAnalyzeVLLM：绕过 API 直连 vLLM
```

## 五、深读子页地图（50 页精选 6）

1. **25 Code Execution and Agentic Loop** — 循环全景：代码抽取、沙盒配置、终止规则表、流式/非流式双实现
2. **49 Action Tags Reference** — 7 种标签完整规范、状态机、检测正则、各前端渲染差异
3. **5 Training Pipeline** — 三阶段课程训练与 ms-swift/SkyRL 逐阶段复现路径
4. **6 DataScience-Instruct-500K Dataset** — SFT/RL 双 portion 数据构造与奖励信号设计
5. **26 Workspace and File Tracking** — 文件系统 diff 感知与产物收集的算法细节
6. **40 Simpson's Paradox Analysis** — 35KB 完整案例：多轮迭代自我调试 vs 其他 LLM 的失败模式对比

## 六、与"我们"的关系（一句话）

它是"把 Agent 能力训进模型权重"这条路线少有的全链开源样本（模型+数据+训练+服务一体），与讲透系列讲的编排层框架恰好互补——补上"模型层如何学会当 Agent"的另一半拼图。

---
生成：2026-08-21 · deepwiki 50 页全归档
