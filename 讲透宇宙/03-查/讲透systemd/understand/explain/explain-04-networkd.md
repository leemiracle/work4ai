# explain-04 · src/network/networkd.c + networkd-manager.c — networkd 主循环：事件源装配与请求队列

## 一、角色定位

systemd-networkd 是"声明式网络配置守护进程"：读 /etc/systemd/network/*.network 与 .netdev，把内核 rtnl 事件流（网卡通断、地址路由变化）驱动成期望状态。本仓采用瘦入口+胖实体架构：networkd.c 仅 130 行，`run_networkd()`（networkd.c:34）只做进程级准备——COMMAND 元数据声明（networkd.c:24）、解析参数、**降权**（以 systemd-network 用户运行但保留六个 capability：CAP_NET_ADMIN/BIND_SERVICE/BROADCAST/RAW/SYS_ADMIN/BPF，networkd.c:73-79）、创建 /run/systemd/netif 运行时目录（networkd.c:86-93）、然后依次调 manager_new → manager_setup → manager_parse_config_file → manager_load_config → manager_enumerate → manager_deserialize → manager_start（networkd.c:95-121），最后 `sd_event_loop(m->event)`（networkd.c:125）交出控制权。真正的循环机制在 networkd-manager.c（1427 行）：事件源装配、14 类 rtnl 回调注册、请求队列驱动与优雅退出状态机。

## 二、内部结构

`manager_setup()`（networkd-manager.c:637）是装配清单：默认事件循环（643）、五个信号源——SIGTERM/SIGINT 终止、SIGUSR2 重启、SIGHUP 重载、SIGRTMIN+18（networkd-manager.c:648-652）——加 memory_pressure（654）与关键的 **post 事件源**（658，`manager_post_handler`，每轮循环尾都跑）；随后接通 rtnl/genl/nfnl 三条 netlink、varlink 三个端点（本体 io.systemd.Network、metrics、resolve hook）、D-Bus、udev 监视、hostname inotify、sd_resolve 异步解析器、地址池（662-717 区段）。`manager_connect_rtnl()`（networkd-manager.c:374）注册 14 类消息回调：RTM_NEWLINK/DELLINK→process_link、QDISC/TCLASS（流量控制）、NEWADDR/DELADDR、NEWNEIGH/DELNEIGH、NEWROUTE/DELROUTE、NEWRULE/DELRULE、NEWNEXTHOP/DELNEXTHOP（networkd-manager.c:403-465），最后 `manager_setup_rtnl_filter`（467）在内核侧装 BPF 过滤器削减不关心的事件洪峰。`Manager` 结构体里两条核心队列：`request_queue` 与 `remove_request_queue`（networkd-manager.h:128-129，OrderedSet）——所有配置下发（地址/路由/邻居/规则）都先成为 Request 对象去重入队（networkd-queue.c:175-194，注释强调循环内重入的 `request_queued` 标志）。

## 三、外部连接

上游内核面：rtnl（配置）、genl（wireless 等）、nfnl（防火墙）；设备面：udev monitor（networkd-manager.c:189 manager_connect_udev，match udev 事件决定 link 何时纳入管理）；服务面：D-Bus（manager_connect_bus:114，含 prepare-for-sleep 睡眠回调:70）与 varlink（manager_varlink_init 系列）。下游消费者：systemd-resolved（取接口 DNS 配置）、journald（日志）、speed meter（traffic 统计）。与其他 daemon 的一个精巧耦合：manager_start 里先 `manager_install_sysctl_monitor`（networkd-manager.c:883，BPF ringbuf 监控 sysctl 写入，详见 explain-06），装完立即 drop CAP_SYS_ADMIN 与 CAP_BPF（networkd-manager.c:884-892，887/891 两处 drop_capability，注释言明"加载 BPF 需要这两个能力，装完无论成败都弃"）——capability 生命周期被压缩到启动窗口内。

## 四、数据流

稳态数据流全部汇入 post handler：`manager_post_handler()`（networkd-manager.c:470）每轮循环末执行——MANAGER_RUNNING 态依次 `manager_process_requests`（把去重后的 Request 队列真正下发 rtnl）与 `manager_clean_all`（清理过期对象）（networkd-manager.c:479-480）。事件路径：rtnl 消息（如 RTM_NEWLINK）→ manager_rtnl_process_link → link 状态机推进（见 explain-05）→ 产生配置 Request 入队 → 下一轮 post 下发。退出路径是显式三态机：`manager_stop()`（networkd-manager.c:504）把状态从 RUNNING 拨到 TERMINATING/RESTARTING，对所有 link 调 `link_stop_engines`（networkd-manager.c:529-530，可能保动态地址）；post handler 在 TERMINATING 态持续检查两件事——remove_request 队列已清空、三条 netlink 的 reply callback 计数归零（networkd-manager.c:485-491）——都满足才 `manager_serialize` 落盘状态文件、`sd_event_exit` 退出（networkd-manager.c:493-495）。这个"等租约释放与在途应答"的协议就是 networkd 重启不掉线的原因：新进程经 manager_deserialize（networkd.c:115）接手。启动路径 manager_start（networkd-manager.c:875）则负责冷启动收尾：把 PENDING 态 link 逐个 `link_check_initialized`（903-909）、写 manager 与 link 状态文件（913-918）。

## 五、设计决策

1. **post 事件源做集中驱动**：不用定时器轮询，而用 sd-event 的 post 源在"每轮循环做过事之后"跑队列，天然与事件合并——rtnl 事件再密集也只按轮次批量下发。
2. **请求去重队列**：同一前缀/同一地址的重复请求在 OrderedSet 里按 hash 合并（networkd-queue.c:175），10 个来源要配同一地址只发一次 netlink——幂等性与防抖在同层解决。
3. **最小特权窗口**：CAP_SYS_ADMIN/CAP_BPF 只为装 BPF 存活数毫秒（networkd-manager.c:884-890），运行期网络管理只靠 CAP_NET_ADMIN；配合 networkd.c:73-79 的白名单式降权，攻击面收敛。
4. **内核侧 rtnl 过滤**：manager_setup_rtnl_filter（networkd-manager.c:340）把过滤下沉到内核，用户态不再被无关组播事件唤醒——嵌入式/大内存压力场景的省电关键。
5. **序列化重启协议**：退出前必须等三个 netlink 的 reply 计数归零（488-491），杜绝"新进程重复下发半途请求"。

## 六、新人提示

读 networkd 别从 networkd.c 找逻辑——它是现代 systemd daemon 的标准瘦壳样板（COMMAND 宏+run 函数），真正要读的是 manager_setup 的装配顺序与 manager_post_handler 的三态分支。排障三板斧：`networkctl status`（读的就是 link 状态文件，manager_save/networkd-manager.c:913 写的那份）、`SYSTEMD_LOG_LEVEL=debug systemd-networkd` 前台跑、以及检查 /run/systemd/netif/ 目录（networkd.c:86-89 创建的 leases/links/）。理解"为什么我的配置没生效"时先想请求队列：配置改了但 Request 尚在队列、或被去重合并，都会表现为"看起来没动作"——debug 日志里 request attach/detach 是关键词。Kylin 工作区提示：若要加自定义链路监控（如麒麟网卡命名或国产网卡驱动事件），正确的挂点是 manager_connect_rtnl 的 netlink_add_match 家族与 udev match（189 区段），不要在 link 状态机里直接 hook。
