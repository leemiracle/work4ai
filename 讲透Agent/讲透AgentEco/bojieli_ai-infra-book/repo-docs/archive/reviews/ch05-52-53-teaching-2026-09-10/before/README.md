# 第五章正文与插图

[阅读版 HTML](../05-算子与运行时.html) · [正文 Markdown](../05-算子与运行时.md) · [写作大纲](../../outlines/05-算子与运行时.md)

正文按设备执行、单算子、算子链、编译器、运行时和完整请求六节展开，含 22 小节、12 道带解例题和 9 项章末实验。每组例题从条件推导结果，再改变条件形成设计判断。段落通过数据依赖、资源限制与前一方案尚未解决的问题衔接；机制图与时间线先说明工作如何执行，再与公式和数值对应。AKG 的多面体编译通过 Halide／TVM 风格的循环变换、依赖与存储寿命解释。

十七幅插图均提供 SVG 与 PNG；图号和完整图题位于正文 caption。阅读版内嵌图片、KaTeX 公式和字体，可离线阅读。

| 图 | 内容 | 文件 |
| --- | --- | --- |
| 5-1 | 提交、执行与结果可用的时间 | [SVG](figure-5-1-execution.svg) · [PNG](figure-5-1-execution.png) |
| 5-2 | 局部容量与矩阵重读 | [SVG](figure-5-2-tiles.svg) · [PNG](figure-5-2-tiles.png) |
| 5-3 | 补齐行跨度如何分散 bank 请求 | [SVG](figure-5-3-banks.svg) · [PNG](figure-5-3-banks.png) |
| 5-4 | RMSNorm 拆分后的归约与输入重读 | [SVG](figure-5-4-reduction.svg) · [PNG](figure-5-4-reduction.png) |
| 5-5 | 融合边界与中间读写 | [SVG](figure-5-5-boundaries.svg) · [PNG](figure-5-5-boundaries.png) |
| 5-6 | 同样四块数据的串行与双缓冲执行 | [SVG](figure-5-6-fusion-buffer.svg) · [PNG](figure-5-6-fusion-buffer.png) |
| 5-7 | 在线 Softmax 如何合并两个块 | [SVG](figure-5-7-online-softmax.svg) · [PNG](figure-5-7-online-softmax.png) |
| 5-8 | 注意力块大小在访问量与更新次数之间的取舍 | [SVG](figure-5-8-attention-tradeoff.svg) · [PNG](figure-5-8-attention-tradeoff.png) |
| 5-9 | 循环层级决定临时数据的保存时间 | [SVG](figure-5-9-polyhedral.svg) · [PNG](figure-5-9-polyhedral.png) |
| 5-10 | 保存量化结果如何减少后续读取 | [SVG](figure-5-10-quantization.svg) · [PNG](figure-5-10-quantization.png) |
| 5-11 | 调用比例与平均执行时间 | [SVG](figure-5-11-feedback.svg) · [PNG](figure-5-11-feedback.png) |
| 5-12 | 主机提交与设备执行的对应关系 | [SVG](figure-5-12-runtime.svg) · [PNG](figure-5-12-runtime.png) |
| 5-13 | 图重放的固定收益与输入复制时间 | [SVG](figure-5-13-graph-copy.svg) · [PNG](figure-5-13-graph-copy.png) |
| 5-14 | 准备成本与累计执行时间 | [SVG](figure-5-14-specialization.svg) · [PNG](figure-5-14-specialization.png) |
| 5-15 | 从等待全部投影到逐块开始激活 | [SVG](figure-5-15-persistent.svg) · [PNG](figure-5-15-persistent.png) |
| 5-16 | 局部加速引起关键路径切换 | [SVG](figure-5-16-critical-path.svg) · [PNG](figure-5-16-critical-path.png) |
| 5-17 | 完整请求的逐轮配对时间差 | [SVG](figure-5-17-request.svg) · [PNG](figure-5-17-request.png) |

[取材记录](reading-notes.md)说明已读 calculations、survey、论文与实验的采用范围。[sources.json](sources.json)锁定输入，[figure-data.json](figure-data.json)保存图数据，[manifest.json](manifest.json)记录输出。未运行新 GPU 基准，未将已有 partial 实验改为完成。

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
