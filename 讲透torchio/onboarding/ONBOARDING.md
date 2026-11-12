# TorchIO 新人上手指南（ONBOARDING）

> 版本锚定：commit `9b1be950`，`torchio 2.0.0a2`（`pyproject.toml:3`）。知识图谱 969 节点/1827 边/14 层/16 步导览，校验 0 issues。本文全部行号锚经 grep 核实于该 commit。

## 1. 一句话定位

TorchIO 是面向 CT/MRI/PET 等三维医学影像的 PyTorch 库，一句话职责写在 `pyproject.toml:4`：**"Medical image preprocessing, augmentation, and patch-based training"**——加载（多格式 IO、懒加载、远程存储）、预处理（重采样、重定向、归一化）、增强（强度与空间变换、扫描伪影模拟）、patch 化训练（采样、队列、聚合）四件事一条龙。它解决的核心痛点是：医学影像天然是三维甚至四维体积、格式高度碎片化、单卷动辄数百 MB 装不进显存，直接套用为自然图像二维 pipelines 设计的工具链会处处碰壁；TorchIO 把这些领域特有问题封装成与 PyTorch 生态无缝衔接的原语。

这是一个科研向库：配有正式论文（Pérez-García et al., *Computer Methods and Programs in Biomedicine* 2021，引用格式在 `README.md:236`），`CITATION.cff` 让"可引用性"本身成为功能。README 首页的增强 GIF 矩阵与 Queue patch 训练示意（`README.md:204-210`）一图胜千言，值得先花五分钟看懂。包根入口 `src/torchio/__init__.py:1` 的 module docstring 与定位一致。生态位上，它与 MONAI 是同域竞品也是互操作伙伴（第 4 节的适配器可让两库混用），底层则站在 nibabel 与 SimpleITK 两个格式读写巨人的肩膀上，自身专注"数据结构 + 变换 + patch 训练"这一层。

新人必须知道的第一件事：当前代码处于 **v2 alpha**（版本号 `2.0.0a2`），API 相对 v1 有大规模改名与语义调整，网上大量教程、Stack Overflow 答案乃至本仓部分文档示例仍在用 v1 名字。上手第一份材料建议就是 `docs/get-started/migration.md` 的迁移对照表（第 8 节有摘要），先建立新旧名词映射再读其余文档，能少走很多弯路。

## 2. 核心架构总览（14 层）

图谱 14 层可归并为五条带，依赖梯度单向向下 `transforms → data → core → datasets`，没有环：

| 带 | 图谱层 | 职责与量化事实 |
|---|---|---|
| 数据底座 | L0 core-foundation（13 文件）、L1 data（15 文件） | 包根门面（fan-in 85）、types/constants 类型与常量、io/loader 读写入口；**data 层 fan-in 173 为全库最高**——transforms 有 71 条边、datasets 17 条、core 15 条边指向它，是整个库的地基 |
| 变换骨架 | L2 transform-framework（10）、L3 spatial（14）、L4 intensity+label（23） | **transform-framework fan-out 185 为全库最高**：`Transform` 基类向上被全部具体变换继承，向下依赖 data 层的 Subject/Image，构成变换体系骨架；spatial 层操作几何（affine/形状），intensity/label 层逐体素改值，是数据增强主力 |
| 纯消费端 | L5 datasets（14） | IXI、MNI、Slicer、MedMNIST 等公开数据集的下载与访问封装；**无任何模块反向依赖它**，位于依赖图最顶层 |
| 质量防线 | L6-L9 四个测试层（共 86 文件） | data 组件测试 23、空间变换测试 12、强度/框架测试 34、夹具数据 17；tests→core 68 条边、tests→data 36 条边，是正确性主防线 |
| 文档与外环 | L10-L12 文档三层（91）、L13 工程 CI（29） | mkdocstrings 自动 API 页与 src 三层镜像（数据与工具 13 页、变换 43 页、教程指南 35 篇）；tox/GHA 驱动测试与发布 |

