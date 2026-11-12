# 第六章正文与配图

[阅读版 HTML](../06-超节点.html) · [正文 Markdown](../06-超节点.md) · [写作大纲](../../outlines/06-超节点.md)

七节、25 个小节，十项练习。正文用同一 Qwen3-8B 续写任务，贯通逐卡容量、矩阵分工、集合通信、物理路径、会话调度与成本；MoE 和内存池解释专家分工与远端访问。十三个编号公式和逐步展开的例题连接各节。二十一幅原创插图提供 SVG、PNG、PDF；图号、完整图题与说明位于图片外。HTML 内嵌图片、公式与公式字体，可离线阅读；外部来源仍指向仓库。

| 图 | 内容 | SVG | PNG | PDF |
|---|---|---|---|---|
| 6-1 | 八张卡上的实例分组 | [SVG](figure-6-1-placement.svg) | [PNG](figure-6-1-placement.png) | [PDF](figure-6-1-placement.pdf) |
| 6-2 | 模型分片与每卡内存占用 | [SVG](figure-6-2-capacity.svg) | [PNG](figure-6-2-capacity.png) | [PDF](figure-6-2-capacity.pdf) |
| 6-3 | TP 的切分方向与输出部分和 | [SVG](figure-6-3-tp.svg) | [PNG](figure-6-3-tp.png) | [PDF](figure-6-3-tp.pdf) |
| 6-4 | 四阶段流水的填充与排空 | [SVG](figure-6-4-pipeline.svg) | [PNG](figure-6-4-pipeline.png) | [PDF](figure-6-4-pipeline.pdf) |
| 6-5 | token 派发和专家结果合并 | [SVG](figure-6-5-dispatch.svg) | [PNG](figure-6-5-dispatch.png) | [PDF](figure-6-5-dispatch.pdf) |
| 6-6 | TP 与 EP 的分组及归约方向 | [SVG](figure-6-6-ep-layout.svg) | [PNG](figure-6-6-ep-layout.png) | [PDF](figure-6-6-ep-layout.pdf) |
| 6-7 | 批内专家复用与权重读取 | [SVG](figure-6-7-reuse.svg) | [PNG](figure-6-7-reuse.png) | [PDF](figure-6-7-reuse.pdf) |
| 6-8 | 专家复用与设备负载分布 | [SVG](figure-6-8-expert-load.svg) | [PNG](figure-6-8-expert-load.png) | [PDF](figure-6-8-expert-load.pdf) |
| 6-9 | 环形归约的逐轮状态 | [SVG](figure-6-9-ring-rounds.svg) | [PNG](figure-6-9-ring-rounds.png) | [PDF](figure-6-9-ring-rounds.pdf) |
| 6-10 | 增加 TP 卡数时各项时间的变化 | [SVG](figure-6-10-tp-time.svg) | [PNG](figure-6-10-tp-time.png) | [PDF](figure-6-10-tp-time.pdf) |
| 6-11 | 消息大小与环树选择 | [SVG](figure-6-11-collectives.svg) | [PNG](figure-6-11-collectives.png) | [PDF](figure-6-11-collectives.pdf) |
| 6-12 | 并发时的资源竞争与完成时间 | [SVG](figure-6-12-resources.svg) | [PNG](figure-6-12-resources.png) | [PDF](figure-6-12-resources.pdf) |
| 6-13 | 下联与上联端口分配 | [SVG](figure-6-13-ports.svg) | [PNG](figure-6-13-ports.png) | [PDF](figure-6-13-ports.pdf) |
| 6-14 | 相同发送量与不同物理路径 | [SVG](figure-6-14-topology.svg) | [PNG](figure-6-14-topology.png) | [PDF](figure-6-14-topology.pdf) |
| 6-15 | 三维环面网络的二分链路 | [SVG](figure-6-15-torus.svg) | [PNG](figure-6-15-torus.png) | [PDF](figure-6-15-torus.pdf) |
| 6-16 | 三种系统的连接组织 | [SVG](figure-6-16-systems.svg) | [PNG](figure-6-16-systems.png) | [PDF](figure-6-16-systems.pdf) |
| 6-17 | 借用前后的物理内存位置 | [SVG](figure-6-17-pool-placement.svg) | [PNG](figure-6-17-pool-placement.png) | [PDF](figure-6-17-pool-placement.pdf) |
| 6-18 | 远端读取中的在途事务 | [SVG](figure-6-18-read-window.svg) | [PNG](figure-6-18-read-window.png) | [PDF](figure-6-18-read-window.pdf) |
| 6-19 | 访问频率与带宽需求 | [SVG](figure-6-19-memory-pool.svg) | [PNG](figure-6-19-memory-pool.png) | [PDF](figure-6-19-memory-pool.pdf) |
| 6-20 | 实例数量与四会话的完成顺序 | [SVG](figure-6-20-session-schedule.svg) | [PNG](figure-6-20-session-schedule.png) | [PDF](figure-6-20-session-schedule.pdf) |
| 6-21 | 期限、故障与按时完成会话的平均成本 | [SVG](figure-6-21-scale-cost.svg) | [PNG](figure-6-21-scale-cost.png) | [PDF](figure-6-21-scale-cost.pdf) |

