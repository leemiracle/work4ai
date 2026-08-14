# UT Austin M 381C — Real Analysis (Graduate)

> **学校**：UT Austin | **学期**：Fall (研究生)
> **一手来源**：[catalog.utexas.edu](https://catalog.utexas.edu/general-information/coursesatoz/m/) + [math.utexas.edu/information/graduate-students/preliminary-exams](https://math.utexas.edu/information/graduate-students/preliminary-exams)

## 课程信息
- **编号**：M 381C / CSEM 385R（互认）
- **先修**：M 365C/D 或同等本科实分析
- **教材**：**Folland, *Real Analysis: Modern Techniques and Their Applications*** ★；或 Rudin *Real & Complex*
- **特色**：**UT Austin Analysis Prelim 序列第一学期**——PhD 资格考基础

## 教学大纲
1. **Set theory & σ-algebras**
2. **Measures** ★
3. **Lebesgue measure & integral** ★
4. **Convergence theorems**（MCT, DCT, Fatou）
5. **$L^p$ spaces**
6. **Differentiation theory**
7. **Product measures, Fubini-Tonelli**
8. **Hausdorff measure 入门**

## 与 ML 的关联（**ML 理论核心**）
- 测度论 = 概率论严格基础
- 学完后：能读所有 ML 理论论文

## 参考资源
- Folland, *Real Analysis* (2nd, Wiley)
- Rudin, *Real and Complex Analysis* (3rd)
- MIT 对照：[MIT 18.125](../../mit-math-courses/)

## 📍 在数学全景中的位置

```
前置                         本课                         后续
───────────────────────────────────────────────────────────────
M 365C (Rudin)        →   UT Austin M 381C       →   M 382C 泛函分析
(度量空间)                  (测度论+Lebesgue)           M 385C 概率论
```

| 阶梯 | 课程 | 角色 |
|---|---|---|
| 本科 | M 365C | Rudin 度量空间 |
| **研究生 ★** | **M 381C** | **测度论 + Lebesgue + $L^p$ + 收敛模式** |
| 高阶 | M 382C | 泛函分析 |

## 🔬 理论联系实际
1. **DCT → SGD**: mini-batch 梯度 → 全梯度的换序合法性 ★★★
2. **$L^p$ 空间 → RKHS**: Hilbert 空间 = 核方法的基础
3. **4 种收敛 → 概率论**: $L^p \Rightarrow$ 依概率 $\Rightarrow$ 依分布; a.s. $\Rightarrow$ 依概率 ★★★
4. **Radon-Nikodym → 变分推断**: $\text{KL}(q\|p) = \int \log(dq/dp) \, dp$
5. **压缩映射 → 优化收敛**: $\eta < 2/L \Rightarrow$ SGD 线性收敛

## 🆕 2024-2026 最新研究
- **Score-based Diffusion**: Radon-Nikodym 导数 = score function ⚠️
- **Wasserstein GAN**: 最优传输 = 测度空间上的优化 ⚠️
- **NTK 理论**: $L^2$ 空间上的积分算子 ⚠️
- **变分推断**: KL 散度的测度论基础 ⚠️

---

📌 **下一步**：→ [M 383C Methods of Applied Mathematics](../m383c_applied_mathematics/)
