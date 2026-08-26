# RESUME-0826 · 讲透Loop 断点续传（✅ 单元完成态）

> 建单元：2026-08-26 | **状态：00-12 章全完成 + E1-E5 全跑通 + 挂网 6 处。本文件从断点转为完成档案 + 期权清单**

## 已完成 ✅

0. **第二轮（08-26 晚）**：
   - **03-验证的阶梯.md** 成文：验证不对称性物理学 + 五级阶梯（2607.07663）+ 累积漏检律 **p<ε/T**（理论 20.5% vs E2 实测 19.4%，偏差 1.1pp）+ Lean 零复利霸权 + 几何等待 1/p_leak + 四盆冷水（验证收费/gate≠goal/判官独立性稀缺/L5 形式化成本天花板）
   - **experiments/04_outer_loop.py** ✅ 跑通（E4 双相外环闭环）：
     - Phase A 诚实外环（reward=真成功率）3 代爬坡：A0 裸奔 {self,无K,无cap} 真成功 8.0% → 一次 trace 读出双补丁（升 machine+装 K8）→ A2 全守卫 53.3%（理论上限 66.7%=8/12 可解任务）；**R4 熔断过敏诊断**：正常任务误杀 19%>8% → 自动 K 8→14（42.8→53.3）
     - Phase B 污染外环（reward=claimed/tokens，"降本增效"接管）：一刀 machine→self，产出率 1.841→5.388 %/k（**+193%**），真成功 52.9→8.6%，早停 19.5→91.4%——**Goodhart 剪刀差铁证**
     - 诚实局限（写 Ch07 时要交代）：本模拟器 stall 计数器只见真实进展，**cap 防的"伪进展不收敛"（progress hacking 型卡死）无法在此表达**——这正是 cap 与熔断的本质分工：熔断防无进展，cap 防假进展
   - papers.md DeepVerifier 条目转正（ACL anthology 一手已核）

1. **README.md**：篇目表（00-12 目录宪法）+ 四层堆栈定位 + 三部曲分工表 + 一图流心智模型
2. **papers.md**：4 篇 arXiv（2607.00038 / 2608.21884 / 2607.13104 / 2607.07663）+ 7 篇灰色文献全核实（Osmani 命名文双版 / LangChain 四层 / DSD 10 模式 / vibeengines 四形状 / aipatternbook / eesel / Willison）
3. **00-从Prompt到Context到Loop.md**：命名史 + 控制权三次上交 + 内外循环之辨 + 验证中心论 + IMPROVE 算子预告 + 三盆冷水 + 练习
4. **experiments/01_loop_dynamics.py** ✅ 跑通（E1+E2）：
   - E2a：自评停止 87.3% 早停 vs 机器可查 80.7% 成功（漏检 1% 被轮数放大到 19.4%）
   - E2b：卡死 agent 场景"机器可查+无 cap"最贵 155k tok（等漏检出口 1/p_leak=100 轮）；熔断 K=8 止损 19k；**反直觉：自评的虚报反而是歪打正着的止损出口**
   - E2c：p_progress 扫描曲线（守卫价值在低 p 区最大）
5. **experiments/03_loop_shapes.py** ✅ 跑通（E3）：四形状 24h 蒙特卡洛——Heartbeat 无锁事故费 +37%（日均 13.9 次重叠）；Cron 最便宜 233k 但延迟一天；Hook 271k 性价比好；Goal 无上限 1550k = Hook 的 5.7 倍；**cap=25 形同虚设（P(超25轮)=0.13%）——cap 必须设在任务分布尾部之内**
6. **挂网 4 处**：讲透Agent 主README（生态表）/ MATH_LOOP_ENGINE §十（挂网清单）/ 讲透Context README（终章行）/ 讲透Prompt README（三部曲升维行）

## 已完成 ✅（终局清单）

7. **第三轮（08-26 深夜，一次性完成）**：01/02/04/05/06/07/08/09/10/11/12 全部落盘 + E5 跑通：
   - 01 内循环解剖：五阶段 + 三易混对象 + MDP 同构族（OODA/Kolb/RL/science）
   - 02 五件套：50-loop 语料（74/70/66 vs 22/20/32）+ 36,710 仓（0.59%/2 个 state file/6290 零命中）+ YAML 填写模板
   - 04 四形状：四定律（心跳固定税/无锁事故/延迟-线性权衡/goal 5.7 倍 + cap 远尾失准）+ 决策树
   - 05 三守卫：E2b 互补性 + **熔断防无进展 vs cap 防伪进展**（E4 局限的反向收获）+ 守卫税与 R4 退法 + 调参优先级
   - 06 外部状态：三规则（读帧写验/事实非vibes/resume一行）+ 2608.21884 缺口 + RESUME 模式自检（4/5 件套）
   - 07 loopcraft：四层塔 + E4 双相（A: 8.0→53.3% 三代收敛含熔断精调；B: +193%/-44pp 剪刀差）+ 堆叠三原则
   - 08 RSI：IMPROVE 算子统一表（Ralph→OPRO→AlphaProof→E4）+ 三类信号 + bounded vs open-ended + 三活体坐标 + 安全清单六条
   - 09 数学：Banach + E5 三演示——D1 步长分界（r<2 收敛；**慢收敛=预算内发散**新洞察 r=1.8）/ D2 遗忘地板 e*=f/(r+f) **0.2222 精确命中**（state file 的数学辩护）/ D3 E[T]=W/p 偏差 0.1%
   - 10 活案例：三活体五件套对号（MLE=教科书实现超语料均值；Prover=L5 bounded 标本；opencode=零件库）+ 完全体组装图（零件全齐未组装=经济判断）
   - 11 批判：四账（证据 0.59%/经济/认知/安全）+ 四理论空白（loop benchmark/reward 层级无定理/非平稳/多循环交互）+ 值不值得学的三条理由
   - 12 收官：12 问清单 + 三部曲总纲（四层塔一图 + 分工终表）+ 十定律速查 + 毕业练习

## 四、断点期权（下一波，不欠债）

1. **E6+ 真模型线**：模拟器结论在真 LLM 抽查复验（delegation 做 maker-checker 早停率实测）
2. **完全体组装**：schedule_job + RESUME + Lean 退出码的 Wave 4 自动版（10 章三节）
3. **上游反哺**：07 章外环思想回灌 MATH_LOOP_ENGINE（锚点轨迹自动分析→R1-R5 触发建议）
4. **三部曲合订导览页**（优先级低，减法优先）

## 环境与纪律备忘

- 模拟器实验纯 Python+numpy+matplotlib（Noto Sans CJK SC），无 GPU 依赖，`timeout 300` 内跑完
- arxiv.org abs 页本机不通：用 websearch 直抓 HTML 全文 + cs.SE 列表页交叉核实（本次 2608.21884 即此法）
- 待核实清单在 papers.md 末尾（swyx loopcraft 原文 / Steinberger 列表 / Anthropic 200+ 特征清单 / DeepVerifier ID）
- 脱敏：README/papers 已按公开仓规范（无内网路径/IP）
