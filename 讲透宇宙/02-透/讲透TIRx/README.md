# 讲透 TIRx · 深度知识库

> 基于 understand-anything 中文知识图谱 + 核心源码深解的 TIRx-kernels 学习知识库。
> 生成于 2026-09-04，对应源码 commit `f72461b`（2026-09-03）。

## 这是什么

TIRx-kernels 是 mlc-ai 的 GPU kernel 合集与调度库：以 TVM TIR 作为 kernel 表示，统一注册、调度并运行 flash-attention / cuDNN / FlashInfer / DeepGEMM / DeepEP 等多个上游 kernel 源，为 MLC 生态提供高性能算子层。本知识库服务于三类场景：

| 场景 | 用哪部分 | 怎么用 |
|---|---|---|
| 新人系统上手 | `onboarding/ONBOARDING.md` | 从头读：项目总览→14 层架构→15 个关键概念→15 步学习路径→文件地图→复杂度热点 |
| 啃核心源码 | `explain/`（12 篇） | 每篇一个核心文件的深度解析：角色定位→内部结构→外部连接→数据流→设计决策→新人提示 |
| 交互式探索 | 知识图谱（仓内） | 2973 节点/4865 边/14 层/15 步导览全中文图谱，位于 `~/ai/TIRx-kernels/.understand-anything/knowledge-graph.json`，用 understand-anything 插件 `/understand-chat`、`/understand-dashboard` 交互查询 |

> 注：DeepWiki 未收录 TIRx-kernels（探测确认为未索引状态），本仓知识库以 understand 图谱为主力数据源。

## 目录结构

```
讲透TIRx/
├── README.md                  # 本文件
├── onboarding/
│   └── ONBOARDING.md          # 新人上手指南（4200 字，14 节，源码交叉验证）
└── explain/                   # 12 篇核心文件深解
    ├── tirx-kern-dsl.md           # Kern DSL 总纲（fan-in 105 全库最高）
    ├── tirx-registry.md           # KERNEL_META 注册协议（tokenize 零导入）
    ├── tirx-runner.md             # 统一运行器/测试 CLI（fan-in 35）
    ├── tirx-protocol.md           # KernelModule Protocol 类型基础
    ├── tirx-bench-run.md          # 基准编排核心（2612 行：GpuPool 世代化+pinned sweep）
    ├── tirx-bench-ab.md           # 同 GPU 配对 A/B 实验
    ├── tirx-ratio-diff.md         # 基线比值检查（1.01 门禁）
    ├── tirx-low-level-ir.md       # 低层 IR 契约校验（no-tile violation）
    ├── tirx-basic-gemm.md         # 原生 kernel 代表（TMA+2-SM MMA+CLC）
    ├── tirx-cudnn-bsa.md          # cuDNN 移植代表（块稀疏注意力）
    ├── tirx-flashinfer-gdn.md     # FlashInfer 移植代表（GDN 线性注意力）
    └── tirx-msa-atten.md          # MSA 稀疏注意力（3564 行最难 kernel）
```

## 推荐阅读路径

```
ONBOARDING.md（1h，全局观）
   ↓ 挑感兴趣的模块
explain/ 基础设施四篇（kern-dsl → registry → runner → protocol）
   ↓ 基准体系三篇（bench-run → bench-ab → ratio-diff）
explain/ kernel 家族四篇（basic-gemm → cudnn-bsa → flashinfer-gdn → msa-atten）
   ↓ 想动手时
知识图谱交互探索（understand-chat / understand-dashboard）
```

## 生成方式

- 图谱：understand-anything 流水线（scan 532 文件 → 48 批 file-analyzer 5 并发 → merge 2973 节点/4865 边 → 14 层 architecture-analyzer → 15 步 tour-builder → 校验 0 issues → fingerprints 基线）
- 指南与深解：全部基于图谱 + 源码只读交叉验证（wc -l 行号实测）
