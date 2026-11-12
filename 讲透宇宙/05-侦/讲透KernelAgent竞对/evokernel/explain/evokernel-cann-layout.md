# EvoKernel Ascend 910B CANN 三层布局深解——以 AdaptiveAttentionCustom 为主例

> 对象：`ops-attention-910b/AdaptiveAttentionCustom/`，对照 `ops-mhc-910b/FusedMhcKernelsCustom/` 与 `ops-kernelbench-910b/ArgmaxOverADimensionCustom/`。图谱依据 `.understand-anything/knowledge-graph.json`（ascend-910b-kernel 层），源码逐文件核实。

## ① 角色定位：CANN 标准布局如何映射到数据集

EvoKernel 的 910B 合集（58 attention + 15 MHC + 165 KernelBench）不是散装脚本，而是华为 CANN「自定义算子开发」标准工程的忠实快照。每个 `<OpName>Custom/` 目录固定含五件：`op_host/`（算子注册+tiling）、`op_kernel/`（AscendC 设备实现）、`CppExtension/csrc/op.cpp`（PyTorch 桥）、`<op>.json`（算子接口描述）、`result.json`（评测记录）。这套布局的意义：LLM 合成 kernel 时必须同时产出 host/device/桥接三份协同代码才能编译通过——布局本身就是对生成能力的结构性约束，也是数据集筛选器（attention 合集 58/58 编译且正确，MHC 合集仅 10/15）。

## ② 三层分工解剖

**op_host（CPU 侧）**：两个文件。`*_tiling.h` 用 `BEGIN_TILING_DATA_DEF/END_TILING_DATA_DEF` 定义 TilingData 结构体并 `REGISTER_TILING_DATA_CLASS` 注册——这是 host↔device 的唯一数据通道。`op_host/*.cpp` 提供 `TilingFunc`（`optiling` 命名空间，从 `TilingContext` 读输入 shape，算出切分参数，`SaveToBuffer` 写入 tiling buffer，`SetBlockDim` 申报核数，`GetWorkspaceSizes` 报 workspace）与 `OpDef` 子类（`ops` 命名空间，链式声明 Input/Output 的 dtype/format，`AICore().SetTiling()` 绑定，`AddConfig("ascend910b")` 指定 SoC），最后 `OP_ADD` 宏注册进算子注册表。

**op_kernel（device 侧）**：`#include "kernel_operator.h"` 进入 AscendC 世界。`Kernel<Op>` 类持 `TPipe`+若干 `TBuf`（Unified Buffer）+`GlobalTensor`（GM 指针），`Init`（`SetGlobalBuffer`+`InitBuffer`）/`Process`（`GetBlockIdx/GetBlockNum` 分摊任务）两段生命周期。入口是 `extern "C" __global__ __aicore__ void <op>(GM_ADDR..., tiling)`，其中 `GET_TILING_DATA` 反序列化 host 侧产物。

**CppExtension（PyTorch 桥）**：`check_inputs` 式校验（设备=`PrivateUse1`、dtype、连续性、维度）→ `at::empty_like` 分配输出 → `EXEC_NPU_CMD(aclnn<Op>, ...)` 启动两阶段算子（aclnnXxx 由 CANN 编译期自动生成）。三宏收尾：`TORCH_LIBRARY(myops,...)` 定义 schema、`TORCH_LIBRARY_IMPL(myops, PrivateUse1,...)` 绑 NPU 实现、`PYBIND11_MODULE` 导出 Python。

## ③ AdaptiveAttention 实现走读

**tiling 怎么算**（`TilingFunc`）：从 q 的 storage shape 取 B/H/S/D，校验 k/v 同形、D≤128、S≤4096、totalRows=B·H·S 不溢出 uint32。切分策略全是经验规则：coreNum=min(totalRows,48)（910B 典型核数）；dTile=64 或 D 向下取 2 的幂（向量指令友好）；sTile=128 起、上限 256，D≥128 时压到 64（控 UB 占用）；scale=1/√D 直接算好传下去——device 侧免去超越函数。

**kernel 核心循环**（`ComputeRow`，行级 flash-attention）：一行=一个 (b,h,qi) 查询。三遍扫描 S 维：Pass1 求 rowMax（逐 K 行 `DotQK` 取 max）；Pass2 重算 logits、减 rowMax、`Exp`、`ReduceSum` 累出 rowSum；Pass3 再算一遍概率、乘 invSum 归一，按 dTile 分段与 V 加权累加进 outRow，最后 `DataCopy` 写回 GM。K/V 按 sTile 分块经 `DataCopy` 搬入 UB（`PipeBarrier<PIPE_MTE2>` 等搬运完成）。注意这是「三遍重算」而非教科书 online-softmax 的单遍 rescale——牺牲 2 倍 QK 计算量换取逻辑简单，是 LLM 合成代码的典型取舍。

