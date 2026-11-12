# ViMax ONBOARDING — 智能体驱动的端到端视频创作框架

> 图谱基线：509 节点 / 1058 边 / 14 层 / 16 步 tour @ commit fd4b72e7；行号锚均从源码核实（2026-11）。

## 1. 这是什么系统

ViMax 是 HKUDS（港大数据智能实验室，LightRAG 同门）开源的**智能体驱动的端到端视频创作框架**（readme.md:22 挂 arXiv 技术报告 2606.07649，当前 v1.2.0）。一句话定位：自研 agent 循环（Python）编排三条管线——Idea2Video / Script2Video / Novel2Video，把创意、剧本或长篇小说经「叙事规划→角色立绘→分镜→相机树→关键帧→镜头视频→拼接」变成成片；配 Ink 终端 TUI 与 Web 控制台双前端，渲染矩阵可插拔 Google 官方 SDK（Nano Banana/Veo）与 yunwu、OpenRouter、豆包 Seedance 等网关。仓内另带 35 任务一致性基准（12 Type A 单主体跨场景+12 Type B 固定场所+11 Type C 多主体交互，vimax_benchmark/benchmark_index.json 实测）作为成色标尺。

## 2. 总体架构：14 层堆栈

| # | 层 | 职责 | 代表文件 |
|---|---|---|---|
| 1 | 入口与 CLI 分发 | bash 分发器 + 无头 agent CLI + 两管线示例入口 | vimax、main_agent.py |
| 2 | Agent 运行时核心 | 50 轮循环、13 内置工具、压缩、提示词、会话、LLM 客户端 | agent_runtime/loop.py |
| 3 | 视频生成管线 | script2video 渲染枢纽 + idea/novel 两前置管线 | pipelines/script2video_pipeline.py |
| 4 | 叙事创作 Agent 群 | 14 个单职责 LLM/生成 agent | agents/screenwriter.py 等 |
| 5 | 渲染数据契约 | Pydantic 数据词汇表（三粒度 Character、双密度 Shot） | interfaces/__init__.py |
| 6 | 渲染后端与生成器 | 工厂动态加载 4 图像 + 6 视频生成器 | tools/render_backend.py |
| 7 | 通用基础设施 | 双窗口限流、重试分类、容错 JSON 解析 | utils/rate_limiter.py |
| 8 | TUI 终端前端 | Ink/React，spawn 引擎并归约 JSONL 事件流 | ui/src/cli.tsx |
| 9 | Web 桥接服务 | 零依赖 node:http 手写 API + SSE | web/server.mjs |
| 10 | Web 浏览器前端 | Vite + React 单页控制台 | web/src/App.tsx |
| 11 | 一致性基准数据 | 35 任务逐 shot 双提示 | vimax_benchmark/ |
| 12 | 测试保障 | 26 个单测文件锁定运行时行为 | tests/test_agent_loop.py |
| 13 | 配置体系 | 5 个 YAML + pyproject | configs/agent.example.yaml |
| 14 | 文档与提示词契约 | 双语 README + 运行时装配的人格/工作流提示词 | prompts/agent.md、prompts/workflow.md |

架构叙事主线是「一个引擎、两个壳、一组可插拔渲染后端」：Python 引擎（层 2-7）承载全部智能，TUI 与 Web（层 8-10）只是事件流的两种归约视图，渲染能力（层 6）由 YAML 声明式装配。

## 3. 核心数据流：从 vimax CLI 到视频产出

以 `vimax tui` 发起一次 idea→视频为例：

