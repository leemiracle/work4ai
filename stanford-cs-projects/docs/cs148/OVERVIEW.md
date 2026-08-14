# CS148: Introduction to Computer Graphics and Imaging

> **课程官网**: http://cs148.stanford.edu/
> **学期**: Summer 2026（Kate Baker 主讲）
> **前置课程**: CS107（计算机系统）、MATH 51（线性代数）
> **语言要求**: 熟练的 Python
> **评分构成**: 作业 + 最终项目（光线追踪器）— **无考试！**
> **GER 认证**: 满足 WAY-CE（创意表达）通识要求
> **项目代码**: `topic11-graphics/ray_tracer.py`（Python 光线追踪器）

---

## 📚 课程定位

CS148 是斯坦福计算机图形学序列的**入门先修课程**，向学生介绍合成计算机生成图像背后的技术原理。课程由 **Kate Baker** 主讲（Summer 2026），以 **Blender**（工业级 3D 建模工具）为起点，逐步深入到底层的光线追踪数学与渲染算法。

### 教学理念

CS148 的独特之处在于**"从创作到理解"**（create then understand）的教学路径：

1. **先动手创作**——用 Blender 做出令人惊艳的视觉作品，建立对图形管线的直觉
2. **再理解原理**——拆解三角形、法线、插值、纹理映射等底层概念
3. **最终构建引擎**——期末项目是从零构建一个光线追踪器

评分侧重于**现场 demo**（in-person demos）——不看代码本身有多漂亮，而看你用代码创造出了多震撼的视觉图像。**创造力与视觉冲击力被高度鼓励。**

### 与其他图形学课程的关系

| 课程 | 层次 | 重点 |
|------|------|------|
| **CS148** | 入门 | 图形管线全景 + Blender + 光线追踪入门 |
| CS248A | 中级 | 实时渲染（GPU、光栅化、着色器）|
| CS348B | 高级 | 高级渲染算法（路径追踪、蒙特卡洛）|
| CS348C | 高级 | 物理仿真与动画 |

---

## 🎯 学习目标

完成本课程后，你将能够：

1. **理解渲染管线的全流程**——从 3D 几何到屏幕上 2D 像素的完整链路
2. **熟练使用 Blender**——建模、材质、灯光、渲染
3. **掌握图形学数学基础**——向量运算、变换矩阵、插值、光照方程
4. **理解光与颜色的物理学**——光谱、色彩空间、HDR、色调映射
5. **实现光线追踪器**——光线-物体求交、阴影、反射、抗锯齿
6. **评估渲染质量**——走样与抗走样、加速结构、蒙特卡洛采样

---

## 📅 完整模块（按周/讲）

### 第 1-2 周：扫描线渲染与几何基础

| 讲次 | 主题 | 关键概念 |
|------|------|----------|
| L1 | Introduction & Blender basics | CG 全景、Blender 界面、基本建模 |
| L2 | Triangles & rasterization | 三角形是最基本的图元、扫描线算法 |
| L3 | Coordinate systems & transforms | 模型/视图/投影变换、齐次坐标 |
| L4 | Transformations deep dive | 平移/旋转/缩放矩阵、组合变换 |

**作业**: Blender 建模练习——用基本几何体构建场景

### 第 3-4 周：着色与网格

| 讲次 | 主题 | 关键概念 |
|------|------|----------|
| L5 | Shading basics | 法线、朗伯漫反射、Flat/Gouraud/Phong 着色 |
| L6 | Triangle meshes | 网格表示、索引、拓扑 |
| L7 | Subdivision surfaces | Catmull-Clark 细分曲面、平滑 |
| L8 | Marching Cubes | 等值面提取、体素→三角网格 |

### 第 5-6 周：纹理映射与光/色理论

| 讲次 | 主题 | 关键概念 |
|------|------|----------|
| L9 | Texture mapping | UV 映射、纹理坐标、Mipmap |
| L10 | Bump & displacement mapping | 法线贴图、视差贴图、位移贴图 |
| L11 | Light & color fundamentals | 光谱、辐射度量学（辐射通量/辐照度/辐射强度）|
| L12 | Color spaces & displays | sRGB、CIE 色度图、色域、Gamma 校正 |

### 第 7-8 周：光照方程与 BRDF

| 讲次 | 主题 | 关键概念 |
|------|------|----------|
| L13 | BRDF & reflection models | 双向反射分布函数、镜面反射、漫反射 |
| L14 | Lighting equation (渲染方程) | 全局光照概念、直接/间接光照 |
| L15 | Cameras & displays | 针孔相机模型、景深、曝光、色调映射 (Tone Mapping) |
| L16 | Global illumination overview | 辐射度 (Radiosity)、路径追踪简介 |

