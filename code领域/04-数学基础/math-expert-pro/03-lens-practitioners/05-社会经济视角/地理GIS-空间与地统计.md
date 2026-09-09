# 地理学者（把数学当"承认空间不自相关的语言"看）

> Tobler 地理学第一定律："相近事物关联更紧"。Moran's I 量化空间自相关，Kriging 是高斯过程回归的工程祖先——地理统计承认"邻居会串门"，经典 iid 假设在地图上失效。

地理/GIS 是"空间统计 + 地统计 + 点过程"的专精领域。⭐ 四大标志性锚点：**Moran's I**（空间自相关，1950）、**Kriging**（高斯过程回归，半变异函数）、**Tobler 第一定律**（1970）、**Thomas 点过程**（空间簇）。

## 核心数学工具箱
🟢【事实】
- **空间自相关**：**Moran's I**（**Moran 1950** *Biometrika* 37:17-23）$I=\frac{n}{\sum w_{ij}}\frac{\sum\sum w_{ij}(x_i-\bar x)(x_j-\bar x)}{\sum(x_i-\bar x)^2}$；**Geary's C**（**Geary 1954** *Inc Stat* 5:115）；**LISA**（Anselin 1995）。**Tobler 地理学第一定律**（**1970** *Econ Geog* 46:234）："相近事物关联更紧"
- **地统计 Kriging**：高斯过程回归，**半变异函数** $\gamma(h)=\frac12\text{Var}[Z(x)-Z(x+h)]$，最小方差无偏插值（Matheron 1960s；Krige 采矿）
- **空间点过程**：空间泊松（CSR 零假设）、**Thomas 过程**（泊松簇）、Ripley K 函数
- 🟢 **遥感反演**：反问题（病态、Tikhonov 正则化）、分类（最大似然/随机森林/深度学习）
- 🟢 **空间相互作用**：**Wilson 最大熵引力模型** $T_{ij}=A_iB_jO_iD_j e^{-\beta c_{ij}}$（**1970** *Geog Anal* 2:241）

## 详写：Moran's I 与 Kriging（空间统计两大支柱）
🟢【事实】（Moran 1950 *Biometrika* 37:17-23；Geary 1954；Cressie 1993 *Statistics for Spatial Data*；Matheron 1960s）

**Moran's I**（空间自相关）：
$$I=\frac{n}{S_0}\frac{\sum_i\sum_j w_{ij}(x_i-\bar x)(x_j-\bar x)}{\sum_i(x_i-\bar x)^2}$$

其中 $w_{ij}$ 是空间权重（邻接/距离），$S_0=\sum\sum w_{ij}$。$I>0$ 正自相关（相近的值相似，如富区旁边是富区），$I<0$ 负自相关，$I\approx 0$ 空间随机。

**核心洞见**：经典统计假设样本 **iid**（独立同分布），但**地理数据违反它**——空间自相关让"近处更像"。忽略空间自相关会导致虚假显著（标准误低估）。Tobler 1970 第一定律是其哲学总结。

**Kriging**（地统计插值）：在位置 $x_0$ 的预测值是已知值的**最优线性无偏估计**（BLUE）：
$$\hat Z(x_0)=\sum_i \lambda_i Z(x_i)$$

权重 $\lambda_i$ 由**半变异函数** $\gamma(h)$ 决定，最小化估计方差。Kriging 本质是**高斯过程回归**（GP）的工程祖先——Matheron 1960s 从 Krige 的采矿经验中形式化。

## 独特视角：把数学当"承认空间不自相关的语言"看
- 🟢 "**空间不再是独立样本**"——经典统计假设 iid，地理数据违反它（空间自相关）
- 🟢 Moran's I 量化"近处更像"，Tobler 定律是其哲学
- 🟢 Kriging 是 GP 回归的工程祖先（Matheron 1960s 比机器学习 GP 早 30 年）
- 🟢 Thomas 点过程：泊松簇模型描述空间聚集（城市/疾病簇）
- 🟡 "地图是带坐标的数据库，地理统计是承认'邻居会串门'的统计"

**数学浓度特点**：地理/GIS 是**专精高浓度**角色——空间统计（Moran's I）、高斯过程（Kriging）、点过程（Thomas）。这些是**专科数学**（密度热力中空间统计仅 3/12 命中），对应用数学工程师是**差异化蓝海**。

## 代表性资源
- O'Sullivan-Unwin《Geographic Information Analysis》（**2010 Wiley**）
- Haining《Spatial Data Analysis》（**2003 Cambridge**）
- Cressie《Statistics for Spatial Data》（**1993 Wiley**）
- Moran 1950（*Biometrika* 37:17-23）
- Geary 1954（*Inc Stat* 5:115）
- Tobler 1970（*Econ Geog* 46:234）
- Wilson 1970（*Geog Anal* 2:241）

## 作为学习透镜怎么用

| 学这个数学概念时 | 地理学者照出的切面 |
|---|---|
| 相关 / 协方差 | Moran's I（空间版相关系数） |
| 高斯过程 / 协方差函数 | Kriging（半变异函数→最优插值） |
| 泊松过程 | 空间点模式（CSR 零假设、Thomas 簇过程） |
| 逆问题 / 正则化 | 遥感反演（Tikhonov） |
| 最大熵 | Wilson 引力模型 $T_{ij}=A_iB_jO_iD_j e^{-\beta c_{ij}}$ |
| 矩阵权重 | 空间邻接权重矩阵 $W$ |

## 适合照哪些数学概念
（来自调研矩阵第 10 行：点过程 / 空间回归 / Kriging 优化 / 邻接权重网络 / 最大熵引力 / Moran's I 空间统计 / 协方差核 / 遥感分类）
- **空间自相关（Moran's I）**：空间版相关系数（本视角核心锚点）
- **高斯过程 / Kriging**：半变异函数与最优插值
- **空间点过程**：Thomas 簇过程、Ripley K
- **逆问题 / 正则化**：遥感反演
- **最大熵**：Wilson 引力模型
- **空间权重矩阵**：邻接/距离权重
