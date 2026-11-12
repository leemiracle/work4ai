# 讲透 semantic-segmentation

> NVIDIA/semantic-segmentation —— PyTorch 语义分割训练框架：五族骨干（ResNet/SE-ResNeXt/WiderResNet/Xception/HRNet）× DeepLabV3+/Mscale 双尺度/OCR 对象上下文 × uniform 类均衡采样 + RMI 损失，Cityscapes/Mapillary SOTA 级实验场（runx 派发）。
> 本地仓：/usr-data/data2/repos/agent-repos/NVIDIA/semantic-segmentation（commit 7726b144）

## 状态（2026-11-10 ✅ 全链路完成）

| 步骤 | 状态 | 产物 |
|---|---|---|
| DeepWiki 全量 | ✅ | [deepwiki/](deepwiki/)（16 内容页 100%） |
| understand 中文图谱 | ✅ | 仓内 `.understand-anything/knowledge-graph.json`（**168 节点/325 边/8 层/12 步 tour**，validator 0 issues，fingerprints 57 文件基线@7726b144） |
| onboarding | ✅ | [onboarding/ONBOARDING.md](onboarding/ONBOARDING.md)（8667 不计空格字符，7 节，81 行号锚全验证通过） |
| explain 系列 | ✅ | [explain/](explain/) 3 篇（3542/3823/3815 字符，六节结构，锚 21+14+15 全验证） |

## explain 索引（3 篇）

| # | 篇 | 对象 |
|---|---|---|
| 01 | [mscale-networks.md](explain/01-mscale-networks.md) | MscaleBase 递归多尺度骨架+OCR 三模块+MscaleOCR SOTA 合体 |
| 02 | [backbones.md](explain/02-backbones.md) | 五族骨干+get_resnet 小写类陷阱+Norm2d BN 单点开关+bn_helper 死资产 |
| 03 | [data-sampling.md](explain/03-data-sampling.md) | uniform 类均衡采样（质心统计→epoch 重组→裁剪偏置）+BaseLoader 骨架 |

## 本轮沉淀的勘误（对 DeepWiki/图谱摘要/直觉的修正，均源码实证）

- **双死资产钉版**：network/bn_helper.py（11 行）torch 0.x 分支引用的 network/sync_bn 目录不存在（network/bn_helper.py:5，ls 实证）且全仓零消费者——改 BN 后端的真出口是 mynn.py 的 Norm2d（network/mynn.py:18 经 cfg.MODEL.BNFUNC）；utils/f_boundary.py（boundary F-score，源自 DAVIS）全仓无 import——训练用边界权重真源是 transforms/transforms.py:74 的 RelaxedBoundaryLossToTensor
- **WiderResNetA2 独立实现**：直接继承 nn.Module（network/wider_resnet.py:270），与 WiderResNet（:190）无继承关系，只共享 IdentityResidualBlock（:67）——别按"A2 是子类"读码
- **get_resnet 是类不是函数**：`class get_resnet(nn.Module)` 小写命名违规（network/utils.py:48），实为"按名构造并持有骨干"的包装类
- **get_loss 实为四分支非"六种损失"**：RMILoss/ImageBasedCE/ImgWtSoftNLL/CE（loss/utils.py:49-63）；MultiChannelBCEWithLogits（:234）与 EdgeWeightedCrossEntropyLoss2d（:319）定义了但工厂无分支、全仓零消费者——半死资产
- **Dockerfile 与 requirements.txt 两套并行清单**：镜像逐个 pip install（Dockerfile:3-13）且零 COPY requirements
- **联合变换 18 个类非 19 个**（transforms/joint_transforms.py 顶层 class 计数）
- **DistributedSampler 是函数体内延迟 import**（datasets/__init__.py:162/:185）——静态依赖图对此天然失明（图谱已按 AST 补边）

## 工程信息

- 流水线：DeepWiki MCP 通道 + understand 批分析 + layers/tour + finalize + 写作收官
- 字数口径：不计空格总字符；行号锚口径：仓内唯一 basename 自动展开后逐一验证（81/21/14/15 全过）
