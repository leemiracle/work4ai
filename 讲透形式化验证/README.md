# 讲透形式化验证（Formal Verification）

> 形式化验证是"**用数学证明保证软件永远不会有某类 bug**"的工程学科。从 seL4（2009，第一个全验证的 OS 内核）到 Atmosphere（SOSP 2025，20 秒验证全微内核），2024-2026 这门学科正从"11 人年证明 8.7K 行"进入"工程实用性竞赛"阶段。本系列从"为什么形式化"讲到 Lean4 SOTA，重点是把**形式化方法**和**神经符号 RL**（AlphaProof 式）连起来——这是 2025-2026 的前沿交叉。
>
> 配套：[`讲透神经符号`](../讲透神经符号/)（AlphaProof 闭环）+ [`讲透RL/04`](../讲透RL/04-RL与形式证明.md)（RL 证定理）+ [`讲透可解释性`](../讲透可解释性/)

> **系列宪法**：形式化验证是"**在可判定性边界的这一侧，为每类系统性质找到可计算的检查方法**"的工程学科。卷零讲为什么形式化（Lean4/神经符号视角），卷一攻 NP/coNP（把断言喂给求解器），卷二攻 PSPACE（让所有路径说话），卷三攻 P（概率定量），卷四参观引擎室（BDD/进程代数/自动机学习），收尾把 19 个工具归位到复杂度动物园的格子里——**每章末尾标注复杂度格，是全系列的横向主线**。
>
> **造桥**：03 SMT→卷零 Lean4 的 saturn/Duper 外部求解器；06 Dafny（全自动）↔ Lean4（交互）；12 BDD→10/11 PRISM/Storm 符号引擎底层；50 复杂度地图→`讲透优化`（NP 难度）、`讲透复杂系统`。

---

## 篇目

> 状态列：✅ 已完成 ｜ ○ 占位待写。

### 卷零 · 引论：为什么形式化（00-02，已完结）

| # | 标题 | 状态 | 核心锚点 | 仪器 |
|---|------|------|----------|------|
| **00** | [为什么形式化 + Lean4 SOTA](./00-为什么形式化+Lean4SOTA.md) | ✅ | seL4→Verus→Atmosphere 演化、Lean4 为何成新宠、`omega` 解不掉的边界、验证剧场陷阱 | — |
| **01** | [Lean4 作为 RL 奖励验证器：速度可行性](./01-Lean4作为RL奖励验证器.md) | ✅ | 实测 sub-second（14.9× 余量）、三个陷阱（Mathlib/复杂度/稀疏）、与 Alive2 对比 | Lean4 实测 |
| **02** | [从代码到规则：形式化的两层](./02-从代码到规则-形式化的两层.md) | ✅ | 形式化代码（seL4）vs 形式化因果规则（神经符号新范式） | — |

### 卷一 · NP/coNP：把断言喂给求解器（03-06）

| # | 标题 | 状态 | 核心锚点 | 仪器 |
|---|------|------|----------|------|
| 03 | [SMT 求解：DPLL(T) 与 Z3/cvc5](./03-SMT求解与Z3cvc5.md) | ✅ | DPLL→CDCL（**冲突子句 UIP 分析手推**）→ T-传播/E-传播；Nelson-Oppen 理论组合（LRA×EUF 共享变量）；SMT-LIB 语法；Z3 架构（简化器/核心/理论插件）；cvc5 的证明输出；应用：符号执行、SMT 竞赛格局。【NP/coNP】 | z3 + cvc5（均 pip）+ 手写 mini-CDCL |
| 04 | [有界模型检查：CBMC/ESBMC](./04-有界模型检查CBMC.md) | ✅ | 程序 k 步展开→SSA→断言取反→SMT，**反例=模型**；**3 行循环程序 k=2 展开编码手推**；k-induction 突破有界；CBMC 的 goto-IR/指针数组编码 vs ESBMC 的并发上下文界/多后端；不可判定问题的"有界"出路。【NP】 | cbmc.exe（Windows 官方包，可选）+ z3 复现编码 |
| 05 | [抽象解释与 CPAchecker](./05-抽象解释与CPAchecker.md) | ○ | 过近似：**符号函数的区间抽象跑 3 轮收敛不动点手推**；可靠≠完备（假报警）；CEGAR 闭环（反例→Craig 插值→谓词精化，**完整走一轮**）；CPA 可配置框架=域×迁移×合并；SV-COMP 赛场格局。【不可判定→可靠近似】 | 手写区间域解释器 + CPAchecker（Java，可选） |
| 06 | [Dafny：验证感知语言](./06-Dafny验证语言.md) | ○ | 前置/后置/循环不变式；**WP 三规则手推**（赋值/顺序/if）；Boogie 中间层→Z3；**BinarySearch 中点不变式**；终止性度量；全自动（Dafny）vs 交互（Lean4）——卷零之桥。【不可判定→义务分解到 NP】 | z3 复现 WP 检查 + Dafny（zip 需 .NET，可选） |

