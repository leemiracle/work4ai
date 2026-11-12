> 标题：发布边界回归测试——安全闸门、导出器与改名兼容性的验收单 · 源文件：tests/test_public_release.py（155 行）· 图谱标签：test / security / release-guard / packaging（图谱度数 in=3 / out=9）

## 角色定位

第 27 篇讲的 `scripts/check_public_release.py` 安全闸门与 `scripts/export_public_repo.py` 导出器，本文件是它们的回归验收单，外加第三重职责：**sys1mem→jev-mem 改名后的兼容性契约**。文件头自述（tests/test_public_release.py:1）："Regression tests for the release boundary and project-name compatibility"——两件事，一类测试。它在 CI 里随默认套件执行（`python -m pytest -q`，.github/workflows/ci.yml:29），且 CI 紧跟着跑 `--tracked` 扫描与 `python -m build`（.github/workflows/ci.yml:30-31），本文件就是这三步的第一道防线。

这个套件的特殊性在于**被测物是元级别**的：不是业务逻辑，而是"仓库对外暴露什么、打包什么、历史里藏着什么"。发布手册 docs/releasing.md 记载的人肉流程（默认扫描 docs/releasing.md:11、`--git-objects` 历史扫描 docs/releasing.md:12、导出后 `--all-files` 复验 docs/releasing.md:22-23），每一步的支撑函数都在这里被钉死行为。

## 内部结构

十一个测试函数，四族：

- **manifest 与打包同步**：`test_public_manifest_passes_and_excludes_local_data`（tests/test_public_release.py:15-24）对**真实仓库根**跑 scan_worktree，断言零 finding 且 .env.example/README/config 在清单、.env 与 data/locomo10.json 不在——闸门对自家仓库必须绿灯，这是其余一切的前提。`test_packaging_manifest_matches_release_allowlist`（tests/test_public_release.py:113-118）把 `MANIFEST.in` 的 include 行集合与 scan_worktree 的清单集合做全等断言——**发布 allowlist 与打包清单不允许漂移**，改一处不改另一处直接红。
- **私有物拒绝与凭据卫生**：`test_private_artifacts_are_rejected`（tests/test_public_release.py:26-31）参数化十一个路径（.env 家族、数据、图产物、results/reports/vectors、`../secret.txt` 穿越、.agents/settings.json）逐一断言 private_path 为真。`test_credentials_detected_without_printing_values`（tests/test_public_release.py:34-47）参数化八种凭据形状（apikey_/sk-/github_pat_/赋值式/hf_/xoxb-/HF_TOKEN=），断言既检出又**不在 findings 字符串里出现明文**（tests/test_public_release.py:47）——把第 27 篇讲的"只报位置不打印值"从实现细节升格为被测契约。`test_placeholder_env_and_endpoint_are_allowed`（tests/test_public_release.py:50-54）测反向：.env.example 空键放行，Azure 端点占位符 YOUR-RESOURCE 放行、真租户名 private-tenant 报 finding（tests/test_public_release.py:53-54）。
- **导出器与分层 Git 检查**：`test_export_is_allowlisted_and_refuses_overwrite`（tests/test_public_release.py:57-74）在 tmp_path 造迷你源树，断言 export 只拷 allowlist 两文件（.env 排除）、生成 SHA256SUMS、ZIP 名单精确等于三文件（tests/test_public_release.py:70-71）、二次导出抛 "already exists"（tests/test_public_release.py:72-73，对应 scripts/export_public_repo.py:22 的卫语句）。`test_release_refuses_symlinks`（tests/test_public_release.py:76-81）钉死符号链接绕过被拒。最精彩的是 `test_tracked_check_reads_index_not_working_copy`（tests/test_public_release.py:84-101）：subprocess 建真 Git 仓、写密钥、`git add`、再把工作树改成干净文本——scan_index 必须仍报**暂存区里的**密钥（tests/test_public_release.py:94-96），重新 add 干净版后 index 绿但 scan_git_objects 仍能在本地对象库找到旧 blob（tests/test_public_release.py:98-101）。一条测试讲清三层真相：工作树、索引、对象库，一层比一层顽固——这正是导出器不信任 Git 历史而从 allowlist 重抄新树的原因。`test_complete_release_check_finds_untracked_files`（tests/test_public_release.py:104-110）补全第四层：全树扫描对清单外文件同时报 "file outside public allowlist" 与 "private artifact path" 两个理由。
- **改名兼容与入口卫生**：`test_public_imports_and_saved_config_are_compatible`（tests/test_public_release.py:121-137）参数化新旧两个缓存配置文件名（jev_mem_config.json / sys1mem_config.json），先做三组 `is` 同一性断言（tests/test_public_release.py:128-129）——`memory.JevMemConfig`、`jev_mem.JevMemConfig`、直接 import 的 JevMemConfig 必须是**同一个类对象**，`main.JevMemSystem` 与 `JevMemSystem` 同理；再用 validate_reuse_memory 验证"检索参数可调、构造参数锁定"契约：anchor_count 改动可复用旧图（tests/test_public_release.py:135），candidate_top_k 改动抛 "construction settings"（tests/test_public_release.py:136-137，字段表在 jev_mem/benchmarks/locomo.py:54-56）。`test_cli_advertises_only_jev_mem_names`（tests/test_public_release.py:140-147）子进程跑 main.py 与 test_fixed_memory.py 的 `--help`：四个 jev flag 必须在场、旧名 "sys1" 必须绝迹（tests/test_public_release.py:145-147）——改名卫生的最终验收。`test_synthetic_locomo_example_loads`（tests/test_public_release.py:150-155）守护仓内合成数据集 examples/locomo_synthetic.json 的形状（一样本、两问、第二会话三轮）。

