# distilled_math — 模型数学知识蒸馏库（教师模型内隐知识 → 可验证外显资产）

> **这是什么**：把教师模型（GLM-5.3 + 文献核检）头脑中的数学知识，按域系统化蒸馏为**可验证的知识卡**。
> 与 [AI_MATH_FOREST.md](../AI_MATH_FOREST.md) 的分工：FOREST 回答"AI 需要哪些数学"（需求地图），本库回答"模型肚子里有哪些数学"（供给侧显性化）——两边对撞就是 [BIDIRECTIONAL_FLYWHEEL](../BIDIRECTIONAL_FLYWHEEL.md) 的知识面。
> **方法论**：[METHODOLOGY.md](METHODOLOGY.md)（本地十条蒸馏规律 × 网络最新六法的融合操作规程，必读）。
> **血缘**：本单元是 [实战案例-Prover数学Agent](../../讲透Agent/实战案例-Prover数学Agent/README.md) 逆向蒸馏经验的泛化——从"蒸馏证明能力"扩展到"蒸馏数学知识"。
> 建库：2026-08-27。

---

## 蒸馏宪法（三条，来自 METHODOLOGY）

1. **每个数学断言必须带置信分层**：★已机器验证（SymPy/NumPy 断言通过）/ ☆教师模型高置信但未独立核 / ⚠有争议或简化叙述。禁止无标记断言。
2. **arXiv ID 绝不凭记忆写**（项目铁律）：不确定的一律写"出处待核"，宁缺毋滥。
3. **新卡必须挂网**：写入本目录的卡必须登记进下方篇目表 + 至少一条 FOREST 域互链，否则是孤儿内容。

## 篇目表（目录宪法）

### 方法论

| 文件 | 内容 | 状态 |
|------|------|------|
| [METHODOLOGY.md](METHODOLOGY.md) | 蒸馏操作规程：Prover 十条规律（R1-R10）× 网络最新六法（OPD/SIKeD/VCRD/DRP/DED/Caprese）→ 知识蒸馏管线 | ✅ |

### 域卡（教师模型的域级知识显性化）

| card_id | 域 | 互链 FOREST 域 | 状态 |
|---------|----|---------------|------|
| [DM-LIN-01](DM-LIN-01-线性代数.md) | 线性代数 / 矩阵分析（样板卡，主会话亲笔；含教师公式错误被断言推翻的诚实留痕） | 域一 | ✅ |
| [DM-ALG-01](DM-ALG-01-抽象代数.md) | 抽象代数（群环域 / Galois） | 域十六（范畴侧） | ✅ |
| [DM-NUM-01](DM-NUM-01-数论.md) | 数论（初等 / 解析 / 代数数论导引） | 域十九·B | ✅ |
| [DM-CAT-01](DM-CAT-01-范畴论.md) | 范畴论与组合语义 | 域十六 | ✅ |
| [DM-REAL-01](DM-REAL-01-实分析与测度.md) | 实分析 / 测度论 / 积分 | 域六 | ✅ |
| [DM-CPLX-01](DM-CPLX-01-复分析.md) | 复分析 | 域六（延伸） | ✅ |
| [DM-FUNC-01](DM-FUNC-01-泛函分析.md) | 泛函分析（Banach / Hilbert / 算子谱） | 域六 / 域十一 | ✅ |
| [DM-PROB-01](DM-PROB-01-概率与随机过程.md) | 概率论 / 随机过程 / 高维概率 | 域二 / 域十五 | ✅ |
| [DM-INFO-01](DM-INFO-01-信息论与编码.md) | 信息论 / 编码理论 | 域三 / 域十九·D | ✅ |
| [DM-COMB-01](DM-COMB-01-组合与图论.md) | 组合数学 / 图论 | 域十四 | ✅ |
| [DM-ODE-01](DM-ODE-01-微分方程与动力系统.md) | ODE / PDE / 动力系统 / 混沌 | 域十三 | ✅ |
| [DM-GEO-01](DM-GEO-01-几何与拓扑.md) | 几何与拓扑（微分几何 / 代数拓扑导引） | 域八 / 域十 | ✅ |
| [DM-OPT-01](DM-OPT-01-优化与变分.md) | 优化理论 / 变分法 | 域四 | ✅ |
| [DM-NUMA-01](DM-NUMA-01-数值分析.md) | 数值分析 / 计算数学 | 域七 | ✅ |
| [DM-LOGIC-01](DM-LOGIC-01-数理逻辑与计算理论.md) | 数理逻辑 / 可计算性 / 复杂性 | 域十九·B | ✅ |
| [DM-META-01](DM-META-01-学习元知识.md) | 学习元知识：证明策略库 + 模型视角的解题模式 | 全域（横切） | ✅ |

