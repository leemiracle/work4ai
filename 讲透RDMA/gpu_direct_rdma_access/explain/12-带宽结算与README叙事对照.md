# 12 带宽结算与 README 叙事对照：口径、边界与承诺差集

> 对应 tour 第 14 步「收官：循环迭代与带宽结算」。源码锚均对 HEAD `a99d506` 核实。

## 一、角色定位

`print_run_time`（utils.c:66-86，21 行）是全仓最后一个被执行的函数，client 与 server 各自调用一次（client.c:440、server.c:407）——同一场传输，两份账本，互为校验。它做的事极简：拿起始时间戳算 elapsed、拿 size×iters 算总量、打两行数字。但这两行数字的**口径边界**比函数体长得多：它量的是停等协议包着的单向 RDMA 载荷流，不是网卡极限。

本篇做两件事：先审计这把尺子（量了什么、没量什么、什么情况下会虚报），再把 README 的叙事逐条对照实现，钉出承诺与代码的差集——README 是 2019 年的手笔（MLNX_OFED 4.6-1.0.1.0、CUDA 10.1，README.md:25、32），代码此后演进过一轮（HEAD 提交名 "rdma_exec_params initialization fix (#4)"），文档漂移在所难免。

## 二、内部结构

print_run_time 的全部逻辑三行（utils.c:77-83）：

```c
usec  = (end.tv_sec - start.tv_sec) * 1000000 + (end.tv_usec - start.tv_usec);
bytes = (long long) size * iters;
printf("%lld bytes in %.2f seconds = %.2f Mbit/sec\n", ...);   /* utils.c:80-81 */
printf("%d iters in %.2f seconds = %.2f usec/iter\n", ...);    /* utils.c:82-83 */
```

单位口径由此钉死：**Mbit/sec** 与 **usec/iter**。这里有一处图谱勘误要落锤：知识图谱对 utils.c 的节点摘要写着"平均带宽（GB/s）与每秒消息数"，与实现不符——实际打印兆比特每秒与微秒每迭代，既无 GB/s 也无消息速率。引用带宽结论时以 utils.c:80-83 为准。

计时锚点的位置：client 在打包完成后、循环开始前取 start（client.c:401）；server 在 accept 之后、循环开始前取（server.c:291）。persistent 模式下 server 每个连接重取一次（sock_listen 标签在取时点上游，server.c:283-291），cnt 也随 for 归零（server.c:300）——每连接独立结算，互不污染。

## 三、外部连接

print_run_time 的三个入参全部来自第 7/8 篇的循环结构：start 是循环前的时间戳、size 与 iters 是命令行直传的 usr_par 字段（server.c:407 传 usr_par.size/iters，client.c:440 同构）。它不接触任何 RDMA 结构——账目是"计划量"而非"实测量"：真实完成数靠循环不失败隐式保证（任何失败都 goto 清理链，根本走不到 print_run_time，server.c:407 只在循环自然结束后执行）。

另一个外部锚是 README 的叙事层：README.md:4 用一段话讲完整个流程（client 分配→TCP 请求→server RDMA Write→done 回执→循环），这段叙事与 client.c:410-437/server.c:300-404 的实现骨架吻合——README 的**流程描述基本诚实**，漂移集中在细节承诺上（见第五节清单）。

## 四、数据流

被测时间窗内发生的真实事件序列（client 视角，每迭代）：

```
write(触发包) ──> server recv ──> RDMA 传输 ──> server poll ──> server write(ack) ──> client recv
```

停等协议（第 7 篇）意味着窗口内串行嵌着**两次 TCP 往返 + 一次 RDMA 完成**。因此测得的 Mbit/sec 满足上界 `size/(RTT_tcp×2 + t_rdma + t_poll)`——消息越小，TCP 往返占比越大，数字越接近"时延的倒数"而非带宽。README 示例用 `-s 10000000`（README.md:70、88）正是让 10MB 载荷摊薄控制面开销，量到接近真实带宽的数字。

三个账实差要点：

