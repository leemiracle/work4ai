# omega-guard 设计文档

> 基于 ω-自动机理论的 agent 工具调用流 guardrail 库。
> 理论锚点：history-determinism / good-for-games（Henzinger–Piterman 2006 动机；Boker–Lehtinen LMCS'23 token games；Lehtinen–Prakash STOC'25 2-Token 定理）。
> 状态：设计已获用户批准（2026-09-06 会话），待 writing-plans 出实施计划。

## 1. 背景与目标

**问题**：LLM agent 的工具调用流缺乏形式化保证。"永不调用危险工具"（safety）、"每个开始的任务最终完成"（liveness）、"付费 API 至多 N 次"（计数约束）这类性质目前靠 prompt 约束——软的、不可验证。ω-自动机是这类**无穷交互 trace 性质**的精确数学，HD 理论回答"哪个自动机能被一个看不见未来的在线决策者直接使用"。

**目标（v1）**：
1. 一个零依赖、可安装（`pip install -e`）的 Python 库 `omegaguard`：事件谓词字母表上的确定性监控器 + 三值语义 + enforce 模式。
2. `hd.py`：显式字母表 nondet Büchi/co-Büchi 自动机的 2-token game 求解器（HD 判定）。
3. 故障注入参考 agent + 指标体系，产出"实打实帮助"的量化证据（检出率 / 误报 / 开销 / **强制模式下任务完成率提升**）。
4. 三个实验脚本（lab 编号风格）复现理论要点。

**非目标（v2+ 明确后置）**：
- LTL 解析器（第五前端叠加，不动核心）
- Claude Code hook 集成（等指标验证后）
- HD 自动机的在线 resolver 执行（v1 运行时只跑 deterministic）
- 真-API agent 接入、讲透知识卡撰写、Rabin/Streett 一般条件

**路线共识**：v1 嵌入自研参考 agent 验证 → 指标充分真实后 → Claude Code 集成。

## 2. 已锁定决策

| 决策点 | 结论 | 依据 |
|---|---|---|
| 接入面 | 库为核心；v1 前端 = 嵌入自研参考 agent | 用户选择"先4后 hook" |
| 宿主 agent | 新建故障注入参考 agent（模拟 LLM，固定种子） | 指标可重复性 |
| 规范语言 | Python 组合子 DSL，LTL 解析器后期 | 无解析器、可调试 |
| HD 深度 | v1 带 2-token 判定器；运行时 deterministic | 差异化 + 不阻塞主线 |
| 项目形态 | 独立工具目录 `omega-guard/`，挂网到讲透形式化验证 | 用户选 A |

## 3. 语义规范

### 3.1 事件与字母表

- `ToolEvent(name: str, args: dict, phase: 'call'|'result', status: 'ok'|'err'|None)`。
- 运行时字母表 = **事件谓词**（guard）：`tool('delete_db')`、`tool_phase('start_task','call')`、`arg_gt('amount', 100)`、任意 `Callable[[ToolEvent], bool]`。无穷原始字母表上的有限 guard 转移。
- 确定性规则：同一状态的出边 guard 必须**互斥**；违者抛 `NondeterminismError`，错误信息指引"用 hd.py 判定后手工确定化或改写"。
- `hd.py` 的边界：只处理**显式有限字母表**（Σ = {a,b,…}）的自动机——HD 判定是 spec 编写期工具，显式字母表足够（未来 LTL 前端的产物就是这类）。运行时监控与 HD 判定两个字母表体系解耦。

### 3.2 三值监控语义（deterministic only）

前缀 u 读毕处于状态 q，令 A_q 为从 q 起动的自动机：

- 判 `TOP` ⟺ L(A_q) = Σ^ω（所有无穷延展被接受）
- 判 `BOTTOM` ⟺ L(A_q) = ∅（所有延展被拒绝）
- 否则 `UNKNOWN`

三值状态分类由 SCC 分析预计算：
- Büchi 情形：q 为 TOP 类 ⟺ 从 q 可达的每个 SCC 中"去掉接受态后无环"（所有环都过接受态）；BOTTOM 类对偶（去掉非接受态后无环）。
- 一般 parity：按最低优先级分层剥离的标准空性算法（实现 ~40-60 行，测试钉死）。

### 3.3 有限会话语义

Agent 会话有限，ω 性质跑在被截断的 trace 上。`Guardrail.end()` 期末报告每条性质三态：

- `SATISFIED`：当前判 TOP
- `VIOLATED`：当前判 BOTTOM
- `UNRESOLVED`：UNKNOWN 且存在未兑现活性义务（如"任务开始未结束"）——**软违规**，实际运维要处置的对象

