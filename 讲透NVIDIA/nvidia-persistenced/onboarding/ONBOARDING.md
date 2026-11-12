# nvidia-persistenced 深度导览（ONBOARDING）

> 仓：/usr-data/data2/repos/agent-repos/NVIDIA/nvidia-persistenced @57f3a3f7（驱动 615.78.08，version.mk:1）
> 图谱：137 节点 / 223 边 / 7 层 / 7 步导览，fingerprints 44 文件。44 个源文件共约 1 万行纯 C。

## 1. 这个项目是什么：为什么 GPU 需要一个"驻守进程"

nvidia-persistenced 是 NVIDIA Linux 驱动的**持久化守护进程**：让 GPU 常驻"已初始化"状态，消灭每个客户进程首次打开 /dev/nvidia* 时的驱动初始化延迟。没有它，最后一个客户进程退出后驱动就会掉回未初始化态（nvidia-persistenced.c:2 的文件头注释即此定位）。它的全部运行时状态就是一张设备表：`NvPdDevice`（nvidia-persistenced.c:56-64），每台 GPU 五元组——libnvidia-cfg 句柄、PCI 信息、persistence 模式、UVM persistence 模式、NUMA 状态。

工作方式不是轮询，而是**被动服务**：主流程 `main()`（nvidia-persistenced.c:998）做完四步初始化后进入 `svc_run()`（nvidia-persistenced.c:1033）事件循环永驻，等 nvidia-smi 等客户端经 unix domain socket 发 ONC RPC 过来。所谓"维持持久状态"，本质是守护进程自己持有每台 GPU 的设备句柄不放手（`set_device_mode` 打开设备 nvidia-persistenced.c:383-394，关闭即释放）。

## 2. 源码地图：七层结构与文件分层

图谱七层（依赖方向自下而上）：

| 层 | 内容 | 代表文件 |
|---|---|---|
| L03 驱动类型基座 | 驱动共享头：nvtypes.h(844行)/nvstatus.h/nvstatuscodes.h/cpuopsys.h(442行) | 纯类型，无逻辑 |
| L03 ioctl 契约 | NV_IOCTL_MAGIC 'F'（nv-ioctl-numbers.h:33）、NV_ESC_NUMA_INFO=BASE+15（nv-ioctl-numa.h:44）、SET_NUMA_STATUS=+16（:45）、七态机 0-6（nv-ioctl-numa.h:73-79） | 与内核驱动的 ABI |
| L02 共享工具库 | common-utils/（nvgetopt.c 490 行选项解析、common-utils.c 861 行字符串/文件工具、msg.c 428 行打印）——NVIDIA 开源工具链（nvidia-settings/nvidia-xconfig 同源）共享库，src.mk:8-10 列三件套 | 可复用件 |
| L04 ONC RPC 协议层 | nvpd_rpc.h（156 行契约：NVPD_PROG=35006 :84，V1=Set/Get，V2=SetOnly/SetNuma :105-124）+ rpcgen 预生成 server/xdr 两件 | 无人手写 |
| L05 守护进程核心 | nvidia-persistenced.c(1043)/options.c/option-table.h/command_server.c/syslog-utils | 本仓心脏 |
| L06 NUMA 子系统 | nvidia-numa.c(897) + nvidia-numa.h，sysfs memory-hotplug 操作全集中于此 | 独立子系统 |
| L01/L07 构建与集成 | Makefile(185)+utils.mk(629)+dist-files.mk(62)+m4 manpage；init/ 三系模板 + install.sh(813) | 打包与部署 |

hub 节点是 common-utils/common-utils.h（fanIn=7，全仓最被依赖的头）与 nvpd_rpc.h（协议单一契约）。

## 3. 核心链路一：daemon 生命周期（fork 协议与降权）

`daemonize()`（nvidia-persistenced.c:799-996）是教科书级双进程握手：父进程先屏蔽 TTY 信号（:812-817），建 init pipe（:830），fork（:838）后父进程在 `wait_for_init_complete()`（:254）上阻塞读管道；子进程 setsid（:864）、关 stdio（:874-876）、chdir("/")（:894）、mkdir 运行时目录（:903，**只有自己建的目录才会在退出时删除**，:911-917 置 remove_dir 标志）。随后**先降权再干活**：chown 目录 → setgid → setuid（:923-942），因此守护可以以非 root 用户运行；PID 文件 /var/run/nvidia-persistenced/nvidia-persistenced.pid（nvpd_defs.h:35 + nvidia-persistenced.c:53）用 `lockf` 排他锁（:964）保证单实例。子进程全部初始化成功后经 `init_complete()`（:230）向管道写 1 字节，父进程才以 EXIT_SUCCESS 退出——systemd `Type=forking` 模板正是为此设计。

