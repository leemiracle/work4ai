# 10 · PyTorch 内核精读

> 本文综合精读 PyTorch 核心开发者 **Edward Yang (ezyang)** 博客 + **Kieran Didi** 源码追踪 + **Christian Perone** 编译栈 + 官方导览（详见各节出处标注），用**一根主线**把 PyTorch 内核串成一个可深入理解的整体。
>
> **主线论点：PyTorch 的整个架构可以用「分派（dispatch）」这一根线串起来**——数据层靠三元组决定分派、调度层靠 dispatch key 统一所有横切关注点、算子层靠 codegen 消灭组合爆炸、autograd/编译/分布式都是在分派机制上叠加的"层"。

---

## 一、数据层：Tensor / Storage / stride（出处：ezyang "PyTorch internals"）

### 1.1 stride 是 view 的灵魂
张量是 n 维数学对象，但内存是一维的。PyTorch 用 **stride（步幅）** 摊平：

$$
\text{物理偏移} = \text{offset} + \sum_i \text{索引}[i] \times \text{stride}[i]
$$

stride 的杀手锏：**view（零拷贝视图）的基础**。取一行改 offset、取一列改 stride、transpose/permute 全是改 `sizes + strides + offset` 而**不动数据**。这是 eager 风格灵活、内存高效的根基。

**代价**：非连续张量在 kernel 里慢（cache 不友好、难向量化），需 `.contiguous()`；共享 storage 改 view 会改原 tensor（生命周期坑，需 `.clone()` 断开）。

### 1.2 Tensor ↔ Storage 解耦
```
Storage = dtype + 物理内存
Tensor  = 指向 Storage + sizes + strides + offset（逻辑解释）
```
即使 `torch.zeros(2,2)` 也是 Tensor-Storage 成对。ezyang 当时预告要消除独立 Storage（让 view = "由 base tensor 支撑的 tensor"），这正是后续演进方向。

### 1.3 扩展三元组：device / layout / dtype
一个张量"是什么"由三个**正交维度**的笛卡尔积穷举：

| 维度 | 含义 | 判别 |
|------|------|------|
| **device** | 数据存哪（CPU/CUDA/XLA）| 每个 device 独立 allocator |
| **layout** | 如何解释内存（strided/sparse/blocked）| sparse 用 (indices,values) |
| **dtype** | 元素类型（float/int/量化）| 含非平凡类型 |

**第四条路**：不该改三元组时，写包装类（如 `nn.Parameter`）。判别黄金测试：**该张量要在 autograd 反向中当梯度传吗？需要→真扩展；不需要→包装类**。

> 🎯 这三元组直接决定了张量会被**分派**到哪个后端 kernel——是后面所有 dispatch 机制的输入。

---

## 二、算子层：从 yaml 到 BLAS kernel（出处：Kieran Didi；ezyang "PyTorch internals"）

### 2.1 为什么算子"藏得那么深"
找 `torch.nn.Linear` 的实现很痛苦，两个原因：① **dispatcher 动态分发**（CPU/CUDA/MPS 各有不同 kernel）；② **codegen 生成**（很多代码不在仓库里，构建时自动生成）。所以读源码的入口**不是 grep 函数名，而是先读 `native_functions.yaml`**。

### 2.2 native_functions.yaml —— 算子的"单一事实源"
`aten/src/ATen/native/native_functions.yaml` 用 YAML 描述每个算子的元数据，被 codegen 消费。`addmm` 的记录：

```yaml
- func: addmm(Tensor self, Tensor mat1, Tensor mat2, *, Scalar beta=1, Scalar alpha=1) -> Tensor
  structured_delegate: addmm.out    # functional 版委托给 .out 实现
  variants: function, method        # 生成 at::addmm() 和 tensor.addmm()
  dispatch:                         # ← 这就是 dispatcher 路由依据!
    SparseCPU: addmm_sparse_dense_cpu
    SparseCUDA: addmm_sparse_dense_cuda
```

