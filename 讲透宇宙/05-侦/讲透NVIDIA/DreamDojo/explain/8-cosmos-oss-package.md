# 第 8 篇：packages/cosmos-oss——OSS 正本与根目录副本层的源头

## 一、角色定位

`packages/cosmos-oss/` 是 uv workspace 里的**发行正本**：根 `pyproject.toml:70-71` 声明 `[tool.uv.workspace] members = ["packages/*"]`，根发行名 cosmos-predict2 的运行依赖只有 `"cosmos-oss==0.1.0"`（`pyproject.toml:39`）加 workspace source——"根包薄壳 + cosmos-oss 承载全部依赖与工具链"。仓里的怪象由此解释：根目录的 `conftest.py`、`Dockerfile`、`bin/uv_lock.sh`、`scripts/train.py`、`scripts/check_environment.py`、`docker/nightly-entrypoint.sh`、`pyrefly.toml`、`pyrefly-src.toml` 与包内同名文件**全部字节级相同**（diff 八组零差异实证）——它们是包正本在根目录的镜像，让开发者站在仓根就能跑 `torchrun -m scripts.train` 与 pre-commit，PyPI 用户则拿到包内自洽版本。版本单点在 `packages/cosmos-oss/cosmos_oss/__about__.py:16`（`__version__ = "1.4.1"`）。

## 二、内部结构

**依赖与 CUDA extras（核心资产）**。`packages/cosmos-oss/pyproject.toml` 定义互斥 extras：`cu128_torch27`（torch 2.7.0 + flash-attn 2.7.3 + transformer-engine 2.2.0 + 整套 `nvidia-*-cu12==12.8.x` 锁定轮子）与 `cu130_torch29`（torch 2.9.0 + flash-attn 2.7.4.post1 + TE 2.8.0 + `nvidia-*-cu13` 轮子），两组头注释均为 "Match nvcr.io/nvidia/pytorch:25.10-py3"。两组都以 `"cosmos-cuda"` 哨兵打头（`pyproject.toml:97`、`:127`）。`[tool.uv] conflicts` 声明互斥，`[tool.uv.sources]` 把 decord/flash-attn/natten/TE/torch/torchvision/triton/xformers 按 extra 路由到两个 `explicit=true` 私有索引 `https://nvidia-cosmos.github.io/cosmos-dependencies/v1.2.0/{cu128_torch27,cu130_torch29}/simple`——uv 官方"optional-dependencies 切换加速器"范式的落地。根 pyproject 再做别名：`cu128 = ["cosmos-oss[cu128_torch27]"]`、`cu130 = ["cosmos-oss[cu130_torch29]"]`（`pyproject.toml:44-45`），`uv sync --extra cu128` 一条命令直达全套锁定 CUDA 栈。甄别一处陈旧：根 conflicts 仍列 cu129（`pyproject.toml:66`）而 extras 已无 cu129 定义，历史残留。

**训练入口链**。`cosmos_oss/scripts/train.py` 是 `torchrun -m scripts.train` 的真实末端：`init_environment()` 起 loguru/profiler/分布式（`train.py:64`），`--config` 指向 python 配置模块，`opts` 余位收 `path.key=value` 覆盖（`train.py:67-89`）；`SMOKE` 模式自动追加 `trainer.max_iter=2` 等三连覆盖（`train.py:93-96`）；launch 里 `config.validate()` + `freeze()`（`train.py:39-41`），`load_path` 以 `.pt` 结尾走 `create_model_from_consolidated_checkpoint_with_fsdp`，否则 `instantiate(config.model)`（`train.py:47-50`）。根 `scripts/train.py` 是 19 行薄转发；文件头有 `TOKENIZERS_PARALLELISM=false` setdefault（`train.py:19`）。

**运行时初始化与测试基建**。`cosmos_oss/init.py` 装 loguru 双 sink、输出目录、pyinstrument profiler、分布式 init/cleanup——各处的 `init_environment()/init_output_dir()` 来自这里。`conftest.py`（根/包同文）做分级 GPU 门控：`_ALLOWED_GPUS_BY_LEVEL = {0:[0,1], 1:[0,1,8], 2:[0,1,8]}`，`nvidia-smi --list-gpus` 数卡，配合 PYTEST_XDIST_WORKER 与 level/gpus/manual marker。`cosmos_oss/fixtures/script.py` 的 ScriptRunner 按 `NUM_GPUS` 拼 `--nproc_per_node` 起 torchrun 子进程，把 shell 脚本纳入 pytest。`.pytest.ini` 约定 `*_test.py` 命名；`.ruff.toml` 行宽 120、TID252 禁相对导入。

