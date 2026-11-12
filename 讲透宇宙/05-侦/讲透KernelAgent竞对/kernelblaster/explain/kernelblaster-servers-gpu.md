# KernelBlaster 服务设施深解：GPU Server / Compile Server / Resources

> 对象：`src/kernelblaster/servers/gpu.py`、`servers/compile.py`、`resources/servers.py`、`resources/client.py`（辅以 `servers/management.py`、`servers/cuda_env/CMakeLists.txt`）
> 图谱定位：`compute-servers` 层（编译与 GPU 服务层）+ `resources` 层（资源管理层）。全库 fan-out 最高模块（compile 25 / gpu 19）。

## ① 角色定位：为什么编译和评测要走独立 server

KernelBlaster 是多 agent 并发生产候选 kernel 的系统：一次批量实验（`scripts/run_RL.py`）会用 Semaphore 同时调度几十个 workflow，每个 workflow 反复"生成→编译→运行→剖析"。若编译和 GPU 执行散落在各 agent 进程内，会立刻撞上三类问题：

- **资源争用**：GPU 计算是独占资源，并发进程直接抢卡会让计时失真。GPU server 启动时 `check_gpu_processes()` 甚至会因发现任何遗留 GPU 进程而拒绝启动（psutil 校验存活、过滤 `[Not Found]` 僵尸条目）——保证测量基线干净。
- **并发控制**：两个 server 都用 `asyncio.Queue` + N 个 worker 把"无限并发的 HTTP 请求"整流为"受控的串行/并行执行"。compile server 默认 8 worker（按管理器拉起时为物理核数-1），GPU server 每 GPU 一个 worker，靠执行期注入 `CUDA_VISIBLE_DEVICES` 绑定专属卡。
- **环境一致性**：`NVIDIA_TF32_OVERRIDE=0` 全局钉死（关 TF32 保数值可比）；CMake 层清除 PyTorch 注入的全部 `-gencode` 再按 `-DGPU_ARCH_VERSION` 注入单一目标架构，避免 fatbin 污染。

两个服务都是 FastAPI + uvicorn 的**无状态** HTTP 服务（compile 2001 / gpu 2002），因此可以同机拉起，也可以通过环境变量指向远端（甚至 NVCF 云函数——`commands.py` 对 `api.nvcf.nvidia.com` 有专门 Bearer 认证分支）。

## ② 内部结构：生命周期、任务协议、cuda_env

**生命周期**（两 server 同构）：`management.py` 的 `initialize_*` 先查 `config`（`COMPILE_SERVER_URL` / `GPU_SERVER_URL_<GPU>` 环境变量）——已有 URL 则直连（`process=None, is_managed=False`）；否则 `find_free_port` 从 2001/2002 探测空闲口，`subprocess.Popen` 以 `python -m` 拉起子进程（`start_new_session` 独立进程组），日志重定向到实验目录的 `compile_server.log` / `gpu_server.log`。`ManagedServer.wait_for_connection()` 以 0.25s 间隔轮询 `/health`（容忍僵尸/包装器进程），失败时转储服务日志。FastAPI `lifespan` 启动 worker 协程；compile server 关闭时 `free_cuda_envs()` 递归删除环境目录。

**任务协议**：核心是"7 元组 + Future"队列模式。`GET /compile`（注意：源码走**文件路径**而非上传，隐含同机共享文件系统假设）校验文件存在、`NamedTemporaryFile` 预生成输出路径，入队 `(job_name, main_file, cuda_file, sm_version, persistent_artifacts, output_path, future)`；handler `await future` 后组装 `CompilationResult`。GPU 侧 `POST /gpu/binary` 是 multipart 上传（二进制 + args/env_vars JSON/prefix_command/n_runs/timeout），入队 `(binary_path, args, env_vars, prefix, n_runs, timeout, future)`；worker 把结果写回 Future，`GpuCommandResult` 携带 stdout/stderr（`n_runs>1` 时为列表）。旧 `GET /gpu/cmd`（2 元组裸命令）保留兼容但已弃用。

**与 cuda_env/CMakeLists.txt 的关系**：`cuda_env/` 是随源码分发的编译环境模板（仅一份 CMakeLists.txt）。compile server 首次用到时 `shutil.copytree` 出每 worker 一份（`cuda_eval_{thread_id}`，可被后续任务覆写复用）；`ENV_DIR = artifacts_dir/uuid4()` 做服务实例级隔离。编译分三步：`split_files_for_compilation` 把 main.cu 拆成 `main.cpp` + `cuda_model.cuh`（用 `find_kernel_launch_header` 抽出 kernel 启动声明，前置 `<cstdint>`/`torch/torch.h`）+ `cuda_model.cu`（去 `inline`/`extern "C"` 以便链接）；cmake configure 只在 `build_{sm_version}` 不存在时执行（架构不变则复用缓存）；然后 `make -j8`（360s 超时，超时经 `safe_kill_process` 按进程组击杀）。产物 `build/main` 拷到输出路径并 chmod 755。

