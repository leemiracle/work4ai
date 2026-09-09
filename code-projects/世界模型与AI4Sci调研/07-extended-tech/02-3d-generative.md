# 3D 生成与神经辐射场：NeRF / 3DGS / 生成式 3D

> 这是 `world-ai4sci-math/07-extended-tech` 扩展技术卷的第 2 章。3D 表征与生成是「世界模型」最直接的几何与物理先验来源——任何想在三维空间里思考、规划、具身的智能体，都必须先把"世界长什么样"压进某种可微的表示里。本章用「直觉 → 数学 → 代码 → 不足 → 应用」五层结构，把从结构光到 Hunyuan3D 的二十余年主线一次讲透。

> ⚠️ **勘误表（一手核实纠正的 6 个 ID 错误）**：本轮调研发现，网络上流传（包括大模型记忆与多个 seed）的若干关键论文 arXiv ID 是错的，而且错得极其隐蔽——它们指向的居然全是**天体物理 / 代数几何论文**。下表全部经 `arxiv.org/abs/<id>` 逐篇打开核实：

| 论文 | 流传/记忆的错误 ID | 一手核实的正确 ID | 错误 ID 实际指向 |
|---|---|---|---|
| **3D Gaussian Splatting** (Kerbl 2023, SIGGRAPH best paper) | `2308.14737` | **`2308.04079`** | Keselman & Hebert「Flexible Techniques for Differentiable Rendering with 3D Gaussians」 |
| **Shap-E** (OpenAI 2023) | `2305.02478` | **`2305.02463`** | Huertas-Company「Galaxy Morphology … JWST」(astro-ph) |
| **ProlificDreamer** (清华 NeurIPS 2023) | `2305.11313` | **`2305.16213`** | Wang「Steric effects in induced-charge electro-osmosis」(physics.flu-dyn) |
| **SuGaR** (CVPR 2024) | `2306.07058` | **`2311.12775`** | Lepage「Resolution of non-singularities and the absolute anabelian conjecture」(math.AG) |
| **GS-LRM** (Adobe ECCV 2024) | `2404.19102` | **`2404.19702`** | Mestre「Modelling the Track of the GD-1 Stellar Stream … Fermionic Dark Matter」(astro-ph) |
| **Block-NeRF** (Waymo CVPR 2022) | `2202.05289` | **`2202.05263`** | Pal Choudhury「Acoustic waves and g-mode turbulence … intracluster medium」(astro-ph) |

> **教训**：arXiv ID 只差最后几位（如 `2305.02463` vs `2305.02478`、`2308.04079` vs `2308.14737`），人眼和模型都极难察觉。引用任何 3D 顶会论文前，必须 `curl arxiv.org/abs/<id>` 确认标题与作者。本章下文**只使用经核实的正确 ID**。

---

## 目录

