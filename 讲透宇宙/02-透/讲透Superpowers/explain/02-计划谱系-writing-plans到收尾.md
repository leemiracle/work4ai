# 02 · 计划谱系：writing-plans → executing-plans → 收尾

## 角色定位

计划谱系是 superpowers 交付进程的骨干三段：writing-plans 把已批准的 spec 翻译成逐任务的实施计划；executing-plans 在新会话里按计划顺序执行；finishing-a-development-branch 在全部任务完成后决定集成方式并清理现场。三者与上游 brainstorming、下游 TDD/子代理执行共同构成"设计→计划→执行→收尾"的完整闭环。

三段的分工哲学值得先记住：**writing-plans 假设执行者是个"热情但没有判断力、没有项目上下文、厌恶测试的初级工程师"**（README.md:15 的原话描述），所以计划必须自包含到令人发指——每步给出完整代码与验证命令；executing-plans 是无子代理平台的兜底路径，明文建议"有子代理就改用 subagent-driven-development"（skills/executing-plans/SKILL.md:14）；finishing 技能则把"接下来怎么办"这种开放问题收敛成编号菜单。

## 内部结构

**writing-plans（152 行）** 的骨架：开头宣告技能使用（SKILL.md:14），计划存 `docs/superpowers/plans/YYYY-MM-DD-<feature-name>.md`（SKILL.md:18）。Scope Check 要求 spec 若覆盖多个独立子系统就建议拆成多份计划、每份独立产出可测软件（SKILL.md:21-23）。File Structure 段先锁文件级分解——每个文件一个清晰职责、按责任而非技术层切分、大文件是"做了太多事"的信号（SKILL.md:25-34）。任务粒度钉到"一步一个动作（2-5 分钟）"：写失败测试、跑它确认失败、写最小实现、跑测试确认通过、提交——五步各自独立成步（SKILL.md:36-43）。计划文档头部强制包含 `For agentic workers` 指令行，声明必须用 subagent-driven-development（推荐）或 executing-plans 逐任务执行（SKILL.md:47-61）。任务模板给足 Files（Create/Modify 带精确路径甚至行号）+五步 checkbox（SKILL.md:63-104）。

**No Placeholders 是灵魂条款**（SKILL.md:106-114）：TBD/TODO/"稍后实现"/"加适当的错误处理"/"写测试覆盖上述内容（不给实际测试代码）"/"类似 Task N"（执行者可能乱序阅读）统统判为计划失败——每步必须含执行者需要的真实内容。Self-Review 三查（SKILL.md:122-132）：spec 覆盖（每条需求能指到对应任务吗）、占位符扫描、类型一致性（Task 3 的 `clearLayers()` 到 Task 7 变成 `clearFullLayers()` 就是 bug）。收尾 Execution Handoff 给用户两个选项：子代理驱动（推荐）或本会话内联执行（SKILL.md:136-144）。

**executing-plans（70 行精简版）**：加载计划→批判性审查（有疑虑先向人伙伴提出，SKILL.md:18-22）→逐任务按步执行→全部完成后强制移交 finishing-a-development-branch（SKILL.md:32-37）。停止条件清单：遇阻、计划有缺口、指令不懂、验证反复失败——"宁可问不要猜"（SKILL.md:39-47）。红旗含"未经用户明确同意不得在 main/master 上开工"（SKILL.md:63）。

**finishing-a-development-branch（251 行）**：五步流程"验证测试→检测环境→呈现选项→执行选择→清理"（SKILL.md:12）。测试不过必须停在 Step 1（SKILL.md:27-36）。环境检测用 `GIT_DIR==GIT_COMMON` 判普通仓库 vs linked worktree，detached HEAD 则菜单收缩为三项（SKILL.md:40-55）。标准菜单固定四项：本地合并/推送建 PR/保留分支/丢弃（SKILL.md:68-79），不加解释保持简洁（SKILL.md:93）。选项 4 丢弃要求用户逐字输入 'discard' 确认（SKILL.md:146-158）。清理按出处判定：只有 worktree 路径在 `.worktrees/`、`worktrees/` 或 `~/.config/superpowers/worktrees/` 下才是 superpowers 自建、拥有清理权，其余归宿主环境管（SKILL.md:171-192）。

## 外部连接

