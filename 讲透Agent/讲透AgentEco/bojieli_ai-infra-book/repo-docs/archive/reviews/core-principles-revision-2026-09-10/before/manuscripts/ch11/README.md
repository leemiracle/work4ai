# 第十一章正文与配图

本章依据现行 outline 的 5 节、18 个小节扩写，以代码 Agent 为贯穿案例，RL 用于阶段配比与验证约束。正文包含逐步推导、带解算例、证据边界、章末小结和十项练习。

- [HTML 阅读版](../11-资源调度与运行环境.html)：离线公式、图片、目录和表格。
- [Markdown 编辑源](../11-资源调度与运行环境.md)：正式正文与外部图注。
- [写作前阅读记录](reading-notes.md)：已有 calculations、survey 与实验材料的采用范围。
- [固定来源](sources.json)、[图数据](figure-data.json)、[产物清单](manifest.json)。
- [结构与数值检查](validation.json)、[公式检查](math-validation.json)、[浏览器检查](browser-validation.json)。

## 插图

全部由本书脚本绘制，图内无“图 11-1”或其他章节图号，编号和解释只在正文 caption。机制图的几何长度不充当测量值；定量图注明教学参数和已有计算来源。SVG 用于编辑，PNG 用于跨设备阅读，PDF 用于排版导出。

| 图号 | 内容 | SVG | PNG | PDF |
| --- | --- | --- | --- | --- |
| 11-1 | 模型调用、工具工作和环境驻留的三轮时间线 | [SVG](figure-11-1-timeline.svg) | [PNG](figure-11-1-timeline.png) | [PDF](figure-11-1-timeline.pdf) |
| 11-2 | 模型响应变慢对三类资源需求的不同影响 | [SVG](figure-11-capacity.svg) | [PNG](figure-11-capacity.png) | [PDF](figure-11-capacity.pdf) |
| 11-3 | Agent 控制器、平台、模型服务与工具隔离边界 | [SVG](figure-11-2-boundary.svg) | [PNG](figure-11-2-boundary.png) | [PDF](figure-11-2-boundary.pdf) |
| 11-4 | 不同环境内容加载方式的本地数据量 | [SVG](figure-11-pages.svg) | [PNG](figure-11-pages.png) | [PDF](figure-11-pages.pdf) |
| 11-5 | 同一段模型等待中的内存保留与暂停恢复 | [SVG](figure-11-pause.svg) | [PNG](figure-11-pause.png) | [PDF](figure-11-pause.pdf) |
| 11-6 | 全程保留环境与每轮重建的内存占用时间 | [SVG](figure-11-residency.svg) | [PNG](figure-11-residency.png) | [PDF](figure-11-residency.pdf) |
| 11-7 | 准备提前量与调用等待的关系 | [SVG](figure-11-3-lifecycle.svg) | [PNG](figure-11-3-lifecycle.png) | [PDF](figure-11-3-lifecycle.pdf) |
| 11-8 | 资源碎片与迁移整理前后的节点配置 | [SVG](figure-11-4-placement.svg) | [PNG](figure-11-4-placement.png) | [PDF](figure-11-4-placement.pdf) |
| 11-9 | 均匀到达与同时到达时的排队过程 | [SVG](figure-11-queue.svg) | [PNG](figure-11-queue.png) | [PDF](figure-11-queue.pdf) |
| 11-10 | 生成速度加倍后仍未缩短的其他阶段 | [SVG](figure-11-rl-stages.svg) | [PNG](figure-11-rl-stages.png) | [PDF](figure-11-rl-stages.pdf) |
| 11-11 | 六个接收实例共用一个发送出口 | [SVG](figure-11-weights.svg) | [PNG](figure-11-weights.png) | [PDF](figure-11-weights.pdf) |
| 11-12 | 逐条提交与整批后提交的验证时间线 | [SVG](figure-11-5-stages.svg) | [PNG](figure-11-5-stages.png) | [PDF](figure-11-5-stages.pdf) |
| 11-13 | 思考缩短后单次费用的组成 | [SVG](figure-11-thinking.svg) | [PNG](figure-11-thinking.png) | [PDF](figure-11-thinking.pdf) |
| 11-14 | 模型服务入口、后端选择及计费位置 | [SVG](figure-11-6-service.svg) | [PNG](figure-11-6-service.png) | [PDF](figure-11-6-service.pdf) |
| 11-15 | 费用曲线与按时通过测试的要求的交点 | [SVG](figure-11-7-routing.svg) | [PNG](figure-11-7-routing.png) | [PDF](figure-11-7-routing.pdf) |
| 11-16 | 固定支出与每项任务费用决定采购交点 | [SVG](figure-11-purchase.svg) | [PNG](figure-11-purchase.png) | [PDF](figure-11-purchase.pdf) |
| 11-17 | 重试分支的概率与累计完成时间 | [SVG](figure-11-retry-tree.svg) | [PNG](figure-11-retry-tree.png) | [PDF](figure-11-retry-tree.pdf) |
| 11-18 | 恢复策略的单位成本与完成比例比较 | [SVG](figure-11-8-retry.svg) | [PNG](figure-11-8-retry.png) | [PDF](figure-11-8-retry.pdf) |
| 11-19 | 普通模型与快速模型的三轮完成时间 | [SVG](figure-11-decision.svg) | [PNG](figure-11-decision.png) | [PDF](figure-11-decision.pdf) |

