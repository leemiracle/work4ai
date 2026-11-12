# 09 元数据交换线：rdma_buffer_attr 协议与两个交换窗口

> 对应导览第 12 步（前半）「数据面双雄：交换」｜节点：`function:src/rdma_client.c:client_xchange_metadata_with_server`、`function:src/rdma_server.c:send_server_metadata_to_client`、`class:src/rdma_common.h:rdma_buffer_attr`

## ① 角色定位

RDMA 单边操作的前提是一道"门禁"：对端缓冲的**地址 + 长度 + 钥匙**三样东西不拿到手，网卡不知道往哪 DMA。本仓用一对函数把这场交接演完：客户端 `client_xchange_metadata_with_server`（`src/rdma_client.c:243-302`）先发后收，服务端 `send_server_metadata_to_client`（`src/rdma_server.c:277-357`）先收后发。线上跑的载荷是 16 字节的 `rdma_buffer_attr`（结构布局、packed 理由与 lkey/remote_stag 双视角已详第 02 篇，本篇不重讲）——本篇专讲**协议编排**：谁在什么窗口里挂什么缓冲、先发谁后发谁、length 字段如何兼职"容量协商"。常见讲法把要交换的内容说成"五元组"（addr/len/type/lkey/rkey），落到本仓源码是**三字段**：type 字段不存在（协议固定"单个缓冲、单一语义"，无需类型标签），lkey/rkey 共用一个 union 槽位（`src/rdma_common.h:64-69`）。

## ② 内部结构（协议的四拍）

**第 0 拍（窗口期，两拍之前就已发生）**：两端各预挂一个收货箱——服务端把 `client_metadata_attr` 注册成 MR 并 `ibv_post_recv`（`src/rdma_server.c:211-231`，发生在 `rdma_accept` **之前**）；客户端把 `server_metadata_attr` 注册并 post_recv（`src/rdma_client.c:179-196`，发生在 `rdma_connect` **之前**）。这一拍是第 07/08 篇讲过的"先备货后开门"，此处只强调：**收货箱在连接存在之前就已在 RQ 里排队**。

**第 1 拍，客户端发包**（`src/rdma_client.c:247-288`）：注册 src 缓冲（LOCAL_WRITE|REMOTE_READ|REMOTE_WRITE，`:250-252`）→ 把 MR 三元组写进 `client_metadata_attr`（`:258-260`）→ 给这个结构体本身再注册一个 MR（`:262-265`，元数据也是内存，上线前同样要注册）→ 填 SGE/WER（`:271-279`，opcode=`IBV_WR_SEND`、`IBV_SEND_SIGNALED`）→ `ibv_post_send`（`:281`）。

**第 2 拍，服务端收包+回包**（`src/rdma_server.c:286-348`）：收割第 0 拍预挂的 recv WC（`:286`，收到的正是客户端 16 字节）→ `show_rdma_buffer_attr` 打印（`:293`）→ **读 `client_metadata_attr.length` 当容量请求**，按它 `rdma_buffer_alloc` 服务端数据缓冲（`:294-302`，权限同样是三连 LOCAL|REMOTE_READ|REMOTE_WRITE）→ 填 `server_metadata_attr`（`:315-317`，此处塞的是 lkey，教学简化见第 02 篇勘误③）→ 注册元数据 MR（`:318-321`）→ `ibv_post_send` 发回（`:341`）。

**第 3 拍，客户端双收割**（`src/rdma_client.c:289-301`）：一次 `process_work_completion_events(..., 2)`（`:292-293`）同时等两个 WC——自己 SEND 的完成 + 服务端回包的 recv 完成；`ret != 2` 即失败（`:294`）。随后 `show_rdma_buffer_attr(&server_metadata_attr)`（`:300`）打出对端缓冲三件套——README 示例输出里那三行 `buffer attr, addr: 0x... , len: 10 , stag : 0x1617b400`（`README.md:40-42`）就是它。

## ③ 外部连接（图谱 calls 边）

- 两条 `rdma_buffer_register` 边挂在 `client_xchange_metadata_with_server` 下（`:247` src 缓冲、`:262` 元数据箱），一条挂在 `send_server_metadata_to_client` 下（`:298` alloc→register 内部、`:318` 元数据箱）——元数据线消耗了全仓 7 次注册中的 5 次，是**注册最密集的一段**。
- 双方各一条 `→ process_work_completion_events` 边：服务端两次单收割（`:286` 收、`:350` 发），客户端一次双收割（`:292`）——同一原语三种用法（第 5 篇）。
- 双方各一条 `→ show_rdma_buffer_attr` 边（`src/rdma_server.c:293`、`src/rdma_client.c:300`）：协议的"人肉抓包"端点，打印的正是线上那 16 字节的本地镜像。
- 交接面：拍完后客户端手里的 `server_metadata_attr.stag.remote_stag/.address` 被 `client_remote_memory_ops` 直接当 rkey/remote_addr 用（`:336-337, 367-368`）——本协议的全部产出就是这两个赋值的右手边。

## ④ 数据流（两个方向的线上旅程）

