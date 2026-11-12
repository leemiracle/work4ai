# agent-projects 组 understand 图谱队列（2026-10-30 立线）

> **认领公告（跨实例协议）**：本队列由 agent-repos 会话实例维护。当前认领：**首批 4 小仓**（下方 ⏳ 标记），
> 本实例 2026-10-30 起处理。其他实例请从「待认领」段取仓，开工时把仓移入「处理中」并写实例标识，
> 终态回写本文件。图谱产物=仓内 `.understand-anything/knowledge-graph.json`；人读产物=`讲透agent-projects/{仓}/`。

## 排序原则
小仓优先（批少链路短，快速积累基线）→ 文档型仓 → 中型 → 大仓（需 .understandignore 裁剪 node_modules/dist 等）。
规模=代码文件数（粗口径，scan 为准）。

## 处理中（本实例 2026-10-30 认领）
| 仓 | 规模 | 状态 |
|---|---|---|
| agents-towards-production | 15py+28ipynb | ⏳ prepare |
| Jobs_Applier_AI_Agent_AIHawk | 32py | ⏳ prepare |
| Open-AutoGLM | 40py | ⏳ prepare |
| planning-with-files | 127md+34sh | ⏳ prepare |

## 待认领（按规模升序）
bytebot(151ts/tsx) · page-agent(136ts/tsx) · nanobrowser(124ts) · AutoAgent(99py) · excelize(85go) ·
trae-agent(75py) · learn-claude-code(45md+43tsx) · owl(60py) · TradingAgents(58py) · huginn(470rb) ·
DeepResearch(174py) · Bert-VITS2(182py) · ml-agents(241cs/py) · ART(245py) · AgentGPT(254tsx) ·
gpt-researcher(279py) · serena(297py) · daily_stock_analysis(306py) · vanna(330py) · khoj(373py) ·
deer-flow(408ts/py) · agentscope(449py) · hello-agents(468py) · RD-Agent(498py) · WeKnora(552ts/py,**已有独立讲透WeKnora图谱,可跳**) ·
haystack(572py) · LangBot(584py) · genai-toolbox(711go) · cua(740py/ts) · E2B(740ts) · hive(773py) ·
agent-zero(824py) · MetaGPT(913py) · SurfSense(918ts) · BrowserOS(924ts) · vibe-kanban(1064ts) ·
arthas(1098java) · camel(1137py) · tambo(1184ts) · adk-python(1249py) · 1Panel(1289go) · vector(1453rs) ·
eliza(1705ts) · MaxKB(1747py) · ragflow(1934py/ts) · continue(2033ts) · OpenHands(2225py) · FastGPT(2290ts) ·
JeecgBoot(2386java/vue) · botpress(2535ts) · astron-agent(2621java) · bisheng(2921py) · nacos(3836java) ·
lobehub(6629ts) · pinpoint(8266java) · coze-studio(10970ts)

（awesome-ai-agents/CV=清单与资料仓无代码，不进 understand 线）

## 已完成
（空——首批 4 仓完成后回填：节点数/边数/层数/tour 步数/issues/fingerprints/onboard 字数/explain 篇数）

## 流水线命令（钉版，全在 pipeline-bin/understand/）
```bash
bash ~/ai/pipeline-bin/understand/prepare_understand.sh <repo> <name> <中文描述>
# 4 并发子代理批分析（file-analyzer.md + batches.json batchIndex 从 1 起 + 写 batch-N.json 无 slug + 禁原仓编译 + imports 对账）
python3 /home/lwz/.agents/skills/understand/merge-batch-graphs.py <repo>
python3 ~/ai/pipeline-bin/understand/phase4_prep.py <repo>   # layers/tour 任务输入
python3 ~/ai/pipeline-bin/understand/finalize_graph.py <repo>  # 组装+0issues+fingerprint
python3 ~/ai/pipeline-bin/understand/onboard_prep.py <repo>    # onboard 输入
```
