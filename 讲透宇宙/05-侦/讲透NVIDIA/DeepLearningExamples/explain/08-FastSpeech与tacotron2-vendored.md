# 08 · FastSpeech 全链与 vendored tacotron2：教师对齐、YAML 继承树与 TRT 推理器

## 角色定位

`CUDA-Optimized/FastSpeech/` 是本仓少有的**端到端语音合成**示例：FastSpeech 谱预测模型（PyTorch 训练 + TensorRT 推理双形态）+ 整仓 vendored 的 tacotron2（教师模型）与 waveglow（声码器）两个上游目录，构成 text→mel→wav 完整管线。它的独特价值在于展示了"蒸馏对齐"工程范式：FastSpeech 本身是并行模型学不了时长，于是先用 Tacotron2 教师前向拿注意力矩阵、argmax 折算音素帧时长，再供 FastSpeech 的 duration predictor 监督训练。仓内还有一套自研的轻量超参框架（YAML parent_yaml 递归继承）与手写 TRT 网络构建器（populate_* 系列把 PyTorch 算子逐一翻译成 TensorRT network API）。

## 内部结构

包结构按职责切分。`fastspeech/model/` 两文件：`module.py` 是积木库——`FFTBlocks`（module.py:49）/`FFTBlock`（:124）/`MultiHeadAttention`（:182）/`ScaledDotProductAttention`（:262）/`LengthRegulator`（:396，时长展开核心）/`DurationPredictor`（:447）；`fastspeech.py:38` 的 `Fastspeech` 主模型组合 Phoneme-Side FFT、Length Regulator、Mel-Side FFT 三段。`fastspeech/trainer/` 两层：基类 `Trainer`（trainer.py:49，模板方法模式——`train()`（:131）驱动循环，子类覆写 `loss()`（:168）钩子），`FastspeechTrainer`（fastspeech_trainer.py:33）只实现 `loss()`（:45）注入 FastSpeech 特有的 mel mask 损失。推理侧三件：`inferencer/inferencer.py:39` 抽象基类（固化 eval/FP16/DataParallel/seed），`fastspeech_inferencer.py:32` 原生实现，`trt/` 下 TRT 实现的**三层类链**：`TRTInferencer`（trt_inferencer.py:46，engine 生命周期与插件加载）→ `FastSpeechTRTInferencer`（fastspeech_trt_inferencer.py:49，populate_network（:161）及 populate_fft/populate_slf_attn/populate_scaled_dot/populate_length_regulator（:595）等十余个翻译函数）→ `FastSpeechTRTMultiEngineInferencer`（fastspeech_trt_multi_engine_inferencer.py:50，`set_engine_and_context`（:106）按输入长度选最小可容纳 engine）。

超参框架是自研亮点：`fastspeech/utils/hparam.py` 里 `load_hparam`（:36，yaml.load_all 支持多文档）、`merge_dict`（:43，递归默认值合并：default 中 new 缺失的键补进去，父配置作 default 被子覆盖）、`Dotdict`（:53，点号访问 dict）、`Hparam.set_hparam`（:88）四件套。`get_hp` 内部函数沿 `parent_yaml` 字段递归上溯（:99-107），且显式禁止自引用父配置（:101-102 抛 'To set myself on parent_yaml is not allowed'）。九个 YAML 构成继承树，最深的一条是 **trt_fp16_multi_engine.yaml → trt_multi_engine.yaml → trt.yaml → infer.yaml → base.yaml 五层链**——叶配置只写 use_fp16 与四个 FP16 engine 路径，其余全靠链条继承。

## 外部连接

vendored `tacotron2/` 是 PyTorch 官方 Tacotron2 示例的**历史快照**：`distributed.py:83` 手写了一个 `class DistributedDataParallel(Module)`——用 `_flatten_dense_tensors`（:38）/`_unflatten_dense_tensors`（:54）压平梯度、`apply_gradient_allreduce`（:158）注册 backward hook（`allreduce_hook` :196）做梯度allreduce，这是 PyTorch 0.3 时代官方 DDP 尚未问世时的实现，NVIDIA 整目录原样保留未升级。`tacotron2/train.py:37` 导入它、:76 在 load_model 时包装。教师对齐脚本 `fastspeech/align_tacotron2.py`：`get_tacotron2`（:42）按 tacotron2.hparams 建教师、`get_duration`（:54）跑前向取注意力、`compute_duration`（:69）逐帧 argmax 累加折算时长——:71 有显式 Warning 注释"This code assumes the attention is monotonic"（依赖注意力单调性假设），`preprocess_aligns`（:83）以 batch_size=1 遍历 LJSpeech 逐条落 `*.align.npy`。跨包依赖走路径 hack：`inferencer/denoiser.py` 开头 `sys.path.append('tacotron2')` 后 `from stft import STFT`，把 vendored 目录当运行时库用。声码器侧 waveglow 同为 vendored，`generate.py` 端到端入口把三段计时（E2E/FastSpeech/WaveGlow）做成 TimeElapsed 上下文。

