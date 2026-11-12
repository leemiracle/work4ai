# 12 教程·示例·paper 三线对照总览：同一知识点的三副面孔

> 对象：全仓四板块的整体关系（tutorial.md / example code / paper / interview）；行号锚均于 2026-11-11 对照 commit `c760004` 源码核实。本篇是 explain 系列 12 篇的收官，为前三线提供横向对照视图。

## 一、角色定位

本篇对应的不是某个文件，而是仓库的**顶层设计本身**：根 `README.md:3-7` 把全仓切成 example code/interview/paper 三板块并交给 tutorial 统摄——同一套 RDMA 知识被刻意写了三遍，三遍的角色分工不同：教程线问「是什么、有哪些选择」（`tutorial.md:80-94` 把五参数抛成选择题），示例线给「最简可跑的一种答案」（两组代码各锁一种 verb 与 RC 连接），paper 线给「什么条件下选什么」（11 篇笔记全部围绕 it depends 展开），面试线负责「你能不能说出来」（见第 11 篇）。这种「一题三写」结构是本仓区别于普通教程仓的本质特征：知识点不是线性罗列，而是**从问题到默认解到条件解的漏斗**。图谱 12 层的前两层（L01 总览/L02 教程）、中间五层（L03-L07 示例）、后四层（L09-L12 paper）、L08 面试，层的分段就是三线的拓扑表达。

## 二、内部结构

以教程 2.2 五参数（`tutorial.md:84-88`）为经线，拉出全仓核心知识点的三线对照：

| 知识点 | 教程线（tutorial.md） | 示例线（example code） | paper 线 |
|---|---|---|---|
| send/recv | 2.1 六步（L67-72）+2.3 代码五小节 | send_recv 组：client.c/server.c 自包含；**实为单向演示**（server.c:269-271 的 on_connection 调用被注释） | FaSST.md:21-23（two-sided=Simple） |
| write/read | 2.4 四行浓缩骨架（L227-230） | write_read 组：SEND 换 MR 钥匙→单边 WR（rdma-common.c:215-226）+状态机（L44-55） | HERD.md:9（WRITE 延时一半）；RFP.md:24（inbound 优先） |
| poll 策略 | 2.2 双策略（L88）+2.3.5 事件式代码（L197-218） | 只实现 event-triggered（rdma-common.c:242-257）；busy 版需自己动手 | HERD.md:21 自实现 busy poll；Isolation.md:9-12（策略定隔离）；Cluster.md:16（应动态切换） |
| inline/signal | 2.2 两参数（L86-87）+2.6.1 实验（L247-257） | 只用 SIGNALED 不用 INLINE（rdma-common.c:320、send_recv/client.c:239）——教程 2.3.4 的 L187 却写着 IBV_SEND_INLINE | Design.md:20-23（DMA 次数解释）；Hybrid.md:11（Passive ACK=unsignal 思想） |
| QP 类型 RC/UC/UD | 2.2 一句定义（L84） | **两组示例全锁 RC**（build_qp_attr 设 IBV_QPT_RC，rdma-common.c:135） | HERD.md:13/FaSST.md:17-19：UD 是主角，RC 的可扩展性困境是整组论文的靶子 |
| MR/内存 | 2.3.2 注册与权限（L159-165） | register_memory 四块 MR、REMOTE_WRITE/READ 按 mode 走（rdma-common.c:294,306） | LITE.md:25（整物理内存单 MR）；RFP.md:24（client READ server 缓存） |
| 拥塞控制 | 3.2 一行方向（L312-315） | 无 | HPCC.md:9-15 三不足+INT 方案 |
| 建连状态机 | 2.3.1 只见 rdma_cm 黑盒（L100-157） | 同为 rdma_cm 封装 | 面经 L144 括号里的裸 reset→INIT→RTR→RTS 才是考点 |

## 三、外部连接

