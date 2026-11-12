# 第1章正文与配图

[Markdown 正文](../01-初识 AI Infra.md) · [HTML 阅读版](../01-初识 AI Infra.html)

本章按逐节设计组织概念、推导、例题与练习。当前共 8 幅配图，均提供 SVG 和 PNG；正文、图表中的数学表达采用 LaTeX，HTML 使用本地 KaTeX 渲染并嵌入图片与字体。

[前三章逐节设计](../../research/ch01-03-model-led-rewrite-2026-09-10/section-design.md) · [练习参考解答](../../research/ch01-03-model-led-rewrite-2026-09-10/exercise-answers.md) · [本轮修订记录](../../research/ch01-03-model-led-rewrite-2026-09-10/README.md)

## 配图

图号按阅读顺序排列，文件名保持稳定。

| 图示 | SVG | PNG |
| --- | --- | --- |
| AI Infra 六层全景：从应用需求到设备与互联，右侧为跨层平台能力，底部为共同物理条件。 | [SVG](figure-1-1-panorama.svg) | [PNG](figure-1-1-panorama.png) |
| 请求经过应用、入口、路由、实例调度、GPU 执行与输出返回；另标模型加载、KV 状态与多设备协作。 | [SVG](figure-1-2-request.svg) | [PNG](figure-1-2-request.png) |
| 数据中心通过网络连接多个超节点，放大一个超节点展示计算托盘、CPU 与主存、GPU 与 HBM、内部互联和网卡。 | [SVG](figure-1-3-datacenter.svg) | [PNG](figure-1-3-datacenter.png) |
| 关键数字分为历史访问延迟与 H100 SXM 资源卡。延迟采用对数刻度；容量、带宽与计算吞吐分别列示。 | [SVG](figure-1-4-numbers.svg) | [PNG](figure-1-4-numbers.png) |
| 图 1-5 每卡容量与执行时的权重读取 | [SVG](figure-1-capacity-path.svg) | [PNG](figure-1-capacity-path.png) |
| 教学模型的算力、带宽和批复用变化，以及独立 Qwen3-8B 实测中的吞吐和每请求时间。 | [SVG](figure-1-5-budget.svg) | [PNG](figure-1-5-budget.png) |
| 图 1-7 batch 增长时的计算、读取与吞吐转折 | [SVG](figure-1-batch-transition.svg) | [PNG](figure-1-batch-transition.png) |
| TPU、SmartNIC 与 Unified Bus 分别改变专用资源配置、处理位置和协作范围。 | [SVG](figure-1-6-designs.svg) | [PNG](figure-1-6-designs.png) |

## 构建与数据

在仓库根目录安装本目录 requirements.txt 中的依赖，并准备 Node.js，运行：

```sh
python manuscripts/ch01/build.py
```

生成器查找 macOS 或 Noto 中文字体，也可使用 `--font /path/to/font.ttf`。共享机制图由 [teaching_figures.py](../teaching_figures.py) 生成。

[sources.json](sources.json) 保存输入文件及哈希；[figure-data.json](figure-data.json) 保存绘图数据；[manifest.json](manifest.json) 保存生成产物校验值；[math-validation.json](math-validation.json) 记录公式解析。输入变化时须先审查再更新来源锁。本轮使用已有 calculations、survey 与实验记录以及明确给出的教学条件，没有执行新的 GPU 实验。
