# 讲透PyTorch源码 —— PyTorch 源码深度学习专区

> 创建：2026-09-03 ｜ 源仓库：`/data/usershare/pytorch`（HEAD `f634d0e`, main）
> 数据源：DeepWiki pytorch/pytorch 全量 80 页（@580b06，2026-09-02 索引）+ understand 知识图谱（637 文件/4730 节点）+ 10 篇源码精读

## 📚 目录导航

| 资产 | 路径 | 说明 |
|---|---|---|
| **新人上手指南** ⭐ | `ONBOARDING.md` | 架构说明 + 核心模块 + 14 步推荐学习路径（含 DeepWiki 章节映射） |
| **架构总纲** ⭐ | `PyTorch架构全景.md` | 一图流 + 15 层架构 + 6 大子系统深读索引 + 版本勘误 |
| **DeepWiki 全量** | `deepwiki/`（80 个 .md，566KB） | pytorch/pytorch wiki 逐页抓取，含 Relevant source files 行号引用 |
| **重要文件讲解** | `重要文件讲解/`（10 篇） | 每篇 200-400 行源码级精读，行号实测 |
| **知识图谱** | `understand/knowledge-graph.json`（3.9MB） | 15 层 + 14 步 tour + 4730 节点，中文摘要；配 `understandignore-whitelist.txt` |

## 📖 deepwiki/ 章节索引（80 页）

- **ch1 概览**（3 页）：1 overview · 1.1 getting-started · 1.2 repository-map
- **ch2 编译系统**（24 页）：2 · 2.1 compile流水线 · 2.2 Dynamo（2.2.1-2.2.3）· 2.3 export（2.3.1-2.3.3）· 2.4 AOTAutograd（2.4.1-2.4.2）· 2.5 Inductor（2.5.1-2.5.6）· 2.6 高阶算子 · 2.7 FX（2.7.1-2.7.2）
- **ch3 设备后端**（12 页）：3 · 3.1 ATen（3.1.1 注册调度 · 3.1.2 OpInfo）· 3.2 CUDA（3.2.1 分配器 · 3.2.2 CUDA Graphs · 3.2.3 BLAS）· 3.3 MPS（3.3.1）· 3.4 XPU · 3.5 attention
- **ch4 分布式**（18 页）：4 · 4.1 c10d（4.1.1 ProcessGroup · 4.1.2 Reducer/DDP）· 4.2 DTensor（4.2.1-4.2.5）· 4.3 Symmetric Memory（4.3.1-4.3.2）· 4.4 FSDP（4.4.1-4.4.2）· 4.5 pipeline · 4.6 checkpoint
- **ch5 构建测试**（6 页）：5 · 5.1 构建与codegen · 5.2 测试与OpInfo · 5.3 CI/CD · 5.4 二进制发布 · 5.5 vLLM CI
- **ch6 代码生成**（4 页）：6 · 6.1 torchgen · 6.2 自定义算子 · 6.3 AOTI C shim
- **ch7 推理运行时**（3 页）：7 · 7.1 NativeRT · 7.2 序列化
- **ch8 量化**（3 页）：8 · 8.1 PT2E/QAT · 8.2 eager
- **ch9 ONNX**（3 页）：9 · 9.1 TorchScript 版 · 9.2 torch.export 版
- **ch10 性能剖析**（3 页）：10 · 10.1 Kineto · 10.2 内存可视化
- **ch11 术语表**（1 页）：11

## 📖 重要文件讲解（10 篇）

1. `01-torch-入口-init.md` — import torch 的 13 阶段装配时序
2. `02-Dispatcher-算子调度核心.md` — DispatchKeySet 查表 + torch.add 全链路
3. `03-autograd-engine-反向传播引擎.md` — 就绪队列拓扑排序 + 多线程/流同步
4. `04-Dynamo-eval_frame-编译前端入口.md` — PEP 523 + guards 缓存
5. `05-FakeTensor-元数据推演.md` — __torch_dispatch__ + SymInt 集成
6. `06-Inductor-compile_fx-编译后端总入口.md` — fx_passes 三段式 + 四态缓存
7. `07-distributed_c10d-分布式通信塔基.md` — init_process_group + 集合通信包装
8. `08-TensorImpl-Cpp张量内核.md` — intrusive_ptr + key_set_ + 版本计数器
9. `09-nn-Module-神经网络基类.md` — __setattr__ 注册魔法 + hook 编排
10. `10-FX-Graph-公共中间表示.md` — 链表式 DAG + 源码再生成

## 🔧 图谱使用

```bash
# 交互式浏览（在 pytorch 仓库目录下）
cd /data/usershare/pytorch
# 然后运行 /understand-dashboard（understand-anything 插件）
# 图谱位置: .understand-anything/knowledge-graph.json（与本目录副本同源）

# 增量更新图谱
cd /data/usershare/pytorch && /understand   # 自动检测 f634d0e 之后的变更
```

## ⚠️ 阅读须知

- DeepWiki 内容对应 commit `580b06`（2026-09-02 索引），本地仓库是 `f634d0e`——结构差异已在 `PyTorch架构全景.md` §3 勘误表列明（DTensor 目录迁移、pipelining 命名等 6 项）
- 所有讲解保留英文技术术语（Dispatcher/guard/kernel 等），遵循 GLOSSARY.md 术语规范
- 图谱白名单 637 文件聚焦架构核心（非全仓 21,682 文件），覆盖 DeepWiki ch2-ch10 全部章节对应的代码路径

---

## 🔗 四层编译管线视角（2026-09-03 补）

模型运行流程的统一抽象（与 vLLM 共享，**hpc-agent 项目总索引**：`/data/usershare/ai/hpc-agent/docs/FOUR-LAYER-PIPELINE.md`）：

```
L1 Python 定义 ──→ L2 算子图 ──→ L3 算子 ──→ L4 硬件指令
   ch1+精读01/09     ch2(Dynamo/export/FX)   ch2.4/3.1/6(torchgen)   ch2.5(Inductor)+3.2(CUDA)
```

本专区 80 页 = 这条管线的源码级展开；hpc-agent 的 06 规则库 L1-L4 层与本管线一一对应（其 README 已补"深读资产锚点"列，规则卡 schema v0.2 增 `deepwiki_ref` 字段）。
