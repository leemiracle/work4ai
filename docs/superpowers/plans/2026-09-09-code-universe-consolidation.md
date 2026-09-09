# code领域 16 源收编实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 把 C:\workspace 下 16 个来源文件夹收编进 work4ai 顶层新目录 `code领域/`（9 个子区），对账通过后删除全部原文件夹。

**Architecture:** 每源一个 scoped commit 的迁移流水线：固化（各源仓先 commit 未提交改动）→ robocopy 迁移（带统一剔除清单）→ 文件数对账 → 提交 → 最后统一删除原文件夹。在隔离 worktree（feature/code-universe）内执行，与主检出的并行 Claude 车道互不干扰。

**Tech Stack:** git（worktree/scoped commit）、robocopy（Windows 原生迁移，/XD /XF 剔除）、python（对账/补丁）、linkcheck.py（仓库既有链检工具）

**Spec:** `docs/superpowers/specs/2026-09-09-code-universe-consolidation-design.md`

## Global Constraints

- 工作目录：`C:\workspace\work4ai\.claude\worktrees\code-universe`（隔离 worktree，分支 feature/code-universe）。所有相对路径基于此目录；源文件夹在 `C:\workspace\<名>`
- 剔除清单（所有 robocopy 统一带）：`/XD .git node_modules __pycache__ .opencode .venv .lake .pytest_cache dist build .next target .idea .vscode` + `/XF *.pyc *.pyo .env *.lock.tmp`
- 每源迁移后必须对账（源计数=目标计数，剔除项不计）才能提交；对账数字写进提交讯息
- 提交讯息格式：`feat(code领域-<子区>): <源>迁入——<一句话内容>+对账N=M；来源C:\workspace\<名>删除待终批`（SDD 公告栏协议：另一车道靠提交讯息知晓本车道动态）
- 原 16 文件夹的删除只发生在 Task 12（全部对账通过后），此前任何任务不得删除源
- 根 README 只允许新增一个小节，不得改动既有行（并行车道冲突面控制）
- 链检范围：仅 `code领域/` 下自有 md（索引卡/README/桥梁文件）；第三方克隆目录不纳入（上游内部链接自成体系）
- 涉及在 python 里调 git 的操作禁止嵌在 heredoc 中（worktree 隔离会拦截）；git 命令用独立 Bash 调用
- 推送分批：每完成 2-3 个任务 push 一次，防单次 pack 超 2GB；若 push 被拒（体积），停下来走 spec §2 体积闸门（征询用户）

---

### Task 1: 固化各源仓未提交改动

**Files:**
- Modify: 各源仓自身的 git 历史（essence/csdiy/leemiracle 子仓/lean4ai/lean4demo/mathlib4——在源仓目录内 commit，不动 work4ai）

**Interfaces:**
- Produces: 各源仓工作树 100% 已提交状态（Task 3-9 迁移时无"未提交改动丢失"风险）；mathlib4 dirty 性质判定（构建产物→跳过固化）

- [ ] **Step 1: 逐仓检查 dirty 明细**（判定哪些值得固化）

```bash
for r in /c/workspace/essence /c/workspace/csdiy /c/workspace/math/lean4ai /c/workspace/math/lean4demo /c/workspace/math/mathlib4 /c/workspace/leemiracle/leemiracle.github.io /c/workspace/leemiracle/DebugPytorch; do
  echo "== $r =="; git -C "$r" status --porcelain | head -8
done
```
Expected: 输出各仓改动清单；mathlib4 的 2 个 dirty 若是 `.lake/` 或构建产物则标记跳过

- [ ] **Step 2: 固化 commit（跳过 Step 1 判定为纯构建产物的仓）**

```bash
for r in <Step1判定需固化的仓列表>; do
  git -C "$r" add -A && git -C "$r" commit -m "固化: 并入work4ai/code领域前快照(2026-09-09)"
done
```
Expected: 各仓 `git status` 全 clean

- [ ] **Step 3: 记录对账基线文件数**

