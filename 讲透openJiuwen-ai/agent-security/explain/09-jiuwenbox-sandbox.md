# 09 · jiuwenbox 沙箱执行：bwrap/seccomp/cgroup/Landlock 与 Windows 对位件

## 一、角色定位

jiuwenbox 是本仓"执行侧"子系统：把不可信代码放进隔离环境跑。`supervisor/` 是系统调用层，Linux 与 Windows 两线各成体系：

- **Linux 线**（bwrap.py 524 行 + seccomp.py 336 行 + cgroup.py 528 行 + landlock_launcher.py 296 行 + sandbox_daemon.py 1156 行 + network.py 877 行）：以 bubblewrap 为核心四重隔离叠加——mount namespace（看见什么文件）、seccomp BPF（能调什么 syscall）、cgroup（用多少资源）、Landlock（路径级第二道闸）。
- **Windows 线**（supervisor 下 10 个 `win_*` 模块约 9700 行 + `native/softdelete/softdelete.c` 3856 行 + `server/runtime/windows/runtime.py` + 3 个 Windows 测试文件）：不用容器，用 WFP 网络过滤 + NTFS DACL + Job Object + Detours 钩子拼出对等能力。

两线共享 `SecurityPolicy` 数据模型与六份策略 YAML，由 server 侧 policy_engine 裁剪下发。

## 二、内部结构

### bwrap.py：SecurityPolicy 到 CLI 参数的纯翻译器

`BwrapConfig.from_policy`（bwrap.py:133-143）把策略对象翻译成配置，`to_args`（bwrap.py:338-522）再翻成 bwrap 命令行。模块头定位声明：真正的进程孵化在 `server/runtime/process.py`，因其需要 `pass_fds`/`preexec_fn`/`start_new_session` 旋钮（bwrap.py:2-8）。

这个文件一半的复杂度在**挂载顺序的正确性**上，三处注释都对应真实事故：

1. **bind_root_entries 先于 bind_mounts**（bwrap.py:163-181）：前者是"通配父挂载"（如 `host_root: "/"` 展开为根下每个直接子项），后者是用户显式单路径覆盖；bwrap 后挂载覆盖先挂载，通配在前才能保证显式覆盖不被冲掉。
2. **按目标深度排序 emit bind**（bwrap.py:479-497）：rw 父目录先挂、ro 子目录后挂，子目录才保持只读；同深度 ro 先于 rw，同路径 rw 才能正确覆盖 ro。注释钉着两个 dev-stable patch 号（fb0dc85de / 32a5caead）。
3. **丢弃遮蔽 bwrap 自管 tmpfs 的 bind**（bwrap.py:300-336）：bwrap 必在 `--proc`/`--dev` 目标上新挂 tmpfs，策略若把 ro-bind 叠到 /dev 上，bwrap 在 tmpfs 里 `open(O_CREAT)` /dev/null 直接 Permission denied——过滤后故障压缩为忽略单条 bind。

`--die-with-parent` 注释（bwrap.py:95-111）值得整段读：daemon 以 `start_new_session=True` 孵化、自成进程组，box-server 蒸发后无人杀它；该标志把 `PR_SET_PDEATHSIG=SIGKILL` 武装到 bwrap 监视器、pid namespace init、被启命令三级，覆盖"协作拆除"外的一切不协作死亡。

### seccomp.py：手写 BPF 字节码

不依赖 libseccomp，直接 `struct.pack` 拼 BPF 指令（seccomp.py:216-222）。过滤器四段（seccomp.py:294-306）：架构校验（不匹配 KILL_PROCESS）→ 载 syscall 号 → 逐号 inline RET ERRNO → **daemon 信号守卫** → 默认 ALLOW。

两个精妙点：

