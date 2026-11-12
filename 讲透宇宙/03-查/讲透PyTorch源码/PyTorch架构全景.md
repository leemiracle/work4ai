# PyTorch 架构全景（2026-09 版）

> **文档来源三重交叉验证**：DeepWiki pytorch/pytorch 全量 80 页（indexed 2026-09-02 @ `580b06`）× 本地仓库源码（`/data/usershare/pytorch` @ `f634d0e`）× understand 知识图谱（637 文件 / 4730 节点 / 10744 边）。
> 本文档是「讲透PyTorch源码」系列的架构总纲，细节请下钻 `deepwiki/`（按页）与 `重要文件讲解/`（按文件）。

---

## 0. 一图流：从 `torch.compile` 到 GPU kernel

```
用户 Python 代码 (nn.Module + Tensor ops)
        │
        ▼ PEP 523 帧求值挂钩
┌──────────────────────────────────────────────────────────┐
│ TorchDynamo 前端 (torch/_dynamo, 86 文件)                 │
│   eval_frame.py → convert_frame.py → variables/*         │
│   字节码 ──符号执行──▶ FX Graph + Guards                  │
└──────────────────────────────────────────────────────────┘
        │ FX Graph（公共 IR：torch/fx/graph.py）
        ▼
┌──────────────────────────────────────────────────────────┐
│ 规范化层                                                  │
│   FakeTensorMode (_subclasses/fake_tensor.py) 元数据推演 │
│   Functionalization (functional_tensor.py) 消除 mutation │
│   torch.export → ExportedProgram + SymInt 动态形状       │
└──────────────────────────────────────────────────────────┘
        │
        ▼ AOTAutograd 联合前后向追踪（joint graph → min-cut 切分）
┌──────────────────────────────────────────────────────────┐
│ TorchInductor 后端 (torch/_inductor, 35 核心文件)         │
│   fx_passes(pre/joint/post) → ir.py lowering →           │
│   scheduler.py fusion → Triton/C++ codegen → codecache   │
└──────────────────────────────────────────────────────────┘
        │ 生成的 kernel
        ▼
┌──────────────────────────────────────────────────────────┐
│ 运行时：Dispatcher (ATen core/dispatch) ──DispatchKeySet──▶│
│   CUDA kernel / MPS Metal / XPU / CPU (aten/src/ATen/*)  │
│   CUDACachingAllocator 管显存 · autograd 引擎跑反向      │
└──────────────────────────────────────────────────────────┘
```

不 compile 时（eager 模式）：`torch.add` → `torch/_ops.py` → `at::_ops::add_Tensor::call` → Dispatcher 按 key 选 kernel；autograd key 先录反向图再 redispatch 到后端 kernel。

---

## 1. 分层架构（知识图谱 15 层实证划分）

| # | 层 | 文件数 | 一句话 |
|---|---|---|---|
| 1 | nn 神经网络模块 | 40 | Module 体系 + 标准层 + attention（flex_attention/_fa3/_fa4） |
| 2 | 优化器与学习率调度 | 22 | SGD/Adam(W)/lr_scheduler |
| 3 | 张量核心与 C++ 调度 | 38 | Python Tensor 门面 + ATen Dispatcher + c10 基础类型 |
| 4 | C++ 核心绑定 (torch/csrc) | 39 | pybind 绑定 + autograd 引擎 + dynamo C 层 |
| 5 | TorchDynamo 编译前端 | 86 | 字节码捕获 + VariableTracker + guards |
| 6 | FX 中间表示 | 29 | Graph/Node/Tracer + symbolic_shapes |
| 7 | 导出与张量子类机制 | 28 | export 管线 + FakeTensor + FunctionalTensor |
| 8 | Inductor 编译后端 | 35 | IR/lowering/scheduler/codegen/autotune/缓存 |
| 9 | CUDA 计算栈 | 90 | ATen CUDA + TensorIterator + 缓存分配器 + torch.cuda |
| 10 | MPS/XPU 异构设备后端 | 40 | Apple Metal + Intel GPU |
| 11 | 分布式训练 | 99 | c10d → DeviceMesh → DTensor → FSDP + symm-mem + checkpoint |
| 12 | 量化 (torch/ao) | 24 | PT2E/QAT + Observer/FakeQuant |
| 13 | ONNX 导出 | 24 | dynamo 新导出器 + TorchScript 旧导出器 |
| 14 | 性能剖析 | 8 | Kineto + chrome trace + 内存剖析 |
| 15 | 代码生成与构建 | 35 | torchgen + native_functions.yaml + 构建 |

---

## 2. 六大子系统深读索引

### 2.1 编译栈（DeepWiki ch2，24 页 → 图谱层 5-8）
- **总览**：`deepwiki/2.1-torch-compile-pipeline.md`
- **Dynamo 三部曲**：帧求值（2.2.1）→ 变量追踪（2.2.2，28 个 VariableTracker 文件全解析）→ guards 与重编译（2.2.3）
- **export**：ExportedProgram（2.3.1）→ SymInt 符号形状（2.3.2）→ FakeTensor（2.3.3）
- **AOTAutograd**：联合追踪与 functionalization（2.4/2.4.1）+ autograd 缓存（2.4.2）
- **Inductor**：IR 与 lowering（2.5.1）→ fusion 调度（2.5.2）→ autotune（2.5.3）→ Triton/CUTLASS/Pallas 代码生成（2.5.4）→ 编译缓存（2.5.5）
- **文件级深讲**：`重要文件讲解/04-Dynamo-eval_frame`、`05-FakeTensor`、`06-Inductor-compile_fx`、`10-FX-Graph`