这张表给出三条阅读纪律。其一，**改 data 层要有全库意识**：fan-in 173 意味着任何接口变动都会波及变换、数据集与全部测试，改动前先 grep 引用面。其二，**加新变换只需继承框架层**：fan-out 185 的骨架已铺好继承路径，写一个子类、实现 `apply_transform` 即可自动获得批处理包装、参数采样、历史记录与注册表登记。其三，**datasets 层永远安全**：没有模块依赖它，是最适合新人练手的区域。门面 `src/torchio/__init__.py:98` 的 `__all__` 就是全库公开清单，对照它读代码不会迷路；data 子包另有自己的 barrel（`src/torchio/data/__init__.py:18` 起 re-export `ScalarImage`、`Queue` 等符号）。

## 3. 关键模块深读

### 3.1 数据载体：Image 与 Subject

- **`Image`**（`src/torchio/data/image.py:104`，继承 `Invertible`）是全库心脏：把四维张量 `(C,I,J,K)`、affine 仿射矩阵与空间轴语义打包成单一对象。它是**惰性加载器**——类 docstring 明言"data is only read from disk when first accessed"（`image.py:107-109`），构造时只挂路径，首次访问数据才真正读盘；这对动辄几百 MB 的医学卷至关重要，遍历大数据集做元数据统计不会触发任何磁盘读取。构造函数按源类型自动分派（分派表在 `image.py:119-126`）：路径/URL/文件对象走懒加载，Tensor/ndarray 急加载进内存，Nifti1Image 经 NibabelBackend 懒加载，zarr Store 经 zarr2nii 桥接，bytes 经临时文件解码，None 留空后补。语义子类 `ScalarImage`（`image.py:1238`，强度数据）与 `LabelMap`（`image.py:1251`，分割标签）——变换用 isinstance 区分二者，例如对 LabelMap 强制最近邻插值以防标签值被插值污染。
- **`Subject`**（`src/torchio/data/subject.py:25`，`__init__` 在 `subject.py:59`）把同一受试者的 T1/T2/label 等多张 Image，连同 `Points`（`src/torchio/data/points.py:20`，三维点标注）、`BoundingBoxes`（`src/torchio/data/bboxes.py:207`，格式封装 `bboxes.py:37`）与任意元数据，聚合成一个训练样本；构造时自动分类条目并校验各图像 spacing/方位/形状一致——这是多模态增强几何同步的前提。它混入 `Invertible`（`src/torchio/data/invertible.py:10`），把每次应用的变换记入历史，是可逆变换与测试时增强的基础。
- **`AffineMatrix`**（`src/torchio/data/affine.py:20`）封装 4×4 体素→世界坐标仿射矩阵，提供 spacing/origin/direction 属性与求逆、复合运算；`validate_axes`（`src/torchio/data/axes.py:50`）负责 LPS/RAS 与解剖轴记号（'A'/'P'/'L'/'R'…）的解析。**方向搞反是医学影像的经典事故源**——左右翻转的脑图在视觉上几乎察觉不出，却能让病灶定位错边，这两个小模块因此是全库正确性基石，值得逐行读。`PatchLocation`（`src/torchio/data/patch.py:11`）则描述 patch 在体积内的角点索引。

为什么是 Image/Subject 两级容器而不是一张大方阵？因为医学影像的"样本"天然是多模态复合体：同一个受试者的 T1、T2、FLAIR、分割标签是不同数值类型（强度 vs 整数标签）、常常不同分辨率，却必须共享同一套空间坐标做同步增强。Image 承载单卷及其几何，Subject 承载"一个人的一次检查"并担保几何一致，训练管线里再由 Batch（第 4 节）升维成张量批——三级各司其职，是这个库最值得借鉴的领域建模。

### 3.2 Transform 三层继承体系

变换体系的根在 `src/torchio/transforms/transform.py`，三层结构清晰：

