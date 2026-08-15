# 分册 D · 训练 / 多模态 / 语音 / 教育（11 仓深读）

> 深读材料：README（前 300 行）+ 关键源文件（≤350 行）+ 代码树指标。行号证据限于已读片段。

### hiyouga/LlamaFactory
- **架构模式**：零代码一体化 LLM 微调工厂——CLI/WebUI/OPEN API 三入口共用一套 YAML 驱动的训练引擎。
- **核心抽象**：`ChatModel`（src/llamafactory/api/app.py:21）、`launcher`（src/llamafactory/cli.py:19-24）、`EngineName` 引擎抽象（app.py:22，HF/vLLM/SGLang 可换后端）。
- **关键机制**：
  - CLI 分流 V0/V1 双实现：`USE_V1` 环境变量选择 launcher（cli.py:19-24）。
  - OpenAI 兼容 API 层：`/v1/chat/completions` 同步/SSE 流式双路径（app.py:96-110）。
  - 生成/评分双用途端点互斥校验 `engine.can_generate`（app.py:103、119）。
  - GPU 显存回收后台协程 `sweeper` 每 300s `torch_gc()`（app.py:54-66）。
  - 方法覆盖广：SFT/PPO/DPO/KTO/ORPO + LoRA~8bit QLoRA（README:106-108）。
- **工程亮点**：Day-0/Day-1 新模型适配节奏（README:114-120）；一套 API 同时服务训练产物评测与部署。
- **教学映射**：讲透PyTorch、讲透Transformer（微调实践侧）、讲透RL（PPO/DPO 对比）。
- **一句话本质**：把"选模型-选方法-配资源-训-部署"压缩成一条 YAML 命令，让非框架工程师一天内完成百款模型微调。

### unslothai/unsloth
- **架构模式**：本地"跑+训+部署"桌面级训练平台——Tauri Desktop + FastAPI Studio 后端 + 核心加速库三层。
- **核心抽象**：`studio/backend/main.py` 的 app 工厂（main.py:284-310 挂载 20+ router）、硬件检测层 `utils.hardware`（main.py:331-337）、torch 预热器 `torch_warmup`（main.py:339-345）。
- **关键机制**：
  - Windows AMD ROCm DLL 注入：`os.add_dll_directory()` 在 torch import 前注册（main.py:44-86）。
  - bitsandbytes ROCm 版本嗅探：glob `libbitsandbytes_rocm*.dll` 反推 `BNB_ROCM_VERSION`（main.py:102-148）。
  - WSL Strix Halo 经 `/dev/dxg` 检测启用 `HSA_ENABLE_DXG_DETECTION`（main.py:157-174）。
  - 安装指纹 `studio_install_id`（64-hex）做健康检查同源判别（main.py:243-271）。
  - `unsloth start claude` 把本地模型挂给 Claude Code/Codex 当 subagent（README:94-117）。
- **工程亮点**：跨平台 GPU 兼容矩阵（CUDA/ROCm/Vulkan/Metal）几乎全用启动期环境探测硬啃下来。
- **教学映射**：讲透PyTorch（显存/内核优化视角）、讲透学习型Agent（本地模型驱动 coding agent）。
- **一句话本质**：用重写的 Triton 内核把消费级显卡上的微调速度翻倍、显存降 70%，并把这条加速通路包装成小白可装的桌面应用。

### Comfy-Org/ComfyUI
- **架构模式**：节点图执行引擎——前端画布只产 DAG JSON，后端做拓扑执行+显存调度。
- **核心抽象**：`folder_paths` 模型目录注册表（main.py:128-158）、`PromptQueue/prompt_worker` 异步执行循环（main.py:339-350）、`SubgraphManager`（server.py:56）。
- **关键机制**：
  - 动态显存 comfy-aimdo：按 headroom 初始化并切换 `ModelPatcherDynamic`（main.py:60-70、261-292）。
  - 自定义节点 prestartup_script 隔离执行+耗时统计（main.py:171-217）。
  - torch 禁止早导入守护：main.py:233-234 显式警告。
  - LRU/RAM 双层模型缓存按 total_ram 10% 自适应（main.py:343-350）。
  - aiohttp 中间件链：CORS/gzip/弃用路径告警（server.py:83-121）。
