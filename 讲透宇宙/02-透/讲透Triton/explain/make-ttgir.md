# make-ttgir.md — `third_party/nvidia/backend/compiler.py`（NVIDIA 后端与 TTGIR pass 编排，Triton 3.8.0）

## 1. 角色定位

`compile()`（compiler/compiler.py）发号施令，本文件是执行者：`CUDABackend`（L167）实现 `BaseBackend` 全部契约，其中 `make_ttgir`（L292-377）单函数编排 40 余个 MLIR pass，是 Triton GPU 优化心脏。图谱未覆盖 third_party，逻辑上桥接 `layer:runtime-backends` 与 `layer:passes-analysis`：pass 本体在 `lib/Dialect/TritonGPU/Transforms/`，经 pybind 暴露为 `passes.ttgpuir.add_*`。

## 2. 内部结构

- **`CUDAOptions`**（L108-164）：num_warps/num_stages/maxnreg 等 30 项；`parse_options`（L206）按 capability 剪裁（num_ctas>1 需 SM90+）；ptxas 版本进后端 `hash()`（L657）。
- **五个 stage**：`make_ttir`（L276）机器无关优化；`make_ttgir`（L292）主角；`make_llir`（L407）TTGIR→LLVM-IR（`add_to_llvmir` L433）；`make_ptx`（L525）；`make_cubin`（L559）。
- **`add_stages`**（L644-655）：注册 ttir→ttgir→llir→ptx→cubin；GLUON 跳过 ttir 走 `gluon_to_ttgir`（L379）。

## 3. 外部连接

上游：`compiler.py:291` 经 `add_stages` 消费，L302 调 `load_dialects`。依赖 `triton._C.libtriton` 的 `ir/passes/llvm/nvidia` pybind 模块（L2）；每个 add_* 对应 `Coalesce.cpp` 等实现（用 AxisInfo）。AMD 对照 amd/backend/compiler.py:260。

## 4. 数据流（make_ttgir 的 pass 顺序）

输入 TTIR 输出 TTGIR：`ir.pass_manager`（L298）追加，`pm.run`（L375）跑完，抽 `tensordesc_meta`（L376）。分段：

1. **入口**（L294-301）：写 `ttg.maxnreg`；`add_convert_to_ttgpuir` 转 TTGIR 并分配初始 blocked layout。
2. **布局段**（L305-316）：`add_coalesce`（AxisInfo 定连续访存）→`add_f32_dot_tc`→`add_plan_cta`→`add_remove_layout_conversions`→`add_optimize_thread_locality`→`add_accelerate_matmul`（L311，dot 改 MMA layout）→`add_optimize_dot_operands`→`loop_aware_cse`。
3. **调度段**：SM8x/9x（L317-326）`fuse_nested_loops`→`triton_licm`→(9x)`hopper_warpspec`→`assign_latencies`→`schedule_loops`→`add_pipeline`（软件流水）；SM10x（L327-342）另有 tmem 链 `hoist_tmem_alloc`/`warp_specialize` 等。
4. **降级段**（L345-373）：prefetch→`coalesce_async_copy`→`tma_lowering`（SM90+）→`lower_clc`（SM100+）→`remove_layout_conversions`→`reorder_instructions`→`fence_insertion`→`lower_mma`（L364 落 wgmma/tcgen05）→sccp/cse/canonicalizer。

## 5. 设计决策

- **Python 编排 + C++ pass**：顺序按 capability/option 分支，放 Python 免重编译；图变换放 C++ 复用 MLIR。
- **顺序即正确性**：coalesce 先于 accelerate_matmul——先定通用访存布局再改 dot 布局；每次布局变更后紧跟 `remove_layout_conversions`（L309/313/357）传播收敛，防冗余 convert 吃光寄存器（L307 留 TODO）。`assign_latencies`→`schedule_loops`→`pipeline` 有严格数据依赖；`tma_lowering` 要等流水化定下的异步拷贝形态；`lower_mma` 倒数第二，保证优化都在抽象 layout 上做。
- **num_warps 可被改写**：warp specialization 分裂 warp 组，`make_llir` 从 `ttg.total-num-warps` 回读覆写 metadata（L507-509），`shared` 由 `ttg.shared` 回填。

## 6. 新人提示

- **切入点**：从 L301 数到 L375 对照 dump。
- **dump**：`MLIR_ENABLE_DUMP=1`（可填函数名过滤）打印每 pass 前后 IR；`TRITON_KERNEL_DUMP=1` 落盘全套 stage。
- **单 pass 实验**：`triton-opt` 跑 `.ttgir`；回归 `test/TritonGPU/*.mlir`。
- **对照**：DeepWiki 4.1/4.4 章。