- **syscall 号解析三级降级**：优先读 `/usr/include` 头文件（x86_64/aarch64 各一组，seccomp.py:171-183）解析 `#define __NR_*`；头文件缺失落内置硬编码表（seccomp.py:94-159）。syscall 名查不到号只 warning 跳过（seccomp.py:288）。
- **daemon 信号守卫**（seccomp.py:225-271）：kill/tkill/tgkill 若目标是 0/1/2/进程组/广播（`_DAEMON_PROTECTED_KILL_TARGETS`，seccomp.py:64-72）则 EPERM——保护沙箱 PID namespace 基础设施进程。注释记录两个 BPF 跳转偏移历史 bug：错误 fall-through 会把其他 kill 目标一并 EPERM；inline RET 而非尾跳是为让守卫段不扰动 blocklist 偏移（seccomp.py:304-306, 322-324）。

clone3 返回 ENOSYS 而非 EPERM（seccomp.py:326）：glibc 遇 ENOSYS 回落老 clone，遇 EPERM 报错。

### cgroup.py：三限与 fail-closed

三限对应三 controller：`_REQUIRED_CONTROLLERS = ("memory", "cpu", "pids")`（cgroup.py:49），映射 memory_max/cpu_max/pids_max（java-policy.yaml:200-208 范本：512M/1 核/128 进程，注释明言 pids_max "caps thread/fork storms"）。v2 优先、v1 回退探测一次性 lru_cache（cgroup.py:116-134）。关键语义：**策略要求限额但 cgroup 不可写时，setup 抛 `CgroupSetupError` 中止建沙箱而非静默丢限**（cgroup.py:12-14, 39）——box 内少见的 fail-closed 点（12 篇）。

### landlock_launcher.py：零 execve 设计

沙箱内最后一层。launcher 在 bwrap 挂载完成后的沙箱里跑三步：先把 daemon 脚本**读进内存**，再对自己应用 Landlock，最后 `compile`+`exec` 在**同一 Python 进程**跑 daemon 代码（landlock_launcher.py:212-267）。为什么必须这样：Landlock 之后不再有任何 execve，daemon 及全部子进程直接继承规则集，`/jiuwenbox` 可完全留在白名单**之外**——用户代码永远读不到沙箱控制脚本（landlock_launcher.py:11-20）。`__name__` 刻意不设 `"__main__"` 绕过 daemon 底部 SystemExit 守卫、直接调 `main()`（landlock_launcher.py:224-228）。ABI 2/3 的 REFER/TRUNCATE 位按内核能力渐进放开（landlock_launcher.py:75-86）。

`compatibility` 控制失败语义：`hard_requirement` 时 Landlock 不可用直接退出码 126（landlock_launcher.py:123-127, 239-240），`best_effort`/`disabled` 继续——同一机制两种立场。

### sandbox_daemon.py：exec 摊销

沙箱常驻 daemon 在内部 Unix socket 上接 exec 请求、fork+exec 用户命令（sandbox_daemon.py:1-8）。daemon 已带全部隔离，bwrap 启动每沙箱生命周期只发生一次。控制 socket 的 listener fd 由 box-server 在孵化 bwrap **前** bind/listen 好再 `pass_fds` 传入（sandbox_daemon.py:32-40）——IPC 通道在沙箱可见路径之外，用户代码够不着也删不掉。

### Windows 对位件

| Linux 机制 | Windows 对位 | 锚点 |
|---|---|---|
| netns 网络隔离 | WFP 回环代理 | win_wfp.py:14-18 |
| cgroup 三限 | Job Object 三限 | win_job.py:6-8 |
| Landlock/bwrap 文件闸 | NTFS DACL 合成 SID | win_acl.py:5-9 |
| 无（Linux 删除即删） | softdelete.c 回收站拦截 | softdelete.c:1-40 |
| sandbox_daemon | CreateProcessWithLogonW→AsUserW | win_exec.py:1-9 |

**WFP 线**：`IP_REMOTE_ADDRESS == 127.0.0.1` + 端口范围的 Permit 过滤器放 Block 之前（win_wfp.py:551-566, 1116-1117），效果即"沙箱用户所有出站被 Block 拦截，唯一出口是回环代理端口"（win_wfp.py:14-18）。win_proxy 只绑 60080，60081-60089 留给沙箱内本地服务（win_proxy.py:716-718）。

