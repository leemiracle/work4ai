# 数学知识词典 - 第四卷：几何与拓扑
## Volume IV: Geometry and Topology

**MSC分类**: 51-XX, 53-XX, 54-XX, 55-XX, 57-XX, 58-XX  
**版本**: 1.0  
**日期**: 2025-03-26

---

## 目录

1. [微分几何 (53-XX)](#1-微分几何)
2. [黎曼几何 (53-XX)](#2-黎曼几何)
3. [代数拓扑 (55-XX)](#3-代数拓扑)
4. [流形理论 (57-XX)](#4-流形理论)
5. [整体分析 (58-XX)](#5-整体分析)

---

## 1. 微分几何 (53-XX)

### 1.1 微分流形 [53Axx]

#### 定义 XXVI.1.1 (微分流形)
**Definition XXVI.1.1 (Smooth Manifolds)**

**n维微分流形** M 是Hausdorff拓扑空间配备:
1. **图册**: 坐标卡族{(U_α, φ_α)}
   - U_α ⊆ M开
   - φ_α: U_α → ℝ^n 同胚
2. **相容性**: φ_β∘φ_α^{-1}: φ_α(U_α∩U_β) → ℝ^n 光滑
3. **极大性**: 图册极大

**例子**:
- ℝ^n (标准流形)
- S^n (球面): n+1个坐标卡
- ℝP^n (实射影空间): n+1个坐标卡
- GL(n,ℝ) (一般线性群)
- Lie群

#### 定义 XXVI.1.2 (切空间)
**Definition XXVI.1.2 (Tangent Spaces)**

**切向量**: p点处方向导数的等价类

**切空间** T_pM: p点处所有切向量构成的n维向量空间

**构造**:
1. **导数定义**: T_pM ≅ {D: C^∞(M) → ℝ 线性, Leibniz法则}
2. **曲线定义**: 等价类[γ']，γ(0)=p
3. **坐标定义**: ∂/∂x_i|_p (局部坐标)

**切丛**: TM = ⋃_{p∈M} T_pM (2n维流形)

---

### 1.2 向量场与微分形式 [53Axx]

#### 定义 XXVI.2.1 (向量场)
**Definition XXVI.2.1 (Vector Fields)**

**向量场** X: M → TM的光滑截面，即X(p) ∈ T_pM

**Lie括号**: [X,Y]f = XYf - YXf
- 反对称: [X,Y] = -[Y,X]
- Jacobi恒等式: [X,[Y,Z]] + [Y,[Z,X]] + [Z,[X,Y]] = 0

**流**: φ_t: X的积分曲线，(d/dt)φ_t(p) = X(φ_t(p))

#### 定义 XXVI.2.2 (微分形式)
**Definition XXVI.2.2 (Differential Forms)**

**k-形式** ω ∈ Ω^k(M): 反对称k阶协变张量场

**外微分**: d: Ω^k(M) → Ω^{k+1}(M)
- d(dω) = 0 (Poincaré引理局部成立)
- d(f dx^{i₁}∧...∧dx^{i_k}) = df∧dx^{i₁}∧...∧dx^{i_k}

**楔积**: ∧: Ω^k × Ω^ℓ → Ω^{k+ℓ}
- α∧β = (-1)^{kℓ}β∧α

**例子**:
- 0-形式: 光滑函数f
- 1-形式: df = Σ (∂f/∂x_i)dx^i
- n-形式 (M是n维): 体积形式

#### 定理 26.1 (Stokes定理)
**Theorem 26.1 (Stokes' Theorem)**

设M是n维定向流形(带边界∂M)，ω是(n-1)-形式(紧支集)。则:
```
∫_M dω = ∫_{∂M} ω
```

*特例*:
1. **微积分基本定理**: ∫_[a,b] df = f(b) - f(a)
2. **Green定理**: ∫_D (∂Q/∂x - ∂P/∂y)dxdy = ∮_{∂D} Pdx + Qdy
3. **Gauss定理**: ∫_V ∇·F dV = ∫_{∂V} F·n dS
4. **Kelvin-Stokes**: ∫_Σ (∇×F)·n dS = ∮_{∂Σ} F·dl

*证明*. 局部坐标 + 单位分解。 □

---

### 1.3 联络 [53Axx]

#### 定义 XXVI.3.1 (仿射联络)
**Definition XXVI.3.1 (Affine Connections)**

**仿射联络** ∇: TM × Γ(TM) → Γ(TM), (X,Y) ↦ ∇_X Y

满足:
1. ∇_{fX+gY} Z = f∇_X Z + g∇_Y Z (对X线性)
2. ∇_X (Y+Z) = ∇_X Y + ∇_X Z (对Y加性)
3. ∇_X (fY) = (Xf)Y + f∇_X Y (Leibniz法则)

**Christoffel符号**: ∇_{∂/∂x^i} (∂/∂x^j) = Γ^k_{ij} ∂/∂x^k

**测地线**: ∇_{γ̇} γ̇ = 0
```
(d²x^k/dt²) + Γ^k_{ij} (dx^i/dt)(dx^j/dt) = 0
```

**例子**:
- ℝ^n的标准联络: ∇_X Y = (X(Y¹),...,X(Y^n))，Γ^k_{ij}=0
- 浸入子流形的诱导联络

#### 定义 XXVI.3.2 (挠率与曲率)
**Definition XXVI.3.2 (Torsion and Curvature)**

**挠率张量**: T(X,Y) = ∇_X Y - ∇_Y X - [X,Y]

**曲率张量**: R(X,Y)Z = ∇_X∇_Y Z - ∇_Y∇_X Z - ∇_{[X,Y]} Z

**分量形式**:
- T^k_{ij} = Γ^k_{ij} - Γ^k_{ji}
- R^ℓ_{ijk} = ∂_iΓ^ℓ_{jk} - ∂_jΓ^ℓ_{ik} + Γ^ℓ_{im}Γ^m_{jk} - Γ^ℓ_{jm}Γ^m_{ik}

**Bianchi恒等式**:
1. 第一恒等式: R(X,Y)Z + R(Y,Z)X + R(Z,X)Y = 0 (挠率=0时)
2. 第二恒等式: (∇_X R)(Y,Z) + (∇_Y R)(Z,X) + (∇_Z R)(X,Y) = 0

---

## 2. 黎曼几何 (53-XX)

### 2.1 黎曼度量 [53Bxx]

#### 定义 XXVII.1.1 (黎曼度量)
**Definition XXVII.1.1 (Riemannian Metrics)**

**黎曼度量** g: 对每点p ∈ M指定内积g_p: T_pM × T_pM → ℝ，光滑变化

**局部表示**: g = g_{ij} dx^i ⊗ dx^j = g_{ij} dx^i dx^j

**例子**:
- ℝ^n: g = dx₁² + ... + dx_n² (标准度量)
- S^n: 诱导度量
- 双曲空间H^n: (dx₁² + ... + dx_n²)/x_n²
- Lie群: 双不变度量

**黎曼流形**: (M,g)

#### 定理 27.1 (黎曼度量的存在性)
**Theorem 27.1 (Existence of Riemannian Metrics)**

每个微分流形都容许黎曼度量。

*证明*. 局部构造 + 单位分解。 □

---

### 2.2 Levi-Civita联络 [53Bxx]

#### 定理 27.2 (Levi-Civita定理)
**Theorem 27.2 (Levi-Civita Theorem)**

在黎曼流形(M,g)上存在唯一的无挠度量联络∇，称为**Levi-Civita联络**:
1. 无挠: T(X,Y) = 0
2. 度量: X⟨Y,Z⟩ = ⟨∇_X Y, Z⟩ + ⟨Y, ∇_X Z⟩

**Christoffel符号**:
```
Γ^k_{ij} = (1/2)g^{kℓ}(∂_i g_{jℓ} + ∂_j g_{iℓ} - ∂_ℓ g_{ij})
```

*证明*. Koszul公式:
```
2⟨∇_X Y, Z⟩ = X⟨Y,Z⟩ + Y⟨Z,X⟩ - Z⟨X,Y⟩ + ⟨[X,Y],Z⟩ - ⟨[Y,Z],X⟩ + ⟨[Z,X],Y⟩
```
□

---

### 2.3 曲率 [53Bxx]

#### 定义 XXVII.3.1 (黎曼曲率张量)
**Definition XXVII.3.1 (Riemann Curvature Tensor)**

**黎曼曲率张量**: R ∈ T^0_4(M)
```
R(X,Y,Z,W) = ⟨R(X,Y)Z, W⟩
```

**对称性**:
1. R(X,Y,Z,W) = -R(Y,X,Z,W)
2. R(X,Y,Z,W) = -R(X,Y,W,Z)
3. R(X,Y,Z,W) = R(Z,W,X,Y)
4. 第一Bianchi: R(X,Y,Z,W) + R(Y,Z,X,W) + R(Z,X,Y,W) = 0

**Ricci曲率**: Ric(X,Y) = tr(R(·,X)Y) = R^k_{ikj} (缩并)

**标量曲率**: R = g^{ij} Ric_{ij} (Ricci的迹)

#### 定义 XXVII.3.2 (截面曲率)
**Definition XXVII.3.2 (Sectional Curvature)**

对线性无关的X,Y ∈ T_pM，**截面曲率**:
```
K(X,Y) = R(X,Y,Y,X) / (||X||²||Y||² - ⟨X,Y⟩²)
```

**几何意义**: 由X,Y张成的2维子空间的Gauss曲率

**常曲率空间**:
- K ≡ c > 0: 球面S^n (半径1/√c)
- K ≡ 0: 欧氏空间ℝ^n
- K ≡ c < 0: 双曲空间H^n

#### 定理 27.3 (Gauss-Bonnet定理)
**Theorem 27.3 (Gauss-Bonnet Theorem)**

**局部形式** (曲面): 对紧曲面(M,g)带边界∂M:
```
∫_M K dA + ∫_{∂M} κ_g ds = 2πχ(M)
```
其中K是Gauss曲率，κ_g是测地曲率，χ是Euler示性数。

**整体形式** (2n维):
```
∫_M Pf(-R/2π) = χ(M)
```
Pf是Pfaffian。

*意义*: 曲率的拓扑不变性

*证明*. 三角剖分 + Gauss曲率定义。 □

---

### 2.4 测地线 [53Bxx]

#### 定理 27.4 (测地线的存在唯一性)
**Theorem 27.4 (Existence and Uniqueness of Geodesics)**

对任意p ∈ M和v ∈ T_pM，存在唯一的极大测地线γ: I → M使得γ(0)=p, γ̇(0)=v。

**指数映射**: exp_p: T_pM → M, exp_p(v) = γ_v(1)

**定义域**: 存在ε>0使exp_p在B_ε(0)上有定义

**正规邻域**: 存在δ>0使exp_p: B_δ(0) → B_δ(p)是微分同胚

#### 定理 27.5 (Hopf-Rinow定理)
**Theorem 27.5 (Hopf-Rinow Theorem)**

对完备黎曼流形M，以下等价:
1. 测地完备: 每条测地线可无限延伸
2. 度量完备: (M,d)是完备度量空间
3. 有界闭集紧

*推论*:
1. 任意两点可用最短测地线连接
2. M是完备的 ⟺ exp_p对全T_pM有定义

*证明*. 测地线的变分性质。 □

---

### 2.5 Jacobi场 [53Bxx]

#### 定义 XXVII.5.1 (Jacobi场)
**Definition XXVII.5.1 (Jacobi Fields)**

沿测地线γ的**Jacobi场** J满足Jacobi方程:
```
D²J/dt² + R(J,γ̇)γ̇ = 0
```

**几何意义**: 测地线变分的变分场

**例子**:
- γ̇ (切方向): J(t) = tγ̇
- 垂直方向: 刻画附近测地线的分离

**共轭点**: 存在非零Jacobi场J使J(0)=J(t₀)=0

**定理**: p的共轭点集是exp_p的临界值。

---

## 3. 代数拓扑 (55-XX)

### 3.1 基本群 [55Pxx]

#### 定义 XXVIII.1.1 (基本群)
**Definition XXVIII.1.1 (Fundamental Group)**

**道路**: γ: [0,1] → M连续

**道路同伦**: γ₀ ∼ γ₁ 如果存在H: [0,1]×[0,1] → M使H(·,0)=γ₀, H(·,1)=γ₁

**基本群** π₁(M,x₀): 基于x₀的闭路同伦类，配备拼接运算

**性质**:
- 群结构
- 基点无关(若M道路连通)
- 同胚不变量

**例子**:
- π₁(ℝ^n) = {1} (可缩)
- π₁(S¹) = ℤ
- π₁(T²) = ℤ²
- π₁(ℝP²) = ℤ/2ℤ

#### 定理 28.1 (van Kampen定理)
**Theorem 28.1 (van Kampen's Theorem)**

设M = U ∪ V，U,V,U∩V道路连通。则:
```
π₁(M) = π₁(U) *_{π₁(U∩V)} π₁(V)  (推出)
```

*应用*: 计算图的π₁(自由群)、多边形的π₁

---

### 3.2 覆盖空间 [55Pxx]

#### 定义 XXVIII.2.1 (覆盖空间)
**Definition XXVIII.2.1 (Covering Spaces)**

**覆盖映射** p: Ê → E: 每点有邻域U使p^{-1}(U) = ⊔ V_α，每个V_α同胚于U

**通用覆盖**: Ê单连通

**例子**:
- ℝ → S¹, t ↦ e^{2πit} (通用覆盖)
- Sⁿ → ℝPⁿ, x ↦ {x,-x} (二重覆盖)
- S³ → SO(3) (二重覆盖，Spin群)

#### 定理 28.2 (Galois对应)
**Theorem 28.2 (Galois Correspondence)**

对道路连通、局部道路连通、半局部单连通的空间X:
```
{覆盖空间 p: Ê → X}/≃ ⟷ {π₁(X)的子群}
Ê ↦ p_*(π₁(Ê))
```

*证明*. 单值化定理。 □

---

### 3.3 同调论 [55Nxx]

#### 定义 XXVIII.3.1 (单纯同调)
**Definition XXVIII.3.1 (Simplicial Homology)**

**单纯复形**: K = {单形σ} (点、边、三角形...)

**链复形**: C_n(K) = n维单形生成的自由Abel群

**边缘算子**: ∂_n: C_n → C_{n-1}
```
∂[v₀,...,v_n] = Σ_{i=0}^n (-1)^i [v₀,...,v̂_i,...,v_n]
```

**同调群**: H_n(K) = Ker(∂_n)/Im(∂_{n+1})

**直观**:
- H₀: 连通分支
- H₁: 1维洞
- H₂: 2维空腔

#### 定理 28.3 (Euler-Poincaré公式)
**Theorem 28.3 (Euler-Poincaré Formula)**

**Euler示性数**: χ(K) = Σ_{i} (-1)^i rank H_i(K) = Σ_{i} (-1)^i (i维单形数)

**例子**:
- χ(S²) = 2
- χ(T²) = 0
- χ(ℝP²) = 1

---

### 3.4 上同调 [55Nxx]

#### 定义 XXVIII.4.1 (奇异上同调)
**Definition XXVIII.4.1 (Singular Cohomology)**

**上链**: C^n(X;G) = Hom(C_n(X), G)

**上边缘**: δ: C^n → C^{n+1}, (δf)(σ) = f(∂σ)

**上同调群**: H^n(X;G) = Ker(δ^n)/Im(δ^{n-1})

**杯积**: ⌣: H^p × H^q → H^{p+q}

**性质**:
1. H^n(X;ℤ) = [X, K(ℤ,n)] (Eilenberg-MacLane空间)
2. de Rham定理: H^n_{dR}(M) ≅ H^n(M;ℝ)
3. Poincaré对偶: H^k(M) ≅ H_{n-k}(M) (M紧定向n维流形)

---

### 3.5 特征类 [55Rxx]

#### 定义 XXVIII.5.1 (Stiefel-Whitney类)
**Definition XXVIII.5.1 (Stiefel-Whitney Classes)**

对n维实向量丛E → B，**Stiefel-Whitney类** w_i(E) ∈ H^i(B;ℤ/2)

**公理**:
1. w_0(E) = 1, w_i(E) = 0 (i > rank E)
2. 自然性
3. Whitney和: w(E⊕F) = w(E)⌣w(F)
4. w_1(γ¹) ≠ 0 (γ¹是ℝP^∞上的万有线丛)

**应用**:
- w_1(TM)=0 ⟺ M可定向
- w_n(TM) ≠ 0 ⟺ M无处处非零向量场

#### 定义 XXVIII.5.2 (陈类)
**Definition XXVIII.5.2 (Chern Classes)**

对复向量丛E → B，**陈类** c_i(E) ∈ H^{2i}(B;ℤ)

**性质**:
1. c(E⊕F) = c(E)⌣c(F)
2. c_1(γ¹) ≠ 0 (γ¹是ℂP^∞上的万有线丛)

**例子**:
- c(TℂP^n) = (1+x)^{n+1}，x = c_1(γ¹)
- c_1(L⊗L') = c_1(L) + c_1(L') (线丛)

---

## 4. 流形理论 (57-XX)

### 4.1 微分拓扑基础 [57Rxx]

#### 定理 29.1 (Whitney嵌入定理)
**Theorem 29.1 (Whitney Embedding Theorem)**

光滑n维流形M可嵌入ℝ^{2n}，浸入ℝ^{2n-1} (n > 0)。

*改进*: 可嵌入ℝ^{2n-1} (n > 1，某些情况)。

*证明*. 浸入的稠密性 + 逼近。 □

#### 定理 29.2 (Sard定理)
**Theorem 29.2 (Sard's Theorem)**

对光滑映射f: M → N，临界值集的测度为零。

*推论*: 正则值稠密。

*证明*. 归纳法 + 零测集性质。 □

---

### 4.2 横截性 [57Rxx]

#### 定义 XXIX.2.1 (横截性)
**Definition XXIX.2.1 (Transversality)**

映射f: M → N与子流形S ⊆ N**横截** (f ⋔ S) 如果:
```
T_{f(p)}N = df_p(T_pM) + T_{f(p)}S  (对所有p ∈ f^{-1}(S))
```

**定理**: f ⋔ S ⟹ f^{-1}(S)是M的子流形，维数 = dim M - (dim N - dim S)

**Thom横截性定理**: 对任意f，存在任意逼近f的光滑g使g ⋔ S。

---

### 4.3 Morse理论 [57Rxx]

#### 定义 XXIX.3.1 (Morse函数)
**Definition XXIX.3.1 (Morse Functions)**

**临界点**: df(p) = 0

**非退化**: Hessian在临界点非奇异

**Morse函数**: 所有临界点非退化

**Morse指标**: 临界点处Hessian的负特征值个数

#### 定理 29.3 (Morse不等式)
**Theorem 29.3 (Morse Inequalities)**

设M紧，f是Morse函数，c_k是指标k的临界点数。则:
```
c_k ≥ b_k = rank H_k(M)  (弱不等式)
Σ_{i=0}^k (-1)^{k-i} c_i ≥ Σ_{i=0}^k (-1)^{k-i} b_i  (强不等式)
Σ (-1)^k c_k = χ(M)  (等式)
```

**Morse引理**: 临界点附近，f ≈ f(p) - x₁² - ... - x_λ² + x_{λ+1}² + ... + x_n²

---

### 4.4 配边理论 [57Rxx]

#### 定义 XXIX.4.1 (配边)
**Definition XXIX.4.1 (Cobordism)**

两个n维闭流形M₀, M₁是**配边的** 如果存在(n+1)维紧流形W使得∂W = M₀ ⊔ M₁。

**配边群**: Ω_n = {n维闭流形}/配边

**结构**:
- Ω_0 = ℤ
- Ω_1 = Ω_2 = Ω_3 = 0
- Ω_4 = ℤ (示性数)

**Thom定理**: Ω_* ⊗ ℤ/2 是多项式代数ℤ/2[x_{2i}: i ≠ 2^j-1]

---

### 4.5 纽结理论 [57Mxx]

#### 定义 XXIX.5.1 (纽结与链环)
**Definition XXIX.5.1 (Knots and Links)**

**纽结**: S¹在S³中的光滑嵌入 (定向、逐点不同)

**链环**: 多个S¹的不交并的嵌入

**等价**: 存在S³到自身的同痕将一个变到另一个

**不变量**:
1. **环绕数** (linking number)
2. **Alexander多项式**
3. **Jones多项式** (V. Jones, 1984)
4. **HOMFLY多项式**
5. **纽结群** π₁(S³\K)

**应用**: DNA拓扑、量子场论

---

## 5. 整体分析 (58-XX)

### 5.1 流形上的分析 [58Axx]

#### 定义 XXX.1.1 (de Rham上同调)
**Definition XXX.1.1 (de Rham Cohomology)**

**闭形式**: dω = 0

**恰当形式**: ω = dη

**de Rham上同调**: H^k_{dR}(M) = {闭k-形式}/{恰当k-形式}

**例子**:
- H^0_{dR}(M) = ℝ (M连通)
- H^1_{dR}(S¹) = ℝ (由dθ生成)
- H^k_{dR}(S^n) = ℝ (k=0,n), 0 (其他)

#### 定理 30.1 (de Rham定理)
**Theorem 30.1 (de Rham's Theorem)**

```
H^k_{dR}(M) ≅ H^k(M;ℝ)
```

*意义*: 微分形式与拓扑的桥梁

*证明*. 层上同调 + 奇异上同调。 □

---

### 5.2 Hodge理论 [58Axx]

#### 定义 XXX.2.1 (Laplace算子)
**Definition XXX.2.1 (Laplace Operator)**

在黎曼流形(M,g)上，**Laplace-Beltrami算子**:
```
Δ = dδ + δd: Ω^k(M) → Ω^k(M)
```
其中δ = d* (外微分的伴随)

**调和形式**: Δω = 0

#### 定理 30.2 (Hodge分解定理)
**Theorem 30.2 (Hodge Decomposition Theorem)**

在紧定向黎曼流形M上:
```
Ω^k(M) = Im(d) ⊕ Harm^k(M) ⊕ Im(δ)
```
其中Harm^k(M) = Ker(Δ)是调和k-形式空间。

**推论** (Hodge定理):
```
H^k_{dR}(M) ≅ Harm^k(M)
```

*意义*: 上同调有代表调和形式(最小范数)

---

### 5.3 Atiyah-Singer指标定理 [58Axx]

#### 定理 30.3 (Atiyah-Singer指标定理)
**Theorem 30.3 (Atiyah-Singer Index Theorem)**

对紧流形M上的椭圆算子D:
```
ind(D) = dim Ker(D) - dim Coker(D) = ∫_M ch(σ(D))Td(TM) / e(TM)
```

其中:
- ch: 陈特征
- Td: Todd类
- e: Euler类

**特例**:
1. **Gauss-Bonnet**: ind(d+δ) = χ(M)
2. **Hirzebruch-Riemann-Roch**: ind(∂̄) = ∫ ch(E)Td(TM) (复流形)
3. **符号差定理**: ind(符号差算子) = Sign(M)

*意义*: 分析不变量 = 拓扑不变量

---

## Lean4 代码示例

本节提供与第四卷（几何与拓扑）内容相关的Lean4代码示例。

### 1. 流形与切丛

```lean4
import Mathlib.Geometry.Manifold.Basic
import Mathlib.Geometry.Manifold.TangentBundle

-- 流形的定义通过ChartedSpace类型类
-- 切空间在Lean4中通过结构定义

-- 光滑函数
example (M : Type*) [TopologicalSpace M] [ChartedSpace (EuclideanSpace ℝ n) M] 
    [SmoothManifoldWithCorners (EuclideanSpace ℝ n) M] :
    SmoothMap M (EuclideanSpace ℝ n) := sorry

-- 切向量作为导数的等价类
-- 在Mathlib中，切向量通过等价类定义
```

### 2. 微分形式

```lean4
import Mathlib.Geometry.Manifold.Forms.Basic
import Mathlib.Geometry.Manifold.Forms.Derivative

-- 外代数
example (V : Type*) [AddCommGroup V] [Module ℝ V] : 
    ExteriorAlgebra ℝ V = (TensorAlgebra ℝ V).Quotient := rfl

-- k-形式的定义
-- 在Mathlib中，微分形式通过Map
-- 例：ω : SmoothMap M (AlternatingMap ℝ V)

-- 外积
example (V : Type*) [AddCommGroup V] [Module ℝ V] [FiniteDimensional ℝ V]
    (ω₁ : AlternatingMap ℝ V ℝ (Fin k)) (ω₂ : AlternatingMap ℝ V ℝ (Fin l)) :
    AlternatingMap ℝ V ℝ (Fin (k + l)) := sorry

-- 外微分
-- d : Ω^k(M) → Ω^{k+1}(M)
-- d² = 0
example (M : Type*) [SmoothManifoldWithCorners (EuclideanSpace ℝ n) M]
    (ω : SmoothMap M (AlternatingMap ℝ (TangentSpace ℝ M) ℝ (Fin k))) :
    SmoothMap M (AlternatingMap ℝ (TangentSpace ℝ M) ℝ (Fin (k + 1))) := sorry
```

### 3. 黎曼几何基础

```lean4
import Mathlib.Geometry.Riemannian.Basic
import Mathlib.Geometry.Riemannian.Curvature

-- 黎曼度量
-- Riemannian structure是光滑的对称正定双线性形式

-- 联络（Levi-Civita联络）
-- 无挠且度量相容的唯一联络

-- 曲率张量
-- R(X,Y)Z = ∇_X ∇_Y Z - ∇_Y ∇_X Z - ∇_{[X,Y]} Z

-- 截面曲率
example (M : Type*) [SmoothManifoldWithCorners (EuclideanSpace ℝ n) M]
    [Riemannian M] (p : M) (v w : TangentSpace ℝ p) (hv : v ≠ 0) (hw : w ≠ 0) :
    ℝ := sectionalCurvature p v w

-- Ricci曲率
example (M : Type*) [SmoothManifoldWithCorners (EuclideanSpace ℝ n) M]
    [Riemannian M] (p : M) : TangentSpace ℝ p →L[ℝ] ℝ := ricciCurvature p

-- 数量曲率
example (M : Type*) [SmoothManifoldWithCorners (EuclideanSpace ℝ n) M]
    [Riemannian M] (p : M) : ℝ := scalarCurvature p
```

### 4. 基本群

```lean4
import Mathlib.Topology.FundamentalGroup
import Mathlib.Topology.CoveringSpaces

-- 基本群的定义
-- π₁(X, x₀) = 道路类群 (道路的同伦类，乘法=连接)

-- 道路
def Path (X : Type*) [TopologicalSpace X] (x₀ x₁ : X) := 
  {f : ℝ → X // Continuous f ∧ f 0 = x₀ ∧ f 1 = x₁}

-- 道路的连接
def Path.concat {X : Type*} [TopologicalSpace X] {x₀ x₁ x₂ : X} 
    (p₁ : Path X x₀ x₁) (p₂ : Path X x₁ x₂) : Path X x₀ x₂ := sorry

-- 同伦
example (X : Type*) [TopologicalSpace X] {x₀ x₁ : X} 
    (p₁ p₂ : Path X x₀ x₁) : Prop := 
  ∃ H : ℝ × ℝ → X, Continuous H ∧ 
    (∀ t, H 0 t = p₁.val t) ∧ (∀ t, H 1 t = p₂.val t)

-- 群结构
example (X : Type*) [TopologicalSpace X] [PathConnectedSpace X] (x₀ : X) :
    Group (Quotient (Path.homotopic.setoid X x₀ x₀)) := by
  infer_instance

-- S¹的基本群是ℤ
example : π₁ (Circle) 1 ≃* ℤ := by
  sorry  -- 需要技术性证明
```

### 5. 同调与上同调

```lean4
import Mathlib.Topology.Homology
import Mathlib.Topology.Cohomology

-- 单纯复形的同调
-- 在Lean4中，通过链复形定义

-- 链复形
structure ChainComplex (C : Type*) [Category C] [Preadditive C] where
  chain : ℕ → C
  d : ∀ n, chain (n + 1) ⟶ chain n
  sq_zero : ∀ n, d n ≫ d (n + 1) = 0 := by obviously

-- 同调群
def homology (C : ChainComplex Ab) (n : ℕ) : Ab := 
  (C.d n).ker ⧸ (C.d (n + 1)).range

-- Euler示性数
example (X : Type*) [TopologicalSpace X] [CompactSpace X] 
    [FiniteHomologicalDimension X] :
    ℤ := ∑ n, (homologicalDimension X n : ℤ) * (-1 : ℤ) ^ n
```

### 6. 覆盖空间

```lean4
import Mathlib.Topology.CoveringSpaces.Basic

-- 覆盖映射
structure CoveringMap (E X : Type*) [TopologicalSpace E] [TopologicalSpace X] where
  toFun : E → X
  continuous_toFun : Continuous toFun := by obviously
  isCovering : ∀ x : X, ∃ U : Set X, IsOpen U ∧ x ∈ U ∧ 
    ∃ ι : Type*, ∃ (F : ι → Set E), 
    (∀ i, IsHomeomorphOn (toFun.restrict F i)) ∧ 
    (⋃ i, F i) = toFun ⁻¹' U

-- 万有覆盖
example (X : Type*) [TopologicalSpace X] [PathConnectedSpace X] 
    [LocallyPathConnectedSpace X] [SemilocallySimplyConnectedSpace X] :
    ∃ (X̃ : Type*) [TopologicalSpace X̃], Nonempty (CoveringMap X̃ X) ∧ 
    SimplyConnectedSpace X̃ := by
  sorry

-- 覆盖空间的分类
-- π₁(X, x₀)的作用于纤维上的单可迁作用
```

### 7. 流形嵌入与浸入

```lean4
import Mathlib.Geometry.Manifold.Embedding

-- 浸入
def IsImmersion (M N : Type*) [SmoothManifold M] [SmoothManifold N]
    (f : M → N) : Prop := 
  ∀ p : M, Injective (df p)  -- df是切映射

-- 嵌入
def IsEmbedding (M N : Type*) [SmoothManifold M] [SmoothManifold N]
    (f : M → N) : Prop := 
  IsImmersion M N f ∧ Embedding f

-- Whitney嵌入定理
example (M : Type*) [SmoothManifold M] [CompactSpace M] 
    [FiniteDimensional ℝ M] (hdim : dim ℝ M = n) :
    ∃ (f : M → EuclideanSpace ℝ (2 * n + 1)), IsEmbedding M _ f := by
  sorry
```

### 8. 向量丛

```lean4
import Mathlib.Geometry.VectorBundle

-- 向量丛的定义
structure VectorBundle (B E : Type*) [TopologicalSpace B] [TopologicalSpace E]
    (R : Type*) [CommRing R] [AddCommGroup R] [Module R R] where
  proj : E → B
  continuous_proj : Continuous proj := by obviously
  fiber : B → Type*
  fiberModule : ∀ b, Module R (fiber b)
  trivialization : ∀ b₀ : B, ∃ U : Set B, IsOpen U ∧ b₀ ∈ U ∧
    ∃ e : LocalHomeomorph (Σ b : B, fiber b) E,
    e.toFun ∘ (fun b => ⟨b, (fiber b)⟩) = id

-- 切丛
example (M : Type*) [SmoothManifold M] : VectorBundle M (TangentBundle M) ℝ := by
  sorry

-- 示性类
-- 在Lean4中，Stiefel-Whitney类和陈类需要更多代数拓扑基础
```

---

## 参考文献

### 微分几何
1. do Carmo, M.P., *Riemannian Geometry*, Birkhäuser, 1992
2. Lee, J.M., *Introduction to Smooth Manifolds*, 2nd ed., Springer, 2012
3. Lee, J.M., *Riemannian Manifolds: An Introduction to Curvature*, Springer, 1997

### 代数拓扑
4. Hatcher, A., *Algebraic Topology*, Cambridge, 2002
5. May, J.P., *A Concise Course in Algebraic Topology*, Chicago, 1999
6. Spanier, E.H., *Algebraic Topology*, Springer, 1981

### 微分拓扑
7. Guillemin, V., Pollack, A., *Differential Topology*, Prentice Hall, 1974
8. Milnor, J., *Morse Theory*, Princeton, 1963
9. Hirsch, M.W., *Differential Topology*, Springer, 1976

### 整体分析
10. Warner, F.W., *Foundations of Differentiable Manifolds and Lie Groups*, Springer, 1983
11. Wells, R.O., *Differential Analysis on Complex Manifolds*, 3rd ed., Springer, 2008

### 特殊主题
12. Milnor, J., Stasheff, J., *Characteristic Classes*, Princeton, 1974
13. Lawson, H.B., Michelsohn, M.L., *Spin Geometry*, Princeton, 1989
14. Berline, N., Getzler, E., Vergne, M., *Heat Kernels and Dirac Operators*, Springer, 2004

---

**注**: 本文档是第四卷，涵盖了几何与拓扑的核心内容。

---

*本卷完成日期: 2025-03-26*  
*下一卷预告: 概率与统计*
