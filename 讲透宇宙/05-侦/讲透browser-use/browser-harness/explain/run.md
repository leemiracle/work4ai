# run.py 精讲 — CLI 入口：子命令路由、exec 沙箱与全路径遥测

> 源码：`src/browser_harness/run.py`（413 行）｜图谱层 L06「CLI 入口与编排」

## ① 角色定位

run.py 是 `browser-harness` 命令的落点（pyproject 的 console_script 指向 `main()`），一个文件干三件事：**子命令路由**（doctor/auth/skill/recordings/video/telemetry/update/reload）、**agent 脚本执行器**（无参数+stdin 非 tty 时读入 Python 代码 `exec(code, globals())`，run.py:377-409）、以及**遥测采集包装器**——无论脚本成败，退出前都发一条结构化 cli_event（run.py:240-301）。

它对 agent 的核心承诺写在 HELP 里："Helpers are pre-imported. The daemon auto-starts."（run.py:45）——`from .helpers import *`（run.py:33）加上预启动守护进程，让 heredoc 里三行代码就能干活。

## ② 内部结构

- **编码急救**（run.py:4-11）：import 任何东西**之前**先把 stdout/stderr reconfigure 成 UTF-8。Windows 默认 cp1252 编不了马标记 emoji 和页面标题，traceback 会 UnicodeEncodeError（注释引用 issue #124(4)）。
- **HELP/USAGE 文本**（run.py:35-76）：全部子命令的唯一权威清单，`skill` 子命令直接打印包内 SKILL.md（UTF-8 读，_print_skill，run.py:111-114）。
- **云端自举护栏**（run.py:79-108）：`_local_chrome_listening` 探测 9222/9223 的 `/json/version`——刻意不做裸 TCP connect，非 Chrome 进程占了端口也不该伪装成本地 Chrome 触发跳过云端引导（run.py:79-91）；`_explicit_cdp_configured` 检查 `BU_CDP_URL/BU_CDP_WS`，注释讲透动机：没有这个护栏，admin 的 start_remote_daemon 会**覆盖用户显式指定的端点，还为其计费一个从没要过的云浏览器**（run.py:94-100）。
- **trace 设施**（run.py:145-190）：`_traced` 包装器给每个公开 helper 记 `{helper, args, duration, error}`，上限 500 步、参数截 300 字符（run.py:145-148）；成功路径调 `recorder.observe`（run.py:174）——录制与遥测共用这一插点。`_install_helper_trace` 只包装 run.py globals 里可调用且未带 `__bh_traced__` 标记者，防重复包（run.py:181-190）。
- **`_StreamTail`**（run.py:196-212）：透传流包装器，边写边留 500 字符尾部与总长——遥测要输出摘要又不肯无限截留内容。
- **main 的三段式**（run.py:240-301）：记录起点 → `_run(args)` → SystemExit/Exception/成功三条出口都组装同构 cli_event，finally 恢复真实流。错误消息优先取 `str(exc.code)`（字符串退出码），否则取 stderr 尾部（run.py:269）。

## ③ 外部连接

- **admin.py**：14 个符号的大宗进口（run.py:13-31），doctor/update/reload/云端启停全部委托；`ensure_daemon` 的自愈语义（清僵尸、拉起关闭的 Chrome、引导 chrome://inspect 授权）都在那边实现。
- **helpers/recorder/telemetry/auth/macos/video**：`from .helpers import *` 提供脚本内置名；recordings 子命令直连 recorder 的偏好读写（run.py:336-359）；video 子命令延迟导入并交给 `video.run_cli`（run.py:360-363）。
- **遥测数据流**：`_telemetry_command` 把 argv 归一成 command 字符串（run.py:117-135）；`_telemetry_browser` 询问 daemon 的 browser_kind（cloud/cdp/local），遥测关闭时直接 None（run.py:229-237）。telemetry.py 侧有 18 词 FORBIDDEN_KEYS 键名黑名单（api_key/cookie/password/url/title/text…，telemetry.py:30-49）+ 值里的 `://` 一律 `[redacted]`（telemetry.py:141-143），发送走 detached 子进程绝不阻塞 CLI（telemetry.py:189-206）。

