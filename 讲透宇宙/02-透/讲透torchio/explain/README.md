# 讲透 TorchIO · explain 系列索引（12 篇重要文件精讲）

> 版本锚定：torchio 仓 commit `9b1be950`（torchio 2.0.0a2）。配套：知识图谱 969 节点/1827 边/14 层/16 步 tour（0 issues）、`../onboarding/ONBOARDING.md`。本系列 12 篇按 tour 核心步骤选题，每篇六节结构：①角色定位 ②内部结构（类/函数地图+行号）③外部连接（imports/tested_by 邻居，取自图谱）④数据流（调用链走读）⑤设计决策（含批判视角）⑥新人提示。

## 篇目清单

| # | 文件 | 主题 | 不计空格字符 | 纯汉字 | 锚（带文件名/上下文） |
|---|---|---|---|---|---|
| 01 | `src/torchio/__init__.py` | 包门面与公开 API 清单（92 条 `__all__`、v2 改名见证、别名考古） | 3940 | 983 | 34 / 8 |
| 02 | `src/torchio/data/image.py` | Image：体素、affine 与惰性加载（三态状态机、懒切片、8 源分派） | 4652 | 1086 | 28 / 60 |
| 03 | `src/torchio/data/subject.py` | Subject：样本聚合与可逆簿记（伪 dict 协议、惰性一致性校验、Study 别名） | 3899 | 1027 | 19 / 36 |
| 04 | `src/torchio/data/queue.py` | Queue：随机 patch 训练缓冲（线程池流水线、背压、内存估算批判） | 3930 | 1022 | 13 / 41 |
| 05 | `src/torchio/data/sampler.py` | patch 采样器族与 GridSampler（推理 map-style/训练 iterable 双继承） | 4292 | 1062 | 18 / 45 |
| 06 | `src/torchio/transforms/transform.py` | 变换体系基座（10 个 forward 重载、逐实例参数体系、注册表） | 4515 | 1229 | 14 / 71 |
| 07 | `src/torchio/transforms/spatial/spatial.py` | 空间统一引擎（单次 grid_sample、A_in⁻¹@T⁻¹@A_out、label 部分体积） | 4798 | 1134 | 8 / 97 |
| 08 | `src/torchio/transforms/intensity/motion.py` | Motion：k 空间伪影与向量化范式（恒等占位+torch.where 还原） | 4736 | 1305 | 10 / 83 |
| 09 | `src/torchio/data/backends.py` | 懒加载后端体系（协议+注册表+三实现，含 data/io.py 读写链） | 4773 | 1136 | 17 / 55 |
| 10 | `src/torchio/cli.py` | CLI：tyro 驱动的六个子命令（含 `to_nifti_zarr` 缺失方法实锤 bug） | 3984 | 909 | 14 / 41 |
| 11 | `src/torchio/datasets/ixi.py` | 公开数据集封装范式（函数返 Subject 列表、MD5+幂等下载+配对装配） | 3753 | 1005 | 12 / 46 |
| 12 | `tests/conftest.py` | 向量化等价门禁（整批 vs 逐元素重放、rtol=0 逐位 no-op 断言） | 4099 | 1291 | 20 / 31 |
| — | 合计 12 篇 | | 51471 | 13189 | 207 / 614（共 821 处） |

## 字数口径说明（钉版）

- **验收口径 = 不计空格总字符**（`len(re.sub(r'\s','',text))`，含标题/表格/代码块/行号锚的全字符）：全系列单篇 3753-4798，均落在 2500-4800 要求区间。行号锚密度（每篇数十处 `file.py:NNN`）显著推高非空白字符占比，是本系列区别于普通科普文的特征。
- 纯汉字数（正则 `[一-鿿]`）另列仅供参考：单篇 909-1305。汉字占比 ~25-32% 属正常——代码标识符、路径、行号锚、英文术语按约定保留英文。
- 两口径差异 ~3.5 倍，引用字数时务必注明口径（沿袭 SB3/zoo 轮钉版经验）。

## 行号锚核验说明

全部 821 处行号锚经脚本对 commit `9b1be950` 逐条核验：带文件名的 207 处（`file.py:N` 或 `file.py:N-M`）做路径解析+行号界内检查，**0 悬空、0 越界**；上下文裸锚 614 处（`:N` 形式，指同句/同段刚提及的文件）按所在篇主角文件做界内检查并通过。多义文件已消歧：仓内 11 个 `__init__.py`（01 篇开头有消歧声明，裸写一律指 `src/torchio/__init__.py`，跨篇引用均带目录前缀）；`io.py` 在 09 篇统一写 `data/io.py` 以区别于包根 `src/torchio/io.py`；`spatial.py` 多类锚一律写 `spatial.py:N` 且行内容即类定义行，正文注明"类在头部/引擎在中部/解析在尾部"导航。

## 本轮增量实证发现（对 ONBOARDING 的补充勘误）

1. **CLI 实为六个子命令**：Plot/Animate/Info/Convert 之外还有 `Transform`（`cli.py:134`，任意变换施加）与 `Cache`（`cli.py:204`，内含 Dir/Clean）——ONBOARDING 第 6 节只列了四个。
2. **`cli.py:128` 调用不存在的 `Image.to_nifti_zarr`**：全仓 grep 唯一引用就是该调用点，`torchio convert a.nii.gz b.nii.zarr` 必抛 AttributeError；正确实现是私有 `_save_nii_zarr`（`image.py:744`），且 `Image.save`（`image.py:718`）本就按后缀自动分派——一行修复的理想 first PR。
3. **`RescaleIntensity`/`ZNormalization` 是 v1 兼容别名**：分别等于 `Normalize`（`normalize.py:369`）与 `Standardize`（`standardize.py:178`），非独立类。
4. **Subject 文档比代码严**：docstring 称 "At least one Image must be provided"（`subject.py:36`），但构造校验只要求"至少一个条目"（`subject.py:75`）——纯元数据 Subject 合法，空 images 下 `spatial_shape` 会以 StopIteration 而非友好报错收场。
5. **Motion docstring 与实现不符**：docstring 称段切分 "along a random axis"（`motion.py:40-41`），实现固定沿第一空间轴（`motion.py:365-366`）。
6. **Queue 的 `max_length` 非硬内存上限**：只约束 patch 缓冲，在途 futures 里还压着增强后的整卷副本；`max_memory` 估算只按 float32 patch 本体计。
7. **门禁理论盲区**：`_keep` 全灭时 forward 不写历史（`transform.py:235`），conftest 取 `applied_transforms[-1]`（`conftest.py:41`）会取到前一变换的记录——p=0.5 批 6 全灭概率约 1.6%，播种缓解但未消除。

## 阅读路线建议

按依赖梯度（与图谱 14 层一致）：01 门面 → 02/03 数据载体 → 09 读写链 → 05 采样 → 04 队列 → 06 变换基座 → 07 空间引擎（最重，可后置）→ 08 向量化范式 → 12 质量门禁收束；10 CLI 与 11 数据集是纯消费端，任意时间穿插。每篇六节中③外部连接给出的图谱 fan-in/fan-out 数字可帮助判断"改这里会波及谁"。
