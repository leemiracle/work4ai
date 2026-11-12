# 02 · `src/torchio/data/image.py`：Image——体素、affine 与惰性加载

## 一、角色定位

`Image`（`image.py:104`，继承 `Invertible`）是全库的心脏数据结构：把四维张量 `(C, I, J, K)`、4×4 affine 仿射矩阵、任意元数据与点/框标注打包成单一对象。它最重要的身份是**惰性加载器**——类 docstring 明言 "data is only read from disk when first accessed"（`image.py:107-109`）。医学影像单卷动辄数百 MB，惰性意味着遍历数据集统计 shape/spacing 时零磁盘读取，只有真正访问 `.data` 才落盘读入。图谱中 fan-in 41：subject、全部空间/强度变换、可视化、Jupyter 富文本都依赖它。

两个语义子类只是空壳：`ScalarImage`（`image.py:1238`）表示强度数据、`LabelMap`（`image.py:1251`）表示分割标签——变换层用 `isinstance` 区分二者（如 `LabelMap` 强制最近邻插值，`src/torchio/transforms/spatial/spatial.py:1230` 附近按 `_image_class` 分派插值模式），因此选错子类会直接改变变换行为。

## 二、内部结构

1261 行，四段式：

**构造与分派**：`__init__`（`image.py:173`）先初始化公共状态（`_data=None`、`_backend=None`、`_affine`、`applied_transforms=[]` 于 `image.py:204`），再把 source 交给 `_dispatch_source`（`image.py:211`）按类型路由：Tensor/ndarray 急加载（`image.py:222` → `_init_from_tensor` `image.py:240`）；`nib.Nifti1Image` 挂 NibabelBackend 懒加载（`image.py:224` → `image.py:256`）；SimpleITK 急转张量（`image.py:227` → `image.py:260`）；bytes/BytesIO 走临时文件（`image.py:228` → `_init_from_bytes` `image.py:284`，读完即删）；远程 zarr URI 只存字符串（`image.py:230`）；zarr Store 存引用（`image.py:232` → `_is_zarr_store` `image.py:310`）；其余路径/URL/file-like 统一经 `resolve_source` 落成本地 Path（`image.py:236`）。构造函数 docstring 里的分派表在 `image.py:119-127`。`_parse_tensor` 强制 4D（`image.py:322`，检查在 :327-329）。

**元信息属性（全部不触发整卷加载）**：`path`（:384）、`is_loaded`（:390）、`data`（:395，惰性触发点在 :397-398 的 `if self._data is None: self.load()`）、`affine`（:403，先问后端再兜底 load）、`dataobj`（:428，直接暴露后端做切片）、`shape`（:441，四级策略：内存→后端→zarr/路径→SimpleITK 头）、`spatial_shape`（:469）、`spacing`（:479，由 affine 派生）、`memory`（:489）、`dtype`（:495，未加载时读盘上 dtype）、`orientation`（:519）。

**加载与修改**：`load()`（:535）三步走——先试现有后端（`_try_load_via_backend` :560 → `_load_from_backend` :574），再对惰性 reader 创建后端，最后才走自定义 reader 全量读（:544）。`_reader_supports_lazy`（:550）判定 reader 能否提供后端：default reader 或实现 `LazyReader` 协议者。`set_data`（:590）换数据后用 `_refresh_backend_from_data`（:605）把后端换成 TensorBackend 保持一致。`to()`（:644）、`numpy()`（:658）、`new_like`（:670，保留元数据/标注/affine 的克隆工厂）、`save`（:699，zarr 走 `_save_nii_zarr` :744，其余走 SimpleITK `_save_sitk` :723，写前 RAS→LPS 转换在 :735）。

**切片与表示**：`__getitem__`（:832）双语义——str 查元数据（:876-880），索引则切片；关键在 `normalize_index`（backends.py:52）归一后走 `_slice_data`（:901）：**未加载时直接在后端上切**（:911-913），大卷切小区域不整卷入内存；切完把起点体素折算进 affine origin（`affine_matrix[:3, 3] += affine_matrix[:3, :3] @ start_voxel`，:897），几何始终正确。`__repr__`（:929）输出 spacing/origin/朝向角/内存占用的多行卡片；`__getattr__`（:1137）把未知属性代理到元数据；`__deepcopy__`（:1149）对路径源重挂路径（保持懒）、仅内存数据被 clone（`_deepcopy_from_source` :1193）。

