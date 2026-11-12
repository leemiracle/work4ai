# batch-027 semantic data (subprocess group: control protocol, linux scope, runner, windows job)
BATCH = {
 'files': {
  'packages/subprocess/README.md': {
   'type': 'document', 'complexity': 'simple',
   'summary': 'subprocess 能力组总览：进程生成契约（dsh-subprocess）+本地 provider（Linux systemd scope / Windows Job 对象）+win32 FFI 绑定的包目录。',
   'tags': ['documentation', 'package-group', 'subprocess', 'overview']},
  'packages/subprocess/subprocess/README.md': {
   'type': 'document', 'complexity': 'moderate',
   'summary': 'dsh-subprocess 包参考：子进程生成能力 seam 的契约——spawn 规范、受管范围所有权（BoundProcessOwner）、输出读取与终局 outcome 词汇。',
   'tags': ['documentation', 'package-reference', 'service-definition']},
  'packages/subprocess/subprocess/package.json': {
   'type': 'config', 'complexity': 'simple',
   'summary': '@deepseek-ai/dsh-subprocess 包清单：子进程能力契约包。',
   'tags': ['configuration', 'package-manifest']},
  'packages/subprocess/subprocess/src/control.ts': {
   'type': 'file', 'complexity': 'simple',
   'summary': '继承字节通道协议：fd 7 保留给可选 subprocess 控制通道，DSH_SUBPROCESS_CONTROL 私有启动标记在子进程执行应用代码前被消费；openInheritedControlChannel 打开继承管道（标记缺失即抛）。',
   'tags': ['protocol', 'ipc', 'control-channel'],
   'members': [
    {'kind': 'function', 'name': 'openInheritedControlChannel', 'start': 19, 'end': 23,
     'summary': '消费启动标记并在 fd 7 打开继承的控制管道，返回调用方拥有的双工流；消息即使端点继承也仍不可信。',
     'tags': ['ipc', 'exported'], 'complexity': 'simple', 'exported': True}]},
  'packages/subprocess/subprocess/tsconfig.json': {
   'type': 'config', 'complexity': 'simple',
   'summary': 'dsh-subprocess 的 TypeScript 编译配置。',
   'tags': ['configuration', 'typescript']},
  'packages/subprocess/subprocess/tsdown.config.ts': {
   'type': 'config', 'complexity': 'simple',
   'summary': 'dsh-subprocess 的 tsdown 打包配置（index/control/output 多入口）。',
   'tags': ['configuration', 'tsdown', 'build-system']},
  'packages/subprocess/subprocess-local/README.md': {
   'type': 'document', 'complexity': 'complex',
   'summary': 'dsh-subprocess-local 包参考：本地子进程 provider——Linux 用户 systemd transient scope + 一次性 execve bootstrap、Windows 受限令牌 Job runner、私有 runner 协议（Linux 启动文件/Windows IPC）、有界输出尾与 spill 文件。',
   'tags': ['documentation', 'package-reference', 'subprocess', 'local-provider']},
  'packages/subprocess/subprocess-local/package.json': {
   'type': 'config', 'complexity': 'simple',
   'summary': '@deepseek-ai/dsh-subprocess-local 包清单：本地子进程 provider（多入口导出 runner/output 子路径）。',
   'tags': ['configuration', 'package-manifest']},
  'packages/subprocess/subprocess-local/src/bin.ts': {
   'type': 'file', 'complexity': 'simple',
   'summary': 'runner 薄入口（打包为 runner.js）：运行已被打包 bootstrap 剥离的选择器，runSelectedSubprocessRunner 分发到 spawn-runner；import.meta.main 下无选择器即退出码 127。',
   'tags': ['entry-point', 'runner', 'bootstrap'],
   'members': [
    {'kind': 'function', 'name': 'runSelectedSubprocessRunner', 'start': 10, 'end': 18,
     'summary': '执行已剥离的 runner 选择器：委托 runSpawnRunner，失败经 reportSpawnRunnerFailure 上报。',
     'tags': ['runner', 'exported'], 'complexity': 'simple', 'exported': True}]},
  'packages/subprocess/subprocess-local/src/control-spawn.ts': {
   'type': 'file', 'complexity': 'simple',
   'summary': '父方对显式请求的继承控制管道的装配：controlPipe 从 Node stdio 元组读 fd 7 双工端点，controlEnvironment 在拒绝调用方覆盖后向新子环境盖私有启动标记。',
   'tags': ['ipc', 'spawn', 'environment'],
   'members': [
    {'kind': 'function', 'name': 'controlEnvironment', 'start': 27, 'end': 30,
     'summary': '向新建子环境盖 DSH_SUBPROCESS_CONTROL 标记（先拒绝调用方同名覆盖）。',
     'tags': ['environment', 'exported'], 'complexity': 'simple', 'exported': True}]},
  'packages/subprocess/subprocess-local/src/linux-execve.ts': {
   'type': 'file', 'complexity': 'moderate',
   'summary': '一次性 Linux bootstrap 用的惰性 libc execve 与描述符绑定：经 koffi FFI 加载 execve/fcntl，替换当前进程映像同时保留 argv/env，标准描述符与控制 fd 的 FD_CLOEXEC 清除。',
   'tags': ['ffi', 'execve', 'linux', 'bootstrap'],
   'members': [
    {'kind': 'function', 'name': 'loadLinuxExecve', 'start': 49, 'end': 79,
     'summary': '惰性加载并返回 execve 绑定（含描述符保持逻辑），供 runner 一次性替换进程映像。',
     'tags': ['ffi', 'exported'], 'complexity': 'moderate', 'exported': True}]},
  'packages/subprocess/subprocess-local/src/linux-scope-selector.ts': {
   'type': 'file', 'complexity': 'moderate',
   'summary': '基于注入宿主观测的 Linux 原生 containment 决策：LinuxScopeSelector 在 scope/直接/等-manager 三类决策间裁决，探测触发器含首次/scope 未启动/新监听者/launcher 变更。',
   'tags': ['decision', 'containment', 'linux'],
   'members': [
    {'kind': 'class', 'name': 'LinuxScopeSelector', 'start': 53, 'end': 101,
     'summary': ' containment 决策器：消费宿主观测（探测/manager 监听者/确认/launcher 身份）产出 LinuxScopeDecision 并缓存裁决直至失效触发器。',
     'tags': ['decision', 'cache', 'exported'], 'complexity': 'moderate', 'exported': True}]},
  'packages/subprocess/subprocess-local/src/linux-scope.ts': {
   'type': 'file', 'complexity': 'complex',
   'summary': 'Linux 用户 systemd scope 启动与受管范围所有权（724 行核心）：探测 transient scope 支持（literal-argv）、systemd-run 身份确认、SystemdScopeOwner 实现 BoundProcessOwner（启动/信号/终局收割），直接进程路径退化为进程组信号；启动文件协议恢复目标状态。',
   'tags': ['linux', 'systemd', 'scope', 'process-owner'],
   'members': [
    {'kind': 'class', 'name': 'SystemdScopeOwner', 'start': 284, 'end': 540,
     'summary': '实现 BoundProcessOwner 的 systemd scope 拥有者：经 systemd-run 启动 transient scope、管理单元 stem、等待终局并回收（含启动失败重试与直接路径降级）。',
     'tags': ['process-owner', 'systemd', 'exported'], 'complexity': 'complex', 'exported': True},
    {'kind': 'function', 'name': 'launchLinuxScope', 'start': 672, 'end': 724,
     'summary': 'Linux 受管启动入口：探测决策→scope 或直接路径启动→绑定 owner 与输出收集。',
     'tags': ['launch', 'linux', 'exported'], 'complexity': 'complex', 'exported': True},
    {'kind': 'function', 'name': 'prepareLinuxTerminalScope', 'start': 635, 'end': 662,
     'summary': '为交互终端准备 Linux scope 启动（保留用户 startup 文件的 shell 特殊路径）。',
     'tags': ['terminal', 'launch', 'exported'], 'complexity': 'complex', 'exported': True},
    {'kind': 'function', 'name': 'probeLinuxScope', 'start': 126, 'end': 155,
     'summary': '深度探测 transient scope 支持：确认 literal-argv 选项可用性与 manager 可达。',
     'tags': ['probe', 'exported'], 'complexity': 'complex', 'exported': True},
    {'kind': 'function', 'name': 'systemdRunIdentity', 'start': 224, 'end': 240,
     'summary': '解析 systemd-run 二进制的可解析身份，用于 launcher 变更检测。',
     'tags': ['identity', 'exported'], 'complexity': 'moderate', 'exported': True},
    {'kind': 'function', 'name': 'signalLinuxDirectProcess', 'start': 593, 'end': 603,
     'summary': '直接路径进程的信号投递（进程组语义）。',
     'tags': ['signals', 'exported'], 'complexity': 'moderate', 'exported': True}]},
  'packages/subprocess/subprocess-local/src/managed-owner.ts': {
   'type': 'file', 'complexity': 'simple',
   'summary': '受管进程拥有者契约：BoundProcessOwner/ManagedProcessLaunch 类型与 waitWithAbort（可中止的进程等待，终局结果化）。',
   'tags': ['contract', 'process-owner', 'waiting'],
   'members': [
    {'kind': 'function', 'name': 'waitWithAbort', 'start': 39, 'end': 56,
     'summary': '可中止等待进程 exit 事件并产出 outcome，AbortSignal 优先返回。',
     'tags': ['waiting', 'cancellation', 'exported'], 'complexity': 'moderate', 'exported': True}]},
  'packages/subprocess/subprocess-local/src/output.ts': {
   'type': 'file', 'complexity': 'complex',
   'summary': '进程 provider 共享的有界输出尾与私有 spill 文件：OutputCollector 每流保留内存尾+超限溢写私有 spill 文件（打开/追加失败丢弃 spill 继续收集并回报一次），spill 目录私有且会话清理。',
   'tags': ['output', 'spill', 'bounded-collection'],
   'members': [
    {'kind': 'class', 'name': 'OutputCollector', 'start': 129, 'end': 313,
     'summary': '有界输出收集器：滚动内存尾+确定性 spill 溢写，终局产出 CollectedOutput（截断标志与 spill 路径）。',
     'tags': ['output', 'collector', 'exported'], 'complexity': 'complex', 'exported': True},
    {'kind': 'function', 'name': 'logSpillFailure', 'start': 77, 'end': 86,
     'summary': '把一次 spill 失效交付拥有者记录（每 collector 至多一次，报告器抛错被包含并写 stderr）。',
     'tags': ['logging', 'exported'], 'complexity': 'simple', 'exported': True}]},
  'packages/subprocess/subprocess-local/src/runner-launch.ts': {
   'type': 'file', 'complexity': 'complex',
   'summary': '私有原生 runner 的父方调用与 bootstrap 状态：DSH_SUBPROCESS_RUNNER 私有环境变量、runner stdio 装配、Windows 可执行文件解析（PATH 目录拼装+PATHEXT 扩展名枚举+空字节拒绝）与目标环境恢复。',
   'tags': ['runner', 'spawn', 'windows-path'],
   'members': [
    {'kind': 'function', 'name': 'resolveWindowsExecutable', 'start': 252, 'end': 282,
     'summary': 'Windows 可执行文件解析：PATH 目录×扩展名候选枚举与存在性验证，坏路径（空字节等）显式失败。',
     'tags': ['windows', 'path-resolution', 'exported'], 'complexity': 'complex', 'exported': True},
    {'kind': 'function', 'name': 'runnerStdio', 'start': 119, 'end': 147,
     'summary': '装配 runner 子进程的 stdio 元组（继承端点+控制管道槽位）。',
     'tags': ['stdio', 'exported'], 'complexity': 'moderate', 'exported': True},
    {'kind': 'function', 'name': 'runnerEnvironment', 'start': 68, 'end': 86,
     'summary': '构造 runner 子进程环境（私有选择器标记+目标环境恢复准备）。',
     'tags': ['environment', 'exported'], 'complexity': 'moderate', 'exported': True},
    {'kind': 'function', 'name': 'spawnRunnerInvocation', 'start': 29, 'end': 42,
     'summary': '产出一个 runner 调用（argv 与 env）供父方 spawn 私有 runner。',
     'tags': ['runner', 'exported'], 'complexity': 'moderate', 'exported': True}]},
  'packages/subprocess/subprocess-local/src/runner-protocol.ts': {
   'type': 'file', 'complexity': 'complex',
   'summary': '原生 subprocess runner 的封闭私有传输：Linux 启动文件（目标 cwd/env/argv 的恢复请求，权限收紧的临时目录）、Windows IPC 启动/终止/结果消息与错误序列化——全部结构校验、坏消息拒绝。',
   'tags': ['protocol', 'runner', 'ipc', 'serialization'],
   'members': [
    {'kind': 'function', 'name': 'createLinuxLaunchFiles', 'start': 103, 'end': 118,
     'summary': '在私有临时目录创建 Linux 启动请求文件（目标状态载体，权限收紧）。',
     'tags': ['protocol', 'linux', 'exported'], 'complexity': 'moderate', 'exported': True},
    {'kind': 'function', 'name': 'parseWindowsRunnerResult', 'start': 199, 'end': 217,
     'summary': '解析 Windows runner 的结果消息（退出码/信号/PID，结构校验）。',
     'tags': ['protocol', 'windows', 'exported'], 'complexity': 'moderate', 'exported': True},
    {'kind': 'function', 'name': 'serializeRunnerError', 'start': 224, 'end': 234,
     'summary': '把 runner 端错误序列化为封闭传输可携带的结构（含反序列化对）。',
     'tags': ['serialization', 'exported'], 'complexity': 'moderate', 'exported': True},
    {'kind': 'function', 'name': 'cleanupLinuxLaunchFiles', 'start': 255, 'end': 273,
     'summary': '清理 Linux 启动文件（成功消费或失败后的确定性删除）。',
     'tags': ['protocol', 'cleanup', 'exported'], 'complexity': 'moderate', 'exported': True}]},
  'packages/subprocess/subprocess-local/src/shell-activity.ts': {
   'type': 'file', 'complexity': 'moderate',
   'summary': '私有 shell 生命周期文件：普通输出永不授权终端回收——ShellActivity 以修订号+观测状态跟踪一个交互 shell 的 opt-in 启动集成与状态文件。',
   'tags': ['shell', 'lifecycle', 'tracking'],
   'members': [
    {'kind': 'class', 'name': 'ShellActivity', 'start': 10, 'end': 51,
     'summary': '交互 shell 的启动集成与修订跟踪：私有目录的状态文件观测、失效检测与状态机。',
     'tags': ['shell', 'state-machine', 'exported'], 'complexity': 'moderate', 'exported': True},
    {'kind': 'function', 'name': 'prepareShellActivity', 'start': 60, 'end': 131,
     'summary': '为终端 spawn 准备 shell 活动跟踪（注入 startup 集成并装配状态文件）。',
     'tags': ['shell', 'terminal', 'exported'], 'complexity': 'complex', 'exported': True}]},
  'packages/subprocess/subprocess-local/src/spawn-runner.ts': {
   'type': 'file', 'complexity': 'complex',
   'summary': '一次性 Linux exec bootstrap 与 Windows Job 拥有 runner：runSpawnRunner 按选择器分发 Linux（execve 替换映像+控制 fd 保持）或 Windows（WindowsJobRunner 以受限令牌 Job 对象拥有进程、IPC 结果回报）；spawn 错误归一区分平台路径解析失败。',
   'tags': ['runner', 'linux-exec', 'windows-job', 'bootstrap'],
   'members': [
    {'kind': 'class', 'name': 'WindowsJobRunner', 'start': 225, 'end': 440,
     'summary': '以受限令牌 Job 对象拥有子进程的 Windows runner：创建 Job、轮询进程退出、终止回收与 IPC 结果序列化。',
     'tags': ['windows', 'job-object', 'exported'], 'complexity': 'complex', 'exported': True},
    {'kind': 'function', 'name': 'runSpawnRunner', 'start': 449, 'end': 462,
     'summary': 'runner 分发入口：消费选择器，Linux 走 exec 路径、Windows 走 Job runner。',
     'tags': ['runner', 'dispatch', 'exported'], 'complexity': 'moderate', 'exported': True},
    {'kind': 'function', 'name': 'reportSpawnRunnerFailure', 'start': 470, 'end': 490,
     'summary': 'runner 失败的封闭上报（序列化错误经 IPC/启动文件回传父方）。',
     'tags': ['error-handling', 'exported'], 'complexity': 'moderate', 'exported': True},
    {'kind': 'function', 'name': 'execLinuxTarget', 'start': 150, 'end': 177,
     'summary': 'Linux 目标执行：恢复目标状态后 execve 替换映像（保留 stdio 与控制通道）。',
     'tags': ['linux', 'exec'], 'complexity': 'complex'}]},
  'packages/subprocess/subprocess-local/src/windows-job.ts': {
   'type': 'file', 'complexity': 'complex',
   'summary': 'Windows 父方 Job 启动与拥有：probeWindowsJob 探测受限令牌 Job 支持，launchWindowsJob spawn 私有 runner（Job 对象+IPC 管道+序列化错误恢复），WindowsJobOwner 实现 BoundProcessOwner。',
   'tags': ['windows', 'job-object', 'process-owner'],
   'members': [
    {'kind': 'class', 'name': 'WindowsJobOwner', 'start': 70, 'end': 116,
     'summary': '实现 BoundProcessOwner 的 Windows Job 拥有者：Job 终止与进程终局等待。',
     'tags': ['process-owner', 'windows', 'exported'], 'complexity': 'moderate', 'exported': True},
    {'kind': 'function', 'name': 'launchWindowsJob', 'start': 125, 'end': 247,
     'summary': 'Windows 受管启动主路径：runner spawn+Job 绑定+IPC 结果解析+错误反序列化恢复。',
     'tags': ['launch', 'windows', 'exported'], 'complexity': 'complex', 'exported': True},
    {'kind': 'function', 'name': 'probeWindowsJob', 'start': 57, 'end': 68,
     'summary': '探测当前令牌 Job 对象支持（绑定加载+能力探测）。',
     'tags': ['probe', 'exported'], 'complexity': 'moderate', 'exported': True}]},
  'packages/subprocess/subprocess-local/tsconfig.json': {
   'type': 'config', 'complexity': 'simple',
   'summary': 'dsh-subprocess-local 的 TypeScript 编译配置。',
   'tags': ['configuration', 'typescript']},
  'packages/subprocess/subprocess-local/tsdown.config.ts': {
   'type': 'config', 'complexity': 'simple',
   'summary': 'dsh-subprocess-local 的 tsdown 打包配置：index/runner/output 三入口（runner 即 bin.ts）。',
   'tags': ['configuration', 'tsdown', 'build-system']},
  'packages/subprocess/win32-process/README.md': {
   'type': 'document', 'complexity': 'moderate',
   'summary': 'dsh-win32-process 包参考：win32 进程原语的 koffi FFI 绑定——受限令牌 Job 对象、进程退出轮询、CRT 启动描述符装配。',
   'tags': ['documentation', 'package-reference', 'ffi', 'windows']},
  'packages/subprocess/win32-process/package.json': {
   'type': 'config', 'complexity': 'simple',
   'summary': '@deepseek-ai/dsh-win32-process 包清单：win32 FFI 绑定包。',
   'tags': ['configuration', 'package-manifest']},
  'packages/subprocess/win32-process/src/control-stdio.ts': {
   'type': 'file', 'complexity': 'simple',
   'summary': '带一个继承控制管道的 Node 载荷的 Windows CRT 启动描述符：inheritedControlStdio 组装原生 stdio 句柄+启动器选定的单个附加描述符。',
   'tags': ['windows', 'stdio', 'ffi'],
   'members': [
    {'kind': 'function', 'name': 'inheritedControlStdio', 'start': 29, 'end': 47,
     'summary': '组装 CRT 启动描述符（stdin/stdout/stderr+控制管道句柄）供原生 spawn 使用。',
     'tags': ['stdio', 'exported'], 'complexity': 'moderate', 'exported': True}]},
 },
 'extra_edges': [
  {'source': 'class:packages/subprocess/subprocess-local/src/linux-scope.ts:SystemdScopeOwner', 'target': 'function:packages/subprocess/subprocess-local/src/managed-owner.ts:waitWithAbort', 'type': 'calls', 'direction': 'forward', 'weight': 0.8},
  {'source': 'class:packages/subprocess/subprocess-local/src/spawn-runner.ts:WindowsJobRunner', 'target': 'function:packages/subprocess/subprocess-local/src/runner-protocol.ts:parseWindowsRunnerResult', 'type': 'calls', 'direction': 'forward', 'weight': 0.8},
  {'source': 'function:packages/subprocess/subprocess-local/src/spawn-runner.ts:runSpawnRunner', 'target': 'function:packages/subprocess/subprocess-local/src/linux-execve.ts:loadLinuxExecve', 'type': 'calls', 'direction': 'forward', 'weight': 0.8},
  {'source': 'function:packages/subprocess/subprocess-local/src/windows-job.ts:launchWindowsJob', 'target': 'class:packages/subprocess/subprocess-local/src/spawn-runner.ts:WindowsJobRunner', 'type': 'calls', 'direction': 'forward', 'weight': 0.8},
  {'source': 'function:packages/subprocess/subprocess-local/src/linux-scope.ts:launchLinuxScope', 'target': 'class:packages/subprocess/subprocess-local/src/linux-scope.ts:SystemdScopeOwner', 'type': 'calls', 'direction': 'forward', 'weight': 0.8},
  {'source': 'function:packages/subprocess/subprocess-local/src/bin.ts:runSelectedSubprocessRunner', 'target': 'function:packages/subprocess/subprocess-local/src/spawn-runner.ts:runSpawnRunner', 'type': 'calls', 'direction': 'forward', 'weight': 0.8},
 ],
}
