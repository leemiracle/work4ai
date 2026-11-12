# ONBOARDING —— NVIDIA Audio2Face-3D Training Framework 新人导航

> 图谱基线：265 节点 / 524 边 / 14 层 / 15 步 tour，validator 0 issues，fingerprints 113 文件 @ commit 112c5eb3。
> 版本 1.0.1（VERSION.md），论文 arXiv 2508.16401，Apache-2.0。本文所有行号锚均从源码逐条核实。

## 1. 项目定位：A2F 生态的"训练侧"

Audio2Face-3D（A2F）是 NVIDIA 的音频驱动高保真面部动画技术：输入一段语音，输出皮肤/下颌/舌头/眼睛的全脸顶点动画（README.md:10）。它不是一个仓库，而是一个**对偶生态**：

- **推理侧**：闭源预训练模型 + Audio2Face-3D SDK 仓（运行时推理）+ Maya-ACE 插件仓（DCC 内消费，README.md:6）；
- **训练侧**：本仓——把 A2F 模型的**训练能力**开源，让用户用自己的角色/语言/风格数据训出定制模型，再交回 SDK/Maya-ACE 消费（README.md:12）。

理解这个定位后，仓内很多设计就顺理成章：训练收尾自动导出 ONNX（`train_diffusion.py:271-280` 的 `export_onnx` 延迟调用）、deploy 阶段产出 `network_info.json` + `network.onnx` + 情感库（`deploy.py:50/70/110`）——产物形态完全对齐推理侧消费者的接口，而不是训完即止的学术式代码。

双网络架构并存：**回归线**（`conv_w2v_autocorr.py`，JAS 架构逐音素回归）与**扩散线**（`diffusion_rnn.py`，RNN 主干+扩散去噪头，本仓主力）。两条线由配置 `NETWORK_TYPE` 切分（`config_train_regression_base.py:25` 硬编码 `'regression'`，`config_train_diffusion_base.py:25` 硬编码 `'diffusion'`），在 runners 层分流（`runners/run_train.py:43` 的 `utils.get_network_type_or_raise`）。

## 2. 架构总览：主机侧包装器 → 容器内 runners → audio2face 核心

仓根的 `run_train.py`/`run_preproc.py`/`run_deploy.py`/`run_inference.py` 四个脚本是用户敲的命令，但**它们不是真入口**——只做两件事（`run_train.py:31-40`）：

1. 用根目录 `utils.py` 的 `load_config`（L54）按 `configs/<name>/config_<type>.py` 惯例以 `importlib` 动态加载 Python 配置模块并转 dict（L42 `load_module`），配置名先过 `validate_identifier_or_exit`（L36）防路径注入；
2. 把配置 dict 序列化为 JSON，`subprocess` 调 `docker/run_*.sh`（L73 `run_process`）。

docker 启动器统一做三卷挂载（datasets/workspace/framework）+ `--gpus all --privileged` + 64MB 栈 ulimit，容器内 `cd /framework` 后执行 `python runners/run_<task>.py` 并转发 JSON 参数（`docker/run_train.sh:27,33-50`）。**真逻辑入口在 `runners/`**：`runners/run_train.py` 在容器内把 sys.path 指回仓根（L27），解析三个 JSON 修饰器后按网络类型分发到 `train_regression.run` 或 `train_diffusion.run`（L50-52）。每个 runner 还有 `*_debug` 变体（如 `runners/run_train_debug.py`），仅多了一步根目录 utils 的本地配置加载，供 VSCode launch.json 容器内调试。

容器内核心包 `audio2face/` 按图谱 14 层组织为：包装器层 → runners 层 → 训练主线层 → 网络与损失层 → 数据供给层 → 预处理层 → 几何缓存层 → charsiu 层 → MDM 层 → 工具层 → 配置基线层 → 配置样例层 → Docker 层 → 工程工具层。

## 3. 继承主线：Trainer ← InferenceEngine ← Converter

本仓最关键的复用设计是一条三级继承链（NOTES-DIGEST batch-1/batch-3 双批独立实证）：

```
train_diffusion.Trainer (train_diffusion.py:43)
    ↑ 继承
infer_diffusion.InferenceEngine (infer_diffusion.py:32, class InferenceEngine(Trainer))
    ↑ 继承
convert_onnx.Converter (convert_onnx.py:26, class Converter(InferenceEngine))
```

- **Trainer**（562 行）：`setup()`（L410）完成配置装载、数据集组装、`create_gaussian_diffusion`（L457-464）与 uniform schedule sampler（L465）、Adam+余弦退火（L467-478）；`run()`（L512）逐 epoch 训练，KeyboardInterrupt 可优雅收尾，结束后**无条件调用 `export_onnx`**（L271-276，函数体内延迟 import `convert_onnx`，防循环导入）。
- **InferenceEngine**：复用 Trainer 的 `compose_network_info`/`create_network` 等装配逻辑，`setup()`（L89）改为装载训练产物（`weights.pth` strict 加载，L122-124），按 `INFERENCE_MODE`（offline/streaming/streaming_stateless/offline_onnx）逐窗或整轨采样（`run()` L137，offline 分支 L180，streaming 分支 L200 起），导出 Maya cache 动画。
- **Converter**：复用 InferenceEngine 的模型装载，再用 `WrapModel`（L117）把整个扩散去噪循环包装为固定输入形状的单步 `forward`，`torch.onnx.export` 导出部署用 `network.onnx`（L108-115，opset 14，动态 batch 维）。

