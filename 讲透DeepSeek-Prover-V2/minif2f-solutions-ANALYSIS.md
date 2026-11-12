# DeepSeek-Prover-V2 minif2f-solutions.zip 开采报告（2026-11-03）

来源：`/usr-data/data2/repos/deepseek-ai/DeepSeek-Prover-V2/minif2f-solutions.zip`（455,902 B，git 仅一版 e598a57）
解包：`unzip -o minif2f-solutions.zip -d /tmp/minif2f-solutions/`（只读原仓，产出 valid/ test/ 两目录）

## 1. 口径判定：不是 147 题，是 438 题完整解

**"147 题"不成立**——zip 内 438 个唯一题名（无重名、无多解同题），零 `sorry`/`admit`。精确口径：

| split | 解出数 | miniF2F v1 标准数 | 比例 | 对应论文数字 |
|---|---|---|---|---|
| test | **217** | 244 | **88.93%** | = 论文 MiniF2F-test **88.9% pass@8192**（精确吻合）|
| valid | **221** | 244 | 90.57% | 论文未单列，量级一致 |
| 合计 | **438** | 488 | 89.75% | — |

- miniF2F v1 全集是 **244 valid + 244 test = 488**，不是 244；"244" 是**单 split** 标准数（常见误记）。
- 判定：该 zip = Prover-V2 在两个 split 上 pass@8192 解出的**全部题**（test 217 恰是 88.9%×244=216.9 的取整；valid 顺带全量放出）。未解出：test 27 题 + valid 23 题（多为 imosl/组合方向，本 zip 不含）。
- 147 与 zip 内任何切分都对不上（竞赛题域、行长阈值均试过），推测为上游任务误传。

## 2. 基础统计（全部脚本实算，可复跑）

```
find . -name '*.lean' | wc -l                          → 438
grep -rl ':= by' . | wc -l                             → 438  (Lean 4)
grep -rlE '^\s*begin\s*$' . | wc -l                    → 0    (零 Lean3)
grep -rl '^import Mathlib' . | wc -l                   → 438
grep -l 'set_option maxHeartbeats 0' -r . | wc -l      → 438  (统一去心跳上限)
grep -l '^/-- ' test/*.lean valid/*.lean | wc -l       → 438  (题面原文 docstring 全嵌)
```

| 指标 | valid (n=221) | test (n=217) |
|---|---|---|
| 行数 min/p25/med/p75/p90/max | 14/45/**61**/81/111/360 | 13/34/**60**/114/181/**2120** |
| 行数 mean | 69.6 | 97.7 |
| ≤30 行短解 | 24 | 42 |
| ≥200 行长解 | 5 | 17 |
| have 总数（均/文件） | 2977（13.5） | 6141（28.3） |
| `--` 注释（均/文件） | 2696（**12.2**） | 407（**1.9**） |
| 注释≥5 行文件 | **182/221 (82%)** | 35/217 (16%) |
| 零注释文件 | 15/221 (7%) | **118/217 (54%)** |

tactic 频率 top：`norm_num` 2655 / `linarith` 2549 / `exact` 1182 / `nlinarith` 1030 / `omega` 906 / `simp` 571 / `field_simp` 450 / `ring` 408——**算术归一化类占绝对主导**，与"子目标分解到单 tactic 可闭"的生成方式互为因果。

## 3. 抽样 5 题：两代风格分层（重要发现）

zip 混有**两种风格代际**，与 split 强相关（推断：valid 多为 3B 子目标冷启动链路带 CoT 注释版，test 多为 RL 阶段无注释版——风格证据充分，归属推断）：

**A. 子目标分解+注释风格**（valid 主力，如 `mathd_algebra_116.lean` 49 行）
- 结构 = 题面 docstring → 带参 theorem（h₀/h₁ 前提）→ 4-6 个 `have` 子目标 → 每个 tactic 前一行英文自然语言注释（"Substitute the given value…"/"Normalize the numbers…"）
- 冗余特征：h₂ 与 h₃ 命题完全相同、h₅:=h₄ 纯转抄——树搜索合并痕迹，非人类写法
- 瑕疵实证：`mathd_algebra_116.lean` 注释里有**中文残留"开孔"**（"multiplying through by开孔"），tokenizer/生成污染直接可见

**B. 无注释 RL 风格**（test 主力，如 `aime_1983_p2.lean` 57 行 0 注释）
- 同样是 have 链但零注释，节奏更紧；`<;> linarith`/`<;> norm_num` 组合高频
- 极端短解：`mathd_numbertheory_127.lean` 12 行，`have h : (∑ k in Finset.range 101, 2^k) % 7 = 3 := by rfl`——**靠 kernel 决定性计算直接_refl 过**，策略上"取巧"（非人类意图证明）

**C. 暴力展开型长解**（两 split 各有）
- `test/aime_1984_p7.lean`：**2119 行 / 574 have**，把递归 f(n)=f(f(n+5)) 从 1004 手工展开到 84，每 5 一档共 ~194 个机械 have（`have h₁₉₄ : f 84 = 997`）——**不用归纳法，纯步进展开**，pass@8192 预算下"算力换洞察"的典型
- `valid/aime_1987_p8.lean`：246 have，其中 ~100 个是 `have h₉₉ := h_bounds 96 255` 式**通用引理逐点实例化**（暴力枚举到 112）
- `test/imo_1992_p1.lean`：588 行 274 have，整数整除分类讨论，by_contra+linarith 密集

**vs 人类风格**：人类 Lean 解会用 `induction`/`decide`/引理引用收敛这种展开；模型解系统性偏向**去洞察化的机械分解**（每步一个简单 tactic、超大 have 链、宁可 2000 行不写一行归纳）。

## 4. 使用建议

1. **few-shot 语料**：按"目标题风格"取材——教模型分解用 valid（A 风格，注释=思维链，直接当 CoT- Lean 双轨样本）；追求可读产出用 test B 风格。建议先清洗：剔除 `rfl` 投机解（12-15 行那批）与中文残留文件。
2. **评测基准**：438 解本身就是 miniF2F 的**可复算 answer key**（全部 `set_option maxHeartbeats 0`，统一 Lean 4 + Mathlib + Aesop 头，可批量 `lake env lean` 复验 pass 状态——zip 不含编译输出，pass 证据=零 sorry + 论文口径吻合）。test 27 题+valid 23 题未解出清单 = 天然 hard-set。
3. **oprover-math skill 素材**：最有价值的不是解本身而是**风格统计先验**——norm_num/linarith 双塔占 47% 提示"先归一化再线性推理"是默认骨架；2119 行展开解证明 maxHeartbeats 0 + 机械分解在工程上合法，可作"卡题时降级策略"范例。
4. **风险提示**：冗余 have/注释污染说明**不能当黄金标准答案直接蒸馏**，需先做去重（h₂≡h₃ 类）与注释清洗；rfl 解不可作为"学证明"教材。

——统计脚本：`/tmp/mf2f_stats.py`（全量）、`/tmp/mf2f_pct.py`（百分位）、`/tmp/mf2f_style.py`（tactic/风格）；解包产物 `/tmp/minif2f-solutions/`。
