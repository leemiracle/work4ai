# 法学 · Neurosymbolic 法律 AI 理论

> **博士级**：法律 AI 的 Neurosymbolic 方法学。

## 一、为什么法律适合 Neurosymbolic

| 法律 | 神经 | 符号 |
|---|---|---|
| 条文 | LLM 理解 | 逻辑编码 |
| 判例 | 相似度检索 | 案例推理 |
| 推理 | LLM 生成 | 演绎 |

**互补** → Neurosymbolic 是法律 AI 的天然架构。

## 二、法律推理的形式化

### 2.1 经典：法律三段论

```
大前提：法律规定（"故意杀人的，处死刑"）
小前提：案件事实（"张三故意杀人"）
结论：判决（"处死刑"）
```

**形式**：$\forall x (P(x) \to Q(x))$, $P(a)$, $\therefore Q(a)$

### 2.2 现实：复杂法律推理

- **判例约束**（precedent binding）
- **解释**（法律解释）
- **抗辩**（defense）
- **平衡**（不同原则）

## 三、LLM + 符号融合

### 3.1 RAG（检索增强）

- LLM 生成回答 + 检索法律条文
- **Harvey / Lexis+ AI** 用
- 详见 [`讲透RAG`](../../../讲透RAG/)

### 3.2 知识图谱 + LLM

- 法律本体（OWL / RDF）
- 实体 + 关系抽取
- 推理 + LLM 解释

### 3.3 形式化验证

- LLM 生成候选答案
- **Lean / Coq** 验证逻辑

### 3.4 Probabilistic Logic

- **DeepProbLog**：神经 + 概率逻辑
- 适合法律不确定性

## 四、关键挑战

### 4.1 引用准确性

- LLM 容易**编造引用**
- **必须检索 + 验证**
- **RAG + verifier** 双重保险

### 4.2 多法系

- 普通法（case law）vs 大陆法（code law）
- 跨法系迁移
- **不同推理模式**

### 4.3 伦理 + 监管

- **GDPR 22 条**：拒绝纯算法决策
- **可解释性**强制
- **责任归属**

## 五、Harvey 等案例

### 5.1 Harvey 架构（推测）

```
用户问题
   ↓ GPT-4
理解 + 生成
   ↓ RAG over Lexis 数据库
检索法律
   ↓ Verifier
验证
   ↓ Output
答案 + 引用
```

### 5.2 商业模式

- B2B SaaS（顶级律所）
- 定制化（按律所知识库）
- **估值 $3B+**（2024）

## 六、博士级练习

1. 用 LangChain + GPT-4 实现简单法律 RAG
2. 评估 LLM 在 CAIL2018 的引用准确率
3. 设计 Neurosymbolic 法律推理系统

## 关键引用

- Ashley 2017 *Artificial Intelligence and Legal Analytics*
- Bench-Capon et al. 2012 *A History of AI and Law*
- Brass & Tielman, **Neurosymbolic AI for Law** (2024)
