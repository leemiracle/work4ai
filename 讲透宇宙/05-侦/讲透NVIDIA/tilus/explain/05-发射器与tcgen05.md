# 05 · 后端发射器与 tcgen05（python/tilus/backends/）

## 1. 角色定位

`python/tilus/backends/`（图谱 L12，63 文件）是编译管线第 3 步的执行者：把 Tilus IR（语句+指令+布局）下降为 Hidet IRModule——每条指令一个发射器，硬件资源由上下文族记账。这是 tilus 性能真正落地的地方：布局代数在这里变成具体的 PTX 调用与地址算术。Blackwell（sm_100+）的第五代 TensorCore **tcgen05** 是当前发射器家族的最高地——TMEM（Tensor Memory）成为第四种存储层级（`TMemoryTensor`，`python/tilus/ir/tensor.py:661`）正由此而来。

## 2. 内部结构

**框架三件**：`FunctionCodegen`（`python/tilus/backends/codegen.py:76`，26 方法）遍历 Tilus 语句树，对每条指令 `resolve_inst_emitter`（:123）查表取发射器；`ProgramCodegen`（:487）+ `generate_ir_module`（:503）总装。`BaseInstEmitter`（`python/tilus/backends/emitter.py:34`，33 方法）是发射器基类（继承 StmtBuilder，发射即构建 Hidet 语句）；`register_emitter`（:267）按 **(指令类型, target) 二维注册**进 `BaseInstEmitter.REGISTRY`，重复注册直接 ValueError——静态防冲突。注意 `resolve_inst_emitter` 的解析顺序敏感：沿 REGISTRY 迭代序取**第一个**匹配父类即 break（python/tilus/backends/codegen.py:124-131），mro 语义靠注册顺序近似。

**上下文族**（`python/tilus/backends/contexts/`）：`EmitContexts`（`python/tilus/backends/contexts/contexts.py:27`）聚合全部子上下文——`SharedMemoryAllocator`（`python/tilus/backends/contexts/smem_alloc_ctx.py:28`，first-fit 空闲槽分配 + 相邻槽合并的 free，直接决定最终 dynamic shared memory 大小；上下文包装 :87）、全局内存池化分配（`gmem_alloc_ctx.py`）、mbarrier 槽位表（`python/tilus/backends/contexts/mbarrier_alloc_ctx.py:33`，供异步拷贝与 MMA 查空闲 barrier）、TMEM 分配状态（`python/tilus/backends/contexts/tcgen05_ctx.py:23`，分配列/视图跟踪/提交组计数）、常量寄存器复用（`const_reg_ctx.py`）、leader lane 选取（`leader_lane_ctx.py`，单线程域发射辅助）、循环不变量跟踪（`invariant_ctx.py`）。

**发射器家族**（22 通用模块 + 15 CUDA 模块 + Blackwell 子包）：访存/元素级/规约/扫描/变换等通用族在 `emitters/`；CUDA 族覆盖三代异步拷贝与三代 MMA——cp_async（Ampere，注意类名 `CopyAysncInstEmitter`，`python/tilus/backends/emitters/cuda/cp_async.py:42`，Aysnc 拼错钉版）、cp_async_bulk（TMA 四方向 + commit/wait，`python/tilus/backends/emitters/cuda/cp_async_bulk.py:142,172,197,237`）、mbarrier、wgmma（Hopper，`python/tilus/backends/emitters/cuda/wgmma.py:115` WgmmaMmaSSEmitter）、**tcgen05 全家**（`emitters/cuda/tcgen05/` 四模块：python/tilus/backends/emitters/cuda/tcgen05/alloc.py:38-136 五个发射器、python/tilus/backends/emitters/cuda/tcgen05/ldst.py:55-207 TMEM 读写、python/tilus/backends/emitters/cuda/tcgen05/copy.py:60、python/tilus/backends/emitters/cuda/tcgen05/mma.py:199）与 CLC 工作窃取（`python/tilus/backends/emitters/cuda/blackwell/clc.py:25,40`）。架构分派发生在**指令层而非发射器内部**：`DotInstEmitter`（`python/tilus/backends/emitters/cuda/mma_dot.py:28`）只发 warp 级 `mma_sync_v2`（:99）；Hopper/Blackwell 用户应改用 wgmma/tcgen05 指令（各自独立 IR 与发射器）——"一个 emitter 按架构分派三代 MMA"的说法不成立（勘误）。

## 3. 外部连接

