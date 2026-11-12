# 06 · Dafny：验证感知语言

> 卷一收官站。04 章截断（k 步内完备）、05 章过近似（可靠但假阳性），本章走第三条出路——**人给不变式**：Leino（MSR 起家）的**Dafny** 把合同直接写进语言（`requires`/`ensures`/`invariant`/`decreases`），编译器把每个方法变成一串**验证义务**（最弱前置条件 WP），每条义务恰是 [03 章](./03-SMT求解与Z3cvc5.md)吃得下的 NP/coNP 公式——**不可判定没有被解决，被分解绕开了**。手推 lab06 的 `if (x>y) {r=x} else {r=y}`：后置 r≥x∧r≥y 两分支化简全绿、后置 r>x 当场出反模型；爬 **BinarySearch 的两道不变式墙**（界墙+值墙）；掀开 **Boogie 中间层**看 Dafny→Boogie→Z3 的两级降维；最后造桥回卷零——**全自动（Dafny）vs 交互（Lean4）**：义务粒度、红球绿球、证明搜索的三维对照。仪器：[`experiments/lab06_wp_dafny.py`](./experiments/lab06_wp_dafny.py)（z3 复现 WP 检查）+ Dafny zip（.NET，可选）+ [`max.dfy`](./experiments/max.dfy)。【不可判定→义务分解到 NP】

---

## 一、义务驱动的编程：合同写在哪

程序安全不可判定（[04 章](./04-有界模型检查CBMC.md) §一），三条出路各付各的税：BMC 付 k、抽象解释付假阳性、**本章付人年**——不变式由人写，检查由机器做。Dafny 的答案是让"验证"成为语言的**一等语法**，而不是外部工具的事后审计：

```dafny
method Max(x: int, y: int) returns (r: int)   // ← max.dfy 原文
  ensures r >= x && r >= y && (r == x || r == y)
{
  if x > y { r := x; } else { r := y; }
}
```

`ensures` 写在签名旁、花括号里只有普通代码——**合同即签名**。五个关键字各就各位：

| 关键字 | 写在哪 | 管什么 | 违反时 |
|---|---|---|---|
| `requires` | 方法签名 | 前置：调用者的义务 | 调用点红叉 |
| `ensures` | 方法签名 | 后置：实现者的义务 | 方法体红叉+反例 |
| `invariant` | 循环头 | 循环不变式：循环的合同 | 循环体红叉 |
| `decreases` | 方法/循环 | 终止性度量（良基递减） | 不终止即红叉 |
| `assert`/`lemma` | 任意位置 | 中途事实 / 可调用引理 | 该行红叉 |

合同还带来**模块化**：每个方法独立清偿自己的义务——验证 `Max` 的方法体时 `assume` 它的 `requires`、证明它的 `ensures`；将来任何调用点，`Max(x,y)` 的 `ensures` 直接当**已证事实**用（实现细节不再进场）。大程序不必一次性摊开，义务按方法切块、逐块清偿——这正是 seL4 一脉（卷零 00）"逐层精化"的日常工具版。规格侧还有**幽灵元素**（ghost 变量/函数）：只参与证明、不参与编译——规格想说的数学，不必伪装成可执行代码。Dafny 默认还查终止：变式猜不出就报错让人补 `decreases`；验证过的程序可提取 C#/Go/Java 等真代码——**证明一次，部署多处**。

## 二、WP 三规则手推：lab06 的完整推导

Dafny 内部把"这个方法对不对"变成"这条公式永真吗"——翻译官是**最弱前置条件**（weakest precondition，Dijkstra 1976《A Discipline of Programming》）：`wp(S, Q)` = 能使 S 执行后 Q 成立的**最弱**前置条件（弱 = 约束最少、罩住最多的初始状态）。三条规则就够推 lab06 的程序：

1. **赋值**：`wp(x := e, Q) = Q[e/x]`——把后置里的 x 逐个换成 e，**倒着**代回去；
2. **顺序**：`wp(S1; S2, Q) = wp(S1, wp(S2, Q))`——从最后一句话往回复合；
3. **if**：`wp(if g then S1 else S2, Q) = (g → wp(S1,Q)) ∧ (¬g → wp(S2,Q))`——两个卫蕴含拼合。

