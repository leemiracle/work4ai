# 第四章正文与配图

[阅读版 HTML](../04-加速器架构.md) · [正文 Markdown](../04-加速器架构.md) · [写作大纲](../../outlines/04-加速器架构.md)

七节、二十三小节，采用问题、机制、推导与设计取舍的教材体例。用同一 Q 投影贯穿计算与存储分析，再加入注意力、专家路径、封装和专用化；章内三道带解例题与七项实验。正文包含脚注和本地引用。

十四幅插图均提供 SVG、PNG 和 PDF。图号、图题和说明全部位于正文图片外；图内仅保留机制、子面板、单位与坐标标注。阅读 HTML 嵌入图像、公式与字体，可以离线阅读。

| 图 | 内容 | 文件 |
|---|---|---|
| 4-1 | 输入行数增加怎样分摊权重读取 | [SVG](figure-4-1-reuse.svg) · [PNG](figure-4-1-reuse.png) · [PDF](figure-4-1-reuse.pdf) |
| 4-2 | 加速器组成与矩阵数据路径 | [SVG](figure-4-2-components.svg) · [PNG](figure-4-2-components.png) · [PDF](figure-4-2-components.pdf) |
| 4-3 | 专家分派怎样改变补零计算量 | [SVG](figure-4-3-expert-rows.svg) · [PNG](figure-4-3-expert-rows.png) · [PDF](figure-4-3-expert-rows.pdf) |
| 4-4 | 提高不同资源速率后的瓶颈转移 | [SVG](figure-4-4-attention.svg) · [PNG](figure-4-4-attention.png) · [PDF](figure-4-4-attention.pdf) |
| 4-5 | 低比特权重的两种计算方法 | [SVG](figure-4-5-precision.svg) · [PNG](figure-4-5-precision.png) · [PDF](figure-4-5-precision.pdf) |
| 4-6 | 权重、工作区与逐条请求的 KV 占用 | [SVG](figure-4-6-capacity.svg) · [PNG](figure-4-6-capacity.png) · [PDF](figure-4-6-capacity.pdf) |
| 4-7 | 并发请求数怎样限制有效带宽 | [SVG](figure-4-7-memory.svg) · [PNG](figure-4-7-memory.png) · [PDF](figure-4-7-memory.pdf) |
| 4-8 | 子矩阵有效数据与行步长 | [SVG](figure-4-8-layout.svg) · [PNG](figure-4-8-layout.png) · [PDF](figure-4-8-layout.pdf) |
| 4-9 | 最少三个输入槽怎样实现连续计算 | [SVG](figure-4-9-pipeline.svg) · [PNG](figure-4-9-pipeline.png) · [PDF](figure-4-9-pipeline.pdf) |
| 4-10 | 计算位置怎样改变跨裸片传输内容 | [SVG](figure-4-10-locality.svg) · [PNG](figure-4-10-locality.png) · [PDF](figure-4-10-locality.pdf) |
| 4-11 | 带宽翻倍对大小消息的不同收益 | [SVG](figure-4-11-interconnect.svg) · [PNG](figure-4-11-interconnect.png) · [PDF](figure-4-11-interconnect.pdf) |
| 4-12 | 固定权重与随 batch 增长的 KV 读取 | [SVG](figure-4-12-specialization.svg) · [PNG](figure-4-12-specialization.png) · [PDF](figure-4-12-specialization.pdf) |
| 4-13 | 输入行数怎样改变计算与传输时间 | [SVG](figure-4-13-roofline.svg) · [PNG](figure-4-13-roofline.png) · [PDF](figure-4-13-roofline.pdf) |
| 4-14 | 以 DRAM 读取检验投影耗时的缓存解释 | [SVG](figure-4-14-performance.svg) · [PNG](figure-4-14-performance.png) · [PDF](figure-4-14-performance.pdf) |

## 依据与复现

先阅读已有 calculations、survey、案例与实际实验记录，再编写正文。[reading-notes.md](reading-notes.md)说明采用范围；[sources.json](sources.json)锁定输入；[figure-data.json](figure-data.json)保存画图数据；[manifest.json](manifest.json)记录输出校验值。没有新跑 GPU 或模型质量实验。

```sh
python3 -m venv /tmp/ch04-book-venv
/tmp/ch04-book-venv/bin/pip install -r manuscripts/ch04/requirements.txt
/tmp/ch04-book-venv/bin/python manuscripts/ch04/build.py
/tmp/ch04-book-venv/bin/python manuscripts/ch04/check_browser.py
/tmp/ch04-book-venv/bin/python manuscripts/ch04/verify.py
```

构建需要 Python 3 和 Node.js。优先采用 macOS 中文字体，Linux 可安装 Noto Sans CJK 或传 `--font`。公式使用仓库已有 `../ch03/vendor/katex/` 的 KaTeX 0.16.11 和许可证，构建后字体和公式已嵌入 HTML。浏览器检查优先使用本机 Chrome，也支持 `CH04_CHROME` 指定可执行文件；没有浏览器时可安装 Playwright Chromium。

