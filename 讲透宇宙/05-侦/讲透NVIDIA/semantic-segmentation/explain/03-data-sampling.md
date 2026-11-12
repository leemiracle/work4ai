# 03 · datasets/ 数据线 — uniform 类均衡采样与 BaseLoader 骨架

> 源码：`datasets/uniform.py`（324 行）、`datasets/base_loader.py`、`datasets/__init__.py`（199 行）、`transforms/joint_transforms.py` 的 _ClassUniform · 图谱定位：8 层第 3/4 层「数据装载与类均衡采样层 + 联合变换层」· uniform.py 是 Cityscapes 小类 mIoU 提升的关键机制

## 一、角色定位：长尾分布的配平器

Cityscapes 是典型长尾：路面/建筑占像素大头，栅栏/地形/火车等小类不足 1%——普通随机采样下小类梯度信号被淹没，mIoU（逐类平均）被小类拖死。本仓的解法是**两层类均衡**：epoch 层的 uniform.build_epoch（datasets/uniform.py:278）让贫类样本高频复现、富类降频；裁剪层的 _ClassUniform（transforms/joint_transforms.py:579）让裁剪窗口偏向含小类的质心区域。配合 BaseLoader 把机制无感地接进任意数据集 Loader，这是该仓数据侧的独门武器，也是新人最容易低估的文件。

## 二、内部结构：质心统计 → epoch 重组 → 裁剪偏置

**质心统计**（datasets/uniform.py 前半）：`calc_tile_locations`（:67）把图像切成 tile 网格；`class_centroids_image`（:84）统计单图每类像素的质心坐标；`pooled_class_centroids_all`（:138）/`unpooled_class_centroids_all`（:167）两种聚合并行策略；`class_centroids_all`（:189）汇总全数据集。结果可缓存到文件，`build_centroids`（:219）是入口——支持 cv 交叉验证（缓存名带 `_cv` 后缀 :240）与 coarse 粗标数据。

**epoch 重组**：`build_epoch`（datasets/uniform.py:278）按 min_samples/every_cnt 两个旋钮工作——每类先保底 min_samples 个样本，再按 every_cnt 间隔从富类抽取，贫类优先复现；输出重组后的样本列表交给 DataLoader。BaseLoader 的 `build_epoch` 方法（datasets/base_loader.py:62）每个 epoch 调它刷新 self.imgs（:68），使"类均衡"持续生效而非一次性预处理。

**裁剪偏置**：`_ClassUniform`（transforms/joint_transforms.py:579）在 RandomCrop 语义上加质心偏置——以质心表选目标类，裁剪窗口向该类像素密集区移动；与 SlidingCrop（:526，验证期滑窗）、RandomSizeAndCrop（:433）并列于 18 个联合变换类（Compose :37、RandomCrop :73、CenterCropPad :212 等），全部保证 image/mask 同步几何变换。

**装载骨架**：`setup_loaders`（datasets/__init__.py:45）是 train.py 取数唯一入口——构造训练/验证 DataLoader，**分布式分支的 DistributedSampler 是函数体内延迟 import**（datasets/__init__.py:162/:185，sampler.py 提供 pad=False/连续/permutation 三模式）。BaseLoader（datasets/base_loader.py:45）收编图像发现、joint transforms 应用（:128-129 循环）、build_epoch 调度与 dump_images 可视化（:102）；具体 Loader（cityscapes.py 的 cities_cv_split :41 与 coarse_cities :92、mapillary.py 的 65 类 v1.2）只覆写文件发现与掩码读取。nullloader.py 返回全零占位——免真实数据单 batch 调网络。

## 三、外部连接：三处消费与一处真源

上游：train.py 的 main（train.py:324）调 setup_loaders（datasets/__init__.py:45）；config.py 的 assert_and_infer_cfg（config.py:205）派生 DATASET.NUM_CLASSES 与 mean/std 供 Loader 使用。下游：uniform.py 被 BaseLoader import（datasets/base_loader.py:40 `from datasets import uniform`）与 cityscapes.py/mapillary.py 的 build_centroids 消费；randaugment.py 的 20 余算子由 joint_transforms 管线尾部按 (op, random magnitude) 二元组驱动。边界权重的真源在 transforms/transforms.py:74 的 RelaxedBoundaryLossToTensor——它与 ImgWtLossSoftNLL（loss/utils.py:150，工厂分支 :57）配对，给训练提供边界加权；**utils/f_boundary.py 虽名为边界工具但全仓零消费者**（死资产，别混淆）。

## 四、数据流：一个 epoch 的重组走读

训练启动 → setup_loaders 建 train_set（BaseLoader 子类）→ build_centroids（datasets/uniform.py:219）扫全数据集算质心（首跑落盘缓存）→ 每 epoch 开始 BaseLoader.build_epoch（datasets/base_loader.py:62）调 uniform.build_epoch（:278）：对每类按质心表配额采样、贫类复现 → 新样本列表进入 DDP DistributedSampler 分片（datasets/__init__.py:185）→ 单条样本经 joint_transform_list（:128）逐层变换：_ClassUniform 按质心选窗（transforms/joint_transforms.py:579）→ RandomSizeAndCrop（:433）→ RelaxedBoundaryLossToTensor（transforms/transforms.py:74）出边界权重 → batch 进网络。一句话：**类别分布的均衡发生在两个采样粒度（epoch 复现 + 窗口偏置），而非损失加权**。

## 五、设计决策：三个值得偷师的取舍

1. **采样配平优于损失加权**：对小类，过采样（build_epoch）比加大损失权重数值更稳——不放大噪声梯度，只改变出现频率；代价是 epoch 内样本重复，需与数据增强（randaugment）配合防过拟合。
2. **质心表缓存与数据集形状解耦**：class_centroids_all（datasets/uniform.py:189）结果落盘、cv 后缀区分（:240）——质心计算是 O(全数据集) 的重活，缓存让重启训练秒级就绪。
3. **基类收编横切、子类只写差异**：BaseLoader（datasets/base_loader.py:45）把 transforms/采样/dump 全部收编，cityscapes.py 只覆写发现与掩码逻辑（cities_cv_split :41）——加新数据集约 150 行；nullloader.py 的全零占位设计让"没有数据也能测网络装配"成为可能。

## 六、新人提示

- 想看类均衡是否生效：打印 build_epoch（datasets/uniform.py:278）前后样本列表里含小类图片的频次对比，或直接看 dump_images（datasets/base_loader.py:102）输出的质心可视化。
- min_samples/every_cnt 在 dataset 类构造参数里调（build_centroids datasets/uniform.py:219 传递链）；调大 every_cnt=更激进的贫类偏置。
- 粗标数据联合训练走 cityscapes.py 的 coarse_cities（:92，leftImg8bit_trainextra），SOTA 配置里的 coarse dropout 策略在 scripts/train_cityscapes_sota.yml。
- 排查"数据管线 bug"最短路径：先用 nullloader.py 跑通网络，再换真实 Loader——把变量从两个减到一个。
- 勘误提醒：图谱/层摘要称联合变换 19 个类，顶层 class 实数 18（transforms/joint_transforms.py grep 计数）；DistributedSampler 延迟 import（datasets/__init__.py:162/:185）使静态依赖图失明，跨文件追踪时以源码为准。
