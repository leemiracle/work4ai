# batch-029 semantic data (terminal group READMEs, terminal package manifest, terminal-bash backend)
BATCH = {
 'files': {
  'packages/terminal/README.md': {
   'type': 'document', 'complexity': 'simple',
   'summary': 'terminal 能力组总览：持久 PTY 会话族——owner 隔离的会话管理（terminal）+shipped shell 后端（terminal-bash，POSIX bash/Windows pwsh）；会话进程本地、不跨 harness 重启存活。',
   'tags': ['documentation', 'package-group', 'terminal', 'overview']},
  'packages/terminal/terminal/README.md': {
   'type': 'document', 'complexity': 'moderate',
   'summary': 'dsh-terminal 包参考：owner 作用域持久终端会话的 ctx.terminals 服务——铸造不透明会话 id、经注册后端路由会话创建、owner/服务销毁时等待静默清理；自身不定义终端机制（spawn 与就绪归后端，呈现归工具层）。',
   'tags': ['documentation', 'package-reference', 'service-definition', 'pty']},
  'packages/terminal/terminal/package.json': {
   'type': 'config', 'complexity': 'simple',
   'summary': '@deepseek-ai/dsh-terminal 包清单：持久终端会话契约服务。',
   'tags': ['configuration', 'package-manifest']},
  'packages/terminal/terminal-bash/README.md': {
   'type': 'document', 'complexity': 'moderate',
   'summary': 'dsh-terminal-bash 包参考：shipped shell 后端——沙箱策略下的持久交互 bash/pwsh（shellDialect 设置），就绪检测+有界行式输出；与本地/远程执行世界经挂载的 subprocess provider 组合，全屏终端应用在契约之外。',
   'tags': ['documentation', 'package-reference', 'backend', 'pty']},
  'packages/terminal/terminal-bash/package.json': {
   'type': 'config', 'complexity': 'simple',
   'summary': '@deepseek-ai/dsh-terminal-bash 包清单：shell 类型终端后端插件。',
   'tags': ['configuration', 'package-manifest']},
  'packages/terminal/terminal-bash/src/config.ts': {
   'type': 'file', 'complexity': 'moderate',
   'summary': '本地 PTY 后端的校验配置：backendType（默认 shell）、shellDialect（bash/pwsh，选择 argv/env/启动默认值）与 sandbox 模式栅栏等字段的 schemastery 声明、resolveConfig 解析与 validateConfig 拒绝未知键。',
   'tags': ['configuration', 'schemastery', 'validation'],
   'members': [
    {'kind': 'function', 'name': 'resolveConfig', 'start': 78, 'end': 110,
     'summary': '把插件配置解析为后端可用配置（方言默认值、期限与保留预算）。',
     'tags': ['resolution', 'exported'], 'complexity': 'moderate', 'exported': True},
    {'kind': 'function', 'name': 'validateConfig', 'start': 119, 'end': 126,
     'summary': '配置写入校验：未知键与非法方言组合大声失败。',
     'tags': ['validation', 'exported'], 'complexity': 'moderate', 'exported': True}]},
  'packages/terminal/terminal-bash/src/index.ts': {
   'type': 'file', 'complexity': 'complex',
   'summary': 'terminal-bash 插件入口（inject=terminals/sandboxPolicy/subprocess/workingDirectory）：注册 shell 后端类型；沙箱模式栅栏在持久会话打开期间阻止会话级 sandbox/mode 变更；BashTerminalBackend 把创建路由到 LocalPtySession 并处理启动失败清理。',
   'tags': ['entry-point', 'plugin', 'backend', 'sandbox-fence'],
   'members': [
    {'kind': 'class', 'name': 'BashTerminalBackend', 'start': 181, 'end': 228,
     'summary': '实现 TerminalBackend 的 shell 后端：就绪检测、spawn argv 装配（方言相关）、启动失败后的启动清理拒绝路径。',
     'tags': ['backend', 'exported'], 'complexity': 'complex', 'exported': True},
    {'kind': 'function', 'name': 'apply', 'start': 231, 'end': 231,
     'summary': '插件 apply：向 ctx.terminals 注册 shell 后端类型。',
     'tags': ['plugin-entry', 'exported'], 'complexity': 'moderate', 'exported': True},
    {'kind': 'function', 'name': 'ensureSandboxModeFence', 'start': 36, 'end': 58,
     'summary': '为 owner 安装沙箱模式栅栏：持久终端打开或创建中时拒绝 session 级 sandbox/mode 变更事件（internal/dispatch 拦截）。',
     'tags': ['fence', 'sandbox'], 'complexity': 'moderate'}]},
  'packages/terminal/terminal-bash/src/session.ts': {
   'type': 'file', 'complexity': 'complex',
   'summary': '持久 PTY 会话实现（793 行核心）：LocalPtySession 实现 TerminalBackendSession——@xterm/headless 惰性加载做终端协议回写、BoundedTextBuffer 摊销保留的行式输出、LocalSendOperation 单次发送的生命周期（前台 pgid 跟踪/取消/截断继承）、就绪证据重置与 utf8 尾部安全截断。',
   'tags': ['pty', 'session', 'xterm', 'bounded-output'],
   'members': [
    {'kind': 'class', 'name': 'LocalPtySession', 'start': 237, 'end': 793,
     'summary': '实现 TerminalBackendSession 的本地 PTY 会话：initialize/startSend/read/signal/status/close 契约面；经 subprocess 终端句柄驱动 xterm headless 仿真器，管理发送操作集合与协议回写串行化。',
     'tags': ['pty', 'session', 'exported'], 'complexity': 'complex', 'exported': True},
    {'kind': 'class', 'name': 'LocalSendOperation', 'start': 158, 'end': 234,
     'summary': '实现 TerminalSendOperation 的单次发送：输出缓冲、settle/fail 终局、取消请求与初始前台 pgid 跟踪（stdin 等待裁决）。',
     'tags': ['send-operation', 'exported'], 'complexity': 'complex', 'exported': True},
    {'kind': 'class', 'name': 'BoundedTextBuffer', 'start': 54, 'end': 156,
     'summary': '有界文本缓冲：追加时摊销保留（块链+字节数/换行预算），读时组装并报告截断标志。',
     'tags': ['buffer', 'bounded'], 'complexity': 'complex', 'exported': True}]},
  'packages/terminal/terminal-bash/tsconfig.json': {
   'type': 'config', 'complexity': 'simple',
   'summary': 'dsh-terminal-bash 的 TypeScript 编译配置。',
   'tags': ['configuration', 'typescript']},
 },
 'extra_edges': [
  {'source': 'class:packages/terminal/terminal-bash/src/index.ts:BashTerminalBackend', 'target': 'class:packages/terminal/terminal-bash/src/session.ts:LocalPtySession', 'type': 'calls', 'direction': 'forward', 'weight': 0.8},
  {'source': 'class:packages/terminal/terminal-bash/src/session.ts:LocalPtySession', 'target': 'class:packages/terminal/terminal-bash/src/session.ts:LocalSendOperation', 'type': 'calls', 'direction': 'forward', 'weight': 0.8},
  {'source': 'class:packages/terminal/terminal-bash/src/session.ts:LocalPtySession', 'target': 'class:packages/terminal/terminal-bash/src/session.ts:BoundedTextBuffer', 'type': 'calls', 'direction': 'forward', 'weight': 0.8},
 ],
}
