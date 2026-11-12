# CompileIQ 新人上手指南（ONBOARDING）

> 基于知识图谱 582 节点 / 920 边 / 12 层 / 13 步导览（commit `4df0d5c8`，fingerprints 262 文件）生成；全部行号锚从源码逐条核实。

## 1. 项目定位：编译器控制项的超参优化器

CompileIQ 是 NVIDIA 开源的**编译器控制项（compiler controls）调参框架**——把"该给 ptxas/nvcc 传什么编译选项"这件事本身变成一个可搜索的优化问题。一句话心智模型：

- **你**定义目标函数（编译一次、跑一次、计一个分）+ 搜索空间（哪些编译控制项、各自取值范围）；
- **CompileIQ** 用搜索引擎（默认且唯一捆绑的 `amber`，编译版 NSGA-III 运行时）经 ask → evaluate → tell 循环逐代逼近最优配置；
- 产出 ACF（applied controls file）候选与 `SearchResult`，再用统计检验门（Welch t 检验）确认加速真实后才建议发货。

为什么需要它？编译器控制项的组合空间是组合爆炸的（一个 ACF 可同时钉几十个开关与阈值），人工试错与网格扫描都不可行；而每次评估都要真编译、真运行，成本高且带计时噪声——所以搜索引擎必须样本高效（NSGA-III 的参考点机制适合多目标），结论必须过统计检验（booster-pack 技能的存在意义就是"先试精选候选，别急着付全量搜索的钱"）。产出物 ACF 可直接经 `--apply-controls` 注入 ptxas/nvcc/Triton 等工具链（`agent-skills/compileiq-author-objective/SKILL.md` 的 description 覆盖五类注入目标）。

权威出处：`README.md:37-39` 与 `docs/install.md:14`（"In CompileIQ 1.1, `amber` replaces the original search core"）。它是 **Python 前端 + 可插拔引擎后端** 的世界：前端 `compileiq/` 包纯 Python（引擎无关），引擎经 entry point 注册、进程内创建（`AGENTS.md` Architecture 节）。仓库同时是"框架 + 五族编译器示例 + 一个自带测试的 XLA 深度子项目 + 7 个 AI 代理技能 + 一套 fail-closed 发布工程"的复合体——这决定了新人的阅读路径必须分层。

技术栈：Python ≥3.11（CI 覆盖 3.11-3.14，`AGENTS.md` Build 节）、Poetry 依赖分组（`pyproject.toml`，native-runtime 组在 `pyproject.toml:38-41`）、Pydantic 建模、Ruff lint（E/F 规则、行长 100）。

## 2. 仓库架构：12 层图谱总览

知识图谱把 262 个分析文件组织为 12 层，从门面到测试呈现清晰的依赖梯度（节点类型分布：file 179 / function 181 / class 109 / document 55 / step 30 / config 24）：

| 层 | 名称 | 内容要点 |
| --- | --- | --- |
| 0 | 仓库门面与工程治理 | README/AGENTS/CLAUDE（单一事实源转发）、Makefile（55 个 target）、pyproject、EULA/NOTICE/SECURITY/CONTRIBUTING、pyrightconfig 双文件 |
| 1 | 核心搜索运行时 | `compileiq/` 包主干：ciq.py / backends.py / worker.py / types.py / results.py / tracker.py |
| 2 | 搜索空间体系 | base.py 四原语、compilers.py 加密 provider、models.py/manifest.py 清单模型、resolver.py 资产解析 |
| 3 | amber 原生运行时矩阵 | `native-runtime-wheels/` 16 格 wheel + 16 份 manifest（Git LFS 分发） |
| 4 | 通用 API 示例 | `examples/` 根 9 个脚本铺开前端 API 用法面 |
| 5 | 编译器调优示例 | `examples/compilers/` 五族：ptxas/nvcc/triton/nvbench/cutile |
| 6 | xla_ciq 深度示例子系统 | 55 文件自带 16 个测试文件与 dump 夹具的子项目 |
| 7 | agent-skills 技能集 | 7 个 agentskills.io SKILL.md 技能 + 安装器 |
| 8 | dev 发布工程 | 21 个组装/验证/守卫脚本 |
| 9 | CI 门禁与协作自动化 | ci.yml 15 job / nightly.yml / docs.yml |
| 10 | 测试体系 | unit（26 文件）/integration（7）/fuzz（1）/compiler_ss 四分区 |
| 11 | 文档体系 | Sphinx 站 + 19 篇 markdown（search_strategy.md 435 行最深） |

