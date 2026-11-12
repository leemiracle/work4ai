# 01 · models/partialconv2d.py — PartialConv2d：mask 卷积归一化的算子心脏

> 源码：`models/partialconv2d.py`（84 行）+ 姊妹篇 `models/partialconv3d.py`（86 行）· 图谱定位：4 层第 2 层「部分卷积算子原语层」· 图谱 fanIn=6（被 pd_resnet/pd_vgg/__init__ 等全下游消费）

## 一、角色定位：全仓唯一不可替代的原语

如果只能读这个仓的一个文件，就是它。84 行实现了两篇论文共享的核心机制：**卷积输出按有效像素占比重新归一化**——ECCV 2018 inpainting 论文（arXiv:1804.07723）用它处理不规则洞，padding 技术报告（arXiv:1811.11718）用它替代 zero-padding。仓里其余一切（pdresnet/pdvgg 两族骨干、main.py 训练入口）都只是这个算子的消费者；图谱里它的 fanIn=6 是全仓最高集中度之一，README.MD:39 那句"直接替换 nn.Conv2d"的承诺完全由这个文件背书。

一句话定位：**PartialConv2d = nn.Conv2d 的全部能力 + 一个并行的 mask 通道**。mask 记录"每个窗口里有多少真像素"，输出据此缩放——补边不造假数据。

## 二、内部结构：构造期偷参、前向期四步

**构造（models/partialconv2d.py:15-41）**：`class PartialConv2d(nn.Conv2d)`（:14）不改签名，用 `*args, **kwargs` 接收全部标准 Conv2d 参数，先 `kwargs.pop` 摘走 `multi_channel`（:18-22）与 `return_mask`（:24-28）两个私有参数，再 `super().__init__(*args, **kwargs)`（:30）——父类看到的是一份纯净的 Conv2d 参数表，这是"drop-in 替换"的工程根基。随后建全 1 的 `weight_maskUpdater`（:32-35，multi_channel 时 `(out,in,k,k)`，否则 `(1,1,k,k)`）并记 `slide_winsize` 滑窗满分量（:37）。

**前向（models/partialconv2d.py:43-83）四步**：

1. mask 准备：`mask_in=None` 时自建全 1 掩码（:52-57）；整个更新块包 `torch.no_grad()`（:48）——mask 是数据不是参数，梯度绝不流过。
2. mask 更新：`F.conv2d(mask, weight_maskUpdater, stride/padding/dilation 与主卷积同构)`（:61）得每位置有效邻居数；`clamp(0,1)`（:66）得下一代 mask。
3. 比例归一化：`mask_ratio = slide_winsize/(update_mask + 1e-8)`（:64）——除以有效占比放大回满窗量级；ε 防零除，注释 :63 明言混合精度训练改 1e-6（README.MD:75-77 的 AMP 改法其一）；先算 ratio 再乘 clamp 后的 mask（:67），全零窗口输出归零不爆炸。
4. 输出重标定：显式传 mask 时先把洞置零再卷积（:70）；有 bias 先减后加避免 bias 被二次缩放（:72-75），无 bias 直接乘（:77）；`return_mask=True` 返回 `(output, update_mask)` 元组（:80-83）供下一层级联。

## 三、外部连接：两种消费形态

图谱证据：file 级 fanIn=3（pd_resnet.py、pd_vgg.py、`models/__init__.py` 的 star-import，pd_vgg.py:17）+ class 级 fanIn=6。消费分两种语义，**共用同一实现**：

- **padding 替代形态**（分类线）：消费方 forward 只传 `x`（PDResNet.forward 单参数，models/pd_resnet.py:156）→ mask_in=None → 内部全 1 掩码，只有边界窗口的有效数 < 满值，mask_ratio 自动补齐边界——洞传播机制完全静默。
- **inpainting 形态**：调用方显式传 mask 且开 `multi_channel=True, return_mask=True`（README.MD:42-46 范式），逐层 `out, mask = layer(x, mask)` 级联，洞随深度收缩。

`models/partialconv3d.py:14` 的 PartialConv3d 是同构第三消费者形态：继承 nn.Conv3d（:30）、断言 5D（:44）、`F.conv3d`（:61）、四维连乘的 slide_winsize（:37）、5D bias view（:75）——面向视频/体数据。

## 四、数据流：一个 3x3 边界窗口的数值走读

设 stride=1、padding=1、无 bias、multi_channel=False。输入 5x5 全 1 图像（mask 全 1）：中心窗口 update_mask=9、ratio=9/9=1、输出不变；**角落窗口** update_mask=4（卷积的 zero-padding 让 mask 卷积只数到 4 个真邻居，models/partialconv2d.py:61）、ratio=9/4=2.25——标准卷积在此处输出的量级只有"满窗"的 4/9，partial conv 把它放大 2.25 倍补齐，等效于"窗口内只对有效像素取平均再乘核响应"。inpainting 场景把 mask 换成洞掩码（洞=0）即同一机制换语义。缓存优化藏在 :45-46——只有 mask_in 非空或输入形状变化才重算 update_mask/mask_ratio，分类训练里第一个 batch 后 mask 通道近乎免费。

## 五、设计决策：三个值得偷师的取舍

1. **继承而非组合**：组合式（持一个 Conv2d 成员）要手抄全部 Conv2d 参数透传；继承 + kwargs.pop（:18-30）零成本拿到 groups/dilation/转置卷积无关的全部父类行为，代价是与父类 forward 强耦合（:70 显式调 super）。
2. **mask 更新与数据卷积解耦**：mask 通道用独立的全 1 核（:32-35）而非复用主 weight——语义干净（计数与加权分离），且 no_grad（:48）+ 缓存（:45-46）把开销压到最低。
3. **bias 的减加三明治**（:72-75）：`(raw_out - bias) * ratio + bias`——若直接乘 raw_out，bias 会被归一化重复缩放，边界输出系统性偏小。这个细节论文不写，只有读码才得。

## 六、新人提示

- 读码顺序：先 :61-67（mask 通道四行）再 :70-77（数据通道），公式即 arXiv:1804.07723 式 (1)。
- 坑一：`slide_winsize` 用 weight_maskUpdater 的形状算（:37），multi_channel 开关会改变它——但两者分子分母同步变，ratio 语义不变，别被绕晕。
- 坑二：3D 版 :72 直接 `torch.mul(input, mask_in)`，2D 版 :70 乘的是局部变量 mask——行为等价（仅显式传 mask 时才乘），代码不完全对称，移植时别照抄混用。
- 坑三：`1e-8` 在 fp16 下会下溢（:63-64 注释即为此），复现论文 AMP 数字记得换 1e-6，并同步改 loss.py 的 Gram 矩阵两步除法（models/loss.py:30-31，README.MD:66-73）。
- 验证练习：单层 PartialConv2d 喂全 1 图 + 全 1 mask，打印角落与中心的 update_mask（应为 4 与 9）与输出比例——十行脚本钉死你对归一化的理解。
