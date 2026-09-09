# TileKernels 新人指南（ONBOARDING）

> 基于 knowledge-graph（10 层/12 步导览）与 README。

## ① 项目是什么与定位

TileKernels 是 DeepSeek 用 TileLang 编写的 LLM 高性能 GPU 算子库；TileLang 是"用 Python 表达 GPU 内核"的 DSL，主打易迁移与自动优化。六大算子域：Gating/MoE Routing（专家路由门控）、Quantization（FP8/FP4/E5M6 量化）、Transpose（批量转置）、Engram（记忆增强门控）、MHC（Manifold HyperConnection 流形超连接）、Modeling（autograd 封装）。多数内核已逼近硬件极限，部分已内部使用，README 自言非最佳实践、仍在打磨。

定位：DeepSeek 系内核的 TileLang 实验场——用 Python 写出接近手写 CUDA 的性能，每内核配 PyTorch 参考实现与系统性基准，"内核-参考-测试"三位一体。

## ② 架构分层（按图谱 layers）

- **L1 共享基础设施**：config.py（SM 数/共享内存，set_num_sms 限核）、utils.py 对齐三件套（ceil_div/align）、testing/。
- **L2 MoE 路由内核**（11 个）：top2_sum_gate/topk_gate、expand_to_fused、reduce_fused（FP8 反量化）、get_fused_mapping + 五辅助算子。
- **L3 量化内核**（12 文件）：common.py 共享设施 + per-token/per-block/per-channel 三粒度（含无损/融合变体）+ SwiGLU 融合 + cast_back 反量化。
- **L4 Engram 内核**：hash 哈希寻址、gate 前反向、grad_w_reduce 梯度归约、fused_weight 权重融合。
- **L5 MHC 内核**（9 个）：sinkhorn、拆分/施加混合、norm_fn、post、pre_big_fuse、expand、多层重算等。
- **L6 转置内核**：批量 2D 转置，逼近带宽上限。
- **L7 PyTorch 参考实现**：纯 torch 对照，测试真值源。
- **L8 高层建模层**：autograd.Function 封装（EngramGateFn、MHC ops、functional 接口）。
- **L9 测试套件**：每内核对应的 pytest 正确性+基准用例。
- **L10 配置与测试框架**：pyproject（setuptools-scm、ruff）+ 两个自研 pytest 插件——基准插件（477 行：CUDA 事件计时、带宽/回归检测）与种子插件（节点哈希固定种子保复现）。

## ③ 核心模块

- **top2_sum_gate_kernel.py**（424 行）：最核心单内核，单 kernel 完成 top-2 选择、四评分（sigmoid/sqrtsoftplus/softmax/identity）与权重归一化。
- **MoE 路由管线**：get_fused_mapping→expand_to_fused（带 SF 变体）→reduce_fused 闭环。
- **quant/common.py**（295 行）：量化地基——向量化宽度、CastConfig、SF 分配/计算/加载/存储全流程；types.py 定（数据,SF）二元组。
- **engram_gate_kernel.py**（570 行最大文件）：前向融合 RMSNorm+哈希寻址+top-k 门控，反向完整反传。
- **MHC 亮点**：pre_big_fuse 多步融为单 kernel；multilayer_recompute 指针表跨层重算（计算换访存）。
- **torch/ 参考**：cast.py 位级 E2M1/FP8 编解码（RTZ 细节）、topk.py 复刻四评分——真值标尺。
- **modeling/**：把内核升级为可训练层接入训练图。

## ④ 快速上手（摘自 README）

**环境**：Python≥3.10、PyTorch≥2.10、TileLang≥0.1.9、SM90/SM100 GPU、CUDA≥13.1。

**安装**：开发版 `pip install -e ".[dev]"`；发行版 `pip install tile-kernels`。

**测试**：`pytest tests/transpose/test_transpose.py -n 4`（正确性）；加 `--run-benchmark` 附基准；压测 `TK_FULL_TEST=1 pytest -n 4 --count 2`。

**目录**：tile_kernels/ 下 moe/quant/transpose/engram/mhc/modeling/torch/testing 八子包，tests/ 同分域。

## ⑤ 学习路径（按 12 步导览串讲）

1. 总览：README + pyproject，记六大域与硬件要求。2. 共享设施：set_num_sms 与对齐三件套。3. 质量体系：两个 pytest 插件与断言工具，先懂验证再学内核。4. 核心内核：精读 top2_sum_gate，对照 scoring.py 四种评分。5. 路由管线：expand/mapping/reduce 三件套+辅助算子。6. 量化地基：common.py 的 SF 生命周期。7. 量化 I：per_token_cast 与 per_block_cast（无损钳制变体）。8. 量化 II：SwiGLU 融合族（三重融合最激进）与 cast_back（FP8/E5M6）。9. Engram：hash→gate 前反向→梯度归约→权重融合。10. MHC：sinkhorn 归一化→拆分/施加→pre_big_fuse→多层重算。11. 参考实现：通读 torch/ 子包，理解真值源。12. 建模层收官：EngramGateFn/MHC ops 进训练图，回看 test_top2_sum_gate 体会三位一体。

节奏：1-3 步半天建骨架，4-5 步两天吃透 MoE 主线，量化/MHC 按需。
