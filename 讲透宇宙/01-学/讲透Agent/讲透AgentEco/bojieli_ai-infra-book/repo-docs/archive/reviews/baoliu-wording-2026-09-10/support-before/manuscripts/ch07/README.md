# 第七章正文与配图

[阅读版 HTML](../07-数据中心网络.md) · [正文 Markdown](../07-数据中心网络.md) · [写作大纲](../../outlines/07-数据中心网络.md)

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

## 当前阅读版配图（2026-09-10）

正文现引用 48 幅图，以下清单按当前阅读顺序列出；上文旧图号用于追溯构建记录。

| 图号 | 内容 | SVG | PNG | PDF |
| --- | --- | --- | --- | --- |
| 7-1 | 固定两台服务器，每台四张卡。卡的数据先经过本地互联，再由两张网卡跨服务器传输；两张网卡共用的接口在每个方向上提供 40 GB/s。 | [SVG](figure-7-1-boundaries.svg) | [PNG](figure-7-1-boundaries.png) | [PDF](figure-7-1-boundaries.pdf) |
| 7-2 | 固定跨服务器需求下的设备扩展。每方向发送 336 MiB，共享出口为 40 GB/s；计算时间从 20 ms 开始，随设备数增加而按反比缩短。曲线分别按计算与通信串行、完全重叠计算，通信项取割集传输时间。 | [SVG](figure-7-2-cut.svg) | [PNG](figure-7-2-cut.png) | [PDF](figure-7-2-cut.pdf) |
| 7-3 | 连续环将同一服务器内的参与者排在一起。3→4 与 7→0 两条有向边跨服务器。颜色表示参与者所在服务器。 | [SVG](figure-7-3-hierarchy.svg) | [PNG](figure-7-3-hierarchy.png) | [PDF](figure-7-3-hierarchy.pdf) |
| 7-4 | 按 A、B 两服务器交替排列参与者，八条有向边都跨服务器。每参与者的总发送量保持不变。 | [SVG](figure-7-ring-interleaved.svg) | [PNG](figure-7-ring-interleaved.png) | [PDF](figure-7-ring-interleaved.pdf) |
| 7-5 | 本地先把八份贡献中的本机四份归约成分片，再由两台服务器交换对应分片，最后在本地收集完整结果。每列从上向下执行，横向箭头表示跨服务器交换。 | [SVG](figure-7-hierarchy-stages.svg) | [PNG](figure-7-hierarchy-stages.png) | [PDF](figure-7-hierarchy-stages.pdf) |
| 7-6 | 三方案的逻辑发送总量均为 2688 MiB；橙色跨服务器部分分别为 672、2688、384 MiB。两个方向合计。 | [SVG](figure-7-hierarchy-bytes.svg) | [PNG](figure-7-hierarchy-bytes.png) | [PDF](figure-7-hierarchy-bytes.pdf) |
| 7-7 | 四个前向阶段如何处理八个微批次。每格为 1 ms，数字表示微批次编号；同一编号沿右下方移动，表示该微批次依次通过各阶段。每个阶段计算 8 ms，在 11 ms 的总时间中各空闲 3 ms。阶段耗时相同，图中忽略额外交接开销。 | [SVG](figure-7-4-pipeline.svg) | [PNG](figure-7-4-pipeline.png) | [PDF](figure-7-4-pipeline.pdf) |
| 7-8 | 将全部 32 MiB 送入一张 25 GB/s 网卡，接收至少需要约 1.34 ms。 | [SVG](figure-7-5-expert.svg) | [PNG](figure-7-5-expert.png) | [PDF](figure-7-5-expert.pdf) |
| 7-9 | 四张独立网卡各接收 8 MiB，接收阶段缩短到约 0.34 ms。 | [SVG](figure-7-expert-path-1.svg) | [PNG](figure-7-expert-path-1.png) | [PDF](figure-7-expert-path-1.pdf) |
| 7-10 | 32 MiB 都需要先经过 40 GB/s 的共享入口，接收阶段受限于约 0.84 ms。这里各图均只计算接收载荷的传输。 | [SVG](figure-7-expert-path-2.svg) | [PNG](figure-7-expert-path-2.png) | [PDF](figure-7-expert-path-2.pdf) |
| 7-11 | 借用相邻网卡的路径。直接路径最多传输 40 GB/s；两张中继网卡合计 80 GB/s，但必须先经过剩余带宽为 60 GB/s 的本地互联。两路在下游汇合，最后还受外部网络和接收端可用带宽限制。箭头表示传输方向。 | [SVG](figure-7-6-relay.svg) | [PNG](figure-7-6-relay.png) | [PDF](figure-7-6-relay.pdf) |
| 7-12 | 主机 RPC 的参数从 CPU A 所在主机出发，经网卡和网络到达 CPU B 所在主机，由远端执行请求。箭头表示参数数据路径，返回结果沿反方向传送。 | [SVG](figure-7-7-access.svg) | [PNG](figure-7-7-access.png) | [PDF](figure-7-7-access.pdf) |
| 7-13 | 数据从 GPU 内存直接经过网卡到达远端 GPU 内存；虚线表示 CPU 提交请求，数据载荷无需经过 CPU 内存。映射和访问权限预先建立。 | [SVG](figure-7-access-1.svg) | [PNG](figure-7-access-1.png) | [PDF](figure-7-access-1.pdf) |
| 7-14 | GPU 通过 NVLink 访问对端 GPU 内存，由发起设备执行已授权的访问。 | [SVG](figure-7-access-2.svg) | [PNG](figure-7-access-2.png) | [PDF](figure-7-access-2.pdf) |
| 7-15 | 设备通过 URMA 提交异步读写，载荷经过 UB 互联到达目标设备；请求完成后按接口定义观察结果。 | [SVG](figure-7-access-3.svg) | [PNG](figure-7-access-3.png) | [PDF](figure-7-access-3.pdf) |
| 7-16 | 每次使用都访问远端，会重复传送同一份数据；下一图先搬回本地，再进行多次复用。两种路径处理同一份不变快照。 | [SVG](figure-7-snapshot-paths.svg) | [PNG](figure-7-snapshot-paths.png) | [PDF](figure-7-snapshot-paths.pdf) |
| 7-17 | 每次读取完整 144 MiB 快照时，两种方法的累计耗时。先搬回本地需要一次固定成本，从第二次复用开始节省时间。 | [SVG](figure-7-8-snapshot.svg) | [PNG](figure-7-8-snapshot.png) | [PDF](figure-7-8-snapshot.pdf) |
| 7-18 | 每次远程读取和本地读取都只访问 10%，但搬回时仍复制全部快照；因此需要更多复用才能抵消固定成本。 | [SVG](figure-7-snapshot-partial.svg) | [PNG](figure-7-snapshot-partial.png) | [PDF](figure-7-snapshot-partial.pdf) |
| 7-19 | 一项请求从分配记录开始占用槽位，经历传输与等待，完成状态被处理后归还记录。这里的 2 μs 覆盖完整占用区间。 | [SVG](figure-7-slot-lifetime.svg) | [PNG](figure-7-slot-lifetime.png) | [PDF](figure-7-slot-lifetime.pdf) |
| 7-20 | 128 个槽位在约 0.82 μs 内全部用完，要等最早的槽位在 2 μs 释放后继续提交。313 个槽位足以覆盖等待。蓝色表示载荷发送，灰色表示链路空闲。 | [SVG](figure-7-9-window.svg) | [PNG](figure-7-9-window.png) | [PDF](figure-7-9-window.pdf) |
| 7-21 | 蓝线只考虑链路和槽位，橙线再加入每 100 ns 发起一次请求的约束。增加槽位使蓝线升高，橙线仍受 2.56 GB/s 的提交速率限制。 | [SVG](figure-7-window-rate.svg) | [PNG](figure-7-window-rate.png) | [PDF](figure-7-window-rate.pdf) |
| 7-22 | 源缓冲占用到 5 μs 发送完成；目的缓冲持续保留到 12 μs 消费者用完。绿色为 8–12 μs 的读取区间。虚线标出 6 μs 提前覆盖目的地址的错误操作。 | [SVG](figure-7-10-lifetime.svg) | [PNG](figure-7-10-lifetime.png) | [PDF](figure-7-10-lifetime.pdf) |
| 7-23 | 两个应用端点分别保存身份与绑定记录，关系绑定指向同一目标的共享传输状态。共享部分维护传输进度，端点仍能区分各自请求。 | [SVG](figure-7-11-state.svg) | [PNG](figure-7-11-state.png) | [PDF](figure-7-11-state.pdf) |
| 7-24 | 64 个端点访问 128 个目标。蓝色为端点记录，橙色为关系绑定，绿色为传输状态。虚线为 1 MiB 容量；八类隔离复制八份目标传输状态。 | [SVG](figure-7-state-capacity.svg) | [PNG](figure-7-state-capacity.png) | [PDF](figure-7-state-capacity.pdf) |
| 7-25 | 将独立传输也排在发布之后：先写入 20 μs，恢复并使数据可见 80 μs，通知 2 μs，再执行独立传输 10 μs。 | [SVG](figure-7-12-ordering.svg) | [PNG](figure-7-12-ordering.png) | [PDF](figure-7-12-ordering.pdf) |
| 7-26 | 写入、恢复、通知仍依次进行；使用独立资源的传输从 0 μs 开始。蓝色为写入，橙色为恢复，绿色为通知，紫色为独立传输。 | [SVG](figure-7-ordering-independent.svg) | [PNG](figure-7-ordering-independent.png) | [PDF](figure-7-ordering-independent.pdf) |
| 7-27 | 按时间依次列出实际读取、数据更新、就绪通知和结果返回。5 μs 返回的仍是 1 μs 读到的旧值；若在 4 μs 发现冲突并重读，6 μs 得到新值。 | [SVG](figure-7-13-stale.svg) | [PNG](figure-7-13-stale.png) | [PDF](figure-7-13-stale.pdf) |
| 7-28 | 蓝色表示提交到传输完成，橙色表示等待软件处理完成通知，橙色结束才释放槽位。所有请求的时刻取自事件记录。 | [SVG](figure-7-14-reclaim.svg) | [PNG](figure-7-14-reclaim.png) | [PDF](figure-7-14-reclaim.pdf) |
| 7-29 | 增加槽位后，后续请求更早提交。完成通知仍每 20 μs 批量处理四项，最后一个槽位仍在 80 μs 释放。两图时间轴相同。 | [SVG](figure-7-reclaim-more.svg) | [PNG](figure-7-reclaim-more.png) | [PDF](figure-7-reclaim-more.pdf) |
| 7-30 | 两作业每 100 ms 各发送 20 ms，单作业速率 40 GB/s。不同高峰重叠程度产生不同的总到达速率，共享出口为 50 GB/s。 | [SVG](figure-7-15-congestion.svg) | [PNG](figure-7-15-congestion.png) | [PDF](figure-7-15-congestion.pdf) |
| 7-31 | 将到达与服务速率的差额随时间累积，得到 600、150、0 MB 三种峰值。此算例使用无限缓冲计算需求积压。 | [SVG](figure-7-congestion-queue.svg) | [PNG](figure-7-congestion-queue.png) | [PDF](figure-7-congestion-queue.pdf) |
| 7-32 | 数据沿实线进入队列并由出口发送；虚线表示拥塞反馈返回发送端。反馈到达并生效前，原发送速率继续填充队列。 | [SVG](figure-7-feedback-loop.svg) | [PNG](figure-7-feedback-loop.png) | [PDF](figure-7-feedback-loop.pdf) |
| 7-33 | 反馈生效之前，缓冲区还会继续填满。到达速率为 80 GB/s，出口为 50 GB/s，512 KiB 缓冲初始占用一半。8.7 μs 时填满，到 20 μs 降速前持续丢弃超额到达的数据；降至 40 GB/s 后，出口以 10 GB/s 的净速率排空积压。曲线直接取自既有有限缓冲模型，时间与降速幅度为给定条件。 | [SVG](figure-7-16-feedback.svg) | [PNG](figure-7-16-feedback.png) | [PDF](figure-7-16-feedback.pdf) |
| 7-34 | 两路径传播时延均为 1 μs，八报文约在 5.1 μs 全部到齐。圆点表示到达；到达后因缺口等待的区间用横线表示。 | [SVG](figure-7-17-packets.svg) | [PNG](figure-7-17-packets.png) | [PDF](figure-7-17-packets.pdf) |
| 7-35 | 第二条路径传播时延增加到 9 μs。快路径后续报文先到，仍需等待前方缺口；约 13.1 μs 全部可交付。 | [SVG](figure-7-packets-1.svg) | [PNG](figure-7-packets-1.png) | [PDF](figure-7-packets-1.pdf) |
| 7-36 | 序号 0 丢失后按算例等待时间重传，其他七个报文保留在接收端。只补发缺失报文后，约 23 μs 全部可交付。 | [SVG](figure-7-packets-2.svg) | [PNG](figure-7-packets-2.png) | [PDF](figure-7-packets-2.pdf) |
| 7-37 | 两项请求分别持有 A、B，各自等待对方持有的资源。箭头表示等待关系，两个请求都无法完成并释放资源。 | [SVG](figure-7-18-deadlock.svg) | [PNG](figure-7-18-deadlock.png) | [PDF](figure-7-18-deadlock.pdf) |
| 7-38 | 请求、执行、响应使用独立资源并按顺序申请。响应有预留缓冲和发送机会，能够返回并释放原请求。 | [SVG](figure-7-response-reserve.svg) | [PNG](figure-7-response-reserve.png) | [PDF](figure-7-response-reserve.pdf) |
| 7-39 | 原安排中，前三参与者等待第四个在 2 ms 就绪，再交换 0.4 ms。灰色为尚未就绪，橙色为等待其他参与者，蓝色为交换。 | [SVG](figure-7-19-progress.svg) | [PNG](figure-7-19-progress.png) | [PDF](figure-7-19-progress.pdf) |
| 7-40 | 就绪时刻相同，交换从 0.4 ms 减到 0.2 ms，全组从 2.4 ms 提前到 2.2 ms 完成。 | [SVG](figure-7-progress-1.svg) | [PNG](figure-7-progress-1.png) | [PDF](figure-7-progress-1.pdf) |
| 7-41 | 四个参与者在起点同时就绪，交换仍需 0.4 ms，全组在 0.4 ms 完成。三图时间轴相同。 | [SVG](figure-7-progress-2.svg) | [PNG](figure-7-progress-2.png) | [PDF](figure-7-progress-2.pdf) |
| 7-42 | 连续环串行安排：计算 20 ms，通信约 8.8 ms，更新 2 ms。灰为计算，蓝为通信，绿为更新；圆点为通信数据就绪。 | [SVG](figure-7-20-step.svg) | [PNG](figure-7-20-step.png) | [PDF](figure-7-20-step.pdf) |
| 7-43 | 通信缩短到约 6.6 ms，整步约 28.6 ms。 | [SVG](figure-7-step-1.svg) | [PNG](figure-7-step-1.png) | [PDF](figure-7-step-1.pdf) |
| 7-44 | 128 个在途事务限制远端吞吐，通信拉长到约 13.8 ms。 | [SVG](figure-7-step-2.svg) | [PNG](figure-7-step-2.png) | [PDF](figure-7-step-2.pdf) |
| 7-45 | 通信与剩余计算同时推进，更新等两者都结束；整步约 25.6 ms。 | [SVG](figure-7-step-3.svg) | [PNG](figure-7-step-3.png) | [PDF](figure-7-step-3.pdf) |
| 7-46 | 通信在计算结束前完成，更新从 20 ms 开始，整步 22 ms。 | [SVG](figure-7-step-4.svg) | [PNG](figure-7-step-4.png) | [PDF](figure-7-step-4.pdf) |
| 7-47 | 出口减至 20 GB/s，通信超出计算区间，整步约 30.6 ms。上述时间线采用同一横轴范围。 | [SVG](figure-7-step-5.svg) | [PNG](figure-7-step-5.png) | [PDF](figure-7-step-5.pdf) |
| 7-48 | 原配置每轮启动 5 μs、带宽 25 GB/s。绿色将带宽增至 75 GB/s，橙色将每轮启动减至 2 μs；小消息主要受启动影响，大消息主要受传输影响。 | [SVG](figure-7-21-message.svg) | [PNG](figure-7-21-message.png) | [PDF](figure-7-21-message.pdf) |
