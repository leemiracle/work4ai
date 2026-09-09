# LocalAI 新人上手指南（ONBOARDING）

> 基于知识图谱（10637 节点 / 103809 边 / 18 层 / 15 步导览，commit 9e831d7）生成，关键事实（52 RPC、各文件行数、后端数量）均已对照源码核实。

---

## 1. 项目总览

**LocalAI 是什么**：一个自托管、OpenAI 兼容的本地 LLM 推理服务。Go 实现 API 层，通过 gRPC/CGo/purego 桥接多种语言的后端（llama.cpp / Diffusers / Transformers / vLLM / piper / whisper 等），支持文本生成、嵌入、重排、语音（ASR/TTS/WebRTC 实时对话）、图像与视频生成、函数调用、微调与量化，最终打包成单二进制/单容器部署。

**它解决的核心问题**：把"OpenAI API"变成一个可以完全私有部署的替代品——外部应用只需把 `base_url` 指向 LocalAI，即可零改造切换到本地推理。三重价值：

1. **OpenAI 兼容**：`/v1/chat/completions`、embeddings、audio、images、rerank、realtime 等全套端点，兼容生态里的 SDK、LangChain、各类客户端直接工作；
2. **多后端聚合**：通过统一 gRPC 契约，让 80+ 种开源模型（LLM/语音/图像/人脸/声纹）以"一份 YAML 配置"的形式从 HuggingFace/Ollama 源一键安装；
3. **可扩展成集群**：单机起步，需要时横向扩展为分布式推理集群（NATS 命令通道 + PostgreSQL 状态持久化 + edgevpn P2P 可选组网），配 React 运维控制台。

**一句话架构观**：`OpenAI 兼容 HTTP API（Go）→ 统一 gRPC 契约（backend.proto，52 个 RPC）→ 可插拔后端进程（Go/Python/C++/Rust 四语言矩阵）`，外加 React Web UI 与分布式调度层。

---

## 2. 架构分层说明（18 层）

图谱把全仓 2656 个文件组织为 18 层，自上而下是"用户入口 → API → 服务 → 契约 → 后端 → 基础设施"：

| # | 层 | 职责 | 代表文件 |
|---|---|---|---|
| 0 | CLI 与应用启动层 | 二进制入口、kong 命令树、DI 容器、启动编排、分布式装配 | `application.go`、`startup.go`、`core/cli/worker.go` |
| 1 | OpenAI 兼容 API 端点层 | 108 个 OpenAI 风格端点处理器 | `endpoints/openai/chat.go`、`inference.go`、`realtime.go` |
| 2 | LocalAI 原生 API 端点层 | 模型安装/任务调度/webhook/TTS 管理等运维端点 | `endpoints/localai/nodes.go`、`backend_logs.go` |
| 3 | 多协议兼容 API 端点层 | Ollama/Anthropic/OpenResponses/MCP/ElevenLabs | `endpoints/ollama/chat.go`、`anthropic/messages.go` |
| 4 | HTTP 服务框架层 | gin/Echo 路由注册、中间件链、鉴权、Swagger embed | `core/http/app.go`、`core/http/routes/*.go` |
| 5 | React Web UI 前端层 | 内置聊天与管理界面（React/TS，Go embed 进二进制） | `react-ui/src/App.jsx`、`pages/Chat.jsx` |
| 6 | 分布式集群与 P2P 层 | 节点注册/心跳/调度、edgevpn 组网、explorer 发现 | `core/services/nodes/`、`core/p2p/p2p.go` |
| 7 | 核心业务服务层 | 路由、galleryop、worker、agentpool、messaging、jobs | `core/services/routing/`、`galleryop/models.go` |
| 8 | 模型后端抽象与契约层 | **全仓架构枢纽**：core/backend 包装 + backend.proto 本体 | `backend/backend.proto`、`core/backend/embeddings.go` |
| 9 | 配置与数据 Schema 层 | YAML 加载/校验/热重载 + 领域 schema | `core/config/model_config.go`、`core/schema/prediction.go` |
| 10 | 模型库 Gallery 层 | 85 个模型 YAML + 导入器 + 提示词模板 | `core/gallery/gallery.go`、`gallery/flux.yaml` |
| 11 | Go 后端桥接层 | 32 个 Go 后端（purego 动态加载 C 库） | `backend/go/whisper/main.go` |
| 12 | Python 后端层 | 37+ 个 Python 后端（vLLM/diffusers/whisper 族） | `backend/python/vllm/backend.py` |
| 13 | C++/Rust 原生后端层 | llama-cpp、ik-llama-cpp、turboquant、audio-cpp 等 | `backend/cpp/llama-cpp/grpc-server.cpp` |
| 14 | pkg 公共库层 | gRPC 生成代码、模型加载框架、下载器、硬件探测 | `pkg/grpc/client.go`、`pkg/model/initializers.go` |
| 15 | 测试与形式化验证层 | e2e/integration 测试 + FizzBee 形式化规约 | `tests/e2e-aio/`、`formal-verification/*.fizz` |
| 16 | 构建与部署基础设施层 | CI 矩阵、Dockerfile 全家桶、Makefile（1665 行） | `Makefile`、`docker-compose.yaml` |
| 17 | 文档与网站层 | Hugo 文档站、官网、AI 编码助手指引 | `docs/`、`.agents/` |