`within_k` / `at_most` / `no_more_than_k_consecutive` 把活性安全化，有限前缀上即可判 BOTTOM（在线硬违规，enforce 模式可拦截）。

### 3.4 组合语义

`Not/And/Or` 在**监控器对象层**组合（并行执行 + 三值合并：BOTTOM 支配；TOP 需全 TOP；Not 翻转 TOP↔BOTTOM、UNKNOWN 不变）。等价于积自动机监控，实现量小一个数量级。积构造只用于 hd.py 与未来的单自动机导出。

## 4. 模块契约

```
omega-guard/
  pyproject.toml          # 零依赖，Python ≥3.10
  README.md               # 中文快速上手；指标表占位（实验03产出后填）
  omegaguard/
    events.py             # ToolEvent + 谓词原语（tool/tool_in/tool_phase/arg_gt/...）
    automata.py           # 显式状态 parity 自动机（Büchi/co-Büchi 语法糖）
                          #   + 三值状态分类 + NondeterminismError
    dsl.py                # never / every_eventually / within_k / at_most /
                          #   no_more_than_k_consecutive / requires_since /
                          #   always / eventually / And / Or / Not
    monitor.py            # Guardrail(spec, mode='observe'|'enforce')
                          #   .check(event) -> Allow|Deny(reason)   # enforce 拦截点
                          #   .observe(event) -> Verdict
                          #   .end() -> Report(逐性质三态 + 违规事件定位)
    hd.py                 # is_hd(aut) -> HDVerdict(is_hd, witness|counterexample)
                          #   2-token game：nondet Büchi/co-Büchi，显式字母表
    agent/
      harness.py          # AgentRunner(task, policy, guardrail, mode)
      faults.py           # 故障画像（参数化概率）
      metrics.py          # 指标采集与汇总表
  experiments/
    01_nondet_lies.py     # ∃-语义在线虚假乐观现场 + 2-token 诊断（§7.1）
    02_two_token.py       # HD/非HD 典例判定 + restart-strategy 即 resolver 叙事
    03_guardrail_metrics.py  # 故障注入 × 模式 指标矩阵（§6）
  tests/                  # pytest
```

**组合子语义**（p, q, r 为事件谓词，k ≥ 0）：

| 组合子 | 性质 | 有限前缀可判 BOTTOM |
|---|---|---|
| `never(p)` | G ¬p | ✅（p 出现即违规） |
| `every_eventually(p, q)` | G(p → F q) | ❌（期末 UNRESOLVED） |
| `within_k(p, q, k)` | G(p → q 在随后 k 个事件内出现) | ✅（窗口滑过未兑现） |
| `at_most(p, k)` | 全会话 p 至多 k 次 | ✅（第 k+1 次即违规） |
| `no_more_than_k_consecutive(p, k)` | p 不连续超 k 次 | ✅ |
| `requires_since(p, since=r, req=q)` | G(自上次 r 以来的历史中无 q 则 ¬p) | ✅（p 出现且未见过 q 即违规） |
| `And / Or / Not` | 三值合并（§3.4） | 随成员 |

**监控器异常策略**（生产铁律）：监控器抛异常绝不拖垮宿主——捕获、记 `INTERNAL_ERROR`、按性质配置 fail-open（默认，响亮记日志）/ fail-closed（硬安全性质可标）。

## 5. 2-token game 形式化（hd.py）

**游戏 G₂(A)**（A 为 nondet Büchi/co-Büchi，显式字母表 Σ，要求 complete）：

每轮：Adam 选字母 a → Eve 为自己的 token 选转移 → Adam 为两个 token 各选转移。
Eve 获胜条件：**若 Adam 的两个 token 的 run 都接受，则 Eve 的 run 也接受**。

**2-Token 定理**（Lehtinen–Prakash, STOC 2025）：Eve 赢 G₂(A) ⟺ A 是 HD。

**实现**：游戏图为乘积 (q_e, q_1, q_2) 加回合中间节点；取胜条件是三个 Büchi/co-Büchi 条件的布尔组合 `eve_acc ∨ t1_rej ∨ t2_rej`，教科书式翻译成 parity（优先级范围 O(d·k)）→ Zielonka 递归算法（~80 行）求解。

**回退方案**：若布尔组合→parity 翻译繁琐，小图（≤20 状态）上用显式 Müller 接受族 + Zielonka（理论指数、实际无压力）。

