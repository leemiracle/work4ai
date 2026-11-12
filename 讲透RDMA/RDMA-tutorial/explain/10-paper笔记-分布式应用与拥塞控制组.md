# 10 paper 笔记·分布式应用与拥塞控制组：Hybrid is Better / TensorFlow / HPCC

> 对象：`paper/Deconstructing RDMA-enabled Distributed Transactions Hybrid is Better!.md`（18 行）、`paper/Improving the Performance of Distributed TensorFlow.md`（19 行）、`paper/HPCC.md`（21 行）；行号锚均于 2026-11-11 对照 commit `c760004` 源码核实。

## 一、角色定位

paper 线收官组（图谱 L12「paper 笔记：分布式应用与拥塞控制」，3 节点），从「参数与资源」上升到「**真实分布式系统怎么用 RDMA**」。三篇覆盖三个应用面：Hybrid is Better（上交 IPADS）面向分布式事务，主张按阶段混搭元语；TensorFlow 笔记面向深度学习训练，直接替换 gRPC；HPCC（SIGCOMM，阿里云）面向网络本身，解决 RoCE 拥塞控制。组内张力点在 verb 选择题的三种答案形态：Hybrid 答案是「逐阶段混合」（Deconstructing.md:5）、TensorFlow 答案是「工程替换+踩坑」（L17）、HPCC 则把问题下沉到「速率由什么信息决定」（L15）。这一组也是作者研究纲领的最终佐证层——Deconstructing.md:5 自评「完美的佐证了我第一个研究点的主要内容：固定的RDMA参数并不总能给应用带来最佳的性能」。

## 二、内部结构

**Hybrid is Better 是三段短评**：看标题猜主旨（L3「难道是指RDMA参数的混合？」果然）→ 核心方法 phase-by-phase——「不在纠结于是one-sided还是two-sided……而是逐阶段的分析分布式事务在execution、validation、commit、logging阶段分别适合使用哪些元语」（L5）→ 新知识点 Passive ACK（L11）：one-sided 侧即 unsignal，two-sided 侧利用对称传输「请求的完成可以通过对方的回复而得知，从而减少一半的数据包」——作者随即质疑「感觉是应用层次上的优化……在传统网络里也可以这么做？」（L11）。**TensorFlow 笔记是实验+工程复盘**：背景实验（L5）——TCP/IP 下分布式训练 Alexnet 反而慢于单机，证瓶颈在网络；方案（L11）——分析 TF 的 send/receive 流程定位替换模块，用 WRITE/READ 替换 gRPC；工程深水区（L17）——作者读雅虎开源的 RDMA 版 TF 源码，动手把 write_with_imm 改成 write（手写数字识别上有些许提升），又想把 ps-worker 一对多改 UD 但因「UD只支持MTU的数据包传输，而深度学习模型中的参数会很大」放弃；反思（L19）——write 替换后需 poll 内存检测请求到来（呼应 HERD），CPU 消耗变大，「在CPU资源不足的情况下……是得不偿失的」。**HPCC 是问题-方案-挑战骨架**：三不足（L9-11）——ECN/RTT 粗粒度反馈致收敛缓慢、先建队列再调速伤延时敏感流、参数复杂致网络不稳定；方案（L15）——「利用INT（网络遥感）技术获取细粒度的网络负载信息来计算精确的流速率」；两挑战（L19-21）——INT 信息在包尾会被拥塞波及、逐 ACK 响应会过度调整。

## 三、外部连接