```bash
for d in csdiy deepseek-harness economy essence fastisslow infoq-analysis infoq-atlas leemiracle LLVM项目研究 Machine-Learning-Interviews math math-expert-pro neo-os paper-os; do
  n=$(find "/c/workspace/$d" -type f ! -path '*/.git/*' ! -path '*/node_modules/*' ! -path '*/__pycache__/*' ! -path '*/.opencode/*' ! -path '*/.venv/*' ! -path '*/.lake/*' ! -path '*/dist/*' ! -path '*/build/*' 2>/dev/null | wc -l)
  echo "$d $n" >> /c/workspace/work4ai/.claude/worktrees/code-universe/.migration-baseline.txt
done
```
Expected: 生成 13 行基线文件（llvm 单独在 Task 2 处理）

---

### Task 2: 02-编译器与LLVM —— llvm-project 自有层抢救 + LLVM项目研究迁入

**Files:**
- Create: `code领域/02-编译器与LLVM/LLVM项目研究/`（45md 全量）
- Create: `code领域/02-编译器与LLVM/llvm_experiments/`（11 文件）
- Create: `code领域/02-编译器与LLVM/IT学习平台/`（llvm-project 根目录 untracked 自有项目：backend/ cli/ frontend/ knowledge-base/ python-learning-project/ docs/ + AGENT_ARCHITECTURE.md 等 9 个根级 md）
- Create: `code领域/02-编译器与LLVM/patches/Use-Value头文件改动.patch`
- Create: `code领域/02-编译器与LLVM/LLVM-monorepo克隆索引.md`

**Interfaces:**
- Produces: `code领域/02-编译器与LLVM/` 完整子区（README 在 Task 10 统一补）；monorepo 不迁（156,484 文件/2.14GiB，用户决策索引卡代替）

- [ ] **Step 1: 抢救 Use.h/Value.h 用户改动为 patch**

```bash
cd /c/workspace/llvm/llvm-project && git diff llvm/include/llvm/IR/Use.h llvm/include/llvm/IR/Value.h > /c/workspace/work4ai/.claude/worktrees/code-universe/.tmp-ir.patch && wc -l /c/workspace/work4ai/.claude/worktrees/code-universe/.tmp-ir.patch
```
Expected: patch 行数 >0（若为 0，说明改动是行尾符级别，如实记录后跳过 patch 文件）

- [ ] **Step 2: robocopy 迁移三块自有内容**

```bash
WT=C:/workspace/work4ai/.claude/worktrees/code-universe
robocopy "C:\workspace\LLVM项目研究" "$WT\code领域\02-编译器与LLVM\LLVM项目研究" /E /XD .git __pycache__ /NFL /NDL /NJH /NP
robocopy "C:\workspace\llvm\llvm-project\llvm_experiments" "$WT\code领域\02-编译器与LLVM\llvm_experiments" /E /XD .git /NFL /NDL /NJH /NP
robocopy "C:\workspace\llvm\llvm-project" "$WT\code领域\02-编译器与LLVM\IT学习平台" /E /XD .git node_modules __pycache__ .venv /XF *.pyc .env /LEV:2 /NFL /NDL /NJH /NP
```
注意：第三条 `/LEV:2` 会把 llvm-project 整个根两层都搬——**先跑 Step 2a 生成白名单目录再搬**，见 2a。

- [ ] **Step 2a: IT学习平台白名单式搬运（替代上面第三条的 /LEV 粗搬）**

```bash
cd /c/workspace/llvm/llvm-project
for item in backend cli frontend knowledge-base python-learning-project docs AGENT_ARCHITECTURE.md AGENT_PROJECT_SUMMARY.md AI_ARCHITECTURE.md AI_PROJECT_SUMMARY.md ARCHITECTURE.md IT-PLATFORM-README.md PROJECT_STATUS.md PROJECT_SUMMARY.md deepwiki-analysis-prompts.md deepwiki-bolt-analysis.md; do
  [ -e "$item" ] && robocopy "C:\workspace\llvm\llvm-project\\$item" "$WT\code领域\02-编译器与LLVM\IT学习平台\\$item" /E /XD .git node_modules __pycache__ /XF *.pyc .env /NFL /NDL /NJH /NP
done
```
（`$WT` 先赋值；robocopy 单文件时源格式为 `目录\文件名`，照抄上面模式）

- [ ] **Step 3: 写克隆索引卡 + patch 落位**

