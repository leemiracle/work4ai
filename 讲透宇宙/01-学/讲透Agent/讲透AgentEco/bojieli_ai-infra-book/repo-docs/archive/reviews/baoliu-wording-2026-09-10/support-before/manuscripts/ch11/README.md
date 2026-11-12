# 第十一章正文与配图

本章依据现行 outline 的 5 节、18 个小节扩写，以代码 Agent 为贯穿案例，RL 用于阶段配比与验证约束。正文包含逐步推导、带解算例、证据边界、章末小结和十项练习。

- [HTML 阅读版](../11-资源调度与运行环境.md)：离线公式、图片、目录和表格。
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

## 当前阅读版配图（2026-09-10）

正文现引用 39 幅图，以下清单按当前阅读顺序列出；上文旧图号用于追溯构建记录。

| 图号 | 内容 | SVG | PNG | PDF |
| --- | --- | --- | --- | --- |
| 11-1 | 三轮串行任务共需 30 s。蓝色为三次各 9 s 的模型调用，橙色为三次各 1 s 的工具执行；工具累计消耗 3 CPU·秒。 | [SVG](figure-11-1-timeline.svg) | [PNG](figure-11-1-timeline.png) | [PDF](figure-11-1-timeline.pdf) |
| 11-2 | 同一任务的环境始终占 2 GiB，持续 30 s，矩形面积为 60 GiB·秒。等待模型时仍保留环境，因而内存占用持续时间长于工具的 CPU 执行时间。 | [SVG](figure-11-memory-area.svg) | [PNG](figure-11-memory-area.png) | [PDF](figure-11-memory-area.pdf) |
| 11-3 | 每秒 10 项任务、每次模型调用 9 s 时，三种资源的需求占容量比例。柱末给出需求量／可用容量；虚线为 100%。 | [SVG](figure-11-capacity.svg) | [PNG](figure-11-capacity.png) | [PDF](figure-11-capacity.pdf) |
| 11-4 | 每次模型调用由 9 s 延长到 12 s，CPU 需求仍为 30 核；并发调用增至 360，环境内存增至 780 GiB。虚线为 100% 容量。 | [SVG](figure-11-capacity-slow.svg) | [PNG](figure-11-capacity-slow.png) | [PDF](figure-11-capacity-slow.pdf) |
| 11-5 | 代码任务经过模型服务与工具环境两条路径。控制器从模型取得参数，再向环境平台发起工具操作；执行结果成为下一轮输入。虚线框标出工具环境所在的执行节点。 | [SVG](figure-11-2-boundary.svg) | [PNG](figure-11-2-boundary.png) | [PDF](figure-11-2-boundary.pdf) |
| 11-6 | 进程拥有独立地址空间，通过权限限制访问；同一节点上的进程共享宿主内核。 | [SVG](figure-11-isolation-0.svg) | [PNG](figure-11-isolation-0.png) | [PDF](figure-11-isolation-0.pdf) |
| 11-7 | 容器为任务建立各自的资源视图和配额，底层仍使用同一宿主内核。 | [SVG](figure-11-isolation-1.svg) | [PNG](figure-11-isolation-1.png) | [PDF](figure-11-isolation-1.pdf) |
| 11-8 | microVM 让每个任务环境运行独立客体内核，通过虚拟硬件访问宿主资源。 | [SVG](figure-11-isolation-2.svg) | [PNG](figure-11-isolation-2.png) | [PDF](figure-11-isolation-2.pdf) |
| 11-9 | 模板保存共享的文件与依赖，私有内容保存环境修改；程序运行时还会占用进程内存和缓冲区。模板安装量与活跃环境内存分别核算。 | [SVG](figure-11-template-runtime.svg) | [PNG](figure-11-template-runtime.png) | [PDF](figure-11-template-runtime.pdf) |
| 11-10 | 四种方案采用相同的横轴尺度，比较每个环境本地保存的数据。另有一份共享的 2 GiB 模板，不计入各环境的柱长。数值来自例 11-2；管理开销为每环境 4 MiB。 | [SVG](figure-11-pages.svg) | [PNG](figure-11-pages.png) | [PDF](figure-11-pages.pdf) |
| 11-11 | 第 10—19 s 等待模型时始终保留 2 GiB 环境，占用 18 GiB·秒。横轴与下一图一致。 | [SVG](figure-11-pause.svg) | [PNG](figure-11-pause.png) | [PDF](figure-11-pause.pdf) |
| 11-12 | 第 10—11 s 保存状态，第 18—19 s 恢复，中间释放 7 s 内存。两个有色区间共占 4 GiB·秒，下一次工具仍在第 19 s 开始。 | [SVG](figure-11-pause-release.svg) | [PNG](figure-11-pause-release.png) | [PDF](figure-11-pause-release.pdf) |
| 11-13 | 环境从任务开始保留到结束。模型每轮 9 s、工具每轮 1 s，三轮累计占用 60 GiB·秒。与下一图使用相同横轴。 | [SVG](figure-11-residency.svg) | [PNG](figure-11-residency.png) | [PDF](figure-11-residency.pdf) |
| 11-14 | 每轮只在准备 2 s 和执行 1 s 期间保留环境，三次合计 18 GiB·秒。工作目录和结果已持久化，三轮仍在第 30 s 完成。 | [SVG](figure-11-residency-rebuild.svg) | [PNG](figure-11-residency-rebuild.png) | [PDF](figure-11-residency-rebuild.pdf) |
| 11-15 | 按需创建：第 4 s 调用到达才开始准备，第 6 s 就绪，等待 2 s。蓝色为准备，虚线为调用时刻；以下四图使用相同横轴。 | [SVG](figure-11-3-lifecycle.svg) | [PNG](figure-11-3-lifecycle.png) | [PDF](figure-11-3-lifecycle.pdf) |
| 11-16 | 预测正确且提前 1 s：从第 3 s 准备到第 5 s，调用在第 4 s 到达后仍需等 1 s。 | [SVG](figure-11-prewarm-1.svg) | [PNG](figure-11-prewarm-1.png) | [PDF](figure-11-prewarm-1.pdf) |
| 11-17 | 预测正确且提前 2 s：准备恰好在第 4 s 调用到达时完成。 | [SVG](figure-11-prewarm-2.svg) | [PNG](figure-11-prewarm-2.png) | [PDF](figure-11-prewarm-2.pdf) |
| 11-18 | 预测正确且提前 3 s：准备在第 3 s 完成，橙色部分为等待调用的 1 s 就绪空闲。 | [SVG](figure-11-prewarm-3.svg) | [PNG](figure-11-prewarm-3.png) | [PDF](figure-11-prewarm-3.pdf) |
| 11-19 | 预测错误：第 2—4 s 准备了不需要的环境（灰色）；第 4 s 取消后，再花 2 s 准备实际所需环境。此图采用立即取消、无资源争用的题设。 | [SVG](figure-11-prewarm-wrong.svg) | [PNG](figure-11-prewarm-wrong.png) | [PDF](figure-11-prewarm-wrong.pdf) |
| 11-20 | 整理前：新作业需要同节点四张 A 型 GPU 与 16 核。节点 1 缺 CPU，节点 2 的 GPU 类型不符。 | [SVG](figure-11-4-placement.svg) | [PNG](figure-11-4-placement.png) | [PDF](figure-11-4-placement.pdf) |
| 11-21 | 将占用 8 核的 CPU 任务从节点 1 迁到节点 2 后，节点 1 同时拥有四张 A 卡和 16 核，可以启动新作业。 | [SVG](figure-11-placement-after.svg) | [PNG](figure-11-placement-after.png) | [PDF](figure-11-placement-after.pdf) |
| 11-22 | 十次调用每隔 1 s 到达，一个执行进程每次处理 1 s。圆点为到达，蓝色为执行，每次均可立即开始。 | [SVG](figure-11-queue.svg) | [PNG](figure-11-queue.png) | [PDF](figure-11-queue.pdf) |
| 11-23 | 十次调用同时在第 0 s 到达；灰色为等待、蓝色为执行，各行的等待依次为 0—9 s。处理器仍只工作 10 s，平均排队为 4.5 s。 | [SVG](figure-11-queue-burst.svg) | [PNG](figure-11-queue-burst.png) | [PDF](figure-11-queue-burst.pdf) |
| 11-24 | 四个阶段依次执行。生成时间由 40 秒降至 20 秒，其余三段仍共需 45 秒，因此每轮总时间由 85 秒降至 65 秒。条形长度按时间比例绘制。 | [SVG](figure-11-rl-stages.svg) | [PNG](figure-11-rl-stages.png) | [PDF](figure-11-rl-stages.pdf) |
| 11-25 | 每个接收实例都需要一份完整的 30 GB 权重，六路传输共用 200 Gbit/s 发送出口。每个接收端为 50 Gbit/s，单份传输至少 4.8 秒，而发送端累计发送 180 GB 至少需要 7.2 秒；图中六个接收框各代表一个独立实例。 | [SVG](figure-11-weights.svg) | [PNG](figure-11-weights.png) | [PDF](figure-11-weights.pdf) |
| 11-26 | 三条样本分别在第 0、10、20 s 到达，立即提交给唯一的验证进程，每条处理 10 s，整批在第 30 s 完成。圆点标到达时刻。 | [SVG](figure-11-5-stages.svg) | [PNG](figure-11-5-stages.png) | [PDF](figure-11-5-stages.pdf) |
| 11-27 | 先等三条样本全部在第 20 s 就绪，再依次验证，结束于第 50 s。与前图执行相同的 30 s 验证工作，区别来自提交时机。 | [SVG](figure-11-stages-batch.svg) | [PNG](figure-11-stages-batch.png) | [PDF](figure-11-stages-batch.pdf) |
| 11-28 | 九条验证各用 1 s，一条用 100 s。虚线是已经执行的 10 s；到此时仍未结束的样本只可能来自 100 s 那一类，剩余时间为 90 s。 | [SVG](figure-11-remaining-time.svg) | [PNG](figure-11-remaining-time.png) | [PDF](figure-11-remaining-time.pdf) |
| 11-29 | 两次调用的输入和可见输出相同，只改变思考长度。橙色成本缩短到原来的十分之一，蓝色和绿色成本保持不变，所以总成本由 0.032 降到 0.023，减少约 28%。价格和 token 数见例 11-5。 | [SVG](figure-11-thinking.svg) | [PNG](figure-11-thinking.png) | [PDF](figure-11-thinking.pdf) |
| 11-30 | 同一任务的模型服务与成本路径。外部应用程序接口（API）按调用用量收费，自建副本按设备预留及运行支出计价；两条路径都将成本归到任务及尝试。输入拆分为普通处理、缓存创建和缓存读取，生成单独计量。 | [SVG](figure-11-6-service.svg) | [PNG](figure-11-6-service.png) | [PDF](figure-11-6-service.pdf) |
| 11-31 | B 的成功任务成本随命中率提高而下降，在约 84.9% 处等于 A。两者的成本先按各自成功数归一化；本图只比较成本，下一图单独加入期限。 | [SVG](figure-11-7-routing.svg) | [PNG](figure-11-7-routing.png) | [PDF](figure-11-7-routing.pdf) |
| 11-32 | 只有 B 命中的 4 s 路径满足 6 s 期限；再乘 98% 质量概率，按时成功比例为 0.98h。达到 90% 目标要求 h 至少约 91.8%。 | [SVG](figure-11-routing-deadline.svg) | [PNG](figure-11-routing-deadline.png) | [PDF](figure-11-routing-deadline.pdf) |
| 11-33 | 自建总成本为 1,000＋0.002N，API 为 0.012N，其中 N 为提交任务数。两者成功率相同，并有足够能力满足期限。自建曲线起点较高、斜率较小，在 100,000 项时与 API 相交。 | [SVG](figure-11-purchase.svg) | [PNG](figure-11-purchase.png) | [PDF](figure-11-purchase.pdf) |
| 11-34 | 外部系统已执行并提交操作 K，确认却丢失。恢复环境不会撤回外部效果；控制器按同一操作 ID 查询结果后接续任务。实线表示请求与执行，虚线表示确认及恢复查询。 | [SVG](figure-11-commit-ack.svg) | [PNG](figure-11-commit-ack.png) | [PDF](figure-11-commit-ack.pdf) |
| 11-35 | 首次尝试在 10 s 后分为成功、局部修复、直接升级三类。框内比例以全部提交为分母；下一图展开修复的条件分支。 | [SVG](figure-11-retry-tree.svg) | [PNG](figure-11-retry-tree.png) | [PDF](figure-11-retry-tree.pdf) |
| 11-36 | 把修复节点放大：进入此处的 12% 中，60% 修复成功，占全部提交 7.2%；40% 转入升级，占全部提交 4.8%。升级再用 8 s，因此后一条路径累计 22 s。 | [SVG](figure-11-retry-conditional.svg) | [PNG](figure-11-retry-conditional.png) | [PDF](figure-11-retry-conditional.pdf) |
| 11-37 | 同一批提交任务换用恢复策略后的成本与结果。各柱均以相应策略的全部支出为分子，再分别除以通过测试的任务数或按时通过测试的任务数；只做首次尝试的成功率为 80%，有限恢复策略约为 99.7%，其中约 95.0% 的提交在 20 秒内成功。分支概率、成本和时间见例 11-8，期限用于评价而不强制停止执行。 | [SVG](figure-11-8-retry.svg) | [PNG](figure-11-8-retry.png) | [PDF](figure-11-8-retry.pdf) |
| 11-38 | 模型加速使原本可隐藏的环境创建暴露出来。两种情况都在零时刻开始创建环境；工具须同时等待模型决策与环境就绪。横轴为秒。 | [SVG](figure-11-environment-overlap.svg) | [PNG](figure-11-environment-overlap.png) | [PDF](figure-11-environment-overlap.pdf) |
| 11-39 | 两种方案均在模型调用期间准备环境，工具执行均为每轮 1 秒。模型调用从每轮 9 秒降至 6 秒，三轮结束时刻从第 30 秒移到第 21 秒，越过 24 秒期限线。 | [SVG](figure-11-decision.svg) | [PNG](figure-11-decision.png) | [PDF](figure-11-decision.pdf) |
