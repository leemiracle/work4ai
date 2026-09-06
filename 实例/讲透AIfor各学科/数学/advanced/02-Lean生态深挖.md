# 数学 · Lean 生态深挖

> **博士级**：Lean 4 的生态 + 工具 + 工作流。

## 一、Lean 4 是什么

**Leonardo de Moura**（2013+）创建的定理证明器。
- **Dependent Type Theory** 基础
- **程序 = 证明**（Curry-Howard）
- 同时是**编程语言** + **证明助手**

## 二、生态组件

### 2.1 mathlib（数学库）

- **100 万+ 行**已形式化
- 覆盖：分析 / 代数 / 拓扑 / 几何 / 数论 /...
- **社区驱动**（3000+ 贡献者）

**关键定理**：
- **Fermat 大定理**（2023 完整形式化）
- **Perfectoid Spaces**（Scholze）
- **Cantor 定理** / **Gödel 不完备** / **4 色定理**

### 2.2 工具

- **Lean 4**：核心语言
- **VS Code 插件**：开发环境
- **Lean Copilot**：LLM 辅助（2023）
- **mathport**：自动从 Lean 3 迁移

### 2.3 自动化

- **LeanDojo**（2023）：Python + RL 接口
- **Sledgehammer**：找已有引理
- **tactic suggestions**：LLM 建议

## 三、顶级数学家的采用

### 3.1 Terence Tao（UCLA）

- Fields Medal
- 2023 开始用 Lean
- 公开博客讨论

### 3.2 Peter Scholze（Bonn）

- Fields Medal
- **Liquid Tensor Experiment**（2021）形式化自己工作
- 推动数学形式化

### 3.3 Kevin Buzzard（Imperial）

- 代数几何学家
- Lean 教育推广者
- **"Xena Project"**

### 3.4 Jeremy Avigad（CMU）

- 形式化哲学
- 数学自动推理

## 四、关键工作流

### 4.1 传统写数学

```
1. 想 idea
2. 写 paper（LaTeX）
3. 投稿 + 同行评议
4. 出版
5. 可能发现错（5 年后）
```

### 4.2 Lean 工作流

```
1. 想 idea
2. 写 paper + Lean appendix
3. Lean 验证（100% 可靠）
4. 投稿（reviewer 信 Lean）
5. 永久正确
```

## 五、关键案例

### 5.1 Fermat 大定理

- 358 年历史
- Wiles 1994 证明（~100 页）
- 2023 Lean 形式化（mathlib）

### 5.2 Polynomial Freiman-Ruzsa Conjecture

- Tao 2023 解
- Lean 形式化（几周）

### 5.3 Liquid Tensor Experiment

- Scholze 的 perfectoid 工作
- 2021 Lean 形式化（社区协作）

## 六、AI 增强 Lean

### 6.1 Lean Copilot（2023）

- LLM 建议下一个 tactic
- Hugging Face 风格
- 在 VS Code 集成

### 6.2 LeanDojo（2023）

- Python API 操作 Lean
- Reinforcement Learning 环境
- **miniF2F benchmark**

### 6.3 AlphaProof（2024）

- DeepMind
- IMO 银牌
- Lean 验证

## 七、学习资源

### 7.1 入门

- **The Natural Number Game**（在线游戏）
- **Theorem Proving in Lean 4**（在线书）
- **Mathematics in Lean**（数学家向）

### 7.2 社区

- **Lean Zulip**（主要讨论）
- **Mathlib4 文档**
- **Terence Tao blog**

## 八、挑战

### 8.1 学习曲线陡

- 需要数学 + 编程
- 培训成本高

### 8.2 形式化成本

- 复杂证明形式化费时
- 但**一次性投入**，永久受益

### 8.3 文化障碍

- 老一辈数学家不习惯
- 同行评议系统的变化

## 九、博士级练习

1. 完成 **Natural Number Game**
2. 在 mathlib 找一个简单定理形式化
3. 用 Lean Copilot 辅助证明

## 十、关键引用

- de Moura 2015 Lean *ITP*
- mathlib 2020 *CICM*
- Yang 2023 LeanDojo *NeurIPS*
- Han 2023 Lean Copilot
