# 09 paper 笔记·资源共享与隔离组：LITE / Performance Isolation Anomalies / Resource Sharing

> 对象：`paper/LITE.md`（37 行）、`paper/Performance Isolation Anomalies in RDMA.md`（41 行）、`paper/Toward Effective and Fair RDMA Resource Sharing.md`（33 行）；行号锚均于 2026-11-11 对照 commit `c760004` 源码核实。

## 一、角色定位

paper 线第三组（图谱 L11「paper 笔记：资源共享与性能隔离」，3 节点），把前两组的「单应用怎么跑快」翻转为「**多应用共存时会发生什么**」。三篇是问题-方案-进阶关系：Performance Isolation Anomalies（KBNets 2017）用实验证明共享 RDMA 网络的应用互相干扰且不可预测；LITE（SOSP 2017）在内核加 indirection layer 一揽子解决接口/可扩展性/共享三问题；Resource Sharing（APNet 2018 best paper，系统名 Avatar）专攻共享 QP 的锁竞争与公平调度。本组与作者本人研究点关系最深：Isolation Anomalies 是「我第一篇读懂的关于RDMA的文章，也是领我入门的一篇文章」（`Performance Isolation.md:3`），Resource Sharing 作者是其阿里师兄（L3 长段交往记），LITE 则「我后续的很多研究也是受到这批文章的启发」（`LITE.md:3`）。它还是面试线的弹药库——阿里云二面「QP share已经有具体的实现方法了啊？（我们是在无锁的情况下如何公平的share）」（面经 L162）、「吞吐量敏感和延时敏感的流量同时存在怎么办？」（L170）、三面「讲一讲资源共享的问题？无锁的实现？」（L180）三道真题全部由本组三篇笔记供弹。

## 二、内部结构

**Isolation Anomalies 是三组实验的报告**：流分类（L5）——大于 1MB 为吞吐敏感大流、小于 1KB 为延时敏感小流，三组竞争实验：大流 vs 大流（L7-12）——epoll 方式下包更大者抢到更多带宽，busy poll 方式下隔离有保障；大流 vs 小流（L18-20）——大流 epoll+小流 busy poll 时小流延时与吞吐急剧下降、大流不受影响；小流 vs 小流（L26-28）——即使包大小相同结果也不可预测。结论节（L34-38）把三现象归因到 WQE 层：大流间竞争取决于 poll 策略（即应用向网卡投递请求的速率）、大流压迫小流因小流 WQE 排队、小流彼此因 WQE 都被快速处理而充满随机性。**LITE 是标准系统论文笔记**：三背景问题（L9-11 接口难用/可扩展性差 lkey·rkey·PTE·QP 数量/缺共享隔离）→ 类比虚拟内存与文件系统的 indirection layer 方案（L15）→ 三挑战（L17-19 加层不伤性能/通用灵活/不改硬件驱动 OS）→ 三设计小节：内存抽象（L23-25，把整个物理内存注册成一个 MR，消除 RNIC 中 PTE，lkey/rkey 数量降为 1）、LITE RPC（L27-29，WRITE with imm + 全部请求共享一个 CQ 省 CPU）、资源共享（L31-33，「没有具体的资源共享的策略」）。**Resource Sharing 是两层方案**：无锁层（L15-19）——应用不直接 post WQE 到 QP 而是缓存进自己的 egress queue，由 Avatar 层的 worker 线程用 epoll+efd 监听各队列统一投递，锁竞争消失；公平层（L29-31）——schedule 层把大 data block 切成小 segment，同优先级 Round-Robin。

## 三、外部连接

图谱 related 边两条汇聚于本组：`Performance Isolation → Resource Sharing`、`LITE → Resource Sharing`——后者是组内终点站，它继承前两者的遗题：LITE 自认「没有具体的资源共享的策略」（LITE.md:33），Resource Sharing 正是来填这个坑的；Isolation Anomalies 证明的不公平现象（epoll 下大流抢带宽，L11）则是公平层（Round-Robin+切 segment）要治的病。文本佐证：Resource Sharing.md:5 的背景叙述「很多文章提到的RDMA网卡缓存有限导致的可扩展性的问题，现有研究都是直接通过多个线程共享QP来缓解」承接 HERD 的可扩展性叙事（第 07 篇）。向上游，教程 3.1 节列「QP share解决可扩展性问题[7]」（`tutorial.md:309`），参考 7 即 Resource Sharing（L337）——这是教程三章研究地图与 paper 线的官方对位之一。LITE.md:3 还牵出跨组人际线：「阿里师兄APNet那篇文章据说灵感来自于这篇文章」——LITE 是 Cluster Configuration（第 08 篇）的灵感上游，组间由此再添一条隐性引用链。面试线的 `面经 → 知识点` related 边（L08 层）虽是文档间边，其知识实质由本组承接：知识点.md:13 要求了解「拥塞控制的一些方法、多路径传输、和虚拟化的结合」，前半在 HPCC（第 10 篇）、虚拟化的结合源头即 LITE 的内核层抽象。

