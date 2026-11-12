# partialconv 新人上手文档（ONBOARDING）

> 基于知识图谱（41 节点 / 80 边 / 4 层 / 5 步导览，commit `610d373f`，fingerprints 8 文件基线）生成，全部行号锚经源码逐行核实。
> 仓库：`/usr-data/data2/repos/agent-repos/NVIDIA/partialconv`（NVIDIA/partialconv，2018 年 NVIDIA 官方代码）

## 1. 项目定位与一句话理解

**一句话**：partialconv 是 NVIDIA 官方的"部分卷积"（Partial Convolution）算子参考实现——一个继承 `nn.Conv2d` 的自定义层，让卷积只对有效像素归一化，既可当作 zero-padding 的替代补边方案，也可用于不规则空洞的图像 inpainting（README.MD:5）。

这个仓是两篇论文的代码落地：① ECCV 2018《Image Inpainting for Irregular Holes Using Partial Convolutions》（arXiv:1804.07723，README.MD:14）提出 partial conv 解决 inpainting 中 hole 区域的归一化；② 技术报告《Partial Convolution based Padding》（arXiv:1811.11718，README.MD:8）把它推广为分类网络的 padding 替代方案。两篇的第一作者都是 Guilin Liu（联系方式见各文件头，如 models/partialconv2d.py:6）。

动机锚点在 README 的对比图（README.MD:21 与 zero padding 对比、README.MD:108 与 zero/reflection/replication 三种 padding 的 5 次运行对比）：标准卷积把 padding 区当有效像素参与归一化，边界输出被"编造的像素"稀释；partial conv 用 mask 记录每个位置的有效邻居数，输出按有效占比重新缩放——"补边不再造假数据，只对真数据归一化"。

心智模型：全仓 8 个文件就是**一个算子 + 两族骨干 + 一个入口 + 两条旁支**。读懂 `models/partialconv2d.py`（84 行）就读懂了核心；`main.py` 是 ImageNet 分类训练入口（自述改编自 pytorch/examples/imagenet，main.py:10，差异注释在 main.py:12-15）；`partialconv3d.py` 与 `loss.py` 是不在分类主线上的延伸。

## 2. 五分钟上手

仓库无 requirements.txt——安装指引直接外链 pytorch/examples/imagenet 的环境（README.MD:27-28），即"装好 PyTorch 即可"。

算子级使用（README.MD:36-46 的两行对照）：

```python
import torch.nn as nn
# 标准 zero padding
nn.Conv2d(3, 16, kernel_size=3, stride=1, padding=1, bias=False)
# partial conv based padding：签名完全兼容，直接替换
PartialConv2d(3, 16, kernel_size=3, stride=1, padding=1, bias=False)
# inpainting 模式：multi_channel=True + return_mask=True
PartialConv2d(3, 16, kernel_size=3, stride=1, padding=1, bias=False,
              multi_channel=True, return_mask=True)
```

ImageNet 分类训练（README.MD:84-100 四条命令的范式）：baseline 与 partial conv 模型只差一个 `-a` 参数——`python main.py -a resnet50 ...`（zero padding，README.MD:84）vs `python main.py -a pdresnet50 ...`（partial conv，README.MD:89），VGG 同理（README.MD:99 的 `pdvgg16_bn`）。常用参数：`--data_train/--data_val` 分开的训练/验证目录（main.py:56-60）、`--batch-size` 默认 192（main.py:78）、`--workers 32`、`--prefix/--ckptdirprefix` 拼出 checkpoint 目录名（main.py:115）。预训练权重不在代码里下载，官方放了一个 Dropbox 打包链接（README.MD:102-105）。

注意两条坑（第 6 节展开）：`--pretrained` 只对 baseline 模型可用（pd 系工厂的 model_urls 是空串，见 5.2）；多机分布式默认 `--dist-url tcp://224.66.41.62:23456` 是硬编码的 NVIDIA 内网地址（main.py:96），开箱必改。

## 3. 架构总览（按 4 层图谱）

知识图谱把 8 个文件切成 4 层，依赖方向自上而下：

**L01 文档与训练入口层**：`README.MD`（11 节主文档）与 `main.py`（458 行训练入口）。main.py 的 documents 边只指向这两个文件——README 预告的全部主线就由 main.py 承担。