拿 lab06 的程序 `if (x > y) { r = x } else { r = y }`、后置 `Q: r≥x ∧ r≥y` 完整手推（docstring 锚点原样展开）：

```
then 分支:  WP(r:=x, Q) = (x≥x ∧ x≥y)   ⟸ 卫 x>y
            化简: x≥x 永真；x>y ⟹ x≥y（整序）→ 只剩 x≥y，被卫本身蕴含 ✓
else 分支:  WP(r:=y, Q) = (y≥x ∧ y≥y)   ⟸ 卫 ¬(x>y) 即 x≤y
            化简: y≥y 永真；只剩 y≥x ⟸ x≤y ✓
合:         WP(if, Q) = (x>y → x≥y) ∧ (x≤y → y≥x) —— 两支全被卫白送，永真
```

义务交给 [03 章](./03-SMT求解与Z3cvc5.md)的引擎：**WP 永真 ⟺ ¬WP 不可满足**——`check_valid` 就是 03 章 §五"取反喂求解器"的姿势原样搬来。lab06 实跑输出：

```
Q: r>=x ∧ r>=y  → VALID（WP 手推两条分支化简见 docstring）
Q': r>x         → 不可证, 反模型: [y = -1, x = 0]（x≥y 即踩爆：x>y 时 r=x、x=y 时 r=y，都不严格大）
lab06 自检通过
```

后置加强成 `Q': r>x` 会怎样？then 分支的 WP 变成 `x>x`——**恒假**，任何 x>y 都是反模型；z3 给出 [x=0, y=-1]（x>y 走 then，r=x，r>x 即 0>0 不成立）。红叉连着反例模型一起递到手上——**义务化编程的第一现场**：规格写错，机器不猜、只给你反例（04 章"反例=模型"在源码级的复刻）。

max.dfy 的 `ensures` 其实还有第三个合取支 `(r == x || r == y)`——两分支各自 `x==x`、`y==y` 永真，∨ 一边即真，与 lab06 的 VALID 互为印证。顺手把**顺序规则**也用掉，看赋值连写时规则怎么接力（语句 `s = x + y; r = s - y`，后置 `r == x`）：

```
内层:  WP(r := s−y, r==x) = (s−y == x)                      ← 从最后一句倒代换
外层:  WP(s := x+y; r := s−y, r==x) = WP(s:=x+y, s−y==x)
     = ((x+y)−y == x)   永真 ✓（数学整数；32 位机上 y=INT_MAX 就是另一部电影）
```

从最后一句往回传，外层赋值把内层算出的 WP 当自己的后置——这就是规则 2 的全部含义：**WP 是台倒着开的翻译机**，程序顺着写、证明倒着算。

**while 规则一段话**：`wp(while g do S, Q)` 的精确最弱前置需要对"S 的语义"做不动点迭代——一般不可算，这正是不可判定性的老巢。工程出路是**不动量**：人给不变式 I，机器只查四条小义务——①入口 `P ⟹ I`；②保持 `(I ∧ g) ⟹ wp(S, I)`（I 是不动量：转一圈还在）；③出口 `(I ∧ ¬g) ⟹ Q`；④终止 `decreases` 良基递减。I 不必最弱，**足够强就行**——人给提示、机器给检查，这就是"义务分解到 NP"的全部秘密。Hoare 三元组 `{P}S{Q}` 与 WP 的关系一句话收拢：`{P}S{Q} ⟺ P ⟹ wp(S,Q)`（部分正确性；加 ④ 即完全正确性）。

## 三、BinarySearch 两道墙：不变式的工艺

二分查找是 Dafny 的"hello world"级考题——Leino《Program Proofs》（MIT Press 2023）的招牌例。完整代码（四条义务下文逐一验收）：

