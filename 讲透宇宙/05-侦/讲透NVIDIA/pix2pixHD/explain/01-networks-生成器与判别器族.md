# 精讲一：networks.py——生成器族与判别器族的工厂与损失库

## 角色定位

models/networks.py 是 pix2pixHD 的"网络百科全书"：416 行装下三个生成器、两个判别器、三个损失与全部装配工厂。models/pix2pixHD_model.py:35 的 define_G 与 models/pix2pixHD_model.py:45 的 define_D 都指向这里，UIModel（models/ui_model.py:11）也复用同一工厂——两套模型分支唯一的共享层。

## 内部结构

工厂层：`get_norm_layer` 用 functools.partial 把 batch/instance 归一化包装成可传参构造器（models/networks.py:18）；`define_G` 三分支派发 global/local/encoder（models/networks.py:27），装配后统一 `netG.apply(weights_init)` 用 0.02 正态初始化（models/networks.py:43）。生成器族：GlobalGenerator 是 7×7 反射卷积头（models/networks.py:190）+ n_downsampling 次 stride-2 下采样（models/networks.py:192）+ n_blocks 个 ResnetBlock（models/networks.py:199）+ ConvTranspose2d 上采样（models/networks.py:205）+ Tanh；LocalEnhancer 内部实例化 ngf 翻倍的 GlobalGenerator 并砍掉末尾 3 层卷积（models/networks.py:137），局部增强层用 setattr 动态挂名 `model{n}_1/_2`（models/networks.py:162）。判别器族：MultiscaleDiscriminator 注册 num_D 个 NLayerDiscriminator（models/networks.py:300），forward 由粗到细、级间 AvgPool2d(3,stride=2) 降采样（models/networks.py:308）；NLayerDiscriminator 是 4×4 核 PatchGAN（models/networks.py:340），通道数以 min(nf*2,512) 封顶（models/networks.py:347），getIntermFeat 时按层拆注册（models/networks.py:366）。

## 外部连接

上游被两套模型的 initialize 消费；损失端 GANLoss 直接读判别器输出的 list-of-list（models/networks.py:100 判型）；VGGLoss 内嵌 Vgg19（models/networks.py:386），五个 slice 按索引 0-1/2-6/7-11/12-20/21-29 从 torchvision 预训练 VGG19 切出 relu1_2 到 relu5_4（models/networks.py:395），全部 requires_grad=False（models/networks.py:405）。

## 数据流

LocalEnhancer.forward（models/networks.py:167）：先构输入金字塔——原图逐级 AvgPool（models/networks.py:165）；最粗层过全局网得 output_prev；逐级 `model_downsample(input_i) + output_prev` 残差相接再上采样（models/networks.py:180）。判别器侧 MultiscaleDiscriminator.forward（models/networks.py:319）反向遍历尺度，getIntermFeat 把每层中间输出累积成 list 返回（models/networks.py:312）——正是特征匹配损失的输入形态。Encoder 前向在编解码后做实例均值池化：np.unique 列实例（models/networks.py:282），逐实例逐通道写回均值（models/networks.py:287）。

## 设计决策

第一，"局部增强器复用全局生成器"是参数效率关键：LocalEnhancer 实例化现成 GlobalGenerator 再裁剪（models/networks.py:137），1024p 模型因此能用 512p 预训练权重热启动。第二，setattr 动态注册实为 state_dict 命名服务——`model1_1` 前缀让 niter_fix_global 的参数过滤（models/pix2pixHD_model.py:96 的 startswith 匹配）成为一行代码。第三，GANLoss 双模态：use_lsgan 切 MSE/BCE（models/networks.py:77），目标张量按 input 尺寸惰性创建并缓存（models/networks.py:85）。第四，VGG 权重 1/32→1 递增（models/networks.py:117），浅层低权重防止感知损失过度约束纹理。

## 新人提示

建议按"工厂→生成器→判别器→损失"顺序读，每个类先看 __init__ 的 setattr 再看 forward。两个易错点：getIntermFeat 返回嵌套 list，直接 .backward 会踩形状坑，先看 models/networks.py:310 的 singleD_forward 分支；Encoder.forward 的 Python 四重循环（实例×通道）在 2048×1024 下极慢（models/networks.py:284 的逐 batch 循环），勿进主训练循环。另外 define_G 的 else 分支 `raise('generator not implemented!')`（models/networks.py:38）在 Python3 抛 TypeError，报错会出乎意料。
