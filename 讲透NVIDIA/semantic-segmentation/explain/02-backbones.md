# 02 · network/ 骨干族 — WiderResNetA2、get_resnet 包装类与 BN 单点开关

> 源码：`network/wider_resnet.py`（450 行）、`network/utils.py`（382 行）、`network/mynn.py`（114 行）、`network/bn_helper.py`（11 行，死资产）· 图谱定位：8 层第 5 层「网络通用件与骨干族层」· mynn.py fanIn=13 为网络侧被引用最深的底座

## 一、角色定位：所有架构共享的积木层

network/ 的骨干族（Resnet.py/SEresnext.py/wider_resnet.py/xception.py/hrnetv2.py 五文件）不是孤岛——它们被 network/utils.py 的 get_trunk 按名装配（network/utils.py:102），归一化统一走 mynn.py 的 Norm2d（network/mynn.py:18），再由各模型文件拼装成分割网。本篇讲透这层的三个关键件与两颗雷：WiderResNetA2 的独立实现、get_resnet 的小写类陷阱、bn_helper 死资产与 Norm2d 真出口。

## 二、内部结构：五族骨干 + 共享积木

**五族骨干各一句**：Resnet.py——torchvision 风格 BasicBlock/Bottleneck/ResNet，conv3x3 走 mynn 封装，resnet18-152 工厂；SEresnext.py——SEModule squeeze-excitation 通道注意力，se_resnext50/101_32x4d 工厂；xception.py——SeparableConv2d 深度可分离+entry/middle/exit 三段流（xception71）；hrnetv2.py——HighResolutionNet 全程保持高分辨率分支反复融合（OCRNet/Mscale 系的 trunk）；**wider_resnet.py——IdentityResidualBlock（network/wider_resnet.py:67，预激活恒等残差）+ WiderResNet（:190）与 WiderResNetA2（:270）**。

**勘误级事实：WiderResNetA2 不是 WiderResNet 的子类**。`class WiderResNetA2(nn.Module)`（network/wider_resnet.py:270）直接继承 nn.Module，与 WiderResNet（:190）是**两个独立实现**——A2 变体更深、带 dropout、前两个块用 max-pooling 下采样（docstring :271-275 自述），二者只共享 IdentityResidualBlock 积木。按"A2 是子类改 super 参数"的直觉读码必错。

**共享积木**（network/utils.py）：`get_resnet`（:48）、`get_trunk`（:102）、`get_aspp`（:301）、`make_seg_head`（:320）、`make_attn_head`（:343）。其中 **get_resnet 是第二颗雷：`class get_resnet(nn.Module)`（network/utils.py:48）是 nn.Module 子类却用小写命名**（Python 规范违规）——它是"按 trunk 名构造并持有骨干"的包装类：构造器内建 trunk、暴露 trunk_channel 等属性，不是工厂函数。get_trunk（:102）才是真正的按名分发出口（ResNet/SEResNeXt/WiderResNet/Xception/HRNet/EffNet 全名单在此）。

**BN 单点开关**（network/mynn.py）：Norm2d（:18-25）经 `getattr(cfg.MODEL, 'BNFUNC')` 取归一化构造器——BN/InPlaceABN/GN/SyncBN 的切换全仓只改 config.py 一处（cfg.MODEL.BNFUNC 赋值即可）；配套 initialize_weights（network/mynn.py:27，Kaiming）与 Upsample/Upsample2/Down2x/scale_as（:43/:52/:60/:70）尺寸算子被全部网络文件 star 依赖。

## 三、外部连接：谁消费骨干族

上行消费者是第 6 层的全部模型文件：deepv3.py（DeepV3Plus network/deepv3.py:40 经 get_trunk 取 R50/SRNX50/SRNX101/W38/W38I/X71/EffB4 七骨干，工厂 :96-121）、mscale.py（MscaleV3Plus network/mscale.py:232 的 W38 头即 WiderResNetA2）、ocrnet.py（HRNet_Mscale network/ocrnet.py:341）。装配链：train.py 的 get_net（network/__init__.py:12）→ importlib 动态取模型类（:51）→ 模型类内 get_trunk（network/utils.py:102）→ 骨干工厂 → 全部卷积经 mynn.Norm2d。并行包装由 wrap_network_in_dataparallel（network/__init__.py:33）决定 apex/DP。

## 四、数据流：一个 trunk 名字的解析之旅

config 里 `arch: network.ocrnet.HRNet_Mscale` → assert_and_infer_cfg（config.py:205）派生 arch_true → get_net（network/__init__.py:12）importlib 取类 → 模型构造器里 get_trunk(' wider_resnet38'...) → get_resnet 包装类（network/utils.py:48）实例化：内部按名调 WiderResNetA2 工厂（network/wider_resnet.py:270 族）→ 每个卷积块的 BN 都换 mynn.Norm2d（network/mynn.py:18）→ cfg.MODEL.BNFUNC 在 config.py 里指到 nn.BatchNorm2d 或 SyncBatchNorm（DDP 时）→ trunk 输出四级特征通道数经 trunk_channel 暴露给 ASPP/OCR 头（get_aspp network/utils.py:301、make_seg_head :320）。理解这条链，任何"加一个骨干"的需求都只是 wider_resnet.py 加工厂 + get_trunk 加分支两处。

## 五、设计决策：三个值得偷师的取舍

1. **Norm2d 间接层**：全仓不做 `nn.BatchNorm2d` 直接引用，统一过 cfg.MODEL.BNFUNC（network/mynn.py:18-25）——SyncBN/InPlaceABN/GN 实验是分割训练高频变量，单点开关把"改遍全仓"压成"改一处 config"；代价是多一层间接、IDE 跳转失效。
2. **包装类持骨干而非继承**：get_resnet（network/utils.py:48）持 trunk 实例并转发——相比继承（WiderResNetA2 若继承 WiderResNet 要懂全部内部结构），组合让"骨干名→特征"的映射独立演进；它的命名失误（小写）提醒：API 长得像函数不等于它是函数。
3. **同一积木两个实现**：WiderResNet 与 A2（network/wider_resnet.py:190/:270）宁可重复 IdentityResidualBlock 的组装逻辑也不强行抽公共基类——预激活残差网的结构微调（下采样方式/dropout 位置）侵入性强，继承树反而僵硬。

## 六、新人提示

- **bn_helper.py 是死资产**（network/bn_helper.py 全 11 行）：torch 0.x 分支引用的 `.sync_bn.inplace_abn.bn`（:5）目录不存在、全仓零消费者——改 BN 一律走 Norm2d/cfg.MODEL.BNFUNC。
- W38/W38I 这些 SOTA 常客对应 wider_resnet.py 的 A2 变体（network/wider_resnet.py:270），想改深度/dropout 直接改 A2 类，别去动 WiderResNet（:190，DeepV3 老基线在用）。
- 查"某 arch 用哪个骨干"最短路径：get_trunk（network/utils.py:102）的分支名即全部合法 trunk 名。
- initialize_weights（network/mynn.py:27）在预训练加载前调用，restore 时 forgiving_state_restore（loss/optimizer.py）会跳过形状不匹配权重——换骨干迁移不炸的秘密在这对组合。
- 验证练习：print 一个实例化的 get_resnet('xception')（network/utils.py:48），观察其 trunk_channel 与内部模块名——五分钟建立"包装类"直觉。
