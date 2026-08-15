# B-03 `open-spaced-repetition/fsrs4anki`（4K★）
> 克隆：C:\Users\mirac\AppData\Local\Temp\opencode\memory-clones\open-spaced-repetition__fsrs4anki（HEAD）
> JavaScript（Anki 自定义调度注入脚本）+ Python optimizer notebook（fsrs4anki_optimizer.ipynb / simulator.ipynb）+ archive/{candidate,experiment,research}
> 一句话定位：**人类记忆科学**的工程化——Free Spaced Repetition Scheduler 用 D/S/R 三变量状态 + 幂律遗忘曲线 + 检索即再巩固，把"何时复习"变成可优化问题；**与 Agent 记忆的 decay 机制互鉴是本篇重点**

调度器本体仅 375 行（`fsrs4anki_scheduler.js`，v6.1.1，头部 `set_version()` 写版本号 :1-2,319-325）；21 个参数 `w[0..20]` 由 optimizer 从**个人复习历史**用 ML 拟合（README.md:40"用机器学习学习你的记忆模式"）。另有 Qt5 变体 `fsrs4anki_scheduler_qt5.js` 平行维护。

## 1. 三变量记忆状态模型（对 Agent 记忆的直接馈赠）

| 变量 | 含义 | 值域/语义 | 代码位置 |
|---|---|---|---|
| D | Difficulty 难度 | [1,10]，越大越难学 | `next_difficulty`（scheduler:205-209） |
| S | Stability 稳定性 | 天数；**R 降到 90% 所需的间隔** | `init_stability`/`next_recall_stability`（:250-252, 213-222） |
| R | Retrievability 可提取性 | [0,1]，此刻还能想起来的概率 | `forgetting_curve`（:195-197） |

- 每张卡片（记忆条目）在 `customData` 里持久保存 `(d, s)`，且 **again/hard/good/easy 四个键位各存一份预计算状态**（`init_states`，:237-246）。
- 复习时先算当前 R，再按四种可能评分分别更新 S/D——**记忆条目是带状态的实体，不是带时间戳的日志**。

## 2. 核心公式深读（全部钉版 `fsrs4anki_scheduler.js` 行号）

### 2.1 幂律遗忘曲线（:97-98, 195-197）
```js
DECAY  = -w[20];                      // 幂指数
FACTOR = 0.9^(1/DECAY) - 1;           // 使 S 恰为 R=90% 的间隔
R(t, S) = (1 + FACTOR · t / S)^DECAY
```
- 不是指数衰减而是**幂律**（大量记忆实验支持：遗忘先快后慢、长尾）。
- FACTOR 的取法让 `S` 被校准为 R=90% 的间隔——**参数有语义锚点**，可解释、可迁移。
- 对 Agent：decay 函数应取 `R(t) = (1 + a·t/S)^{-b}` 形式而非 `e^{-λt}`；条目存 (S, D)，R 现算无需存储。

### 2.2 间隔 = 反解曲线到目标保留率（:198-201）
```js
I(S) = clamp( S/FACTOR · (requestRetention^{1/DECAY} − 1), 1, maximumInterval )
```
- `requestRetention`（推荐 0.75~0.95，:15）是**用户可控的成本旋钮**：愿意忘多少。低保留率 → 更长间隔 → 更少复习。
- `maximumInterval = 36500` 天（100 年上限，:16）。
- 对 Agent：记忆预算不该是"存多少条"，而应是"可容忍的检索失败率"——由它反推每条记忆的巩固周期。

### 2.3 成功检索后的稳定化（:213-222）
```
S' = S · (1 + e^{w8} · (11−D) · S^{−w9} · (e^{(1−R)·w10} − 1) · hardPenalty · easyBonus)
```
四个乘子的认知科学含义：
- `(11−D)`：越难的条目，回忆成功后涨得越多；
- `S^{−w9}`：**边际递减**——已稳定的条目再巩固收益小；
- `(e^{(1−R)·w10} − 1)`：**合意困难（desirable difficulty）**——在 R 低（快忘）时成功检索，S 增幅最大；R→1 时增幅→0；
- `hardPenalty/easyBonus`（w15/w16，:214-215）：评分的修正项。
- 对 Agent：检索命中时的元数据更新应按此**非线性加权**——在快遗忘时命中的记忆强化最大，而非简单 touch `updated_at`。

### 2.4 遗忘后的重建（:223-229）
```
S'new = min( w11 · D^{−w12} · ((S+1)^{w13} − 1) · e^{(1−R)·w14},  S / e^{w17·w18} )
```
- 新稳定性与旧 S 弱相关（幂次 w13<1），由 D 主导——"忘了的难点从头学起"；
- **上界钳制** `S/e^{w17·w18}`：重学收益不得超过旧稳定性的固定比例，防"反复遗忘-重学"刷高稳定性。
- 对 Agent：记忆失效后重建（重新抽取、重新验证）不应完全清零历史——**弱相关 + 有上界的延续**是稳妥设计。

### 2.5 同日短期稳定性（:230-236）
- `S' = S · e^{w17(r−3+w18)} · S^{−w19}`，且 r≥3（good/easy）时增幅下限为 1（不退步）。
- 短时重复接触与长期复习**分用两套动力学**——对应 Agent：会话内的重复提及与会话间的重访，巩固权重应不同。

### 2.6 难度更新：线性阻尼 + 均值回归（:202-212）
```
ΔD = −w6·(rating−3) · (10−D)/9        // 阻尼：D 近上限时单次变化变小
D' = w7·D_init + (1−w7)·D             // 均值回归：向初始难度拉回
```
- **估计量长期有界不漂移**：Agent 记忆里任何持续累加的元数据（重要度、置信度、访问计数）都应有同款回归项。