## 来源与重建

[阅读记录](reading-notes.md)说明 calculations、survey、案例与已有实验的采用范围。[sources.json](sources.json)锁定来源，[figure-data.json](figure-data.json)保存画图数据，[manifest.json](manifest.json)保存输出校验值。所有性能教学输入与实测分别标注，没有新执行 GPU 实验。

[贯穿算例说明](continuous-example.md)列出教学设备、访问模型、续写输入、调度与故障条件；[计算脚本](continuity_model.py)生成[完整精度结果](continuity-model.json)。正文先从矩阵与 KV 访问推导单步时间，再累加八步并安排四个会话，图 6-21 使用同一执行模型。原先独立指定 62／100／160 ms 服务时间的调度情景保留在 `figure-data.json` 的 `legacy_schedule` 及原计算材料中。修订前正文与图数据保存在 [archive-before-continuity](archive-before-continuity/manuscript.md)。

在仓库根目录运行：

```sh
python3 -m venv /tmp/ch06-book-venv
/tmp/ch06-book-venv/bin/pip install -r manuscripts/ch06/requirements.txt
/tmp/ch06-book-venv/bin/python manuscripts/ch06/build.py
/tmp/ch06-book-venv/bin/python manuscripts/ch06/verify.py
```

[新增图示脚本](visual_examples.py)绘制容量分摊、TP／EP 分组、专家负载、单步时间分解、端口分配、环面网络二分、内存借用、在途事务和会话时序。[图号与文件清单](figure-catalog.json)统一管理正文图号与生成文件名。

生成器需要 Node.js 和中文字体，默认寻找 macOS Arial Unicode 或 Linux Noto CJK；可用 `--font /path/to/font` 指定。来源校验值变化会停止生成，需审阅来源后更新锁文件。KaTeX 0.16.11 与许可证在 vendor/katex 中。

## 校验与预览

[内容与数据校验](validation.json)覆盖七节与 25 个小节、十项递进练习、十三个公式编号、二十一幅图及外部图注、来源与输出校验值、链接，并独立复算单步执行、会话调度、成本和主要算式；[公式校验](math-validation.json)记录正文全部表达式。[浏览器检查](browser-validation.json)在 1440 px 与 390 px 宽度验证图片加载、公式、目录锚点与页面宽度。

[桌面预览](preview-desktop.png) · [手机预览](preview-mobile.png) · [桌面 MoE 图文](preview-desktop-moe.png)。复杂插图可使用上表中的独立 SVG／PDF 放大阅读。可选浏览器检查使用 Playwright：`python browser-check.py --executable /path/to/chrome`，不属于基本构建依赖。

## 路由观测配套图

[V4-Flash 路由热图 PNG](route-observation.png) · [SVG](route-observation.svg) · [PDF](route-observation.pdf)。采用 `retrieval-2048-A-early` 的 prefill 原始计数，43 层、2036 个有效 token，每层共选择六个路由专家。颜色表示各专家被选择的次数除以 token 数；每层各专家频率之和为 6。这是单个固定输入的观测，不是长期请求分布或跨卡性能测量。

路由热图单独作为配套，主图 6-7 集中比较同样 512 次分派下的专家权重复用。实际路由的正文讨论与来源链接保留。新增图 6-4 解释 PP 的时序，图 6-5 解释专家派发与返回，图 6-9 解释归约各轮数据的变化；容量、所有权、CPU 实测、端口与 NUMA 算例仍由相邻正文和表格展开。