**分层的本质**：0-5 层是"一个 HTTP 产品的外壳"；6-7 层是分布式与业务服务；**8 层是全仓架构枢纽**——所有后端与 API 层之间唯一的边界，理解了它就理解了 LocalAI 的可扩展性来源；9-10 层是"模型即配置"哲学的载体；11-13 层是四语言后端矩阵；14-17 层是支撑设施。

---

## 3. 核心模块

### 3.1 CLI 入口与启动装配
`cmd/launcher/main.go` 是桌面启动器（Fyne 窗口+托盘），服务化的真正入口在 `core/cli`（kong 命令树：models/worker/workerregistry/explorer 等）。`core/application/application.go` 的 **Application 结构体 = 全局依赖注入容器**，聚合模型加载、配置、认证、PII 治理、路由决策、人脸/语音注册表等三十余项服务；`startup.go` 编排启动顺序（数据目录迁移、HMAC 密钥加载、看门狗、配置热重载监视）。新人先记住：**所有模块都在这里被构造和注入**，读任何服务前先看它如何被装配。

### 3.2 backend.proto 统一契约（52 个 RPC）
`backend/backend.proto` 定义**单一 gRPC `Backend` 服务**：文本生成/流式推理/embedding/重排/TTS/ASR/图像/向量存储/健康检查/加载卸载/微调/量化等 52 个 RPC。所有 Go/Python/C++/Rust 后端都实现这一契约，API 层只面对这一个接口——这是"API 核心 + 可插拔后端"架构的钥匙。`core/backend/options.go` 是选项组装中枢（ModelOptions 加载链 + gRPC 模式协商）；`core/backend/embeddings.go` 展示典型包装模式：加载后端并返回闭包，按 `EmbeddingResult.layout` 协商池化职责。

### 3.3 gRPC 运行时桥接（embed / 远程进程两种模式）
- `pkg/grpc/interface.go`：`AIModel` 全能力接口；`pkg/grpc/base/base.go`：默认基类实现，后端只需覆写自己支持的方法。
- `pkg/grpc/client.go`（1410 行）：客户端最大实现——惰性建连、并行互斥/在途计数、bearer token 凭据、流式回调与 streamCleanup 生命周期。
- **远程进程模式**：后端作为独立进程运行（崩溃隔离，不拖垮 API 核心），由 `pkg/model/initializers.go`（pkg 层 fan-in 最高，188）负责"这个模型用哪个后端进程、如何启动、LRU/并发组驱逐、失败冷却与重试"。
- **embed 模式**（`pkg/grpc/embed.go`，876 行）：把 Backend 全表面适配到进程内 server，免去本地回环 gRPC，含 12 个流适配类，用于单二进制内嵌与单元测试。