```dafny
method BinarySearch(a: array<int>, key: int) returns (r: int)
  requires forall i, j :: 0 <= i < j < a.Length ==> a[i] <= a[j]   // 升序
  ensures 0 <= r <= a.Length                                      // r = 插入点
  ensures forall k :: 0 <= k < r ==> a[k] < key                   // 左边全 <
  ensures forall k :: r <= k < a.Length ==> key <= a[k]           // 右边全 ≥
{
  var lo, hi := 0, a.Length;
  while lo < hi
    invariant 0 <= lo <= hi <= a.Length                           // 墙一：界墙
    invariant forall k :: 0 <= k < lo ==> a[k] < key              // 墙二左
    invariant forall k :: hi <= k < a.Length ==> key <= a[k]      // 墙二右
    decreases hi - lo
  {
    var mid := (lo + hi) / 2;
    if a[mid] < key { lo := mid + 1; } else { hi := mid; }
  }
  r := lo;
}
```

**墙一（界墙）** `0 ≤ lo ≤ hi ≤ n`：入口成立（0≤n 由数组定义白送）；保持靠中点引理——lo<hi 时**lo ≤ mid < hi**（下取整除法），于是 `lo := mid+1` 不冲破上界（mid+1≤hi）、`hi := mid` 不冲破下界（mid≥lo）。界墙还顺手保安全：`a[mid]` 的访问自动生成义务 `0 ≤ mid < a.Length`——**越界不是运行时崩溃，是验证期红叉**。若中点取上整 `(lo+hi+1)/2`，lo=hi−1 时 mid=hi，hi=n 时当场越界红——界墙不答应。

**墙二（值墙）** `a[<lo] < key`、`key ≤ a[≥hi]`（∀k<lo: a[k]<key ∧ ∀k≥hi: key≤a[k] 的速记）：二分的不变量是"key 若在数组里，只能藏在 [lo,hi) 这扇未搜区里"，左右墙就是搜过的两半的验收单。维护拿 then 分支走一遍：`lo := mid+1` 后要证 `∀k<mid+1: a[k]<key`——老左墙给 k<lo 的部分，分支条件给 k=mid，**中间那段 k∈[lo,mid) 呢？**靠 `requires` 的排序传递性：a[k] ≤ a[mid] < key——SMT 必须把排序量词实例化到 (k, mid) 上（03 章 E-matching 的 trigger 机制），链子才接得上。这是本例唯一非平凡的一步，也是"**排好序**"三个字在证明里的确切位置。else 分支对称（key ≤ a[mid] 传给右墙）。

**出口与终止**：循环退出时 lo≥hi，与界墙合逼 lo=hi——左墙给 r 以左、右墙给 r 起右，三条 `ensures` 全落；`decreases hi−lo` 严格递减（mid<hi 保证 then 支至少 +1、hi:=mid 至少 −1）——终止性不是注释，是第四条义务。顺手一个工业彩蛋：C 里 `(lo+hi)/2` 的加法溢出让 JDK 的二分错了近十年（Bloch 2006："几乎所有人的二分都是错的"）；Dafny 的 `int` 是无界数学整数，加法不溢出，越界另有界墙把守——**两类经典 bug，各有各的守门人**。

## 四、Boogie 中间层：Dafny→Boogie→Z3 的两级降维

Dafny 不直接调求解器，中间垫一层 **Boogie**（MSR Spec# 时代独立出来的中间验证语言，一族验证器的公共母机——VCC/Corral 同栖）。**两级降维**：第一级**语言→逻辑**，Dafny 把类/数组/归纳类型/量词/幽灵元素统统降成朴素命令式 + 一阶逻辑（数组就是 03 章表里的 ARR 理论 select/store）；第二级**逻辑→判定**，Boogie 把每个 `assert` 连同一路的 `assume` 卷成一条验证条件，喂 Z3。max.dfy 的翻译（简化示意，去了标签编号与堆簿记）：

```boogie
procedure Impl$Max(x: int, y: int) returns (r: int)
{
  if (x > y) { r := x; } else { r := y; }
  assert r >= x && r >= y;      // ← 后置变成义务
}
```

每个 assert 的判定姿势：`assume 之前的全部 ∧ ¬assert` → **unsat 即证毕**——与 lab06 的 `check_valid`、03 章 §五的符号执行一模一样。整条流水线画出来：

