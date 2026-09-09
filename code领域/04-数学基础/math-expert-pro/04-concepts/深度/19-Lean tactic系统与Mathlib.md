# Lean tactic 系统与 Mathlib 结构

> Lean 4 不只是证明检查器——它的 tactic 系统是"自动证明助手"。

## Lean 的架构
1. Kernel（内核）：类型检查器（最小可信基础）
2. Elaborator：把人类书写转为 kernel 代码
3. Tactic framework：交互式证明策略
4. Mathlib：社区数学库（150万行+）

## 核心 tactic
| Tactic | 功能 | 等价数学操作 |
|--------|------|-------------|
| intro | 引入假设 | "设 x:A" |
| apply | 反向推理 | "由 B 只需证 A" |
| exact | 直接提供 | "用这个证明" |
| simp | 自动化简 | "显然" |
| ring | 环等式 | 交换环恒等式自动证 |
| norm_num | 数值计算 | 算术 |
| omega | Presburger | 线性整数算术 |
| induction | 归纳法 | "对 n 归纳" |
| tauto | 经典命题 | 命题逻辑自动 |

## Mathlib 的组织
- Algebra（代数）：群/环/域/模/线性代数
- Analysis（分析）：拓扑/微积分/测度/PDE
- Topology（拓扑）：点集拓扑/代数拓扑
- NumberTheory（数论）：素数/同余/椭圆曲线
- CategoryTheory（范畴论）：范畴/函子/伴随
- Data（数据结构）：列表/集合/树

## 贡献流程
1. Fork mathlib4 → 写证明 → PR
2. CI 自动检查（编译+测试+格式）
3. 维护者 review → 合并
4. 每个定理永久可验证

## 关联
- [百科-19-形式化与AI](../百科-19-形式化与AI数学.md)
- [14-frontier/AI-for-Math/02-Lean入门](../../14-frontier/AI-for-Math/02-Lean形式化数学入门.md)
- [14-frontier/AI-for-Math/03-Tao](../../14-frontier/AI-for-Math/03-Tao的AI数学实践.md)
