# 第3章正文与配图

[Markdown 正文](../03-推理与训练负载.md) · [HTML 阅读版](../03-推理与训练负载.md)

本章按逐节设计组织概念、推导、例题与练习。当前共 12 幅配图，均提供 SVG 和 PNG；正文、图表中的数学表达采用 LaTeX，HTML 使用本地 KaTeX 渲染并嵌入图片与字体。

[前三章逐节设计](../../research/ch01-03-model-led-rewrite-2026-09-10/section-design.md) · [练习参考解答](../../research/ch01-03-model-led-rewrite-2026-09-10/exercise-answers.md) · [本轮修订记录](../../research/ch01-03-model-led-rewrite-2026-09-10/README.md)

## 配图

图号按阅读顺序排列，文件名保持稳定。

| 图示 | SVG | PNG |
| --- | --- | --- |
| 图 3-1 同一模型的 Prefill 与 Decode | [SVG](figure-3-1-stages.svg) | [PNG](figure-3-1-stages.png) |
| 图 3-2 请求组成与阶段积压 | [SVG](figure-3-2-workload-budget.svg) | [PNG](figure-3-2-workload-budget.png) |
| 图 3-3 每次尝试的费用与每个成功任务的费用 | [SVG](figure-3-success-cost.svg) | [PNG](figure-3-success-cost.png) |
| 图 3-4 Agent 轨迹与 KV 生命周期 | [SVG](figure-3-3-agent.svg) | [PNG](figure-3-3-agent.png) |
| 图 3-5 工具依赖决定关键路径与状态寿命 | [SVG](figure-3-tool-dependency.svg) | [PNG](figure-3-tool-dependency.png) |
| 图 3-6 图像位置合并与特征宽度的变化 | [SVG](figure-3-vision-shapes.svg) | [PNG](figure-3-vision-shapes.png) |
| 图 3-7 实时交互的端到端时序 | [SVG](figure-3-4-realtime.svg) | [PNG](figure-3-4-realtime.png) |
| 图 3-8 推理与各训练阶段的计算和状态 | [SVG](figure-3-5-training.svg) | [PNG](figure-3-5-training.png) |
| 图 3-9 RL／OPD 的工作与数据流 | [SVG](figure-3-6-rl.svg) | [PNG](figure-3-6-rl.png) |
| 图 3-10 训练预算与生命周期成本 | [SVG](figure-3-7-scaling.svg) | [PNG](figure-3-7-scaling.png) |
| 图 3-11 Llama 与 Qwen 的模型—数据选择 | [SVG](figure-3-8-history.svg) | [PNG](figure-3-8-history.png) |
| 图 3-12 公开 GPU 小时与训练阶段 | [SVG](figure-3-9-gpu-hours.svg) | [PNG](figure-3-9-gpu-hours.png) |

## 构建与数据

在仓库根目录安装本目录 requirements.txt 中的依赖，并准备 Node.js，运行：

```sh
python manuscripts/ch03/build.py
```

生成器查找 macOS 或 Noto 中文字体，也可使用 `--font /path/to/font.ttf`。共享机制图由 [teaching_figures.py](../teaching_figures.py) 生成。

[sources.json](sources.json) 保存输入文件及哈希；[figure-data.json](figure-data.json) 保存绘图数据；[manifest.json](manifest.json) 保存生成产物校验值；[math-validation.json](math-validation.json) 记录公式解析。输入变化时须先审查再更新来源锁。本轮使用已有 calculations、survey 与实验记录以及明确给出的教学条件，没有执行新的 GPU 实验。

## 当前阅读版配图（2026-09-10）

正文现引用 32 幅图，以下清单按当前阅读顺序列出；上文旧图号用于追溯构建记录。

