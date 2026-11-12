# 02 测试框架抽象：TEST 结构与方法表

## 一、角色定位

qperf 支持 40 个测试（12 socket 系 + 25 RDMA 系 + 3 XRC 系，按编译条件浮动），横跨三代传输技术：BSD socket（TCP/UDP/SCTP/SDP）、RDS 内核模块、RDMA verbs。让这三代技术在同一个 CLI、同一套选项系统、同一条 client-server 协议下工作，靠的不是面向对象继承，而是 qperf.c 里三个相互咬合的表结构：`TEST` 方法表（qperf.c:139-143）、`PAR_INFO` 参数表（qperf.c:316-354）与 `REQ` 线上请求结构（qperf.h:153-176）。本文拆解这套"函数指针 + 参数登记"的轻量框架，它是全仓最有复用价值的设计。

## 二、内部结构

**TEST 三元组**（qperf.c:139-143）只含测试名字符串与 client/server 两个 `void (*)(void)` 函数指针。方法表本体 `Tests[]`（qperf.c:556-597）借助宏：

```c
#define test(n) { #n, run_client_##n, run_server_##n }
```

一行 `test(rc_rdma_read_bw)` 即完成注册。表按字母序排布，并用两层条件编译裁剪：`#ifdef RDMA` 包住 L569-596 的 25 项，`#ifdef HAS_XRC` 再包住 L591-595 的 3 项 xrc 测试——方法表本身就是构建配置的声明。server 端选择测试不用字符串查找，直接 `test = &Tests[Req.req_index]`（qperf.c:1371），线上传的是下标而非名字，省一次表遍历也杜绝了拼写歧义。

**参数系统是框架的核心**。每个可调参数在 PAR_INDEX 枚举（qperf.h:94-133）中占相邻的 L_/R_ 两位（如 L_MSG_SIZE/R_MSG_SIZE），P_NULL 必须为 0。`ParInfo[P_N]`（qperf.c:316-354）按完全相同的顺序登记每个参数的类型字符（'l'=普通整数、's'=size、't'=time、'p'=字符串指针）与存储地址（L_* 指向本机 REQ，R_* 指向 RReq 副本）。`ParName[]`（qperf.c:291-309）再挂一层展示用名。三张表靠 initialize() 的顺序断言（qperf.c:619-621）与 par_info() 的运行时校验（qperf.c:1299-1307）保持同步。

每个参数有三个状态位：`set`（用户显式设置过）、`used`（测试声明会消费它）、`inuse`（客户端本次迭代在用）。配套工具函数：`setp_u32/setp_str`（qperf.c:1223-1247）写入并登记来源；静默版本 `setv_u32`（qperf.c:1212-1217）"不让任何人知道我们设了它"，专供框架填默认值；`par_use`（qperf.c:1253-1260）测试声明消费意图。

**opt_check 是契约的执法者**（qperf.c:1314-1330）：测试初始化末尾必调，凡 set 而 !used 的参数打"warning: %s set but not used in test %s"。用户 `qperf host -mt 4096 tcp_bw` 会立刻被告知 MTU 选项对 TCP 测试无效——这是该框架对用户体验的最大贡献。

**LOOP 迭代器**（qperf.c:93-100）支持 `--loop msg_size:1K:1G:*2` 这类扫描：parse_loop（qperf.c:971-1041）解析冒号分隔的 init:last:incr（incr 前缀 '*' 切乘法模式），多个 --loop 串成链表；`do_loop`（qperf.c:773-795）递归展开——每层循环把当前值 snprintf 回参数 argv 再调 do_option，最内层才 client(test)。这使"一次连接跑完 1K 到 1G 的 18 档带宽扫描"成为内建能力。

## 三、外部连接

