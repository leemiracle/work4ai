# 11 · README 与教程叙事对照：承诺与实现的差异清单

## ① 角色定位

README.md（25 行，图谱 `document:README.md` 节点）是本教程的**目录页与承诺书**：它承诺四件事——这是一个 example based tutorial（README:2-3）、硬件软件要求（README:5-9）、make 即可构建（README:13-15）、示例按 git commit 组织（README:17-21）。但 README 描述的是"教程的理想形态"，真正交付给克隆者的是 HEAD 的代码快照 + 14 个 commit 的历史 + 一个不在仓内的 Wiki。本篇做叙事与代码的逐条对照，产出一张**差异清单**——它是新人"从 README 进入仓库"时最需要的一份勘误地图，也是把前几篇的零散发现（Wiki 外置、RDMA write 不在 HEAD、时代印记）收拢到"文档视角"的一篇。

## ② 内部结构

README 四段结构：①定位段（README:1-3）——项目名 + "example based tutorial on RDMA based programming" + Wiki 链接；②环境段（README:5-9）——Mellanox HCAs / GNU make / gcc-4.4 / Mellanox OFED 3.3 四项要求；③使用段（README:11-21）——`make` 与 `make debug` 两条构建命令 + "项目含 4 个示例，代码按 git commit 组织，`git log --oneline` 查版本号"的导航说明；④联系段（README:23-25）。25 行里没有 License 章节、没有运行说明、没有配置格式——这些空白都是本篇④的对照素材。

## ③ 外部连接

README 的两条出边性质不同：**Wiki 链接是仓外依赖**（github.com/jcxue/RDMA-Tutorial/wiki，README:3/19 两处引用）——教程声称的"detailed discussion"全部住在 GitHub 服务上，`git clone` 拿不到，离线环境等于失联；**git commit 是仓内导航**（README:20-21）——这是本仓最独特的教学设计：目录不按文件组织而按历史组织，每个 Example 是一个可 checkout 的快照。README 与 Makefile 的连接已在第 10 篇拆过（构建承诺由 23 行 Makefile 兑现，且靠 2019 年的社区 PR 才真正可用）；README 与 LICENSE 的连接则是**缺失**的——仓根有 Apache 2.0 全文 LICENSE，README 正文只字未提（对照开源惯例的 License 章节，这是 2014 年小项目的常见省略）。

## ④ 数据流：承诺 vs 实现的逐条对照

**对照 1："4 examples" vs git 历史的 6 个演进 commit**。`git log --oneline` 实测（全 14 commits）：65893ec "Example 1: use RDMA send/recv" → e1570c6 "Example 1: minor tweaks" → f73736e "Example 2: use RDMA write" → 1b460c2 "Example 3: use message inlining" → d7dd63e "Example 3: use message batching" → ec2a4db "Example 4: use SRQ"，另有 36e6b6a 初始提交与 5 个 README/Makefile 维护提交（含第 10 篇的 PR #7）。编号确实是 4 个，但 **Example 1 有两个 commit、Example 3 有两个 commit**——按 README 的"commit 即示例"导航法，实际可 checkout 的教学站点是 6 个而非 4 个，Example 3 的 inlining→batching 两步演进本身就是一个被 README 编号掩盖的教学单元。

**对照 2：HEAD ≠ 全部教程**。本系列 12 篇（含本篇）分析的全部是 HEAD=be4d713，即 **Example 4（SRQ 版 echo 基准）的最终态**。HEAD 里没有 RDMA write 的实现（那是 Example 2 的内容，f73736e 才有）、没有 message inlining 的演进痕迹——post_send 固定 `IBV_SEND_SIGNALED` 且 8 字节消息远小于内联阈值（第 6 篇⑤⑤）。换句话说：**只读 HEAD 的人永远看不到 README 承诺的一半教学内容**，git checkout 逐站游历才是本仓的正确打开方式。