## 四、数据流

论文观点进入实践的三条通路：①**实验方法论的移植**——Isolation Anomalies.md:3 强调「提供了实验对比的源码……进一步分析源码，深刻理解在一般的科研过程中，如何结合已有的RDMA编程的知识去设计RDMA实验」（SymbioticLab/frdma_benchmark），大流/小流的流分类法（L5）直接复刻进作者自己的研究与面试答案（面经 L170 的提问正是用这对概念组织回答）。②**epoll 经验的闭环**——Resource Sharing.md:33 自述复现 Avatar 时的 epoll/efd 实战「给我当时找工作带来了不少帮助」，与面经 L186「epoll的实现」（阿里三面）、面经 L123「I/O多路复用技术」（百度系统部三面）形成「论文→复现→面试」的完整数据流；同技术还出现在 Cluster Configuration 的 busy/event 切换结论里——epoll 是贯穿 08/09 两组的共享词汇。③**接口分层思想的传递**——LITE 的 indirection layer（L15）与 Cluster Configuration.md:18 的 higher-level 库构想同构，Resource Sharing 的 Avatar 层（L17）是其用户态变体；三者叠加把「要不要在应用与 RNIC 之间加一层」从单篇论文的主张变成一个研究方向的共识，教程 3.1 的「易于使用且高性能的RDMA编程库[6]」（`tutorial.md:308`）即其条目化。

## 五、设计决策

①**组内排序即知识递进**：现象（Isolation Anomalies）→ 系统性方案（LITE）→ 聚焦深化（Resource Sharing），图谱层节点序 [LITE, Isolation, Resource Sharing] 是字典序，但阅读序应取 Isolation→LITE→Resource Sharing（ONBOARDING 第七节即此序）。②**LITE 笔记保留批判性追问**：L35-37 指出 LITE 接口只是三种元语的封装、「应用在与RDMA结合时还是要自己去决策选用哪种传输方式」、资源共享缺策略——两问分别被 Cluster Configuration 的「该由库屏蔽复杂性」和 Resource Sharing 的公平调度接走，批判成了组内导航。③**Isolation 笔记记下负结果**：L40 提到曾尝试用 IB 链路层 virtual lane 做隔离「当时尝试后失败，而且这篇文章中也提到这种方式不可行」——失败路径被记录，防止后人重复踩坑；同段提出的「先提供调度的框架，策略再往里加」设想正是其后续研究纲领。④**Resource Sharing 笔记的人情味段落刻意保留**（L3 整段师兄交往记、L33 结尾）——它解释了这篇为何被精读并复现，是理解笔记深度差异（为何此篇有实现细节 epoll/efd 而他篇无）的钥匙。

## 六、新人提示

先读 Isolation Anomalies（最易读，实验故事完整），再 LITE（系统设计范本），最后 Resource Sharing（需要 epoll/efd 前置）。三个前置检查：①不懂「为什么 QP 多了会慢」先回 HERD.md:13（网卡缓存有限）；②不懂 LITE 消 PTE 的意义先记结论——MR 注册会在 RNIC 里建地址翻译表，把整块物理内存注册成单一 MR 则表项数与 lkey/rkey 都坍缩为 1（LITE.md:25）；③Resource Sharing 的 egress queue+worker 模型建议画一遍时序图——「谁持锁→谁 post」换人是无锁的本质。面试向读者重点背三组对应：流分类（>1MB/<1KB）→面经 L170；无锁共享（egress queue+epoll+efd）→L180；QP 共享的动机（缓存有限+锁竞争）→L162。提醒：本组三篇均无代码落地在本仓示例中（示例是单应用视角），共享/隔离实验需自行去 frdma_benchmark 仓库。
