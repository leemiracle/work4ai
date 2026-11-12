# 08 远程执行协议：REQ 编码与带外控制通道

## 一、角色定位

qperf 是双进程协作的测量工具，client 怎么让千里之外的 server 跑 rc_lat 而不是 tcp_bw？答案是仓库里唯一的一条"指令"：TCP 控制通道上的 REQ 结构（qperf.h:153-176）。它相当于一个极简 RPC——`req_index` 一个字段就是全部指令集（测试下标），其余 19 个字段全是该指令的参数。围绕它形成四层协议机制：可移植编码器（support.c）、版本两步握手（qperf.c server）、控制消息与同步原语（send_mesg/recv_sync）、以及出错时的 TCP 带外数据通道（urgent）。任务书提到的"RI_ 前缀指令集"在本仓库不存在（grep 全源码零命中），那是后来某些 fork/后续版本的机制；0.4.11 世代的远程控制就是 REQ+OOB 这一套。

## 二、内部结构

**指令载体 REQ**（qperf.h:148-172）：头四个字段 ver_maj/ver_min/ver_inc/req_index 各 uint16_t，其后 17 个 uint32_t 选项位（access_recv…use_cm）加两个定长字符串（id/static_rate，STRSIZE）。结构体注释是协议的"宪法条款"：*"Do not move or change the first four elements"*——因为 server 是分两步收的，头部位置被锁死；选项字段清一色 uint32_t 也是刻意的（qperf.h:148-152 注释：选项按 32 位值设置）。

**编码器**（support.c:87-154）：不做任何 htonl/ntohs，而是字节流式自定义小端编码。`enc_init` 把静态指针 EncodePtr 定位到缓冲区（support.c:87），`enc_int(l, n)` 按一次一字节右移写出 n 字节（support.c:129-138），`dec_int` 反向拼装（support.c:142-150），字符串直接 memcpy（enc_str，support.c:107）。好处是字段宽度由 `sizeof(host->xxx)` 当场决定，异构 32/64 位、大小端机器互操作不依赖同构结构体布局——代价是每加字段必须手写 enc/dec 三处。

**enc_req/dec_req 三件套**（qperf.c:2631-2700）：`enc_req`（qperf.c:2631）逐字段按声明顺序编码；解码侧刻意拆成 `dec_req_version`（qperf.c:2666，只解头三个版本字段）与 `dec_req_data`（qperf.c:2680，解剩余全部）——拆分本身服务于两步握手。

**两步握手**（qperf.c:1354-1366）：server 先 `recv_mesg(&req, s, "request version")` 只收 `offset(REQ, req_index)` 个字节，解码版本，`Req.ver_maj != VER_MAJ || Req.ver_min != VER_MIN` 立即 `version_error()`；过关才收余下部分并 `dec_req_data`。`version_error`（qperf.c:1388-1409）会比较高低位，给出方向明确的报错："upgrade qperf on server from 0.4.9 to 0.4.11"——把协议不兼容变成可操作的诊断。注意 ver_inc 不参与兼容判定（增量版可互通）。

**指令分发**（qperf.c:1368-1378）：`req_index >= cardof(Tests)` 防越界后直接 `test = &Tests[Req.req_index]; (test->server)()`。client 侧的填充在 `client()`（qperf.c:1488）：`RReq.req_index = test - Tests`——指针差即下标。这意味着**指令集稳定性依赖 Tests 表的物理顺序**（qperf.c:556-597）：插入或删除任何一项都会让新旧版本对同一 index 解析出不同测试，所以 REQ 注释才要求结构变更必须升 VER_MIN。表按字母序排（conf/quit/rds_bw/…/xrc_lat）纯属可读性，协议安全靠"只追加不改序"的君子协定。

**控制消息收发**（support.c:276-298 → send_recv_mesg support.c:301-366）：所有控制流字节都走 `send_mesg/recv_mesg`，底层一个 select 循环带 `Req.timeout` 超时（缺省 DEF_TIMEOUT），对端无响应报"x not responding"；收发均循环到 len 清零，天然处理短读短写。**同步原语** `synchronize`（support.c:235）= send_sync + recv_sync：双方互发同一段 ASCII 标签串（如"synchronization before test"），recv_sync 还 memcmp 校验内容（support.c:259-271）——不是形式主义，两端步调错位时立即暴露。`sync_test`（qperf.c:1794）在此基础上起计时器，是所有测试的"预备-跑"。

