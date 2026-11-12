# 第十章正文与配图

[阅读版 HTML](../10-训练系统.html) · [正文 Markdown](../10-训练系统.md) · [写作大纲](../../outlines/10-训练系统.md)

六节、23 个小节，约 1.9 万汉字，包含定量例题、144 个公式和十道分层习题。正文先解释数据如何保存、传输和参与计算，再用算例推导显存、耗时与完成期限。32／48 卡设计案例贯穿各节，RL 部分进一步解释阶段协作和策略版本。

二十幅插图分别提供 SVG、PNG、PDF。图中用张量分片、时间轴、数据路径、注意力面积和曲线解释机制，完整条件和图号位于图片外。HTML 内嵌图片与公式字体，可以离线阅读。

| 图 | 内容 | SVG | PNG | PDF |
|---|---|---|---|---|
| 10-1 | 训练状态与推理权重的容量比较 | [SVG](figure-10-1-state.svg) | [PNG](figure-10-1-state.png) | [PDF](figure-10-1-state.pdf) |
| 10-2 | 容量下界与不同效率下的计算设备数 | [SVG](figure-10-2-budget.svg) | [PNG](figure-10-2-budget.png) | [PDF](figure-10-2-budget.pdf) |
| 10-3 | 参数分片与执行时的完整参数缓冲区 | [SVG](figure-10-3-sharding.svg) | [PNG](figure-10-3-sharding.png) | [PDF](figure-10-3-sharding.pdf) |
| 10-4 | 保存乘积与反向前重建乘积的时间对比 | [SVG](figure-10-4-recompute.svg) | [PNG](figure-10-4-recompute.png) | [PDF](figure-10-4-recompute.pdf) |
| 10-5 | CPU 与 GPU 转换梯度时的传输路径 | [SVG](figure-10-5-casting.svg) | [PNG](figure-10-5-casting.png) | [PDF](figure-10-5-casting.pdf) |
| 10-6 | 分片参与者数与每卡容量 | [SVG](figure-10-6-candidates.svg) | [PNG](figure-10-6-candidates.png) | [PDF](figure-10-6-candidates.pdf) |
| 10-7 | 两种流水的依赖等待与激活保存 | [SVG](figure-10-7-pipeline.svg) | [PNG](figure-10-7-pipeline.png) | [PDF](figure-10-7-pipeline.pdf) |
| 10-8 | 链路占用怎样使归约延迟到计算结束之后 | [SVG](figure-10-8-overlap.svg) | [PNG](figure-10-8-overlap.png) | [PDF](figure-10-8-overlap.pdf) |
| 10-9 | 等长与不等长序列的因果注意力面积 | [SVG](figure-10-9-attention-area.svg) | [PNG](figure-10-9-attention-area.png) | [PDF](figure-10-9-attention-area.pdf) |
| 10-10 | 预取进度与已经完成的训练进度 | [SVG](figure-10-10-input-queue.svg) | [PNG](figure-10-10-input-queue.png) | [PDF](figure-10-10-input-queue.pdf) |
| 10-11 | 从四份权重分片恢复为八份分片 | [SVG](figure-10-11-resharding.svg) | [PNG](figure-10-11-resharding.png) | [PDF](figure-10-11-resharding.pdf) |
| 10-12 | 写带宽与故障时可用恢复点 | [SVG](figure-10-12-recovery.svg) | [PNG](figure-10-12-recovery.png) | [PDF](figure-10-12-recovery.pdf) |
| 10-13 | 保存间隔对保存成本与故障重做成本的相反影响 | [SVG](figure-10-13-save-interval.svg) | [PNG](figure-10-13-save-interval.png) | [PDF](figure-10-13-save-interval.pdf) |
| 10-14 | 生成验证学习的处理瓶颈与权重反馈 | [SVG](figure-10-14-rl-flow.svg) | [PNG](figure-10-14-rl-flow.png) | [PDF](figure-10-14-rl-flow.pdf) |
| 10-15 | 权重同步次序与显存峰值 | [SVG](figure-10-15-rl.svg) | [PNG](figure-10-15-rl.png) | [PDF](figure-10-15-rl.pdf) |
| 10-16 | 同步等待与跨批次异步执行的时间对比 | [SVG](figure-10-16-async-cycle.svg) | [PNG](figure-10-16-async-cycle.png) | [PDF](figure-10-16-async-cycle.pdf) |
| 10-17 | 重放离散选择与重算当前数值 | [SVG](figure-10-17-replay.svg) | [PNG](figure-10-17-replay.png) | [PDF](figure-10-17-replay.pdf) |
| 10-18 | 32卡与48卡方案的完成时间分解 | [SVG](figure-10-18-deadline.svg) | [PNG](figure-10-18-deadline.png) | [PDF](figure-10-18-deadline.pdf) |
| 10-19 | 通信带宽变化对每步耗时的影响 | [SVG](figure-10-19-hardware.svg) | [PNG](figure-10-19-hardware.png) | [PDF](figure-10-19-hardware.pdf) |
| 10-20 | 给定期限下模型规模与设备数边界 | [SVG](figure-10-20-scale.svg) | [PNG](figure-10-20-scale.png) | [PDF](figure-10-20-scale.pdf) |

