# 知识图谱（Knowledge Graph）工程手册

> **建立**：2026-08-13
> **是什么**：用图谱组织个人知识——节点（概念）+ 边（关系）。**不是文件夹，是网络**。
> **为什么重要**：人脑记忆是**联想网络**，不是目录树。知识图谱 = 给大脑建外存。

---

## 1. 是什么 + 为什么

**个人知识图谱** = 你的"第二大脑"：
- **节点**：每个概念 / 论文 / 想法 = 一个 note
- **边**：note 之间的双向链接（`[[双向链接]]`）
- **属性**：tag / metadata / backlinks

**vs 文件夹**：
- 文件夹：一个文件只能在一个目录
- 图谱：一个 note 可以连任意多个其他 note

**核心工具**：**Obsidian**（本地 + 双向链接 + 插件生态）

---

## 2. 听说读写 4 能力

| 能力 | 含义 |
|------|------|
| **听** | 解析别人的知识图谱（看 backlinks / tag 结构）|
| **说** | 用 PKM 圈行话（Zettelkasten / atomic note / backlink / MOC）|
| **读** | 读知识管理书（《How to Take Smart Notes》《Building a Second Brain》）|
| **写** | 建自己的图谱 + 持续维护 |

---

## 3. Zettelkasten 5 要素

```
A - Atomic（原子化）：每个 note 只讲 1 个 idea
L - Linked（链接化）：每个 note 必须有 ≥ 1 个双向链接
I - In-own-words（自己的话）：不用复制，用自己的语言写
V - Visualizable（可视化）：能用 graph view 看到结构
E - Evolving（演化）：note 可合并 / 拆分 / 重命名
```

---

## 4. 6 维度评价

| 维度 | 指标 |
|------|------|
| **1. 准确性** | note 内容是否正确 + 最新 |
| **2. 稳健性** | 跨时间一致性（半年后还能用）|
| **3. 可迁移性** | 跨工具（Obsidian → Notion → Logseq）|
| **4. 效率** | 写 note 时间 vs 检索时间 |
| **5. 可控性** | graph 是否清晰（不是一团乱麻）|
| **6. 安全性** | 隐私 / 备份 / 同步 |

---

## 5. 工具栈（2026-08）

| 工具 | 类型 | 特点 |
|------|------|------|
| **Obsidian** | 本地优先 | 双向链接 + 800+ 插件 + 免费 |
| **Logseq** | 本地优先 | 大纲式 + 开源 |
| **Notion** | 云端 | 团队协作 + 数据库 |
| **Roam Research** | 云端 | 双向链接鼻祖（贵）|
| **RemNote** | 云端 | 闪卡集成 |
| **Anki** | 闪卡 | 间隔重复（与 Obsidian 联动）|
| **Heptabase** | 白板 | 视觉化思考 |

### Obsidian 必装插件

| 插件 | 用途 |
|------|------|
| **Dataview** | 用 SQL 查询笔记 |
| **Templater** | 模板系统 |
| **Excalidraw** | 手绘图 |
| **Graph Analysis** | 图谱分析 |
| **Obsidian Git** | Git 同步 |
| **Anki Sync** | 闪卡同步 |
| **Tasks** | 任务管理 |

---

## 6. PKM 方法对比

| 方法 | 核心思想 | 适合 |
|------|---------|------|
| **Zettelkasten**（Luhmann）| 原子化 + 双向链接 | 学术 / 研究 |
| **Building a Second Brain（CODE）** | Capture/Organize/Distill/Express | 通用 |
| **PARA**（Tiago Forte）| Projects/Areas/Resources/Archives | 行动导向 |
| **MOC**（Maps of Content）| 主题索引页 | 大型知识库 |
| **Smart Notes** | 文献笔记 + 永久笔记 | 论文阅读 |

---

## 7. 实战案例：研究生的知识图谱

### 结构

```
00-Inbox/          # 快速捕获（待整理）
10-Notes/          # 永久笔记（atomic，1 idea/note）
20-MOCs/           # Maps of Content（主题索引）
30-Papers/         # 论文笔记
40-Projects/       # 项目笔记
50-Daily/          # 日志
60-Templates/      # 模板
90-Archive/        # 归档
```

### 一个 atomic note 示例

```markdown
---
tags: [ml/attention, concept]
created: 2026-08-13
sources: [[Vaswani_2017_Attention_Is_All_You_Need]]
---

# Self-Attention 的数学本质

Self-attention = 每个位置"看"所有其他位置，加权平均。

公式：Attention(Q,K,V) = softmax(QK^T/√d_k) · V

## 直觉
图书馆员同时翻所有书，给每本打相关度分数。

## 关键
- Q(query): 我在找什么
- K(key): 每本书的标签
- V(value): 每本书的内容

## 关联
- [[Multi-Head_Attention]]：多个 attention 并行
- [[Positional_Encoding]]：attention 本身无序
- [[Induction_Heads]]：ICL 的物理基础
- [[讲透Transformer]]：work4ai 深挖

## 参考
- [[Vaswani_2017_Attention_Is_All_You_Need]]
```

---

## 8. 反模式 10 条

1. **复制粘贴**：不自己的话 = 没消化
2. **巨型 note**：1 个 note 5000 字（违反 atomic）
3. **无链接的孤岛**：note 没有 `[[链接]]`
4. **过度 tag**：1 个 note 20 个 tag
5. **只存不查**：建了 1000 note 但没用过
6. **完美主义**：花 2 小时排版 1 个 note
7. **无模板**：每个 note 格式不同
8. **无备份**：本地崩溃丢全部
9. **无 inbox**：所有东西直接进永久区
10. **无 MOC**：1000 note 没有索引 = 找不到

---

## 9. 下一步

- 装 Obsidian + 必装插件（Dataview / Templater / Excalidraw）
- 读《How to Take Smart Notes》（Ahrens）
- 读《Building a Second Brain》（Forte）
- 建第一个 MOC：`[[AI 学习地图]]`
- 每天写 3-5 个 atomic note

---

## 10. 自动化供给端：graphify

手工建图之外，2026 年出现了**自动给图供料**的工具——[`Agent上下文案例/graphify知识图谱skill/`](../../Agent上下文案例/graphify知识图谱skill/)：

- `/graphify .` 把代码库（tree-sitter AST）+ 文档/PDF/视频映射成知识图谱，**可一键导出 Obsidian vault**（`--obsidian`，节点=笔记、边=`[[链接]]`）——本手册 §3 的 ALIVE 五要素由机器预填
- `graphify add <arxiv-url>` 收论文、`add <youtube-url>` 收视频转写，`graphify global add` 进全局图——Inbox（00-Inbox）的自动化进料口
- Leiden 社区检测 ≈ 自动生成 MOC（每社区一个主题索引）；god nodes ≈ 自动找到你的"枢纽概念"

详见该案例 [笔记 02](../../Agent上下文案例/graphify知识图谱skill/notes/02-skill交付面与平台策略.md) §6。

---

**版本**：v1.0（2026-08-13；2026-08-14 增 §10 graphify 自动化供给端）
**核心理念**：**知识不是文件夹，是网络。给大脑建外存 = 给思想装扩容。**
