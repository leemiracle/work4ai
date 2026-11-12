# Ising-Decoding 新人入门（ONBOARDING）

> 基于 understand-anything 知识图谱（1150 节点/2395 边/12 层/14 步 tour，fingerprints 210 文件@ea7c1bb3）生成；全部行号锚经源码核实。

## 1. 项目定位与一句话画像

**一句话**：NVIDIA 开源的量子纠错（QEC）AI 预解码器（pre-decoder）训练配方——神经网络跨时空读入 Stim 检测器综合征（detector syndromes），预测纠错以压低综合征密度，再交给标准全局解码器（surface code 用 PyMatching，color code 用 Chromobius）做最终逻辑判定。

- **为什么叫 pre-decoder**：它不替代全局解码器，而是先"消化"掉大部分错误信息，让后续匹配类解码器更快更准（LER 更低或延迟更低）。
- **两族码**：surface code 是主路径（HuggingFace 预训练模型三个：Surface Fast/Accurate、Color Fast）；color code 跑在 Torch + cuStabilizer 运行时上，多一步 augmented-DEM 预计算。
- **两篇论文**：surface 族 "Fast and accurate AI-based pre-decoders for surface codes"（arXiv:2604.12841，2026-04，见 `README.md:64`）；color 族同名 color codes 版（NVIDIA Research，2026-07）。
- **运行哲学**：两族码共用**单一用户配置** `conf/config_public.yaml` 与**单一 runner** `code/scripts/local_run.sh`，公开版刻意收敛入口。

## 2. 技术栈与运行形态

- **语言与框架**：Python 3.11/3.12/3.13（CI 矩阵 `.github/workflows/ci-gpu.yml:57`）；PyTorch 训练 + Stim（量子电路模拟/采样）+ PyMatching（surface 全局解码）+ Chromobius（color 全局解码）+ cuQuantum cuStabilizer（GPU 快稳态采样，`code/qec/dem_sampling.py:18`）+ CuPy（DLPack 零拷贝可选）。
- **配置系统**：Hydra/OmegaConf。`conf/` 下 10 个 yaml：`config_public.yaml` 是唯一用户入口，其余按码族/码距/fp8/本地测试分档（如 `config_color_accurate_d17.yaml` 为 8 节点大训练参考配方）。
- **双 CUDA 轨**：cu12/cu13 两套 requirements 并存；GPU CI 用 `torch-cuda: ["cu128","cu130"]` 矩阵（`.github/workflows/ci-gpu.yml:59`），并按轨选 requirements 文件（`.github/workflows/ci-gpu.yml:89`）。cu128 的 NCCL 2.28.9 多卡有 SIGSEGV 已知问题，cu13（NCCL 2.29.7）不受影响（`README.md:180`），train-cu13 即规避路径。
- **三种运行形态**：本地 `local_run.sh`（无 SLURM）；Docker 单阶段镜像（`Dockerfile:31` 唯一 `FROM`，`Dockerfile:65` 的 CMD 即安装+训练脚本）；SLURM 集群 `sbatch_train.sh`。大训练三件套：color generator superbatching / SyncBatchNorm / bf16-fp16 autocast；8 GPU 最优每 epoch 67M shots（`TRAINING.md:180`）。

## 3. 目录地图

| 目录 | 规模 | 职责 |
|---|---|---|
| `code/qec/`（顶层 62 文件） | 共享基座 | 噪声模型、DEM 采样、augmented-DEM 预计算 |
| `code/qec/surface_code/`（117） | 主路径 | Stim 记忆电路构建、同调等价校验、检测器编码 |
| `code/qec/color_code/`（70） | 平行路径 | 三色嵌合几何、色码电路、超密噪声参考 |
| `code/data/`（25） | 数据管线 | 三条 Torch 生成器、Stim datapipe、superbatch、种子布局 |
| `code/model/` + `code/training/`（74） | 模型与训练 | 637 行 predecoder、registry/factory、1869 行 train.py 主循环 |
| `code/evaluation/`（112） | 评测 | LER 两版、推理入口、失败分析（1311 行）、threshold/SDR/timing 结果脚本 |
| `code/workflows/` + `code/export/`（34） | 编排与导出 | 867 行 run.py 总入口、config_validator、safetensors/ONNX/CUDA-Q 导出 |
| `code/scripts/` + `code/benchmarks/`（96） | 外围 | 18 个集群/分层测试脚本、8 个基准脚本 |
| `code/tests/` + `cookbook/`（529） | 质量与上手 | 三层测试体系、两本 notebook |

`conf/` 全部 10 个 yaml 即配置层全部；`code: surface|color` 一个字段切换码族（`conf/config_public.yaml:31`）。

## 4. 核心架构链路

总链路：**config_public.yaml → local_run.sh → workflows/run.py → run_surface/run_color → 三生成器 → predecoder → LER 评测 → 导出**。

