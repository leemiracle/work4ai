# Bobber ONBOARDING —— 容器化 AI 系统性能基准框架（v6.3.1）

> 仓：`NVIDIA/Bobber` @ 39435ee（本地 `/usr-data/data2/repos/agent-repos/NVIDIA/Bobber`）。
> 图谱：仓内 `.understand-anything/knowledge-graph.json`（149n/294e/4 层/6 步 tour，validator 0 issues，fingerprints 45 文件）。
> 本文所有行号锚均从源码核实（2026-11-07）。

## 1. 项目定位：它在解决什么问题

Bobber 是 NVIDIA 开源的**单/多节点 AI 系统性能验收基准框架**——把"一台 DGX 或一组节点是否达到应有的存储/网络/数据管线水位"这件过去要手工拼脚本的事，收敛为一个 pip 安装的 CLI（`setup.py:31` 的 `bobber=bobber.bobber:main`）加一个自包含 Docker 镜像。版本 `bobber/__version__.py:2` 为 `6.3.1`，PyPI 包名 `nvidia-bobber`（`setup.py:9`）。

它的测试面覆盖五类负载（这也是任务书中"五类基准"的准确口径）：

- **NCCL 集合通信**：`bobber/test_scripts/nccl_multi.sh` 跑 `all_reduce_perf` 扫消息尺寸取最大 bus bandwidth；
- **fio 存储三件套**：带宽（1MB 块）/125K 块/4K IOPS，同一脚本 `fio_multi.sh` 靠环境变量改变块大小；
- **IO500/mdtest 元数据**：`bobber/test_scripts/mdtest_multi.sh:34` 调 `/io-500-dev/bin/mdtest`；
- **DALI 数据摄取**：`dali_multi.sh` + `call_dali_multi.sh` 跑 DALI 自带 RN50 数据管线（jpg 与 tfrecord 两种格式 × 两种分辨率）；
- **OSU 与 MLPerf**：注意这两者在本仓中**没有 runner 脚本**——OSU 微基准只被构建进镜像（`Dockerfile:56-62` 编译、`Dockerfile:111` 拷贝），MLPerf 只有独立解析器 `bobber/lib/analysis/parse-mlperf.py`。"五类"里 OSU/MLPerf 是"建好待用"的半成品接口，运行链上真正有 runner 的是 NCCL/fio×3/mdtest/DALI。

一句话定位：**Bobber = 生命周期管理（build/export/load/cast）+ 测试编排（7 个 run-* 命令）+ 日志解析与验收（parse-results + 基线比对）的闭环**，被测对象是"GPU 节点 + 存储 + 网络"这一整条 AI 基础设施栈。

## 2. 总体架构：五子系统与依赖方向

代码全部在 `bobber/` 包内，按 `bobber/lib/` 分成五个子系统（与图谱 L02 子系统层一致）：

| 子系统 | 位置 | 职责 |
|---|---|---|
| CLI 门面 | `bobber/bobber.py`（409 行） | 参数解析、命令分发、settings 加载/保存 |
| docker | `bobber/lib/docker/`（`__init__.py` + `management.py` + `Dockerfile`） | 镜像构建、容器拉起、命令注入执行 |
| tests | `bobber/lib/tests/run_tests.py` | 测试编排：按命令/迭代/节点组合派发脚本 |
| analysis | `bobber/lib/analysis/`（13 个 py） | 日志解析、聚合、表格输出、基线比对 |
| system/杂项 | `bobber/lib/system/file_handler.py`、`constants.py`、`exit_codes.py` | 文件读写、系统常量、退出码 |

依赖方向是严格单向的：`bobber.py` → `tests/run_tests.py` → `docker/__init__.py` → `docker/management.py`；`bobber.py` → `analysis/parse_results.py` → 五个单测解析器（`fio.py`/`nccl.py`/`dali.py`/`meta.py`）+ `aggregate_results.py` + `table.py` + `compare_baseline.py`。两个例外值得记住：`analysis/parse-mlperf.py` 自带 `parse_args`/`main` 独立入口（`parse-mlperf.py:55-68`），不被任何模块 import；`parse_results.py` 与 `parse-mlperf.py` 同目录但互不依赖。

