# explain-05 · flow.c：所有 L4 代理共用的流跟踪底座

## 1. 角色定位

`flow.c`（1279 行）实现"逻辑流"（flow）的跟踪：TCP 连接、TCP splice 连接、UDP 类连接、ICMP/ICMPv6 ping 序列，全部是 `flowtab[]` 里的表项。它把"识别一条流、决定它的目的地、建立 socket、挂进 epoll、周期性巡检、最终回收"这整条生命周期做成与协议无关的骨架，各协议模块只在 TYPED 状态之后填充自己的联合体字段。三个文件构成完整叙事：`flow.h` 定义状态机与 `flowside` 词汇；`flow_table.h` 定义 `union flow`（各协议连接结构的联合体表项）与全部内联访问器；`flow.c` 是实现。`pif.h` 的词汇表统一了接口概念——`PIF_TAP`（guest 侧 L2）、`PIF_HOST`（宿主 socket）、`PIF_SPLICE`（pasta 命名空间直连），一张流就是"从一个 pif 到另一个 pif"。

## 2. 内部结构

**状态机**（`flow.h:30-120` 的注释块是权威规格）：FREE → NEW（`flow_alloc()`）→ INI（`flow_initiate*()` 登记 INISIDE 五元组）→ TGT（`flow_target()` 判定目的地）→ TYPED（`FLOW_SET_TYPE()` 选定 FLOW_TCP/FLOW_UDP/...）→ ACTIVE（`FLOW_ACTIVATE()`）。每个状态精确列出"允许的操作/禁止的操作/陷阱"，最关键的陷阱：**NEW/INI/TGT/TYPED 任一时刻至多一个在途**（`flow.h:50-52`），所以 `flow_alloc()` 之后必须一口气走到 ACTIVE 才能回主循环——`flow_defer_handler()` 开头 `assert(!flow_new_entry)`（`flow.c:901`）就是这条不变量的运行时守卫。ACTIVE 态的流只能由协议自己的 defer/timer 回调返回 true 来终结。

**表分配：free cluster 链**（Theory of Operation，`flow.c:79-128`）。设计权衡写得非常清楚：全表扫描做周期性巡检，稀疏空洞浪费扫描时间；但完全紧凑化（删除时搬移表项）要同步改哈希表和 epoll 引用，太容易错。折中方案：**空闲簇**（连续空闲表项，首项存 `free.n` 长度与 `free.next` 下一簇索引，`flow.c:89-99`），簇间按索引严格递增串成链。`flow_alloc()`（`flow.c:606`）永远取链头簇的第一项——最低可用索引；簇长于 1 就从簇头切一项并前移 `flow_first_free`（`flow.c:625-636`），等于 1 就整簇消费跳 `next`（`flow.c:637-638`）。释放只允许两条路（`flow.c:109-121`）：`flow_alloc_cancel()`（`flow.c:651`）撤销最近一次分配——因为分配总在最低位，撤销后必然又成最低位，不变量自动保持，注释 `flow.c:663-665` 甚至明说"放回去成单元素簇就行，下次 defer 会顺手合并"；以及 `flow_defer_handler()` 扫表中按序归还——此时天然能正确重建簇链。扫描本身的复杂度是 `活跃连接数 + 空闲簇数`（`flow.c:123-127`），不是 FLOW_MAX。

**哈希索引**：`flow_hash()`（`flow.c:672-688`）用 SipHash（种子 `c->hash_secret`，来自 `random_init()`）对 flowside 的 oaddr/eaddr/oport/eport+proto+pif 混合——防外部流量哈希碰撞 DoS。表 `flow_hashtab[FLOW_HASH_SIZE]`（`flow.c:140`），负载因子 70%（`flow.c:136-137`），static_assert（`flow.c:142-143`）保证表容量 > 2×FLOW_MAX 以支撑安全线性探测。`flow_hash_remove()`（`flow.c:769`）实现了标准的 backward-shift 删除（`flow.c:781-793` 沿簇回扫，能落在洞里的就上移补位），避免线性探测的经典"删除断链"问题。`flowside_lookup()`（`flow.c:805`）探测时全字段比对；`flow_lookup_af()`/`flow_lookup_sa()`（`flow.c:835/857`）是给协议层的两个便捷包装（分别从裸地址/套接字地址构造查询键）。注意**每个流的两侧各自插入哈希**（`flow_hash_insert` 以 `flow_sidx_t` 为单位，sidx=流索引+侧号），tap 方向与 socket 方向都能 O(1) 查到同一条流。

**目的地判定**：`flow_target()`（`flow.c:505`）是转发规则的汇聚点。按 INISIDE 的 pif 分三路：PIF_TAP 走 `fwd_nat_from_tap()`（tap 进来的流量按 fwd 表 NAT/直通/回环）；PIF_SPLICE/PIF_HOST 必须命中规则（`assert(rule)`），分别走 `fwd_nat_from_splice()`/`fwd_nat_from_host()`，host 侧还要 `fwd_neigh_mac_get()` 查邻居 MAC（`flow.c:540`）。找不到目的地就报错撤销。

