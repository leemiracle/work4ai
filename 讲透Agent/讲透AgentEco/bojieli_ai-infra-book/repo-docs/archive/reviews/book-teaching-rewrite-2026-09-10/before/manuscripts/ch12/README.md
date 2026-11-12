# 第十二章正文与配图

[阅读版 HTML](../12-端边云协同.html) · [正文 Markdown](../12-端边云协同.md) · [写作大纲](../../outlines/12-端边云协同.md)

正文按六节、20 个小节展开。图片用于分析各步骤的耗时与依赖，音频用于解释连续播放，30 轮截图任务贯穿分工与部署；最后从已完成十轮的状态比较剩余二十轮。Queqiao 案例通过预测、对照实验和执行记录解释性能差异，八项练习按计算、改变条件和解释机制分步展开。

十六幅插图提供 SVG、PNG 和 PDF。图号、完整图题与说明均位于图片外；图内仅含面板说明、对象、图例与单位。HTML 内嵌图片、数学公式和公式字体，可离线阅读，外部来源链接仍指向仓库。点击插图可打开大图并横向查看，手机也可缩放页面；独立 SVG／PDF 适合放大或出版使用。

| 图 | 说明 | SVG | PNG | PDF |
|---|---|---|---|---|
| 12-1 | 上行速率改变三种精修方案的完成时间 | [SVG](figure-12-1-raw.svg) | [PNG](figure-12-1-raw.png) | [PDF](figure-12-1-raw.pdf) |
| 12-2 | 分块计算怎样与后续上传重叠 | [SVG](figure-12-2-overlap.svg) | [PNG](figure-12-2-overlap.png) | [PDF](figure-12-2-overlap.pdf) |
| 12-3 | 一个音频块晚到如何推迟后续播放 | [SVG](figure-12-3-paths.svg) | [PNG](figure-12-3-paths.png) | [PDF](figure-12-3-paths.pdf) |
| 12-4 | 接收比播放慢时缓冲逐渐耗尽 | [SVG](figure-12-4-buffer.svg) | [PNG](figure-12-4-buffer.png) | [PDF](figure-12-4-buffer.pdf) |
| 12-5 | 下一轮截图依赖本轮操作完成 | [SVG](figure-12-5-agent.svg) | [PNG](figure-12-5-agent.png) | [PDF](figure-12-5-agent.pdf) |
| 12-6 | 相同上行下原图与完整视觉特征的传输时间 | [SVG](figure-12-6-placement.svg) | [PNG](figure-12-6-placement.png) | [PDF](figure-12-6-placement.pdf) |
| 12-7 | 逐轮节省如何抵消迁移开销 | [SVG](figure-12-7-migration.svg) | [PNG](figure-12-7-migration.png) | [PDF](figure-12-7-migration.pdf) |
| 12-8 | 两台设备每层都要汇总结果才能继续计算 | [SVG](figure-12-8-sync.svg) | [PNG](figure-12-8-sync.png) | [PDF](figure-12-8-sync.pdf) |
| 12-9 | 窗口用完后链路空闲等待确认 | [SVG](figure-12-9-window.svg) | [PNG](figure-12-9-window.png) | [PDF](figure-12-9-window.pdf) |
| 12-10 | 相同发送轨迹下交付顺序改变音频完成时间 | [SVG](figure-12-10-transport.svg) | [PNG](figure-12-10-transport.png) | [PDF](figure-12-10-transport.pdf) |
| 12-11 | 短数据帧也需要相同的无线交换固定开销 | [SVG](figure-12-11-wireless.svg) | [PNG](figure-12-11-wireless.png) | [PDF](figure-12-11-wireless.pdf) |
| 12-12 | 两条接入路径汇入共同出口 | [SVG](figure-12-12-multipath.svg) | [PNG](figure-12-12-multipath.png) | [PDF](figure-12-12-multipath.pdf) |
| 12-13 | 调优基线使同一语音请求的时间差缩小 | [SVG](figure-12-13-queqiao.svg) | [PNG](figure-12-13-queqiao.png) | [PDF](figure-12-13-queqiao.pdf) |
| 12-14 | 不同执行设备的时间组成 | [SVG](figure-12-14-budgets.svg) | [PNG](figure-12-14-budgets.png) | [PDF](figure-12-14-budgets.pdf) |
| 12-15 | 云路径上行决定部署方案何时满足期限和何时更快 | [SVG](figure-12-15-deployment.svg) | [PNG](figure-12-15-deployment.png) | [PDF](figure-12-15-deployment.pdf) |
| 12-16 | 保留提交记录可以少做哪些工作 | [SVG](figure-12-16-recovery.svg) | [PNG](figure-12-16-recovery.png) | [PDF](figure-12-16-recovery.pdf) |

