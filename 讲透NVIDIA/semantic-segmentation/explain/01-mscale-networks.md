# 01 · network/mscale.py + ocrnet.py — MscaleBase 双尺度族与 SOTA 的 MscaleOCR

> 源码：`network/mscale.py`（515 行）、`network/ocrnet.py`（342 行）、`network/ocr_utils.py`（158 行）· 图谱定位：8 层第 6 层「分割模型族层」· SOTA 配置 `ocrnet.HRNet_Mscale`（scripts/train_cityscapes_sota.yml 的 arch）由本篇三文件合装

## 一、角色定位：SOTA 曲线的两根支柱

README 结果表顶端的配置由两个机制叠加而成：**mscale 多尺度连续推理**（network/mscale.py 的 MscaleBase，尺度注意力让不同尺度的预测互补）与 **OCR 对象上下文**（network/ocr_utils.py 的三模块，把粗分割按区域聚合成对象表征再回注像素）。MscaleBase 是骨架、OCR 是头，二者在 network/ocrnet.py:158 的 MscaleOCR 合体，经 HRNet_Mscale 工厂（network/ocrnet.py:341）暴露给 get_net。train.py 的 SOTA 配置再叠 Mapillary 预训练迁移 + RMI 损失 + supervised_mscale_loss_wt 0.05（scripts/train_cityscapes_sota.yml:20-22）。

## 二、内部结构：递归多尺度骨架 + OCR 三模块

**MscaleBase**（network/mscale.py:41）的核心是**递归的多尺度前向**：`recurse_fuse_fwd`（network/mscale.py:53）从 scales 列表弹出当前尺度，非 1.0 时先 ResizeX 缩放输入（:69），子类实现的 `_fwd`（:50）出预测 p 与尺度注意力 attn，经 `scale_as` 对齐回原分辨率（:76），再与下一尺度递归结果融合——低分辨率（视野大）优先、高分辨率（细节足）补充。`nscale_fused_forward`（network/mscale.py:88）是 ASPP 融合变体入口（fuse_aspp 时 ASPP 特征先上行再逐尺度施加注意力）。三个派生头：**MscaleV3Plus**（network/mscale.py:232，DeepV3+ 头，工厂 DeepV3W38/DeepV3X71/DeepV3EffB4 等 :335-360）、**MscaleDeeper**（:363，output_stride=8 深骨干）、**MscaleBasic**（:450，Basic 头）。注意 mscale2.py（282 行）是同族二代重构，GSCNN 时代变体——两代并存，新实验应基于 mscale.py。

**OCR 三模块**（network/ocr_utils.py，分工三段）：`SpatialGather_Module`（:17）以粗分割 softmax 为权重，把像素特征按类别**聚合**成对象级表征；`ObjectAttentionBlock`（:49）做对象-像素交叉注意力（query=像素、key/value=对象）；`SpatialOCR_Module`（:122）组合二者输出对象上下文增强特征。ocrnet.py 据此装配四档：`OCR_block`（network/ocrnet.py:42）单块、`OCRNet`（:94，HRNet 骨干直配 OCR）、`OCRNetASPP`（:125，ASPP 变体）、**`MscaleOCR`（:158）双尺度+OCR 的 SOTA 合体**；工厂出口 HRNet（:337）与 HRNet_Mscale（:341）。

## 三、外部连接：get_net 动态装配与 HRNet trunk

上行：network/__init__.py 的 get_net（network/__init__.py:12）拿 args.arch_true 字符串 `network.ocrnet.HRNet_Mscale`，get_model 经 `importlib.import_module(module)`（network/__init__.py:51）取类实例化——零注册即插即用。trunk 全部来自 network/utils.py 的 get_trunk（network/utils.py:102）：HRNet 骨干在 network/hrnetv2.py（HighResolutionNet 全程高分辨率+HighResolutionModule 融合单元），W38 系则用 network/wider_resnet.py 的 WiderResNetA2（:270，独立实现，详见本系列 02 篇）。归一化全部走 mynn.Norm2d（network/mynn.py:18）。训练侧：mscale 的双尺度监督权重由 SOTA YAML 的 supervised_mscale_loss_wt 0.05 控制（scripts/train_cityscapes_sota.yml:22）；损失由 loss/utils.py:40 的 get_loss 派发 RMILoss（loss/rmi.py:33）。

## 四、数据流：一张 2048x1024 图的双尺度之旅

train.py 把 batch 喂给 wrap 后的 MscaleOCR → MscaleBase.recurse_fuse_fwd 取 scales=[0.5, 1.0]：先 0.5 尺度（ResizeX 半分辨率，network/mscale.py:69）→ HRNet trunk 出四级特征 → OCR 头出粗预测与 attn → scale_as 上采回 1x（:76）→ 递归进 1.0 尺度，其输出与上一尺度的注意力图融合（低尺度视野信息制导高尺度细节）→ 最终 logits 经 criterion（RMILoss 或 ImgWtLossSoftNLL，loss/utils.py:49/:57）出 loss；mscale 监督项以 0.05 权重并入。验证期 validate（train.py:536）走 eval_minibatch 滑窗拼接（utils/trnval_utils.py），大图分块推理。

## 五、设计决策：三个值得偷师的取舍

1. **递归而非并列的多尺度**：recurse_fuse_fwd（network/mscale.py:53）把"n 尺度融合"写成递归——尺度列表任意长（不只是 2），每个尺度的注意力都能被更粗尺度制导；并列式双分支（传统 FPNU-Net 系）表达不了这种级联优先级。
2. **粗分割当 OCR 的聚合权重**：SpatialGather（network/ocr_utils.py:17）复用网络自己的粗预测做 soft 聚类——无需额外监督即得对象表征，训练早期粗糙的软权重随主损失共同进化。
3. **骨架与头解耦的族谱**：MscaleBase 三个头（:232/:363/:450）× get_trunk 五族骨干（network/utils.py:102）自由组合，新增头或骨干互不干扰——这正是"架构实验场"能快速扫超参组合的结构原因。

## 六、新人提示

- 读码顺序：ocr_utils.py 三模块（158 行）→ ocrnet.py 的 MscaleOCR（:158 起）→ mscale.py 的 MscaleBase 与 recurse_fuse_fwd（:41/:53）——先懂头再懂骨架。
- 排错免数据：nullloader.py 全零占位 + `python train.py --local_rank 0 --arch network.ocrnet.HRNet_Mscale ...` 单 batch 前向，可验证装配（datasets/nullloader.py 设计初衷）。
- 复现 SOTA 记得两步走：train_mapillary.yml 预训练 → train_cityscapes_sota.yml 迁移（lr 1e-2/max_epoch 175，scripts/train_cityscapes_sota.yml:17-18），直接第二步没有预训练权重数字对不上 README。
- 改 BN 后端去 mynn.py 的 Norm2d（network/mynn.py:18，cfg.MODEL.BNFUNC）——**bn_helper.py 是死资产**（network/bn_helper.py:5 引用不存在的 sync_bn 目录）。
- 验证练习：给 MscaleV3Plus 的 scales 传 [1.0] 单尺度跑一遍再传 [0.5,1.0]，对比验证 mIoU——十行脚本体感尺度注意力的增益。
