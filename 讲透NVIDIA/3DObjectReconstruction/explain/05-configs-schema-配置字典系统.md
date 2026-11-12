# 05 · configs/schema.py — 配置 schema 唯一事实源

## ① 角色定位

`src/nvidia/objectreconstruction/configs/schema.py`（329 行）是整条重建管线的**配置声明中心**：感知、跟踪、SDF 训练、纹理烘焙各组件的默认值与嵌套结构全部以 `@dataclass` 树钉在这里。

先钉版一处甄别：任务书称"12 类配置字典"，源码实为 **19 个顶层 dataclass + 4 个嵌套（共 23 个 `@dataclass`，schema.py:10-329）**，configs/__init__.py:11-23 对外导出 11 个。更关键的定位事实：**仓内运行时消费点只有一处 re-export**（objectreconstruction/__init__.py:33）——真正执行链走 `yaml.load` 纯 dict（preprocessing.py:16-39；nvbundlesdf.py:174 收 `ConfigDict=Dict[str,Any]`）。它是**声明式契约 + 对外类型面**，不是运行时校验器。

## ② 内部结构

自底向上四组：

**感知叶子**（未注文件名的行号均指 schema.py）：`RoMaConfig`（:10-17，双权重路径）；`FoundationStereoConfig`（:26-38，scale=0.3、z_far=10、**自持内参与基线 0.0657696127**）；`SAM2Config`（:40-46，默认 bbox `[1144,627,2227,2232]` 即 retail_item 样本目标框）；`CameraConfig`（:20-24，step=4 帧步进、fx=3079.6 为 Qoocam 立体相机标定值）；`TextureBakeConfig`（:48-52）。

**BundleTrack 族**：`DepthProcessingConfig`（:60-90）内嵌 Erode(:65-69)/BilateralFilter(:73-79)/OutlierRemoval(:81-86) 三小类，把深度清洗链（截断→腐蚀→双边滤波→离群移除→百分位截断）整棵参数化；`BundleConfig`（:92-113）是 BA 核心（外/内迭代 7×5、窗口 5、Huber robust_delta=0.005）；另有 Keyframe/Sift/FeatureCorres/Ransac/P2P/SDFEdge/Shape 七个子配置（:115-176，Sift 匹配、RANSAC 内外参门槛、TSDF Shape 体素 0.005），由 `BundleTrackConfig`（:178-198）以 10 个 `field(default_factory=...)` 组装。

**NeRFConfig（:201-307，106 行全文件最大）**：分 12 个注释段——网络（netdepth=8）、训练（N_rand=2048 光线、双学习率均 0.01，:215-223）、采样（N_samples=64+around_depth=256，:225-230）、hash 编码（:247-251）、**八叉树组**（use_octree=1+四个 0.02 体素尺寸，:253-261）、场景（near=0.1/far=1.0，:263-269）、损失权重 20 项（:271-290）、网格提取+嵌套 `MeshSmoothingConfig`（:292-306）。

**根**：`BasePathConfig`（:309-314）三个 MISSING 路径；`NVBundleSDFConfig`（:316-329）以两个 MISSING + 8 个 default_factory 子树封顶。

## ③ 外部连接

上游仅标准库 + `omegaconf.MISSING`（schema.py:4-6）。下游两条 re-export 链（configs/__init__.py:11-23 与 objectreconstruction/__init__.py:33）。**不连接的**：cli 的 `validate_config_file`（cli/main.py:185）只查 yaml 六个 section 名，不实例化任何 dataclass；NVBundleSDF/NerfRunner 收到的都是 dict 切片。

## ④ 数据流

实流：`data/configs/base.yaml` → cli 校验 → 按顶层键切子 dict → `NVBundleSDF.__init__(config_nerf, cfg_bundletrack, roma_config, cfg_texture)`（nvbundlesdf.py:174）→ `config_nerf['save_dir']` 式逐键取用（nvbundlesdf.py:197）。schema 默认值与 base.yaml 是**两份平行维护的数值**：前者文档态默认，后者执行态默认。

## ⑤ 设计决策

1. **dataclass 而非 pydantic**：`from omegaconf import MISSING`（:6）说明本意为 OmegaConf structured 模式准备，但仓内未走到那步——选轻声明、放弃强校验。
2. **MISSING 只标运行时必注入的 5 个路径**（:180,207,312-314,319-320）；权重路径给容器内默认值——镜像中位置固定，不属于用户输入。
3. **BundleTrack 族不进公共导出面**：8 个子配置是 C++ BundleTrack 直系参数（注释直接引用 loss.cpp，:104），暴露即承诺兼容第三方内部行为。
4. **FoundationStereo 自持内参与基线**：立体深度尺度由（内参,基线）对决定，与 CameraConfig 分属两个传感器模型，混用直接产出尺度错误的深度。

## ⑥ 新人提示

- **改 schema 默认值 ≠ 改运行行为**：管线读 base.yaml，两份默认值无一致性测试守护，漂移时以 base.yaml 为准。
- 权重路径默认值是容器内绝对路径（:16-17,30-31,43-44），裸机安装必须显式覆盖。
- `SegmentationConfig`（:54-58）已改用 SAM2 而暂不启用——别删，C++ 侧仍读这组键。
- `BundleConfig` 的 w_rpi/w_sdf/w_pm（:103,106-107）权重为 0 属保留接口；带 "Used for" 注释的参数（:99-104）直连 C++ 侧，改动跨语言生效。

---
*甄别：任务书"12 类配置字典"与源码不符——实为 19 顶层 dataclass（含嵌套 23 个），对外导出 11 个；图谱"19 个 dataclass"与顶层类数一致，以源码为准。*
