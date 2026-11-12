# explain-10 · conf.c：配置解析、地址探测与运行时重配置服务端

## 1. 角色定位

`conf.c`（2237 行）是守护进程的"装配车间"：解析 60 多个命令行选项与配置文件、探测宿主地址与路由、初始化转发规则表、执行用户切换，还兼任运行期配置 socket 的服务端（pesto 客户端连的就是它）。它与 `fwd.c`（扫 /proc/net 维护端口转发规则与 NAT 判定）、`fwd_rule.c`/`parse.c`（`-t/-u/-T/-U` 转发语法：all/auto/~排除）构成配置线。调用时序：`main()` 里 `conf_mode()`（`passt.c:365`）先只解析模式；随后 `conf()`（`passt.c:392`）做全部工作；`conf_tap_fd()` 则更早——`isolate_fds()`（`passt.c:348`）要在关 fd 前把 `--fd` 传的 socket 抢救出来。conf 的位置横跨特权边界：`conf_open_files()` 必须在 setuid 之前（文件要以真实 uid 打开，`conf.c:1935` 注释），`isolate_user()` 恰好嵌在 conf 流程中间（`conf.c:1937`）。

## 2. 内部结构

**入口 `conf()`（`conf.c:1241`）**：一张巨型 `getopt_long` 选项表（`conf.c:1244+`），flag 型选项（no-tcp/no-dhcp 等）直接写 `c->` 字段。解析分两遍：第一遍吃掉全部选项并处理日志/DNS/地址类参数；随后是**探测阶段**（`conf.c:1855+`）：`nl_sock_init` 起 netlink，`conf_ip4()`/`conf_ip6()` 用 netlink 探测出接口（`nl_get_ext_if`）、默认网关（`nl_route_get_def`）、地址与前缀（`nl_addr_get`，`conf.c:459-505` 的 conf_ip6 是样例）——guest 的网络参数默认"镜像宿主"，这是 passt 免配置体验的根源。探测不到外接口时走**本地模式**（`conf.c:1883-1898`）：`conf_ip4_local()`（`conf.c:436-446`）落到链路本地默认 169.254.2.1/16、网关 169.254.2.2（`conf.c:59-65`，注释注明 libslirp 用 10.0.2.x，这里刻意避开）。`map_host_loopback` 默认映射到 guest_gw（`conf.c:1902-1908`）——guest 访问"网关地址"即访问宿主回环，`--no-map-gw` 关闭。

第二遍解析（`conf.c:1913-1935`，`optind=0` 重吃）专门处理转发选项：此时 IPv4/IPv6 上下文已就绪，`fwd_rule_parse` 才能校验端口范围；`-t/-u` 填 HOST 表、`-T/-U` 填 SPLICE 表。之后 pasta 特有分支：`conf_pasta_ns()`（`conf.c:315`）处理目标 PID/PID 文件/netns 路径三元组的复杂辨析（`conf_netns_opt`，`conf.c:288`）。收尾三件事：`conf_open_files()`（`conf.c:1078`，pidfile/logfile/pcap 都在降权前打开）、`isolate_user()`（切 uid/userns，见 explain-03）、pasta 的 `pasta_open_ns`/`pasta_start_ns`。`conf_print()`（`conf.c:801`）输出启动横幅。

**DNS 处理族**（`conf.c:81-160`）是透明性的一块暗功：`add_dns_resolv4/6()` 读宿主 `/etc/resolv.conf` 收 DNS 服务器，但要做环回翻译——宿主 resolver 若是 127.0.0.53（systemd-resolved），guest 根本到不了，必须改写成 `map_host_loopback`（即 guest_gw 地址）并在 `dns_match` 里记下匹配规则，让 UDP 代理把发往该地址:53 的查询转发给宿主的真实 resolver（`conf.c:120-130` 的三段注释讲清 redirect 与 shadow 两种场景）。

**配置 socket 服务端**（`conf.c:2003-2237`，本文件的运行期角色）：`conf_listen_handler()`（`conf.c:2113`）accept（已有连接则暂拒，`conf.c:2119-2125`）；`conf_accept()`（`conf.c:2134`）发 `pesto_hello`（magic/version/PIF_NAME_SIZE/IFNAMSIZ 尺寸协商，`conf.c:2136-2141`——客户端按这些尺寸准备缓冲，跨版本安全）+ `conf_send_rules()`（`conf.c:2003`）全量推送当前规则表；`conf_handler()`（`conf.c:2199`）收客户端回写：先清 `fwd_pending[]` 各表，`conf_recv_rules()`（`conf.c:2047`）逐条读入（校验 count 上限 MAX_FWD_RULES、ifname NUL 终止），然后 `fwd_listen_switch()` 原子换表——**新旧规则表整体切换**而非逐条增删，一致性由 pending→commit 两阶段保证。FIXME 注释（`conf.c:2150-2153`、`conf.c:2208-2210`）诚实记录已知债：事务基本同步、恶意客户端可阻塞主循环。

