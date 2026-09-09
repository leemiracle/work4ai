# LLM × 社会 · 用 AI Agent 仿真整个小型社会

> **结合子领域**：全部（这是终极的"跨子领域"）
> **配套工程**：`agent-guide/` 项目（用户已完成的 LLM Agent 课程）+ `projects/p5-llm-society/`
> **配套 CSSCI**：检索"大模型 + 社会科学"、"人工智能 + 社会仿真"

---

## 1. 为什么这是社会科学的革命

2023 年 4 月，Stanford 的 Joon Sung Park 等人在 arXiv 发表《Generative Agents: Interactive Simulacra of Human Behavior》（arXiv:2304.03442）。

他们做了什么：
- 在沙盒小镇 Smallville 里放了 **25 个 LLM agent**
- 每个 agent 有：身份、记忆、计划、社交关系
- agent 之间可以交流、互动、累积记忆
- **跑下去**，自发涌现出：
  - **情人节派对**（一个 agent 想办派对 → 邀请朋友 → 朋友邀请朋友 → 25 人中有 20 人到场）
  - **意见领袖**（某些 agent 比其他人更影响决策）
  - **小团体**（按共同兴趣形成）
  - **信息差**（同一事件不同 agent 知道的信息不同）

这是社会科学第一次有了**真正的"实验室"**——
- 物理学有粒子加速器
- 生物有湿实验室
- 社会科学……以前只能靠问卷调查 + 自然实验
- 现在：**LLM agent 沙盒 = 社会实验室**

---

## 2. 为什么这是"并结合子领域"的极致

LLM × 社会的研究**必然涉及本项目所有子领域**：

| 子领域 | LLM 仿真里的体现 |
|---|---|
| relations | agent 之间的社交网络自发生成 |
| cooperation | agent 自发合作 / 背叛 |
| inequality | 资源分配不均涌现 |
| power-politics | 意见领袖 / 投票 / 抗争 |
| culture-cognition | 信息扩散 / 观点动力学 |
| markets-cities | 经济交换 / 空间聚集 |

→ 一个 LLM agent 社会仿真，可以同时验证 6 个子领域的理论。

---

## 3. 三代 LLM 社会仿真

### 第一代（2023）：Smallville 原型
- Park et al. 2023, Generative Agents
- 25 agents，静态小镇，2 天仿真
- 涌现：派对、社团、信息传播

### 第二代（2024）：大规模社会
- **Project Sid**（altera.al）：1000+ agent 在 Minecraft 跑社会实验
- 出现：经济系统、宗教、政府、文化
- arXiv 检索：Project Sid

- **Concordia**（DeepMind）：开源 LLM 社会仿真框架
- GitHub: google-deepmind/concordia

### 第三代（2025-2026）：多模态 + 现实校准
- agent 不只文本，还有图像/语音
- 与真实数据对齐：用 Twitter/微博数据校准 agent 行为
- AI Town（a16z）：开源 Smallville 实现

---

## 4. 关键技术（与 agent-guide 项目对接）

LLM agent 社会仿真需要：

### 4.1 Agent 架构
- **Memory**：记忆流（Park 等的"记忆-反思-计划"架构）
- **Planning**：每日计划 → 每小时调整
- **Reflection**：定期从记忆中抽象出"信念"
- **Action**：自然语言行动 → 环境更新

参考你的 `agent-guide/04-memory/` 和 `05-planning/`。

### 4.2 环境架构
- 空间（家、咖啡馆、公园）
- 物品（家具、食物、书）
- 其他 agent

### 4.3 LLM 调用
- 推荐用 **GLM-4.6 或 glm-4-flash**（参考你的 `glm52-access` 经验）
- 频繁调用要控制成本（你已知道 glm-4-flash 比 glm-4.6 快 13 倍）
- 每个 agent 每次决策 1 次调用
- 25 agent × 24 小时 × 每小时 3 决策 = 1800 调用/天

### 4.4 评估
- 涌现指标：网络中心性、信息熵、社会流动
- 对比指标：和真实社会数据对比
- LLM-as-judge：用 LLM 评估 agent 行为合理性

---

## 5. 推荐动手项目：5-agent Smallville

参考你已完成的 `agent-guide/project3-content-factory`（3-agent 内容工厂）。

### 目标
跑一个 5-agent 的小型社会，验证：
- Granovetter 弱连带（模块 1）
- Nowak 合作演化（模块 2）
- Kuran 革命相变（模块 4）
- HK 观点动力学（模块 5）

### 实现步骤（用 GLM-5.2 / glm-4-flash）

