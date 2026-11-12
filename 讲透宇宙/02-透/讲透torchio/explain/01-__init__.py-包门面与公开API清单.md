# 01 · `src/torchio/__init__.py`：包门面与公开 API 清单

## 一、角色定位

这个文件是 `import torchio as tio` 背后的全部魔法：一个 193 行的纯门面（facade），不包含任何逻辑，只做两件事——把散落在 data/transforms/io/loader/types 各处的公开符号 re-export 到顶层命名空间，再用 `__all__`（`__init__.py:98`）钉死对外承诺的边界。图谱中它 fan-in 85 为全库最高：所有教程、测试、CLI（`src/torchio/cli.py:16` 的 `import torchio as tio`）与下游用户都从这里进来。它是新人最好的"API 地图"——通读一遍 `__all__` 的 92 个条目，就能知道这个库认为什么东西值得公开、什么东西刻意藏起来。

门面还是 v2 改名的最权威见证：这里的导入清单里已经找不到任何 `Random*` 前缀、`SubjectsDataset`、`ToCanonical`、`GridAggregator`——网上旧教程里的这些名字在 v2 全部不存在，凡 AttributeError 先对照 `docs/get-started/migration.md` 的改名总表，再对照本文件核对。

## 二、内部结构

> 消歧说明：仓内共有 11 个 `__init__.py`（data/transforms/datasets 等子包各有 barrel），本篇裸写的 `__init__.py:N` 一律指本篇主角 `src/torchio/__init__.py`；引用其他子包 barrel 时均带目录前缀（如 `datasets/__init__.py:7`）。

文件三个区块，无类无函数，纯声明式：

| 区块 | 行号 | 内容 |
|---|---|---|
| 元数据 | `__init__.py:1` | module docstring，一句话定位 "Medical image preprocessing, augmentation, and patch-based training" |
| 数据层导入 | `__init__.py:5-34` | `from . import datasets`（:5）起：容器（Image/ScalarImage/LabelMap，`__init__.py:14-16`）、采样与队列（Queue `__init__.py:19`、五个 Sampler `__init__.py:20-24`）、Subject/Study（`__init__.py:25-26`）、矩阵 IO（`__init__.py:27-28`）、loader 与 collate（`__init__.py:29-34`） |
| 变换层导入 | `__init__.py:36-85` | 约 50 个变换类按字母序导入：`Affine`（:37）、`Compose`（:44）、`Motion`（:62）、`Normalize`（:64）、`Resample`（:71）、`Spatial`（:76）、基类 `Transform`（:83）等；`__init__.py:86` 补 `apply_inverse_transform` |
| 类型别名 | `__init__.py:87-96` | 10 个 `Type*` 别名（TypePath/TypeSpacing 等） |
| 公开清单 | `__init__.py:98-191` | `__all__` 共 92 个字符串条目 |
| 版本 | `__init__.py:193` | `__version__ = version(__name__)`，经 importlib.metadata 读包元数据 |

一个值得注意的细节：`RescaleIntensity` 与 `ZNormalization`（`__init__.py:72/85`）不是独立类，而是 v1 兼容别名——`RescaleIntensity = Normalize`（`src/torchio/transforms/intensity/normalize.py:369`）、`ZNormalization = Standardize`（`src/torchio/transforms/intensity/standardize.py:178`）。同理 `Study`（`__init__.py:25`）只是 `Subject` 的别名（`src/torchio/data/subject.py:367`），DICOM 术语里 "study 包含 series" 与 Subject 语义同构，官方让用户自选叫法。

## 三、外部连接

- **上游**：`importlib.metadata`（版本号）；`.transforms` barrel（`src/torchio/transforms/__init__.py`，自身也是近百行的二级门面，从 compose/intensity/label/spatial 聚合）；`.datasets` barrel（`src/torchio/datasets/__init__.py:7-8` 暴露 `ixi`/`ixi_tiny`）。
- **下游**：fan-in 85 的消费者里最重的三块——`tests/` 全部测试模块的 `import torchio as tio`；`src/torchio/cli.py` 的六个子命令；`docs/` 里几乎所有示例代码。图谱 fan-out 17 指向其 re-export 的子模块。
- **同级**：`types.py`（别名本体）、`logging.py`（`enable_logging` 在 `__init__.py:35` 导出）、`external/imports.py`（可选依赖惰性导入，不直接出现在门面）。

## 四、数据流

门面本身无数据流，但用户的一次 `tio.ScalarImage("t1.nii.gz")` 全程借道这里导出的符号：

1. 用户 `import torchio as tio` → 解释器执行本文件，依次触发 `torchio.data`、`torchio.transforms` 等子包初始化（也就此加载 nibabel/SimpleITK/torch 等重依赖——首次 import 慢的原因）。
2. `tio.ScalarImage` 解析到 `__init__.py:16` 导出的 `data.image.ScalarImage`，构造惰性图像（详见 02 篇）。
3. `tio.Resample(1)` 解析到 `transforms.spatial.spatial.Resample`（`src/torchio/transforms/spatial/spatial.py:759`）。
4. `tio.SubjectsLoader`（`__init__.py:31` → `src/torchio/loader.py:39`）消费 `tio.Queue`（`__init__.py:19` → `src/torchio/data/queue.py:23`）产出的 patch 流。
5. `tio.apply_inverse_transform`（`__init__.py:86` → `src/torchio/transforms/inverse.py:64`）用 Subject 历史回放逆变换。

## 五、设计决策（含批判）

**纯 barrel 门面 + `__all__` 白名单**是科研库的成熟做法：用户 API 面收敛到一处、IDE 补全友好、`from torchio import *` 不会泄漏内部符号。92 个条目的规模控制得不错——对比某些把上百个类全倒出来的同类库，这里 `_ParameterRange`、`_wrap` 等内部件确实被拦在外面。

批判视角有三。其一，**别名双轨是债务**：`RescaleIntensity`/`ZNormalization`/`Study` 三组别名让文档、教程、错误栈可能出现两个名字指同一物，新人在 grep 源码时会困惑；v2 已经历一次大改名，这些"半改名"残留要么转正要么在 v2 正式版砍掉。其二，**门面无法表达结构**：92 个平铺条目看不出"容器/采样/变换/工具"的分层，全靠用户读文档（`docs/reference/` 页面按目录组织弥补了这一点）。其三，`from . import datasets`（`__init__.py:5`）在 import 时即拉起整个 datasets 子包，而数据集类都依赖 `download.py` 的联网设施——纯离线环境 `import torchio` 也要为它付出导入时间；不过 datasets 模块自身惰性（不下载），实际代价可控。

## 六、新人提示

1. 把 `__all__`（`__init__.py:98-191`）当目录通读一遍，遇到不认识的条目去 `docs/reference/` 查对应页——这是建立全库词汇表最快的方式。
2. 记住三条"名字陷阱"：`RescaleIntensity` 就是 `Normalize`；`Study` 就是 `Subject`；一切 `Random*` 都已改名（`Flip(degrees=...)` 类构造参数直接给范围）。
3. 改公共 API 时必须同步三处：实现文件、本门面导入与 `__all__`、`docs/reference/` 对应 mkdocstrings 页——漏一处就会出现"文档有、包里无"的幽灵 API。
4. `__version__` 来自安装元数据（`__init__.py:193`），在未安装的源码树里直接 `import torchio` 会抛 PackageNotFoundError——贡献者开发时用 `uv pip install -e .` 规避。