注意回归线是**并列的独立 Trainer**（`train_regression.py:38`），与扩散线无继承关系——继承链只存在于扩散线。`infer_diffusion.run()` L138 留有 TODO 自述："ONNX Converter depends on InferenceEngine.setup(), should be disentangled"——作者自己承认这条依赖耦合是技术债。

## 4. 数据供给与预处理：PCA 压缩是训练前提

**预处理三阶段**（`preproc.py:51` 的 `run()` 按 actor 编排）：**实际执行顺序是 skin → tongue → deploy**（`preproc.py:89-91` 依次调 `preproc_skin.run` → `preproc_tongue.run` → `preproc_deploy.run`）。deploy 是**汇聚收口阶段**——`preproc_deploy.py:176-197` 加载前两阶段产出的 `skin_pca_shapes.npz`/`tongue_pca_shapes.npz`，再计算均值几何与刚体变换参数，产出部署侧工件。

- **skin 阶段**（`preproc_skin.py:348` `run`）：`pruneSimilarPoses`（L53）剪枝相似姿态 → `selectDistinctPosePca`（L126）选区分性姿态 → `runPca`（L241）截断 PCA → `computePcaCoeffs`（L316）回算系数。方差阈值 `SKIN_PCA_VARIANCE_THRESHOLD=0.9995`（`config_preproc_base.py:51`）。
- **tongue 阶段**（`preproc_tongue.py:212` `run`）：`decoupleTransformDeformation`（L29）用刚体变换解耦舌头整体运动与局部形变，再 `computePcaVectors`（L84）求基。
- PCA 数学核心在 `geometry/pca.py:21` 的 `pca_truncated`（中心化 SVD），刚体对齐在 `geometry/xform.py:19` 的 `rigidXform`。

**训练数据集**（`dataset.py`，全仓最大 1047 行）：三路 Provider——`AudioProvider`（L38）/`PhonemeProvider`（L117）/`TargetProviderFullFace`（L381，继承 L164 抽象基类 `TargetProviderBase`）；样本单元 `Shot`（L520）/`Clip`（L627）各有 Muted 静音变体（`MutedShot` L582、`MutedClip` L707）专服务数据增广；两种 torch Dataset——`AnimationSequenceDataset`（L896）与 `AnimationSegmentDataset`（L969），共享 L748 的 `AnimationDatasetBase`。动画缓存读取统一走 `geometry/anim_cache.py:22` 的 `read_cache` 按扩展名分发（.npy 直读/.xml 走 Maya cache/.pc2 走点缓存），Maya 格式解析含字节序检测（`maya_cache.py:76` `_need_byte_swap`）。

## 5. vendored 双库：charsiu 与 MDM

`audio2face/deps/` 下内嵌两个第三方库（vendored，非 pip 依赖）：

- **charsiu**（音素对齐，arXiv 2110.03876）：上游有 6 个 aligner 家族（`Charsiu.py` L41 基类 + L109 forced/L241 attention/L327 chain_attention/L407 chain_forced/L485 predictive），但**本仓唯一实际消费入口是 `charsiu_predictive_aligner`**——`phoneme.py:68` 在 `PhonemeDetector.__init__` 函数体内延迟 import（控制 transformers 依赖加载时机，L84 `prepare_for_charsiu_import` 先抑制警告/重定向 HF 缓存）。预处理器是 en→zh 三级继承链：`CharsiuPreprocessor`（L49）→ `CharsiuPreprocessor_en`（L130，ARPabet 音素化）→ `CharsiuPreprocessor_zh`（L279，直接继承 en 而非基类，实现中文声韵母拆分 L452 `_separate_syllable`）。
- **motion_diffusion_model（MDM）**：扩散数学引擎，vendored 自 OpenAI improved-diffusion 经 Guy Tevet 的 motion-diffusion-model（版权头自述，`utils/misc.py` 头部注明 Modified from MDM 2022）。**只移植了 diffusion/ 子目录 + utils/misc.py**，没有移植 MDM 的训练脚本与数据管线。核心 `gaussian_diffusion.py`（1697 行）：三枚举选预测目标与变体（`ModelMeanType` L91/`ModelVarType` L101/`LossType` L115）、`q_sample` 前向加噪（L240）、`p_sample_loop` 反向去噪（L591）；`respace.py:31` 的 `space_timesteps` 支持时间步压缩（DDIM 加速）。本仓训练直接消费其 `training_losses` 与 `p_sample_loop`，经 `script_utils.py:27` 的 `create_gaussian_diffusion` 工厂构造，且固定 `predict_xstart=True`（直接预测 x0，`train_diffusion.py:457-463`）。

## 6. 配置三层体系与双 utils 甄别