- **三种变体**：`op`（functional）/ `op_`（in-place，codegen 自动生成）/ `op_out`（out-of-place，真正主力）。
- **`dispatch:` 映射表**：每个 backend key → 具体 kernel 函数名。一个算子要写 **(变体 × backend)** 份实现 = 海量 boilerplate，**这就是 codegen 存在的根因**。

### 2.3 Structured Kernels（2021，RFC-0005）—— 现代算子定义范式
`structured: True` 让每个算子**只需写两样**：
1. **meta 函数**（`TORCH_META_FUNC`）：shape 检查/推断，不碰数据；
2. **impl 函数**（`TORCH_IMPL_FUNC`）：针对 `.out` 写实际计算。

其余（functional/in-place 变体、跨 backend 样板）全由 codegen 自动生成。`structured_delegate: addmm.out` 表示 functional 版别自己写，委托给 `.out`。

> **设计哲学**：把"算子语义(schema)+分发表"留在 yaml 一处真相源，"shape 推断"和"计算"分离，让 codegen 负责一切粘合。

### 2.4 一条完整路径：addmm 从调用到 BLAS
```
torch.addmm(...)                              # Python API
  → at::addmm(...)  [codegen 生成, Functions.h]
    → at::_ops::addmm_out::call(...)          # codegen 生成的 ops 结构体
      → Dispatcher 按 dispatch key 路由
        → TORCH_META_FUNC(addmm): shape 检查 + 推断输出形状(不分配)
        → TORCH_IMPL_FUNC(addmm_out_cpu):     # CPU
            addmm_impl_cpu_() → cpublas::gemm(...)   # ← 终点: 一次 BLAS 调用
        → TORCH_IMPL_FUNC(addmm_out_cuda):    # CUDA
            addmm_out_cuda_impl() → at::cuda::blas::gemm/bgemm(...)
```

> 💡 **剥开层层 wrapper、shape check、dtype dispatch、硬件特判，算子的真正"核心计算"最终仍是一次 BLAS 库调用**。PyTorch 的复杂度几乎全在"如何把这一次调用安全、高效、跨 backend 地包起来"。

### 2.5 读源码方法论（实操）
1. 先查 `native_functions.yaml` 找 `func:`，看 `structured`/`structured_delegate`/`dispatch`/`variants`。
2. functional 版常 `structured_delegate` 到 `.out`，真正实现在那。
3. `git grep "<op>"` 在 `aten/src/ATen/native/`，认准 `TORCH_META_FUNC`（shape）和 `TORCH_IMPL_FUNC(_cpu/_cuda)`（计算）。CPU 在 `LinearAlgebra.cpp` 类，CUDA 在 `cuda/Blas.cpp` 类。
4. 别在三套 codegen 线里迷路：① 算子层 yaml→codegen（现代）；② 旧 cwrap/generic builds（考古，已被①取代）；③ L2 Dynamo/Inductor（图级，在①之上）。

---

## 三、调度层：dispatcher 深度（出处：ezyang "Let's talk about the PyTorch dispatcher"）

> 这是全文的**枢纽**。dispatcher 表面是"根据张量属性选 kernel"的 glorified if，但 ezyang 的核心论点：**它是 PyTorch 内部代码组织的核心抽象，把所有横切关注点解耦成可组合的层**。

### 3.1 Dispatcher = 每个算子一张函数指针表
对每个算子维护一张表：**dispatch key → 函数指针**。dispatch key 粗略对应一个横切关注点（CPU/CUDA/XLA/Autograd/Tracing...）。dispatcher 算出该用哪个 key，间接跳转。

**与 C++ vtable 的本质区别**：

