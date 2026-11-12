# 第 9 篇：cosmos-cuda 哨兵包与 cosmos-gradio 服务框架

## 一、角色定位

`packages/cosmos-cuda` 是整个 uv workspace 里最小的包——README 只有 3 行："Sentinel package for determining if CUDA extra is installed"（`packages/cosmos-cuda/README.md:3`）。它零依赖（`packages/cosmos-cuda/pyproject.toml` 的 `dependencies = []`）、零逻辑（`cosmos_cuda/__init__.py` 只 re-export `__version__`），唯一职能是**证明用户装了哪个 CUDA extra 并与主包版本对齐**。`packages/cosmos-gradio` 则是另一极端：一个完整的"UI 进程 + GPU worker 进程"服务框架（依赖 gradio>=4/torch/loguru/pydantic-settings），原属 cosmos-predict2 上游的演示部署设施，随 workspace 一起进入本仓，是理解"Cosmos 模型如何变成可交互 Demo"的模板。

## 二、内部结构

**哨兵闭环**。校验逻辑双侧对称：`packages/cosmos-oss/cosmos_oss/__init__.py:19-32` 与 `cosmos_predict2/__init__.py:19-32` 都定义 `_check_cuda_extra()`——`import cosmos_cuda` 失败抛 `RuntimeError("CUDA extra not installed. Please run 'uv sync --extra=<cuda_name>'")`；版本不等抛 CUDA extra version mismatch（`__init__.py:26-29`）。包尾直接 `_check_cuda_extra()`，import 即校验，任何绕过 uv sync 的手工安装都会在首次 import 时被拦下。安装侧：cosmos-oss 的两组 extras（cu128_torch27/cu130_torch29）各含 `"cosmos-cuda"` 字符串（`packages/cosmos-oss/pyproject.toml:97`、`:127`），经 `cosmos-cuda = [{ workspace = true }]` 解析到本包；版本号静态写在 `cosmos_cuda/__about__.py:16`（1.4.1），`[tool.hatch.version] path` 消费同一文件。于是形成三文件对齐：oss/predict2/cuda 三个 `__about__.py` 必须 bump 到同一版本，否则 mismatch 报错。`just test-install` 配方是该机制的负向测试：先 `rm -f .cuda-name` 再 `uv sync -q`，import 应打印 "CUDA extra not installed..." 并以 `-` 前缀容忍预期失败；正常路径下 `just install cu128` 把 extra 名写进 `.cuda-name` 文件，`bin/entrypoint.sh:22` 在容器里按 `CUDA_NAME` 重新 `uv sync --locked --extra=${CUDA_NAME} || true`。

**cosmos-gradio 分层**。四层结构：① `deployment_env.py` 的 `DeploymentEnv(BaseSettings)`——pydantic-settings 环境单例，模块级 `_instance` 存在类外以避开 Pydantic 私有属性语义，`get_instance()` 惰性创建；字段含 model_name/model_size（默认 "2B/pre-trained"）/output_dir/uploads_dir/log_file/num_gpus/disable_guardrails/worker_timeout=3600。② IPC 层 `model_ipc/`：`command_ipc.py` 是**基于文件的 JSON 轮询协议**——`WorkerCommand` 往 `/tmp/worker_{rank}_commands.json` 写 `{"command":..., "params":...}`（`command_ipc.py:37-46`），worker 侧 `wait_for_command` 死循环 0.5s 轮询文件存在即读即删（`command_ipc.py:53-69`）；`WorkerStatus` 反向写状态文件，`_get_worker_status` 默认 1800s 超时（`command_ipc.py:118-128`），`WorkerException` 序列化远端栈回传。③ 进程层：`model_server.py` 的 `ModelServer` 按 num_gpus spawn `ModelWorker` 子进程、广播 infer、聚结果（`model_server.py:75` start_workers、`:175` infer）；`model_worker.py` 的 `worker_main` 读 `FACTORY_MODULE/FACTORY_FUNCTION` 环境变量反射构造 pipeline，`poll` 循环处理 inference/shutdown。④ UI 层 `gradio_app/`：`gradio_app.py` 的 GradioApp 持 ModelServer 暴露 infer；`gradio_ui.py` 的 `create_gradio_UI` 把推理表单、`gradio_file_server.py`（上传/输出浏览/文件查看）与 `gradio_log_file_viewer.py`（`_tail_file` + 定时器刷新）拼成一个 Blocks；`gradio_app_cli.py` 是无双向通道的 CLI 变体（错误不回传）；`gradio_test_harness.py` 起 server 子进程轮询 `/health` 做测试夹具。

## 三、外部连接

