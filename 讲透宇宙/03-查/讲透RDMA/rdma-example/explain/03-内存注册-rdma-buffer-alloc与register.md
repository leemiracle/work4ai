# 03 内存注册：rdma_buffer_alloc 与 rdma_buffer_register

> 对应导览第 3 步「内存注册：RDMA 第一课」｜节点：`file:src/rdma_common.c`、`function:rdma_buffer_alloc`、`function:rdma_buffer_register`

## ① 角色定位

RDMA 第一课：**网卡只能读写注册过的内存**。任何缓冲（发送源、接收落点、被单边操作的目标）在进入数据面之前都必须先 `ibv_reg_mr` 注册成 Memory Region（MR），MR 同时携带本地钥匙 lkey 与远端钥匙 rkey。`rdma_common.c` 是全仓公共实现层（图谱第 3 层「内存注册底座」5 节点中的 3 个在本篇：文件节点 + alloc + register），被 CMake 同时编进两个 target（第 1 篇已述）。alloc 与 register 这对函数是"分配"与"注册"两个正交动作的两种打包：前者分配+注册一步到位，后者只注册调用方已有的内存——全仓 7 个 MR 全部经它们产生。

## ② 内部结构

**`rdma_buffer_alloc(pd, size, permission)`**（`src/rdma_common.c:40-59`）四步：
1. pd 判空（`:44-47`）——PD 是注册的归属域，NULL 直接打回。
2. `calloc(1, size)`（`:48`）——注意用 calloc 非 malloc，缓冲零初始化；失败报 `-ENOMEM` 风格消息（`:49-52`）。
3. 委托 `rdma_buffer_register(pd, buf, size, permission)`（`:54`）——alloc 的注册部分完全复用 register。
4. 失败兜底：注册失败时 `free(buf)`（`:55-57`）——内存不泄漏，alloc 要么返回可用 MR 要么干净失败。

**`rdma_buffer_register(pd, addr, length, permission)`**（`src/rdma_common.c:61-80`）三步：
1. pd 判空（`:66-69`）。
2. `ibv_reg_mr(pd, addr, length, permission)`（`:70`）——唯一一行真 verbs 调用；失败返回 NULL 并打印 `-errno`（`:71-74`）。
3. 成功路径 debug 打印 `mr->addr / mr->length / mr->lkey`（`:75-78`），返回 mr。

两个函数共用 `permission` 参数（`enum ibv_access_flags` 的按位或），把"授什么权"的决定权完全交给调用方。

## ③ 外部连接（图谱 calls 边）

register 的 5 条直接调用边 + alloc 的 1 条（权重 0.8）：

| 调用方 | 边 | 现场位置 | 权限组合 |
|---|---|---|---|
| 服务端 `accept_client_connection` | →register | `src/rdma_server.c:211-214` | LOCAL_WRITE（收客户端元数据） |
| 服务端 `send_server_metadata_to_client` | →alloc | `src/rdma_server.c:298-302` | LOCAL_WRITE\|REMOTE_READ\|REMOTE_WRITE（数据缓冲） |
| 服务端 `send_server_metadata_to_client` | →register | `src/rdma_server.c:318-321` | LOCAL_WRITE（元数据结构本身） |
| 客户端 `client_pre_post_recv_buffer` | →register | `src/rdma_client.c:179-182` | LOCAL_WRITE（收服务端元数据） |
| 客户端 `client_xchange_metadata_with_server` | →register ×2 | `src/rdma_client.c:247-252, 262-265` | src 缓冲加 REMOTE 位；元数据仅 LOCAL |
| 客户端 `client_remote_memory_ops` | →register | `src/rdma_client.c:313-318` | dst 缓冲 LOCAL\|REMOTE_* |

规律清晰：**元数据缓冲只要 LOCAL_WRITE（自己收/发用 lkey），数据缓冲加 REMOTE_READ/WRITE（授权对端单边访问用 rkey）**。alloc 全仓只有一个用户——服务端数据缓冲，因为只有它是"先有尺寸需求、再要新内存"的场景。

