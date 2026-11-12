# 05 · Linux 驱动——computer_use_linux（AT-SPI + X11 双栈）

## 一、角色定位

`os_adapter/linux/` 是独立 pip 包 `computer-use-linux`（`pyproject.toml:6-11`，依赖钉死 `python-xlib==0.33`+`Pillow==11.3.0`），protocol-6 三平台驱动中最"轻"的一个：**没有引擎侧组合框架，全部逻辑是"校验函数 + 每域 Pipeline 类 + 一个串行 Server"**。它回答：在一台 Linux 桌面上，如何把 AT-SPI 无障碍树（读）与 X11（截屏/输入/剪贴板）组合成 04 篇那条 JSON-lines 通道的服务端。

- `runtime/server.py`（203 行）：协议端点。docstring（server.py:4）"One protocol thread owns sequencing, request cache and cancellation"——一个协议线程独占定序，读线程只排队帧和取消。
- `runtime/native.py`（365 行）：组合根 `NativeExecution`，装配 20 余个埢单元成三条管线，按 `begin/inspect/execute/capture/finish` 分派（perform，native.py:275-354）。docstring（L4）："Protocol 6 operations; never forward to legacy Reader or Control."
- `contracts/protocol.py`（182 行）：wire 契约件——`Failure/require/fields` 校验原语、`Request` 取消上下文、`desktop_lease` 跨进程桌面锁。

入口 `__main__.py` 极薄（72 行）：三个 flag 解析后 `Server(native_backend, output=output).run()`（`__main__.py:57-68`），并挂 `prctl(PR_SET_PDEATHSIG)`——宿主死了驱动自收（L61-67）。

## 二、内部结构

**server.py**
- `Server`（L20-37）：`inbox = queue.Queue(maxsize=64)`（L29）、`pending` dict+锁、`cache = OrderedDict`（L32）、`high_id` 单调水位（L33）。
- `_reader` 读线程（L51-100）：每行 4MB 上限（L57）、BOM 拒绝、`object_pairs_hook` 拒重复 JSON 字段（L60-66）、`parse_constant` 拒 NaN/Infinity（L71）——与引擎侧帧纪律一一对应。`cancel` 帧（L75-89）只 `ctx.cancelled.set()`，绝不碰执行。
- `execute`（L137-203）单线程执行：`fingerprint = sha256(json.dumps(raw, sort_keys=True))`（server.py:139）——同 id 重放必须逐字节同内容否则 `request_conflict`（L172-176）；id 必须 > `high_id`（L177）；hello（L149-169）协商 `maxTimeoutMs=120000` 并回显 capabilities；Failure 的 `target/effect/context` 从执行上下文回填（L184-192）——错误码是协议字段而非日志文本。

**native.py**
- `CAPABILITIES`（L35-64）28 项基础能力；构造函数按后端探测**动态追加**：`can_capture` → `nativeCapture/nativeCaptureKinds`（L192-194），`can_input` → 5 项（L195-202），两者兼得才给 `nativePointer/nativeDesktopInput`（L203-204）。能力是探测结果不是编译常量。
- 模块级校验函数：`binding()`（L68-86）识别 installation 型与 window 型（六键 `BINDING_KEYS`，L65），断言不变式——instance/rootWindow 与 surface 同生共死（L81）、node 必须挂 window、capture 与 node 互斥（L82-85）；`query()`（L96-164）按八种 kind 校验 inspect，其余直接 `mode_unsupported`（L163）。
- `perform`（L275-354）begin 分支是 30 行校验链，全部在 `resources.acquire` 之前（注释 L276-277："Validate the entire frame before touching a provider or taking a scope"）：clickContract v1 只配 write click（L288-293）、launch 只配 installation binding（L295-302）、capture 目标只收 pointer 类意图（L303-310）、read 不能绑输入意图（L327-328）、桌面级输入要 exclusive（L334-340）、`require(self.current is None, "Another native operation is active.")`（L342）。

**contracts/protocol.py**
- 校验原语（L26-77）：`Failure(detail, code, target, effect, next)` 五字段异常（L26-41）；`integer` 上限 2^53-1（L57）；`string` 拒代理对（L66）。
- `Request` dataclass（L119-150）：`check()` 抛 cancelled/deadline；`sent()`（L135-138）把 effect 从 `none` **单向棘轮**到 `possible`；`pause()`（L140-145）先 `pump()` 事件再睡。
- `desktop_lease`（L153-182）：跨进程桌面互斥，安全细节密集——目录属主/权限位校验（L163-167）、锁文件 `O_NOFOLLOW` 0600（L169）、fstat 再验（L171-172）、flock 非阻塞循环配合 `ctx.pause()`（L173-179）。

## 三、外部连接