**L02 部分卷积算子原语层**：全仓核心贡献。`models/partialconv2d.py:14` 的 `PartialConv2d(nn.Conv2d)` 与 `models/partialconv3d.py:14` 的 `PartialConv3d(nn.Conv3d)`——两个算子是被下游全部模型消费的唯一原语，也是 import 依赖图的汇聚点。

**L03 分类骨干模型层**：`models/__init__.py` 是 2 行 barrel（`from .pd_resnet import *` / `from .pd_vgg import *`，models/__init__.py:1-2），把两族工厂函数 re-export 到包命名空间；`models/pd_resnet.py` 复刻 torchvision ResNet 骨架但 conv3x3（pd_resnet.py:38-41）与 downsample（pd_resnet.py:143-145）全部换 PartialConv2d，提供 pdresnet18/34/50/101/152 五个深度工厂（pd_resnet.py:174-231）；`models/pd_vgg.py` 走 cfg 配置表路线（pd_vgg.py:103-108），make_layers_pd 生成特征层（pd_vgg.py:85-98），提供 8 个工厂（pd_vgg.py:111-220）。

**L04 感知损失扩展层**：`models/loss.py`（316 行）是面向 inpainting 的独立旁支——VGG16Partial 特征提取器 + VGG16PartialLoss（L1+感知+风格）。它与分类主线**零 import 关联**（main.py 不引用它），也不依赖 L02 算子。

纵观四层：L02 被 L03 消费、L03 被 L01 消费、L04 悬挂在外——依赖图无环，且 L04 的独立性正是"分类仓里塞了一个 inpainting 损失模块"这一论文配套形态的体现。

## 4. 深潜一：PartialConv2d 算子（全仓最有价值的 84 行）

### 4.1 构造：继承 + kwargs.pop 的签名兼容术

`class PartialConv2d(nn.Conv2d)`（partialconv2d.py:14）。它不重写 `__init__` 签名，而是用 `*args, **kwargs` 透传，再用 `kwargs.pop` 摘走两个自定义参数（partialconv2d.py:18-28）：

- `multi_channel`（默认 False）：mask 是逐通道（形状随 out_channels/in_channels）还是单通道共享；
- `return_mask`（默认 False）：forward 是否额外返回更新后的 mask。

摘完再调 `super().__init__(*args, **kwargs)`（partialconv2d.py:30）——父类看到的就是标准 Conv2d 参数表。这就是 README.MD:36-39 那行"直接替换"能成立的原因：**任何接 nn.Conv2d 的代码都能无缝换成 PartialConv2d**。

随后构造 mask 更新核：`weight_maskUpdater = torch.ones(...)`（partialconv2d.py:32-35）——multi_channel 时形状 `(out_channels, in_channels, k, k)`，否则 `(1, 1, k, k)`；`slide_winsize` 记录滑窗内元素总数（partialconv2d.py:37），即"满分"邻居数。

### 4.2 forward：mask 卷积 + 比例归一化

`forward(self, input, mask_in=None)`（partialconv2d.py:43），四步：

1. **mask 准备**：`mask_in` 为 None 时自建全 1 掩码（multi_channel 建 `(B,C,H,W)`，否则 `(1,1,H,W)`，partialconv2d.py:52-57）；更新逻辑包在 `torch.no_grad()` 里（partialconv2d.py:48）——mask 是数据不是参数，绝不能让梯度流过。
2. **mask 更新**：`self.update_mask = F.conv2d(mask, self.weight_maskUpdater, ...)`（partialconv2d.py:61）——用全 1 核对 mask 卷积，得到每个输出位置的有效邻居计数；`torch.clamp(update_mask, 0, 1)`（partialconv2d.py:66）压回 [0,1] 作为新 mask（洞会随层数加深逐步收缩，这正是 inpainting 论文里 mask 传播机制）。
3. **比例归一化**：`mask_ratio = slide_winsize / (update_mask + 1e-8)`（partialconv2d.py:64）——除以有效占比，把"只卷到部分邻居"的输出放大回"满窗"的量级；ε 防零除，注释明言混合精度训练时应把 1e-8 改 1e-6（partialconv2d.py:63，对应 README.MD:75-77 的 AMP 改法）。注意 mask_ratio 在 clamp 之前算、clamp 之后再乘回（partialconv2d.py:67），全零窗口的 ratio 被压成 0，输出归零而非爆炸。
4. **输出重标定**：`raw_out = super().forward(torch.mul(input, mask) if mask_in is not None else input)`（partialconv2d.py:70）——先乘 mask 把洞显式置零再卷积（仅显式传 mask 时）；有 bias 时先减 bias、乘 ratio、再加回（partialconv2d.py:72-75），保证 bias 不被归一化重复缩放；无 bias 直接乘（partialconv2d.py:77）。`return_mask=True` 时返回 `(output, self.update_mask)` 元组（partialconv2d.py:80-83），供下一层链式传入。

