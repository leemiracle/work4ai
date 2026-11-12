# NV-Kernels 新人入门（ONBOARDING）

> 图谱基线：commit `c3d16b0f`，50 节点 / 57 边 / 6 层 / 12 步导览；行号锚均从源码核实。

## 1. 项目定位

NV-Kernels 的默认分支 `github-actions` 是一条**孤儿分支**：不是内核源码本体，而是挂在内核仓上的 CI 基础设施，只有 `.github/` 与 README 是自己的（`README.md:L44-48`）。它干三件事：把 linux-nvidia-6.6/6.12/6.18 每日 rebase 到 Greg KH 稳定 tag；x86_64 + ARM64 4K/64K 三档矩阵构建并跑 QEMU kselftest；对内核分支 PR 做 backport 溯源与提交卫生门禁。技术栈：4 条工作流 + 无扩展名 Python 3 脚本（validate-pr 1086 行、patchscan 174 行）+ git plumbing，pip 依赖仅 GitPython/b4/colorama。

## 2. 架构总览（六层）

- **L01 配置与依赖基座**：config_4k/config_64k 两份 .config 与 requirements.txt；两 config 同为 Linux 6.12.33 基线，仅 72 行差异定档页大小（`CONFIG_ARM64_64K_PAGES=y` 在 `.github/workflows/config_64k:L452`）。
- **L02 核心校验脚本引擎**：validate-pr（提交卫生全量校验）与 patchscan（cherry-pick 溯源 + Fixes 审计）。
- **L03 内核构建与同步流水线**：update-and-rebase.yml（每日 UTC 午夜 cron，`.github/workflows/update-and-rebase.yml:L4-5`）与被其复用的 kernel-build.yml。
- **L04 PR 质量门禁流水线**：patchscan.yml（pull_request_target 编排）与 validate-pr-tests.yml（脚本自测）。
- **L05 黑盒回归测试**：test_validate_pr.py，612 行 22 用例。
- **L06 项目文档总览**：README.md。

依赖方向：L04 编排 L02，L03 消费 L01，L05 验证 L02。

## 3. 核心链路

**构建线（每日心跳）**：cron → `prepare` 用 `git ls-remote --tags` 免克隆探测 gregkh/linux 最新稳定 tag 生成矩阵（`.github/workflows/update-and-rebase.yml:L39-43`）→ `update-rebase-branch`：tag 已存在则跳过，否则 `git rebase --onto`（`L105-108`）后强推 `<branch>-<tag>` 标签 → build-6-x job 以新 tag 为 `build_ref` 复用 kernel-build.yml（`L123-143`）→ 三档矩阵（`.github/workflows/kernel-build.yml:L27-33`）checkout、拉 config、vng 编译、QEMU 冒烟、跑 mm/dma/iommu/locking kselftest（`L91-98`）。

**PR 门禁线**：PR 触发 patchscan.yml（pull_request_target 面向 4 个 linux-nvidia 分支，`.github/workflows/patchscan.yml:L3-10`）→ 元数据正则校验 → checkout base 且 `persist-credentials: false`（`L134`）→ merge-base..head 区间依次跑 patchscan 与 validate-pr → github-script@v9（`L310`）发 PR Validation Report，更新既有 bot 评论而非重发（`L405-412`）→ 有 error 即 exit 1。validate-pr 主流程：溯源 trailer 解析 → patch-ID 粗筛 → merge-tree 重放 → 冲突时锚定编辑证明 → SoB/lint/元数据 → 任一 E: 级错误退出 1（`.github/scripts/validate-pr:L1081-1082`）。

## 4. 关键文件深读

**`.github/scripts/validate-pr`（1086 行，全仓最重资产）**。灵魂是等价性判定：`is_equivalent_replay`（`L394-466`）先比稳定 patch-ID，不等时退化比 zero-context patch-ID（抗上下文漂移），再在临时 `GIT_OBJECT_DIRECTORY` 隔离环境里 `git merge-tree --write-tree --merge-base=<上游父>` 重放上游补丁，tree 相同才算等价。冲突≠不等价：`is_equivalent_by_anchored_edits`（`L360-391`）要求两侧有序编辑载荷相同（`L338-357`）且每个编辑块有一侧相邻上下文在双父版本中唯一（`L309-335`）；patch-ID 由 `get_patch_id`（`L158-193`）严格校验。

**`.github/scripts/patchscan`（174 行）**。backport 审计员：`get_src_commit_strs`（`L29-37`）只匹配三种显式 trailer；`is_upstream`（`L42-69`）验证上游 SHA 可解析、标题/作者一致、被上游分支包含；`check_fixes`（`L81-114`）用 `git log --grep "Fixes: <sha8>"` 反查上游修复报缺失清单。

