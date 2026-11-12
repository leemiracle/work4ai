# 讲透 LocalAI · 深度知识库

> 基于 understand-anything 中文知识图谱 + 核心源码深解的 LocalAI 学习知识库。
> 生成于 2026-09-05，对应源码 commit `9e831d7`（2026-09-03）。

## 这是什么

LocalAI 是自托管的 OpenAI 兼容本地 LLM 推理服务：Go 实现 API 层，通过 gRPC 桥接 40+ 推理后端（llama.cpp/Diffusers/Transformers/vLLM/piper/whisper 等），支持文本/语音/图像/嵌入/函数调用/Realtime，单二进制容器化部署，并内置 NATS+PostgreSQL 分布式集群能力。

本知识库服务于三类场景：

| 场景 | 用哪部分 | 怎么用 |
|---|---|---|
| 新人系统上手 | `onboarding/ONBOARDING.md` | 从头读：项目总览→18 层架构→15 个关键概念→15 步学习路径→51 条文件地图→复杂度热点 |
| 啃核心源码 | `explain/`（12 篇） | 每篇一个核心文件的深度解析：角色定位→内部结构→外部连接→数据流→设计决策→新人提示 |
| 交互式探索 | 知识图谱（仓内） | 10637 节点/103809 边/18 层/15 步导览全中文图谱，位于 `~/ai/localai/.understand-anything/knowledge-graph.json`，用 understand-anything 插件 `/understand-chat`、`/understand-dashboard` 交互查询 |

> 注：DeepWiki 未收录 localai（探测确认为未索引状态），本仓知识库以 understand 图谱为主力数据源。

## 目录结构

```
讲透LocalAI/
├── README.md                  # 本文件
├── onboarding/
│   └── ONBOARDING.md          # 新人上手指南（4117 字，9 节，源码交叉验证）
└── explain/                   # 12 篇核心文件深解
    ├── localai-entry.md           # CLI 入口与服务启动（kong + RunCMD 主流程）
    ├── localai-backend-proto.md   # backend.proto 统一契约（52 RPC 双协议）
    ├── localai-grpc-client.md     # gRPC 客户端（1410 行，流生命周期三套封装）
    ├── localai-grpc-embed.md      # 进程内桥接（876 行 + 12 流适配类）
    ├── localai-model-config.md    # 模型配置类型系统（2342 行，配置即模型）
    ├── localai-openai-chat.md     # OpenAI 兼容主线（ComputeChoices + 流式 worker）
    ├── localai-nodes-registry.md  # 分布式注册表（2788 行 NodeRegistry）
    ├── localai-smart-router.md    # SmartRouter（三级择优 + prefix-cache 亲和）
    ├── localai-gallery.md         # Gallery 模型库（安装编排 + 变体漏斗）
    ├── localai-llama-backend.md   # Go 后端代表（CGO vs purego 双模式）
    ├── localai-realtime.md        # Realtime WebSocket（2931 行 + 四协调器）
    └── localai-agent-worker.md    # Agent worker（NATS 消费 + 进程监督）
```

## 推荐阅读路径

```
ONBOARDING.md（1h，全局观）
   ↓ 挑主线：API 兼容层
explain: entry → openai-chat → backend-proto
   ↓ 转运行时：gRPC 桥接
explain: grpc-client → grpc-embed → llama-backend
   ↓ 深服务层
explain: model-config → smart-router → nodes-registry
   ↓ 特色功能
explain: gallery → realtime → agent-worker
   ↓ 想动手时
知识图谱交互探索（understand-chat / understand-dashboard）
```

## 图谱规模

- **10637 节点**：file 2656 / function 5387 / class 1361 / document 432 / config 286 / step 209 / schema 80 / endpoint 63 / pipeline 121 / service 42
- **103809 边**：imports 89833 / contains 7134 / exports 4038 / depends_on 747 / tested_by 732 / related 418 / calls 359 / configures 237…
- **18 层架构**（CLI 入口→API 端点×3→HTTP 框架→React UI→分布式→核心服务→后端契约→配置→Gallery→后端矩阵×3→pkg 库→测试→构建→文档网站）
- **15 步导览** + 10 个 languageLesson（Go DI 选项模式/Protobuf 契约/purego vs CGO/FizzBee 形式化验证等）

## 勘误记录（实测钉版）

1. `backend.proto` 实际在 `backend/backend.proto`（非 pkg/grpc）
2. `realtime.go` 在 `core/http/endpoints/openai/`（非 localai/），同目录约 20 个 realtime_* 协作文件
3. `backend/go/llama-cpp/main.go` 不存在——llama.cpp 主力后端是 C++ 单体 gRPC server（`backend/cpp/llama-cpp/grpc-server.cpp`）；Go 桥接代表为 `backend/go/llm/llama`（旧 CGO）+ `backend/go/whisper`（purego 现役）

## 生成方式

- 图谱：understand-anything 流水线（scan 3503 文件 → 221 批 file-analyzer（主会话 4 并发 + opencode run 无人值守 worker 双引擎）→ merge 10637 节点/103809 边 → 18 层 architecture-analyzer → 15 步 tour-builder → 校验 0 issues → fingerprints 基线）
- 指南与深解：全部基于图谱 + 源码只读交叉验证（行号 wc -l 实测）
