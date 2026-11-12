# 03 · sandbox 子系统：虚拟路径、白名单与三种执行后端

## 角色定位

`deerflow/sandbox/` 定义 agent 的一切代码执行与文件操作边界。核心思想是**虚拟路径系统**：模型永远只看到 `/mnt/user-data/{workspace,uploads,outputs}` 与 `/mnt/skills`，物理路径（`backend/.deer-flow/threads/{thread_id}/user-data/...`）对 LLM 不可见——无论背后是本机进程、Docker 容器还是 K8s Pod，提示词与工具契约保持同一套。这层抽象让"local 单机模式"与"aio/provisioner 容器模式"可以纯配置切换（config.yaml 的 `sandbox.use` 类路径）。

## 内部结构

**双 ABC 契约**。`sandbox.py:4` 的 `Sandbox` 定义五个抽象方法：`execute_command`（:16）、`read_file`（:28）、`list_dir`（:40，默认 max_depth=2）、`write_file`（:53，支持 append）、`update_file`（:64，二进制写）。`sandbox_provider.py:8` 的 `SandboxProvider` 管生命周期三方法 `acquire/get/release`（:12/:21/:30）。工厂 `get_sandbox_provider`（:42）是单例，经 `resolve_class(config.sandbox.use, SandboxProvider)` 反射装载并强制继承校验（:54）——工厂即插件点，`set_sandbox_provider`（:87）留给测试注入 mock。

**LocalSandbox 双向映射**（local/local_sandbox.py:10）：`_resolve_path` 容器路径→物理路径（local_sandbox.py:23），`_resolve_paths_in_command` 命令串批量替换（local_sandbox.py:106），`_reverse_resolve_path` 反向（local_sandbox.py:46）、`_reverse_resolve_paths_in_output` 把输出里的物理路径改回容器路径（local_sandbox.py:70）——四个方向全部按映射键长度降序做最长前缀匹配（:36、:59、:83、:119），保证 `/mnt/skills/sub` 优先于 `/mnt/skills` 命中。`execute_command` 用 `subprocess.run(shell=True)` 走探测到的 shell（`_get_shell` 依次试 /bin/zsh→bash→sh→PATH，:136-150），timeout=600 秒（:162），returncode 非 0 时把退出码拼进输出（:167-168）；文件读写的 OSError 一律改写回**原始容器路径**再抛，隐藏内部物理路径（:186-187）。`LocalSandboxProvider` 是极致单例（local_sandbox_provider.py:5）：acquire 永远返回同一个 "local" id（:41-45），映射表只装 skills 目录（:13-39，函数体内延迟 import get_app_config 规避循环，:26）。

**工具层三防**（sandbox/tools.py）：`resolve_local_tool_path`（sandbox/tools.py:120）是本地模式白名单校验——路径必须以 `/mnt/user-data/` 开头（:128-129），经 `replace_virtual_path`（:28）翻译后 `Path.resolve()` 再对三个 allowed_roots 逐一 `relative_to`（:147-153），全部失配抛 "path traversal detected"（:154）。bash 走 `validate_local_bash_command_paths`（:157）：正则抓命令里全部绝对路径（:17 的模式），虚拟前缀与 /bin、/usr/bin、/dev 等系统白名单放行（:18-25），其余拒绝并提示改用 /mnt 路径（:181-183）。输出侧 `mask_local_paths_in_output`（:91）把物理路径掩码回虚拟路径。`replace_virtual_path` 自己还带"共同父目录"优化：三目录同父时把虚拟根 `/mnt/user-data` 整体映射过去（:76-81）。

**惰性获取枢纽** `ensure_sandbox_initialized`（sandbox/tools.py:265）：state 里已有 sandbox_id 就复用（:289-298）；缺失则从 runtime.context 取 thread_id 调 `provider.acquire` 并写回 state（:300-309）——与 SandboxMiddleware 的 lazy_init=True 配对，纯聊天轮零沙箱开销。`sandbox_from_runtime`（:237）已标 DEPRECATED。`ensure_thread_directories_exist`（sandbox/tools.py:320）在首次工具调用时才真正建目录，`thread_directories_created` 标记防重（:342-354）。五个 @tool 包装（bash:357 / ls:388 / read_file:417 支持 start_line/end_line 切片:443-444 / write_file:458 / str_replace:494 支持 replace_all:525-528）统一模式：ensure 沙箱 → ensure 目录 → local 模式走三步（校验:375 → 翻译:376 → 掩码输出:378）→ 异常转 "Error: ..." 字符串。`is_local_sandbox` 以 `sandbox_id == "local"` 判别（tools.py:234）。