## 外部连接

import（tests/test_public_release.py:10-12）：`JevMemConfig` 直连 memory.jev_mem_config；check_public_release 六个函数（private_path/scan_content/scan_index/scan_worktree/scan_all_files/scan_git_objects，定义于 scripts/check_public_release.py:49 至 scripts/check_public_release.py:162）；export（scripts/export_public_repo.py:15）。函数内延迟 import 的兼容链最值得画：`from memory import JevMemConfig` 走 memory 包的 `_MODULES` 惰性 `__getattr__`（memory/__init__.py）；`from jev_mem import JevMemConfig` 走 jev_mem 包的 `_EXPORTS` 惰性转发（jev_mem/__init__.py，目标标 memory.jev_mem_config）；`from main import JevMemSystem` 走根垫片 main.py——它 `sys.modules` 整体替换成 jev_mem.cli（main.py:8），而 jev_mem/cli.py:15 import 了 JevMemSystem；`from test_fixed_memory import validate_reuse_memory` 同款垫片转发到 jev_mem/benchmarks/locomo.py:38。`from load_dataset import load_locomo_dataset`（tests/test_public_release.py:151）又是垫片→jev_mem/datasets/locomo。**这份测试同时是所有垫片与惰性转发机制的活性证明**。CI 侧被 .github/workflows/ci.yml:29 的 pytest 总命令拉起。

## 数据流

本地回路：开发者新增/改名文件→跑本套件→manifest 族与私有物族立刻对发布清单与内容扫描给出红绿；credential 族保证新代码里的密钥形状会被闸门抓住且不回显。CI 回路（.github/workflows/ci.yml:29-31）：pytest（含本文件）→`check_public_release --tracked`→`python -m build`——测试绿只是入场券，真正的发布流程仍按 docs/releasing.md 走导出与复验。兼容性回路：任何人在 memory 包、jev_mem 包、根垫片三层之间改动 import 面，同一性断言（tests/test_public_release.py:128-129）先于一切用户报错变红。

## 设计决策

**把安全属性写成属性测试**。"不打印密钥值"（tests/test_public_release.py:47）不是对某个函数输出的快照断言，而是对整条 findings 管线的属性约束——未来任何人往 Finding 或扫描器里加"方便调试"的值回显，这条立即抓住。同理，`is` 同一性断言钉住的是"无论从哪条路径 import 都拿到同一个类"，这是 sys.modules 垫片方案能成立的唯一充要条件。

**三层 Git 真相的正向教学**。test_tracked_check（tests/test_public_release.py:84-101）用真实 subprocess git 复现"暂存了密钥又改干净工作树"的经典事故姿势，验证 scan_index 读的是 `git cat-file blob` 取的暂存内容而非磁盘文件；末尾 scan_git_objects 仍报旧 blob（tests/test_public_release.py:100-101）则演示数据残留——这两段合起来是发布手册为什么要求 `--git-objects` 的可执行解释。

**值得记录的取舍与缝隙**：一，credential 检出测试的八种形状是样例集不是完备集，正则护栏的语义盲区（第 27 篇作者自认 "pattern guardrail, not a semantic privacy audit"）不会被本套件消除，只能被点名。二，`test_public_manifest_passes_and_excludes_local_data` 对真实仓库根跑（tests/test_public_release.py:16-17），意味着它同时是"仓库当前状态"的快照测试——本地若有未清理的私有产物，此测试在开发者机器上就会红，CI 上则永远针对 checkout 状态，两边的绿含义不同。三，CLI 卫生测试只跑两个入口脚本的 `--help`（tests/test_public_release.py:143-144），jev-mem 主 CLI 的帮助文本不在参数表里（它由 tests/test_project_layout.py 的 dispatch 测试覆盖，见第 35 篇）。四，validate_reuse_memory 的构造字段锁定依赖 jev_mem/benchmarks/locomo.py:54-56 的元组硬编码，新构造参数若忘加进元组，锁就漏——测试只能守住已列字段。

## 新人提示

先读 tests/test_public_release.py:84-101 的三层 Git 测试，它五分钟讲明白整个发布工具链的存在理由；再读 34-47 的凭据族看"检出但不回显"怎么测。跑法：`python -m pytest tests/test_public_release.py -q`，全程离线，tmp_path 自清理，唯一的真实仓库依赖是 manifest 族与 MANIFEST.in 族。

四个提醒：给 public-release-files.txt 加文件必须同步 MANIFEST.in（tests/test_public_release.py:113-118 会拦，但红在测试不如红在本地预检）；写新入口脚本先想清楚要不要进 py-modules 垫片体系——同一性断言的网只罩住已声明的名字；tests/test_public_release.py:121 参数表里的 sys1mem_config.json 是历史缓存名，删旧名支持前先看有没有线上缓存还在用；密钥测试里那些 "a"*32 拼出来的假凭据永远别改成真形状之外的变体去"测得更狠"——正则表是白名单式样例集，扩形状应该先扩 scripts/check_public_release.py 的 PATTERNS。
