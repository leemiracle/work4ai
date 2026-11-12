# 02 · SKILL.md 契约与 kernels/discussions 双研究域

## 一、角色定位

本仓的产品不是库而是**契约**：`skills/nvidia-kaggle-skill/SKILL.md`（173 行）是 agent 运行时唯一必读文件，frontmatter 声明五项权限（shell/network/env/file_read/file_write，skills/nvidia-kaggle-skill/SKILL.md:5-10），正文把七类自然语言请求（竞赛上下文/简报/writeups/讨论/kernels/复现/提交/数据集）分派到脚本或子文档。契约的执行主体是两个**严格同构的研究域**：kernels 与 discussions，各四件套数据层 + 四个 CLI，把 Kaggle 的公开智力资产抓进本地 SQLite 供 agent 离线检索（本篇锚相对 `skills/nvidia-kaggle-skill/`）。

## 二、内部结构

**契约层**：SKILL.md 的分派规则是"quick task 直接给命令，复杂工作流指向子文档"（skills/nvidia-kaggle-skill/SKILL.md:67-69），四个能力文档 `writeups.md/kernels.md/kernel-setup.md/submission.md` 按渐进披露原则存在且必须被 SKILL.md 引用——这不是约定而是测试：`tests/test_day_one_skill_contracts.py:72-80` 逐文件断言。

**kernels 域**（`scripts/kernels/`）：
- `skills/nvidia-kaggle-skill/scripts/kernels/kaggle_client.py:16` 裸 REST `/api/v1` + KGAT Bearer；`list_kernels` 用 page/pageSize 数字分页（:117-131），空页/短页即停（:133, :150-152）。
- `skills/nvidia-kaggle-skill/scripts/kernels/database.py:15-27` SQLite `kernels` 表，主键 `(competition_id, kernel_ref)`，外加 `competition_info` 表（:29-39）与两索引（:41-44）。
- `skills/nvidia-kaggle-skill/scripts/kernels/models.py:23-33` pydantic `KernelMetadata`；`NotebookContent.render_readable`（skills/nvidia-kaggle-skill/scripts/kernels/models.py:55-66）把 cell 渲染成带执行序号的 markdown。
- `kernels/notebook_reader.py`：下载缓存到 `data/notebooks/<comp>/<sanitized-ref>/`（:37-38），缓存目录出现多个 .ipynb 直接 raise（:45-49）。

**discussions 域**（`scripts/discussions/`）完全镜像：`discussions/discussion_client.py` 列表走 `api.kaggle.com` 搜索服务（:21），详情走 `/api/i` XSRF 会话调 `GetForumTopicById` 递归展开评论树（:264-328）；`skills/nvidia-kaggle-skill/scripts/discussions/database.py:17-52` 三表（discussions/discussion_comments/competition_info），评论表外键 `ON DELETE CASCADE`（:51）。

## 三、外部连接

两域共用的管道在 `runtime.py`：输入归一化（`competition_slug` :14、`kernel_ref` :20）、官方 API 实例（:36-48）、XSRF web 客户端（:54-130）。上游消费方是 SKILL.md 分派（讨论 :104-121、kernels :123-125）；下游喂给 agent 的研究工作流——`research-brief.md` 教 agent 把竞赛页+讨论+kernel 分数串成开题简报，`fetch_top_kernel_scores.py` 与 `kaggle_search.py` 供"抄谁"的选型数据（`skills/nvidia-kaggle-skill/scripts/kernels/kaggle_search.py:61` 的 `best_public_score`+`has_linked_submission`）。

## 四、数据流

以"研究某竞赛的公开 kernels"为例：

```
agent → kernel_ingest.py <slug> ─→ KaggleKernelClient.list_kernels（分页抓全）
      ─→ KernelDatabase.upsert_kernels（ON CONFLICT 更新，skills/nvidia-kaggle-skill/scripts/kernels/database.py:91）
agent → kernel_query.py <slug> --search X --min-votes N
      ─→ query_kernels（参数化 SQL+排序白名单 skills/nvidia-kaggle-skill/scripts/kernels/database.py:145-148）
agent → kernel_read.py owner/slug ─→ NotebookReader（缓存未命中才下载）
      ─→ render_readable → rich Markdown 输出
```

讨论线同构：`discussion_ingest.py` 列表入库后逐帖抓详情——列表页 `comment_count` 恒 0（`skills/nvidia-kaggle-skill/scripts/discussions/discussion_client.py:254`），由详情的 `total_messages` 回填（`skills/nvidia-kaggle-skill/scripts/discussion_ingest.py:61`）。

## 五、设计决策

- **按竞赛标题搜索而非 slug**：Kaggle Search API 只认 title（`skills/nvidia-kaggle-skill/scripts/discussions/discussion_client.py:133-135` docstring），故有 `_resolve_competition_title`（:130-146）+ slug 兜底链（:167-170）。
- **排序白名单防注入**：`query_kernels` 的 `allowed_sort`（skills/nvidia-kaggle-skill/scripts/kernels/database.py:145-148）与 discussions 的对应集合（skills/nvidia-kaggle-skill/scripts/discussions/database.py:178）——ORDER BY 无法参数化，白名单是唯一解。
- **两套分页协议并存**：REST 数字页 vs 搜索 `pageToken`（skills/nvidia-kaggle-skill/scripts/discussions/discussion_client.py:215-217）——域同构不等于协议同构，client 层各自吸收差异。
- **重试策略分档**：kernels 客户端 6 次重试且 429 专用 `max(30, 5·2^attempt)` 指数地板退避（skills/nvidia-kaggle-skill/scripts/kernels/kaggle_client.py:42-44）；runtime web 客户端 3 次/2s 线性（skills/nvidia-kaggle-skill/scripts/runtime.py:63）——抓列表的更耐打。
- **权重即排序**：两域默认按 votes/total_votes DESC（skills/nvidia-kaggle-skill/scripts/kernels/database.py:43 索引专门为它建），社区投票是免费的预筛器。

## 六、新人提示

- 改任何脚本前先过契约测试：`tests/test_day_one_skill_contracts.py:49-59` 连目录名自命名、manifest 精确映射都断言；SKILL.md 里禁出现 "uv run python"（:69，依赖策略是"装进当前环境"而非隔离子环境）。
- 新增域内功能时先问"另一个域是不是已经有了"——`db_info`/`query`/`read`/`ingest` 四件 CLI 在两域一一对应，复制模式再改协议细节。
- 空查询结果先查库再查网：skills/nvidia-kaggle-skill/SKILL.md:164 的故障表把"空结果"第一归因定为"没跑过 ingest"。
- notebook 缓存多 .ipynb 会 raise 而非猜（skills/nvidia-kaggle-skill/scripts/kernels/notebook_reader.py:45-49）——宁停不蒙是本仓检索链的一致哲学。

（字数 3240（非空白字符）/锚 22）