## 外部连接

三条执行后端链：(1) local 即上述；(2) **Docker DooD 链** `community/aio_sandbox/`——backend 容器内装 docker CLI（backend/Dockerfile COPY --from=docker:cli），容器里再起沙箱容器；thread 三目录以虚拟前缀挂载进容器，DooD 场景换 `DEER_FLOW_HOST_BASE_DIR` 宿主侧路径（config/paths.py 语境）。`AioSandboxProvider.release`（aio_sandbox_provider.py:525）不是销毁而是**停入温池**（:545-547 注释钉版：容器保持运行，同 thread 下轮免冷启动复用，仅 replicas 驱逐/shutdown/idle 超时才真停）——与 local 的空操作 release 形成语义光谱：销毁↔温池↔空操作，上层中间件统一调同一个 release。(3) **provisioner K8s 链** `docker/provisioner/app.py`——独立 FastAPI（:181），每个 sandbox_id 一个 Pod+NodePort Service（`_build_pod`（app.py:214），挂载点 `/mnt/skills`（app.py:275）与 `/mnt/user-data`（app.py:280） 与虚拟路径系统同名对齐），create_sandbox 两处 409 容忍保证幂等、Service 失败回滚 Pod。上层消费：SandboxMiddleware（middleware.py:21）管轮次级 acquire/release；gateway 的 uploads 路由对非本地沙箱经 `sandbox.update_file` 同步文件；skills 的 `get_container_path` 生成 /mnt/skills 虚拟路径与本法对齐。

## 数据流

一次 bash 工具调用的路径流转：模型输出 `/mnt/user-data/workspace/.venv/bin/python main.py` → ensure 沙箱（首调用触发 acquire）→ ensure 目录 → is_local_sandbox 判真 → 校验命令内全部绝对路径（系统前缀+虚拟前缀放行）→ 虚拟→物理翻译 → subprocess 在 zsh/bash 执行 → stdout/stderr/退出码拼接 → 物理路径掩码回 /mnt 虚拟路径 → 返回模型。本地模式三步（校验/翻译/掩码）与 LocalSandbox 内部映射（skills）是**两层独立翻译**：工具层管 thread_data 三目录，sandbox 层管 skills 目录，互不越界。

## 设计决策

1. **虚拟路径优先于容器化**：local 模式根本没有容器，"沙箱"退化为路径白名单+进程隔离缺失的坦诚取舍——安全性靠 resolve 白名单与 bash 命令校验兜底，而 aio/provisioner 才是真隔离。同一工具契约三种强度，用户按部署环境选。
2. **release 的语义落差（甄别）**：local_sandbox_provider.py:56-57 注释称"本方法刻意不被 SandboxMiddleware 调用以复用沙箱"，但 sandbox/middleware.py:66-78 的 after_agent **每轮都调 release**——注释是旧行为残留，现状靠 release 空操作兜底才没破坏复用语义。读此文件勿信注释信调用点。
3. **两级映射刻意分离**：thread_data 映射按请求动态构建（tools.py:61-83），skills 映射按配置静态构建（provider 初始化一次），前者随线程生死、后者进程级常驻。
4. **错误即字符串**：所有工具把异常转 "Error: ..." 返回而非抛出，配合 ToolErrorHandlingMiddleware 的兜底形成双保险——工具层先转，漏网之鱼中间件再转。

## 新人提示

- 调路径问题先打印 `thread_data`（三物理路径）与 `sandbox_id`，90% 的 "file not found" 是虚拟/物理翻译层错位。
- `sandbox_from_runtime` 是弃用 API，新代码一律用 `ensure_sandbox_initialized`（tools.py:237 docstring 明示）。
- local 模式下模型想读 `/etc/passwd` 会被 tools.py:154 拒绝——这是特性不是 bug，测试别绕。
- aio 的 replicas 是软上限（全忙时继续创建只记 warning），容量规划别指望它硬限流。
