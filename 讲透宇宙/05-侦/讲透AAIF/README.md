# 讲透 AAIF（aaif.io/projects 全聚合 · 7 仓知识库）

> AAIF（Agentic AI Foundation，Linux Foundation）全部项目本地聚合仓：`/usr-data/data2/repos/aaif-projects`（建于 2026-10-21，README 状态表工具链见仓根 README.md）。
> 本目录为组级索引；各仓产物在同级 `讲透<仓名>/` 目录。

## 终态总表（2026-11-01 收官盘点）

| # | 仓 | 定位 | DeepWiki | 图谱（nodes/edges/层/步） | onboard | explain | 状态 |
|---|---|---|---|---|---|---|---|
| 1 | [A2A](讲透宇宙/02-透/讲透A2A) | agent2agent 协议（Google 发起） | 36 页 368K ✅ | 183/352/8/8@98279d62 ✅ | 3018 汉字 ✅ | 6 篇（docs 小仓口径）✅ | **全链** |
| 2 | [goose](讲透宇宙/02-透/讲透goose) | AI agent 桌面/CLI（Block） | 51 页 652K ✅ | 4437/9220/16/16@390dfb8c ✅ | 4012 汉字 ✅ | 12 篇 ✅ | **全链** |
| 3 | [agentgateway](../讲透agentgateway) | agent 流量网关（CNCF 沙箱） | 109 页 1.72M ✅ | 7792/19479/16/16@f51a7fbc ✅（流水线史上最大之一） | 4064 汉字 ✅ | 12 篇 ✅ | **全链** |
| 4 | [agent-router](../讲透agent-router) | K8s 原生 agent 路由（Envoy ext_proc） | 43 页 388K ✅ | 3083/12740/15/16@7bcb4547 ✅ | 4008 汉字 ✅ | 12 篇 ✅ | **全链** |
| 5 | [modelcontextprotocol](讲透宇宙/02-透/讲透modelcontextprotocol) | MCP 协议规范+SDK（Anthropic 发起） | 46 页 466K ✅ | 633/1800/14/15@80041ab0 ✅ | 4110 汉字 ✅ | 12 篇 ✅ | **全链** |
| 6 | [agents.md](../讲透agents.md) | AGENTS.md 标准官网 | 25 页 223K ✅ | 55/81/12/14@d001185d ✅ | 9,885 非空白 ✅ | 6 篇（小仓口径）✅ | **全链** |
| 7 | [project-proposals](讲透宇宙/03-查/讲透project-proposals) | AAIF 项目提案流程 | ➖ 未索引 | ➖ 无代码 | repo-docs 等价 ✅ | ➖ | **终态**（repo-docs 全量收割） |

- 图谱均在各仓内 `.understand-anything/knowledge-graph.json`（validator 全 0 issues）。
- 全链 6 仓合计：**16,183 节点/43,672 边**，ONBOARDING 6 份，explain 60 篇（6+12+12+12+12+6）。

## 时间线

- 2026-10-21：建聚合仓（7/7 git 健康）+ DeepWiki 全量抓取（6 仓 MCP 通道 + project-proposals repo-docs 兜底）
- 2026-10-22：goose prepare（91 批）
- 2026-10-23~24：goose 全链 → A2A 全链（14 批）→ agentgateway 全链（95 批，1308 团灭复活两波）
- 2026-10-26~27：agent-router（57 批，site/ 473 文件裁）→ modelcontextprotocol（79 批，examples 夹具裁）
- 2026-11-01：收官盘点——agent-router README/PROGRESS 漏更新补齐 + modelcontextprotocol explain 11/12 补篇（SEP 状态机三件套/validate-examples）+ 本组级索引建立；同日用户裁定 agents.md 补全链 → **7/7 终态收官**（agents.md 5 批 30 分钟全链：55n/81e/12 层/14 步+6 篇 explain）

## 值得先读（跨仓视角）

- **协议演进主线**：A2A（agent 间协议）与 MCP（agent×工具协议）是 AAIF 双支柱——MCP 的 stateless 转向（2026-07-28 GA）与六版本演进史见 讲透modelcontextprotocol/explain/01+03。
- **数据面双雄**：agentgateway（Envoy 生态，Rust+Go 混合，7792 节点最大图谱）vs agent-router（K8s CRD 原生，Go 单仓）——同为 agent 流量治理的两种架构答案，explain 系列可直接对照读。
- **应用端代表**：goose（4437 节点，Rust 核心+TS 桌面+TUI 全家桶）是"协议消费者"侧最大样本。
- 勘误精选：MCP 死导出双主张（AUTO_TRANSITION_RULES/getStalenessRule）与"CI 门禁不成立"（validate-examples 零 workflow 调用）——讲透modelcontextprotocol/README.md 勘误节。