第一层是**基类 `Transform(nn.Module)`**（`transform.py:69`）。它最关键的设计是输入归一化：`transform.py:194-212` 连续十个 `forward` 签名（九个类型化重载加一个 `Any` 兜底）把 Subject/Image/Tensor/ndarray/SimpleITK/Nifti1Image/dict/ImagesBatch/SubjectsBatch 任意输入统一包装成批处理再分派——用户永远只调 `transform(x)`，不必关心内部包装。基类还内置 `_TRANSFORM_REGISTRY` 自动登记子类（`transform.py:47`）、`AppliedTransform` 历史记录与参数序列化（`transform.py:30`）、Hydra 配置导出与 include/exclude 作用域声明。

第二层是**语义分支**：`SpatialTransform`（`transform.py:668`）作用于受试者内全部图像并同步变换点/框标注；`IntensityTransform`（`transform.py:677`）只作用于 ScalarImage、跳过 LabelMap 与注释。二者是写新变换时选择父类的分岔口。

第三层是**具体变换**：空间层 14 个文件加强度/标签层 23 个文件。注意一个反直觉事实——**Crop/Pad/CropOrPad 有独立文件**（`crop.py:34`、`pad.py:37`、`crop_or_pad.py:381`），但 **Resample/Affine/ElasticDeformation 没有独立源文件**，全在统一引擎 `spatial.py` 里（详见 3.4 与第 8 节）。

编排与随机性在框架层解决：`Compose` 顺序流水线、`OneOf` 随机选一、`SomeOf` 随机子集（`compose.py:38/101/184`），后两者支持批内逐实例独立选择；`get_inverse_transform` 与 `apply_inverse_transform`（`src/torchio/transforms/inverse.py:15/64`）配合 Subject 的历史实现精确求逆。随机参数被统一为"标量/范围/Choice/分布"四形态，由 `_ParameterRange`（`parameter_range.py:143`）与 `Choice`（`parameter_range.py:27`）承载。**v2 已彻底取消 Random* 前缀**：随机性不再靠类名表达，而是在构造参数里显式给范围（如 `Affine(degrees=(-10,10))`），每个批内实例独立采样——这一设计正是第 5 节向量化等价门禁存在的原因。

### 3.3 backends：多格式读写

医学影像格式高度碎片化（NIfTI、DICOM 系列、NRRD、MHA、远程 zarr……），TorchIO 用一条分层读写链抹平差异。`src/torchio/data/backends.py` 定义惰性后端体系：协议 `ImageDataBackend`（`backends.py:110`）约定读切片接口，三个内置实现分别是 `TensorBackend`（161，内存张量）、`NibabelBackend`（207，支持内存映射）、`ZarrBackend`（323，分块惰性读取）；Image 类经 `BackendRequest`（`backends.py:376`）与后端解耦，`register_backend`（`backends.py:434`）开放注册表让用户接入私有格式（how-to `docs/how-to/custom-reader.md` 有完整配方）。上游读写分派在 `src/torchio/data/io.py`：`resolve_source`（`src/torchio/data/io.py:31`）把本地路径与远程 URI 统一解析，读者函数 `read_nibabel`（125）、`read_sitk`（148，经 SimpleITK 覆盖上百种格式）、`read_nifti_zarr`（191）按探测结果分派。根级 `src/torchio/io.py` 另管一类小众 IO——变换矩阵文件（ITK .tfm、NiftyReg .txt）的读写与 LPS↔RAS 约定转换。

### 3.4 Queue/GridSampler：大体积分块

