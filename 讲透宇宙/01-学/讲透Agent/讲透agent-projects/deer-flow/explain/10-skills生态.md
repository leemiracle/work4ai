# 10 · Skills 生态：SKILL.md 即插件的装载与校验

## 角色定位

Skills 是 DeerFlow 的"可插拔能力卡"：每个 skill 是一个含 `SKILL.md` 的目录（frontmatter 元数据 + markdown 指令正文 + 任意 scripts/references/assets 资产），agent 运行时把启用技能的容器路径列进系统提示词，模型按需 Read SKILL.md 再黑盒调用其脚本。装载器在 `backend/packages/harness/deerflow/skills/`（仅 4 文件 306 行），资产本体在仓根 `skills/`。先做一处计数勘误：磁盘 `skills/public/` 实有 **17 个**技能目录（bootstrap、chart-visualization、claude-to-deerflow、consulting-analysis、data-analysis、deep-research、find-skills、frontend-design、github-deep-research、image-generation、podcast-generation、ppt-generation、skill-creator、surprise-me、vercel-deploy-claimable、video-generation、web-design-guidelines），此前流传的"13 技能"口径不含 bootstrap/consulting-analysis/frontend-design/surprise-me 等目录，以 `ls skills/public/` 为准。

包 barrel 只有 5 行，导出面有一个刻意设计：`_validate_skill_frontmatter` 带下划线私有名却被 `__all__` 显式再导出（`skills/__init__.py:3-5`）——它是 Gateway install 端点的校验依赖，包级暴露是有意的 API 契约。

## 内部结构

四个文件一条链，依赖方向 types ← parser ← loader，validation 独立：

- **types.py（53 行）**：`Skill` dataclass 九字段（`types.py:9-16`），核心是 `get_container_path`（`types.py:24`）——把宿主物理路径翻译成沙箱容器内的 `/mnt/skills/{category}/{name}` 虚拟路径，默认基路径 `/mnt/skills`（`types.py:24` 参数默认值），与 sandbox 虚拟路径系统对齐：agent 只见容器视图，物理位置在宿主 threads 目录。零仓内依赖，处于依赖链最底层。
- **parser.py（65 行）**：轻量解析路线。正则截取 `---...---` frontmatter（`parser.py:26`）后**自实现逐行 key:value 解析**（`parser.py:33-41` 的 split(":", 1) 循环），仅支持扁平标量；name/description 缺失即判无效返回 None（`parser.py:47-48`）。
- **validation.py（85 行）**：重量校验路线。**用 yaml.safe_load 完整解析**（`validation.py:41`）并做结构校验——同一份 frontmatter 两条解析路线并存是本包最大的设计奇观（详见设计决策）。白名单 `ALLOWED_FRONTMATTER_PROPERTIES` 八键（`validation.py:12`）：name/description/license/allowed-tools/metadata/compatibility/version/author；name 规则 `^[a-z0-9-]+$`（`validation.py:67`）、禁首尾/连续连字符（`validation.py:69`）、上限 64 字符（`validation.py:71`）；description 禁尖括号（`validation.py:80`）、上限 1024（`validation.py:82`）。
- **loader.py（98 行）**：扫描与状态合并。`get_skills_root_path` 用"文件位置向上数五层"推导 backend 目录再取同级 skills（`loader.py:16-18`）；`load_skills` 依次扫 public/custom 双目录（`loader.py:58`），os.walk 时隐藏目录过滤 + 排序保证遍历确定性（`loader.py:65`）。

## 外部连接

**入向：三处消费面。** ① agent 系统提示词：`get_skills_prompt_section` 每轮构建 prompt 时 `load_skills(enabled_only=True)`（`prompt.py:323`），容器基路径读 config 的 `skills.container_path`、读不到回退 `/mnt/skills`（`prompt.py:329-331`），生成 `<skill_system>` 块注入模板的 `{skills_section}` 槽位（`prompt.py:236`）。② Gateway skills 路由：列表/详情/开关/安装四类端点。③ config 系统：skills_config 的 `get_skills_path` 未配置时延迟 import 本包 `get_skills_root_path`（07 篇 `skills_config.py:34` 的循环依赖断点）。

