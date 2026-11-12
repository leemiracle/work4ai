# Kumo-TS 新人上手指南

> 依据知识图谱（447 节点/724 边/10 层/12 步 tour，af74798b）撰写；行号锚均经源码核实。

## ① 项目定位与核心价值

Kumo-TS 是 NVIDIA 开源时序分析库，前身 NV-Tesseract（CHANGELOG.md:3），一个仓装两个独立 Python 包：

- **Kumo-Forecast**：预训练 transformer backbone 的 DataFrame-first 多变量预测，招牌是 DARR 上下文增强（kNN 记忆混合）与模型无关可解释性框架。
- **Kumo-Anomaly**：基于扩散重构的异常检测，配 NVIDIA 专有 SCS/MACS 置信序列自适应阈值；DPM-Solver 把采样步数从上千压到约 20 步。

核心价值：预测线零训练即可推理（HF 权重自动下载）；异常线无监督端到端（变换→残差→阈值→PDF）。

## ② 总体架构

仓根治理层 8 件+双包共用工程底座：Makefile 提供 lint/SPDX 目标，Ruff 配置唯一取自 Kumo-Forecast/pyproject.toml（Makefile:7）；CI 用 uv 在 Python 3.12 分环境装两包跑 CPU 单测。两包必须分环境安装，因都暴露顶层 sdk 模块（README.md:30）。

预测线四层：backbone.py（T5 编码器骨干，895 行单文件）→ model.py（装配工厂）→ dataset_longhorizon.py（数据集层）→ sdk/forecasting.py（3082 行门面，入口 forecasting.py:2545）；旁挂 interpretability.py 等 5 文件可解释性矩阵。

异常线四层：models/main_model.py（TSDiffuser 扩散管线）+diff_models.py（去噪网络）+utils/dpm_solver_pytorch.py（内嵌 ODE 采样器）→utils/ 预处理与阈值→sdk/inference_ad.py（推理主入口）+inference_worker.py（多卡 worker）→anomaly_analysis.py（编排）+reporting.py（PDF）。

## ③ 核心模块地图

**预测线**

- BackboneModel（backbone.py:445）：RevIN 归一化（backbone.py:208）+ Patching 词元化（backbone.py:319）+ T5 编码器（backbone.py:551）+ 四种任务头；可选跨通道注意力（backbone.py:344）。
- BackbonePipeline（backbone.py:718）混入 PyTorchModelHubMixin 支持 HF from_pretrained；build_model（model.py:37）按名加载可冻结。
- ForecastingConfig（forecasting.py:79，frozen dataclass 40+ 字段）是 v1.0.0 起唯一配置入口，有逐行注释 YAML 模板。
- 可解释性：explain_forecast（interpretability.py:1356）聚合潜轨迹稳定性/语义流/lag×horizon/线性替代四条归因轴，channel_flow 等四文件支撑。

**异常线**

- TSDiffuser_base（main_model.py:63）：calc_loss 含时间一致性辅助损失（main_model.py:251）；三种采样 impute/ddim/dpm_solver（main_model.py:533）。
- 推理双入口：单进程 inference_ad_tesseract2（inference_ad.py:1134）与多进程 _mp（inference_ad.py:1222）；残差在 evaluate_ad_tesseract2（inference_ad.py:852）。
- 编排 perform_anomaly_analysis_with_diffusion（anomaly_analysis.py:88）串推理→阈值→报告，SCS/MACS 按名分发（anomaly_analysis.py:218）；专有阈值算法在 utils/adaptive_threshold.py。

## ④ 数据流/控制流

**预测主链**：df → 列校验与数值列自动特征化（forecasting.py:2627）→ InferenceOnlyDataset → autoregressive_forecast（forecasting.py:629）：视界≤模型视界时单次前向（forecasting.py:653），否则每次产出 model_horizon 步滑窗外推 → inverse_transform 还原尺度（forecasting.py:2952）→ {target}_forecast 列；return_all_channels=True 逐通道输出（forecasting.py:2976），上限 512 步（forecasting.py:2580）。

**DARR 支链**：context_df → build_context_memory 建记忆库（forecasting.py:549）→ knn_forecast 检索近邻未来（forecasting.py:579，温度 softmax 加权）→ preds_hybrid=alpha*direct+(1-alpha)*knn（forecasting.py:2927）。

**异常主链**：df → 数值校验（anomaly_analysis.py:146）→ PCA/填充定维 → 掩码窗口 Dataset → 扩散重构（默认 DPM-Solver）→ 样本中位数（inference_ad.py:899）→ MAE 残差（inference_ad.py:936）→ SCS/MACS 阈值 → Anomaly+MAE 列（anomaly_analysis.py:232）→ 可选 PDF；单 GPU 自动退单进程（inference_ad.py:1270）。

## ⑤ 环境与运行方式

