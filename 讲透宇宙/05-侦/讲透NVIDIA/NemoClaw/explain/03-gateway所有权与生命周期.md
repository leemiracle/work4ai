# 03 · gateway 所有权与生命周期

对象：`src/lib/onboard/gateway-ownership.ts`（529 行，#6576 模型）、`src/lib/onboard/host-gateway-process.ts`（819 行）、`src/lib/tunnel/gateway-port-release.ts`（198 行，端口释放 fail-closed）。

## 角色定位

网关是 OpenShell 沙箱的控制面入口，"谁拥有网关生命周期"是全系统最贵的不变量。`gateway-ownership.ts` 定义 #6576 的双权威事故模型并把它变成纯函数判定；`host-gateway-process.ts` 是宿主侧网关进程收割器——pgrep 候选、cmdline 门控、属主检查、TERM→KILL 升级、端口再验证；`gateway-port-release.ts` 是 `nemoclaw stop` 的端口级释放入口（#5968）。三者共同回答：这个网关进程能不能杀、杀了之后端口是否真能空出来、以及"杀不动"时如何安全地交还给人。

## 内部结构

#6576 模型写在 gateway-ownership.ts 头注释（:5-26）：任一时刻恰好一个组件拥有网关生命周期；要防的事故是"外部监督者（如平台镜像自带的网关服务）拥有进程、NemoClaw 又静默回退自起 standalone 网关——两层都认为自己拥有同一端口，一个换掉活监听、另一个重启它，宿主留下持久 bind 冲突且无权威属主"。因此 externally supervised 模式永不允许 standalone 回退：要么附着并校验，要么失败。属主来源三值 `declared | packaged-service | standalone`（:47）；`sameGatewayOwner`（:187）保证一次运行内权威不变——后来的解析若不同即为迁移而非静默切换。`gateway-teardown-authority.ts:11-16` 把契约延伸到 onboard 退出后的命令：credentials 增改、stop、最终清理、uninstall 在动 provider/扫监听/发信号/删运行时资源前必须重新加载权威。收割器侧：`HOST_GATEWAY_PGREP_PATTERN`（host-gateway-process.ts:92）是锚定正则，注释（:86-90）说明 pgrep -f 只见 cmdline 不见 argv0，compat 父进程只能靠启动时写的 PID 文件重发现；进程状态由 `ps -o stat=` 解析为 exited/running/unknown 三态（:176-192）；scoped 停机的所有权证明链 `scopedGatewayOwnershipFailure`（:355）要求 PID 文件与 runtime marker 指同一进程（:370）、provider 已注册（:373）、marker 端口/平台/架构匹配（:389-401）、沙箱命名空间可证（:403）且 cmdline 匹配（:408）；`tryStopPid`（:588）在 SIGTERM 与 SIGKILL 之间、以及发信号前都重验身份（:596/:602），身份漂移即返回 `identity-changed` 拒绝继续。

## 外部连接

图谱中 host-gateway-process 的 23 个连接覆盖三条消费线：destroy 线（`destroy-gateway.ts`、`destroy-gateway-cleanup.ts`）、doctor 线（`doctor-gateway-fallback.ts`）、网关运行时线（`docker-driver-gateway-runtime.ts`、`docker-driver-gateway-prelaunch.ts`、`gateway/state-ownership.ts`）。port-release 由 stop 命令与 uninstall 消费，`gateway-port-release-fail-closed.test.ts`/`gateway-port-release-lifecycle.test.ts` 各自锁死失败语义。ownership 的 `isExternallySupervised` 被 port-release:107 用来短路（外部监督网关保持运行），`sameGatewayOwner` 被 rebuild journal 的权威重验（journal:692）复用——篇 2 的 #8103 拒绝路径就是这套比较的消费者。onboard.ts:1158 是模型的行为落点：外部与 provider 拥有的网关绕过 Docker 清理效果。

## 数据流

stop 命令进入 `releaseManagedGatewayPort`（gateway-port-release.ts:67）：先解析端口绑定，无有效注册即整体跳过并给出诊断（:86-103）；再解析权威，外部监督网关直接"保持运行"返回 skipped（:105-120）；然后 lsof 扫描该端口的监听 PID（:131-138）——只有 lsof 观察到、且 cmdline 门控通过的 PID 才会成为信号候选，PID 文件内容本身永不直接作为候选（doc :61-66，防陈旧/复用 PID 误杀隔壁 worktree 的同名网关）；`stopHostGatewayProcesses` 以 `usePidFile:false, usePgrepFallback:false` 调用（:147-154）；最后 `confirmGatewayPortReleased` 实际 bind 验证端口可重绑（:163）。收割器内部：候选来自 pid-file/explicit/pgrep 三源（:655-691），显式 PID 在场时默认不做全宿主扫描（:677-684 注释：drift-restart 不能顺手终结无关 worktree 的网关）；逐个候选查状态→查身份→查属主，他用户进程列入 `foreignUserPids` 并保持运行（:753-761）；停止成功后还要端口真空闲（:788），失败则进 `sudoRemediationPids` 并打印"不要对保存的 PID 直接发信号"的补救指引（:179-188）。

## 设计决策

①**fail-closed 而非 fail-empty**：lsof 两阶段失败语义被刻意区分（gateway-port-release.ts:125-138、156-172）——初次扫描失败则整个确认跳过，后续 bind 成功也不能弥补扫描不完整；任何失败都不被强转为"无监听者"。②**身份先于信号**：每次发信号前重验属主/cmdline/命名空间，等待窗口内身份变化立即停手（host-gateway-process.ts:783-785）。③**他用户进程不可触碰**：UID 不匹配只警告不停机（:215-223）。④**pgrep 缺席要可见**：最小镜像无 pgrep 时警告"uninstaller 不得在孤儿网关仍绑定时报成功"（:801-811）。⑤**端口自由度的证明是 bind 而非推断**：`isHostPortFree` 用子进程真实监听 127.0.0.1 端口（:522-540），`scopedHostGatewayProcessAbsenceFailure` 在扫描前后各验一次端口（:467/:494）。⑥**能力契约对内不对网关**：OpenShell 无能力发现端点，`requiredCapabilities` 按本 NemoClaw 构建校验——新平台声明旧版给不了的能力时依然 fail-closed（gateway-ownership.ts:20-24）。

## 新人提示

排障入口顺序：`resolveGatewayOwner` 看属主判定 → `stopHostGatewayProcesses` 的返回结构体（:74-84 八个字段把 stopped/failed/foreign/sudo-remediation 分桶）读结果 → port-release 的 skipped/released 看 stop 命令为何没杀进程。改 pgrep 正则前必读 :86-90 注释（argv0 盲区）；加新停机路径时先决定 scoped 还是 sweep——scoped 要求"规范名+端口+PID 文件"三元组齐备（:642-653），这个前置拒绝是有意的窄化。测试方面 `host-gateway-process-target.test.ts` 与 `gateway-port-release-fail-closed.test.ts` 分别锁身份链与失败语义，是改动前必跑的两条。