1. **入口分发**：vimax bash 脚本自解析符号链接定位仓库根，tui 分支 exec `ui/node_modules/.bin/tsx ui/src/cli.tsx`（vimax:102），web 分支 exec npm dev/start（vimax:53,55）。
2. **引擎拉起**：cli.tsx 经环境变量链（VIMAX_AGENT_COMMAND→VIMAX_PYTHON_CMD→VIMAX_UV_CMD→.venv/uv，ui/src/cli.tsx:114-121）spawn `main_agent.py --jsonl --stdin-repl`（main_agent.py:24,26）。
3. **循环运转**：AgentLoop 驱动「采样 assistant→执行工具→回填消息」多轮循环，上限 MAX_TOOL_PASSES=50（agent_runtime/loop.py:17）；采样前 token 预检压缩历史，事件以 JSONL 逐行打印 stdout。
4. **管线调用**：agent 调 `vimax_narrative_planning`（agent_runtime/vimax_adapters.py:49）→ Idea2VideoPipeline：扩写故事→抽角色→三视图立绘→改剧本，再委托 Script2VideoPipeline 做分镜、相机树、关键帧多候选举优与镜头视频。
5. **渲染落地**：生成器对由 RenderBackend 从 YAML class_path 经 importlib 动态实例化（tools/render_backend.py:57-58），双窗口限流节流，产物落 .working_dir/<session>/ 支持断点续跑。
6. **回流展示**：渲染拼接经 `vimax_render_video`（vimax_adapters.py:85）执行，进度事件回流 TUI/Web——lineMapping.ts 与 web/src/events.ts 各自归约为界面行/聊天消息，成片出现在产物面板。

## 4. 关键子系统深读

**agent_runtime（引擎心脏）**：tools.py:391-403 装配恰好 13 个内置工具（读/写/glob/搜索/记忆/todo/view_image/sleep/run_shell 等），其中 run_shell 默认禁用、需 VIMAX_ENABLE_RUN_SHELL=1 且带危险命令黑名单（tools.py:403）；context_compactor.py 定义 SUMMARY_SECTIONS（:11）与 should_preflight_compact（:74），LLM 摘要失败降级本地启发式；session_index.py 以 fcntl.flock 排他锁（:61,65）、损坏先备份（:78）、临时文件 os.replace 原子写（:87）保护 .vimax/sessions.json；llm.py 对字符串/字典/Pydantic 多形状响应宽容解析，429/5xx 有界重试。

**pipelines（渲染枢纽）**：script2video_pipeline.py 是全仓最重的文件——角色/分镜/镜头分解/相机树规划加 15 个异步渲染方法，是 idea 与 novel 两条管线的共同终点；novel2movie_pipeline.py 两阶段（plan_text_artifacts 压缩→事件抽取→FAISS RAG 场景改写→全局角色合并，render_video_artifacts 委托渲染）。

**tools 生成器（可插拔矩阵）**：protocols.py 用 runtime_checkable Protocol 定义 ImageGenerator（:15）与 VideoGenerator（:27）鸭子类型契约，生成器无需继承；test_generator_protocol.py 用 inspect.signature 强制所有视频生成器接受 **kwargs（流水线要传 progress 回调）。

**web 桥**：server.mjs 以密集 if 链手写 13 个 /api/ 路由分支（web/server.mjs:36-108，覆盖会话/配置/历史/产物/上传/agent 启停/SSE/健康检查），--dev 挂 Vite 中间件；config-store.mjs 读写 YAML 且 API key 永不回传（仅 has_api_key 布尔）。

## 5. 设计决策与取舍

- **TS→Python 跨语言桥选 spawn+JSONL 而非 HTTP/RPC**：两个前端复用同一个无头 CLI，进程边界即协议边界，零额外服务进程；代价是事件流单向、交互靠 stdin 注入。web/test/fake-agent.mjs 替身让前端脱离 Python 独立开发，是此决策的红利。
- **YAML class_path 动态加载**（render_backend.py:57-58）：新增供应商只需写一个类+改一行配置，工厂自动按 RPM/RPD 装配限流器；代价是类名拼错要到运行时才爆。
- **PEP 562 惰性导出**（agent_runtime/__init__.py:12 模块级 __getattr__）：避免 import 包即拉起 langchain/faiss 等重依赖。
- **双前端共享一套事件协议、各自纯函数归约层**（lineMapping.ts / events.ts 均有单测）：视图层完全不掺业务。
- **一切落盘**：产物、会话、轮次、tool_calls 遥测全部持久化，长渲染任务崩了可续跑——对分钟级外部调用链是生存必需。

## 6. 已知问题与坑