阅读顺序建议直接复用图谱 13 步导览（tour）：t01 全景 → t02/t03/t04 核心运行时三角（Search/backends/worker）→ t05 搜索空间 → t06/t07 示例 → t08 xla 深水区 → t09 技能 → t10/t11 发布与 CI → t12 测试 → t13 文档收官。核心代码全部集中在第 1-2 层的 16 个 Python 文件里（共约 6400 行），是"小内核、大周边"的典型布局。

## 3. 核心搜索引擎：Search 门面（ciq.py）

`compileiq/ciq.py`（1695 行）是主入口，`Search` 类在 `ciq.py:341`。生命周期四步：

1. **构造**：`Search(objective_function=..., search_space=..., search_config=...)`；Pydantic 校验器 `normalize_search_config`（`ciq.py:463`）与 `normalize_engine`（`ciq.py:472`）规范化输入；
2. **ask**（`ciq.py:756`）：从后端拿参数候选；`sample`（`ciq.py:723`）可独立采样不启动搜索；
3. **evaluate**（`ciq.py:907`）：把候选交给 worker 并行执行目标函数；嵌套字典参数对用户透明地 flatten/restore（示例见 `examples/nested_search_space.py`，50 行）；
4. **tell**（`ciq.py:930`）：提交分数，`start`（`ciq.py:1470`）托管整个 ask/evaluate/tell 主循环。

**tell 的三重校验是全仓最重要的契约**：在后端接受前依次验证 (a) 候选 ID 有效性——重复/未知/已上报即拒（`ciq.py:944-950`）；(b) 目标数与搜索配置一致（`ciq.py:951-958`）；(c) 归一化分数存在且合法（`ciq.py:966-980`）；可选的 params 回显也要匹配签发候选（`ciq.py:960-965`）。任何一步失败都 `raise ValueError` 且**不产生任何状态变更**——所有状态写入（`self._has_activity = True`、`_backend_impl.tell`、结果行追加）都在校验全过之后（`ciq.py:1029-1035`）。这条"拒绝零残留"契约被 `tests/unit/test_backends.py` 的 pristine 模式锁死（见第 8 节）。

两个容易踩的行为细节：其一，baseline 分数走特殊通道——`tell` 里 `is_baseline` 的分数不计入非基线校验集合，params 缺省时以 `BASELINE_CONFIG` 补齐（`ciq.py:1013-1018`）；归一化模式下失败的候选由 `Worker.invalidate_score` 统一填充（`ciq.py:1023-1024`）。其二，第一代保护：若 `exit_on_failure` 开启且第 0 代全部候选失败（`_check_fail_count`，`ciq.py:1691`），直接 `RuntimeError` 提醒"你的目标函数可能整个就是坏的"，可用 `exit_on_failure=False` 关闭（`ciq.py:996-1003`）——这是把"目标函数写错"从漫长无效搜索提前到第一代就暴露的防御设计。

checkpoint 体系：5 个相关类——`CheckpointCompatibilityWarning`（`ciq.py:152`，UserWarning）+ 4 个 Pydantic 数据类 `CheckpointSearchConfig`（`ciq.py:173`）/`CheckpointResultRow`（`ciq.py:236`）/`CheckpointResultLedger`（`ciq.py:270`）/`CheckpointEnvelope`（`ciq.py:281`）；`save_checkpoint`（`ciq.py:1170`）、`restore_checkpoint`（`ciq.py:1237`）、`Search.from_checkpoint`（`ciq.py:1389`）。

配套模块：`types.py`（731 行）持有全部配置类型——`ProblemType`（`types.py:34`）、`WorkerTypes`（`types.py:356`）、`SearchConfiguration`（`types.py:489`，`extra="forbid"`），并维护现代与 legacy 字段的双向转换 `to_legacy`/`from_legacy`（`types.py:633`/`types.py:674`，均带弃用警告——1.0 配置迁移通道）；`results.py` 的 `SearchResult`（`results.py:14`）包装 pandas DataFrame，提供 `get_best_result`（`results.py:253`）与 `pareto_front`（`results.py:303`）；`tracker.py`（303 行）提供 DisabledTracker（`tracker.py:59`）/Loguru/MLflow 三种可插拔实验跟踪，`logging_exception` 装饰器（`tracker.py:40`）保证 tracker 故障不拖垮搜索。

