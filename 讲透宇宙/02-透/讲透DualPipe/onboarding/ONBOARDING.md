# DualPipe 新人指南（简版）

> 依据仓库知识图谱（40 节点/92 边/6 层/9 步导览）与 README 整理。姊妹篇：《讲透EPLB》《讲透LPLB》。

## 一、项目定位

DualPipe 是 DeepSeek-V3 技术报告（arXiv:2412.19437）提出的**双向流水线并行算法**：微批从流水线两端同时注入、对称相向推进，让前向与反向的通信阶段被计算完全覆盖，同时压缩流水线气泡。代码极小（`dualpipe/` 包 4 个文件），本质是一份可运行算法参考实现而非生产框架。

包内还提供 **DualPipeV**——Sea AI Lab 对 DualPipe 做 "cut-in-half" 得到的 V 形调度，用一半设备达到同等气泡/内存指标。

家族定位：DualPipe 解决**流水线维度**的效率问题；EPLB/LPLB 解决 **MoE 专家维度**的负载不均；三者与 DeepEP（通信库）、3FS（存储）共同构成 DeepSeek 训推基础设施。

## 二、架构分层

知识图谱 6 层，自顶向下：

1. **入口与包结构层**：`__init__.py` 重导出 DualPipe/DualPipeV/WeightGradStore 与 P2P 配置。
2. **流水线引擎层**：`dualpipe.py`、`dualpipev.py`——双向与 V 形两个调度引擎。
3. **P2P 通信层**：`comm.py`——shapes/dtype 全局配置、接收缓冲预分配、批量 isend/irecv 打包。
4. **张量与梯度工具层**：`utils.py`——WeightGradStore、run_backward、scatter/gather 切分重组。
5. **示例与验证层**：`examples/` 两个端到端正确性示例。
6. **文档与构建层**：README（调度图、气泡/内存对比表）与 setup.py。

## 三、核心模块

- **DualPipe 引擎**：`step()` 手工展开 8 PP rank × 20 micro-batch 双向调度表，交错执行 forward / backward / forward_backward / weight 四类 chunk；两个方向对称，成对 chunk 经 `overlapped_forward_backward` 重叠执行；`_commit_and_wait_comm` 把通信打包成批量 P2P。
- **DualPipeV**：结构与 DualPipe 镜像，差异在阶段边界用 `detach().requires_grad_()` 重挂梯度衔接反向图。
- **WeightGradStore（关键机制）**：backward 时把权重梯度计算打包成闭包入队（put/flush），由调度的 weight chunk 时机再执行，使权重更新可与通信重叠；`run_backward` 直连 autograd 引擎精确控制反传入口。
- **comm.py**：`set_p2p_tensor_shapes/dtype` 配置 → `build_from_tensor_shapes` 预分配接收缓冲 → `append_irecv/append_isend` 打包成 `dist.P2POp` 供 `batch_isend_irecv` 一次提交——这是计算-通信重叠的前提。

气泡对比（PP 为偶数阶段数）：1F1B 气泡 (PP−1)(F+B)；DualPipe 仅 (PP/2−1)(F&B+B−3W)；代价是参数每设备 2×、激活 PP+1。

## 四、快速上手

```bash
pip install -e .        # 依赖 PyTorch >= 2.0
python examples/example_dualpipe.py
python examples/example_dualpipev.py
```

示例用多进程拉起 8 卡（不足会自动减小规模），与朴素串行参考逐步比对输出、损失、all_gather 后的权重梯度，全部对齐即正确。README 明确提示：真实模型需为每个流水线阶段实现自定义 `overlapped_forward_backward`（成对 chunk 内先前后反），并把权重梯度改造为可延迟计算——两个示例就是模板。

## 五、学习路径

1. 读 README：调度图（黑框包围的两格=互相重叠的通信与计算）+ 气泡/内存对比表。
2. 跑 `example_dualpipe.py`，看 `LinearFunc` 如何把权重梯度交给 WeightGradStore、`PipelineStage` 如何实现重叠接口。
3. 精读 `dualpipe.py` 的 `step()` 调度表，对照调度图逐格理解。
4. 读 `utils.py` 的 WeightGradStore/run_backward，理解"延迟权重梯度"为何能腾出重叠窗口。
5. 对照 `dualpipev.py` 找 V 形差异；最后尝试把示例模板接到自己的小模型上。