**Job Object 线**：CPU 速率 + 进程数上限 + KILL_ON_JOB_CLOSE，内存 JOB_MEMORY+PROCESS_MEMORY 双保险（win_job.py:149-166）——与 cgroup 三限对齐。

**DACL 线**：读控制 deny-then-allow、写控制 allow-only（合成 SID `JHXSandboxWrite`），只增删沙箱 SID 的 ACE、不动 Users/Everyone 既有条目（win_acl.py:5-12）；盘符根与 Users 目录禁改（win_acl.py:166-167）。

**softdelete.c**：8 个 Detours 钩子——ntdll 层 NtClose/NtDeleteFile/NtSetInformationFile/NtCreateFile/NtOpenFile + kernelbase 层 CreateProcessInternalW/DeleteFileW/RemoveDirectoryW（定义 softdelete.c:2039/2135/2180/2275/2330/3371/3551/3592，安装 3660-3682）。删除改写为回收站移动或同卷归档改名（softdelete.c:1141-1176）；子进程注入靠 CreateProcessInternalW 给 suspend 态子进程导入表打补丁（softdelete.c:5-7）。MSYS/Git Bash 不注入（额外 DLL 使其 fork 永久等待），改用调试循环在 rm/rmdir/unlink/shred 的 main 前载入 DLL（softdelete.c:15-18）；conhost.exe 注入崩主机故跳过（softdelete.c:25-26）。**best-effort 钉在头注释**：回收站/归档/broker 不可用回落原始删除，"命令必须跑成"（softdelete.c:8-10, 34-36）。

**recycle broker**：沙箱进程以 jbx-sandbox 身份跑、写不进登录用户回收站，DLL 把绝对路径发给 box-server 上的 broker，由其以服务器身份调回收站接口；**"接口成功且原文件消失才返回成功"**（win_recycle_broker.py:7-8）——SHFileOperationW 返回后还要 `os.path.lexists` 复查，回收站不收但文件还在就挪归档（win_recycle_broker.py:434-447）。broker 端口必须落在 WFP 放行回环段内（win_recycle_broker.py:13-15），从高端口向下取、避开 60080（win_recycle_broker.py:587-593）。

## 三、外部连接

- **上游**：`server/policy_engine.py` 产出 SecurityPolicy 并守护保留路径（`_RESERVED_SANDBOX_PATHS` 防用户策略把 /jiuwenbox 塞回 Landlock 白名单）；`server/runtime/process.py` 孵化 bwrap；`server/runtime/windows/runtime.py` 走 win_exec 两跳。
- **策略源**：configs/ 六份 YAML 分级实证：default 全注释范本（isolated，default-policy.yaml:224-228）；java 同 isolated 且注释明言"Java 代码无出站连接"（java-policy.yaml:174-179）；**code-agent 是 `mode: host`**（code-agent-policy.yaml:99-100）——直接用宿主网络、跳过 namespace 防火墙，全家族最宽面；windows-policy 用专属 `wfp_loopback_proxy`（windows-policy.yaml:48-51）；enterprise-policy.yaml 无代码引用（孤儿，10 篇）；inference-policy.yaml 服务 8322 代理。
- **win_softdelete.py**：DLL 与 Python 侧环境变量契约（ENV_RECYCLE_PORT/TOKEN/ARCHIVE，win_recycle_broker.py:29-32）。
- **daemon_ipc.py**：Linux daemon 与 Windows runner 共用帧协议（win_exec.py:24-40）。

## 四、数据流

Linux 建一次沙箱的装配流：

