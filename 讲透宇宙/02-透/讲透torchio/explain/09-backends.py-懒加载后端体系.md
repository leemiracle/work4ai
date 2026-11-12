# 09 · `src/torchio/data/backends.py`：懒加载后端体系（读写链）

## 一、角色定位

医学影像格式高度碎片化（NIfTI/DICOM 系列/NRRD/MHA/远程 zarr/云 URI），本文件提供抹平差异的**惰性数据访问层**：协议 `ImageDataBackend`（`backends.py:110`）约定统一契约，三个内置实现 `TensorBackend`（:161，内存张量）、`NibabelBackend`（:207，NIfTI 内存映射）、`ZarrBackend`（:323，分块远程读取）各包一种存储，注册表（`_BACKEND_REGISTRY` :431 + `register_backend` :434）对外开放扩展点。它与 `src/torchio/data/io.py`（下文裸写 `data/io.py`，区别于管仿射矩阵文件的包根 `src/torchio/io.py`）组成完整读写链：data/io.py 负责"源解析与格式探测"（`resolve_source` `data/io.py:31` 把 URL/fsspec/文件对象统一成本地路径；`default_reader` `data/io.py:177` 按 NIfTI/Zarr/SimpleITK 分派急加载读取），backends.py 负责"元数据与区域访问"（header 级 shape/affine/dtype 与懒切片）。02 篇的 Image 通过 `BackendRequest`（`backends.py:376`）与这层解耦。协议 docstring 自我定位很清醒（:115-117）：这是 I/O adapter 层不是惰性计算框架——加速元数据与切片，不延迟算术。

## 二、内部结构

**契约**（:109-158）：`@runtime_checkable Protocol`，五问契约写在 :119-129——`shape` 恒为 4D `(C,I,J,K)`（3D NIfTI 也补通道 1）、`affine` 是 float64 的 `(4,4)` 张量、`dtype` 报盘上 numpy dtype、`__getitem__` 接受与 `Image.__getitem__` 相同的索引且**永不降维**（整数索引保留 size-1 轴，:150）、`to_tensor` 物化全卷并尽量保 dtype。模块级 `normalize_index`（:52）把任意 int/slice/Ellipsis/元组归一成四个 slice 并右侧补全（:104-105），是全库索引语义的守门员。

**TensorBackend**（:161-204）：最简实现，包内存张量；`__slots__`（:172）省属性字典；`dtype` 用空张量换算 torch→numpy dtype（:197）；`to_tensor` 返回 clone（:204）而非引用——防御性拷贝。

**NibabelBackend**（:207-320）：核心懒实现。构造期只读 header：`get_data_shape` 归一 3/4/5D（:236-250，5D 是 SimpleITK 写出的 `(I,J,K,1,C)` 向量 NIfTI 特例，:244-247）；`affine` 从 `header.get_best_affine()` 取、可被 override 覆盖（:257-263，用户显式传 affine 时保持 view 一致）；`__getitem__`（:269-302）做布局翻译——磁盘 `(I,J,K)`/`(I,J,K,C)`/`(I,J,K,1,C)` 三形态映回 `(C,I,J,K)`（:279-290），底层走 `self._nii.dataobj[...]` 代理（:281/:285/:289，.nii 内存映射、.nii.gz 流式解压、zarr 经 dask 分块），只读请求区域；只读数组补 copy（:297-301，PyTorch 不接受只读 buffer）。它同时服务 NIfTI-Zarr——`zarr2nii` 返回的正是 dataobj 为 dask 数组的 Nifti1Image（docstring :214-216）。

**ZarrBackend**（:323-369）：纯委托壳，构造期 `niizarr.zarr2nii`（:350）后全转 NibabelBackend（:351-369），价值在于承接远程 URI 与 chunked 语义。

**解析与注册**（:372-577）：`BackendRequest` frozen dataclass（:375-398）携带 path/remote_zarr_uri/zarr_store/affine/reader 五要素，让 resolver 不依赖 Image 类；`LazyReader` 协议（:401-414）定义 `create_backend`——自定义 reader 实现它即可享受懒访问；`register_backend`（:434-462）带 `prepend=True` 优先级参数（:459，自定义后端默认插队首）与同名替换（:457）；`resolve_backend`（:475-489）顺序问询 matcher，无人认领返回 None（调用方回退急加载）；`_register_builtin_backends`（:557-574）按 custom-reader → remote-zarr → zarr-store → nifti-zarr → nifti 的顺序登记五个内置项，模块导入尾即执行（:577）。

## 三、外部连接

