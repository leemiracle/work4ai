# 07 server 主线：就位、CPU 缓冲与持久监听

> 对应 tour 第 9 步「server 就位：TCP 婚介与命令行」。源码锚均对 HEAD `a99d506` 核实。

## 一、角色定位

server.c 是两个 main 里更"重业务感"的一个（427 行），扮演 README 所说的"file storage simulation"（README.md:2）。但读代码前先破除一个预期：它没有任何文件 I/O，"存储后端"只是叙事外衣——实际就是一个分配在 CPU 内存上的普通缓冲（server.c:263 注释明说 "On the server side, we allocate buffer on CPU and not on GPU"）。它的真实职责是当**RDMA 动词的发起方**：接收 client 经 TCP 发来的远端缓冲凭据，然后用本侧 DCI QP 把本地缓冲数据直写（或直读）client 的 GPU/CPU 缓冲。第 1 篇说过"client 是靶、server 是弓"，本篇讲弓的就位与每一次放箭的节奏。

它同时是全仓唯一持有两条生命周期线的角色：单连接的迭代循环，与 `-P` 持久模式下的"服务完一个再等下一个"外循环（server.c:414-415）——这条外循环也是错误恢复路径 `rdma_reset_device` 的唯一触发场景（详见第 11 篇）。

## 二、内部结构

main（server.c:239-427）按职责切四段：

| 段 | 行锚 | 内容 |
|---|---|---|
| 就位 | server.c:249-288 | parse_command_line→rdma_open_device_server→CPU 缓冲分配→注册→SIGINT 注册→监听 |
| 迭代循环 | server.c:300-404 | 每轮收两段包→组 task→提交→收割→回 ack |
| 结算 | server.c:407-410 | print_run_time（第 12 篇详述） |
| 清理链 | server.c:412-426 | goto 标签逆序：socket→rdma_buff→内存→设备 |

支撑件全部集中在文件头：`MAX_SGES 512`（server.c:52，sg_list 模式的本地 gather 上限）、`ACK_MSG "rdma_task completed"`（server.c:53，20 字节定长回执，含 NUL）、`PACKAGE_TYPES 2`（server.c:54，每轮必须收齐的两类包）。user_params 六字段（server.c:66-74）：persistent/port/size/iters/num_sges/hostaddr——注意没有 use_cuda 和 bdf，这两个 client 专属字段在 server 侧根本不存在，server 从命令行就注定与 GPU 无缘。

`keep_running` 是 volatile int（server.c:76），SIGINT 处理器只置零不退出（server.c:78-81），让主循环与收割循环各自跑到安全点再收尾——这是长跑服务的基本卫生。

## 三、外部连接

server main 对库的调用恰好覆盖核心库 API 的一半：`rdma_open_device_server`（server.c:256，DCI 设备创建，第 9 篇详述）、`work_buffer_alloc(size, 0, NULL)`（server.c:264，use_cuda 硬编码 0，第 3 篇的 CPU 分支）、`rdma_buffer_reg`（server.c:273，第 5 篇）、`rdma_submit_task`（server.c:370）与 `rdma_poll_completions`（server.c:380，第 10 篇）。

控制面由 `open_server_socket`（server.c:89-144）搭台：getaddrinfo 带 AI_PASSIVE（server.c:93）、SO_REUSEADDR（server.c:118）方便重启、bind 失败则轮询下一个地址族（server.c:113-125）、`listen(tmp_sockfd, 1)`（server.c:135）——backlog 故意为 1，一次只婚配一个 client；`accept` 拿到会话 socket 后**立刻 close 临时监听 socket**（server.c:136-137）。监听 socket 用完即弃，是"婚介所"模型：牵完线就退场，会话与监听彻底解耦。这条 TCP 通道上流动的只有凭据包与 ack，一字节数据都不走（数据面全部走 RDMA）。

反向依赖是库对 server 的"身份判定"：`is_server()` 以 `srq == NULL` 为判据（gpu_direct_rdma_access.c:171-175）——server 设备不建 SRQ（创建序列里 server.c 对应的 gpu_direct_rdma_access.c:775 留有明注 "We don't create SRQ for DCI (server) side"），这决定 `rdma_reset_device` 只对 server 放行（gpu_direct_rdma_access.c:1011-1014）。

## 四、数据流

一次迭代的完整节奏（server.c:300-404）：

