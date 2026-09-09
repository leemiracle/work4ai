# 讲透 AI 产品经理（AI Product Manager）

> **AI PM = 在概率性系统上做产品决策的人。** 传统 PM 管理确定性系统（按钮点了就触发事件）；AI PM 管理概率性系统（模型 92% 的时候是对的，你的工作是让那 8% 不毁掉用户信任）。本系列从角色本质 → 产品形态 → 方法论 → 评估 → 设计 → 画像 → 社科 → 商业 → 能力模型 → 前沿，十个视角讲透这个 2024-2026 年 crystallize 的新工种，并交付一个可运行的 **AI 产品经理 Agent**（`.opencode/agent/ai-pm.md`）。
>
> 信息来源：2026 年一手调研（OpenAI/Anthropic/DeepMind 职位描述、institutepm/ODSC/Paraform 2026 行业报告、Microsoft AI-native 四态框架、MCP/Linux Foundation 2025-12 治理事实）+ 本仓库姊妹条目。数字均标注来源与日期。

## 一句话总纲

**AI PM = 经典 PM 手艺（discovery/优先级/利益相关者）× 概率性系统三新艺（eval 定义"好"、cost-quality-latency 三角定"位"、信任与降级设计定"险"）**——手艺可迁移，三新艺必须重学；不懂 eval 的 AI PM 等于不开灯开车。

## 篇目表（目录宪法）

| # | 标题 | 状态 | 核心 |
|---|------|------|------|
| **00** | [为什么需要 AI 产品经理](./00-为什么需要AI产品经理.md) | ✅ | 确定性→概率性世界观；两种角色（用 AI 的 PM vs 造 AI 产品的 PM）；角色为何 2024-2026 结晶 |
| **01** | [AI 产品形态全景](./01-AI产品形态全景.md) | ✅ | 形态光谱七类；chatbot→copilot→agent→digital employee 四级阶梯；AI-native 八层表面；形态决定 PM 工作 |
| **02** | [方法论武器库](./02-方法论武器库.md) | ✅ | 经典六器（JTBD/RICE/Kano/双钻/North Star/HEART）+ AI 特有五器（eval 门控/幻觉预算/数据需求/能力窗口/降级设计） |
| **03** | [评估驱动开发](./03-评估驱动开发.md) | ✅ | eval = AI PM 的 spec；离线 eval 集/rubric/LLM-as-judge；上线门槛；在线监控与漂移 |
| **04** | [概率性产品设计](./04-概率性产品设计.md) | ✅ | cost-quality-latency 三角；降级连续谱 UX；拒绝分类学；HITL 决策树；信任修复回路 |
| **05** | [用户与客户画像](./05-用户与客户画像.md) | ✅ | C 端/B 端/开发者三分法；B2B 采购中心六角色；技术采纳曲线与鸿沟；AI 产品的信任画像 |
| **06** | [管理学与社科视角](./06-管理学与社科视角.md) | ✅ | 八个社科镜头：委托代理/交易成本/创新扩散/颠覆性创新/行为经济学/组织变革/知识管理/算法管理 |
| **07** | [商业化与单位经济学](./07-商业化与单位经济学.md) | ✅ | token 经济学；per-seat 崩塌与四种新定价；毛利结构；数据/分发/信任三重壁垒 |
| **08** | [能力模型与工作流](./08-能力模型与工作流.md) | ✅ | 技能三环；一周工作流解剖；PRD-AI 版模板；转型路径与 2026 薪酬事实 |
| **09** | [前沿与展望](./09-前沿与展望.md) | ✅ | 2025-2026 前沿（agent 产品化/能力窗口/vibe coding 冲击）；AI PM 的反身性——被 AI 改造的 PM 岗位本身 |
| 🏛️ | [AGENT-OS.md](./AGENT-OS.md) | ✅ | **三 Agent 协作宪法**：五角色（CEO-Choose/PM-Shape/Domain-Translate/Code-Build/Validator-Measure）+ 三契约唯一定义（SC/PRC/DEC）+ 闭环流程 + 本仓落地映射（2026-09-04 二期） |
| 🤖 | [`ceo` Agent](../.opencode/agent/ceo.md) | ✅ | 领导 agent：10 工作流（战略/组合/资本/组织/风险…）+ 反 PM 权力（非局部最优决策器）+ 证据分级 + Decision Memory 落盘 |
| 🤖 | [`ai-pm` Agent](../.opencode/agent/ai-pm.md) | ✅ | Shape 层：11 工作流 + 上下游接口（收 SC/发 PRC/回 PIC）（一期 2026-09-04） |
| 🤖 | [`domain-expert` Agent](../.opencode/agent/domain-expert.md) | ✅ | 领域→代码专家：四层编译（L1意图→L2领域→L3技术→L4任务）+ 八模块 + **本仓领域知识路由表**（30+ 知识宇宙）+ DEC 契约编译器 |
| 🧪 | [`e2e/case-trustworthiness/`](./e2e/case-trustworthiness/) | ✅ | **全链闭环案例**（2026-09-04 完结，七件套）：SC→PRC→DEC 接力 + 接口检验（回流链 3 缺口→宪法 v1.1）+ **三 agent 行为一致性检验**（3/3 过，纪律指纹 4 条）+ T1-T5 仿真 Evidence（三门槛全过，HA 52% 主根因）+ CEO 闭环（invest_more，decision-log 回填）|
| 🧪 | [`experiments/`](./experiments/) | ✅ | 三个可运行实验：RICE 优先级计算器 / Kano 问卷模拟 / 成本-质量-延迟三角与单位经济 |

## 快速上手

```bash
cd experiments
python3 01_rice_priority.py     # RICE 优先级 + reach 诚实度敏感性分析
python3 02_kano_classify.py     # Kano 模型：问卷→分类（魅力/期望/必备/无差异/反向）
python3 03_cql_tradeoff.py      # 三档模型配置的成本-质量-延迟 Pareto 与毛利模拟
# 调用 AI PM agent：在 opencode 中 @ai-pm
```

## 关联条目

- [`讲透管理/`](../讲透管理/)——委托代理/机制设计/交易成本的数学内核（本系列 06 章的理论底座）
- [`讲透Agent/`](../讲透Agent/)——Agent 技术全栈（本系列 01 章形态学的工程实现）
- [`讲透Agent/Agent设计总纲-2026-08.md`](../讲透Agent/Agent设计总纲-2026-08.md)——本系列 agent 产品的设计宪法
- [`讲透模型/讲透模型宇宙/04-能力评估.md`](../讲透模型/04-能力评估.md)与[`讲透模型/讲透模型宇宙/05-选型决策.md`](../讲透模型/05-选型决策.md)——03/07 章的模型侧技术底座
- [`讲透AI应用全景/`](../讲透AI应用全景/)——AI 应用的域地图（本系列 01 章的垂直切片）
- [`讲透Prompt/`](../讲透Prompt/)——PM 也该会的 prompt 工程

---

📜 **本宇宙编辑史**：2026-09-04 由用户令创建（"参考已有资源、网络上 AI 产品形态、产品经理方法论、管理学社科知识、客户画像，讲透 AI 产品经理并生成 agent"）；同日二期：按用户 Agent OS 规划增建 ceo/domain-expert 两 agent + AGENT-OS 协作宪法（五角色三层编译闭环）。
