# 06 · V0 沙箱巨石：`runtime/` 子系统全图

> 覆盖：`openhands/runtime/base.py`（1345 行）、`__init__.py`（工厂）、`impl/`（docker/remote/local/cli）、`utils/git_handler.py`+`git_changes.py`+`git_diff.py`、`utils/windows_bash.py`（1499 行）、`utils/runtime_build.py`+`runtime_templates/Dockerfile.j2`
> 选题甄别：任务书"1240 行"实为 **1345 行**（Legacy 收尾期仍在长）；54 方法 grep 实数。`local.py/docker.py/remote.py` 实际路径是 `impl/*/`。

## 1. 角色定位

`openhands/runtime/` 是 V0 的**执行子系统**：Agent 跑命令/读写文件/开浏览器都经 Runtime 落到真实环境（Docker 容器/远程主机/K8s/本机进程/CLI）。它是全仓**最大 Legacy-V0 撤离面**——`base.py:1-7` 头注、`__init__.py` 全文件、`impl/` 全目录都带 Tag，V1 用 02 篇 Sandbox 体系整体替换。但**GitHandler 脚本注入、warm server 预热池、Dockerfile 模板构建链**三个设计在 V1 侧都有回声；`CLIRuntime`（`impl/cli/cli_runtime.py:97`）是唯一不带 Legacy 头的幸存支线。

## 2. 内部结构

**Runtime 巨石**：`class Runtime(FileEditRuntimeMixin)`（`openhands/runtime/base.py:106`）54 方法五族：①装配族 `__init__`（`:144-223`）——GitHandler **双回调注入**构造（`:158-161`）；订阅 `EventStreamSubscriber.RUNTIME`（`:163-167`）；非 headless 自动补 VSCode 插件（`:172-174`）；`atexit.register(self.close)`（`:181`）；构造 ProviderHandler 同步拉平台 env vars（`:187-196`）；协作式初始化 FileEditRuntimeMixin（`:203-207`）；可选 SecurityAnalyzer（`:215-220`）。②事件族 `on_event`→`_handle_action`（`:390`、`:438`）派发到 `run_action`（`:1033`）——不可运行动作就地翻译，TaskTracking 竟把任务清单写进 FileStore 的 TASKS.md，emoji 状态图标硬编码（`:1043-1073`）。③动作族七执行器 run/run_ipython/read/write/edit/browse/browse_interactive/call_tool_mcp（`:1183-1217`）+文件传输三件（`:1219-1238`）+暴露信息 `vscode_url/web_hosts` 等（`:1240-1262`，01 篇弃用端点消费的正是后者）。④Git 族 `_execute_shell_fn_git_handler`（`:1263-1281`，`CmdRunAction(is_static=True, hidden=True)`）与 `get_git_changes/get_git_diff/get_workspace_branch`（`:1290-1318`）全委托 git_handler。⑤生命周期 connect/close/setup/teardown/上下文管理器（`:1133`、`:240`、`:1339-1345`、`:1126-1129`）。

**GitHandler：零 import 沙箱脚本+注入回退**：常量钉死沙箱内路径 `python3 /openhands/code/openhands/runtime/utils/git_changes.py` 与 `git_diff.py {file_path}`（`openhands/runtime/utils/git_handler.py:17-18`）。两脚本头注立铁律："**Since this is run as a script, there should be no imports from project files!**"（`openhands/runtime/utils/git_changes.py:9-10`）——只 import glob/json/os/subprocess/pathlib（`:13-16`），被原样拷进容器按脚本跑。容错在 `get_git_changes`（`git_handler.py:88-125`）：标准路径失败且未回退过（`:113-115`），则 `_create_python_script_file`（`:58-64`：mktemp→读本地脚本→`create_file_fn` 写进沙箱→chmod）**注入**老沙箱重试（`:121-125`）——"legacy runtimes may be missing the script"（`:117`）：老镜像兼容补丁。`get_git_diff` 同款双跳（`:147-157`），路径 `shlex.quote` 防注入（`:141`）。

**impl/ 四实现一底座**：`ActionExecutionClient(Runtime)`（`impl/action_execution/action_execution_client.py:68`）是 HTTP 底座（Semaphore(1) 串行单动作），三实现叠它：`DockerRuntime`（`impl/docker/docker_runtime.py:82`）、`RemoteRuntime`（`impl/remote/remote_runtime.py:46`，对接 V0 RemoteRuntime API——02 篇 RemoteSandboxService 适配的正是这侧遗产）、`LocalRuntime`（`impl/local/local_runtime.py:133`）。工厂 `get_runtime_cls`（`runtime/__init__.py:84-99`）：六键映射（`:22-29`，**`'eventstream'` 是 `'docker'` 历史别名**）→未命中走 `get_impl` 支持全限定类名（`:92`）；第三方 runtime 经 `pkgutil.iter_modules` 扫 `third_party.runtime.impl` 动态发现（`:47-53`），类名猜 `E2BRuntime/DaytonaRuntime` 两模式（`:59-66`），可选依赖 ImportError 静默（`:74-75`）。

**LocalRuntime 预热池**：模块级 `_WARM_SERVERS: list[ActionExecutionServerInfo] = []`（`local_runtime.py:76`）。`connect()`（`:227`）读 `DESIRED_NUM_WARM_SERVERS`（`:232`）：池非空且非 attach 则 `pop(0)` 摘现成 server 进程直接接管（`:298-310`）——**删旧临时工作区、mkdtemp 新区、复用进程与端口**（`:312-328`），注册 `_RUNNING_SERVERS`（`:331-340`）；摘取失败降级现起新 server（`:343-359`）；连接完池低于目标则循环补池（`:406-417`）；`setup` 类方法按 `INITIAL_NUM_WARM_SERVERS` 启动期预热（`:419-437`）。**本质：把"起 server 进程"的秒级成本从请求路径挪到空闲期**。