上游：brainstorming 的唯一出口是本谱系的 writing-plans；spec 与计划的目录约定（specs/plans 分离）由 v5.0.0 确立（RELEASE-NOTES.md:287）。下游：writing-plans 的 handoff 直通 subagent-driven-development（04 篇）或 executing-plans；executing-plans 完工后 REQUIRED SUB-SKILL 指向 finishing（SKILL.md:36）。横向：计划开头引用 using-git-worktrees 保证隔离工作区（writing-plans SKILL.md:16）；finishing 与 worktrees 技能通过目录约定强耦合——`.worktrees/` 前缀既是创建偏好也是清理权限边界。评审层：writing-plans 的质量控制曾靠派 plan-document-reviewer-prompt.md 子代理（49 行模板，校验完整性/spec 对齐/任务分解/可构建性，skills/writing-plans/plan-document-reviewer-prompt.md:18-34），v5.0.6 起被内联 Self-Review 三查取代（RELEASE-NOTES.md:100-107）。

## 数据流

一份计划的旅行：brainstorming 产出的 spec（含架构/组件/数据流/错误处理/测试覆盖，SKILL.md:91）→ writing-plans 把 spec 逐节映射为 Task N，每任务五步 checkbox、含真实代码与验证命令 → 计划文件落盘 `docs/superpowers/plans/` → 用户选择执行方式 → （内联路径）executing-plans 新会话加载计划、批判性审查、TodoWrite 建任务清单、逐步执行并在每步跑验证 → 全部完成后 finishing 接管：跑测试套件→读 GIT_DIR/GIT_COMMON→出菜单→执行所选（选项 1 先合并、在合并结果上再验测试、再清 worktree、最后删分支——顺序不可颠倒，SKILL.md:104-119）→清理或保留。测试夹具佐证：tests/subagent-driven-dev/go-fractals/plan.md:3 首行就是"Execute this plan using the superpowers:subagent-driven-development skill"，Do/Verify 结构正是本技能的规范输出格式。

## 设计决策

- **为零上下文执行者而写**：计划假设读者什么都不懂——这既是给弱模型兜底，也是给"未来的另一个会话"兜底；"类似 Task N"被禁因为任务可能被乱序、跨会话消费。
- **checkbox 是消费契约**：`- [ ]` 语法让计划文件本身成为执行追踪载体，两个执行技能都以 checkbox 驱动进度。
- **收尾菜单化对抗开放问题**：finishing 的 Common Mistakes 直指"接下来做什么？"式开放提问是歧义之源（SKILL.md:209-211）；四选项固定措辞让用户决策成本最小。
- **顺序纪律源自真实事故**：RELEASE-NOTES.md:18 记载 v5.1.0 修复的三个 bug——选项 2 误清 worktree（#940）、先删分支后删 worktree 导致 `git branch -d` 失败（#999）、在 worktree 内部执行 remove 静默失败（#238）；现技能明文"merge 成功确认前不删任何东西、删 worktree 前先 cd 回主仓"（SKILL.md:112,221-223）。
- **2026-04 rototill 重写**：worktree/finishing 两技能从"上来就 git worktree add"改为"检测→原生工具→兜底"三级，行为经 TDD 验证并跨五 harness 检查（RELEASE-NOTES.md:11-19）；v5.1.0 同时移除了技能尾部的 Integration 节（历史遗留，agents 有原生技能系统后无用）。

## 勘误与新人提示

勘误：docs/plans/ 下的历史计划引用了已迁移/删除的路径——2025-11-28-skills-improvements-from-user-feedback.md 引用 skills/testing-anti-patterns/SKILL.md（实际已迁至 skills/test-driven-development/testing-anti-patterns.md）；2025-11-22-opencode 两份文档写 `.opencode/plugin/`（单数，实际落地复数 plugins/）并引用已不存在的 lib/skills-core。RELEASE-NOTES 里 v5.0.0 之前"writing-plans 强制 subagent-driven、executing-plans 去批量化"的演化史（RELEASE-NOTES.md:293-299）与现行"恢复用户选择权"（v5.0.5，RELEASE-NOTES.md:127 附近）方向相反——读版本史别拿旧政策当现状。

新人提示：写计划前先跑 Scope Check，子系统级拆分在 brainstorming 就该发生；Self-Review 的类型一致性检查最容易漏（跨任务符号名漂移是 LLM 写长计划的通病）；finishing 的 detached HEAD 三选项菜单（SKILL.md:81-91）在外部管理的 worktree（如 Codex App 沙箱）会触发，此时没有任何清理权，只报告不动作。
