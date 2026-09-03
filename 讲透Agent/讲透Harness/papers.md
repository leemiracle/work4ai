# 讲透Harness · 引用与核实状态

> 宪法：**arXiv ID 绝不凭记忆**；本单元只引用下列已核实来源。核实方式与日期逐条标注。
> 最后更新：2026-08-26

## 一、学术线（全部一手核实）

| 引用 | 核实日期/方式 | 一句话 |
|---|---|---|
| Meng et al. 2026, preprints **202604.0428** | 2026-08-17 webfetch abs | 六组件 H=(E,T,C,S,L,V) + 23 系统 Completeness Matrix；order-of-magnitude 可靠性提升 |
| Li et al. 2026, OpenReview *Agent Harness Engineering: A Survey* | 2026-08-17 | 七层 ETCLOVG（Observability/Governance 独立成层） |
| Ning et al. 2026, arXiv:**2605.18747** | 2026-08-17 | Code as Agent Harness 三层（Interface/Mechanisms/Scaling） |
| Guo et al. 2026, arXiv:**2606.20683** | 2026-08-17 | model–harness 耦合六运行时责任 + **四范式演化**（prompt→context/workflow→harness→agent-native co-evolution） |
| AHE, arXiv:**2604.25850** | 2026-08-17 | 自动进化 harness：Terminal-Bench 2 69.7→77.0（+7.3pp 超人工 Codex 71.9%）；**消融：增益在 tools/middleware/长期记忆，system prompt-only 负收益**；跨模型 +2.3~+10.1pp（越弱获益越大）；同家族非单调（harness 超参对模型过拟合） |
| **Harness-Bench, arXiv:2605.27922** | **2026-08-26 websearch+abs 全文**（Qihoo360/harness-bench，2026-05-27） | 106 沙箱任务 × 6 可配置 harness × 8 模型 = 5194 轨迹；同模型池 harness 差距 **NanoBot 76.2 vs OpenClaw 52.4（23.8 分）**；Codex 80.4（参照）；**harness dependence：弱模型受 harness 影响更大**；失败症状：contract/format 36.4% / tool-recovery 24.6% / evidence 14.6%；主张**按 model–harness 配置报告能力** |
| Chen et al., arXiv:**2502.18036** (v6) | 2026-08-17 | LLM Ensemble 三阶段分类（before/during/after） |
| Chen Z. et al., TMLR 2024, arXiv:**2405.01769** | 2026-08-17 | FHL（金融/医疗/法律）领域 harnessing 综述 |
| HarnessCard / CAR, preprints **202603.1756** | 2026-08-17 | Control–Agency–Runtime 分解 + 结构化报告格式 |
| 行为定位 AHE 读路径搭档, arXiv:**2607.13285** | 2026-08-20 | L1/L2/L3+BGPD 行为地图（手册 13 章引用） |

## 二、工程线（官方/一手）

| 来源 | 核实日期 | 用在哪 |
|---|---|---|
| walkinglabs/learn-harness-engineering（11.4k★） | 2026-08-15 raw README 快照 | Ch01/02/06：五子系统、会话生命周期仪式、最小四文件、"模型够聪明 harness 让它可靠" |
| walkinglabs/awesome-harness-engineering（3.8k★） | 2026-08-15 | Ch10：40+ 基准按"测 harness 不测模型"筛选；Foundations 五支柱索引 |
| Anthropic《Effective harnesses for long-running agents》+ 续篇 | 2026-08-17（经 awesome 转述定位） | Ch04/06：initializer/feature list/init.sh/自验证/交接 |
| Arize 2026-04-28 四大 harness 参数分析 | 2026-08-17 | Ch07：Pi/OpenClaw/Claude Code/Letta 上下文参数趋同解 |
| $9 vs $200 对照实验 | walkinglabs 教程转述（**二手**，标注使用） | Ch01 动机（E1 是它的本地微型复现） |