医学影像动辄数百 MB 装不进显存，TorchIO 的答案是 patch 化：训练与推理都不整卷进出，而是切块处理。**采样器族**在 `src/torchio/data/sampler.py`：`GridSampler`（`sampler.py:70`）生成稠密网格覆盖整个体积，用于推理不漏块；训练侧则是 `UniformSampler`（171，均匀随机）、`WeightedSampler`（226，按概率图加权）、`LabelSampler`（288，以标签为中心采样，保证 patch 含前景）。**`PatchAggregator`**（`src/torchio/data/aggregator.py:12`）负责反向拼装：重叠 patch 以 crop/average/hann 三种模式融合，把分块输出拼回完整体积。**`Queue`**（`src/torchio/data/queue.py:23`，`__init__` 在 65）是 `IterableDataset` 子类：把"加载 subject→增强→采样 patch"整条链放到后台线程执行，以 `max_length` 为内存上限缓冲产出（docstring `queue.py:24-27`），对训练循环而言就是一个普通可迭代数据源，无缝接入 PyTorch DataLoader。

### 3.5 空间统一引擎 spatial.py（选读）

`src/torchio/transforms/spatial/spatial.py` 是全库最重的单文件（2762 行）：`Spatial` 全功能类（`spatial.py:158`）把重采样、全局仿射、弹性形变合并进**单次 grid_sample 调用**（`spatial.py:4` 的 docstring 自述这一设计），`Resample`（759）、`Affine`（806）、`ElasticDeformation`（872）三个便捷子类只是它的参数预设。合并的意义是性能与精度：连续空间变换若各自独立重采样，会累积多次插值误差；统一引擎一次构网格一次插值，还配套了抗混叠与部分体积标签重采样。理解这个文件需要较强的坐标几何功底，新人可先跳过，用到再回来。

## 4. 数据流与典型调用链

训练管线的标准流向（官方完整示例在 `docs/tutorials/first-pipeline.md`）：

```
SubjectsDataset 列表 ──transform(增强)──▶ Queue(queue.py:23, 后台线程采样 patch)
      │                                          │
      ▼                                          ▼
SubjectsLoader(loader.py:39, collate_subjects 在 loader.py:15)
      │ 聚合为
      ▼
SubjectsBatch(batch.py:124; 张量批为 ImagesBatch batch.py:21)
      │ Transform.forward(transform.py:212) 统一入口
      ▼
model(batch.t1.data) —— 训练循环
```

逐步解读：先用数据集类或手写列表准备 Subject 序列并挂上增强 transform；交给 `Queue` 后，后台线程逐个加载并增强 subject、按采样器抽取 patch 缓冲；`SubjectsLoader`（`loader.py:39`）用自定义 collate（`collate_subjects`，`loader.py:15`）把样本聚合成 `SubjectsBatch`（`batch.py:124`）；变换经统一 `forward` 入口（`transform.py:212`）作用其上；最后模型消费 `batch.t1.data` 这类字段式张量访问。**关键边界在 `batch.py`**：`ImagesBatch`（`batch.py:21`）持有 `(B,C,I,J,K)` 张量与逐样本 affine，是"单样本世界与张量批世界"的交界，全部变换经它处理批量输入（fan-in 56）；推理路径用 `ImagesLoader`（`loader.py:66`）与 `collate_images`（`loader.py:27`）。生态适配上，`MonaiAdapter`（`src/torchio/transforms/monai_adapter.py:22`）与 `CornucopiaAdapter`（`cornucopia_adapter.py:19`）把第三方库的 callable 包装成本库 Transform，经 MetaTensor 桥接两套元数据体系，适配后的变换可混入同一 Compose 管线——既有 MONAI 工程可渐进式采用 TorchIO 的 IO 与 patch 设施（配方在 `docs/how-to/monai.md`）。

## 5. 测试与质量体系