### 3.4 后端矩阵（四语言，78+ 个后端）
- **Go（32 个，backend/go）**：whisper/stablediffusion-ggml/piper/sherpa-onnx/trellis2cpp 等，特色是 **purego 运行时 dlopen 动态库**并注册 C 符号，无需 CGO 编译期绑定（见 `backend/go/whisper/main.go`）——"Go 壳 + C/C++ 共享库"让传统 AI 库按需打包成独立后端镜像。
- **Python（37+ 个，backend/python）**：vLLM/sglang/transformers/trl（LLM）、diffusers（图像视频，importlib 动态发现管线）、faster-whisper/whisperx/qwen-asr（语音）、kokoro/vibevoice/coqui 等（TTS），全部共享 `backend/python/common/libbackend.sh`（625 行：便携 Python 下载、uv/pip venv、protobuf 生成、启停编排）。
- **C++（backend/cpp）**：llama-cpp（GGUF LLM 主执行者）、ik-llama-cpp、ds4、bonsai、turboquant、audio-cpp 语音族共享库、privacy-filter；**Rust**：kokoros。每个后端的通用形态 = 实现 BackendServicer + 暴露 Health/LoadModel/Predict。

### 3.5 Gallery 模型库
"模型"在 LocalAI 中是声明式商品：`gallery/*.yaml` 85 个模型定义（flux 走 diffusers 生图、deepseek-r1 配 131072 上下文走 llama-cpp）。三件套协作：`core/gallery/gallery.go`（索引拉取、SSRF 防护的 URL 校验、搜索/模糊过滤/分页）→ `core/gallery/models.go`（安装主流程、变体解析 ResolveVariant、删除与安全扫描）→ `core/services/galleryop/models.go`（持锁安装 modelHandlerLocked：下载、配置快照、失败回滚 restore）。回看 3.1 的配置层：**这些 YAML 正是 ModelConfig 的实例化**。

### 3.6 分布式集群（nodes / NATS / PostgreSQL）
- `core/services/nodes/`（99 个文件）是调度核心：`registry.go`（2788 行，GORM 持久化 BackendNode/NodeModel/调度配置，103 个方法覆盖节点审批、心跳、VRAM 预算、副本放置与 LRU 逐出）+ `router.go`（**SmartRouter**，2117 行，idle-first 放置决策链）+ `distributed_store.go`（本地 store 外包 PostgreSQL 后备查找）。
- **NATS 是命令通道**：worker 以 JWT+seed 凭据注册（`workerregistry/credentials.go`）、心跳、接收任务；`messaging/client.go` 封装自动重连。`file_staging_client.go` 让分布式模式对 core/backend **透明**——gRPC 调用前把输入文件 stage 到后端节点、调用后取回输出。
- **P2P 可选**：`core/p2p/p2p.go` 基于 edgevpn/libp2p 无中心组网与服务发现，`core/explorer/discovery.go` 从区块链账本拉取网络数据。

### 3.7 React Web UI
`core/http/react-ui/`：`App.jsx` 根组件组装侧边栏布局并初始化主题/认证/品牌/i18n Context；`utils/api.js` 是与后端通信的**唯一出口**（UI 层 fan-in 第一）；`AuthContext.jsx` 管理登录态。重页面：Chat.jsx（1637 行，流式对话+工具调用+画布+MCP）、Backends.jsx（1020 行目录管理）、Nodes（集群管理）、Usage（用量统计）、AgentChat 等。构建产物由 Go embed 进二进制，调用第 2 层原生管理 API 完成前后端闭环。

---

## 4. 关键概念（从图谱节点 summary/tags 提炼，15 个）