## 4. 引擎后端：backends 与 amber entry-point 注册

`compileiq/backends.py`（451 行）定义引擎世界的三个角色：

- **`EngineConfig`**（`backends.py:27`，frozen Pydantic）：引擎选择；
- **`SearchBackend` ABC**（`backends.py:165`）：引擎实现的接口——`current_generation`/`pending_candidates`/`ask`/`tell`/`checkpoint`/`restore`/`is_complete` 等抽象成员；
- **entry-point 发现**：`_load_entry_point_backends`（`backends.py:326`）经 `importlib.metadata.entry_points` 按 group `"compileiq.backends"` 过滤（`backends.py:339-341`），加载每个 entry point 为 callable registrar 调 `register_backend`（`backends.py:289`）；`create_backend`（`backends.py:391`）进程内实例化。

**CompileIQ 1.1 的关键架构变更**：编译的 NSGA-III 运行时 `amber`（发行名 `compileiq_native_runtime`，版本 1.1.0.dev0）经此 entry point 注册，**取代了原 socket IPC 搜索核心**（`AGENTS.md` Project Overview；`docs/install.md:14`）。含义：前端与引擎同进程、无 IPC 序列化开销，但引擎是带平台标签的二进制 wheel——这就是第 6 层 16 格矩阵存在的原因。

amber 的一个文档化行为差异值得记住：**`amber` 从不重复候选**（`docs/install.md:18`），所以小空间会提前触发空间耗尽（`SearchSpaceExhaustedError`，`backends.py:72`）。

原生绑定集中在 `compileiq/utils/_libciq.py`（249 行）：ctypes 手工管理缓冲——`merge_controls` 的 restype/argtypes 声明在 `_libciq.py:78-89`，ACF 输入经 `from_buffer_copy` 转指针数组（`_libciq.py:163-165`），**合并完成后库侧结果缓冲必须显式 `library.free_buffer(result)` 释放**（`_libciq.py:187`），错误码经 `MERGE_ERRORS` 映射表（`_libciq.py:30`）转 Python 异常。开发态可用 `CIQ_LIBCIQ_PATH` 环境变量指向自编 libciq（`_libciq.py:25`、`load_libciq` 在 `_libciq.py:98`）。

## 5. 搜索空间体系：原语、加密 provider 与 resolver

`compileiq/search_spaces/` 四个模块构成三层结构：

**原语层**（`base.py`，185 行）：只有四个构造函数——`range`（`base.py:12`）、`choice`（`base.py:83`）、`literal`（`base.py:124`）、`log_sampling`（`base.py:157`）。刻意设计：**`range` 遮蔽 Python 内建名**，惯用法是 `from compileiq.search_spaces import range`（docstring 示例：`range(0,8,2)` 产生闭区间 `[0,2,4,6,8]`，`base.py:20-22`）。`range` 还接受 `knockout_prob`/`seed_low`/`seed_high`——后者是 xla_ciq 钉 seed 布局的关键武器（见第 6 节）。

**provider 层**（`compilers.py`，102 行）：`SearchSpaceProvider` 是 Protocol（`compilers.py:21`，`retrieve() -> dict | pathlib.Path`）；`CompilerSearchSpaceBase`（`compilers.py:32`）是 GitHub-release 加密搜索空间的基类（子类设 `compiler` 类属性、网络可关）；两个具体 provider `PtxasSearchSpace`（`compilers.py:66`）与 `NvccSearchSpace`（`compilers.py:75`）下载并校验加密 .bin（大小 + sha256）；`LocalSearchSpaceBin`（`compilers.py:84`）绕过网络用本地 .bin，`retrieve` 在 `compilers.py:101`。**注意 LocalSearchSpaceBin 是独立实现而非 CompilerSearchSpaceBase 子类**——它只满足同一个 Protocol，这是"协议独立实现"的甄别点（两个 provider 体系不共享基类）。为什么要"加密搜索空间"：编译器控制项的合法取值域与内部阈值是 NVIDIA 紧跟编译器版本演进的资产（发布在 GitHub Release 而非硬编码进包），加密 .bin + manifest 校验让前端可以在不暴露明文定义的情况下引用最新域，同时保持离线可缓存。模块 docstring（`compilers.py:9`）建议：已有本地 .bin 时直接用 `LocalSearchSpaceBin`。

