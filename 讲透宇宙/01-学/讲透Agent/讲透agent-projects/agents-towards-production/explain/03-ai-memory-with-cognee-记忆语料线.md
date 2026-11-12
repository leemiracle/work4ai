# 03 | ai-memory-with-cognee——从五份语料到 126 节点记忆图谱

## ① 角色定位

`tutorials/ai-memory-with-cognee/` 占图谱两层：L4"记忆语料"（5 节点：两份 JSON + 三份 md）与 L5"图谱工件"（guido_contributions.html）。教学主张一句话：**agent 记忆 = 可检索的知识资产**。README.md:9 给出定位——把 Guido van Rossum 的贡献记录、PEP 规范、个人编码对话等分散数据统一进 cognee 知识图谱。tour step-04/05 把语料分成事实类与准则类两类记忆，step-06 用 HTML 工件展示终态。

## ② 内部结构

七件资产按角色分四组：
- **README.md**：导览。mermaid 图（README.md:11-29）画"Your Data→Knowledge Graph→AI Memory→Smart Insights"四跳；学习目标四条（README.md:33-36）。
- **环境**：requirements.txt:1 单行 `cognee[notebook]==0.3.3`（版本硬钉）；.env.template:1-2 两行——`LLM_API_KEY` 与 `LLM_MODEL="openai/gpt-4o-mini"`。
- **事实类语料**：`tutorials/ai-memory-with-cognee/data/guido_contributions.json` 279 行仅 4 条记录（2 条 mypy PR + mypy/cpython 各 1 条 commit，见 tutorials/ai-memory-with-cognee/data/guido_contributions.json:3-4、tutorials/ai-memory-with-cognee/data/guido_contributions.json:105-106、tutorials/ai-memory-with-cognee/data/guido_contributions.json:166-167），但每条是 12 字段富结构：type/repository/title/description/url/date/files_changed/related_issues/code_samples/commit_message_style/python_version/pep_status（tutorials/ai-memory-with-cognee/data/guido_contributions.json:2-6 起）；`tutorials/ai-memory-with-cognee/data/copilot_conversations.json` 108 行含 5 段 AI 编程对话（conversations 数组 tutorials/ai-memory-with-cognee/data/copilot_conversations.json:2，conv_001 topic "async/await patterns" tutorials/ai-memory-with-cognee/data/copilot_conversations.json:6；五段主题：async 模式、dataclass vs pydantic、测试、性能、错误处理；时间戳 tutorials/ai-memory-with-cognee/data/copilot_conversations.json:5-69 连续五天；另有 metadata 顶层键）。
- **准则类语料**：`tutorials/ai-memory-with-cognee/data/my_developer_rules.md`（30 行行为准则——"Respond only to explicit requests" tutorials/ai-memory-with-cognee/data/my_developer_rules.md:8、"never be sneaky" tutorials/ai-memory-with-cognee/data/my_developer_rules.md:22、"If unsure, say I don't know" tutorials/ai-memory-with-cognee/data/my_developer_rules.md:27）；`tutorials/ai-memory-with-cognee/data/pep_style_guide.md`（75 行 PEP 8 精要——缩进/行宽 tutorials/ai-memory-with-cognee/data/pep_style_guide.md:4-5、命名约定 tutorials/ai-memory-with-cognee/data/pep_style_guide.md:40-43、E501/E225/E402 违规码 tutorials/ai-memory-with-cognee/data/pep_style_guide.md:71-73）；`tutorials/ai-memory-with-cognee/data/zen_principles.md`（75 行 Python 之禅实用化——19 条原则逐条给工程指导 tutorials/ai-memory-with-cognee/data/zen_principles.md:8-63、"Modern Python Tie-ins" tutorials/ai-memory-with-cognee/data/zen_principles.md:65-68、评审 checklist tutorials/ai-memory-with-cognee/data/zen_principles.md:70-74）。
- **图谱工件**：`guido_contributions.html` 178KB 单文件——内嵌 D3.js 与 126 节点/241 边快照（regex 解析实证：Entity 89、Event 25、Timestamp 4、EntityType 4、DocumentChunk 2、NodeSet 1、TextDocument 1）。

