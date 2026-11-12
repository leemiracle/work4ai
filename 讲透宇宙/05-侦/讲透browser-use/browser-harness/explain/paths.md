# paths.py — 目录约定的单点真相与 0o700 私有目录基线

## 一、角色定位

`paths.py` 只有 49 行、6 个函数，却是全仓**文件系统布局的唯一立法者**：配置、IPC 端点、临时产物、录制工作区四类状态分别落在哪里、可以被哪些环境变量覆盖、权限位是多少，全部在这一个文件里定死。其余模块（_ipc、recorder、helpers、daemon、admin、auth、telemetry）一律 `paths.xxx()` 取路径，不许自己拼 `~/.config`。

它解决的三个现实问题：**可移植**（XDG 约定 + 显式环境变量逃生门）、**多实例隔离**（每个目录都有独立 env 覆盖，供测试与并行 agent 沙箱用）、**隐私**（浏览器录制与凭据天然敏感，目录一律 0o700 起步）。

## 二、内部结构

- **`home_dir()`（paths.py:9-16）**：基座解析，优先级链为 `BH_HOME` > `BROWSER_HARNESS_HOME`（:10，两个名字等价）> `XDG_CONFIG_HOME/browser-harness`（:13-15）> `~/.config/browser-harness`（:16）。取到后 `expanduser().resolve()` 规范化。
- **`ensure_private_dir(path)`（:19-24）**：唯一的写动作函数。`mkdir(parents=True, exist_ok=True)` 后，若目录是**本次新建**且非 Windows，`chmod 0o700`（:22-23）。注意 `existed` 标志的语义：已存在的目录**不**改权限——尊重用户对老目录的显式设定。
- **四个目录访问器**，全部同构——env 覆盖则用覆盖值，否则 `home_dir()` 下挂默认子目录，且都过 `ensure_private_dir`：
  - `config_dir()`（:27-29）：`BH_CONFIG_DIR`，默认 home 本身。存 auth.json、telemetry.json、version-cache.json、recording.json、inspect-opened 标记。
  - `runtime_dir()`（:37-39）：`BH_RUNTIME_DIR`，默认 `home/runtime`。存 IPC 的 sock/port/pid 端点。
  - `tmp_dir()`（:42-44）：`BH_TMP_DIR`，默认 `home/tmp`。存截图、debug overlay、daemon 日志。
  - `workspace_dir()`（:47-49）：`BH_AGENT_WORKSPACE`，默认 `home/agent-workspace`。录制目录与其下 recordings/、agent 的 .env。
- **`inspect_marker()`（:32-34）**：`config_dir()/inspect-opened`，docstring 写明语义："Marker recording that the harness opened a chrome://inspect tab"。

## 三、外部连接（消费方地图，逐一源码核实）

- **_ipc.py**：`_TMP = paths.tmp_dir()`（_ipc.py:22）与 `_RUNTIME`（:23，BH_RUNTIME_DIR 覆盖时绕过 paths 直取 env 值但仍过 `ensure_private_dir`）。其头部注释（_ipc.py:9-16）解释了为何 runtime 与 tmp 必须分设：macOS AF_UNIX `sun_path` 上限 104 字节，长用户名下共享深目录会爆，独立短路径兜底。
- **recorder.py**：`workspace_dir()/recordings`（recorder.py:71）与 `config_dir()/recording.json`（recorder.py:75，跨进程录制状态）。
- **helpers.py**：模块级 `AGENT_WORKSPACE = paths.workspace_dir()`（helpers.py:16），是文件上传等工具的工作根。
- **daemon.py**：`workspace = paths.workspace_dir()`（daemon.py:15，.env 注入子进程）；`inspect_marker().exists()`（daemon.py:398）与 `.unlink()`（daemon.py:537）管理 chrome://inspect 提示的节流状态。
- **admin.py**：`VERSION_CACHE = paths.config_dir() / "version-cache.json"`（admin.py:131）；`_load_env` 搜 `workspace/.env`（admin.py:110）；`_open_chrome_inspect_once` 用 `paths.inspect_marker()` 做 180 秒节流（admin.py:1389）。
- **auth.py**：`config_dir()/auth.json`（auth.py:130，可被 BH_AUTH_PATH 覆盖——那是 auth 自己的逃生门，不走 paths）。
- **telemetry.py**：`_config_dir()` 直接转发 `paths.config_dir()`（telemetry.py:45），telemetry.json 落同一配置区。

