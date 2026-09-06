# Harvard Math 154 — Number Theory

> **学校**：Harvard
> **一手来源**：Harvard Undergraduate Brochure 2025-2026

## 课程信息
- **编号**：Math 154
- **先修**：Math 122（推荐）
- **教材**：Niven, Zuckerman, Montgomery, *An Introduction to the Theory of Numbers*
- **特色**：经典解析数论入门

## 教学大纲
1. **Divisibility & primes**
2. **Modular arithmetic**
3. **Chinese remainder theorem**
4. **Quadratic reciprocity** ★
5. **Continued fractions**
6. **Diophantine equations**
7. **Cryptographic applications**（RSA 入门）

## 与 ML 的关联
- **直接关联少**（除非做密码学或量子计算）
- **价值**：数学成熟度
- **学完本课后**：理解 RSA / Diffie-Hellman

## 参考资源
- Niven-Zuckerman-Montgomery, *An Introduction to the Theory of Numbers* (5th ed)
- 替代：Hardy & Wright, *An Introduction to the Theory of Numbers*

📌 **下一步**：→ 进入 [Stanford 数学](../../stanford-math-courses/)

---

## 📍 在数学全景中的位置

- **前置**：基础证明能力 + [Berkeley 113 代数](../../berkeley-math-courses/math113_abstract_algebra/)（群/环结构）
- **本课**：素数 → 同余 → CRT → RSA → 椭圆曲线 → 解析数论入门
- **交叉**：密码学/安全工程 + 概率论（素数定理）

## 🔬 理论联系实际
1. **RSA = Euler 定理的应用**：$m^{ed} \equiv m \pmod{n}$，公钥加密的基石
2. **椭圆曲线密码（ECC）**：256-bit ECC ≈ 3072-bit RSA → Bitcoin/ETH 签名
3. **CRT → 联邦学习**：大模数运算拆成并行小模数 → 隐私计算
4. **素数定理 → Neural Scaling Laws**：$x/\ln x$ 的标度律思维

## 🆕 2024-2026 最新研究
| 子主题 | 进展 | 参考 |
|---|---|---|
| 全同态加密 (FHE) | 基于格的密码 → 隐私保护 ML | ⚠️ 2024 |
| 后量子密码 | NIST 标准化格密码 (Kyber/Dilithium) | NIST 2024 ✅ |
| 数论算法 | 大数分解仍无多项式算法（经典计算）| 开放问题 |