## 三、论述性命名 → 已核实锚点映射（2026-08-26 用户论述整合）

用户 2026-08-26 论述中的概念名，其中 **Harness-Bench 已核实为真实实体**；其余为论述性命名，按下表映射到已核实锚点，**不为它们虚构引用**：

| 论述概念 | 状态 | 已核实对应物 |
|---|---|---|
| Harness-Bench | ✅ 真实实体 | arXiv:2605.27922（见上表） |
| Meta-Harness（生成 harness 的 harness） | 论述性命名 | Trellis spec 晋升循环（37 仓核实）；AHE 的"估→提取特征→优化→自动化"外环（手册 11 章） |
| Self-Harness（运行时自调） | 论述性命名 | AHE 三观测性支柱（运行时监控/干预）；Guo Phase 4 agent-native co-evolution；本仓 harness_rl v4 的 AHE 外环双靶迭代 |
| Evo-Harness（进化搜索优化 harness） | 论述性命名 | AHE arXiv:2604.25850 全文；**讲透Loop E4 双相外环**（本地已跑通：A0 8%→A2 53.3%，Goodhart 剪刀差） |
| SkillX / SkillOpt / SkillOps（技能库当工程对象） | 论述性命名 | 讲透Skills 六线全核实（MCE 2601.21557 / SkillRL 2602.08234 / MemSkill / Memento-Skills，2026-08-25 核实） |
| "隐式胶水→显式运行时→可优化对象"三阶段 | 论述性框架 | Guo 四范式演化（已核实）同构，作 Ch02/Ch12 主线 |
| Anthropic 长程 Harness | 概念成立 | Anthropic《Effective harnesses...》（官方博客）；渐进披露省 93.1% = 讲透Skills E2 实测 |

## 四、本单元实验数字（本机实测，非引用）

| 实验 | 日期 | 核心数字 |
|---|---|---|
| E1 naive vs harness | 2026-08-26 | 真实完成 4/6→5/6；naive FCR=true（自称 6/6 实际 4/6）；harness FCR 结构性 0；调用 2→8 |
| E2 验证器三级 | 2026-08-26 | V0 自评漏报 2/13（全集中在"看起来合理的代码"）；V1 拦 6/13（只语法层）零误杀；成本 V1≈0ms<V2≈3ms<<V0≈3862ms |
| E3 状态与失忆 | 2026-08-26 | 无账本=100%幻觉恢复；账本=信息充分但 0.5B 解析仅 1/3 全对（harness dependence 本地版）；meta 教训：解析器 bug 曾高估幻觉 |
| E4 预算守卫 | 2026-08-26 | 矛盾任务（magic(5)==10∧==12）3/3 条件零诚实放弃（IMPOSSIBLE 出口给了也不用）；cap=2 省 3× 调用 |
| E5 SELECT 代码化 | 2026-08-26 | ask_model 0%（3/3 全选已完成的 count_vowels）→ hybrid 100%（兜底 3/3 触发）→ code_select 100%（0 调用） |
| E6 验证即级联 | 2026-08-26 | glm-4-flash 全过 6 题 → cascade≡all_flash 成本（6 vs 120，1/20）零遗憾侧；升级路径 0 次触发（救回侧留 E6b，诚实标注） |
| E7 mini-Evo | 2026-08-26 | 贪心扫全空间（retries{0,1,2}×fb{raw,guided}）零收益（终配置=默认(1,raw)）；train 75% vs held-out 100%（难度方差主导）；gap=0 恒等（chosen==baseline）——小样本上配置搜索是伪命题，AHE 入场费=大任务池+冻结迁移+结构层 |
| 部署 e2e | 2026-08-26 | deepseek-agent-harness × zhipu glm-5.3 coding 通道：self-test 14+项全绿、probe 三门全过、真实修 bug 任务 6 步完成且人工复核为真；通道判定三环证据链（key 尾3KXf/端点含 /coding/ 段/差分 400） |
