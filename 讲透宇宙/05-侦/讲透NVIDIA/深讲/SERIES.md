# 深讲系列 · NVIDIA 全栈七线（2026-11-04 起）

**方法论**：费曼学习法（输出倒逼输入）+ 第一性原理（每线从一个物理/工程必然性出发推导）+ 程序员视角（落到 API/代码/调试实操）。

**原料三层**：
1. `../../../../讲透宇宙/05-侦/讲透NVIDIA//<repo>/deepwiki/`（282 仓 wiki 全文，INDEX.md 入口）
2. 本地源码 `/usr-data/data2/repos/agent-repos/NVIDIA/<repo>/`（行号锚必须从源码核实）
3. 横切底座 `/usr-data/data2/repos/deepseek-ai/distilled/nvidia/NVIDIA-CUDA-STACK.md`（七层栈地图+三问分析，2026-11-03）

**统一六节结构**（每篇 3500-6000 字，不计空格口径）：
1. 第一性原理设问——这一线存在的物理/工程必然性是什么
2. 直觉层——比喻 + 为什么长成这样
3. 机制层——真实工作原理，带本地源码行号锚（≥3 个，从源码核实，禁止凭记忆）
4. 程序员实操——API/配置/调试路径，工作里怎么用
5. 批判边界——局限、失败模式、坑、适用边界
6. 费曼检验——3 道自测题（能不看书答出才算懂）+ 一句话总结

| # | 篇 | 主仓 | 一句话 |
|---|---|---|---|
| 00 | 总纲：七层栈地图与第一性原理 | 全 org | NVIDIA 栈为什么是七层、层间契约是什么 |
| 01 | 编译线：从 .cu 到 SASS | cuda-tile/numba-cuda/cuda-rust/jitify/cccl/MatX | kernel 怎么变成硬件指令 |
| 02 | 算子线：CUTLASS 与 GEMM | cutlass/cudnn-frontend/AMGX/FasterTransformer | 张量核心的第一性原理与模板架构 |
| 03 | 通信线：NCCL 与集合通信 | nccl/nvshmem/nvbandwidth/gdrcopy | 多 GPU 必然要通信，代价怎么压到最小 |
| 04 | 训练线：五维并行与 FP8 | Megatron-LM/TransformerEngine/apex/Energon/DALI | 大模型训练 = 并行策略×精度配方×数据管线 |
| 05 | 推理线：TRT-LLM 六层优化栈 | TensorRT-LLM（blog26 金矿）/TensorRT/Edge-LLM | 从 984 到 1618 tok/s 的每一步 |
| 06 | 数据线：RAPIDS | cudf/cuml/cuCollections/cuvs/cuopt | GPU 数据科学为什么快、生态位在哪 |
| 07 | 运维线：GPU 数据中心操作系统 | container-toolkit/gpu-operator/DCGM/mig-parted/nvtrust | 千卡集群的驱动/监控/切分/信任链 |
| 08 | Agent 线：NVIDIA 的 Agent 新贵 | NemoClaw/OpenShell/SkillSpector/NeMo-Agent-Toolkit | 老牌硬件厂的 agent 布局与注意力经济学 |