- 安装：cd Kumo-Forecast（或 Kumo-Anomaly）后 `uv sync --frozen --python 3.12`；两包分开装（Forecast Python≥3.10，Anomaly≥3.12 且 numpy<2）。
- 快跑：Kumo-Forecast/sdk/quick_example.py 演示标准/DARR/可解释；Kumo-Anomaly/examples/quick_example.py 注入合成异常跑管线。
- 微调：两包 examples/finetune_example.py，支持单机与 torchrun。
- 工程：`make lint`/`make spdx-check`；CI 在 .github/workflows/ci.yml（lint→SPDX→双包 CPU 单测）。
- 权重自动从 HF 下载（inference_ad.py:102），设备自动检测 cuda→mps→cpu（inference_ad.py:94）。

## ⑥ 设计决策与权衡

1. **单文件骨干+合成包注册**：895 行单文件+尾部 _register_submodules()（backbone.py:829）注入 sys.modules 合成包，零包结构即可 import，代价是 IDE 跳转失效。
2. **双包分环境**：顶层 sdk 撞名（README.md:30），牺牲同环境共存换取各自独立 lockfile 与依赖矩阵。
3. **跨通道注意力向后兼容**：use_cross_channel=True 只新增 cross_channel_attn.* 键（backbone.py:488），旧权重 strict=False 加载不破坏；SDK 从权重反推是否启用（forecasting.py:189）。
4. **DARR 默认近全 kNN**：alpha 默认 0.01（forecasting.py:90），默认 99% 走检索，记忆库质量主导预测质量。
5. **DPM-Solver 内嵌 vendor**：不受 PyPI 版本漂移影响，20 步采样（宣称 50-100x 加速）始终可用。
6. **归因并行走 fork-join 每卡一进程**（parallel.py），刻意不用 DataParallel/DDP——归因单元粗粒度独立。

## ⑦ 已知问题与勘误

1. **前身 NV-Tesseract 痕迹遍布**：CHANGELOG.md:3 明言 formerly NV-Tesseract，PR 链接仍指旧仓（CHANGELOG.md:11）；包元数据名仍是 tesseract_forecasting/ad-diffusion-oss（CHANGELOG.md:43）；环境变量 TESSERACT_BACKBONE_MODEL（model.py:13）同源。
2. **MOMENT 血统残留**：默认 backbone 名 AutonLab/MOMENT-1-large（model.py:13、forecasting.py:74、forecasting_inference_config.yaml:23），但 backbone.py:436 的 SUPPORTED_HUGGINGFACE_MODELS 只列 google/flan-t5-*，两处不一致；非跨通道检查点名 moment_head_512_6hr.pt（forecasting.py:72）。
3. **连字符目录+sys.path**：两子包目录名是非法 Python 标识符，仓内 18 处 sys.path.append 把子包根塞进路径后再 from models.xxx/sdk.xxx 解析（inference_ad.py:88、anomaly_analysis.py:16、main_model.py:57）；inference_ad.py:12 文档串还留着 '/path/to/Kumo-Anomaly' 占位写法。
4. **backbone.utils.utils 并无对应目录**：合成模块由 sys.modules.update（backbone.py:877）注入，control_randomness 实际定义在单文件内（backbone.py:94）。
5. **ETTh_4feature.csv 全仓零引用**：孤儿测试夹具（另两份 ETTh CSV 被 quick_example 实际使用）。
6. **dpm_solver_pytorch.py 是 MIT 内嵌**：文件头+third_party/dpm-solver/LICENSE+NOTICE 三重证据；NVIDIA 修改部分 Apache-2.0 双声明。
7. **NOTICE 实为法律声明**：图谱 scanner 曾误标为 code 节点，阅读时按文档处理。
8. **v1.0.0 两处 breaking**：perform_forecasting 收敛到 config= 参数（CHANGELOG.md:22）；AD 分析 config_path 改名 model_config_path。
9. **尺度契约**：训练/评测须向去噪器呈现一致归一化尺度（test_inference_scale_contract.py 锁定）。

## ⑧ 新人上手路线

1. 读根 README+CHANGELOG，建立"双子包、前身 NV-Tesseract、分环境安装"心智。
2. Forecast：跑 sdk/quick_example.py → 读 BackboneModel.__init__（backbone.py:445）→ 跟 perform_forecasting（forecasting.py:2545）主干。
3. Anomaly：跑 examples/quick_example.py → 读 main_model.py 文件头（三种采样对照）→ 跟 anomaly_analysis.py:88 一条链到 PDF。
4. 改动前先看测试：test_forecasting.py 69 用例是预测线行为规格；掩码合并/尺度契约/共享内存测试锁定异常线不变量。
5. 动骨干前先理 use_cross_channel 权重兼容语义；动依赖前先看两份 pyproject 与 CI 安装顺序。