- **工程亮点**：图级"部分重执行"——只重算变更节点，配合智能 offload 让 8GB 卡跑通大流。
- **教学映射**：讲透CV、讲透多模态（图/视频/3D/音频统一为节点）、讲透群体智能（节点协作隐喻）。
- **一句话本质**：把扩散模型推理拆成可组合的数据流图，让复杂多模型管线变成可保存、可复现、可商品化的工作流资产。

### AUTOMATIC1111/stable-diffusion-webui
- **架构模式**：单体 Gradio WebUI——modules/ 下 154 个 Python 文件按功能切分（txt2img/img2img/extras），无图层抽象。
- **核心抽象**：`modules` 包（tree-metrics：modules[154]）、extensions-builtin 插件目录（43 项）、"tab"概念（txt2img/img2img/Extras/PNG Info）。
- **关键机制**：
  - 生成参数随图落盘（PNG chunks/EXIF），拖图即复参（README:41-46）。
  - Attention 语法 `(tuxedo:1.21)` 进 prompt 权重（README:15-18）。
  - 4GB 显存可用+低显存实时预览网络（README:38、53-54）。
  - 一键 bat/sh 安装器锁定 Python 3.10.6（README:113-117）。
- **工程亮点**：以"功能清单即产品"的方式定义了 SD 时代桌面出图工具的事实标准（X/Y/Z plot、Highres fix 等皆出自此处）。
- **教学映射**：讲透CV（扩散模型应用侧）、讲透多模态（文图条件生成）。
- **一句话本质**：把论文级 Stable Diffusion 变成 Windows 用户双击 bat 就能跑的作图工具，是 AIGC 大众化的起点。

### hacksider/Deep-Live-Cam
- **架构模式**：极简启动器 + modules 单体管线——run.py 只管环境修复，core.run() 承载一切。
- **核心抽象**：`modules.core.run()`（run.py:95-98）、`platform_info`（run.py:92-93）、modules/ 31 个文件的 swap 管线。
- **关键机制**：
  - Windows CUDA DLL 目录注册使 onnxruntime-gpu 找到 cuDNN/cublas（run.py:12-31）。
  - OpenVINO provider 容错降级 CPU（run.py:37-55）。
  - Linux 侧 `ctypes.CDLL(RTLD_GLOBAL)` 预载 pip wheel 里的 NVIDIA .so（run.py:62-90）。
  - 内置 NSFW/敏感内容检查门（README:19-23）。
  - "3 clicks"交互：选脸→选摄像头→直播（README:67-71）。
- **工程亮点**：跨 OS 原生库加载的启动期修补写法可作系统课范例。
- **教学映射**：讲透CV（人脸检测/对齐/换脸三段式）、讲透多模态。
- **一句话本质**：把 InsightFace+GFPGAN 等三个模型串成单图即可启动的实时摄像头换脸工具。

### facefusion/facefusion
- **架构模式**：CLI 驱动的作业编排平台——命令即产品，全部能力暴露为 job 子命令。
- **核心抽象**：job 生命周期（drafted→queued→failed/completed）（README:41-55）、`headless-run/batch-run` 无头模式（README:36-38）、benchmark 命令（README:40）。
- **关键机制**：
  - job-step 级编辑：add/remix/insert/remove step（README:47-50）。
  - run/batch/headless 三形态复用同一管线（README:36-39）。
  - facefusion[184] 文件、tests[47] 高覆盖结构（tree-metrics）。
- **工程亮点**：把"换脸"建模为可重放、可断点、可批处理的 step 序列而非一次性 GUI 操作。
- **教学映射**：讲透CV、讲透多模态（管线化生产思维）。
- **一句话本质**：给专业换脸流程配上工业级作业队列——面向可批量交付的内容生产线而非玩具 demo。