图谱 related 边两条接出本组：`Deconstructing → On the Impact of Cluster Configuration`（第 08 篇）——两篇同证「参数无全局最优」，前者按事务阶段混合、后者按集群状态调整，是同一命题的应用态与配置态；`Improving TF → HERD`（第 07 篇）——TensorFlow.md:17 明写「需要监测数据请求的到来（见HERD的实现分析）」，poll 内存法跨应用移植。向上游是全 paper 线最密的教程接口：教程 2.7 节整个 TensorFlow 段落（`tutorial.md:283-301`，含手写数字识别实验图 L297-301）即此篇笔记的教程版；参考文献 L333（参考 3=tensorflow verbs 仓库）、L339（参考 9=HPCC）与笔记里给出的同一仓库链接（TensorFlow.md:17 尾部 github.com/tensorflow/.../contrib/verbs）逐字对应——**教程与笔记互为镜像**。HPCC 对位教程 3.2「拥塞控制[8][9]」（`tutorial.md:314`）。面试线接口密集：RDMA 拥塞控制是四公司高频题——百度系统部一面 L79「RDMA拥塞控制、TCP拥塞控制」、二面 L108「TCP拥塞控制」+L109 发送/拥塞/接收窗口关系、腾讯一面 L220-221「tcp和rdma在拥塞控制方面的根本差别」「tcp在哪里感知拥塞，roce呢」、阿里二面 L163「RDMA和TCP本质上的差别（想听的是传输层拥塞控制的一些区别）」——HPCC 笔记的三不足框架（L9-11）正是组织这些答案的现成骨架。

## 四、数据流

本组是「论文观点→教程正文」渗透最深的一组：教程 2.7 的叙事线（TCP 瓶颈实验→替换 gRPC→注意参数选择）与 TensorFlow 笔记的背景-方案-反思三段几乎逐点同构，教程 L291 的总纲句「大量单纯在工程上修改应用的工作……忽略了应用自己的特性以及服务器的资源状态」是笔记 L19「得不偿失」教训的规范化。Hybrid 的数据流方向相反——它是从论文**流向作者研究点**的证据：L5 明言佐证「RDMA参数需要在应用运行时根据应用的特性和服务器资源状态进行调整」，与 HERD.md:27、Cluster Configuration.md:13-16 构成三时间点三来源的同命题收敛（2014 KV 场景→2019 集群配置→事务分阶段）。HPCC 的知识则流向面试线：INT/ECN/RTT 三个词把「RoCE 拥塞控制怎么答」从一句「和 TCP 不同」扩展为机制对比——TCP 在丢包/RTT 信号上启发式收敛，RoCE 网卡侧 ECN 标记+PFC 保无损，HPCC 主张 INT 遥测精确算速率（HPCC.md:9-15）。

## 五、设计决策

①**三篇代表 RDMA×应用的三种结合深度**：黑盒替换（TensorFlow 直接换 gRPC）、按阶段定制（Hybrid 逐阶段选元语）、下沉网络层（HPCC 改拥塞机制本身）——组的命名「分布式应用与拥塞控制」即此二分。②**笔记保留未竟工程**：TensorFlow.md:17 详细记录 UD 替换失败原因（MTU 限制+集群小+「只是工程上的问题，没有理论科学问题，老师不是很认可」）——负结果与放弃理由同记，与 Isolation 笔记记 virtual lane 失败（第 09 篇）同一作风。③**Passive ACK 的质疑是批判性阅读示范**：Deconstructing.md:11 对论文卖点追问「和RDMA没啥关系？在传统网络里也可以这么做？」——不因论文会议光环而放过可迁移性的检证。④**HPCC 笔记止于 Challenges 未写 Solution 细节**（L17 节后无正文），与 RFP 笔记的空 Solution 节（第 07 篇）同属未完成态——11 篇笔记中 2 篇有此结构，读时先查文末是否还有下文再动手推导。

## 六、新人提示

阅读顺序建议 TensorFlow→Hybrid→HPCC：TensorFlow 最贴近教程 2.7（可对照 `tutorial.md:297-301` 的实验图同读），Hybrid 需要先有 one/two-sided 词汇（回教程 2.2 与第 07 篇），HPCC 需要拥塞控制前置（ECN/RTT/INT 三个词先查清）。三个抓手：①Hybrid 的阶段名 execution/validation/commit/logging 是分布式事务的骨架词，不熟事务也可只记结论「逐阶段选元语优于全局单选」；②TensorFlow 笔记 L17 的 write_with_imm→write 改造是全 paper 线唯一的动手改码记录，配合 HERD.md:21 理解 poll 内存代价；③HPCC 三不足（收敛慢/先排队/参数多）背成三行，面试遇拥塞题先铺框架再展开。提醒：本组 PDF 在 `paper/pdf/`（RDMA Tensorflow.pdf 等 11 份）可查论文原文，但笔记引用的插图 URL（GitHub blob 链接）离线会挂，本地对应 `image/paper/` 目录。
