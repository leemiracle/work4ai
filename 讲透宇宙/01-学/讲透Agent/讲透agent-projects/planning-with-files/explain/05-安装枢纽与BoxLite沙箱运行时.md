# 05 · 安装枢纽与 BoxLite 沙箱运行时（分发线与隔离线）

> 对应图谱 L9「安装枢纽与沙箱运行时」，tour t11。核心文件：`docs/installation.md`（169 行）、`docs/boxlite.md`（191 行）、`examples/boxlite/quickstart.py`（122 行，仓库唯一可运行 Python 示例）。

## ① 角色定位

`docs/installation.md` 是全部 16 平台安装路径的**总枢纽**——四条安装方法+验证/更新/卸载全生命周期，其余平台分册都从这里分流出去。`docs/boxlite.md` 是矩阵里唯一的**沙箱运行时**分册（README.md:112-118 特意单列并注明"BoxLite is a sandbox runtime, not an IDE"）：把 Claude Code+本技能装进硬件隔离 micro-VM 跑不可信代码。`examples/boxlite/quickstart.py` 是ClaudeBox Skill 注入 API 的可运行样例。三者合起来回答"怎么装、装到哪、装进笼子怎么办"。

## ② 内部结构

**installation.md** 四方法阶梯：方法1 插件安装（docs/installation.md:18-31，marketplace add+install 两命令，优势=自动更新+完整钩子）；方法2 手动安装三选项——直接 clone 进 `.claude/plugins/`（docs/installation.md:38-43）、git submodule（docs/installation.md:45-49）、`claude --plugin-dir` 临时挂载（docs/installation.md:51-56）；方法3 Legacy 纯技能安装（docs/installation.md:60-67，只拷 skills/ 到 ~/.claude/skills/）；方法4 单行安装器（docs/installation.md:71-79，curl tar.gz 解压抽取技能目录）。后接验证（docs/installation.md:83-90，期待看到 Ready 消息）、更新（docs/installation.md:92-113 三法各一条命令）、卸载（docs/installation.md:115-135）、Requirements（docs/installation.md:139-143：Claude Code v2.1.0+ 才有完整钩子支持）、平台分流（docs/installation.md:146-163 链 windows/cursor/codex/opencode 四分册）。

**boxlite.md** 六节：Overview（docs/boxlite.md:7-18）——BoxLite 定位 "SQLite for sandboxing"（docs/boxlite.md:9，可嵌入库、每 box 独立内核而非 namespace），ClaudeBox 是其官方 Claude Code 集成层，技能以 Skill 对象在启动时注入 VM 文件系统（docs/boxlite.md:11）；四大卖点（docs/boxlite.md:13-18）——硬件隔离跑不可信代码、规划文件经 `~/.claudebox/sessions/` 跨会话持久（docs/boxlite.md:15）、快照回滚、三钩子照常工作；Prerequisites（docs/boxlite.md:22-27，Python 3.10+/Docker 仅管 OCI 镜像/ANTHROPIC_API_KEY）；Quick Start 代码（docs/boxlite.md:48-103）——Skill 对象 files dict 注入+首会话建计划+`ClaudeBox.reconnect()` 续会话（docs/boxlite.md:96-98）+cleanup_session（docs/boxlite.md:100）；VM 内钩子表（docs/boxlite.md:107-117）；Snapshots（docs/boxlite.md:134-154，snapshot("pre-refactor")→出错则 restore）；Troubleshooting 四问（docs/boxlite.md:158-179）。

**quickstart.py**：`load_skill()` 从本地 `~/.claude/skills/planning-with-files/` 读 SKILL.md（examples/boxlite/quickstart.py:28-29）与 check-complete.sh（examples/boxlite/quickstart.py:30），未装则抛 FileNotFoundError 并贴安装命令（examples/boxlite/quickstart.py:32-38）；files dict 把两文件映射到 VM 内路径 `/root/.claude/skills/...`（examples/boxlite/quickstart.py:40-48）；main 用 `/planning-with-files:plan` 命令+一个 JWT 认证任务驱动 VM（examples/boxlite/quickstart.py:71-76）。

## ③ 外部连接

