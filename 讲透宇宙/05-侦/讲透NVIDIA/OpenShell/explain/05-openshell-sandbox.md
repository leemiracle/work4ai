# 05 · openshell-sandbox：沙箱内的隔离边界运行时

## 一、角色定位

`openshell-sandbox` 是跑在**沙箱内部**的监督器二进制——不是从外部"关住"工作负载的容器，而是工作负载自己的守门进程。crate 文档只有一句（crates/openshell-sandbox/src/lib.rs:4）："Capability-free in-workload sandbox boundary"（无特权能力的负载内边界）。它假设自己以普通 UID、零 capability 运行，靠 Landlock + seccomp-notify 这类无特权内核原语完成自证明与自我约束：启动时主动鉴定运行时资格（不合格直接 fail-fast），然后拉起受保护的边界服务，接管 workload 的所有 exec 与网络出口。任务书提到的 `compute/mod.rs` 实际属于 `openshell-server`（15,710 行、内嵌大量 cfg(test) impl），与本 crate 无涉——本篇按源码实际聚焦 boundary 四件套。

## 二、内部结构

**资格鉴定（Phase 0 探针）**：`RuntimeQualification`（crates/openshell-sandbox/src/lib.rs:35-43）固化八项硬证据：seccomp 证据、landlock_abi 版本、landlock allow/deny 双向、UDP/TCP DNS 往返、TCP 允许/拒绝往返。`qualify_runtime()`（crates/openshell-sandbox/src/main.rs:113）逐项主动探测而非读文档——例如 `probe_dns_relay_bind`（crates/openshell-sandbox/src/main.rs:238）要求 `net.ipv4.ip_unprivileged_port_start=0` 并真的在 127.0.0.53:53 绑定 TCP+UDP；Landlock 必须 **ABI ≥ 3**（crates/openshell-sandbox/src/main.rs:170-173，理由是自保护需要 truncation 支持）；`probe_landlock_allow_deny`（:262）在"全新受信子进程"里装一条硬 allow-list 验证一放一拒（注释 crates/openshell-sandbox/src/main.rs:258-260：Landlock 不可逆，只能拿子进程做实验）；`probe_socket_virtualization`（:363）验证 seccomp 通知拦截 socket 系统调用的能力。二进制还内置一组子命令：`copy-self`（crates/openshell-sandbox/src/main.rs:16，init 容器让二进制自己把自己拷进共享卷，**不借助 sh/cp**——宿主侧工具面越小越安全）、`bootstrap`、`seed-workspace`、`capability-probe` 等（crates/openshell-sandbox/src/main.rs:17-33）。

**boundary_server.rs（5528 行，入口编排）**：`run_boundary`（boundary_server.rs:194-249）是启动序列的骨架，顺序即安全属性：①装信号处理器（:198，SIGTERM/SIGINT 只置原子标志 :189-192，async-signal-safe）；②`make_boundary_nondumpable`（:199→:251-262，`prctl(PR_SET_DUMPABLE,0)`——此后密钥都在内存，不可被 ptrace/dump）；③`disable_core_dumps`（:200→:264-278，RLIMIT_CORE 归零）；④读+校验配置（:206-207 `validate_config` + 资源声明校验）；⑤**校验运行身份**（:208-211 `validate_running_identity`，:417 定义——UID/GID/补充组必须与驱动声明一致）；⑥**消费即删除**一次性 bootstrap 配置（:212-214 `remove_file`，单用凭据不留盘）；⑦序列化子环境到 `USER_ENVIRONMENT` 环境变量（:220-222，只对 workload 子进程生效）；⑧`apply_supervisor_startup_hardening`（:223，定义在 sandbox/mod.rs:42）；⑨PID 1 时启动孤儿收割器（:225-228）；⑩起 workload launcher 与 **NetworkBroker**（:229/:235），最后 tokio 多线程 runtime 上 `serve`（:248）。控制面监听三形态 TlsTcp/Unix/Vsock（:231-233），TlsTcp 端口作为"受保护控制端口"传给 broker 防自环。

**boundary_exec.rs（1064 行，RFC 0012 的负载侧实现）**：`LocalBoundaryExec`（boundary_exec.rs:32-43）是唯一执行器——每次 spawn 复用同一份已准入策略与执行环境控制，但取**新鲜的 provider 凭据快照**（:24-26 注释）。`async fn exec`（:422）分两路：`spawn_piped`（:209，管道 stdio）与 `spawn_pty`（:301，openpty 终端会话）；`command()`（:124）按策略组装 argv/env；`prepare_sandbox`（:198）落地身份切换。测试锚点直陈边界语义：`exec_rejects_after_boundary_end`（:907）——边界结束后拒绝一切 exec；`failed_exec_leaves_boundary_active_without_registered_processes`（:925）——失败 exec 不留注册进程也不伤边界。

