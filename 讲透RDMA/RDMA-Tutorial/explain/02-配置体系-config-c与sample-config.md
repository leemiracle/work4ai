# 02 · 配置体系：config.c 与 sample.config

## ① 角色定位

config.c（245 行）+ config.h + sample.config 构成本仓唯一的输入接口：节点拓扑（谁是 server 谁是 client）、消息大小、在途消息深度全部由它决定，命令行只补一个 sock_port（main.c:26）。它在图谱中占两层——"配置数据模型与运行样例"（第 4 层，config.h 契约+样例）与"配置解析器"（第 5 层，config.c 状态机），tour 第 4/5 步。它的产出 `config_info`（config.c:10）是三个全局结构之一，setup_ib 按 num_clients/num_servers 定 QP 数（setup_ib.c:246-250），client/server 数据面按 msg_size/num_concurr_msgs 控制流量——配置文件的每一行都会一路流到 verbs 调用参数里。

最特殊的职责是**角色自动判定**：parse_config_file 末尾强制调 get_rank（config.c:190-191），用本机 hostname 对着两张节点列表自证身份，这一步直接决定了 main.c:34-38 走 server 还是 client 线。

## ② 内部结构

**契约侧 config.h**：ConfigInfo 结构（config.h:14-27）八个字段——num_servers/num_clients 计数、servers/clients 字符串二级指针、is_server/rank 角色对、msg_size/num_concurr_msgs 负载参数、sock_port。`__attribute__((aligned(64)))`（config.h:27）把结构体对齐到缓存行，因为它在数据面热循环里被反复读取。解析状态枚举 ConfigFileAttr（config.h:7-12）：ATTR_SERVERS/ATTR_CLIENTS/ATTR_MSG_SIZE/ATTR_NUM_CONCURR_MSGS。

**解析侧 config.c** 四个函数构成流水线：

- **clean_up_line**（config.c:13-26）：双指针原地压缩，剔除空格/Tab/\r/\n，把 `server1 .. server2` 压成 `server1..server2`。这是后续一切 strstr 匹配的前置条件。
- **parse_node_list**（config.c:36-90）：单趟扫描区间表达式。第一循环走到 `.` 为止（config.c:43-51），非数字字符攒前缀、数字按 `start = start*10 + digit` 攒起始编号；`i += 2` 跳过两点（config.c:53）；第二循环攒 end（config.c:54-59）；`num_nodes = end - start + 1`（config.c:61）。随后 calloc 指针数组（config.c:64）并逐个生成 128 字节名字缓冲（config.c:72-84）——生成规则是**硬编码二选一**：前缀含 "mnemosyne" 则 `mnemosyne%02d`，否则一律 `saguaro%d`（config.c:77-81）。
- **get_rank**（config.c:92-133）：uname 取 nodename（config.c:102-105），先扫 servers 列表命中即 is_server=true（config.c:108-114），再扫 clients——若已命中 servers 则 check(0) 报"同时列在两个列表"（config.c:122-124）。匹配方向是 `strstr(hostname, 列表项)`：**hostname 包含列表项**。
- **parse_config_file**（config.c:135-202）：主状态机，详见数据流节。

**样例 sample.config**（8 行）：`servers:` 区段写 `server1 .. server2`，`clients:` 区段写 `client1 .. client2`，`num_concurr_msgs: 64`，`msg_size: 8`。区段标记与值各占一行。

另有两个附属函数：print_config_info（config.c:229-244，开头打 "Configuraion" 拼写错误原样保留，config.c:231/243）与 destroy_config_info（config.c:204-227）。

## ③ 外部连接

上游只有 main.c:24 的一个调用。下游消费者分三档：main.c 用 is_server 分发角色（main.c:34）并读 rank 起日志文件名（main.c:51-55）；setup_ib.c:246-250 用 num_clients/num_servers 决定 QP 数量与缓冲三因子（setup_ib.c:273）；client.c/server.c 数据面读 msg_size/num_concurr_msgs/num_qps 控制预投与循环深度（client.c:16-18、server.c:16-18）。反向依赖 config.c 的只有 debug.h 的日志宏。图谱上它是"配置解析器"层，向右被 IB 资源层与双负载线引用，是参数语义的源头。