| 维度 | C++ vtable | PyTorch dispatcher |
|------|-----------|-------------------|
| 表的归属 | **每个类**一张 | **每个算子**一张 |
| 扩展方向 | 易加子类，难加虚方法 | **易加算子**（新表），难加 dispatch key（改 core）|
| 分派依据 | 只看 this（单分派）| **看所有参数 + 线程局部状态 TLS**（多分派）|

PyTorch 选"每算子一张表"——因为主要扩展是**定义新算子**，让"加算子"便宜符合需求。

### 3.2 Dispatch key set —— 用 bitset 算该走哪条路
```
最终 key set = (∪ 各 tensor 输入的 key set) ∪ (local include set, TLS) ∪ (global set)
             − (local exclude set, TLS)
取优先级最高的 key → 跳转
```
**经典模式**：handler 处理完某 key 后，把自己加进 `exclude set`，防止后续重复处理。

**Autograd 例**（最典型）：顶层 Autograd 在 global，dispatch 选它 → autograd handler 记录计算图，并用 RAII guard 把 Autograd 加进 exclude set → redispatch 时 Autograd 被 exclude，跳过它 → 落到 CPU handler → 整个调用树绕过 autograd → 函数返回 guard 析构恢复。

> 这就是"autograd 只在最外层触发一次、内部不再重复"的机制本质——**靠 TLS exclude set 实现"处理一次后屏蔽"**。

### 3.3 三种算子注册（网格视角）
| 注册方式 | 填什么 | 优先级 |
|---------|--------|--------|
| 为某算子在某 key 注册 kernel | 一个格子 | 最高（exact）|
| catch-all kernel（所有 key 同一实现）| 一整行 | 中（罕见，移除中）|
| fallback（某 key 所有算子同一实现）| 一整列 | 最低 |

**fallback 的价值**：后端只需写一个泛型 fallback 就支持所有算子（哪怕没逐个实现）——这是后端快速接入的基础。

### 3.4 Boxing / Unboxing —— 让一份 kernel 跑遍所有算子
- **`IValue`（双字：payload + tag）**是装箱表示，让一份 boxed kernel 能处理所有算子。
- 两种调用约定：unboxed（C++ 直接，用户从 C++ API 来 fastpath）vs boxed（IValue 栈，JIT/fallback 来）。
- C++ 模板自动生成 boxing/unboxing adapter 桥接两者。

> 没有这套机制，就无法让人写**一个** boxed kernel 跑遍所有算子（过去只能靠 codegen 给每个算子生成重复 kernel）。

### 3.5 dispatcher 统一了一切（全文高潮）
**PyTorch 的所有横切关注点——autograd、tracing、vmap、量化、各后端——都被统一建模成 dispatcher 表上的一行行 dispatch key**：

- **Tensor** 贡献 dispatch key（device/dtype/layout/autograd）。
- **Autograd** = 一个 dispatch key + 进入 handler 后自我屏蔽。
- **后端（CPU/CUDA/XLA）**= backend dispatch key 上的 kernel 注册。
- **torch.compile / vmap / tracing** = 本质都是"注册一组 dispatch key + handler"。

理解了 dispatcher，就理解了 PyTorch 为什么能让这些功能**正交组合**（autograd + CUDA + vmap 同时生效），以及为什么组合顺序重要。

---

## 四、autograd 内核：反向图与 mutation（出处：ezyang "Autograd and Mutation"；配实验01 手写引擎）

### 4.1 基本机制：前向记账，反向算账
前向时每个运算生成反向节点 `OpBackward`，挂在结果 tensor 的 `grad_fn`。叶子节点有隐藏的 `AccumulateGrad`（把流入梯度累加进 `.grad`）。反向 = **拓扑逆序 + 链式法则**。

### 4.2 核心心法：autograd 只处理"隐式的纯前向图"
**根本立场：autograd 只处理纯图。没有 `MulInplaceBackward` 这种东西。**