1. **入口编排**：`run.py:181` 的 `run(cfg)` 按码族分派到 `run_surface`（`code/workflows/run.py:207`）或 `run_color`（`code/workflows/run.py:300`）；color 路线另支持 threshold/sdr/chromobius_timing 等任务。
2. **配置防线**：`config_validator` 在起跑前拦截非法组合，并为 color 自动补齐专属电路/数据默认（`code/workflows/config_validator.py:298`）；内部字段（如 `precomputed_frames_dir`）对公开配置隐藏（`code/workflows/config_validator.py:446`）。
3. **数据装配**：`DatapipeFactory` 训练态返回 `(None, None)` 表示 on-the-fly——生成器由 train.py 直接创建（`code/data/factory.py:54`/`69`）；推理态才走 Stim datapipe。
4. **三生成器**（train.py 内直接实例化）：`MultiQCDataGeneratorTorch`（多码距混合，`code/training/train.py:1034`）、`ColorQCDataGeneratorTorch`（`code/training/train.py:1085`）、`QCDataGeneratorTorch`（surface，`code/training/train.py:1156`）。
5. **模型**：`ModelFactory.create_model`（`code/model/factory.py:25`）按配置从 registry 取模型规格；HF 上 Fast/Accurate 两档即出自这里。
6. **评测与导出**：LER 是最终度量；checkpoint 经 `checkpoint_to_safetensors.py`（`code/export/checkpoint_to_safetensors.py:16`）转 HF 格式，`generate_test_data.py` 产 CUDA-Q QEC 测试数据（detectors.bin 等，`code/export/generate_test_data.py:31`）。

## 5. 数据流（从量子电路到逻辑错误率）

```
Stim 记忆电路(按 25p 噪声模型构建)
  → detector error model (DEM, H/p/A 矩阵)
  → GPU 采样(cuStabilizer BitMatrixSampler / 纯 Torch 生成器)
  → SuperbatchBuffer 超批组批(确定性预取)
  → predecoder 前向(降综合征密度预测)
  → 全局解码器(PyMatching / Chromobius)
  → logical error rate (LER, 有/无预解码器对照)
```

- **噪声语义**：`NoiseModel` dataclass 显式枚举态制备/测量/idle/CNOT 共 22+3 个误差位置概率（`code/qec/noise_model.py:169`），支持 `from_single_p`（`code/qec/noise_model.py:266`）与 SI1000 构造；训练期可放大噪声（upscaling）。
- **augmented-DEM 预计算（color 专属）**：`precompute_dem_bundle_surface_code`（`code/qec/precompute_dem.py:821`）与 `precompute_dem_bundle_color_code`（`code/qec/precompute_dem.py:1844`）构建/缓存概率向量 bundle；color 生成器消费它（`code/data/generator_torch_color.py:20`），缺 bundle 时 train.py 报错并指引用 CLI 生成（`code/training/train.py:1083`）。
- **组批与可复现**：`SuperbatchBuffer`（`code/data/superbatch.py:27`）做确定性驻留超批缓冲；seed_layout 保证切分可复现。

## 6. 关键设计决策

1. **两码族单配置单 runner**：公开版只暴露一个配置文件一个脚本，color 专属默认由校验器补齐——surface/color 的电路、数据、解码器差异全部被 `code:` 一个开关吸收（`conf/config_public.yaml:31`）。
2. **延迟 import 全仓惯例**：run.py 独占 9 处函数体内延迟 import（如 `code/workflows/run.py:216` 的 inference、`:322` 的 color LER），按任务裁剪重依赖；更关键的是 `code/qec/precompute_dem.py:2191` 延迟 import `data.precompute_frames`，源码注释明示为规避循环依赖。
3. **augmented-DEM 预计算独立成步**：color 训练把"概率向量的采样与缓存"从训练循环中剥离成可复用 artifact（bundle 带元数据与内存护栏），训练只消费——代价是新手必须先跑预计算 CLI。
4. **三层测试 + mid 层无 `__init__.py` 天然隔离**：short（pre-merge）/mid（约 5-10 分钟 GPU）/long 三层；`code/tests/mid/` 刻意不放 `__init__.py`，short 层 `unittest discover` 天然收不到它（`code/tests/README_TEST_TIERS.md:26`），HE compile 测试即住 mid 层（`code/tests/README_TEST_TIERS.md:43`）。
5. **fp8 仅是导出精度**：fp8 命名的配置自述 "fp8 in the name is for the intended export target; training runs in fp32"（`conf/config_qec_decoder_r13_fp8.yaml:18`）——训练精度与部署精度解耦。
6. **契约测试锁架构**：`code/tests/test_color_accurate_model_contract.py:27` 硬编码 `EXPECTED_PARAMS = 25_397_764` 并硬读 `config_color_accurate_d17.yaml`，参数量/stem 类型/块数/SiLU 全部断言——改模型必改契约。