## ④ 数据流

以服务端 `rdma_buffer_alloc(pd, client_metadata_attr.length, ...)`（`src/rdma_server.c:298`）为例走一遍内部旅程：

1. calloc 拿到一段普通用户态虚拟内存（此时网卡完全不认识它）。
2. `ibv_reg_mr` 进入 libibverbs 用户态库 → 驱动进入内核：把这段虚拟内存对应的物理页**钉住（pin）**——登记进网卡的可访问映射表，之后内核不再迁移/换出这些页。
3. 网卡据此获得"虚拟地址→物理地址"的直接翻译能力，后续 DMA 不经内核。
4. 返回的 `struct ibv_mr` 携带 `addr/length/lkey/rkey` 四元组：lkey 供本端 post WR 时填 SGE（如 `src/rdma_server.c:222-224`），rkey 供对端单边操作（经第 2 篇的元数据交换过线）。
5. 之后该缓冲参与的每次收/发，WR 的 SGE 都必须带这个 lkey——网卡硬件会用它校验"你确实有权 DMA 这块内存"。

## ⑤ 设计决策

- **为什么要 pin**：RDMA 的本质承诺是网卡异步 DMA、内核不介入。DMA 进行中若页框被内核迁走，网卡会写/读到废内存——注册即锁定物理页，这是 RDMA 性能与安全模型的基座。
- **为什么拆成 alloc/register 两个函数**：本仓恰好用到两种内存来源——"新分配的匿名缓冲"（服务端数据缓冲、用 alloc）与"已存在的具名内存"（两端的 `*_metadata_attr` 全局结构体，`src/rdma_server.c:211` 直接 register 其地址；客户端 `src/rdma_client.c:247` 的 src 字符串同理）。后者的 free 责任在调用方（全局生命周期=进程生命周期），若走 alloc 语义会被错误地 free——API 的分立对应内存所有权的分立。
- **为什么权限由调用方传**：最小授权原则的结构化表达。对比同一函数服务的两个场景（元数据仅 LOCAL vs 数据缓冲全开）就知道：库层不替你决定授权范围。
- **errno 负号打印习惯**：`-errno`（`src/rdma_common.c:50,72`）把正 errno 显示成负数，与内核风格返回值一致，纯属作者风格统一。

## ⑥ 新人提示（坑与勘误）

1. **ibv_reg_mr 失败返回 NULL 而非 -1**：判断只能 `if (!mr)`，errno 要在返回后立刻读（`:72`）——中间任何库调用都可能覆盖它。
2. **注册成本不便宜**：pin 页+建映射是重操作，真实系统（NCCL、KVCache 层）用 MR 池/大块注册+切窗复用；教学仓每缓冲一次 register，别照搬到生产。
3. **debug 打印的是 lkey 不是 rkey**（`src/rdma_common.c:78`）：排查"对端单边操作失败"时日志里看不到 rkey——结合第 2 篇勘误③（本例 rkey==lkey 才成立）一起理解。
4. **权限漏设的症状在对端**：若服务端数据缓冲忘了 `IBV_ACCESS_REMOTE_WRITE`（`src/rdma_server.c:300-302` 少一个位），报错不在服务端——客户端的 RDMA WRITE 会在**服务端**产生 local protection error，并通过 CQ 状态回传到客户端 WC（第 5 篇的 WC 校验捕获），跨端归因是新手最常见的迷惑点。
5. alloc 失败路径的 `free(buf)`（`:55-57`）是本仓少见的精细善后——对比 `src/rdma_server.c:7` 的 TODO 注释（"error condition 时不清理已分配资源"），两端代码的错误路径大量直接 return，教学仓明确放弃了错误清理完整性，读代码时别学这部分。

——MR 有了，下一站是它的终点站：deregister 与 free（导览第 4 步）。
