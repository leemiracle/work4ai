# explain-04 · 配置装载：lib/ff_config.c（INI → 结构体 → EAL argv）

## 角色定位

ff_config.c（2138 行）是 F-Stack 唯一的事实入口：config.ini 的每个节、命令行的每个参数，都经由它汇聚成全局 ff_global_cfg（`:52`）并进一步合成 DPDK EAL 的 argv 数组（dpdk_argv/dpdk_argc `:53-54`）。它的三段式职责——默认值兜底、INI 解析分发、一致性校验——决定了"进程还没碰到网卡之前"的全部行为：lcore 掩码、端口 IP、KNI 模式、热升级参数（graceful_reload/reload_heartbeat_timeout_ms/drain_ring_size）、FreeBSD 栈的 hz 与 sysctl，全在这一个文件里定型。数据面运行期的几乎所有 if 分支，都能在 config.ini 里找到对应的那个开关。

## 内部结构

文件分四段：① 解析工具（xdigit2val `:65`、parse_lcore_mask `:79` 十六进制掩码→lcore 数组、__parse_config_list `:265` 逗号列表解析）；② 分节 handler——ini_parse_handler（`:1019`）是巨型 if-else 分发器，"dpdk" 节内联处理（MATCH 宏 `:1026`，含 graceful_reload/drain_ring_size 等热升级键 `:1045-1070`），复杂子结构委托给专门的 handler：port_cfg_handler（`:553`，按 `port%d` 节名建 struct ff_port_cfg）、vlan_cfg_handler `:664`、vip_cfg_handler `:388`、vdev/bond `:774/:831`、freebsd_conf_handler `:164`（boot/sysctl 链表）、rss_check_cfg_handler；③ 生命周期：ff_default_config（`:1651`：numa_on=1、pkt_tx_delay=BURST_TX_DRAIN_US、freebsd.hz=100、mbuf_mode=LARGE 等全套兜底）、ff_load_config（`:1696`）、ff_unload_config（FU-S2-2，逐字段 free 并 zero-init）；④ 合成段：ff_check_config（`:1397` 起）与 dpdk_args_setup（`:1194`）。

## 外部连接

上游输入有两路：main 的 argv（ff_parse_args 支持 -c/--conf、-t/--proc-type、-p/--proc-id，`long_options` 表 `:57`）与 INI 文件（ff_ini_parser.c 的 ini_parse 逐行回调，inh 风格）。下游消费者：ff_dpdk_init 直接吃 dpdk_argc/dpdk_argv 喂 rte_eal_init；ff_freebsd_init 消费 freebsd.boot 链表当 kenv 启动参数、freebsd.sysctl 链表逐项写入 sysctl；ff_dpdk_if.c/ff_dpdk_kni.c/ff_epoll.c 全都读 ff_global_cfg 的字段做运行时分支。ff_unload_config 经 atexit 注册（FU-S2-2 注释块 `:1742` 起），也供 ff_load_config 幂等重入（`:1697-1705` 先卸后装，测试与热重载场景不堆内存）。

## 数据流

装载流水线（ff_load_config `:1696`）：幂等检查→ff_default_config memset+strdup 默认值→ff_parse_args 抽命令行（proc_type/proc_id 优先级高于 INI）→ini_parse 回调 ini_parse_handler 逐键覆写→ff_check_config 语义校验→dpdk_args_setup 合成 EAL 参数。合成细节见 dpdk_args_setup（`:1194`）：-c 掩码、-n channel、--proc-type、--base-virtaddr，vdev 拼成 `--vdev=virtio_user%d,path=%s,queues=%u...`，allow 按逗号 strtok 成多个 --allow。校验细节见 ff_check_config：kni.enable 必须配 method（accept|reject，`:1399`）、kni_action 只认 alltokni|alltoff|default、每端口 addr/netmask/broadcast/gateway 四项强制（CHECK_VALID 宏 `:1430`）、端口的 lcore_list 必须都在全局掩码内（二分查找 `uint16_binary_search :220`）。热升级键有专门的负数防御：reload_heartbeat_timeout_ms（`:1047-1056` 注释直言负数经 atoi 进 unsigned 会变巨值、静默禁用失活检测，故 <=0 一律重映射默认值）。

## 设计决策

① **无 schema 的 if-else 分发**而非表驱动——牺牲优雅换取零依赖、可读性直白，且 MATCH 宏让每个键一行；代价是新增配置要同时改 handler、default、check 三处，漏一处就是"静默不生效"。② ff_unload_config 的注释（`:1742-1760`）暴露了刻意的取舍：log.dir 可能指向字符串字面量也可能指向 strdup 值，无法区分就"接受一次性 O(strlen) 泄漏换崩溃安全"（FU-CB-CFG-LOGDIR 编号挂着）——认怂注释比假装正确高明。③ vip_addr_array 的释放（`:1792`）只 free 容器不 free 元素，因为 rte_strsplit 原地切分、元素指针指进 vip_addr_str——别名语义贯穿 freebsd_conf_handler（value 别名 str，`:209`）与释放代码两处，改一处必炸另一处。④ thread_mode=1 的配置变形（`:1630-1647`）：强制 proc_type=primary、nb_threads=nb_procs、nb_procs 归一为 1——"多进程配置自动翻译成多线程"，让 start.sh 不用分叉两套配置。

## 新人提示

排查配置问题记住两句话：键名拼错不报错（ini_parse_handler 未匹配的键静默 fall through 返回 1），先开 INI 回调里的 printf（`:1024` 每键打印）确认键真的进来再查拼写；校验失败只打 stderr 不带行号，对照 ff_check_config 读。freebsd_conf_handler 的链表插入（`:210-215`）是"头后插入"——首项固定在头，其余项逆序排在后面，sysctl 有顺序依赖时别假设 INI 顺序即生效顺序。tests/unit/fixtures/ 下的 valid/invalid INI 全家桶就是这层的契约测试，加新配置键务必同步补夹具，否则 CI 的配置契约就漏了一角。