1. **只计单向载荷**：bytes = size×iters（utils.c:78），TCP 触发包（~110 字节）、ack（20 字节）、RDMA 协议开销全部不计——这是"有效载荷吞吐"口径，与 perftest 惯例一致，但引用时要说明。
2. **sg_list 模式虚报**：第 7 篇证明 `-l N` 时实际传输是 `N × ((size/N) & ~0x3F)` 字节，尾差被 64 字节对齐吃掉；而结算仍按 size×iters 记账（server.c:407 传的是 usr_par.size）。size=10000、-l 3 时实转 9984/迭代，报告虚高 0.16%；极端 size/N<64 时实转 0 字节、报告照旧全额——带 `-l` 测出的带宽永远是错的。
3. **debug 印刷污染**：README 的 server 示例带 `-D 1`（README.md:70）——每个包都有 DEBUG_LOG/FAST_PATH 输出（第 1 篇坑 4），I/O 阻塞直接压进时间窗。测性能请 `-D 0`。

## 五、设计决策

- **为什么单位用 Mbit/sec**：与 perftest/ethtool 生态对齐（链路速率习惯以兆比特计），方便与 100GbE 等线速直接比照；若要 GB/s 除以 8000 即可。两侧各自打印而非汇总单点，是分布式基准的朴素互验——两份独立计时器的差值本身就是同步质量的观测值。
- **为什么收在 utils.c 而非 main 内联**：两个 main 复用同一段格式化逻辑，保证两侧口径逐字节一致——若各自内联，单位漂移几乎是必然事故。
- **README 承诺 vs 实现差集**（逐条核实）：
  1. README.md:49 路径 `./write_to_gpu/arp_announce_conf.sh`——**write_to_gpu/ 目录不存在**，脚本在仓根（仓内 ls 实证）；历史目录结构残留。
  2. README.md:4 "sends back a TCP 'done' message"——实际回执串是 "rdma_task completed"（server.c:53、client.c:59，20 字节定长）。
  3. README.md:2 "acting as a file storage simulation"——无任何文件 I/O，"存储内容"是 sprintf 进缓冲的 "Read iteration N"（server.c:351，宏定义 server.c:62 实为 sprintf）。
  4. README.md:68-71 Run Server 示例未提 `-P`（持久模式）与 `-l`（sg_list）两个已实现选项（server.c:152、157 的 usage 有完整文案）；反向地，Makefile 的 `PRINT_LAT=1` 时延测量构建维度（Makefile:15-19）README 全程未记载。
  5. README.md:4 只提 "RDMA Write"，但 `-t 1` 的 READ 方向完整可用（client.c:194-195、237；动词选择 gpu_direct_rdma_access.c:899-901）。
  6. 流程主线（分配→TCP→RDMA→ack→循环）、拓扑建议（README.md:6 同桥 BDF）、依赖清单（README.md:23-42）与实现一致，无漂移。

## 六、新人提示

1. **引用带宽先念三句口径**：单向有效载荷、停等协议含 TCP 往返、debug 关闭——三条件缺一，数字不可比。本仓数字的意义是"该消息尺寸下的应用层吞吐"，不是 NIC 峰值（对比线速请用 perftest）。
2. **对比两端输出**：client 与 server 各自的 seconds 应当接近（差值 ≈ 一边多计的打包/accept 时间）；若差距大，说明有一侧在窗口内干了别的事（比如开了 debug）。
3. **想要 GB/s 与 msg/s 自己换算**：`Mbit/sec ÷ 8 ÷ 1000 = GB/s`；`10⁶ ÷ usec/iter = msg/s`——两行单位换算补齐图谱摘要臆想的两项。
4. **别用 `-l` 模式出报告**：第 7 篇的 64 字节对齐尾差 + 本篇的虚报账，双杀数字可信度；该模式的正确用途是测多 SGE 分片路径的功能（第 10 篇），不是带宽。
5. **README 当"2019 年快照"读**：版本号、路径、示例 flag 都可能滞后于代码（上节六条差集是完整清单）；跑通以 usage 文案（server.c:146-160、client.c:188-204）与 Makefile 为准——它们与二进制同源，永不漂移。
