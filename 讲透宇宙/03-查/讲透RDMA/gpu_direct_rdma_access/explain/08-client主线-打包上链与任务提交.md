# 08 client 主线：凭据打包上链与任务提交链

> 对应 tour 第 10 步「client 发起：显存注册与描述串打包上链」+ 第 11 步的触发半边。源码锚均对 HEAD `a99d506` 核实。

## 一、角色定位

client.c（466 行，两个 main 中较长者）是整个 demo 的甲方：按 `-u BDF` 选卡分配（默认 CPU 的）工作缓冲、注册成 MR、把"远端可达凭据"序列化发给 server，然后每轮发一个触发包、等一个回执。最容易误解的一点是：**client 进程从头到尾不调用任何 RDMA 数据面动词**——`rdma_submit_task`/`rdma_poll_completions` 都在 server 进程里跑（server.c:370、380）。client 的 CQ 里安静得没有一朵 CQE，它只是把靶子立好、把箭（触发包）递过去。"GPU Direct" 的 GPU 侧反而没有任何 RDMA 活动，这是 DC 模型"目标无连接"的直接后果（第 9 篇）。

第 1 篇的数据流四步里，本篇吃下第 2 步（凭据上链）的全部细节，并顺着触发包落到 server 后进入库内 `rdma_submit_task`（gpu_direct_rdma_access.c:1342）的前半段——解析、校验、AH 缓存，最后把接力棒交给 `rdma_exec_task`（第 10 篇）。

## 二、内部结构

main（client.c:302-466）分段：

| 段 | 行锚 | 内容 |
|---|---|---|
| 参数 | client.c:313-326 | parse + hostaddr 强制检查 |
| 连接 | client.c:328-335 | open_client_socket 三次握手 |
| 设备与缓冲 | client.c:337-366 | open_device_client→work_buffer_alloc→buffer_reg |
| 凭据组装 | client.c:368-398 | 两个 desc_str → 两次 pack 拼一个 package |
| 迭代循环 | client.c:410-437 | write 触发包 → recv ack |
| 清理链 | client.c:445-465 | 六级 goto 逆序 |

文件私有的打包件是本篇主角：`enum payload_t`（client.c:123）定义两类载荷——RDMA_BUF_DESC（缓冲凭据串）与 TASK_ATTRS（任务标志串）；`struct payload_attr`（client.c:125-128）就是类型+字符串的二元组；`pack_payload_data`（client.c:144-159）执行三段 memcpy：1 字节 type、2 字节 size、size 字节 payload（含 NUL，client.c:147）。函数头的 ASCII 图（client.c:140）钉死了线上格式：`PACKAGE = {|type|size|---------payload----------|}`——一个自描述的长度前缀协议，TCP 流上无粘包歧义，server 侧的 recv 镜像解析（server.c:313-340）。

另一半是 `rdma_task_attr_flags_get_desc_str`（client.c:175-186）：把 32 位 flags 格式化成 `"%08x"`（client.c:183），定长 8 字符 + NUL 共 9 字节——任务方向（WRITE/READ）就这样以文本形式上了链。

## 三、外部连接

client 依赖链五件：`open_client_socket`（client.c:78-121，getaddrinfo 解析 servername 后循环 connect，失败换下一个地址族）、`rdma_open_device_client`（client.c:338，DCT 设备，第 9 篇）、`work_buffer_alloc`（client.c:347，GPU/CPU 分派，第 3 篇）、`rdma_buffer_reg`（client.c:362，第 5 篇）、`rdma_buffer_get_desc_str`（client.c:370）——后者把 GID/rkey/地址/大小/LID/DCTN/is_global 序列化成七段冒号串（格式化在 gpu_direct_rdma_access.c:1251-1257），这是 wire 协议的编码半边（第 4 篇有字段表）。

触发包落地后，server 调 `rdma_submit_task`（gpu_direct_rdma_access.c:1342-1419），其前半段是本篇的"下游接力"：

1. 拷贝本地侧五字段进 exec_params（client.c 视角是远端，server 视角是本地缓冲，gpu_direct_rdma_access.c:1350-1356）；
2. `sscanf` 六段解出远端 addr/size/rkey/lid/dctn/is_global（gpu_direct_rdma_access.c:1363-1366），is_global 时 `wire_gid_to_gid` 把冒号分组十六进制逐 32 位 ntohl 还原（gpu_direct_rdma_access.c:1215-1227、:1369）；
3. 按 `remote_buf_offset` 平移远端地址并缩尺寸（gpu_direct_rdma_access.c:1381-1382）；
4. **仅 debug 模式**做 buff_size_validation 尺寸对账（gpu_direct_rdma_access.c:1388-1395，注释言明快路径交给硬件报错）；
5. 组 ah_attr（RoCE 时填 dgid/sgid_index/hop_limit/traffic_class，gpu_direct_rdma_access.c:1399-1411），走 `rdma_create_ah_cached` 查 khash 缓存（gpu_direct_rdma_access.c:1413，第 6 篇）；
6. 进 `rdma_exec_task`（gpu_direct_rdma_access.c:1416，第 10 篇）。