### upscayl/upscayl
- **架构模式**：Electron+Next.js 壳进程，把 upscayl-ncnn 二进制当子进程调用（Vulkan 推理）。
- **核心抽象**：IPC 命令层 `ELECTRON_COMMANDS`（electron/index.ts:84-105）、commands/ 目录单命令单文件（index.ts:7-22）、jotai atom 状态（renderer…/index.tsx:6-13）。
- **关键机制**：
  - `imageUpscayl/batchUpscayl/doubleUpscayl` 三种放大命令 IPC 注册（index.ts:99-103）。
  - `get-gpu-info` 暴露 GPU 检测给渲染层（index.ts:107-114）。
  - Mac App Store 安全作用域资源+FOSS 双构建 feature flag（index.ts:59-82）。
  - 自定义 file/public 协议解决 asar 路径（index.ts:32-45）。
- **工程亮点**：无 Python 依赖——ncnn Vulkan 推理让核显也能本地超分，Linux 发行版全渠道打包。
- **教学映射**：讲透CV（超分辨率/传统模型部署）、讲透多模态。
- **一句话本质**：把 Real-ESRGAN 类 ncnn 模型包进跨平台桌面应用，让"右键图片→高清化"对非程序员成立。

### pipecat-ai/pipecat
- **架构模式**：框架级语音 Agent 管线——transport/STT/LLM/TTS 皆为可插拔 frame 处理器，多 Agent 走 handoff/共享总线。
- **核心抽象**：`Pipeline`（README:27-28"每条管线即一个 Agent"）、服务矩阵（README:88-103 十余类目录）、CLI Typer app（cli/main.py:65-113）。
- **关键机制**：
  - CLI 惰性构建，未装 cli extra 时优雅降级打印安装提示（cli/main.py:8-30、65-69）。
  - entry-point 插件发现：单个坏插件跳过而不拖垮全局（cli/main.py:115-155）。
  - 官方未装插件注册可发现 stub（cli/main.py:157-175）。
  - `pipecat init` 脚手架即配好 AI coding agent 构建（README:50、cli/main.py:82-86）。
- **工程亮点**：插件隔离加载与 stub 可发现性设计是 CLI 生态课的佳例。
- **教学映射**：讲透多Agent协作、讲透多模态（音/视频流）、讲透记忆（mem0 集成位）。
- **一句话本质**：为"实时语音对话"提供统一的帧流水线抽象，使 STT→LLM→TTS 的百种组合可声明式拼装。

### livekit/agents
- **架构模式**：服务器端"可编程参会者"框架——WebRTC 媒体面 + AgentServer 作业调度面 + 语音管线面三层。
- **核心抽象**：`Agent`（voice/agent.py:39）、`AgentSession`（README:75）、`entrypoint/AgentServer`（README:76-77）。
- **关键机制**：
  - Agent 构造器统一注入 stt/vad/llm/tts，字符串自动经 `inference.*.from_model_string` 解析（agent.py:84-96）。
  - `update_options` 通话中途热换 STT/TTS（agent.py:263-299）。
  - turn_handling 新旧参数迁移 `_migrate_turn_handling`（agent.py:68-77）。
  - chat_ctx 只读视图+按 tools 过滤无效函数调用（agent.py:154-164、235-261）。
  - 语义 turn 检测（transformer 判句尾）降打断（README:40）。
- **工程亮点**：Agent 可继承（`camel_to_snake_case` 自动 id，agent.py:63-66），多 Agent handoff 内建。
- **教学映射**：讲透多Agent协作、讲透多模态、讲透上下文缓存（ChatContext 管理）。
- **一句话本质**：把语音 Agent 做成 WebRTC 房间里的"一等公民参会者"，解决电话级实时交互的调度与管线工程。

### microsoft/generative-ai-for-beginners
- **架构模式**：21 课静态课程仓——每课 README+Python/TypeScript 双语示例，GitHub Action 自动多语言翻译。
- **核心抽象**：Learn/Build 双课型（README:53）、lesson 目录约定（06/07/08…21）、Co-op Translator 流水线（README:19-43）。
- **关键机制**：
  - 示例直接指向 Azure OpenAI v1 兼容端点 `<endpoint>/openai/v1/`（06…/main.ts:11-14）。
  - 双跳 prompt 链：先生成食谱再把输出拼进购物清单请求（main.ts:53-72），天然的"以上下文续写"教学例。
  - Responses API + `store:false` 隐私默认（main.ts:34-48）。
  - 稀疏克隆指引避开 50+ 翻译目录（README:26-42）。