- **qperf.h 是契约文本**：PAR_INDEX、REQ、USTAT/STAT/RES、以及按文件分组的全部 run_client_X/run_server_X 原型（qperf.h:238-357）。三条传输线的函数在这里"报到"，Tests 表在 qperf.c 里"点名"，两处必须一致——链接器兜底函数级一致，help.txt 兜底文档级一致。
- **do_option 的类型分发**（qperf.c:847-965）按 OPTION.type 字符串（"int"/"size"/"time"/"str"/"set1"...）决定参数怎么解析（arg_long/arg_size/arg_time 分别支持不同单位语法，str_size qperf.c:1125-1150 认 kb/mb/kib/mib 全家）并 setp 到 L_ 与 R_ 两个槽位——默认对端同配，loc_/rem_ 前缀选项才只写一侧。
- **RDMA 线的特化**：rd_params（rdma.c:1425-1465）是 rdma.c 版的 ip_parameters——按传输类型决定 use_cm 是否可用（RC 才 par_use，其余 setv_u32 强制 0）、非 CM 模式才启用 MTU/SL/static_rate/src_path_bits 一堆 IB 专有参数，最后同样 opt_check 收口。
- **展示端**：show_used（qperf.c:2043-2095）遍历 ParName 表，凡 inuse 的参数按 loc/rem 值是否相同决定合并还是分行展示——参数表同时驱动了 `-vu` 的回显。

## 四、数据流

参数从命令行到网卡的单向流动：

```
argv → find_option(查 Renamed 兼容表→Options) → do_option 按类型解析
     → setp_u32 写 ParInfo[index].ptr（即 Req.msg_size 等字段）
     → 测试入口 run_client_X：
         setp_u32(0, L_MSG_SIZE, 默认值)   # 未显式设则填默认
         par_use(L_MSG_SIZE)               # 声明消费
         opt_check()                       # 报未用警告
     → client_send_request: enc_req 逐字段小端编码整包 REQ → TCP
     → server: dec_req_* 解码进 Req（此时 Req 即对端配置）
     → 数据面循环读 Req.msg_size / Req.time 等字段
```

统计回流对称：数据面只往 LStat（USTAT s/r 四组，qperf.h:192-202）累加 no_bytes/no_msgs/no_errs；exchange_results 后 calc_results 把 LStat/RStat 合并出 Res 七个 double，show_info 按 MEASURE 枚举（LATENCY/MSG_RATE/BANDWIDTH/BANDWIDTH_SR，qperf.h:139-144）挑主指标展示——每个测试入口函数最后一行 `show_results(BANDWIDTH)` 就是在声明自己的量纲。

## 五、设计决策

- **名字即协议**：`run_client_##n` token-pasting 把命名约定变成编译期契约，框架零注册成本；代价是 qperf.h 必须手写全部原型，于是出现了 run_client_bug/run_server_bug（qperf.h:308-309）这类声明后从未实现的死原型——抽象的维护成本留在头文件里。
- **参数双槽（L_/R_）而非单值**：同一选项默认写两端，对端配置的可见性（RReq 保留 server 视图）使 show_used 能并排打印 loc_/rem_ 实际生效值，这在调测双机差异时极有价值。
- **req_index 传下标不传名**：兼容性收窄到"两端 Tests 表同序"，由版本协商（ver_min）背书；比传字符串省去大小写/别名问题。
- **默认值由测试自填而非框架预置**：ip_parameters（socket.c:565-575）每个入口填自己的 msg_size 默认（TCP 64K、UDP 32K、lat 类 1 字节），框架只管"用户没设才允许设"+ opt_check。这让"什么是合理默认"的领域知识留在领域代码里。
- **条件编译而非运行时探测**：RDMA/HAS_XRC 在构建期由 configure.ac 探测 libibverbs 决定（AC_CHECK_LIB 两连测，rdma 测试缺席时 help/man 也同步裁剪），二进制里不留死分支——代价是换机器必须重编。

## 六、新人提示

- 新增一个测试的完整清单：①在对应传输线写 run_client_X/run_server_X；②qperf.h 对应分组加原型；③qperf.c Tests 表加 `test(X)`（注意保持字母序，server 端按下标分发，乱序不影响正确性但影响可读性）；④help.txt 的 Tests 节加描述（man 页由 mkman 自动生成）。
- 排查"set but not used"警告时先想到 par_use：不是选项坏了，是当前测试没声明消费它；去测试入口函数找 par_use 列表。
- 读 LOOP 相关 bug 时记住循环是"参数回填"实现的：do_loop 伪造 argv 调 do_option（qperf.c:783-787），所以循环变量走的完全是普通选项路径，Debug 输出里会看到重复的设置痕迹。
- qperf.h:280-282 注释写"Socket tests in socket.c"，但紧随其后的 run_client_rds_bw 等 4 个原型实现在 rds.c——头文件分组注释已与文件演化脱节，按文件找函数时别被注释误导。
