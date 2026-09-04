# 讲透 SGLang

> SGLang 深度知识库——DeepWiki 全量中文抓取 + 中文知识图谱 + 新人上手指南 + 核心文件逐行解析
> 代码基线：commit `ec075d8bc`（本地）≈ `94183a8d`（DeepWiki 索引，2026-08-27）| 构建日期：2026-09-04
> 姊妹篇：[讲透vLLM](../讲透vLLM/)（同一流水线产物）

## 目录结构

```
讲透SGLang/
├── README.md                 ← 本文件（总入口）
├── FINAL-REPORT.md           ← 构建终报（方法论+质量数据）
├── deepwiki/                 ← DeepWiki 110/110 页全量中文抓取（2.0 MB）
│   ├── INDEX.md              ← 全量索引（24 章 110 页，中文对照）
│   ├── 1-overview.md … 24.2-glossary-….md
│   ├── _links.txt            ← 原始 URL 清单（110 条）
│   ├── _coverage-check.md    ← 覆盖率验证（110/110 零遗漏）
│   └── related/              ← 8 个生态仓（flashinfer/nixl/xgrammar/vllm/TRT-LLM/TGI + 2 占位说明）
├── knowledge-graph/          ← /understand --language zh 中文知识图谱
│   ├── knowledge-graph.json  ← 5652 节点 / 12950 边 / 27 层 / 12 步导览（6.0 MB）
│   └── GRAPH-SUMMARY.md      ← 图谱摘要与校验记录
├── onboarding/
│   └── ONBOARDING.md         ← 新人上手指南（27 层架构 + 8 大核心概念 + 请求生命周期 + 14 天学习路径）
└── explain/                  ← 18 篇核心文件深度解析（7590 行）
    ├── sglang-srt-server_args.md            ← 全部服务器参数（能力面总目录）
    ├── sglang-srt-entrypoints-engine.md     ← Engine 子进程编排
    ├── sglang-srt-entrypoints-http_server.md← HTTP 80+ 端点全枚举
    ├── sglang-srt-managers-io_struct.md     ← ZMQ IPC 消息圣经（~90 个消息类）
    ├── sglang-srt-managers-tokenizer_manager.md
    ├── sglang-srt-managers-scheduler.md     ← 调度器心脏（event loop 全解析）
    ├── sglang-srt-managers-schedule_batch.md← Req/ScheduleBatch 全字段
    ├── sglang-srt-model_executor-model_runner.md
    ├── sglang-srt-model_executor-forward_batch_info.md
    ├── sglang-srt-model_executor-cuda_graph_runner.md
    ├── sglang-srt-mem_cache-radix_cache.md  ← RadixAttention 前缀树
    ├── sglang-srt-mem_cache-memory_pool.md  ← KV Cache 内存池
    ├── sglang-srt-speculative-eagle_worker.md← EAGLE 投机解码状态机
    ├── sglang-srt-model_executor-models-llama.md ← 模型实现罗塞塔石碑
    ├── sglang-srt-layers-moe-topk.md        ← MoE TopK 路由
    ├── sglang-srt-layers-dp_attention.md    ← DP Attention 通信组
    ├── sglang-rust-cache_aware.md           ← Rust 缓存感知路由
    └── sglang-rust-worker_manager.md        ← Rust worker 管理
```

## 推荐使用姿势

| 你是谁 | 入口 | 路径 |
|--------|------|------|
| 完全新人 | `onboarding/ONBOARDING.md` | 14 天路径：跑起来 → 请求主干 → 内存缓存 → 算子 → 分布式 → 投机 → 协议 → Rust 面 |
| 想懂某子系统 | `deepwiki/INDEX.md` | 24 章索引直达（如第 5 章内存 / 第 12 章投机解码） |
| 要读源码 | `explain/` | 18 篇逐方法解析，行号锚定本地 commit，改代码前先读对应篇 |
| 要架构全景 | `knowledge-graph/GRAPH-SUMMARY.md` | 27 层 + 12 步导览；json 可喂 dashboard/RAG |
| 做竞品分析 | `deepwiki/related/vllm.md` + 讲透vLLM | vLLM/TRT-LLM/TGI 横向对比 |

## 三个基线事实（防版本漂移误读）

1. **rust workspace 已拆分**：路由/网关代码在仓根 `sgl-model-gateway/` crate（不在 `rust/` 下——那里只剩 sglang-grpc）。
2. **模型文件已迁移**：`srt/model_executor/models/` → `srt/models/`（193 个模型文件）。
3. **forward 分派演进**：模型侧单一 `forward` 入口，graph-vs-eager 分派在 ModelRunner 层，extend-vs-decode 在 attention backend 层。

## 质量声明

- DeepWiki 110/110 页零遗漏（目录树正则提取 + 反向核对，见 `_coverage-check.md`）
- 知识图谱 2026-09-04 校验：0 悬挂边 / 0 层重复 / 0 导览断链 / 中文 100%
- explain 18 篇全部行号实测核对（task 交付时逐条 grep 验证，并修正了 3 处过时认知：模型路径迁移 / forward 分派演进 / Noisy Router 不存在于推理框架）
- 仓内链接 114 条全部有效（自动校验 0 断链）
