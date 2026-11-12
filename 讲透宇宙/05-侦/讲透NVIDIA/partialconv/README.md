# 讲透 partialconv

> NVIDIA/partialconv —— 部分卷积（Partial Convolution）算子官方实现：nn.Conv2d 兼容的"按有效像素归一化"层，padding 替代 + 图像 inpainting 双用途（ECCV 2018 arXiv:1804.07723 + 技术报告 arXiv:1811.11718）。
> 本地仓：/usr-data/data2/repos/agent-repos/NVIDIA/partialconv（commit 610d373f，2018 年代码，8 个源文件）

## 状态（2026-11-10 ✅ 全链路完成）

| 步骤 | 状态 | 产物 |
|---|---|---|
| DeepWiki 全量 | ✅ | [deepwiki/](deepwiki)（11 内容页 100%） |
| understand 中文图谱 | ✅ | 仓内 `.understand-anything/knowledge-graph.json`（**41 节点/80 边/4 层/5 步 tour**，validator 0 issues，fingerprints 8 文件基线@610d373f） |
| onboarding | ✅ | [onboarding/ONBOARDING.md](onboarding/ONBOARDING.md)（8824 不计空格字符，6 节，96 行号锚全验证通过） |
| explain 系列 | ✅ | [explain/](explain) 2 篇（3244/3719 字符，六节结构，锚 11+19 全验证） |

## explain 索引（2 篇）

| # | 篇 | 对象 |
|---|---|---|
| 01 | [partialconv2d.md](explain/01-partialconv2d.md) | PartialConv2d：mask 卷积更新+比例归一化+kwargs.pop 签名兼容 |
| 02 | [training-pipeline.md](explain/02-training-pipeline.md) | main.py 双字典选模型+pd_resnet/pd_vgg 骨干改造+ImageNet 实验线 |

## 本轮沉淀的勘误（对 DeepWiki/图谱摘要/直觉的修正，均源码实证）

- **骨干 forward 不传 mask**：图谱摘要称 BasicBlock/PDResNet"前向逐层传递 (x, mask) 二元组"——实际 `def forward(self, x)` 单参数（models/pd_resnet.py:57、:156；models/pd_vgg.py:65）；分类线里 mask 是算子内部自建的全 1 静默通道（models/partialconv2d.py:52-57）
- **pd 系 `--pretrained` 是坏的**：model_urls 全空串（models/pd_resnet.py:30-36、models/pd_vgg.py:28-36），`model_zoo.load_url('')` 必炸；torchvision 真实 URL 被注释在 pd_vgg.py:37-44，真权重走 README.MD:102-105 的 Dropbox 链接
- **main.py 没有 AMP**：图谱 hub 摘要"Autocaster 包裹前向+GradScaler"系幻觉——main.py:291-347 是朴素 fp32 循环，全文无 apex/autocast/GradScaler（grep 实证唯一 "amp" 命中是 DistributedSampler 子串）；README.MD:48-77 的 AMP（apex）指引只适用于 inpainting 训练侧
- **VGG16Partial 的 "Partial" ≠ 部分卷积**：截取 VGG16 前若干层的感知损失特征提取器，卷积是标准 nn.Conv2d（models/loss.py:112）、加载 torchvision 官方权重（loss.py:128-132）且冻结（loss.py:158-159），与 partialconv2d.py 零继承关系
- **--dist-url 默认是 NVIDIA 内网 IP** tcp://224.66.41.62:23456（main.py:96），多机分布式开箱必改
- **pd_vgg 用已废弃的无下划线 init API**（nn.init.kaiming_normal/constant/normal，models/pd_vgg.py:74-82，现代 PyTorch 已移除）；同仓 pd_resnet.py:132-137 是现代写法，两年代并存
- models/__init__.py 实为 2 行 barrel 且首行 CRLF 结尾（cat -A 实证 ^M$），图谱 sizeLines=1 系末行无换行符所致
- 小勘误：README.MD:76-77 把 mask_ratio 改前/改后的行号写反（算式实在 models/partialconv2d.py:64、注释在 :63）

## 工程信息

- 流水线：DeepWiki MCP 通道 + understand 批分析 + layers/tour + finalize + 写作收官（本仓 4 批图谱）
- 字数口径：不计空格总字符；行号锚口径：仓内唯一 basename 自动展开后逐一验证（96/96、11/11、19/19 全过）
