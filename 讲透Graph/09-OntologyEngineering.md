# 09 · Ontology Engineering：类型系统是产品

> 讲透Graph 第 09 章 ★用户重点 | 用到 E1 的 edge_index

## 1. 直觉层：本体是宪法，数据库是楼

vanja.io 的判词值得刻在每张图的开头：

> **graph engineering 不是"把数据放进 Neo4j"——数据库是实现，本体才是产品。** 烂本体装进贵图库，只是一堆标签贴错了的箱子，摆得更好看而已。

Ch01 讲了类型边的威力（$\log_2|\Sigma|$ bit/边）；本章讲它的代价面：**这套类型系统从哪来、谁来定、怎么不变烂**。综述 2608.21156 把 ontology engineering 列为系统智能的未来方向（§6）——图之间的互操作、共享语义层，全靠它。

**Prescribed vs learned**（Graphiti 的分类，工程上最实用的一刀）：

| | prescribed（前置规定） | learned（数据涌现） |
|---|---|---|
| 定义方式 | Pydantic 模型先声明实体类型/边类型 | 抽取时让结构自己长出来 |
| 优点 | 可校验、可治理、跨图一致 | 冷启动快、不怕漏设计 |
| 风险 | 设计过度/过时（没人敢删旧类型） | 类型漂移、同义类型增殖 |
| 适用 | 领域稳定、多系统互操作 | 探索期、单系统自用 |

务实路线是**两者混用**：核心实体（User/Doc/Decision）prescribed，长尾关系 learned，成熟一个收编一个。

## 2. POLE+O：五个类型的通用起手式

Neo4j 的 Create Context Graph 给了通用起始 schema——**POLE+O**：

- **P**erson（人：用户、审批者、agent 操作者）
- **O**bject（物：文档、工单、代码、产品）
- **L**ocation（位置：系统、环境、仓库、部门——广义"在哪"）
- **E**vent（事件：发生了什么——incident、部署、会话）
- **+O**rganization（组织：团队、公司、角色——谁归属谁）

为什么 5 类起手优于从零画：**事件（E）强迫你把"发生的事"与"存在的东西"分开**——这是 temporal 思维的入口（Event 天然带时间戳、天然连接 P/O/L）；Organization 把权限模型（谁能干什么）挂上图。设计原则不是"5 类是魔法数字"，而是"每类对应一个稳定的管理问题"。

## 3. 治理：让活图不变成 undead knowledge

三条铁律（Neo4j Berlin meetup + vanja.io 的合流）：

1. **矛盾在构建期解决，不留到推理期**（Yann Bilien）：两个数据源对同一政策说法不一，要在建图时调和完——扔给 LLM 在运行时仲裁 = 每次查询都重付仲裁费还可能来回变；
2. **agent 写的边 ≠ 人确认的边**：source / timestamp / confidence / review state 全部一等公民。没有这条，agent 的幻觉会污染知识库且**不可溯源清除**；
3. **建 context graph 首先是知识管理问题，不是工程问题**（Jessica Talisman）：decision traces 是知识不是数据，捕获它需要知识启发（elicitation）、形式化编码、本体——多数工程团队没在用这些学科。**先建知识模型，再建持久层。**

治理缺位的终局，vanja.io 给了名字：**undead knowledge**——活的、持久的、且不再连着真相。

## 4. 代码层：prescribed ontology 的最小实现

E1 的 `edge_index` 就是 prescribed 本体的骨架；工程化只差校验层：

```python
from pydantic import BaseModel

class Relation(BaseModel):
    src: str; dst: str
    type: Literal["supersedes", "depends_on", "caused", "blocks", "see_also"]
    source: Literal["human", "agent"]          # 治理铁律 2
    confidence: float; reviewed: bool = False

def add_edge(rel: Relation, graph: dict):
    assert NODE_TYPES[rel.src].allows(rel.type, NODE_TYPES[rel.dst])  # 类型校验
    if rel.source == "agent" and not rel.reviewed:
        mark_pending(rel)                        # agent 边进待审区
    ...
```

一个 linter（检查目标存在 + 边类型合法）+ 这层校验，就是"markdown 知识库 proto-graph"（→ Ch10）到"可治理图"的全部距离——不需要先买图数据库。**声音好的本体让日后迁移容易；烂本体只是分布式 nonsense。**

## 5. 不足与坑

- **本体腐化（ontology rot）**：类型系统没人维护就烂——新事实塞不进旧类型，大家开始乱标。症状监测：`untyped` 边占比、类型分布的熵漂移；
- **过度设计是默认结局**：第一版就画 30 个类型的团队，6 个月后没人记得类型的区别。从 POLE+O 起步，让 learned 收编；
- **跨图本体对齐**是未解难题：你的 `depends_on` 和我的 `depends_on` 不是一个东西——综述 §6 把它列为 graph-native OS 的前置障碍。

## 6. 与姊妹篇接口

- ← 讲透Skills：skill 的 frontmatter（card_id/universe/burke/status）就是 prescribed ontology 的 markdown 形态——本仓已经在做本体工程，只是没叫这个名字；
- → Ch10：AGENTS.md 的"卡片宪法" = 本仓的宪法层，E6 实测它的执行状况。

---

📌 下一步：Ch10 活案例——拿图论工具照 work4ai 自己。
✍️ 练习：给本仓写一个最小 POLE+O 映射：知识卡=Object？系列=Organization？commit=Event？——哪些现有的 markdown 约定（frontmatter/挂网）能直接当边？哪些边类型缺失（比如"替代了"哪张卡）？
