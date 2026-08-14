# Harvard Math 55a · 习题集（线代部分，最高抽象度）

> **风格**：抽象证明题（55a 传统）。⚠️ 门槛极高，标注难度。

---

## 第 1 章 · 张量积 ★

### Q1.1（中等·张量积维数）
证明 $\dim(V\otimes W)=(\dim V)(\dim W)$。

<details><summary>解</summary>

设 $\{e_i\},\{f_j\}$ 分别为 $V,W$ 基。则 $\{e_i\otimes f_j\}$ 生成 $V\otimes W$（张量积的构造）。需证独立：若 $\sum c_{ij}e_i\otimes f_j=0$，取双线性映射 $B_{kl}(e_i,f_j)=\delta_{(i,j),(k,l)}$，由泛性质得 $\tilde B_{kl}(\sum c_{ij}e_i\otimes f_j)=c_{kl}=0$。故 $\{e_i\otimes f_j\}$ 是基，维数 $=(\dim V)(\dim W)$。
</details>

### Q1.2（开放·双线性化）★
证明张量积的泛性质：对任意双线性 $B:V\times W\to U$，存在唯一线性 $\tilde B:V\otimes W\to U$ 使 $B(v,w)=\tilde B(v\otimes w)$。

<details><summary>解（构造）</summary>

定义 $\tilde B(e_i\otimes f_j)=B(e_i,f_j)$，线性扩张到 $V\otimes W$。需验证良定义（与基选择无关）+ 唯一性（由 $e_i\otimes f_j$ 张成决定）。这就是"张量积线性化双线性"的核心。
</details>

---

## 第 2 章 · 外代数与行列式

### Q2.1（中等·行列式的抽象定义）
用外代数定义 $\det T$：$\bigwedge^n T$ 在 1 维空间 $\bigwedge^n V$ 上是标量乘法，定义为 $\det T$。证明这与 $\det(T)$ 的通常定义一致。

<details><summary>解</summary>

$\bigwedge^n V$ 是 1 维（由 $e_1\wedge\cdots\wedge e_n$ 张成）。$(\bigwedge^n T)(e_1\wedge\cdots\wedge e_n)=Te_1\wedge\cdots\wedge Te_n=(\det T)(e_1\wedge\cdots\wedge e_n)$。这个 $\det T$ 满足多重线性+交错+$\det I=1$，由行列式唯一性 = 通常 $\det$。
</details>

---

## 第 3 章 · 典型群 ★

### Q3.1（中等·正交群 = 等距）
证明 $T\in\mathrm{O}(V)$ ⟺ $T$ 保内积（$\langle Tu,Tv\rangle=\langle u,v\rangle$）。

<details><summary>解</summary>

(⟹) $\langle Tu,Tv\rangle=\langle u,T^*Tv\rangle=\langle u,v\rangle$（$T^*T=I$）。
(⟸) 保内积 ⟹ $\langle u,T^*Tv\rangle=\langle u,v\rangle$ ∀$u,v$ ⟹ $T^*T=I$ ⟹ $T\in\mathrm{O}(V)$。
</details>

### Q3.2（开放·SO(3) 旋转）★
证明 $\mathrm{SO}(3)$ 中每个元素是绕某轴的旋转（Euler 旋转定理）。

<details><summary>解（思路）</summary>

$R\in\mathrm{SO}(3)$，$\det R=1$。特征多项式是 3 次实系数 ⟹ 有实根 $\lambda_1$。$|\lambda_i|=1$（正交矩阵特征值模 1），$\prod\lambda_i=\det=1$。若 $\lambda_1=1$（必有，因复根成对且积为 1），则对应特征向量是旋转轴。$R$ 在该轴垂直平面是 $2\times2$ 旋转。故 $R=$ 绕轴旋转某角度。
</details>

---

## 第 4 章 · 谱定理（最一般）

### Q4.1（证明·正规算子）★
证明：$T$ 正规（$TT^*=T^*T$）⟺ $\|Tv\|=\|T^*v\|$ ∀$v$。

<details><summary>解</summary>

$\|Tv\|^2=\langle Tv,Tv\rangle=\langle T^*Tv,v\rangle$。$\|T^*v\|^2=\langle TT^*v,v\rangle$。
$\|Tv\|^2-\|T^*v\|^2=\langle(T^*T-TT^*)v,v\rangle$。
$T$ 正规 ⟺ $T^*T-TT^*=0$ ⟺ 左边 $=0$ ∀$v$ ⟺ $\|Tv\|=\|T^*v\|$。
（最后一步用：自伴算子 $S$，$\langle Sv,v\rangle=0$ ∀$v$ ⟹ $S=0$，由极化恒等式。）
</details>

---

## 综合大题

### Q-Final（等变网络数学·开放）★★
设计一个 $\mathrm{SO}(2)$-等变的线性层 $L:\mathbb{R}^2\to\mathbb{R}^2$（即 $L(R\mathbf{x})=RL(\mathbf{x})$ ∀$R\in\mathrm{SO}(2)$）。
(a) 证明 $L$ 必须是旋转-缩放 $L=rR_\theta$（$r\geq0$，$R_\theta\in\mathrm{SO}(2)$）。
(b) 这对应复数乘法 $L(z)=\alpha z$（$\alpha=re^{i\theta}$）。

<details><summary>解</summary>

(a) $\mathrm{SO}(2)$-等变 ⟺ $L$ 与所有旋转交换。$\mathrm{SO}(2)$ 的中心化子在 $\mathrm{End}(\mathbb{R}^2)$ 中 = $\mathrm{SO}(2)$ 的线性组合 = $\{aI+bJ:a,b\in\mathbb{R}\}$（$J=\begin{pmatrix}0&-1\\1&0\end{pmatrix}$，90° 旋转）。即 $L=\begin{pmatrix}a&-b\\b&a\end{pmatrix}$，这正是旋转-缩放 $rR_\theta$，$r=\sqrt{a^2+b^2}$。

(b) 把 $\mathbb{R}^2\cong\mathbb{C}$，$L$ 对应 $z\mapsto(a+ib)z=\alpha z$。复数乘法天然 $\mathrm{SO}(2)$-等变。

> **ML 关联**：等变神经网络用此约束——若数据有旋转对称性（图像/分子），等变层保证预测旋转不变，大幅减少参数。AlphaFold 的 SE(3)-等变层是其 3D 推广。
</details>