**解析层**（`resolver.py`，423 行）：把 GitHub release 上的搜索空间资产解析到 `~/.cache/compileiq/<tag>/`（`resolver.py:104`，`_cache_root`）。latest-tag 解析是**三级容错缓存**：(1) 进程内 `@functools.lru_cache(maxsize=8)`（`resolver.py:223-224`）；(2) 磁盘缓存带 TTL——默认 7 天，环境变量 `CIQ_SS_LATEST_TTL_DAYS` 可调（`resolver.py:54-55`），缓存键按 repo+tag_prefix 哈希（`resolver.py:132-135`）；(3) GitHub 请求失败时**回退过期缓存**并告警（`resolver.py:241-248`）。hub 级入口是 `resolve_with_metadata`。清单模型在 `models.py`（110 行，`RangeParamConfig` 等）与 `manifest.py`（144 行，`SearchSpaceManifestModel`）；仓根 `schemas/search-space-manifest-v1.schema.json` 约束发布目录。

## 6. 编译器示例五族与 xla_ciq 深水区

**五族最短闭环**（`examples/compilers/`）：

- **ptxas_example**：调 ptxas 寄存器溢出最小化。脚本 `ptx_spill.py`（注意与负载文件区分：`ptx_spill.py:21` 引用 `PTX_SOURCE = SCRIPT_DIR / "w8_spill.ptx"`——2772 行故意制造寄存器压力的内核）。加密搜索空间入门首选，README：`python ptx_spill.py --arch sm_90a`；
- **nvcc_example**：`optimize_reduction.py` 对 `reduction.cu` 逐候选编译计时；
- **triton_example**：双变体对照——`triton_ptx.py` 纯加密空间 vs `mixed_triton.py` 加密+原语混合空间；
- **nvbench_example**：示范第三方基准框架对接（CMake 构建 + JSON 解析两段胶水，`optimize_reduction.py`）；
- **cutile_example**：`cutile_autotune.py` 单脚本调优。

根目录另有 9 个通用 API 示例（层 4）：`single_objective.py`（37 行，最小闭环起步）→ `multi_objective.py`（38 行，分数向量与 Pareto）→ `nested_search_space.py`（50 行）→ `normalizing.py`（57 行，基线目标函数自动归一化）→ `custom_worker.py`（110 行，继承 Worker 基类）→ `distributed.py`（59 行，Ray）→ `loguru_tracker.py`/`mlflow_tracker.py`（44/98 行）→ `ciq_xgboost.py`（67 行，证明非编译器场景同样成立）。

**xla_ciq_example 是仓内最大子项目**（55 文件，自带 16 个测试文件与 `tests/fixtures/xla_dump/module.ptx` 夹具），主线：**XLA dump → TMA tile 枚举 → ACF bundle**。这条链路的工程含义：XLA 编译出的内核用 TMA（Tensor Memory Accelerator）搬运数据时，tile/box 的切法既是性能关键又受硬件对齐约束，xla_ciq 把"从 dump 里读出当前布局、枚举所有合法替代布局、把调优结论打包成 bundle"整条生产者侧流水做了出来。边界先看 `workflow.md` 的责任表——搜索算法归父 CompileIQ 包，本子项目只做 dump 解析、指纹与序列化（"producer-side"定位，下游 XLA consumer 不在本仓；bundle 的指纹、版本、ACF 应用与回退行为**不是**稳定跨项目契约，`workflow.md` 明言 fail-closed 指纹重算只在评估侧演示）。四个关键模块：

- `xla/dump.py`（170 行）：`inspect_dump`（`dump.py:47`）索引 dump 内核；`_index_ptx_kernels`（`dump.py:91`）扫 module.ptx；`_enrich_from_thunks`（`dump.py:101`）rglob `*.thunk_sequence.txt`/`*.thunk_metadata.txt`；`_enrich_shapes_from_hlo`（`dump.py:133`）从 HLO 提形状；
- `xla/tensor_map.py`（308 行）：`TensorMapSpec`（`tensor_map.py:44`）+ `from_hlo_shape`（`tensor_map.py:186`）把 HLO shape（行主序打印）转 **CUDA innermost-first 序**（`tensor_map.py:11` 注释明说两者维度顺序相反）；
- `search/ptx_meta.py`（198 行）：纯正则解析 PTX——四组模式 `_ARRAY_RE`/`_SCALAR_RE`/`_ALIGN_RE`/`_MOV_PARAM_RE`（`ptx_meta.py:14-20`）覆盖参数声明与使用，`inspect_ptx_entry`（`ptx_meta.py:158`）入口；
- `search/tensor_map_search.py`（271 行）：枚举合法 TMA box。硬约束 `_TMA_ALIGN_BYTES = 16`（内轴 16 字节对齐，`tensor_map_search.py:19`）；**joint ACF×tile 空间爆炸控制**——只保留 seed box 及其邻域（`tensor_map_search.py:22-27` 注释）；最巧妙的是 `_index_knob`（`tensor_map_search.py:98-111`）：`choice` 无法置 seed，改用 `range(0, count-1, 1, seed_low=0, seed_high=0)` 把初始采样钉在已知可启动的 seed 布局上。

