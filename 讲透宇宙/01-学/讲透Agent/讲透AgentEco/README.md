# 讲透AgentEco — agent 仓 DeepWiki 知识库（2026-10-27）

扫描 `/usr-data/data1/agent/repo/agent` 全部 271 个含 `.git` 子目录 → 269 个唯一 GitHub org/name（镜像域名已归一化；1 重复、1 非 GitHub 托管）。
通道 `mcp.deepwiki.com/mcp`（dw_fetch_mcp.py，10 并发，全程 ~8 分钟）；30 个 exit-1 假阴性经 dw_reconcile_dir.py 全层级对账终判全部 TRUE_100。

## 总览

| 状态 | 数量 | 说明 |
|---|---|---|
| ✅ deepwiki 全量收录 | 114 | 每仓 `<org>_<name>/deepwiki/` 含 INDEX.md + 全部章节页 + _coverage-check.md |
| ❌ DeepWiki 未收录→放弃 | 155 | 见 [放弃清单-no-deepwiki.txt](放弃清单-no-deepwiki.txt) |
| ⭕ 非 GitHub 托管 | 1 | agent-mem-unified（code.gitlink.org.cn） |

合计 4549 页 / 61,719,638 字符。
本地图谱（understand）/onboard/explain 未做（后续按需）。

## 收录明细（114 仓）

