# 07 · 运维线：GPU 数据中心操作系统

> 系列第 07 篇：**千卡集群的驱动/监控/切分/信任链**。原料：nvidia-container-toolkit@a672e378 · libnvidia-container@24a848d · gpu-operator@3e1873a · DCGM@64df9f8(4.6.1) · dcgm-exporter@fafd151(4.8.4) · mig-parted@26d51f55 · k8s-device-plugin@d7265fd · enroot@ead3a25 · pyxis@0.24.0 · nvtrust@2026.10 + deepwiki 16 仓 + 横切底座 NVIDIA-CUDA-STACK.md。行号锚 2026-11-04 于 `/usr-data/data2/repos/agent-repos/NVIDIA/` 逐一核实（下文锚省略该前缀，写法 `<repo 相对路径>:<行>`）。

## 一、第一性原理设问：为什么 GPU 集群需要一套"操作系统"

CPU 服务器虚拟化成熟三十年：内存可换页、进程可抢占、时间片轮转代价微秒级。GPU 的三条物理事实全部相反——**显存不可换页**（换出等于上下文销毁，训练作业一天白跑）、**计算不可抢占**（kernel 一旦上 SM 只能跑完或杀进程）、**驱动是内核态单例**（一个内核模块服务全机所有卡）。于是 GPU 是"共享稀缺资源"里最难共享的一类：一台 8×H100 数十万人民币，10GB 显存的推理租户独占 80GB 卡是浪费，两个租户裸共享一张卡则互相踩显存、踩带宽、踩故障域。

整条运维线就是这个矛盾的六次分解，每层解决一个子矛盾：

| 层 | 子矛盾 | 解 |
|---|---|---|
| 驱动/固件（内核态） | 内核态单例 vs 千节点版本漂移 | 驱动留在宿主，容器只装用户态库 |
| 容器化（用户态隔离） | 镜像可移植 vs 驱动必须匹配宿主 | nvidia-container-toolkit：设备节点+驱动库按需注入 |
| 编排（K8s 调度） | 调度器不认识 GPU vs 节点异构滚动升级 | device-plugin 扩展资源 + gpu-operator 声明式收敛 |
| 可观测（DCGM） | nvidia-smi 人肉轮询 vs 秒级千卡告警 | DCGM 字段体系 → exporter → Prometheus |
| 切分（MIG） | 整卡粗粒度 vs 小负载多租户 | MIG 硬件切分 / vGPU 时间片 / MPS 共享 |
| 信任（nvtrust） | 物理共处互不信任 | CC mode + attestation |

把这张表竖着读：抽象硬件（驱动）、隔离执行（容器）、分配资源（调度）、监控健康（DCGM）、切分供给（MIG）、证明清白（attestation）——正是一台计算机的操作系统干的六件事。运维线 = **GPU 数据中心的内核**。

## 二、直觉层：把千卡集群当一台计算机用

**nvidia-container-toolkit = 动态链接器**。容器镜像里没有驱动库（驱动跟宿主内核绑死，装进镜像必炸），就像可执行文件不自带 libc；toolkit 在容器启动瞬间干 ld.so 的活——把宿主的 libcuda/libnvidia-ml 连同 /dev/nvidia* 设备节点"链接"进容器视野，且按 capability（compute/utility/graphics）决定链接哪几样。

**gpu-operator = 声明式 init 系统**。传统装机是运维在每台节点跑 20 条命令；operator 把"GPU 节点该长什么样"写成一份 ClusterPolicy CRD，控制循环不停对比现状与声明并补差——相当于包管理器永远在后台 `make install`，节点加一台收敛一台，驱动升一级滚动一轮。为什么必须 operator 化：集群里同时存在多代 GPU（A100/H100/B200）、多种 OS、多个内核小版本，手工运维的组合数爆炸，只有"声明 + 收敛"可扩展。

**DCGM = /proc + SMART**。nvidia-smi 是给人看的一次性快照；DCGM 把 GPU 状态变成字段 ID 宇宙（`DCGM/dcgmmlib/dcgm_fields.h` 一个头文件 3993 行），守护进程后台按频率采样进 cache，exporter 再翻译成 Prometheus 指标——GPU 的 procfs。

**MIG = NUMA 硬分区**。软件时间片（驱动轮转多个 context）像 CPU 分时——便宜但互踩；MIG 把一张卡的 GPC/L2/显存通道物理切成最多 7 份——像 NUMA 硬分区，一份的故障与带宽劣化不扩散到别份。