1. **OpenAI 兼容层**：108 个端点处理器复用 `inference.go` 的 `ComputeChoices` 管线（模板求值→后端 Predict→token 流回调→函数调用解析），读懂一处等于读懂全部。
2. **Backend 接口双协议**：Inference（Predict/Embedding/TTS…）与 Control（Health/LoadModel…）合并在单一 gRPC 服务里。
3. **模型即配置（ModelConfig）**：每个模型=一份 YAML；`model_config.go` 2342 行类型系统是载体，gallery YAML 是实例。
4. **进程隔离**：后端默认独立进程，崩溃不拖垮 API 核心；embed 模式是单二进制场景的例外。
5. **purego 动态加载**：Go 后端运行时 dlopen C/C++ 共享库，免 CGO 编译期绑定。
6. **libbackend.sh**：Python 后端共享构建/运行库（便携 Python + venv + protobuf 生成）。
7. **gallery importer**：HuggingFace/Ollama/HTTP 三源拉取 + 签名校验 + 变体解析 + 失败回滚。
8. **SmartRouter**：分布式请求放置决策（模型已加载？→空闲 VRAM？→空闲节点？→可驱逐 LRU？逐级下探至 wait-then-evict）。
9. **prefix-cache 路由**：`nodes/prefixcache` 的 radix-tree 热前缀索引 + pressure 滚动窗口计数器，作为"温副本饱和应扩容"的自动伸缩信号。
10. **realtime 状态机协调器（M1-M5）**：实时语音 API 拆成五个可形式化验证的子状态机——M1 连接生命周期、M2 轮次检测（turncoord）、M4 会话压缩等，各配独立 .fizz 规约。
11. **FizzBee 形式化验证**：`formal-verification/*.fizz` 对模型加载器关停路径（LocalForce/GracefulShutdown/DistributedForce 三模式）与 realtime 各状态机做模型检查，断言 TeardownOnce、SingleFlight 等不变量——比单元测试更强的正确性证明。
12. **多协议兼容**：Ollama API（/api/chat）、Anthropic Messages（/v1/messages）、OpenResponses、MCP 工具协议、ElevenLabs 语音，让存量客户端零改造迁移。
13. **agent 拦截中间件**：`agent_responses.go` 缓冲请求体嗅探 model 名，命中 Agent Pool 则改道 agent 执行并适配响应，否则透传正常管线。
14. **file staging**：分布式下多模态调用的输入文件先分级（stage）到目标节点、输出取回本地，覆盖 Predict/TTS/ASR 等全部多模态方法。
15. **VRAM 预算与 LRU 驱逐**：节点显存预算支持 "80%"/"12GB" 解析并在心跳中钳制 available_vram；模型实例按 LRU 逐出 + 失败冷却。

---

## 5. 推荐学习路径（按 tour 15 步递进）

建议顺序执行，每步先看文件、再理解机制、最后用自检问题验收：

| 步 | 看什么文件 | 理解什么 | 自检问题 |
|---|---|---|---|
| 1 | `README.md` | 全局地图：Go API+四语言后端+React UI+集群 | 一个 OpenAI 请求经过哪些层、到达哪个后端？ |
| 2 | `cmd/launcher/main.go`、`application.go`、`startup.go` | 入口与依赖注入装配 | 为什么说 Application 是全局 DI 容器？ |
| 3 | `core/config/application_config.go`、`model_config.go` | "模型即配置"哲学 | 模型 YAML 里最重要的字段有哪些？ |
| 4 | `core/http/app.go`、`routes/openai.go` | Echo 装配、中间件链、路由总装 | 请求必经的中间件顺序是什么？ |
| 5 | `endpoints/openai/chat.go`、`inference.go`、`embeddings.go` | ComputeChoices 共享推理管线 | 函数调用在哪一步被解析？ |
| 6 | `routes/ollama.go`、`anthropic.go`、`localai.go` | 多协议兼容+原生管理 API | Ollama 客户端为何零改造可用？ |
| 7 | `backend/backend.proto`、`core/backend/options.go` | 52 RPC 统一契约 | 为什么单一服务而非按能力拆分？ |
| 8 | `pkg/grpc/interface.go`、`base.go`、`client.go`、`pkg/model/initializers.go` | AIModel 接口+模型加载框架 | 后端进程如何被启动与驱逐？ |
| 9 | `backend/cpp/llama-cpp/grpc-server.cpp` | C++ 后端通用形态 | GGUF 模型的实际归宿在哪？ |
| 10 | `backend/python/vllm/diffusers/faster-whisper` 各 `backend.py` | Python 后端三代表 | 三者共享什么骨架？ |
| 11 | `backend/go/whisper/main.go`、`stablediffusion-ggml/main.go` | purego 动态加载 | 与 CGO 编译绑定相比优劣？ |
| 12 | `core/gallery/gallery.go`、`models.go`、`gallery/flux.yaml`、`deepseek-r1.yaml` | 声明式模型商品 | 安装失败如何回滚？ |
| 13 | `core/application/distributed.go`、`nodes/interfaces.go`、`distributed_store.go`、`core/p2p/p2p.go` | 集群调度与 P2P 组网 | NATS 与 PostgreSQL 各承担什么？ |
| 14 | `react-ui/src/App.jsx`、`utils/api.js`、`AuthContext.jsx` | 前后端闭环 | UI 调的是哪一层 API？ |
| 15 | `tests/e2e-aio/e2e_test.go`、`formal-verification/*.fizz`、`Makefile`、`Dockerfile` | 测试/形式化验证/交付 | FizzBee 断言比单测强在哪？ |

