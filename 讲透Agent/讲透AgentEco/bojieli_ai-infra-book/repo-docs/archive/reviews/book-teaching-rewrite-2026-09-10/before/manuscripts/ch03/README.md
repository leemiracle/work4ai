# 第3章正文与配图

[Markdown 正文](../03-推理与训练负载.md) · [HTML 阅读版](../03-推理与训练负载.html)

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