installation.md 是 docs/ 树的根节点：上链 README 徽章与 Quick Install 区，下链 16 平台分册（本文四条+平台分册线详见本系列第 6 篇）。boxlite.md 依赖三个外部件：pip 包 claudebox（docs/boxlite.md:35）、GitHub 仓 boxlite-ai/claudebox（docs/boxlite.md:11）、Docker（docs/boxlite.md:25，仅镜像管理）；See Also 还链 boxlite-mcp（docs/boxlite.md:187）。quickstart.py 依赖**本地已安装的技能副本**（examples/boxlite/quickstart.py:28）——它不从本仓读文件，跑之前必须先装技能。v2.18.0 把 BoxLite 集成进主干（README.md:50）。

## ④ 数据流

标准安装线：marketplace.json→插件缓存→`CLAUDE_PLUGIN_ROOT` 生效→SKILL.md 的钩子/模板/脚本全部可用（skills/planning-with-files/SKILL.md:24 即引用该变量）。沙箱线另有四站：宿主读本地技能→Skill(files={VM路径:内容})（examples/boxlite/quickstart.py:40-48）→VM 启动时注入 `/root/.claude/skills/`（docs/boxlite.md:11）→规划文件写进 box 工作目录、经有状态 workspace 持久化于 `~/.claudebox/sessions/`（docs/boxlite.md:15）→跨会话 reconnect 复用同一 workspace（docs/boxlite.md:96-98）。快照流是旁路：危险阶段前 snapshot→响应含 error 则 restore 回滚（docs/boxlite.md:143-151）。会话恢复在 VM 内降级为手动：让 agent 自己跑 session-catchup.py（docs/boxlite.md:123-130）。

## ⑤ 设计决策与陷阱

- **四方法能力不均**：只有插件法承诺"完整钩子支持"（docs/installation.md:29-30）；Legacy/单行法只拷技能，SKILL.md 里 `${CLAUDE_PLUGIN_ROOT}` 类引用（skills/planning-with-files/SKILL.md:24、skills/planning-with-files/SKILL.md:42、skills/planning-with-files/SKILL.md:58）在无插件根时会落空——docs/installation.md:141 明示旧版 Claude Code "hooks may not fire"。选安装法=选强制力等级。
- **quickstart.py 只注入两个文件**：SKILL.md+check-complete.sh（examples/boxlite/quickstart.py:40-48），PreToolUse/PostToolUse 是 SKILL.md frontmatter 内联命令不依赖外部脚本所以能活，但模板没注入——VM 内模型只能凭 SKILL.md 正文重建三件套。docs/boxlite.md:171 也承认"Hooks not running? → 把 check-complete.sh 加进 files dict"。
- **"Docker 依赖"易误解**：Docker 只拉 OCI 镜像，沙箱本体是 micro-VM（docs/boxlite.md:175 明确"the sandbox itself does not run as a Docker container"）；Windows 宿主必须走 WSL2+KVM（docs/boxlite.md:179）。
- **安装器路径漂移风险**：方法4 的 tar 解包 strip-components=2 依赖仓目录层级稳定（docs/installation.md:76），上游挪动 skills/ 深度即静默断链。
- BoxLite 持久化与 Claude Code 原生 session-catchup 是两套恢复机制：前者 workspace 级（文件全在），后者对话级（找未同步消息）——VM 场景下手跑 catchup 仍是补充（docs/boxlite.md:123-130）。

## ⑥ 新人提示

普通用户走方法1 两行命令（docs/installation.md:8-10）后立即按 docs/installation.md:87-89 验证 Ready 消息；对钩子没把握就别用 Legacy 法——省下的安装步骤会在运行期还债。想体验 BoxLite：先在宿主装好技能再跑 quickstart.py（否则 examples/boxlite/quickstart.py:32-38 直接报错）；把它当作"给 agent 的一次性实验笼"——快照点选在破坏性阶段前（docs/boxlite.md:144 的 pre-refactor 命名是好习惯）。运维视角记住两个持久化路径的分工：插件缓存在 `~/.claude/plugins/`，沙箱工作区在 `~/.claudebox/sessions/`，排障先确认文件落在哪一侧。