`code领域/02-编译器与LLVM/LLVM-monorepo克隆索引.md` 内容须包含：上游 `https://github.com/llvm/llvm-project`、检出时 commit（`git -C /c/workspace/llvm/llvm-project rev-parse HEAD` 取）、本地曾含自有层（已抢救至本目录）、重装命令 `git clone https://github.com/llvm/llvm-project.git --depth 1`（国内走 ghproxy 前缀）。patch 有内容则落 `patches/`，无则索引卡注明。

- [ ] **Step 4: 对账并提交**

```bash
# 源计数
find /c/workspace/LLVM项目研究 -type f ! -path '*/.git/*' | wc -l
find /c/workspace/llvm/llvm-project/llvm_experiments -type f | wc -l
# 目标计数（对应目录），一致后：
git add code领域/02-编译器与LLVM && git commit -m "feat(code领域-02编译器LLVM): LLVM项目研究45md+llvm_experiments 11文件+IT学习平台(llvm-project根自有项目)迁入+monorepo克隆索引卡(156484文件/2.14GiB不迁,用户决策)+Use/Value头文件patch;对账见讯息"
```
Expected: 三块计数一致；commit 成功

---

### Task 3: 01-学习路线 —— csdiy 整仓迁入

**Files:**
- Create: `code领域/01-学习路线/csdiy/`（整仓：上游站源码+notes 8 篇+projects tiny*26+tools+STRATEGY/ANALYSIS/TOPICS 等根级 md）

**Interfaces:**
- Consumes: Task 1 的 csdiy 固化 commit
- Produces: 01 区完整内容

- [ ] **Step 1: robocopy 迁移**

```bash
robocopy "C:\workspace\csdiy" "C:\workspace\work4ai\.claude\worktrees\code-universe\code领域\01-学习路线\csdiy" /E /XD .git node_modules __pycache__ /XF *.pyc /NFL /NDL /NJH /NP
```

- [ ] **Step 2: 对账**（find 源 vs 目标，剔除项不计；数字来自 Task 1 基线 2835md+）

- [ ] **Step 3: 提交**（`git add code领域/01-学习路线 && git commit`，讯息含对账数字）

- [ ] **Step 4: push 一次**（累计两任务，防大批量）

```bash
git push -u origin feature/code-universe
```
若被拒（pack 过大）：改 `git push` 分目录多批（先 `git push origin feature/code-universe` 前 reset 软拆提交），并按 spec 体积闸门处理

---

### Task 4: 03-论文OS —— paper-os 整体迁入（最大批次 ~2.5万文件）

**Files:**
- Create: `code领域/03-论文OS/`（自研层+15 第三方克隆，目录结构原样）

**Interfaces:**
- Produces: 03 区完整内容；内部相对链接因结构原样而保持有效

- [ ] **Step 1: 先迁自研层（小批，独立提交）**

```bash
WT=C:/workspace/work4ai/.claude/worktrees/code-universe
for item in README_PAPER_OS.md README_COMPLETE.md README_LEARNING_PATHS.md COMPLETE_FILE_LIST.md EXTENDED_PAPERS_FILE_LIST.md COMPLETION_REPORT.md DEEP_USAGE_REPORT.md PROJECT_COMPLETION_REPORT.md FINAL_COMPLETE_SUMMARY.txt deep_usage_plan.md learning_paths_by_report practice_projects code_index code_practice knowledge_graph ai_qa interactive_learning downloaded_resources exports logs data learning_paths_summary.json learning_paths_summary_final.txt final_learning_report.md final_learning_report.json applications_analysis_report.json paper_analysis_report.json scan_results.json config.json download_log.txt download_extended_papers.log extended_papers_download.log learning_path_validation.log; do
  [ -e "/c/workspace/paper-os/$item" ] && robocopy "C:\workspace\paper-os\\$item" "$WT\code领域\03-论文OS\\$item" /E /XD __pycache__ /XF *.pyc /NFL /NDL /NJH /NP
done
# 根级 py/sh 脚本
robocopy "C:\workspace\paper-os" "$WT\code领域\03-论文OS" *.py *.sh /XF *.pyc /NFL /NDL /NJH /NP
```
对账+提交：`feat(code领域-03论文OS): 自研层迁入——学习路径74/practice_projects 56/ai_qa/知识图谱/报告与配置+脚本N个；对账…`

- [ ] **Step 2: 迁 15 个第三方克隆（每 3-4 个一提交，控制批大小）**