**三层配置**是全仓最重要的约定（NOTES-DIGEST batch-4 实证"配置即 Python 模块"）：

1. **基线层** `audio2face/config_base/` 六个模块提供全部默认值（dataset/preproc/train_regression/train_diffusion/inference_regression/inference_diffusion）；
2. **修饰器层** `configs/<name>/` 四个同名文件按键覆盖，Actor 专属参数一律 `{actor: value}` 字典、缺失回退默认（`config_dataset_base.py:23` 的 `AUDIO_ROOT = {}` 空字典起步）；合并由 `audio2face/utils.py:61` 的 `dict_deep_update` + L83 `module_to_easy_dict` 完成；
3. **白名单层** `config_base/exposed.py:18` 的 `EXPOSED_CONFIG_PARAMS` 枚举 partial exposure 模式下允许覆盖的键——`utils.py:331` 的 `validate_cfg_mod` 在 `is_partial_exposure()`（L361，开源版硬编码 `return False`）为真时只对白名单校验，且此模式下训练结束**不保存 weights.pth**（`train_diffusion.py:531`）——这是 NVIDIA 保留的"数据集可开放、权重不出门"发布变体钩子。任何修饰器里的未知参数键都会报 `ValueError` 拒绝运行。

**双 utils 陷阱**：仓根 `utils.py`（78 行，主机侧：校验/加载配置/转发进程）与 `audio2face/utils.py`（401 行，容器内：EasyDict/深合并/校验器/日志）**同名不同物**。判别法： runners 与根包装器 `from utils import ...`（主机侧，`run_train.py:16`），核心包内 `from audio2face import utils`（`infer_diffusion.py:29`）。

## 7. Docker 容器化与工程支撑

单 stage Dockerfile 基于 `nvidia/cuda:12.8.1-devel-ubuntu22.04`（Dockerfile:1），系统依赖仅 clang/libtool-bin/libsndfile1 等少量包，Python 环境由 poetry 1.8.2 按 `docker/pyproject.toml` + poetry.lock 锁定——**torch 2.7.1+cu128 以 URL wheel 指定、不走 PyPI 名字解析**（NOTES-DIGEST batch-9）。六个 `run_*.sh` 启动器共享 `docker/utils.sh` 公共函数库：`read_env_file` source 仓根 `.env` 导出数据集/工作区路径、`wrap_and_escape_args` 做单引号转义、`compose_docker_hostname` 生成 `主机__用户__任务` 式容器名（`docker/run_train.sh:31-33`）。主机路径与容器路径的映射关系通过 `EXTERNAL_A2F_*` 三个环境变量透传，并由 `audio2face/utils.py` 的 `get_state_info`（L372 起）写入运行产物，日志收尾时回显映射（`preproc.py:92-94`、`train_diffusion.py:543-545`）。

工程支撑面：CONTRIBUTING 规定 black 120 列 + flake8（`.flake8` 忽略 E203/E402），`tools/format_code.py` 一键格式化；`tools/utils/render_markdown.py` 把 docs/ 的 markdown 渲染成 NVIDIA 风格 HTML；`.vscode/` 提供 launch.json 调试配置（配 runners `*_debug` 变体）。

## 8. 新人上手路径（建议顺序）

1. **跑通 quick start**（README.md:65 起）：clone → 配 `.env` → 从 HuggingFace 下载 claire 示例数据集 → `python run_preproc.py example-diffusion` → `run_train.py` → `run_deploy.py` → `run_inference.py`，先获得端到端体感（最小配置集 `configs/example-diffusion-min/` 只需两项路径即可起步）。
2. **读配置三层**：对照 `config_train_diffusion_base.py`（183 个有效行常量）与 `configs/example-diffusion/config_train.py` 全量样例，理解"基线默认 + 修饰器覆盖 + 白名单校验"。
3. **跟一次训练主线**：`runners/run_train.py` → `train_diffusion.py` 的 `setup`（L410）/`train_step`（L334）/`run`（L512），注意收尾 `export_onnx`。
4. **看继承链两端**：`infer_diffusion.py:32` 与 `convert_onnx.py:26/117`，体会"推理与导出都以训练器为底座"的复用设计。
5. **下探 vendored**：按需读 `gaussian_diffusion.py` 的枚举与 `p_sample_loop`、`Charsiu.py:485` 的 predictive aligner，其余上游功能全集可先跳过。
6. **动预处理**：改 `SKIN_PCA_VARIANCE_THRESHOLD` 等参数重跑 preproc，观察 PCA 基文件变化。
7. 需要产品级消费时，转入 Maya-ACE 插件仓（README.md:42-46 有专门文档 using_maya_ace.md）。

> 常见坑：①改配置必须同时留意基线层键名（校验器会拦未知键）；②预处理 run 名带时间戳（`preproc.py:57`），训练配置里的 `PREPROC_RUN_NAME_FULL` 必须回填实际产物目录名，占位值 `XXXXXX_XXXXXX` 会被显式拒绝（`train_diffusion.py:429-431`）；③推理/导出找不到权重时先确认 partial exposure 开关状态。