## 四、数据流

凭据的生产与消费闭环：

- **一次组装**：desc_str（client.c:370，栈上 256 字节）与 task_opt_str（client.c:371，16 字节）在循环外生成；package 按精确公式分配 `(ret_desc_str_size + ret_task_opt_str_size) + 2*sizeof(uint16_t) + 2*sizeof(uint8_t)`（client.c:379）并 memset 清零（client.c:381）；两次 `pack_payload_data` 头尾相接拼进同一 buffer（client.c:385、394）。
- **每轮一写一读**：`write(sockfd, package, buff_package_size)` 发触发（client.c:417），`recv(sockfd, ackmsg, sizeof ackmsg, MSG_WAITALL)` 等回执（client.c:425）——注意 `buff_package_size` 是两次打包的累计值（client.c:394 的 `+=`），两段包一次 syscall 发完。
- **ack 定长对账**：两侧都用 `sizeof ACK_MSG`=20 字节（client.c:412 vs server.c:399），短读即失败。
- **调试窥视**：`if (!usr_par.use_cuda)` 才打印缓冲内容（client.c:434-436）——显存指针不可解引用，第 1 篇坑 3 的防线。

## 五、设计决策

- **凭据复用**：desc_str/task_opt_str/package 全在循环外组装，循环体只剩一次 write + 一次 recv。真实存储场景里"一次注册、多次传输"正是 MR/rkey 的设计意图，demo 把这一点做成了形状。
- **方向语义的双视角命名**：usage 文案 `-t` 位 0：0=WRITE（默认）、1=READ（client.c:194-195，解析在 client.c:237 只取 bit0）；而库内选动词的注释恰好反写——`ibv_wr_rdma_read // client wants to send data to the server`（gpu_direct_rdma_access.c:899-901）。两处都没错：verbs 视角（server 执行 READ）与数据流视角（client 的数据流向 server）互为镜像，读代码时必须先站好队再读方向词。
- **offset 语义留给库**：`remote_buf_offset` 字段在 client/server 两边都不填（server memset 后未设，server.c:343），恒为 0；但库仍实现了平移逻辑（gpu_direct_rdma_access.c:1381-1382）——API 能力超出 demo 用量，第 4 篇契约里它是对外承诺的一部分。
- **BDF 即用即弃**：`-u` 参数解析时 strdup（client.c:262-267），work_buffer_alloc 用完立即 free 并置 NULL（client.c:354-357）——clean_usr_par 兜底的 `if (usr_par.bdf)`（client.c:461）因此不会双 free。小处见卫生。
- **parse 失败也走清理**：client.c:313-319 注释明说"可能已有部分内存分配成功"，失败 goto clean_usr_par 而非直接 return——两个 main 里唯一带语义的提前出口。

## 六、新人提示

1. **别在 client 里找 CQ 轮询**：submit/poll 都是 server 侧动作，client 的"完成通知"是 TCP ack。grep `ibv_poll` 只会命中 gpu_direct_rdma_access.c 与 server.c。
2. **-a 只支持 IPv4，且是真陷阱**：usage 写明 "ipaddr v4 (mandatory)"（client.c:196），但 utils.c:58 的 `memcpy(addr, res->ai_addr, sizeof(struct sockaddr_in6))` 在 IPv6 解析结果下会向 16 字节的 `struct sockaddr hostaddr`（client.c:70）**溢出写 28 字节**——防御只靠文档，传 IPv6 地址不是"不支持"而是静默栈破坏。
3. **package 布局手工对账**：想抓包看协议时，记住两段 package 是背靠背的：`|0|len_lo len_hi|desc...\0|1|len_lo len_hi|flags...\0|`，uint16 size 未显式 htonl——同构机器间的 demo 假设，跨端序环境直接错位。
4. **task_opt_str 定长 8 字符**：`%08x` 保证前导零（client.c:183），server 侧 `sscanf(t, "%08x", &flags)`（server.c:337）对定长信任——若手改协议去掉前导零，长度对账（pl_size）仍过，内容语义不变，但定长假设就该守住。
5. **servername 是位置参数**：必须在所有选项之后单独给一个（client.c:281-297：optind==argc 报缺失、argv[optind] 取值、多给报 usage）——README 示例 `./client -t 0 -a ... 172.172.1.34 -u ...`（README.md:88）里那串裸 IP 就是它。