### 第 9-10 周：光线追踪与高级渲染

| 讲次 | 主题 | 关键概念 |
|------|------|----------|
| L17 | Ray tracing fundamentals | 光线表示、光线-球/平面求交、递归追踪 |
| L18 | Acceleration structures | 包围盒 (BVH)、空间划分 (KD-Tree)、网格 |
| L19 | Sampling & antialiasing | 超采样、抖动采样、蒙特卡洛积分 |
| L20 | Advanced ray tracing | 反射、折射（透射）、景深、运动模糊 |

### 第 11 周：蒙特卡洛与期末项目

| 讲次 | 主题 | 关键概念 |
|------|------|----------|
| L21 | Monte Carlo ray tracing | 重要性采样、方差缩减、双向光追 |
| L22 | Light maps & baking | 预计算光照、纹理烘焙 |
| L23 | Final project workshop | 构建完整光线追踪器 |

---

## 🧮 核心算法/数学

### 1. 变换矩阵（Transformations）

所有图形学变换都是 **4×4 齐次坐标矩阵**：

**平移**：
$$T = \begin{bmatrix} 1 & 0 & 0 & t_x \\ 0 & 1 & 0 & t_y \\ 0 & 0 & 1 & t_z \\ 0 & 0 & 0 & 1 \end{bmatrix}$$

**绕 Z 轴旋转**（角度 θ）：
$$R_z(\theta) = \begin{bmatrix} \cos\theta & -\sin\theta & 0 & 0 \\ \sin\theta & \cos\theta & 0 & 0 \\ 0 & 0 & 1 & 0 \\ 0 & 0 & 0 & 1 \end{bmatrix}$$

**透视投影**（焦距 f）：
$$P = \begin{bmatrix} f & 0 & 0 & 0 \\ 0 & f & 0 & 0 \\ 0 & 0 & 1 & 0 \\ 0 & 0 & -1 & 0 \end{bmatrix}$$

变换组合顺序：$M = T \cdot R \cdot S$（先缩放，再旋转，再平移）——矩阵乘法**不可交换**！

### 2. 光线-物体求交（Ray-Object Intersection）

光线方程：$\mathbf{r}(t) = \mathbf{o} + t\mathbf{d}$（原点 + 方向 × 参数）

**光线-球体求交**（球心 $\mathbf{c}$，半径 $r$）：
$$\|\mathbf{o} + t\mathbf{d} - \mathbf{c}\|^2 = r^2$$
展开为二次方程 $at^2 + bt + c = 0$，其中：
- $a = \mathbf{d} \cdot \mathbf{d}$
- $b = 2\mathbf{d} \cdot (\mathbf{o} - \mathbf{c})$
- $c = (\mathbf{o} - \mathbf{c}) \cdot (\mathbf{o} - \mathbf{c}) - r^2$

判别式 $\Delta = b^2 - 4ac > 0$ → 两个交点，取最近的正根。

**光线-平面求交**（平面法线 $\mathbf{n}$，平面点 $\mathbf{p}_0$）：
$$t = \frac{(\mathbf{p}_0 - \mathbf{o}) \cdot \mathbf{n}}{\mathbf{d} \cdot \mathbf{n}}$$

### 3. Phong 光照模型

$$I = k_a I_a + \sum_{\text{lights}} \left[ k_d (\mathbf{N} \cdot \mathbf{L}) + k_s (\mathbf{R} \cdot \mathbf{V})^{n_s} \right] I_l$$

| 分量 | 含义 |
|------|------|
| $k_a I_a$ | 环境光（ambient）—— 常数，模拟间接光照 |
| $k_d (\mathbf{N} \cdot \mathbf{L})$ | 漫反射（diffuse）—— N 为法线，L 为光照方向 |
| $k_s (\mathbf{R} \cdot \mathbf{V})^{n_s}$ | 镜面高光（specular）—— R 为反射方向，V 为视线方向，$n_s$ 为光泽度 |

反射方向：$\mathbf{R} = 2(\mathbf{N} \cdot \mathbf{L})\mathbf{N} - \mathbf{L}$

### 4. BRDF（双向反射分布函数）

$$f_r(\omega_i, \omega_o) = \frac{dL_o(\omega_o)}{L_i(\omega_i) \cos\theta_i \, d\omega_i}$$

描述从方向 $\omega_i$ 入射的光有多少被反射到方向 $\omega_o$。

