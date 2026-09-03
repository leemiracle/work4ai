# 讲透 vLLM · 深度知识库

> 基于 DeepWiki 全量文档 + understand-anything 中文知识图谱 + 核心源码深解的 vLLM 学习知识库。
> 生成于 2026-09-03，对应 vLLM 源码 commit `$(git -C /data/usershare/ai/vllm rev-parse --short HEAD)`。

## 这是什么

一个三层数据源的 vLLM 知识库，服务三类场景：

| 场景 | 用哪部分 | 怎么用 |
|---|---|---|
| 新人系统上手 | `onboarding/ONBOARDING.md` | 从头读到尾：项目总览→16 层架构→15 个关键概念→14 步学习路径→文件地图→复杂度热点 |
| 按图索骥查专题 | `deepwiki/`（64 页） | 查 `deepwiki/INDEX.md` 索引，按章节号直达（配置/引擎/调度/GPU 执行/量化/注意力/分布式/测试/术语表 + 12 个相关仓库摘要） |
| 啃核心源码 | `explain/`（14 篇） | 每篇对应一个核心文件的深度解析：角色定位→内部结构→外部连接→数据流→设计决策→新人提示 |
| 交互式探索 | `knowledge-graph/` | 11615 节点/33598 边的中文知识图谱，先读 `GRAPH-SUMMARY.md`，再用 understand-anything 插件的 `/understand-chat`、`/understand-dashboard` 在 vLLM 仓交互查询 |

## 推荐阅读路径

```
ONBOARDING.md（2h，全局观）
   ↓ 挑 3-5 个感兴趣的层
deepwiki/ 对应章节（每章 30-60min）
   ↓ 遇到想深挖的核心文件
explain/ 对应深解（每篇 20-30min）
   ↓ 想动手改代码时
knowledge-graph/ 交互探索依赖关系
```

## 目录结构

```
讲透vLLM/
├── README.md                  # 本文件
├── FINAL-REPORT.md            # 生成过程报告（含裁剪说明）
├── onboarding/
│   └── ONBOARDING.md          # 新人上手指南（4600 字）
├── deepwiki/                  # DeepWiki 全量抓取（1.6MB）
│   ├── INDEX.md               # 62 页中文索引
│   ├── 1-overview.md ... 13-glossary.md
│   ├── related/               # 12 个 vllm-project 相关仓库摘要
│   ├── _links.txt / _coverage-check.md / _repo-list.md
├── knowledge-graph/
│   ├── GRAPH-SUMMARY.md       # 图谱摘要（16 层统计）
│   └── knowledge-graph.json   # 完整图谱（11.5MB）
└── explain/                   # 14 篇核心文件深解
    ├── vllm-config-vllm.md            # VllmConfig 配置中枢
    ├── vllm-engine-arg_utils.md       # EngineArgs 参数体系
    ├── vllm-v1-engine-core.md         # V1 EngineCore 主循环
    ├── vllm-v1-engine-async_llm.md    # AsyncLLM 异步门面
    ├── vllm-v1-core-sched-scheduler.md    # 调度器（vLLM 心脏）
    ├── vllm-v1-core-kv_cache_manager.md   # KV Cache 管理（PagedAttention 核心）
    ├── vllm-v1-worker-gpu_model_runner.md # GPU ModelRunner（7717 行总指挥）
    ├── vllm-v1-worker-gpu_worker.md       # GPU Worker
    ├── vllm-v1-worker-gpu_input_batch.md  # InputBatch 批次状态
    ├── vllm-v1-attention-backends-flash_attn.md # FlashAttention 后端
    ├── vllm-entrypoints-openai-api_server.md    # OpenAI 兼容 API 服务
    ├── vllm-entrypoints-llm.md                 # 离线推理 LLM 类
    ├── vllm-model_executor-models-llama.md     # Llama 参考实现（模型模板）
    └── vllm-distributed-parallel_state.md      # 分布式并行态
```

## 知识图谱快速统计

- **11615 节点**：file 2226 / class 4620 / function 4750 / config 16 / document 3
- **33598 边**：imports 13102 / contains 9370 / exports 8268 / inherits 1937 / calls 746 / implements 87 / depends_on 54 / 其他 134
- **16 架构层**：模型实现(516) / 服务入口(234) / 计算层(264) / 量化与MoE(214) / 分布式(145) / 共享基础设施(142) / 注意力后端(130) / GPU执行(124) / Rust前端(99) / V1引擎核心(80) / 工具调用(70) / 多模态(66) / 图编译(51) / 调度与KV(49) / 配置(41) / 平台适配(20)
- **14 步导览**：从项目总览到调优基准的完整请求生命周期故事线

## 数据时效

- DeepWiki 抓取：2026-09-02（62 子页 + 相关仓库）
- 知识图谱：2026-09-03（对应 vLLM 主分支 commit，见 GRAPH-SUMMARY.md）

---

## 🔗 四层编译管线视角（2026-09-03 补）

模型运行流程的统一抽象（与 PyTorch 共享；vLLM 在 L2-L4 大量集成 torch.compile/Inductor）：

```
L1 Python 定义 ──→ L2 算子图 ──→ L3 算子 ──→ L4 硬件指令
  ch2(配置)/explain-config    ch2.4+3.1(EngineCore)   ch3.3/3.4(调度/KV)+自定义ops   ch4(GPU执行)+10/11.4(JIT)
```

**两仓交汇点**：PyTorch 仓 ch5.5 = vLLM CI。总索引：`/data/usershare/ai/hpc-agent/docs/FOUR-LAYER-PIPELINE.md`（hpc-agent 06 规则库各层已挂本专区锚点）。