## 复现

需要 Python 3、Node.js；绘图依赖见 requirements.txt。浏览器检查另需 Playwright 和 Chrome／Chromium。KaTeX 0.16.11 的运行文件与许可证保存在 vendor 中，HTML 内嵌公式字体与 PNG，无 CDN 依赖。

```sh
python -m pip install -r manuscripts/ch11/requirements.txt
python manuscripts/ch11/build.py
python manuscripts/ch11/verify.py
python manuscripts/ch11/check_reading.py
```

构建脚本只写本章图片、HTML、图数据和清单，不执行模型、创建云环境或改写 calculations／experiments。若 sources.json 中任一已读来源变化，脚本拒绝继续，需先检查其变化如何影响正文。可用 `--font /path/to/font.ttf` 指定中文字体。

## 实验编号

沿用现行 outline：11-1、11-2、11-10 为核心。预热为当前 11-3，成组作业为 11-4，rollout 恢复为 11-5，验证为 11-6，模型路由为 11-7，采购为 11-8。既有目录保留旧编号；[映射表](../../research/ch11-reorganization-2026-09-10/README.md)解释每项练习与证据地址。

本章没有新增云端或 GPU 实测。局部进程 RSS 不代表完整环境内存，有限重试和路由概率为教学输入，自建／API 基线同时采用后续优化审计的限定。

## 量化叙述修订

本轮将版本和核验进度收进注释，用同一组条件连续推导容量、等待和成本。图 11-2、11-3、11-5、11-7、11-8 已按单一关系重绘，数值精度随用途调整；精确计算和原稿仍保留。见[修订记录](../../research/ch11-teaching-revision-2026-09-10/README.md)。

## 全章连贯推导修订

正文以同一个代码修复平台贯穿需求、生命周期、模型选择和最终设计。新增[精确设计数据](platform-design.json)与[计算程序](platform_design.py)，构建时自动生成；事件扫描核对每阶段依赖、资源积分及峰值，费用比较包含四个方案和轮间等待交点。常驻环境循环复用，每轮重建环境按轮支付准备开销；条件在正文计算前给出。原始 calculations 和 survey 证据保持原有锁定。

修订前版本与论证调整见[本轮记录](../../research/ch11-coherent-revision-2026-09-10/README.md)。

本章中文术语与句式已统一修订，见[表达修订记录](../../research/ch11-language-revision-2026-09-10/README.md)。正文采用累计 CPU 时间、并发调用数、每轮重建环境等表达，并解释计量单位。

已逐段修订中文语序、搭配和句间衔接，见[句式修订记录](../../research/ch11-fluency-revision-2026-09-10/README.md)。

## 图示与段落衔接

本轮新增 11 张图，全章共 19 张；图号按正文顺序重排，文件名保留稳定地址。新增绘图程序为 [extra_figures.py](extra_figures.py)，图号映射见 [figure-order.json](figure-order.json)。段落过渡围绕尚未解决的问题展开，时间线、排队图、费用组成和重试分支均有对应的数值复核。见[修订记录](../../research/ch11-visual-narrative-2026-09-10/README.md)。
