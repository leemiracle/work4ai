# 第七章正文与配图

[阅读版 HTML](../07-数据中心网络.html) · [正文 Markdown](../07-数据中心网络.md) · [写作大纲](../../outlines/07-数据中心网络.md)

六节、23 个小节，六道完整例题与十项练习（核心为 7-3、7-7、7-10）。以两台服务器的 192 MiB 梯度归约贯穿流量与资源、并发与吞吐、依赖与关键路径三个模型，推导选择边界并回到整步时间。21 幅原创插图各提供 SVG、PNG、PDF；图号与完整图注位于图片外。HTML 内嵌图片、公式和公式字体，可离线阅读，外部来源链接仍指向仓库。

| 图 | 内容 | SVG | PNG | PDF |
|---|---|---|---|---|
| 7-1 | 八个参与者的分布与服务器边界 | [SVG](figure-7-1-boundaries.svg) | [PNG](figure-7-1-boundaries.png) | [PDF](figure-7-1-boundaries.pdf) |
| 7-2 | 设备扩展与固定通信需求 | [SVG](figure-7-2-cut.svg) | [PNG](figure-7-2-cut.png) | [PDF](figure-7-2-cut.pdf) |
| 7-3 | 归约路径与跨服务器流量 | [SVG](figure-7-3-hierarchy.svg) | [PNG](figure-7-3-hierarchy.png) | [PDF](figure-7-3-hierarchy.pdf) |
| 7-4 | 四阶段流水线中的计算与空闲 | [SVG](figure-7-4-pipeline.svg) | [PNG](figure-7-4-pipeline.png) | [PDF](figure-7-4-pipeline.pdf) |
| 7-5 | 专家分派在独立入口与共享入口上的传输 | [SVG](figure-7-5-expert.svg) | [PNG](figure-7-5-expert.png) | [PDF](figure-7-5-expert.pdf) |
| 7-6 | 直接网卡与相邻网卡中继的带宽限制 | [SVG](figure-7-6-relay.svg) | [PNG](figure-7-6-relay.png) | [PDF](figure-7-6-relay.pdf) |
| 7-7 | 通信发起位置与数据通路 | [SVG](figure-7-7-access.svg) | [PNG](figure-7-7-access.png) | [PDF](figure-7-7-access.pdf) |
| 7-8 | 按需远读与搬回本地的复用交点 | [SVG](figure-7-8-snapshot.svg) | [PNG](figure-7-8-snapshot.png) | [PDF](figure-7-8-snapshot.pdf) |
| 7-9 | 请求槽位不足造成的链路空闲 | [SVG](figure-7-9-window.svg) | [PNG](figure-7-9-window.png) | [PDF](figure-7-9-window.pdf) |
| 7-10 | 源缓冲和目的缓冲的不同复用时刻 | [SVG](figure-7-10-lifetime.svg) | [PNG](figure-7-10-lifetime.png) | [PDF](figure-7-10-lifetime.pdf) |
| 7-11 | 应用关系与共享传输状态 | [SVG](figure-7-11-state.svg) | [PNG](figure-7-11-state.png) | [PDF](figure-7-11-state.pdf) |
| 7-12 | 必要依赖与独立操作的完成时间 | [SVG](figure-7-12-ordering.svg) | [PNG](figure-7-12-ordering.png) | [PDF](figure-7-12-ordering.pdf) |
| 7-13 | 实际读取时刻与按序返回的区别 | [SVG](figure-7-13-stale.svg) | [PNG](figure-7-13-stale.png) | [PDF](figure-7-13-stale.pdf) |
| 7-14 | 传输完成后仍被占用的请求槽位 | [SVG](figure-7-14-reclaim.svg) | [PNG](figure-7-14-reclaim.png) | [PDF](figure-7-14-reclaim.pdf) |
| 7-15 | 通信高峰与积压 | [SVG](figure-7-15-congestion.svg) | [PNG](figure-7-15-congestion.png) | [PDF](figure-7-15-congestion.pdf) |
| 7-16 | 有限缓冲的填满与反馈后的排空 | [SVG](figure-7-16-feedback.svg) | [PNG](figure-7-16-feedback.png) | [PDF](figure-7-16-feedback.pdf) |
| 7-17 | 多路径报文到达与等待缺口 | [SVG](figure-7-17-packets.svg) | [PNG](figure-7-17-packets.png) | [PDF](figure-7-17-packets.pdf) |
| 7-18 | 循环资源依赖与响应通路 | [SVG](figure-7-18-deadlock.svg) | [PNG](figure-7-18-deadlock.png) | [PDF](figure-7-18-deadlock.pdf) |
| 7-19 | 就绪与交换的关键路径 | [SVG](figure-7-19-progress.svg) | [PNG](figure-7-19-progress.png) | [PDF](figure-7-19-progress.pdf) |
| 7-20 | 通信优化如何改变训练步的关键路径 | [SVG](figure-7-20-step.svg) | [PNG](figure-7-20-step.png) | [PDF](figure-7-20-step.pdf) |
| 7-21 | 小消息启动开销与大消息传输开销 | [SVG](figure-7-21-message.svg) | [PNG](figure-7-21-message.png) | [PDF](figure-7-21-message.pdf) |

## 来源与重建

[阅读记录](reading-notes.md)说明 calculations、survey、作者文章与已有实验的采用范围。[sources.json](sources.json)锁定来源，[figure-data.json](figure-data.json)保存绘图数据，[teaching-data.json](teaching-data.json)保存新推导的选择边界与整步算例，[models.py](models.py)生成这些计算，[manifest.json](manifest.json)保存输出校验值。教学计算、公开运行记录与本机 CPU 实测分别标注，本轮未执行新的 GPU 实验。

在仓库根目录运行：

```sh
python3 -m venv /tmp/ch07-book-venv
/tmp/ch07-book-venv/bin/pip install -r manuscripts/ch07/requirements.txt
/tmp/ch07-book-venv/bin/python manuscripts/ch07/build.py
/tmp/ch07-book-venv/bin/python manuscripts/ch07/verify.py
```

需要 Node.js 和中文字体；默认寻找 macOS Arial Unicode 或 Linux Noto CJK，也可用 `--font /path/to/font` 指定。来源变化会停止构建，审阅后再更新来源锁。KaTeX 0.16.11 与许可证在 `vendor/katex/`。

## 校验与预览

[内容与数据校验](validation.json)检查提纲覆盖、练习、外部图注、链接、来源与输出 SHA256，以及主要算式和图数据。[公式记录](math-validation.json)包含 98 个表达式；[插图范围检查](figure-layout-check.json)检查文字是否超出画布。

[浏览器检查](browser-validation.json)覆盖 1440 px 桌面与 390 px 手机宽度的图片加载、公式、目录锚点与页面宽度。[桌面预览](preview-desktop.png) · [手机预览](preview-mobile.png) · [分层归约图文](preview-desktop-hierarchy.png)。复杂插图可用独立 SVG／PDF 放大阅读。

浏览器检查另需 Playwright 和 Chrome：安装 `playwright` 后运行 `python manuscripts/ch07/browser-check.py --executable /path/to/chrome`。

本轮章节组织与原提纲的对应关系见[结构说明](../../research/ch07-textbook-revision-2026-09-10/README.md)。

本轮新增 12 幅机制图，并重写段落之间的因果与比较关系。图号按阅读顺序重新编排，图内不重复图号；修改说明见[图文修订记录](../../research/ch07-visual-revision-2026-09-10/README.md)。
