# 04 · preflight 与 readiness 就绪体系

对象：`src/lib/onboard/preflight.ts`（2298 行巨石）、`src/lib/state/launch-readiness-lease.ts`（1870 行）、`src/lib/state/legacy-port-migration.ts`（1272 行）。图谱同属"onboard 编排主干与 preflight 就绪域"。

## 角色定位

preflight 是 onboard 的体检科：在任何昂贵操作前评估宿主（运行时/包管理器/GPU/CDI/cgroup/资源/端口/内存/swap/DNS 三探测），把"环境不行"变成带修复建议的早退；readiness 租约体系是"就绪"的持久证明——launch 命令只有持有效 lease 才算权威就绪；legacy 端口迁移解决历史遗留：共享状态根切到 per-port 根的一次性搬迁，是三层锁序下的可恢复事务。

## 内部结构

`assessHost`（preflight.ts:599）是宿主全量评估入口，全部探测经 opts 注入（runCaptureEx/commandExists/gpuProbe 皆可替换）。Docker 权威判定三个精细分支：DOCKER_HOST 压制 DOCKER_CONTEXT，幸存的 context 选择器视为不可用端点（#11719，:623-633）；显式选择的端点 socket 缺失不误诊为 docker 组/停 daemon——那两个药方（含 root 级组授权）会基于假前提行动（:663-680）；默认端点不可达且两个可达引擎身份不同才是权威冲突（#10622，:682-703）。端口链：`probePortAvailability`（:906）真实 bind 探测，EPERM/EACCES 与意外错误都返回 ok+warning 而非假冲突（:928-940）；`checkPortAvailable`（:966）lsof 主探，空输出不权威（非 root 看不见 root 监听者）再试 `sudo -n lsof`（:998-1017）。资源链：`isDockerUnderProvisioned`（:447）用 `docker info` 的 CPU/内存解析（:403/:417）判欠配；`ensureSwap`（:1206）不足时 `sudo dd` 造 4GB swap 写 fstab（:1159-1206），失败给手工命令。DNS 三探测：`probeContainerDns`（:1736）在 busybox 容器里 nslookup，probeName 经 RFC1035 正则、dnsServer 经 `net.isIP` 双注入防护后才进 `sh -c`（:1746-1759）；`ensureProbeImageCached`（:1404）预拉镜像使计时只计探测不计拉取，daemon 卡死返回独立 `docker_daemon_unreachable`；`probeHostDns`（:2062）默认探 `integrate.api.nvidia.com`（:1991）；`probeDockerBridgeContainerStart`（:2172）跑 bridge 容器 `true` 防 veth 不支持。readiness 侧：lease 记录含 bootId/uid/home 与 store 的 device+inode（lease.ts:46-63），24h 有效（:12），16KB 上限（:16）；读取五态 missing/unsafe/malformed/expired/identity/valid（:90-96）；`fenceLaunchReadinessLease`（:1646）换随机发布 epoch，注释规定锁序——lifecycle lock→route lock→释放→经 mutation gate 重取双锁并重验 epoch 才做最终发布（:1638-1645）。

## 外部连接

preflight 的 82 个图谱连接里最重的是 `advisories/checks/host/*` 六检查器与 `advisories/runner.ts`——advisory 体系是它的问题呈现层；`llama-cpp/managed-installer` 与 `serving/managed-cluster-discovery-production` 反向依赖它做生产探测。测试面：`preflight.test.ts` 1875 行 19 个 describe 专题（端口/内存/assessHost/swap/容器 DNS/bridge 启动/镜像缓存/#2514 资源检测等），onboard 目录另有 25 个 preflight 专项测试（gateway 序列/复用 #6576、CDI、podman 兼容、DNS resolver 覆盖、docker 超时、权威冲突等）。lease 消费方是 `actions/sandbox/launch-readiness.ts`、`launch-readiness/health.ts` 与 openclaw 配对资格模块。迁移入口在 `cli/public-dispatch.ts`，依赖 `state/registry/lock` 进程锁与 `gateway-registry`。

## 数据流

preflight 输出 HostAssessment + advisories，供 onboard 编排决定继续/补救/退出；DNS 失败签名（`Error response from daemon`、`no servers could be reached`）被 `isRegistryResolutionFailure`（:1641）等分类器路由成 fatal/inconclusive，`isFatalContainerDnsProbeFailure`（:1955）与 `isFatalHostDnsProbeFailure`（:2162）给最终判死标准。readiness：launch 前提→fence 换 epoch→预检通过→`publishLaunchReadinessLease`（:1741）写 lease→后续命令 `readLaunchReadinessLease`（:1396）五态判定，mutating 操作先过 `checkLaunchReadinessMutationAuthority`（:1594）——三元组不匹配即 changed，异常即 unsafe。迁移：`migrateLegacyPortState`（migration:1056）先读 intent，默认端口路径只清陈旧 intent 目录（:1072-1092）；非默认端口取 migration 目录锁→断言两根 onboard.lock 均缺席（:1118，绝不自动删）→取 legacy 注册表锁→有 pending intent 校验端口一致后 `applyMigrationIntent` 续跑（:1122-1136）→否则按行内持久化网关端口把注册表行二分（:1144-1148）。

## 设计决策

①**误诊防护优先于覆盖率**：显式端点 socket 缺失不套用默认端点的补救话术（preflight.ts:663-668），权威冲突只在 DOCKER_HOST 未设时观察（:682-687）——每个诊断分支都限定在自己的前提内。②**探测不确定性显式建模**：bind 探测的意外错误"不得报告假冲突"（:936），lsof 空输出降级而非采信。③**shell 注入面收口**：唯一非定常 token（probeName/dnsServer）进 `sh -c` 前正则/IP 双验证（:1741-1759）。④**计时公平**：预拉镜像让冷缓存拉取不被算进探测预算、误报为 bridge 超时（#3630，:2188-2196）。⑤**lease 是身份绑定而非时间戳**：bootId+device+inode 防"同路径不同机器/挂载"的假续期，fence 保留原 lease 时间参数（lease.ts:65-88）防时间不安全窗口。⑥**迁移锁是世代化目录锁**：lock 目录只允许含 owner 文件、UID/模式全验、摘除走 quarantine+同世代校验+失败回滚（migration:860-960）；stale 判定用 PID 存活而非盲等（:955-962）。

## 新人提示

改 preflight 先看 `assessHost` 的 opts 注入面——新增探测必须可注入才能进专题测试。诊断文案各分支都有 issue 锚（#11719/#10622/#7320/#3630/#2514），改行为前先读注释块，那里写的是"为什么不能更宽松"。lease 侧先读 lease.ts:1-100 类型定义再读 fence/publish，五态读取结果决定上层重试还是拒绝。迁移代码不要单测某个 move 函数——`migrateLegacyPortState` 的锁序（migration lock→onboard.lock 断言→registry lock）是握手协议的一半，onboard 写者拿到 onboard.lock 后会反查 migration lock（:1115 注释），单边改动会开竞态窗口。
