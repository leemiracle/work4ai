# 06 · nsys_jax 性能分析：nsys 包装器、嵌入式补丁与可插拔分析层

> 锚定 NVIDIA/JAX-Toolbox `.github/container/nsys_jax/`。

## 1. 角色定位

`nsys_jax` 是"Nsight Systems 之上的 JAX/XLA 专用探针层"：`nsys-jax` 包装 `nsys profile`，除 profile 外还抓 XLA protobuf dump、源码、元数据，后处理成 parquet 打成自包含 `.zip`——内附 `install.sh`，解包即可重建同版本环境。包内三层：`scripts/` 是 CLI、`nsys_jax/` 是分析库、`analyses/` 是数据文件。

## 2. 内部结构

**nsys_jax.py（875 行）**：`main()`（`.github/container/nsys_jax/nsys_jax/scripts/nsys_jax.py:102`）`parse_known_args` 剥包装器参数，以第一个 `--` 为界切成 nsys 参数与被测程序（`.github/container/nsys_jax/nsys_jax/scripts/nsys_jax.py:182-188`）。专属参数：`--nsys-jax-analysis[-arg]`、`--nsys-jax-condition`（L148-155，如 `$SLURM_LOCALID == 0`，L200-206）、`-o`（`%q{ENV}` 展开）。随后覆写四项 nsys 默认（L267-271）注入：`xla_dump_hlo_as_proto=true`（`.github/container/nsys_jax/nsys_jax/scripts/nsys_jax.py:307`）、`xla_dump_to=<tmp>`、`JAX_TRACEBACK_IN_LOCATIONS_LIMIT=-1`（L279）。跑完后 `ThreadPoolExecutor` 并行后处理（L794-872）：recipe/stats 转 parquet、元数据 sqlite、protos、源码内嵌（protoc 现编 xla_pb2 解析 .hlo.pb 取源文件名，`.github/container/nsys_jax/nsys_jax/scripts/nsys_jax.py:589-603`）；输出线程写 zip、30 秒心跳、哨兵 `None`（`.github/container/nsys_jax/nsys_jax/scripts/nsys_jax.py:789`）。`install_script_template` 把 commit 烧进 install.sh。

**scripts/utils.py（77 行）**：`analysis_recipe_path`（L32-46）装载——`importlib.resources.files("nsys_jax").joinpath("analyses", script + ".py")`（`.github/container/nsys_jax/nsys_jax/scripts/utils.py:38-40`）优先取内置分析，命中则 `as_file()`（zip 安装解临时文件），否则按文件系统路径；`execute_analysis_script`（L49-77）在唯一目录 `data/analysis/<名>-N` 运行。

**patch_nsys.py（1850 行 1 真函数）**：L5-1802 是四段嵌入字符串——2024.5.1/6.1（L5-27）、2024.6.2（L29-898）、2025.1.1-65（L899-1348）、2025.1.1-110（L1349-1802），≈1798 行是 diff。唯一函数 `main()`（`.github/container/nsys_jax/nsys_jax/scripts/patch_nsys.py:1805-1850`）：解析 `nsys --version`，match/case 选补丁（65/110 分叉 L1817-1828），再从 `nsys recipe --help` 正则抠出 nsys_recipe 目录，`git apply` 以 stdin 喂入补丁（`.github/container/nsys_jax/nsys_jax/scripts/patch_nsys.py:1844-1849`）。

**延迟 import 模式**：`protobuf_utils.ensure_compiled_protos_are_importable`（L60-79）先试 `from xla.service import hlo_pb2`（L70），ImportError 才把 protoc 绑定塞进 sys.path；`visualization.py` 的 IFrame import 也藏在函数体内——不拖 Jupyter/protoc。`Analysis.ipynb`：load_profiler_data → warmup 启发式 → module/thunk 三级索引与通信统计。

## 3. 外部连接（图谱佐证）

图谱边：nsys_jax.py `depends_on` Analysis.ipynb、`triggers` nsys-jax.yaml（仅本目录变更触发的非 GPU CI）；scripts/utils.py `depends_on` analyses/ 三 CLI。上游：`.github/container/Dockerfile.jax:150-152` COPY+install-nsys-jax.sh 把三个钩子写进 pip-tools；_ci.yaml 的 nsys 测试（`.github/workflows/_ci.yaml:430`/`:504`）8 GPU 真机采样。

## 4. 数据流

一次 `nsys-jax -o out.zip -- train.py`：解析参数 → 覆写 nsys/XLA 默认 → `nsys profile` 跑程序（sigterm 折叠为 0，L333-345）→ tmp 里产出 `out.nsys-rep` 与 `dump/*.hlo.pb` → 六路后处理（recipe/stats/元数据 parquet、protos、lzma pb、源码内嵌）→ 输出线程汇总成 `out.zip`（含 install.sh/notebook）→ 若给了 `--nsys-jax-analysis`，在镜像目录逐个跑分析、产物入包（L697），其非零退出码即包装器退出码（L706）。离线：解包 → `./install.sh` 按 commit 重装 → 读 parquet/解析 pb 重建四帧。

## 5. 设计决策

- **自包含归档**：代码+数据+安装脚本+钉扎一体打包，集群采样、笔记本分析。
- **`--` 切割+parse_known_args**：不复制 nsys 参数面，只拦四个参数，其余透传，升级零适配。
- **补丁以 diff 字符串内嵌**：nsys recipe 的 NVTX→GPU 投影对 JAX 多流不友好，与其 fork nsys 不如按版本贴补丁；97% 是数据不是代码。
- **延迟 import + protoc 现场编译**：最小环境下分析库仍可导入。

## 6. 新人提示（坑/勘误）

1. **patch_nsys.py 的版本矩阵硬编码**：只认 2024.5.1/6.1/6.2、2025.1.1(65|110)，其余 `patch_content = None` 静默跳过（L1829-1830）——升级 nsys 后投影可能悄悄退回未补丁行为。
2. **`--nsys-jax-condition` 的短路是特性**：条件不满足时程序照常跑、不采样且 `sys.exit(0)`（L350）——多 rank 只有 rank0 出 zip 是预期。
3. **expected_returncodes 折叠**（L333-345）：kill 码归零，"被 sigterm 杀"与"成功"不可区分。
4. **`xla_dump_to` 会被强占**：显式给的 dump 目录被覆写并打 WARNING（L313-314）；禁用 dump 则宣告 "things will break"（L317）。
5. **version.py 不在版本控制里**：镜像内从 artifact 注入（`.github/actions/build-container/action.yml:119-131`），本地由 scm 生成——两来源可能不同。
6. protobuf_utils 产物不落盘，每个新进程重编 proto。

---
自报：正文（python len 去空白）3,494 字；行号锚 33 处，其中全路径标准式 11 处。全部源码核实。