## 来源与重建

[阅读记录](reading-notes.md)说明 calculations、survey、协议、案例和已有实验的实际采用范围。[sources.json](sources.json)锁定来源，[figure-data.json](figure-data.json)保存图数据及条件，[manifest.json](manifest.json)保存输出校验值。正文明确区分固定形状计算、教学参数与已有实测，没有新执行模型、网络或设备性能实验。

在仓库根目录运行：

```sh
python3 -m venv /tmp/ch12-book-venv
/tmp/ch12-book-venv/bin/pip install -r manuscripts/ch12/requirements.txt
/tmp/ch12-book-venv/bin/python manuscripts/ch12/build.py
/tmp/ch12-book-venv/bin/python manuscripts/ch12/verify.py
```

生成需要 Node.js 与中文字体，默认使用 macOS Arial Unicode 或 Linux Noto CJK，也可传 `--font /path/to/font`。KaTeX 0.16.11 复用仓库的 `manuscripts/ch06/vendor/katex` 及原有许可证；其生成结果和字体均已嵌入 HTML。来源变化时构建停止，先审阅变化再更新来源锁。

## 校验与预览

[内容与数据校验](validation.json)检查小节、练习、外部图注、来源与输出 SHA-256、本地链接、图片文本与主要算式。[公式检查](math-validation.json)记录 KaTeX 的严格解析结果。[练习算术核对](exercise-check.json)提供关键数值，不替代开放式解释题的讨论。

[浏览器检查](browser-validation.json)覆盖 1440 px 桌面与 390 px 手机，检查图片加载、公式、目录锚点和横向溢出。[插图总览](preview-figures.png)、[桌面图文](preview-desktop-raw.png)、[手机正文](preview-mobile.png)。十六幅插图已逐图目视检查，图例和标签无裁切，所有图片内部均无图号。

可选浏览器复验需要 Playwright 和本地 Chromium／Chrome：

```sh
/tmp/ch12-book-venv/bin/pip install playwright
/tmp/ch12-book-venv/bin/python manuscripts/ch12/browser-check.py --executable '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
```

## 数字论证与配图修订

本次按条件、推导、结论与下一项问题重写全章。配置形状与整数边界保留精确值，性能和成本采用能解释选择的精度。上一轮七幅主图各用一组坐标突出一个关系；播放设备记录、双连接故障及精确统计移入[配套证据说明](evidence-notes.md)和脚注。[修订记录](../../research/ch12-prose-revision-2026-09-10/README.md)保存图文调整及旧稿归档位置。

## 教材体例重写

[本轮修订记录](../../research/ch12-textbook-revision-2026-09-10/README.md)说明统一主例、模型递进和案例重组。正文减少重复小算例，深入解释依赖、摊销与反馈；新增带宽波动、期限余量及恢复进度推导。定义和例题开头交代模型条件，段落以因果解释和推导结果推进。

## 中文表达修订

正文、图注、习题和脚注已逐段润色：按上下文明确设备、部署方案、计算、传输和播放等具体对象，调整生硬搭配与主语不清的句子。计算结果、公式含义和章节结构保持一致。[修订说明](../../research/ch12-language-revision-2026-09-10/README.md)记录本轮修改范围。

## 段落衔接与直观图解

本轮新增九幅图，将分块重叠、缓冲耗尽、Agent 的逐轮依赖、迁移回本、层内同步、窗口停等、共享出口、部署时间组成与恢复进度画出来。每幅图旁说明应看哪一段、哪个箭头或交点，前后段落据此继续推导。所有图按阅读顺序重新编号，[figure-catalog.json](figure-catalog.json)记录编号与文件，[修订记录](../../research/ch12-visual-revision-2026-09-10/README.md)说明衔接调整和数据核对。新增图由 `draw-concepts.py` 绘制，`build.py` 统一生成阅读版和配图。