### 卷二 · PSPACE：让所有路径说话（07-09）

| # | 标题 | 状态 | 核心锚点 | 仪器 |
|---|------|------|----------|------|
| 07 | [LTL 与 Spin：显式状态的工艺](./07-LTL与Spin.md) | ✅ | LTL 语法（U/F/G 与五等价换算）；**F p 的 tableau 手推**；乘积 Büchi+nested-DFS（**双 DFS 手推环检测**）；on-the-fly、偏序归约、Never claim；Promela 建模互斥协议。【PSPACE-complete（公式长度）】 | 手写 nested-DFS + Spin（MinGW/WSL，可选） |
| 08 | [TLA+：规约即数学](./08-TLA+与TLC.md) | ✅ | 行为规约（状态=值，无对象）；PlusCal→TLA+ 翻译；**两阶段提交 PlusCal 死锁手推**；TLC 显式枚举+不变式+覆盖；TLAPS 证明层；AWS CACM 2015（S3/DynamoDB）案例；vs 07：规格语言×检查工艺正交。【模型检查 PSPACE；TLC=显式枚举】 | 手写 TLC 式 BFS + TLC jar（Java，可选） |
| 09 | [Alloy：关系逻辑的小世界](./09-Alloy关系逻辑.md) | ✅ | 一切皆关系（点乘/方盒/转置算子）；事实/断言/检查；**地址簿 alias 断言 scope=3 小反例手推**；Kodkod→SAT（回连 03 CDCL）；"小反例"哲学 vs 定理证明；轻量级 FM 定位。【有界=NP；无界不可判定】 | z3 关系编码对拍 + Alloy jar（Java，可选） |

### 卷三 · P：概率定量（10-11）

| # | 标题 | 状态 | 核心锚点 | 仪器 |
|---|------|------|----------|------|
| 10 | [PRISM：概率模型检测](./10-PRISM概率模型检测.md) | ✅ | DTMC/CTMC/MDP；PCTL 语法；**2 态 DTMC 的 P(F reach) 线性方程组手推**；MDP=max-min→LP/价值迭代（numpy 跑例）；**P≤p 的定量保证**；参数化模型与置信重构。【P】 | numpy 手推 + PRISM（Windows 安装包，可选） |
| 11 | [Storm：高性能概率检查](./11-Storm与高性能概率检查.md) | ✅ | 稀疏引擎 vs 符号引擎（**连 12：BDD/MTBDD**）；精确有理数 vs 浮点；JANI/PRISM 双前端；stormpy；PRISM 入门 vs Storm 上量的分工；1100 万状态案例叙事。【P（大输入的工程战）】 | scipy.sparse 价值迭代 + stormpy（WSL，可选） |

### 卷四 · 引擎室：BDD/进程代数/自动机学习（12-14）

| # | 标题 | 状态 | 核心锚点 | 仪器 |
|---|------|------|----------|------|
| 12 | [BDD：状态爆炸的解药](./12-BDD与CUDD.md) | ✅ | Shannon 展开/ite；**同一公式两种变量序节点数手推（n vs 2ⁿ）**；apply/restrict/∃量化；CUDD 架构（唯一表/计算缓存/互补边）；ZDD 一句；Sylvan 多核 work-stealing；dd 的 CUDD 绑定；**PRISM/Storm 符号引擎=CUDD 生态闭环**。【PSPACE 的符号化武器】 | dd（pip）+ 手写 ite 对拍 |
| 13 | [进程代数与 mCRL2](./13-进程代数与mCRL2.md) | ✅ | CCS 的前缀/选择/并行‖/限制；**两进程互模拟判定手推**；μ-演算=LTL∪CTL 公共超集（**NP∩coNP 未解之谜**——Zoo 活展品）；LPE 线性化；mCRL2 工具链 vs FDR/CSP。【交替不动点：NP∩coNP】 | 手写 CCS toy + pyformlang + mCRL2（Windows 包，可选） |
| 14 | [自动机学习 L\*：从黑盒重建模型](./14-自动机学习Lstar.md) | ✅ | Angluin L*：成员+等价查询、观察表闭合+一致；**(a\|b)\*ab 观察表演化手推**；MAT 模型；反例加列；W 方法测试上界一句；LearnLib/AutomataLib 架构；应用：协议逆向/legacy 系统。【多项式查询复杂度】 | 手写 L* + automata-lib 对拍 + pyformlang 交叉 |