### 2.2 调度与算子系统（DeepWiki ch3，12 页 → 图谱层 3/4）
- **核心链路**：native_functions.yaml（~2000 算子单一事实源）→ torchgen 生成 → Dispatcher 按 DispatchKeySet 查表
- **文件级深讲**：`02-Dispatcher-算子调度核心`（含 torch.add 全链路追踪）、`08-TensorImpl-Cpp张量内核`
- **测试**：OpInfo 框架驱动全算子 × 全 dtype × 全设备矩阵（3.1.2）

### 2.3 autograd（跨 DeepWiki 2.4 / 图谱层 4）
- 前向录图（Autograd key kernel）→ `engine.cpp` 就绪队列拓扑排序反向执行
- **文件级深讲**：`03-autograd-engine-反向传播引擎`（GraphTask 生命周期/多线程/流同步）

### 2.4 分布式（DeepWiki ch4，18 页 → 图谱层 11）
- **金字塔**：ProcessGroup(c10d) → DeviceMesh → DTensor(placement/Shard/Replicate + OpStrategy 分片传播) → FSDP(1.x fully_sharded_data_parallel / 2.x _fully_shard)
- **新前沿**：Symmetric Memory（NVSHMEM/NCCL 后端，4.3 章）——推理时代的高速通信
- **文件级深讲**：`07-distributed_c10d-分布式通信塔基`

### 2.5 设备后端（DeepWiki ch3.2-3.4 → 图谱层 9/10）
- CUDA：CUDACachingAllocator（3.2.1，内存池/碎片治理）+ CUDA Graphs（3.2.2）+ cuBLAS（3.2.3）
- MPS/XPU：表驱动调度的扩展示范——新设备只需注册 DispatchKey + kernels

### 2.6 专业化方向（DeepWiki ch7-10 → 图谱层 12-14）
- **推理运行时**：AOTI/NativeRT（7/7.1）——torch.export 产物编译成 .so，脱离 Python 运行
- **量化**：PT2E（8.1）与 eager FX-graph-mode（8.2）
- **ONNX**：新旧两代导出器并存（9.1 legacy TorchScript / 9.2 dynamo+onnxscript）
- **Profiler**：Kineto + CUPTI + MemoryViz（10/10.1/10.2）

---

## 3. 本地仓库 vs DeepWiki 版本差异（重要勘误）

抓取与图谱构建中发现本地 HEAD（`f634d0e`，main）与 DeepWiki 索引版（`580b06`）的结构差异，阅读 DeepWiki 时注意：

| DeepWiki 表述 | 本地仓库实际（f634d0e） |
|---|---|
| DTensor 在 `torch/distributed/dtensor/` | 已迁移为 `torch/distributed/_tensor/`（实现）+ `torch/distributed/tensor/`（公共 API + _ops/ 分片策略，16 文件） |
| Pipeline parallelism 路径 | 本地为 `torch/distributed/pipelining/`（注意 -ing） |
| `torch/csrc/dynamo/` 独立目录描述 | 存在（eval_frame.c/cache_entry/guards.cpp），但 autograd 的 compiled_autograd 也在其中 |
| FSDP2 作为独立章 | 本地 fsdp2 已并入 `fsdp/_fully_shard/`（9 文件） |
| ATen `dispatch/` 子目录 | 已并入 `aten/src/ATen/core/dispatch/` |
| `torch/distributed/fsdp/_fully_shard` 中 `al`（async llm） | 未见独立 `al/` 目录；DeepWiki 若提及 al 均为 580b06 之后或之前的状态 |

**结论**：DeepWiki 适合当「架构叙事」，本地代码以本仓库为准；本目录 understand 图谱即本地版的权威结构快照。

---

## 4. 怎样使用这套资料（阅读动线）

```
第一遍（1周）：ONBOARDING.md → 本文档 → deepwiki/1-overview + 2.1 + 3.1.1
第二遍（2周）：重要文件讲解 01-05（入口/调度/autograd/Dynamo/FakeTensor）
              对照 deepwiki ch2 相应页
第三遍（按需）：06-10（Inductor/c10d/TensorImpl/Module/FX）+ ch3/ch4 深读
工具：understand/knowledge-graph.json 用 /understand-dashboard 交互浏览
      （在 /data/usershare/pytorch 下启动；图谱绑定本地 commit f634d0e）
```

---

## 5. 质量声明

- DeepWiki 80/80 页全量抓取（566KB），无缺页，含行号级 source 引用
- 图谱 637 文件覆盖 15 层，验证 0 issues（节点/边/层/tour 全约束通过）
- 10 篇重要文件讲解全部基于本地源码精读，行号实测核对
- 三处来源冲突已在上表勘误