- **ScriptEnhancer 是死代码候选**：agents/script_enhancer.py:74 定义 class ScriptEnhancer，全仓 grep 唯一引用就是它自己——不在 agents/__init__.py 导出（该 barrel 仅 6 个导出）、无任何 pipeline/test 消费。读架构时请跳过它。ScriptPlanner 也仅被 tests/test_robustness.py 引用，无生产消费方。
- **shadowing 死 import 群**：8 个 agent 文件写 `from utils.robust_json_parser import TrailingCommaTolerantPydanticOutputParser as PydanticOutputParser`（agents/screenwriter.py:5、agents/character_extractor.py:4、agents/event_extractor.py:7 等）——IDE 跳转会把你带到 LangChain 的同名类，实际用的是本地尾随逗号容错版；改动解析行为时别改错文件。
- **example 配置陷阱**：configs/agent.example.yaml 必须复制为 configs/agent.local.yaml 才会被 agent_runtime/config.py 读取，环境变量（VIMAX_LLM_API_KEY 等）优先于文件值；忘记复制是「跑不起来」的头号原因。
- **README_ZH 滞后**：中文版动态段只有 2 条（README_ZH.md:50-51），英文 News 有 7 条历史（readme.md:56-62）——查版本演进以英文版为准。
- **命名分裂**：pyproject.toml:2 发行名是 autolongvideogeneration（v1.2.0，:3），与仓名 ViMax 不一致；pip 装到的包名容易让人迷惑。另要求 Python>=3.12（:6）。
- **run_shell 默认禁用**：不是 bug，是安全默认；需要时显式设 VIMAX_ENABLE_RUN_SHELL=1。

## 7. 新人上手路径（对应 tour 前 6 步）

1. **读双语 README 建立全景**（step-1）：先英文 readme.md 的特性矩阵与 News 时间线，再看四大引擎定位。
2. **跑通进程拓扑**（step-2）：读 vimax 分发器与 main_agent.py 参数区（:24-26），理解「TS 壳 spawn Python 引擎」；`vimax tui` 实际起一次会话。
3. **啃主循环**（step-3）：agent_runtime/loop.py 从 MAX_TOOL_PASSES=50（:17）往下读，build_runtime 是装配总入口。
4. **看 agent 的手**（step-4）：tools.py:391-403 的 13 个 ToolSpec 一屏读完，再看 tool_executor 的校验与遥测。
5. **看 agent 的记忆**（step-5）：context_compactor（预检压缩+降级摘要）、prompts.py（六段装配）、session_index.py（文件锁+原子写）三件套。
6. **配模型端点**（step-6）：cp configs/agent.example.yaml 为 agent.local.yaml，填 llm/image/video 三节；回头跑 main_idea2video.py 走一遍无前端管线。

之后按 tour step 7-16 依次进入管线、数据契约、agent 群、生成器与基准。

## 8. 与 HKUDS 家族的关系

本仓所在的 HKUDS org 本地集群有 20+ 仓，ViMax 是家族中罕见的**生成侧**成员：

- **LightRAG**（"Simple and Fast Retrieval-Augmented Generation"，README.md:7）：图知识表示 + 多模式检索的 RAG 框架，家族的检索基座。
- **RAG-Anything**（"All-in-One RAG Framework"，README.md:7；:72 自述 built on LightRAG 的多模态文档 RAG，arXiv 2510.12323）：把检索扩到文本/图像/表格/公式全模态。
- **CLI-Anything**（README 口号 "Tomorrow's Users will be Agents"）：为 agent 用户重设计终端工具的 ACI 尝试。
- **VideoAgent / VideoRAG**：视频理解侧，与 ViMax 的创作生成侧互补。

对照定位：LightRAG 系回答「如何从已有知识里找」，ViMax 回答「如何从无到有造」——但复用了同样的工程范式：自研 agent 循环 + 可插拔后端 + 断点续跑。值得注意的是 novel2movie 管线只内嵌了 FAISS+CacheBackedEmbeddings 的轻量检索，并未复用 LightRAG——这是「单仓自治、依赖最小」对「复用家族基建」的明确取舍。而 agent_runtime 的工具循环形态（文件读写/搜索/记忆/todo 内置工具 + 适配器扩展）与 CLI-Anything 的 agent 优先理念同源，可视为家族内 agent 工程范式的延续。
