# _ipc.py 精讲 — 传输无关的 IPC 基石与它的导入期副作用

> 源码：`src/browser_harness/_ipc.py`（201 行）｜图谱层 L01「包入口与路径/IPC 基石」

## ① 角色定位

下划线前缀说明它是**包内私有模块**：整个 harness 的客户端-daemon 通信全部经它，却不对外承诺任何 API 稳定性。它把"POSIX 用 AF_UNIX 命名 socket、Windows 用 TCP 回环"这一平台分裂封装在一组对称原语后面（`connect/request/serve`，_ipc.py:83-106, 165），上层（helpers 的 `_send`、daemon 的 `serve`、admin 的孵化逻辑）完全感知不到平台差异。

它同时还是**运行时文件布局的所有者**：socket、pid、port、log 四类路径的命名与落盘规则都在这里（_ipc.py:51-54）。201 行里近一半是注释——每条防御性代码背后都写清了威胁模型，是这个仓库最值得精读的"安全注释范本"。

## ② 内部结构

- **双目录环境变量**（_ipc.py:8-23）：`BH_RUNTIME_DIR` 放 sock/port/pid——macOS 的 `sun_path` 只有 104 字节，路径必须短，调用方自己负责预算；`BH_TMP_DIR` 放截图/调试覆盖/日志，无长度敏感。二者缺省回落到 paths 模块的默认布局。配套 `*_SHARED=1` 标志决定文件名是裸 `bu` 还是带实例名的 `bu-<NAME>`（`_runtime_stem`/`_tmp_stem`，_ipc.py:41-48）。
- **导入期副作用**（_ipc.py:22-25）：`_TMP.mkdir` 与 `_RUNTIME.mkdir` 在 **import 时**执行，且 `_RUNTIME` 经 `paths.ensure_private_dir` 获得 0700 权限（paths.py:19-24）。也就是说任何 import 本模块的进程都会立刻拥有这两个目录——这让"目录不存在"类竞态从根源消失。
- **路径守卫**：`_check` 用 `_NAME_RE = \A[A-Za-z0-9_-]{1,64}\Z` 拦截 BU_NAME 里的路径穿越（_ipc.py:26, 35-38）。所有 stem 函数先过这道闸。
- **Windows 令牌**：模块级 `_server_token` 初始 None（_ipc.py:32）；`serve()` 在 Windows 分支生成 `secrets.token_hex(32)` 写入 port 文件；daemon `handle()` 对每个请求校验 `req["token"]`。POSIX 分支恒 None——AF_UNIX + 600 权限就是边界，注释把这套"TCP 回环没有 chmod 等价物"的推理写全了。
- **孵化旗标**：`spawn_kwargs`（_ipc.py:72-80）POSIX 返回 `start_new_session=True`；Windows 返回 `CREATE_NEW_PROCESS_GROUP | CREATE_NO_WINDOW`，注释专门解释为何**故意不加** `DETACHED_PROCESS`——它会覆盖 CREATE_NO_WINDOW，让 Windows 给仍属 console 子系统的 python.exe 新开一个控制台。
- **探针双雄**：`ping`（_ipc.py:109-127）与 `identify`（_ipc.py:130-162）都先 connect 再发 `{"meta":"ping"}`，且都先 `isinstance(resp, dict)` 再取字段——注释明说 request 可能解析出 list/标量（陈旧或恶意端点），盲 `.get()` 会炸。

## ③ 外部连接

- **helpers.py**：`_send` 用 `connect+request` 发 CDP 命令（helpers.py:52-69），默认截图落 `ipc._TMP`（helpers.py:180, 334）。
- **daemon.py**：`serve()` 调 `ipc.serve(NAME, handler)` 起监听（daemon.py:829）；`handle()` 用 `expected_token()` 做请求级鉴权（daemon.py:669-671）；退出时 `cleanup_endpoint` 清残留端点（daemon.py:863）。
- **admin.py**：孵化器用 `pid_path`/`log_path`/`spawn_kwargs` 三件套（admin.py:579-588），守护进程判活 `daemon_alive` 底层是 `ipc.ping`（daemon.py:872-875）；`restart_daemon` 杀进程前用 `ipc.identify` 拿端到端验证过的 PID（identify docstring，_ipc.py:131-135）。
- **paths.py**：`tmp_dir()`/`runtime_dir()`/`ensure_private_dir` 是目录语义与 0700 权限的最终出处。