- **规模**：`tests/` 下 69 个 .py（含 conftest/__init__），即 67 个测试模块，与图谱 L6-L8 三个测试层一一对应（data 23、spatial 12、intensity+framework 34）。
- **向量化等价门禁**是 v2 质量体系的精髓。`tests/conftest.py:17` 定义 `assert_vectorized` fixture；`tests/test_vectorization.py:1` 的开头 docstring 讲明语义——"applying the transform to a batch produces, for every element, the same result as applying the element's own parameters to that element alone"，即批量执行结果必须与"逐元素施加各自采样参数"严格逐体素等价，任何跨元素污染或广播错误都会当场失败。参数化入口 `test_vectorization.py:46` 覆盖 Ghosting/Spike/Blur/BiasField/Flip/Motion/Swap/Anisotropy 八个变换；在 `apply_transform` 内部自行采样的 Noise/LabelsToImage 被显式排除、由各自测试覆盖。这个门禁守护的正是 3.2 节"逐实例随机参数+向量化执行"架构的正确性，改任何变换实现都必须过它。
- **集成测试面广**：`test_hydra.py:8`（TestToHydra，变换参数导出为 Hydra 配置并回放）、`test_remote_zarr.py:20`（TestIsRemoteNiftiZarr，远程 zarr URI 判定）、`test_monai_adapter.py`（MONAI 互操作）、`test_remote_loading.py`（fsspec 远程读取）、`test_device.py`（GPU）、`test_cli.py`（命令行冒烟）。单测层面 `test_image.py:413`（TestSimpleITKReader）等用 SimpleITK 现场写临时文件再读回，真实模拟磁盘 IO 与多格式后端，而非内存里造张量自欺。
- **真实影像夹具**：`tests/image_data/dicom/` 存有 17 张 DICOM 小体量影像——但注意它们目前是孤儿，详见第 8 节勘误。
- 本地复现 CI：pytest 配置在 `pyproject.toml`，`slow` marker 区分全量与快速（CI 在 push 时只跑非 slow，定时任务跑全量）。本地一条 `tox -e test` 即可复现 CI 的测试环境，改了变换实现后先跑 `tox -e test -- tests/test_vectorization.py` 再跑全量，能最快定位向量化回归；提交前 `tox -e lint,format,types` 过三关静态检查，与 `.pre-commit-config.yaml` 的钩子同源。

## 6. 构建发布与 CI

- **tox 编排七个环境**：`tox.ini:2` 的 envlist 为 test/lint/format/types/docs-test/docs-build/prek，另有 coverage（`tox.ini:16`）、types（38）、docs-build（51，执行 `zensical build`）；依赖组直读 pyproject 的 dependency_groups，工具链锁定用 uv。
- **构建后端是 uv**（`pyproject.toml:81-82`，`uv_build`），v2 现代化的一环。运行依赖共 14 条（`pyproject.toml:38-51`：torch/nibabel/simpleitk/einops/fsspec[http]/tyro/loguru 等），可选 extras 九组（`pyproject.toml:64` 起：cornucopia/plot/niivue/video/monai/s3/azure/gcs/zarr）。**zarr 被 capped 在 `<3.2`**，原因注释在 `pyproject.toml:73-77`：nifti-zarr 1.0.0rc6 对 zarr≥3.2 新引入的 PEP 695 类型别名做 isinstance 会抛 TypeError，只能等上游适配——装环境遇版本冲突时先想到这里。
- **CLI 工具**：入口 `torchio = "torchio.cli:main"`（`pyproject.toml:62`，tyro 驱动），子命令 Plot/Animate/Info/Convert（`src/torchio/cli.py:25/52/99/111`），装好包即可在终端查看、绘制、转换影像而无需写 Python。
- **CI 实为五条 workflow**：`tests.yml`（测试矩阵 Python 3.10-3.14 × 三 OS，`tests.yml:24`；每日 cron `0 4 * * *` 跑全量含 slow，`tests.yml:10`；覆盖率上传 Codecov）、`docs.yml`（文档站预览与部署）、`publish.yml`（PyPI 发布）、`code_quality.yml`、`check_pull_request_title.yml`。注意：**.github 目录共 12 个文件**（5 条 workflow 加 codecov/dependabot 配置与 issue/PR 模板），图谱层描述"12 个 CI workflow"把模板也计入了——对外引用请说 5 workflows。
- **文档站**：`zensical.toml:2`（site_name）加 nav 五区（`zensical.toml:17`），API 页由 mkdocstrings 从源码 docstring 自动生成——**改 docstring 即改文档**，这就是源码里 docstring 写得极详尽（嵌 mkdocs 语法链接、含 doctest 风格示例）的原因；改公共 API 时同步更新 docstring 是硬要求，否则文档站与代码漂移。

