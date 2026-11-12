# 讲透 DeepStream

> NVIDIA DeepStream SDK 9.1 **全源码仓**——GStreamer 视频分析管线框架（多路多模型，dGPU/Jetson/SBSA）。**agent-first 仓第六例**（AGENTS.md 直言"给 Claude Code/Cursor/Codex 的指南"+14 个官方 skill+example_prompts；CLAUDE.md 是 AGENTS.md 的符号链接）。

## 全链状态表

| 阶段 | 状态 | 产出 |
|---|---|---|
| understand 图谱 | ✅ 2026-11-07 | 仓内 `.understand-anything/knowledge-graph.json`：**6474n/9673e/16 层/16 步 tour，validator 0/0，fingerprints 2876@0a63ef8b** |
| onboarding | ✅ 2026-11-07 | `onboarding/ONBOARDING.md`（8 节 11998 字不计空格，141 锚全源码抽验命中） |
| explain 12 篇 | ✅ 2026-11-07 | `explain/01-12` 合计 **72784 字符**，双组合计 424 锚，主会话终验 0 坏 |

## 战况（246 批）

四 worker 滚动 64 段+末段，两次 1308（05:40 团灭/08:22 杀 layers+w1）均死前落盘+SendMessage 复活零重做。全量终验：295 件全合法/6471 ID 唯一/2876 文件全覆盖零缺失；merge 15 悬空边归因（3 前缀错位改写+3 纯虚接口类手术补建：TextMapPropagator/IDSPostProcessLibrary/IDSCustomLibrary）回补 9 边。

## 甄别精选（源码级实证）

1. **agent-first 资产层**：14 skill（标定 AMC×4/评测微调/管线生成/模型导入/profiling/MV3DT/SOP/rtvi×3/dev）+ example_prompts 14 篇+**brev 实验室 ds_agent_lab.py 3044 行 79 函数**；generate-pipeline 检索语料 data.csv 272 行
2. **nvinfer vs nvinferserver 双后端**：进程内引擎 vs Triton（CAPI/gRPC 双模式互斥校验 `has_grpc()&&has_model_repo()`）；model_config.pb 巨对 15879/17780 行
3. **msgconv 三版本 schema 演进**：原版→mega（加 bbox3d/llm）→mega2d（修泄漏加 embedding）；四协议适配器 amqp/azure/kafka/mqtt
4. **streammux2 开源核心**：`USE_NEW_NVSTREAMMUX` 环境变量切换 legacy；"凑满或超时"双条件出批+NTP 单调钳制
5. **nvtracker 的 NvMOT C ABI**：dlopen 六符号（必需 3+可选 4），控制流搭数据流便车
6. **C/C++ 盲区再实证**：tree-sitter 对 .h/.hpp/.cu 全空——手扫补 1939 条（OTel vendored 大树 600+794 边）+21 个 CUDA kernel（conversion.cu 18+patterns.cu 3）；尖括号项目内 include 新盲区
7. 勘误集：cuosd 字号上限实测 200 非 500；Python 样例镜像实际在 service-maker（flow_api test1 仅 68 行 vs C 版 348）；TAO 三后端矩阵实测 14 家族（README 自称 twelve 且 OCDNet/OCRNet 仓内无配置）；RT-DETR 在 Blackwell 需 strongly-typed=1 否则全空检测；sam2 根目录 5 yaml 与 configs/ 逐字节副本
8. vendored 深度：OTel v1.23+prometheus-cpp+half.hpp 4618 行+absl 垫片（600+794 手补边主战场）

## 分层速览（16 层，2940 文件节点）

构建部署 → skills/agent 资产 → vendored 第三方 → includes 公共契约（nvdsmeta 1130 行根契约）→ 框架/公共库 → 核心插件（推理双后端/解码/追踪/分析/消息）→ 应用层（sample/tao/reference 三群）→ 工具（yolo/sam2）→ 配置资产

*2026-11-07 · cuda-stack-第七轮会话（舰队认领）*