`docker/__init__.py` 是一个精巧的**方法别名门面**：模块加载即实例化单例 `manager = DockerManager()`（`__init__.py:5`），再把实例方法提升为模块级变量（`__init__.py:9-13` 的 `build/cast/execute/export/load`），于是下游可以写 `bobber.lib.docker.build(version)` 而感觉不到类存在（`bobber.py:380-386` 正是这么用的）。

## 3. 命令面与参数系统：一个 189 行的 parse_args

`bobber/bobber.py:65-253` 的 `parse_args()` 单函数构建全部命令树：

- **12 个子命令**：7 个测试命令（`run-all`/`run-dali`/`run-nccl`/`run-stg-bw`/`run-stg-125k`/`run-stg-iops`/`run-stg-meta`，常量定义在 `constants.py:7-13`）+ 5 个生命周期命令（`build`/`export`/`cast`/`load`/`parse-results`，`constants.py:2-6`）。测试命令共享同一个 `commands_parent` 父解析器（`bobber.py:87`），因此继承了约 20 个通用 flag。
- **hosts 唯一性校验**：`unique_hosts()`（`bobber.py:34-62`）以自定义 `type=` 挂进 `--hosts`（`bobber.py:93-95`），重复主机名直接 `ArgumentTypeError`——因为 Bobber 不能在同一主机并发跑。
- **`--system` 系统预设**：三个 DGX 预设字典（`constants.py:15-50`）注入 gpus/threads/batch-size/网卡等默认值，`choices=SYSTEMS.keys()`（`bobber.py:172`）。**关键坑**：DGX_A100 系列键用下划线（`bw_threads`，`constants.py:17`），DGX_2 用连字符（`bw-threads`，`constants.py:41`）——因为 `load_settings()` 把字典键直接 `setattr` 到 args（`bobber.py:345-347`），而 argparse 的 dest 恰好两种风格都有（`--bw-threads`→`bw_threads` 但 DGX_2 时代 dest 是连字符），消费端 `run_tests.py:84` 的 `args.bw_threads` 只认下划线版本。选 `--system dgx-2` 且不显式覆盖线程数时，预设键对不上 args 属性，等于没生效。
- **`--sweep` 节点扫描**：`bobber.py:154-160` 开启后 `test_selector()`（`run_tests.py:341-348`）从单节点逐台加机器跑完全组合，这是 Bobber 输出"1..N 系统扩展性曲线"的来源。
- **可复现测试**：每次跑测先把全部参数 dump 成 `{log_path}/command_parameters.json`（`save_config()`，`bobber.py:307-309`）；下次 `--config-path` 指回该文件即可复现（`load_settings()` 优先走 config，`bobber.py:339-340`）。`--no-direct` 在这里被翻译成 `direct=0/1` 数值属性（`bobber.py:354-357`）。

命令分发在 `execute_command()`（`bobber.py:361-393`）：parse/build/export/cast/load 五个直接走 docker 门面；其余测试命令统一做版本下划线化（`bobber.py:389`，用于日志文件名）→ `load_settings` → 建日志目录 → 存 config → `run_tests.test_selector()`。

## 4. 容器子系统：双 stage 镜像与 SSH 2222 通信底座

**Dockerfile 是多机测试的物理基础**（`bobber/lib/docker/Dockerfile`）：