## 7. 新人路线图（图谱 tour 前 5 步）

16 步导览的前五步构成一条从外到内的渐进线：

1. **Step 1 项目概览**：读 `README.md`（增强 GIF 矩阵与 Queue 示意在 `README.md:204`）→ `docs/index.md` → `docs/concepts/data-model.md`。概念页开篇即给出五大核心类（`data-model.md:3`：Image/Points/BoundingBoxes/Subject/AffineMatrix）的 mermaid 类图，是后续所有代码步骤的语义底座。过关标准：能回答"TorchIO 解决什么问题、两大核心抽象分别叫什么"。
2. **Step 2 安装与 CLI**：`docs/get-started/installation.md` 加 `quickstart.md` 走最短路径；装好后玩 `torchio` CLI（Plot/Animate/Info/Convert，`cli.py:25` 起）建立体感；环境疑难用 `print_system.py` 收集诊断信息贴 issue。
3. **Step 3 包门面**：`import torchio as tio` 背后就是 `src/torchio/__init__.py`（fan-in 85 全库最高），把它当公开 API 清单通读一遍；再看 `types.py` 类型别名与 `external/imports.py` 可选依赖惰性导入（缺失时报错并提示该装哪个 pip extra）。
4. **Step 4 读写链**：`src/torchio/data/io.py:31`（resolve_source）→ `backends.py:110`（协议）→ 三个内置后端；动手做 how-to `custom-reader.md`（接入私有格式）与 `remote-nii-zarr.md`（远程 zarr 存储）两个练习。
5. **Step 5 Image 深读**：`image.py:104` 加 `affine.py:20` 加 `axes.py`，配概念页 `docs/concepts/lazy-loading.md`——方向语义（LPS vs RAS、解剖轴记号）必须在这一步吃透，后面所有空间变换都建立在它之上。

之后按 tour 顺延：Step 6 Subject 与可逆簿记 → Step 7 采样分块（配 `docs/tutorials/large-volumes.md` 与 `docs/how-to/patch-inference.md`）→ Step 8 Queue 训练管线 → Step 9-11 变换三层（框架/空间/强度标签）→ Step 12 生态适配器 → Step 13 公开数据集 → Step 14 测试体系 → Step 15-16 文档与工程外环。**第一周可量化的目标**：跑通 `first-pipeline.md` 的完整训练示例，并用 `tio.datasets.Colin27()`（`src/torchio/datasets/mni/colin.py:29`）加载真实脑模板肉眼 plot 一张三正交切面图。

## 8. 已知坑与勘误（图谱实证发现）