目标函数侧：`RuntimeObjective`（`search/compileiq_runtime.py:54`）docstring 直说设计动机——"Picklable CompileIQ objective (multiprocess workers cannot pickle nested defs)"：多进程 worker 无法 pickle 嵌套 def，所以目标函数必须是模块级类实例（可 pickle 供子进程、可哈希供去重，tensor map specs 以值对象嵌入，`compileiq_runtime.py:77`）。bundle 序列化走 protobuf：schema 源在 `examples/compilers/xla_ciq_example/schemas/xla_ciq_bundle.proto`（注意不在仓根 schemas/），再生命令在 `bundle.py:3-5`（`python -m grpc_tools.protoc ...`）；`xla_ciq_bundle_pb2.py`（52 行）是 protoc 生成物**不建议手改**。CI 在 `ci.yml:235-242` 跑该子项目的 mock reference example 与 protobuf binding check。

## 7. agent-skills：把 CompileIQ 交给 AI 代理

`agent-skills/` 提供 7 个 agentskills.io 约定的 SKILL.md 技能，让任何 AGENTS.md 感知的 coding agent（Claude Code/Codex/Cursor/Copilot/Aider/Windsurf）都能驱动 CompileIQ 调优战役：

| 技能 | 时机 |
| --- | --- |
| compileiq-bootstrap | 首次配置/首次评估挂起时；五步环境自检（CUDA 13.3+、ptxas、GPU、import 解析） |
| compileiq-booster-pack | 全量搜索前先试精选 ACF 候选（含 Debug 包 O0/O3 注入金丝雀） |
| compileiq-search-space | 选 provider 类或钉版本；`att` 变体面向 attention 负载 |
| compileiq-author-objective | 写/修 `objective_function=`，覆盖 PTXAS/NVCC/Triton/Helion/cuTeDSL/FlashInfer 注入 |
| compileiq-run-search | 组装 `Search(...)`、选 worker、配 SearchConfiguration 尺寸 |
| compileiq-validate-result | 宣称加速前过 Welch t 检验 + Cohen's d 门 |
| compileiq-debug | 症状索引速查（挂起/INVALID_SCORE/分数不涨/CV% 过高） |

安装器 `agent-skills/install.sh` 为每种 agent 生成 `mount_`/`unmount_`/`check_` 三件套函数（如 `install.sh:93/112/124` 的 claude_code 三件套，codex 在 `install.sh:137/165/177`），主分发循环按 agent×模式 case 派发（`install.sh:443-448`）；`python_bin`（`install.sh:39`）探测保证渲染器可用。统计检验门的实现在 `compileiq-validate-result/scripts/welch_validate.py`：CLI 头文档即用例（`welch_validate.py:1-21`），判定三合一——p<0.05 且均值下降且 Cohen's d>0.2 才算 significant（`welch_validate.py:127`），不显著时给出 `not_significant(p=...,d=...)` 原因（`welch_validate.py:274`），自带 self-test 断言（`welch_validate.py:313-327`）。

## 8. 发布工程、CI fail-closed 与新人上手

**worker 执行面**（`compileiq/worker.py`，1161 行）：五种后端——ManualWorker（`worker.py:49`）、MultiProcessWorker（默认本地进程池，`worker.py:83`）、IsoMultiProcessWorker（每任务一进程，`worker.py:356`）、RayWorker（分布式）、AsyncWorker。IsoWorker 的超时隔离是**管道 done_event + kill**：每任务 `iso_ctx.Event()`（`worker.py:512`），主循环 `time.monotonic()` 超时且 event 未置位即 `p.kill()` 转 INVALID_SCORE（`worker.py:539-546`）——注释直言常规进程池方案无法按需杀进程（`worker.py:500-502`）。目标函数异常一律被 `_function_wrapper` 捕获转 Score 失效（`worker.py:266-273`）而非炸掉搜索。