---

## 6. 文件地图（按层速查，47 条）

**启动与装配**
- `cmd/launcher/main.go` → 桌面启动器入口（Fyne+托盘）
- `core/application/application.go` → 全局 DI 容器
- `core/application/startup.go` → 启动编排（fan-out 全仓第一）
- `core/application/distributed.go` → 分布式模式装配
- `core/application/p2p.go` → P2P 生命周期与模型状态广播
- `core/cli/` → kong 命令树（models/worker/explorer）

**API 层**
- `core/http/app.go` → Echo 主装配与中间件链
- `core/http/routes/openai.go` → OpenAI 路由总装（282 行）
- `core/http/endpoints/openai/chat.go` → /v1/chat/completions 核心
- `core/http/endpoints/openai/inference.go` → ComputeChoices 共享管线
- `core/http/endpoints/openai/embeddings.go` → 批量向量化（float/base64）
- `core/http/endpoints/openai/realtime.go` → Realtime WebSocket 实现
- `core/http/endpoints/openresponses/responses.go` → Open Responses 端点
- `core/http/routes/ollama.go` / `anthropic.go` → 第三方协议兼容
- `core/http/routes/localai.go` → 原生管理 API 总路由
- `core/http/endpoints/localai/agent_responses.go` → agent 拦截中间件

**契约与桥接**
- `backend/backend.proto` → 52 RPC 统一契约（架构枢纽）
- `pkg/grpc/interface.go` → AIModel 全能力接口
- `pkg/grpc/base/base.go` → 后端默认基类
- `pkg/grpc/client.go` → gRPC 客户端最大实现（1410 行）
- `pkg/grpc/embed.go` → embed 进程内桥接（876 行）
- `pkg/model/initializers.go` → 模型加载/LRU 驱逐框架（fan-in 188）
- `core/backend/options.go` → 选项组装中枢
- `core/backend/embeddings.go` → 嵌入包装（返回闭包）

**配置与 Gallery**
- `core/config/model_config.go` → ModelConfig 类型系统（2342 行）
- `core/config/application_config.go` → 应用级总配置
- `core/config/model_config_loader.go` → 模型配置加载器
- `core/gallery/gallery.go` → 画廊索引与搜索
- `core/gallery/models.go` → 安装主流程/变体解析
- `core/services/galleryop/models.go` → 持锁安装与回滚
- `gallery/flux.yaml` / `gallery/deepseek-r1.yaml` → 模型定义样例（共 85 个）

**后端矩阵**
- `backend/cpp/llama-cpp/grpc-server.cpp` → GGUF LLM 主后端
- `backend/python/vllm/backend.py` → vLLM 高吞吐后端
- `backend/python/diffusers/backend.py` → 动态发现 Diffusion 管线
- `backend/python/faster-whisper/backend.py` → CTranslate2 加速 ASR
- `backend/python/common/libbackend.sh` → Python 后端公共构建库（625 行）
- `backend/go/whisper/main.go` → purego 动态加载代表

**分布式**
- `core/services/nodes/registry.go` → 节点注册表核心（2788 行）
- `core/services/nodes/router.go` → SmartRouter（2117 行）
- `core/services/nodes/distributed_store.go` → PG 后备 store
- `core/services/nodes/prefixcache/provider.go` → 前缀缓存接缝接口
- `core/services/nodes/file_staging_client.go` → 分布式文件分级
- `core/services/messaging/client.go` → NATS 客户端封装
- `core/p2p/p2p.go` → edgevpn/libp2p 组网
- `core/explorer/discovery.go` → P2P 网络发现