1. **收两段包**：内层 `for (i = 0; i < PACKAGE_TYPES; i++)`（server.c:313）先收 1 字节 pl_type + 2 字节 pl_size（server.c:314-315，MSG_WAITALL），再按类型分流——case 0 收描述串（server.c:317-326），case 1 收 8 字符十六进制 flags 并 `sscanf("%08x")` 还原（server.c:327-338）。两段包与 client 侧 pack_payload_data 的打包严格镜像（client.c:144-159，第 8 篇）。
2. **组任务**：memset task_attr 后填五个字段，`wr_id = cnt`（server.c:348）——以迭代号为请求号，收割时凭它对账。
3. **（可选）切 sg_list**：带 `-l N` 时把本地缓冲切成 N 段 iovec（server.c:353-369，下节展开）。
4. **提交并收割**：`rdma_submit_task`（server.c:370）后进入 do-while 轮询，条件 `reported_ev < 1 && keep_running`（server.c:379-382）——每轮迭代至少等一个完成事件，宁可空转（代码里留着 TODO 注释"we can put sleep here"，server.c:381）。
5. **验尸与回执**：逐个检查完成状态（server.c:385-396），失败时 persistent 模式下先 `rdma_reset_device`（server.c:392）再跳清理；成功则 `write(sockfd, ACK_MSG, sizeof ACK_MSG)` 回执（server.c:399）。

每轮都以 TCP ack 收尾，client 收到才进下一轮——**停等协议**（stop-and-wait），这是第 12 篇带宽口径分析的骨架。

## 五、设计决策

- **CPU 缓冲硬编码**：server.c:264 的 `work_buffer_alloc(usr_par.size, 0, NULL)` 把 use_cuda 写死为 0。语义上"存储后端"的数据本来就该在主机内存；工程上让 server 机器零 CUDA 依赖（Makefile 的非 USE_CUDA 分支，第 2 篇）。
- **64 字节对齐切片的代价**：`portion_size = (size / num_sges) & 0xFFFFFFC0`（server.c:364，注释 "64 byte aligned"）对齐 PCIe payload 粒度，但向下取整意味着**尾差字节被静默丢弃**：size=10000、num_sges=3 时 3333→3328，实际只覆盖 9984 字节。更极端的 size=4096、num_sges=100：4096/100=40，40 再清低 6 位直接变 **0**——所有 SGE 零长度，RDMA 照常提交一个空传输。库侧 buff_size_validation 只会 WARN 不拦截（gpu_direct_rdma_access.c:1330-1333）。用 `-l` 时务必保证 size/num_sges ≥ 64 且整除。
- **sg_list 上限双层**：server 侧 MAX_SGES=512 先拦（server.c:354-358），库侧每 WR 最多 MAX_SEND_SGE=10 个 SGE 再自动分片（gpu_direct_rdma_access.c:893，第 10 篇），两层各管一段。
- **失败恢复只在 persistent 模式**：完成状态非 SUCCESS 时，`if (usr_par.persistent && keep_running) rdma_reset_device(...)`（server.c:391-393）——**返回值被忽略**，复位失败也只能继续走 sock_listen 重来；非 persistent 则直接收档退出。这是"样例级容错"的诚实边界：恢复失败不重试、不上报，重启大法兜底。
- **每连接重新计时**：`sock_listen` 标签在 accept 前（server.c:283-285），gettimeofday(&start) 在 accept 后（server.c:291），cnt 在 for 里归零——persistent 模式下每次连接独立结算一次 print_run_time（server.c:407），统计互不污染。

## 六、新人提示

1. **读 main 先认四个 goto 标签**：sock_listen/clean_socket/clean_rdma_buff/clean_mem_buff/clean_device（server.c:283、412-424）是控制流骨架，错误路径全部走标签逆序回退，与资源申请顺序严格镜像。
2. **debug 模式会污染数据缓冲**：SDEBUG_LOG_FAST_PATH 定义实为 sprintf（server.c:62），server.c:351 那句 `SDEBUG_LOG_FAST_PATH((char*)buff, "Read iteration N %d", cnt)` 在 `-D` 位 1 开启时把"Read iteration N"写进**待传输的缓冲本身**——测带宽时开 fast-path 调试，数据内容与校验都受影响（第 1 篇坑 4 的另一面）。
3. **desc_str 的栈上定长**：server.c:303 用与库内 BUFF_DESC_STRING_LENGTH 同构的字面量字符串 sizeof 定长（gpu_direct_rdma_access.c:1240），两边靠"同一个示例串"维持一致而非共享宏——改协议格式要两处同步，这是样例代码的债。
4. **usage 与 README 不同步**：`-P` 与 `-l` 只在 usage（server.c:152、157）有文案，README 的 Run Server 示例（README.md:68-71）完全没提；对照清单见第 12 篇。
5. **persistent 模式的退出路径**：SIGINT 置 keep_running=0 后，主循环与收割循环相继退出，clean_socket 处的 `if (usr_par.persistent && keep_running)` 为假，不再回 sock_listen，顺清理链退出——优雅关停靠的是"两处循环条件 + 一处 goto 条件"都检查同一个 volatile 标志。