处理 mutation 的方法：**想象一个没有 mutation 的等价程序**——那个纯图才是反向对象。
```python
y = x**2; y.mul_(2)   # autograd 等价看待为:
                      # y = x**2; y2 = y*2  (此后 y 换成 y2)
```
机制两步：① 生成对应反向节点；② **就地改被影响 tensor 的 `grad_fn`** 指向新节点。

### 4.3 View + Mutation：CopySlices + rebase（最难的部分）
`v = y[0]; v.mul_(2)`（只改 y 一行）：`y.grad_fn` 不能是 `MulBackward0`（那相当于整个 y 乘2）。解法是 **`CopySlices`** 复合反向节点（等价于 `select_scatter→mul→select` 链）。

**PL 视角**（ezyang 点睛）：视图本质是 **lens**——总有 putback 把修改 scatter 回 base。这个纯函数解释有反向，就是 CopySlices。

mutation 后：`y.grad_fn → CopySlices`；view `v` 的 `grad_fn` 被 **rebase** 到新 CopySlices 节点之上（避免重复算 MulBackward）。

### 4.4 多别名：惰性 rebase（精妙设计）
`v1=y[0,:]; v2=y[:,0]; v1.mul_(2)`——怎么知道要 rebase v2？**让 base 跟踪所有 view 的方案被否决**（内存循环引用 + 多线程争用）。改用**惰性 rebase**：在 view 的 `grad_fn` 记 parent 的 version，访问时检查，不同步就**按需生成 rebased 节点**。

> 🎯 **设计哲学**：PyTorch 选择"拒绝全局 view 跟踪表"，换来无锁、无循环引用、内存可控。代价是 rebase 的惰性 + version 机制。这是工程权衡典范——用一点算法复杂度换并发安全与内存简洁。

### 4.5 串到 dispatcher
autograd 就是 dispatcher 表上的一个 key（见 3.2 的 exclude set 机制）。这也是为什么 `loss.backward()` 能在任意后端上工作——autograd 层和 backend 层是正交的 dispatch key。

### 4.6 实验19透视：version counter 报错与 detach 边界

```bash
cd experiments && python3 19_mutation_views.py
```

**version counter（安全网）**：每个 tensor 有 version 计数器，in-place 改它就 +1。如果反传发现"我为这个节点存的输入 version 变了"，**拒绝算（报错而非算错）**：
```python
y = x**2; z = y.sum(); y.add_(1)   # 在非leaf y上in-place
z.backward()  # RuntimeError: variable needed for gradient
              # computation has been modified by inplace
```
> 这解释了常见报错"variable modified by inplace"的根因——反传检测到缓存失效。

**detach：断梯度但不断 version**：`y.detach()` 把 tensor 摘下当普通数据（`requires_grad=False`），但**仍共享 version counter**。所以 detach 后 in-place 仍能被反传安全网检测到。

**数学反传 vs PyTorch backward 的鸿沟**：

| 数学反传（理想）| PyTorch backward（工程）|
|--------------|----------------------|
| 纯函数、无 mutation | 必须处理 in-place、view 别名 |
| 梯度直接算 | 用 version counter 防过期 |
| 节点固定 | CopySlices + rebase + 惰性 rebase |

过了这层，才算真懂 PyTorch 的 `backward()`——它不只是 VJP，还解决了真实代码里 mutation/aliasing 带来的所有边界。

---

## 五、编译栈：Dynamo → AOTAutograd → Inductor（出处：Perone "PyTorch 2 Internals"；ASPLOS'24 论文）

### 5.1 为什么需要编译栈
eager 一次只看到一个算子，**无法做跨算子优化（fusion/scheduling）**。PyTorch 2 用 `torch.compile` 全新栈解决，核心三件套：

```
Python eager 代码
  → ① TorchDynamo (Python 字节码→FX graph, PEP 523 frame eval)
  → ② AOTAutograd (提前捕获 forward+backward, lowering 到 ATen/Prims IR)
  → ③ TorchInductor (scheduling + fusion → Triton GPU / C++ OpenMP CPU)
```