**向量寄存器使用**：无 warp 概念，全部操作是 UB 上的向量指令——`Mul/Add/Muls/Exp/Duplicate`（整段 dTile 元素一次算）+`ReduceSum`（归约）+`GetValue/SetValue`（标量回读）。每条向量指令间手工插 `PipeBarrier<PIPE_V>` 保序（AscendC 无硬件依赖追踪，漏插即数据竞争）。`DotQK` 对 D≤64 走快速路径（一次 Mul+一次 ReduceSum），否则按 dTile 分块累加、尾部标量补零头；六个 UB buffer 中 calcBuf 手工二次切分成 tmpReduce/redOut/mulTmp/prodAcc/vTmp/vAccTmp 六段。

## ④ 跨 kernel 验证：布局同构

三个算子复杂度悬殊（122 行 vs 431 行 vs ~110 行），骨架完全同构：

| | AdaptiveAttention | FusedMhcKernels | ArgmaxOverADimension |
|---|---|---|---|
| tiling.h | 9 字段（B/H/S/D/…/scale） | 11 字段（B/L/D/n/+4 个 Ceil8 对齐 padding） | 7 字段（totalX/totalY/batch/reduceDim/innerDim/tileInner/tilesPerBatch） |
| TilingFunc 特征 | 动态 coreNum=min(rows,48) | InferN 由 outCols=n²+2n 反推 n + 8 对齐 | blockDim=batch×tilesPerBatch 静态映射 |
| kernel 调度 | 行循环 stride=bnum | BL 行循环 RunOneRow | 1 block=1 (b,tile) |
| 算子注册差异 | 3 入 1 出 | 10 入 3 出+`SetInferShape/SetInferDataType`（唯一带动态 shape 推理） | 1 入 1 出，桥接层未单独 def schema |
| 计算风格 | 向量指令为主 | 向量+ExpApprox/LogApprox 多项式近似（Sinkhorn log-space，N4 特化） | `__gm__` 裸指针标量循环+4 路展开 |

结论：op_host/op_kernel/CppExtension 三层+tiling.h 通道+五件目录结构在全部 238 个 910B 算子上不变，变化的只有 TilingData 字段集与 kernel 内算法。

## ⑤ result.json 与目录内元数据 json 的关系

`adaptive_attention_custom.json` 是**算子接口契约**（op 名+input_desc/output_desc 的 param_type/format/type），与 op_host 的 `OpDef` 声明互为镜像，供 CANN 工程构建；`result.json` 是**评测结果**（outer_iter=25 轮迭代选优后 compiled=true、correctness=true、performance.mean=3.84ms）；合集根的 `manifest.json` 汇总全部 kernel 的 result 并给 compiled_rate/correctness_rate。两套 json 一静态一动态：前者决定「算子长什么样」，后者记录「演化管线最终跑出什么」。字段有协议差异：attention/KernelBench 合集用六字段+performance 对象，MHC 合集扩展为十字段（mean_ms/speedup_vs_baseline/log2_speedup…）——FusedMhcKernels 即 negative sample（outer_iter=39 仍 compiled=false，仅 baseline_mean_ms=1.097 有值）。

## ⑥ 与 CUDA 路线的本质差异

同数据集的 `ops-*-cuda-ncu` 合集是另一物种：单个 `best_code.py` 经 `torch.utils.cpp_extension.load_inline` 内联 CUDA，无独立工程。三点本质差异：**编程模型**——CUDA 是线程级（warp shuffle `__shfl_down_sync` 归约、shared memory、`__launch_bounds__(32*WARPS_PER_BLOCK,2)` occupancy 控制），AscendC 是 block 级向量级（一个 block 一次吃整段 UB，显式 PipeBarrier，无线程分化问题）；**精度**——CUDA 样本同样坚持 float32（CHECK_FLOAT32），但生态上 CUDA 常见 half/bf16 快路径，本数据集 910B 侧全部 DT_FLOAT、无量化类型；**编译链**——CUDA 走 nvcc 运行时 JIT，CANN 走离线编译（op_host 进算子库、op_kernel 经 CCE 编成 AscendC 二进制、aclnn 适配层自动生成），EXEC_NPU_CMD 与 load_inline 是两条不兼容的调用通道。

## ⑦ 新人提示

1. **读一个算子从 tiling.h 入手**：字段集就是该算子的全部调度自由度，比先读 kernel 快得多。
2. **PipeBarrier 是 AscendC 第一大坑**：向量指令/搬运之间必须手工 barrier，漏插的结果是「偶发错误」而非报错。
3. **GET_TILING_DATA 与 REGISTER_TILING_DATA_CLASS 的算子名必须严格一致**，否则 device 侧取到的是空 tiling。
4. UB 容量约束决定 sTile/dTile 上限，改 tile 先算 `sTile×D×4B` 是否超 UB。
5. 别把 attention 合集的三遍重算当范本——它是正确但非最优的合成产物；MHC 的 negative sample（39 轮未编译过）同样是数据集的财富，适合做失败模式研究。
