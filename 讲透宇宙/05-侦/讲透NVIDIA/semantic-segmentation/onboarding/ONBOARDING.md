# semantic-segmentation 新人上手文档（ONBOARDING）

> 基于知识图谱（168 节点 / 325 边 / 8 层 / 12 步导览，commit `7726b144`，fingerprints 57 文件基线）生成，全部行号锚经源码逐行核实。
> 仓库：`/usr-data/data2/repos/agent-repos/NVIDIA/semantic-segmentation`（NVIDIA/semantic-segmentation，Cityscapes SOTA 级 PyTorch 分割训练仓）

## 1. 项目定位与一句话理解

**一句话**：NVIDIA 的 PyTorch 语义分割训练框架——把"架构实验场"做成了一条流水线：五族骨干（ResNet/SE-ResNeXt/WiderResNet/Xception/HRNet）× 多种分割头（DeepLabV3+/Mscale 双尺度/OCR 对象上下文）× 类均衡采样与 RMI 损失，在 Cityscapes/Mapillary 上追求小类 mIoU 与整体 SOTA。

两条主线藏在 scripts/ 的 YAML 名字里：**基线线** train_cityscapes.yml / train_cityscapes_deepv3.yml（DeepV3+ 族）；**SOTA 线** train_mapillary.yml（预训练第一步）→ train_cityscapes_sota.yml（Mapillary 预训练的 ocrnet.HRNet_Mscale 迁移 Cityscapes：175 epoch、RMI 损失、supervised_mscale_loss_wt 0.05，见 scripts/train_cityscapes_sota.yml:18/scripts/train_cityscapes_sota.yml:20/scripts/train_cityscapes_sota.yml:22）。README 的 SOTA 结果表对应后者。