| 图号 | 内容 | SVG | PNG | PDF |
| --- | --- | --- | --- | --- |
| 3-1 | 恢复 6144 个上下文位置，处理 2048 个新输入并生成四个输出。首输出来自 prefill，后续三次 decode 各追加一个位置；纵向表示调用次序，间距用于示意。 | [SVG](figure-3-1-stages.svg) | [PNG](figure-3-1-stages.png) | [PDF](figure-3-1-stages.pdf) |
| 3-2 | 请求到达、首输出与末输出决定三个计时区间。首响应包含开始生成前的等待，输出间隔描述生成过程，完整请求时间从到达累计到结束。 | [SVG](figure-3-request-clocks.svg) | [PNG](figure-3-request-clocks.png) | [PDF](figure-3-request-clocks.pdf) |
| 3-3 | 保留 1 GiB 状态等待十秒，对应面积为 10 GiB·s。横轴为状态存活时间，纵轴为占用空间；面积描述这段等待消耗的空间时间。 | [SVG](figure-3-state-time-area.svg) | [PNG](figure-3-state-time-area.png) | [PDF](figure-3-state-time-area.pdf) |
| 3-4 | 相同两分钟总量的三种窗口组成。长输入类为 8192 输入、256 输出，长输出类为 1024 输入、2048 输出；两类混合比例改变阶段需求。 | [SVG](figure-3-2-workload-budget.svg) | [PNG](figure-3-2-workload-budget.png) | [PDF](figure-3-2-workload-budget.pdf) |
| 3-5 | 三种窗口组成对应的输入与后续生成需求。输入数按 token 计，后续生成按每请求的一次 decode 步计；每请求首输出已计入 prefill。 | [SVG](figure-3-stage-demand.svg) | [PNG](figure-3-stage-demand.png) | [PDF](figure-3-stage-demand.pdf) |
| 3-6 | 工作先进入队列，再由处理资源完成。到来快于处理时差额留在队列中；处理快于到来时，资源逐步消化已有积压。 | [SVG](figure-3-queue-mechanism.svg) | [PNG](figure-3-queue-mechanism.png) | [PDF](figure-3-queue-mechanism.pdf) |
| 3-7 | 每秒完成 6144 个 decode 步的流体模型。后一分钟积压至 79,632 步，120 秒后停止到达，再经过约 12.96 秒排空。 | [SVG](figure-3-queue-backlog.svg) | [PNG](figure-3-queue-backlog.png) | [PDF](figure-3-queue-backlog.pdf) |
| 3-8 | 同一实际实例回放两种到达序列的结果。完整请求 p95 接近，首响应 p95 则相差约十六秒；模型、设备、KV 池与并发上限均按正文实验条件固定。 | [SVG](figure-3-arrival-measured.svg) | [PNG](figure-3-arrival-measured.png) | [PDF](figure-3-arrival-measured.pdf) |
| 3-9 | 各尝试 100 次的教学比较。所有尝试的成本都进入分子，通过检查的成功任务数进入分母；两种策略的成功任务成本分别为 2 和 2.5 单位。 | [SVG](figure-3-success-cost.svg) | [PNG](figure-3-success-cost.png) | [PDF](figure-3-success-cost.pdf) |
| 3-10 | 代码任务四轮调用的模型墙钟时间，各轮从自己的起点计时。模型时间合计 76.294 秒，工具合计约 0.078 秒，整任务另含控制与交接时间。 | [SVG](figure-3-3-agent.svg) | [PNG](figure-3-3-agent.png) | [PDF](figure-3-3-agent.pdf) |
| 3-11 | 两个工具存在前后依赖时的任务时间线。模型先运行两秒，工具 A 用六秒，工具 B 用十秒，模型最后运行三秒，总计二十一秒。 | [SVG](figure-3-tool-dependency.svg) | [PNG](figure-3-tool-dependency.png) | [PDF](figure-3-tool-dependency.pdf) |
| 3-12 | 两个工具独立时可以同时开始，模型在较慢的工具 B 完成后继续，任务共十五秒。与前图使用相同时间尺度；工具工作总量仍为十六秒。 | [SVG](figure-3-tool-parallel.svg) | [PNG](figure-3-tool-parallel.png) | [PDF](figure-3-tool-parallel.pdf) |
| 3-13 | 两个生成分支指向同一份公共前缀，并各自保存新增尾部。箭头表示引用关系，共享前缀只计一份容量。 | [SVG](figure-3-branch-state.svg) | [PNG](figure-3-branch-state.png) | [PDF](figure-3-branch-state.pdf) |
| 3-14 | 图像从像素网格变为模型位置。640 方图切成 40×40 个块，相邻 2×2 块合并成一个位置，形成 20×20、共 400 个位置。 | [SVG](figure-3-vision-shapes.svg) | [PNG](figure-3-vision-shapes.png) | [PDF](figure-3-vision-shapes.pdf) |
| 3-15 | 位置数与每位置特征宽度分别计量。四组 2560 维 BF16 编码特征占 7.8125 MiB；这些位置进入语言模型后，另产生各层的 KV 状态。 | [SVG](figure-3-vision-state.svg) | [PNG](figure-3-vision-state.png) | [PDF](figure-3-vision-state.pdf) |
| 3-16 | 可组合的多模态阶段。编码形成模型输入，语言模型生成回复，声学模块将回复转成音频，接收端缓冲与播放设备决定何时真正发声。 | [SVG](figure-3-4-realtime.svg) | [PNG](figure-3-4-realtime.png) | [PDF](figure-3-4-realtime.pdf) |
| 3-17 | 八块音频的教学播放时间线。每块长二十毫秒，圆点标到达，短竖线标原定播放时刻，色条标实际播放；第三块晚到五毫秒，后续播放随之顺延。 | [SVG](figure-3-audio-timing.svg) | [PNG](figure-3-audio-timing.png) | [PDF](figure-3-audio-timing.pdf) |
| 3-18 | 同一教学场景中的本地打断。123 ms 发出操作，130 ms 设备静音；远端计算是否停止属于另一条控制路径。 | [SVG](figure-3-audio-interrupt.svg) | [PNG](figure-3-audio-interrupt.png) | [PDF](figure-3-audio-interrupt.pdf) |
| 3-19 | 一层激活从前向完成后保留到相应反向用完。横轴按事件排列，间距表示过程顺序；反向需要的前向输入决定这段存活区间。 | [SVG](figure-3-activation-lifetime.svg) | [PNG](figure-3-activation-lifetime.png) | [PDF](figure-3-activation-lifetime.pdf) |
| 3-20 | 训练沿前向依赖计算输出，再沿反向依赖传递梯度。当前层既向前层传输入梯度，也计算自己的权重梯度，供优化器更新。 | [SVG](figure-3-5-training.svg) | [PNG](figure-3-5-training.png) | [PDF](figure-3-5-training.pdf) |
| 3-21 | Qwen3-8B 全参数训练的参数相关状态。每参数包括两字节计算权重和四组四字节状态，共十八字节；激活和工作区由各自寿命另行核算。 | [SVG](figure-3-training-states.svg) | [PNG](figure-3-training-states.png) | [PDF](figure-3-training-states.pdf) |
| 3-22 | Qwen3-8B 的 8192 输入全参数训练。全部位置执行词表头、没有重计算；按矩阵逐项累计，前向加反向为 431.368 TFLOPs。 | [SVG](figure-3-training-flops.svg) | [PNG](figure-3-training-flops.png) | [PDF](figure-3-training-flops.pdf) |
| 3-23 | 强化学习中的角色和数据流。生成端产生回答，反馈环节评价结果，筛选后送给学习器更新；新权重再用于下一批生成。 | [SVG](figure-3-6-rl.svg) | [PNG](figure-3-6-rl.png) | [PDF](figure-3-6-rl.pdf) |
| 3-24 | 保持十六条有效样本目标，生成数由三十二增到六十四。生成输入、后续生成和参考评分随全部回答增加，策略更新处理的样本数保持相同。 | [SVG](figure-3-rl-stage-work.svg) | [PNG](figure-3-rl-stage-work.png) | [PDF](figure-3-rl-stage-work.pdf) |
| 3-25 | 八个公开 C4 观测的预测与实际损失。六点用于拟合，两点预先留出作检验；对角线表示预测等于观测，点到线的偏差反映误差。 | [SVG](figure-3-7-scaling.svg) | [PNG](figure-3-7-scaling.png) | [PDF](figure-3-7-scaling.pdf) |
| 3-26 | 同一组预测误差的放大视图。F1—F6 为拟合点，H1—H2 为留出点；纵轴是预测减观测，保留正负号。 | [SVG](figure-3-scaling-residual.svg) | [PNG](figure-3-scaling-residual.png) | [PDF](figure-3-scaling-residual.pdf) |
| 3-27 | 训练与服务累计成本的题设比较。截距是训练投入，斜率是单次调用成本；虚线标出超出拟合参数或数据范围的方案，竖线为约 2.048 亿次的成本交点。 | [SVG](figure-3-lifecycle-cost.svg) | [PNG](figure-3-lifecycle-cost.png) | [PDF](figure-3-lifecycle-cost.pdf) |
| 3-28 | 相近参数规模的模型投入不同数量的训练 token。柱值为报告训练数据量除以参数数，Qwen 采用模型家族披露的数据预算。 | [SVG](figure-3-8-history.svg) | [PNG](figure-3-8-history.png) | [PDF](figure-3-8-history.pdf) |
| 3-29 | MoE 的总参数与每 token 激活参数分别对应容量和部分计算需求。图中采用公开报告的总量与激活量，二者都使用十亿参数为单位。 | [SVG](figure-3-moe-history.svg) | [PNG](figure-3-moe-history.png) | [PDF](figure-3-moe-history.pdf) |
| 3-30 | 采用 A100 80GB 的 Llama 训练用量。各柱是公开 GPU 小时，同一张图使用相同设备类别与线性尺度。 | [SVG](figure-3-9-gpu-hours.svg) | [PNG](figure-3-9-gpu-hours.png) | [PDF](figure-3-9-gpu-hours.pdf) |
| 3-31 | 采用 H100 80GB 的 Llama 3.1 训练用量。纵轴分模型规模，横轴为百万 GPU 小时；设备类别与前图分开呈现。 | [SVG](figure-3-h100-hours.svg) | [PNG](figure-3-h100-hours.png) | [PDF](figure-3-h100-hours.pdf) |
| 3-32 | DeepSeek-V3 采用 H800 的三个训练阶段。分别累计预训练、上下文扩展与后训练用量，保留各阶段的公开统计范围。 | [SVG](figure-3-v3-stage-hours.svg) | [PNG](figure-3-v3-stage-hours.png) | [PDF](figure-3-v3-stage-hours.pdf) |


