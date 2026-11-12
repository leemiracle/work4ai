# batch-026 semantic data (shell-env src, tool-bash, tool-bash-persistent, tool-pwsh, tool-pwsh-persistent)
BATCH = {
 'files': {
  'packages/shell/shell-env/src/index.ts': {
   'type': 'file', 'complexity': 'complex',
   'summary': 'ctx.shellEnv 注册表实现（name=shell-env）：内置 shell 事实（DSH_HOME/DSH_SHELL=1/DSH_SESSION_ID/DSH_PROFILE*）由注册表自持，插件可注册 effect 作用域的可枚举附加事实；重复所有权与未声明运行时键大声失败。',
   'tags': ['service-definition', 'registry', 'environment', 'cordis'],
   'members': [
    {'kind': 'class', 'name': 'ShellEnvRegistry', 'start': 93, 'end': 202,
     'summary': 'ctx.shellEnv 的 Cordis Service：受信 DSH_* 变量的注册/枚举/逐执行收集，内置事实读取 launcher 提供的 profileContext，插件事实随 effect 处置。',
     'tags': ['service-definition', 'registry', 'exported'], 'complexity': 'complex', 'exported': True},
    {'kind': 'function', 'name': 'apply', 'start': 209, 'end': 211,
     'summary': '插件 apply：注册 ShellEnvRegistry 服务。',
     'tags': ['plugin-entry', 'exported'], 'complexity': 'simple', 'exported': True}]},
  'packages/shell/shell-env/tsconfig.json': {
   'type': 'config', 'complexity': 'simple',
   'summary': 'dsh-shell-env 的 TypeScript 编译配置。',
   'tags': ['configuration', 'typescript']},
  'packages/shell/tool-bash/README.md': {
   'type': 'document', 'complexity': 'complex',
   'summary': 'dsh-tool-bash 包参考：模型面 bash 工具——前台+run_in_background 执行（job 注册表组合时每次调用注册 ctx.jobs）、DSH_* 托管环境、逐调用沙箱策略解析与同轮升级面（sandbox_permissions+justification 经 ctx.approval）、拒绝渲染与截断通知。',
   'tags': ['documentation', 'package-reference', 'tool', 'bash']},
  'packages/shell/tool-bash/package.json': {
   'type': 'config', 'complexity': 'simple',
   'summary': '@deepseek-ai/dsh-tool-bash 包清单：模型面 bash 工具插件。',
   'tags': ['configuration', 'package-manifest']},
  'packages/shell/tool-bash/src/background.ts': {
   'type': 'file', 'complexity': 'moderate',
   'summary': 'bash 进程句柄的通用 job 适配：注册表记录的终局 outcome、它泵出的拉取源、前台调用停止等待时渲染的环形读——沙箱事实（runner 未跑命令/拒绝+升级提示）以标记形式附加。',
   'tags': ['jobs', 'background', 'adaptation'],
   'members': [
    {'kind': 'function', 'name': 'processJob', 'start': 99, 'end': 129,
     'summary': '把后台 ShellProcess 适配为 JobHooks 生命周期：outcome/sources/ring 读的接线与终局标记追加。',
     'tags': ['jobs', 'exported'], 'complexity': 'complex', 'exported': True},
    {'kind': 'function', 'name': 'processOutcome', 'start': 44, 'end': 55,
     'summary': '把已定局运行的沙箱/退出事实投影为 job 终局 outcome。',
     'tags': ['jobs', 'outcome', 'exported'], 'complexity': 'moderate', 'exported': True}]},
  'packages/shell/tool-bash/src/index.ts': {
   'type': 'file', 'complexity': 'complex',
   'summary': '模型面 bash 工具主体（apply 355 行）：defineTool 注册 bash 工具——参数校验、工作目录解析、逐调用沙箱策略、前台等待 job 或超时返回 id、后台立即返回 id；部署策略归 tools/pre-execute 与沙箱 executor。',
   'tags': ['tool', 'bash', 'consumer', 'jobs'],
   'members': [
    {'kind': 'function', 'name': 'apply', 'start': 202, 'end': 556,
     'summary': '工具注册主体：bash 工具 schema/描述/呈现器与执行器（前台等待+后台注册 job+升级审批流），经 ctx.tools 注册。',
     'tags': ['plugin-entry', 'tool-registration', 'exported'], 'complexity': 'complex', 'exported': True},
    {'kind': 'function', 'name': 'canonicalBashResult', 'start': 155, 'end': 179,
     'summary': '把 shell 运行结果整形为规范的工具结果（含截断通知与退出状态）。',
     'tags': ['result-shaping'], 'complexity': 'moderate'},
    {'kind': 'function', 'name': 'presentBashCall', 'start': 108, 'end': 124,
     'summary': 'UI 调用呈现器：终端卡片形态的调用视图。',
     'tags': ['presentation'], 'complexity': 'moderate'}]},
  'packages/shell/tool-bash/src/render.ts': {
   'type': 'file', 'complexity': 'moderate',
   'summary': 'bash 工具的模型面结果渲染：stdout→标记 stderr 节→退出状态标记；非零退出是报告而非错误（模型自行决定反应），只有基础设施失败（spawn 错误/中止）才是 isError。',
   'tags': ['rendering', 'model-output', 'exit-status'],
   'members': [
    {'kind': 'function', 'name': 'renderResult', 'start': 28, 'end': 66,
     'summary': '把完成运行渲染为模型可见文本：流截断通知附 spill 路径，退出状态以标记呈现。',
     'tags': ['rendering', 'exported'], 'complexity': 'moderate', 'exported': True},
    {'kind': 'function', 'name': 'renderJobRead', 'start': 97, 'end': 118,
     'summary': '渲染一次后台 job 的环形读取增量。',
     'tags': ['rendering', 'jobs', 'exported'], 'complexity': 'moderate', 'exported': True}]},
  'packages/shell/tool-bash/tsconfig.json': {
   'type': 'config', 'complexity': 'simple',
   'summary': 'dsh-tool-bash 的 TypeScript 编译配置。',
   'tags': ['configuration', 'typescript']},
  'packages/shell/tool-bash-persistent/README.md': {
   'type': 'document', 'complexity': 'moderate',
   'summary': 'dsh-tool-bash-persistent 包参考：经 owner 作用域 PTY seam 的持久 bash 工具——单所有者会话、滚动缓冲截断告知、命令完成标记轮询与会话退出响应。',
   'tags': ['documentation', 'package-reference', 'persistent-shell', 'pty']},
  'packages/shell/tool-bash-persistent/package.json': {
   'type': 'config', 'complexity': 'simple',
   'summary': '@deepseek-ai/dsh-tool-bash-persistent 包清单：持久 bash 工具插件。',
   'tags': ['configuration', 'package-manifest']},
  'packages/shell/tool-bash-persistent/src/index.ts': {
   'type': 'file', 'complexity': 'complex',
   'summary': '持久 bash 工具实现：persistentShells 会话注册表管理 owner 隔离的 PTY 会话，executeCommand 包装命令并轮询完成标记（一页 1000 行足够找刚发出的标记，整段滚动缓冲仅在命令定局或需要部分输出时组装）；截断/前缀丢失/重置/超时各有固定文案。',
   'tags': ['tool', 'persistent-shell', 'pty', 'scrollback'],
   'members': [
    {'kind': 'function', 'name': 'apply', 'start': 467, 'end': 487,
     'summary': '插件 apply：向 ctx.tools 注册持久 bash 工具。',
     'tags': ['plugin-entry', 'exported'], 'complexity': 'moderate', 'exported': True},
    {'kind': 'function', 'name': 'persistentShells', 'start': 224, 'end': 298,
     'summary': '会话注册表工厂：按 agent 持有/复用持久 PTY 会话并处理会话退出与重置。',
     'tags': ['registry', 'sessions'], 'complexity': 'complex'},
    {'kind': 'function', 'name': 'executeCommand', 'start': 300, 'end': 393,
     'summary': '单条命令执行：包装标记→写入 PTY→轮询完成→按 deadline 截断，超时以 PERSISTENT_BASH_TIMEOUT 报告。',
     'tags': ['execution', 'polling'], 'complexity': 'complex'},
    {'kind': 'function', 'name': 'registerPersistentBash', 'start': 400, 'end': 441,
     'summary': '定义并注册持久 bash 工具（schema+执行器接线）。',
     'tags': ['tool-registration'], 'complexity': 'complex'}]},
  'packages/shell/tool-bash-persistent/tsconfig.json': {
   'type': 'config', 'complexity': 'simple',
   'summary': 'dsh-tool-bash-persistent 的 TypeScript 编译配置。',
   'tags': ['configuration', 'typescript']},
  'packages/shell/tool-pwsh/README.md': {
   'type': 'document', 'complexity': 'complex',
   'summary': 'dsh-tool-pwsh 包参考：Windows 组合的模型面 pwsh 工具（PowerShell 方言：原生 C:\\ 路径与 $env:NAME 变量），与 dsh-tool-bash 逐调用镜像——job 注册、DSH_* 环境、逐调用沙箱策略、升级面与标记渲染同构。',
   'tags': ['documentation', 'package-reference', 'tool', 'pwsh']},
  'packages/shell/tool-pwsh/package.json': {
   'type': 'config', 'complexity': 'simple',
   'summary': '@deepseek-ai/dsh-tool-pwsh 包清单：模型面 pwsh 工具插件。',
   'tags': ['configuration', 'package-manifest']},
  'packages/shell/tool-pwsh/src/background.ts': {
   'type': 'file', 'complexity': 'moderate',
   'summary': 'pwsh 进程句柄的通用 job 适配（tool-bash/background 的逐调用孪生）：终局 outcome、拉取源、环形读与沙箱事实标记。',
   'tags': ['jobs', 'background', 'pwsh'],
   'members': [
    {'kind': 'function', 'name': 'processJob', 'start': 101, 'end': 131,
     'summary': '把后台 pwsh ShellProcess 适配为 JobHooks 生命周期。',
     'tags': ['jobs', 'exported'], 'complexity': 'complex', 'exported': True},
    {'kind': 'function', 'name': 'processOutcome', 'start': 46, 'end': 57,
     'summary': '把已定局运行的沙箱/退出事实投影为 job 终局 outcome。',
     'tags': ['jobs', 'outcome', 'exported'], 'complexity': 'moderate', 'exported': True}]},
  'packages/shell/tool-pwsh/src/index.ts': {
   'type': 'file', 'complexity': 'complex',
   'summary': '模型面 pwsh 工具主体（apply 404 行）：与 bash 工具逐调用镜像的 PowerShell 方言契约——路径/环境变量语义、job 注册、沙箱策略、升级审批与标记渲染；呈现为解析退出状态的终端卡片。',
   'tags': ['tool', 'pwsh', 'consumer', 'jobs'],
   'members': [
    {'kind': 'function', 'name': 'apply', 'start': 212, 'end': 615,
     'summary': '工具注册主体：pwsh 工具 schema/描述/执行器（前台等待+后台 job+升级审批）注册到 ctx.tools。',
     'tags': ['plugin-entry', 'tool-registration', 'exported'], 'complexity': 'complex', 'exported': True},
    {'kind': 'function', 'name': 'canonicalPwshResult', 'start': 161, 'end': 187,
     'summary': '把 pwsh 运行结果整形为规范工具结果（截断通知与退出状态）。',
     'tags': ['result-shaping'], 'complexity': 'moderate'},
    {'kind': 'function', 'name': 'pwshDescription', 'start': 121, 'end': 149,
     'summary': '生成 pwsh 工具的动态描述（PowerShell 方言指引）。',
     'tags': ['description'], 'complexity': 'moderate'}]},
  'packages/shell/tool-pwsh/src/render.ts': {
   'type': 'file', 'complexity': 'moderate',
   'summary': 'pwsh 工具的模型面结果渲染（bash 版孪生）：stdout/stderr 标记节/退出状态标记，非零退出是报告非错误。',
   'tags': ['rendering', 'model-output', 'pwsh'],
   'members': [
    {'kind': 'function', 'name': 'renderPwshResult', 'start': 48, 'end': 86,
     'summary': '把完成运行的 pwsh 结果渲染为模型可见文本。',
     'tags': ['rendering', 'exported'], 'complexity': 'moderate', 'exported': True},
    {'kind': 'function', 'name': 'renderPwshJobRead', 'start': 117, 'end': 138,
     'summary': '渲染一次后台 pwsh job 的环形读取增量。',
     'tags': ['rendering', 'jobs', 'exported'], 'complexity': 'moderate', 'exported': True}]},
  'packages/shell/tool-pwsh/tsconfig.json': {
   'type': 'config', 'complexity': 'simple',
   'summary': 'dsh-tool-pwsh 的 TypeScript 编译配置。',
   'tags': ['configuration', 'typescript']},
  'packages/shell/tool-pwsh-persistent/README.md': {
   'type': 'document', 'complexity': 'moderate',
   'summary': 'dsh-tool-pwsh-persistent 包参考：owner 作用域 PTY seam 上的持久 pwsh 工具，与 bash 持久版共享会话注册表/轮询环/重置契约（jscpd 标注的刻意镜像）。',
   'tags': ['documentation', 'package-reference', 'persistent-shell', 'pwsh']},
  'packages/shell/tool-pwsh-persistent/package.json': {
   'type': 'config', 'complexity': 'simple',
   'summary': '@deepseek-ai/dsh-tool-pwsh-persistent 包清单：持久 pwsh 工具插件。',
   'tags': ['configuration', 'package-manifest']},
  'packages/shell/tool-pwsh-persistent/src/index.ts': {
   'type': 'file', 'complexity': 'complex',
   'summary': '持久 pwsh 工具实现（bash 持久版的刻意镜像）：会话注册表、命令包装（Select-String 截断提示方言）、完成标记轮询、滚动缓冲组装与会话退出响应；超时码 PERSISTENT_PWSH_TIMEOUT。',
   'tags': ['tool', 'persistent-shell', 'pty', 'pwsh'],
   'members': [
    {'kind': 'function', 'name': 'apply', 'start': 478, 'end': 498,
     'summary': '插件 apply：向 ctx.tools 注册持久 pwsh 工具。',
     'tags': ['plugin-entry', 'exported'], 'complexity': 'moderate', 'exported': True},
    {'kind': 'function', 'name': 'persistentShells', 'start': 247, 'end': 308,
     'summary': 'pwsh 持久会话注册表：按 agent 持有/复用 PTY 会话并处理退出重置。',
     'tags': ['registry', 'sessions'], 'complexity': 'complex'},
    {'kind': 'function', 'name': 'executeCommand', 'start': 310, 'end': 404,
     'summary': '单条 pwsh 命令执行：包装→写入→轮询完成标记→截断组装。',
     'tags': ['execution', 'polling'], 'complexity': 'complex'},
    {'kind': 'function', 'name': 'registerPersistentPwsh', 'start': 411, 'end': 452,
     'summary': '定义并注册持久 pwsh 工具（schema+执行器接线）。',
     'tags': ['tool-registration'], 'complexity': 'complex'}]},
  'packages/shell/tool-pwsh-persistent/tsconfig.json': {
   'type': 'config', 'complexity': 'simple',
   'summary': 'dsh-tool-pwsh-persistent 的 TypeScript 编译配置。',
   'tags': ['configuration', 'typescript']},
 },
 'extra_edges': [
  {'source': 'function:packages/shell/tool-bash/src/index.ts:apply', 'target': 'function:packages/shell/tool-bash/src/background.ts:processJob', 'type': 'calls', 'direction': 'forward', 'weight': 0.8},
  {'source': 'function:packages/shell/tool-bash/src/index.ts:apply', 'target': 'function:packages/shell/tool-bash/src/render.ts:renderResult', 'type': 'calls', 'direction': 'forward', 'weight': 0.8},
  {'source': 'function:packages/shell/tool-pwsh/src/index.ts:apply', 'target': 'function:packages/shell/tool-pwsh/src/background.ts:processJob', 'type': 'calls', 'direction': 'forward', 'weight': 0.8},
  {'source': 'function:packages/shell/tool-pwsh/src/index.ts:apply', 'target': 'function:packages/shell/tool-pwsh/src/render.ts:renderPwshResult', 'type': 'calls', 'direction': 'forward', 'weight': 0.8},
  {'source': 'function:packages/shell/tool-bash-persistent/src/index.ts:registerPersistentBash', 'target': 'function:packages/shell/tool-bash-persistent/src/index.ts:persistentShells', 'type': 'calls', 'direction': 'forward', 'weight': 0.8},
  {'source': 'function:packages/shell/tool-pwsh-persistent/src/index.ts:registerPersistentPwsh', 'target': 'function:packages/shell/tool-pwsh-persistent/src/index.ts:persistentShells', 'type': 'calls', 'direction': 'forward', 'weight': 0.8},
 ],
}