## 四、数据流

本文件无运行时数据流，只有**解析链**：环境变量（进程启动时读一次）→ Path 对象 → 调用方拼接具体文件名。每次调用 `paths.config_dir()` 都会重新读 env 并 `mkdir`——这不是缓存，意味着**进程内改 `BH_CONFIG_DIR` 立即生效**（测试里 monkeypatch env 后无需重载模块）。副作用是每次调用多一次 `mkdir(exist_ok=True)` 系统调用，换来"任何模块任何时刻拿到的目录必然存在"的保证。

权限数据流单向：目录首次创建时 0o700，之后永不触碰。文件级权限（0o600）由各属主模块自己负责——telemetry 的 `_save_config`（telemetry.py:66-68）、auth 的 `_write_private_json`（auth.py:468-480）都只管自己的文件。

## 五、设计决策与取舍

- **"每次调用都解析"而非模块级常量**：与 helpers.py 的 `AGENT_WORKSPACE` 常量（helpers.py:16）形成对照——后者冻结在导入时刻。paths 侧保持动态是有意的：测试沙箱切换 env 不需要重启解释器。
- **双名 `BH_HOME`/`BROWSER_HARNESS_HOME` 并存**（:10）：短名给日常用户，长名给不愿引入 BH_ 前缀生态的部署；`BH_*` 系列是这个 env 家族的一致命名（BH_CONFIG_DIR/BH_RUNTIME_DIR/BH_TMP_DIR/BH_AGENT_WORKSPACE/BH_AUTH_PATH…）。
- **尊重 XDG 但不依赖 xdg 库**：手写三行实现 XDG_CONFIG_HOME 语义，零第三方依赖——这个仓的整体风格（标准库优先）在最小文件里也贯彻。
- **`existed` 防御性 chmod**（:22-23）：只在新建时收紧权限。若改成每次 chmod，会覆盖掉用户在共享机器上特意放宽的目录权限，属于典型的"安全功能变成骚扰"。
- **runtime/tmp 分家的深层原因**在 _ipc.py:9-16：端点路径受 sun_path 长度硬约束，而 tmp 里放的是截图这类长名字文件，两者寿命与清理策略也完全不同（端点随 daemon 生死，tmp 可随时清）。
- **Windows 跳过 chmod**（:22 的 `sys.platform != "win32"`）：POSIX 权限位在 NTFS 上无意义，硬 chmod 反而抛错。

## 六、新人提示

- **加新状态文件时先问归哪类**：跨调用持久的配置 → config_dir；进程协作端点 → runtime_dir；可丢弃产物 → tmp_dir；面向 agent 的工作内容 → workspace_dir。放错类（比如把录制放进 tmp_dir）会直接被清理策略误伤。
- **多实例隔离的标准做法**：测试与并行 agent 各给一套 `BH_CONFIG_DIR`+`BH_RUNTIME_DIR`+`BH_TMP_DIR`+`BH_AGENT_WORKSPACE`。只设一个不够——_ipc 的端点发现（admin.py:392-408）是按 runtime 目录 glob 的，config 不隔离会出现两个实例读同一 auth.json。
- **`BH_HOME` 与四个子目录 env 可以混用**，但子目录 env 优先：设了 `BH_CONFIG_DIR` 后再改 `BH_HOME` 不会影响 config 落点（:27-29 先查覆盖）。
- **`ensure_private_dir` 不修正已存在目录的松权限**（:22 的 existed 判断）：诊断"为什么我的 0o755 目录没被收紧"时先看这一行——这是特性不是 bug。
- **daemon 与 CLI 必须看到同一套 env**：admin 拉起 daemon 时透传 `os.environ`（admin.py:562），如果只在一侧 shell 里 export 了 `BH_RUNTIME_DIR`，两侧端点会各说各话，ping 永远不通——这类"daemon 起了但找不到"的排障第一步是比对两边进程的 env。
- **本文件故意不提供"列出所有路径"的 API**：布局知识分散在各消费方，paths 只立法不巡检；想要全景就得看本篇第三节那张消费地图。