**UI、测试与构建**
- `core/http/react-ui/src/App.jsx` → React 根组件
- `core/http/react-ui/src/utils/api.js` → 后端通信唯一出口
- `formal-verification/model_loader_shutdown.fizz` → 加载器关停规约
- `core/http/endpoints/openai/turncoord/turncoord.go` → realtime M2 状态机
- `Makefile` → 1665 行、124 target 构建中枢
- `tests/e2e-aio/e2e_test.go` → 单二进制 e2e 入口

---

## 7. 复杂度热点（新人慎入）

图谱标记 complex 文件 639 个（moderate 1128 / simple 889），UI 页面占比最高。核心热点（行数已实测核实）：

| 文件 | 行数 | 为什么难 | 建议 |
|---|---|---|---|
| `core/http/endpoints/openresponses/responses.go` | 3193 | OR↔OpenAI 双向转换 + 前台/后台×流式/非流式四路径 + SSE | 先读 `core/schema/openresponses.go` 再回来 |
| `core/http/endpoints/openai/realtime.go` | 2931 | 会话/对话/项三层状态机 + Opus 解码→VAD→转写音频管线 | 配合 M1-M5 .fizz 规约对照读 |
| `core/services/nodes/registry.go` | 2788 | 103 个方法覆盖全部控制面状态（审批/心跳/VRAM/驱逐） | 按用例查，不要通读 |
| `core/services/nodes/router.go`（SmartRouter） | 2117 | idle-first 四级放置决策链 | 先看 docs 流程图再读代码 |
| `core/config/model_config.go` | 2342 | 数十个配置节 + YAML 严格解析 + 深度校验 | 当字典按需查 |
| `pkg/grpc/client.go` | 1410 | 惰性建连 + 并行互斥 + 流生命周期 | 完成学习路径第 8 步后再读 |
| `core/http/react-ui/src/pages/Chat.jsx` | 1637 | 流式+工具调用+画布+MCP 全家桶 | UI 侧最后攻 |
| `core/http/react-ui/src/App.css` | ~13000 | 2331 个类的手写 BEM | 永远别通读 |

**规律**：复杂度集中在"协议转换（responses/realtime）""分布式状态管理（registry/router）""配置类型系统"三处——也是最容易引入回归的地方，改动前先跑第 15 步的形式化规约与测试。

---

## 8. 与生态的关系

- **vs llama.cpp**：llama.cpp 是单一 GGUF 推理引擎（C++），LocalAI 把它（连同 ik-llama-cpp 等衍生）作为后端之一纳入统一契约——**LocalAI 是"多引擎聚合的 API 服务层"，llama.cpp 是引擎**。LocalAI 还携带两个上游补丁（score-task/tts-task）扩展其 server 能力。
- **vs ollama**：定位最接近（本地 OpenAI 替代+模型库），但 LocalAI 走"单 gRPC 契约 + 四语言后端矩阵"的开放架构：模态远超文本（语音/图像/视频/人脸/声纹/实时语音）、gallery 支持自定义源与变体、并提供 ollama 不具备的分布式集群（NATS/PG/P2P）、形式化验证的核心路径与 React 运维控制台；同时**直接兼容 Ollama API**（/api/chat 等），ollama 客户端可无缝迁移。
- **vs vLLM**：vLLM 是面向高吞吐生产的 Python 推理引擎，LocalAI 把 vllm 作为 Python 后端之一（`backend/python/vllm/backend.py`，含分布式 follower 模式 `worker_vllm.go`）——需要 PagedAttention 级吞吐时在 LocalAI 里选用它，同时保留统一 API 与其他模态后端。
- **一句话**：llama.cpp/vLLM 是"引擎"，ollama 是"同类竞品"，LocalAI 的差异化 = **引擎无关的多模态聚合 + OpenAI/Ollama/Anthropic 多协议兼容 + 分布式扩展 + 单二进制交付**。

---

## 快速上手三件事

1. `docker-compose up`（8080 端口）或 `make run` 起服务；
2. 装一个模型：UI 的 /app/browse 或 `local-ai models install <gallery 名>`；
3. 用任意 OpenAI SDK 把 base_url 指向 `http://localhost:8080/v1` 发第一条 chat 请求——然后带着"这条请求经过了哪些层"的问题，回到第 5 节学习路径的第 4 步。
