# 12 · WASM 多形态分发与编辑器接入（vide-lsp-wasm + editors/vscode）

## 角色定位

同一个 Rust LSP 核心，要在三种形态下活着：桌面进程（VS Code/Zed 扩展 spawn 的原生二进制）、浏览器 playground（WASM 模块）、CI/CLI。`crates/vide-lsp-wasm` 把 server 编译成 Emscripten 目标并暴露 C ABI；`src/browser.rs`（主 crate）提供无 stdio 环境的会话驱动；`editors/vscode/src/extension.ts` 是桌面接插件——管理 server 生命周期、命令、状态栏与中间件。三形态共享 `GlobalState` 与全部语义层，只在「传输层」分叉：桌面是 stdio 线程，浏览器是「调一次函数、拉一串消息」的轮询模型。架构红利是**LSP 逻辑与运行时载体彻底解耦，新编辑器接入只需新传输适配**。

## 内部结构

**vide-lsp-wasm/src/main.rs**（89 行）是 Emscripten 入口。L5 空的 `fn main()`（库型 wasm）；L7-16 时间源 `_emscripten_get_now` 转发 emscripten 时钟；L18-20 `thread_local! SERVER: RefCell<BrowserServer>`——单会话、单线程。五个 C 导出构成 ABI：`vide_lsp_message(json_ptr, json_len) -> *mut c_char`（L22-28，喂一条 LSP JSON 消息，返回新消息数组的 JSON）；`vide_lsp_poll`（L30-33，轮询后台产出）；`vide_lsp_reset`（L35-40，丢弃会话）；`vide_lsp_write_file`（L42-59，文件写进 wasm 内存 FS）；`vide_free_string`（L65-70，**返回串归调用方，用完必须 free**）。L72-81 `run_json` 用 `panic::catch_unwind` 把 panic 转成 `{"error": ...}`——wasm 里 panic 不能崩宿主页面；L83-89 `read_utf8` 做指针→String 切片。

**src/browser.rs**（259 行，主 crate）是会话本体。`BrowserServer{session: Option<BrowserSession>}`（L25-28）只允许一次 initialize（L53-55 重复报错）；`BrowserSession{state: GlobalState, router, outgoing}`（L30-34）——**桌面主循环的全部状态原样复用**，只是没有线程。`handle_message_json`（L46-72）：Initialize 走专门握手（L50-59），其余消息经 `state.handle_lsp_message_for_browser(&router, msg)`（event_loop.rs L122-129——与桌面共享的入口，处理完立即 drain）后 `drain_outgoing` 收走积压响应。`poll_json`（L74-84）周期性调 `drain_browser_queued_events`（event_loop.rs L131-144：三段 try_recv 排干任务与 VFS 队列）模拟主循环下一拍。`initialize`（L91-155）：解析 InitializeParams、构造 Config（L116-129）、建 GlobalState 与 router、发起首轮 workspace reload（L142-143），首个响应连同 config 告警批量返回（L144-152）。`browser_server_caps`（L157-164）抹掉 `execute_command_provider`——L159-162 注释：同页可能跑多个 lab 实例，executeCommand 会注册进页面全局命令注册表，而它们是桌面入口。

**js/vide-lsp.adapter.js**（119 行）是 JS 侧适配：`createVideLspEngine(options)`（L3-28）加载 `vide-core.js`/`vide-core.wasm`（locateFile 处理查询串防缓存混淆，L6-10），先 `writeWorkspace` 落盘初始文件，返回 `{send, poll, writeFile, reset}` 四方法。`drainMessages`（L30-40）循环调 `vide_lsp_poll` 至多 16 轮收干消息；`writeWorkspace`（L42-57）做路径规范化并**拒绝 `..` 逃逸**（L52-54）；`callJson`（L68-91）是 malloc/free 的手工内存协议。

