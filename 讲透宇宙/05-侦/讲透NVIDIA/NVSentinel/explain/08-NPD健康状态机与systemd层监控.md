# 08 | NPD 健康状态机与 systemd 层监控

## 一、角色定位：补上 DCGM 看不见的那一层

从事故起笔：issue #883 中 H100 节点的 `nvidia-fabricmanager` 死了 **2.5 周**，DCGM 侧一直"健康"（docs/designs/050-gpu-system-services-npd-checks.md:13）。根因是语义错位——DCGM 4.5.2 的 `DCGM_FR_FABRIC_PROBE_STATE` 是**注册结果的锁存快照**而非进程活性：FM 注册后死掉，字段停在死前值，枚举里也没有"FM is not running"（050:15）；FM 死亡 → NVLink 恢复协调停摆、负载静默降级，遥测照常报绿。

而 gpu-health-monitor（DCGM）与 syslog-health-monitor（journald/XID）都看不到 systemd 单元状态——NPD 补上第三条腿。定位：NVSentinel 不装不配 NPD，NPD 侧以文档+参考配置交付（050:30-33）；两个 ADR 总分——053 集成上游三个文件系统/硬件 condition（053-npd-checks-integration.md:77），050 用 `CustomPluginMonitor` 主动探测 systemd 新增四个，共用 NPD → Node Condition → KOM → HealthEvent 通路——**Node 对象是数据源，KOM 是翻译器，HealthEvent 是统一货币**。

## 二、内部结构：四个 condition 与三个脚本的小状态机

四个 permanent condition（050:81-87）：`FabricManagerDown`/`FabricManagerFlapping`（均 fatal/`RESTART_BM`）、`FabricManagerNotInstalled`（fatal/`CONTACT_SUPPORT`）、`NvidiaPersistencedDown`（**非致命**）；一服务一 condition，共用会被后出结果覆盖（050:86）。

三个脚本（docs/tutorials/assets/npd-gpu-services/）退出码遵守 NPD 协议：0 健康、1 不健康、3 未知：

- **`check_gpu_service.sh <unit>`（存活）**：`systemctl show` 读 LoadState/ActiveState/SubState。`not-found` 退出 0=不适用（:167）；`active` 确认健康清零计数；`inactive/failed` 连续 3 次探测才置 unhealthy（:59；≈90s 防计划内重启误报）；过渡态 hold 上次确认状态（:194-207）；探测自带 8s 超时低于规则 12s（:65），卡死 systemd 报审慎 unknown 而非插件超时。
- **`check_fm_flapping.sh`（crash-loop）**：flap 判定独立于瞬时活性：`NRestarts` 差分 + 600s 滑窗、3 次达阈（:55-56）。`NRestarts` 不单调——`reset-failed` 冲计数器不重启进程，delta 为负时只在 `ExecMainStartTimestampMonotonic` 也变了才记 1 次可证重启（:180-188）。
- **`check_fm_installed.sh`（存在性）**：`LoadState=not-found` 即 1；仅"FM 必需"舰队装——FM 跑在 GPU Operator 驱动容器里时宿主单元天然不存在，装了只会误报（050:88-101）。

共享契约：**per-check 状态文件**在宿主 `/var/run/nvsentinel/npd/`（tmpfs，boot-scoped，050:146-162）；**probe 失败永不清故障**——unhealthy 无限 hold，healthy 最多 hold 4 次后降级 unknown；NPD 配置侧**四个单 condition 文件而非四合一**：v1.36.0 每 monitor 一份 conditions slice，配合 `skip_initial_status: true`（custom-plugin-fm-liveness.json:7），重启后没有 condition 被未探测默认值覆盖（050:193-196）。

## 三、外部连接：KOM 策略消费与两条 overlay

消费面是"每 condition 一条策略"（values-npd-gpu-services.yaml:66-83）：策略名即 `HealthEvent.CheckName`（pkg/publisher/publisher.go:97）；resource 固定 core/v1 Node；谓词是 CEL（预置 `now`/`lookup`，pkg/cel/environment.go:77），形如 `conditions.exists(c, c.type=="FabricManagerDown" && c.status != "False")`；启动时逐条编译（pkg/policy/evaluator.go:43-47）。

两条 overlay：**values-npd-remediation.yaml** = 默认策略 + 三个上游 NPD 策略，只开 KOM 不开补救，执行 `REPLACE_VM` 须叠 `values-remediation.yaml`（:22-24），验证可加 `STORE_ONLY`（:32-33）；**values-npd-gpu-services.yaml** = 默认策略 + 四个 GPU 服务策略，`NPDNvidiaPersistencedDown` 是唯一 `isFatal: false`（:148）。两者都重复默认策略——**Helm 对列表整体替换不合并**，须手工并入（:28-33）。