### 5.2 三层职责
- **TorchDynamo**：Python bytecode → bytecode 翻译器，靠 PEP 523 在字节码执行前介入，把 torch 算子序列抽成 FX graph。**graph break**（调 numpy/`Tensor.item()` 等时）回退 Python 解释器——这是"灵活性+性能"兼得的关键。**guards + 符号 shape** 缓存已编译图、避免重 trace。
- **AOTAutograd**：Dynamo 只捕获 forward；要加速训练必须也捕获 backward。它**同时 trace fwd+bwd**，lowering 到 **ATen/Prims IR**（即第二章的算子！）。
- **TorchInductor**：拿 ATen/Prims 图 → scheduling（此处做 **fusion**）→ 代码生成。**GPU 出 Triton，CPU 出 C++/OpenMP**。

### 5.3 与算子层的接缝（关键认知）
**Inductor 的 IR 就是 ATen/Prims——即 `native_functions.yaml` 定义的算子。L2 编译栈最终 lowering 到 L1 算子，再经同一个 dispatcher 路由**。

**但 Inductor 的性能赢点恰恰是"绕过单个算子 kernel"**：它把多个 ATen 算子 **fuse 成一个新生成的 Triton/C++ kernel**（如 fused softmax），省掉逐算子 kernel launch 和中间 tensor 物化。

### 5.4 两条部署路径
- **torch.export**：整图捕获（无 graph break），产 Core ATen IR，跨语言部署——**可替 ONNX**。
- **ExecuTorch**：端侧 C++ runtime（~50KB，用户分配器，SRAM/DRAM placement，backend delegation 到 NPU/DSP），**不用 TorchScript**。

> 详见本教程 [06-编译与图模式](06-编译与图模式.md)（含本环境 compile 实测）。

---

## 六、分布式重构：DTensor → sharding-in-types（出处：ezyang 2026 SPMD 系列 7 篇）★最新动态

> 这是最前沿的部分。ezyang 2026 的 7 篇博客揭示：**PyTorch 分布式正在从"运行时解释 sharding 的 auto 模式 DTensor"重构为"类型承载 sharding + 类型可擦除 + global/local 双视图（DTensor + LTensor）"的下一代架构**，对标并试图超越 JAX 的 explicit sharding 类型系统。

### 6.1 DTensor 当前的两大病根
- **病根 A（性能）**：DTensor eager 有 **35–60% 训练 slowdown**（论文 arXiv 2509.07003 实测），单次操作比实际计算慢至少 7 倍（Python shard propagation 极贵）。
- **病根 B（语义）**：DTensor 是"auto 模式"——前/反向 sharding 可不同选，用户无法预测，框架无法保证局部可判定。

### 6.2 两种 SPMD 范式（坐标系）
- **Global SPMD（global view）**：假装单设备写代码，正交机制表达分布。载体：DTensor、JAX `jax.Array`。
- **Local SPMD（per-device view）**：单设备视角 + 显式 collectives（Megatron 式、JAX `shard_map`）。

**关键纠偏**：区别不在控制粒度，而在语义——local SPMD **没有全局真相**，很多情况下"实际执行的计算"≠"在完整张量上执行同一算子"。这就是 Megatron 对实验不友好的根因。

### 6.3 重构蓝图：sharding-in-types（对标 JAX）
JAX 的 sharding 类型系统四组件（DTensor 重构的词汇表）：
- **PartitionSpec**：tensor 维→mesh axis 的切分映射（全局视图）。
- **VMA（varying manual axes）**：local/shard_map 内"值是否随 mesh 维变化"的近似类型。
- **unreduced**：pending reduction，表达 Partial（本地可算但待 reduce）。
- **reduced**：像 replicate 但 cotangent 变 unreduced。

**核心不变量**：cotangent（反向梯度）sharding 必须能从 primal（前向）sharding 直接算出。DTensor 当前缺的正是这条。

