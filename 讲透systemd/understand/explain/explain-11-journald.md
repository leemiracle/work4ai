# explain-11 · src/journal/journald.c + journald-manager.c — journald：采集、落盘与自我循环规避

## 一、角色定位

systemd-journald 是结构化日志中枢：全系统三类入口（/dev/kmsg 内核日志、native socket 的 `sd_journal_send` 结构化条目、转发来的 syslog/audit）汇成带字段的双时间戳条目，落进 append-only 的 journal 文件（运行期 /run/log/journal，可 flushing 到 /var/log/journal）。本仓同样是瘦入口+胖实体：journald.c 仅 160 行的 `run()`，处理进程级特殊性；journald-manager.c（2657 行）是全部业务——socket 群、条目分发、按 UID 分文件、轮转/清理/空间管理、flushing。入口文件最有趣的设定是**自我循环规避**：作为主 journald 运行时不能把日志发给 journald（那是自己），故显式选 console/kmsg 目标并 `log_set_prohibit_ipc(true)`（journald.c:61-63）；带 namespace 参数运行的实例反而可以往主 journald 记日志（journald.c:53-55）——同一二进制两种身份。

## 二、内部结构

run()（journald.c:32）的启动序列：解析可选 namespace 参数（49）；sigbus_install（71，mmap 文件 SIGBUS 兜底——journal 文件是 mmap 的）；journal_auth_init（73，FSS 真实性密钥）；manager_new→set_namespace→load_config→manager_init（75-87，manager.c:2350 的 init 打开全部 socket 与 /dev/kmsg：2486）；然后三件启动家务——vacuum（清过期）、**flush_to_var**（把上次运行的运行期日志并入持久层，journald.c:90）、flush_dev_kmsg（91）。之后进入自带节拍器的循环（107-146）：每轮算两个到期时间——max_retention_usec 触发的清理（120-131）与 journal 文件认证标签 evolve（133-137，Forward Secure Sealing 的时段密钥推进）——取最小者作为 `sd_event_run` 超时（140），醒来后跑 append_tags 与漏发 syslog 检查（144-145）。这是"事件循环 + 定时维护"的混合范式，与 networkd 的纯 post 驱动形成对照。

## 三、外部连接

入口三 socket 全在 manager_init 装配：/run/systemd/journal/socket（native）、/dev/log（syslog 兼容）、audit multicast；`manager_process_datagram`（journald-manager.c:1498）是共同入口，断言三 fd 之一（1534），按 SIOCINQ+audit 最大消息尺寸动态扩缓冲（1545-1553），注释还留着 glibc __convert_scm_timestamps 的缓冲区初始化坑（1512-1518）。出口：journal 文件格式实现独立成 sd-journal 库（journal-file.c）；消费端 journalctl 与 varlink 服务（journalctl-varlink-server.c，io.systemd.journal 流式查询）。横向：审计到 logind 的会话关联、到 manager 的 rate limit（journald.c 系列的 JOURNAL_LOG_RATELIMIT 防刷屏）。命名空间实例（--namespace=X）共享代码但独立 socket/存储目录（m->namespace 贯穿 journald.c:79-96）。

## 四、数据流

写路径：datagram/kmsg 事件 → manager_process_datagram（1498）拆包（ucred/时间戳/fd/SELinux 标签全从 cmsg 取）→ `manager_dispatch_message`（1273）补充可信元数据（_PID/_UID/_GID/_COMM/_BOOT_ID/_MACHINE_ID…，1090 的 dispatch_message_real 组 iovec）→ `manager_write_to_journal`（965）落盘。落盘函数是一篇防御性编程范文，层层设卡：**时钟倒跳立即轮转**（982-992，保证文件内时间严格有序、二分查找才成立）；写前查轮转建议（998）；写失败且可重试则"轮转+vacuum 后再写一次"（1034-1058）；已经 vacuum 过就放弃并限速告警（1036-1040/996-1002）——任何一层都防无限循环。按 UID 选文件（manager_find_journal:994 调 475：系统日志 vs 每 UID 独立用户日志文件，隔离磁盘配额与隐私）。写成功只 `manager_schedule_sync`（1028→1883，按优先级分级延迟 sync，兼顾可靠性与 IO 吞吐）。维护路径：rotate（735）切换新文件、vacuum（838→817）按尺寸/条数清最旧、space_usage_message（214）报磁盘水位；flush_to_var（1322）以 SD_JOURNAL_ASSUME_IMMUTABLE 只读打开运行期日志再逐条转写，转写前清 seqnum 防 #30092 的误轮转（1352-1355）。

## 五、设计决策

1. **结构化优先**：条目是 FIELD=VALUE 的 iovec 数组而非文本行，索引与过滤（journalctl _PID=123）是天生的；文本协议（syslog）只作兼容入口。
2. **分级延迟 sync**（1028/1883）：每条 fsync 会压垮系统，从不 sync 则丢崩溃前日志——按消息优先级设不同延迟窗口，两端折中。
3. **时间单调性硬保证**（982-992）：宁可轮转也不容忍乱序条目，因为查询性能依赖二分——正确性约束显式写进注释。
4. **按 UID 分文件**（475）：多用户机器上单用户刷日志不能挤占系统日志配额，也避免权限交叉。
5. **失败路径全部限速+降级**：JOURNAL_LOG_RATELIMIT/FAILED_TO_WRITE_ENTRY_RATELIMIT 两级限速贯穿，"日志系统自己刷屏"是必须避免的递归灾难。

## 六、新人提示

读 journald 代码先记住身份规则：主实例的日志只走 console/kmsg（journald.c:57-67 注释讲了这个"deal"），调试它别指望 journalctl 里看到它自己的早期日志。排障三板斧：`journalctl --disk-usage`（对应 space_usage_message:214 的口径）、检查 /run/systemd/journal/flushed 标志文件（manager_flushed_flag_is_set:329，决定开机是否重新 flush）、`journalctl --verify` 校验文件完整性（FSS 走 journal_auth_init 那条线）。丢日志的常见三因：rate limit（journalctl 会打 Suppressed N messages）、sync 延迟窗口内断电、vacuum 清理。改写入逻辑务必保留 write_to_journal 的"vacuumed 标志防循环"骨架（999-1002/1036-1040），这是多年事故换来的。Kylin 工作区提示：麒麟等保场景常要求日志集中外发，正确挂点是 journald.conf 的 ForwardToSyslog/ForwardToWall 路径（manager 的 forward 设施），或在 varlink 查询面（io.systemd.journal）做转发代理——不要改落盘路径塞私货，journal 文件格式带哈希链，非标准写入会毁掉 --verify。