**构建链与 Windows 巨石**：`runtime_build.py` 的 `_generate_dockerfile`（`:38`）渲染 j2 模板——`Dockerfile.j2` 从 `FROM {{ base_image }}` 起步（`runtime_templates/Dockerfile.j2:1`）、强制 bash（`:3`）、预置 POETRY/MAMBA/EDITOR 块（`:6-13`）；`build_runtime_image`（`:119`）；镜像 tag 由 lock 文件哈希（`:331`）与源码哈希（`:355`）决定。`windows_bash.py`（1499 行）单类 `WindowsPowershellSession`（`:186`）：经 pythonnet 直接驱动 .NET PowerShell SDK（docstring `:9-12`），`RLock` 护并发（`:21`）。

## 3. 外部连接

- **上游**：04 篇 `create_runtime`（`core/setup.py:79-89`）经工厂选型并注入 event_stream/plugins/LLMRegistry/tokens；`clone_or_init_repo/maybe_run_setup_script/maybe_setup_git_hooks`（`base.py:478/568/600`）被 `initialize_repository_for_runtime`（`core/setup.py:150-185`）按序调用。
- **事件流**：构造即订阅 RUNTIME（`base.py:165-167`）；Observation 经 add_event 回流（04 篇）。
- **平台层**：ProviderHandler（`base.py:187`）来自 03 篇——runtime 是 Git 平台 env vars 的最终注入口。
- **V1 对位**：SandboxService 的 start/pause/delete ↔ Runtime 的 connect/close/teardown；`wait_for_sandbox_running` 的 `/alive` 探活 ↔ `_wait_until_alive`（`local_runtime.py:393`）。

## 4. 数据流

以"Agent 看工作区改了哪些文件"（git 面板触发）为例：`runtime.get_git_changes(cwd)`（`base.py:1290-1293`）→ `git_handler.set_cwd` 后执行 `GIT_CHANGES_CMD` → `GitHandler.execute` 实为 `_execute_shell_fn_git_handler`（`base.py:1263-1281`）组 `CmdRunAction(is_static=True, hidden=True)` 走 `self.run()`——**同一沙箱命令通道，static+hidden 标记使其不污染事件流** → 落到具体实现（容器/子进程里的 action_execution_server；CLIRuntime 直接执行）→ 新沙箱镜像内置脚本直接跑；**老沙箱**首败后注入脚本重试（`git_handler.py:121-125`，注入经 `Runtime.write` `base.py:1283-1288`）→ 脚本 JSON 返回变更清单（`git_handler.py:104`）。LocalRuntime 冷启动对比：无池时 `_create_server` 现_spawn 秒级阻塞（`:353-359`）；有池 `pop`（`:302`）毫秒级接管。

## 5. 设计决策（V0→V1 代际语境）

- **"巨石基类+瘦实现"是 V0 的选择也是病**：54 方法把 git/microagent/任务清单/安全分析全塞进 Runtime（连 TASKS.md 渲染都在 `base.py:1043-1073`），子类继承即背全包袱。V1 反向拆成 Sandbox/agent-server/webhook 三件套（02 篇）——正是对巨石的否定。
- **GitHandler 依赖倒置**：基类不直接跑 git 而注入双回调（`base.py:158-161`）——handler 可在无沙箱环境（测试/CLI）复用，脏活封在 handler 内。巨石里最干净的一块。
- **零 import 脚本约束**（`git_changes.py:9-10`）由部署形态决定：脚本按路径执行而非模块导入——写沙箱脚本时此铁律优先于代码洁癖。
- **warm server 池是 LocalRuntime 独有**：Docker/Remote 靠镜像缓存与 K8s 调度吸收启动成本，本机进程只能自池预热——同一"降首命令延迟"问题在不同后端不同答案。
- **构建链哈希化 tag**（`runtime_build.py:331/355`）配合 02 篇 `AGENT_SERVER_IMAGE` 钉版——两代都靠内容寻址防镜像漂移。
- **第三方 runtime 动态发现**（`runtime/__init__.py:38-79`）：E2B/Daytona 以 optional 依赖接入失败静默——生态扩展点先于 V1 Injector 存在，思路一脉。

## 6. 新人提示

- **坑：`'eventstream'`=`'docker'` 别名**（`runtime/__init__.py:23-24`）——排查"docker 配置为何生效"先查这个。
- **坑：`atexit.register(self.close)`**（`base.py:181`）每实例注册且不注销——长进程大量建删 runtime 时 atexit 列表只增不减，对象滞留源。
- **勘误：TASKS.md 写的是 FileStore 非沙箱**（`base.py:1048-1051`）——任务清单与会话存储耦合，删会话即丢。
- **坑：warm server 复用先 rmtree 旧临时目录**（`local_runtime.py:312-314`）——上次会话未保存状态直接蒸发；池化省时的代价是**沙箱内不能放跨会话要存活的东西**。
- **git 脚本注入只回退一次**（`git_handler.py:113-115`）——注入后仍失败安静返回 None（changes）或抛 ValueError（diff `:149`）。
- **windows_bash 1499 行是"Windows 支持税"**：仅 win32 平台被条件导入；Linux 部署不带它，跨平台调试别在本机找它的行为。
- **`get_runtime_cls` 错误消息列全部键**（`runtime/__init__.py:96-98`）含第三方——日志见 E2B 不代表本机装了，只是注册表合并结果（`:81`）。
- **安全注意：git 面板命令 `is_static=True` 绕过确认模式**（`base.py:1268`）——不经用户确认即在沙箱执行；`shlex.quote` 只护 file_path 一处（`git_handler.py:141`），新增命令拼接注意同标准。
