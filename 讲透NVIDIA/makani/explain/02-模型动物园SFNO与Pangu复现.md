# 02 · 模型动物园：FourCastNet3 旗舰与 SFNO/Pangu 复现

## 角色定位

`makani/models/networks/` 十种预报网络构成 makani 的架构动物园：旗舰 FourCastNet3（论文 arXiv 2507.12144）、FCN2/HENS 主力 SFNO（2306.03838/2408.03100）、FCN1 时代的 AFNO×2（2202.11214）、Pangu-Weather 复现、ViT/SNO 基线与 debug 小网络。对照阅读两条主线：球面几何感知（SFNO 谱方法 vs FCN3 Disco 连续表示）与"复现而非发明"（pangu.py 是对华为 Pangu-Weather 的独立实现）。

## 内部结构

**fourcastnet3.py（1186 行，nettype FCN3）**：Disco 连续表示编解码——fourcastnet3.py:108 `DiscreteContinuousEncoder` / fourcastnet3.py:248 `DiscreteContinuousDecoder`，截止半径由网格与核形推导 fourcastnet3.py:48 `_compute_cutoff_radius`；fourcastnet3.py:428 `NeuralOperatorBlock` 内嵌 disco 卷积（:518-542，`fused_disco` 融合开关 :173/:197）；主网络 fourcastnet3.py:650 `AtmoSphericNeuralOperatorNet` 把大气/表面/辅量三路 embed（atmo/surf/aux_embed_dim，fourcastnet3.yaml:25-27）分别升维再进算子块栈，层间穿插 SFNO 块（`sfno_block_frequency`:5）；fourcastnet3.py:1146 `AtmoSphericNeuralOperatorNetMetaData` 声明模型元信息。3.1 变体在 fourcastnet3_1.py（1168 行）。README.md:243 提示：inductor 编译下 DISCO 卷积尺寸多样会撞 recompile 上限，makani 把 torch 默认 8 提到 32。

**sfnonet.py（1088 行）**：sfnonet.py:52 `SpectralFilterLayer`（球面谐波域滤波）+ sfnonet.py:188 `NeuralOperatorBlock` + 主网络 sfnonet.py:438 `SphericalFourierNeuralOperatorNet`——FourCastNet2 与 HENS 共用主力；sfnonet.py:1022 `FourierNeuralOperatorNet` 直接继承 SFNO（欧氏 FNO 复用球面实现的通道）。配置 sfnonet.yaml 与 icml_models/（HENS 论文库）。

**pangu.py（1160 行，3D Earth Attention 复现）**：pangu.py:40 `get_earth_position_index` 生成 (press,lat,lon) 3D 窗口的位置索引，pangu.py:341 `EarthAttention3D` 实现 3D 窗口注意力 + pangu.py:382 `earth_position_bias_table`（trunc_normal 初始化 pangu.py:398，索引注册为 buffer :391）、`add_earth_pos_bias`:425；pangu_onnx.py（147 行）只做 ONNX 封装对照。

**其余**：afnonet.py（621 行）/afnonet_v2.py（599 行）= FCN1 自适应傅里叶神经算子；vit.py（467 行）与 snonet.py（908 行）基线；debug.py（59 行）CI 冒烟小网络。

**公共层 common/**：layers.py（1232 行 13 类：DropPath/LayerScale/PatchEmbed-Recovery 2D3D/EncoderDecoder/MLP/上下采样）供全部网络共享；spectral_convolution.py（516 行）SpectralConv 与球谐域 SpectralAttention；fft.py（464 行）单进程 FFT 家族。

## 外部连接

**组装三级台阶**（网络→可训练对象）：model_registry.py:147 `get_model` 按 nettype 发现构造（全部训练入口走它）→ model_package.py:99 `ModelWrapper`（569 行）封装网络+预处理器+归一化为可保存/加载模型包 → stepper.py:52 `StepWrapper` 包装多步 rollout（含 checkpoint 安全断言）。生成式线在其上叠 `stochastic_interpolant.py`（562 行）+ noise.py（1239 行球面随机场）。

## 数据流

输入场 (B,C,721,1440) → Preprocessor2D 装配（history 展平/噪声/归一化，preprocessor.py:317/:416）→ FCN3：三路 patch embed→Disco 编码到连续表示→NO 块栈（disco 卷积×SFNO 块交替）→Disco 解码回网格→输出场；SFNO：patch embed→谱域滤波块栈→recovery；Pangu：3D 嵌入→Earth-Attention transformer 层→金字塔拆解。输出经 StepWrapper 喂自回归 rollout。

## 设计决策

1. **连续表示而非网格卷积**：FCN3 的 Disco 把离散网格映到连续函数空间，网格无关性与分辨率伸缩是核心卖点（encoder/decoder 成对出现 :108/:248）。
2. **混合块节奏**：`sfno_block_frequency` 每 N 层插一个 SFNO 块，纯 NO 块与谱块交替（fourcastnet3.yaml:31）——谱正则化混入连续算子栈。
3. **复现件当一等公民维护**：pangu.py 1160 行完整复现 + ONNX 对照封装，用于论文对照基线而非生产。
4. **元数据类随网络走**：每个网络配 `*MetaData`（fourcastnet3.py:1146、sfnonet.py:981 `SphericalFourierNeuralOperatorNetMetaData`）供 registry/模型包消费。
5. **debug.py 是 CI 契约**：59 行小网络让工作流能在无 GPU 环境验证整条管线。

## 新人提示

读 FCN3 先看 yaml 的三层 embed_dim（atmo 45/surf 56/aux 36）再对应 :650 主网络的构造；SFNO 与 FNO 是继承关系不是两份代码（sfnonet.py:1022）；HENS 配置在 config/icml_models 而非 sfnonet.yaml 独档；inductor 报 recompile 警告先读 README.md:243 再调 `--jit_mode`；改网络输出记得同步 `*MetaData` 与模型包测试。
