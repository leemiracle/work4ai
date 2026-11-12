# batch-025 semantic data (shell group: executors, sandbox variants, seam, shell-env head)
BATCH = {
 'files': {
  'packages/shell/README.md': {
   'type': 'document', 'complexity': 'moderate',
   'summary': 'shell 能力组总览：executor 契约（ctx.shell）+本地/沙箱四种实现（bash/pwsh）+shell-env 托管环境+四个模型面工具（bash/pwsh×普通/持久会话）的包目录；一次组合恰好挂载一个 executor，双挂载在加载期即因重复服务注册失败。',
   'tags': ['documentation', 'package-group', 'shell', 'overview']},
  'packages/shell/bash-local/README.md': {
   'type': 'document', 'complexity': 'moderate',
   'summary': 'dsh-bash-local 包参考：POSIX 上以全新 bash -c 进程执行命令，executor 拥有命令默认值/期限/原因分类/模型友好终端环境与后台读取的 stdout-stderr 合并；执行策略归 tools/pre-execute 或沙箱 executor。',
   'tags': ['documentation', 'package-reference', 'bash', 'executor']},
  'packages/shell/bash-local/package.json': {
   'type': 'config', 'complexity': 'simple',
   'summary': '@deepseek-ai/dsh-bash-local 包清单：本地 Bash executor。',
   'tags': ['configuration', 'package-manifest']},
  'packages/shell/bash-local/src/index.ts': {
   'type': 'file', 'complexity': 'complex',
   'summary': '本地 Bash Service Provider：公开命令以 bash -c 经 ctx.subprocess 在受管范围内执行；拥有模型友好环境覆盖（NO_COLOR/TERM=dumb/PAGER=cat）、SIGTERM→SIGKILL 宽限期（默认 3s）、每流 spill 上限（64MiB）与期限钳制；ENV_OVERRIDES 先合并故可信调用方自带条目仍胜出。',
   'tags': ['executor', 'service-provider', 'bash', 'subprocess'],
   'members': [
    {'kind': 'class', 'name': 'LocalBashExecutor', 'start': 97, 'end': 402,
     'summary': 'bash 能力 seam 的本地实现（继承 ShellExecutor，注册为 ctx.shell）：前台 run/后台 spawn 两族方法，命令默认值、deadline 与失败原因分类、后台进程的非消费偏移读取。',
     'tags': ['executor', 'bash', 'exported'], 'complexity': 'complex', 'exported': True}]},
  'packages/shell/bash-local/tsconfig.json': {
   'type': 'config', 'complexity': 'simple',
   'summary': 'dsh-bash-local 的 TypeScript 编译配置。',
   'tags': ['configuration', 'typescript']},
  'packages/shell/bash-sandbox/README.md': {
   'type': 'document', 'complexity': 'moderate',
   'summary': 'dsh-bash-sandbox 包参考：经 sandbox 能力约束的 Bash executor——包装本地 bash argv 经 ctx.sandbox，报告所选模式/强制执行/拒绝事实；runner 可执行却失败的正面证据判定 confinement runner 损坏。',
   'tags': ['documentation', 'package-reference', 'sandbox', 'bash']},
  'packages/shell/bash-sandbox/package.json': {
   'type': 'config', 'complexity': 'simple',
   'summary': '@deepseek-ai/dsh-bash-sandbox 包清单：沙箱 Bash executor。',
   'tags': ['configuration', 'package-manifest']},
  'packages/shell/bash-sandbox/src/helpers.ts': {
   'type': 'file', 'complexity': 'simple',
   'summary': '共享 sandbox 诊断的 shell 结果投影助手：classifyDenial 按当前 wrap 的拒绝方言（大小写不敏感子串+exit code）分类失败运行，其余分类器从 dsh-sandbox 再导出。',
   'tags': ['helpers', 'diagnostics', 'classification'],
   'members': [
    {'kind': 'function', 'name': 'classifyDenial', 'start': 12, 'end': 14,
     'summary': '用拒绝子串签名匹配已定局的前台运行，判定是否命中后端拒绝方言。',
     'tags': ['classification', 'exported'], 'complexity': 'simple', 'exported': True}]},
  'packages/shell/bash-sandbox/src/index.ts': {
   'type': 'file', 'complexity': 'complex',
   'summary': '沙箱消费型 Bash executor：包装精确本地 bash argv 经 ctx.sandbox，继承本地进程机制并报告模式/强制/拒绝事实；runner 可执行证据 → 前台抛 SANDBOX_UNAVAILABLE、后台携带 runnerFailed；配置即本地 executor 的旋钮（沙箱策略在 ctx.sandboxPolicy）。',
   'tags': ['executor', 'sandbox', 'service-provider', 'bash'],
   'members': [
    {'kind': 'class', 'name': 'SandboxBashExecutor', 'start': 45, 'end': 190,
     'summary': '继承 LocalBashExecutor 的沙箱 executor（替代注册为 ctx.shell）：每命令经 ctx.sandbox 包装 argv 并附加完整逐调用策略，拒绝事实投影为 shell 结果的沙箱信息。',
     'tags': ['executor', 'sandbox', 'exported'], 'complexity': 'complex', 'exported': True}]},
  'packages/shell/bash-sandbox/tsconfig.json': {
   'type': 'config', 'complexity': 'simple',
   'summary': 'dsh-bash-sandbox 的 TypeScript 编译配置。',
   'tags': ['configuration', 'typescript']},
  'packages/shell/pwsh-local/README.md': {
   'type': 'document', 'complexity': 'moderate',
   'summary': 'dsh-pwsh-local 包参考：Windows 上以 pwsh -NoLogo -NoProfile -NonInteractive -Command 执行；命令串作为单 argv 元素由 PowerShell 自己解析，无中间 shell 转义层；与 dsh-bash-local 刻意逐调用镜像。',
   'tags': ['documentation', 'package-reference', 'pwsh', 'executor']},
  'packages/shell/pwsh-local/package.json': {
   'type': 'config', 'complexity': 'simple',
   'summary': '@deepseek-ai/dsh-pwsh-local 包清单：本地 PowerShell executor。',
   'tags': ['configuration', 'package-manifest']},
  'packages/shell/pwsh-local/src/index.ts': {
   'type': 'file', 'complexity': 'complex',
   'summary': '本地 PowerShell Service Provider：每条命令以 pwsh -Command（单 argv 元素）经 ctx.subprocess 执行，拥有命令默认值/期限/原因分类与模型友好环境（NO_COLOR 等，刻意无 TERM=dumb）；jscpd 忽略标注的 bash-local 逐调用镜像。',
   'tags': ['executor', 'service-provider', 'pwsh', 'windows'],
   'members': [
    {'kind': 'class', 'name': 'PwshLocalExecutor', 'start': 123, 'end': 446,
     'summary': 'bash 能力 seam 的本地 PowerShell 实现（继承 ShellExecutor）：前台 run/后台 spawn，经 resolvePwshPath 解析 pwsh 可执行文件，环境覆盖与宽限期/spill 语义与 LocalBashExecutor 对齐。',
     'tags': ['executor', 'pwsh', 'exported'], 'complexity': 'complex', 'exported': True}]},
  'packages/shell/pwsh-local/tsconfig.json': {
   'type': 'config', 'complexity': 'simple',
   'summary': 'dsh-pwsh-local 的 TypeScript 编译配置。',
   'tags': ['configuration', 'typescript']},
  'packages/shell/pwsh-sandbox/README.md': {
   'type': 'document', 'complexity': 'moderate',
   'summary': 'dsh-pwsh-sandbox 包参考：dsh-bash-sandbox 的 pwsh 孪生——本地 pwsh argv 经 ctx.sandbox（Windows 上解析为 ACL 受限令牌 runner 链），升级审批流归工具层。',
   'tags': ['documentation', 'package-reference', 'sandbox', 'pwsh']},
  'packages/shell/pwsh-sandbox/package.json': {
   'type': 'config', 'complexity': 'simple',
   'summary': '@deepseek-ai/dsh-pwsh-sandbox 包清单：沙箱 PowerShell executor。',
   'tags': ['configuration', 'package-manifest']},
  'packages/shell/pwsh-sandbox/src/helpers.ts': {
   'type': 'file', 'complexity': 'moderate',
   'summary': '沙箱结果分类助手（bash-sandbox helpers 的逐调用孪生）：仅把 syscall/路径证据确凿指向 argv[0] 的 ENOENT/EACCES 判为 runner 启动失败——先独立排除调用方 cwd 不可用，无错误路径时必须由 syscall 指认。',
   'tags': ['helpers', 'classification', 'runner-failure'],
   'members': [
    {'kind': 'function', 'name': 'classifyRunnerFailure', 'start': 84, 'end': 106,
     'summary': '把 spawn 失败分类为 runner 故障或普通失败：EACCES/ENOENT 且证据（路径/syscall）精确指认 argv[0] 才算 runner 失败。',
     'tags': ['classification', 'exported'], 'complexity': 'complex', 'exported': True},
    {'kind': 'function', 'name': 'isRunnerSpawnFailure', 'start': 42, 'end': 56,
     'summary': '判定错误码是否属于可执行文件解析/权限失败集合并给出初筛。',
     'tags': ['classification', 'exported'], 'complexity': 'moderate', 'exported': True}]},
  'packages/shell/pwsh-sandbox/src/index.ts': {
   'type': 'file', 'complexity': 'complex',
   'summary': '沙箱消费型 PowerShell executor（pwsh 孪生）：包装本地 pwsh argv 经 ctx.sandbox，继承本地机制，报告模式/强制/拒绝事实；前台损坏 runner 抛 SANDBOX_UNAVAILABLE、后台携带 runnerFailed，其余拒绝保持阶段中立的本地语义。',
   'tags': ['executor', 'sandbox', 'pwsh', 'service-provider'],
   'members': [
    {'kind': 'class', 'name': 'SandboxPwshExecutor', 'start': 52, 'end': 197,
     'summary': '继承 PwshLocalExecutor 的沙箱 executor（替代注册为 ctx.shell）：逐调用完整策略+ACL 受限令牌 runner 链，拒绝事实投影同 bash 孪生。',
     'tags': ['executor', 'sandbox', 'exported'], 'complexity': 'complex', 'exported': True}]},
  'packages/shell/shell/README.md': {
   'type': 'document', 'complexity': 'moderate',
   'summary': 'dsh-shell 包参考：ctx.shell 能力 seam 的 executor 契约——前台命令与后台进程句柄、请求/Spec 显式解析步；job id/所有权/轮询/通知归 dsh-jobs，executor 与会话解耦。',
   'tags': ['documentation', 'package-reference', 'service-definition']},
  'packages/shell/shell/package.json': {
   'type': 'config', 'complexity': 'simple',
   'summary': '@deepseek-ai/dsh-shell 包清单：shell executor 契约（Service Definition）。',
   'tags': ['configuration', 'package-manifest']},
  'packages/shell/shell/src/index.ts': {
   'type': 'file', 'complexity': 'moderate',
   'summary': 'ctx.shell 能力 seam 的 Service Definition：抽象 bash 执行服务（子类实现抽象方法后作为插件加载，一个 context 一个实现，重复加载即抛）；再导出 DSH_ENV_PREFIX 与类型词汇。',
   'tags': ['service-definition', 'contract', 'cordis'],
   'members': [
    {'kind': 'class', 'name': 'ShellExecutor', 'start': 64, 'end': 94,
     'summary': 'ctx.shell 的抽象 Service：前台 run/后台 spawn 的契约面，请求→Spec 显式解析步的拥有者；执行策略明确不在 executor 内。',
     'tags': ['service-definition', 'abstract-base', 'exported'], 'complexity': 'moderate', 'exported': True}]},
  'packages/shell/shell/src/types.ts': {
   'type': 'file', 'complexity': 'moderate',
   'summary': 'executor seam 的执行类型：ShellExecRequest/Spec（显式默认解析）、ShellExecution/ShellProcess（后台句柄与状态）、ShellRunResult、后台双流的非消费偏移读取器；托管环境与捕获输出词汇归 subprocess seam 并在此再导出保持单一导入根。',
   'tags': ['type-definition', 'request-spec', 'process-handles']},
  'packages/shell/shell/tsconfig.json': {
   'type': 'config', 'complexity': 'simple',
   'summary': 'dsh-shell 的 TypeScript 编译配置。',
   'tags': ['configuration', 'typescript']},
  'packages/shell/shell-env/README.md': {
   'type': 'document', 'complexity': 'moderate',
   'summary': 'dsh-shell-env 包参考：每个模型 shell 调用共享的受信 DSH_* 环境——内置事实（DSH_HOME/DSH_SHELL/DSH_SESSION_ID/DSH_PROFILE*）+插件可注册的 effect 作用域事实；重复所有权与未声明运行时键都会大声失败。',
   'tags': ['documentation', 'package-reference', 'environment']},
  'packages/shell/shell-env/package.json': {
   'type': 'config', 'complexity': 'simple',
   'summary': '@deepseek-ai/dsh-shell-env 包清单：DSH_* 环境注册表插件。',
   'tags': ['configuration', 'package-manifest']},
 },
 'extra_edges': [
  {'source': 'class:packages/shell/bash-local/src/index.ts:LocalBashExecutor', 'target': 'class:packages/shell/shell/src/index.ts:ShellExecutor', 'type': 'inherits', 'direction': 'forward', 'weight': 0.9},
  {'source': 'class:packages/shell/pwsh-local/src/index.ts:PwshLocalExecutor', 'target': 'class:packages/shell/shell/src/index.ts:ShellExecutor', 'type': 'inherits', 'direction': 'forward', 'weight': 0.9},
  {'source': 'class:packages/shell/bash-sandbox/src/index.ts:SandboxBashExecutor', 'target': 'class:packages/shell/bash-local/src/index.ts:LocalBashExecutor', 'type': 'inherits', 'direction': 'forward', 'weight': 0.9},
  {'source': 'class:packages/shell/pwsh-sandbox/src/index.ts:SandboxPwshExecutor', 'target': 'class:packages/shell/pwsh-local/src/index.ts:PwshLocalExecutor', 'type': 'inherits', 'direction': 'forward', 'weight': 0.9},
  {'source': 'class:packages/shell/bash-sandbox/src/index.ts:SandboxBashExecutor', 'target': 'function:packages/shell/bash-sandbox/src/helpers.ts:classifyDenial', 'type': 'calls', 'direction': 'forward', 'weight': 0.8},
  {'source': 'class:packages/shell/pwsh-sandbox/src/index.ts:SandboxPwshExecutor', 'target': 'function:packages/shell/pwsh-sandbox/src/helpers.ts:classifyRunnerFailure', 'type': 'calls', 'direction': 'forward', 'weight': 0.8},
 ],
}