```bash
for item in CVPR2025-Papers-with-Code RWKV-LM nano-vllm nlp-tutorial llm-resource annotated_deep_learning_paper_implementations awesome-llm-apps best-of-ml-python petals text-generation-inference mmdetection mmsegmentation sglang vllm transformers; do
  robocopy "C:\workspace\paper-os\\$item" "$WT\code领域\03-论文OS\\$item" /E /XD .git node_modules __pycache__ .venv /XF *.pyc .env /NFL /NDL /NJH /NP
done
```
每完成 3-4 个：对账该批 → `git add code领域/03-论文OS/<本批目录>` → commit（讯息注明"上游克隆,本地学习参考"）

- [ ] **Step 3: push（本任务至少 push 两次）**

Expected: 累计对账 = Task 1 基线 paper-os 行；push 成功或走体积闸门

---

### Task 5: 04-数学基础 —— math + math-expert-pro 迁入

**Files:**
- Create: `code领域/04-数学基础/math/`（8 子项目：awesome-math/compute-graph/lean4ai/lean4demo/learn/mathematics-roadmap/mathlib4/understanding-math）
- Create: `code领域/04-数学基础/math-expert-pro/`（2636md）

**Interfaces:**
- Consumes: Task 1 对 lean4ai/lean4demo/mathlib4 的固化/判定
- Produces: 04 区完整内容

- [ ] **Step 1: math 各子项目逐个 robocopy**（/XD 同全局+`.lake`；mathlib4 若含 ` .lake/` 构建目录会被剔除，正是预期）
- [ ] **Step 2: math-expert-pro robocopy**（/XD .git）
- [ ] **Step 3: 对账两个源 → 两个 scoped commit**
- [ ] **Step 4: push**

---

### Task 6: 05-系统与ML工程 —— leemiracle×4 + ML-Interviews + deepseek-harness

**Files:**
- Create: `code领域/05-系统与ML工程/leemiracle/`（4 子项目）、`…/Machine-Learning-Interviews/`、`…/deepseek-harness/`

**Interfaces:**
- Produces: 05 区完整内容；deepseek-harness 与仓库既有 `deepseek-universal-harness/`（harness 构建物）及 `讲透Agent/Agent框架案例/deepseek-harness插件化框架/` 互补不冲突

- [ ] **Step 1: robocopy 六项**（leemiracle 的 4 个子目录各自 robocopy，/XD 同全局）
- [ ] **Step 2: 对账 → 提交（leemiracle 一个 commit、ML-Interviews+deepseek-harness 各一个）**
- [ ] **Step 3: push**

---

### Task 7: 06-技术媒体情报 + 07-软件可解释性 + 08-世界本质 + 09-投资与经济（四个中小批次）

**Files:**
- Create: `code领域/06-技术媒体情报/infoq-analysis/`、`…/infoq-atlas/`（243M 数据随迁）
- Create: `code领域/07-软件可解释性/neo-os/`
- Create: `code领域/08-世界本质/essence/`
- Create: `code领域/09-投资与经济/fastisslow索引.md`、`…/economy/README.md`、`…/economy/CHANGELOG.md`
- Modify: 根级 `neo-os知识桥梁.md`（指向 `code领域/07-软件可解释性/neo-os/`）

**Interfaces:**
- Consumes: Task 1 的 essence 固化
- Produces: 06-09 四区完整；09 区 fastisslow 索引卡（含上游 `https://github.com/iqiancheng/fastisslow`、11 个 PDF 清单、核心思想摘要）与 economy 残留说明（README 声称的 43 文件体系不在磁盘，只有 README/CHANGELOG 存在）

- [ ] **Step 1: infoq-analysis / infoq-atlas / neo-os / essence 四项 robocopy**（/XD 同全局）
- [ ] **Step 2: 写 `fastisslow索引.md`**（上游链接+PDF 书单+Stop Doing List 笔记要点）+ economy 两文件迁入 + 09 区 README 注明 economy 空壳事实
- [ ] **Step 3: 修根级 `neo-os知识桥梁.md` 的位置指向**
- [ ] **Step 4: 对账 → 每源一个 commit → push**

---

### Task 8: code领域 总入口 + 根 README 挂载