**network_broker.rs（2646 行，seccomp-notify 网络中介）**：文档（network_broker.rs:4）"Seccomp-notification broker owned by the in-workload sandbox"。它持有 NotificationListener，拦截 workload 的 connect/DNS 系统调用，向监督器（网关侧）请求放行决定。容量与超时全是常量（:28-45）：SOCKET_CAPACITY=4096、OPEN/DNS 队列 256、DNS_QUERY_TIMEOUT=10s、**NETWORK_DECISION_TIMEOUT=30s**（监督器超时即挂起，不默认放行）、DNS 中继固定 **127.0.0.53:53**（:40-43）。`NetworkBroker::start`（:217）→ `start_with_dns_address`（:233）→ `start_with_decision_timeout`（:246）；`confirm_healthy`（:350）供启动自检。测试名即威胁模型：`protected_control_port_rejects_loopback_aliases_and_pod_addresses`（:2206）、`external_connect_waits_for_explicit_relay_decision`（:2376）、`denied_external_connect_keeps_socket_unconnected`（:2416，拒绝的 socket 必须保持未连接态）、`inherited_dns_socket_after_exec_never_claims_the_connecting_binary`（:2149，防归因欺骗）。

**process.rs（1605 行，进程管理）**：`strip_proxy_env`（crates/openshell-sandbox/src/process.rs:146）剥掉代理环境变量防凭据泄漏给子进程；`harden_child_process`（:241）子进程硬化；`spawn_command_with_workload_launcher`（:342）统一经 launcher（而非裸 spawn）派生——保证每个 workload 子进程都继承 Landlock/seccomp 约束。Landlock（sandbox/linux/landlock.rs，890 行）与 seccomp（seccomp.rs，892 行）两个内核绑定层在此目录。

## 三、外部连接

上游：`openshell-isolation-interface` 提供 contract trait（BoundaryExec/ExecSpec/ExecSession，boundary_exec.rs:15-21）与 Linux 原语（workload_launcher、seccomp_notify、landlock、task_memory、socket_registry）；`openshell-sandbox-backend` 的 boundary_protocol 定义 SeccompEvidence；`openshell-binary-identity` 的 ProcfsIdentityResolver（network_broker.rs:22）解析连接发起者身份。下游：各计算驱动把该二进制注入沙箱镜像；它与网关的 ConnectSupervisor 会话由 supervisor 侧组装。

## 四、数据流

驱动注入一次性 bootstrap → main 解析子命令 → capability-probe 产出 QualificationReport（JSON）→ 不合格 fail-fast → run_boundary 加固+消费配置 → workload launcher + NetworkBroker 就位 → serve 控制面 → workload 进程发起 connect → seccomp 通知挂起 → broker 查 socket 注册表与 /proc 身份 → 监督器决策（30s 超时不放行）→ 放行走 L7 检查链或拒绝并记录 DenialEvent。

## 五、设计决策

1. **主动鉴定优于环境假设**：八项探针全部"跑一遍"而非读内核版本表——能力缺失在启动秒级暴露，而非首次渗出时。
2. **自保护先于服务**：nondumpable/core-dump 禁用排在读配置之前（:198-200），内存中的密钥先立于不可采集之地。
3. **一次性凭据**：bootstrap 文件读后即删（:212），重放窗口收敛到进程启动瞬间。
4. **fail-closed 计时器**：网络决定 30 秒超时宁可挂死也不默认放行——可用性换安全性。
5. **纯 Rust 自拷贝**：copy-self 子命令消掉对宿主 sh/cp 的依赖，镜像面最小化。

## 六、新人提示

- 本 crate 大量模块带 `#[cfg(target_os = "linux")]`（crates/openshell-sandbox/src/lib.rs:9-29），非 Linux 只有占位 `RuntimeQualification`（crates/openshell-sandbox/src/lib.rs:47-49）——在 mac 上编译通过≠能跑。
- DNS 中继地址 127.0.0.53:53 与 `ip_unprivileged_port_start=0` 强耦合（crates/openshell-sandbox/src/main.rs:238-253），K8s 节点 sysctl 不满足时资格鉴定直接失败，报错文案会点名该 sysctl。
- boundary_exec 的 exec 在边界结束后永久拒绝（:907 测试），设计上没有"优雅关闭宽限期"——不要试图加。
- 拒绝的 connect 保持 socket 未连接（:2416）是刻意证据语义；让连接半开再重置会破坏归因审计。
- 任务书所说"cfg(test) 占 56% 的 compute/mod.rs"在 openshell-server/crates 下，不在本 crate——引用行号前先 `find` 落位。