启动序列（main，:1004-1033）：parse_options → daemonize → `setup_nvidia_cfg_api`（:606，dlopen libnvidia-cfg.so.1 并 dlsym 五个函数指针 :631-645；UVM 模式未开则少加载两个符号）→ `setup_devices`（:668，经 nvCfgGetPciDevices 拿设备清单建表，注意 :702-703 硬编码 function=0）→ `setup_rpc`（:734，先 unlink 陈旧 socket :742，手工 socket() :745 再 svcunix_create :752，**V1/V2 两个版本同时注册在同一 transport** :758-763）→ svc_run()。退出走 `shutdown_daemon()`（:487）：svc_unregister 两版本（:499-500）、对每台设备回落 persistence DISABLED（:520-523）、dlclose、解 PID 锁、按 remove_dir 决定是否删目录（:566）。

## 4. 核心链路二：RPC 契约与安全模型

协议是 ONC RPC（Sun RPC）+XDR，走 libtirpc（Makefile:108-117，**硬依赖 ≥1.0.1，pkg-config 探测不到直接 $(error)**）。程序号 NVPD_PROG=35006（nvpd_rpc.h:84）：VersionOne 两过程 nvPdSetPersistenceMode=1 / nvPdGetPersistenceMode=2（:88-91）；VersionTwo 两过程 nvPdSetPersistenceModeOnly=1 / nvPdSetNumaStatus=2（:108-113）——**V2 没有 Get**，Get 只在 V1。分发器 nvpd_prog_1/nvpd_prog_2 是 rpcgen 样板（nvpd_rpc_server.c:23/71），真正的服务端实现在 command_server.c：四个 `*_svc` 函数把 RPC 参数直通到 nvidia-persistenced.c 的 `nvPd*` 实现。

安全模型一句话：**unix socket 上的 SO_PEERCRED 查 uid，非 root 拒绝**。`_nvpdIsClientRoot()`（command_server.c:37-53）经 getsockopt(req->rq_xprt->xp_sock, SOL_SOCKET, SO_PEERCRED) 拿对端凭据。但注意它只在三个 Set 入口被调（:64、:108、:131），**GetPersistenceMode 不做 root 检查**（:82-95）——只读查询放行任意本地用户。socket 文件本身位于 /var/run/nvidia-persistenced/socket（nvpd_defs.h:36-38），目录权限由 install.sh 建用户时的 0755（mkdir，nvidia-persistenced.c:903）决定。

三个 Set 语义有别：`nvPdSetDevicePersistenceMode`（nvidia-persistenced.c:109）同时动 persistence+NUMA，且**先设模式再动 NUMA、失败回滚**（:122-137，注释 :123-128 解释了顺序原因：online 需 libnvidia-cfg 先建设备节点，offline 需先释放句柄）；`...ModeOnly`（:150）只动模式；`...NumaStatus`（:171）只动 NUMA。UVM persistence 是可选第四态：`--uvm-persistence-mode` 开启后 open 设备时 `enable_uvm_persistence_mode()`（:290）轮询 nvCfgEnableUVMPersistence，遇 NV_ERR_NVLINK_FABRIC_NOT_READY 每秒重试、30 秒超时（:292 的 fabricProbeTimeoutMs=30000）。

## 5. 核心链路三：NUMA 内存上下线（nvidia-numa.c）

GPU 显存映射为 host NUMA 节点（ Grace/Hopper 一类 coherent 平台），persistenced 负责把这块内存经 Linux memory-hotplug sysfs 接口上线/下线。入口 `nvNumaOnlineMemory`（nvidia-numa.c:688）/`nvNumaOfflineMemory`（:866）。

上线的完整动作序列：解析 /proc/driver/nvidia/gpus/.../information 拿 Device Minor（`get_gpu_minor_number` :96-131）→ open /dev/nvidiaN（:152）→ ioctl NV_ESC_NUMA_INFO 拿 nid/地址/大小/memblock_size/黑名单地址（`get_gpu_numa_info` :174，结构 nv-ioctl-numa.h:56-65，黑名单上限 64 条 :47）→ 驱动说 use_auto_online 则直接罢手（:719-720）→ ioctl 置 ONLINE_IN_PROGRESS（:760）→ 对齐校验（:770-778）→ `probe_node_memory`（:443）逐块写 /sys/devices/system/memory/probe（**probe 文件不存在不算错**，:460-466，驱动自管 probe 的平台属正常）→ `check_memory_auto_online`（:594）识别 udev/内核 CONFIG_MEMORY_HOTPLUG_DEFAULT_ONLINE 抢先上线的情形：若 zone 非 Movable 打 -ENOTSUP 并警告（:585-591 的警告宏 + :655-659）→ `change_numa_node_state`（:340）逐块写 state 文件：**上线命令是 "online_movable"（:50）不是 "online"，且倒序上线**（:357-374，内核 patchwork 9625081：倒序才能落进 Movable zone；下线则正序，:376-387）→ `offline_blacklisted_pages`（:413）把 RM 报的黑名单地址逐个写 hard_offline_page 退役（:428）→ ioctl 置 ONLINE（:836）。任一步失败：先调 `offline_memory(fd)` 回滚（:852），再置 ONLINE_FAILED（:854），fd 关闭返回 NVPD_ERR_NUMA_FAILURE。