## ④ 数据流

逐行走一遍主状态机（config.c:145-188）：

1. `fgets` 读 128 字节行（config.c:145）；行内任意位置含 `#` 即整行跳过（config.c:147-149）——注释判定在 clean_up_line **之前**，按子串而非行首判定。
2. clean_up_line 压平空白（config.c:151）。
3. 区段标记判定：清理后的行含 `servers:`/`clients:`/`msg_size:`/`num_concurr_msgs:` 之一则切换 attr 状态并 continue（config.c:153-165）。
4. 值分发：attr==ATTR_SERVERS 时把整行交 parse_node_list，返回节点数写入 num_servers（config.c:167-170）；ATTR_MSG_SIZE/ATTR_NUM_CONCURR_MSGS 走 atoi 并 check 正数（config.c:175-184）。
5. **`attr = 0`（config.c:187）**——每个区段标记只对**紧跟的一行**生效，状态不粘滞。servers: 下连写两行，第二行会因 attr 归零被静默忽略。
6. 循环外 get_rank 定角色（config.c:190），fclose 收尾（config.c:193）。

**destroy_config_info 是死代码（实证）**：config.c:204-227 定义了逐元素 free servers/clients 的释放函数，config.h:32 有声明，但全仓 grep 仅此两处——main.c:41-43 的清理只调 close_ib_connection + destroy_env，从不调它。servers/clients 共 2×num_nodes 个堆块随进程退出泄漏给 OS。教程尺度无害，但它说明"写了析构≠接了析构"，读清理代码要顺着调用链验证。

## ⑤ 设计决策

**① 区段式而非 key=value**：作者选了 `servers:` 换行 `值` 的区段格式而非 `key = value`，换来的是解析器可以完全不处理等号与值内空白；代价是状态机+单行生效的脆弱性（见数据流第 5 步）。

**② 区间表达式压缩拓扑**：`node1 .. nodeN` 一行表达 N 台机器（config.c:43-61），配合 rank=列表下标，让"拓扑即编号"——多机实验里这是最低摩擦的写法。

**③ hostname 子串匹配定角色**：好处是节点零参数自定位；代价见下节坑 2/3。check(0) 双列表冲突检测（config.c:123）是这套方案里唯一的防错。

**④ atoi 而非 strtol**：config.c:176/181 用 atoi，无法区分"0"与"垃圾输入"，只能靠事后 check 值>0 兜底——对正数参数恰好够用。

**⑤ 64 字节对齐的全局配置**：config.h:27 的 aligned(64) 让热路径读 config_info 不跨缓存行，是少数为性能做的契约级决定。

## ⑥ 新人提示

**坑 1（最大）：节点名硬编码改写**。parse_node_list 生成名字时只认 mnemosyne/saguaro 两种前缀（config.c:77-81）——sample.config 里写 `server1 .. server2`，实际生成的名字是 `saguaro1`/`saguaro2`！在自己集群上跑必须改 config.c:77-81 两个 sprintf，或把主机命名迁就它，否则 get_rank 必失败退出。

**坑 2：子串匹配的排名碰撞**。`saguaro%d` 不补零，列表扩到 10 台以上时，hostname `saguaro10` 包含列表项 `saguaro1`，会在 i=0 提前命中拿到 rank 0（config.c:108-114 顺序扫描）——saguaro1 与 saguaro10 同 rank。节点数 ≥10 必踩。

**坑 3：单行生效**。在 servers: 下写两批节点，第二批被静默丢弃（config.c:187 的 attr 复位）；正确写法是一行写完整个区间或改用逗号扩展（后者需自己改解析器）。

**坑 4：注释判定过宽**。行内任何位置的 `#` 都会让整行报废（config.c:147）——值域里永远别出现井号。

其余提示：改 msg_size 记得它同时决定 MR 缓冲三因子与路径 MTU 的关系（IB_MTU 固定 4096，ib.h:11，msg_size 超过它会在 RTR 校验失败）；验证配置是否被正确吃进，直接看日志里的 Configuraion 快照（config.c:229-244 经 init_env 落盘）。
