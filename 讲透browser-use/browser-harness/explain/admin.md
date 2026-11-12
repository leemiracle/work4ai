# admin.py — 守护进程生命周期状态机与运维总控

## 一、角色定位

`admin.py`（1588 行，全仓最大模块）是 browser-harness 的**运维大脑**：守护进程的启动/停机/防孤儿、Chrome 权限弹窗的人机协议、云浏览器（Browser Use Cloud）的供给与回收、doctor 诊断、自更新，全集中在这一个文件。模块导入时就执行 `_load_env()`（admin.py:126）从仓库根与 agent 工作区加载 `.env`（:108-123，`setdefault` 不覆盖已有变量），随后钉下全局常量：`NAME`（BU_NAME，默认 "default"，:128）、云 API 基址（:129）、PyPI 版本端点（:130）。

它的核心难题只有一个：**守护进程是异步拉起的、Chrome 的授权是人手点击的，而调用方要一个幂等的 `ensure_daemon()`**。大半篇幅是在给"启动竞态、PID 复用、弹窗重试风暴、孤儿计费浏览器"这些分布式经典坑打补丁。

## 二、内部结构

按功能分六块：

**① 进程身份（:17-105）**。`_process_start_time(pid)` 返回进程启动时刻指纹：Linux 读 `/proc/<pid>/stat` 第 22 字段（comm 可含空格括号，从**最后一个** `)` 之后切分，:44-45）；macOS 用 `ps -o lstart=`；Windows 走 ctypes `GetProcessTimes`，FILETIME 高低 32 位拼 64 位（:102）。配套读侧 `_pending_pid_record`（:169-188，兼容旧版纯文本 pid 文件）、写侧 `_publish_pid`（:222-227，JSON 原子 `os.replace`）。

**② 端点与状态查询（:368-446）**。`daemon_alive()` 用 ping 握手而非裸连接——残留 `.port` 文件 + 端口复用会让裸连接误判（:369-371）。`daemon_browser_kind()` 从 ping 响应读 `browser_kind`（cloud/cdp/local，:374-389）；`_daemon_endpoint_names()` 处理两种拓扑：设 `BH_RUNTIME_DIR` 且非共享只看本名端点，否则 glob `bu-*.{sock,port}` 枚举（:392-408）。

**③ 弹窗与错误分诊（:319-365）**。三个字符串嗅探函数把日志尾映射成状态：`_needs_chrome_remote_debugging_prompt`（DevToolsActivePort 缺失等，:319-335）、`_needs_chrome_permission_popup`（:338-341）、`_chrome_not_running`（:344-346）。`_daemon_wait_windows`（:360-365）定等待策略：默认 60s，本地 Chrome 授权等待在调用方未显式给 wait 时为 **None（无限等）**。

**④ spawn 互斥（:256-316）**。`_spawn_lock` 跨平台文件锁（flock / msvcrt），拿不到锁时 `fd=None` 放行——取舍写在注释："failing to start is worse than an extra popup"（:262-263）。

**⑤ 主状态机 `ensure_daemon()`（:525-708）**：详见第四节。
**⑥ 云浏览器与运维（:886-1588）**：`_browser_use` HTTP 封装（X-Browser-Use-API-Key 头，:886-894）、`start_remote_daemon`/`stop_remote_daemon`、profile 同步（shell 出 `profile-use`，:1047-1091）、版本检查（24h 缓存，:1149-1161）、doctor（:1404-1485）、自更新（:1525-1588）、浏览器启动矩阵（:1219-1230，九种浏览器）。

## 三、外部连接

- **_ipc.py**：pid/port 路径、connect/ping/request/identify、`spawn_kwargs()`、`cleanup_endpoint`——admin 是 _ipc 最大的消费者。
- **daemon.py**：以 `python -m browser_harness.daemon` 子进程拉起（:580-581, :587-588）；反向延迟导入 `supported_browser_running`、`remote_debugging_toggle_profiles`、`PROFILES`、`_devtools_port_live`（:676, :683, :1283, :1347）。
- **auth.py**：`get_browser_use_api_key()`（:887）、`auth_status()`（doctor，:1414）。
- **paths.py**：config_dir（版本缓存 :131）、workspace_dir（.env :110）、inspect_marker（:1389）。
- **run.py / mcp_server.py**：`ensure_daemon` 是两者的入口前奏；CLI 的 `--reload`/`--doctor`/`--update` 直通本文件。
- **外部**：api.browser-use.com/api/v3、pypi.org、命令 `profile-use`/`uv`；`ps`/`tasklist`/`osascript` 等按平台调起。

## 四、数据流

