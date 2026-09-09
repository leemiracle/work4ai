# code领域 总宇宙收编设计（16 源合并进 work4ai）

> 日期：2026-09-09 · 车道：feature/code-universe（隔离 worktree）· 状态：已获用户批准

## 1. 目标与定位

在 work4ai 新建顶层 `code领域/`，把 C:\workspace 下 16 个来源文件夹按 code 主题重组收编（用户选定方案 A：总宇宙收编全部，含非 code 内容作为"code 人视角"子区）。收编完成后**删除全部原文件夹**，work4ai 成为唯一本体。既有讲透宇宙不动；根 README 仅新增一个挂载小节。

并行约束：另一 Claude 会话在主检出（feature/math-universe 车道）实时工作。本车道在 `.claude/worktrees/code-universe` 隔离作业，基于 `origin/main`(b617a684)；改动面收敛于 `code领域/` 新目录 + 根 README 新增小节 + 2 处指针文件修正；合并时手工处理根 README。

## 2. 落位总表（16 源 → 9 区）

| 子区 | 收编内容 | 处理决策 |
|---|---|---|
| `01-学习路线/` | csdiy 整仓（上游 cs-self-learning 站源码 2835md + 自有笔记层 8 篇 + tiny* 26 项目 + STRATEGY/ANALYSIS 反思 + tools） | 全搬 |
| `02-编译器与LLVM/` | LLVM项目研究（45md，Expert_01..13）+ llvm_experiments（11 文件）+ IT学习平台（llvm-project 根目录 untracked 自有项目：backend/cli/frontend/knowledge-base/python-learning-project + 架构文档）+ `LLVM-monorepo克隆索引.md` | 自有层搬入；156,484 文件/2.14GiB 的 monorepo 只留索引卡（上游 URL+commit+重装命令）；用户改过的 Use.h/Value.h 保存为 patch 文件 |
| `03-论文OS/` | paper-os 整体（自研层：学习路径 74 文件/practice_projects 56/ai_qa/知识图谱 + 15 个第三方克隆 transformers/sglang/vllm/mmdetection/mmsegmentation/annotated_dl/RWKV-LM/nano-vllm/nlp-tutorial/CVPR2025/awesome-llm-apps/best-of-ml-python/llm-resource/TGI/petals），目录结构原样保留→内部链接不断 | 全搬（~2.5 万文件） |
| `04-数学基础/` | math 整仓（awesome-math/compute-graph/lean4ai/lean4demo/learn/mathematics-roadmap/mathlib4/understanding-math）+ math-expert-pro 整仓（2636md） | 全搬 |
| `05-系统与ML工程/` | leemiracle 全部 4 子项目（Awesome-ML-SYS-Tutorial 克隆/DebugPytorch/corex/leemiracle.github.io）+ Machine-Learning-Interviews 克隆（27md）+ deepseek-harness 官方克隆（2355md，与仓库既有 deepseek-universal-harness/ 无重复，互补） | 全搬 |
| `06-技术媒体情报/` | infoq-analysis（36md 十维分析）+ infoq-atlas（54md + 243M 数据/neo4j/dashboard） | 全搬 |
| `07-软件可解释性/` | neo-os 整仓（56md）；更新根级 `neo-os知识桥梁.md` 指向新位置 | 全搬 |
| `08-世界本质/` | essence 整仓（259md 跨学科知识库，88 个未提交改动先固化） | 全搬 |
| `09-投资与经济/` | `fastisslow索引.md`（上游仓链接+书单+笔记要点；11 个段永平 PDF 为第三方版权物**不迁**，随原文件夹删除）+ economy 仅 README.md/CHANGELOG.md（README 描述的 43 文件体系不在磁盘上，如实注明） | 索引化 |

**体积闸门**：分批提交、逐批推送；若实测单批 pack 超 GitHub 2GB 推送上限，对 transformers/vllm/sglang/mathlib4 等纯参考源码树回退 gitignore（本地保留不进 git），回退前征求用户确认。

## 3. 清理规则（迁入时一律剔除，不迁）

- `node_modules/`、`__pycache__/`、`.opencode/`、`.venv/`、`.env`
- 构建产物：`.lake/`、`dist/`、`build/`、`*.egg-info`
- **所有嵌套 `.git/` 目录**（否则 git add 会生成损坏的 gitlink 条目）
- economy 的 `.opencode/` 全部内容（node_modules 缓存无价值）
- llvm-project 的 Windows symlink 误报文件（34 个 M/D 状态的 symlink 测试文件，非用户改动）

## 4. 执行流程

1. **协调**（已完成）：fetch → 从 origin/main 切 feature/code-universe → 隔离 worktree。前置修复：origin/main 上 24 个 DeepWiki 文件名含半角冒号（NTFS 非法致 Windows 无法检出），已用 mktree 树重建改名（66efcef5）+ 13 处 INDEX 链接同步（e1e7e121）
2. **固化**：对有未提交改动的自有仓（essence 88/csdiy 40/leemiracle.github.io 6/lean4demo 8/DebugPytorch 2/lean4ai 1）在各自仓内 `git add -A && commit`，历史固化后再迁
3. **迁移**：robocopy 按落位表逐源搬迁（套用 §3 剔除清单），每源一个 scoped commit（SDD 协议：提交讯息即公告栏）
4. **对账**：每源迁移前后文件数比对（剔除项单列），账目一致才进入第 6 步
5. **收尾件**：`code领域/README.md` 总入口（九区导航+来源索引）+ 根 README 新增挂载小节 + `neo-os知识桥梁.md`/`本地仓库全景-Cworkspace迭代索引.md` 指针修正 + Use.h/Value.h patch 落盘
6. **删原文件夹**：对账通过后删除 16 个原文件夹（.git 历史已在第 2 步固化于各仓，或本就无价值）
7. **链检与推送**：linkcheck.py 跑 code领域/ 自有 md（第三方克隆目录不纳入链检范围——上游内部链接自成体系，外部链接非本仓责任）；分批推 feature/code-universe；**不自行合并 main**（留给用户/另一车道决定）

## 5. 风险与回滚

- 不可逆点在第 6 步（删除原文件夹）；此前全程可回退。essence/csdiy 等的 .git 历史删除前已固化在其各自仓内——若需恢复，git 对象仍在其原仓目录中，直至删除生效
- 与并行车道的冲突面收敛于根 README：合并时手工处理
- paper-os 第三方克隆含大量上游版权文件（Apache/MIT 源码+文档）——作为本地学习参考整体入库，合规风险低但仓库体积显著增加（用户已知情并选择）
- mathlib4 的 2 个 dirty 若为 `.lake/` 构建产物则不固化，仅源码改动有价值
- infoq-atlas 的 243M 数据含爬虫 json——按"全搬"决策入库；若推送遇阻走体积闸门

## 6. 已获批准的决策记录

| 决策点 | 用户选择 |
|---|---|
| code领域语义 | 方案 A：新建总宇宙收编全部，非 code 内容入 09 等子区 |
| 第三方克隆 | 全部搬入仓库（fastisslow PDF 除外） |
| 原文件夹处置 | 先固化（各仓 commit）→ 迁移 → 对账 → 删除 |
| fastisslow PDF | 只留索引，PDF 不迁随原文件夹删 |
| llvm-project monorepo | 只迁自有层 + 克隆索引卡 |
| 执行模式 | 自动继续直到全部完成 |
