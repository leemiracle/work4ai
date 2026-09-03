# 03 · Context Graph：把知识建成图（GraphRAG → Graphiti、bi-temporal、作废不删除）

> 讲透Graph 第 03 章 | 实验 E3（`experiments/E3_bitemporal_invalidation.py`）
> 分支：Context Graph（Neo4j/Zep 路线）——节点=实体/事实/决策，边=类型化关系，回答 "What is known & how related?"

## 1. 直觉层：知识的"现在时"管理

三条时间线看清这个分支的进化：

1. **静态知识图谱**（传统 KG）：三元组 `(奥巴马, 出生于, 夏威夷)`——事实被当作**永远为真**。查"现在"没问题，查"当时"没门；
2. **GraphRAG**（微软 2024-04, arXiv 2404.16130）：批处理抽取实体+社区摘要，解决"跨关系连接信息"的检索。但数据一变就要重算，检索靠多轮 LLM 摘要，秒级到十秒级延迟——**不适合做记忆**；
3. **Temporal Context Graph**（Zep/Graphiti, arXiv 2501.13956）：事实带 **validity window**（何时为真）、**episode 溯源**（从哪条原始数据来）、**增量更新 + 自动作废**——为会进化的世界而生。

Neo4j CEO Emil Eifrem 的定义（2026-03 SF Context Graph Meetup）：
> **context graph = 知识图谱 + decision traces**（把组织里"决策是怎么做的"也挂上图）。

Graphiti 官方对 context graph 的定义更精确：**带 validity window 的事实图**——"Kendra loves Adidas (as of March 2026)"。

SurrealDB 补上系统视角：agent 每一轮都是 **read → think → write** 三步——从 context graph 读，在 execution graph 里想，写回两张图。**两张图跨轮一致才是完整的 graph engineering**（这就是本单元"双图统一"立场的出处）。

## 2. 数学层：bi-temporal 语义

每条事实边 $e$ 携带两个时间轴：

$$e = (s, p, o, t_{\text{valid}}^-, t_{\text{valid}}^+, t_{\text{know}}^-, t_{\text{know}}^+)$$

- **valid time** $[t_v^-, t_v^+)$：现实世界里这事实**何时为真**（Kendra 2024-09 起穿 Adidas）；
- **transaction time** $t_k^-$：系统**何时得知**（3 月 1 日换鞋，3 月 5 日才从对话里抽出来）。

**As-of 查询语义**：
$$\text{query}(s, p, \tau) = \{o \mid t_v^- \le \tau < t_v^+\}$$

**矛盾处理（fact invalidation）**：新事实 $(s,p,o_{\text{new}})$ 到来且 $o_{\text{new}} \ne o_{\text{old}}$ 时：
$$t_{\text{valid}}^+(e_{\text{old}}) \leftarrow t_{\text{valid}}^-(e_{\text{new}})$$
——旧边的窗口**关闭**，但边**不删**。三个查询能力由此解锁：现在什么为真 / 当时什么为真 / 这事实哪来的（provenance）。

## 3. 代码层：E3 三种存储对决

模拟 Kendra 的时间线（换鞋 + 搬家 + 角色不变），8 道题（4 现在问 + 4 当时问），结果（`E3_result.json`）：

| 存储 | 现在问 | 当时问 | 总分 | 病理 |
|------|--------|--------|------|------|
| 覆盖式（dict） | 4/4 | 2/4 | 6/8 | **活在没有历史的世界**——旧事实被覆盖蒸发 |
| 追加式（只加不废） | 1/4 | 3/4 | 4/8 | **活在矛盾的世界**——现在同时返回 Adidas 和 Nike |
| bi-temporal | 4/4 | 4/4 | **8/8** | 作废不删除，两个世界都能答 |

追加式的"现在喜欢什么品牌"返回 `['Adidas', 'Nike']`——agent 对用户说"你上次说喜欢 Adidas"就是这类 bug 的产品级表现。溯源演示：bi-temporal 还能答"我们何时得知的"（loves 事实的完整 validity window 时间带，见 E3_bitemporal.png 右图）。

Zep 论文的实测背书（生产级证据）：DMR 基准 94.8% vs MemGPT 93.4%；更难的 LongMemEval 上**准确率 +18.5% 同时延迟 -90%**（检索不靠 LLM 摘要，走语义+BM25+图遍历混合索引）。

## 4. 不足与坑

- **抽取错误的作废**：LLM 抽错一条新事实，会错误地作废一条好事实（错误在时间轴上传播比在空间上更阴险——它改写历史）；
- **时间本身难抽**：对话里的时间常是相对的（"上个月搬的家"），valid time 抽取是 Graphiti 全链路里最脆的一环；
- **bi-temporal 的维护费**：每次写入要做矛盾检测（同 $(s,p)$ 扫描）+ 消歧——E4 会把这笔账算出来（增量更新 3-7×）；
- **权限维度还没标准答案**：哪条边允许 agent 读/写？agent 写的边和人确认的边必须可区分（Ch09 治理）。

## 5. 与姊妹篇接口

- ← 讲透Context：图是"窗口外持久化"的结构化形态。compaction/memory/sub-agent 三逃生通道在图世界对应：图查询序列化进窗口（compaction 的精准版）/ 图即 memory / 子图隔离；
- → Ch04：把 context graph 装上记忆系统（episodic+semantic 双子图）；Ch07：图怎么被检索。

---

📌 下一步：Ch04 记忆即图——从"存事实"升级到"存经历与理由"。
✍️ 练习：给 E3 加第三种关系 `works_on`，事实流：2025-01 works_on(项目A) → 2025-08 works_on(项目B) → 2026-02 works_on(项目A)（又回来了！）。覆盖式/追加式/bi-temporal 各答对几题？（陷阱：去而复返的事实对 validity window 是考验——旧 A 边的窗口在 2025-08 关闭后，2026-02 应开**新**窗口而不是复用旧边。）
