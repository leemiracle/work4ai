# 07 paper 笔记·verb 选择与 RPC 组：HERD / FaSST / RFP

> 对象：`paper/HERD.md`（29 行）、`paper/FaSST.md`（25 行）、`paper/RFP.md`（35 行）；行号锚均于 2026-11-11 对照 commit `c760004` 源码核实。

## 一、角色定位

这是 paper 线四组中的第一组（图谱 L09「paper 笔记：verb 选择与 RPC 设计」，3 节点），回答教程 `tutorial.md:85` 抛出的第一道参数选择题——**verb 怎么选：send/recv、write 还是 read？**。三篇构成一条完整的论辩链：HERD（SIGCOMM 2014）立论「WRITE 优于 READ、UD 优于 RC」；FaSST（OSDI 2016）把同一结论推广到 all-to-all 事务场景并补上微架构论据；RFP 则反转「one-sided 必快」的流行观点，论证 RPC 语义 + inbound 优化可以更快。HERD 笔记开篇即给出本组的阅读价值排序——`HERD.md:3` 称其为「RDMA 与具体应用结合方面最值得看的一篇文章」，理由有二：key-value 应用比 spark/tensorflow 简单（L3），且它做了「非常详细的 RDMA 参数选择的分析」（L3）。这一推荐后来被 ONBOARDING 第七节采纳为 paper 线的首读篇目。

## 二、内部结构

三篇均为「背景→方案→反思」三段式，但各有侧重：

| 笔记 | 会议 | 核心论点 | 关键小节 |
|---|---|---|---|
| HERD.md | SIGCOMM 2014 | WRITE+UD 是 KV 服务最优组合 | WRITE or READ?（L7）/ Scalability（L11）/ HERD 的实现（L19） |
| FaSST.md | OSDI 2016 | UD two-sided RPC = Fast/Scalable/Simple 三节（L7/L17/L21） | 三优势各一节 |
| RFP.md | — | RPC 可快于 server-bypass | 背景问题（L3）/ 解决方案（L7）/ Challenges（L31） |

**HERD 的两个论证**最值得精读：①WRITE vs READ（L9）——此前 Pilaf 等工作用 READ 实现 GET，但 hash 冲突使 GET 平均需 2 次以上 READ（多个 round trip），实验测得「WRITE 的延时是 READ 的一半，吞吐量也比 READ 高」（L9），改用 WRITE 一次往返完成；②Scalability（L11-L13）——服务端若用 WRITE 向多客户端回包，需大量 QP，而「RDMA 网卡的缓存是有限的，当缓存溢出时会从主机内存中取相应的 WQE 信息，性能会急剧下降」（L13），故改用支持一对多的 UD。**FaSST 的 Fast 节（L9-L11）含全 paper 线唯一的论文原文英文引用**——doorbell 机制「per-QP Doorbell register on the NIC」与「ring the Doorbell once per batch」（L10-11），为 UD 的 batching 优势留下可回溯的一手证据。**RFP 的两发现（L11-12）**是逻辑支点：RDMA inbound 性能优于 outbound；server-bypass 因多次 access 实际不如预想——由此推出「server 端将请求结果缓存在自己内存，由 client READ 取回」（L24）的反直觉设计。

## 三、外部连接

图谱 related 边：`FaSST → HERD`（本组唯一的组内边）。文本证据密集：`FaSST.md:3`「会发现和HERD有很多相似之处」、L9「Fast指的是HERD中提到的READ需要多个round trip」、L19 可扩展性问题「类似HERD」——FaSST 笔记是带着 HERD 读的。跨组边两条：`Design Guidelines → HERD/FaSST`（HERD/FaSST 提出的 doorbell batching、cheap RECV posting 在 Design Guidelines 里得到 PCIe 层解释，见第 08 篇）、`Improving TF → HERD`（TensorFlow 笔记 L17/L19 明言「见HERD的实现分析」——poll 内存检测法被作者移植到深度学习框架，见第 10 篇）。向上游，图谱 `tutorial.md documents→` 三笔记的边对应教程参考文献：`tutorial.md:331` 参考 1=HERD、L336 参考 6=RFP。HERD.md:27 还藏着一条时间线证据——作者自述「后面我把tensorflow改成WRITE时自己也是这么做的，后来才反应过来HERD也是这样」，说明 HERD 的方法论先被无意识复用、后被确认为源头。

## 四、数据流

论文观点进入教程的两条通道：①**参数题对位**——教程 2.6.2 verb 实验（`tutorial.md:259-269`，write 与 read 延时对比）就是 HERD L9 论断的读者可复现版；教程 2.2（L85）对 verb 的三行定义在此获得「选哪个、为什么」的答案层。②**问题意识下沉**——HERD.md:27 的反思「是不是WRITE加上这种poll内存的方式在任何情况下都要比READ好呢？其实并不是……在CPU资源不足的情况下……应用的整体性能可能还不如其他节省CPU的verb」，与教程 2.7 的总纲句「具体的RDMA参数选择与不同应用的应用特性以及相关的服务器资源状态有关」（`tutorial.md:291`）同构——后者正是前者的普遍化，也串起 Cluster Configuration 与 Hybrid is Better 两篇后作。组内数据流则是「发现-复用」型：HERD 的「CPU 轮询 keyhash 字段判断请求到来」（L21，作者注「类似于自己实现了busy poll」）经 FaSST 细化、经 TensorFlow 笔记 L17 移植，成为贯穿三组笔记的一条暗线。

## 五、设计决策

①**笔记保留推荐理由而非只留结论**：HERD.md:3 用整整一段解释「为什么初学者先读这篇」（应用简单+参数分析细+作者 Anuj Kalia 源码开放有问必答）——这是选读策略的一部分，不是闲笔。②**三篇覆盖同一问题的三个抽象层**：HERD 站在应用（KV）层、FaSST 站在原语组合（RPC over UD）层、RFP 站在方向性反思（RPC vs bypass）层——组的划分本身就是「verb 选择」这个题目的三层展开。③**英文原文掐句引用是 FaSST 独有的严谨处**：L10-11 直接引原文而不转译，与其它笔记的纯中文转述形成对照——doorbell 是微架构概念，转译易失真。④**RFP 笔记是未完成态**：L35「## Solution」标题下无正文，两挑战（L33-34：client 何时去 read、默认结果大小）悬置——读时须知这是占位结构。⑤HERD.md:29 以「不适合科研，适合做苦力」的自嘲收尾，是作者择业心路的原始记录，也是本仓「工程视角」基调的注脚。

## 六、新人提示

按 HERD→FaSST→RFP 顺序读：HERD 建立问题框架（两个参数选择：verb+连接类型），FaSST 检验框架在 all-to-all 场景的稳健性，RFP 教你警惕「one-sided 更快」的教条。读前确保已掌握教程 2.2 五参数（`tutorial.md:84-88`），否则「UD/RC」「one/two-sided」这些词会悬空。三个抓手：①把 HERD L13 的「网卡缓存有限→WQE 溢出→性能急剧下降」背下来，它是后续 FaSST/Design Guidelines/LITE 三组笔记共用的可扩展性叙事起点；②FaSST 的 doorbell 引文（L10-11）与第 08 篇 Design Guidelines L7 的 MMIO 解释对读；③RFP 只需记两发现+一设计（inbound 优先、server 参与、client READ 回收），不必纠结空缺的 Solution 节。HERD 插图（L15-17、L23-25 的 GitHub URL）离线会挂，结论文字自足可读。