## 来源与复现

[阅读记录](reading-notes.md)注明 calculations、survey、案例与已有实验的阅读范围和采用方式。[sources.json](sources.json)锁定来源文件，[figure-data.json](figure-data.json)保存作图数值及事件，[manifest.json](manifest.json)保存输出校验值。没有执行新的 GPU 训练或增加未测得的跨硬件性能结果。

在仓库根目录执行：

```sh
python3 -m venv /tmp/ch10-book-venv
/tmp/ch10-book-venv/bin/pip install -r manuscripts/ch10/requirements.txt
/tmp/ch10-book-venv/bin/python manuscripts/ch10/build.py
python3 manuscripts/ch10/verify.py
```

构建需要 Node.js 和中文字体；默认寻找 macOS Arial Unicode 或 Linux Noto CJK，可用 `--font /path/to/font` 指定。公式复用仓库已有的 `manuscripts/ch06/vendor/katex`（0.16.11，许可证同目录），无需构建时下载。来源哈希不匹配会停止生成，须审阅变化再更新锁文件。

浏览器校验为可选步骤，需要 Playwright 和 Chrome：

```sh
/tmp/ch10-book-venv/bin/pip install playwright
/tmp/ch10-book-venv/bin/python manuscripts/ch10/browser-check.py --executable /path/to/chrome
```

## 校验

[内容与数据校验](validation.json)覆盖 outline 对齐、全部题号与外部图注、原始数据、图内无图号、插入公式、关键算术和本地链接。[公式校验](math-validation.json)记录公式渲染结果，[布局检查](figure-layout-check.json)记录图片文字边界。[浏览器检查](browser-validation.json)检查 1440 px 与 390 px 阅读视口中的图片、公式、锚点和页面宽度。

[桌面预览](preview-desktop.png) · [手机预览](preview-mobile.png) · [流水图文预览](preview-desktop-pipeline.png)。复杂时序图可通过上表中的 SVG／PDF 放大阅读。

本轮[定量叙述修订记录](revisions/quantitative-prose/README.md)说明算例展开、数字精度与插图重组。

最新[教学结构修订记录](revisions/teaching-structure/README.md)说明全章连贯重写。[贯穿设计题](design-case.md)给出输入与推导，运行 `python3 manuscripts/ch10/design-case.py` 可独立复算。

已完成全章术语和中文句式修订，详见[修订说明](revisions/chinese-terminology/README.md)。

本轮[图示与段落衔接修订](revisions/visual-explanation/README.md)新增十一幅机制图，并按阅读顺序统一编号。旧版图号对应关系见 [figure-number-map.json](figure-number-map.json)。新图由 [mechanism-figures.py](mechanism-figures.py) 生成，统一通过 build.py 构建。