**工程化配置**。`.pre-commit-config.yaml`：addlicense 注入 `bin/license.txt` 的 Apache-2.0 头、markdown-toc、markdown-link-check（`.link-check-relative.json` 忽略全部 https 外链）；base 版钩子集是轻量基线（大文件 10MB 上限、forbid-submodules、gitleaks v8）。`.github/workflows/pre-commit.yml` 在 PR/push main 时 checkout(lfs)+setup-uv 跑 uvx pre-commit。`bin/uv_lock.sh` 对每个 pyproject 先 `uv lock --check` 再按需更新；`bin/uv_lock_script.sh` 识别 PEP 723 头为独立脚本锁依赖；`bin/release.sh`（根版带 `-euo pipefail`，`bin/release.sh:1`）做"无未提交变更→bump→commit+tag→build+publish"。

## 三、外部连接

向上：根包 cosmos-predict2 经 workspace 消费它；`bin/entrypoint.sh:22-24` 容器启动时按 `CUDA_NAME` 执行 `uv sync --locked --extra=${CUDA_NAME} || true`（失败不阻断）再 `exec "$@"`——哨兵校验（第 9 篇）发生在 sync 后首次 import。横向：`docs/setup.md` 给系统要求（Ampere+、驱动 570.124.06、CUDA 12.8.1、glibc 2.35、Python 3.10）；根 `install.sh` 在 `uv sync --extra=cu128 --python 3.10` 之外 uv pip 追加 tianshou/pytorch3d/piq/lightning/moviepy/torchcodec 等——piq 与 lightning 正是 LAM 研究版所需。`vqa/` 是独立 script-only 工程（`vqa/pyproject.toml`，package=false，依赖 vllm/qwen-vl-utils）：VQAEvaluator 逐条推理比对、VQACheck 的 must_pass 失败即中止、batch_runner 汇总成功率、CosmosReasonModel 组装视频 prompt。

## 四、数据流

以 `bash launch.sh 2b_480_640_gr1` 为例：torchrun 拉起 `-m scripts.train` → 根 `scripts/train.py` 转发 `cosmos_oss.scripts.train.main` → `init_environment` → import 配置模块 `cosmos_predict2/_src/predict2/action/configs/action_conditioned/config.py` 并 `make_config()`（触发 experiments 注册，见第 12 篇）→ `override` 吃掉 `experiment=...` → rank0 建输出目录 → freeze → instantiate 模型/数据 → trainer.train。nightly 镜像线是同源分叉：根 `docker/nightly.Dockerfile` 配 313 行 requirements，包内 `packages/cosmos-oss/docker/nightly.Dockerfile` 只装 66 行运行子集——同一源头按"开发镜像/用户镜像"演化，entrypoint 脚本本身字节相同。

## 五、设计决策

**正本+镜像副本**牺牲 DRY（八组文件双写同步）换取两种身份自洽：仓根服务开发者与 `-m` 路径解析，包内服务 PyPI；同步靠习惯而非机制，是最脆弱一环。**加速器选择交给 extras 而非安装期逻辑**：per-extra 私有索引让 GPU 轮子按 extra 精确分流，根层别名使用户无需理解内部命名。**版本对账三件套**：`__about__.py` × 3（oss/predict2/cuda 哨兵）必须同版本，hatch 消费同一文件，import 时双向校验，漏改立刻 RuntimeError。**测试分级**把无卡开发者与 8 卡 CI 纳入同一套 pytest 语义。

## 六、新人提示

改根目录任何"镜像文件"前先确认正本在包内：`diff conftest.py packages/cosmos-oss/conftest.py` 为空才是健康态，改完必须双侧同改。理解依赖地狱先读 `packages/cosmos-oss/pyproject.toml:96-215`（extras+conflicts+sources+index 四件套是 uv 多 CUDA 变体的教科书写法）。练习：① 干净环境跑 `just test-install`——先 `rm -f .cuda-name` 再 `uv sync -q`，import 应打印 "CUDA extra not installed..." 且被 `-` 前缀容忍为预期失败，这是哨兵机制负向验收；② 想 `bin/uv_lock_script.sh` 为何要单独存在（PEP 723 内联脚本不在 workspace 图内）。

> 甄别说明：八组字节级相同由 diff 实测；根 pyproject 依赖 `cosmos-oss==0.1.0` 与包内实际 1.4.1 的版本差异为源码实证——workspace source 使本地解析不受该 pin 影响，但发版时是否同步 bump 未追踪 git 历史验证；nightly-requirements 66/313 行计数为 wc 实测。