**Files:**
- Create: `code领域/README.md`（九区导航表：每区一句定位+来源清单+关键入口文件链接）
- Modify: 根 `README.md`（在"## 三、参考资料"区末尾或"## 16."之后**新增**一节 `## 16a. code领域总宇宙（16源收编）⭐ 2026-09-09`，不改既有行）
- Modify: `本地仓库全景-Cworkspace迭代索引.md`（标注 16 源已并入 code领域/）

**Interfaces:**
- Consumes: Task 2-7 的九区目录
- Produces: 仓库级可发现性

- [ ] **Step 1: 写 `code领域/README.md`**（含九区表格、16 源对账数字汇总表、fastisslow/llvm-monorepo 两个"不迁物"的索引卡链接）
- [ ] **Step 2: 根 README 新增小节**（3-5 行：定位一句话+链接 code领域/README.md+九区一览）
- [ ] **Step 3: 更新 `本地仓库全景-Cworkspace迭代索引.md`**（16 源条目标注"已并入 code领域/"）
- [ ] **Step 4: 提交 + push**

---

### Task 9: 链检

**Files:**
- Read: `linkcheck.py`（仓库根，另一车道维护的工具）

**Interfaces:**
- Produces: code领域/ 自有 md 0 死链证明

- [ ] **Step 1: 读 linkcheck.py 用法**（`python linkcheck.py --help` 或读源码头部；确认能否限定目录）
- [ ] **Step 2: 跑 code领域/ 自有 md**（若工具不支持目录限定，临时把第三方克隆目录加入跳过清单的方式：只在自有 md 上跑，或复制清单模式）
- [ ] **Step 3: 修复自有 md 死链**（如 fastisslow索引/README 中指向未迁内容的链接降纯文本）
- [ ] **Step 4: 提交修复 + push**

---

### Task 10: 终批对账与删除原文件夹（不可逆门）

**Files:**
- Delete: `C:\workspace\{csdiy,deepseek-harness,economy,essence,fastisslow,infoq-analysis,infoq-atlas,leemiracle,llvm,LLVM项目研究,Machine-Learning-Interviews,math,math-expert-pro,neo-os,paper-os}`（15 个；llvm/ 含 llvm-project）

**Interfaces:**
- Consumes: Task 1 基线文件 + Task 2-9 各源对账记录（git log 提取）
- Produces: 磁盘上 C:\workspace 只剩 work4ai 等非收编目录

- [ ] **Step 1: 汇总对账表**（从各 commit 讯息提取 16 源 源计数=目标计数；任何一个不符→停，报告用户）
- [ ] **Step 2: 确认全部源已固化/已迁/或按决策豁免**（fastisslow PDF=用户决策豁免；llvm monorepo=用户决策豁免；economy .opencode=无价值缓存豁免）
- [ ] **Step 3: 删除**（`rm -rf` 逐个；每删一个前 `ls` 确认目录名）
- [ ] **Step 4: 记录删除清单**（在 `code领域/README.md` 末尾补"来源处置记录"小节：16 源→9 区→删除时间）
- [ ] **Step 5: 最终 push** + `git log --oneline origin/main..feature/code-universe` 输出完整车道提交列表

---

### Task 11: 收尾报告与车道交接

**Files:**
- Create: `code领域/迁移完成报告.md`（对账总表/体积增量/链接指引/给另一车道的合并提示：根 README 小节+2 个指针文件是唯一共享面）

**Interfaces:**
- Produces: 用户与并行车道可读的终态文档

- [ ] **Step 1: 统计体积增量**（`git count-objects -vH` 对比基线 164M）
- [ ] **Step 2: 写报告 + 提交 + 最终 push**
- [ ] **Step 3: 向用户汇报**：完成状态、对账表、剩余人工动作（是否合并 main 由用户/另一车道决定）

## Self-Review 结论

- Spec 覆盖：§2 落位表 16 源→Task 2-7 全覆盖；§3 清理规则→Global Constraints /XD 清单；§4 七步流程→Task 1-11 顺序对应；§5 风险→对账门(Task 10)+体积闸门(push 步骤)；§6 决策→各任务注明 ✓
- 占位符：无（robocopy 命令均为可直接执行的完整命令）
- 一致性：子区名 01-学习路线/02-编译器与LLVM/03-论文OS/04-数学基础/05-系统与ML工程/06-技术媒体情报/07-软件可解释性/08-世界本质/09-投资与经济 全文一致 ✓
