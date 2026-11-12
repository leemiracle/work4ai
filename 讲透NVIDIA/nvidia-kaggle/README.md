# 讲透 nvidia-kaggle（NVIDIA/nvidia-kaggle）

> NVIDIA 官方 Kaggle 竞赛 agent 插件仓：单一 skill `nvidia-kaggle-skill` 给 Claude Code / Codex / Claude Agent SDK 提供竞赛调研→kernel 研究→本地复现→提交→数据集上传的端到端工作流。
> 本地仓：/usr-data/data2/repos/agent-repos/NVIDIA/nvidia-kaggle（commit 2b78cf29，2026-11-09 图谱基线）。

## 流水线状态

| 步骤 | 状态 | 产物 |
| --- | --- | --- |
| DeepWiki 全量抓取 | ✅ 既有 | `deepwiki/`（INDEX+全页+wiki_full.md 3313 行） |
| understand 图谱 | ✅ 2026-11-09 | 仓内 `.understand-anything/knowledge-graph.json`：**249 节点/437 边/10 层/12 步 tour**，validator 0 issues，fingerprints 73 文件基线@2b78cf29 |
| onboarding | ✅ 2026-11-09 | `onboarding/ONBOARDING.md`（5960 非空白字符 8 节 46 锚，全部源码核实） |
| explain | ✅ 2026-11-09 | `explain/` 2 篇：01 提交主管线（push→poll→submit→poll 与槽位守卫）/ 02 SKILL.md 契约与 kernels/discussions 双研究域 |

## 口径说明

- 字数采信**不计空格字符**口径；行号锚写作前逐条 `sed -n`/`grep -n` 核实，相对仓根路径；`kernels/`、`discussions/` 前缀系指 `skills/nvidia-kaggle-skill/scripts/` 之下。
- 全仓代码体量：38 个 Python 文件约 4.8k 行，集中 `skills/nvidia-kaggle-skill/scripts/`。

## 源码级实证勘误（vs DeepWiki 快照/仓自身声明）

1. **提交轮询超时不是 1 小时，是 24 小时**：DeepWiki 称 "timeout (default 1 hour)"；源码 `skills/nvidia-kaggle-skill/scripts/constants.py:18` `DEFAULT_KERNEL_TIMEOUT_SECONDS = 86_400`，且 `skills/nvidia-kaggle-skill/scripts/submit_kernel.py:222` 的 argparse help 明写 "= 24h"。
2. **轮询间隔不是 60s，是 30s**：DeepWiki 称 "DEFAULT_POLL_INTERVAL_SECONDS (default 60s)"；源码 `skills/nvidia-kaggle-skill/scripts/constants.py:17` 值为 `30`。
3. **认证里没有 OAuth**：DeepWiki 称 runtime.py "handles authentication (OAuth and XSRF)"；全仓 grep `oauth` 零命中，实际是单一 KGAT token——官方库 `api.authenticate()`（`skills/nvidia-kaggle-skill/scripts/runtime.py:44-48`）+ 裸 REST `Authorization: Bearer`（`skills/nvidia-kaggle-skill/scripts/kernels/kaggle_client.py:33`）+ XSRF 会话种子（`skills/nvidia-kaggle-skill/scripts/runtime.py:74-75`），无任何授权码/刷新流程。
4. **kernels.db 不存 scores/lineage**：DeepWiki 称 "data/kernels.db: Stores kernel metadata, scores, and lineage information"；源码 `skills/nvidia-kaggle-skill/scripts/kernels/database.py:15-44` 仅 `kernels`+`competition_info` 两张表——公开分数在 `skills/nvidia-kaggle-skill/scripts/kernels/kaggle_search.py:61` 的内存对象 `best_public_score`，lineage 无任何持久化。
5. **排行榜 writeup 抓取不是 HTML 抓屏**：DeepWiki mermaid 画 `GET /c/<slug>/leaderboard` 返回 "HTML Leaderboard Data"；源码 `skills/nvidia-kaggle-skill/scripts/fetch_leaderboard_writeups.py:5-7` docstring 明言 "Replaces the previous headless-browser scraper"，实际走 JSON RPC `competitions.CompetitionService/GetCompetition`（:36-38）+ `competitions.LeaderboardService/GetLeaderboard`（:42-45）——DeepWiki 描述的是已被替换的旧架构。
6. **运行时依赖声明与 pyproject 不一致**：skills/nvidia-kaggle-skill/SKILL.md:47/53 主张 "Install only the packages needed"（仅 httpx/kaggle/kagglesdk/nbformat/pydantic/python-dotenv/rich 7 个）；`pyproject.toml:15-26` 的 [project] dependencies 却捆入 claude-agent-sdk、numpy、pandas、pytest、scikit-learn——pip 安装插件会拖进整个数据科学栈。
7. **sdist 排除表泄漏真实竞赛工作区名**：`pyproject.toml:58-59` 排除 `/rapids-svd-oof-0-80/**`、`/titanic-wcg-xgboost-0-84688/**`——两个本地 dogfooding 工作目录名进了包配置，与"发布件只含 skills/ 文档"的 wheel 口径（:44-49）形成卫生反差。
8. **图谱 tour 的"提交历史 20 用例"为口径漂移**：`tests/test_submission_history.py` 实测 `grep -c "^def test_"` = **18** 个测试函数（含损坏行容错/永不抛/timeout 覆盖等边界）。

## 快速上手指针

- 契约总入口 `skills/nvidia-kaggle-skill/SKILL.md`（五项权限 frontmatter:5-10 + 七工作流分派:65-148）。
- 提交主管线走读见 `explain/01-submit-pipeline.md`；双研究域与契约测试见 `explain/02-agent-contract-dual-domain.md`；全景走读见 `onboarding/ONBOARDING.md`。