- **build stage**（`Dockerfile:3-68`）：基于 `cuda:11.2.0-devel-ubuntu20.04`，编译三套工具并**钉死 commit**——nccl-tests@`ec1b5e22`（`Dockerfile:52`）、io-500-dev@`0232acfa`（`Dockerfile:67`）、OSU 5.6.2 源码包（`Dockerfile:56`）。
- **runtime stage**（`Dockerfile:71-128`）：`cuda:11.2.0-runtime`，只 `COPY --from=build` 三组建建产物（`Dockerfile:108/111/114`），再装 fio/openmpi/ssh 等运行时。DALI 仓库以 `git clone` + `reset --hard fd30786d` 进 runtime（`Dockerfile:116-118`），Python 侧装 `nvidia-imageinary['tfrecord']` 与 `nvidia-dali-cuda110`（`Dockerfile:120-124`）。
- **SSH 2222 免密通道**（`Dockerfile:93-103`）：改 `sshd_config` 端口为 2222、`StrictHostKeyChecking no`、预生成 4096 位 RSA 密钥并自授权——这是 MPI 在**多机容器间互通**的前提，所有 mpirun 都带 `-mca plm_rsh_args "-p 2222"`（`nccl_multi.sh:41`、`dali_multi.sh:51`、`mdtest_multi.sh:34`）。

`DockerManager`（`management.py:16-308`）同时持有**高级 + 低级双 Docker 客户端**：`docker.from_env()` 管 containers/images，`docker.APIClient(timeout=600)` 专供 build 的流式输出（`management.py:30-31`）。核心方法：

- `cast()`（`management.py:79-142`）：detached 启动容器跑 `bash -c "/usr/sbin/sshd; sleep infinity"`（`management.py:113`）——容器长驻、SSH 守护、后续测试全部经 `exec` 注入。启动参数里 `network_mode='host'`+`ipc_mode='host'`+`privileged=True`（`management.py:117-119`），被测文件系统 bind 到 `/mnt/fs_under_test`（`management.py:130-135`），`--ignore-gpu` 时去掉 nvidia runtime（`management.py:107-109`）。
- `execute()`（`management.py:215-265`）：先查容器在跑（`running` property，`management.py:288-308`），再做**容器版本 vs 本机版本一致性闸门**（`version_match`，`management.py:267-286`，不一致即 `CONTAINER_VERSION_MISMATCH` 退出），最后 `exec_run(stream=True)` 逐块打印并写日志。
- `export()`/`load()`：把镜像存成 tar 搬到其它节点再加载——多机测试的分发路径（`management.py:144-213`）。

## 5. 测试执行链：Python 编排 → 环境变量注入 → 容器内脚本

`run_tests.py` 为每类测试准备两样东西：**编码全部参数的日志文件名**和**环境变量字典**。以 stg-bw 为例：文件名 `stg_bw_iteration_{i}_threads_..._systems_N_version_X.log`（`run_tests.py:82-90`，这个命名是解析器反查 systems 数与版本号的地基），环境变量含 `IO_DEPTH/DIRECTIO/THREADS/READ_PATTERN/WRITE_PATTERN/HOSTS`（`run_tests.py:91-99`），然后 `manager.execute('tests/fio_multi.sh', ...)` 注入容器。

`kickoff_test()`（`run_tests.py:303-321`）按命令派发；`run-all` 的**固定顺序**是 nccl→meta→bw→dali→iops→125k（`run_tests.py:315-321`）。`--pause N` 在每个测试间 sleep（如 `run_tests.py:57-58`）等系统静默。

容器内脚本层的三个设计点：

