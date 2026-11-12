# 05 · skill-creator 元技能：用技能造技能的生产线与评测工具链

> 仓根 = `/usr-data/data2/repos/agent-repos/anthropics/skills`，锚为仓根相对路径，行号现场核实。

## 1. 角色定位

`skills/skill-creator/` 是仓内唯一的**元技能**——SKILL.md 自我定义："一个用来创建和改进其它技能的技能"（485 行，`skills/skill-creator/SKILL.md`）。它把"技能怎么写、怎么测、怎么迭代"沉淀成可复跑的流程：本仓其余 18 个技能都是这条生产线的（或好或坏的）产物。它与 mcp-builder 构成两条元工程路线：前者管"指令包装"的技能，后者管"服务器实现"的技能。

## 2. 内部结构

- **`SKILL.md`**（485 行）：全流程操作手册。关键节：Skill Writing Guide 的 Anatomy 图（`:75-84`：SKILL.md 必需 + scripts/references/assets 三类可选资源）、**Progressive Disclosure 三级加载**（`:86-96`：metadata 恒在上下文约 100 词→SKILL.md 体触发即载理想 <500 行→bundled resources 按需无限，"scripts can execute without loading"）、Principle of Lack of Surprise（`:111-113`：技能不得含恶意代码、不得违背描述 surprises 用户）、评测五步（`:163-267`）、Description Optimization（`:333-408`）。
- **`scripts/` 八脚本**：`run_eval.py`（310 行，触发率评测）、`run_loop.py`（328 行，迭代循环+holdout）、`improve_description.py`（247 行，描述优化）、`generate_report.py`（326 行，HTML 报告）、`aggregate_benchmark.py`（401 行）、`package_skill.py`（136 行，打包 .skill）、`quick_validate.py`（102 行）、`utils.py`（47 行，frontmatter 解析）。
- **`agents/` 三角色**：comparator.md / analyzer.md / grader.md——comparator 对比 with-skill 与 baseline 产出 JSON，analyzer 归因差异（输入即 comparator 输出），grader 独立打分且罕见地把"**评估评估器**"写成一级职责。

## 3. 外部连接

- **Claude Code 自身是执行引擎**：`run_eval.py` 与 `improve_description.py` 都以子进程调 `claude -p`（`improve_description.py:20-23`：prompt 走 stdin 因为内嵌整个 SKILL.md，argv 会爆；`:30` 还特意摘掉 CLAUDECODE 环境变量以允许嵌套会话）。整条生产线**不直连 API**，全部经 Claude Code 的认证与会话层——技能吃自己的狗粮。
- **`utils.py` 是三脚手公共依赖**：`parse_skill_md()`（`utils.py:7`）手写扫描 `---` 界定的 frontmatter（`:12-13` 无开头即报错、`:22` 无闭合报错、`:38-39` 处理缩进续行的多行 description），被评测/改进/循环三脚本 import——**不引 PyYAML 的零依赖路线**。
- **对仓库其余技能**：skill-creator 的 Writing Guide 就是其余 18 个技能形态的"宪法"——docx 的分派表、internal-comms 的瘦路由、claude-api 的超长 description 都能在 Anatomy/Progressive Disclosure 框架里对号入座。

## 4. 数据流：一次"创建→评测→迭代"循环

1. **意图捕获+访谈**（`SKILL.md:47-70`）：Capture Intent→Interview and Research→写 SKILL.md 初稿。
2. **评测编排**（`:163-221`）：每个测试用例**同轮并发**拉两个子代理——with-skill 与 baseline（新建技能的 baseline 是裸跑；改进技能的 baseline 是旧版快照 `cp -r <skill> <workspace>/skill-snapshot/`）。工作区按 `iteration-N/eval-ID/with_skill|without_skill/outputs/` 组织，`eval_metadata.json` 记 prompt 与断言。
3. **触发率评测**（`run_eval.py:35-49`）：把技能 description 临时注册进 `.claude/commands/` 伪造 available_skills 条目，起 `claude -p` 跑查询；`run_eval.py:108` 用 `select.select` 1 秒粒度监听 stdout，`:133` 捕捉流式事件里的 `content_block_start`——**不等完整回复**（工具执行完才收尾太慢），`:165-168` 命中技能名即 triggered。ProcessPoolExecutor 并发多查询。
4. **报告与查看器**：`generate_report.py:16-17` 的 `generate_html()` 用 286 行字符串模板拼整页 HTML（无模板引擎），auto_refresh 加 meta refresh 标签**边跑边看**。
5. **迭代循环**（`run_loop.py:47`）：`split_eval_set()`（`run_loop.py:24-38`）按 holdout 比例（默认 0.4，`:254`）分层切 train/test——**改进只看 train 集，test 集做诚实验收**，防描述过拟合；每轮改动喂 `improve_description.py` 的 `_call_claude` 生成候选，历史直接回放给 generate_report。
6. **打包交付**：`package_skill.py:42` 打包（`:27-32` 排除规则保护 rel_path 首段即技能名），`quick_validate.py` 快检。

## 5. 设计决策

- **触发率是被测量的，不是被感觉的**：技能的成败首先在"该触发时触发、不该时沉默"，run_eval 把它变成可复跑实验（`SKILL.md:396-398` 还教你怎么设计"实质到值得触发"的查询——简单一步任务 Claude 自己就能做，永不触发是常态不是 bug，这页认知直接决定 eval 集质量）。
- **holdout 防过拟合**：描述优化最容易把 description 调成"背题"——train/test 切分让每轮改进面对诚实验收，这是把 ML 实验纪律移植进 prompt 工程。
- **同轮并发 with/baseline**（`SKILL.md:169` 明令"don't spawn the with-skill runs first"）：拉平环境漂移，让对比在同一时间窗内成立。
- **流式早停**：select+content_block_start 把单查询评测从分钟级压到秒级——评测基础设施的性能直接影响迭代节奏。
- **Anatomy 即预算表**：三级加载给出明确的 token 预算（~100 词/<500 行/无限），"接近 500 行就加一层 hierarchy"（`SKILL.md:96`）——上下文经济学被写成硬指标。

## 6. 新人提示

- 想写自己的技能，先精读 `SKILL.md:71-140`（Writing Guide 全节），再抄 internal-comms（最薄范本）或 docx（最厚范本）的骨架。
- 跑评测前确认在项目根（`run_eval.py:22-32` 向上找 `.claude/` 定位根，找不到就以 cwd 为根，命令文件可能落错位置）。
- 触发率低先查 description 是否只写了"是什么"没写"何时用/何时不用"——对照 `SKILL.md:333-408` 的优化四步。
- 三 agent 文件是给子代理的任务书模板，派发评测时直接复用。
- 改 `utils.py` 注意三脚本共同依赖，跑一遍三个入口再交付。