**渲染方程**（Rendering Equation, Kajiya 1986）：
$$L_o(\mathbf{x}, \omega_o) = L_e(\mathbf{x}, \omega_o) + \int_{\Omega} f_r(\omega_i, \omega_o) L_i(\mathbf{x}, \omega_i) \cos\theta_i \, d\omega_i$$

这是所有全局光照算法的数学基础。光线追踪用蒙特卡洛方法对这个积分进行数值估计。

### 5. 蒙特卡洛积分

$$\int f(x) dx \approx \frac{1}{N} \sum_{i=1}^{N} \frac{f(x_i)}{p(x_i)}$$

其中 $x_i$ 按概率密度 $p$ 采样。方差与 $\sqrt{N}$ 成反比——这就是为什么蒙特卡洛路径追踪**收敛慢**但**极其通用**。

---

## 💻 项目代码

### `topic11-graphics/ray_tracer.py`

**实现内容**：Python 教学版光线追踪器，涵盖 CS148 后半学期核心内容。

| 模块 | 类/函数 | 功能 |
|------|---------|------|
| 向量数学 | `Vec3` (frozen dataclass) | 加/减/乘/点积/叉积/归一化 |
| 几何体 | `Sphere`, `Plane` | 光线求交 `intersect(ray)` + 法线计算 |
| 光线 | `Ray` | 原点 + 方向 + `at(t)` 采样点 |
| 光源 | `Light` | 位置 + 颜色 + 强度 |
| Phong 光照 | `phong_shading()` | 环境光 + 漫反射 + 镜面高光 |
| 阴影 | `trace_ray()` | 发射阴影光线检测遮挡 |
| 渲染器 | `render_ascii()` | ASCII 艺术输出（无需图形库）|
| 场景 | `Scene` | 管理物体列表 + 光源列表 |

**运行命令**:
```bash
cd topic11-graphics
python3 ray_tracer.py
# 输出: ASCII 渲染的球体场景 + 可选 PPM 图像输出
```

**关键算法对应**:

```
render_ascii()
  ├── 对每个像素发射光线 (primary ray)
  ├── 遍历场景物体，找最近交点 (ray-object intersection)
  ├── 计算法线 + Phong 着色 (lighting equation)
  ├── 发射阴影光线 (shadow ray) → 检测是否被遮挡
  └── 映射亮度到 ASCII 字符集 " .:-=+*#%@"
```

### 对应的课程作业（CS148 原版）

| 作业 | 名称 | 工具 | 重点 |
|------|------|------|------|
| HW1 | Blender modeling | Blender | 基本建模、材质 |
| HW2 | Materials & lighting | Blender | PBR 材质、三点光照 |
| HW3 | Procedural geometry | Python | Marching Cubes、细分 |
| HW4 | Ray tracer foundation | Python/C++ | 光线求交 + Phong |
| HW5 | Shading & shadows | Python/C++ | 阴影 + 反射 |
| **Final** | **Complete ray tracer** | Python/C++ | **完整渲染器 + 创意场景** |

---

## 📊 关键论文/教材

### 奠基性论文

