# 01 · networks/nerf_runner.py — SDF 神经场重建核心管线

## ① 角色定位

`src/nvidia/objectreconstruction/networks/nerf_runner.py`（2492 行，全仓最大）是**神经隐式表面重建的执行核心**：输入多帧 RGB+深度+掩码+位姿（归一化空间），训练 SDF 神经场，marching cubes 提网格，再配 250 行多视角纹理烘焙产出照片级贴图网格。它是 NVBundleSDF 第 4b 步 run_global_sdf 的引擎（nvbundlesdf.py:51 导入），技术上是 **BundleSDF 的 NeRF 腿 + instant-ngp 式八叉树稀疏加速（kaolin SPC）+ monoSDF 式深度截断带监督**三股血统融合。

## ② 内部结构

六段（未注文件名的行号均指本文件）：

**基础设施与导入副作用**（:11-64）：import pyrender 前设 EGL（:21）；**硬编码 sys.path.append('/customize_cuda/')**（:23-24，容器路径，裸机必改）；warp 缓存 /tmp（:27）；`import common`（:50）= my_cpp CUDA 扩展（rayColorToTextureCUDA/postprocessOctreeRayTracing/sampleRaysUniformOccupiedVoxels 三核）；哨兵 BAD_DEPTH=99/BAD_COLOR=128（:60-61）。

**渲染与纹理工具**：`get_fixed_camera`（:82-115）环绕机位；`ModelRendererOffscreen`（:118-199）pyrender 离屏（:165 注明 >0.1.32 不可用）；`preprocess_data`（:201-242）归一化（法线 y/z 翻转 :236）；**`build_texture_from_images`（:244-493，约 250 行核心）**——Xatlas 展 UV（:257）→逐帧离屏渲染反投影（:278-287）→igl.signed_distance 找点属三角面（:289）→向量化视线-法线夹角（:298-315）→每三角面收集 (帧,夹角,颜色)（:318-319）→按夹角选 top-N 视角帧（:353-386）→可选帧级亮度重映射（:418-443）→CUDA 写纹理（:452-470）→UV 翻转（:479）→griddata 填洞（:1015-1034）。

**编码与位姿参数化**：`SHEncoder`（:686-769，纯 PyTorch 球谐——**甄别：图谱称"CUDA autograd Function"，源码无此物**）；`get_embedder`（:990-1012）三路工厂——**i_embed=1（schema 默认）走 torch_ngp 的 instant-ngp hash grid**（:1005-1008）、views 走 SH；`FeatureArray`（:772-787）每帧 appearance 潜码；`PoseArray`（:790-816）每帧 6-DoF 修正（tanh 限幅，**首帧锁恒等** :814-815）；`GlobalPoseArray`（:819-845）冻结版；`Embedder`（:904-935）Fourier。

**OctreeManager**（:1037-1170）：kaolin SPC 八叉树——建树+金字塔+dual 角点+trinkets（:1040-1049）；`trilinear_interpolate`（:1082-1104）**手写 coeffs×corner_feat 绕开 kaolin API**（:1086-1089 注释：直接调用反传不良）；`ray_trace`（:1118-1170）kaolin unbatched_raytrace + CUDA 后处理折叠成每光线 in/out 对（:1165）。

**NeRFSmall**（:1173-1251）：sigma_net 2 层×64（尾层出 1 SDF+15 geo_feat）+ color_net 3 层×64；末层 bias 初始化 0.1 鼓励正 SDF（:1202）。**甄别：图谱称"带 skip connection"，源码无 skip**（create_nerf :1419 的 `skips=[4]` 是未使用的死变量）。