另有一个值得注意的性能设计：mask 更新有**缓存**——仅当 `mask_in is not None`（每步都变）或输入形状变化（partialconv2d.py:45-46）才重算 update_mask/mask_ratio；分类训练里 mask 恒为全 1、形状恒定，第一个 batch 之后 mask 通道几乎是免费乘法。这就是"当 padding 用"在算子内省出的效率。

`PartialConv3d`（partialconv3d.py:14）是同构的体数据版：继承 nn.Conv3d（partialconv3d.py:30），断言 5D 输入（partialconv3d.py:44），`F.conv3d` 更新 mask（partialconv3d.py:61），slide_winsize 是四维核连乘（partialconv3d.py:37），bias view 多一维（partialconv3d.py:75）。面向视频/医学体数据的 inpainting。

## 5. 深潜二：骨干模型族与训练主线

### 5.1 双字典选模型：一个入口跑两组对照实验

main.py 的模型装配是全仓最巧的工程点。它同时 import 两套模型字典（main.py:38-39）：`models_baseline`（torchvision.models，zero padding）与 `models_partial`（本仓 models 包）。再用完全相同的过滤规则各收集一遍小写可调用名（main.py:42-48），拼成 `model_names = baseline + partial`（main.py:50）喂给 `--arch` 的 choices（main.py:62-66）。构造时先查 baseline 字典、查不到再查 partial 字典（main.py:149-159）。

于是**同一份训练脚本、同一套超参，`-a resnet50` 与 `-a pdresnet50` 就构成 padding 方案的受控 A/B 实验**——README.MD:108-114 的 5 次运行对比表正是这样产出的。`models/__init__.py` 那 2 行 barrel 是这个机制的前提：star-import 把 pd_resnet/pd_vgg 的工厂函数（pd_resnet.py:18-19、pd_vgg.py:19-22 的 `__all__`）全部抬进包 `__dict__`，`models_partial.__dict__[arch]` 才取得到构造器。

### 5.2 骨干改造：换卷积不换骨架，且 forward 不传 mask

`pd_resnet.py` 自述改编自 torchvision resnet（pd_resnet.py:9-10），骨架逐块复刻：BasicBlock 两卷积（pd_resnet.py:44-73）、Bottleneck 1x1-3x3-1x1（pd_resnet.py:76-112，expansion=4 在 :77）、PDResNet 主体含 7x7 stem（pd_resnet.py:120）与 `_make_layer`（pd_resnet.py:139-154）——但所有 3x3 与 downsample 1x1 都是 PartialConv2d（conv3x3 工厂 pd_resnet.py:38-41；downsample pd_resnet.py:143-145）。pd_vgg 同理，make_layers_pd 按 cfg 表逐项建层（pd_vgg.py:85-98，卷积项在 :92）。

**关键语义（图谱摘要在此翻了车，新人必钉版）**：两条骨干的 `forward` 都只接收单个 `x`（BasicBlock 在 pd_resnet.py:57、PDResNet 在 pd_resnet.py:156、PDVGG 在 pd_vgg.py:65-69），**并不逐层传递 (x, mask) 二元组**。partial conv 在分类线里以"padding 替代"模式工作：mask_in=None，每层算子内部自建全 1 掩码（partialconv2d.py:52-57），边界窗口的有效数 < 滑窗满值，mask_ratio 自动把边界输出放大补齐——洞传播/掩码级联是 inpainting 模式（显式传 mask + return_mask）才启用的语义。

