# 01-概念横切轴（Timothy Gowers）

> "A mathematical object is what it does."——数学对象即其行为，而非其"本质"。

## 核心视角

✅ Gowers（菲尔兹奖）在 *Mathematics: A Very Short Introduction*（Oxford, 2002）中提出：理解数学定义不应只问"它是什么"，而应问"它做什么"。这是函数式本体论——对象由其与其他对象的关系/行为定义，而非由内在构造定义。

✅ Gowers 提出**定义类型学**（博客 *"Definitions"*, 2011），将数学定义分为四类：
- **abbreviation definitions**（缩写型）：纯为书写方便，如"素数"
- **property-picking definitions**（性质选取型）：挑出满足某性质的物体，如"无理数"
- **construction definitions**（构造型）：通过构造过程定义
- **calculation definitions**（计算型）：通过计算规则定义

⚠️ Gowers 的中心主张：每次遇到新定义，应当**意识到它是哪种类型**，这决定了你理解它的方式。构造型定义应追踪构造过程；性质选取型应收集满足/不满足的例子。

✅ 在 *"What is deep mathematics?"*（2008）中，Gowers 进一步提出：**深度**的本质是"让非常困难的东西看起来非常简单"——一旦找到正确观点（right way to think about it），复杂变平凡。浅证明可被自动化技巧生成，深证明要求 "think very hard about how to think correctly about your problem"。

## 作为学习透镜怎么用

学新概念时，不只问"它是什么"，而问一组 **Gowers 元问题**：

1. **这个定义是哪一类？**（缩写/性质/构造/计算）——决定理解策略
2. **它为解决什么问题而存在？**——定义不是凭空产生，追溯动机
3. **换一种定义方式会怎样？**——等价定义的差异暴露本质
4. **"它做什么"比"它是什么"更重要**——收集对象的行为而非构造

具体操作：在笔记的 §0 元数据区标注定义类型；在 §1 直觉层用"它做什么"造句解释。

## 适用数学概念举例

- **连续函数**（ε-δ构造型 vs 拓扑开集拉回型——等价定义暴露不同面貌）
- **群**（性质选取 vs 变换群构造——Gowers行为论的核心案例）
- **导数**（差商极限构造型 vs 最佳线性逼近行为型）
- **素数**（缩写型——但"为什么这个缩写有用"是有深意的问题）
- **积分**（Riemann构造型 vs Lebesgue构造型——不同构造解决不同问题）
- **范畴论中的 functor/monad**（"它做什么"远比"它是什么"重要）
- **拓扑空间的"开集"**（性质选取型——为什么选这些性质？）
- **测度**（构造型——Carathéodory扩展定理为什么这样构造？）

## 来源核实

- ✅ Timothy Gowers, *Mathematics: A Very Short Introduction*（Oxford University Press, 2002）
- ✅ Gowers's Weblog, *"What is deep mathematics?"*（2008）
- ✅ Gowers's Weblog, *"Definitions"*（2011）
- ✅ *The Princeton Companion to Mathematics*（Princeton, 2008, Gowers 编）
- ⚠️ 定义类型学名称为调研归纳的中文转译
