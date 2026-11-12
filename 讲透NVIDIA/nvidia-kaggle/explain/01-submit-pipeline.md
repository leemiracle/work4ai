# 01 · submit_kernel.py — 提交主管线：push→poll→submit→poll 与槽位守卫

## 一、角色定位

`skills/nvidia-kaggle-skill/scripts/submit_kernel.py`（309 行）是全仓唯一有状态的长时管线，也是唯一能把"每日提交槽"这个稀缺资源花出去的脚本（本篇锚相对 `skills/nvidia-kaggle-skill/`）。它把本地 kernel 文件夹推上 Kaggle、等它跑完、把产物提交给竞赛、再等评测出分。工作流契约写在 `skills/nvidia-kaggle-skill/submission.md:3`，脚本本体只是这份契约的执行器。配套三件：`submission_log.py`（JSONL 审计）、`submission_quota.py`（事前守门）、`submission_history.py`（事后读史）。

## 二、内部结构

四段流水（`skills/nvidia-kaggle-skill/scripts/submit_kernel.py:207-305` 的 main）：

1. **元数据校验**（:55-78）：`kernel-metadata.json` 必须含 `id`（:63）与 `code_file`（:68），二者缺一直接 `sys.exit(1)`——错误信息打到 stderr 供 agent 读取。
2. **push**（:81-91）：`api.kernels_push(kernel_path)` 返回 `version_number`；`-v N` 参数可跳过 push 直接提交历史版本（:259-266）。
3. **运行轮询**（:94-120）：`api.kernels_status(slug)`，终态集 `{"COMPLETE","ERROR","CANCEL_ACKNOWLEDGED"}`（:98）；单次 API 异常只打日志继续睡（:108-111）——网络抖动不该杀掉已在 Kaggle 侧跑着的 kernel。默认 30s 间隔/24h 超时取自 `skills/nvidia-kaggle-skill/scripts/constants.py:17-18`。
4. **提交与评测轮询**（:123-204）：`api.competition_submit_code(file, message, competition, kernel=slug, kernel_version=version)`（:127）→ 轮询 `competition_submissions` 列表按 `description == message` 找回自己（:177-180）→ COMPLETE 取 `public_score`（:195）。

审计穿插其间：submit 与 evaluation 事件各落一行 JSONL（:143 与 :153 的 `append_record`）。

## 三、外部连接

- **上游**：`kernel-metadata.json`（push 协议由 Kaggle CLI 生态定义）；`skills/nvidia-kaggle-skill/SKILL.md:131-133` 把"push, poll, or submit"请求分派到本管线。
- **下游**：`data/submissions.jsonl`（`skills/nvidia-kaggle-skill/scripts/submission_log.py:29`）被 `submission_history.py` 读取渲染；`submission_quota.py` 不依赖它（独立双源）。
- **依赖面**：官方 kaggle 库（:37 惰性导入）、`constants`、`submission_log`——不碰 httpx，不碰内部 /api/i，是全仓唯一纯官方 API 的网络路径。

## 四、数据流

```
kernel-metadata.json ─→ read_kernel_metadata ─→ {slug, code_file, competition_sources, ...}
     │                                                      │
     │                                            kernels_push → version N
     ▼                                                      ▼
poll_kernel(slug) ──status──> terminal? ──→ competition_submit_code(--file, message, N)
     ▼                                                      ▼
submissions.jsonl ◄─append_record─ poll_submission(message 匹配) ──→ public_score
```

关键设计：**message 是事实主键**。Kaggle 提交 API 不返回可回查的 ID，管线靠提交列表里的 description 字段反认。默认消息带 UTC 时间戳防重（:27-29 注释明说防"exact-match collisions"）；自定义 `--message` 匹配不到时**永不兜底**——:181-185 注释给出理由：拿列表第一条冒充，可能报告的是别人/别次的提交状态。

## 五、设计决策

- **槽位经济学**：一次成功提交烧一个每日名额，所以 skills/nvidia-kaggle-skill/submission.md:42 用全仓唯一的 "Critical" 段落禁止盲目重跑；`submission_log.append_record` 永不抛异常（`skills/nvidia-kaggle-skill/scripts/submission_log.py:33-37`）——审计写失败不能反噬在途提交。`logged_at` 时间戳最后写入防调用方覆盖（:41-46）。
- **读史合并算法**（`skills/nvidia-kaggle-skill/scripts/submission_log.py:72-112`）：evaluation 折回最近一条**同 (competition,message) 且 accepted 且未评测/timeout** 的 submit（:96-101）——被拒重试不得吞掉早先成功提交的分数；timeout 不是终态，后到的评测可覆盖。
- **限额双实现**：CLI CSV 数行（`skills/nvidia-kaggle-skill/scripts/submission_quota.py:48-70`，:66 头部嗅探容忍弃用告警）与 SDK `submitted_by` 归因（:138）并存；`limit_fallback=5` + `limit_source` 字段（:219）诚实标注限额来源。
- **多竞赛循环**（:282-289）：`competition_sources` 是列表，逐个提交逐个轮询，任一失败置 `overall_success=False` → exit(1)（:304-305），退出码对 agent 可判。

## 六、新人提示

- `--file` 是 kernel 在 `/kaggle/working/` 里写的文件名，不是本地路径（skills/nvidia-kaggle-skill/submission.md:11 表格钉死）；不传则只跑不提交并打印提示（:279-280）。
- 长跑前 `PYTHONUNBUFFERED=1` + 后台运行（skills/nvidia-kaggle-skill/submission.md:33-40）；重跑前先 `submission_history.py`——它零 API 零凭据（`skills/nvidia-kaggle-skill/scripts/submission_history.py:8-9`）。
- 18 个单测（`tests/test_submission_history.py`）覆盖了合并算法全部边界：坏行跳过（:58）、永不抛（:74）、失败尝试不吞分（:119）、timeout 可覆盖（:136）、时间戳权威（:166）——改合并逻辑先跑它们。

（字数 2887（非空白字符）/锚 12）