向上 cosmos-oss 的 `gradio = ["cosmos-gradio==0.1.0"]` extra（`packages/cosmos-oss/pyproject.toml:94`）与根 pyproject 的 `gradio = ["cosmos-oss[gradio]"]` 别名把它挂进主安装链，`cosmos-gradio = [{ workspace = true }]` 同走 workspace 解析。`sample/` 给出完整接入样例：`sample_worker.py` 定义推理参数 schema/校验与 infer 并导出 `create_worker` 工厂；`bootstrapper.py` 读 DeploymentEnv、选工厂、组装 GradioApp+UI；`run_gradio_sample.sh` 设 `MODEL_NAME/NUM_GPUS=2` 后启动；`sample_client.py`（221 行）演示 Cosmos Transfer1 的 sync/async/带上传四种客户端模式；`ipc_demo.py` 直接 `ModelServer(num_gpus=2)` 广播命令（`sample/ipc_demo.py:30`）。构建侧 `BUILD.md` 给两条路线：pip+build（CI/发布）与 uvx+hatchling（本地开发）；包内 `justfile` 提供 black/isort 与 mypy。发版脚本 `packages/cosmos-gradio/bin/release.sh` 是根 `bin/release.sh:1`（`-euo pipefail` 头）的早期变体——缺严格模式头，属同源分叉旧版残留。

## 四、数据流

一次 UI 推理的完整链路：用户在 Gradio 表单提交 → `GradioApp.infer` → `ModelServer.infer` 组 params → `WorkerCommand.broadcast` 给每个 rank 写 `/tmp/worker_{rank}_commands.json` → 各 `ModelWorker.poll` 的 `wait_for_command` 0.5s 轮询命中、读文件、删文件 → 反射构造的 pipeline 执行 `infer(args)` → 结果经 `WorkerStatus.signal_status` 写状态文件 → server 侧 `_get_worker_status` 等到 SUCCESS/异常 → 结果渲染回 UI，输出物落 uploads_dir/output_dir 供文件服务器浏览。命令与状态双通道都是文件轮询而非 socket——牺牲毫秒级延迟换零依赖零端口占用，对"UI 进程与每 GPU 一个 worker"的同机拓扑是够用的取舍。

## 五、设计决策

**哨兵为什么是独立包而不是环境变量**：uv 的 extras 机制只能"装/不装"包，不能设置环境变量；把"已选 extra"物化为一个可 import 的空包，主包就能在 import 期探测，且版本对齐校验顺带拦截"改了主包版本却没重装 extra"的半更新状态——错误信息直接给出修复命令，把分布式环境最常见的坏环境问题变成一条可复制的提示。**IPC 为什么选文件轮询**：多 GPU worker 的命令广播若用 socket 需要端口管理/序列化协议/断连处理三件套；`/tmp` JSON 文件天然支持广播（每 rank 一个文件）、幂等（读后即删）与人类可调试（cat 一下就知道卡在哪）。代价是 0.5s 轮询粒度与 `/tmp` 多实例冲突——同机起两个 server 会互相吃掉对方的命令文件。**甄别与坑**：`bin/start_gradio_app.sh` 的默认 `GRADIO_APP=$REPO_ROOT/server/gradio_app.py` 在本仓**不存在 server/ 目录**（仓根 ls 实证），不带 GRADIO_APP 环境变量直接跑必然 `exit 1`——该脚本是从上游 cosmos 仓搬来的，应用入口需自备；脚本还会 `pip install gradio --break-system-packages`，在受管环境里是副作用。

## 六、新人提示

哨兵报错时按错误信息的命令重装即可，不要手工 `pip install cosmos-cuda` 绕过——那会绕开 extras 依赖组，torch/flash-attn 版本组合就失去保证。读 cosmos-gradio 建议从 `sample/ipc_demo.py`（最短可运行示例）入手，再读 `command_ipc.py` 全文（不到 150 行却是全部协议），最后看 `bootstrapper.py` 的组装顺序。练习：① 写一个两行脚本验证哨兵：`import cosmos_predict2` 在未 sync extra 的环境应抛什么错、在版本不齐的环境应抛什么错；② 把 `ipc_demo.py` 的 `num_gpus=2` 改成 4，观察 `/tmp/worker_*_commands.json` 的数量与生命周期（写入→worker 删除→状态文件出现），并思考若 worker 崩在 infer 中途，server 侧 1800s 超时前 UI 会表现为什么（提示：无心跳，只有超时后的一次性 WorkerException）。

> 甄别说明：双侧 `_check_cuda_extra` 行号、extras 中哨兵字符串、文件 IPC 路径与轮询间隔、1800s 超时、`.python-version` 3.10 均源码核实；"server/ 目录不存在"由仓根实测；gradio release.sh 与根版差异（无 `-euo pipefail`）由 head 实测；"多实例 /tmp 冲突"为协议形态推断，未实际构造冲突复现。