**杂项**：`usage()`（`conf.c:528`）双模式帮助文本（guest/fwd_default 文案随模式变）；`conf_runas/conf_ugid`（`conf.c:946/998`）解析 `--runas` 的 user:group；`conf_nat()`（`conf.c:1045`）解析 `--nat` 映射；`conf_sock_listen()`（`conf.c:1124`）准备 UNIX socket 路径（含临时目录生成）。

## 3. 外部连接

依赖 netlink.c（全部地址/路由探测）、fwd.c/fwd_rule.c（转发表）、pasta.c（ns 开启）、isolation.c（isolate_user）、lineread.c（逐行读配置与 /proc）、serialise.c（配置 socket 的二进制读写原语）、pesto.h（协议常量 PESTO_SERVER_MAGIC/PESTO_PROTOCOL_VERSION 与结构布局——**协议结构体定义在 pesto.h，服务端在 conf.c**，这是这对搭档的分工）。被依赖：passt.c（conf_mode/conf/conf_tap_fd + 两个 epoll 入口 EPOLL_TYPE_CONF*）；pesto.c 客户端经 socket 消费。`--config-net` 等 pasta 选项最终驱动 pasta.c 的 ns 配置逻辑。

## 4. 数据流

典型启动：`./passt --fd 3 --tcp-ports 22` → conf_mode 判 MODE_PASST → conf()：第一遍解析（socket 路径默认 /tmp/passt.sock）→ netlink 探测出 eth0 有 192.168.1.10/24 gw 192.168.1.1 → guest 镜像这些参数（DHCP 将下发同网段地址）→ DNS 从 resolv.conf 收集 → 第二遍解析 `-t 22` 进 HOST 转发表（auto 模式还会探测宿主已监听端口）→ conf_open_files 开 pidfile → isolate_user 降权 → 回到 main 继续 tap_backend_init。运行期：`pesto --show` 连上配置 socket → conf_accept 发 hello+全量规则 → 客户端退出时 EPOLLHUP → conf_close。

## 5. 设计决策

**镜像宿主**是灵魂决策：所有网络参数（地址/前缀/网关/MTU/DNS）默认值都来自对宿主路由的探测而非硬编码，guest 与宿主"同网"，端口转发自然直通、无需 NAT 心智模型——这是 passt 与 slirp 系的根本分歧。**两遍 getopt** 是实用主义：转发规则解析依赖地址探测结果，重置 optind 再扫一遍比造选项依赖图简单得多。**环回/DNS 改写**处理"宿主本地服务对 guest 不可达"这一所有用户态网络方案共同的坑（resolver 在 127.0.0.53、服务绑 127.0.0.1），map_host_loopback+dns_match 两个机制合起来把本地地址翻译成 guest 可达的形式。**配置协议的尺寸协商**（hello 里带结构尺寸）让 pesto 客户端与服务端可以不同步升级。

## 6. 新人提示

加新选项的完整清单：选项表加行（flag 型三列即可）→ `usage()` 补帮助 → `passt.1` 补 man → 若影响转发/地址，考虑要不要进第二遍解析。排障入口：启动横幅 `conf_print()` 会打印全部生效参数（实际下发的地址/网关/DNS/规则一目了然），怀疑探测结果时 `--debug` 有每步 netlink 失败日志。坑四条：`--runas` 与文件打开顺序（conf_open_files 必须在前）耦合，动初始化顺序前重读 `conf.c:1935` 注释；本地模式（无外接口）与正常模式的地址语义不同，测试环境（容器里跑 passt）很容易触发本地模式，日志有 "use local mode" 提示；配置 socket 是同步事务，客户端半途死掉主循环可能卡在 recv——FIXME 已挂，绕法是客户端侧超时；`-t`/`-u` 的 auto 语义依赖宿主端口扫描（fwd.c），在 systemd socket-activated 端口上行为可能出人意料。