| repo | 页数 | 字符 |
|---|---|---|
| aakashadesara/ctop | 31 | 184949 |
| aannoo/hcom | 50 | 408746 |
| aaronjmars/aeon | 37 | 277994 |
| actionbook/actionbook | 34 | 817237 |
| aden-hive/hive | 42 | 467000 |
| ag2ai/ag2 | 59 | 695976 |
| agentset-ai/agentset | 41 | 466692 |
| aklofas/kicad-happy | 23 | 177575 |
| alinaqi/claude-bootstrap | 36 | 855916 |
| angular/skills | 44 | 289266 |
| anomalyco/opencode | 51 | 772898 |
| antonbabenko/terraform-skill | 29 | 517881 |
| arize-ai/phoenix | 39 | 619954 |
| assafelovic/gpt-researcher | 75 | 825837 |
| aymenfurter/microagents | 19 | 194611 |
| blader/humanizer | 22 | 206960 |
| bojieli/ai-agent-book | 38 | 359696 |
| botpress/botpress | 32 | 753846 |
| cactus-compute/needle | 32 | 227533 |
| cline/cline | 89 | 941628 |
| coderabbitai/skills | 22 | 156625 |
| conorluddy/ios-simulator-skill | 68 | 663913 |
| coreyhaines31/marketingskills | 36 | 852115 |
| czlonkowski/n8n-skills | 33 | 314947 |
| deepseek-ai/deepseek-harness | 44 | 782289 |
| deepset-ai/haystack | 27 | 405380 |
| degausai/wonda | 31 | 194155 |
| deusyu/translate-book | 21 | 131245 |
| dust-tt/dust | 62 | 1554048 |
| feder-cr/invisible_playwright | 33 | 268279 |
| flepied/second-brain-agent | 21 | 268665 |
| giselles-ai/giselle | 34 | 994442 |
| gitroomhq/postiz-agent | 25 | 149632 |
| gobii-ai/gobii-platform | 36 | 791977 |
| gokapso/agent-skills | 23 | 165458 |
| google/skills | 24 | 215355 |
| hqhq1025/skill-optimizer | 21 | 140428 |
| huggingface/smolagents | 57 | 627546 |
| hypermodeinc/modus | 26 | 325685 |
| ibelick/ui-skills | 20 | 239129 |
| iflytek/astron-agent | 78 | 1115999 |
| indranilbanerjee/digital-marketing-pro | 38 | 293572 |
| jarrycyx/openlens-ai | 28 | 255339 |
| joinly-ai/joinly | 29 | 465184 |
| josstei/maestro-orchestrate | 30 | 224627 |
| k-kolomeitsev/data-structure-protocol | 28 | 190704 |
| kayba-ai/agentic-context-engine | 80 | 795433 |
| kreneskyp/ix | 20 | 242087 |
| kreuzberg-dev/kreuzberg | 76 | 935762 |
| kubestellar/console | 64 | 1414448 |
| kyegomez/swarms | 42 | 559030 |
| kyrolabs/awesome-agents | 10 | 85631 |
| l33tdawg/sage | 38 | 281617 |
| lackeyjb/playwright-skill | 45 | 894766 |
| landing-ai/vision-agent | 31 | 375263 |
| makenotion/claude-code-notion-plugin | 25 | 353127 |
| makenotion/notion-cookbook | 16 | 255874 |
| mastra-ai/mastra | 125 | 2103114 |
| matevip/mateclaw | 47 | 558109 |
| mattpocock/skills | 40 | 393520 |
| microsoft/autogen | 37 | 572413 |
| microsoft/semantic-kernel | 30 | 609214 |
| miurla/babyagi-ui | 27 | 287174 |
| mixpeek/amux | 52 | 900734 |
| mnfst/manifest | 33 | 339141 |
| modelscope/agentscope | 65 | 761794 |
| mpaepper/llm_agents | 25 | 458139 |
| mvanhorn/last30days-skill | 35 | 330854 |
| neolabhq/context-engineering-kit | 38 | 494233 |
| nextlevelbuilder/ui-ux-pro-max-skill | 38 | 402495 |
| nousresearch/hermes-agent | 73 | 1700441 |
| obra/superpowers | 76 | 905414 |
| openaccountants/openaccountants | 34 | 380143 |
| openai/swarm | 20 | 137503 |
| openclaw/openclaw | 56 | 1264076 |
| openonion/connectonion | 50 | 492896 |
| phuryn/pm-skills | 31 | 571536 |
| pipecat-ai/pipecat | 48 | 724058 |
| plandex-ai/plandex | 33 | 506348 |
| prompt-security/clawsec | 32 | 985531 |
| redis/agent-skills | 18 | 120234 |
| resend/resend-skills | 32 | 217300 |
| run-llama/llama-agents | 36 | 341330 |
| saharmor/voice-lab | 18 | 183859 |
| sanjay3290/ai-skills | 36 | 910136 |
| santifer/career-ops | 49 | 447031 |
| scarletkc/vexor | 64 | 1030163 |
| screenpipe/screenpipe | 52 | 957352 |
| semanser/codel | 17 | 202738 |
| sipyourdrink-ltd/bernstein | 48 | 562117 |
| smixs/creative-director-skill | 26 | 260863 |
| sopaco/cortex-mem | 45 | 473124 |
| sst/opencode | 72 | 951360 |
| stakpak/agent | 36 | 696911 |
| stanford-oval/storm | 24 | 426982 |
| stanfordnlp/dspy | 46 | 472195 |
| steel-dev/steel-browser | 55 | 611511 |
| stepanogil/autonomous-hr-chatbot | 12 | 131575 |
| stitionai/devika | 20 | 225696 |
| strands-agents/sdk-python | 58 | 956981 |
| swarmclawai/swarmclaw | 74 | 686092 |
| testdino-hq/playwright-skill | 34 | 225988 |
| the-open-agent/openagent | 45 | 354269 |
| truongduy2611/app-store-preflight-skills | 16 | 112830 |
| ultraworkers/claw-code | 30 | 333529 |
| vectara/open-rag-eval | 13 | 169326 |
| vectara/py-vectara-agentic | 26 | 259356 |
| vectorize-io/hindsight | 82 | 1531104 |
| video-db/skills | 63 | 1114686 |
| voltagent/voltagent | 70 | 1412982 |
| wrsmith108/linear-claude-skill | 28 | 168548 |
| zarazhangrui/frontend-slides | 47 | 462695 |
| zscole/model-hierarchy-skill | 29 | 452102 |
| zxkane/aws-skills | 18 | 335822 |
