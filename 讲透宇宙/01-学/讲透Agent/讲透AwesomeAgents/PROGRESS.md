# 讲透AwesomeAgents 批量 deepwiki 轮 — 进度（MR-3.1 交接）✅ 终态

## 任务定义
- 源：/usr-data/data1/agent/repo/agent/awesome-agents/repos 下 138 个 git 仓
- 已有产物跳过 2：ColossalAI、DeepSeek-Harness（work4ai 顶层既有讲透目录含 deepwiki）
- 本批 135 仓 → work4ai/讲透AwesomeAgents/{RepoName}/deepwiki/（INDEX+coverage+wiki_full+分页+README）
- 通道：mcp.deepwiki.com MCP（dw_fetch_mcp.py）

## 终态（2026-10-26 10:27 批跑完成，10:5x 收官）
- [x] manifest 生成（135 行）
- [x] 批量抓取：4 并发 ~3min，零 ERROR；首态 DONE100=86 / INCOMPLETE=20 / NOT_INDEXED=29
- [x] INCOMPLETE 甄别：20/20 全 MISSING=0 → FINAL_100（extra/三级页假阴性，零真缺口）
- [x] NOT_INDEXED 改名解析：github.com 重定向解析现 slug，14/29 挽回复抓
      （11 DONE100 + 3 reconcile FINAL_100），真未索引 15 落终态占位
- [x] 全量 README（120 状态表 + 15 占位）+ 集合 README 明细表 + 台账 _ledger.tsv 135 行全终态

## 最终分布
DONE100 97 + FINAL_100 23 = **120/135 抓取成功** · NOT_INDEXED 15（understand 线替代）

## 交接（下一步若继续此工作区）
- understand 图谱线：120 仓源码全部本地在手（awesome-agents/repos/），
  NOT_INDEXED 15 仓 understand 是唯一知识源（同 TIRx-kernels 先例）
- 大仓注意 .understandignore 裁剪；派发模板见 memory 钉版
- 复跑：bash batch_dw_fetch.sh（幂等断点续跑）；甄别：python3 batch_reconcile.py

## 本轮新钉版坑
1. **NOT_INDEXED 假阴性新形态：本地 remote 指向改名前旧 org**——GitHub 自动重定向 clone 不报错，
   DeepWiki 按现 slug 索引 → "Repository not found"。处置=github.com 重定向解析现 slug（clash 代理）
   再探 MCP 复抓。本批 29 个 NOT_INDEXED 里 14 个是改名仓（crewai→crewAIInc/crewAI、
   memgpt→letta-ai/letta、phidata→agno-agi/agno、Agent-LLM→Josh-XT/AGiXT、llama_index→run-llama 等）。
   头部仓报未索引必先怀疑改名。
2. api.github.com 直连与 clash 代理都 000（本轮环境），github.com HTML 301 重定向可靠。
3. 台账 verdict 行丢 slug 前缀 bug 两次复现（batch_reconcile.py 已修根因）——批量脚本写台账
   必须模板含键列，修完跑分布对账（行数=清单数）才能收。