## V4／V4.1 会话修订后的当前图表

当前正文共 33 幅图；下表是当前图号，前文旧图号保留作历史记录。

| 图号 | 内容 | 文件 |
| --- | --- | --- |
| 3-1 | 恢复 6144 个上下文位置，处理 2048 个新输入并生成四个输出。首输出来自 prefill，后续三次 decode 各追加一个位置；纵向表示调用次序，间距用于示意。 | [SVG](figure-3-1-stages.svg) |
| 3-2 | 请求到达、首输出与末输出决定三个计时区间。首响应包含开始生成前的等待，输出间隔描述生成过程，完整请求时间从到达累计到结束。 | [SVG](figure-3-request-clocks.svg) |
| 3-3 | 保留 1 GiB 状态等待十秒，对应面积为 10 GiB·s。横轴为状态存活时间，纵轴为占用空间；面积描述这段等待消耗的空间时间。 | [SVG](figure-3-state-time-area.svg) |
| 3-4 | 相同两分钟总量的三种窗口组成。长输入类为 8192 输入、256 输出，长输出类为 1024 输入、2048 输出；两类混合比例改变阶段需求。 | [SVG](figure-3-2-workload-budget.svg) |
| 3-5 | 三种窗口组成对应的输入与后续生成需求。输入数按 token 计，后续生成按每请求的一次 decode 步计；每请求首输出已计入 prefill。 | [SVG](figure-3-stage-demand.svg) |
| 3-6 | 工作先进入队列，再由处理资源完成。到来快于处理时差额留在队列中；处理快于到来时，资源逐步消化已有积压。 | [SVG](figure-3-queue-mechanism.svg) |
| 3-7 | 每秒完成 6144 个 decode 步的流体模型。后一分钟积压至 79,632 步，120 秒后停止到达，再经过约 12.96 秒排空。 | [SVG](figure-3-queue-backlog.svg) |
| 3-8 | 同一实际实例回放两种到达序列的结果。完整请求 p95 接近，首响应 p95 则相差约十六秒；模型、设备、KV 池与并发上限均按正文实验条件固定。 | [SVG](figure-3-arrival-measured.svg) |
| 3-9 | 各尝试 100 次的教学比较。所有尝试的成本都进入分子，通过检查的成功任务数进入分母；两种策略的成功任务成本分别为 2 和 2.5 单位。 | [SVG](figure-3-success-cost.svg) |
| 3-10 | 代码任务四轮调用的模型墙钟时间，各轮从自己的起点计时。模型时间合计 76.294 秒，工具合计约 0.078 秒，整任务另含控制与交接时间。 | [SVG](figure-3-3-agent.svg) |
| 3-11 | 两个工具存在前后依赖时的任务时间线。模型先运行两秒，工具 A 用六秒，工具 B 用十秒，模型最后运行三秒，总计二十一秒。 | [SVG](figure-3-tool-dependency.svg) |
| 3-12 | 两个工具独立时可以同时开始，模型在较慢的工具 B 完成后继续，任务共十五秒。与前图使用相同时间尺度；工具工作总量仍为十六秒。 | [SVG](figure-3-tool-parallel.svg) |
| 3-13 | 两个生成分支指向同一份公共前缀，并各自保存新增尾部。箭头表示引用关系，共享前缀只计一份容量。 | [SVG](figure-3-branch-state.svg) |
| 3-14 | 同一批 8K 输入的专家矩阵 token 层数。普通全层路径执行 40 层；CED 路径执行 20 层编码器，并为最近 128 个 token 重放 20 层解码器。灰色说明项仍需另外计算；生成阶段执行完整主干。 | [SVG](figure-3-v41-ced.svg) |
| 3-15 | 图像从像素网格变为模型位置。640 方图切成 40×40 个块，相邻 2×2 块合并成一个位置，形成 20×20、共 400 个位置。 | [SVG](figure-3-vision-shapes.svg) |
| 3-16 | 位置数与每位置特征宽度分别计量。四组 2560 维 BF16 编码特征占 7.8125 MiB；这些位置进入语言模型后，另产生各层的 KV 状态。 | [SVG](figure-3-vision-state.svg) |
| 3-17 | 可组合的多模态阶段。编码形成模型输入，语言模型生成回复，声学模块将回复转成音频，接收端缓冲与播放设备决定何时真正发声。 | [SVG](figure-3-4-realtime.svg) |
| 3-18 | 八块音频的教学播放时间线。每块长二十毫秒，圆点标到达，短竖线标原定播放时刻，色条标实际播放；第三块晚到五毫秒，后续播放随之顺延。 | [SVG](figure-3-audio-timing.svg) |
| 3-19 | 同一教学场景中的本地打断。123 ms 发出操作，130 ms 设备静音；远端计算是否停止属于另一条控制路径。 | [SVG](figure-3-audio-interrupt.svg) |
| 3-20 | 一层激活从前向完成后保留到相应反向用完。横轴按事件排列，间距表示过程顺序；反向需要的前向输入决定这段存活区间。 | [SVG](figure-3-activation-lifetime.svg) |
| 3-21 | 训练沿前向依赖计算输出，再沿反向依赖传递梯度。当前层既向前层传输入梯度，也计算自己的权重梯度，供优化器更新。 | [SVG](figure-3-5-training.svg) |
| 3-22 | Qwen3-8B 全参数训练的参数相关状态。每参数包括两字节计算权重和四组四字节状态，共十八字节；激活和工作区由各自寿命另行核算。 | [SVG](figure-3-training-states.svg) |
| 3-23 | Qwen3-8B 的 8192 输入全参数训练。全部位置执行词表头、没有重计算；按矩阵逐项累计，前向加反向为 431.368 TFLOPs。 | [SVG](figure-3-training-flops.svg) |
| 3-24 | 强化学习中的角色和数据流。生成端产生回答，反馈环节评价结果，筛选后送给学习器更新；新权重再用于下一批生成。 | [SVG](figure-3-6-rl.svg) |
| 3-25 | 保持十六条有效样本目标，生成数由三十二增到六十四。生成输入、后续生成和参考评分随全部回答增加，策略更新处理的样本数保持相同。 | [SVG](figure-3-rl-stage-work.svg) |
| 3-26 | 八个公开 C4 观测的预测与实际损失。六点用于拟合，两点预先留出作检验；对角线表示预测等于观测，点到线的偏差反映误差。 | [SVG](figure-3-7-scaling.svg) |
| 3-27 | 同一组预测误差的放大视图。F1—F6 为拟合点，H1—H2 为留出点；纵轴是预测减观测，保留正负号。 | [SVG](figure-3-scaling-residual.svg) |
| 3-28 | 训练与服务累计成本的题设比较。截距是训练投入，斜率是单次调用成本；虚线标出超出拟合参数或数据范围的方案，竖线为约 2.048 亿次的成本交点。 | [SVG](figure-3-lifecycle-cost.svg) |
| 3-29 | 相近参数规模的模型投入不同数量的训练 token。柱值为报告训练数据量除以参数数，Qwen 采用模型家族披露的数据预算。 | [SVG](figure-3-8-history.svg) |
| 3-30 | MoE 的总参数与每 token 激活参数分别对应容量和部分计算需求。图中采用公开报告的总量与激活量，二者都使用十亿参数为单位。 | [SVG](figure-3-moe-history.svg) |
| 3-31 | 采用 A100 80GB 的 Llama 训练用量。各柱是公开 GPU 小时，同一张图使用相同设备类别与线性尺度。 | [SVG](figure-3-9-gpu-hours.svg) |
| 3-32 | 采用 H100 80GB 的 Llama 3.1 训练用量。纵轴分模型规模，横轴为百万 GPU 小时；设备类别与前图分开呈现。 | [SVG](figure-3-h100-hours.svg) |
| 3-33 | DeepSeek-V3 采用 H800 的三个训练阶段。分别累计预训练、上下文扩展与后训练用量，保留各阶段的公开统计范围。 | [SVG](figure-3-v3-stage-hours.svg) |