### 6.4 DTensor erasure（全系列最重要）
借鉴类型论的 type erasure：**擦除所有 placement 后程序仍能正确跑**。ezyang 的更强约束："直接擦除 DTensor，一个 hook 都不加"。剧透答案：**JAX 式 sharding-in-types（无隐式转换）就够了**。

具备 erasure 后：**同一份代码可用 plain Tensor 或 DTensor 跑**——DTensor 当**动态类型检查器**（placement 错了报错），Tensor 当**生产运行时**（省掉所有 shard 检查）。这是 **gradual compilation**（渐进编译）模式：编译器退居为可选的静态分析旁路工具。

### 6.5 两个核心论证
- **Replicate Forwards, Partial Backwards**（第5篇）：ezyang 论证这比 JAX 现行的 replicate→replicate 默认更优——能减少隐式 all-reduce、允许 reduce-scatter 优化。用 DP+TP gated MLP 全程手算（einsum sharding 推导）证明。
- **Megatron via shard_map**（第6篇）：JAX 的 `shard_map` + VMA（`check_vma=True`）类型系统能**让"忘记反向 all-reduce"变得不可能**。**明确预告**：PyTorch 将引入 **LTensor** subclass（对标 VMA，追踪 local SPMD 元数据）。

### 6.6 闭环：DTensor 的未来形态
```
下一代 = DTensor(global, 类型检查器) + LTensor(local, VMA 追踪) 双层结构
       + sharding-in-types(无隐式转换) + erasure(类型可擦除)
       + einsum 统一推导 sharding
```
> 详见本教程 [08-现代PyTorch](08-现代PyTorch(2.x特性).md).md).md).md).md)（DTensor/FSDP2 基础）+ 本文（重构内部动态）。

---

## 七、一根主线串起全部（总结图）

```
                Tensor (device, layout, dtype) ── 决定 ──┐
                                                       ▼
            ┌──────────── Dispatcher (每算子一张表, dispatch key set) ────────────┐
            │                          │                                           │
   autograd key                    backend key                              tracing/vmap key
   (反向图+mutation)              (CPU/CUDA/...)                             (compile捕获)
            │                          │                                           │
            ▼                          ▼                                           ▼
   CopySlices/rebase          native_functions.yaml                    Dynamo→AOTAutograd→Inductor
   (autograd 内核)            → codegen → structured kernels           (编译栈, fuse 算子)
                              → TORCH_META/IMPL → BLAS
                                                                        ↓
                                                              torch.export / ExecuTorch (部署)
                                                                        ↓
                                                              DTensor(sharding-in-types) + LTensor
                                                              (分布式, dispatcher 上的又一层)
```

**核心洞察**：dispatcher 是 PyTorch 内核的"总线"——
- **数据层**给 dispatch 提供输入（三元组）；
- **算子层**填满 dispatch 表（yaml→codegen→kernel）；
- **autograd/compile/分布式**都是在 dispatch 表上**叠加新的 key/层**。

抓住 dispatcher 这根线，PyTorch 的每一个部分（从 `tensor.view()` 到 `torch.compile` 到 FSDP2）都挂在同一棵树上，不再散落。

---

## 八、权威源索引（精读出处 + 延伸）

| 主题 | 权威源 | 本文章节 |
|------|--------|---------|
| 整体架构/stride/dispatch | ezyang "PyTorch internals" (2019) | 一、二 |
| Dispatcher 深度 | ezyang "Let's talk about the PyTorch dispatcher" (2020) | 三 |
| 算子分类法 | ezyang "A brief taxonomy of operators" (2020) | （二补充）|
| autograd+mutation | ezyang "Autograd and Mutation" (2026) | 四 |
| 源码追踪 | Kieran Didi "How does PyTorch implement a linear layer?" | 二 |
| 官方导览(考古) | Trevor Killeen "A Tour of PyTorch Internals" (2017, 官方) | 二背景 |
| 编译栈 | Christian Perone "PyTorch 2 Internals" + ASPLOS'24 论文 | 五 |
| DTensor 重构 | ezyang 2026 SPMD 系列 7 篇 | 六 |
| 设计讨论 | dev-discuss.pytorch.org | 全文 |