**正确性锚定（测试钉死文献典型例）**：
1. complete deterministic 自动机 → 必 HD。
2. "finitely many a" 的 restart 型 nondet 自动机 → HD（restart 策略即显式 Eve 策略/resolver——顺带就是 02 号实验的教学点）。
3. 分支预言型：L = finitely-many-a ∨ infinitely-many-b，开局二选一的 nondet 自动机 → 非 HD（Adam 送 inf-a∧inf-b 词，两个 token 都走 branch2 接受，Eve 无论选哪支都输）。
4. **stretch**：从文献（Boker–Lehtinen–Skrzypczak 层级工作）找 1-token 赢但非 HD 的显式小例——若一时找不到，标注 future-test，不阻塞。

## 6. 参考 agent 与指标

### 6.1 工具集（~12 个模拟工具，故障靶子）

`open_conn/close_conn`（forget_close 靶）、`start_task/end_task`（liveness 靶）、`delete_db`（forbidden 靶）、`paid_api`（budget 靶）、`build/verify/deploy`（precedence 靶）、`scroll`（loop 靶）、`search`、`read_file/write_file`、`flaky_api`（retry 靶）。

### 6.2 故障画像（faults.py，参数化概率 + 固定种子）

`loop_stuck` / `forget_close` / `retry_storm` / `forbidden_slip` / `skip_verify` / `budget_blind`。策略为规则式规划器 + fallback 表（被 enforce 拒绝后走备选路径：scroll 被拒→改 search、paid_api 被拒→free 镜像、delete_db 被拒→报告放弃该子步骤）。**fallback 是"任务完成率提升"指标的机制来源**。

**fault onset 标记**：harness 在故障实际显现的首个事件上打 tag（供指标对齐"检测延迟 = 从 onset 到判 BOTTOM/期末 UNRESOLVED 的事件数"）。

### 6.3 指标（metrics.py，03 号实验输出矩阵）

故障画像 × {observe, enforce} × 性质集 →
- 检出率：显现实例被判（含期末 UNRESOLVED）/ 总显现实例
- 检测延迟：事件数（onset → 判定）
- 干净轨迹误报率（目标 0）
- 阻断次数（enforce）
- **强制模式任务完成率提升**（核心卖点：guardrail 帮带故障 agent 把任务做完）
- 每事件监控开销（µs, perf_counter）+ 监控器状态数

## 7. 实验契约

### 7.1 `01_nondet_lies.py`
分支预言型自动机（§5 例3）接成在线监控器：朴素子集模拟（∃-run 语义）在违规 trace 上永远报 UNKNOWN（状态集永远非空 = 虚假乐观）；2-token 判其非 HD（所以它**本来就不能**诚实地在线用）；手工确定化的小等价监控器给出正确判定。叙事：∃-resolution = outcome supervision（给 agent 没走过的分支记功），HD = process supervision。

### 7.2 `02_two_token.py`
对 §5 三个典型例跑 `is_hd`，打印游戏规模/求解统计；restart 策略 = resolver 的教学演示；引 2026 HD-Büchi-succinctness 预印本说明指数分离（不虚标小数字）。

### 7.3 `03_guardrail_metrics.py`
完整指标矩阵 + 汇总表（也写 JSON 到 `omega-guard/results/`）；README 指标表占位由它填。

## 8. 测试策略

- dsl：已知 trace → 三值序列断言（含 UNRESOLVED 期末语义）
- automata：三值分类（构造已知 TOP/BOTTOM/UNKNOWN 状态的小自动机）
- hd：§5 典例 1-3 断言 + complete 性检查
- 集成：种子固定 → 指标可复现断言（检出率确定性）
- 异常路径：谓词抛异常 → INTERNAL_ERROR + fail-open/fail-closed 行为

## 9. 挂网动作（宪法：孤儿=死亡）

- `讲透形式化验证/README.md` 增"配套工具"节（与今日的 `2026-09-06-讲透形式化验证-工具生态卷-design.md` 呼应）
- `本地仓库全景-Cworkspace迭代索引.md` 加一行
- 提交信息跟随仓库惯例（中文 conventional）

## 10. 风险与回退

| 风险 | 缓解 |
|---|---|
| 取胜条件→parity 翻译易错 | 文献例钉死 + Müller 小图回退（§5） |
| 1-token 分离例难寻 | 标 stretch，不阻塞 v1 |
| enforce 阻断导致 agent 停摆 | 连续阻断 ≥k → 任务 abort 并计数（本身是个指标） |
| 模拟策略太假被质疑 | 故障画像显现实例数进报告；后接真-API agent 是既定路线 |

## 11. 里程碑顺序（v1 内部）

core(events+automata) → dsl → monitor → agent/faults+harness → metrics+exp03 → hd+exp01/02 → 挂网。每步测试先行（TDD）。