- **上游**：`data/io.py` 的探测函数（`is_nifti` `data/io.py:73`、`is_nifti_zarr` `data/io.py:79` 被 matcher 调用 :530/:545）；`external/imports.get_niizarr` 惰性引入可选依赖（:347/:522）。
- **下游**：`Image._ensure_backend`（`image.py:755`）组装 BackendRequest 并 resolve；`Image.shape/dtype/dataobj/__getitem__` 的全部懒路径落到后端；`tests/test_backends.py` 直测本层；`docs/concepts/lazy-loading.md` 讲三态状态机、`docs/how-to/custom-reader.md` 是扩展配方。
- **写链对偶**：data/io.py 只有读（`read_nibabel` `data/io.py:125`、`read_sitk` `data/io.py:148`、`read_nifti_zarr` `data/io.py:191`）；写经 `Image.save`（`image.py:699`）走 SimpleITK/niizarr——读 nibabel 优先、写 SimpleITK 优先的不对称是刻意的（nibabel 懒、SimpleITK 格式广）。

## 四、数据流

远程 zarr 流式读取 `tio.ScalarImage("https://.../t1.nii.zarr")` 全链：

1. Image 构造：`is_remote_nifti_zarr`（`data/io.py:84`）命中 → 存 `_remote_zarr_uri`（`image.py:230-231`），零网络请求。
2. 首次访问 `image.shape` → `_ensure_backend`（`image.py:755`）→ `BackendRequest(remote_zarr_uri=...)`（`image.py:768-775`）→ `resolve_backend`（:475）→ matcher 链：`_match_remote_zarr`（:504）命中 → `_build_remote_zarr`（:508）→ ZarrBackend → `zarr2nii` 只**拉元数据头**（shape/affine/dtype 就绪，体素数据未动）。
3. `image[:, 100:200]` → `NibabelBackend.__getitem__`（:269）→ dask dataobj 只读请求 chunk → `(1,100,J,K)` 张量返回。
4. 对照急加载路径 `tio.ScalarImage(tensor)`：TensorBackend 直裹（:161），`to_tensor` 才 clone。
5. 自定义格式（如 .npy）：按 `docs/how-to/custom-reader.md` 实现 LazyReader.create_backend → `register_backend("npy", matcher, factory)`（:434）→ 因 prepend 优先于内置被选中（:459-460）。

## 五、设计决策（含批判）

**协议 + frozen request + 注册表**三件套是教科书级开闭设计：加格式不动 Image 一行（docstring :445-446 明言），matcher 顺序即优先级。`BackendRequest` 的引入让 resolver 与 Image 双向解耦，测试可以纯函数式构造请求。

批判四点。其一，**ZarrBackend 是伪实现**：全委托 NibabelBackend（:353-369），独立类只为类型语义清晰；若未来 zarr 后端需要真分块策略（如预取），当前壳会掩盖扩展点。其二，`normalize_index`（:52）与 numpy/torch 原生索引语义有细微差异（永不降维），用户拿后端切片与拿 `.data` 切片形状不同——`Image.__getitem__` 统一了入口但底层差异仍在，混用会踩形状坑。其三，注册表是**模块级全局可变状态**（:431），测试间注册/注销（:465）若不清理会串场；prepend 默认 True（:439）让后注册者赢，多插件共存时顺序反直觉。其四，五问契约没有错误语义约定：matcher 误认领（比如扩展名恰好 .nii 的非 NIfTI 文件）会在 factory 深处抛 nibabel 的原始异常，用户看到的是底层报错而非"格式不支持"。

## 六、新人提示

1. 判断一个操作会不会读整卷：看它走不走 `to_tensor`（:156）——`shape/affine/dtype/__getitem__` 都是懒的，只有 `Image.load()`/`.data` 触发物化（02 篇 :395）。
2. 接私有格式的最短路径：简单版返回 `(tensor, affine)`（急加载、十几行）；进阶版实现 `create_backend`（:412）享受懒切——`docs/how-to/custom-reader.md` 两个版本都有完整代码。
3. 远程 IO 的坑都在网络层：fsspec 缓存、S3 凭据、断线重连不在本文件管辖，排障先查 `fsspec.open` 的报错与 `docs/how-to/remote-nii-zarr.md` 的 URI 写法（尾斜杠、query 参数，`data/io.py:86-88` 有清洗）。
4. 改后端契约（五问）时全库grep `_backend.`——Image 的四级属性分支（02 篇）与多个变换都直接摸后端，契约破坏面比看起来大。
5. `dtype` 契约是 numpy dtype（:143）：LabelMap 的 uint16 标签在后端层是 np.uint16，物化时经 `data/io.py:97-102` 的 `_NUMPY_DTYPE_PROMOTIONS` 升 signed（torch.from_numpy 不收 uint16）——标签值域变化要在这一步预期内。