**socket 建立**：`flowside_sock_l4()`（`flow.c:215`）按 pif 分派——PIF_HOST 直接 `sock_l4()`（可选绑定出接口 `ip4/ip6.ifname_out`，环回地址则不绑，`flow.c:226-234`）；PIF_SPLICE 要 `NS_CALL()` 进目标命名空间再建（`flowside_sock_splice()`，`flow.c:194-204`）——splice 的两端 socket 分别活在两个 netns 里，这是 pasta 快路径的前提。`flowside_connect()`（`flow.c:253`）对称地按 flowside connect。

**巡检**：`flow_defer_handler()`（`flow.c:888`，由 `passt.c:117` 的 post_handler 每轮调用）两阶段：先 `flow_foreach` 逐类型调 `tcp_flow_defer`/`tcp_splice_flow_defer`/`udp_flow_defer`（timer 到期时再加 `icmp_ping_timer`/`udp_flow_timer`/`tcp_splice_timer`，`flow.c:896-932`）标记关闭者——注释 `flow.c:903-905` 解释为什么两阶段：`flow_foreach` 中途释放不安全；第二步才真正释放并重建簇链。类型到 epoll 的映射表 `flow_epoll[]`（`flow.c:58-64`）+ 三张 `static_assert` 锁死的字符串/协议映射表（`flow.c:26-66`）让加新流类型漏配直接编译失败。

## 3. 外部连接

依赖：`siphash.h`（密码学哈希）、`inany.h`（IPv4/IPv6 统一地址）、`fwd.c`（NAT 与转发规则）、`repair.h`/`serialise.h`（迁移时流的序列化）。被依赖：tcp.c/tcp_splice.c/udp_flow.c/icmp.c 四个协议模块各自持有 `union flow` 里的联合体槽位；`epoll_ctl.h` 的 `epoll_ref.flowside` 直接装 flow sidx（32 位），事件回流零查表；migrate.c 迁移时遍历全表挑 TCP 流。`flow_table.h:199-222` 导出的 `flow_alloc`/`flow_alloc_cancel`/`flow_target`/`FLOW_SET_TYPE`/`flow_activate` 是协议模块的标准 API 面。

## 4. 数据流

以 UDP 流首次发包为例：tap 来包 → `udp_tap_handler` 查 `flow_lookup_af(PIF_TAP)` 未命中 → `flow_alloc()` 取最低空闲位（NEW）→ `flow_initiate_af` 填 tap 侧 flowside（INI）→ `flow_target()` 经 `fwd_nat_from_tap` 得 PIF_HOST 目标（TGT）→ `FLOW_SET_TYPE(flow, FLOW_UDP)`（TYPED）→ udp 模块填自己的字段、`flowside_sock_l4` 建 socket、`flow_hash_insert` 两侧入哈希 → `FLOW_ACTIVATE()`（ACTIVE，`flow_new_entry` 清空）。此后同五元组包从任一侧来都一次哈希命中。流空闲到期时 `udp_flow_timer` 返回 true，下个 `flow_defer_handler` 周期它被标删、释放、簇链合并。

## 5. 设计决策

一是**零动态分配的全局纪律**：flow 表、哈希表、空闲簇元数据全部静态，配合 tcp.c 的静态缓冲，整个守护进程运行期无一次 malloc——头注释 `tcp.c:59` 把这列为安全目标，flow 表是这个纪律的地基。二是**"最低位分配+受限释放"替代完整紧凑化**（`flow.c:83-87`）：承认完全紧凑化的复杂度不可接受，转而用分配/释放次序的约束换取"表前部大体紧凑"的近似效果，扫描均摊成本可控。这正是宏注释里 "compromise" 一词的含义。三是**状态机即访问控制**：`flow.h:30-120` 每个状态列出的 Caveats（"其它字段不可读"）配合 `flow_set_state()` 的断言，把"哪些字段在哪个阶段已初始化"变成可断言的契约，从根上消灭联合体的野读。

## 6. 新人提示

加新流类型的清单：`flow.h` enum 加 FLOW_*、`flow_table.h` 的 `union flow` 加成员、`flow.c` 三张表（state_str/type_str/proto/epoll）各补一行（static_assert 会逼你）、`flow_defer_handler` switch 加 case。读代码先背 `flow.h:30-120` 的状态规格再打开 flow.c，否则断言会显得莫名其妙。两个易踩点：`flow_alloc()` 后的窗口里不能调任何可能回到主循环的东西（包括调其它会 `flow_alloc()` 的函数）；`flow_hash_remove` 的 backward-shift 是教科书算法，改动前先在纸上推一遍环回索引。调试：`flow_dbg` 的 "hash table insert/remove: bucket" 日志能完整还原哈希轨迹；FLOW_STATE 宏把状态打成人话。
