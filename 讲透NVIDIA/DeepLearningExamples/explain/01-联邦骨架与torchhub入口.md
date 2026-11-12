# 01 联邦骨架与 torchhub 入口

## 角色定位

这个仓库顶层只有三件"全局资产"：`README.md`（L3 Introduction 起）是整个联邦的导航索引，`hubconf.py` 是唯一的跨域粘合代码，`.gitmodules` 是唯一的子模块锚点。除这三件之外，`CUDA-Optimized/`、`PyTorch/`、`TensorFlow/`、`TensorFlow2/`、`MxNet/`、`PaddlePaddle/`、`JAX/`、`Kaldi/`、`DGLPyTorch/`、`Tools/` 十个顶层目录各自是一个独立王国——目录间没有 import 关系、没有共享构建系统，甚至连代码风格都随上游框架各自漂移。图谱把这一层命名为"根入口与联邦骨架"（16 层中的第 1 层），它的本质是：**仓库不是工程，是发布物集合**。

`hubconf.py` 遵循 PyTorch Hub 的惯例——`torch.hub.load('NVIDIA/DeepLearningExamples', ...)` 克隆仓库后直接执行顶层 hubconf.py，顶层 import 即对外 API。它是全仓唯一"一个文件引用多个互不相干顶层目录"的地方。

## 内部结构

`README.md` 按 CV（L15）、NLP（L41）、推荐系统（L53）、语音识别（L66）、TTS（L72）、GNN（L80）、时序预测（L86）七大类以表格列出全部模型。表格列是固定的支持矩阵：框架、AMP、多卡、多节点、TensorRT、ONNX、Triton——这是读者判断"某个示例支不支持我的部署方式"的唯一权威口径。L94 Glossary 起解释 AMP/TF32/DLC 等术语，L91 NVIDIA support 一节明确各示例的容器版本对齐策略（NGC 容器，L6 起详述）。

`hubconf.py` 全文仅 35 行，结构是"import 组 + sys.path 注入"成对出现：

- L4-5：`from PyTorch.Detection.SSD.ssd import nvidia_ssd, nvidia_ssd_processing_utils`，随后 `sys.path.append` 注入 SSD 目录；
- L7-18：ConvNets 组，注册 resnet50/resnext101_32x4d/se_resnext101_32x4d/efficientnet b0·b4·widese_b0·widese_b4 等入口；L16 是别名变体（`nvidia_resneXt`），L18 注入 image_classification 目录；
- L20-21：GPUNet 的 `nvidia_gpunet`；
- L23-26：Tacotron2 组，`nvidia_tacotron2`/`nvidia_tts_utils`/`nvidia_waveglow` 三个符号都从 Tacotron2 目录导出（waveglow 声码器 vendored 在 Tacotron2 目录内，不是独立目录）；
- L28-31：HiFiGAN 组的 `nvidia_fastpitch`/`nvidia_textprocessing_utils`/`nvidia_hifigan`——注意 FastPitch 模型也放在 HiFiGAN 目录下；
- L33-34：TFT 时序预测的 `nvidia_tft`/`nvidia_tft_data_utils`。

`.gitmodules` 只有一条记录（L1-4）：`PyTorch/SpeechRecognition/Jasper/external/triton-inference-server`，锚定 NVIDIA/triton-inference-server 的 `r19.12` 分支——Jasper 语音识别示例对推理服务端的版本钉死。本克隆未执行 submodule init，该 external 目录磁盘上不存在。

## 外部连接

hubconf 的每个 import 目标都是一条对外暴露的边。**图谱 scope-cut 钉版**：本图谱分析口径为 PyTorch/LanguageModeling + Tools/PyTorch + CUDA-Optimized/FastSpeech + Kaldi + MxNet 少量（854 文件，commit 729963dd），hubconf.py 的 8 条 torchhub imports 指向裁出目录（SSD、ConvNets、GPUNet、Tacotron2、waveglow、HiFiGAN×2、TFT tft_torchhub），这些目录磁盘存在但图谱口径外，合并时诚实丢弃这 8 条边、不改 scope 边界——hubconf.py 在图谱里因此是一个"只入不出"的孤立入口节点。

`.gitmodules` 的 submodule 边同理不发向磁盘不存在的子模块内容。README 的表格则全是外链（GitHub 目录链接），图谱记其为 document 节点、向下 documents 各示例 README。

## 数据流

联邦骨架上的"数据流"是**发现流**而非数据流：用户从 README 支持矩阵定位候选模型 → 按图索骥进入对应顶层目录 → 目录内自带自己的 README/Dockerfile/脚本，与根完全解耦。torchhub 用户走另一条路：`torch.hub.load` 拉取仓库 → 执行 hubconf.py → 顶层 import 触发对应子包加载 → `sys.path.append`（hubconf.py:5/18/21/26/31/34）把各示例目录注入搜索路径，使得示例内部的相对 import（它们假设自己就是运行根）得以成立。这个 `sys.path[0]` 锚定的注入写法是理解"联邦仓如何被 hub 化"的钥匙：**每个示例目录都被写成了可独立运行的项目，hubconf 用路径注入而非改造来适配它们**。

## 设计决策

1. **联邦制而非平台化**。NVIDIA 选择每个示例自包含（各自 Dockerfile、各自依赖锁定），根目录只做索引。代价是 deployment_toolkit 这类公共件被复制了十份散布各处（见第 05 篇），版本随复制时点漂移；收益是任何示例可以独立演进、独立废弃而不牵动全局。
2. **hubconf 只覆盖"推理友好"模型**。注册的是 SSD/分类/TTS/时序预测这些有预训练权重可直接加载的入口；BERT/BART 等训练主线不在 hub 暴露面内——hub 面向的是应用者，训练示例面向复现者。
3. **单条 submodule 且钉老分支**。r19.12 是 Triton 推理服务器早期版本，Jasper 之后的新示例（含 BERT Triton）已改用 model-navigator/toolkit 复制件方案，submodule 这条机制事实上被放弃了——`.gitmodules` 是历史层位的化石。
4. **sys.path 注入是粘合层也是风险面**：hubconf.py:5 的 `sys.path[0]` 在不同加载方式（`torch.hub.load` 的 zip 模式 vs git clone）下取值不同，多目录同名模块会互相遮蔽——联邦仓能跑的前提是"一次只装一个域"。

## 新人提示

- 读仓先读 README 的表格再选目录，不要按目录名猜功能；`Tools/` 下不全是工具，TimeSeriesPredictionPlatform 是一个完整平台。
- hubconf.py 里找不到你要的模型 ≠ 仓里没有：它只注册了不到十个入口，BERT/BART/Transformer-XL 都要走目录内 README。
- 克隆后 `ls PyTorch/SpeechRecognition/Jasper/external/` 是空的属正常（未 init submodule）；现代 Triton 部署示例已不依赖它。
- 做图谱/静态分析时记住 scope 钉版：hubconf 的 8 条 imports 边是刻意丢弃的，不是分析遗漏；若扩 scope 应优先补 SSD/ConvNets 这类 torchhub 热路径。
