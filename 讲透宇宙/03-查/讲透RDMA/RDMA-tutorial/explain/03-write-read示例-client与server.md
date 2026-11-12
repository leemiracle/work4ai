# 03 write/read 示例：client 与 server 两端流程对照

> 对象：`example code/rdma_write_read/rdma-client.c`（113 行）与 `rdma-server.c`（104 行）；行号锚经源码核实（commit `c760004`）。

## 一、角色定位

这两个文件是 write_read 示例的「薄入口层」：各自约 110 行，只做三件事——解析命令行、驱动 rdma_cm 事件循环、在正确的时机调用 rdma-common 的 8 个接口。所有通信机制（QP/CQ/内存注册/MR 协议）都下沉在公共库里，入口层呈现的是**RDMA 连接管理器的两种角色模板**：主动端（client）与被动端（server）。对照阅读它们是理解 rdma_cm 事件驱动编程的最短路径——两端 80% 代码同构，差异点恰恰是主动/被动角色的分野，也是面试高频考点（建连状态机、QP 创建时机）的代码出处。教程 2.3.1 建立连接（tutorial.md:100-L157）的 server/client 代码清单就是从这两个文件提炼的。

## 二、内部结构

两文件共用同一副骨架：main（建基础设施+事件循环）+ 每事件一个 on_* 回调 + on_event 分发器 + usage。

**rdma-client.c**（主动端）：main（L12-L50）校验 `argc==4`（L19-L20）→解析 mode 注入 set_mode（L22-L27）→`getaddrinfo`（L29）→建 event_channel/cm_id（L31-L32）→`rdma_resolve_addr`（L33）。回调链四个：on_addr_resolved（L52-L61，建连接+写消息+resolve_route）、on_route_resolved（L97-L106，build_params+rdma_connect）、on_connection（L63-L69，on_connect+send_mr）、on_disconnect（L71-L77，destroy+返回 1 退出循环）。on_event（L79-L95）把四类事件分发到上述回调，未知事件直接 die（L92）。

**rdma-server.c**（被动端）：main（L9-L53）校验 `argc==2`（L17-L18）→set_mode（L20-L25）→构造仅填 AF_INET 的 addr（L27-L28，**port 字段零值**）→bind+listen（L32-L33）→`rdma_get_src_port` 取内核分配的实际端口打印（L35-L37）。回调三个：on_connect_request（L55-L66，build_connection+build_params+写消息+rdma_accept）、on_connection（L68-L73，仅 on_connect 置位）、on_disconnect（L75-L81，destroy+返回 0 **继续监听**）。usage 两端各一份（rdma-client.c:108-L112、rdma-server.c:99-L103），提示合法 mode 串。

## 三、外部连接

两入口对 rdma-common.h 的调用面：client 用到 set_mode（L23/L25）、build_connection（L56）、get_local_message_region（L57）、on_connect/send_mr（L65-L66）、destroy_connection（L75）；server 用到 set_mode（L21/L23）、build_connection/build_params（L60-L61）、get_local_message_region（L62）、on_connect（L70）、destroy_connection（L79）。编译上 Makefile L11-L15 让两个 APP 都链 rdma-common.o。与 send_recv 组的连接是镜像关系：send_recv 的 main/on_event/事件循环与本文两文件逐函数对应（如 send_recv/server.c:47-L81 的 main），可按名对号。与教程的连接：2.3.1 的「监听连接/创建QP/完成连接/解析地址路由/发起连接」五组代码块（tutorial.md:104-L157）按序拼起来就是这两个 main 的骨架；rdma_create_qp 必须在 rdma_connect/rdma_accept 之前（tutorial.md:102）的告诫，落点即 on_addr_resolved/on_connect_request 内的调用顺序。

## 四、数据流

**主动端时序**：`rdma_resolve_addr`→事件 ADDR_RESOLVED→on_addr_resolved：build_connection（此刻建 QP、注册内存、预挂 RECV）、sprintf 把 `"message from active/client side with pid %d"` 写进本端消息区（L57）、`rdma_resolve_route`→事件 ROUTE_RESOLVED→on_route_resolved：build_params+`rdma_connect`→事件 ESTABLISHED→on_connection：on_connect 置 connected=1（解掉公共库 send_message L326 的自旋）、**send_mr 主动交钥匙**（L66）→此后事件循环静默，协议推进权移交 poll 线程的 on_completion→终态对端断开→事件 DISCONNECTED→on_disconnect：destroy_connection、返回 1 退出循环、销毁 event_channel（L47）。

**被动端时序**：bind(port 0)+listen→打印实际端口→事件 CONNECT_REQUEST→on_connect_request：build_connection、build_params、写 server 侧消息（L62）、`rdma_accept`→事件 ESTABLISHED→on_connection **只置位、不发钥匙**——server 的 MR 要等收到 client 的 MSG_MR 后在 on_completion（rdma-common.c:194-L195）被动应答→事件 DISCONNECTED→destroy、返回 0 继续守听。两端最大不对称即在此：**client 是协议发起者（ESTABLISHED 即交钥匙），server 是应答者（收到才回）**；断开策略也不对称——client 退循环进程结束， server 常驻可接下一连接（但 s_ctx 单例限制它只能服务同一 verbs 设备）。

## 五、设计决策

①**端口策略相反**：server 绑 port 0 让内核随机分配（L27-L28 留零+L35-L37 打印），与 send_recv 的硬编码 22222（send_recv/server.c:57）形成对照；readme.md:9 写「default: 22222」是从 send_recv 复制来的错误文档，实际必须填 server 打印的端口。②**事件拷贝模式**：两文件的事件循环都先 `memcpy(&event_copy, event, sizeof(*event))` 再 `rdma_ack_cm_event` 再处理副本（rdma-client.c:38-L44、rdma-server.c:40-L46）——ack 后原事件内存即失效，这是 rdma_cm 的标准防 use-after-free 手法，也是新手最常省略的一步。③**QP 创建时机收敛在 ADDR_RESOLVED/CONNECT_REQUEST**：保证 connect/accept 时 QP 已就绪可交换信息（教程 L102 的规则代码化）。④**消息文本嵌 pid**（client L57/server L62）：运行结束打印的 `remote buffer: message from ... with pid N` 能直接证明数据真的来自对端进程——一行 sprintf 就是单边传输的「防伪标签」。⑤usage 用 `exit(1)` 而非 die（client L111、server L102），保持入口层与公共库错误风格分离。

## 六、新人提示

先跑通再读码：`make` 产出 `rdma-server`/`rdma-client`（Makefile:7，readme 里 `./server` 命令名是错的）；先 `./rdma-server write` 记下打印的端口，再 `./rdma-client write <地址> <端口>`；两端 mode 必须一致，否则权限注册（rdma-common.c:294/L306）与 WR 构造（L215）各自错位、直接失效。读码时建议双栏对照：左 client 右 server，逐函数找不同（端口/回调集/返回值语义/谁发钥匙），这些差异就是主动-被动角色的全部内容。注意 client 的 `freeaddrinfo`（L35）在事件循环前就释放了 addrinfo——resolve_addr 已把地址拷进 cm_id，之后不再需要，这个细节常被误认为泄漏风险。对照 send_recv 组时留意 on_connection 签名差异：write_read 版收 `rdma_cm_id*`（rdma-client.c:63），send_recv 版收 `void* context`（send_recv/client.c:223）——两代演进痕迹。
