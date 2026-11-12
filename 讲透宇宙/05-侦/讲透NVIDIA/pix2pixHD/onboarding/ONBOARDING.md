# pix2pixHD 讲透上手指南（ONBOARDING）

> 图谱基线：101 节点 / 200 边 / 7 层 / 11 步 tour，fingerprints 43 文件 @ commit 14b3b3c（2024-09-30 NVIDIA 镜像末次提交；代码本体为 2018 年 CVPR 论文 *High-Resolution Image Synthesis and Semantic Manipulation with Conditional GANs* 的官方实现）。

## 一、一句话定位

pix2pixHD 是"语义标签图 → 2048×1024 高分辨率照片级图像"的条件 GAN 框架：用粗到细的生成器（全局生成器 + 局部增强器）、多尺度判别器与三路损失（GAN + 判别器特征匹配 + VGG 感知）把 pix2pix 的 256×256 能力推到 2K，并附带实例特征编码（同类对象多样化）与交互式 UI 编辑两个扩展子系统。

## 二、整体架构与模块地图

全仓 27 个 Python 文件，图谱分七层（L01 文档配置 / L02 命令行选项 / L03 数据管线 / L04 网络模型 / L05 训练推理入口 / L06 可视化工具 / L07 实验脚本矩阵），依赖单向向下：

