# 第五章正文与插图

[5.2–5.3 试改阅读版](../05-算子与运行时-5.2-5.3.html) · [整章阅读版 HTML](../05-算子与运行时.html) · [正文 Markdown](../05-算子与运行时.md) · [写作大纲](../../outlines/05-算子与运行时.md)

正文按设备执行、单算子、算子链、编译器、运行时和完整请求六节展开，含 22 小节、12 道带解例题和 9 项章末实验。每组例题从条件推导结果，再改变条件形成设计判断。段落通过数据依赖、资源限制与前一方案尚未解决的问题衔接；机制图与时间线先说明工作如何执行，再与公式和数值对应。AKG 的多面体编译通过 Halide／TVM 风格的循环变换、依赖与存储寿命解释。

二十三幅插图均提供 SVG 与 PNG；5.2–5.3 的十三幅试改图另提供 PDF，按 420 pt（约 148 mm）宽设计，主体标签 12 pt、辅助标签不低于 11 pt。图号和完整图题位于正文 caption。阅读版内嵌图片、KaTeX 公式和字体，可离线阅读。

| 图 | 内容 | 文件 |
| --- | --- | --- |
| 5-1 | 提交、执行与结果可用的时间 | [SVG](figure-5-1-execution.svg) · [PNG](figure-5-1-execution.png) |
| 5-2 | 相邻输出怎样复用同一行输入 | [SVG](figure-5-reuse-steps.svg) · [PNG](figure-5-reuse-steps.png) · [PDF](figure-5-reuse-steps.pdf) |
| 5-3 | 输入块更换而输出累加器保留 | [SVG](figure-5-tile-working-set.svg) · [PNG](figure-5-tile-working-set.png) · [PDF](figure-5-tile-working-set.pdf) |
| 5-4 | 局部容量与矩阵重读 | [SVG](figure-5-2-tiles.svg) · [PNG](figure-5-2-tiles.png) · [PDF](figure-5-2-tiles.pdf) |
| 5-5 | 同一局部存储预算容纳的工作集 | [SVG](figure-5-tile-residency.svg) · [PNG](figure-5-tile-residency.png) · [PDF](figure-5-tile-residency.pdf) |
| 5-6 | 补齐行跨度如何分散 bank 请求 | [SVG](figure-5-3-banks.svg) · [PNG](figure-5-3-banks.png) · [PDF](figure-5-3-banks.pdf) |
| 5-7 | RMSNorm 拆分后的归约与输入重读 | [SVG](figure-5-4-reduction.svg) · [PNG](figure-5-4-reduction.png) · [PDF](figure-5-4-reduction.pdf) |
| 5-8 | 融合前后中间结果经过的路径 | [SVG](figure-5-fusion-path.svg) · [PNG](figure-5-fusion-path.png) · [PDF](figure-5-fusion-path.pdf) |
| 5-9 | 融合边界与中间读写 | [SVG](figure-5-5-boundaries.svg) · [PNG](figure-5-5-boundaries.png) · [PDF](figure-5-5-boundaries.pdf) |
| 5-10 | 两个缓冲槽的交替使用 | [SVG](figure-5-buffer-slots.svg) · [PNG](figure-5-buffer-slots.png) · [PDF](figure-5-buffer-slots.pdf) |
| 5-11 | 同样四块数据的串行与双缓冲执行 | [SVG](figure-5-6-fusion-buffer.svg) · [PNG](figure-5-6-fusion-buffer.png) · [PDF](figure-5-6-fusion-buffer.pdf) |
| 5-12 | 完整中间矩阵与逐块统计量 | [SVG](figure-5-attention-storage.svg) · [PNG](figure-5-attention-storage.png) · [PDF](figure-5-attention-storage.pdf) |
| 5-13 | 在线 Softmax 如何合并两个块 | [SVG](figure-5-7-online-softmax.svg) · [PNG](figure-5-7-online-softmax.png) · [PDF](figure-5-7-online-softmax.pdf) |
| 5-14 | 注意力块大小在访问量与更新次数之间的取舍 | [SVG](figure-5-8-attention-tradeoff.svg) · [PNG](figure-5-8-attention-tradeoff.png) · [PDF](figure-5-8-attention-tradeoff.pdf) |
| 5-15 | 循环层级决定临时数据的保存时间 | [SVG](figure-5-9-polyhedral.svg) · [PNG](figure-5-9-polyhedral.png) |
| 5-16 | 保存量化结果如何减少后续读取 | [SVG](figure-5-10-quantization.svg) · [PNG](figure-5-10-quantization.png) |
| 5-17 | 调用比例与平均执行时间 | [SVG](figure-5-11-feedback.svg) · [PNG](figure-5-11-feedback.png) |
| 5-18 | 主机提交与设备执行的对应关系 | [SVG](figure-5-12-runtime.svg) · [PNG](figure-5-12-runtime.png) |
| 5-19 | 图重放的固定收益与输入复制时间 | [SVG](figure-5-13-graph-copy.svg) · [PNG](figure-5-13-graph-copy.png) |
| 5-20 | 准备成本与累计执行时间 | [SVG](figure-5-14-specialization.svg) · [PNG](figure-5-14-specialization.png) |
| 5-21 | 从等待全部投影到逐块开始激活 | [SVG](figure-5-15-persistent.svg) · [PNG](figure-5-15-persistent.png) |
| 5-22 | 局部加速引起关键路径切换 | [SVG](figure-5-16-critical-path.svg) · [PNG](figure-5-16-critical-path.png) |
| 5-23 | 完整请求的逐轮配对时间差 | [SVG](figure-5-17-request.svg) · [PNG](figure-5-17-request.png) |


