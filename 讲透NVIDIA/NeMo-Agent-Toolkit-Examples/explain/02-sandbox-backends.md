# 02 沙箱抽象后端：BaseSandbox ABC 与 Docker/Daytona 双实现 + 工厂判别

## 角色定位

`src/nat_sandbox_agent/sandbox/` 四件套（base.py 163、docker_sandbox.py 325、daytona_sandbox.py 231、factory.py 215 行）是整个 agent 的**执行地基**：上层工具族（第 4 篇）只面向 `BaseSandbox` 抽象编程，完全不感知底层是本机 Docker 容器还是 Daytona 云沙箱。这一层解决"代码执行环境"的三个工程问题——隔离（容器级文件系统/网络/进程）、可移植（本地 Docker ↔ 云端 Daytona 切换）、统一语义（一套接口抹平两后端差异），是 **Strategy 模式 + discriminated-union 工厂**的落地。

## 内部结构

**base.py** 先立契约：模块级常量固化 /workspace 四目录布局（base.py:26-30：input/output/temp/downloads），`WORKSPACE_INIT_COMMAND` 一条 mkdir -p 全建（base.py:33），`DEFAULT_SCRIPT_PATH` 是 python 工具落盘位（base.py:36）。`CommandResult` dataclass（base.py:39-59）以 `exit_code/stdout/stderr` 三元组描述一次执行，`success` property 判 `exit_code==0`（base.py:47-50），`to_dict` 供序列化（base.py:52-59）。`BaseSandbox(ABC)`（base.py:62）声明六个抽象方法：生命周期 `start`/`cleanup`（base.py:74-82，docstring 强调 cleanup 是不可恢复销毁）、执行 `run_command`（base.py:86-105，签名统一 working_dir/timeout/env）、文件三读二写 `read_file`/`read_file_bytes`/`write_file`（base.py:109-147）。最后挂 async context manager 协议（base.py:151-163），enter 即 start、exit 即 cleanup。

**docker_sandbox.py** 是本地实现：构造器收 image/memory/cpu/network/volumes 等（docker_sandbox.py:48-81），容器名默认 `sandbox_{uuid4[:8]}`（docker_sandbox.py:78）。`start()`（docker_sandbox.py:86-138）流程完整：from_env 建 client → 本地无镜像则 pull（docker_sandbox.py:94-98）→ containers.create 配置字典，其中 `nano_cpus=int(cpu_limit*1e9)`（docker_sandbox.py:109）、`network_mode="bridge"/"none"`（docker_sandbox.py:110）、`tty+stdin_open` 保持长驻（docker_sandbox.py:105-106）→ start → 跑 WORKSPACE_INIT_COMMAND 建目录（docker_sandbox.py:128）。

**daytona_sandbox.py** 是云端实现：SDK 延迟导入（daytona_sandbox.py:74-86），`start()` 用 `CreateSandboxFromImageParams + Resources(cpu/memory/disk)` 声明资源（daytona_sandbox.py:99-107）。

**判别工厂**：`SandboxType` 枚举两值（sandbox/factory.py:30-34）；两个 pydantic 配置类用 `Literal["docker"]`/`Literal["daytona"]` 做 tagged union（sandbox/factory.py:40、82），`SandboxConfig = DockerSandboxConfig | DaytonaSandboxConfig`（sandbox/factory.py:118）；`create_sandbox` 按 type 分支并**延迟 import 实现类**（sandbox/factory.py:153、179——不装 docker SDK 也能用 Daytona）；`create_sandbox_from_dict` 是 YAML/字典入口，type 缺省即 docker（sandbox/factory.py:206）。

## 外部连接

