# 02 rdma_common.h：三个 .c 的公共契约与元数据线格式

> 对应导览第 2 步「公共契约：头文件与元数据协议」｜节点：`file:src/rdma_common.h`、`class:src/rdma_common.h:rdma_buffer_attr`

## ① 角色定位

`rdma_common.h` 是全仓唯一的头文件、三个 .c 文件唯一的公共依赖——图谱里 3 条 `imports` 边全部指向它（rdma_client.c / rdma_common.c / rdma_server.c → rdma_common.h），它同时是图谱 13 条 `exports` 边的契约面：`rdma_common.c` 的 9 个函数全部经此头对外声明。它承载三类契约：**宏契约**（rdma_error/debug）、**参数契约**（CQ_CAPACITY 等四个常量，两端编译时取同一值）、**数据契约**（`rdma_buffer_attr` 结构——两端唯一在线上交换的非内置数据结构）。对这个 133 行的文件理解到什么程度，决定了后面读两端代码时要不要反复回头查签名。

## ② 内部结构

逐块讲：

- **错误宏 `rdma_error`**（`src/rdma_common.h:30-32`）：`do{fprintf(stderr,"%s : %d : ERROR : "msg, __FILE__, __LINE__, ##args);}while(0)`——自动带文件名行号，`do-while(0)` 包裹保证宏在 `if/else` 里当单语句用；注意它只打印**不退出**，失败后控制流继续走。
- **调试宏 `debug`**（`src/rdma_common.h:34-44`）：`#ifdef ACN_RDMA_DEBUG` 双态定义，未定义时展开为空——全仓几十处 debug() 在默认构建里一个字节都不产生。
- **四个常量**（`src/rdma_common.h:47-53`）：`CQ_CAPACITY 16`（完成队列容量）、`MAX_SGE 2`（每个 WR 最多分散聚集元素数）、`MAX_WR 8`（QP 收/发队列各容纳的 WR 数）、`DEFAULT_RDMA_PORT 20886`（默认端口，README 示例输出里 `port: 20886` 即它）。两端 `ibv_create_cq`/`qp_init_attr.cap` 都引用它们，保证对端协商时容量参数一致。
- **线格式 `struct rdma_buffer_attr`**（`src/rdma_common.h:61-70`）：`__attribute((packed))` 紧凑布局，三字段 `uint64_t address` + `uint32_t length` + `union stag{local_stag, remote_stag}`，合计恰好 16 字节。这是两端交换"我的缓冲在哪、多大、用什么钥匙"的三元组。
- **9 个函数原型**（`src/rdma_common.h:72-131`）：get_addr / show_rdma_buffer_attr / process_rdma_cm_event / rdma_buffer_alloc / rdma_buffer_free / rdma_buffer_register / rdma_buffer_deregister / process_work_completion_events / show_rdma_cmid，注释里带参数语义说明，是后续 4 篇的目录。

## ③ 外部连接

- 3 条 `imports` 边把三个 .c 挂到本头：rdma_client.c、rdma_common.c、rdma_server.c 各自第一件事就是 `#include "rdma_common.h"`（如 `src/rdma_server.c:10`）。
- `rdma_buffer_attr` 作为 `class:` 节点被头文件 `contains`——全仓仅此一个结构体享有独立节点，因为它是跨进程数据结构的唯一代表。
- 它的两个"实例锚点"在两端全局区：服务端 `client_metadata_attr/server_metadata_attr`（`src/rdma_server.c:23`）、客户端同名对（`src/rdma_client.c:23`）。这些全局实例就是元数据落点，注册 MR 时直接取它们的地址（`src/rdma_server.c:211-214`、`src/rdma_client.c:179-182`）。
- 头文件聚合的内核/库依赖（`src/rdma_common.h:21-27`）：netdb/inet 系列支撑 get_addr，`rdma/rdma_cma.h` 支撑 CM API，`infiniband/verbs.h` 支撑 ibverbs API——三个 .c 自己不再 include 任何系统头。

