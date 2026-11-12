# 09 选项系统：find_option 与 par-族参数处理链

## 一、角色定位

qperf 命令行有 60 多个长短选项、37 个可设参数（PAR_INDEX 枚举 qperf.h:93-133），还要支持本地端/远端各设一半（`--loc_msg_size` 只设 L_ 前缀、`--rem_msg_size` 只设 R_ 前缀）和 `--loop msg_size:1K:64K:*2` 的批量扫描语法。支撑这一切的是 qperf.c 里一条清晰的三级流水线：`do_args` 逐词扫描 → `find_option`（qperf.c:802）查两张表（Renamed 改名表 + Options 选项表）→ `do_option`（qperf.c:848）按类型字符串分派给 arg_* 解析器，最终写入 ParInfo 驱动的参数槽位。链尾的 `opt_check`（qperf.c:1315）是整个系统的质检员：用户设了但当前测试不认的选项会被点名警告。展示端则有 `commify`（qperf.c:2812）把数字加千分位逗号，与输入端的 `str_size` 后缀解析首尾呼应。

## 二、内部结构

**两张表**。`Renamed[]`（qperf.c:360-418）是改名史档案馆：58 条"旧名→新名"映射，如 `-a`→`-ca`（affinity 改 cpu_affinity）、`-p`→`-ip`（port 让位给 ip_port）、`-vC`→`-vvc`（verbose 细分）。`find_option`（qperf.c:802-829）先扫它，命中即 `error(RET, "warning: obsolete option: %s; use %s instead")` 后按新名继续——废弃名只警告不禁用，向后兼容的姿态。`Options[]`（qperf.c:424-554）是现行选项表，每行四列：名字、类型串、arg1（L_ 索引）、arg2（R_ 索引）。`--msg_size` 同时给两列（双端生效），`--rem_msg_size` 只填 arg2——"本地/远端"语义在表结构里就用空列表达，不靠运行时判断。

**类型分派 do_option**（qperf.c:848-970）。类型串首字符若是 'S' 先跳过（qperf.c:851-853）——这标志着"server 端合法选项"，`do_args` 靠它判定进程角色（见 01 篇）。剩余串进入 if-else 链：`int`→arg_long、`size`→arg_size、`time`→arg_time、`str`→arg_strn、`set1` 直接写 1；特殊类型 `help`/`host`/`lp`/`loop`/`precision`/`version`/四级 verbose 各有专属分支。落点统一是 `setp_u32(option->name, option->arg1, v)` 连调两次（arg 为 0 时 setp_u32 静默跳过，见 par_set 的 P_NULL 短路）。

**四个 arg_* 解析器**（qperf.c:1085-1211）共同遵守"缺参数/坏格式/负数三连拒"的纪律：`arg_long` 用 strtol 且要求尾指针吃完全串（qperf.c:1090-1093）；`arg_size` 委托 `str_size`（qperf.c:1126-1155）；`arg_time`（qperf.c:1172-1211）接受 s/m/h/d 四个单位后缀，如 `-t 10m`。其中 `str_size` 是最有讲头的一个：strtold 吃数值，后缀查表 kb/mb/gb=1000 进制、kib/mib/gib（及大写 K/M/G）=1024 进制（qperf.c:1134-1145）——小写 b 系列是磁盘带宽习惯（十进制），大写与 ib 系列是内存习惯（二进制），一个 `-m 4K` 的语义精确到字节。

**par-族五函数**（qperf.c:1213-1313）。参数槽位本体是 `ParInfo[P_N]`（qperf.c:316-360）：每行 `{索引, 类型字符, 指针}`，指针直指 `Req.xxx`（L_ 前缀）或 `RReq.xxx`（R_ 前缀）——注意 L/R 各指向**不同结构体**（Req 是发出去的请求、RReq 是 client 本地的请求副本框架），这是"本地值/远端值"在内存里的物理分界。`par_info`（qperf.c:1300-1313）按下标取行并校验"表序==枚举序"（initialize，qperf.c:620-621 也全量再验一次）。`par_set(name, index)`（qperf.c:1267-1289）是双模网关：name 非 0（用户显式设置）时记 `set=1` 并存名字；name 为 0（程序缺省值）时只标 `used=1`，且**若该参数已被用户设过则返回 0 让调用方放弃覆盖**——用户输入优先于程序缺省的分支点就在这。`par_use`（qperf.c:1254）标记"本测试认这个参数"（used+inuse 双标志）。`par_isset`（qperf.c:1290）查"用户是否设过"。`setv_u32`（qperf.c:1213）是旁路后门：写值不留任何痕迹，供 rd_params 强制清零 use_cm 这类"测试内部覆写"用。

**质检员 opt_check**（qperf.c:1315-1334）：扫全表，凡 `set && !used`（用户设了、测试没声明用）即 `error(RET, "warning: %s set but not used in test %s")`，并把同名孪生（L_/R_ 成对设置时两行同名）一并清 set 防重复警告。每个 rd_params/ip_parameters 的收尾都是它（rdma.c:1468、socket.c:566）。

