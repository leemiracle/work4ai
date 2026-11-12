# batch-030 semantic data (ssh group: fs-ssh, sandbox-ssh, ssh connection/helper/protocol, helper-runtime)
BATCH = {
 'files': {
  'packages/ssh/README.md': {
   'type': 'document', 'complexity': 'simple',
   'summary': 'ssh 能力组总览：共享 SSH helper 上的远程执行族——连接契约（ssh）+远程文件系统（fs-ssh）+远程沙箱（sandbox-ssh）+远程子进程（subprocess-ssh）+打包 helper 运行时（ssh-helper-runtime）。',
   'tags': ['documentation', 'package-group', 'ssh', 'overview']},
  'packages/ssh/fs-ssh/README.md': {
   'type': 'document', 'complexity': 'moderate',
   'summary': 'dsh-fs-ssh 包参考：与 SSH 子进程/沙箱 provider 配套的远程文件系统——保留远端身份，原子变更由 helper 拥有，fs.resolve/stat/readText/write/move/edit 全部经 SSH RPC 带模式限制执行。',
   'tags': ['documentation', 'package-reference', 'filesystem', 'ssh']},
  'packages/ssh/fs-ssh/package.json': {
   'type': 'config', 'complexity': 'simple',
   'summary': '@deepseek-ai/dsh-fs-ssh 包清单：远程文件系统 provider。',
   'tags': ['configuration', 'package-manifest']},
  'packages/ssh/fs-ssh/src/index.ts': {
   'type': 'file', 'complexity': 'complex',
   'summary': '远程文件系统实现：SshFileSystem 继承 FileSystem（inject=ssh+sandboxPolicy），全部文件操作映射为 SSH RPC 调用并以 zod schema 校验远端观察结果；sandboxMode 取自策略服务，远端路径错误码保留为 FsError 分类。',
   'tags': ['filesystem', 'ssh', 'rpc', 'service-provider'],
   'members': [
    {'kind': 'class', 'name': 'SshFileSystem', 'start': 16, 'end': 124,
     'summary': '继承 FileSystem 的远程文件系统（ctx.fs 的远程实现）：resolve/stat/read/write/move/edit/delete 逐方法转 SSH 请求，结果经 schemas.ts 严格校验。',
     'tags': ['filesystem', 'ssh', 'exported'], 'complexity': 'complex', 'exported': True}]},
  'packages/ssh/fs-ssh/tsconfig.json': {
   'type': 'config', 'complexity': 'simple',
   'summary': 'dsh-fs-ssh 的 TypeScript 编译配置。',
   'tags': ['configuration', 'typescript']},
  'packages/ssh/sandbox-ssh/README.md': {
   'type': 'document', 'complexity': 'moderate',
   'summary': 'dsh-sandbox-ssh 包参考：在 SSH 主机上解析并应用沙箱的远程 argv 包装器——confine 请求经共享 helper 在与其文件系统/子进程同一主机上执行。',
   'tags': ['documentation', 'package-reference', 'sandbox', 'ssh']},
  'packages/ssh/sandbox-ssh/package.json': {
   'type': 'config', 'complexity': 'simple',
   'summary': '@deepseek-ai/dsh-sandbox-ssh 包清单：远程沙箱 provider。',
   'tags': ['configuration', 'package-manifest']},
  'packages/ssh/sandbox-ssh/src/index.ts': {
   'type': 'file', 'complexity': 'simple',
   'summary': '远程沙箱 provider：SshSandboxProvider 继承 SandboxProvider（inject=ssh），confine 把 argv+policy 发给 helper 并按 zod facts schema 校验返回（enforcement/denialSignatures/runnerFailureRules），失败归一为 SandboxUnavailableError。',
   'tags': ['sandbox', 'ssh', 'service-provider'],
   'members': [
    {'kind': 'class', 'name': 'SshSandboxProvider', 'start': 10, 'end': 31,
     'summary': '继承 SandboxProvider 的远程沙箱（ctx.sandbox 的 SSH 实现）：每个约束请求在其文件系统与子进程 provider 同一远端主机上解析。',
     'tags': ['sandbox', 'ssh', 'exported'], 'complexity': 'simple', 'exported': True}]},
  'packages/ssh/sandbox-ssh/tsconfig.json': {
   'type': 'config', 'complexity': 'simple',
   'summary': 'dsh-sandbox-ssh 的 TypeScript 编译配置。',
   'tags': ['configuration', 'typescript']},
  'packages/ssh/ssh/README.md': {
   'type': 'document', 'complexity': 'moderate',
   'summary': 'dsh-ssh 包参考：一个版本匹配 POSIX helper 及其独立转发流的 OpenSSH 连接拥有者——helper 哈希失配拒绝连接、非重连会话（失联即失效全部操作）、租约心跳驱动远端受管清理。',
   'tags': ['documentation', 'package-reference', 'ssh', 'connection']},
  'packages/ssh/ssh/package.json': {
   'type': 'config', 'complexity': 'simple',
   'summary': '@deepseek-ai/dsh-ssh 包清单：SSH 连接契约与 helper 协议（多子路径导出 protocol/schemas/helper）。',
   'tags': ['configuration', 'package-manifest']},
  'packages/ssh/ssh/src/helper-entry.ts': {
   'type': 'file', 'complexity': 'simple',
   'summary': '私有 OpenSSH 进程入口：main 以 stdin/stdout 服务一个 helper 请求（SEA 打包或 node-script 双形态），SIGTERM/SIGHUP/SIGINT 触发中止，任何失败以 stderr 报告+退出码 127。',
   'tags': ['entry-point', 'helper', 'process-entry'],
   'members': [
    {'kind': 'function', 'name': 'main', 'start': 8, 'end': 26,
     'summary': 'helper 进程主函数：装配传输（流+入口路径+形态）并运行 runSshHelper，信号中止与失败退出码语义齐备。',
     'tags': ['entry-point'], 'complexity': 'moderate'}]},
  'packages/ssh/ssh/src/helper-processes.ts': {
   'type': 'file', 'complexity': 'complex',
   'summary': '远端进程拥有与独立转发的字节流：RemoteProcesses 以每进程私有目录+五通道（stdin/stdout/stderr/control/terminal）TLS-PSK 端点管理普通与终端进程，CollectedOutputForwarder 把有界输出经管理通道回传；进程上限 128、文本流上限 128。',
   'tags': ['process-ownership', 'streams', 'tls', 'helper'],
   'members': [
    {'kind': 'class', 'name': 'RemoteProcesses', 'start': 90, 'end': 456,
     'summary': 'helper 侧远端进程管理器：spawn/terminate/terminal 会话的 RPC 处理器，每进程通道端点（TLS 服务器+已连接 socket+挂起集）与过期回收。',
     'tags': ['process-ownership', 'rpc', 'exported'], 'complexity': 'complex', 'exported': True},
    {'kind': 'class', 'name': 'CollectedOutputForwarder', 'start': 53, 'end': 87,
     'summary': '把进程输出快照经管理通道分帧转发回客户端（有界+截断标志）。',
     'tags': ['output', 'forwarding'], 'complexity': 'moderate', 'exported': True}]},
  'packages/ssh/ssh/src/helper.ts': {
   'type': 'file', 'complexity': 'complex',
   'summary': '私有 POSIX SSH helper 主体：runSshHelper 组装私有 Cordis Context（沙箱策略/沙箱文件系统/本地子进程/本地沙箱四插件）承载文件与进程效果，经 SshRpcPeer 服务 fs.*/sandbox/process.* 方法，入口摘要与客户端比对，通道关闭或租约到期即清理。',
   'tags': ['helper', 'rpc-server', 'composition', 'ssh'],
   'members': [
    {'kind': 'function', 'name': 'runSshHelper', 'start': 56, 'end': 289,
     'summary': 'helper 主循环（234 行）：认证 hello、方法分派到本地 provider、远端进程与文本流生命周期、受管清理（租约心跳/通道关闭/进程退出）。',
     'tags': ['helper', 'rpc', 'exported'], 'complexity': 'complex', 'exported': True},
    {'kind': 'function', 'name': 'services', 'start': 28, 'end': 36,
     'summary': '组装 helper 的私有 Cordis Context（SessionProjectionRegistry/SandboxPolicyService/SandboxedFileSystem/LocalSubprocessRuntime/LocalSandboxProvider）。',
     'tags': ['composition'], 'complexity': 'simple'}]},
  'packages/ssh/ssh/src/index.ts': {
   'type': 'file', 'complexity': 'complex',
   'summary': 'OpenSSH 连接拥有者（ctx.ssh 的 Service Definition）：SshConnection spawn 版本匹配的 helper 子进程、经 SshRpcPeer 发有界请求（管理类与普通类分开限流）、维护 ready Hello 与租约心跳；非重连设计——连接丢失使全部活动操作失效且不重放请求。',
   'tags': ['service-definition', 'connection', 'ssh', 'cordis'],
   'members': [
    {'kind': 'class', 'name': 'SshConnection', 'start': 59, 'end': 329,
     'summary': 'ctx.ssh 的 Cordis Service：持有 OpenSSH 子进程与 RPC peer，request() 面向消费者（zod schema 校验响应），配置含 host/launch/helper+helperHash/workspace/请求预算与租约。',
     'tags': ['service-definition', 'connection', 'exported'], 'complexity': 'complex', 'exported': True}]},
  'packages/ssh/ssh/src/protocol.ts': {
   'type': 'file', 'complexity': 'complex',
   'summary': 'SSH 客户端与私有远端 helper 之间的有界版本化协议：SSH_PROTOCOL_VERSION=3、帧四型（request/result/error/cancel）discriminatedUnion 校验、管理类请求（heartbeat/close/process.terminate/fs.streamClose）独立容量配额；SshRpcPeer 拥有 pending 调用并在连接丢失时拒绝模糊操作。',
   'tags': ['protocol', 'rpc', 'framing', 'validation'],
   'members': [
    {'kind': 'class', 'name': 'SshRpcPeer', 'start': 58, 'end': 235,
     'summary': 'RPC 对等端：请求/结果/错误/取消帧的读写与 pending 管理，连接丢失时全部挂起调用定向失败（绝不重放）。',
     'tags': ['rpc', 'peer', 'exported'], 'complexity': 'complex', 'exported': True},
    {'kind': 'class', 'name': 'RemoteOperationError', 'start': 50, 'end': 55,
     'summary': '保留远端类型化文件系统/沙箱 code 的远程操作错误。',
     'tags': ['error-handling', 'exported'], 'complexity': 'simple', 'exported': True}]},
  'packages/ssh/ssh/src/schemas.ts': {
   'type': 'file', 'complexity': 'moderate',
   'summary': 'SSH helper 请求与远端观察的严格 JSON 校验：branded 进程/文本流 id schema、远端 POSIX 绝对路径（拒绝空字节）、target/info/policy/hello/spawn/done 等全套 zod schema，输出快照帧上限常量。',
   'tags': ['schemas', 'zod', 'validation']},
  'packages/ssh/ssh/src/stream-security.ts': {
   'type': 'file', 'complexity': 'simple',
   'summary': '转发流的 TLS-PSK 认证：即使远端路径名被替换也认证对端——无证书 PSK+AEAD 记录（PSK-AES256-GCM-SHA384，无未认证密码套件回落），每流 256 位密钥从不作为数据传输。',
   'tags': ['tls', 'psk', 'security', 'streams'],
   'members': [
    {'kind': 'function', 'name': 'authenticateStream', 'start': 18, 'end': 47,
     'summary': '用私有管理通道派发的每流密钥认证转发 socket，返回暂停的已认证 TLS 流；中止与超时销毁底层 socket。',
     'tags': ['tls', 'authentication', 'exported'], 'complexity': 'moderate', 'exported': True}]},
  'packages/ssh/ssh/tsconfig.json': {
   'type': 'config', 'complexity': 'simple',
   'summary': 'dsh-ssh 的 TypeScript 编译配置。',
   'tags': ['configuration', 'typescript']},
  'packages/ssh/ssh/tsdown.config.ts': {
   'type': 'config', 'complexity': 'simple',
   'summary': 'dsh-ssh 的 tsdown 打包配置：helper 入口独立打包供远端安装。',
   'tags': ['configuration', 'tsdown', 'build-system']},
  'packages/ssh/ssh-helper-runtime/README.md': {
   'type': 'document', 'complexity': 'moderate',
   'summary': 'dsh-ssh-helper-runtime 包参考：SSH helper 及其受管进程 worker 的私有 SEA 分发器——打包可执行内一次分发 helper 或 worker，Landlock 之类原生资源在 SEA 虚拟文件系统之外解析。',
   'tags': ['documentation', 'package-reference', 'sea', 'packaging']},
  'packages/ssh/ssh-helper-runtime/package.json': {
   'type': 'config', 'complexity': 'simple',
   'summary': '@deepseek-ai/dsh-ssh-helper-runtime 包清单：SEA 打包运行时入口。',
   'tags': ['configuration', 'package-manifest']},
  'packages/ssh/ssh-helper-runtime/src/index.ts': {
   'type': 'file', 'complexity': 'moderate',
   'summary': '私有 SEA 分发器：runSshHelperRuntime 校验 SEA 环境、用 registerHooks 把平台原生包解析重定向到可执行文件旁的 native/system 清单（Landlock 在 SEA 虚拟文件系统外执行），再按 DSH_SUBPROCESS_RUNNER 选择分发到 SSH helper 或 subprocess runner。',
   'tags': ['sea', 'bootstrap', 'dispatch'],
   'members': [
    {'kind': 'function', 'name': 'runSshHelperRuntime', 'start': 14, 'end': 39,
     'summary': 'SEA 引导入口：原生资源重定向后按选择器分发 helper/worker 入口，非 SEA 环境显式失败。',
     'tags': ['bootstrap', 'dispatch', 'exported'], 'complexity': 'moderate', 'exported': True}]},
  'packages/ssh/ssh-helper-runtime/tsconfig.json': {
   'type': 'config', 'complexity': 'simple',
   'summary': 'dsh-ssh-helper-runtime 的 TypeScript 编译配置。',
   'tags': ['configuration', 'typescript']},
  'packages/ssh/subprocess-ssh/README.md': {
   'type': 'document', 'complexity': 'moderate',
   'summary': 'dsh-subprocess-ssh 包参考：用共享 SSH helper 实现 ctx.subprocess——可执行查找/普通进程/fd 7 控制流量/终端会话与 SSH 文件系统并行；远端原生进程拥有者管终止与静默，消费者继续拥有命令语义/输出上限/执行期限。',
   'tags': ['documentation', 'package-reference', 'subprocess', 'ssh']},
 },
 'extra_edges': [
  {'source': 'class:packages/ssh/fs-ssh/src/index.ts:SshFileSystem', 'target': 'class:packages/fs/fs/src/index.ts:FileSystem', 'type': 'inherits', 'direction': 'forward', 'weight': 0.9},
  {'source': 'class:packages/ssh/sandbox-ssh/src/index.ts:SshSandboxProvider', 'target': 'class:packages/ssh/ssh/src/index.ts:SshConnection', 'type': 'calls', 'direction': 'forward', 'weight': 0.8},
  {'source': 'class:packages/ssh/ssh/src/index.ts:SshConnection', 'target': 'class:packages/ssh/ssh/src/protocol.ts:SshRpcPeer', 'type': 'calls', 'direction': 'forward', 'weight': 0.8},
  {'source': 'function:packages/ssh/ssh/src/helper.ts:runSshHelper', 'target': 'class:packages/ssh/ssh/src/helper-processes.ts:RemoteProcesses', 'type': 'calls', 'direction': 'forward', 'weight': 0.8},
  {'source': 'function:packages/ssh/ssh/src/helper-entry.ts:main', 'target': 'function:packages/ssh/ssh/src/helper.ts:runSshHelper', 'type': 'calls', 'direction': 'forward', 'weight': 0.8},
  {'source': 'function:packages/ssh/ssh-helper-runtime/src/index.ts:runSshHelperRuntime', 'target': 'function:packages/ssh/ssh/src/helper.ts:runSshHelper', 'type': 'calls', 'direction': 'forward', 'weight': 0.8},
  {'source': 'class:packages/ssh/ssh/src/helper-processes.ts:RemoteProcesses', 'target': 'function:packages/ssh/ssh/src/stream-security.ts:authenticateStream', 'type': 'calls', 'direction': 'forward', 'weight': 0.8},
 ],
}
