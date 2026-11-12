# 第五章正文与插图

[5.2–5.3 试改阅读版](../05-算子与运行时.md) · [整章阅读版 HTML](../05-算子与运行时.md) · [正文 Markdown](../05-算子与运行时.md) · [写作大纲](../../outlines/05-算子与运行时.md)

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

## 当前阅读版配图（2026-09-10）

正文现引用 30 幅图，以下清单按当前阅读顺序列出；上文旧图号用于追溯构建记录。

| 图号 | 内容 | SVG | PNG | PDF |
| --- | --- | --- | --- | --- |
| 5-1 | CPU 提交、H2D 输入复制、设备内核与 D2H 结果返回依次发生。上行内核二十微秒，结果三十五微秒可用；下行内核五微秒，结果二十微秒可用。 | [SVG](figure-5-1-execution.svg) | [PNG](figure-5-1-execution.png) | [PDF](figure-5-1-execution.pdf) |
| 5-2 | 先算一个输出，再算相邻输出。蓝色表示所用的 A 行，橙色表示所用的 W 列，绿色表示本次得到的输出元素。图中矩阵缩小为示意尺寸，实际算例的 K 为 4096。 | [SVG](figure-5-reuse-steps.svg) | [PNG](figure-5-reuse-steps.png) | [PDF](figure-5-reuse-steps.pdf) |
| 5-3 | 一次块乘更新整个 m×n 输出块。A、W 输入为 BF16，累加器为 FP32（每个元素占 4 bytes 的 32 位浮点格式）；沿 K 换入新输入块时，累加器一直保留。图中尺寸符号表示形状，方框面积不按字节数缩放。 | [SVG](figure-5-tile-working-set.svg) | [PNG](figure-5-tile-working-set.png) | [PDF](figure-5-tile-working-set.pdf) |
| 5-4 | 每个点标出输出块形状。扩大输出块能减少跨接口的重复读取，但需要更多局部存储。虚线为三份矩阵各经过一次的 128 MiB；比较条件为 k=32、单组输入缓冲、各输出块独立读取输入。 | [SVG](figure-5-2-tiles.svg) | [PNG](figure-5-2-tiles.png) | [PDF](figure-5-2-tiles.pdf) |
| 5-5 | 条形总长均表示 96 KiB。24 KiB 的工作集能放四份，80 KiB 的只能放一份。这里把输入缓冲和累加器合并计入一个教学预算；实际 GPU 的共享内存、寄存器分别受限，真实驻留数还取决于线程数等约束。 | [SVG](figure-5-tile-residency.svg) | [PNG](figure-5-tile-residency.png) | [PDF](figure-5-tile-residency.pdf) |
| 5-6 | 同一列的 32 个不同字由 32 个 lane 同时请求。上半图行跨度为 32 个字，请求集中到同一 bank；下半图补齐为 33 个字，请求分散到 32 个 bank。图中画出前四个请求；假设每个 bank 每轮提供一个 32-bit 字，不计广播。 | [SVG](figure-5-3-banks.svg) | [PNG](figure-5-3-banks.png) | [PDF](figure-5-3-banks.pdf) |
| 5-7 | 上行由一组处理完整一行，输入保留到归一化结束；下行把一行分为八段，先求局部和，再合并，最后重读输入并归一化。每行 4096 个 BF16 元素；图中仅画一行，推广到 1024 行时，第一阶段任务数由 1024 增至 8192。橙色框表示增加的原输入读取。 | [SVG](figure-5-4-reduction.svg) | [PNG](figure-5-4-reduction.png) | [PDF](figure-5-4-reduction.pdf) |
| 5-8 | 上半图的完整 T 经过一次写出与一次读回；下半图中局部片段 t 直接传给乘法。两种方式仍读取 G、U 并写出 Z，图中省略这些共同的输入输出边。融合保持原来的中间舍入语义。 | [SVG](figure-5-fusion-path.svg) | [PNG](figure-5-fusion-path.png) | [PDF](figure-5-fusion-path.pdf) |
| 5-9 | 每少保存一个 24 MiB 中间量，就少一次写出和一次读入，共 48 MiB。G、U 为 BF16，最终输出占 1 byte/元素，量化尺度预先给定。各方案保留相同的运算与舍入顺序。 | [SVG](figure-5-5-boundaries.svg) | [PNG](figure-5-5-boundaries.png) | [PDF](figure-5-5-boundaries.pdf) |
| 5-10 | 块 0 在 2–5 μs 使用槽 A，所以块 2 到 5 μs 才能开始写入 A。图中抽取三个时段；4–5 μs 的块 1 已在槽 B 中等待，尚未开始计算。颜色固定表示槽 A、B，文字说明当前读写的是哪个块。 | [SVG](figure-5-buffer-slots.svg) | [PNG](figure-5-buffer-slots.png) | [PDF](figure-5-buffer-slots.pdf) |
| 5-11 | 两个输入槽交替复用，让搬运与计算重叠。每块搬运 2 μs、计算 3 μs，资源独立，忽略同步开销；同一颜色表示同一槽，计算读取结束后才能再次写入。 | [SVG](figure-5-6-fusion-buffer.svg) | [PNG](figure-5-6-fusion-buffer.png) | [PDF](figure-5-6-fusion-buffer.pdf) |
| 5-12 | 上半图保存完整 S、P，两份 FP32 矩阵各占 256 MiB，写出与读回合计 1 GiB。下半图只传递已处理部分的最大值 m、指数和 ℓ、加权值 u；每处理完一个块，其分数缓冲即可复用。箭头概括处理顺序，完整计算还需读入 Q、K、V。 | [SVG](figure-5-attention-storage.svg) | [PNG](figure-5-attention-storage.png) | [PDF](figure-5-attention-storage.pdf) |
| 5-13 | 两个块的分数分别为 0、ln 2，值分别为 1、3。最大值增大后，将旧指数和与旧加权值同时乘以 1/2，再加上新块的贡献，最后才做除法。箭头传递的是统计量，旧分数无需保留。 | [SVG](figure-5-7-online-softmax.svg) | [PNG](figure-5-7-online-softmax.png) | [PDF](figure-5-7-online-softmax.pdf) |
| 5-14 | 快速缓冲为 128 KiB，序列长 8192、头维度 128，无掩码；每个点对应正文表格的一种 K/V 块大小。横轴为缓冲与下一层之间的访问量，纵轴为在线更新次数，采用对数刻度。从 b=64 的点移到 b=1 的点，读取减少，更新次数却约增至 43 倍。 | [SVG](figure-5-8-attention-tradeoff.svg) | [PNG](figure-5-8-attention-tradeoff.png) | [PDF](figure-5-8-attention-tradeoff.pdf) |
| 5-15 | 循环层次确定存储寿命。外层选输出块，创建十六 KiB 累加器；内层 ko 反复读取 A、W 块，全部归约结束后再舍入并激活。 | [SVG](figure-5-9-polyhedral.svg) | [PNG](figure-5-9-polyhedral.png) | [PDF](figure-5-9-polyhedral.pdf) |
| 5-16 | 同样两个部分和，先相加得到零，再做 SiLU 仍为零；先对各部分做 SiLU 再相加，得到约 0.4621。两个数说明变换越过归约后改变了函数。 | [SVG](figure-5-activation-order.svg) | [PNG](figure-5-activation-order.png) | [PDF](figure-5-activation-order.pdf) |
| 5-17 | 一行分成两个块，后一块中的十决定整行尺度。第一项要先按这一尺度映射，再舍入到格式允许的值，最后反量化。 | [SVG](figure-5-quantization-scale.svg) | [PNG](figure-5-quantization-scale.png) | [PDF](figure-5-quantization-scale.pdf) |
| 5-18 | 两种方案都先读完整输入以确定行尺度。保存 FP8 结果后十二列块合计重读 192 MiB；融合方案重读 FP16 输入 384 MiB。权重与输出另有相同的 204 MiB。 | [SVG](figure-5-10-quantization.svg) | [PNG](figure-5-10-quantization.png) | [PDF](figure-5-10-quantization.pdf) |
| 5-19 | 形状 A 占比超过 2/3 时，新实现的总执行时间更短。A、B 原耗时均为 10 μs，新实现分别为 5、20 μs；调用串行，图中比较稳态执行。交点由两种实现的平均时间相等确定。 | [SVG](figure-5-11-feedback.svg) | [PNG](figure-5-11-feedback.png) | [PDF](figure-5-11-feedback.pdf) |
| 5-20 | 普通提交的三次 FFN 实测。上行为主机内核启动 API，下行为设备 kernel；横轴从本段标记起点计时。十八次内核启动对应十八个设备 kernel。 | [SVG](figure-5-12-runtime.svg) | [PNG](figure-5-12-runtime.png) | [PDF](figure-5-12-runtime.pdf) |
| 5-21 | 三次 FFN 融合激活链后，主机与设备各有十五次启动和内核执行。数据来自与前图相同实验的独立标记范围。 | [SVG](figure-5-runtime-1.svg) | [PNG](figure-5-runtime-1.png) | [PDF](figure-5-runtime-1.pdf) |
| 5-22 | 三次 graph launch 对应十八个设备 kernel。图重放减少主机提交次数，设备仍执行原图各节点；本图按自身采集范围标出真实时间。 | [SVG](figure-5-runtime-2.svg) | [PNG](figure-5-runtime-2.png) | [PDF](figure-5-runtime-2.pdf) |
| 5-23 | 先融合再重放，主机发起三次图执行，设备执行十五个 kernel。融合与图重放分别改变设备边界和主机提交。 | [SVG](figure-5-runtime-3.svg) | [PNG](figure-5-runtime-3.png) | [PDF](figure-5-runtime-3.pdf) |
| 5-24 | 图执行时读取记录的地址 G。新输入位于 X 时先复制到 G；上游直接写 G 时沿用同一缓冲，省去中间复制。 | [SVG](figure-5-graph-address.svg) | [PNG](figure-5-graph-address.png) | [PDF](figure-5-graph-address.pdf) |
| 5-25 | 橙色为准备，蓝色为额外输入复制，绿色为设备计算。普通方式四十微秒；图的两 MiB 输入约二十七微秒，十六 MiB 输入约四十二微秒。 | [SVG](figure-5-13-graph-copy.svg) | [PNG](figure-5-13-graph-copy.png) | [PDF](figure-5-13-graph-copy.pdf) |
| 5-26 | 同一组调用反复执行时，最省时的策略随复用次数变化。曲线采用例 5-12 的形状、处理率和准备时间，整数选择边界使用未舍入数值计算。 | [SVG](figure-5-14-specialization.svg) | [PNG](figure-5-14-specialization.png) | [PDF](figure-5-14-specialization.pdf) |
| 5-27 | 粗粒度执行先完成八块投影，再启动八块激活。每块投影约 32.2 μs、激活约 39.3 μs，两次主机启动各五微秒；竖线为激活开始。 | [SVG](figure-5-15-persistent.svg) | [PNG](figure-5-15-persistent.png) | [PDF](figure-5-15-persistent.pdf) |
| 5-28 | 矩阵与向量资源独立、缓冲充足。每个任务另计 0.7 μs 调度与通知，首块投影完成后即可激活，八块流水约三百五十八微秒结束。 | [SVG](figure-5-persistent-blocks.svg) | [PNG](figure-5-persistent-blocks.png) | [PDF](figure-5-persistent-blocks.pdf) |
| 5-29 | 收尾等待 A、B 两条分支。A 从 60 μs 缩短至 15 μs 后，较慢分支由 A 切换为 B，请求从 80 μs 降至 60 μs。准备和收尾各为 10 μs，两条分支使用独立资源。 | [SVG](figure-5-16-critical-path.svg) | [PNG](figure-5-16-critical-path.png) | [PDF](figure-5-16-critical-path.pdf) |
| 5-30 | 同轮替换前的请求时间减去替换后的请求时间，正值表示替换后更快。Qwen3-8B，7239-token 输入、强制 32-token 输出，并发 1，BF16、eager，关闭前缀缓存；11 对交错计时，轮内顺序随机，期间有其他驻留服务。虚线为配对时间差的中位数约 1.3 ms。阶段表来自独立 profile。 | [SVG](figure-5-17-request.svg) | [PNG](figure-5-17-request.png) | [PDF](figure-5-17-request.pdf) |