**出向：extensions_config.json 是启用状态的唯一事实源。** loader 完成扫描后逐技能查 `ExtensionsConfig.is_skill_enabled(name, category)` 回填 enabled（`loader.py:86`）。这里有个跨进程关键注释（`loader.py:77-80`）：刻意用 `ExtensionsConfig.from_file()` **直读磁盘**而非 `get_extensions_config()` 单例——因为 Gateway 是独立进程，它对开关状态的修改只有落盘后 LangGraph 侧下次 from_file 才可见。这是与 MCP 配置 mtime 协议（08 篇）平行的第二套"写文件即通信"。

**双路线容错序。** 路径解析链：config 失败 → 回退默认根（`loader.py:46-48`）；extensions 配置失败 → 默认全启用（`loader.py:87-89`）。skill 系统在任何配置损坏下都不阻塞 agent 启动。

## 数据流

**读路径（每轮 agent 构建）**：load_skills 扫描（~17 个 public SKILL.md）→ parser 逐个提取 name/description/license → extensions 启用状态回填 → enabled_only 过滤 → 按 name 排序（`loader.py:96`）→ prompt.py 拼容器路径清单进系统提示词 → 模型决定是否 Read `/mnt/skills/public/xxx/SKILL.md` → 按文档调用 scripts。skills 目录在沙箱侧只读挂载，skill 脚本的执行产物落 thread 的 workspace/outputs。

**写路径（安装一个 .skill 包）**：`POST /api/skills/install`（gateway `skills.py:335`）→ 解压到临时目录，`_safe_extract_skill_archive` 三重防御：拒绝绝对路径与 `..` 成员、**跳过 symlink 条目**（`skills.py:64-66`，symlink 探测基于 ZipInfo external attributes，`skills.py:34`）、总解压体积上限 512MB（`skills.py:44`）→ 校验 frontmatter（`skills.py:416` 调 `_validate_skill_frontmatter`）→ 通过才落位 `skills/custom/`（`skills.py:400-403`）→ 写 extensions_config.json 更新启用状态。先校验后落位的顺序保证 custom 目录里永远不会出现半成品。

## 设计决策

**① 双解析路线的分工。** parser（自实现逐行）服务热路径：每轮 agent 构建都要扫全部 SKILL.md，逐行 split 比 yaml.safe_load 快且零依赖；validation（yaml.safe_load）服务准入路径：安装时刻需要严格结构校验（嵌套 metadata、类型检查、白名单），简易解析器无法胜任。快慢分离，代价是两处对"合法 frontmatter"的定义可能漂移——例如 description 含冒号时 parser 会把值切歪但依旧通过，validation 则正确解析。

**② name 是身份键，目录名不是。** 启用状态按 `name:category` 键控（`loader.py:86`），而 vercel-deploy-claimable 的 frontmatter name=vercel-deploy 与目录名名实分离（上游命名遗留）——开关状态跟 name 走，排查"为什么开关不生效"先核对 frontmatter 而非目录名。

**③ 只读挂载 + 容器路径抽象。** skills 经 `/mnt/skills` 只读挂载进沙箱（config `skills_config.py:13-16` 的 container_path 字段），skill 资产对 agent 是"参考手册"而非可写区——配合 types.py 的路径翻译，宿主目录重组不影响提示词契约。

**④ 校验白名单与安装白名单同源。** validation.py:12 的八键白名单正对应 Gateway install 端点接受的扩展 frontmatter（version/author/compatibility 等）——同一份常量被两进程共享，防止"安装接受的键、运行时解析不了"的代差。

## 新人提示

- 写新 skill 的最小清单：目录 + SKILL.md（frontmatter 必须含 name/description，name 全小写连字符）+ 把目录放 `skills/custom/`（gitignore 区）或提 PR 进 public。装好后 `GET /api/skills/` 确认 name 字段与预期一致。
- description 是模型的路由依据，写得太谦虚会 undertrigger（skill-creator 甚至刻意把 description 写 pushy 来对冲）；禁尖括号、1024 字符上限（`validation.py:80-83`）。
- 装好的 skill 不生效三板斧：查 extensions_config.json 的 skills 节是否 enabled、查 frontmatter name 与开关键是否一致、重启或等待 LangGraph 侧下次 load_skills（from_file 直读磁盘，无需重载配置单例）。
- 给 skill 带脚本时遵守黑盒契约：SKILL.md 写清楚调用方式与参数，脚本自身零仓内依赖（仓内 17 个技能的脚本全部 stdlib/外部包）——脚本跑在沙箱容器里，import 不到 harness 代码。
- 别在 public 技能里放私有凭证：该目录随仓库分发，且 skills 只读挂载意味着 secret 也应走环境变量注入而非文件。
