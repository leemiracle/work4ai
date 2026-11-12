# 08 函数运行时：camel/runtimes/

## 1. 角色定位

runtimes 与 interpreters 解决的是两个不同问题：interpreters 执行"LLM 生成的代码"，runtimes 把"宿主机的 Python 工具函数"搬进隔离环境再暴露成 HTTP 服务——典型场景是把 SearchToolkit/BrowserToolkit 等重依赖工具放进容器跑，宿主 agent 经 HTTP 调用。核心机制是一次"改写函数体"：`add()` 把 FunctionTool 的 `func` 替换成发 `requests.post` 的 wrapper（camel/runtimes/docker_runtime.py:281），工具在远端执行、本地只剩代理。五个实现按隔离强度排：LLMGuardRuntime（无隔离纯门控）→ RemoteHttpRuntime（本机子进程）→ DockerRuntime/UbuntuDockerRuntime（容器）→ DaytonaRuntime（外部云沙箱）。`__init__.py` barrel 导出 6 个 Runtime 类 + TaskConfig，消费方在 examples/runtimes/ 与 test/runtimes/，主包内部无调用——这是一条相对独立的"工具部署线"。

## 2. 内部结构

**BaseRuntime**（camel/runtimes/base.py:20）契约极薄：`add`/`reset`/`cleanup` 三个抽象方法 + tools_map 字典（:26）。cleanup 是生命周期公共 API：`stop()`（:54）与上下文管理器 `__exit__`（:67-74）都只是委托 cleanup——子类必须实现资源回收。

**DockerRuntime**（docker_runtime.py）三阶段流水线：构造期连 Docker daemon、镜像不存在则 pull（:78）；`build()`（:168）创建容器（command="sleep infinity" 保活，:197）、bind mount、put_archive 拷文件、跑 tasks、最后 `exec = ["python3", "api.py", *list(self.entrypoint.values())]`（:241）在容器内拉起 API server；`add()`（:248）注册工具并改写 func 为 HTTP 代理。**UbuntuDockerRuntime**（camel/runtimes/ubuntu_docker_runtime.py:27）是子类：build 时容器内 apt-get 装 curl（:165-176）、以 `python_path` 显式解释器再启一次 api.py（:189-199）并用 curl 探活（:206-209）。

**api.py 是全线的枢纽**（容器内运行，非被 import 的库）：`sys.argv[1:]` 收模块.函数清单，`importlib.import_module`（api.py:90）动态导入——若目标是 BaseToolkit 子类则实例化并取 get_tools（:92-96，实例缓存在 `_toolkit_instances` 跨请求保状态）；每个工具注册成 `app.post("/{endpoint_name}")` 路由（:145），同步工具丢进 4 线程池执行（:32、:140，避免 Playwright 同步 API 卡死事件循环）；redirect_stdout 用 StringIO 劫持 sys.stdout 回传（:110-115）。启动即设 `os.environ["CAMEL_RUNTIME"] = "true"`（:37）——TerminalToolkit 靠此标志自动禁用 Docker 后端（嵌套容器无意义）。**RemoteHttpRuntime** 用 Popen 在本机起同一份 api.py（camel/runtimes/remote_http_runtime.py:61），atexit+`__del__`（:68、:175）双保险回收进程。**LLMGuardRuntime**（llm_guard_runtime.py:63）不隔离进程，add 时把函数包成"先 LLM 打风险分再放行"的 wrapper（GUARDPROMPT 三档评分标准，:28；`threshold < score` 拦截，:163），cleanup 是显式 no-op（:193）。

## 3. 外部连接

- **FunctionTool/BaseToolkit**（camel.toolkits）：add 的入参契约；api.py 端的动态导入约定 entrypoint 字符串必须是 `module.ToolkitClass` 可导入路径。
- **Dockerfile.multi-toolkit**：预装 BrowserToolkit/TerminalToolkit/CodeExecutionToolkit 系统依赖的镜像定义（FROM python:3.10-slim），文件头注释自带完整用法示例（`DockerRuntime("camel-multi-toolkit:latest").add(...)` 链）。
- **utils/ 子包**：FunctionRiskToolkit/IgnoreRiskToolkit 供 LLMGuardRuntime 的评分 agent 当外部工具（IgnoreRiskToolkit 支持按函数名忽略风险白名单，llm_guard_runtime.py:138-143 的 pop 语义=一次性豁免）。注意 `camel/runtimes/utils` 是包目录不是单文件。
- **interpreters 分层**：DockerRuntime 起的容器里若再跑 CodeExecutionToolkit，工具内解释器仍在容器内——与 api.py 的 CAMEL_RUNTIME 标志配合形成双层隔离。