**editors/vscode/src/extension.ts**（1126 行）：`createClient`（L761-819）组装 ServerOptions（L773-787，run/debug 双环境，debug 配 RUST_LOG=debug + full backtrace——`createServerEnv` L585-594）与 clientOptions（L789-810：documentSelector 覆盖 verilog/systemverilog/manifest glob L790-794，middleware 两件——references 的 includeDeclaration 注入 L803-806 与 rename 的 `provideExpandedRenameEdits` L807）；`provideExpandedRenameEdits`（L452-531）实现「递归重命名连通端口」交互闭环：查 `renameExpansionInfo`（L482-489）拿增量符号数 → 弹三选（L499-508）→ 递归分支过冲突确认（L518-520）→ 发 `expandedRename` 换 WorkspaceEdit。`getServerPath`（L314-362）解析平台目录并自动 chmod；`resolveServerLaunch`（L553-583）优先 `vide.server.command`，缺失回落捆绑二进制并给出可操作的报错（L563-567）。`activate`（L986-1109）注册 restart/reloadWorkspace/runQiheAnalysis 等命令、Qihe 状态栏与通知（L229-285）、配置变更触发重启确认（L1084-1103），最后 `startClient` 与 manifest 缺失引导（L650-683）。

## 外部连接

wasm 侧上游是主 crate `vide`（browser.rs 经 lib.rs L21 的 `pub mod browser` 导出）；构建依赖 slang-sys 的 emscripten 分支（第 4 篇 build.rs L305-313 的 `-fwasm-exceptions`）。桌面侧 extension.ts 依赖 `vscode-languageclient/node` 与本目录 platform.ts、initializationOptions.ts、videStatus.ts、projectConfig.ts。扩展间协议：LSP 标准方法 + 私有命令（`vide.server.runQiheAnalysis`/`vide.server.renameExpansionInfo`/`vide.server.expandedRename`，L48-51）与通知（L52-53）。playground 消费 adapter.js 的 engine API。

## 数据流

浏览器里敲一个字符：playground 前端调 `engine.send({method: "textDocument/didChange", ...})` → adapter.js `callJson` 序列化、malloc、调 `vide_lsp_message` → Rust 侧 SERVER 借出，`handle_message_json` → `GlobalState::handle_lsp_message_for_browser`（桌面同款分派 + 立即 drain）→ 变更进 VFS/RootDb、诊断任务排进线程池（Emscripten 下退化为同线程）→ `drain_outgoing` 收集响应 → JSON 数组返回指针 → adapter.js 解析后继续 `drainMessages` 轮询至多 16 轮 → `vide_free_string` 释放。桌面形态则不同：LanguageClient 直接 spawn 二进制（L773-787），stdio 承载同一套 JSON-RPC。两种形态在 `GlobalState::handle_event` 汇合——「核心一份、传输多变」的实证。

## 设计决策

**为什么 WASM 用 C ABI + JSON 字符串而不是直接 LSP over postMessage？** Emscripten 的 wasm 与 JS 间最稳的边界是 `(ptr, len) -> ptr` 字节协议；JSON 序列化复用 lsp_server::Message 的 serde 实现，零额外成本。所有权协议虽手工，却换来语言中立。

**为什么 browser 会话复用 GlobalState 而非精简版？** 维护两套状态机是行为漂移的温床。`handle_lsp_message_for_browser` 与 `drain_browser_queued_events`（event_loop.rs L122-144）以不到 25 行把「线程驱动的循环」改造成「函数调用驱动的循环」，桌面测试顺手覆盖浏览器语义。代价是 capabilities 裁剪（browser.rs L157-164）。

**为什么扩展端 rename 走 middleware 而非自定义请求直连？** 保留标准 `textDocument/rename` 的编辑器互操作性（Zed 等只认标准方法）；middleware 先探测增量信息再决定是否走私有 `expandedRename`，标准路径始终是回退（L495-497）。

**为什么 manifest 缺失要主动提示创建？** 语义功能依赖 compilation profile（第 6 篇），无 manifest 时体验断崖式下降。`promptForMissingProjectConfigs`（L650-683）把「配置缺失」变成一次性引导，创建后重启装载。

## 新人提示

1. 调 wasm 内存问题先看 adapter.js 的双重 finally（L72-90）：任何提前 return 都会漏 free；新增导出函数照抄 `callJson`/`callVoid` 模板。
2. 浏览器诊断「只出来一半」通常是没轮询：`engine.poll()` 要前端定时驱动，16 轮上限防死循环。
3. 改 server capabilities 后两侧都要看：browser_server_caps 的裁剪列表（browser.rs L157-164）与 package.json 的 contributes 需同步。
4. VS Code 端排查启动失败看 Output 面板「Vide Language Server」频道——log 覆盖路径解析、chmod、环境变量全链路（L331-359）。
5. 私有协议（qihe/rename 命令族）改字段要三处同步：server 的 lsp_ext handler、extension.ts 的类型与调用（L402-451）、playground 若有引用。