> 状态图例：🔄 生成中 / ✅ 已验证（SymPy 断言全过+抽查通过）/ ⚠️ 有未过断言待修。

### 验证脚本（experiments/）

每张域卡配一个 `dm_<域>_check.py`：8-20 条 SymPy/NumPy 断言，对应卡内 ★ 标记的断言。卡片状态升 ✅ 的唯一标准 = 脚本真跑全过。

**批次统计（2026-08-27 建库首跑，主会话独立复跑）**：16 卡 / 16 脚本 / 230+ 断言全过 / 互链 163 条 0 死链 / md 总计 2237 行。
**R5 现场案例（验证器抓教师错误 ×4，全部留痕卡内）**：DM-LIN Courant-Fischer 公式方向写反（主会话亲笔卡，L9 断言推翻后修正）；DM-COMB 哑铃图 λ₁ 紧性归属写反（实测纠正教师初稿直觉）；DM-OPT FISTA 斜率定理实测失真降级 ☆；DM-CPLX z=−2 延拓值笔误被自家断言抓住。

已验证批次（16/16，其余 10 脚本：alg/num/cat/real/cplx/func/prob/info/comb/lin，各 12-15 断言全过）：
- `dm_numa_check.py`（DM-NUMA-01，22 断言，2026-08-27 全过：Wilkinson/Runge/Hilbert 条件数/Euler 稳定域/Simpson/Kahan/CG）
- `dm_logic_check.py`（DM-LOGIC-01，14 断言，2026-08-27 全过：对角逃逸/quine/Gödel 编码/归约保持/2-SAT 一致性）
- `dm_meta_check.py`（DM-META-01，19 断言，2026-08-27 全过：不变量/极端原理/强化归纳/R(3,3)/Mertens 警示/Fermat 数）
- `dm_ode_check.py`（DM-ODE-01，13 断言，2026-08-27 全过：Peano 非唯一/有限逃逸/Lyapunov/saddle-node/pitchfork/Lorenz+Benettin/Hopf/辛 Euler/CFL/倒向热不适定）
- `dm_geo_check.py`（DM-GEO-01，15 断言，2026-08-27 全过：球柱面 K/Girard/Poincaré Christoffel/双曲 GB/大圆测地/χ/角盈余/环绕数/Fisher 两参数化/Rao 距离/KL 不对称/双曲圆周）
- `dm_opt_check.py`（DM-OPT-01，13 断言，2026-08-27 全过：Fenchel–Young/LP+Slater 对偶/KKT/软阈值/Moreau/ISTA-FISTA 分离/ADMM+Lasso KKT/最速降线/PL/SP-μP 尺度/非凸 KKT/整数 gap）

```bash
cd top-math-courses/distilled_math/experiments
for f in dm_*.py; do timeout 180 python3 "$f" >/dev/null 2>&1 || echo "FAIL: $f"; done
```

## 使用方式（三种读者）

0. **Agent 自动路由（2026-08-27 已接线）**：项目 skill `math-distilled`（[.opencode/skills/math-distilled/SKILL.md](../../.opencode/skills/math-distilled/SKILL.md)）——任何 opencode 会话遇数学问题自动按域路由到本库卡片 + 强制置信分层引用协议（★ 直引 / ☆ 复核 / ⚠ 明示争议）。
1. **学习者（你）**：每卡 §6 的 ZPD 路径是入口；§3 反例与陷阱是模型见过最多人栽的坑，先读。
2. **AI 助手（未来的会话）**：把本库当作教师模型的知识快照——回答数学问题前先查对应域卡的置信分层，★ 可直接引用，☆ 需复核，⚠ 需明示争议。
3. **发现引擎（MATH_DISCOVERY_ENGINE）**：卡内"模型知识边界"（哪些问题是模型知道没把握的）是埋雷选题的原料。

## 与 13 节点远程的关系（后续增强，非阻塞）

重点定理的 **L3 级验证**（Lean 陈述编译）走远程 Prover-V2 管线（[remote/](../../remote/README.md)，Prover-V2@C500 vllm serve + lean421）。首批以 L1（SymPy）+ L2（出处核实）为准，L3 作为增量任务挂账。

## B 阶段：第二教师交叉验证（2026-08-27，已执行 14/24）

**Qwen2.5-Math-7B-Instruct**（13 节点 C500 推理）作为独立第二教师判断 24 题（18 真题 ★ 断言 + 6 陷阱）。可判定 14 题：**真题 12/12 零分歧** + 陷阱 2/2（其中 F05 为教师出题错误被第二教师纠正——交叉验证的真正价值在"抓教师"）。剩余 10 题因 MACA 驱动队列泄漏（基础设施故障）待续。详见 [experiments/CROSS_VALIDATION_REPORT.md](experiments/CROSS_VALIDATION_REPORT.md)。