新人最该先建立的心智模型：**config.py 是全仓单一配置源**（模块级 AttrDict，被 28 个模块 import），train.py 是唯一入口（main train.py:324 组装一切），scripts/*.yml 只是给这个入口的不同参数包——而一切实验经 runx 工具按 .runx 的作业模板（8 GPU、400G mem）派发。数据集目录结构必须照 PREPARE_DATASETS.md 摆好（leftImg8bit/gtFine+coarse、Mapillary v1.2），否则 datasets/ 的 Loader 全线报错。

## 2. 五分钟上手

环境（Dockerfile:1 基座 nvcr pytorch:19.10-py3）：

```bash
docker build -t semantic-segmentation .   # 镜像内源码装 apex（fp16 与 SyncBN 都靠它）
```

注意两套依赖清单的坑：requirements.txt 只有 5 行核心（torch/scikit-learn/h5py/dominate），而 **Dockerfile 里没有一行 COPY 它**——镜像内是逐个 `pip install` 的 14 个包（Dockerfile:3-13 起），改依赖要两边同步。

数据准备照 PREPARE_DATASETS.md 建 softlink；训练用 runx 派发：

```bash
python -m runx.runx scripts/train_cityscapes.yml          # 基线
python -m runx.runx scripts/train_mapillary.yml           # SOTA 第一步（预训练）
python -m runx.runx scripts/train_cityscapes_sota.yml     # SOTA 第二步（迁移）
```

train.py 同时是评测与可视化入口：eval_cityscapes.yml/eval_mapillary.yml 走滑窗验证（train.py:536 validate），dump_cityscapes.yml/dump_folder.yml 走 ImageDumper 预测转储（无标注文件夹的 demo 模式也支持）。

## 3. 架构总览（按 8 层图谱）

**L01 文档与运行环境层**（5 文件）：README/PREPARE_DATASETS.md/.runx/Dockerfile/requirements.txt。

**L02 训练入口与实验配置层**（10 文件）：config.py（`__C = AttrDict()` config.py:47 定义全量默认值，`assert_and_infer_cfg` config.py:205 在数据集间派生均值方差/类别数/crop 联动）+ train.py（check_termination train.py:303、main train.py:324、train train.py:465、validate train.py:536）+ 八份 runx YAML。

**L03 数据装载与类均衡采样层**（10 文件）：datasets/__init__.py 的 setup_loaders（datasets/__init__.py:45，train.py 取数唯一入口）+ base_loader.py 基类 + cityscapes.py（fine+coarse 联合、cities_cv_split cityscapes.py:41、coarse_cities cityscapes.py:92）+ mapillary.py（65 类 v1.2）+ uniform.py（类均衡核心）+ randaugment.py/sampler.py/nullloader.py（全零占位，免数据调网络）等。

**L04 联合变换与增强层**（3 文件）：joint_transforms.py（18 个 image-mask 同步变换类：Compose joint_transforms.py:37、RandomCrop joint_transforms.py:73、CenterCropPad joint_transforms.py:212、RandomSizeAndCrop joint_transforms.py:433、SlidingCrop joint_transforms.py:526、_ClassUniform joint_transforms.py:579）+ transforms.py（MaskToTensor transforms.py:70、RelaxedBoundaryLossToTensor transforms.py:74——训练用边界权重的真源）。

**L05 网络通用件与骨干族层**（8 文件）：network/__init__.py 的 get_net（network/__init__.py:12，importlib 按 args.arch_true 动态实例化 network/__init__.py:51）+ network/utils.py 共享积木（get_resnet network/utils.py:48、get_trunk network/utils.py:102、get_aspp network/utils.py:301、make_seg_head network/utils.py:320、make_attn_head network/utils.py:343）+ mynn.py（Norm2d mynn.py:18 经 cfg.MODEL.BNFUNC 单点切换 BN 后端）+ 五族骨干文件。

**L06 分割模型族层**（9 文件）：deepv3.py（DeepV3Plus deepv3.py:40 与七骨干工厂 deepv3.py:96-121、DeepV3 deepv3.py:126）、mscale.py（MscaleBase mscale.py:41、MscaleV3Plus mscale.py:232、MscaleDeeper mscale.py:363、MscaleBasic mscale.py:450）、mscale2.py（二代重构）、ocrnet.py + ocr_utils.py（SpatialGather_Module ocr_utils.py:17、ObjectAttentionBlock ocr_utils.py:49、SpatialOCR_Module ocr_utils.py:122）、basic.py/attnscale.py/deeper.py 变体 + **bn_helper.py 死资产**（见第 7 节）。

**L07 损失与优化层**（5 文件）：loss/utils.py 的 get_loss（loss/utils.py:40）+ rmi.py（RMILoss rmi.py:33）+ rmi_utils.py（map_get_pairs/log_det_by_cholesky）+ optimizer.py（get_optimizer/poly 调度/forgiving_state_restore）+ radam.py。

**L08 训练度量与可视化层**（7 文件）：utils/misc.py（fast_hist/eval_metrics/ImageDumper）+ trnval_utils.py（eval_minibatch 滑窗评估）+ results_page.py（dominate HTML 报告）+ my_data_parallel.py（可定制 DataParallel）+ attr_dict.py + **f_boundary.py 死资产**。

依赖方向：L02 消费 L03-L08 全部；L05 被 L06 全部消费；mynn.py fanIn=13 是网络侧被引用最深的底座。

## 4. 深潜一：网络族——MscaleBase 双尺度与五族骨干

**get_net 的注册机制**（network/__init__.py:12-51）：args.arch_true 形如 `network.ocrnet.HRNet_Mscale`，get_model 经 `importlib.import_module(module)` 动态取类（network/__init__.py:51）——新增架构零注册成本；is_gscnn_arch（network/__init__.py:26-30）特判 GSCNN 双分支；wrap_network_in_dataparallel（network/__init__.py:33）按 apex/DP 包装并行。

**MscaleBase 族**（network/mscale.py）：MscaleBase（network/mscale.py:41）是双尺度连续推理骨架——两个尺度分别前向、尺度注意力融合；派生三个头：MscaleV3Plus（network/mscale.py:232，DeepV3+ 头）→ 工厂 DeepV3W38/DeepV3X71 等（network/mscale.py:335-network/mscale.py:360）；MscaleDeeper（network/mscale.py:363，深骨干头）；MscaleBasic（network/mscale.py:450，Basic 头）。mscale2.py 是其第二代重构（282 行，GSCNN 时代变体）。SOTA 配置 `ocrnet.HRNet_Mscale` 在 ocrnet.py 的 MscaleOCR——OCR 上下文（ocr_utils.py 的 SpatialGather 按粗分割聚合对象表征 ocr_utils.py:17、ObjectAttentionBlock 对象-像素交叉注意力 ocr_utils.py:49、SpatialOCR_Module 组合 ocr_utils.py:122）叠加 mscale 双尺度，正是 train_cityscapes_sota.yml 的 arch。

**五族骨干与一处重要勘误**：Resnet.py（torchvision 风格 18-152，conv3x3 走 mynn 封装）、SEresnext.py（SEModule 通道注意力）、xception.py（SeparableConv2d 三段流）、hrnetv2.py（HighResolutionNet 全程高分辨率+HighResolutionModule 融合，OCRNet/Mscale 系的 trunk）、以及 **wider_resnet.py：WiderResNetA2（network/wider_resnet.py:270）直接继承 nn.Module——与 WiderResNet（network/wider_resnet.py:190）是两个独立实现，无继承关系**（容易被想当然认为 A2 是子类）；两者共享的积木是 IdentityResidualBlock（network/wider_resnet.py:67，预激活恒等残差）。骨干由 get_trunk 按名构造（network/utils.py:102）。

**get_resnet 小写类命名违规**（network/utils.py:48）：`class get_resnet(nn.Module)` 是 nn.Module 子类却用小写命名——它实际是"按 trunk 名构造并持有骨干"的**包装类**而非函数（看完构造器就明白：它内部建 trunk、暴露 trunk_channel etc）。读码时别被函数式命名骗了。

**BN 单点开关**：mynn.py 的 Norm2d（network/mynn.py:18-25）经 `getattr(cfg.MODEL, 'BNFUNC')` 取归一化构造器——BN/InPlaceABN/GN/SyncBN 的切换全仓只改 config 一处；initialize_weights（network/mynn.py:27）与 Upsample/Down2x/scale_as（network/mynn.py:43/network/mynn.py:60/network/mynn.py:70）是被所有网络文件 star 依赖的算子。

## 5. 深潜二：数据线——uniform 类均衡采样与联合变换

这是该仓在小类 mIoU 上的独门机制，**两个文件在两层配合**：

- **epoch 层**（datasets/uniform.py）：class_centroids 系列以网格 tile 统计每类像素的质心（class_centroids_image datasets/uniform.py:84、pooled/unpooled_class_centroids_all datasets/uniform.py:138/datasets/uniform.py:167、class_centroids_all datasets/uniform.py:189）；build_centroids（datasets/uniform.py:219，支持 cv 交叉验证后缀 datasets/uniform.py:240 与 coarse 粗标）产出质心表；build_epoch（datasets/uniform.py:278）按 min_samples/every_cnt 参数让**贫类样本优先、富类降频**地重组整个训练 epoch——把 Cityscapes 的长尾分布在 epoch 层面重新配平。
- **裁剪层**（transforms/joint_transforms.py:579 的 _ClassUniform）：裁剪窗口向含小类的质心区域偏移，与 epoch 层机制呼应。

**装载骨架**（datasets/__init__.py）：setup_loaders（datasets/__init__.py:45）构造训练/验证 loader；**分布式分支的 DistributedSampler 是函数体内延迟 import**（datasets/__init__.py:162/datasets/__init__.py:185——静态 import 图看不见，图谱已按 AST 补边），sampler.py 提供 pad=False/连续/permutation 三模式分片。base_loader.py 的 BaseLoader 把图像发现、joint transforms 应用、build_epoch 调度与可视化 dump 收进基类，具体 Loader 只覆写文件发现与掩码读取。cityscapes.py 的 cities_cv_split（cityscapes.py:41）支持按城市交叉验证切分，coarse_cities（cityscapes.py:92）发现 leftImg8bit_trainextra 粗标城市供 fine+coarse 联合训练；nullloader.py 返回全零占位——不碰真实数据就能单 batch 调网络结构，排错利器。

**变换侧**：joint_transforms.py 的 18 个类保证 image/mask 几何一致（SlidingCrop joint_transforms.py:526 是验证期滑窗）；transforms.py 的 RelaxedBoundaryLossToTensor（transforms/transforms.py:74）生成宽松边界张量——**训练用的边界权重真源**（注意不是 f_boundary.py，见第 7 节）；randaugment.py 以 (op, random magnitude) 二元组列表驱动 20 余个 PIL 级算子。

## 6. 深潜三：训练与损失线——config 中枢、OHEM 与 RMI

**config.py 联动**（config.py:47 起）：`__C.TRAIN`（config.py:71）/`__C.DATASET`（config.py:76）/`__C.MODEL`（config.py:119）分层组织默认值；assert_and_infer_cfg（config.py:205）在 Cityscapes/Mapillary 间派生均值方差、NUM_CLASSES、crop 与城市尺度——**换数据集时最该看的联动逻辑**。AttrDict 载体（utils/attr_dict.py）让 cfg.dataset 等价 cfg['dataset']。

**train.py 主循环**：main（train.py:324）组装 config/数据/网络/优化器/损失（含 snapshot 恢复与多卡 AMP）→ train（train.py:465）OHEM 前向反向 + poly 学习率 → validate（train.py:536）滑窗评估（eval_minibatch 含 flip 增强分支）→ check_termination（train.py:303）按 epoch/iteration 收尾。SOTA 配置关键超参在 scripts/train_cityscapes_sota.yml：lr 1e-2（scripts/train_cityscapes_sota.yml:17）、max_epoch 175（scripts/train_cityscapes_sota.yml:18）、rmi_loss true（scripts/train_cityscapes_sota.yml:20）、supervised_mscale_loss_wt 0.05（scripts/train_cityscapes_sota.yml:22）。

**损失工厂 get_loss**（loss/utils.py:40-68）实际只有**四个分支**：RMILoss（loss/utils.py:49，SOTA 点名）→ ImageBasedCrossEntropyLoss2d（loss/utils.py:53）→ ImgWtLossSoftNLL（loss/utils.py:57，边界加权软 NLL——边界权重来自第 5 节的 RelaxedBoundaryLossToTensor）→ CrossEntropyLoss2d（loss/utils.py:62 兜底）；验证 criterion 恒为 CrossEntropyLoss2d（loss/utils.py:66）。**勘误**：文件里还定义了 MultiChannelBCEWithLogits（loss/utils.py:234）与 EdgeWeightedCrossEntropyLoss2d（loss/utils.py:319）两个类，grep 实证全仓零消费者、工厂无分支——半死资产，别当可用选项。

**RMI 损失**（loss/rmi.py:33 RMILoss）：把每像素邻域向量视为区域样本，经 rmi_utils 的 map_get_pairs 构造联合分布、log_det_by_cholesky 用 Cholesky 分解的 log-det 估计预测与标签分布的互信息下界（rmi_utils.py 还附三个数值自测函数）。**优化侧**：optimizer.py 的 get_optimizer 出 SGD/RAdam + poly 调度；forgiving_state_restore 允许形状不匹配权重跳过并告警——跨架构迁移训练（Mapillary→Cityscapes 换头）靠它不炸。

## 7. 新人路线图与避坑

**阅读路线**：README + PREPARE_DATASETS.md → config.py 的 assert_and_infer_cfg（config.py:205）→ train.py main（train.py:324）→ network/__init__.py 的 get_net（network/__init__.py:12）→ 按主线挑 mscale.py（SOTA）或 deepv3.py（基线）→ uniform.py（数据侧独门）→ 遇到度量问题再看 utils/misc.py。

**双死资产勘误（最易踩的两个误区）**：

1. **network/bn_helper.py（11 行）已死**：torch 0.x 分支 `from .sync_bn.inplace_abn.bn import InPlaceABNSync`（network/bn_helper.py:5）引用的 network/sync_bn 目录**根本不存在**（ls 实证）——该分支必然 ImportError；grep 实证全仓零消费者。**改 BN 后端的正确入口是 mynn.py 的 Norm2d**（network/mynn.py:18 经 cfg.MODEL.BNFUNC 切换），不是 bn_helper。
2. **utils/f_boundary.py 已死**：boundary F-score 工具（源自 DAVIS 仓，utils/f_boundary.py:6 注释自证），grep 实证无任何文件 import 它。**训练用边界权重的真源是 transforms/transforms.py:74 的 RelaxedBoundaryLossToTensor**，评测走 fast_hist——"评测边界精度用 f_boundary"是错觉。

**其余勘误与陷阱**（全部源码实证）：

3. **WiderResNetA2 独立实现**：直接继承 nn.Module（network/wider_resnet.py:270），与 WiderResNet（network/wider_resnet.py:190）无继承关系——别按"A2 是 WiderResNet 子类"读代码。
4. **get_resnet 是类不是函数**：小写命名违反 Python 规范（network/utils.py:48），实际是"按名构造并持有骨干"的 nn.Module 包装类。
5. **Dockerfile 与 requirements.txt 两套并行清单**：镜像逐个 pip install（Dockerfile:3-13）且不 COPY requirements.txt——改依赖两边同步。
6. **联合变换是 18 个类不是 19 个**（transforms/joint_transforms.py 顶层 class 计数 18；图谱层摘要写 19）。
7. **get_loss 四分支非"六种损失"**：MultiChannelBCEWithLogits 与 EdgeWeightedCrossEntropyLoss2d 定义了但工厂无分支、全仓零消费者（loss/utils.py:234/loss/utils.py:319）。
8. datasets/__init__.py 的 DistributedSampler 是函数体内延迟 import（datasets/__init__.py:162/datasets/__init__.py:185）——静态依赖分析对它天然失明。