**NerfRunner**（:1253-2491，23 方法）：`__init__`（:1254-1302）set_seed(0)、AMP GradScaler；`get_ray_loader`（:1305-1402）帧降采样+**KDTree 深度去噪**（:1371-1388）；`make_frame_rays`（:1450-1521）光线打包 13 通道、**首帧掩码膨胀 100px 其余 60px**（:1479-1488）、八叉树剔除不相交光线（:1507-1519）；`build_octree`（:1641-1694）27 邻域体素膨胀（:1658-1668）；`train_loop`（:1838-2012）rgb（首帧加权 :1857）+fs/sdf+潜码/位姿正则，按 i_img/i_mesh/i_pose 落盘；`train`（:2015-2030）光线耗尽轮换下批帧；`render_rays`（:2067-2180）**64 均匀+256 集中在深度±trunc 带**（:2114-2131，无效深度退回八叉树均匀）——深度先验即采样先验；`raw2outputs`（:2183-2239）sdf2weights（:2206-2217）/density 双模式；`run_network`（:2297-2381）世界系变换+|x|≤1 有效（:2320）+netchunk 分块；`extract_mesh`（:2431-2490）八叉树过滤后 marching_cubes。

## ③ 外部连接

重度依赖：kaolin（SPC）、torch_ngp_grid_encoder、igl、pyrender/trimesh/open3d、my_cpp common（三 CUDA 核）、pytorch3d se3_exp_map（:42）、.tool 工具集（:51-58）。上游唯一消费者 NVBundleSDF；产物流向 postprocessing 的 USD 导出；`add_new_frames`（:1557）支撑"跟踪一段→增量训练一段"在线模式。

## ④ 数据流

进：reader 帧序列+归一化位姿+内参+八叉树点云。训练态：光线张量 (N,13+) 常驻 GPU，按 N_rand=2048 采样。出：normalized/real_world 网格（:1990-2000）、model_latest.pth（含八叉树 :1749-1750）、optimized_poses.txt（:2004-2010）、带 TextureVisuals 的 trimesh（:483）。

## ⑤ 设计决策

1. **八叉树双角色**：加速结构（ray_trace 裁剪 :1516,2111）+深度去噪参照（KDTree :1381）——SDF 只在有几何证据的叶子里学。
2. **采样偏向深度带**（:2114-2131）：立体深度是管线最可靠监督，80% 采样押在深度±trunc 内；truncation 随训练退火（:1822-1835）。
3. **位姿优化带安全带**：tanh 限幅+首帧锁恒等（:809-815）+冻结版 PoseArray（:1439-1441）——漂移封死在 max_trans/max_rot 内。
4. **纹理选视角而非平均**：按视线夹角取 top-N（:353-374）+亮度重映射（:418-443）——"选最清晰"优于"混合"（混合糊高光）。
5. **三处手写替代库 API**：trilinear_interpolate 绕 kaolin 反传（:1086）、trimesh_split 绕内存炸（:497）、slab 法光线-AABB（:545）——各有注释记录的实证理由。
6. **首帧掩码特殊化**（:1479）：SAM2 首帧由 bbox 标注（最准）后续靠传播（会漂），膨胀 100 vs 60 即此置信度模型。

## ⑥ 新人提示

- **死路代码**：use_mask=0 分支的 `pdb.set_trace()`（:1357，未 import pdb，走到必 NameError）；`skips=[4]`（:1419 未用）。use_mask=1 是唯一被测路径。
- **schema 架构参数是摆设**：netdepth=8/netwidth=256（schema.py:210-213）从未传入——create_nerf 硬编码 NeRFSmall(2 层,64)（:1421），改宽度要改代码。
- `eval(str(...))`（:1258）接受 "1e-3" 字符串——任意代码执行入口，别灌外部输入。
- NeRFSmall 尾层 bias=0.1（:1202）是"初始 SDF 为正"的归纳偏置，改 0 零面会随机穿物体。
- add_new_frames 的 reuse_weights **不继承位姿修正**（:1598 注释）——增量轮位姿从零再学，有意设计。
- 图谱甄别：SHEncoder 非 CUDA（:686 纯 PyTorch）、NeRFSmall 无 skip——两条 summary 与源码不符，以源码为准。

---
*甄别：图谱"NerfRunner 23 方法"与源码一致；"SHEncoder CUDA/NeRFSmall skip"两处 summary 与源码冲突，以源码为准；pdb 残留/schema 架构参数摆设为首轮源码级实证发现。*