### 2.7 初始化与迁移
- 初始稳定性：`S0 = w[rating−1]`（w0..w3 对应首评 again/hard/good/easy，:250-252）；
- 初始难度：`D0 = w4 − e^{w5(r−1)} + 1`（:247-249）；
- **SM-2 迁移**：旧调度器状态（scheduledDays + easeFactor）换算成 (S,D)（`convert_states`，:253-266）——记忆系统升级要带状态迁移路径。

### 2.8 工程细节同样可迁移
- **四键位全预计算 + 单调约束**：四档反应的 next (d,s) 提前算好（:124-177），间隔满足 hard≤good≤easy（:166-168）——一次评估，多档决策，且约束显式。
- **fuzz 防共振**：间隔加 ±5% 随机扰动，**种子取自卡片内容**（seedrandom，:41-43, 182-194, 346-375）——同批卡片不会永远同天到期把队列打尖；Agent 巩固调度同样需要 jitter 去同步。
- **按牌组参数化**：最长前缀匹配选参数组（:76-93），`skip_decks` 白名单关闭（:37-39）——不同领域/来源的记忆用不同 decay 参数组。
- 参数语义总表：w0-w3 初始 S；w4-w5 初始 D；w6-w7 难度动力学；w8-w10 成功稳定化；w11-w14 遗忘重建；w15-w16 评分修正；w17-w19 短期；w20 幂指数。
- 版本号随状态走（customData.again.v 等，:319-325）——**状态迁移的版本对齐**（呼应 B04 符号表、B12 格式版本）。

### 2.9 一个数值自检（说明 S 的语义锚点）
- 取默认参数：`w20 = 0.1542` → `DECAY = -0.1542`，`FACTOR = 0.9^(1/DECAY) − 1 ≈ 0.980`；
- 当 `requestRetention = 0.9` 时：`I(S) = S/FACTOR · (0.9^(1/DECAY) − 1) = S/FACTOR · FACTOR = S`（整）。
- 即**默认配置下复习间隔恰好等于稳定性**——S 被构造性地定义为"R 衰减到 90% 的天数"，公式自洽；
- 若用户把 requestRetention 调低到 0.8，间隔放大约 `S·(0.8^{−6.49}−1)/FACTOR ≈ 3.3S`——同样一批卡片，容忍更低保留率 → 间隔拉长 3 倍 → 复习量骤降。这个"旋钮→间隔"的解析关系就是记忆预算的数学形态。

### 2.10 调用链全景（一张卡的完整生命周期）
```
新卡:   is_new() → init_states()（四键位各得初始 (d,s)）→ next_interval(s)
学习卡: is_learning() → next_short_term_stability(s, rating)（同日动力学）
复习卡: is_review()
  ├─ 无状态(旧卡): convert_states() 从 SM-2 (interval, easeFactor) 换算 (s,d)
  ├─ R = forgetting_curve(elapsedDays, last_s)
  ├─ 四键位预计算: next_difficulty / next_recall_stability / next_forget_stability
  ├─ 间隔单调约束: hard ≤ good ≤ easy（:166-168）
  └─ 写回 customData.*.{d,s,v,seed}（v=算法版本，seed=fuzz 种子链）
```

## 3. 与 Agent 记忆 decay 机制的对位互鉴（本篇重点）

| Agent 记忆问题 | FSRS 现成答案 |
|---|---|
| 该给记忆条目存什么元数据 | `(D, S, last_review_t)` 三件套；R 永远现算不存 |
| 用什么衰减函数 | 幂律 `(1+a·t/S)^{-DECAY}`，非指数 |
| 何时触发巩固/重放 | R 跌到阈值时——按条目独立调度，而非全局定时任务 |
| 检索命中时如何更新 | 收益 ∝ f(1−R)：越接近遗忘的命中强化越大；已熟条目少动 |
| 允许遗忘多少 | requestRetention 作为预算旋钮，反解巩固周期 |
| 重要性估计会不会漂移 | 均值回归项保证有界 |
| 批量调度共振 | 内容种子化 fuzz |
| 参数怎么来 | 从系统自身交互历史在线拟合（optimizer notebook） |
| 系统升级旧数据怎么办 | convert_states 状态迁移 + 状态内版本号 |

**反向馈赠（Agent → FSRS）**：
- Agent 的"检索"是向量召回 + LLM 使用，没有人类的"回忆失败"显式信号；
- 可把"**检索未命中但事后证明该记忆存在且相关**"（后续对话回补了该事实）当作遗忘事件，喂给同类更新公式——Agent 日志天然带这类监督信号，人类复习数据反而没有。

## 4. 局限（含算法演化注记）
- 模型拟合的是人类记忆实验数据；Agent 检索的成本结构与人类回忆不同（检索便宜、无主观费力感），desirable difficulty 的最优工作点必然不同。
- **条目独立建模，无语义关联/干扰建模**：相似记忆互相干扰（interference）只能通过 D 间接体现；Agent 记忆的去重/冲突恰发生在这一层，FSRS 帮不上。
- 参数需重训且对数据量有要求（官方建议 ≥1000 条复习记录再优化）；人的记忆特性会漂移。
- 算法演化注记：仓库 `archive/{candidate, experiment, research}` 保留了 FSRS-4→5→6 的公式演化史料（v6 相对早期版本的主要变化：稳定性更新公式引入 `S^{-w9}` 边际递减与 `(11−D)` 难度耦合、短期/长期稳定性分轨、fuzz 改为内容种子化）——**decay 模型本身也要版本化演进**。
- v6 调度器是 Anki 注入脚本形态，泛化使用应引用同组织的 py-fsrs / ts-fsrs / go-fsrs 库实现。
