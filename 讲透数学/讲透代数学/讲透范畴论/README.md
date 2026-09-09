# 讲透范畴论 · 数学的接口层:函子、伴随与 Yoneda

> **定位句**:这支负责"结构与翻译的总体学问"——不问对象是什么,问对象之间怎么相互定义;范畴论是当代数学的接口协议,也是 Lean/mathlib 的架构层。
> GB/T 11021 三级「范畴论」| 家族:[讲透代数学](../README.md)

## 诞生
1945 Eilenberg & Mac Lane《General theory of natural equivalences》:同调论的不同构造给出同构的群,需要谈论"自然性"本身;术语"函子"取自 Carnap(逻辑学家的语言哲学借来)。1958 Grothendieck 把代数几何范畴化;1960s Lawvere(范畴论做逻辑);1980s-2020s ∞-范畴(Joyal/Lurie)完成下一次升维。

## 核心问题
**已解决**:Yoneda 引理(对象=其关系全体);伴随函子的存在性准则(Adjoint Functor Theorem);Abelian 范畴(同调代数的公理化,Grothendieck 1957);topos 理论(几何×逻辑)。
**未解决/活跃**:∞-范畴的"正确"基础(Quillen 模型/相对范畴/∞-cosmos 多套并行);导出代数几何的定型;Voevodsky 的 HoTT/一价性公理作为数学新基础(〔`../../讲透Lean4数学/`](../../讲透Lean4数学/) 的对岸)。

## 这支最美的一个事实
**Yoneda 引理**:$\mathrm{Nat}(\mathrm{Hom}(-,A),F)\cong F(A)$。"告诉我所有别人怎么看你的方式,我就知道你"——一个对象在范畴中的一切信息,编码在它发出的箭头里。证明三行,后果:表示=理解,万有性质=定义,从此数学的"定义"获得了统一的形状。

## 假设与依赖
本体论最省:对象+箭头+复合律,不问元素;局部小性(每个 hom 是集合)是 Hom 函子存在的底线。一切结构支(群/环/模/拓扑空间)都是它的实例层——范畴论是"层"的学问,不是替代"层"的学问。

## 教材锚
Mac Lane《Categories for the Working Mathematician》(原典)/ Riehl《Category Theory in Context》(现代最佳入门,免费)/ Leinster《Basic Category Theory》(薄);∞:Lurie《Higher Topos Theory》/ Cisinski。

## 章目宪法(五问→五章,待产记账)

| # | 章 | 要点 | 状态 |
|---|----|------|------|
| 00 | 00-体系结构.md | 范畴/函子→Yoneda→伴随→(Abelian/topos/∞)三级跳 | 📝 |
| 01 | 01-近五年创新.md | ∞-范畴语言化;几何 Langlands 的证明语言(检索校准) | 📝 |
| 02 | 02-语言特征.md | 「箭头优先」;泛性质=唯一的定义方式 | 📝 |
| 03 | 03-可构造与结构.md | 表示=对象;伴随=结构的"最优解" | 📝 |
| 04 | 04-范畴论转代码.md | mathlib 的 category 层;Haskell/函数式类型类 | 📝 |

## 关系
横切全家:给每个支提供接口语言 | 逻辑=`../../讲透证明/`+`../../讲透集合/`(topos/HoTT)| 计算机科学=类型论/函数式 | 家族 [01 章](../01-近五年创新.md)五部曲的语法层。