```
box-server: bind/listen 控制 socket → pass_fds 孵化
  bwrap [六 unshare] [--die-with-parent] [--uid/--gid nobody]
        [--ro-bind 按深度排序] [--proc /proc] [--dev /dev]
        [--seccomp <memfd: arch守卫+28号blocklist+信号守卫+ALLOW>]
        -- landlock_launcher.py <b64 payload> --daemon /jiuwenbox/sandbox_daemon.py
launcher: 读 daemon 源码进内存 → no_new_privs → create_ruleset → add_rule →
          restrict_self → compile+exec daemon 同进程
box-server: cgroup 写三限 → attach bwrap PID
此后每次 exec: box-server → 沙箱内 unix socket → daemon fork+exec（继承全部隔离）
拆除: shutdown IPC / SIGKILL + die-with-parent 兜底 + cgroup teardown 杀残余
```

Windows 对应流：box-server → CreateProcessWithLogonW 起 runner（jbx-sandbox）→ CreateProcessAsUserW 起子进程（win_exec.py:3-7），同步 WFP 布防、Job Object 三限、DACL 读写轴、softdelete 注入，出网唯一通道 127.0.0.1:60080。

## 五、设计决策与权衡

1. **四层冗余防御而非单点**：mount namespace 管可见性、Landlock 管路径权限、seccomp 管 syscall 面、cgroup 管资源量。任一层被绕过其余层仍在；代价是排障需逐层定位。
2. **兼容性字段统一降级语义**：Landlock `compatibility` 三档（default-policy.yaml:156 默认 best_effort）把"内核特性缺失"从异常变成策略选择。
3. **cgroup fail-closed 与 Landlock best-effort 并存**：限额丢了抛错拒绝建箱（cgroup.py:12-14），路径强化丢了只记日志。判据是业务影响方向：资源失控伤宿主（不可接受），强化缺失退回"仍有 bwrap+seccomp"（可接受）。
4. **零 execve 是 Landlock 可信链的根基**。若 launcher 用 `execve` 起 daemon，daemon 需在 Landlock 后重读磁盘脚本，/jiuwenbox 就必须进白名单、用户代码便可读沙箱控制件（landlock_launcher.py:11-20，sandbox_daemon.py:15-24 复述）。
5. **Windows 对位件全选 best-effort 回落**：softdelete/broker 回落真删，与 cgroup 硬失败对照。Windows 无 Landlock 级兜底面，单点不回落则用户命令必挂——"命令必须跑成"压倒"删除必须软"（softdelete.c:8-10）。
6. **seccomp 黑名单而非白名单**：28 条 blocklist（default-policy.yaml:163-190）全是结构性威胁调用（kexec/reboot/mount/unshare/setns/bpf/io_uring 等），默认 ALLOW 其余——白名单在多语言 runtime 下维护成本极高，黑名单是务实折中。

## 六、新人提示与坑

- **bwrap 参数顺序是安全属性不是风格**。改 to_args 必须保住三不变量：根 bind 先于子 bind、rw 父先于 ro 子、bind_root_entries 先于 bind_mounts；`test_bwrap_bind_ordering.py` 专项守护。
- **syscall 名查不到是静默跳过**（seccomp.py:288）：arm64 上写错名（如 x86 独有的 `fork`）不报错，该限制直接消失。新增 blocklist 项要在两架构段核对。
- **cgroup 探测被 lru_cache 终身缓存**（cgroup.py:116）：mount 新 cgroup 层后再调 detect_backend 拿旧值，需 `detect_backend.cache_clear()`。
- **Windows 线的"宽"是有意的**：code-agent 的 `mode: host` 意味该档网络面=宿主网络面。六份 YAML 分级（default<java<windows 代理<code-agent host）本身就是攻击面清单。
- **softdelete 的 32 位子进程不挂钩**（softdelete.c:6-7）：x64 DLL 装不进 32 位进程，其删除是真空删。
- **enterprise-policy.yaml 是死配置**：src/ 与 tests/ 零引用（grep 实证），与 agent_moss 同属"文档态领先代码态"差集。
- **win_proxy 端口语义**：60080 代理独占，60081-60089 是"放行但 proxy 不绑"的本地服务段，沙箱内服务监听即自动可达回环外（win_proxy.py:716-718, win_recycle_broker.py:587-593）。