## V4／V4.1 会话修订后的当前图表

当前正文共 31 幅图；下表是当前图号，前文旧图号保留作历史记录。

| 图号 | 内容 | 文件 |
| --- | --- | --- |
| 5-1 | CPU 提交、H2D 输入复制、设备内核与 D2H 结果返回依次发生。上行内核二十微秒，结果三十五微秒可用；下行内核五微秒，结果二十微秒可用。 | [SVG](figure-5-1-execution.svg) |
| 5-2 | 先算一个输出，再算相邻输出。蓝色表示所用的 A 行，橙色表示所用的 W 列，绿色表示本次得到的输出元素。图中矩阵缩小为示意尺寸，实际算例的 K 为 4096。 | [SVG](figure-5-reuse-steps.svg) |
| 5-3 | 一次块乘更新整个 m×n 输出块。A、W 输入为 BF16，累加器为 FP32（每个元素占 4 bytes 的 32 位浮点格式）；沿 K 换入新输入块时，累加器一直保留。图中尺寸符号表示形状，方框面积不按字节数缩放。 | [SVG](figure-5-tile-working-set.svg) |
| 5-4 | 每个点标出输出块形状。扩大输出块能减少跨接口的重复读取，但需要更多局部存储。虚线为三份矩阵各经过一次的 128 MiB；比较条件为 k=32、单组输入缓冲、各输出块独立读取输入。 | [SVG](figure-5-2-tiles.svg) |
| 5-5 | 条形总长均表示 96 KiB。24 KiB 的工作集能放四份，80 KiB 的只能放一份。这里把输入缓冲和累加器合并计入一个教学预算；实际 GPU 的共享内存、寄存器分别受限，真实驻留数还取决于线程数等约束。 | [SVG](figure-5-tile-residency.svg) |
| 5-6 | 同一列的 32 个不同字由 32 个 lane 同时请求。上半图行跨度为 32 个字，请求集中到同一 bank；下半图补齐为 33 个字，请求分散到 32 个 bank。图中画出前四个请求；假设每个 bank 每轮提供一个 32-bit 字，不计广播。 | [SVG](figure-5-3-banks.svg) |
| 5-7 | 上行由一组处理完整一行，输入保留到归一化结束；下行把一行分为八段，先求局部和，再合并，最后重读输入并归一化。每行 4096 个 BF16 元素；图中仅画一行，推广到 1024 行时，第一阶段任务数由 1024 增至 8192。橙色框表示增加的原输入读取。 | [SVG](figure-5-4-reduction.svg) |
| 5-8 | 上半图的完整 T 经过一次写出与一次读回；下半图中局部片段 t 直接传给乘法。两种方式仍读取 G、U 并写出 Z，图中省略这些共同的输入输出边。融合保持原来的中间舍入语义。 | [SVG](figure-5-fusion-path.svg) |
| 5-9 | 每少保存一个 24 MiB 中间量，就少一次写出和一次读入，共 48 MiB。G、U 为 BF16，最终输出占 1 byte/元素，量化尺度预先给定。各方案保留相同的运算与舍入顺序。 | [SVG](figure-5-5-boundaries.svg) |
| 5-10 | 块 0 在 2–5 μs 使用槽 A，所以块 2 到 5 μs 才能开始写入 A。图中抽取三个时段；4–5 μs 的块 1 已在槽 B 中等待，尚未开始计算。颜色固定表示槽 A、B，文字说明当前读写的是哪个块。 | [SVG](figure-5-buffer-slots.svg) |
| 5-11 | 两个输入槽交替复用，让搬运与计算重叠。每块搬运 2 μs、计算 3 μs，资源独立，忽略同步开销；同一颜色表示同一槽，计算读取结束后才能再次写入。 | [SVG](figure-5-6-fusion-buffer.svg) |
| 5-12 | 上半图保存完整 S、P，两份 FP32 矩阵各占 256 MiB，写出与读回合计 1 GiB。下半图只传递已处理部分的最大值 m、指数和 ℓ、加权值 u；每处理完一个块，其分数缓冲即可复用。箭头概括处理顺序，完整计算还需读入 Q、K、V。 | [SVG](figure-5-attention-storage.svg) |
| 5-13 | 两个块的分数分别为 0、ln 2，值分别为 1、3。最大值增大后，将旧指数和与旧加权值同时乘以 1/2，再加上新块的贡献，最后才做除法。箭头传递的是统计量，旧分数无需保留。 | [SVG](figure-5-7-online-softmax.svg) |
| 5-14 | 快速缓冲为 128 KiB，序列长 8192、头维度 128，无掩码；每个点对应正文表格的一种 K/V 块大小。横轴为缓冲与下一层之间的访问量，纵轴为在线更新次数，采用对数刻度。从 b=64 的点移到 b=1 的点，读取减少，更新次数却约增至 43 倍。 | [SVG](figure-5-8-attention-tradeoff.svg) |
| 5-15 | 循环层次确定存储寿命。外层选输出块，创建十六 KiB 累加器；内层 ko 反复读取 A、W 块，全部归约结束后再舍入并激活。 | [SVG](figure-5-9-polyhedral.svg) |
| 5-16 | 同样两个部分和，先相加得到零，再做 SiLU 仍为零；先对各部分做 SiLU 再相加，得到约 0.4621。两个数说明变换越过归约后改变了函数。 | [SVG](figure-5-activation-order.svg) |
| 5-17 | 一行分成两个块，后一块中的十决定整行尺度。第一项要先按这一尺度映射，再舍入到格式允许的值，最后反量化。 | [SVG](figure-5-quantization-scale.svg) |
| 5-18 | 两种方案都先读完整输入以确定行尺度。保存 FP8 结果后十二列块合计重读 192 MiB；融合方案重读 FP16 输入 384 MiB。权重与输出另有相同的 204 MiB。 | [SVG](figure-5-10-quantization.svg) |
| 5-19 | 形状 A 占比超过 2/3 时，新实现的总执行时间更短。A、B 原耗时均为 10 μs，新实现分别为 5、20 μs；调用串行，图中比较稳态执行。交点由两种实现的平均时间相等确定。 | [SVG](figure-5-11-feedback.svg) |
| 5-20 | 普通提交的三次 FFN 实测。上行为主机内核启动 API，下行为设备 kernel；横轴从本段标记起点计时。十八次内核启动对应十八个设备 kernel。 | [SVG](figure-5-12-runtime.svg) |
| 5-21 | 三次 FFN 融合激活链后，主机与设备各有十五次启动和内核执行。数据来自与前图相同实验的独立标记范围。 | [SVG](figure-5-runtime-1.svg) |
| 5-22 | 三次 graph launch 对应十八个设备 kernel。图重放减少主机提交次数，设备仍执行原图各节点；本图按自身采集范围标出真实时间。 | [SVG](figure-5-runtime-2.svg) |
| 5-23 | 先融合再重放，主机发起三次图执行，设备执行十五个 kernel。融合与图重放分别改变设备边界和主机提交。 | [SVG](figure-5-runtime-3.svg) |
| 5-24 | 图执行时读取记录的地址 G。新输入位于 X 时先复制到 G；上游直接写 G 时沿用同一缓冲，省去中间复制。 | [SVG](figure-5-graph-address.svg) |
| 5-25 | 橙色为准备，蓝色为额外输入复制，绿色为设备计算。普通方式四十微秒；图的两 MiB 输入约二十七微秒，十六 MiB 输入约四十二微秒。 | [SVG](figure-5-13-graph-copy.svg) |
| 5-26 | 同一组调用反复执行时，最省时的策略随复用次数变化。曲线采用例 5-12 的形状、处理率和准备时间，整数选择边界使用未舍入数值计算。 | [SVG](figure-5-14-specialization.svg) |
| 5-27 | 粗粒度执行先完成八块投影，再启动八块激活。每块投影约 32.2 μs、激活约 39.3 μs，两次主机启动各五微秒；竖线为激活开始。 | [SVG](figure-5-15-persistent.svg) |
| 5-28 | 矩阵与向量资源独立、缓冲充足。每个任务另计 0.7 μs 调度与通知，首块投影完成后即可激活，八块流水约三百五十八微秒结束。 | [SVG](figure-5-persistent-blocks.svg) |
| 5-29 | 收尾等待 A、B 两条分支。A 从 60 μs 缩短至 15 μs 后，较慢分支由 A 切换为 B，请求从 80 μs 降至 60 μs。准备和收尾各为 10 μs，两条分支使用独立资源。 | [SVG](figure-5-16-critical-path.svg) |
| 5-30 | 全局驻留与逐层逻辑读取分开比较。上方仅计全局 KV 容量，下方读取包含全局条目、局部窗口和索引；两栏各自采用相同横轴尺度。数值为生产布局的逻辑载荷，不是实测 HBM 流量。 | [SVG](figure-5-v41-traffic.svg) |
| 5-31 | 同轮替换前的请求时间减去替换后的请求时间，正值表示替换后更快。Qwen3-8B，7239-token 输入、强制 32-token 输出，并发 1，BF16、eager，关闭前缀缓存；11 对交错计时，轮内顺序随机，期间有其他驻留服务。虚线为配对时间差的中位数约 1.3 ms。阶段表来自独立 profile。 | [SVG](figure-5-17-request.svg) |
