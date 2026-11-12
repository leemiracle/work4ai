# 01 · workflows 编排与配置体系：run.py 双线调度与 Hydra 配置分层

## 一、角色定位

`code/workflows/run.py`（867 行）是仓库总入口：捏合 Hydra 配置/校验/分布式/模型加载，按 `cfg.code` 劈成 `run_surface` 与 `run_color` 两条编排线。配套的 `conf/config_public.yaml`（88 行）是唯一面向用户的配置（README.md:18：两码族共用此入口），`code: surface`（config_public.yaml:31）一行切换到 `color`。`code/workflows/config_validator.py`（635 行）则是公共配置的"海关"：先拒收隐藏字段、再合并内部默认值、按 model registry 钉死架构——"窄门哲学"。

## 二、内部结构

run.py 顶部（run.py:16-29）只 import 训练主循环、两个 Factory 与校验器函数，其余全部按需延迟加载（见第五节）。`run` 被 `@hydra.main` 装饰（run.py:180），默认 config_name 只是占位（conf/ 下无 config.yaml），实际配置由 local_run.sh:56 的 `CONFIG_NAME:-config_public` 传入。主流程（run.py:182-204）：归一 code 名；color 配置若自带 test/train/val 节即绕过校验器（run.py:160-177），否则先 `validate_public_config` 再 `apply_public_defaults_and_model`；按码族分派，非法值直接报错。

`run_surface`（run.py:207）是任务分发器：train / inference / generate_stim_data / data / decoder_ablation 五种 `workflow.task`，历史名 `threshold` 会收到改名提示（run.py:211-214）。`run_color`（run.py:300）另有 threshold/sdr/chromobius_timing 三个"距离×p×basis"扫参任务（run.py:395-437）。`find_best_model`（run.py:628）挑 checkpoint：`PreDecoderModelMemory_` 前缀按 `split(".")[2]` 取最大 epoch（run.py:645），无编号则退回命名 .pt 取字母序末位。

config_validator 的核心是 `_base_hidden_defaults_dict()`（config_validator.py:115-272）：把历史 d9 配置的默认值**直接嵌入代码**（公共发布不随附内部配置文件），含 Lion 优化器、warmup 调度、每 epoch 2^26 shots、threshold 表 [5,7,9,11,13]。

## 三、外部连接

- **model/registry.py**：模型表在 registry.py:78-139——Model 1/2 四层 k=3（R=9）、Model 3 四层 k=5（R=17）、Model 4/5 六层 k=3（R=13）、Model "B" cascade R=13 硬编码（registry.py:132），~2.94M 参数，带完整 `model_overrides` 而非 num_filters。
- **conf/ 其余 9 个 yaml** 是内部实验配方，绕过公共校验器：surface 侧 `config_qec_decoder_r9_fp8.yaml`（Model 1 Fast R=9）与 `config_qec_decoder_r13_fp8.yaml`（Model 4 Accurate R=13）为论文复现配方；color 侧 d17 cascade 训练、d13 threshold 扫参、LR3e-4、model_5 推理四件套；另有历史全量配置 d9 yaml（隐藏默认值源头）、`config_local_test.yaml`（d=3 冒烟）与 `config_v3_timing_test.yaml`（d=5 计时）。
- **training/evaluation/export 三面**：train 直通 `train_main`；推理 surface 走 `evaluation.inference`、color 走 `evaluation.logical_error_rate_color`；模型加载优先读 `PREDECODER_SAFETENSORS_CHECKPOINT` 环境变量（run.py:724）。`PREDECODER_DECODE_MODE=pymatching_only` 时用 `torch.nn.Identity()` 充当模型（run.py:220-221），短路成纯 PyMatching 基线。

## 四、数据流

训练链：local_run.sh 设 CONFIG_NAME → Hydra 加载 → `validate_public_config` 查 model_id（1..5 或 B）与 distance/n_rounds 必填，拒收 train/val/test 节与越权 data 键（白名单仅 code_rotation/noise_model/三开关五键）→ `apply_public_defaults_and_model` 以 `OmegaConf.merge(base, cfg)` 合并，强写 fp16=False/tf32=True 不变量，按码族补默认（color 含 superdense/he_max_iterations=16 等）→ lr 硬编码：color 1e-5，surface 按 model_id 查表（config_validator.py:563-573）；batch_schedule 分档：model 3 与 cascade B 用 256→1024、其余 512→2048 → 训练时 distance=n_rounds=感受野 R（config_validator.py:616-618）。

推理链多一步模型解析：SafeTensors 元数据自报 model_id，color 专用 cascade "B" 撞上 surface 配置即 fail-fast（run.py:745-753）；fp16 权重自动置 enable_fp16=True（run.py:773-774）。

## 五、设计决策

1. **公共面刻意收窄 + fail-fast**：校验器宁可拒绝也不静默容忍，连 OmegaConf 会把字符串 "True" 当布尔的松散性都被 `isinstance` 检查拦下。
2. **延迟 import 按任务裁剪**：run.py 函数体内共 14 行 import、11 个模块（首见 run.py:216，末见 run.py:742），全落在 task 分支内——跑 surface 训练时 color 评测栈一行不加载。（图谱摘要记 9 条；盘上 grep 实证 14 行，以源码为准。）
3. **评估/训练窗口分离**：顶层 distance/n_rounds 只作评估目标，训练窗口锁死 R，模型不可能被训到超出感受野。
4. **fp8 语义勘误**：`*_fp8` 配置名里的 fp8 只指导出目标精度，训练全程 fp32——config_qec_decoder_r9_fp8.yaml:18 原文自述"fp8 in the name is for the intended export target"。按文件名猜精度会踩坑。
5. **旋转型别名**：公共面 O1..O4 映射内部 XV/XH/ZV/ZH（config_validator.py:37-43）。

## 六、新人提示

- 最快跑通：改 config_public.yaml 的 model_id/code/distance 再 `bash code/scripts/local_run.sh`；别往 yaml 加 train/test 节。
- 报错"Config field 'X' is not supported"时，去 `_base_hidden_defaults_dict` 查内部默认值。
- color 训练前需先做 augmented-DEM 预计算（config_public.yaml:30 注释）。
- Model 3 的 R=17 最重，显存紧张选 model 1/2；看 `find_best_model` 带 `[*]` 行确认实际加载的 checkpoint。

`字数|锚数`：3448|27（不计空格字符；带行号锚）
