# vision-agent 深读卡 —— Landing AI 视觉 Agent：自然语言+图像 → 规划选模 → 生成/测试/调试可执行视觉代码

> **定位**：VisionAgent 是 Landing AI（吴恩达团队）的 Visual AI Pilot：输入 prompt + 图像，自动挑选视觉模型并生成可执行的 Python 视觉分析代码。核心差异化：把 OwlV2/CountGD/Florence2/SAM2/GLEE/Qwen2.5-VL 等 SOTA 视觉模型统一封装为远程托管工具，由"planner→coder→tester→debugger"多角色 LMM 流水线闭环产出经沙盒验证的代码。产品级开源工程（LandingLens 生态），无单独论文。
> **本地**：`repos/vision-agent`（landing-ai/vision-agent）｜**深读**：deepwiki 31 子页归档 `deepwiki/vision-agent/full.md`（2026-08-21）

## 一、组件栈（DeepWiki 蒸馏）

| 层 | 职责 | 关键实体 |
|---|---|---|
| 交互层 | Python API 直用 + Flask/Next.js 聊天界面 | `examples/chat/app.py`, `chat-app/`, `ChatSection`, `PolygonDrawer` |
| Agent 层 | 会话路由与动作决策（生成 vs 编辑代码）、HIL 模式 | `VisionAgentV2`, `AgentMessage`, `InteractionContext`, `ErrorContext` |
| 规划层 | 结构化计划：多试规划 + critic 批判 + 探索代码执行 | `VisionAgentPlannerV2`（planner/summarizer/critic）, `PlanContext` |
| 代码层 | 生成→测试→执行→调试闭环 | `VisionAgentCoderV2`（coder/tester/debugger）, `CodeContext`, `<final_code>` |
| 工具层 | 7 类视觉工具注册表 + embedding 工具推荐 | `TOOLS`, `register_tool`, owlv2/countgd/florence2/sam2/glee/qwen, `Sim` |
| 执行层 | Jupyter kernel 隔离执行与结果结构化 | `CodeInterpreter`, `LocalCodeInterpreter`, `Execution`, `exec_isolation` |
| 模型层 | 多 provider LVLM 统一接口 + 按角色配模型 | `LMM`, `AnthropicLMM`/`GoogleLMM`/`OpenAILMM`/`OllamaLMM`, `Config` |
| 远程推理 | 重模型托管在 Landing AI API，本地零 GPU | `sim/sim.py`, `utils/tools.py`（认证/重试/tracing） |

## 二、核心机制

1. **角色化多 LMM 分工流水线**（System Architecture / VisionAgentPlannerV2）：对话 agent、planner+summarizer+critic（规划）、coder+tester+debugger（代码）共 7 个 LMM 角色位，各自可配不同模型（默认 Claude 3.7 Sonnet + Gemini 2.0 Flash）；规划阶段就在 CodeInterpreter 里跑探索代码"看图取证"，计划建立在对图像的真实观察上，而非纯文本空想——同类 code Agent 少见的"规划即实验"。
2. **embedding 检索工具文档**（VisionAgentCoderV2 / Similarity Search）：不把全量工具塞 prompt，而是对计划每条指令 `Sim.top_k(inst, k=1, thresh=0.3)` 检索最相关工具的 docstring 注入代码生成上下文；工具 embedding 离线缓存于 `.sim_tools/embs.npy`，支持 OpenAI/Azure/Ollama/Stella 四种后端——"RAG 选工具"在视觉领域的工程化落地。
3. **代码+测试+隔离执行+3 轮调试闭环**（VisionAgentCoderV2）：write_code → write_test → `exec_isolation(code+test)` 失败则 debug_code 修复重测（最多 3 轮）；产出 `CodeContext{code, test, success, test_result}`，以 `<final_code>/<final_test>` 标签回传上层 Agent，保证交付代码"跑通过"。
4. **工具即托管推理 + HIL 标注回流**（Remote Tool Execution / Chat Interface）：生成代码中的重模型调用统一走 Landing AI 托管端点（API key 认证、重试、tool call tracing），本地无需 GPU；前端 PolygonDrawer 支持用户画多边形修正分割结果，人类反馈回流 Agent 再生成。

## 三、与讲透系列的对位

| vision-agent 概念 | 讲透系列对应概念 |
|---|---|
| `retrieve_tools` embedding top-k 选工具文档 | 工具调用：RAG 式工具检索 |
| coder→tester→debugger 执行-观察-修复循环 | 讲透Agent：ReAct 循环 |
| 7 个 LMM 角色位各司其职 | 讲透多Agent协作：编排模式（pipeline + 角色专用模型） |
| `exec_isolation` Jupyter kernel 隔离执行 | 安全沙盒 |
| HIL PolygonDrawer 人类标注反馈 | Human-in-the-loop / 讲透学习型Agent：人类反馈 |
| 按需注入工具 docstring + embedding 缓存 | 上下文工程 |

## 四、关键入口

```python
vision_agent/agent/vision_agent_v2.py         # 主入口 VisionAgentV2：会话路由，决定 generate/edit 动作，HIL 模式
vision_agent/agent/vision_agent_coder_v2.py   # 代码引擎：retrieve_tools→write_code→write_test→test_code(3轮debug)
vision_agent/agent/vision_agent_planner_v2.py # 规划器：planner/summarizer/critic 三 LMM，规划期执行探索代码
vision_agent/agent/vision_agent_v3.py         # V3 已在仓库出现（wiki 聚焦 V2），对照读演化方向
vision_agent/tools/tools.py                   # ~2600 行工具库：OD/分割/视频跟踪/OCR/文档/VQA/图像处理全家桶
vision_agent/tools/__init__.py                # register_tool 装饰器 + TOOLS 全局注册表
vision_agent/lmm/lmm.py                       # LMM 抽象 + OpenAI/Azure/Anthropic/Google/Ollama 五 provider
vision_agent/utils/execute.py                 # CodeInterpreter/LocalCodeInterpreter：Jupyter kernel 隔离执行
vision_agent/sim/sim.py                       # Sim 相似度检索：embedding top-k 工具推荐（缓存 embs.npy）
```

## 五、深读子页地图（31 页精选 6）

1. **System Architecture**（L355）— 全局四子系统 + 请求处理时序图，最快建立心智模型
2. **VisionAgentCoderV2**（L1844）— 核心引擎页：生成-测试-调试闭环的源码级拆解与 CODE/TEST/FIX_BUG 三套 prompt 模板
3. **Vision Tools**（L2895）— 全 wiki 最大页（20KB）：7 类工具 × 检测/分割/跟踪组合矩阵与输入输出示例
4. **VisionAgentPlannerV2**（L2244）— 多试规划、critic 批判修正、探索代码执行与安全机制
5. **Code Execution System**（L5126）— exec_isolation、Execution 数据模型与错误恢复工作流
6. **Similarity Search**（L7598）— embedding 工具推荐完整实现：四后端、缓存与注册表集成

## 六、与"我们"的关系（一句话）

它是"自然语言→垂直领域可执行代码"最完整的产品级参考（规划-选工具-写码-测试-调试-沙盒执行全闭环 + 托管推理），学 code Agent 工程化与"embedding 选工具"落地，这一仓是视觉领域的标杆。

---
生成：2026-08-21 · deepwiki 31 页全归档