- 上游：引擎侧 `native/connection.py` 的 `_connect` spawn 本包（POSIX fd 桥）；协议常量两侧成对（4MB 行上限、NaN/BOM 双侧拒绝）。
- 平台底座：`runtime/native_backend.py:12-22` 的 `NativeBackend` 组合 `NativeAccessibility()`（AT-SPI/GIO）+ `connect_desktop(...)`（X11）；`installed()` 用 `gio.AppInfo.get_all()` 列安装应用（L24-25）；`pump()` 分别轮询 desktop/ax/clipboard 三事件源（L45-49）。
- 域内：`NativeQueryPipeline/NativeCapturePipeline/NativeInputPipeline`（native.py:229-259）分别服务 inspect/capture/execute；`NativeResourceScope`（L206-212）管租约。
- **条件耦合**：剪贴板只在 `session_type == "x11"` 时可用（native_backend.py:33-38）——Wayland 会话 paste 直接 `mode_unsupported`。

## 四、数据流

一条 `begin(mode=write, intent=click, target={capture...})`：`_reader` 收帧校验后造 `Request(deadline)` 入 pending+inbox（server.py:90-96）→ 主循环 `execute` → `native.perform` begin 链：键域 → clickContract 白名单 → `binding()` → capture 意图白名单 → decoder → exclusive 检查 → `captures.input(target)`（native.py:334-335）→ `expire()` 清旧租约 → 单操作断言（L341-342）→ `resources.acquire` 返回 token。后续 execute/inspect 进各自管线；长操作内部用 `ctx.pause()` 让出并 `pump()` X11 事件（protocol.py:140-145）——驱动永不吃满线程阻塞 D-Bus。终态经 cache 记录（256 条 FIFO，L199-202）与 `reply` 写 stdout（L39-49）。宿主取消：cancel 帧 set `cancelled`，下一次 `ctx.check()` 抛 `Failure(effect=ctx.effect)`（protocol.py:129-131）——effect 已被 `sent()` 棘轮到 possible，宿主据此知道"可能已部分执行"。

## 五、设计决策与权衡

1. **单协议线程 + 只排队不执行的 reader**：与引擎侧单请求串行互为镜像，无需帧 interleaving。代价是单请求吞吐；收益是 cancel 语义简单、cache/high_id 全免锁竞争。
2. **请求缓存 + 指纹去重**：同 id 同内容直接回缓存（幂等重试安全），异内容 conflict。capabilities 里的 `requestDedup`（native.py:37）——**能力声明即契约**，宿主看到它才敢重试。
3. **effect 单向棘轮**：`sent()` 只许 none→possible（protocol.py:135-138），失败翻译时回填（server.py:187-188）——三值契约的 Linux 最小实现。
4. **能力探测而非配置**：`can_capture/can_input` 决定 capabilities（native.py:192-204），X11 缺席时宿主根本不会发 paste，而不是发了被拒。
5. **desktop_lease 的偏执**：四重校验（注释 L159-160："Do not trust another user's runtime directory or follow a pre-created symlink"）；多驱动实例靠 flock 串行化，等待期可取消。
6. **PDEATHSIG 双保险**：信号 handler 管优雅退出（`__main__.py:58-59`）；`prctl(1, SIGTERM)`（L65）管宿主被 kill -9——孤儿驱动会占着 desktop_lease 锁，必须死；L66-67 还处理 prctl 与 getppid 间的竞态。

## 六、新人提示与坑

- **勘误（图谱 tour 措辞）**：S06 说本仓"形态为模块级 pass 函数 + CONTRACT 声明字典"——源码没有引擎侧 `pipeline.Pass` 节点，实际是**模块级校验函数（native.py:68-164）+ `CAPABILITIES` 清单（list 而非 dict）+ 每域 Pipeline 类**，用词会误导你去 import 不存在的东西。
- **stdout 是协议专线**：`__main__.py:43` `redirect_stdout(sys.stderr)` 包住一切诊断（docstring L16）。printf 打到 stdout 会**直接毒化协议流**，宿主侧报"expected response object"。
- **hello 之前不 import native 资源**：`native_backend` 是工厂函数（`__main__.py:19-22`、server.py:156-159 延迟 import）——`--check-permissions` 可在无 D-Bus 环境跑纯校验。
- **id 水位单向**：引擎重启后 `_next_id` 归 1，但驱动只要没重启 `high_id` 停在旧值——两侧行为配套设计（引擎重连必换驱动进程），别单独复用 Server 而不换进程。
- **AT-SPI 与 X11 是独立双栈**：`resources.py:68` 注释明说"AX may be unavailable while X11 remains usable"；剪贴板仅 X11。排障先分清是哪条栈的问题。