```
max.dfy ──Dafny 解析/解引用/归纳数据类型──► Boogie（朴素命令式 + 一阶公理）
        ──Boogie 生成验证条件 VC─────────► SMT-LIB 公式
        ──Z3：DPLL(T)（03 章 §二/§三）───► unsat ✓ / sat + 模型
        ──模型沿行号折回─────────────────► IDE 红球 + 反例
```

于是卷一的链条全线贯通：**Dafny（义务生成器）→ Boogie（逻辑降落伞）→ Z3（03 章的 DPLL(T) 引擎）**——"验证器"三个字的解剖图就是"义务生成器 + 求解器"两只手；05 章 CPAchecker 的每个域迁移、04 章 BMC 的展开公式，兜底也都是同一台引擎。红叉时 Z3 的模型沿原路折回 Dafny 源码行号——反例还是那个反例，只是穿了 IDE 的衣服。

## 五、全自动 vs 交互：Dafny↔Lean4（卷零之桥）

卷零 00 站在 Lean4 一侧看 SOTA；本章站在 Dafny 一侧回望——同一门手艺的两端，三个维度量差距：

| 维度 | Dafny（全自动） | Lean4（交互，卷零 00） |
|---|---|---|
| 义务粒度 | 机器从合同**生成** SMT 公式，人只给提示（不变式/assert/引理） | 人**手写**每一步 tactic，机器检查每个证明项 |
| 红球绿球 | 方法旁绿勾/红叉，打字即重验；红叉带**反例模型**（03 章"反例=模型"） | InfoView 实时显示剩余目标；红字是"**还差哪个目标**" |
| 证明搜索 | 外包给 Z3（线性算术/EUF 决策 + trigger 启发式） | 人肉搜索 + `omega`/`grind`/`duper`（03 章 §五：结果可外包、证明不外包） |

三行表格三句判词。**粒度**：Dafny 的一条义务可能已是 Lean 里十步 tactic 的工作量（线性算术被整块决策掉），反过来 Dafny 证不动的地方（归纳结构、非线性）在 Lean 里只是换个引理——义务切多细，决定自动化能吃下多少。**体验**：Dafny 的绿是"Z3 说证完了"（但你不知道它走了哪条路），Lean 的绿是"每一步都过目"（但一步都省不得）——红的信息量同样不对称：Dafny 给反例（输入侧的why-not），Lean 给目标（证明侧的 to-do）。**信任**：Dafny 默认**信** Z3 的 unsat、不重建证明——Z3 出 bug 就是 Dafny 出 bug；Lean 把证明压到内核检查，但内核也是软件（卷零 #14576 无公理伪证的教训）——两条信任链各有单点，谁也不是免费的安全感。选型口诀：**代码的正确性用 Dafny 敲（合同+提取），数学的正确性用 Lean 磨（Mathlib 生态）**；中间地带正在合拢——Dafny 的 `lemma` 写归纳证明、Lean 的外部求解器重建证明，两端互相伸手（Rust 生态的表亲 Verus，卷零 00 的 Atmosphere 主力，同一门派）。

## 六、仪器

