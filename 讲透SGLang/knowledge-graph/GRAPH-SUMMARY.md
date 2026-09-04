# SGLang 知识图谱摘要（GRAPH-SUMMARY）

> 生成：`/understand --language zh` | 图谱文件：[knowledge-graph.json](knowledge-graph.json)（6.0 MB）
> 本地基线 commit：`ec075d8bc`（2026-09-04 校验通过：0 悬挂边 / 0 层重复 / 0 导览断链 / 中文摘要 100%）

## 规模

| 指标 | 数值 |
|------|------|
| 节点 | 5652 |
| 边 | 12950 |
| 架构层 | 27 |
| 导览步骤 | 12 |
| 分析文件数 | 5618 |
| file 级节点 | 3238（complex 577 / moderate 2009 / simple 652） |

## 项目元数据

- **名称**：SGLang——高性能 LLM/VLM 服务框架（RadixAttention、投机解码、分离式推理、多模态）
- **语言**：python / rust / cuda / c++ / markdown / yaml / toml / shell / dockerfile / protobuf / go / javascript
- **框架**：PyTorch、vLLM（部分内核借用）、FlashInfer、Triton、FastAPI、Tokio、Axum、gRPC

## 27 层架构（节点数）

入口与API层(40) · 调度管理层(10) · 模型执行层(218) · 神经网络算子层(215) · 推理加速层(42) · 内存与缓存层(50) · 分布式通信层(10) · 硬件抽象层(20) · 内核层(36) · JIT内核层(138) · 网关与路由层(174) · 多模态处理层(50) · 多模态生成层(445) · LoRA适配层(20) · 可观测性层(69) · 插件层(1) · 前端语言层(13) · CLI层(3) · 核心工具层(10) · SRT运行时工具层(37) · 测试层(866) · 基准测试层(91) · 基础设施层(26) · 文档层(80) · 示例层(12) · 脚本层(5) · 配置层(8)

## 12 步导览（学习主线）

1. 项目概览（server_args.py 能力面）
2. 服务启动流程（engine.py → http_server.py → TokenizerManager）
3. API 协议层（serving_chat/completions/protocol）
4. 请求调度与 Batch 管理（io_struct → prefill_delayer）
5. 模型执行与 Forward Pass（model_runner → forward_batch_info → cuda_graph_runner）
6. RadixAttention 与 KV Cache（radix_cache → memory_pool → hiradix_cache）
7. 模型注册与实现（registry → llama → deepseek_v2 → loader）
8. 神经网络算子（FusedMoE / FP8 量化 / 采样器）
9. 分布式推理（DeepEP token 分发 / Ray DP controller / custom_all_reduce）
10. 投机解码（EAGLE / Ngram worker / spec_info 注册）
11. CUDA 内核（sgl-kernel 与 JIT kernel）
12. 基础设施（Rust 网关：worker_manager / cache_aware / circuit_breaker）

## 使用方式

- 交互式浏览：把 `.understand-anything/` 放回 SGLang 仓库根，运行 `/understand-dashboard`
- 程序化查询：`jq '.nodes[] | select(.type=="file") | .filePath' knowledge-graph.json`
- 中文摘要：全部节点 summary 为原生中文，可直接做 RAG/检索语料

## 校验记录（2026-09-04）

```
nodes=5652 edges=12950 layers=27 tour=12
dangling_edges=0 layer_dangling=0 layer_dup=0 tour_dangling=0
zh_summary_ratio(first500)=500/500
file_unassigned=676   ← 676 个 file 级节点未纳入 27 层（多为边缘脚本/测试 fixture，不影响主架构浏览）
```
