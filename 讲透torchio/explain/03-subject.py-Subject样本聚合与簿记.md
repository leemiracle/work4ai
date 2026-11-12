# 03 · `src/torchio/data/subject.py`：Subject——样本聚合与可逆簿记

## 一、角色定位

`Subject`（`subject.py:25`，混入 `Invertible`）回答一个领域建模问题：医学影像的"一个训练样本"不是一张图，而是**同一受试者的一次检查**——T1、T2、FLAIR、分割标签是不同数值类型、可能不同分辨率，却必须共享同一套世界坐标做同步增强。Subject 把多张 `Image` 连同 `Points`（`src/torchio/data/points.py:20`）、`BoundingBoxes`（`src/torchio/data/bboxes.py:207`）与任意标量元数据聚合成一个对象，并担保各图像的空间一致性。图谱 fan-in 27：Queue、全部变换、datasets、loader 都以它为流通货币。文件尾部 `Study = Subject`（`subject.py:367`）提供 DICOM 术语别名。

## 二、内部结构

367 行，一个主类加别名，按协议方法分组：

**构造与分类**：`__init__`（`subject.py:59`）遍历 kwargs 按 isinstance 把条目分进四个私有 dict——`_images`/`_points`/`_bounding_boxes`/`_metadata`（分类循环 `subject.py:65-73`），全空才报 `ValueError`（`subject.py:75-77`），并初始化 `applied_transforms` 历史（`subject.py:83`）。注意：**docstring 声称 "At least one Image must be provided"（`subject.py:36`），但代码只要求"至少一个条目"**——`tio.Subject(age=45)` 这种纯元数据 Subject 是合法的，文档比代码严。

**访问协议**（这是它"伪 dict"体验的全部来源）：`__getattr__`（:87）按 images→points→bboxes→metadata 顺序查找属性；`__getitem__`（:98）双语义——str 查条目（:129-133），int/slice/tuple 触发**空间切片** `_spatial_slice`（:135 → :299）：所有图像加 `slice(None)` 前缀后同参切片（:326），点/框/元数据原样带入新 Subject（:328-331），历史列表也拷贝（:333）；`__contains__`（:137）、`__iter__`（:147，只迭代三类空间数据）、`__len__`（:152）。

**一致性属性**：`spatial_shape`/`shape`/`spacing`（:163/:169/:175）全部先过 `_check_consistent_attribute`（:277，`np.allclose` 逐对比较在 :295）再取第一张图的值——**一致性校验是惰性的，发生在属性访问时而非构造时**；`device`（:181）聚合三类条目的设备并校验一致；`images`/`points`/`bounding_boxes` 三个只读 dict 属性（:201/:206/:211）。

**双层标注汇聚**：`all_points`（:215）与 `all_bounding_boxes`（:232）把 subject 级与 image 级标注合并成一个大 dict——subject 级用 str 键，image 级用 `(image_name, annotation_name)` 二元组键（:227-229），空间变换正是靠它们同步变换全部标注。

**操作与表示**：`load`（:251）逐图加载；`to`（:256）递归迁移设备/dtype 并原地返回；`_first_image`（:274）；`__repr__`（:336）一行摘要；`_repr_html_`（:346）接 Jupyter 表格；`plot`（:352）接 matplotlib 网格。

## 三、外部连接

- **上游**：`Image`（:17）、`Points`/`BoundingBoxes`（:16/:19）、`Invertible`（:18，提供 `get_inverse_transform` `data/invertible.py:22`、`apply_inverse_transform` :49、`clear_history` :73——簿记能力的真正实现在这个 mixin）。
- **下游**：`Queue._prepare` 直接对它 load+transform（`queue.py:157`）；`transforms/transform.py` 的 `_wrap` 把单 Subject 升级为 `SubjectsBatch.from_subjects([data])`（`transform.py:502`）；`datasets/ixi.py:145` 用它装配数据集条目；`SubjectsBatch.unbatch` 又把它拆回来。
- **测试**：`tests/test_subject*.py` 系列挂在图谱该节点；一致性校验的失败分支（`subject.py:296` 的 RuntimeError）由形状不匹配用例覆盖。

## 四、数据流

以多模态增强链为例：

1. `sub = tio.Subject(t1=ScalarImage(...), seg=LabelMap(...), age=45)` → 四 dict 分类完成，无 IO。
2. `sub.spatial_shape` → `_check_consistent_attribute("spatial_shape")`（:277）逐图比对——若 T1 与 seg 网格不同当场报 `Inconsistent spatial_shape`，这是多模态配准错误的第一道闸门。
3. `transform(sub)` → `Transform.forward` 把它包成批（`transform.py:502`），`SpatialTransform` 对批内全部图像应用同一几何，并经 `all_points`/`all_bounding_boxes`（:215/:232）同步标注；变换记录 append 进 `applied_transforms`（`transform.py:244`，历史实际存批上，unbatch 时随 Subject 带走）。
4. `sub[80:180, :, :]` → `_spatial_slice`（:299）每张图同参切片、affine origin 由各 Image 自己修正（见 02 篇），产出携带历史的新 Subject。
5. `apply_inverse_transform`（`invertible.py:49`）读 `applied_transforms` 倒序回放，实现测试时增强。

## 五、设计决策（含批判）

**"伪 dict"协议方法组**替代了 v1 的 `dict` 子类：v1 里 Subject 继承 dict，`.get()`/`.keys()` 全可用但与属性访问两套语义打架；v2 改为普通类 + 显式协议方法，类型更清晰，代价是老代码里 `subject.keys()` 之类调用全部失效（迁移表 `migration.md` 有对照）。

批判三点。其一，**文档与代码的松紧不一致**（`subject.py:36` vs :75）会在边界情况反咬：纯元数据 Subject 能构造，但 `_first_image`（:274）在空 images 上抛 StopIteration 而非友好报错——`spatial_shape` 等属性对它不可用。其二，**一致性校验惰性且只查三个属性**：shape/spacing 一致不保证 direction/origin 一致，斜向采样的两卷可以 shape、spacing 全等而方向不同，同步增强仍会错位；严格场景需自行比对 affine。其三，`__getattr__`（:87）对下划线开头直接抛错是好习惯，但元数据键与真实属性同名时会静默遮蔽元数据——命名时避开 `data`/`shape` 等保留名。

## 六、新人提示

1. 构造参数名就是访问名：`t1=tio.ScalarImage(...)` 之后用 `sub.t1` 或 `sub["t1"]`；元数据（年龄/性别）也走同一入口。
2. 遇到 `Inconsistent ...` RuntimeError 先检查各模态是否在**同一空间**（配准+重采样到公共网格），而不是简单删校验。
3. `sub[10:20, 30:60]` 切的是空间维 `(I, J, K)`（`subject.py:107-112`），通道维自动保留——与 Image 切片（含通道维）语义不同，别混。
4. 标注既可以挂 subject 级也可以挂 image 级（构造时传给 `tio.Subject(...)` 或 `tio.ScalarImage(points=...)`），空间变换都会处理，但 `all_points` 的键形态不同（str vs 二元组）。
5. 可逆链路的三件套都在 `Invertible`（`data/invertible.py`）：`get_inverse_transform`/`apply_inverse_transform`/`clear_history`；对增强后的预测图回填历史再做逆变换即得 TTA（配方 `docs/how-to/tta.md`）。
