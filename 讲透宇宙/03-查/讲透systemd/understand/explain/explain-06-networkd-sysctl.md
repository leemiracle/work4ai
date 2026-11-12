# explain-06 · src/network/networkd-sysctl.c — sysctl 下发与 BPF ringbuf"影子守护"

## 一、角色定位

networkd-sysctl.c（833 行）负责两件互补的事：**正向**把 .network/.conf 里的 sysctl 意图写进内核（IP 转发、rp_filter、IPv6 privacy、accept_ra、DAD、hop_limit、MPLS 等二十余项，`link_set_sysctl()`，networkd-sysctl.c:701）；**反向**用一段 cgroup BPF 程序（src/bpf/sysctl-monitor.bpf.c，SEC("cgroup/sysctl")，bpf 源:65）经 ringbuf 向用户态回报"有外部进程在偷改我们管的 sysctl"（`manager_install_sysctl_monitor()`，networkd-sysctl.c:100）。反向监控是 2025 年进入 systemd 的新趋势样本：用 eBPF 把"配置漂移检测"下沉到内核钩子，用户态零轮询。Kylin 工作区把它列为焦点正合适——它是 eBPF 可观测性进入主流系统软件的教科书案例，且安装时机与 capability 生命周期强耦合（见 networkd-manager.c:883-892）。

## 二、内部结构

安装链路 `manager_install_sysctl_monitor`（networkd-sysctl.c:100-165）六步：dlopen libbpf（111，LIBBPF_NOTE recommended，不可用则降级跳过：112-115）；取自身 cgroup 路径并打开根 cgroup fd（117-123）；`sysctl_monitor_bpf__open_and_load` 加载 CO-RE 骨架（125）；把自己 cgroup 的 fd 塞进 `cgroup_map`（134）——BPF 侧用它排除 networkd 自己的写（`bpf_current_task_under_cgroup`，bpf 源:89）；把程序 attach 到根 cgroup 的 sysctl 钩子（137）；把 `written_sysctls` ringbuf map 包成 libbpf ring_buffer 并挂 sd_event io 源（142-155，回调 on_ringbuf_io:89，poll timeout=0 纯 drain）。事件结构 `sysctl_write_event`（src/bpf/sysctl-write-event.h:28+）带版本号防布局漂移（用户态 version!=1 即停用监控，networkd-sysctl.c:50-52）、pid/cgroup_id/comm、路径与新旧值；头文件注释保留了一个真实工程细节：BPF 栈仅 512 字节，成员尺寸是被它掐着的。

正向写入侧，`sysctl_shadow`（Manager 上的 Hashmap）是两者的接合部：每次 networkd 写 sysctl（`sysctl_write_ip_property_*` 系列都带 `manager_get_sysctl_shadow(...)` 参数）都会把"我期望的值"记进影子表；BPF 事件回来时 `sysctl_event_handler`（networkd-sysctl.c:42）先查影子表——没管过的路径直接忽略（68-70），管过但新值与期望值不符才告警（72-84）。

## 三、外部连接

上游：`manager_start()` 在网络配置开始前安装监控（networkd-manager.c:883），装完立即丢弃 CAP_SYS_ADMIN/CAP_BPF（networkd-manager.c:887-892）——BPF 加载特权只存活在启动窗口；`manager_set_sysctl`（networkd-sysctl.c:232）写全局 IPv4/IPv6 forwarding。per-link 入口在 link_configure（networkd-link.c:1327 调 link_set_sysctl）。下游全是内核 /proc/sys：manager 级写 default/all 前缀（networkd-sysctl.c:216-226），link 级写 conf/<ifname>/ 前缀；`link_clear_sysctl_shadows`（178）在网卡消失时按 ipv4/ipv6 conf 前缀清影子表（185-194）。日志契约：两条 warning 文案被 test-network/systemd-networkd-tests.py 断言（networkd-sysctl.c:55-56/73-74 注释明言改文案须同步测试），结构化字段 OBJECT_PID/OBJECT_COMM/SYSCTL/OLDVALUE/NEWVALUE/OURVALUE（77-83）。

## 四、数据流

正向：.network 解析出 Link 值 → `link_set_sysctl()`（701）顺序调二十余个 link_set_* 小函数，每个都先 `link_is_configured_for_family` 滤族（如 378），未配置项返回 0 跳过，写失败仅 warning 不阻断（link 层调用处全用 log_*.errno + ignoring 模式）。特殊联动：`link_set_ip_forwarding`（370）处理 IPMasquerade= 的全局升级——某口开伪装而全局 forwarding 未设时，直接置全局并**对所有 link 重放** per-link 设置（383-399，因为内核的 all/ 转发语义会波及每块网卡）。

反向：任意进程 write /proc/sys/net/** → cgroup/sysctl BPF 钩子触发 → 过滤 net/ 前缀（bpf 源:104）、排除自身 cgroup → 事件推入 ringbuf → sd_event EPOLLIN → `on_ringbuf_io` drain（networkd-sysctl.c:93）→ `sysctl_event_handler` 影子表比对 → 冲突则发 SD_MESSAGE_SYSCTL_CHANGED 结构化告警，附上"是谁（comm+pid）、从什么改成什么、我们期望什么"全套证据（80-84）。注意**只告警不回滚**——设计上是配置漂移的审计面而非强制执行面。

## 五、设计决策

1. **影子表而非重读内核**：期望值在写入时记下（write-through cache），比对 O(1) 且不受读取竞争影响；管不到的路径不告警，消除噪音。
2. **监控自身也最小权限**：attach 到根 cgroup 但只认 cgroup_map 里登记的自己（自排除模式），无需在 BPF 里 hardcode pid；capability 用完即弃。
3. **优雅降级贯穿始终**：无 libbpf、加载失败、attach 失败全部 warning 后继续跑（112-115/126-128/139-140）——监控是增强不是依赖，嵌入式裁剪 BPF 的内核也照常工作。
4. **版本化 ABI**：ringbuf 事件首字段 version（sysctl-write-event.h:31，全路径 src/bpf/），用户态见到未知版本整体停用（50-52），防内核/BPF 侧演进把垃圾读成事件。
5. **warning 即测试契约**：文案改动须同步集成测试（55-56 注释），把可观测性输出当 API 管理。

## 六、新人提示

复现监控效果最简单的办法：`networkctl` 配好接口后手动 `sysctl -w net.ipv4.conf.eth0.forwarding=0`，journal 里应立刻出现 "Foreign process ... changed sysctl"（networkd-sysctl.c:83 文案）；若想看它认了哪些影子项，debug 日志的 sysctl 写入路径都会带出。改 BPF 侧记得 512 字节栈限制（write-event.h 头注释）与 vmlinux.h CO-RE 重编译（meson 的 bpftool 子目标）。Kylin 工作区两点提醒：其一，麒麟内核若裁掉 cgroup BPF 或 CGROUP_SYSCTL 钩子，manager 会走 126-128 的 load 失败降级路径——功能"静默缺失"是预期行为而非 bug，排查时先看 journal 的 LOG_INFO 一行；其二，该机制是"检测"不是"防护"，等保类需求若要求配置漂移**阻断**，需在 SD_MESSAGE_SYSCTL_CHANGED_STR 消费侧（如 audit/EDR）联动，systemd 本体不提供回写纠正。新增 sysctl 配置项的标准动作：写 link_set_xxx 小函数 + 挂进 link_set_sysctl 序列 + 全部带 shadow 参数，忘记带 shadow 会绕过漂移检测。