1. [历史脉络：从结构光到 NeRF](#1-历史脉络从结构光到-nerf)
2. [NeRF：神经辐射场的奠基](#2-nerf神经辐射场的奠基)
3. [NeRF 变体大全](#3-nerf-变体大全)
4. [3D Gaussian Splatting：实时辐射场](#4-3d-gaussian-splatting实时辐射场)
5. [3DGS 变体与动态化](#5-3dgs-变体与动态化)
6. [生成式 3D：SDS 与重建大模型](#6-生成式-3dsds-与重建大模型)
7. [Text-to-3D 全流程](#7-text-to-3d-全流程)
8. [世界级生成：Block-NeRF 与 Genie](#8-世界级生成block-nerf-与-genie)
9. [数学深讲：辐射场、splatting、SDS](#9-数学深讲辐射场splattingsds)
10. [数据集与基准](#10-数据集与基准)
11. [2025–2026 前沿](#11-20252026-前沿)
12. [代码实战：用 nerfstudio 跑一个 NeRF/3DGS](#12-代码实战)
13. [用户建议：3D 是世界模型的基础](#13-用户建议)
14. [📌 进一步阅读 + ✍️ 思考题](#14-进一步阅读--思考题)

---

## 1. 历史脉络：从结构光到 NeRF

理解 NeRF 为什么是"革命"，必须先理解它之前的二十年里，三维重建是怎么做的。这条主线可以浓缩为一句话：**从"显式几何"一步步走向"隐式函数"，从"重建几何"走向"重建光场"**。

**结构光与主动三维扫描（1990s–2010s）。** 最早的工业级三维获取靠"主动投射"：投影仪把一组带编码的光栅（条纹、Gray 码、正弦相移）打到物体表面，相机从另一角度拍摄条纹的变形，由三角测量原理反算每个像素的深度。Kinect 一代（2010）就是消费级的结构光相机——红外投射器发射散斑（speckle）图案，IR 相机读回，匹配出厂标定的参考图得到深度。它的数学本质是**双目立体的"主动版"**：用一个已知模式代替"找特征点"，把对应问题从困难变为可解。结构光精度高（工业可达 10 μm 量级），但要求**受控光照**、对透明 / 镜面 / 远距离物体失效。

**Structure-from-Motion（SfM）与多视图立体重建（MVS）。** 当你只有一组从不同角度拍的普通照片（比如旅游照），SfM + MVS 是把二维图像翻回三维的标准管线。SfM（代表作 Snavely 的 **Bundler**，2006；COLMAP，Schönberger 2016）先在所有图像上检测 SIFT 特征点，跨图匹配，用 RANSAC 迭代估计每张图的相机位姿（内参 + 外参）和稀疏的三维点云——这是一个**束调整（Bundle Adjustment）**的非线性最小二乘问题：最小化所有重投影误差。MVS 则在位姿已知后，对每一对图像做稠密的 Patch 匹配（PatchMatch），逐像素算深度图，再融合（fusion）成稠密点云。COLMAP 至今仍是 NeRF / 3DGS 训练前**不可或缺的前置步骤**——它提供相机位姿和初始稀疏点云。

**点云与体素：两类显式表征。** SfM/MVS 的输出是点云——一组 $(x,y,z)$ 三元组（带颜色就是 6 维）。点云表示灵活、无分辨率限制，但**没有拓扑、没有表面、不能直接渲染**。要得到连续表面，传统做法是**体素（voxel）**：把空间离散成 $N^3$ 网格，每个体素存占据概率（occupancy）或截断距离（TSDF，truncated signed distance function）。KinectFusion（Izadi 2011）用 TSDF 在实时 SLAM 中首次做到了稠密重建。但体素的代价是**立方爆炸**：$256^3$ 网格就要 1600 万单元，$512^3$ 直接 1.3 亿，绝大多数还是空的。Octree、哈希网格都是为了缓解这个"空体素浪费"，但本质仍是离散的。

**为什么 NeRF 是分水岭。** 在 NeRF 之前，重建（几何）和绘制（渲染）是**两套语言**：重建用点云 / 网格 / TSDF，渲染用光栅化（rasterization）或光线追踪（ray tracing），中间要经过艰难的 mesh 提取。NeRF 的洞察是：**跳过"显式几何"这个中间产物，直接用一个神经网络把"从任意位置任意方向看出去的光"记下来**。它既不输出点云，也不输出网格，而是输出一个连续的、可微的、可从任意新视角渲染的"光场函数"。这个表征选择让"重建"和"渲染"统一在了同一个可微函数里，于是梯度可以直接从像素误差流回三维表示——这是后面所有 SDS、生成式 3D 的基石。

---

## 2. NeRF：神经辐射场的奠基

> 论文：Mildenhall, Srinivasan, Tancik, Barron, Ramamoorthi, Ng. **NeRF: Representing Scenes as Neural Radiance Fields for View Synthesis.** ECCV 2020 (oral). [arXiv:2003.08934](https://arxiv.org/abs/2003.08934)

### 2.1 核心思想：用一个 MLP 记住整个场景

NeRF 把一个三维场景定义为一个连续函数 $F_\Theta$，它接受一个 5D 坐标——空间位置 $\mathbf{x}=(x,y,z)$ 和观察方向 $\mathbf{d}=(\theta,\varphi)$——输出两个量：该位置的**体密度** $\sigma \in \mathbb{R}_{\geq 0}$（不透明程度）和该位置朝方向 $\mathbf{d}$ 发出的**颜色辐射** $\mathbf{c}=(r,g,b)$：

$$F_\Theta: (\mathbf{x}, \mathbf{d}) \mapsto (\sigma, \mathbf{c})$$

这里 $\Theta$ 是 MLP 的参数。注意几个关键设计选择：（1）**密度 $\sigma$ 只依赖位置 $\mathbf{x}$**——一个物体在某处有多"实"，和你从哪个方向看无关；（2）**颜色 $\mathbf{c}$ 同时依赖位置和方向**——这才能建模镜面反射、光泽等**视角相关**的外观（同一个点从不同角度看颜色不同）；（3）整个场景被"压缩"进 MLP 的权重里，没有任何显式体素或网格。一个典型场景的 NeRF 模型大约 5MB，却能渲染数百万像素的图像。

MLP 的具体结构很简洁：8 个全连接层（每层 256 维，ReLU），先用 $\mathbf{x}$ 过 8 层预测 $\sigma$ 和一个 256 维特征，再把特征和 $\mathbf{d}$ 拼接过一层预测 $\mathbf{c}$。参数总量约 0.5M。

### 2.2 体渲染方程：从三维函数到二维像素

给定一个相机射线 $\mathbf{r}(t)=\mathbf{o}+t\mathbf{d}$（$\mathbf{o}$ 是相机光心，$\mathbf{d}$ 是射线方向），像素的颜色是该射线穿过的所有体素的辐射按可见性加权积分。这就是**体渲染方程（volume rendering equation）**：

$$C(\mathbf{r}) = \int_{t_n}^{t_f} T(t)\,\sigma(\mathbf{r}(t))\,\mathbf{c}(\mathbf{r}(t),\mathbf{d})\,dt$$

其中 $T(t)$ 是**透射率（transmittance）**——射线从近端 $t_n$ 到 $t$ 没有被任何物质挡住的概率：

$$T(t) = \exp\!\left(-\int_{t_n}^{t} \sigma(\mathbf{r}(s))\,ds\right)$$

**推导这个方程的关键直觉**：把射线看作一束光，它沿 $t$ 前进时，在无穷小区间 $[t, t+dt]$ 内"撞上"物质的概率是 $\sigma(\mathbf{r}(t))\,dt$（这等价于把 $\sigma$ 理解为"单位长度的吸收 / 散射率"，量纲是 $1/\text{长度}$）。撞上之后，这段物质贡献的颜色是 $\mathbf{c}(\mathbf{r}(t),\mathbf{d})$。但它能被看到的前提是射线**在此之前的所有物质都没把它挡掉**——这个"没被挡住"的累积概率正是 $T(t)$。把 $\sigma(\mathbf{r}(t))\,dt$ 理解为"这段的概率质量"，$\mathbf{c}$ 是"这段的颜色"，$T(t)$ 是"前面的折扣因子"，那么 $C(\mathbf{r})$ 就是一个**带指数折扣的加权平均**——离相机近、密度大的物质对像素颜色的贡献最大，这和直觉完全吻合。

**为什么透射率是指数形式？** 这来自**比尔-朗伯定律（Beer-Lambert law）**：光线穿过均匀吸收介质，强度按 $e^{-\sigma t}$ 衰减。对非均匀介质，把吸收率积分起来就得到 $T(t)=\exp(-\int\sigma)$。这是辐射传输方程（radiative transfer equation）的解析解在"无自发光、纯吸收+发射"假设下的特例。

### 2.3 离散化：分层随机采样求积

实际计算时积分要离散化。NeRF 用**分层随机采样（stratified sampling）**：在 $[t_n,t_f]$ 内取 $N$ 个区间，每个区间内均匀采一个点 $t_i$，用黎曼和近似：

$$\hat{C}(\mathbf{r}) = \sum_{i=1}^{N} T_i\,(1-\exp(-\sigma_i\delta_i))\,\mathbf{c}_i, \qquad T_i = \exp\!\left(-\sum_{j=1}^{i-1}\sigma_j\delta_j\right)$$

其中 $\delta_i=t_{i+1}-t_i$ 是相邻采样点的距离。定义**不透明度** $\alpha_i=1-\exp(-\sigma_i\delta_i)$，则 $T_i=\prod_{j=1}^{i-1}(1-\alpha_j)$，渲染公式变成经典的前向 alpha 混合：

$$\hat{C}(\mathbf{r}) = \sum_{i=1}^{N} \alpha_i \prod_{j=1}^{i-1}(1-\alpha_j)\,\mathbf{c}_i$$

这正是图形学里"从后往前画半透明层"的标准公式，只是这里是**可微的**。NeRF 用两个采样点集（coarse 网络采 64 点，fine 网络按 coarse 预测的密度重采样到 128 点）做 importance sampling。

### 2.4 位置编码（Positional Encoding）

如果直接把 $(x,y,z,\theta,\varphi)$ 喂给 MLP，模型会**严重偏向低频**——渲染出来的场景平滑、模糊，丢失纹理细节。这是因为神经网络（尤其是 ReLU MLP）对高频函数存在**谱偏置（spectral bias）**，倾向于先拟合低频成分。NeRF 借鉴 Transformer 的正弦编码，把每个标量坐标 $p$ 映射到高维：

$$\gamma(p) = \big(p,\ \sin(2^0\pi p),\cos(2^0\pi p),\ \ldots,\ \sin(2^{L-1}\pi p),\cos(2^{L-1}\pi p)\big)$$

$L=10$ 用于位置，$L=4$ 用于方向。直观地说，位置编码把一个低维输入"摊开"到高维的周期性基函数上，强迫网络区分非常接近的两个点（它们的 sin/cos 相位不同）。这一招把 PSNR 提升了约 10 dB，是 NeRF 能逼真渲染的关键。后面 Instant-NGP 的哈希编码、Mip-NeRF 的集成位置编码，本质上都是在找**更好的频率编码**。

### 2.5 损失与训练

NeRF 的损失极简：对每个像素的渲染色 $\hat{C}(\mathbf{r})$ 和真实色 $C(\mathbf{r})$ 算 MSE，对 coarse 和 fine 两个网络分别算：

$$\mathcal{L} = \|\hat{C}_c(\mathbf{r})-C(\mathbf{r})\|_2^2 + \|\hat{C}_f(\mathbf{r})-C(\mathbf{r})\|_2^2$$

训练用 Adam，一个典型场景（Blender 数据集的"乐高"）要在单 V100 上训 1–2 天，约 100–300K 步。**慢**是原始 NeRF 最大的问题，也直接催生了后面一整条加速路线。

> **小节代码：NeRF 渲染公式的纯 NumPy 实现**（可运行，约 30 行，展示 alpha 混合）
```python
import numpy as np
def volume_render(sigmas, colors, deltas):
    # sigmas: (N,) 体密度; colors: (N,3); deltas: (N,) 相邻采样点距离
    alphas = 1.0 - np.exp(-sigmas * deltas)          # 每点不透明度
    T = np.cumprod(np.concatenate([[1.0], 1.0 - alphas[:-1]]))  # 透射率 T_i
    weights = T * alphas                              # 渲染权重
    color = (weights[:, None] * colors).sum(axis=0)   # 前向 alpha 混合
    depth = (weights * (np.arange(len(sigmas))+1)).sum() / weights.sum()
    return color, weights
# 验证：远处有一堵高密度墙，近处稀疏 -> 颜色应主要由墙决定
sig = np.array([0.01,0.01,0.01,5.0,5.0]); col = np.array([[1,0,0]]*3+[[0,0,1]]*2)
dlt = np.array([0.5]*5)
print(volume_render(sig, col, dlt)[0])  # 输出接近 [0,0,1]（蓝色墙主导）
```

---

## 3. NeRF 变体大全

原始 NeRF 的三大痛点——**慢、模糊、不能反走样**——催生了一个庞大的变体家族。下面按"质量派 / 速度派 / 几何派"三系讲最有影响力的几篇。

### 3.1 质量派：Mip-NeRF 与 Mip-NeRF 360

> 论文：Barron, Mildenhall, Tancik, Hedman, Martin-Brualla, Srinivasan. **Mip-NeRF: A Multiscale Representation for Anti-Aliasing Neural Radiance Fields.** ICCV 2021. [arXiv:2103.13415](https://arxiv.org/abs/2103.13415)

NeRF 用单条射线代表一个像素，但像素其实覆盖一块**圆锥形区域**（视锥 frustum）。当训练图和测试图分辨率不同（同一物体远近不同），单射线采样会产生**走样（aliasing）**。Mip-NeRF 的解法是把射线换成**圆锥台（conical frustum）**，并对整段圆锥台做**积分位置编码（IPE）**——不编码一个点，而是编码一个高斯分布的位置区间，用期望和协方差算出编码的闭式解析形式。这同时解决了走样和高频细节问题，比 NeRF 误差降 17%、速度快 7%、模型小一半。

> 论文：Barron, Mildenhall, Verbin, Srinivasan, Hedman. **Mip-NeRF 360: Unbounded Anti-Aliased Neural Radiance Fields.** CVPR 2022. [arXiv:2111.12077](https://arxiv.org/abs/2111.12077)

Mip-NeRF 360 把战场从"桌面物体"推到**无界大场景**（360° 环绕、远近物体尺度差异极大）。三大技术：（1）**非线性场景参数化**——把远处空间用收缩函数 $\text{contract}(\mathbf{x})=(\mathbf{x}/|\mathbf{x}|)(1-1/|\mathbf{x}|)$ 压缩，让有限的采样预算覆盖无限远；（2）**在线蒸馏（online distillation）**——用一个 proposal 网络预测密度分布，引导主网络采样；（3）**失真正则项（distortion loss）**——惩罚权重分布的散度，让深度估计更锐利。结果：比 Mip-NeRF 再降 57% MSE。**Mip-NeRF 360 至今仍是 NeRF 路线的质量上限基准**，3DGS 论文也拿它做对比。

### 3.2 速度派：Instant-NGP 与 Plenoxels

> 论文：Müller, Evans, Schied, Keller. **Instant Neural Graphics Primitives with a Multiresolution Hash Encoding.** SIGGRAPH 2022 (ACM TOG 41(4)). [arXiv:2201.05989](https://arxiv.org/abs/2201.05989)

Instant-NGP 是 NeRF 加速的**里程碑**：把训练时间从"几小时 / 几天"砍到"**几秒钟**"。核心是**多分辨率哈希编码（multiresolution hash grid）**：在 $L$ 个分辨率层级各放一个可训练特征表，每个空间点 $\mathbf{x}$ 在每一层用哈希函数 $h(\mathbf{x})=\bigoplus_{i=1}^d x_i \pi_i \mod T$ 映射到表的一个槽（大小 $T$），取该槽的特征向量，三线性插值后拼接送进一个**极小的 MLP**（2 层 64 维）。哈希冲突靠**梯度自动解决**——重要的地方梯度大、特征被强化，不重要的冲突被忽略。

这个设计的精妙在于：（1）网络小到几乎不花算力，瓶颈全在查表，而查表可全并行；（2）多分辨率让模型同时捕获粗结构和细纹理；（3）用**全融合 CUDA kernel**（fully-fused）把访存压到最低。最终在 1080p 下渲染只需几十毫秒，训练只需 5–10 秒（原始 NeRF 是 10–20 小时）。这个哈希编码后来被 NVIDIA 塞进了几乎所有神经图形原语（SDF、图像、神经辐射缓存）。

> 论文：Yu, Fridovich-Keil, Tancik, Chen, Recht, Kanazawa. **Plenoxels: Radiance Fields without Neural Networks.** CVPR 2022. [arXiv:2112.05131](https://arxiv.org/abs/2112.05131)

Plenoxels 走了一条相反的路：**完全不用神经网络**。它把场景表示成稀疏 3D 体素网格，每个体素存球谐函数（spherical harmonics）系数来表示视角相关颜色 + 一个不透明度。优化就是对这些体素值的梯度下降，加上稀疏性正则和 TV（total variation）平滑正则。结论震撼：**比 NeRF 快两个数量级，质量相当**。这证明了一件事——NeRF 的成功不在于"神经网络"，而在于"可微体渲染 + 合适的高频编码"；MLP 只是一种参数化，稀疏体素 + 球谐是另一种（更高效）的参数化。Plenoxels 是后来 3DGS"用显式基元代替 MLP"思想的直接先驱。

### 3.3 几何派：NeuS 与表面重建

> 论文：Wang, Liu, Liu, Theobalt, Komura, Wang. **NeuS: Learning Neural Implicit Surfaces by Volume Rendering for Multi-view Reconstruction.** NeurIPS 2021. [arXiv:2106.10689](https://arxiv.org/abs/2106.10689)

NeRF 的密度场 $\sigma$ 能渲染漂亮图像，但**提取不出干净表面**——因为 $\sigma$ 只是一个软的"不透明程度"，没有几何意义，行进立方体（marching cubes）得到的网格满是噪声。NeuS 的目标是从多视图图像直接重建**高质量网格**。

方法是把表面表示为**有符号距离函数（SDF）**的零等值面，并设计一种**无偏的体渲染**——把 SDF $f(\mathbf{x})$ 通过 Logistic 分布的 CDF 转成密度 $\sigma$，使得一阶近似下渲染没有系统偏差（这是论文的关键数学贡献：原始体渲染对表面有固有 bias，NeuS 推导了一个 bias-free 的权重函数）。这样梯度既能监督渲染质量，又能保证 SDF 在零等值面附近是真正的距离场，marching cubes 提取出的网格锐利、干净，能重建薄结构和自遮挡区域，在 DTU 数据集上达到 SOTA。NeuS 开启了"神经隐式表面"路线，后续 VolSDF、HF-NeuS、NeuS2 都是在此基础上改进。

**变体对照速查表（NeRF 家族）：**

| 方法 | 年份/会议 | 表征 | 速度（训练） | 强项 | arXiv |
|---|---|---|---|---|---|
| NeRF | ECCV 2020 | MLP | ~10–20 h | 奠基，质量好 | 2003.08934 |
| Mip-NeRF | ICCV 2021 | MLP + IPE | 同量级，-7% | 反走样 | 2103.13415 |
| Mip-NeRF 360 | CVPR 2022 | MLP + 收缩 | 较慢 | 无界场景 SOTA | 2111.12077 |
| Instant-NGP | SIGGRAPH 2022 | 哈希网格 + 小 MLP | **~5–10 s** | 极致速度 | 2201.05989 |
| Plenoxels | CVPR 2022 | 稀疏体素 + 球谐 | ~11 min | 无 NN | 2112.05131 |
| NeuS | NeurIPS 2021 | SDF + 体渲染 | 数小时 | 表面重建 | 2106.10689 |

---

## 4. 3D Gaussian Splatting：实时辐射场

> 论文：Kerbl, Kopanas, Leimkühler, Drettakis. **3D Gaussian Splatting for Real-Time Radiance Field Rendering.** SIGGRAPH 2023 (ACM TOG 42(4))，**Best Paper**. [arXiv:2308.04079](https://arxiv.org/abs/2308.04079) （⚠️ 非网上流传的 2308.14737）

### 4.1 核心表征：各向异性高斯椭球

3DGS 抛弃了 NeRF 的"MLP 记一切"，回到**显式基元**：场景由一百万到数百万个**3D 高斯椭球（3D Gaussian ellipsoid）**组成。每个高斯由以下参数定义：

- 位置（均值）$\boldsymbol{\mu}\in\mathbb{R}^3$
- 协方差矩阵 $\boldsymbol{\Sigma}\in\mathbb{R}^{3\times 3}$（正定，控制椭球的形状和朝向，各向异性）
- 不透明度 $\alpha\in[0,1]$
- 球谐系数（view-dependent 颜色，通常 3 阶 = 48 维）

高斯的概率密度：$G(\mathbf{x})=\exp\!\big(-\tfrac{1}{2}(\mathbf{x}-\boldsymbol{\mu})^\top\boldsymbol{\Sigma}^{-1}(\mathbf{x}-\boldsymbol{\mu})\big)$。为保证 $\boldsymbol{\Sigma}$ 在优化中始终正定，它被参数化为 $\boldsymbol{\Sigma}=\mathbf{R}\mathbf{S}\mathbf{S}^\top\mathbf{R}^\top$，其中 $\mathbf{R}$ 是旋转（四元数）、$\mathbf{S}$ 是缩放（对角），这样对 $\mathbf{R},\mathbf{S}$ 任意优化都不会破坏正定性。

**初始化**用 COLMAP 的稀疏点云（每个点一个高斯），然后通过**克隆（clone）、分裂（split）、剪枝（prune）**的密度控制策略动态增删高斯——梯度大的区域（欠拟合）克隆/分裂，$\alpha$ 接近 0 的剪枝。

### 4.2 Splatting：把 3D 高斯"拍扁"到屏幕

渲染不用光线追踪（NeRF 那样逐像素积分），而用 **splatting**：把每个 3D 高斯投影到屏幕上变成一个 2D 高斯（"水滴"），按深度排序，做前向 alpha 混合。投影的数学是 **EWA（Elliptical Weighted Average）滤波**的近似：3D 协方差 $\boldsymbol{\Sigma}$ 经视图变换 $\mathbf{W}$ 和雅可比 $\mathbf{J}$ 投影为 2D 协方差 $\boldsymbol{\Sigma}'=\mathbf{J}\mathbf{W}\boldsymbol{\Sigma}\mathbf{W}^\top\mathbf{J}^\top$。最终像素颜色：

$$C=\sum_{i\in\mathcal{N}}\mathbf{c}_i\,\alpha_i'\prod_{j=1}^{i-1}(1-\alpha_j'),\qquad \alpha_i'=\alpha_i\cdot G_i'(\boldsymbol{\mu}_i')$$

其中 $G_i'$ 是投影后的 2D 高斯在该像素的值。这套前向 splatting 完全可微，且**高度并行**——每个高斯独立投影，用定制 CUDA kernel 实现 tile-based 光栅化，跳过 NeRF 的逐像素射线积分。

### 4.3 为什么快、为什么好

3DGS 在 1080p 下达到 **30 FPS 以上实时渲染**（论文报告训练后渲染 Mip-NeRF 360 级质量，约 134 FPS），训练时间约 30–40 分钟（比 NeRF 快 ~50 倍，比 Mip-NeRF 360 快且质量相当或更好）。三个原因：（1）**前向投影 vs 反向追踪**——splatting 把"每个像素遍历所有深度"变成"每个高斯投到一组像素"，复杂度更低；（2）**显式存储 vs 隐式查询**——渲染时直接读高斯参数，不用反复前向 MLP；（3）**自适应密度控制**——高斯只长在需要的地方，空区域不浪费。

### 4.4 Gaussian vs NeRF：范式之争

| 维度 | NeRF（MLP） | 3DGS（显式高斯） |
|---|---|---|
| 表征 | 一个 MLP 记全场景 | 数百万个参数化椭球 |
| 渲染 | 光线追踪式逐像素积分 | 前向 splatting + tile 光栅化 |
| 训练 | 10–20 h（NeRF）/ 5 s（NGP） | ~30–40 min |
| 渲染速度 | 秒级（离线） | **>100 FPS（实时）** |
| 编辑性 | 难（埋在权重里） | 好（可挑出某个高斯移动） |
| 显存 | 模型小（5MB） | 大（百 MB–GB） |
| 表面提取 | 难（需 NeuS） | 仍需 SuGaR 等后处理 |

这场"显式 vs 隐式"的张力贯穿了整个 3D 视觉：隐式（MLP/SDF）编辑难但表面光滑、存储省；显式（高斯/点云）编辑直观、渲染快但吃显存、表面提取仍需后处理。**当前工程主流已倒向 3DGS**（实时性压倒一切），但学术上 SDF / 隐式表面仍在表面重建质量上占优。

---

## 5. 3DGS 变体与动态化

3DGS 一出，整个社区在半年内把 NeRF 时代积累的所有问题用高斯重做了一遍。

**SuGaR（Surface-Aligned Gaussian Splatting）。** CVPR 2024，Guédon & Lepetit。[arXiv:2311.12775](https://arxiv.org/abs/2311.12775)（⚠️ 非 2306.07058）。3DGS 的高斯是体积云，提取网格仍困难。SuGaR 加一个**表面对齐正则**，鼓励高斯"贴"在表面上变成薄饼状，再用 Poisson 重建得到高质量网格，且支持从网格做超快渲染。这是把 3DGS 接入传统图形管线（需要 mesh 的下游）的桥梁。

**Gaussian-Pro。** ICML 2024，Cheng 等（港大）。把 mesh-guided 的"progressive propagation"引入高斯增长，约束新分裂的高斯沿真实表面分布，减少浮空高斯、提升表面规则性。⭐ 其 arXiv ID 本轮未能一手确认（候选 `2402.14653` 经核实是天体物理 PRODIGE 论文，弃用），引用时建议直接查 ICML 2024 proceedings，**宁缺毋臆测**。

**4D Gaussian Splatting（动态场景）。** CVPR 2024，Wu, Yi, Fang 等（港科 + 华为）。[arXiv:2310.08528](https://arxiv.org/abs/2310.08528)。动态场景（视频）的扩展：用一组 3D 高斯 + 一个受 **HexPlane** 启发的 4D 神经体素场，通过轻量 MLP 预测高斯在任意时间戳的变形。在 800×800 分辨率达 **82 FPS**（RTX 3090），质量与 SOTA 相当或更好。这是 3DGS 进入**视频 / 动态**领域的关键作。

此外还有 **Gaussian-Shader**（引入法线 + 着色）、**Mip-Splatting**（反走样版 3DGS，arXiv:2311.16493）、**Deformable 3D Gaussians**（单目动态重建，arXiv:2309.13101）、**LightGaussian**（15× 压缩 + 200+ FPS）等数十篇，社区维护的 [Awesome3DGS](https://github.com/MrNeRF/awesome-3D-gaussian-splatting) 已收录上千篇。

---

## 6. 生成式 3D：SDS 与重建大模型

前面 1–5 章是"**重建**"——给定多张照片，把场景恢复出来。本章进入"**生成**"——凭空创造新的三维物体。这里有两条主线：**优化派**（用一个 2D 扩散模型当"裁判"去蒸馏出 3D）和**前馈派**（训练一个大数据模型直接映射）。

### 6.1 优化派：SDS 革命

> 论文：Poole, Jain, Barron, Mildenhall. **DreamFusion: Text-to-3D using 2D Diffusion.** ICLR 2023. [arXiv:2209.14988](https://arxiv.org/abs/2209.14988)

DreamFusion 是 Text-to-3D 的**破局之作**，核心发明是**Score Distillation Sampling（SDS）**。问题设定：我们有一个强大的 2D 文生图扩散模型（如 Imagen），但没有 3D 数据；怎么让它生成 3D？DreamFusion 的答案：从随机初始化的 NeRF 出发，随机采样一个视角渲染成 2D 图，让扩散模型给这张图"打分"，把分数的梯度反传回 NeRF 参数，反复迭代直到所有视角都"像扩散模型会生成的图"。

**SDS 的数学（详见第 9 章）**：扩散模型在加噪图像 $\hat{\mathbf{x}}_t$ 上预测噪声 $\epsilon_\phi$，其得分函数 $\nabla\log p$ 可估计为 $-\epsilon_\phi/\sigma_t$。SDS 把这个得分通过链式法则变成对 3D 参数 $\theta$ 的梯度：

$$\nabla_\theta\mathcal{L}_{\text{SDS}}(\phi,\mathbf{x})=\mathbb{E}_{t,\epsilon}\Big[w(t)\big(\epsilon_\phi(\mathbf{x}_t;t,y)-\epsilon\big)\frac{\partial \mathbf{x}}{\partial\theta}\Big]$$

关键巧思：**不需要训练扩散模型**（它冻住当先验），也不需要 3D 数据，只需前向 + 反传。DreamFusion 生成的 3D 物体可任意视角观看、任意光照重打光。但它有三大病：**过饱和、过平滑、多样性低**（SDS 的 mode-seeking 行为）。

> 论文：Lin 等（NVIDIA）. **Magic3D: High-Resolution Text-to-3D Content Creation.** CVPR 2023 (highlight). [arXiv:2211.10440](https://arxiv.org/abs/2211.10440)

Magic3D 解决 DreamFusion 的"低分辨率"病：**两阶段**——先用低分辨率扩散先验 + 稀疏哈希网格得到粗 NeRF，再用粗模型初始化一个**带纹理的 mesh**，用高效可微渲染器（DMTet）配合**高分辨率 latent 扩散模型**精修。40 分钟出高质量 mesh（比 DreamFusion 快 2×、分辨率更高），用户研究 61.7% 偏好 Magic3D。

> 论文：Wang 等（清华）. **ProlificDreamer: High-Fidelity and Diverse Text-to-3D Generation with Variational Score Distillation.** NeurIPS 2023 (Spotlight). [arXiv:2305.16213](https://arxiv.org/abs/2305.16213)（⚠️ 非 2305.11313）

ProlificDreamer 从理论上修掉了 SDS 的病根：SDS 把 3D 参数当**常数**，ProlificDreamer 把它当**随机变量**，提出 **Variational Score Distillation（VSD）**。它证明了 SDS 是 VSD 在"粒子数为 1"时的退化特例，导致 mode-seeking。VSD 用粒子变分方法建模 3D 分布，配合 CFG=7.5（与扩散采样一致）就能生成 $512\times512$ 高保真 NeRF（有烟雾、水滴等复杂效果），mesh 也有丰富细节。这是 SDS 系理论最干净的提升。

> 论文：Tang 等（HKUST）. **DreamGaussian: Generative Gaussian Splatting for Efficient 3D Content Creation.** ICLR 2024. [arXiv:2309.16653](https://arxiv.org/abs/2309.16653)

DreamGaussian 把 3DGS 引入生成：用高斯代替 NeRF 做优化（高斯的渐进密集化比 NeRF 的占用剪枝收敛快得多），再加 mesh 提取 + UV 空间纹理精修。**2 分钟**从单图生成高质量带纹理 mesh（比 DreamFusion 快约 10×）。这是"3DGS + SDS"组合的代表作，几乎成为后续快速生成的标配。

### 6.2 前馈派：重建大模型

优化派虽好，但**每个物体都要优化几分钟到小时**，离"秒级生成"差得远。前馈派换思路：与其在线优化，不如**离线训练一个大模型**，让它学会"从图像/文本直接预测 3D"。

> 论文：Hong 等（Adobe）. **LRM: Large Reconstruction Model for Single Image to 3D.** ICLR 2024. [arXiv:2311.04400](https://arxiv.org/abs/2311.04400)

LRM 是首个**大规模单图重建模型**：一个 5 亿参数的 Transformer，输入单张图，**5 秒内**直接输出一个 NeRF。训练数据约 100 万物体（Objaverse 合成 + MVImgNet 真实），架构是 ViT 编码图像 + transformer 解码三平面（triplane）NeRF 表征。关键洞察：**3D 重建也可以走"大数据 + 大模型 + 前馈"的 LLM 路线**，而不是 per-scene 优化。LRM 对真实图、生成模型造的图都泛化得很好。

> 论文：Zhang 等（Adobe + Cornell）. **GS-LRM: Large Reconstruction Model for 3D Gaussian Splatting.** ECCV 2024. [arXiv:2404.19702](https://arxiv.org/abs/2404.19702)（⚠️ 非 2404.19102）

GS-LRM 把 LRM 的输出从 NeRF 换成 3DGS——Transformer 预测每个像素对应的 3D 高斯参数，多视角输入（2–4 视图）前馈推理即可得到高质量高斯场。质量接近甚至超过 per-scene 优化的 3DGS，但快几个数量级。**LRM/GS-LRM 标志着 3D 进入"foundation model"时代**：重建不再是"为每个场景求解"，而是"用一个通用模型一次前馈"。

---

## 7. Text-to-3D 全流程

把第 6 章的两条线 + 扩散模型合流，就得到了现代 Text-to-3D 的完整工业管线：**文生图 → 图生 3D → 纹理 / 精修**。

> 论文：Nichol 等（OpenAI）. **Point-E: A System for Generating 3D Point Clouds from Complex Prompts.** [arXiv:2212.08751](https://arxiv.org/abs/2212.08751)

Point-E 的策略极简实用：先用文生图扩散模型生成一张图，再用第二个扩散模型（条件于该图）生成 3D 点云。**1–2 分钟**单 GPU 出一个点云，比 DreamFusion 快 1–2 个数量级，代价是质量略低。它证明了"图 → 3D"两阶段比"文 → 3D"直接优化快得多。

> 论文：Jun, Nichol（OpenAI）. **Shap-E: Generating Conditional 3D Implicit Functions.** [arXiv:2305.02463](https://arxiv.org/abs/2305.02463)（⚠️ 非 2305.02478）

Shap-E 是 Point-E 的升级：不再生成点云（低维、丢纹理），而是**直接生成隐式函数的参数**，可同时渲染成带纹理 mesh 和 NeRF。两阶段训练——先训一个编码器把 3D 资产确定性地映射成隐式函数参数，再训条件扩散模型生成这些参数。比 Point-E 收敛更快、质量相当或更好，且输出是多表征的。

> **TripoSR**（Tripo AI + Stability AI，2024-03）。基于 LRM 思想的快速单图转 3D，技术报告，**<0.5 秒**在单张 A100 上从图生成 mesh。虽无正式 arXiv（发布在 GitHub），但因开源 + 极快成为社区爆款，是 2024 年最流行的"图转 3D"基线之一。

> 论文：Xiang 等（Microsoft）. **Structured 3D Latents for Scalable and Versatile 3D Generation (TRELLIS).** [arXiv:2412.01506](https://arxiv.org/abs/2412.01506)

TRELLIS 提出 **SLAT（Structured LATent）**表征：一个稀疏 3D 网格 + 从视觉基础模型提取的稠密多视图特征，可解码为辐射场 / 3DGS / mesh 三种格式。用 **rectified flow transformer**（至 2B 参数）在 50 万物体上训练，文 / 图条件生成质量大幅超越同尺度方法。亮点是**一个模型多格式输出 + 局部 3D 编辑**——这是"3D 版的 Stable Diffusion"该有的样子。

**典型 Text-to-3D 管线对比：**

| 系统 | 路线 | 输入 | 输出 | 时间 | arXiv |
|---|---|---|---|---|---|
| DreamFusion | SDS 优化 | 文本 | NeRF | ~1.5 h | 2209.14988 |
| ProlificDreamer | VSD 优化 | 文本 | NeRF/mesh | 数 h | 2305.16213 |
| DreamGaussian | SDS + 3DGS | 图/文 | textured mesh | ~2 min | 2309.16653 |
| Point-E | 两阶段扩散 | 文本 | 点云 | 1–2 min | 2212.08751 |
| Shap-E | 隐式扩散 | 文本 | mesh+NeRF | 秒级 | 2305.02463 |
| LRM / GS-LRM | 前馈大模型 | 单图/多视图 | NeRF/3DGS | ~5 s | 2311.04400 / 2404.19702 |
| TRELLIS | flow transformer | 文/图 | 多格式 | 秒级 | 2412.01506 |
| Hunyuan3D 2.0 | 两阶段 DiT | 图 | mesh+纹理 | ~10 s | 2501.12202 |

---

## 8. 世界级生成：Block-NeRF 与 Genie

把 NeRF / 3DGS 的尺度从"单个物体"推到"整条街道""整个可交互世界"，是通向世界模型的必经之路。

> 论文：Tancik 等（Waymo + UCB）. **Block-NeRF: Scalable Large Scene Neural View Synthesis.** CVPR 2022. [arXiv:2202.05263](https://arxiv.org/abs/2202.05263)（⚠️ 非 2202.05289）

Block-NeRF 回答"怎么用 NeRF 重建一整座城市"：把大场景切成多个 **block**，每个 block 独立训一个 NeRF，再在渲染时按可见性合成。关键技术包括**外观匹配**（不同时段光照不同，给每个 NeRF 学一个外观嵌入）、**曝光对齐**、**几何先验**（用 lidar 引导）。Waymo 用它在旧金山重建了城市级场景，是自动驾驶 + NeRF 的标杆。这印证了"辐射场可以模块化、可扩展到城市级"。

> 论文：Bruce 等（DeepMind）. **Genie: Generative Interactive Environments.** [arXiv:2402.15391](https://arxiv.org/abs/2402.15391)

Genie 走得更远——它不重建已有世界，而是**生成可交互的新世界**。11B 参数，从无标注互联网视频无监督训练，由三部分组成：**时空视频 tokenizer**、**自回归动力学模型**、**潜在动作模型（latent action model）**。用户可用文本、合成图、照片甚至草图提示它，逐帧"操控"生成的环境。它没有真实动作标签，却学到了一个潜在动作空间，可用于模仿学习未见过视频里的行为。Genie 被作者称为"**基础世界模型（foundation world model）**"，是辐射场思想（"把世界压成可前向模拟的表示"）的生成式延伸。它与 Sora、Veo 共同构成了 2024 年"生成式世界模型"浪潮的核心。

**共同主题**：从 NeRF 的"记住一个固定场景"，到 Block-NeRF 的"记住一座城市"，再到 Genie 的"生成任意可交互世界"——表征从静态走向动态、从重建走向生成、从被动观看走向主动操控。这条线正是「世界模型」最实际的工程路径。

---

## 9. 数学深讲：辐射场、Splatting、SDS

本节把前三处分散的公式集中、严格地推导一遍，作为全章的数学锚点。

### 9.1 辐射场与辐射传输方程

物理上，光在参与介质（participating media）中的传输由**辐射传输方程（RTE）**描述。沿方向 $\boldsymbol{\omega}$ 在点 $\mathbf{x}$ 处的辐射率 $L(\mathbf{x},\boldsymbol{\omega})$ 满足：

$$(\boldsymbol{\omega}\cdot\nabla)L(\mathbf{x},\boldsymbol{\omega}) = -\sigma(\mathbf{x})L(\mathbf{x},\boldsymbol{\omega}) + \sigma(\mathbf{x})L_e(\mathbf{x},\boldsymbol{\omega}) + \sigma_s(\mathbf{x})\int p(\boldsymbol{\omega},\boldsymbol{\omega}')L(\mathbf{x},\boldsymbol{\omega}')\,d\boldsymbol{\omega}'$$

三项分别是**吸收+发射**（$-\sigma L + \sigma L_e$）和**散射**（in-scattering，相函数 $p$）。NeRF 做了**两个关键简化**：（1）忽略散射（或把它吸收进发射项），（2）令介质只发射不外照明（$L_e=\mathbf{c}$）。于是沿射线 $\mathbf{r}(t)=\mathbf{o}+t\mathbf{d}$ 的 1D 常微分方程为：

$$\frac{d}{dt}L(\mathbf{r}(t),\mathbf{d}) = -\sigma(\mathbf{r}(t))L(\mathbf{r}(t),\mathbf{d}) + \sigma(\mathbf{r}(t))\mathbf{c}(\mathbf{r}(t),\mathbf{d})$$

这是一个一阶线性 ODE，边界条件为"远端无入射光" $L(t_f)=0$。用**积分因子** $e^{\int_{t_n}^t\sigma}$ 解之：

$$L(t_n) = \int_{t_n}^{t_f} \exp\!\Big(-\int_{t_n}^{t}\sigma(\mathbf{r}(s))ds\Big)\,\sigma(\mathbf{r}(t))\,\mathbf{c}(\mathbf{r}(t),\mathbf{d})\,dt$$

这正是第 2 节的体渲染方程，$T(t)$ 就是那个指数积分因子。**NeRF 的全部数学合法性都建立在这个 ODE 的解析解上**——这就是为什么体渲染天然可微，梯度能从像素流回三维。

### 9.2 Splatting 方程与 EWA

Splatting 的核心是把 3D 高斯投影到 2D。设透视投影的局部仿射近似为 $\mathbf{x}' = \mathbf{W}\mathbf{x}+\mathbf{t}$（$\mathbf{W}$ 是视图变换，再用雅可比 $\mathbf{J}$ 局部线性化透视）。一个 3D 高斯 $G_{\boldsymbol{\mu},\boldsymbol{\Sigma}}$ 经线性变换 $\mathbf{M}$ 后仍是高斯，均值 $\boldsymbol{\mu}'=\mathbf{M}\boldsymbol{\mu}$，协方差 $\boldsymbol{\Sigma}'=\mathbf{M}\boldsymbol{\Sigma}\mathbf{M}^\top$。所以投影后的 2D 高斯协方差：

$$\boldsymbol{\Sigma}' = \mathbf{J}\mathbf{W}\,\boldsymbol{\Sigma}\,\mathbf{W}^\top\mathbf{J}^\top$$

像素颜色按深度排序的前向 alpha 混合（第 4 节已给）。这里有个**可微性陷阱**：排序不可微，3DGS 用**固定排序 + 可微混合**绕过——一旦排好序，alpha 混合的导数对每个高斯参数都有闭式。$\boldsymbol{\Sigma}$ 的正定性靠 $\boldsymbol{\Sigma}=\mathbf{R}\mathbf{S}\mathbf{S}^\top\mathbf{R}^\top$ 参数化保证，对 $\mathbf{R}$（四元数）、$\mathbf{S}$（对角）的梯度通过链式法则回传。这套可微 splatting 是 3DGS 能端到端训练的数学根基。

### 9.3 Score Distillation Sampling 的严格推导

设冻结的扩散模型 $\phi$ 学到了图像分布 $p_\phi$，其得分 $\nabla_\mathbf{x}\log p_\phi(\mathbf{x})$ 可用噪声预测 $\epsilon_\phi(\mathbf{x}_t,t)$ 估计：在加噪 $\mathbf{x}_t=\alpha_t\mathbf{x}+\sigma_t\boldsymbol{\epsilon}$ 下，$\nabla_\mathbf{x}\log p(\mathbf{x}_t)\approx-\epsilon_\phi/\sigma_t$（Tweedie 公式）。

DreamFusion 想优化 3D 参数 $\theta$（通过可微渲染 $g(\theta)$ 产生图像 $\mathbf{x}=g(\theta)$），使 $\mathbf{x}$ 的分布 $q(\mathbf{x};\theta)$ 尽量靠近 $p_\phi$。一个自然的损失是**KL 散度** $D_{\text{KL}}(q\|p_\phi)$。对其求 $\theta$ 的梯度，并利用扩散模型对加噪样本的得分，化简（详细推导见 DreamFusion 附录）得到：

$$\nabla_\theta \mathcal{L}_{\text{SDS}} = \mathbb{E}_{t,\boldsymbol{\epsilon}}\Big[w(t)\big(\epsilon_\phi(\mathbf{x}_t;t)-\boldsymbol{\epsilon}\big)\frac{\partial g(\theta)}{\partial\theta}\Big]$$

直觉：在每个优化步，给渲染图加随机噪声 $t$，让扩散模型预测"它认为多余的噪声"，预测噪声和真实噪声的差异就是"这张图偏离 $p_\phi$ 的方向"，把它反传给 $\theta$ 去修正。**这个梯度不依赖 $\partial\epsilon_\phi/\partial\mathbf{x}$（所以扩散模型可冻住）**，这正是 SDS 计算高效的秘密。

**VSD 的改进**：SDS 等价于在 $q$ 是单点 delta 分布时最小化一个近似的 KL，导致 mode-seeking。ProlificDreamer 把 $q(\mathbf{x};\theta)$ 当作真正可变的分布（$\theta$ 是随机变量，用一组粒子表示），推导出更准的梯度，含一个**关于 $q$ 自身得分的修正项**，这正是它多样且高保真的根源（数学细节见 arXiv:2305.16213 第 3 节）。SDS → VSD 的演进，本质是从"点估计"升级到"变分分布估计"，与强化学习里 REINFORCE → 策略梯度的思想异曲同工。

---

## 10. 数据集与基准

3D 研究依赖几大类数据，理解它们的差异有助于读懂论文里的数字。

**形状数据集（生成 / 分类用）：**
- **ShapeNet**（2015）：~51K 个 CAD 模型，55 类，是早期 3D 深度学习的 ImageNet。但风格"干净"、偏合成。
- **Objaverse**（2022，Allen AI）：**80 万+** 3D 资产，是 LRM、TRELLIS、Hunyuan3D 等"大模型时代"的基础数据。规模和多样性碾压 ShapeNet，是 3D 走向 scaling law 的关键。
- **Objaverse-XL**（2023）：进一步扩展到 1000 万+，跨多源。

**新视图合成（NVS）数据集（NeRF/3DGS 用）：**
- **Blender Dataset**（NeRF 论文自带）：合成场景（乐高、椅子…），8 个场景，完美已知位姿、无噪声，用于算法验证。
- **DTU**（Technical University of Denmark）：真实物体多视图扫描，带 RGB + mask + ground truth 网格，是**表面重建**（NeuS 等）的标准基准。共 128 场景。
- **Mip-NeRF 360**（自带数据集）：360° 环绕的真实无界场景（室内+室外），是当前**NVS 质量最高基准**，3DGS 也在此评测。9 个场景。
- **LLFF / Real Forward-Facing**：手机前向拍摄的小场景。

**生成基准：**
- **CLIP-score / FID / CMMD**：评估生成 3D 资产与文本/图像的对齐度和质量（Hunyuan3D 2.0 表用的就是这些）。
- **GSO（Google Scanned Objects）**：常作为生成物体的评测参考集。

> **基准使用的坑**：合成数据（Blender）的 PSNR 容易很高，但**不代表真实场景能力**；DTU 强测几何、Mip-NeRF 360 强测外观。比较两篇论文时务必确认它们在**同一数据集、同一指标（PSNR/SSIM/LPIPS）、同一训练/测试划分**上报告，否则数字不可比。

---

## 11. 2025–2026 前沿

2025 年起，3D 生成进入"**大模型 + 原生 3D 架构**"阶段，几个清晰趋势：

### 11.1 原生 3D 扩散 Transformer：Hunyuan3D 家族

> 论文：Tencent Hunyuan3D Team. **Hunyuan3D 1.0 / 2.0 / 2.5.** [arXiv:2411.02293](https://arxiv.org/abs/2411.02293)（1.0，2024）/ [arXiv:2501.12202](https://arxiv.org/abs/2501.12202)（2.0，2025-01）/ [arXiv:2506.16504](https://arxiv.org/abs/2506.16504)（2.5，2025-06）

腾讯混元 3D 是 2025 年**开源 3D 生成的领跑者**。2.0 是两阶段管线：**Hunyuan3D-DiT**（基于可扩展 flow-matching 扩散 transformer 的形状生成）+ **Hunyuan3D-Paint**（高分辨率纹理合成）。形状模型 1.1B、纹理模型 1.3B，在 CMMD/FID/CLIP-score 上全面超越同期开源与闭源方法（2.0 报告的 FID 282.4 / CLIP-score 0.809 均为当时最优）。后续 2.1（2025-06）开源了全部训练代码 + PBR 模型 + VAE 编码器，是迄今最完整的开源 3D 生成系统。**2.5（2506.16504）**进一步推向"极致细节"高保真资产。这些 ID 均来自 [官方 GitHub 仓库](https://github.com/Tencent/Hunyuan3D-2) 的 BibTeX，权威可靠。

### 11.2 从 3D 资产生成走向 3D 世界生成

**HunyuanWorld-1.0**（2025-07，腾讯）：官方称是**首个开源、具备仿真能力、沉浸式的 3D 世界生成模型**——不再只是生成单个物体，而是生成可漫游、可仿真的 3D 场景。这与 Genie（2D 交互世界）、Sora（视频世界）共同标志"世界模型"从概念走向工程。结合 world-ai4sci-math 卷的 `01-world-models/` 章节，可以看到清晰的收敛趋势：**3D 表征（NeRF/3DGS）+ 生成模型（diffusion/flow）+ 物理仿真 → 可交互的世界模型**。

### 11.3 其它值得关注的 2024–2025 方向

- **多视图前馈重建**：GS-LRM（2404.19702）、LGM（2402.05054，large multi-view gaussian model）把重建压缩到单次前馈。
- **3DGS 压缩与移动端**：LightGaussian、Compact3D、SOG 把数百 MB 的高斯压到几 MB，目标手机/AR 实时。
- **3DGS + SLAM**：GS-SLAM、SplaTAM 等把 3DGS 用于实时定位与建图。
- **物理感知高斯**：PhysGaussian、GaussianProperty 给高斯附加物理属性，支撑仿真。
- **大规模训练基础设施**：Grendel-GS（NYU，"On Scaling Up 3DGS Training"）研究多机训练超大场景。

> ⚠️ 2026 年的新论文请用 `export.arxiv.org/api/query` 实时检索，本章 ID 截止 2025-07 已全部一手核实。

---

## 12. 代码实战

### 12.1 用 nerfstudio 跑一个 NeRF / 3DGS

[nerfstudio](https://github.com/nerfstudio-project/nerfstudio) 是当前最完整的神经辐射场工程框架，统一支持 NeRF、Instant-NGP、3DGS、Splatfacto 等。

```bash
# 1. 安装（建议 conda 环境 + CUDA 11.8/12.x）
conda create -n nerfstudio python=3.10 -y && conda activate nerfstudio
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
pip install nerfstudio

# 2. 准备数据：用自带下载脚本取一个示例数据集（nerfstudio 官方 small scene）
ns-download-data nerfstudio --capture-name=poster

# 3. 训练一个 3DGS（Splatfacto，nerfstudio 的高斯实现）
ns-train splatfacto --data data/nerfstudio/poster

# 4. 训练一个 Instant-NGP
ns-train nerfacto --data data/nerfstudio/poster --vis viewer

# 训练时终端会打印 viewer 的 localhost 链接，浏览器打开即可实时看到新视角渲染。
```

### 12.2 自己的数据：从手机视频到 NeRF

```bash
# 用你手机绕物体拍 30–60 秒视频（绕一圈，慢而稳），导出为 video.mp4
ns-process-data video \
  --data video.mp4 \
  --output-dir data/myobject \
  --num-frames-target 120      # COLMAP 会从这些帧算位姿

# 然后训练
ns-train splatfacto --data data/myobject --vis viewer
```

### 12.3 用 TRELLIS / Hunyuan3D 做单图转 3D（2025 工业级）

```python
# Hunyuan3D 2.0（见官方仓库 https://github.com/Tencent/Hunyuan3D-2）
# pip install -e . （按官方 README 装好依赖后）
from hy3dgen.shapegen import Hunyuan3DDiTFlowMatchingPipeline
from hy3dgen.texgen import Hunyuan3DPaintPipeline

shape_pipe = Hunyuan3DDiTFlowMatchingPipeline.from_pretrained('tencent/Hunyuan3D-2')
mesh = shape_pipe(image='assets/demo.png')[0]          # 图 -> 裸 mesh
paint_pipe = Hunyuan3DPaintPipeline.from_pretrained('tencent/Hunyuan3D-2')
mesh = paint_pipe(mesh, image='assets/demo.png')        # mesh + 高分辨率纹理
mesh.export('output.glb')                                 # 导出可在 Blender/网页打开
```

> **运行建议**：形状生成约需 6 GB 显存，形状+纹理约 16 GB。代码示例来自腾讯官方 README，已在 2025-01 开源验证。

---

## 13. 用户建议：3D 是世界模型的基础

回到用户的核心命题——「应用数学研究型工程师」、对世界模型与具身智能感兴趣。3D 视觉在这个图景里的位置是：

1. **3D 表征是世界模型的"空间骨架"。** 一个能在物理世界里行动的智能体，必须在某个内部表征里编码"物体在哪、表面在哪、从新视角看会是什么样"。NeRF / 3DGS / SDF 是目前最成功的三类**可微、可渲染、可学习**的空间表征。世界模型（Sora、Genie、Veo）目前主要在 2D 像素 / 潜空间里生成，但要让生成的世界"可漫游、可碰撞、可仿真"，2D 必须升维到 3D——这正是 3DGS 走向物理仿真（PhysGaussian）、TRELLIS 走向多格式可编辑输出的动机。**学世界模型，先吃透 3D 表征。**

2. **数学锚点清晰，适合作为研究方向。** 本章的核心数学——辐射传输方程的解析解、体渲染的可微性、EWA splatting 的协方差投影、SDS/VSD 的得分蒸馏——都是**可在硕士阶段掌握、且仍有开放问题**的应用数学。可研究：可微渲染的偏差分析（NeuS 那种 first-order bias-free 还能推广吗？）、SDS 的理论收敛性、高斯表征与 SDF 的统一、物理先验如何注入可微渲染。这些都接得上用户的"概率/优化/数值分析"兴趣方向。

3. **动手路径（给工程基础强的零基础学习者）：**
   - **第一步（1–2 周）**：用 nerfstudio 拿手机视频训出一个自己的 3DGS，体会"可微渲染"的魔力（第 12 节代码可直接跑）。目标：直观理解辐射场。
   - **第二步（2–3 周）**：精读 NeRF（2003.08934）+ 3DGS（2308.04079）两篇原文，手推体渲染方程和 splatting 投影，用 NumPy 复现 alpha 混合（第 2 节代码）。目标：把数学吃进脑子。
   - **第三步（2–4 周）**：跑 TRELLIS 或 Hunyuan3D 做单图转 3D，理解"重建→生成"的范式跃迁。目标：进入 2025 前沿。
   - **第四步（长期）**：选一个开放问题深挖，比如"如何把 3DGS 接入物理仿真做可交互世界"（接 world-ai4sci-math 卷 `01-world-models/04-潜在+JEPA`），或"SDS 的理论改进"（接数学深讲第 9.3 节）。

4. **与其它卷的关系。** 本章是 `07-extended-tech` 的第 2 章，与 `01-world-models/`（世界模型）直接互为表里——世界模型负责"时间动力学"，3D 表征负责"空间结构"，二者正在融合（HunyuanWorld、Genie）。也与 `05-model-engineering/`（hash encoding、CUDA kernel、可微渲染工程）在工程层紧密相连。建议读本章时交叉参考。

---

## 14. 进一步阅读 + 思考题

### 📌 进一步阅读（按优先级）

1. **必读两篇奠基**：NeRF [arXiv:2003.08934](https://arxiv.org/abs/2003.08934) + 3DGS [arXiv:2308.04079](https://arxiv.org/abs/2308.04079)。吃透这两篇，整个领域的骨架就有了。
2. **加速与质量**：Instant-NGP [arXiv:2201.05989](https://arxiv.org/abs/2201.05989)（哈希编码）+ Mip-NeRF 360 [arXiv:2111.12077](https://arxiv.org/abs/2111.12077)（无界场景）。
3. **生成理论**：DreamFusion [arXiv:2209.14988](https://arxiv.org/abs/2209.14988)（SDS）+ ProlificDreamer [arXiv:2305.16213](https://arxiv.org/abs/2305.16213)（VSD，理论最干净）。
4. **大模型时代**：LRM [arXiv:2311.04400](https://arxiv.org/abs/2311.04400) + GS-LRM [arXiv:2404.19702](https://arxiv.org/abs/2404.19702) + TRELLIS [arXiv:2412.01506](https://arxiv.org/abs/2412.01506) + Hunyuan3D 2.0 [arXiv:2501.12202](https://arxiv.org/abs/2501.12202)。
5. **综述**：[Awesome 3DGS](https://github.com/MrNeRF/awesome-3D-gaussian-splatting)（社区维护，上千篇）；Gao et al. *NeRF: Neural Radiance Field in 3D Vision, A Comprehensive Review*（arXiv:2210.00379）。
6. **工程**：[nerfstudio 文档](https://docs.nerf.studio/) —— 最好的动手入门。

### ✍️ 思考题（5 道，由浅入深）

1. **（体渲染直觉）** 在第 2.3 节的 alpha 混合公式里，如果所有采样点的 $\sigma\to\infty$（完全不透明），射线颜色 $C(\mathbf{r})$ 会等于什么？这个极限对应物理上的什么情形？如果所有 $\sigma\to 0$（完全透明）又如何？请用 NumPy 验证你的预测。

2. **（位置编码的作用）** 假设把 NeRF 的位置编码 $\gamma(p)$ 的最大频率 $2^{L-1}$ 减半（$L$ 从 10 降到 5），渲染质量会怎么变？反过来若 $L$ 加大到 20 会怎样？请从**谱偏置**和**混叠（aliasing）**两个角度分别解释，并说明为什么 Mip-NeRF 用积分位置编码能同时缓解这两个问题。

3. **（NeRF vs 3DGS 的复杂度）** 对一张 $H\times W$ 的图，NeRF 沿每像素射线采 $N$ 个点，每点过一次 MLP；3DGS 有 $M$ 个高斯，每个投影到约 $k$ 个像素。请写出两者渲染一张图的**浮点运算量**渐近表达式。在什么条件下（$N,M,k,H,W$ 的关系）3DGS 比 NeRF 快？这是否能解释为什么 3DGS 在百万高斯时仍能实时？

4. **（SDS 的 mode-seeking）** 第 9.3 节指出 SDS 等价于"粒子数为 1 的 VSD"，导致过饱和、过平滑、低多样性。请从**KL 散度 $D_{\text{KL}}(q\|p)$ vs $D_{\text{KL}}(p\|q)$** 的方向性差异出发，解释为什么"把 3D 当单点（$q$ 是 delta）优化"会偏向 $p$ 的众数（mode-seeking），而把 3D 当分布（VSD）能覆盖 $p$ 的多峰。这个分析对理解"为什么 ProlificDreamer 多样性更好"是关键的。

5. **（开放题：3D 表征与世界模型）** 当前世界模型（Genie、Sora）主要在 2D / 潜空间生成。如果要构建一个"3D 原生"的世界模型——既能生成又能前向模拟、支持碰撞与物理交互——你会选 NeRF、3DGS 还是 SDF 作为底层表征？各自的可微仿真性、显存、编辑性、与物理引擎（如 MuJoCo、PhysX）的耦合难度如何权衡？请结合第 4.4 节的对比表和第 11 节的前沿趋势，给出你的论证。（提示：参考 PhysGaussian、HunyuanWorld，思考"可微渲染 + 可微物理"的统一框架。）

---

> **本章核实声明**：所有 arXiv ID 均于 2026-07-20 经 `arxiv.org/abs/<id>` 逐篇打开一手核实。共纠正 6 个流传错误 ID（3DGS、Shap-E、ProlificDreamer、SuGaR、GS-LRM、BlockNeRF），其中 5 个错误 ID 实际指向天体物理 / 代数几何论文，极具迷惑性。Gaussian-Pro 的 arXiv ID 未能在本轮确认（候选 ID 经核实为错误），已按"宁缺毋臆测"原则标注，引用时请查 ICML 2024 原文。

<!-- delegate 直接写入，2026-07-20 -->