[取材记录](reading-notes.md)说明已读 calculations、survey、论文与实验的采用范围。[sources.json](sources.json)锁定输入，[figure-data.json](figure-data.json)保存图数据，[figure-index.json](figure-index.json)将当前图号映射到稳定文件名。新增图片后图号已顺延；旧文件名与数据键保留，避免破坏复算引用。[manifest.json](manifest.json)记录输出。未运行新 GPU 基准，未将已有 partial 实验改为完成。

## 重建

从仓库根目录执行，需要 Python 3、Node.js 和中文字体：

```sh
python3 -m venv /tmp/ch05-book-venv
/tmp/ch05-book-venv/bin/pip install -r manuscripts/ch05/requirements.txt
/tmp/ch05-book-venv/bin/python manuscripts/ch05/build.py
/tmp/ch05-book-venv/bin/python manuscripts/ch05/verify.py
```

生成器优先使用 macOS Arial Unicode，Linux 可用 Noto CJK，或指定 `--font /path/to/font`。来源变化时构建停止，需审阅后更新锁。KaTeX 0.16.11 与许可证随 vendor 保存。

## 检查

[validation.json](validation.json)包含目录、练习、引用、输入输出校验及主要算例复核；[math-validation.json](math-validation.json)记录公式渲染；[figure-layout-check.json](figure-layout-check.json)记录文字边界。图像已目视检查。[browser-validation.json](browser-validation.json)记录桌面 1440 px 和手机 390 px 的图片加载、公式与横向溢出检查。

可选浏览器检查：安装 `playwright` 后运行 `python manuscripts/ch05/check_reading.py`。macOS 优先使用独立无头 Chrome；其他平台需先安装 Playwright Chromium。此项不读取个人浏览器会话。

## 5.2–5.3 图文试改

本轮新增六幅过程图，重画七幅既有图，并按“对象与操作 → 机制 → 数量关系 → 限制条件”重排正文。`teaching_revision.py` 集中绘制这十三幅图；`build.py` 继续读取既有算例与实验数据，并生成整章和独立试读版。手机端保留图中文字大小，可在图内左右滑动。

[修改说明与修改前快照](../../reviews/ch05-52-53-teaching-2026-09-10/README.md) · [试读 PDF](../../reviews/ch05-52-53-teaching-2026-09-10/sections-5.2-5.3.pdf)。