- **options/**：三层继承的 argparse 体系。`BaseOptions.initialize()` 注册 40 余个通用参数（options/base_options.py:11），`TrainOptions`（options/train_options.py:3）追加判别器与训练节奏参数（`num_D` 默认 2 在 options/train_options.py:25、`pool_size` 默认 0 在 options/train_options.py:32），`TestOptions` 追加 TRT 三开关 `--engine/--onnx/--export_onnx`（options/test_options.py:14）。
- **data/**：`AlignedDataset` 负责标签/真实图/实例图/特征图四路对齐加载（data/aligned_dataset.py:6）；`CustomDatasetDataLoader` 包 torch DataLoader（data/custom_dataset_data_loader.py:21）。
- **models/**：`networks.py` 是网络工厂与损失库；`Pix2PixHDModel` 承载训练/推理主体（models/pix2pixHD_model.py:9）；`BaseModel` 提供存取骨架（models/base_model.py:5）；`ui_model.py` 独立实现交互编辑器后端（models/ui_model.py:11）。
- **顶层入口**：train.py / test.py 两大入口 + encode_features.py、precompute_feature_maps.py 两个特征预计算脚本 + run_engine.py（TensorRT 推理，models 之外唯一非 main-guard 脚本群）。
- **util/**：tensor2im/Colorize 图像工具（util/util.py:10、util/util.py:85）、ImagePool 历史缓冲（util/image_pool.py:4）、Visualizer 可视化门面。
- **scripts/**：13 个 shell 脚本构成的实验矩阵（9 训练 + 4 测试）。

## 三、核心模块深读

### 3.1 模型装配：create_model 与继承链

`create_model(opt)`（models/models.py:3）按 `--model` 分派：`pix2pixHD` 时从 `pix2pixHD_model` 同时导入 `Pix2PixHDModel` 与 `InferenceModel`（models/models.py:5），训练态实例化前者（models/models.py:7）、测试态实例化后者（models/models.py:9）；否则走 `UIModel`（models/models.py:11）。注意继承链的真相：`InferenceModel` 定义在 models/pix2pixHD_model.py:299（继承 Pix2PixHDModel，仅覆写 forward 为推理桥接），而 `UIModel` 直接继承 BaseModel（models/ui_model.py:11）且自行调用 define_G/define_D，与 Pix2PixHDModel 是平行分支——两套模型共享 networks 工厂但互不依赖。训练态且非 fp16 时在工厂里包 DataParallel（models/models.py:17）。

### 3.2 网络工厂 networks.py

`define_G` 三分支（models/networks.py:27）：`global`→GlobalGenerator、`local`→LocalEnhancer、`encoder`→特征编码器 Encoder；`define_D` 只产 MultiscaleDiscriminator（models/networks.py:48）。GlobalGenerator 是 c7s1-64 头（7×7 反射填充卷积，models/networks.py:190）+ 3 次下采样 + 9 个 ResnetBlock（models/networks.py:199）+ 对称上采样 + Tanh。LocalEnhancer 是论文"粗到细"的精髓：内部先造一个 ngf 减半的 GlobalGenerator 并砍掉尾部 3 层（models/networks.py:137），再用 `setattr(self, 'model'+str(n)+'_1'/'_2')` 动态注册每级局部增强子网（models/networks.py:162），forward 时构建输入金字塔、最粗层过全局网、逐级上采样残差相加（models/networks.py:167）。MultiscaleDiscriminator 用同样手法注册 num_D 个 PatchGAN（models/networks.py:300），forward 从最粗尺度开始、每级 AvgPool2d 降采样（models/networks.py:308）；`getIntermFeat` 时按层注册为 `scale{i}_layer{j}`（models/networks.py:304）——这正是特征匹配损失的取数点。Encoder（models/networks.py:255）前半是标准编解码，尾部做实例均值池化：`np.unique` 取实例 id 后逐实例逐通道 Python 双重循环替换为均值（models/networks.py:282），语义直白但速度慢。

### 3.3 三损失联合训练主体

`Pix2PixHDModel.forward`（models/pix2pixHD_model.py:152）一条龙完成：encode_input 里 label 做 one-hot scatter（models/pix2pixHD_model.py:118）、实例图经 get_edges 四方向位移或运算得边缘通道（models/pix2pixHD_model.py:262）、拼接后（可选）过 netE 得特征图（models/pix2pixHD_model.py:159）再喂 netG（models/pix2pixHD_model.py:163）。判别分两路：假图走 ImagePool 缓冲历史（models/pix2pixHD_model.py:166，pool.query 在 util/image_pool.py:11，50% 概率换出旧图维持缓冲多样性 util/image_pool.py:22），真图与"新鲜假图"直评。损失权重设计见 models/pix2pixHD_model.py:180：尺度间 1/num_D、层间 4/(n_layers_D+1)，乘 lambda_feat=10（options/train_options.py:28）。多卡 + ImagePool 显式禁用（models/pix2pixHD_model.py:66）。`init_loss_filter` 用闭包按开关过滤五元损失向量（models/pix2pixHD_model.py:13），保证 loss_names 与返回值一一对应（models/pix2pixHD_model.py:81）。

### 3.4 实例特征两段管线

第一段 encode_features.py：加载全部真图，调 `model.module.encode_features`（encode_features.py:31；实现在 models/pix2pixHD_model.py:240，取每实例中心像素特征 + 面积占比），按标签聚成大表后 KMeans 聚类（encode_features.py:43，面积阈值 0.5 过滤在 encode_features.py:47，簇数上限保护在 encode_features.py:49），落盘 `features_clustered_%03d.npy`（encode_features.py:52）。第二段 precompute_feature_maps.py：直接前向 netE（precompute_feature_maps.py:29，volatile=True 是 PyTorch 0.3 免梯度写法），上采样 2× 后把特征图存成 png 图像（precompute_feature_maps.py:30），供 1024p 训练时 `--load_features` 直接读盘（data/aligned_dataset.py:28）。推理时 `sample_features` 从聚类中心随机采样填充实例区域（models/pix2pixHD_model.py:219），实现"同标签不同外观"的多样的生成。

## 四、数据流全链路

训练态一次迭代的完整数据流：

1. `TrainOptions().parse()` 解析参数并把 opt.txt 落盘（options/base_options.py:93）；train.py 先把 print_freq 与 batchSize 取最小公倍数对齐（train.py:28，lcm 自实现在 train.py:9）。
2. `CreateDataLoader`（data/data_loader.py:2）→ `CustomDatasetDataLoader` → `CreateDataset` → `AlignedDataset`，两层函数体内延迟 import（data/custom_dataset_data_loader.py:7）。
3. `AlignedDataset.__getitem__` 双 transform 分支：label 图走 NEAREST 插值、不归一化、乘 255 保留类别索引（data/aligned_dataset.py:44-45）；真实图走默认 BICUBIC + (0.5,0.5,0.5) 归一化到 [-1,1]（data/base_dataset.py:55）。crop/flip 参数由 get_params 统一抽取、保证 A/B/inst 三路一致（data/base_dataset.py:27）。
4. train.py 调 model(**Variable 包装输入**)（train.py:70），得到五元 losses + 可选假图。
5. 损失组装：D 取两路均值、G 为三项相加（train.py:78-79）；fp16 时 apex.amp 在函数内延迟导入（train.py:43）并用 amp.initialize 包装（train.py:45），G/D 分别 zero_grad–scale_loss–step（train.py:85）。
6. 断点续训靠 iter.txt 记 (epoch, epoch_iter) 二元组（train.py:21、train.py:118）；niter_fix_global 到点后 `update_fixed_params` 解冻全局生成器（train.py:136 → models/pix2pixHD_model.py:279）；niter 之后线性衰减学习率（train.py:140 → models/pix2pixHD_model.py:288）。

测试态：test.py 强制单线程单 batch 串行不翻转（test.py:13），按 --engine/--onnx/--export_onnx 三开关分流（test.py:26、test.py:36、test.py:47）；ONNX 导出用 torch.onnx.export 后直接 exit(0)（test.py:50）。

## 五、配置与运行入口

`--model pix2pixHD`（默认）走训练/测试主线；`--model ui` 激活交互编辑后端（models/models.py:11 分支）。分辨率轴：512p 用默认 global 生成器，1024p 用 `--netG local --ngf 32 --resize_or_crop none`（README 与 scripts/test_1024p.sh 对应）；`resize_or_crop=none` 时 get_transform 会把图像边长对齐到 2^(n_downsample_global)（局部增强再乘 2^n_local_enhancers）的倍数（data/base_dataset.py:44-48）。实例特征轴：`--instance_feat` 开特征管线，`--load_features` 切换"训练时在线编码"与"读预计算特征图"两种模式（models/pix2pixHD_model.py:24-25 的 use_features/gen_features 两个布尔决定 netE 是否随训练更新）。精度轴：`--fp16` 走 apex O1；`--data_type 16/8` 在测试态把输入与模型转 half/uint8（test.py:28-31、test.py:41-46）。

## 六、关键设计决策

1. **延迟 import 破循环依赖**：data_loader.py 与 custom_dataset_data_loader.py 把 import 挪进函数体（data/data_loader.py:3），使 data 包可以自引用闭环；test.py 对 run_engine 的延迟导入（test.py:36）同时起到"未装 TensorRT 也能跑普通测试"的环境隔离作用。
2. **loss_filter 闭包统一损失口径**（models/pix2pixHD_model.py:13）：开关变化不改调用方代码，loss_names 与返回 list 严格同步。
3. **ImagePool 稳定判别器**：历史假图混入判别缓冲是 pix2pix 系的标配（util/image_pool.py:4），但作者明确只在单卡开（models/pix2pixHD_model.py:66），多卡池子不共享会引入不一致。
4. **参数名驱动局部微调**：niter_fix_global 阶段仅更新 key 前缀为 `model{n_local_enhancers}` 的参数（models/pix2pixHD_model.py:96），即只训最外层局部增强器——粗到细策略的可执行化。
5. **加载三级兜底**（models/base_model.py:50）：直接 load → 过滤多余层 → 按 size 逐键匹配并报告未初始化层，兼容不同 ngf/层数的预训练权重。
6. **np.load encoding='latin1'**（models/pix2pixHD_model.py:222）：读 Python2 时代序列化的聚类文件，兼容性残留。

## 七、坑与勘误（详版见 ../README.md 勘误清单）

1. run_engine.py 的 ONNX 路径在现代环境必然 NameError：`range(iter)` 引用未定义名（run_engine.py:115）、`max_batch_size/max_workspace_size` 未定义（run_engine.py:157）、末行 `engine` 应为 `trt_engine`（run_engine.py:173）；且 trt.infer.ConsoleLogger（run_engine.py:33）是 TensorRT 3.x API，TRT 5+ 已全部移除。
2. `raise('字符串')` 双现（models/base_model.py:58、models/networks.py:38）：Python3 下抛 TypeError 而非预期消息，Python2 残留。
3. `BaseModel.update_learning_rate` 定义缺 self（models/base_model.py:90），全靠子类覆写掩盖。
4. `fractions.gcd` 在 Python 3.9 移除，train.py:9 的 lcm 在新解释器直接 AttributeError。
5. `transforms.Scale`（data/base_dataset.py:37）是 torchvision 0.2 时代 API，新版需换 Resize。
6. `volatile=True`（precompute_feature_maps.py:29、models/pix2pixHD_model.py:241）为 PyTorch 0.3 写法，0.4+ 被忽略并告警；同文件 inference 里却写了 0.4 的 no_grad 分支（models/pix2pixHD_model.py:212），新旧 API 混用是移植时的隐形雷。

## 八、新人上手路线

1. **第 1 步（30 分钟）**：读 README + 本指南第一、二节，跑 `python test.py --name label2city_512p`（预训练权重需另行下载），对着 test.py:26-59 看三路推理分支。
2. **第 2 步（1 小时）**：精读 models/networks.py:129-211（LocalEnhancer/GlobalGenerator），手画输入金字塔到输出残差相加的草图；再读 models/networks.py:292-331 理解多尺度判别器的 setattr 动态注册。
3. **第 3 步（1 小时）**：跟 models/pix2pixHD_model.py:152-193 的 forward 数清五元损失的来源；对照 util/image_pool.py:11 的 query 逻辑理解判别缓冲。
4. **第 4 步（1 小时）**：跑通实例特征两段管线（encode_features.py → precompute_feature_maps.py），对照 scripts/train_512p_feat.sh 的参数组合理解 `--instance_feat/--load_features` 差异。
5. **第 5 步（进阶）**：读 models/ui_model.py 的 style_forward（models/ui_model.py:225）与 get_crop_region（models/ui_model.py:293），理解交互编辑的增量推理；最后浏览 scripts/ 13 个脚本体会"分辨率×特征×显存×并行"四轴矩阵，注意 train_1024p_12G/24G 只是显存预算差异。
6. **避坑**：不要在现代 Python/torchvision 上直接跑 run_engine.py 与 fp16 路径（apex 已停更）；改动 label 加载逻辑时严守 aligned_dataset.py:44-45 的双 transform 分支，破坏"NEAREST×255"约定会让 one-hot scatter 静默产出错位标签。