另一颗雷：pd 系工厂的 `pretrained=True` 分支走 `model_zoo.load_url(model_urls[...])`（如 pd_resnet.py:182），但 **model_urls 的值全是空字符串**（pd_resnet.py:30-36、pd_vgg.py:28-36）——torchvision 真实 URL 只以注释形式留在 pd_vgg.py:37-44。`-a pdresnet50 --pretrained` 会因空 URL 直接抛错；真权重要走 README.MD:102-105 的 Dropbox 链接或手工 load_state_dict（PartialConv2d 与 nn.Conv2d 参数名形状一致，torchvision 权重可直接迁移——这是把 URL 留空的底层依据）。

### 5.3 训练循环：朴素 fp32 + 断点续训 + 晚期逐 epoch 留档

main() 流程（main.py:111-288）：建 checkpoint 目录与 loss.txt 日志（main.py:115-118）→ 构模型 → 三形态并行包装：指定 `--gpu` 单卡、`world_size>1` 走 DistributedDataParallel（main.py:140-144，backend 默认 gloo，main.py:98）、否则 DataParallel——且 VGG 系只包 `model.features`（main.py:175-176，classifier 太小不值得拆卡）→ SGD 只收 `requires_grad` 的参数（main.py:185-187）→ 断点恢复（main.py:190-204）→ 标准 ImageNet 增强管线（RandomResizedCrop 224 + 翻转，main.py:216-223；验证 Resize256/CenterCrop224，main.py:234-242）→ 主循环逐 epoch 调 `adjust_learning_rate`（main.py:261；阶梯 0.1×/30 epoch，main.py:432-436）→ train（main.py:291-347，纯 fp32 的 forward/backward/step，main.py:311-323，**没有任何 AMP 代码**）→ validate（main.py:350-405，torch.no_grad 在 :359）→ `prec1 > best` 判优存 `model_best.pth.tar`（main.py:270-278、save_checkpoint main.py:408-411），且 `epoch >= 94` 后每个 epoch 额外留一份快照（main.py:281-288）——配合默认 100 epoch（main.py:69-70），是给 5 次运行挑 best 做统计的实验形态。

## 6. 新人路线图与避坑

**阅读路线**：README（动机与结论）→ models/partialconv2d.py（算子，1 小时）→ main.py:38-50 与 :147-159（双字典机制）→ pd_resnet.py（改造范式）→ 按需看 loss.py（inpainting 侧）。

**勘误与陷阱清单**（全部源码实证）：

1. **VGG16Partial 的 "Partial" 不是部分卷积**：它是"截取 VGG16 前若干层"的特征提取器——卷积是标准 `nn.Conv2d`（loss.py:112），权重来自 torchvision vgg16 官方文件（loss.py:128-132），且整体冻结（loss.py:158-159）。它与 partialconv2d.py 零继承关系，别当第三个 partial conv 变体读。
2. **图谱/直觉说骨干 forward 传 (x, mask)——实际不传**：见 5.2，mask 传播是算子内部机制，不是模型级数据流。
3. **`--pretrained` 对 pd 系模型是坏的**：model_urls 全空串（5.2）；README 的 Dropbox 才是权重真源。
4. **main.py 没有 AMP**：README.MD:48-77 的混合精度指引（apex 的 amp.initialize/scale_loss，README.MD:52-62）只适用于 inpainting 训练侧；main.py 全文无 apex/autocast/GradScaler。图谱 hub 摘要所谓 "Autocaster" 系幻觉，以源码为准。
5. **`--dist-url` 默认是 NVIDIA 内网 IP**（main.py:96 `tcp://224.66.41.62:23456`），多机训练必改。
6. **pd_vgg 用了已废弃的无下划线初始化 API**：`nn.init.kaiming_normal`/`nn.init.constant`/`nn.init.normal`（pd_vgg.py:74-82）在新版 PyTorch 已移除，复现请用 2018 年代环境或手工加下划线；对照 pd_resnet.py:132-137 用的就是带下划线的现代写法——同仓两种风格并存。
7. 小坑两则：`models/__init__.py` 实为 2 行且首行是 CRLF 结尾（编辑器痕迹，图谱 sizeLines 记 1 是末行无换行符所致）；README.MD:76-77 把 mask_ratio 的"改前/改后"行号写反了（实际算式在 partialconv2d.py:64、注释在 :63），引用以源码为准。