## 7. 新人上手路径（按 tour 14 步）

1. 读 `README.md` + `TRAINING.md` 把握两族码与工作流全貌。
2. 看三条 Actions 流水线与 Dockerfile，知道提交会被什么验证。
3. 打开 `conf/config_public.yaml`，理解单入口与 `code:` 开关。
4. 进 `code/workflows/run.py` 看总编排与 config_validator 防线。
5. 读 `code/qec/noise_model.py` + `dem_sampling.py` 打好噪声与采样地基。
6. 看 surface code 记忆电路构建与 1275 行同调等价校验（主路径）。
7. 看 color code 三色几何、1497 行同调等价参考与超密噪声。
8. 弄清训练数据两条路线（Stim datapipe vs 纯 Torch 生成器）与 superbatch。
9. 读 637 行 `code/model/predecoder.py` 与 registry/factory（`code/model/predecoder.py:250` 起的模型族、`:115` 的 CascadeBottleneckBlock3D）。
10. 进 1869 行 `code/training/train.py` 主循环（`code/training/train.py:732` 的 main），看精度/分布式/优化器装配。
11. 读 `logical_error_rate.py` 两版理解 LER 如何统计（`code/evaluation/logical_error_rate.py:122` 的 decode_mode）。
12. 对照 Chromobius 基线（`code/evaluation/logical_error_rate_color.py:40` 起 import）与 threshold/SDR/timing 结果脚本、1311 行失败分析。
13. 跑通导出链：checkpoint→safetensors→ONNX/TensorRT→CUDA-Q 测试数据。
14. 收尾上外围：cluster/sbatch 集群脚本、`run_tests_tier.sh` 分层测试、cookbook notebook 动手复现。

## 8. 常见坑与勘误（流水线实证）

- **语义错位**：`triangular_color_code_circuit` 是 color code 电路构建器，却物理住在 surface_code 目录（`code/qec/surface_code/memory_circuit.py:1236`），按目录找色码会走错；色码本体在 `code/qec/color_code/color_code.py:74` 的 `ColorCode`。
- **名不副实**：`code/data/precompute_frames.py` 的 legacy 帧预计算 CLI 已被 `qec.precompute_dem` 的 Torch augmented-DEM 管线取代，docstring 自述只剩 config loader（`code/data/precompute_frames.py:18`）。
- **stdlib 撞名**：`code/training/logging.py:21` 的 `import logging` 是标准库不是自引用，工具误报可忽略。
- **死代码陷阱**：`code/training/utils.py:177` 的 `dict_to_device` 藏在字符串字面量里（注释旧版），真身在 `:186`——搜定义会搜到两个。
- **唯一继承链**：`MemoryCircuit(Circuit)`（`code/qec/surface_code/memory_circuit.py:794`，父类 `:332`）是全仓唯一类继承链；`code/qec/color_code/homological_equivalence.py:1413` 的 `ColorCode` import 在 `__main__` 自测块内，不是库依赖。
- **双参数量口径并存**：registry 模型 B ~2.94M（`code/model/registry.py:122`，mock/论文口径）vs d17 color 契约 25,397,764（`code/tests/test_color_accurate_model_contract.py:27`）——不同配置不同模型，非矛盾。
- **孤儿与 CI 外脚本**：`test_training_progress.py` 的被测脚本不在仓内，skipTest 守卫休眠（`code/tests/test_training_progress.py:23`）；`code/tests/measure_d9_ler.py:20` 自述 "Not run by CI"（LER 阈值校准用）。
- **本地脚本环境变量纪律**：`local_run.sh` 刻意忽略 `BASE_OUTPUT_DIR`/`LOG_BASE_DIR`，只认 `PREDECODER_` 前缀（`code/scripts/local_run.sh:79`）；`offline_smoketest.sh` 默认权重 `models/*.pt` 仓内不存在，脚本防御跳过（`code/scripts/offline_smoketest.sh:72`）。
- **evaluation 三胞胎**：threshold/SDR/chromobius_timing 三个结果脚本同构（fcntl 锁+normalize+merge+append：`code/evaluation/color_threshold_results.py:62`/`:212`、`code/evaluation/color_sdr_results.py:176`、`code/evaluation/color_chromobius_timing_results.py:226`），改一个记得看其余两个。
- **TRT 契约测试是镜像**：`test_tensorrt_fallback.py` 不导入 `logical_error_rate.py`，只镜像其 TensorRT 导入语义做契约断言——别在这里找运行时行为。
- **CI 看不见的 mid 层**：short 层 discover 收不到 mid 层测试（无 `__init__.py`，设计使然），跑全量用 `run_tests_tier.sh mid`。

---

元数据：字数（不计空格）= 7959；锚 52 个（全部源码核实）；8 节；图谱 1150n/2395e/12L/14tour，commit ea7c1bb3。