## ④ 数据流

跟随 `rdma_buffer_attr` 走一次完整的线旅程（这是理解第 12 步单边操作的钥匙）：

1. 服务端分配数据缓冲后，把 MR 的三元组填进本地实例（`src/rdma_server.c:315-317`）：`address=server_buffer_mr->addr`、`length=mr->length`、**`stag.local_stag = mr->lkey`**——发送方视角叫 local_stag。
2. 该结构体整体注册成 MR、经 `IBV_WR_SEND` 发出（`src/rdma_server.c:331-341`），16 字节裸字节流过线。
3. 客户端预挂的 receive 缓冲恰好是它自己的 `server_metadata_attr`（`src/rdma_client.c:179-196`），硬件 DMA 把 16 字节直接落进去——**同一个联合体，接收方读的字段名换成 `stag.remote_stag`**（`src/rdma_client.c:336` 取 `server_metadata_attr.stag.remote_stag` 当 rkey 用）。
4. 客户端随后发起 RDMA WRITE/READ 时，`wr.rdma.rkey=remote_stag`、`wr.rdma.remote_addr=attr.address`（`src/rdma_client.c:336-337`）——元数据交换的全部意义就是把这两个值交到对端手里。

## ⑤ 设计决策

- **为什么 packed**：这是"线格式"不是内存结构——若不 packed，编译器会在 8 字节对齐的 `address` 之后给 `length+stag` 区段补 4 字节尾垫（8+4+4→24 字节布局随 ABI 漂移），两端编译器不同就可能错位。packed 把布局钉死为 16 字节，注释直接给了 GCC 文档链接（`src/rdma_common.h:55-60`）。
- **为什么 union 双命名**：同一个 32bit key，本端发出去时它是"我的本地 stag"，对端收到后它是"访问我的远程 stag"——union 不占空间却把两种视角写进类型系统，是极佳的教学命名法。
- **为什么常量集中放头文件**：CQ/QP 容量是两端必须一致的协商参数，放头文件让三个 .c 编译期共享，避免两端各写一份魔数漂移。

## ⑥ 新人提示（坑与勘误）

1. **debug 宏默认全灭**：启用要 `-DACN_RDMA_DEBUG`，但 CMakeLists.txt 通篇没有 `add_definitions(-DACN_RDMA_DEBUG)`——想看 debug 输出得手工 `cmake . -DCMAKE_C_FLAGS=-DACN_RDMA_DEBUG`（注意是 C_FLAGS，理由见第 1 篇勘误①）。
2. **`__attribute` 拼写**（`src/rdma_common.h:61`）：GCC 双下划线标准拼法是 `__attribute__`，单下划线版 GCC 同样接受，但非 GCC 系编译器（MSVC 等）两者都不认——教学仓可接受，移植时注意。
3. **本例发的是 lkey 不是 rkey**：`src/rdma_server.c:317` 塞进 `local_stag` 的是 `mr->lkey`，而客户端拿它当 rkey 做单边操作。多数 provider 上同一 MR 的 rkey 与 lkey 数值相同（rkey 由 lkey 派生），示例因此能跑；但 API 语义上授权远端应使用 `mr->rkey`——严谨复刻时建议改发 rkey，并理解示例这里做了简化。
4. 校验线格式最简单的办法：两端各 `sizeof(struct rdma_buffer_attr)`，都应得 16；若得 24 说明 packed 没生效。
5. `rdma_error` 宏字符串拼接用法 `rdma_error("xx %d\n", v)` 中格式串末尾要自带 `\n`——宏体内不补换行，忘了会与下一条错误输出粘行。

——本篇的 `rdma_buffer_attr` 是第 12 步"数据面双雄"的入场券；下一篇进入它的前置条件：让缓冲合法地进入数据面（内存注册）。