- **`setup_fio.sh` 是函数库**（无 shebang，被 `fio_multi.sh:39` `source`）：`drop_caches()`/`stop_servers()`/`start_servers()`/`create_jobfile()`/`launch_fio()` 五函数 + 环境变量默认值区（`setup_fio.sh:108-133`）。`FSTYPE` 由 `df -T` 自动探测（`setup_fio.sh:109`）。
- **GPFS 缓存分流**（`setup_fio.sh:1-28`）：`drop_caches()` 对 gpfs 明确跳过（服务端缓存不在客户端可控范围，`setup_fio.sh:5-7`），lustre/nfs/ext4/wekafs 及未知类型都执行 `ssh` 并行下发 `sysctl vm.drop_caches=3`（`setup_fio.sh:20-25`）——保证读测试是冷缓存。
- **fio 的 create-then-test 模式**（`fio_multi.sh:53-59`）：先 `--create_only=1` 大块预写（官方注释：先建文件能提升后续性能且小块创建太慢），再 write→drop_caches→read→drop_caches，最后 `stop_servers` 清场。多机时用 fio 的 `--client` 模式把任务文件分发到 nodelist（`setup_fio.sh:94-98`）。
- **DALI 数据工厂**（`dali_multi.sh:35-49`）：现场用 `imagine create-images/create-tfrecord` 合成两种分辨率随机图（数量=GPUS×1000），tfrecord 还要 `tfrecord2idx` 建索引；四轮测试（sm-jpg/lg-jpg/sm-tf/lg-tf）每轮之间同样 `sysctl vm.drop_caches=3`（`dali_multi.sh:52-61`）；真正跑分的是 `call_dali_multi.sh:8-10` 调 `/dali/dali/test/python/test_RN50_data_pipeline.py`。
- **NCCL**（`nccl_multi.sh:41`）：`all_reduce_perf -b 8 -e ${NCCL_MAX}G -f 2`（8B 起步、2 倍步长扫到上限）；`-mca btl ^openib` 显式禁用 openib 传输、`-mca btl_tcp_if_include $SSH_IFACE` 锁管理网网卡，避免 MPI 走错网段。mdtest 则硬编码 `THREADS=44`（`mdtest_multi.sh:4-5` 注释：更多线程会"blow up"，原因未明）。

## 6. 解析器链：文件名协议 → 五解析器 → 聚合 → 验收

`parse-results` 的入口 `parse_results.main()`（`parse_results.py:307-411`）是全仓最重的编排函数，7 个关键字参数对应 CLI 的全部输出选项。流水线四步：

1. **找文件+版本闸门**：glob 全部 `*.log`（`parse_results.py:39`）；`check_bobber_version()`（`common.py:70-109`）从文件名里的 `version_x_y_z` 段核对所有日志同版本，混版本目录直接 `ValueError`（可用 `--override-version-check` 跳过）。
2. **按系统数分桶**：`divide_logs_by_systems()`（`common.py:273-306`）按文件名里的 `systems_N_` 段（`num_systems()`，`common.py:35-37`）把日志分组，六个 parse 函数（`parse_results.py:356-365`）各取所需：bw/125k/iops/nccl/dali/meta。注意 `parse_fio_125k_bw()`（`parse_results.py:113-146`）与 bw 完全同构，复用 `parse_fio_bw_file`，仅日志前缀 `stg_125k_iteration` 不同——**125K 不是独立解析器，是 fio 解析器的第二实例**。
3. **单文件解析的口味**：fio 解析抓 `READ: bw=`/`WRITE: bw=` 行并核对命中数==系统数（`fio.py:99-103`），IOPS 多机时 fio 会多打一行"半聚合"结果、解析器显式丢弃最后一行（`fio.py:151-166`）；NCCL 只认 `float sum` 行、每日志取最大 busbw 及对应消息尺寸（`nccl.py:35-41`）；DALI 解析器先丢掉每系统一份的 warmup 轮（`sorted(all_speeds)[systems:]`，`dali.py:210`），聚合时再 ×系统数外推集群吞吐（`dali.py:272-275`）——这是"单节点均值 × N"的近似口径，不是真聚合。fio 参数本身也被解析（`common.py:245-270` 的 `fio_command_details`），跨日志参数不一致会报错，保证可比性。
4. **聚合与输出**：`AggregateResults`（`aggregate_results.py:34-461`）吃 17 个字典参数（`aggregate_results.py:99-116`），对每个系统数产出一份结果；`average_decorator`（`aggregate_results.py:6-31`）包住所有 `_average_*` 方法做容错均值（TypeError/ZeroDivisionError 兜底 0.0）。出口三件套：`display_table`（tabulate 彩色表，`table.py`）、`save_yaml_baseline` 自动把本次结果存成可复用基线 `baseline.yaml`（`parse_results.py:257-304`——注意这是**无条件写**的）、可选 JSON 落盘与基线比对（`compare_baseline`，容差语义为"只罚低于基线且超出容差"的单边判定，`compare_baseline.py:44-51`）。

