# nvidia-kaggle 仓库 Onboarding

> 仓库 `/usr-data/data2/repos/agent-repos/NVIDIA/nvidia-kaggle`（commit 2b78cf29）；图谱 249 节点/437 边/10 层/12 步导览，fingerprints 73 文件基线。锚均经源码核实；锚相对仓根，`scripts/`、`kernels/`、`discussions/` 等前缀系指 `skills/nvidia-kaggle-skill/scripts/` 之下。

## 1. 这是什么仓库

NVIDIA 官方的 **Kaggle 竞赛 agent 插件仓**：不是给人用的 CLI，而是给 Claude Code / Codex / Claude Agent SDK 等 agent 运行时装载的单一 skill `nvidia-kaggle-skill`，覆盖竞赛调研→kernel 研究→本地复现→提交→数据集回流的全流程。README.md:9 一句话定位："gives agents end-to-end Kaggle competition workflows through a single skill"。发布面是三份清单：`.claude-plugin/plugin.json:6`（skills 指向 `./skills/nvidia-kaggle-skill/`）、`.claude-plugin/marketplace.json`、`.codex-plugin/plugin.json`。全部 Python 代码 38 文件约 4.8k 行，集中在 `skills/nvidia-kaggle-skill/scripts/`。

## 2. 五分钟心智模型：四条 HTTP 通道 + 三块本地存储

代码量小，真正的复杂度在**对 Kaggle 四个互不相同的 API 面的取舍**：

1. **官方 kaggle 库**（`KaggleApi`）：提交主管线专用——`skills/nvidia-kaggle-skill/scripts/submit_kernel.py:37` 惰性导入 `kaggle.api.kaggle_api_extended.KaggleApi`，push/status/submit 全走它。
2. **裸 REST `/api/v1`**（httpx + Bearer）：`skills/nvidia-kaggle-skill/scripts/kernels/kaggle_client.py:16` 基址 `https://www.kaggle.com/api/v1`，列表/元数据/notebook 下载；`skills/nvidia-kaggle-skill/scripts/discussions/discussion_client.py:44` 同款 GET。
3. **内部 web 服务 `/api/i`**（XSRF 会话）：`skills/nvidia-kaggle-skill/scripts/runtime.py:51` 基址；`KaggleWebServiceClient`（skills/nvidia-kaggle-skill/scripts/runtime.py:63）先 GET 首页取 `XSRF-TOKEN` cookie（skills/nvidia-kaggle-skill/scripts/runtime.py:74-75）再 POST。仅供公开 API 缺数据的地方：排行榜 writeup 链接（skills/nvidia-kaggle-skill/scripts/fetch_leaderboard_writeups.py:36-45 的 GetCompetition/GetLeaderboard）、论坛帖全文（skills/nvidia-kaggle-skill/scripts/discussions/discussion_client.py:274 `discussions.DiscussionsService/GetForumTopicById`）、**历史最优版本**（skills/nvidia-kaggle-skill/scripts/kernels/archive.py:24-26 三个 service 方法——REST 只暴露最新版，见 skills/nvidia-kaggle-skill/scripts/kernels/archive.py:6-7 docstring）。
4. **kagglesdk 类型化搜索**：`skills/nvidia-kaggle-skill/scripts/kernels/kaggle_search.py:11-20` 用 `SearchApiClient`+`ListEntitiesRequest` 查公开分数；讨论列表则走裸 `api.kaggle.com/v1/search.SearchApiService/ListEntities`（skills/nvidia-kaggle-skill/scripts/discussions/discussion_client.py:21）。

本地存储三件套：`data/kernels.db`（skills/nvidia-kaggle-skill/scripts/kernels/paths.py:11）、`data/discussions.db`（skills/nvidia-kaggle-skill/scripts/discussions/database.py:76）、`data/submissions.jsonl` 提交流水（skills/nvidia-kaggle-skill/scripts/submission_log.py:29），外加 `data/notebooks/` notebook 缓存（skills/nvidia-kaggle-skill/scripts/kernels/paths.py:15）。项目根定位用 `find_project_root`（skills/nvidia-kaggle-skill/scripts/runtime.py:208，`PROJECT_ROOT` 环境变量可覆盖），.env 由 `load_project_env`（skills/nvidia-kaggle-skill/scripts/runtime.py:228）装载。

## 3. 目录地图

