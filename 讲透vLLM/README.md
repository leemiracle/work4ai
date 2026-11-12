# 讲透 vLLM · 深度知识库

> 基于 DeepWiki 全量文档 + understand-anything 中文知识图谱 + 核心源码深解的 vLLM 学习知识库。
> 初版 2026-09-03 @ `7894394b` · **增量更新 2026-10-31 @ `06e172b5cf`**（3222 commits 增量：图谱 11615→14454 节点，DeepWiki 74 页全刷新）· **ONBOARDING 重写 + explain 13 篇刷新 2026-11-01**（详见 [FINAL-REPORT.md](FINAL-REPORT.md) 更新章节）。

## 这是什么

一个三层数据源的 vLLM 知识库，服务三类场景：

| 场景 | 用哪部分 | 怎么用 |
|---|---|---|
| 新人系统上手 | `onboarding/ONBOARDING.md`（2026-11-01 重写） | 从头读到尾：项目总览→16 层架构→15 个关键概念→16 步学习路径→文件地图→复杂度热点→两个月演进勘误 |
| 按图索骥查专题 | `deepwiki/`（74 页，2026-10-28 刷新） | 查 `deepwiki/INDEX.md` 索引，按章节号直达（配置/引擎/调度/GPU 执行/量化/注意力/分布式/测试/术语表 + 12 个相关仓库摘要） |
| 啃核心源码 | `explain/`（19 篇：13 篇重写 + api_server 代差重写 + 5 篇新子系统，均 2026-11-01） | 每篇对应一个核心文件/子系统的深度解析：角色定位→内部结构→外部连接→数据流→设计决策→新人提示；行号锚全部 @06e172b5cf 源码核实 |
| 交互式探索 | `knowledge-graph/` | **14454 节点/41124 边**（16 层/16 步导览，2026-10-28 基线）的中文知识图谱，先读 `GRAPH-SUMMARY.md`，再用 understand-anything 插件的 `/understand-chat`、`/understand-dashboard` 在 vLLM 仓交互查询 |

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
│   └── ONBOARDING.md          # 新人上手指南（2026-11-01 重写，不计空格 10846 字符/79 全路径锚）
├── deepwiki/                  # DeepWiki 全量抓取（1.6MB）
│   ├── INDEX.md               # 74 页中文索引（2026-10-28 刷新）
│   ├── 1-overview.md ... 13-glossary.md
│   ├── related/               # 12 个 vllm-project 相关仓库摘要
│   ├── _links.txt / _coverage-check.md / _repo-list.md
├── knowledge-graph/
│   ├── GRAPH-SUMMARY.md       # 图谱摘要（16 层统计）
│   └── knowledge-graph.json   # 完整图谱（2026-10-28 基线 14454n/41124e）
└── explain/                   # 19 篇核心文件/子系统深解
    ├── vllm-config-vllm.md            # VllmConfig 配置中枢
    ├── vllm-engine-arg_utils.md       # EngineArgs 参数体系
    ├── vllm-v1-engine-core.md         # V1 EngineCore 主循环
    ├── vllm-v1-engine-async_llm.md    # AsyncLLM 异步门面
    ├── vllm-v1-core-sched-scheduler.md    # 调度器（vLLM 心脏）
    ├── vllm-v1-core-kv_cache_manager.md   # KV Cache 管理（PagedAttention 核心）
    ├── vllm-v1-kv_cache_interface.md      # KV 接口层：spec 族+量化模式（新）
    ├── vllm-v1-worker-gpu_model_runner.md # GPU ModelRunner（7192 行总指挥，V2 线索见篇内）
    ├── vllm-v1-worker-gpu_worker.md       # GPU Worker
    ├── vllm-v1-worker-gpu_input_batch.md  # InputBatch 批次状态
    ├── vllm-v1-attention-backends-flash_attn.md # FlashAttention 后端
    ├── vllm-parser-abstract_parser.md     # 声明式 tool-call parser 引擎（新）
    ├── vllm-snapshot.md                   # 进程检查点子系统 CRIU+彩排（新）
    ├── rust-server-lib.md                 # Rust 前端 crate 主脊（新）
    ├── vllm-entrypoints-launchers.md      # 新服务入口 launchers 组装链（新）
    ├── vllm-entrypoints-openai-api_server.md    # api_server 垫片代差说明（重写）
    ├── vllm-entrypoints-llm.md                 # 离线推理 LLM 类
    ├── vllm-model_executor-models-llama.md     # Llama 参考实现（模型模板）
    └── vllm-distributed-parallel_state.md      # 分布式并行态
```

## 知识图谱快速统计（2026-10-28 @06e172b5cf）

- **14454 节点**：function 6290 / class 4990 / file 3113 / config 25 / service 13 / document 10 / step 6 / pipeline 5 / schema 2
- **41124 边**：imports 18562 / contains 11248 / exports 9116 / inherits 1733 / calls 310 / depends_on 122 / related 13 / 其他 20
- **16 架构层**：模型实现·厂商新架构(611) / 模型实现·经典注册表与加载(377) / 服务化入口(244) / Rust 前端(218) / MoE 与 Transformer 组件(215) / 分布式并行与 KV 传输(196) / 核心算子与内核库(183) / 多模态、LoRA 与 HF 兼容(183) / V1 Worker 与采样投机(178) / 流式解析与渲染引擎(167) / 注意力与 KV 缓存管理(165) / V1 引擎核心与编译捕获(126) / 量化体系(126) / 平台适配与配置体系(62) / 全局基础与通用工具(82) / 构建与 CI(35)
- **16 步导览**：从项目总览到调优基准的完整请求生命周期故事线

## 数据时效

- DeepWiki 抓取：2026-10-28（74 页 + 相关仓库，全量刷新）
- 知识图谱：2026-10-31（@06e172b5cf，见 GRAPH-SUMMARY.md）
- ONBOARDING / explain：2026-11-01 重写+新写 19 篇（@06e172b5cf；explain 字数口径=不计空格 4635-6397 字符/篇，锚密度 27-111/篇，`_update-20261028/verify_explain.py` 全量终验 0 坏）

---

## 🔗 四层编译管线视角（2026-09-03 补）

模型运行流程的统一抽象（与 PyTorch 共享；vLLM 在 L2-L4 大量集成 torch.compile/Inductor）：

```
L1 Python 定义 ──→ L2 算子图 ──→ L3 算子 ──→ L4 硬件指令
  ch2(配置)/explain-config    ch2.4+3.1(EngineCore)   ch3.3/3.4(调度/KV)+自定义ops   ch4(GPU执行)+10/11.4(JIT)
```

**两仓交汇点**：PyTorch 仓 ch5.5 = vLLM CI。总索引：`/data/usershare/ai/hpc-agent/docs/FOUR-LAYER-PIPELINE.md`（hpc-agent 06 规则库各层已挂本专区锚点）。