```
方向A 客户端→服务端（先）:
  client_metadata_attr[addr=src, len=strlen, stag=lkey]
    └─SEND─→ RC 流量 ─→ DMA 落进服务端预挂的 client_metadata_attr
              服务端 WC#1(:286) ─→ 读 length ─→ alloc(size=length)
方向B 服务端→客户端（后）:
  server_metadata_attr[addr=buf, len=length, stag=lkey]
    └─SEND─→ RC 流量 ─→ DMA 落进客户端预挂的 server_metadata_attr
              客户端 WC#send + WC#recv(:292) ─→ 交给数据面当 rkey/addr
```

注意两个方向各占**一个 RQ 空位、各产生一枚 WC**——双边 SEND/RECV 的成本双侧各付一次；对比数据面单边 WRITE/READ：只有发起方出 WR、对端零感知零消耗。本协议只在"授权建立"时用一次双边，之后数据面全单边，这个分工是 RDMA 编程的标准经济学。

## ⑤ 设计决策

- **length 兼职容量协商**：客户端没发"我想要多大缓冲"的独立请求，而是直接把 `strlen(src)` 塞进 attr.length（`:259`），服务端照单全收 `rdma_buffer_alloc(pd, client_metadata_attr.length, ...)`（`:298-299`，printf 也明说"The client has requested buffer length of" `:294`）。一发一收捎带完成协商——妙处是零额外报文，代价是服务端对 length 完全不设防（客户端发个 4GB 就 OOM 给你看，见⑥）。
- **客户端元数据"发而不用"**：服务端收下 client_metadata_attr 却只消费 length 字段，addr/stag 弃置——注释（`src/rdma_client.c:238-242`）自陈"shown here how to do it for the illustration purposes"：演示双向对称的交换姿势，本例的数据面只朝一个方向单边。理解这点就不会误以为服务端也要 RDMA READ 客户端。
- **为什么交换用 SEND 而不用第一次 WRITE**：单边 WRITE 需要事先知道对端地址+rkey——可这两样恰恰是要交换的内容。鸡生蛋问题只能用双边原语破：SEND 只要"对端挂了 recv 缓冲"即可送达，不需要地址钥匙。这就是 RDMA 世界"第一包必须双边"的公理。
- **客户端一次收割 2 个 WC 的巧妙**：SEND 完成与 RECV 到达在同一次通知窗口里到达的概率极高（RC 上这两件事本来就被对端 send 串行化），`:289-293` 注释明说期待 2 个——把两步等待合成一步，省一次 `ibv_get_cq_event` 往返。隐患是第 5 篇勘误①的忙等假设：若两枚 WC 不同批入队，do-while 会空转。

## ⑥ 新人提示（坑与勘误）

1. **交换窗口 = "accept/connect 之前 post_recv"**：两个收货箱的 post_recv 都发生在连接建立前（服务端 `:229`→accept `:244`；客户端 `:194`→connect `:215`）。把 post_recv 挪到 ESTABLISHED 之后就成了竞速：对端 SEND 若先到，RQ 空 → RNR 错误（RC 下重试几次后连接报错）。"先备货后开门"是协议级纪律，不是性能优化。
2. **收货箱尺寸两端编译期对齐**：双方 post 的 SGE length 都是 `sizeof(rdma_buffer_attr)`（`:223`、`:188`，经 MR->length 间接而来）。这依赖两端链接同一份头文件；若两端各自改结构体（哪怕加一个字段），服务端 SEND 超长会被截/错——16 字节全靠 packed 钉死（第 02 篇），升级协议必须两端同步换二进制。
3. **协议裸奔三连**：无魔数、无版本号、无字节序转换——`address` 是 uint64_t 原样上线，两端一台 x86 一台大端机（历史上 POWER 时代的 RDMA 卡真实存在）就会拿到字节序颠倒的地址。跨机部署自研协议请补 `htobe64/be64toh`。
4. **rkey 语义留了个洞**（承接第 02 篇勘误③）：`:317` 发出去的是 `server_buffer_mr->lkey`，客户端当 rkey 用（`:336`）多数 provider 数值恰好相等所以能跑；严谨实现发 `mr->rkey`。另注意服务端数据缓冲注册时**给了 REMOTE_READ|REMOTE_WRITE**（`:300-302`），没这两面旗，rkey 再对网卡也会拒单边访问。
5. **`server_metadata_mr` 与 `server_metadata_attr` 是两个东西**：前者是 16 字节收货箱自己的 MR（`:179-182`），后者将来装的是**服务端数据缓冲**的三元组（`:300` 打印的 attr）。名字只差一个后缀，初读极易混淆——记住"attr 是信，mr 是信封"。
6. **show_rdma_buffer_attr 打的是本地镜像不是线上原文**：它读的是收货箱结构体（DMA 已落位），若要抓"线上到底发了什么"，得在两端 printf 之间对时间轴——教学仓没有抓包钩子，理解全靠这对镜像打印。

——16 字节落位后，单向门全部打开；下一篇暂缓数据面（第 12 步后半的单边操作归入 verbs 速查与对照篇），先讲全剧最后一幕的固定动作：怎么把这一摊资源干净地拆掉。