## ③ 外部连接：谁调用它

- **`agents/utils/commands.py`**（核心客户端）：`compile_cu` → `GET /compile`；`run_gpu_executable` 按 `GPUType` 从 config 路由 URL → `POST /gpu/binary`（含一次瞬时错误重试）；`compile_and_run_cu_file` 是复合流程（编译→n_runs 次运行→`passed_keyword` 正确性判定→NamedTimer 计时）。所有调用共享 `TCPClient` 单例（1024 连接池 aiohttp 会话）。
- **`scripts/run_RL.py`**：批量实验入口，直接实例化 `CompileServer`/`GPUServer` 拉起服务。
- **`servers/serve_api.py`**：工作流任务队列服务（更上层的服务），间接消费整套设施。
- **NCU 系 agent**（`opt_ncu_rl.py` 等）：`prefix_command="ncu ..."` + `persistent_artifacts=True`。
- **`docker/entrypoint.sh`** 依赖 gpu server 与 serve_api 部署。

## ④ 数据流：一个候选 kernel 的服务端旅程

1. **生成**：CUDA agent 在实验目录写出 `kernel.cu` + `main.cu`。
2. **编译**：`compile_cu` 携带绝对路径与 `sm_version` 请求 `/compile` → worker 复制 cuda_env、拆分三文件、cmake（按需）+ make → 返回 `output_path`（服务器侧临时二进制）。
3. **运行/计时**：`run_gpu_executable` 读二进制字节 POST 上传 → server `mkstemp` 落盘（随机后缀防并发重试撞名/"Text file busy"）→ 入队 → worker 注入 `CUDA_VISIBLE_DEVICES=<专属卡>` → `./binary args` 跑 n_runs 轮 → stdout 列表经 Future/JSON 回传 → 临时二进制清理（成败皆清）。
4. **NCU**：同一端点，`prefix_command="ncu -o ..."` 前缀执行；因 worker 环境会被后续编译覆写，编译时开 `persistent_artifacts` 把源码存进唯一目录供 NCU 源码级标注（`-lineinfo` 已在 CMake 里为 NCU 预埋）。

## ⑤ 设计决策

- **编译与执行分离**：CPU 密集（可 8-40 并行）与 GPU 独占（每卡串行）资源性质不同，拆成两个服务各配各的并发模型。
- **执行期注入环境变量**而非进程级固定：worker 每次任务合并 env，显式传入的 `CUDA_VISIBLE_DEVICES` 优先，实现"每 worker 绑卡 + 调用方覆盖"双语义。
- **双形态部署**：本地受管子进程（自动端口、随实验清理）与预置 URL（共享/远程/NVCF）由 config 一切换。
- **不对称传输**：GPU 走上传（跨机可用），compile 走路径（同机假设）——迁移时注意。
- **多卡扩展约定**：worker 数与绑卡由环境变量声明（`KERNELBLASTER_GPU_SERVER_GPU_IDS="0,1,2,3"` 或 `KERNELBLASTER_GPU_SERVER_NUM_WORKERS=4`），队列天然把请求分派到空闲 worker，上层无需感知卡数。
- **缓存与复用的取舍**：每 worker 复用同一 cuda_env 目录换取 cmake 缓存命中（架构不变时只跑 make），代价是源文件被覆写——`persistent_artifacts` 就是为对冲这个代价而设的逃生门。
- **安全细节**：`safe_kill_process` 带 pgid 0/1 黑名单防误杀；`timeout_graceful_shutdown=0.1` 快速停机；上传文件名只取 basename。

## ⑥ 新人提示

- 调试先看实验目录下 `compile_server.log`/`gpu_server.log`（受管模式）或 `/tmp/kernelblaster/`（独立模式）；worker 日志带 `[Worker N]` 前缀可定位到卡。
- "二进制编译成功但运行报错"多半是拆分环节（header 抽取失败/inline 残留），先读 `CompilationError` 里的 make stderr。
- GPU server 启动失败优先怀疑遗留进程独占显卡；compile 失败优先怀疑 torch cmake 前缀路径（`torch.utils.cmake_prefix_path` 必须存在）。
- 想共享 server 给多进程：用 `scripts/start_gpu_server.py`（`start_standalone_gpu_server`），再以 `GPU_SERVER_URL_*` 环境变量让各进程直连。
- 计时数字不稳先查三处：是否误开了 NCU 前缀（`-lineinfo` 本身有运行时开销，剖析与基准不要混跑）、`NVIDIA_TF32_OVERRIDE` 是否被调用方 env_vars 覆盖、GPU 是否真被 worker 独占（看日志里 `Assigned GPU CUDA_VISIBLE_DEVICES=` 行）。