**nvtrust = Secure Boot**。开机度量 GPU 固件与驱动、签发令牌，证明"这张卡跑的确实是 NVIDIA 签名的镜像"，是多租户云里租户与宿主互不信任时的信任根。

## 三、机制层：六层怎么落到代码

### 3.1 容器化为什么难：CDI 与 legacy 两条注入路径

容器跑 CUDA 需要四类宿主资源：字符设备（/dev/nvidia0、nvidiactl、nvidia-uvm、MIG 的 nvidia-caps/*）、驱动用户库（libcuda.so、libnvidia-ml.so…）、IPC socket（persistenced/fabricmanager）、固件——外加一件"容器内收尾"的活（符号链接+ld 缓存）。工具包本体是一个 OCI runtime wrapper：`nvidia-container-toolkit/internal/runtime/runtime_factory.go:59` 把低层运行时包进 ModifyingRuntimeWrapper，按四种模式构造 spec 修改器（`nvidia-container-toolkit/internal/modifier/mode.go:13-23`：legacy / csv / cdi / jit-cdi；csv 是驱动跑在容器里、无宿主设备树时的清单模式）。

**legacy 链（docker 默认路径）**：wrapper 往 OCI spec 塞一个 prestart hook（`nvidia-container-toolkit/internal/modifier/stable.go:65-68`）→ 容器创建前执行 nvidia-container-runtime-hook，它先断言自己处于 legacy 模式（`nvidia-container-toolkit/cmd/nvidia-container-runtime-hook/main.go:85` assertModeIsLegacy），然后拼出 `nvidia-container-cli configure` 并 exec（`:115`、`:154` syscall.Exec）→ libnvidia-container 的 `nvc_driver_mount`（`libnvidia-container/src/nvc_mount.c:694`）enter 容器 mount namespace（`:705` ns_enter），依次挂 procfs、驱动 bins/libs/固件（`:727-764`）、IPC socket 与设备节点——两者都按 capability 门控：persistenced/fabricmanager socket 只给 utility（`:767-776`），UVM 等计算设备只给 compute（`:779` 起）；MIG 设备走 nvidia-capabilities 专用节点（`:631` cap_device_mount），并解析 procfs 的 MIG minors 清单把设备号加进容器 cgroup 白名单（`:662` setup_mig_minor_cgroups）。注入完还要在容器里重建符号链接（`:746` symlink_libraries）+ 刷 ld 缓存，否则 dlopen 找不到库。

**CDI 链（K8s 现行路径）**：`nvidia-ctk cdi generate` 预先枚举本机 GPU/MIG，产出一份声明式 YAML（默认目录 `/var/run/cdi`，`nvidia-container-toolkit/cmd/nvidia-ctk-installer/toolkit/toolkit.go:175-180`），内含 devices/mounts/hooks 三段；调度后 device plugin 把 CDI 设备名写进容器注解，containerd/cri-o 按 spec 注入——NVIDIA 私有 runtime 不再挂在链路中间。容器内的细活改由六个 hook 子命令在 OCI 生命周期执行（`nvidia-container-toolkit/internal/discover/hooks.go:48-63`）：create-symlinks、update-ldcache、enable-cuda-compat、disable-device-node-modification、apply-cuda-memory-limits、update-application-profile，挂点覆盖 createRuntime/createContainer/startContainer 三个时点（`:33-38`）。jit-cdi 更进一步：spec 不落盘、运行时现场生成。

闭环在 NVML：整条运维工具链（device plugin、DCGM、mig-parted、toolkit 的资源发现）探测 GPU 全靠 dlopen `libnvidia-ml.so.1`（go-nvml `go-nvml/pkg/nvml/lib.go:30-31`，RTLD_LAZY|RTLD_GLOBAL）——这正是注入链里那只库。**容器里 NVML 能否初始化，就是注入链通没通的试纸。**

### 3.2 编排：从设备插件到 gpu-operator 的声明式收敛

K8s 原生不认识 GPU。device plugin 向 kubelet 注册 `nvidia.com/gpu` 扩展资源，ListAndWatch 上报设备清单与健康变化（`k8s-device-plugin/internal/plugin/server.go:267-285`）；Allocate 时若启用 CDI 策略则把设备名写进注解（`:329-334`）。注意 `:277` 的源码 FIXME：设备一旦标 Unhealthy **永不恢复**——生产必须配自愈（重启插件 pod 或节点）。

gpu-operator 把"装驱动→装 toolkit→装插件→装监控"变成一次状态机收敛。安装顺序硬编码于 `gpu-operator/controllers/state_manager.go:798-818`：pre-requisites → **state-driver → state-container-toolkit → state-operator-validation → state-device-plugin → state-mps-control-daemon → state-dcgm → state-dcgm-exporter → gpu-feature-discovery → state-mig-manager** → node-status-exporter → sandbox 系（vgpu/vfio/kata/cc-manager）。这个顺序就是依赖顺序：没有驱动没有 toolkit，没有 toolkit 插件拿不到 CDI spec，没有插件 DCGM exporter 没有调度语义。`step()`（`:955-993`）逐态推进、NotReady 即停——声明式系统里保留了确定性的安装序。各组件落点由节点标签矩阵控制（`:98-126` 的 nvidia.com/gpu.deploy.* 系列标签决定 DaemonSet 落哪些节点）；机架级配线方面，驱动 DaemonSet 直接挂 /run/nvidia-fabricmanager socket 供 NVLink fabric 管理（`gpu-operator/assets/state-driver/0500_daemonset.yaml:114-115`）。驱动正走向独立 NVIDIADriver CRD（`:965-976` 检测到即接管，orphan 清理 ClusterPolicy 的 driver DaemonSet）；拓扑感知调度从"标签约定"走向 DRA 一等资源模型（GPUCluster/ComputeDomain CRD，`:131-137`）是 2026 年最大的增量。两个源码级陷阱：MIG manager 落点判断硬编码产品名 contains h100/a100/a30（`:341-360`），新卡必须先有 mig.capable 标签；无 MIG 标签时 operator 不部署 mig-manager，切分能力静默缺席。

### 3.3 可观测：DCGM 的字段宇宙与故障先兆

架构（deepwiki 与源码同证）：`nv-hostengine` 守护进程 + 可插拔模块（diag/nvswitch/sysmon/health/policy/profiling）+ 中央 DcgmCacheManager + 统一 API 库 dcgm.so（嵌入式进程内 / 远程连守护两种模式）；GPU 走 NVML，**NVSwitch 走 NSCQ 不是 NVML**——DCGM ≠ NVML 封装。字段体系恰好覆盖任务书说的 engine/memory/port 三类计量：引擎占用族（`DCGM/dcgmmlib/dcgm_fields.h:2538` GR_ENGINE=1001、`:2557` TENSOR=1004、`:2563` DRAM=1005，另有 FP64/32/16 管线占比）、端口流量（`:2586-2606` PCIE/NVLINK TX/RX bytes=1009-1012）、链路健康（`:1278-1308` NVLink CRC FLIT 逐 lane 错误=400-409）。

故障先兆按"预告程度"排序读：**ECC SBE 计数爬升**（=310/312，可纠错但预示显存退化）→ **温度逼近阈值**（`DCGM/dcgmmlib/dcgm_fields.h:619` GPU_TEMP=150、`:654-659` SLOWDOWN=158/SHUTDOWN=159）→ **降频原因位**（clock throttle reasons 非 0 = 开始用性能换安全）→ **NVLink CRC 增长**（线缆/链路先兆）→ **XID**（`DCGM/dcgmmlib/dcgm_fields.h:806` XID_ERROR=230，已经出事：48=双位错、79=掉卡、63/64=row remap 系）。DCGM 还有内置 policy 引擎，七种故障条件的位掩码就在 `DCGM/dcgmlib/dcgm_structs.h:1880-1890`：DBE/PCI/retired pages/thermal/power/NVLINK/XID——dcgmi 的策略告警即此物。

出口在 dcgm-exporter：字段 → Prometheus 指标，映射表就是一份 CSV。**坑：默认只开 26 个指标，四条 ECC 计数全部被注释**（`dcgm-exporter/etc/default-counters.csv:55-59`），NVLink CRC 在 HPC 套件里同样默认注释（`dcgm-exporter/etc/dcp-metrics-included.csv:59-64`）；XID 默认导出（`:29`）但语义是"最后一个 XID 值"的 gauge；ROW_REMAP_FAILURE 默认开（`:89`）。装完 exporter ≠ 有故障预警——ECC/NVLink CRC 要自己解注释再重启。

### 3.4 切分：MIG 的配置模型与运维时序

MIG 规格记法 `<计算切片>c<GPU 切片>g<显存>`（`mig-parted/pkg/types/mig_profile.go:28`），如 1g.10gb = 1 份 GPC 切片 + 10GB 显存；`mig-parted/pkg/mig/config/known_configs.go:33-48` 列出 A100 的全规格表（1c.1g.5gb 到 7c.7g.40gb）。mig-parted 的配置模型只有四个字段（`mig-parted/api/spec/v1/spec.go:36-41`）：device-filter（按 PCI/型号筛）+ devices（卡号或 all）+ mig-enabled + mig-devices（规格→数量），校验干净利落（`:173-178`）：开 MIG 必须给 mig-devices，关 MIG 不许带。

真正难的是**运维时序**——MIG 模式切换要求 GPU 上没有任何客户。K8s 侧 mig-manager 的重配置状态机在 `mig-parted/pkg/mig/reconfigure/reconfigure.go:136-251`：打 pending 标签 → 摘掉 GPU 客户端 daemonset 的落点标签驱散它们（`:173`）→ 等这些 pod 删干净（`:179`）→ 关宿主 GPU 客户端并 sleep 30 秒（`:184-192`）→ 切 MIG 模式（`:194`）；若切换失败且允许重启，直接 `chroot /host reboot`（`:206`）——MIG enable 是持久位，部分状态只有重启能救。切完规格必须重新生成 CDI spec（`:221`，否则容器按旧设备名引用必失败），再逆序拉回所有客户端。**三种共享方式的物理差异**：时间片/vGPU = 驱动调度层轮转，故障与干扰会扩散；MPS = 共享 context 省切换开销但显存不隔离；MIG = GPC/L2/显存物理划分，一份 OOM/挂死不波及别份——**尾延迟隔离（p99 不被邻居炸掉）只有 MIG 做得到**，这是推理服务混部小租户必须 MIG 的原因。

### 3.5 HPC 拼图：enroot + pyxis——为什么 Slurm 阵营不投 K8s

HPC 批处理要三样东西：拓扑感知排队（同 NVLink 域内分配）、作业级生命周期（起容器→跑→拆，不留常驻）、对节点 cgroup 的绝对控制权。K8s 的 DaemonSet 常驻模型三条全反。NVIDIA 给 HPC 的答案是极简两件套：**enroot** 无守护进程容器运行时（rootfs 就是目录树+squashfs，秒级启动），**pyxis** Slurm SPANK 插件。

GPU 注入层 enroot 不重造轮子——hook 脚本直接 exec libnvidia-container 的 CLI（`enroot/conf/hooks/98-nvidia.sh:86` `nvidia-container-cli --user configure`），环境变量语义与 docker 同名兼容（NVIDIA_VISIBLE_DEVICES→--device，`:36-38`；capabilities→--compute/--utility，`:50-64`）。两个 HPC 特色：`--no-cgroups --ldconfig=@...`（`:30`）——**设备隔离交给 Slurm 自己的 cgroup，容器运行时不越权**；--compute 时顺手挂 /dev/gdrdrv（GDRCopy）与 nvidia-caps-imex-channels（`:81-84`，IMEX=CUDA 跨容器共享内存通道）。pyxis 侧：SPANK 回调挂进 slurmd 任务启动（`pyxis/pyxis_slurmstepd.c:1562` slurm_spank_task_init）；同节点多 task 用共享内存+mutex 协调，第一个 task 负责建并启动容器（`:1484` enroot_start_once、`:1504-1510` init_tasks==1），其余共享其 namespace；还干了一件 HPC 用户人人受益的事——环境变量重映射 SLURM_PROCID→RANK、SLURM_LOCALID→LOCAL_RANK（`:1456`），PyTorch DDP 在 Slurm 里开箱即用。

### 3.6 信任链：nvtrust 与 GPU 机密计算的生态位

多租户云的终极矛盾：租户模型明文躺在 HBM，宿主管理员理论上可见。GPU CC mode 让 HBM/PCIe 走 TEE 加密、GPU 上下文对宿主不可见；nvtrust 提供配套件：guest 侧 attestation SDK（Python 版已宣布弃用、转向 C++ SDK，local_gpu_verifier 已并入 SDK）、RIM 参考完整性清单比对、host 侧 CC mode 配置工具与 KVM 启动脚本；2026 年新增 PPCIE verifier——多卡全部处于 PPCIE 模式时允许 NVLink 明文直连、同时保持 CVM 安全，解开"机密计算=牺牲 NVLink"的两难。gpu-operator 的 state-cc-manager（`gpu-operator/controllers/state_manager.go:818`）把它接进 K8s 主线。生态位判断：今天它主要是公有云/政企的合规件（远程证明签发令牌→才允许调度敏感负载，与 GPUCluster/DRA 的"可信节点池"天然互补）；自建中小集群六层里可最晚装。

## 四、程序员实操

**排错决策树：容器里看不到 GPU / nvidia-smi 报错**（按注入链四段二分，从容器往外查）：

1. `nvidia-smi: command not found` → 库段都没到：镜像没带 nvidia-smi，或 utility capability 未注入——查 `NVIDIA_DRIVER_CAPABILITIES`（docker 缺省 `compute,utility`）。
2. `Failed to initialize NVML: Driver/library version mismatch` → 注入链通了但版本不符：宿主刚升驱动、toolkit 注入的还是旧缓存库——重启容器运行时或重跑 `nvidia-ctk runtime configure`；对比容器内外 `ls -l /usr/lib/x86_64-linux-gnu/libnvidia-ml.so.1` 指向。enroot 用户另查缺省 capabilities 只有 utility 的坑（见勘误 #2）。
3. `No CUDA devices are available` / CDI `unknown device` → 设备段断了：`ls /dev/nvidia*` 看节点；K8s+CDI 场景九成是 spec 过期（MIG 重切/驱动升级后没重生成）——`nvidia-ctk cdi generate --output /var/run/cdi/nvidia.yaml` 后删 Pod 重建。
4. `CUDA driver version is insufficient` → 宿主驱动太老：上 cuda-compat（toolkit 的 EnableCudaCompatHook 专管此事）或升宿主驱动。

宿主侧三板斧先行：`nvidia-smi`（驱动活着吗）、`dmesg | grep -i -e xid -e nvidia`（出过几号错）、`dcgmi diag -r 1`（一级诊断，约半分钟）。

**DCGM 告警起步三条规则**（先把 default-counters.csv 的 ECC 注释放开）：`DCGM_FI_DEV_XID_ERRORS > 0`（立即 page）；`increase(DCGM_FI_DEV_ECC_DBE_VOL_TOTAL[1h]) > 0`（DBE 是 RMA 前兆，counter 口径可用 increase）；`DCGM_FI_DEV_GPU_TEMP > 85` 持续 5 分钟。进阶再加 NVLink CRC 增长率与 `DCGM_FI_DEV_CLOCK_THROTTLE_REASONS != 0`（正在降频=性能悄悄流失）。

**MIG 实操**：`nvidia-smi mig -lgip` 看本卡合法规格 → `nvidia-mig-parted export` 导出现状 → 写配置文件（骨架即 3.4 的四字段模型：`mig-configs: {"all-1g10gb": [{devices: all, mig-enabled: true, mig-devices: {"1g.10gb": 7}}]}`）→ 裸机 `nvidia-mig-parted apply -f config.yaml`，K8s 打标签 `kubectl label node <n> nvidia.com/mig.config=all-1g10gb`（mig-manager 自动走 3.4 状态机）→ `nvidia-mig-parted assert` 验收。切换窗口按分钟级预算（驱散+重切+CDI 再生成+拉回客户端）。

## 五、批判边界

1. **MIG 不是默认选项**：只有部分数据中心卡支持（operator 白名单源码只认 h100/a100/a30），最多 7 份，重切要驱散全节点客户（3.4 时序），规格组合受芯片播种约束。它是尾延迟敏感场景的手术刀；碎片化共享的日常解仍是时间片——便宜但互踩。
2. **device plugin 的 Unhealthy 是单行道**（`server.go:277` FIXME）：GPU 恢复健康也不回池，"可恢复性"被外包给集群管理员的自愈循环。
3. **operator 的抽象会漏雨**：驱动容器化要编译内核模块，安全基线强的环境直接禁用（OpenShift 只能用 Driver Toolkit 折衷）；内核小版本一变，driver DaemonSet 全节点重建——"声明式收敛"收敛的是状态，收敛不了停机窗口。
4. **可观测默认值偏乐观**：exporter 默认 26 指标不含 ECC/NVLink CRC（3.3），XID 是"最后值"gauge 而非累计——对 gauge 误用 `increase()` 会静默漏报。
5. **两套世界观的税**：K8s（gpu-operator）与 Slurm（enroot/pyxis）共享 libnvidia-container 底座但互不感知，混合集群要维护两套镜像/MIG/监控逻辑；DRA 是 K8s 侧对拓扑感知的补票，尚未跨阵营。
6. **信任链的折衷**：CC mode 有带宽税；attestation 证明"卡没被动过"，不证明"租户代码无害"——租户间的硬件级隔离仍靠 MIG/调度域，侧信道风险属研究前沿而非产品承诺。

## 六、费曼检验

1. **为什么容器镜像里不能装 NVIDIA 驱动，而 CUDA 程序又要求"驱动匹配"？** 驱动=内核模块+用户态库对，内核模块跟宿主内核绑死；镜像只装 CUDA 运行时，libcuda/libnvidia-ml 由 toolkit 在容器启动时从宿主注入（`nvc_mount.c:694` 的挂载矩阵），NVML 库正是所有运维工具 dlopen 的那只（`lib.go:30`）——"版本匹配"发生在注入那一刻，mismatch 就是注入了旧缓存库。
2. **CDI 模式比 legacy hook 好在哪，六个 hook 又为什么省不掉？** legacy 在 runtime 路径中间插私有 prestart hook（`stable.go:65-68`），注入逻辑运行时才展开、绑定 NVIDIA runtime；CDI 把注入预计算成声明式 spec（设备/挂载/钩子三段，默认 `/var/run/cdi`），containerd 原生消费、device plugin 用注解点名设备，跨运行时可移植。但"必须在容器 mount namespace 里干"的细活（建符号链接、刷 ld 缓存）消不掉（`hooks.go:48-63`），只是从私有链路移进标准 CDI 钩子。
3. **为什么 MIG 重配置要驱散整节点客户端、甚至可能重启节点，vGPU 却不用？** MIG 模式是 GPU 全局持久状态，切换前提是设备无任何客户进程，部分卡上 enable 位需重置才生效（`reconfigure.go:194-214` 的 reboot 分支）；切完设备名全变，CDI spec 必须重生成（`:221`）。vGPU 是驱动调度层虚拟化、不动硬件分区状态——代价对价正是 MIG 的故障/性能双隔离。

**一句话总结**：运维线是把"GPU 不可抢占、不可换页、驱动内核态单例"这个物理事实逐层翻译成软件可处理的抽象——toolkit 把驱动降维成"库+设备节点"两样注入行李，operator 把装机降维成一份 CRD 的持续收敛，DCGM 把健康降维成四千个字段 ID，MIG 把整卡降维成七个带隔离的租约，nvtrust 把"卡可信"降维成一张可验证令牌——六层合起来，才是"GPU 数据中心操作系统"。

---

## 勘误（旧文/deepwiki/常见认知 vs 本仓源码）

1. **"nvidia-container-toolkit 是个 runtime hook"**（deepwiki 概览口径）：现版本是完整 OCI runtime wrapper + 四模式分发（legacy/csv/cdi/jit-cdi，`nvidia-container-toolkit/internal/modifier/mode.go:13-23`）；hook 只是 legacy 模式的一环，且显式 `assertModeIsLegacy`（hook main.go:85）——CDI 路径下它根本不跑。
2. **"enroot 与 nvidia-container-toolkit 是两套竞争的 GPU 容器方案"**：GPU 注入层完全同源——enroot 的 NVIDIA hook 直接 exec `nvidia-container-cli`（libnvidia-container 的 CLI，`98-nvidia.sh:86`）；差异在容器生命周期模型（无守护/无 cgroup/作业级），不在注入机制。且其 capabilities 缺省值是 `utility` 单项（`:50-52`），比 docker 缺省 `compute,utility` 更保守，HPC 用户忘设会踩。
3. **"DCGM 是 NVML 的封装"**：NVML 只覆盖 GPU 模块；NVSwitch 模块走 NSCQ、sysmon 走 sysfs，另有 policy/diag/health 引擎与 host engine/cache manager——监控能力大于 NVML 之和。
4. **"装了 dcgm-exporter 就有 GPU 故障告警数据"**：默认 CSV 仅 26 个指标、四条 ECC 计数被注释（`default-counters.csv:55-59`）、NVLink CRC 在 HPC 套件同样默认注释（`dcp-metrics-included.csv:59-64`）；XID 虽默认导出但是"最后值"gauge 口径（`:29`）。
5. **"MIG 可以在线动态切换"**：切规格尚可（驱散客户后分钟级）；**切模式**（enable/disable MIG）部分状态要节点重启（`reconfigure.go:206` 的 `chroot reboot` 分支），K8s 路径切完必须重生成 CDI spec（`:221`）——"在线"两字不成立。
6. **"gpu-operator 对所有卡都支持 MIG 管理"**：mig-manager 落点判断硬编码 h100/a100/a30 子串（`state_manager.go:353-355`），新卡需 `nvidia.com/mig.capable` 标签先就位，否则 mig-manager 静默不部署。
