# browser_use/cli.py — CLI 3.0

## ① 角色定位

cli.py 是 `browser-use` 命令的入口，465 行的"薄壳路由器"。它自报家门为"Browser Use CLI backed by Browser Harness"（cli.py:1）——CLI 3.0 的核心架构变化就藏在这句：命令的**执行引擎整体外包给独立包 browser-harness**（pyproject.toml:50 钉死 `browser-harness==0.1.13`，源码在另一仓 browser-harness/），cli.py 只做四件事：本地处理少数专用命令（--mcp/--cli-mcp/install/init/skill）、把其余 argv 原样委托给 harness 的 run.main()、拦截 2.x 时代的旧子命令给出 3.0 迁移提示、全程打 CLI 遥测。CLI 3.0 的用户面革命（`_CLI3_GUIDE`，cli.py:241）：预设子命令全部废除，改成"把 Python 管道进 stdin，在常驻浏览器会话里执行"——`browser-use <<'PY'  new_tab("https://...")  print(page_info())  PY`，new_tab/goto_url/click_at_xy/js/cdp 等助手函数预注入（`_CLI3_GUIDE` 清单 241-244 与 `_QUICKSTART` 312 处两份），浏览器管理（daemon 启动、Chrome attach、等待）由 harness 后台代管。

## ② 内部结构

调度核心 `_dispatch`（357）按优先级短路：`--cli-mcp`→`_run_cli_mcp_server`（79）、`--mcp`→`_run_mcp_server`（75），两者共用 `_run_mcp_stdio_server`（60）——importlib 动态加载目标模块、压制日志后 asyncio.run(main)，这是 stdio 服务器必经的静音舱；`install`（83）subprocess 跑 `uvx playwright install chromium`（Linux 附 --with-deps）；`init`（111）转接 init_cmd.main（模板来自 GitHub template-library，init_cmd.py:28），`--template/-t` 也归入 init；`skill`（370）交给 skills/install.handle——把 browser-use SKILL.md 装进 8 个 AI 编码助手目录（agents/claude/codex/copilot/cursor/gemini/openclaw/opencode，install.py:26-34）。之后查 `_LEGACY_HINTS`（206-229，22 条旧子命令/旗标→新写法映射），命中则 stderr 打 `_legacy_migration_message`（254）并 exit 2。无参数时：tty 打 `_QUICKSTART`（303），管道有代码则把 stdin 换成 StringIO 喂给 harness（384-388）。兜底 `_run_browser_harness`（185）设 BH_CLIENT/BH_CLIENT_VERSION 环境变量、调 `_patch_browser_harness_cli_text`（159）后进 run.main()。main（423）本身是遥测编排：`_command_name`（338）先归一命令名，`_StderrTail`（403）包装 stderr 保留尾部 500 字符作错误上下文，`_capture_via_harness`（34）经 harness 的 capture_cli_event 上报 action=completed/error、时长、退出码；`_delegated_to_harness` 旗标（182）防止 harness 内部再报一次造成双计。

## ③ 外部连接

对 browser-harness 的依赖有三种姿态并列：**委托**（run.main，harness run.py:240）、**遥测**（telemetry.capture_cli_event，harness telemetry.py:247）、**白标化改写**——`_as_browser_use_cli_text`（130）把文本里的 "Browser Harness"/"browser-harness" 字符串替换成 "Browser Use"，再由 `_patch_browser_harness_cli_text` 用它改写 harness 的 run.HELP/run.USAGE 模块级常量（162-163），并对 auth/telemetry 子命令包一层 stdout/stderr 捕获重定向（`_normalize_captured_cli_output`，134）实现输出文案的品牌置换——用户看到的永远是 browser-use，尽管引擎是 harness。对主库内部：mcp 双服务器（browser_use.mcp.server/cli_mcp）、init_cmd 模板系统、skills/install 的技能分发。唯一显式特判的 harness 子命令是 doctor（193-199）：只接受 `--fix-snap` 一个参数，其余打印 usage 后 exit 2。

## ④ 数据流