## 三、外部连接

- **上游依赖**：`AffineMatrix`（`data/affine.py`）承载全部几何；backends 体系（`image.py:27-33` 导入 BackendRequest/ImageDataBackend/LazyReader/NibabelBackend/TensorBackend/normalize_index/resolve_backend，详见 09 篇）；`data/io.py` 的 `resolve_source`/`default_reader`/zarr 判定（`image.py:36-40`）。
- **被谁消费**：图谱 in 边 41 条——`subject.py` 聚合它；`transform.py` 与十余个强度/标签变换 import 它；`spatial.py`、`crop_or_pad.py` 等空间变换；`visualization.py`、`repr_html.py`（Jupyter 表格）；`datasets/ixi.py`、`medmnist.py` 构造数据集条目。
- **测试防线**：`tests/test_image.py`（880 行 18 个测试类）与 `tests/test_image_annotations.py` 直接挂在该节点上（graph out 边），其中 SimpleITK 现场写临时文件再读回（如 test_image.py:413 的 TestSimpleITKReader）保证 IO 真实性。

## 四、数据流

以 `img = tio.ScalarImage("t1.nii.gz"); patch = img[:, 50:100]` 为例走读：

1. 构造：`_dispatch_source` 把 Path 存入 `self._path`，零 IO。
2. `img[:, 50:100]` → `__getitem__`（:832）→ `normalize_index` 补齐为 4 个 slice → `self.shape`（:884）触发 `_ensure_backend`（:755）组装 `BackendRequest` 并 `resolve_backend` 得到 NibabelBackend（**只读 header**）。
3. `_slice_data`（:901）发现 `_data is None`，直接 `self._backend[sc, si, sj, sk]`（:913）——nibabel 的 dataobj 代理对 .nii 走内存映射、.nii.gz 走解压流，只取所需区域。
4. affine origin 修正（:897）后 `new_like`（:670）产出携带相同元数据的切片 Image。
5. 若用户随后访问 `patch.data`（:395）→ `load()`（:535）→ `_load_from_backend`（:574）`to_tensor()` 物化。

## 五、设计决策（含批判）

**三态状态机（无源/懒源/已物化）+ 后端协议**是本文件最核心的架构：`_data`、`_backend`、`_path/_remote_zarr_uri/_zarr_store` 三组字段的组合表达全部状态，属性访问器逐级降级（内存→后端→header→兜底加载）。收益是大体积影像的元数据操作零成本；代价是每个属性都要写四级分支——`shape`（:441-466）与 `dtype`（:495-516）的重复结构是明显的复杂度税，新增属性容易漏分支。

批判三点。其一，**`__getitem__` 的 str 语义偏隐晦**：`image["protocol"]` 查元数据与切片共用一个入口，对读代码的人是惊喜；v1 里 Image 曾是 dict 子类，这个设计是历史包袱的收敛但没收敛干净。其二，`_init_from_bytes`（:284）与 `_init_from_sitk`（:260）急加载、nibabel 源懒加载——同为"传入内存对象"行为却不同，边界情形多，好在 docstring 分派表（:119-127）写清了。其三，`save` 的写路径全押 SimpleITK（:723），与读路径 nibabel 优先不对称：.nii.gz 经 sitk 写回会重排轴序（:729 的 "1 i j k -> k j i"），跨库对读时 dtype/方向差异要靠 affine 兜底校验——官方教程因此建议"谁写的谁读"。

## 六、新人提示

1. 判断"有没有真读盘"只看 `is_loaded`（:390）；`print(image)` 的 repr（:929）会显示 `(lazy, NIfTI)` 或 `(loaded)` 状态行。
2. 切大卷请直接用 `img[a:b, c:d, e:f]` 而不是先 `.data` 再切——前者走后端懒切（:901-914），后者整卷入内存。
3. `ScalarImage` vs `LabelMap` 的选择会改变插值与强度变换的适用性，构造时就选对（`image.py:1238/1251`）。
4. 想接私有格式：优先写实现 `LazyReader.create_backend` 的 reader（`src/torchio/data/backends.py:402`），而不是只返回 `(tensor, affine)` 的简单 reader——后者永远整卷加载。
5. 调试几何问题时先打印 `image.affine` 与 `image.orientation`：切片不改方向只改 origin（:897），空间变换才动 direction。
