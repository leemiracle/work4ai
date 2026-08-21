# superagi 深读卡 —— 2023 自主 Agent 的"平台化"范本：ReAct 循环装进 FastAPI+Celery 服务栈

> **定位**：SuperAGI 是 2023 年与 AutoGPT/BabyAGI 同期爆火的头部开源自主 Agent 平台（TransformerOptimus 出品，无论文、纯产品驱动），核心差异化是给自主 Agent 一个"可运营的产品外壳"——Next.js Web UI + 工具/模板市场 + 资源管理与多 LLM 接入。相比 AutoGPT 的单进程脚本式全自动，它把 Agent 执行拆成可暂停、可审批、可调度的服务化状态机。
> **本地**：`repos/superagi`（TransformerOptimus/SuperAGI）｜**深读**：deepwiki 25 子页归档 `deepwiki/superagi/full.md`（2026-08-21）

## 一、组件栈（DeepWiki 蒸馏）

| 层 | 职责 | 关键实体 |
|---|---|---|
| Web GUI（Next.js） | Agent 创建/实时监控/审批/市场 | AgentWorkspace、ActivityFeed、ActionConsole、Marketplace |
| API 后端（FastAPI） | 业务 REST 层 | AgentController、AgentExecutionController、ToolController、ModelsController、VectorDBController |
| 异步执行（Celery+Redis） | 后台逐"步"跑 Agent | `execute_agent` Celery 任务自链调度、AgentExecutor |
| 数据层（PostgreSQL/SQLAlchemy） | 配置/执行史/权限持久化 | Agent、AgentExecution、AgentConfiguration、AgentWorkflowStep、Resource |
| Agent 执行引擎 | 推理与工具执行 | 3 个 StepHandler + AgentPromptBuilder + OutputParser |
| 工具系统 | 能力扩展 | BaseTool/BaseToolkit ×20+ 工具包（file/code/email/search/image_gen…） |
| LLM 集成 | 多模型统一接入 | LLMModelFactory → OpenAI/GooglePalm/HuggingFace/Replicate/LocalLLM |
| 资源与知识 | 文件存储 + RAG | FileManager/S3、ResourceSummary → VectorStoreFactory（Pinecone/Qdrant/Weaviate/Redis/Chroma） |

部署形态为 docker-compose 六容器（backend/celery/gui/PostgreSQL/Redis/Nginx），Nginx 按 `/` 与 `/api` 分流。

## 二、核心机制

1. **步骤状态机执行引擎**（来源：Agent Execution、System Architecture）：`AgentExecutor.execute_next_step` 按 `AgentWorkflowStep.action_type` 分派三类 Handler——Iteration 步（组提示→调 LLM→解析）、Tool 步（直接执行工具）、Wait 步（定时/等待）；每步是一个独立 Celery 任务，跑完自链调度下一步。创新点：把 AutoGPT 的 while 循环拆成**可暂停/可恢复/可水平扩展的分布式状态机**（9 种执行状态：CREATED/RUNNING/PAUSED/WAITING_FOR_PERMISSION/ITERATION_LIMIT_EXCEEDED…），并支持带过期时间与次数上限的定时/循环调度。
2. **人在环权限系统（HITL）**（来源：Agent Execution）：工具分 "god mode" 直通与 restricted 两档；restricted 下工具调用前先落库 `AgentExecutionPermission` 记录并置状态为 WAITING_FOR_PERMISSION，前端 Action Console 轮询展示，用户批准/拒绝后才恢复执行——这是它对 AutoGPT"全自动不可控"痛点的直接回应，也是产品化的关键一步。
3. **资源向量化 RAG 管线**（来源：Resource Management、File Storage）：上传文件经 Resource Summarizer 摘要后由 VectorStoreFactory 写入任选向量库，Agent 通过 QueryResourceTool/KnowledgeSearch 语义查询——把 RAG 做成平台一等公民能力而非外挂，文件本体走本地 FILE 或 S3 双通道。
4. **三合一市场生态**（来源：Marketplace、Agent Templates、Model Management）：Agent 模板（goals/instructions/constraints/tools 的序列化）、工具包、LLM 模型均可从 Marketplace 一键安装/发布，配套 GitHub OAuth/JWT 多租户（Organisation→Project→Agent）——复刻"应用商店"打法，是 2023 年 Agent 平台与 CLI 玩家的分水岭。

## 三、与讲透系列的对位

| SuperAGI 概念 | 讲透系列对应概念 |
|---|---|
| Iteration Step + AgentPromptBuilder（思考→选工具→观察，goals/constraints 变量注入） | 讲透Agent · ReAct 循环 + 上下文工程（提示组装） |
| BaseTool/ToolManager + OutputParser（name+description+args schema+execute） | 讲透Agent · 工具调用（文本协议版 function calling） |
| Resource 摘要→向量库→QueryResourceTool | 讲透Agent · 记忆机制（RAG 外置长期记忆） |
| AgentWorkflow Step 状态机 + Celery 逐步调度 | 讲透多Agent协作 · 编排模式（单 Agent 内状态机编排） |
| WAITING_FOR_PERMISSION + Action Console | 安全沙盒 / 人在环审批（HITL） |

## 四、关键入口

```python
superagi/jobs/agent_executor.py               # 执行引擎：按步分派三类 Handler，检查权限/迭代上限
superagi/agent/agent_iteration_step_handler.py # ReAct 心跳：组提示→调 LLM→解析→写 execution feed
superagi/agent/agent_prompt_builder.py        # 提示组装：goals/instructions/constraints/tools 模板变量注入
superagi/agent/output_parser.py               # 把 LLM 文本响应解析为 {name, args, response} 动作
superagi/tools/base_tool.py                   # 工具抽象基类：name/description/args_schema/execute()
superagi/llms/llm_model_factory.py            # LLM 工厂：OpenAI/PaLM/HF/Replicate/LocalLLM 统一接口
superagi/resource_manager/resource_summary.py # 资源摘要+向量化入库（RAG 管线入口）
gui/pages/Content/Agents/AgentWorkspace.js    # 前端主界面：ActivityFeed/ActionConsole/资源管理器三联动
```

## 五、深读子页地图（25 页精选 6）

1. **System Architecture**——11 张图的组件/数据流/权限流全景，30 分钟建立整体心智模型
2. **Agent Execution**——执行生命周期 9 状态 + 权限/调度/等待步细节，核心引擎必读
3. **Tools System**——BaseTool/BaseToolkit 抽象、注册与执行流，写自定义工具的说明书
4. **Resource Management**——FILE/S3 双通道 + 摘要向量化三路管线，看 RAG 如何平台化
5. **LLM Integration**——5 家 Provider + 本地 LLM（GPU 版 compose）接入与模型市场
6. **Docker Deployment**——六容器 compose 拓扑与排障，自托管最快入口

## 六、与"我们"的关系（一句话）

它是"Agent 从实验脚本到可运营平台"的最佳解剖样本——看 ReAct 循环如何被拆成可审批、可调度、可装市场的分布式状态机，这一步正是 2023 年 AutoGPT 系与后来 Agent 平台（及 MCP 生态）之间的分水岭。

---
生成：2026-08-21 · deepwiki 25 页全归档