一次 `browser-use` 调用的数据流：argv → main 记 monotonic 起点与命令名 → _dispatch 逐级短路判定 → 命中本地命令就地执行返回 (exit_code, command)；否则进入 harness 委托：设 BH_CLIENT env → patch 帮助文案 → run.main() 接管 stdin（此前可能已被换成装着管道代码的 StringIO）与 argv → harness 在常驻 daemon 里执行 Python 助手调用。异常路径有两条精心设计：SystemExit 且未委托 harness 时，取 `_StderrTail.tail`（尾部 500 字符）当 error_message 上报再 re-raise（434-443）；NameError 且确认源自管道代码（`_raised_from_piped_code` 检查最内层帧的 co_filename=='<string>'，294-300）时，`_unknown_exec_name` 从异常提取名字（284），打印 `_unknown_helper_message`（272）——把"助手函数名打错"转化成带 `_CLI3_GUIDE` 的教学时刻。旧命令流：`browser-use open https://x` → `_legacy_command` 认出 'open' → 迁移消息给出等价 Python（`new_tab("https://example.com")`）+ heredoc 示例 → exit 2 让脚本显式失败而非静默错行。

## ⑤ 设计决策与取舍

一是**引擎与壳分离**：CLI 语义（helper 函数集、daemon 管理）沉淀在 browser-harness 独立发版，browser-use 主包的 cli.py 保持在 500 行内只管路由与品牌——代价是版本强钉 `==0.1.13` 与跨仓的文本替换 hack。二是**文案 monkeypatch 而非 fork**：直接改 harness 模块的 HELP/USAGE 常量 + 捕获重定向，维护面最小但脆弱——harness 改个打印方式（绕过这两个常量或直接写 sys.stdout.buffer）白标就失效。三是**旧命令硬失败**：迁移提示 exit 2（377-378），宁可让 2.x 脚本断（信息给足）也不做隐式兼容——3.0 是语义不兼容重写（子命令→Python），兼容层只会更乱。四是**NameError 教学化**：管道代码里未定义名几乎必是助手名拼错，这是新手最高频错误，值得一条专用错误通道。五是**遥测防双计**：委托后 harness 自己会报，壳层用 `_delegated_to_harness` 闭嘴（436/445/451 三处判定）。六是**stdin 的 tty/管道双态**：无参数交互式给教程、管道给执行、空管道给专门的空 stdin 提示（332-335），三种形态都有出路。

## ⑥ 新人提示（坑/勘误）

- **文档版本代差是真实坑**：skills 目录下的 subagent.md 等文档描述的仍是 CLI 2.x 命令面（open/state/screenshot 等子命令），与 cli.py 3.0 的"Python 管道"模型存在整代差距；以 `_LEGACY_HINTS`（206）与 `https://github.com/browser-use/browser-use/blob/main/browser_use/skills/browser-use/SKILL.md`（250）为唯二权威。
- **`browser-use close`、`--session`、`--cdp-url` 全没了**：对应迁移是 `browser-use --reload`、`BU_NAME=<name>` 环境变量、`BU_CDP_URL=<url>` 环境变量（215-224），环境变量替代旗标是 3.0 的一贯风格。
- **真正干活的代码不在本仓**：`page_info()`/`click_at_xy()` 等助手函数的定义、daemon 生命周期全在 browser-harness 包（`==0.1.13` 钉版本）；在本仓 grep 这些名字一无所获是正常的。
- **`browser-use install` 装的是 Playwright Chromium**（96-99 `uvx playwright install chromium`）：项目运行时虽主打直连 CDP，安装器仍借 Playwright 的浏览器分发渠道拿 Chromium 二进制。
- **doctor 只认 --fix-snap**（197-199）：传别的参数 exit 2，别以为 doctor 坏了。
- **mcp 模式的一切输出都被 CRITICAL 压制**（67-69）：`--mcp` 下排障别指望日志，用 `--cli-mcp`（面向 CLI 生态的另一台服务器）或脱离 mcp 模式复现。
- 遥测在 main 的所有出口（SystemExit/Exception/正常返回）都会上报（437/446/452），关停走 harness 的 telemetry 子命令或环境变量，cli.py 自身无开关。