## ④ 数据流

一次典型 agent 调用 `browser-harness <<'PY' ... PY`：

1. run.py:8-11 流编码修正 → import admin/auth/helpers（后者连带 _ipc 建目录、读 .env、加载 agent_helpers）；
2. `main()` 清空 trace、起 `_StreamTail`；
3. `_run`：无 `-h/--version/子命令` 且 stdin 非 tty → 读入代码，空脚本打 USAGE 退出（run.py:377-382）；
4. `print_update_banner()` 提示更新；
5. **云端自举判定**（run.py:384-403）：脚本以 `start_remote_daemon(`/`stop_remote_daemon(` 开头视为 cloud 管理脚本跳过引导；否则五条件与门——daemon 不活 && 本地 9222/9223 无 Chrome && 未显式配 CDP && 云凭证在 && `BU_AUTOSPAWN` 已设——才拉云浏览器；`BROWSER_USE_API_KEY` 单独存在**不**触发（注释：该 key 常因无关原因存在，run.py:384-387）。然后 `ensure_daemon()` 兜底；
6. `_install_helper_trace()`（run.py:408）→ `exec(code, globals())`（run.py:409）——脚本与 CLI 同一 globals，helper 调用被逐个记账并流向 recorder/telemetry；
7. 退出路径组装 cli_event：command/task/browser/输出尾部/步骤清单/时长/退出码，detached 发往 PostHog EU。

## ⑤ 设计决策与取舍

- **exec 而非子进程**：脚本与 CLI 同进程同 globals，trace 包装器才能拦到每次 helper 调用；代价是脚本可以覆盖 CLI 状态——对"agent 是可信调用方"的威胁模型这是正确取舍。
- **trace 记参数 repr 而非截断值**：300 字符上限防泄漏面失控，遥测层再过一遍黑名单+脱敏，双层防线。
- **`--debug-clicks` 用环境变量传递**（run.py:374-376 设 `BH_DEBUG_CLICKS=1`）：flag 只属于 CLI，而消费方在 helpers 的 click_at_xy（helpers.py:175-192）——环境变量是跨 exec 边界最朴素的通道。
- **USAGE 与 HELP 分离**：无 stdin 脚本时打两行短用法而非 35 行全文，尊重终端信噪比。
- **守护进程自举放在脚本执行前**：脚本第一行就能用浏览器；但 cloud 自举收紧为五条件与门，宁可让 agent 显式调用 start_remote_daemon，也不冒误计费风险。

## ⑥ 新人提示（坑/勘误）

- **`_read_task` 只在 stdin 非 tty 时读代码**（run.py:215-222）；`--debug-clicks` 会被剥掉再判断有无剩余参数——这是唯一允许与脚本并存的 flag。
- 遥测事件里的 `task`/`output`/`steps` 已过黑名单与截断，但**键名**命中 FORBIDDEN_KEYS 的属性整个丢弃而非置空（telemetry.py:137-139）——排查"为什么少字段"先查名字是否含 url/token 等词。
- `_exit_code`：`sys.exit(None)`=0，`sys.exit(int)`=原值，其他对象=1（run.py:138-143）。
- 云端自举注释里的 precedence 承诺（install.md）：显式 `BU_CDP_URL/BU_CDP_WS` 永远赢——改自举逻辑前先读 run.py:94-100 注释，那里有完整的误计费事故模型。
- exit 前的 finally 恢复 stdout/stderr（run.py:287-289）是必须的：`_StreamTail.__getattr__` 透传一切属性，若留在原地，后续库对 `sys.stdout.fileno()` 之类调用会隐性异常。
- scripts 的异常不会中断遥测：三条出口路径都 `raise` 原异常，调用方看到的退出码与 traceback 保持原样。