内置两条基线在 `constants.py`：`SINGLE_DGX_STATION_BASELINE`（1 节点，`constants.py:71-97`）与 `DGX_A100_POD_BASELINE`（1-8 节点线性外推，`constants.py:99-286`）。

## 7. CI 双轨与版本工程

- **GitHub Actions**（`.github/workflows/python-package.yml`）：纯静态检查轨——Python 3.6-3.9 矩阵（`:14`）、pycodestyle lint（`:29`）、构建并安装 wheel（`:32-33`）、`bobber build` 验证镜像可构建（`:36`）。无真机测试。
- **GitLab CI**（`.gitlab-ci.yml`）：真机验收轨，三 stage（`pre_clean`→`docker_build`→`test`）：pre_clean 清空全部 Docker 资产（`:13-15`）；test stage 在真机 DGX 上 `bobber cast /raid` → `run-all`（2 迭代、显式覆盖 6 个线程/batch 参数，`:44`）→ `parse-results --compare-baseline single-dgx-station-baseline`（`:45`）。注意 `:7` 的 `GIT_SUBMODULE_STRATEGY: recursive`：本仓**没有 `.gitmodules`**，nccl-tests/io-500-dev 等是 Dockerfile 构建期 git clone 的，该变量实际是残留配置。
- **开发版轮子**（`build-dev-wheel`）：bash 函数分发的典型样例——先用 `echo "# SPDX..." > bobber/__version__.py` **重写**版本文件（`:31`），再按 minor/patch/current 追加一行 `__version__ = 'M.m.p.dev<timestamp>'`（`:8/16/24`），最后 `setup.py bdist_wheel sdist`（`:39`）。追加而非原地替换，所以版本文件永远只有 2 行。

## 8. 新人上手路径

1. **先读两条链**：命令链 `bobber.py:main → parse_args → execute_command`（`bobber.py:396-405`）与数据链 `run_tests.py 环境变量 → fio_multi.sh → 日志文件名 → parse_results 分桶`。读懂这两条，仓的 80% 就通了。
2. **跑通单节点**（不需要 DGX 也能理解流程）：`pip install .` → `bobber build`（约 30-60 分钟）→ `bobber cast /mnt/your/fs` → `bobber run-stg-bw --system dgx-a100-single <logdir> localhost` → `bobber parse-results <logdir>`。非 DGX 系统参 `docs/non_dgx_support.md`。
3. **改测试参数**：入口在 `bobber.py:100-181` 的通用 flag 区；改了 flag 记得同步三处——`run_tests.py` 的日志文件名模板（否则解析器分桶失败）、对应 `*_multi.sh` 的环境变量读取、`constants.py` 的系统预设。
4. **加新基准**：抄 fio 三件套的全链模式——test_scripts 新脚本 + `run_tests.py` 新 `run_xxx()` + `kickoff_test` 分支 + `parse_results` 新 parse 函数 + 文件名带 `systems_N`/`version_X` 段（解析器依赖此协议）。
5. **常见坑**：①DGX_2 预设键连字符/下划线错位（见 §3）；②日志目录混入其它版本结果会被版本闸门拦（`common.py:105-107`）；③`parse-results` 每次都会覆盖写 `baseline.yaml`（`parse_results.py:404`），自定义基线请另存；④容器与 CLI 版本必须一致，升级后要 `docker kill bobber` 重 cast（`management.py:242-246`）。
6. **文档补充**：`docs/` 七篇（baselines/building/docker/parsing/troubleshooting/non_dgx_support/sample_baseline.yaml）+ 顶层 README 有逐命令示例； troubleshooting 覆盖 SSH/网络/Docker 常见故障。

（完 · 锚 60+，字数口径=不计空格字符）