- **Python 保底（本 lab）**：`python 讲透形式化验证/experiments/lab06_wp_dafny.py`——WP 三规则手推的机器版：max 后置两分支化简后 `check_valid` 得 unsat → VALID；strict 后置取反 sat，反模型原样打印（§二 输出即本 lab 输出）。仅依赖 z3。
- **Dafny（zip 需 .NET，可选）**：[github.com/dafny-lang/dafny/releases](https://github.com/dafny-lang/dafny/releases) 下载 `dafny-x.x.x-x64-win.zip` → 装 **.NET SDK 8+**（`winget install Microsoft.DotNet.SDK.8`）→ 解压、把 `dafny` 目录加 PATH → 实跑：`dafny verify 讲透形式化验证/experiments/max.dfy`（4.x 前的老版本直接 `dafny max.dfy`），预期末行 `Dafny program verifier finished with 1 verified, 0 errors`（单方法、老版横幅；Dafny 4.x 的 `dafny verify` 成功时静默退出——无横幅即成功）。再把 ensures 改强成 `r > x` 跑一遍——错误落在 ensures 行、反例模型（x>y 一类）随之而来，就是 §二 Q' 的红叉现场。IDE 体验（§五 红球绿球）：VS Code 装 Dafny 官方扩展即得。
- 依赖与环境自检见 [`experiments/requirements.txt`](./experiments/requirements.txt) 与 [`env_check.py`](./experiments/env_check.py)（本 lab 仅用 z3）。

## 七、不足与边界

1. **不变式仍是人的负担**：05 章的抽象解释自动给的只是弱不变式（区间墙撑不起 BinarySearch 的值墙）；足够强的不变式非平凡——"人给提示"意味着验证成本随程序巧妙度回潮，seL4 的 20 人年里大半花在这。
2. **量词实例化是玄学**：§三 的排序传递性要 E-matching 猜对 trigger (k, mid)——猜错就 timeout/unknown；义务属于 NP/coNP ≠ 自动解得动，指数阈值在等每个人。
3. **别名/堆的编码代价**：对象图翻成 `$Heap` 的 select/store + 动态帧（`modifies` 子句），每条义务随堆形状膨胀——纯函数式的 Max 三行义务，链表反转可能一屏——指针密集的 C 风格代码在 Dafny 里写得很贵。
4. **信任 Z3 的单点**：不重建证明（对照 cvc5 的证明输出与 lean-smt 的证明重建，03 章 §四/§五）——solver 的 unsat bug 直接传染；实验性的证明证书选项尚不成气候。
5. **终止性的边角**：`decreases` 猜不到要人给；复杂终止论证（势能法）要拆引理——完全正确性的第四条义务从不白送。
6. **卷一收官的账**：不可判定没有消失——04 章截断付 k、05 章近似付假阳性、本章分解付人年；三格在 [50 章](./50-复杂度动物园与选型.md)动物园归位，本章的格是"**不变式给定后，每条义务 ∈ NP/coNP**"。下一卷换问法：不再"对一切输入"，而是"对一切路径"——[07 章](./07-LTL与Spin.md)起进 PSPACE。

---

**锚点行**：Dafny（Leino，MSR）= 验证感知语言——合同（requires/ensures/invariant/decreases）写进语法，程序翻译成验证义务；WP（Dijkstra 1976）三规则：赋值 Q[e/x] 倒代换、顺序往回复合、if 卫蕴含合取——手推 `if (x>y){r=x}else{r=y}` 对 r≥x∧r≥y：then 化简 x≥y⟸x>y、else 化简 y≥x⟸x≤y，永真 ✓lab06；换 r>x 则 x>x 恒假、反模型 [x=0,y=−1] 即规格错误第一现场；while=不动量（入口/保持/出口/终止四义务）；BinarySearch 两道墙——界墙 0≤lo≤mid<hi≤n 保界保安全（越界=验证期红叉）、值墙 a[<lo]<key≤a[≥hi] 靠排序传递性（E-matching 实例化 (k,mid)）——JDK 二分溢出 bug（Bloch 2006）在无界 int+界墙下无处藏身；两级降维 Dafny→Boogie→Z3（回链 03：assume∧¬assert→unsat）；全自动 vs 交互（义务粒度/红球绿球/证明搜索——卷零之桥，Dafny 信 solver、Lean 压内核）；复杂度：**不可判定分解成无穷个 NP/coNP 小义务——人付提示、机器付搜索**。【不可判定→义务分解到 NP】

🔗 上一章 [05 抽象解释](./05-抽象解释与CPAchecker.md)（三条出路的第二格）｜下一章 [07 LTL 与 Spin](./07-LTL与Spin.md)（卷二 PSPACE 开卷）｜义务的引擎 [03 SMT](./03-SMT求解与Z3cvc5.md)｜截断的第一格 [04 BMC](./04-有界模型检查CBMC.md)｜卷零之桥 [00 Lean4 SOTA](./00-为什么形式化+Lean4SOTA.md)｜动物园归位 [50](./50-复杂度动物园与选型.md)