**对照 3："Mellanox HCAs" vs 代码的隐性网络限定**。README 只说需要 Mellanox HCA，但代码里 `ah_attr.is_global=0`（ib.c:38）+ 纯 LID 寻址（QPInfo 的 lid 字段，ib.h:30）意味着**只支持经典 InfiniBand 子网**——RoCE（v1/v2）需要 GID 与 GRH 全局路由（is_global=1 + gid_index），本代码结构上就跑不了。README 的环境段还停在 2014（gcc-4.4/OFED 3.3），实际现代发行版装 libibverbs-dev 即可编（第 10 篇⑤③）——环境承诺"过时但不挡路"，网络类型承诺"缺失且真挡路"，两处时代印记的性质不同。

**对照 4：README 的沉默清单**。以下事实对运行至关重要，README 全部未提，仅能从代码/样例反推：运行方式 `./rdma-tutorial config_file sock_port`（main.c:20 的 usage 是唯一出处）；sample.config 是配置格式的唯一文档（servers/clients 区间写法、num_concurr_msgs、msg_size，第 2 篇已拆）；**角色判定靠 hostname 匹配配置列表**（config.c:92-133），换集群必踩节点名硬编码坑（config.c:77-81 的 saguaro/mnemosyne 二选一，第 12 篇展开）；日志落在 server[rank].log / client[rank].log（main.c:52-54）；至少两台机（client/server 各一）才有意义。教程的"上手补全信息"实际由三处分担：README（构建）、Wiki（原理，仓外）、sample.config+源码（运行）。

## ⑤ 设计决策

**① 为什么用 commit 当章节**：对比常见做法——每示例一个目录（rdma-write/、srq/ 平铺）——commit 组织法的独特优势是**演进可 diff**：`git diff f73736e ec2a4db` 直接给出"从 RDMA write 到 SRQ 改了什么"的最小增量，这是目录平铺给不了的。代价是新人的默认视野（HEAD）只含最终态，且教程结构对 git 门外汉不友好——README:20 用一句 "Simply do git log --oneline" 把导航成本压到最低，算是坦诚的折中。

**② README 的极简主义是身份自认**：25 行的 README 把自己定位成"路标"而非"手册"，细节全部外包给 Wiki 与 commit 信息。这符合 2014 年个人教学仓的习惯；但 Wiki 单点依赖 GitHub 服务的风险在十年后显形——若 Wiki 失效，本仓的可读性将大打折扣（幸而代码注释密度尚可，且本系列 explain 即是对仓内自足知识的一次重建）。

**③ README 自身也活在历史里**：git log 里 4 次 "Update README.md"（含 a6c2e78）说明这份 25 行文档同样被反复修订——文档与代码一样是演进 artifact，读 README 也该带 `git log -p README.md` 的考古意识，与第 10 篇 Makefile 考古互为镜像。

## ⑥ 新人提示

推荐阅读序：README（5 分钟）→ `git log --oneline`（把 6 个 Example 站点记下来）→ 本系列 01 篇（HEAD 的六段生命周期）→ **按 65893ec → ec2a4db 逐 commit checkout 对读 diff**——每个 Example 的教学增量都在 diff 里（Example 1→2 看 RDMA write 怎么替代 send/recv，2→3 看 batching/inlining 的性能手法，3→4 看 SRQ 怎么把接收池从 per-QP 提到全局）。三个提醒：① 别在旧 commit 上用 HEAD 的认知读代码——Example 1 时 sock.c/ib.c 的形态都不同；② 若要在真实集群复现，先过第 12 篇的边界清单（节点名/IB 类型/拓扑假设），README 的环境段不足以保证跑通；③ 想引用本教程时注明它 Apache 2.0（LICENSE 文件），README 没写不等于没有授权。最后的元提示：本篇的差异清单法（承诺逐条 vs 实现逐条）适用于任何教程仓的入门审查——README 的"沉默处"往往比"明说处"更影响第一次运行的成功率。