- **Kajiya (1986)**. [The Rendering Equation](https://dl.acm.org/doi/10.1145/15922.15902). *SIGGRAPH*. — 全局光照的数学基础，定义了渲染方程
- **Whitted (1980)**. [An Improved Illumination Model for Shaded Display](https://www.cs.drexel.edu/~david/Classes/Papers/p343-whitted.pdf). *CACM*. — 递归光线追踪的起源
- **Cook, Porter, Carpenter (1984)**. [Distributed Ray Tracing](https://dl.acm.org/doi/10.1145/800031.808590). *SIGGRAPH*. — 超采样抗锯齿、软阴影、运动模糊
- **Veach (1997)**. [Robust Monte Carlo Methods for Light Transport](https://www.stat.uchicago.edu/~lekheng/courses/191/veach.pdf). *PhD Thesis, Stanford*. — 多重重要性采样、双向路径追踪
- **Lorensen & Cline (1987)**. [Marching Cubes](https://dl.acm.org/doi/10.1145/37402.37422). *SIGGRAPH*. — 等值面提取经典算法

### 推荐教材与资源

- **Shirley**. [*Ray Tracing in One Weekend*](https://raytracing.github.io/books/RayTracingInOneWeekend.html) — **强烈推荐**，免费在线，CS148 光线追踪作业的直接参考
- **Pharr, Jakob, Humphrey**. [*Physically Based Rendering: From Theory to Implementation*](http://www.pbr-book.org/) (PBRT). — 渲染领域的圣经，免费在线
- **Marschner & Shirley**. *Fundamentals of Computer Graphics*. — 经典教材
- **Blender 官方文档** & [Blender Guru 教程](https://www.blenderguru.com/) — Blender 实战

---

## 🎯 学习路径

```
Week 1-2  ┌─ Blender + 渲染管线全景（先"玩"起来）
          │   └─ 直觉理解：3D 怎么变成 2D 像素？
          │
Week 3-4  ├─ 几何与变换（数学基础）
          │   └─ 矩阵变换：所有几何操作的统一语言
          │   ⚠️ 线性代数是硬门槛，MATH 51 是前置
          │
Week 5-6  ├─ 纹理 + 光/色（物理直觉）
          │   └─ 理解"颜色"不是物理量，是人类感知
          │
Week 7-8  ├─ BRDF + 渲染方程（理论核心）
          │   └─ ⚠️ 渲染方程是图形学的"大统一理论"
          │
Week 9-10 ├─ 光线追踪实现（动手构建）
          │   └─ 先跑 Python 版 ray_tracer.py 建立直觉
          │
Week 11   └─ 期末项目：构建完整光线追踪器
              └─ 重点：创意 + 视觉冲击力 > 代码技巧
```

### 给自学者的建议

1. **先装 Blender 跟着教程做一个甜甜圈**——[Blender Guru Donut Tutorial](https://www.youtube.com/watch?v=TPrnSACiTJ4)，2 小时建立直觉
2. **然后读 *Ray Tracing in One Weekend***——跟着写一个 100 行的光线追踪器
3. **本项目的 `ray_tracer.py` 可作为参考**——它是纯 Python 无依赖版，ASCII 输出无需安装图形库
4. **重点理解三个方程**：光线方程、Phong 光照、渲染方程
5. **期末项目重在创意**——做一个有故事、有美感的场景比写复杂的算法更得分

---

## 💡 反思

### CS148 的独特价值

1. **艺术与工程的交叉**：作为 WAY-CE（创意表达）课程，CS148 是少有的"左脑+右脑"课程。你不仅在写算法，更在创造美。
2. **Blender 优先**：先用工业工具做出专业级作品，再理解底层原理——这是"top-down"的教学智慧。
3. **无考试**：100% 项目驱动，鼓励迭代和打磨。
4. **社区驱动**：CS148 的 CA 团队（包括 Lvmin Zhang 等）提供丰富的 office hours 和现场 grading。

### 常见学习陷阱

- **数学恐惧**：图形学重度依赖线性代数。如果你对矩阵乘法不熟，先复习 MATH 51。
- **光追性能焦虑**：Python 光追很慢是正常的。重点在算法正确性，不在速度（那是 CS348B 的事）。
- **忽视创意**：技术只是手段，视觉作品才是目的。不要花 10 小时优化代码却只花 1 小时设计场景。

---

## 🚀 扩展

### 深入方向

| 方向 | 推荐课程/资源 |
|------|---------------|
| 实时渲染 / GPU | Stanford **CS248A**（计算机图形学中级）|
| 高级渲染 | Stanford **CS348B**（高级渲染，路径追踪大师课）|
| 物理仿真 | Stanford **CS348C**（仿真与动画）|
| 计算摄影 | Stanford **CS478**（计算摄影）|
| 游戏引擎 | 学习 Unreal Engine 5 (Nanite/Lumen) 或 Godot 源码 |
| 工业级光追 | 阅读 [NVIDIA OptiX](https://developer.nvidia.com/rtx/optix) 和 [PBRT-v4](https://github.com/mmp/pbrt-v4) 源码 |

### 实战项目建议

1. **扩展 `ray_tracer.py` 添加反射和折射**——递归追踪实现玻璃球效果
2. **实现 BVH 加速结构**——让光追支持 10000+ 三角形场景
3. **加入蒙特卡洛软阴影**——从硬阴影升级到物理正确的区域光
4. **实现路径追踪 (Path Tracing)**——求解渲染方程的完整全局光照
5. **用 Blender 制作动画短片**——从 CS148 走向独立创作者

### 与其他课程的关系

```
CS107 (系统) + MATH51 (线代) ──> CS148 (图形学入门)
                                     │
          CS248A (实时渲染) <────────┤
          CS348B (高级渲染) <────────┤
          CS348C (物理仿真) <────────┘
```

CS148 是图形学世界的"入口"——无论你走向实时渲染（游戏/VR）、离线渲染（电影特效）还是仿真（物理引擎），CS148 都为你打下了从数学到创作的完整基础。

---

> *"Graphics is the art of making computers paint with light."* — CS148 精神