## ③ 外部连接

图谱内 cognee README 以 related 边指向五份语料（step-04/05 五节点），HTML 工件 related 指回 guido_contributions.json（step-06）；zen→pep 还有一条 related 边（规范语料互引）。运行期连接全在 notebook：cognee-ai-memory.ipynb:104 `%pip install cognee==0.3.3`、cognee-ai-memory.ipynb:219 `await cognee.prune.prune_data()` 清态、cognee-ai-memory.ipynb:329-330 `from cognee import visualize_graph; await visualize_graph('./guido_contributions.html')`——HTML 工件就是这两行的落盘产物。语料被 notebook cognee-ai-memory.ipynb:461-464 四次 `cognee.add` 摄入并打 node_set 标签（conversations+rules→developer_data，zen+pep→principles_data）。仓外依赖仅 OpenAI API（.env.template:1）。

## ④ 数据流

输入：五份语料 + LLM_API_KEY。管线（notebook 实证）：`prune_data`（cognee-ai-memory.ipynb:219）→ 首轮 `cognee.add`（cognee-ai-memory.ipynb:254，先只摄 Guido 记录）→ `cognify`（cognee 内部抽实体/关系，README.md:42 的说明）→ `cognee.search("Show me commits")`（cognee-ai-memory.ipynb:296）→ `visualize_graph` 导 HTML（cognee-ai-memory.ipynb:330）→ 二轮全量 add 打 node_set（cognee-ai-memory.ipynb:461-464）→ `await cognee.memify()`（cognee-ai-memory.ipynb:552，跨源推断隐式规则构建"记忆层"）→ 按域检索 `node_type=NodeSet`（cognee-ai-memory.ipynb:650-654）与时间查询（cognee-ai-memory.ipynb:699 起）。输出：自然语言查询结果 + 可视化图谱。两类语料在数据流里角色不同：事实类回答"发生过什么"，准则类在被检索后约束 agent 行为（step-05 的教学点）。

## ⑤ 设计决策与陷阱

- **决策：语料刻意小型高质**。4 条贡献记录+5 段对话——cognify 要调 LLM 抽取，小语料让教程在几分钟内跑完且 API 费用可控；HTML 工件入库让"图谱长什么样"零成本可验。
- **决策：node_set 双域隔离**（developer_data vs principles_data，cognee-ai-memory.ipynb:461-464）——提前演示了生产记忆系统"按域检索"的最小形态，cognee-ai-memory.ipynb:650-654 的 NodeSet 过滤是其消费端。
- **陷阱 1：版本硬钉 0.3.3**。cognee API 在相邻版本变动剧烈（prune/memify/visualize_graph 均为 0.3.x 接口），升级 requirements.txt:1 大概率断链。
- **陷阱 2：.env 必须手工创建**。仓内只有 .env.template，`cp .env.template .env` 后填真实 key；LLM_MODEL 默认 openai/gpt-4o-mini（.env.template:2），换模型需同步确认 cognee 支持矩阵。
- **陷阱 3：别把 HTML 当可交互应用**。它是构建期快照，重新摄入语料后不会自动更新，需重跑 visualize_graph（cognee-ai-memory.ipynb:330）。
- **陷阱 4：JSON 语料的 12 字段 schema 是"给 LLM 看的"**——cognee 靠文本化整个 JSON 抽实体，改字段名会直接影响图谱里 Entity/Event 的产出形态。

## ⑥ 新人提示

建议三步消费：(1) 不装任何东西，直接浏览器打开 guido_contributions.html 看 126 节点终态，找 Entity 与 Timestamp 的连线建立直觉；(2) 读三份准则语料体会"规则也是记忆"——它们与你日后写给 agent 的 system prompt 是同构资产；(3) 再跑 notebook，重点盯 cognee-ai-memory.ipynb:461-464 的 node_set 打标与 cognee-ai-memory.ipynb:552 memify 前后的 search 结果差异。扩展练习：把自己的 git log 导出成同 schema JSON 替换 guido_contributions.json，重跑全管线获得"个人开发记忆图谱"——这正是本教程的终极命题（README.md:5 "learns from Python's creator" 的镜像用法）。