1. **codecov.yml 是 v1 时代遗留**：`.github/codecov.yml:6-9` 的 ignore 列表写着 `"setup.py"`、`"torchio/external/due.py"`、`"torchio/datasets"`、`"torchio/download.py"`——但仓库早已没有 setup.py，包也已迁到 `src/torchio/` 的 src layout，**这些路径前缀全部失配**，覆盖率 ignore 实际一项都不生效。若要修，需改成 `src/torchio/...` 前缀。
2. **docs/examples 六个示例脚本仍用 v1 API，直接跑必报错**：`plot_3d_to_2d.py:26-30` 用了 `tio.RandomFlip/RandomAffine/SubjectsDataset`，`plot_history.py:7/35` 用了 `torchio.utils.history_collate` 与 `tio.SubjectsDataset`，`plot_include_exclude.py:19-20` 用 RandomAffine/RandomBlur，`plot_custom_z_spacing.py` 与 `plot_video.py:63` 同病。对照事实：v2 门面 `src/torchio/__init__.py:98` 的 `__all__` 已无这些名字；改名总表在 `migration.md:111-127`（如 `RandomFlip→Flip`、`RandomGamma→Gamma` 共 17 行），`SubjectsDataset` 的移除与替代写法在 `migration.md:451`，`GridAggregator→PatchAggregator` 改名在 `migration.md:536`。这批脚本是文档站图库（gallery.py 驱动渲染）的素材，v2 正式发布前必须重写——也是新人练手的好入口。
3. **Affine/Resample 无独立源文件**：`src/torchio/transforms/spatial/` 目录里没有 affine.py 与 resample.py——统一引擎 `spatial.py` 内 `Spatial`（158）、`Resample`（759）、`Affine`（806）、`ElasticDeformation`（872）共享单次 grid_sample 路径。但 `docs/reference/transforms/` 下每个变换仍有独立文档页——**按文档页文件名猜源码路径会扑空**，从 `__init__.py` 的 import 链找才稳。
4. **17 张 DICOM 孤儿夹具**：`tests/image_data/dicom/IMG0001.dcm` 起共 17 张，图谱 fan-in 全为 0，全仓 grep 无任何测试引用——是 v1 时代 SimpleITK 多格式读取的遗留资产。图谱层描述称该目录有"各格式 .nii.gz/.nrrd/.img 与 medical_decathlon 数据"，与磁盘不符：**该目录现仅存 dicom 一个子目录**。现代测试已改为 SimpleITK 现场写临时文件（如 `test_image.py:413`），这批夹具可安全删除或留作 DICOM 后端实验材料。
5. **图谱计数小勘误三则**（引用图谱数字时先校正）：层 13 描述"12 个 CI workflow"实为 5 条 workflow/.github 共 12 个文件；tour 与层描述说"13 个运行依赖"实为 14 条（`pyproject.toml:38-51` 逐行可数）；枢纽摘要说 Transform 有"11 个 forward 重载"实为 10 个签名（`transform.py:194-212`）。
6. **v2 alpha 语义变化坑**：`Flip` 的 `flip_probability` 默认值从 v1 的 0.5 改为 1.0（`migration.md:131-133`）——从 v1 迁移的代码若依赖旧默认会静默变行为；改名后的增强变换在无参数时是确定性 no-op（`migration.md:15`），随机性必须显式给范围，这与 v1 "`RandomAffine()` 无参即随机"的心智模型完全相反。
7. **数据集层依赖联网**：`ixi_tiny()`（`src/torchio/datasets/ixi.py:60`）体量小、号称"医学影像界 MNIST"最适合练手，但所有数据集类都经 `download.py` 的 `download_and_extract_archive`（`src/torchio/download.py:153`）联网下载并做 MD5 校验——离线环境需提前备好缓存目录；MedMNIST 系列（`src/torchio/datasets/medmnist.py:62` 起）另依赖 medmnist 第三方包。

**避坑总纲**：本仓当前最大的认知陷阱是"v1 惯性"——教程、示例、旧代码里的 `ToCanonical/Random*/SubjectsDataset/GridAggregator` 名字在 v2 全部不存在或已改名，遇到 AttributeError 先查 `migration.md:111-127` 对照表再怀疑自己；其次是"文档页≠源码文件"（第 3 条）与"路径前缀失配"（第 1 条）两个导航陷阱。把这三条记住，新人在这个仓里基本不会迷路。

---

**字数口径**：不计空格总字符 ≈ 13511；纯汉字 ≈ 4019。（统计范围为正文全文，含表格与代码块，不含本行。）全文 file:line 行号锚共 93 处（唯一锚 86 个），全部经脚本对 commit `9b1be950` 逐条 grep 核实，路径可唯一定位、行号均在文件界内。
