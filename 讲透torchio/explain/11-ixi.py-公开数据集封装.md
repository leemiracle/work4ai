# 11 · `src/torchio/datasets/ixi.py`：公开数据集封装范式

## 一、角色定位

IXI（Information eXtraction from Images）是约 600 例健康被试的脑 MRI 公开数据集（module docstring `ixi.py:1-9`，CC BY-SA 3.0 许可）。本文件提供两个入口：`ixi()`（`ixi.py:26`）下载加载全量五模态（T1/T2/PD/MRA/DTI，数 GB），`ixi_tiny()`（`ixi.py:60`）是 566 例 T1+分割的小子集、全部图像 83×44×55（:65-67 docstring 数字）——官方定位"医学影像界 MNIST"，新人跑通 first-pipeline 的推荐数据。更重要的是它的**范式价值**：datasets 层 14 个文件（MNI 模板、Slicer、MedMNIST 等）全部复刻这里的"URL+MD5+下载解压+glob 装配 Subject"四段式，图谱中该层 fan-in 为 0（无模块反向依赖），是最安全的练手区。

## 二、内部结构

184 行，两公开函数四私有 helper 一组常量：

**常量区**（:90-102）：`_IXI_BASE_URL`（:90）模态名模板化（`IXI-{modality}.tar`）；`_IXI_MD5`（:93-99）五模态校验和字典；tiny 版走 Dropbox 直链（`_IXI_TINY_URL` :101）+ MD5（:102）。

**`ixi(root, download=False, modalities=("T1","T2"))`**（:26-57）：三段流——模态名校验（:48-51，必须属于 MD5 字典）、按需下载（:52-53）、目录存在性检查（:54-56，缺失即提示 `download=True`）后装配。**`download` 是显式 opt-in**，绝不明抢。

**`ixi_tiny(root, download=False)`**（:60-83）：同构瘦身版，返回带 `image`（ScalarImage）与 `label`（LabelMap）两个键的 Subject 列表（docstring `ixi.py:74-75`，构造在 :173-179）。

**下载 helper**：`_download_ixi`（:105-122）逐模态跳过已存在目录（:112-113 断点续传语义）、`NamedTemporaryFile` 中转 .tar（:116-118）；`_download_ixi_tiny`（:149-162）下载后把 zip 内 `ixi_tiny/image`、`ixi_tiny/label` 两目录上提再删壳（:159-162 的 rename+rmtree 重排）。两者都委托 `download_and_extract_archive`（`src/torchio/download.py:153`，下载→MD5 校验→解压一条龙，底层 `download_url` :48 与 `extract_archive` :113）。

**装配 helper**：`_load_ixi_subjects`（:125-146）是多模态对齐的范本——以第一模态的文件列表为骨架（:130 排序 glob），按 `_subject_id`（:183-184，文件名去末段）在其他模态目录找同名伴（:138 `glob(f"{sid}-{m}.nii.gz")`），**任一模态缺伴则整例丢弃**（:140-143 的 skip 逻辑）——宁可少样本不可错配对。`_load_ixi_tiny_subjects`（:165-180）用 `zip(..., strict=True)`（:172）强约束 image/label 文件数一致，找不到文件给修复指引（:168-170 "Remove root and try again"）。

## 三、外部连接

- **上游**：`ScalarImage`/`LabelMap`（:19-20）、`Subject`（:21，`subject_id` 作为元数据随构造传入 :177）、`download_and_extract_archive`（:22）、`TypePath`（:23）。
- **下游**：`datasets/__init__.py:7-8` re-export 两函数并列入 `__all__`（`datasets/__init__.py:35-36`）；用户侧 `tio.datasets.ixi_tiny(...)`。图谱 in 边仅此一条——典型的依赖图顶层。
- **同层对照**：`mni/colin.py:29`（Colin27 模板，ONBOARDING Step 1 推荐加载）是单文件数据集的更简形态；`medmnist.py:62` 起六个 3D 数据集依赖第三方 medmnist 包；`download.py`（12 个消费者，fan-in 12）是全层共享的下载设施。
- **测试**：数据集类因依赖联网多为文档驱动，离线单测集中在 `download.py` 的校验和逻辑。

## 四、数据流

`subjects = tio.datasets.ixi_tiny("~/data/ixi_tiny", download=True)` 走读：

1. `download=True` → `_download_ixi_tiny`（:149）：目录已存在直接返回（:150-151，幂等）；否则 Dropbox 下载 zip → `download_and_extract_archive`（:153-158）内部先 MD5 校验（`download.py:39` `check_integrity`）再解压。
2. 目录重排（:159-162）：`ixi_tiny/image`→`root/image`、`ixi_tiny/label`→`root/label`，删空壳。
3. `_load_ixi_tiny_subjects`（:165）：双侧排序 glob（:166-167）→ `zip strict=True`（:172）逐对构造 `Subject(image=ScalarImage(img), label=LabelMap(lbl), subject_id=...)`（:173-179）——**全部惰性**，只是挂路径（02 篇），566 例瞬间返回。
4. 用户把列表交给 `tio.Queue(subjects, ...)`（04 篇）——首次真正读盘发生在 Queue 的后台线程 `subject.load()`（`queue.py:159`）。

全量版多一步配对过滤：T1 有而 T2 缺的被 skip（:140-143），返回数可能小于磁盘文件数。

## 五、设计决策（含批判）

**"函数返 Subject 列表"而非"torch Dataset 子类"** 是 v2 的关键转向：v1 的 `SubjectsDataset` 已移除（`migration.md:451`），现在数据集函数只负责"把磁盘文件变成 Subject 列表"，批处理/迭代交给 Queue+Loader 组合——数据获取与训练管线彻底解耦，列表还能随意 filter/shuffle/切分。

批判四点。其一，**MD5 硬编码是双刃剑**：防篡改防静默损坏，但上游文件一变（IXI 服务器重打包）全网用户同时炸，且错误信息只有 checksum mismatch 无修复指引。其二，**Dropbox 直链寿命堪忧**（:101）：`?dl=1` 分享链是 tiny 版单点故障，离线环境文档建议预缓存（ONBOARDING 坑 #7）但没有镜像机制。其三，`_download_ixi_tiny` 的目录重排（:159-162）假设 zip 内部结构固定，上游改打包布局即 KeyError；且 rename 跨设备时会失败（shutil.move 才稳）。其四，多模态 skip 逻辑（:140-143）静默丢样本——数据集规模缩水没有日志提示，统计训练集大小时要自己重新数，`len(subjects)` ≠ 官方标称 566/600 可能由此而来。

## 六、新人提示

1. 第一次跑：`subjects = tio.datasets.ixi_tiny(root, download=True)`，然后 `subjects[0].plot()` 肉眼检查 image/label 对齐——这是验证下载完整性的最快方式。
2. 离线/内网环境：在有网机器跑一次 `download=True`，把整个 root 目录打包搬运；`download=False` 时函数只做装配。
3. 想只拿 T1：`ixi(root, modalities=("T1",))`；混合模态注意返回样本数按"全模态齐备"过滤（:140-143）。
4. 给库加新数据集就照抄本文件四段式：常量（URL+MD5）→ 下载 helper（幂等+校验）→ 装配 helper（排序 glob+配对）→ 公开函数（opt-in download）；装配完在 `datasets/__init__.py` 登记 re-export 与 `__all__`。
5. `subject_id` 元数据（:177）可用于按被试切分训练/验证集——先按 id 分组再切，避免同一被试跨集泄漏。