- **工程亮点**：12160 文件中 8030 是翻译图片——内容工程的规模化管理范例。
- **教学映射**：讲透RAG（lesson 15）、讲透多Agent协作（lesson 17）、讲透记忆/上下文（lesson 07 chat）。
- **一句话本质**：给零基础开发者一条从 prompt 到 RAG 到 Agent 的 21 步标准化上坡道，微软云生态的官方入门漏斗。

### rasbt/LLMs-from-scratch
- **架构模式**：书籍配套代码仓——章节目录即课程，纯 PyTorch 手写 GPT 全链路。
- **核心抽象**：`GPTModel`（ch07…/app.py:16、32-40 的 GPT_CONFIG_355M）、`generate/text_to_token_ids`（app.py:17-21）、`pkg/llms_from_scratch` 可安装包（tree-metrics pkg[38]）。
- **关键机制**：
  - 配置字典驱动的模型规格（vocab 50257/16 头/24 层，app.py:32-40）。
  - SFT 权重 `gpt2-medium355M-sft.pth` 加载+chainlit 聊天界面（app.py:44-68）。
  - Alpaca 风格 `### Instruction/### Response` 模板与输出截取（app.py:60-92）。
  - 章节即模块：ch02 分词→ch03 attention→ch04 GPT→ch05 预训练→ch06/07 微调（README:68-73）。
- **工程亮点**：所有主章节代码在普通笔记本可跑完，LoRA 留在附录 E 做进阶。
- **教学映射**：讲透Transformer、讲透PyTorch（最贴题的仓）、讲透RL 可衔接 ch05 损失视角。
- **一句话本质**：把 GPT 从 embedding 到指令微调逐行写给你看，消灭"LLM 是黑盒"的恐惧。

---

## 组内横向对比

**微调双雄（LlamaFactory vs unsloth）**：LlamaFactory 走"广度优先"——以 YAML 配置覆盖 100+ 模型、十余种对齐算法（README:105-112），本质是 HuggingFace 生态的编排层，甚至把 unsloth 当作可选加速开关（README:109）。unsloth 走"深度优先"——用重写内核换 2 倍速/70% 显存（README:86），近期更向桌面产品与 coding-agent 本地底座演化（`unsloth start claude`）。二者一个赢在方法学覆盖与 Day-0 适配，一个赢在单卡效率极限：main.py:20-24 里连 CUDA 设备排序、ROCm DLL 注入都要在 torch import 前抢跑，可见其护城河在系统层而非算法层。

**节点图（ComfyUI）vs 单体 WebUI（SD-webui）**：SD-webui 是"功能堆叠"架构——modules/ 154 个文件、每个 feature 一个 tab（README 特性清单长达 90 行），扩展靠社区 fork extensions；其价值在定义了用户预期。ComfyUI 是"数据流"架构——一切皆节点，功能组合空间从 N 个 tab 变成 DAG 的指数空间，工作流本身成为可 JSON 化、可 API 化的资产（README:43、82-84）。演化本质：从"预设流水线的消费者"到"流水线的搭建者"，这也解释了为何生产管线与视频/3D 等长链路任务全面倒向节点图。

**语音管线（pipecat vs livekit/agents）分层**：pipecat 是"框架层"——不自带基础设施，transport（Daily/LiveKit/WebSocket）本身也是可插拔服务（README:96），主打 frame 流水线抽象与多 Agent handoff 的轻量组合。livekit/agents 是"全栈层"——底层绑死自家 WebRTC SFU，向上长出作业调度（AgentServer/dispatch）、telephony、turn 检测等运维能力（README:36-43）。有趣的是二者非纯竞争：pipecat 可把 LiveKit 当 transport，分层关系大于对抗关系——pipecat 管"管线怎么搭"，livekit 管"媒体怎么传、作业怎么调度"。