## ④ 数据流

**客户端一次调用**：`connect(name)` →（POSIX 直连 `.sock`；Windows 先 `_read_port_file` 拿 {port, token} 再 `create_connection` 到 127.0.0.1，_ipc.py:83-93）→ `request` 把 JSON+`\n` 发出去，循环 `recv(1<<16)` 直到读到换行，`json.loads` 返回（_ipc.py:96-106）。协议是**单行 JSON、一连接一请求**，daemon 侧 `readline()` 后即写回并关闭（daemon.py:812-818）。

**daemon 启动**（serve，_ipc.py:165-190）：POSIX 先 unlink 陈旧 socket，然后 `os.umask(0o077)` 包住 `start_unix_server`——bind 创建的 socket 文件直接就是 0600，**不存在先建后 chmod 的 TOCTOU 窗口**（_ipc.py:171-174）；Windows 绑 `127.0.0.1:0` 随机端口，生成 token，port 文件先写 `.tmp` 再 `os.replace` 原子落盘，防止并发读者看到半截文件（_ipc.py:178-185）；finally 里尽力删除 port 文件。

**判活链**：`ping` 只认 `{"pong": true}` 字典——防的是"daemon 崩溃后无关进程复用端口，裸 TCP connect 居然成功"的假活（_ipc.py:110-112）。

## ⑤ 设计决策与取舍

- **换行分帧而非长度前缀**：`recv` 拼到 `\n` 为止实现 8 行搞定，代价是无法传输内嵌裸换行的 payload——JSON 序列化天然满足，协议自洽。
- **每请求新建连接**：没有连接池与多路复用，但客户端永不泄漏、daemon 无连接状态机；对"每次 CLI 调用都是新进程"的使用模式这是最简正确解。
- **identify 的 bool-PID 防御**（_ipc.py:148-157）：`type(pid) is int` 刻意不用 `isinstance`——Python 里 `isinstance(True, int)` 为真，恶意/有 bug 的 daemon 回 `{"pid": True}` 会被当成 PID 1（init）去 `os.kill`。同时拒绝 0/负数（`os.kill(0,...)` 会信号整个进程组）与超过 2^31 的值（超出 pid_t 会让 `os.kill` 抛 OverflowError 逃出 restart_daemon 的清理逻辑）。这是全仓最细的一处防御性类型检查。
- **ping/identify 吸收全部 OSError**：判活函数的契约是"绝不抛"，调用方拿布尔值即可分支，网络异常被就地翻译成 False/None。
- **Windows 无文件权限边界 → 应用层令牌**：不引入 ACL、不做握手协议，单 hex token 存同目录 port 文件里（0700 目录保护），够用且可审计。

## ⑥ 新人提示（坑/勘误）

- **import 即建目录**：哪怕只想用 `_ipc.sock_addr` 显示个路径，也会 mkdir 两个目录。CI 或只读环境里要意识到这点。
- macOS 上自定义 `BH_RUNTIME_DIR` 路径过长会直接撞 104 字节 `sun_path` 上限——注释把责任划给调用方（_ipc.py:9-11）。
- port 文件只在 Windows 存在；POSIX 上找 `.port` 文件排查问题是缘木求鱼，应看 `.sock`。
- `_runtime_stem`/`_tmp_stem` 的共享语义：默认调用方给的目录被视为"每实例私有"所以用裸 `bu`；多 BU_NAME 共用一个目录时必须设 `*_SHARED=1`，否则实例间互相覆盖 socket 文件。
- `sock_addr` 仅用于日志展示（Windows 显示 `127.0.0.1:<port>`），别拿它当连接端点重复实现 connect。
- 改协议（比如想加压缩或多请求复用）要同时动 `request`、daemon 的 `handler`（daemon.py:812-827）、以及 admin 的 `daemon_alive` 探测——三处都默认"一行 JSON"契约。