三线之间由图谱显式边缝合：`README documents→ tutorial`（主话语权）、`tutorial documents→` 两组示例 readme 与全部 11 篇 paper 笔记及两篇 interview 文件（L02 向六层辐射）、paper 层间 8 条 related 边（第 07-10 篇逐一拆解）。文本回指则稀疏不对称：教程 2.5（L237-241）与 `example code/README.md:3-4` 互相链接是唯一双向对；示例代码内无任何注释回指教程章节；paper 笔记反向引用教程也几乎没有——**对照表只存在于读者脑中，仓库本身不提供**，本篇与 ONBOARDING 第四节即是补这一层的产物。explain 系列内部：01 篇拆教程结构、02-06 篇逐文件深读示例（common 库/两入口/双边真相/poll_cq/状态机）、07-10 篇按四组拆 paper、11 篇做面试覆盖透视，本篇是 12 篇的汇总视图。

## 四、数据流

一个知识点的标准流转以 poll 策略为例走全程：教程 2.2（L88）抛出「busy 换速度、event 换 CPU」的二选一→示例 poll_cq（rdma-common.c:242-257）落地 event 式三件套（get_cq_event/ack/req_notify 重挂）→第 05 篇拆其线程模型→paper 线加条件：HERD.md:21 显示 KV 场景干脆放弃 CQE 自己 poll 内存、Isolation.md:9-12 实测 epoll 下大流抢带宽而 busy poll 保隔离、Cluster.md:16 结论是「poll 的机制应该要随着CPU的使用情况动态切换」→面试线（腾讯 L215、百度 L123）要求你把这串条件当场讲清。**教程给参数全集、示例取最简子集、paper 加条件、面试验表达**——四步漏斗每步都在收窄并深化。反向流也存在：作者自述的写作顺序实为「先跑实验与工程（HERD.md:27、TF.md:17 改雅虎源码）→再总结成教程给实验室同学」（README.md:3），即 paper 线在时间上先于教程线，教程是研究经验的降维表达——L291 那句总纲（参数选择取决于应用特性与资源状态）正是其研究结论的教学化。

## 五、设计决策

①**示例刻意只做子集**：全 SIGNALED、零 INLINE、全 RC——教学代码求正确可读不求性能全集；代价是教程 2.2 介绍的 5 个参数有 2.5 个（inline/busy poll/UD）在示例里找不到实例，读者须去 perftest 或论文找。②**教程代码块与示例源码是「浓缩改写」非拷贝**：2.3.5 的 poll_cq 与 rdma-common.c:242-257 同构，但 2.4 四行（L227-230）变量名 `M.remote_addr` 对应 `conn->peer_mr` 的浓缩（第 01 篇已勘误「一字不差」说法）；对照阅读以源码为准。③**send_recv 示例与教程叙述存在行为差**：教程 L74「和socket编程差不多」暗示双向，示例因 server.c:269-271 注释实为单向（ONBOARDING 勘误 1）——三线对照时「文档说了什么」与「代码做了什么」要分开记。④**paper 线不设 UD/拥塞控制等盲区的代码佐证**：教程承认研究边界（三章只列方向 L303-319），示例不越界——盲区诚实留白而非假装覆盖，与 11 篇透视出的三处面试盲区互为印证。⑤**面试线放在 interview/ 而非教程尾部**，保持教程的知识纯度——考核与教学分离。

## 六、新人提示

推荐闭环路径：教程一章+2.1-2.2 建词汇→第 01 篇看结构→示例 send_recv 跑通+第 04/05 篇读真相→write_read 精读+第 02/03/06 篇→教程 2.6/2.7 回看参数后果→paper 按 07→08→09→10 顺序（HERD 先行）→第 11 篇自测→回本篇表格查漏。三个对照习惯：①每学一个参数，立刻在第二节表格里横跳一次三线，问「教程怎么说、示例怎么做、论文怎么条件化」；②警惕「教程=代码」的错觉，两处已知偏差（单向演示、浓缩改写）要记；③UD 与拥塞控制是示例线空白，别在 example code/ 里找——直接去 paper 线（FaSST/HPCC）与 perftest。一句话总结本仓：**它用一份教程、两组代码、11 篇笔记、一份面经，把 RDMA 参数选择从「知识点」训练成「判断力」**——判断力的最终形态，就是面经 L161 括号里那句自注：「强调针对多应用、自底向上的分析以及运行时调整参数的亮点」。