| 目录/文件 | 职责 |
|---|---|
| `skills/nvidia-kaggle-skill/SKILL.md` | agent 契约总入口：frontmatter 权限（skills/nvidia-kaggle-skill/SKILL.md:5-10）+ 七类工作流分派（:65-148）+ 故障表（:157-168） |
| `skills/nvidia-kaggle-skill/*.md` | 渐进披露工作流文档：`kernels.md`/`submission.md`/`writeups.md`/`kernel-setup.md`/`research-brief.md` |
| `scripts/runtime.py` | 统一底座：slug/ref 解析、KaggleApi 认证、XSRF 客户端、HTML→markdown（skills/nvidia-kaggle-skill/scripts/runtime.py:178） |
| `scripts/kernels/` | kernels 域数据层：HTTP 客户端/SQLite/pydantic 模型/路径（四件套） |
| `scripts/discussions/` | 讨论域数据层：与 kernels 域同构（database/discussion_client/models/paths） |
| `scripts/kernel_*.py`+`discussion_*.py` | 域 CLI：ingest/query/read/db_info/archive 六个入口 |
| `scripts/submit_kernel.py` 等 | 提交主管线 + 限额 + 历史 + `upload_dataset.py` 数据集出口 |
| `tests/` | 三层防线：结构契约/管线单测/agent 验收清单（tests/agent_acceptance_test.md） |

## 4. 分层走读（图谱 10 层重组为四段）

**发布与契约层（L01-03）**：SKILL.md 是灵魂——frontmatter 声明 shell/network/env/file_read/file_write 五项权限边界（skills/nvidia-kaggle-skill/SKILL.md:5-10），正文把七类请求分派到脚本或子文档；`tests/test_day_one_skill_contracts.py:72` 用测试钉死渐进披露结构（四个能力文档必须在 SKILL.md 被引用）。多端发布：Claude Code 走 marketplace.json、Codex 走 `.codex-plugin/plugin.json:6`（skills 指向整个 `./skills/` 目录）。

**统一底座（L04）**：`runtime.py` 被几乎所有脚本 import——看懂它，每个 CLI 的前 20 行就不用再看。三个入口函数 `competition_slug`（skills/nvidia-kaggle-skill/scripts/runtime.py:14）/`kernel_ref`（:20）/`require_kaggle_token`（:28）承担全部输入归一化；凭据是单一 KGAT token `KAGGLE_API_TOKEN`，无 OAuth 流程。

**双研究域（L05-08）**：kernels 与 discussions **严格同构**——都是 client+database+models+paths 四件套配 ingest/query/read/db_info 四 CLI。差异在 API 形态：kernels 走 REST 分页（skills/nvidia-kaggle-skill/scripts/kernels/kaggle_client.py:117-131 page/pageSize 参数），discussions 走 pageToken 翻页（skills/nvidia-kaggle-skill/scripts/discussions/discussion_client.py:215-217）；讨论搜索按**竞赛标题**而非 slug 匹配（skills/nvidia-kaggle-skill/scripts/discussions/discussion_client.py:133-135 docstring 明说），所以有 slug→title 解析步（:130-146）。

**动作域（L09-10）**：提交主管线（见下）与数据集上传 `upload_dataset.py`——用户名从 KGAT token introspect（skills/nvidia-kaggle-skill/scripts/upload_dataset.py:39），协作者**必须走 SDK 单独打补丁**，因为 `dataset-metadata.json` 的 collaborators 字段被 CLI 静默忽略（skills/nvidia-kaggle-skill/scripts/upload_dataset.py:163 注释实证）。

## 5. 数据流与控制流：提交主管线

`submit_kernel.py` 是全仓唯一有状态的长管线，四段串联（:207-305 main）：

1. **读元数据**（:55-78）：`kernel-metadata.json` 必须有 `id`（:63）与 `code_file`（:68），缺一即 exit(1)。
2. **push**（:81-91）：`api.kernels_push` 推新版本，返回 `version_number`。
3. **轮询运行**（:94-120）：`kernels_status`，终态集 `{"COMPLETE","ERROR","CANCEL_ACKNOWLEDGED"}`（:98）；API 异常不致命，sleep 后继续（:108-111）；超时默认 86400s=24h（skills/nvidia-kaggle-skill/scripts/constants.py:18）、间隔 30s（skills/nvidia-kaggle-skill/scripts/constants.py:17）。
4. **提交+轮询评测**（:123-204）：`competition_submit_code` 带 `kernel_version`（:127）→ 按 `description==message` 在提交列表里找自己（:177-180），兜底取最新仅限默认时间戳消息（:181-185 注释解释了为何自定义消息不许兜底）→ COMPLETE 后取 `public_score`（:195）。

