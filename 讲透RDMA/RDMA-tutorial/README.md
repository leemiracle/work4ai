# 讲透 RDMA-tutorial

[StarryVae/RDMA-tutorial](https://github.com/StarryVae/RDMA-tutorial) @c760004 · RDMA 中文教程（教程主线+write_read/rdma_send_recv 示例+paper 笔记 11 篇+面试线）

| 产物 | 状态 | 明细 |
|---|---|---|
| deepwiki | — | NOT_INDEXED → repo-docs 兜底（18 文件） |
| understand 图谱 | ✅ | 84n/127e/12 层/16 步 tour · validator 0 issues · fingerprints 26 files@c760004e |
| onboarding | ✅ | 5997 字 8 节 · 85 锚零越界 |
| explain | ✅ | 12 篇 42238 字符 · 120 锚终验真坏 0（缩略路径别名归一后全过） |

## 源码级勘误精选

- **send_recv 示例实为单向演示**：server.c:269-271 ESTABLISHED 分支被注释（问候函数成死代码）+ client.c:198 post_receives 被注释——图谱 tour 11/12 步描述与代码不符，onboard/explain 04 已纠
- tree-sitter 实测漏 5 函数（get_peer_message_region+usage×2+die×2），任务书口径 4，实测以源码为准
- tutorial.md 浓缩改写非逐字拷贝（L227-230 四行单边骨架，M 即 conn->peer_mr）；L90 承诺"黄色背景标注"未兑现；两个 2.6.2 节号重复
- write_read readme 命令名与 Makefile 产物名不符；端口非 22222（内核随机分配）
- RFP.md:35「## Solution」空节、HPCC 笔记止于 Challenges（未完成态笔记）
- struct connection 系 C struct+匿名枚举状态机（SS_RDMA_SENT 隐式中间态），误标 class 已纠
- 面试线量化：177 题/12 轮/RDMA 题 31 道，识别 3 处教程盲区（裸 QP 状态机/RDMA vs DPDK/RoCE 组网部署）