> ⚠️ **易混淆澄清**（brisk-azure-owl subagent 纠正）：有三篇常被混为一谈的经典文——① Killeen 2017 官方 "A Tour"；② Perone 2018 "Internal Architecture Tour"；③ ezyang 2019 "PyTorch Internals"。三者不同，本文分别引用。

---

## 九、反传的边界与未来

> 第四章讲了 autograd 怎么工作。最后反思：**反传的局限在哪？有没有替代范式？** 这关系到"PyTorch 的核心求导机制是否永远是反传"。

### 9.1 反传的四个局限
1. **要求完全可微**：不可导点用次梯度（ReLU 的 0），不可微操作（采样）要绕过。
2. **需要完整计算图**：要等整个前向跑完才能反传，无法在线增量学习。
3. **全局同步**：所有参数梯度一起算，和生物大脑的局部、异步学习完全不同。
4. **能耗巨大**：训 GPT-4 要消耗海量电力（前向+反向各一遍）。

### 9.2 绕过不可微：reparameterization 与 straight-through
- **重参数化（VAE）**：采样 $z\sim\mathcal{N}(\mu,\sigma)$ 不可微。改写成 $z=\mu+\sigma\epsilon,\ \epsilon\sim\mathcal{N}(0,1)$——把随机性外移到 $\epsilon$，对 $\mu,\sigma$ 的路径就可微了。
- **Straight-Through Estimator**：量化/离散化前向不可微（argmax），但前向用硬离散、反传用软近似（sigmoid）的梯度"假装"流过。用于二值网络、VQ-VAE。

### 9.3 绕过"需要完整图"：graph break
`torch.compile` 捕获计算图时，遇到不可捕获部分（调 numpy、`Tensor.item()`）会**断图**（graph break），回退 eager（见 5.2 TorchDynamo）。这是"反传/编译要求可捕获"约束在现代编译栈里的体现。

### 9.4 替代反传的范式（研究前沿）
- **Forward-Forward Algorithm（Hinton 2022）**：用两次前向（正/负样本各算 goodness）替代"前向+反向"，更接近生物学习。目前精度不如反传，但是对"反传是否唯一可能"的重要探索。
- **Feedback Alignment**：用固定随机矩阵传反向梯度，证明网络能学会自己对齐——挑战反传的"精确转置"必要性，更接近生物（突触没有精确转置）。
- **预测编码（Predictive Coding）**：类脑算法，层级预测误差驱动学习，局部更新无需全局反传。

> **批判**：这些替代范式**目前都不如反传**（精度/效率）。反传的"VJP + $m\ll n$"优势太硬。但它们回应了真实担忧：反传的生物不合理性、能耗、对完整图的依赖。**短期反传仍是唯一主流；长期若硬件范式（类脑/光计算）变化，格局可能变。** 一句话：反传是当前深度学习的唯一答案，但不是唯一可能的答案。

---

📌 **下一步**：
- 想动手验证：跑 `experiments/01_autograd_from_scratch.py`（90 行手写引擎，对应第四章）+ `experiments/19_mutation_views.py`（version counter/CopySlices，对应 4.6）+ `experiments/07_compile_deep.py`（profiler 看 fusion，对应第五章）。
- 想挖更深：每章末尾的"出处"文章都是一手材料，按主题速查表（[README](README.md) 权威资源索引）入门。
- 本文是"深入理解 PyTorch 内核"的核心综合。配合前面 00–09 章（怎么用）+ 实验（实证），构成"原理→实现→用法→内核"的完整闭环。
