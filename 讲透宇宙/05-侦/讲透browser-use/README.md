# 讲透browser-use · 知识库状态表（2026-10-30 deepwiki 全量轮 · 2026-11-01 understand 七仓全链收官）

> star>1k 七仓（browser-use/video-use/jev-ultrafast/browser-harness/web-ui/workflow-use/macOS-use）understand 全链完成：图谱 7 份 2111n/4230e（validator 0 issues + fingerprints 基线）+ ONBOARDING 7×~6000字 + explain 84 篇 392,191 字；台账见仓群 deepwiki-batch/understand-7.md。其余仓 understand 未排期。

来源：GitHub org browser-use 全部 60 公开仓克隆于 /usr-data/data2/repos/browser-use/（8 并发三源轮转）；DeepWiki MCP 通道 10 并发抓取（dw_fetch_mcp.py + dw_reconcile_dir.py 终判）。
既有 7 仓为同日全量清单分层轮（stars>1k）产物，本批扩展至全 org。

| 仓 | stars | 层 | 终判 | understand |
|---|---|---|---|---|
| browser-use | 119,512 | A | TRUE_100 | ✅912n/1957e/16L/16T |
| video-use | 30,114 | A | TRUE_100 | ✅84n/128e/12L/13T |
| jev-ultrafast | 23,899 | A | TRUE_100 | ✅78n/179e/13L/15T |
| browser-harness | 18,710 | A | TRUE_100 | ✅275n/480e/13L/15T |
| web-ui | 16,628 | A | TRUE_100 | ✅117n/279e/12L/15T |
| workflow-use | 4,242 | B | TRUE_100 | ✅491n/899e/16L/16T |
| macOS-use | 1,999 | B | TRUE_100 | ✅154n/308e/14L/16T |
| macos-harness | 973 | C | TRUE_100 | ⏳ |
| awesome-prompts | 966 | C | TRUE_100 | ⏳ |
| vibetest-use | 832 | C | TRUE_100 | ⏳ |
| browsercode | 784 | C | TRUE_100 | ⏳ |
| desktop | 706 | C | TRUE_100 | ⏳ |
| agent-sdk | 685 | C | TRUE_100 | ⏳ |
| terminal | 656 | C | TRUE_100 | ⏳ |
| qa-use | 608 | C | TRUE_100 | ⏳ |
| open-duet | 499 | C | REPO_DOCS | ⏳ |
| browser-harness-js | 496 | C | TRUE_100 | ⏳ |
| bux | 459 | C | TRUE_100 | ⏳ |
| browser-use-pi | 445 | C | TRUE_100 | ⏳ |
| life-recorder | 339 | C | TRUE_100 | ⏳ |
| cdp-use | 326 | C | TRUE_100 | ⏳ |
| rl-env-use | 164 | C | TRUE_100 | ⏳ |
| benchmark | 161 | C | TRUE_100 | ⏳ |
| awesome-projects | 134 | C | REPO_DOCS | ⏳ |
| bubus | 126 | C | TRUE_100 | ⏳ |
| windows-harness | 79 | C | REPO_DOCS | ⏳ |
| browser-agent-template | 73 | C | REPO_DOCS | ⏳ |
| n8n-nodes-browser-use | 48 | C | REPO_DOCS | ⏳ |
| eval | 45 | C | TRUE_100 | ⏳ |
| contact-use | 38 | C | REPO_DOCS | ⏳ |
| browser-use-node | 30 | C | TRUE_100 | ⏳ |
| stress-tests | 28 | C | REPO_DOCS | ⏳ |
| sdk | 28 | C | TRUE_100 | ⏳ |
| plugins | 26 | C | REPO_DOCS | ⏳ |
| agent-studio | 26 | C | REPO_DOCS | ⏳ |
| template-library | 25 | C | REPO_DOCS | ⏳ |
| chat-ui-example | 23 | C | REPO_DOCS | ⏳ |
| online-mind2web | 20 | C | REPO_DOCS | ⏳ |
| browser-use-python | 15 | C | TRUE_100 | ⏳ |
| browser-harness-tui | 14 | C | REPO_DOCS | ⏳ |
| browser-use-examples | 13 | C | REPO_DOCS | ⏳ |
| go-harnessless | 12 | C | REPO_DOCS | ⏳ |
| nicehack69 | 12 | C | REPO_DOCS | ⏳ |
| webagents.md | 12 | C | REPO_DOCS | ⏳ |
| docs | 9 | C | REPO_DOCS | ⏳ |
| gemini-demo | 9 | C | REPO_DOCS | ⏳ |
| browser-use-rsi | 8 | C | REPO_DOCS | ⏳ |
| cc_compaction | 6 | C | REPO_DOCS | ⏳ |
| profile-use-releases | 5 | C | REPO_DOCS | ⏳ |
| vc-use | 4 | C | REPO_DOCS | ⏳ |
| browser-worlds-tinker-rl | 4 | C | REPO_DOCS | ⏳ |
| mix-eval-go | 4 | C | REPO_DOCS | ⏳ |
| .github | 3 | C | — | ⏳ |
| eve | 3 | C | REPO_DOCS | ⏳ |
| plugin-marketplace | 2 | C | REPO_DOCS | ⏳ |
| media | 2 | C | REPO_DOCS | ⏳ |
| studio-pair | 1 | C | REPO_DOCS | ⏳ |
| evaluation-endpoint | 1 | C | REPO_DOCS | ⏳ |
| usercontent-host | 0 | C | REPO_DOCS | ⏳ |
| agentenv-framework | 0 | C | REPO_DOCS | ⏳ |

**收录 27/60**（TRUE_100）；未收录 33 仓见 放弃清单-no-deepwiki.txt（MCP 明确 Repository not found；收录决定权在 DeepWiki 后台，钉版：匿名触发索引不可依赖）。终判口径：exit0=coverage n/n(100%) 结构全命中；EXIT1 经 dw_reconcile_dir.py 终判 MISSING=0。

## 2026-10-31 复核轮（bu-reprobe）

33 仓放弃清单全量重探（MCP 10 并发，台账 `deepwiki-batch/bu-reprobe/`）：**33/33 仍 NOT_INDEXED**，隔天零转化，再证收录决定权在后台。兜底分支（project-proposals 先例）：本地有克隆的 **32 仓走 repo-docs 全量收割**（README+docs 原文 → 各仓 `repo-docs/`，含 _filelist.txt；总索引 `_docs-index.md`），终判 REPO_DOCS。`.github` 无本地克隆维持 —。至此 **60/60 全部有知识库产物**：27 deepwiki + 32 repo-docs + 1 弃（.github）。

## 2026-11-01 understand 全链轮（七仓 star>1k）

用户令"star大于1k的仓库做完 understand 流水线"。七仓全链完成（图谱+onboarding+explain 各 12 篇）：合计图谱 2101 节点/4130 边/0 issues、ONBOARDING 7×~6000 字、explain 84 篇 ≈39.2 万字（行号锚全部源码核实）。台账 `deepwiki-batch/understand-7.md`（含 1308 中断与恢复实录）。子代理甄别成果显著：macOS-use 系 browser-use 移植中间态（tests 全量不可运行+上游 PostHog 遥测残留含任务原文上报）、workflow-use 后端每请求新建 service 实例 bug+CI 测试禁用、主仓 14 watchdog 子类/watchdog 装配点 L1706-1727/beta 为 Rust 包装层等。