```python
# 伪代码框架
from agent_guide_common.config import get_glm_client

class Agent:
    def __init__(self, name, personality):
        self.name = name
        self.personality = personality
        self.memory = []  # 记忆流
        self.relationships = {}  # 与其他 agent 的关系
        self.opinions = {}  # 对各议题的观点
    
    def perceive(self, environment):
        """感知环境，写入记忆"""
        ...
    
    def reflect(self):
        """从记忆中抽象出信念"""
        ...
    
    def plan(self):
        """制定下一步行动"""
        ...
    
    def act(self, environment, other_agents):
        """执行行动，可能影响其他 agent"""
        ...

class Society:
    def __init__(self, agents):
        self.agents = agents
        self.environment = {}
        self.history = []
    
    def step(self):
        for agent in self.agents:
            agent.perceive(self.environment)
        for agent in self.agents:
            agent.reflect()
        for agent in self.agents:
            action = agent.plan()
            agent.act(self.environment, self.agents)
        self.history.append(self.snapshot())
    
    def run(self, n_steps):
        for _ in range(n_steps):
            self.step()

# 配置 5 个 agent
agents = [
    Agent("Alice", "外向、健谈、关心政治"),
    Agent("Bob", "内向、技术宅、不关心政治"),
    Agent("Carol", "意见领袖、社交媒体达人"),
    Agent("Dave", "保守、信仰坚定、家庭至上"),
    Agent("Eve", "激进、年轻、渴望改变"),
]

society = Society(agents)
society.run(n_steps=100)  # 跑 100 步

# 分析：网络中心性、合作率、观点演化
```

### 实际工程参考
- 你的 `agent-guide/07-multi-agent/` 已经有双 Agent 协作的实现
- 升级到 5 个 agent，加记忆和反思机制

---

## 6. CSSCI 配套研究

### NCPSSD 检索关键词
- "大模型" + "社会科学"
- "人工智能" + "社会仿真"
- "生成式 AI" + "社会治理"
- "LLM" + "社会实验"

### 中国相关研究

**段伟文（中国社科院哲学所）**：
- AI 伦理、数据伦理
- 与 Floridi/O'Neil 对话

**国内 LLM 社会仿真团队**：
- 复旦 NLP 团队（邱锡鹏等）
- 清华 KEG（唐杰等，已做 GLM 系列）
- 智谱 AI（GLM 团队，本项目用的就是他们的 API）

**中国 LLM 社会研究 = 本项目的工程基础**：
- 你的 agent-guide 项目已经用智谱 GLM 完成 3-agent 内容工厂
- 升级到 5-agent 社会仿真是自然延伸
- 这是中国本土 LLM 应用的特色——可以用中文跑中国社会仿真

---

## 7. 批判：LLM 仿真能取代真实社会科学吗？

### 反对意见

**1. LLM agent ≠ 真实人**
- LLM 是分布的"压缩"，不是有真实需求/情感的个体
- 它的行为是"统计意义上的可能"，不是"必然"

**2. 训练数据偏倚**
- LLM 训练于人类文本 → 仿真就是"仿真仿真"
- 不可逃避的循环

**3. 成本与可重复性**
- 跑一次 1000-agent 仿真 = 上万美元 API 费用
- 难以学术复现

**4. 解释性差**
- 涌现发生了，但"为什么"难解释
- LLM 是黑盒

### 支持意见

**1. ABM 一直如此**
- 传统 ABM 也是"仿真"，LLM 只是更精细
- 仿真目的是**启发理论**，不是预测

**2. 新假设生成器**
- LLM 仿真可以发现新的社会机制
- 然后用真实数据验证

**3. 政策沙盒**
- 在 LLM 社会里试政策（如 UBI、税收）
- 看涌现效应，再决定是否在真实社会试点

---

## 8. 推荐文献

### 必读 ⭐
- Park, J.S. et al. (2023). *Generative Agents.* arXiv:2304.03442
- Park, J.S. et al. (2023). *Social Simulacra.* UIST.
- Horton (2023). *Homo Silicus.* NBER WP.

### 进阶
- Project Sid (2024). arXiv.
- Concordia (DeepMind, 2023). GitHub.
- Argyle et al. (2023). *Out of One, Many.* Political Analysis.

### 中文配套
- 段伟文：AI 伦理
- 邱锡鹏：自然语言处理
- 周涛（电子科大）：复杂网络 + LLM

---

## 9. 与本项目其他模块的交叉实验

完成本专题后，可以设计**跨模块实验**：

### 实验 A：Schelling × LLM
- 把 Schelling 模型的 agent 换成 LLM
- 让 LLM agent 决定是否搬家（基于"自然语言理由"）
- 看是否涌现隔离？

### 实验 B：Axelrod × LLM
- 跑 LLM 锦标赛，让不同 prompt 的 LLM 互相对抗
- 看哪种 prompt 表现像 TIT-for-TAT？

### 实验 C：Kuran × LLM
- 仿真 LLM agent 在"政治压力"下的双重偏好
- 看是否能跑出"革命相变"？

### 实验 D：Piketty × LLM
- 让 LLM agent 进行经济交换
- 看财富分布是否涌现帕累托？

---

## ✍️ 思考题

1. 用 LLM 仿真一个 5-agent 小社会，最难的工程问题是什么？
2. LLM 仿真发现的"涌现"，能用真实数据验证吗？
3. 如果让你设计"AI 议会"，agent 怎么配置？投票规则怎么定？
4. LLM 仿真会取代问卷调查吗？哪些场景能 / 不能？
5. **挑战**：把 `agent-guide/project3-content-factory` 升级为 5-agent 社会仿真。

---

*下一专题：[`cities-case.md`](cities-case.md) — 城市规模法则的深度案例研究*