**带外错误通道**（support.c:419-460 urgent）：对端 error() 致命退出前，向 TCP 连接发一个字节的 MSG_OOB 带外数据（'.' 表示正常结束，其它为错误前导），本端 SIGURG→`urgent()`（qperf.c:717 注册）读 OOB 字节：是 '.' 就 `set_finished()` 让本端体面收尾；是错误就顺着带外标记 `sockatmark` 找到流内错误文本，冠以 `remote_name()`（support.c:522，client 视角返回"server"）打印后 die。这条通道让"对端死了"从无限超时变成即时带原因的失败。

## 三、外部连接

- **向上**：`do_args`/`find_test`（qperf.c:832）在本地把测试名翻译成 TEST 结构，`client()` 负责填 RReq 版本三连与 req_index（qperf.c:1486-1488）。
- **向下**：`rd_open`（rdma.c:1472）与 socket 线的 `client_init`（socket.c:586）都在自己的第一步调 `client_send_request()`（qperf.c:1503）——各传输线的"开火授权"统一由协议层发出。测试完成后的 `exchange_results`（qperf.c:1582）用同一通道互发 STAT（enc_stat/dec_stat，qperf.c:2706/2726）。
- **横向**：`run_client_quit`（qperf.c:1765）与 `run_server_quit`（qperf.c:1779）是协议里仅有的两个"管理指令"：client 发 REQ(index=quit) 后 sync 完即 exit；server 端 sync 后 read 等对端先退，再 `kill(getppid(), SIGQUIT)` 让常驻 accept 循环的父进程退场（qperf.c:1779-1789）——这是唯一能让 server 进程组自杀的方式。conf 测试（qperf.c:1614/1637）则是"只取信息不测量"的指令变体。

## 四、数据流

一次完整指令往返：client `client()` 填 RReq → `client_send_request`（qperf.c:1503-1547）connect 成功后 `remotefd_setup` 置非阻塞+F_SETOWN（让 SIGURG 找得到进程）→ `enc_req` 编码整个 REQ → send_mesg 发出。server accept 后 fork，子进程两步收包、查表分发 `(test->server)()`。数据面测试期间控制通道静默，仅在 `rd_prep` 交换 NODE（rdma.c:1521-1526）、`sync_test`、`exchange_results` 三个节点短暂活跃；任何一端 fatal error 时 OOB 通道介入。结束 client 调 `remotefd_close`（qperf.c:1569）。

## 五、设计决策

1. **自定义小端字节流而非结构体直传**：放弃"双端同构直接 send(sizeof(REQ))"的诱惑，换取跨端序/跨字长稳定性——1990 年代网络工具在异构集群上的生存底线。
2. **版本两步收**：先收头部再决定要不要继续，版本不符时连参数都不必解，且能在报错里给出明确的升级方向——把协议演进成本转嫁给版本比较而不是字段猜测。
3. **req_index 而非测试名上协议**：一个 uint16_t 比 ASCII 名省流量，但把 Tests 表顺序冻结成了事实 ABI；"只追加"约定 + ver_min 门禁是这个便宜方案的全部保险。
4. **同一通道复用于 sync/NODE/STAT/port 中继**：不另开管理连接，超时/错误处理只需实现一遍；代价是数据面起跑前必须串行过几次 RTT（高延迟链路上 `-t 1` 会被协议开销吃掉可观比例）。
5. **OOB 而非 IN-band 错误标记**：带外字节不会与在途数据混淆，`sockatmark` 能精确切出错误文本边界；TCP OOB 虽是出了名的各栈实现不一，但 2009 年的目标环境（Linux OFED）里它足够可靠。

## 六、新人提示

- 改 REQ 的第一冲动应该是"别改"：先读 qperf.h:148-152 的三条注释（uint32_t 约定、头四字段冻结、ver_min 升级规则），再看 Tests 表（qperf.c:556）追加新测试是否够用——追加 test() 宏项 + 同步更新双端 qperf.h 原型即可，不动协议。
- 排查"server 收到坏 index"类崩溃，先比对两端 Tests 表长度：`cardof(Tests)` 在 RDMA 与非 RDMA 构建下不同（qperf.c:569 的 #ifdef），混用 --use_cm 配置前确认两端二进制同代。
- `debug("sending request: %s", TestName)`（qperf.c:1489）与 server 的"received request"（qperf.c:1375）是一对现成的协议窥探点，`qperf -D` 即可看到指令流。
- recv_sync 的 memcmp 失败报"synchronize failure: data does not match"几乎总是双向 sync 交错错位的信号（一端多调了一次 synchronize），而不是网络坏了。
- server 父进程不退是特性：quit 指令设计成"client 先走"，若 client 异常死亡，OOB 通道的 die() 是 server 子进程的唯一出口；两条路都断时等 `Req.timeout`（DEF_TIMEOUT）超时。