- **上游消费者**：register.py:145 建实例；tools/sandbox 全族经 executor 持有 `BaseSandbox`；image_describe 跨层读文件（image_describe.py:99）。
- **第三方依赖**：docker SDK（docker_sandbox.py:24-27）、daytona-sdk（daytona_sandbox.py:78）、标准库 tarfile/shlex/asyncio。
- **环境变量通道**：`DEFAULT_PASS_ENV_VARS=["TAVILY_API_KEY"]`（sandbox/factory.py:27）+ `_build_environment`（sandbox/factory.py:121-137）把宿主 TAVILY_API_KEY 自动注入容器、显式 environment 优先（sandbox/factory.py:132）——沙箱内若也需搜网的密钥补充通道。
- **配置侧**：configs/config.yaml 的 `sandbox_config:` 块、config_daytona.yaml 切云后端，均落到 factory 的两个 Config 类。

## 数据流

以 `run_command("ls")` 为例：DockerSandbox 把命令包成 `timeout N /bin/bash -c {shlex.quote(command)}`（docker_sandbox.py:171-175）→ `exec_run(demux=True)` 分流 stdout/stderr（docker_sandbox.py:181-185）→ utf-8 errors="replace" 解码（docker_sandbox.py:193-194）→ exit_code==124（Linux timeout 的超时码）翻译成 -1 并在 stderr 标注（docker_sandbox.py:197-203）。Daytona 路径等价（`sandbox.process.exec`，daytona_sandbox.py:153-157），但 stdout 取 `result.result` 且 **stderr 恒空串**——daytona_sandbox.py:166 直言 "stderr not available in new API"，两后端语义不对等的诚实标注。文件读写：Docker 走 get_archive/put_archive tar 流（docker_sandbox.py:240-252、301-321），Daytona 直接 fs.download_file/upload_file（daytona_sandbox.py:192、228）。

## 设计决策

1. **双层超时防孤儿进程**。Docker 实现里 asyncio.wait_for 只能取消 Python 侧 await，容器内进程会变孤儿继续跑；所以先在命令外裹 Linux `timeout`（docker_sandbox.py:171-175），外层 wait_for 再加 5 秒余量"给容器侧超时先开火的机会"（docker_sandbox.py:187）。容器执行系统的常见坑，本仓给出教科书答案。
2. **全同步 SDK 用 run_in_executor 包异步**。docker/daytona SDK 都是同步的，所有阻塞调用一律 `run_in_executor`（docker_sandbox.py:98、122、125；daytona_sandbox.py:110、127），保证不卡事件循环。
3. **组件感知的路径白名单不在本层**而在工具层（file_ops.py:31，见第 4 篇）——沙箱层只管 IO，策略归上层，职责切分干净。
4. **写文件两实现都先 mkdir -p 父目录且 shlex.quote 防注入**（docker_sandbox.py:314-315、daytona_sandbox.py:220-223），注释明说 "shell-escape to prevent injection"。
5. **NotFound→FileNotFoundError 归一化**：Docker 把 SDK NotFound 翻译成 Python 惯用异常（docker_sandbox.py:259-260），Daytona 没有专用异常类型、只能字符串匹配 `"not found" in str(e).lower()`（daytona_sandbox.py:195）——能力差异在适配层抹平，但 Daytona 字符串判定脆弱。
6. **失败兜底**：start 失败主动 close client 防泄漏（docker_sandbox.py:134-137）；cleanup 容忍 NotFound（docker_sandbox.py:147-149）。

## 新人提示

- 加第三种后端（gVisor/k8s Pod 等）只需：继承 BaseSandbox 实现六方法 + 新 Config 类加进 union（sandbox/factory.py:118）+ create_sandbox 加分支——工具层零改动，这是 ABC 红利。
- Docker read_file 拉**整个 tar 归档**再解第一个成员（docker_sandbox.py:248-249），大文件是隐形性能税；Daytona 的 download_file 更直接。
- Daytona stderr 缺失意味着错误诊断在云后端天然残缺，排查问题优先本地 docker。
- auto_remove 默认 False（sandbox/factory.py:61-64）配合 cleanup 的 force remove（docker_sandbox.py:145）——销毁权收编在显式 cleanup，容器不会静默消失。
- 集成测试锚：test_docker_sandbox_integration.py 全部真容器（见第 6 篇），test_daytona_sandbox.py 纯 mock——Daytona 无集成测试，云端回归靠手工。
