# 讲透 WebLLM · 深度知识库

> 基于 DeepWiki 全量文档 + understand-anything 中文知识图谱 + 核心源码深解的 WebLLM 学习知识库。
> 生成于 2026-09-05，对应源码 commit `56d318c`（2026-09-02）。

## 这是什么

WebLLM 是浏览器内原生 LLM 推理引擎：基于 WebGPU 与 Apache TVM 的 MLC 技术栈，将模型编译为 WebAssembly/WebGPU kernel 在浏览器本地运行，OpenAI 兼容 API，支持流式生成/结构化输出/embedding/多模型服务，TypeScript 实现。

| 场景 | 用哪部分 | 怎么用 |
|---|---|---|
| 新人系统上手 | `onboarding/ONBOARDING.md` | 项目总览→11 层架构→14 个关键概念→15 步学习路径 |
| 按图索骥查专题 | `deepwiki/`（25 页） | 查 `deepwiki/INDEX.md` |
| 啃核心源码 | `explain/`（5 篇） | engine / llm_chat / config / web_worker / openai-protocol |
| 交互式探索 | 知识图谱（仓内） | 395 节点/574 边/11 层/15 步导览，`~/ai/web-llm/.understand-anything/knowledge-graph.json` |

## 目录结构

```
讲透WebLLM/
├── README.md
├── deepwiki/                  # DeepWiki 抓取（25 页 + INDEX + 覆盖率检查）
├── onboarding/ONBOARDING.md  # 新人指南（4085 字，8 节）
└── explain/                   # 5 篇核心深解
    ├── webllm-engine.md          # MLCEngine 门面（1432 行）
    ├── webllm-llm-chat.md        # 推理管线（2298 行：prefill/decode/KVCache/采样）
    ├── webllm-config.md          # 模型目录（2607 行 prebuiltAppConfig）
    ├── webllm-web-worker.md      # Worker RPC（844 行三态通信）
    └── webllm-openai-protocol.md # OpenAI 兼容协议四件套
```

## 生成方式

- DeepWiki 25 页 100% + understand 流水线（236 文件→21 批→395 节点/574 边→11 层→15 tour→0 issues→fingerprints）
- 指南与深解：图谱+源码只读交叉验证