上游吃 Tilus IR 与布局：`DotInstEmitter.resolve_mma_config` 用**布局除法** `p / q` 匹配 AtomicMmaConfig（`python/tilus/backends/emitters/cuda/mma_dot.py:41-47`，p 能整除出 config 的碎片布局即命中）；wgmma 发射器从 CanonicalSharedLayout 取 LBO/SBO 乘 dtype 字节数（`python/tilus/backends/emitters/cuda/wgmma.py:169-177`）。PTX 原语全部来自 hidet 基座：`register_tcgen05_instructions`（`python/tilus/hidet/ir/primitives/cuda/tcgen05.py:268`）注册 9 个 Kind 枚举全参数空间的指令生成器；描述符位域编码 `tcgen05_encode_smem_descriptor`（:545）/`tcgen05_encode_mma_inst_descriptor`（:559）。下游交 `optimize_ir_module`（`python/tilus/drivers.py:97`）跑 hidet 32 pass，首个就是 `inline_register_tensor_pass`（`python/tilus/backends/transforms/inline_register_tensor.py`：RegisterTensorCollector:52 / Filter:98 / MappingCollector:114 三阶段收集单用途寄存器张量并内联——发射期产出物的首次清理）。

## 4. 数据流（tcgen05 MMA 一个样本）

Blackwell matmul v4+（`examples/blackwell_matmul/matmul_v4.py`，275 行，TMEM+tcgen05 集成）里一条 `self.tcgen05.mma_ss(...)` 的旅程：前端指令组（`python/tilus/lang/instructions/tcgen05.py`，374 行 12 方法）落成 `Tcgen05MmaSSInst`（`python/tilus/ir/instructions/cuda/tcgen05.py:143`）；布局推断按 `Tcgen05MmaSSRule` 推 TMEM/SMEM 布局（`inference_rules/tcgen05/mma.py`，规则序最前组）；发射时 `TMemoryMmaSSEmitter`（`python/tilus/backends/emitters/cuda/tcgen05/mma.py:199`，413 行）组装两件硬货——**共享矩阵描述符**（起始地址/LBO/SBO/swizzle 模式位域，对接 `python/tilus/hidet/ir/primitives/cuda/tcgen05.py:545` 的编码器；wgmma 同款结构见 `python/tilus/backends/emitters/cuda/wgmma.py:54` SharedMatrixDescriptor，lbo>>4/sbo>>4 移位 :61-66）与**MMA 指令描述符** `Tcgen05MmaInstDesc`（`python/tilus/backends/emitters/cuda/tcgen05/mma.py:60`：sparsity/dtype 三元/negate/transpose/n>>3/m>>4 全位域，`encoded()`:100 调 hidet 编码器；字段名 `maximim_shift_in_ws`:75 拼错钉版，对应 PTX 文档 maximum_shift_in_ws）；最终经原语生成内联 PTX（AsmStmt，`python/tilus/hidet/ir/stmt.py:306`），TMEM 分配/释放由 `Tcgen05AllocEmitter`（`python/tilus/backends/emitters/cuda/tcgen05/alloc.py:66,107`）与 Relinquish（:130）配平。

## 5. 设计决策

**每指令一发射器而非整函数代码生成**：指令集在膨胀（tcgen05 一族 12 条），注册表模式让新增硬件指令只加文件不动主干；代价是跨指令优化（如自动软件流水）只能留给上层 pass。**(指令, target) 二维注册**：同名指令在不同 target 可有不同实现，`match_target` 选最Specific——为未来多后端留缝（当前实际只有 CUDA 族）。**资源记账进上下文而非发射器**：共享内存/mbarrier/TMEM 的分配复用是全局决策，发射器只申请不管理——`SharedMemoryAllocator` 的 first-fit+合并让 free_shared 真正省内存。**描述符编码下沉 hidet 原语层**：位域编码是纯函数，放原语库可被发射器与测试共用，发射器只管语义字段。**leader_lane/invariant 上下文**：单线程域发射（barrier arrive 等）需要选 lane、循环归纳变量值需缓存免重算——这类"发射期常识"集中化避免每个发射器重复实现。

## 6. 新人提示

- 入门顺序：`emitter.py`（框架）→ `emitters/assign.py`（最简发射器）→ `emitters/cuda/mbarrier.py`（中等复杂度+上下文交互）→ `tcgen05/mma.py`（最硬）。
- 对照读 `examples/hopper_matmul/matmul_v2.py`（TMA 引入）与 `matmul_v3.py`（wgmma 流水）、`examples/blackwell_matmul/matmul_v4.py`（TMEM 集成），三个示例恰好踩过三代硬件发射路径。
- 发射器调试：`tilus.option.cache_dir` 看生成的 source.cu；`debug_block`（`python/tilus/lang/script.py:43`）打印指定 block 的指令输出。
- 记住 store_shared→TMA 必插 `fence.proxy_async`（CLAUDE.md:69-83）——发射器不自动补，漏了是数据竞争级别的 bug，且 SASS 层面难查。
- 新增发射器四步：写类继承 BaseInstEmitter、实现 `emit`、`register_emitter(指令类, target=...)` 注册、在 `emitters/__init__.py` 或 `emitters/cuda/__init__.py` barrel 里 import 触发注册——漏掉 barrel import 等于没注册。
