# 00 · AI for Mathematics 是什么

> **第一性问题**：数学是**所有形式科学的基础**——证明是逻辑的最高形式。AI 能"做数学"吗？
>
> **2024 突破**：**AlphaProof + AlphaGeometry 2**（DeepMind）在 IMO 拿**银牌**——这是机器做数学的"AlphaGo 时刻"。配合 Lean / Coq 等形式化证明助手，AI 数学正在快速演进。
>
> 配套：[`讲透AI应用全景/02-AI4Math`](../../讲透AI应用全景/02-AI4Math.md)（综述）+ [`讲透符号主义`](../../讲透符号主义/)（Neurosymbolic）+ [`讲透因果推断`](../../讲透因果推断/)

---

## 一、数学为什么需要 AI

### 1.1 证明复杂度爆炸

- **Fermat 大定理**（358 年）：Wiles 1994 证明 ~100 页
- **分类有限单群**：1.5 万页
- **开普勒猜想**：Hales 1998，300 页 + 计算验证
- **Lean 数学库**：100 万+ 行已形式化

**人验证不了**——必须机器。

### 1.2 猜想生成

- 数学家靠**直觉**猜新定理
- AI 能扫描**百万组合**找规律
- **Erdős** 的"上帝之书"——AI 能找？

### 1.3 计算数学

- 高维积分、组合优化、特殊函数
- AI 加速 + 新算法

---

## 二、AI 在数学的五大应用

### 2.1 自动定理证明（ATP）

**经典方法**：分辨率 / 表决议（Coq / Isabelle / Lean / Vampire）
**问题**：组合爆炸——人能想的 AI 找不到。

**AI 增强**：
- **hammer 工具**（Sledgehammer / HOL Hammer）：找已有引理
- **GPT-f / AlphaProof**：神经网络引导搜索
- **Lean 的 mathport**：自动形式化

### 2.2 形式化数学（Formalization）

**Lean 数学库**（2020+）：
- 100 万+ 行已形式化
- **Fermat 大定理**已形式化（2023）
- **Perfectoid Space**（Scholze Fields Medal 工作）已形式化
- 数学教育的未来

**AI 加速形式化**：
- **Lean Copilot**（2023）：自动补全 + 解释
- **Autoformalization**：自然语言 → Lean
- **DeepMind AlphaProof**：在 Lean 中验证

### 2.3 猜想生成

**代表**：
- **Ramanujan Machine**（2020 *Nature*）：自动找连分数恒等式
- **FunSearch**（DeepMind 2023 *Nature*）：LLM + 进化，**找新组合学下界**
- **AI 发现新矩阵乘法算法**（AlphaTensor 2022）

**意义**：AI 不只是证明——**生成新数学**。

### 2.4 计算数学加速

- **AlphaTensor**：矩阵乘法 $O(n^{2.37})$ → 找到新常数
- **AlphaDev**：排序算法新纪录
- **AI 解微分方程**（Neural Operators）

### 2.5 数学教育 + LLM

- **GPT-4 / Claude** 解数学题（GSM8K / MATH benchmark）
- 个性化辅导
- **争议**：LLM 真理解还是模式匹配？（[`讲透基础模型/advanced/02 涌现`](../../讲透基础模型/advanced/02-涌现的争论.md)）

---

## 三、数学专属的方法学

### 3.1 Lean / Coq / Isabelle

**Lean 4**（Leonardo de Moura, 2013+）：
- 主流形式化数学语言
- **Terence Tao** 等顶级数学家用
- 2023 Lean 社区爆发

### 3.2 LLM + 符号 = Neurosymbolic

**AlphaProof 架构**（2024）：
```
1. 自然语言题目
   ↓ LLM (Gemini)
2. 翻译为 Lean 形式化
   ↓ Lean 求解器
3. 搜索证明（RL 引导）
   ↓ Lean 验证
4. 通过 = 真 proof
```

**意义**：**神经的直觉 + 符号的严谨**——AI 数学的新范式。

详见 [`讲透符号主义`](../../讲透符号主义/) § Neurosymbolic。

### 3.3 RL 搜索

- 证明 = 巨大的搜索树
- **AlphaZero 风格**：自我对弈
- **强化学习** 引导 Lean 求解器

### 3.4 数据稀缺 + 合成

- 顶级数学证明稀缺
- **自动生成 + LLM 蒸馏**
- **Lean Dojo** / **miniF2F** benchmark

---

## 四、当前前沿（2024-2026）

### 4.1 AlphaProof（DeepMind 2024）

- IMO 银牌（4/6 题）
- 包括**最难的几何题**（AlphaGeometry 2）
- **银牌接近金牌**——下一次？

### 4.2 Lean 4 生态爆发

- **数学库**：100 万+ 行
- **Terence Tao / Peter Scholze** 等用
- **Lean Copilot** / **LeanDojo**
- 数学论文 + Lean 附件成趋势

### 4.3 FunSearch（DeepMind 2023）

- LLM + 进化 = 找新数学
- **组合学下界**：超 20 年未改进
- **意义**：AI 不只证明，**发现**

### 4.4 数学 LLM

- **DeepSeek-Math / Qwen2.5-Math**（2024）：开源 SOTA
- **GPT-4 / Claude 3.5** 解奥数题
- **MATH / AIME benchmark**：分数飙升

### 4.5 自动形式化

- 自然语言 → Lean（**Autoformalization**）
- 解决"翻译瓶颈"
- 让非专家也能用 Lean

---

## 五、AI 改变了数学的什么

### 5.1 数学家的角色

- **经典**：手写证明 → 同行评议
- **AI 时代**：人想 idea → AI 形式化 → 验证

### 5.2 猜想验证加速

- "这个方向成立吗" → AI 快速测试
- 失败的尝试不再浪费月年

### 5.3 数学的可靠性

- Lean 验证 = **100% 可靠**（无人工错误）
- 关键定理（Fermat / Kepler）已重做
- **数学的标准提升**

### 5.4 数学的可访问性

- Lean Copilot 让普通人能形式化
- 教育改革（中学开始 Lean）
- **数学民主化**

---

## 六、开放问题

1. **AI 能解决 Hilbert 第 8 问题**（Riemann 假设）吗？何时？
2. **AI 发现的新数学算数学发现吗**？（[`讲透科学的现代性/03`](../../讲透科学的现代性/03-AI时代的科学哲学.md)）
3. **形式化数学的极限**？所有数学都能形式化吗？
4. **LLM 解题 vs AlphaProof 形式化**——哪个更接近"理解"？
5. **数学教育**怎么改革？Lean 进中学？

---

## 七、一句话总结

> 🎯 **四句话**：
> 1. **AlphaProof 2024 IMO 银牌**——AI 数学的 "AlphaGo 时刻"。
> 2. **五大应用**：ATP / 形式化（Lean）/ 猜想生成（FunSearch）/ 计算加速（AlphaTensor）/ 教育（LLM）。
> 3. **Neurosymbolic** = LLM 直觉 + Lean 符号严谨——AI 数学新范式。
> 4. **AI 改变数学**：可靠性提升 + 猜想验证加速 + 数学民主化——**Lean 4 生态爆发**。

---

📌 **下一步**

1. **读**：AlphaProof 2024 / FunSearch *Nature* 2023 / Lean mathlib。
2. **和 [`讲透AI应用全景/02-AI4Math`](../../讲透AI应用全景/02-AI4Math.md) + [`讲透符号主义`](../../讲透符号主义/) 对照**。
3. **思考开放问题**——AI 能解决 Riemann 假设吗？博士论文级。
4. **进入 [01 AlphaProof 深挖](./)**（待补）。
