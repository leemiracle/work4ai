# 06 地址解析与调试打印：get_addr 与 show 族

> 对应导览第 6 步「地址解析与调试打印」｜节点：`function:src/rdma_common.c:get_addr`、`show_rdma_cmid`、`show_rdma_buffer_attr`

## ① 角色定位

公共层 `rdma_common.c` 的最后三个函数，图谱第 5 层「地址解析与调试辅助」全层即此三节点。角色分两类：`get_addr` 是**功能性辅助**——把 `-a` 参数（IP 或主机名）翻译成 `sockaddr`，是 CM 侧 bind/resolve 的寻址入口，两端 main 都依赖它；`show_rdma_cmid` 与 `show_rdma_buffer_attr` 是**教学性辅助**——把 opaque 的 cm_id 与元数据结构打印成人可核对的三元组，是验证"元数据交换是否正确"的最小工具。它们不参与数据面，但初学者第一次跑通程序时，确认"两端看到同一份缓冲属性"靠的就是 show 输出。

## ② 内部结构

**`get_addr(dst, addr)`**（`src/rdma_common.c:197-209`，`:196` 注释致谢 librdmacm 的 rping.c 示例）四步：
1. `getaddrinfo(dst, NULL, NULL, &res)`（`:201`）——service 传 NULL，只解析主机名到地址，不解析端口；同时接受点分 IP 与 DNS 主机名。
2. 失败报"invalid hostname or IP address"（`:202-204`）并**原样返回 getaddrinfo 的错误码**（EAI_* 系列，非 errno）。
3. `memcpy(addr, res->ai_addr, sizeof(struct sockaddr_in))`（`:206`）——把解析结果按 IPv4 结构体定长拷进调用方缓冲。
4. `freeaddrinfo(res)`（`:207`）归还链表，返回 ret（成功时为 0）。

**`show_rdma_cmid(id)`**（`src/rdma_common.c:10-25`）：判空后依次打印 cm_id 指针、`id->verbs` 设备上下文与设备名（`:17-19`，双重判空防野指针）、事件通道（`:20-21`）、QP 指针/port_space/port_num（`:22-24`）——一个 cm_id 背后的资源五联单。

**`show_rdma_buffer_attr(attr)`**（`src/rdma_common.c:27-38`）：判空后用两条分隔线（`:32,37`）夹住一行核心三元组 `addr / len / stag`（`:33-36`）——注意取的是 `attr->stag.local_stag` 字段名（联合体的"本端视角"分支，见第 2 篇）。

## ③ 外部连接（图谱 calls 边）

- `client main → get_addr`：现场 `src/rdma_client.c:494`，解析 `-a` 参数。
- `server main → get_addr`：现场 `src/rdma_server.c:444`，同理。
- `server send_server_metadata_to_client → show_rdma_buffer_attr`：现场 `src/rdma_server.c:293`，打印**收到的客户端**元数据。
- `client client_xchange_metadata_with_server → show_rdma_buffer_attr`：现场 `src/rdma_client.c:300`，打印**收到的服务端**元数据——README 示例输出里 `buffer attr, addr: 0x5629832e22c0 , len: 10 , stag : 0x1617b400`（`README.md:41`）正是这一行打的。
- **`show_rdma_cmid`：零调用方**。图谱与源码双向核实（grep 全仓仅 `src/rdma_common.c:10` 定义、`:131` 原型声明），它是"死导出"——写好了备着、从未被用，属于教学库常见残留（头文件原型 `src/rdma_common.h:131` 同样无消费者）。

## ④ 数据流