**循环语法 parse_loop**（qperf.c:974-1046）：`--loop msg_size:1K:64K:*2` 冒号四段=变量:初值:上限:步长。变量名在 Options 表里反向查找（剥掉前导 `-`/`--` 比对，qperf.c:991-1006），步长前缀 `*` 表示乘法增长（`*2` 即翻倍，mult 标志，qperf.c:1011-1015）。多个 loop 用单向链表串接（Loops 尾插，qperf.c:1036-1044），`do_loop`（qperf.c:774-799）做笛卡尔积式嵌套迭代。这把"逐点扫曲线"从脚本外移进了工具本体——`qperf host --loop msg_size:1:4K:*2 rc_bw` 一条命令出整条带宽-消息尺寸曲线。

**展示端 commify**（qperf.c:2812-2857）：从尾部向前找数字段（含小数点前段，qperf.c:2824-2832），每三位插一个逗号，原地 realloc 平移（qperf.c:2838-2851）。`UnifyUnits` 置位时直接跳过（qperf.c:2822）——千分位便于人读，但会破坏脚本对输出做 awk 数值切分，所以留了总闸。

## 三、外部连接

- **上游**：do_args（qperf.c:727）扫描原始 argv；非选项裸参数第一个当 ServerName（qperf.c:744-747），第二个交给 find_test——选项系统与测试分发在同一个循环里。
- **下游**：ParInfo 指针直写 Req/RReq 字段，REQ 编码（08 篇）随后把 L_ 侧打包发出；`server()` 收到 REQ 后整结构覆盖本端 Req，于是远端选项随指令天然生效——选项系统的"远端半边"根本不走本地 ParInfo。
- **横向**：rd_params/ip_parameters 用 setp_u32(0,...) 填测试缺省值、par_use 声明白名单、opt_check 收尾；`client()`（qperf.c:1467-1471）每次测试前清 inuse 再补 DEF_TIME/DEF_TIMEOUT 缺省。
- **help 系统**：`--help categories` 列出的目录与 Options 表的选项完全由 help.txt 单源生成（11 篇），表与文档不双写。

## 四、数据流

`qperf -mm 64K --rem_msg_size 4K -cp host rc_bw` 的处理流：`-mm` 非标准名？不，`-m` 是 msg_size 的短名、第二个 m 是参数——find_option 命中 `{ "-m", "size", L_MSG_SIZE, R_MSG_SIZE }`，arg_size→str_size("64K")=65536，setp_u32 两次写 Req.msg_size 与 RReq.msg_size 并记 set；`--rem_msg_size` 只写 RReq 侧；`-cp` 是 cq_poll 的 set1 型。rc_bw 的 rd_params 又对 MSG_SIZE 调 setp_u32(0,...)——因用户已设，par_set 返回 0，65536 保住。opt_check 时 cq_poll 已 par_use，无警告。若用户此时多打了 `--sl 5`，rd_params 没声明 SL（RC+CM 模式下不开放），opt_check 点名"service_level set but not used in test rc_bw"。输出端 view_long→place_val→commify 把 104857600 显示成 104,857,600 bytes/sec。

## 五、设计决策

1. **表驱动而非 switch(name)**：选项语义集中在两表四列里，加选项=加一行；do_option 只按类型分派，代码量与选项数解耦。
2. **L_/R_ 双列设计**：本地/远端差分用一个空列表达，避免为每个"只影响一端"的选项写专门分支；副作用是 Options 表行数翻倍（成对出现），换来绝对规整。
3. **par_set 的 name=0 协议**：用"参数是否传名字"区分用户显式设置与程序缺省，一处分支解决优先级问题，且让 par_isset/opt_check 共享同一份真相。
4. **废弃名警告而非报错**：迁移期策略——老脚本不 break，但每次运行都提醒。
5. **str_size 双进制并存**：带宽工具横跨网络（SI 十进制）与内存（IEC 二进制）两个语境，强制统一必得罪一方。
6. **opt_check 放在测试入口**：只有知道测试是谁才能判定"用不用"，警告带 TestName 更可定位。

## 六、新人提示

- 加选项四步：PAR_INDEX 枚举加对（L_ 在前 R_ 紧随）、ParInfo 加行、Options 加行、必要时 help.txt 补条目；漏第一步 initialize 的表序自检（qperf.c:620）会在启动时用 BUG 错误拦住你。
- 调试选项去向最快的办法是 `qperf -D`：setp_u32 不打日志，但 debug 输出能看到 REQ 里的最终值；两端 -vv 的 "loc_*"/"rem_*" 输出节是选项落地的官方对账单。
- `--loop` 的初值缺省是 mult?1:0（qperf.c:1022-1025），乘法序列想从 1K 开始必须显式写 1K，写 `--loop msg_size::64K:*2` 会从 0 起步永远乘不出 1K——这是新手最常踩的静默坑。
- commify 的 realloc 失败路径调 error(0,...) 而非 SYS（qperf.c:2837-2838），错误码语义略糊，但实际触发条件（几字节的 realloc 失败）意味着进程早已病入膏肓。
- 想知道某个选项"谁会消费"：在 rdma.c/socket.c grep 它的 PAR_INDEX（如 L_POLL_MODE），par_use 的位置就是消费方的白名单。
