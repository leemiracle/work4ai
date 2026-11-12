# 02 · patchscan 脚本 + patchscan.yml — pull_request_target 的安全门禁范式

## 1. 角色定位

这一对文件组成 PR Validation 工作流：`patchscan`（174 行无扩展名 Python 3，作者署名 Canonical，`.github/scripts/patchscan:L2`）是 **backport 审计员**——验证 cherry-pick 溯源真实、反查上游 `Fixes:` 修复是否已同步；`patchscan.yml`（434 行）是**编排与安全壳**，以 `pull_request_target` 触发（`.github/workflows/patchscan.yml:L4-10`，4 个 linux-nvidia 目标分支），串起 patchscan 与 validate-pr 并把结果贴回 PR 评论。`pull_request_target` 在 base 上下文运行、能拿写权限，是公认危险触发器——本 yml 因此成为"安全使用它"的教科书案例。

## 2. 内部结构

**脚本侧**：`get_src_commit_strs`（`L29-37`）只认三种显式 trailer（cherry picked/backported from commit、行首 Upstream commit），散文里 informal 提到的 SHA 故意不匹配防误报（`L34-35`）；`is_upstream`（`L42-69`）四连验证——SHA 可解析（`L51`）、标题逐字相同（`L57`）、作者相同（`L61`）、上游分支 `--contains`（`L65`）；`check_fixes`（`L81-114`）对每个溯源 SHA 在 `<src>..upstream` 区间 `git log --grep "Fixes: <sha8>"` 反查修复（`L96-101`），`has_fix`（`L71-79`）过滤本地已有；`main`（`L119-171`）里 `verification_failed` 只由溯源失败置位，末尾 `sys.exit(1)`（`L169-171`，`import sys` 是函数内延迟导入）。

**yml 侧**：元数据正则防线（`L40-127`）——SHA 必须 40 位 hex（`L102-106`），base_ref 拒 `..`/尾斜杠/`.lock`（`L107-113`，全是 git ref 陷阱）；checkout base 且 `persist-credentials: false`（`L129-134`）；PR 提交经显式 `git fetch refs/pull/N/head` 落为远端引用、从不 checkout（`L162-164`）；标题正文走 `gh api`+jq 落文件（`L181-183`）；脚本本体从 `origin/github-actions` 取（`L185-191`）。判定收口 awk 三态（`L246-256`）：`All fixes:` 后有 `Fixes for` 行→缺修复；有标记无条目→干净；**无标记→脚本崩溃，归 error**。评论由 `github-script@v9` upsert：更新既有 bot 报告而非重发（`L399-418`），30000 字符截断保头 60% 尾 40%（`L319-329`），escapeHtml 防注入（`L330-334`）。

## 3. 外部连接

脚本 import GitPython/colorama；yml 依赖 `actions/checkout@v6`（`L130`）、`setup-python@v6`、`github-script@v9`（`L310`）；上游参考统一 `origin/linux`（`L203-205`）。**脚本输出格式即接口**：awk 找 `All fixes:`/`Fixes for`，grep 找 `^E:`/`^W:`（`L300-306`）——改打印语句等于改协议。权限最小化 `pull-requests: write, contents: read`（`L26-28`）。

## 4. 数据流

PR 事件（或 dispatch 的 PR 号，可跨仓 `inputs.repo`）→ 元数据校验 → checkout base → fetch PR head 对象 → 取脚本装依赖、fetch origin/linux → `merge-base..head` 区间（`L219-220`）先 patchscan（PIPESTATUS 取真实退出码，`L234`）再 validate-pr → 去 ANSI 分类 → PR Validation Report 评论（Patchscan + PR Lint 两节图标化）→ `Fail on errors`（`L420-434`）：缺修复或验证错误或 lint error 任一命中即 exit 1。

## 5. 设计决策

- **为何选 pull_request_target**：要评论 PR 且支持 dispatch 扫任意仓 PR；代价是 secrets 可见，于是全套补偿——永不 checkout/执行 PR 代码、不可信数据一律经 `env:` 中转进 shell（`L137-141` 模式，杜绝 `${{ }}` 直插 run 的注入）、正则白名单前置。
- **【甄别】action 并非 SHA 钉**：本 yml 用 `@v6`/`@v9` tag ref，kernel-build.yml 用更旧 `@v4`，全仓唯一 SHA 钉在低频自测 validate-pr-tests.yml。防护重心在输入面而非 action 供应链。
- **"缺修复"判定在 yml 不在脚本**：patchscan 对 missing fixes 只打 W: 不置失败（`L112`），fail 语义由 awk 文本分类实现，脚本崩溃也归 error 失败——fail-closed。
- **跨仓扫描不发评论**：`if: ... pr_repo == github.repository`（`L309`），异仓无评论权限，结果只留 Actions 日志。
- **【勘误】README 过时**：称只针对 `24.04_linux-nvidia-6.17-next`（`README.md:L20`），实际 4 分支（`L6-10`）。
- 小瑕疵：`has_fix` 两条件等价冗余（`L76`）。

## 6. 新人提示

改脚本输出必须同步 awk/grep 分类逻辑；改触发分支清单要同步 README 与 validate-pr 的 `TRACKED_BRANCH_RE`。新增不可信字段先过正则再进 shell，维持 env 中转模式。评论 upsert 靠 `github-actions[bot]` 身份与标题串匹配，改报告标题会孤儿化旧评论。