## 4. 数据流

注册期：宿主 `runtime.add(tools, entrypoint_str)` → wrapper 改写 func（此时 tools_map 里的 FunctionTool 已是代理）→ `build()` 把 entrypoint 清单作为 argv 传给容器内 `python3 api.py` → api.py 动态导入真实实现并注册路由。调用期：agent step 触发 FunctionTool → wrapper 发 `http://localhost:{port}/{func_name}`（Pydantic 参数先 model_dump）→ 容器内 api.py 线程池执行真实现 → json 回传（redirect_stdout 时附 stdout）。get_tools()（camel/runtimes/base.py:76）把代理工具交回 agent——agent 全程无感知工具已被搬到远端。

## 5. 设计决策

1. **"函数体改写"而非"工具协议转发"**：不改 FunctionTool schema，只换 func 指针——agent 侧零改动，但代价是 wrapper 里 `func=func` 默认参数绑定后，**循环外的 `self.entrypoint[func.get_function_name()] = entrypoint`（camel/runtimes/docker_runtime.py:315 / camel/runtimes/remote_http_runtime.py:143）引用的是最后一个循环变量**：一次 add 传多个函数时只有最后一个函数名进 entrypoint，前面的函数在 api.py 侧静默少注册（图谱钉版高置信 bug）。
2. **同一份 api.py 双形态复用**：容器内与本地子进程共用，差异只在谁拉起——这是"本地开发→容器部署"无缝迁移的设计。但父子类各自再启一次 API server（DockerRuntime.build 尾 :241 已 exec_run 过，UbuntuDockerRuntime.build :189-199 又启动一次），第二次依赖第一次端口未释放成功与否，仅 curl 探活兜底；且父类用命令名 python3、子类用 python_path，解释器选择不一致。
3. **UbuntuDockerRuntime 的脆弱假设**：PYTHONPATH 由 `python_path` 拼出 `lib/python3.10/site-packages`（:193-195）——与 Debian/Ubuntu 实际 dist-packages 布局常不匹配；exec_python_file 中 :279 先写死 `/usr/local/lib/python3.10/site-packages` 又在 :282-284 立即被派生值覆盖，第一处是死代码。换 3.11/3.12 镜像需手改三处硬编码。
4. **复制漂移的双胞胎 typo**：camel/runtimes/docker_runtime.py:298 与 camel/runtimes/remote_http_runtime.py:126 的 logger.error 都以 `"ailed to execute function"` 开头（Failed 丢 F），而两文件返回值 error dict 里同一文案拼写又是对的——两处 if/else 分支同源复制的实证。
5. **LLM 门控选"每次调用评分"而非静态白名单**：分数看描述+实参（危险函数+无害参数可降档），IgnoreRiskToolkit 提供运行时豁免通道；代价是每个工具调用多一次 LLM 往返，且评分 agent 无 tool_call 时直接禁用函数（llm_guard_runtime.py:157-160），保守失败方向。

## 6. 新人提示

- **port=0 是随机端口**（camel/runtimes/docker_runtime.py:71 的 randint(10000,20000)），多 runtime 并存时端口冲突少见但日志要抓准；RemoteHttpRuntime 的 api.py 监听 8000 是容器内端口，宿主映射才是 self.port。
- **entrypoint 字符串必须在容器内可 import**：写 `camel.toolkits.SearchToolkit` 这类全路径；自定义函数要先 copy/mount 进容器并在 sys.path——api.py 只做了 `sys.path.append(os.getcwd())`（:39，即 /home）。
- **debug 三入口**：`GET /health`（api.py:54）回报已加载 toolkit 与已注册端点；容器内 curl /docs 探活（:207）；宿主测 `runtime.exec_run(TaskConfig(...))` 走 build 期 tasks 通道。
- **reset() 会循环 stop+build**（camel/runtimes/docker_runtime.py:319）——容器重建后 tools_map 里的 wrapper 仍指向旧端口？不会，port 不变；但容器内 `_toolkit_instances` 缓存的状态会丢，有状态 toolkit（如登录态）reset 后需重建。
- **LLMGuardRuntime 无隔离**：风险分只是软门控，真要防 shell 注入仍需容器档；其 threshold 参数在 add 时逐函数可调（默认 2），别与 GUARDPROMPT 的 1-3 分制搞混量纲。