**启动（ensure_daemon）**：alive 检查（:528）→ 假活鉴别：ping 通但 CDP 死的守护进程用 `Target.getTargets` 真探（:533-540）；stale 分诊——`browser_kind` 是 cloud **或 None** 一律 `stop_remote_daemon`（孤儿云浏览器在计费，未分类按最坏处理，:541-549），本地/cdp 才 restart。然后最多 3 轮（:561）：本地模式先取 spawn 锁，锁内 double-check alive、识别"停在看弹窗上的"（`_parked_daemon_pid`，日志尾 `handshake-wait` + pid 指纹，:230-243）与"刚起还没写日志的"（:246-253）两代在途者避免重复拉起；否则 Popen + `_publish_pid`。等待循环（:597-628）三个出口：alive 即返回（顺手清掉我们拉起但没用上的浏览器，:599）；子进程死（:601-606）；日志出现 `handshake-wait` 则 deadline 抬成无限（:608-610），2 秒后打印"点 Allow / 跑 mac-approve"提示（:611-627）。失败路径三条铁律：pending 死于权限→**绝不自动重拉**（重拉=新弹窗=重试风暴，:641-648）；pending 活着停在弹窗→**留着它撑弹窗**、抛 permission-blocked（:650-657，注释记录了杀掉导致弹窗重提的历史 bug）；chrome 没开→重启守护进程、`_launch_browser()` 开浏览器、等 15s 再循环（:667-680）。

**停机（restart_daemon，:747-883）**：名不副实——只停不启（docstring :749-752 自嘲）。先分辨 ready 守护进程（identify 给 pid）与 pending 代（指纹对上才允许动，:792-817 且全程持 spawn 锁、动手前再 ping 0.2s 防竞态）。ready 路径发 `meta:shutdown`（require_clean 时要 `{"ok": true}` 确认、超时 50s，:830-838），等 15s 退场；超时后**二次验明正身**（identify 同 pid，或启动时刻指纹未变）才补 SIGTERM（:868-877）——PID 可能已被系统复用。

**云启动（start_remote_daemon，:997-1036）**：POST /browsers 拿 cdpUrl → `/json/version` 换 webSocketDebuggerUrl（:914-915）→ ensure_daemon 注入 `BU_CDP_WS`/`BU_BROWSER_ID`；daemon 起不来则回滚停掉云浏览器，回滚也失败时用 `BaseExceptionGroup` 把两个错误一起抛（:1029-1032）。

## 五、设计决策与取舍

- **PID 复用零信任**：身份体系建立在"pid 文件不可信，pid+启动指纹才可信"上（:17-32 长注释）。指纹拿不到就只做 identify 校验，也不回到"信 pid 文件"的老洞。
- **升级兼容双轨**：`daemon_pid`（新版 ping 自报）与 `daemon_alive`（任何版本能答 pong）分开跟踪（:776-784），旧守护进程也能被干净停掉。
- **弹窗的一次性原则**：Allow 弹窗一次审批对应一条连接，"杀掉重试"只会再造弹窗，所以 permission 分支文案都强调 "did not retry or create another connection"（:646-647, :656, :692）。
- **失败关闭的 require_existing_daemon（:711-730）**：受信编排器专用——守护进程死了就报错，绝不自动发现别的本地 Chrome，防 agent 静默漂移。
- **未分类守护进程按云处理（:545-549）**：重启可能拥有计费云浏览器的进程代价高于多停一次，不确定性按最贵结局兜底。
- **_repo_dir 只认两级父目录（:1106-1120）**：防把 venv 外层用户仓库当"本仓"去 `git pull`。
- **doctor 与 doctor --json 分家**：人读版可联网查版本（:1404-1456），JSON 版非网络化且 strict 模式只看指定 daemon（:1459-1465），供编排器轮询。

## 六、新人提示

- **`restart_daemon` 不 restart**（:739-744 注释钉版）：只停。重启语义靠"下一次调用 ensure_daemon 自动拉起"，名字是历史遗留。
- **permission-blocked 类报错是设计出来的终止**，不是 bug：正确动作是引导用户点那个还开着的弹窗再重跑，不要在异常处理器里循环重试。
- **改日志文案前先 grep**：`_needs_chrome_*`（:319-346）和 `_parked_daemon_pid`（:238）都在做**字符串前缀匹配**，守护进程日志措辞一变状态机就瞎。
- **`.env` 是导入时副作用**（:126）：单测里 import admin 就可能吃进仓库根 `.env`，测试环境变量来源要心里有数。
- **勘误两则**：启动等待默认不是永远 60 秒——本地 Chrome 授权路径会转无限等（:608-610）；`_launch_browser` 只在"Chrome 完全没跑"分支才被调用，不是常规路径。
- **Windows 指纹依赖 ctypes 现场 argtypes 声明**（:73-87），别"简化"掉声明——指针类型错了不会立刻炸，而是在错误进程上做判断。
- **自更新在 git 模式拒绝脏工作区**（:1550-1552）：开发机上 `--update` 报 uncommitted changes 是保护，不是故障。