下线 `offline_memory`（:511）是同一状态机的镜像：RM 状态在 DISABLED/OFFLINE 直接 0 返回（:528-530），OFFLINE_IN_PROGRESS 视为非法（:539-542）。状态机七态（DISABLED/OFFLINE/ONLINE_IN_PROGRESS/ONLINE/ONLINE_FAILED/OFFLINE_IN_PROGRESS/OFFLINE_FAILED，nv-ioctl-numa.h:73-79）与 `mem_state_to_string`（nvidia-numa.c:72-93）一一对应，是驱动 RM 与用户态守护的共享真值。

## 6. 构建系统与 init 三系集成

构建：顶层 Makefile include utils.mk（NVIDIA 工具链共享 629 行：OUTPUTDIR/quiet_cmd/依赖自动生成），dist-files.mk:36-41 列六个 C 源（含 RPC 两件与 nvidia-numa.c），common-utils/src.mk 追加三件共享源（Makefile:77-78）。rpcgen 产物**预生成入库**（README:12-14 明说去掉构建期 rpcgen 依赖；仓库没有 .x 文件），Makefile:80-84 只是给 RPC_SRC 补 -Wno-unused-variable / -Wno-cast-function-type 压 rpcgen 代码的警告。manpage 由 m4 合成：gen-manpage-opts（宿主编译，Makefile:162-172）吃 option-table.h 生成 options.1.inc（:174），再 m4 进 nvidia-persistenced.1.m4（:177-182）。

init 集成是"三系模板 + 一个安装器"：systemd（Type=forking，ExecStopPost 直接 `rm -rf /var/run/nvidia-persistenced` 兜底，init/systemd/nvidia-persistenced.service.template:34）、SysV（chkconfig --level 2345）、Upstart（expect fork + post-stop rm -rf）。init/install.sh（813 行）自带小事务框架：`nvpdCommand`（:126）执行命令并把回滚命令前插进 cleanup_cmd 链（:136-142），失败时 `nvpdError`（:99）逆序回滚；`checkCommon` 查 sed/useradd/userdel/id（:190），`installCommon` useradd 建系统用户（-s /sbin/nologin -d '/' -r，:254-256）；探测顺序 targets="systemd upstart sysv"（:706）与 usage 声明一致（:77-78）。

## 7. 新人上路：改动路线与陷阱清单

**按目的找文件**：改守护行为→nvidia-persistenced.c；加 RPC 命令→先改（闭源驱动树里的）.x 再同步预生成件（本仓三件都标"do not edit"）；改 NUMA 上下线→nvidia-numa.c；改命令行→option-table.h（选项表）+options.c（解析）；改打包→dist-files.mk。**上手顺序**建议沿图谱 tour：README→Makefile→nvidia-persistenced.c（main/daemonize/setup_*）→command_server.c→nvpd_rpc.h→nvidia-numa.c→init/。

陷阱六条：① get_device 只匹配 domain/bus/slot，**function 字段被忽略**（nvidia-persistenced.c:208-223），且建表时 function 硬编码 0（:702-703）——RPC 参数里的 function 纯装饰；② 非法命令行参数以 EXIT_SUCCESS 退出（options.c:190），脚本判退出码会漏错；③ 命令行默认 persistence_mode=ENABLED（options.c:100），裸启动即全设备开启；④ daemonize 降权后无法删 root 拥有的运行时目录属预期（:566-577 特判 EACCES 降级为 notice）；⑤ NUMA 上线必须 Movable zone：自动上线到 Normal 会 -ENOTSUP（nvidia-numa.c:655-659），查 udev 规则与内核 CONFIG_MEMORY_HOTPLUG_DEFAULT_ONLINE；⑥ install.sh 的 -d（不删用户）与 -u 顺序敏感：-d 先出现会把 nvpd_user 清空，随后的 -u 被吞（install.sh:650-657）。

（完·锚点均经源码逐行核实）
