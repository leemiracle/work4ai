# EvoKernel 知识图谱摘要

- 生成：2026-09-03（understand --language zh 全链路）· git commit `af61b2a307d6`
- 规模：**86 节点 / 136 边 / 5 架构层 / 9 步导览**
- 校验：内联校验 0 issue（详见 FINAL-REPORT）
- 交互：在本体仓（/data/usershare/ai/EvoKernel）运行 /understand-dashboard 或 /understand-chat 查询

## 节点类型分布

| 类型 | 数量 |
|---|---|
| function | 38 |
| file | 24 |
| class | 16 |
| config | 5 |
| schema | 2 |
| document | 1 |

## 边类型分布

| 类型 | 数量 |
|---|---|
| contains | 54 |
| exports | 29 |
| related | 25 |
| depends_on | 12 |
| documents | 10 |
| defines_schema | 6 |

## 架构层

- **数据集定义层**（6 节点）：README 数据集卡片与五个合集 manifest，定义 EvoKernel 的五大导出（Ascend 910B 的 attention/MHC/Kernel
- **Ascend 910B CANN 算子实现层**（14 节点）：三个采样算子（AdaptiveAttention/ArgmaxOverADimension/FusedMhcKernels）的 CANN 自定义算子工程，统一遵
- **CUDA NCU 迭代选优产物层**（2 节点）：NCU 迭代选优后的终版 best_code.py（torch load_inline 内联 CUDA 源码而非 triton），分别采样自 attention
- **评测元数据层**（5 节点）：五个采样算子的 result.json 单点评测记录（outer_iter、compiled、correctness 与 performance 统计），其中 
- **PyTorch 参照任务层**（5 节点）：与合成 kernel 一一对应的 PyTorch 参照任务，统一采用 get_inputs/get_init_inputs/Model 三件套协议（Kernel

## 导览步骤

1. 数据集卡片总览
2. 五大合集统计清单
3. 910B 三层布局（上）：接口契约与 host 侧 tiling
4. 910B 三层布局（下）：设备实现与 PyTorch 桥接
5. MHC 融合核：最复杂样例
6. KernelBench 910B 迁移样例
7. CUDA NCU 迭代选优产物
8. 评测元数据：result.json 对照
9. PyTorch 参照任务与评测协议