每次 submit/evaluation 都落一行 JSONL（:143/:153）；`submission_attempts`（skills/nvidia-kaggle-skill/scripts/submission_log.py:72-112）把评测事件折回最近一条**被接受且未评测**的同 key submit——失败重试不得吞掉早先成功提交的分数（:84-87 docstring）。限额由 `submission_quota.py` 前置守门：SDK 读 `max_daily_submissions`（:26-45），CLI CSV 数今日提交（:48-70，头部嗅探容忍弃用告警 :66），额度是**团队共享**而非按人（skills/nvidia-kaggle-skill/submission.md:58）。

## 6. 构建与运行

- Python ≥3.10（pyproject.toml:6）；运行期依赖按需装：`uv pip install httpx kaggle kagglesdk nbformat pydantic python-dotenv rich`（skills/nvidia-kaggle-skill/SKILL.md:53）。
- 凭据检查惯用 shell 断言 `: "${KAGGLE_API_TOKEN:?...}"`（skills/nvidia-kaggle-skill/SKILL.md:62）。
- 测试：`pytest`；集成测试打真 API，须 `--run-integration`（tests/conftest.py:25）；tests 通过 sys.path 注入 scripts 目录（tests/conftest.py:20）解决平铺 import。
- CI（.github/workflows/test.yml）跑结构契约+单测；license.yml 查 SPDX 头。

## 7. 设计决策与陷阱

- **消息即主键**：Kaggle 提交 API 不返回 ID，管线用时间戳默认消息防撞（skills/nvidia-kaggle-skill/scripts/submit_kernel.py:27-29），自定义消息则永不兜底——读史+匹配全靠它。
- **限额双源**：CLI 数行数拿不到提交人，SDK `submitted_by` 可以（skills/nvidia-kaggle-skill/scripts/submission_quota.py:138）——by-user 口径只有 SDK 路线。
- **best version 要走私货 API**：`kernel_read.py` 永远只拿最新版，:59-64 明确提示用 `kernel_archive.py` 抓历史最优（方向自动推断见 skills/nvidia-kaggle-skill/scripts/kernels/archive.py:196-205）。
- **search 按 title 不按 slug**：讨论搜索前必须解析标题，失败则裸 slug 兜底（skills/nvidia-kaggle-skill/scripts/discussions/discussion_client.py:167-170）。
- **comment_count 列表页恒 0**（skills/nvidia-kaggle-skill/scripts/discussions/discussion_client.py:254），ingest 抓详情时回填（skills/nvidia-kaggle-skill/scripts/discussion_ingest.py:61）。
- 429 专用退避：`wait = max(30, delay·2^attempt)`（skills/nvidia-kaggle-skill/scripts/kernels/kaggle_client.py:42-44）——指数但有 30s 地板。
- 日志永不抛异常（skills/nvidia-kaggle-skill/scripts/submission_log.py:33-37）：审计是 best-effort，不能反噬在途提交。

## 8. 新人上手指引

1. 先读 SKILL.md 全文 + submission.md，再动任何脚本——契约先行是本仓铁律（结构测试会咬人，tests/test_day_one_skill_contracts.py:65-69 连"uv run python"字样都禁）。
2. 跑通顺序建议：`fetch_competition_info.py <slug>`（纯打印，最安全）→ `kernel_ingest.py`+`kernel_query.py` → `submission_quota.py --as-json` → 最后才碰 `submit_kernel.py`。
3. 改 kernels 域前先看 discussions 域是否已有同构解——两域 90% 模式可复制；反之亦然。
4. 所有新落盘产物放 `data/` 下；`pyproject.toml` 的 sdist 排除表（:54-59）已把 `data/` 连同两个真实竞赛工作区一起挡在发布外。
5. 任何"再跑一次提交"的冲动，先 `submission_history.py`（本地零 API，skills/nvidia-kaggle-skill/scripts/submission_history.py:8-9）再决策——skills/nvidia-kaggle-skill/submission.md:42 的 "never rerun blindly" 是全仓唯一用 Critical 标注的段落。

（字数 6047（非空白字符）/锚 50）