## 数据流

训练流：`fastspeech/train.py` 的 `train()`（:52 起，:167 fire.Fire 挂 CLI）→ Hparam 单例已在包导入时构造（`fastspeech/__init__.py:31`，import 即读盘的包级副作用）→ `LJSpeechDataset` 读 metadata.csv，mel 谱按需 librosa 现算或读 `.mel.npy` 缓存（ljspeech_dataset.py 尾部 fire 脚本 preprocess_mel 可离线预生成）、时长标签从 `.align.npy` 加载 → `PadDataLoader`（data_load.py，静态 pad_collate_fn 按批内最大维零填充）→ `FastspeechTrainer.train()` 循环。推理流：`infer.py` 的 `get_inferencer`（:130）按 `hp.trt_multi_engine`（:132）→ `hp.use_trt` 三态分派，TRT 分支全部**函数体内延迟 import**（:133、:146）避免无 TRT 环境的安装负担；多引擎模式下数据集开 `sort_by_length=True`（infer.py:103）+ `shuffle=False`（:110）按长度分桶减少 padding 浪费。TRT engine 构建：populate 系列把 checkpoint 权重逐层写进 TensorRT network，`__enter__/__exit__`（trt_inferencer.py:75/:78）管理 engine 与 context 生命周期；多引擎版按文本长度调 `set_engine_and_context` 切换 i32.o256/i64.o512/i96.o768/i128.o1024 四档。

## 设计决策

四个决策值得咀嚼。①**YAML 继承树 vs Hydra**：同期仓内其他项目已用 Hydra，FastSpeech 坚持自研 parent_yaml——胜在零依赖、心智直白（叶配置一眼看到与父的差异），代价是命令行覆盖靠 fire 收 **kwargs 再 merge，没有 Hydra 的插值与组合能力。图谱钉版其兼容性暗雷：`yaml.load_all` 未指定 Loader（hparam.py:36），PyYAML>=6 直接抛错。②**train.py:39-42 的 apex 守卫是坏味道样本**：`except ImportError: ImportError('Required to install apex.')` 只构造不 raise——缺 apex 时静默通过，直到训练深处才报 NameError，对照 Transformer-XL 的 warnings.warn 正确写法，可看出同仓不同代的防御性编程水平差。③**populate_* 手写 TRT 网络**而非 ONNX 导入：2019-2020 年 TRT 的 ONNX parser 对自定义算子（LengthRegulator 等需 CUDA 插件）支持弱，手写翻译换取完全控制，MANIFEST.in 打包 `fastspeech/trt/plugins/*.so` 印证插件二进制随包分发。④**vendored 不升级**：tacotron2 的手写 DDP 早已被官方取代，但作为"教师推理-only"用途保留原样——历史代码的价值冻结策略，避免为不参与训练的代码付迁移成本。

## 新人提示

入手顺序：先读 `hparams/base.yaml`（31 键按 Path/Audio/Text/Model 四组注释分节，是全仓参数语义字典）→ `model/module.py` 的 LengthRegulator 理解时长展开 → `trainer/trainer.py` 模板方法骨架 → `align_tacotron2.py` 理解数据从哪来。三个坑：① PyYAML 6+ 环境跑任何入口都会在 hparam 加载处崩，先降级 PyYAML<6 或给 load_all 补 Loader 参数；② `generate.py` 用 `librosa.output.write_wav`（librosa 0.8+ 已移除，需换 soundfile），README 性能段里 A100 数据被 HTML 注释整段注释掉（仅发布 V100/T4）——复现基准别找错硬件；③ 改 TRT 推理相关代码时注意 `trt_force_build=True` 会强制重建 engine 并覆盖 `trt_file_path`，多引擎模式的四档 engine 与 max_seq_len 列表长度必须对齐，错位在运行期才爆。