[validation.json](validation.json)包含大纲一致性、链接、图号、公式、来源与数值校验；[browser-validation.json](browser-validation.json)检查 1440 px 和 390 px 视口的图片、公式、目录与溢出。图布局另有自动边界检查与人工预览。

本次全章编辑的论证调整、有效数字规则与移入配套的细节见[编辑说明](editorial-revision.md)。

本轮全章重写增加节间递进、设计转折点和随文思考题；[教学推导与题解](teaching-notes.md)提供三槽流水、计算翻倍变体及容量、互联和 Roofline 边界。[证据记录](evidence-notes.md)集中保存版本、原始采集方法与数值检查。

[语言修订说明](language-revision.md)记录术语与中文句法调整；[段落衔接与配图修订](visual-revision.md)说明新增图的教学目的及对应推导。

## 当前阅读版配图（2026-09-10）

正文现引用 26 幅图，以下清单按当前阅读顺序列出；上文旧图号用于追溯构建记录。

| 图号 | 内容 | SVG | PNG | PDF |
| --- | --- | --- | --- | --- |
| 4-1 | 两种调用都使用同一份 32 MiB 权重。上方是一行输入，下方以部分条带示意 256 行；每行分摊的权重读取从 32 MiB 减至 128 KiB。 | [SVG](figure-4-1-reuse.svg) | [PNG](figure-4-1-reuse.png) | [PDF](figure-4-1-reuse.pdf) |
| 4-2 | 主机、显存与芯片内部的关系。实线表示数据经过缓存、局部缓冲、矩阵单元和累加存储，虚线表示主机提交工作。图按硬件功能分组。 | [SVG](figure-4-2-components.svg) | [PNG](figure-4-2-components.png) | [PDF](figure-4-2-components.pdf) |
| 4-3 | 模型与硬件跨代协同。实线沿时间向下：既有设备限制候选，软件暴露持续瓶颈，硬件回应需求，新设备重新打开模型选择空间。 | [SVG](figure-4-codesign-loop.svg) | [PNG](figure-4-codesign-loop.png) | [PDF](figure-4-codesign-loop.pdf) |
| 4-4 | 三行三列的乘加阵列示意。输入沿行传递，权重沿列传递，每个乘加位置保留自己的部分和。这里用小阵列解释操作数复用。 | [SVG](figure-4-matrix-array.svg) | [PNG](figure-4-matrix-array.png) | [PDF](figure-4-matrix-array.pdf) |
| 4-5 | 一个专家的 16 行计算块。每专家只有两行时，剩余十四行填零；每专家有 64 行时，可组成四个完整块，图中展示其中一块。 | [SVG](figure-4-3-expert-rows.svg) | [PNG](figure-4-3-expert-rows.png) | [PDF](figure-4-3-expert-rows.pdf) |
| 4-6 | 相同 512 行有效输入在全部专家上的执行量。分散到 256 个专家后总计执行 4096 行，集中到八个专家时只执行 512 行。 | [SVG](figure-4-expert-padding-total.svg) | [PNG](figure-4-expert-padding-total.png) | [PDF](figure-4-expert-padding-total.pdf) |
| 4-7 | 同一注意力块在四种资源配置下的服务周期。矩阵、共享存储和指数三项分别比较，单独增加一种能力后，其他资源可能成为较长的一项。 | [SVG](figure-4-4-attention.svg) | [PNG](figure-4-4-attention.png) | [PDF](figure-4-4-attention.pdf) |
| 4-8 | 相同压缩权重的两条计算路径。先展开会形成 32 MiB 的 BF16 副本；低精度路径在计算过程中完成缩放和合并。压缩权重及缩放因子共 8.5 MiB。 | [SVG](figure-4-5-precision.svg) | [PNG](figure-4-5-precision.png) | [PDF](figure-4-5-precision.pdf) |
| 4-9 | 固定 24 GB 显存中的权重、工作区和 KV。8K 四请求与 16K 两请求可以容纳，8K 五请求超过虚线标出的容量上限。 | [SVG](figure-4-6-capacity.svg) | [PNG](figure-4-6-capacity.png) | [PDF](figure-4-6-capacity.pdf) |
| 4-10 | 读取请求从发出到返回一直占用请求记录空间。多个独立请求交叠，才能在单次访问等待期间持续利用接口；图中只画四个代表请求。 | [SVG](figure-4-memory-inflight.svg) | [PNG](figure-4-memory-inflight.png) | [PDF](figure-4-memory-inflight.pdf) |
| 4-11 | 在每事务 128 bytes、返回延迟 500 ns 的题设下，增加在途请求数提高带宽上界，直到碰到接口本身的速率上限。 | [SVG](figure-4-7-memory.svg) | [PNG](figure-4-7-memory.png) | [PDF](figure-4-7-memory.pdf) |
| 4-12 | 每行前 256 bytes 是实际读取区间，相邻行起点相差 8192 bytes。128 行合计读取 32 KiB，行间灰色区域由步长跳过。 | [SVG](figure-4-8-layout.svg) | [PNG](figure-4-8-layout.png) | [PDF](figure-4-8-layout.pdf) |
| 4-13 | 一个输入槽从发起到释放的完整生命周期。传输 64 tick，额外等待 128 tick，数据在 192 tick 就绪，再计算 128 tick，于 320 tick 释放。 | [SVG](figure-4-slot-lifetime.svg) | [PNG](figure-4-slot-lifetime.png) | [PDF](figure-4-slot-lifetime.pdf) |
| 4-14 | 一个输入槽的四块时序。蓝条为传输，橙线为就绪，绿条为计算，浅灰为槽占用；上一块用完后才能再次发起，完成时刻为 1280 tick。 | [SVG](figure-4-9-pipeline.svg) | [PNG](figure-4-9-pipeline.png) | [PDF](figure-4-9-pipeline.pdf) |
| 4-15 | 两个输入槽使用相同时间尺度。前两块可提前发起，但第三块到 512 tick 才就绪，第二块在 448 tick 已结束，留下六十四 tick 空闲。 | [SVG](figure-4-pipeline-two.svg) | [PNG](figure-4-pipeline-two.png) | [PDF](figure-4-pipeline-two.pdf) |
| 4-16 | 三个输入槽提前发起前三块，第一槽释放后接收第四块。矩阵单元从 192 连续计算到 704 tick，第四槽不再缩短完成时间。 | [SVG](figure-4-pipeline-three.svg) | [PNG](figure-4-pipeline-three.png) | [PDF](figure-4-pipeline-three.pdf) |
| 4-17 | 矩阵与向量单元通过完整行组交接。QK 产生分数，Softmax 产生概率，PV 使用概率后释放槽；另一槽容纳相邻行组，使不同组可以重叠推进。 | [SVG](figure-4-matrix-vector-handoff.svg) | [PNG](figure-4-matrix-vector-handoff.png) | [PDF](figure-4-matrix-vector-handoff.pdf) |
| 4-18 | 计算集中在裸片 0 时，需要跨连接读取裸片 1 上的 32 GiB 权重。题设链路为每秒一 TiB，仅这笔跨裸片传输约需 31 ms。 | [SVG](figure-4-10-locality.svg) | [PNG](figure-4-10-locality.png) | [PDF](figure-4-10-locality.pdf) |
| 4-19 | 计算放到权重所在裸片后，跨连接交换输入与结果，共 64 MiB。在相同链路上，传输约六十一微秒；权重由各裸片本地读取。 | [SVG](figure-4-locality-compute.svg) | [PNG](figure-4-locality-compute.png) | [PDF](figure-4-locality-compute.pdf) |
| 4-20 | 8 KiB 小消息的启动与传输。固定启动两微秒，带宽从 100 增至 200 GB/s 只缩短蓝色传输项。 | [SVG](figure-4-11-interconnect.svg) | [PNG](figure-4-11-interconnect.png) | [PDF](figure-4-11-interconnect.pdf) |
| 4-21 | 2 MiB 消息在相同启动条件下的传输时间。较大的蓝色传输项使带宽翻倍带来更显著的收益；本图纵轴范围与小消息图分别标注。 | [SVG](figure-4-large-message.svg) | [PNG](figure-4-large-message.png) | [PDF](figure-4-large-message.pdf) |
| 4-22 | 固定权重的同时，各请求仍独立读取 KV。题设每请求保留 8K 上下文，batch 从十三起 KV 读取超过共享权重读取。 | [SVG](figure-4-12-specialization.svg) | [PNG](figure-4-12-specialization.png) | [PDF](figure-4-12-specialization.pdf) |
| 4-23 | 独立只读权重改变两条存储路径。上方权重与 KV 争用 HBM；下方 ROM 提供权重，HBM 保留可写状态。箭头表示读取，KV 还需写入新状态。 | [SVG](figure-4-rom-paths.svg) | [PNG](figure-4-rom-paths.png) | [PDF](figure-4-rom-paths.pdf) |
| 4-24 | 同一 Q 投影随输入行数增加的资源时间。计算量按行数增长，片外访问同时包含固定权重和增长的输入输出；从 179 行起计算项较长。 | [SVG](figure-4-13-roofline.svg) | [PNG](figure-4-13-roofline.png) | [PDF](figure-4-13-roofline.pdf) |
| 4-25 | RTX PRO 6000 的投影总耗时。每个条件测十一轮、每轮十六次调用，取每轮平均耗时的中位数；计时包含提交与同步。 | [SVG](figure-4-14-performance.svg) | [PNG](figure-4-14-performance.png) | [PDF](figure-4-14-performance.pdf) |
| 4-26 | 相同四个条件下另行采集的 DRAM 读取计数。单行均约 32 MiB，256 行复用为 256 bytes、轮换约 32.1 MiB。访问计数与常规计时分别测量。 | [SVG](figure-4-performance-traffic.svg) | [PNG](figure-4-performance-traffic.png) | [PDF](figure-4-performance-traffic.pdf) |