get_addr 的产出如何流入 CM：客户端 `-a 10.0.0.2` → getopt（`src/rdma_client.c:472`）→ get_addr 填好 `server_sockaddr` → `rdma_resolve_addr(cm_client_id, NULL, s_addr, 2000)`（`src/rdma_client.c:61`）以它为目的地址启动连接；服务端 `-a` 的结果喂给 `rdma_bind_addr`（`src/rdma_server.c:149`）决定监听地址。两端 main 还各自兜底：客户端无 `-a` 时默认 `INADDR_LOOPBACK`（`src/rdma_client.c:468`），服务端默认 `INADDR_ANY`（`src/rdma_server.c:438`）；端口无 `-p` 时统一回落 `DEFAULT_RDMA_PORT`（client `:509-512`、server `:459-462`）。

show 族的产出则是**日志流**：服务端 accept 后先收元数据再打印（`src/rdma_server.c:286→293`），客户端交换完成后打印（`:300`）——两端各打一次对端的 buffer attr，肉眼比对即确认第 2 篇的 16 字节线格式交换成功。

## ⑤ 设计决策

- **为什么用 getaddrinfo 而非 inet_pton**：getaddrinfo 同时接受主机名与 IP、协议无关，且是 POSIX 推荐接口；inet_pton 只认 IP 串。教学仓用 `-a server1.example.com` 也能跑。
- **为什么 service 传 NULL**：端口由 `-p`/默认值单独管理（main 里 strtol→htons），地址解析与端口解析解耦——代价见⑥-1 的覆盖坑。
- **为什么 memcpy 定长 sockaddr_in**：getaddrinfo 返回的是通用 `sockaddr*`，而 CM API（rdma_bind_addr/rdma_resolve_addr）要的就是它；按 IPv4 结构体定长拷贝最简单，代价是 IPv6 结果被截断（本仓 RDMA_PS_TCP + IPv4 教学定位可接受）。
- **show 族为什么保留在库层**：打印 cm_id 涉及 verbs 设备上下文的嵌套指针（`id->verbs->device->name`），新手最容易在这里解引用出野指针——库层代劳双重判空（`:12,17`）后打印，是安全的自查样板。

## ⑥ 新人提示（坑与勘误）

1. **get_addr 会连端口一起覆盖（最大的坑）**：`:206` 的 memcpy 整个 `sockaddr_in`，而 getaddrinfo 的结果里 `sin_port=0`（service 传了 NULL）。于是命令行 `-p 12345 -a 10.0.0.2`（p 在前 a 在后）时，get_addr 把 12345 清零，随后 main 的"端口为 0 则回落默认"兜底（`src/rdma_client.c:509-512`）把端口悄悄改成 20886——服务端根本不在 12345 上监听。`-a` 的 case 注释"Remember, this will overwrite the port info"（`src/rdma_server.c:443`、`src/rdma_client.c:493`）说的正是此事，但初读极易误以为是"覆盖地址信息"。规避：**要么先 -a 后 -p，要么改 get_addr 只拷 sin_addr**。
2. **getaddrinfo 错误码不是 errno**：失败返回 EAI_NONAME 之类（`:201-204` 原样透传），用 perror/strerror 打不出有意义的消息——本仓的报错文案干脆不带码，调试时记得用 gai_strerror。
3. **show_rdma_cmid 是死代码**：全仓无调用方（见③），复刻本仓做自己的项目时可以直接删，或留作调试垫片。
4. **show_rdma_buffer_attr 的字段名骗人**：打印统一走 `stag.local_stag`（`src/rdma_common.c:36`），但客户端打印收到的服务端属性时（`src/rdma_client.c:300`），这个值语义上是 remote_stag/rkey——同一段输出在两端语义不同（第 2 篇 union 双视角的副作用），读日志时以"谁打印的"判断含义。
5. **打印的是原始指针值**：`addr: 0x5629832e22c0`（README:41）是服务端进程的虚拟地址，在客户端机器上无意义——它只用于核对"交换前后数值未变"以及喂给 RDMA READ/WRITE 的 remote_addr（`src/rdma_client.c:337`），别拿它在自己进程里解引用。

——公共层 9 函数至此讲完。从下一篇（导览第 7 步）起进入服务端链路：start_rdma_server 如何把监听立起来。