`CheckName` 的对外身份：platform-connectors 的 k8s connector 把事件折算回 Node condition，reason 拼作 `<CheckName>IsNotHealthy`（platform-connectors/pkg/connectors/kubernetes/process_node_events.go:1009-1015）。更外一圈：KOM 策略静态、无触本级抑制（050:440-442）；复发兜底是 analyzer 的 `MultipleRemediations`——7 天 5 次补救即触发、**无自动 healthy clear**（050:443-449）；软/硬分类跨信号归 analyzer（050:429-437）。

## 四、数据流：从 systemctl 到 RESTART_BM 的完整时序

链路：脚本 30s 探测 → NPD `CustomPluginMonitor`×4 写 Node Condition → KOM watch core/v1/Node → HealthEvent → platform-connector → quarantine/remediation；connector 再写回策略 condition。

KOM 心脏是 `ResourceReconciler.reconcilePolicy`（pkg/controller/reconciler.go:247-293），纯**边沿触发**：CEL 求值（必须返回 bool，pkg/policy/evaluator.go:84）→ 以 `stateKey=策略名/节点名`（reconciler.go:364）查内存表 → `matched && !wasMatched` 发 unhealthy 并落状态（:284）、反向发 healthy 并清（:288）、无变化零输出——稳态零噪音。双保险：`matchStates` 每次转换同步写 Node annotation（pkg/annotations/manager.go:33），重启经 `RestoreState` 恢复（reconciler.go:84），不丢状态也不重复发布。

时序：探测 30s；首报 ≤42s（monitoring-gpu-system-services.md:198-200）；down 确认 ≈90s；flap = 第 3 次重启进窗后 ≤30s；**恢复一次 healthy 探测即清**（防抖只在不健康方向，:295-297）。

## 五、设计决策

**1. 锁存 vs 自清是第一性原理。** 053 的三个 condition 来自 `SystemLogMonitor`——匹配日志行判定、**没有恢复探针**，True 锁存到 NPD 进程结束（053:63-68）；NPD 重启也重置 condition（053:70-73）。050 的主动探测一次 healthy 即回 False（monitoring-gpu-system-services.md:80-82）。

**2. 实际谓词是三态 `!= "False"`，比 ADR 示例更强（源码为准）。** ADR 示例写 `status == "True" && reason == "..."`，overlay 七条策略清一色 `!= "False"` 且不匹配 reason（values-npd-gpu-services.yaml:75-76、values-npd-remediation.yaml:80-82）。NPD 插件超时/exec 失败把 condition 置 `Unknown`——按 `== "True"`，KOM 会把 Unknown 当健康边沿、取消补救（050:407-421）；`!= "False"` 让 Unknown 依然匹配——ADR 定位的"补全件"三态处理（050:418-419）在 overlay 先行落地。

**3. `NRestarts` 消歧是 flap 检测的信誉所在**（见第二节）。`RESTART_BM` 是"最便宜的有胜算尝试"而非软/硬判决——NVSwitch 硬件故障曾有整机架退回记录，分类归 analyzer（050:429-437）；一条采集通路一种信号：DCGM/journal/systemd 各归各（050:475-476）。

## 六、新人提示

**验证三段式**（monitoring-gpu-system-services.md:258-263）：① `STORE_ONLY` 干跑；② 停 `nvidia-persistenced` 走通非致命全链；③ 致命 FM 路径只在排空可弃节点做。

**五个坑**：① flap 验证别用手动 restart（不进 NRestarts），要 `systemctl kill --signal=SIGKILL` 三次间隔 20s（:323-334）；② DaemonSet NPD 忘挂宿主 `/var/run/nvsentinel/npd` = flap 检测静默失效（:156-173）；③ 上游 NPD 镜像没有 systemctl，用 `chroot /host` shim（:175-185）；④ NPD 重启前后的转换不作数（:355-364），`Unknown` 永远不是健康（:365-371）；⑤ 开 KOM 策略没套 NPD 配置=安全但哑，按 050:376-380 场景矩阵配对。

**一处教程与源码的出入（源码为准）**：教程 4a 期望停 persistenced 后 Node 出现策略 condition `NPDNvidiaPersistencedDown=True`（monitoring-gpu-system-services.md:285-293），但 connector 写回路径两处过滤 `!IsHealthy && !IsFatal`（process_node_events.go:248、:1140）——非致命 unhealthy 事件只产生 K8s Event（:1089），不落 Node condition。

**一句话总结**：NPD 是把"节点本地 systemd 事实"翻译成"Kubernetes 对象事实"的搬运工；状态机三段接力——脚本防抖/滑窗/hold"别误报"，KOM 谓词+边沿触发"别漏报别重报"，analyzer 跨信号管"复发升级"。#883 那 2.5 周盲区由此闭合。