### 收尾 · 复杂度动物园（50）

| # | 标题 | 状态 | 核心锚点 | 仪器 |
|---|------|------|----------|------|
| **50** | [收尾：复杂度动物园与选型决策树](./50-复杂度动物园与选型.md) | ○ | 全系列复杂度地图（P→NP/coNP→PSPACE→NP∩coNP→不可判定，每工具归位）；**两问定位决策树**（你有什么×你要什么→工具）；工具依赖生态图（CUDD→PRISM/Storm 符号引擎；Z3←Dafny/Alloy；CBMC 自带 SAT 求解器谱系）；验证剧场批判（连卷零 00）；识别"我的问题在哪一格"三步法（判定化→证书结构→归约）。 | 决策树 + 生态图 |

### 教学实验（experiments/，双轨：Python 保底 + 原生可选）

依赖安装（阿里源）：`pip install -i https://mirrors.aliyun.com/pypi/simple/ -r experiments/requirements.txt`；环境自检：`python experiments/env_check.py`。每个 lab 为 `lab{NN}_{slug}.py`（服务对应章节，正文「仪器」节给命令）；原生工具一律 `--native` 开关、默认跳过、装不通不阻塞。

---

## 怎么用

- **想知道"形式化验证到底验证什么"**：直接读 [00 篇](./00-为什么形式化+Lean4SOTA.md)
- **想把 Lean4 塞进 RL 训练循环**：[00](./00-为什么形式化+Lean4SOTA.md) → [01 篇](./01-Lean4作为RL奖励验证器.md)（速度可行性 + 工程陷阱）
- **想搞 AlphaProof 式神经符号闭环**：[00](./00-为什么形式化+Lean4SOTA.md) → [`讲透神经符号`](../讲透神经符号/)
- **想理解 RL 为什么在形式化域有根本难点**：[00](./00-为什么形式化+Lean4SOTA.md) §五 → [`讲透RL/04`](../讲透RL/04-RL与形式证明.md) §五

---

## 配套

- 实战：[`讲透RL/04-RL与形式证明`](../讲透RL/04-RL与形式证明.md)（AlphaProof 后时代）
- 神经符号闭环：[`讲透神经符号`](../讲透神经符号/)
- RL 能力边界：[`讲透RL/05-RLVR的极限`](../讲透RL/05-RLVR的极限.md)

---

## 🔗 理论锚点（§12-15 横向打通）

> 本系列讲"为什么形式化 + Lean4 SOTA"；名校理论课把每一层**公理化**：
> 枢纽：[`§12-15 整合`](../§12-15%20理论·形式化·安全·可信AI%20整合.md) §21

| 课程 | 产物 | 公理化的内容 |
|---|---|---|
| §13.1 Oxford CPP | [`cpp.py`](../top-cs-projects/oxford-cs-projects/topic12-foundations/cpp.py) | Curry-Howard + STLC + CCC——Lean4 的类型论根基 |
| §13.2 Cambridge Hoare Logic | [`hoare_logic.py`](../top-cs-projects/cambridge-cs-projects/topic4-compiler/hoare_logic.py) | Hoare 三元组 + WP + 循环不变式方法（seL4 验证的方法论祖先）|
| §13.3 ETH FM（Basin）| [`formal_methods.py`](../top-cs-projects/eth-cs-projects/topic3-fm/formal_methods.py) | CTL Model Checking + DPLL + TLA+ 规约 |
| §13.4 CMU 15-414（Platzer）| [`diff_dyn_logic.py`](../top-cs-projects/cmu-cs-projects/topic12-theory/diff_dyn_logic.py) | differential dynamic logic + barrier certificate（cyber-physical 验证）|


---

## 🎭 欺骗动力学视角：数学/程序里藏漏洞

> 承接 [`欺骗动力学-社会进步的隐秘引擎.md`](../欺骗动力学-社会进步的隐秘引擎.md) §5。

### 三问

1. **讲透形式化验证 防的是什么欺骗？** → 证明或代码里的错误被人忽略（hand-waving 掩盖漏洞）。
2. **被什么攻破？** → 形式化系统本身的元理论不一致 / 公理选择错误。
3. **沉淀进哪条主链？** → 密码学主链 + 验证主链——Lean4 把证明可信从「人审」变成「机器可检验」。

### 一句话

> 形式化验证是反欺骗的终极形态：把「我相信这个证明」变成「机器必须验证这个证明」。
