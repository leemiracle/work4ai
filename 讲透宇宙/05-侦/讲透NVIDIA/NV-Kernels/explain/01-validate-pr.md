# 01 · .github/scripts/validate-pr — PR 提交卫生的判定引擎

## 1. 角色定位

`validate-pr` 是 NV-Kernels 仓（`github-actions` 孤儿分支）最重的逻辑资产：1086 行、无扩展名 Python 3，回答一个问题——PR 里每个 commit 是否"干净、可溯源、与上游等价"。内核分支是稳定内核上的补丁叠层，卫生程度决定日后 rebase 成本，所以它挂在 PR 门禁跑（`.github/workflows/patchscan.yml:L284-292`），任一 `E:` 级错误即 CI 失败；同时是 612 行黑盒测试的唯一被测对象。纯校验器：只读 git 对象与 lore，退出码是唯一控制信号。

## 2. 内部结构

- **trailer 解析族**（`L34-76`）：`get_cherry_pick_sha` 匹配 `(cherry picked from commit <sha> [linux-next])`（`L34-38`）；`get_upstream_commit_sha` 合并三种溯源（`L44-50`）；`get_linux_next_patch_url` 从 `Link:` trailer 挑补丁链接且 patch.msgid.link 优先（`L71-73`）。
- **等价性四层判定（灵魂）**：`get_patch_id` 用 `git patch-id --stable`，zero-context 变体（`L160-165`）加 `--unified=0` 抗上下文漂移；`is_equivalent_replay`（`L394-466`）在临时 `GIT_OBJECT_DIRECTORY` 隔离环境里 `git merge-tree` 重放（`L424-447`），tree 相同即等价；冲突≠不等价——`is_equivalent_by_anchored_edits`（`L360-391`）要求两侧有序编辑载荷一致（`L349-351`）且每个编辑块有一侧相邻上下文在双父版本中唯一（`L309-335`）。
- **SoB 审计**：`missing_sob_lines` 用 Counter 做多重集差（`L107-115`）；URL 型 backport 走 `describe_sob_chain_backport`（`L502-547`），规定"原作者 trailer → 溯源 trailer → [Name: note] → backporter SoB"。
- **b4/lore 对比**：`check_backport_diff`（`L701-755`）用 `_diff_fingerprint`（`L611-619`，只哈希 +/- 内容行）比对本地与 lore diff，差异且无 `[Author: note]` 才算 MISMATCH。
- **主流程**：`build_digest`（`L758-925`）分四类出表；`lint_commits`（`L928-989`）跑 R5-R10；`check_pr_metadata`（`L994-1020`）跑 R1/R3（tracked 分支须带 Launchpad BugLink，`L992`）；`main` 串联，`all_errors` 非空即 `sys.exit(1)`（`L1081-1082`）。

## 3. 外部连接

imports GitPython/colorama；`b4` 以子进程调用（`L654`）。依赖 `origin/linux` ref（`L1032-1034` assert）；上游 SHA 解析不到时定向 fetch，注释明言依赖 GitHub"按 SHA fetch 任意可达对象"（`L856-866`）。消费方：`patchscan.yml` 用 `grep -qE "^E:"/"^W:"` 分类输出（yml `L300-306`）；`test_validate_pr.py` 子进程黑盒驱动。**`E:`/`W:` 前缀是与 yml 层的接口契约**。

## 4. 数据流

输入 `check_range`+`upstream_remote/branch`，可选 `--pr-title/--pr-body/--base-branch`。`main` 开仓（`L1024`）→ 枚举 commit → `build_digest` 解析/拉取/patch-ID/重放 → `lint_commits` 再扫 → `check_pr_metadata`。输出 Unicode 表格（`L561-577`，红/绿行）+ W/E 列表 + 退出码；错误消息带 `sha12 ("subject")` 前缀，人机两读。

## 5. 设计决策

- **递进且 fail-closed**：patch-ID→zero-context→merge-tree 重放→锚定编辑证明，逐层收紧；任何一层证据不足（patch-id 畸形 `L186-193`、merge-tree 未知格式 `L204-230`、二进制/增删 blob `L385-387`、编辑块超 128 `L286-288`）一律 False 并打 `W: unable to verify`——宁可报警不猜。
- **linux-next 困境显式建模**：其 SHA 每日重建、CI 解析不到，此时报"必须补公共 Link: trailer"而非"无法解析"（`L869-876`）——把数据缺陷转成对贡献者的可执行指令。
- **【勘误】docstring 与实现不一致**：`check_backport_diff` docstring 写二元组（`L704`），实际三元组（`L718/L755`，调用方 `L807/L838` 三解包）；状态串写 `'annotated'`（`L709`），实际返回 `'noted'`（`L753`）。
- **【勘误】规则编号有洞**：只有 R1/R3/R5-R10（`L941-1007`），R2/R4 全仓零命中——编号引自外部 backport 规范全集，本脚本只实现八条。
- 分级刻意：R5/R6/R8 是 error，R7/R9/R10 是 warning；R9 豁免 SAUCE/UBUNTU，因前缀已吃掉 12-20 字符（`L957-959`）。

## 6. 新人提示

改正则先同步 `test_validate_pr.py`（22 用例全围绕这些 trailer 建 fixture）。**动输出格式必须看 yml 消费端**：`E:`/`W:` 前缀被 grep/awk 消费，改前缀=改跨文件 API。b4 失败归 `fetch-err` 非 error（`L725-727`），别改成硬失败。新规则延续 `R<n>` 编号并想清楚分级。