**发布工程**（`dev/`，21 脚本）：`compose_compileiq_wheel.py` 的硬约束是 "one distribution one platform tag"——前端与运行时 wheel 必须同平台同标签才能合并（`compose_wheel` 在 `compose_compileiq_wheel.py:236`，manylinux 标签归一 `_normalize_wheel_tag:64`，entry points 合并 `_parse_entry_points:177`）；`materialize_native_runtime.py` 在 16 格矩阵中按主机**唯一匹配**物化（`_select_runtime_artifact`，`materialize_native_runtime.py:97`），且 `_reject_lfs_pointer`（`materialize_native_runtime.py:29`）显式拒绝把 Git LFS 指针文件当真轮子。配套守卫：`verify_complete_wheel.py`、`check_public_artifacts.py`（16 格精确交叉积 + 私有标识符/构建机路径泄漏拒绝）、`check-linux-abi.py`（GLIBC/GLIBCXX 版本门）。16 格矩阵 = 4 Python（cp311-314）× 4 平台（linux x86_64/aarch64、macosx arm64、win amd64），每格一份 manifest json 记录三级溯源：outputs（filename/sha256/size）+ provenance（job_id/pipeline_id/source_commit）+ runtime 标签组。**注意 whl 是 Git LFS 指针**（`.gitattributes` filter=lfs），clone 后必须 `git lfs pull`。

**CI fail-closed**（`.github/workflows/ci.yml`，15 个 job）：从 `public-artifact-guard`（`ci.yml:21`）起步，经 lint/typecheck/unit/integration/fuzz/run-examples/validate-binary-ss 与四段 wheel 流水（smoke-test-wheel-matrix → build-and-smoke-test-wheel → compose-complete-wheels → complete-wheel-matrix → verify-and-test-complete-wheel），到 `ci-pass`（`ci.yml:631`）聚合收口。fail-closed 的精确实现：`ci-pass` 以 `if: always()` 运行、needs 列出其余 13 个 job，内联 Python 检查每个 need 的 result 非 success 即 fail（`ci.yml:653-671`）——**任何 job 缺席（未运行/被跳过）都会失败**，唯一显式例外是 PR 上允许跳过 `verify-and-test-complete-wheel`（`ALLOWED_SKIPS`，`ci.yml:647-651` 注释解释了原因）。`concurrency` 按 ref 取消旧跑（`ci.yml:15-17`）。nightly.yml 以 `CIQ_FUZZ_EXAMPLES=100` 深跑 Hypothesis（`nightly.yml:6`）。

**测试四分区**（`tests/`，48 文件）：unit 35 最快最厚（不需要原生引擎——用 scripted 纯 Python 引擎 fixture）；integration 在 scripted 引擎 + amber 真引擎（`requires_amber` marker，未装自动跳过，`pyproject.toml:115`）；fuzz 默认 `--ignore` 排除（`make test-fuzz` 显式跑）；compiler_ss 验证二进制搜索空间。最厚的 `tests/unit/test_backends.py`（2417 行、87 个测试函数）用密封 fake 引擎锁死 Search 门面契约，"search.pristine for restore" 模式确保被拒绝的操作零状态残留。

**新人上手路径**（综合 AGENTS.md 与图谱 tour）：

1. `make install-frontend`（无引擎，够 lint/typecheck/unit）→ `make validate` 快验；
2. 读 `examples/single_objective.py`（37 行）跑通最小闭环；再 `make install`（先 `git lfs pull`）装上 amber；
3. 按需深入：调 ptxas 看 `examples/compilers/ptxas_example/`；写目标函数前读 agent-skills 的 author-objective；XLA 用户从 `examples/compilers/xla_ciq_example/workflow.md` 的责任表入门；
4. 深水区文档：`docs/search_strategy.md`（435 行，原语语义最全）与 `docs/workers.md`（385 行，五种 worker）；
5. 改动 CI 相关行为时记住：加 job 必须同时挂进 `ci-pass` 的 needs，否则 fail-closed 设计会让流水直接红。

最后一条心法：这个仓库的每一层都在表达同一个工程哲学——**不确定就不放行**。tell 拒绝零残留、CI 任何 job 缺席即红、发布产物过泄漏守卫与 sha256 溯源、加速宣称过 Welch 检验门、物化运行时拒绝 LFS 指针。读懂这条主线，各层的防御式写法就都不再显得啰嗦。