**`.github/workflows/patchscan.yml`（434 行）**。pull_request_target 能读密钥、属危险触发器，防护教科书：输入与元数据正则校验（`L41-67`）、checkout 关凭据（`L134`）、awk 分类输出（`L242-256`），脚本崩溃归 error 而非静默通过。

**`.github/scripts/test_validate_pr.py`（612 行）**。黑盒测试范式：setUp 建真实 git fixture（`L21-40`）；`_validate`（`L359-368`）以子进程跑被测脚本；`_fake_git_env`（`L237-298`）用假 git 包装器注入七种故障，未命中时透传真 git。

## 5. 模块间关系

- **workflow_call 复用**：update-and-rebase 的 build job `uses` kernel-build.yml（`.github/workflows/update-and-rebase.yml:L126`），`build_ref` 为唯一契约参数。
- **跨分支取物**：两工作流运行时都从 github-actions 分支拉资产——patchscan.yml 拉三个脚本（`.github/workflows/patchscan.yml:L196-204`），kernel-build 拉 config。内核分支无需携带 CI 文件，这是孤儿分支存在的主因。
- **依赖与基准**：b4 供 validate-pr 的 `check_backport_diff`（`.github/scripts/validate-pr:L701-755`），GitPython 供 patchscan，colorama 供着色；两脚本都以 `origin/linux` 为上游参考。
- **测试覆盖不对称**：test_validate_pr.py 只测 validate-pr，patchscan 无自测。

## 6. 构建与运行

本分支无需构建：

- **本地复现校验**：`pip install -r .github/scripts/requirements.txt` 后 `python3 .github/scripts/validate-pr <range> origin linux --no-update ...`，参数见 argparse（`.github/scripts/validate-pr:L14-30`）；patchscan 同签名。
- **回归测试**：`python3 .github/scripts/test_validate_pr.py -v`。CI 侧仅当 PR 改动脚本/测试/requirements.txt/工作流自身时触发（`.github/workflows/validate-pr-tests.yml:L7-11`），action 钉死 commit SHA（`L22`、`L27`）。
- **手动触发**：patchscan.yml 输 PR 号可扫任意 PR；kernel-build 有分支下拉。

## 7. 设计决策与取舍

1. **等价性验证的递进与 fail-closed**：patch-ID → zero-context → merge-tree 重放 → 锚定编辑证明；patch-id 畸形返回 None（`.github/scripts/validate-pr:L186-192`）、merge-tree 未知输出归 error（`L204-230`）、二进制 blob 判否（`L383-384`）、超限放弃证明（`L286-288`），宁可报无法验证也不猜。
2. **脚本与编排分工**：patchscan 对缺失修复只打黄色 W:，exit 1 仅由溯源失败触发（`.github/scripts/patchscan:L158-171`）；"缺修复即 CI 失败"由 yml 层 awk 判定。
3. **孤儿分支 + 默认分支组合**：linux 每日 `git reset --hard` 会抹掉追加提交，工作流须另立分支（`README.md:L50-54`）；cron 只在默认分支运行，故 github-actions 设为默认（`README.md:L56-58`）。
4. **【勘误】README 的 patchscan 分支清单过时**：README 称只针对 `24.04_linux-nvidia-6.17-next`（`README.md:L20`），实际 4 个分支（`.github/workflows/patchscan.yml:L5-10`），BugLink 要求正则也覆盖全系（`.github/scripts/validate-pr:L992`）。
5. **【勘误】README 工作流清单漏了第四条**：只列三条（`README.md:L5-42`），未提 validate-pr-tests.yml；另称 linux 为 "Torvalds' upstream mirror"（`L52`）而 rebase 上游实为 gregkh/linux 稳定树。
6. **【勘误】check_backport_diff 文档串与返回值不一致**：docstring 写 `'annotated'`（`.github/scripts/validate-pr:L708`），实际返回 `'noted'`（`L754`）。注入防护三件套（正则校验/关凭据/更新评论）见第 4 节。

## 8. 新人上路

**阅读顺序**：README（三分支模型）→ patchscan.yml（门禁全景）→ validate-pr 自顶向下（main 从 `.github/scripts/validate-pr:L1023` 起）→ test_validate_pr.py 学 fixture 手法。

**动手前必知**：
- 改 validate-pr 先本地跑通 22 用例——CI paths 过滤自动接手，摘要表格式改动必破坏逐行断言。
- 两个校验脚本**无扩展名**，shebang `#!/usr/bin/python3`（`.github/scripts/validate-pr:L1`）；改两份 config 保持最小 diff——价值恰在那 72 行差异。
- **永远不要往 linux 分支提交东西**：每日硬同步会静默抹掉；变更一律走 github-actions 分支 PR；新增内核分支要同步改两条工作流 options 与 README。
