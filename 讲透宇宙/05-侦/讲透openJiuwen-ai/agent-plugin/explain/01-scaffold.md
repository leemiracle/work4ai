# 01 · 脚手架：scripts/init.py 与 templates/plugin-template/

## 一、角色定位

`scripts/init.py`（125 行）是 agent-plugin 仓的插件包生成器：开发者执行 `init.py my-plugin --skill X --tool Y --rail Z`，它就从 `templates/plugin-template/` 模板树复制出 `plugins/my-plugin/` 骨架，是整个贡献流程的第一环。docstring 开宗明义（`scripts/init.py:4-7`）：它与 jiuwenswarm 主仓 plugin-creator 的 `init_plugin.py` 输出**同源**——两条路径产出的骨架完全一致，保证"本地开发"与"向官方仓贡献"零迁移成本。

它的设计哲学是**双层占位符**：`{{VAR}}` 由机器在生成时替换（插件名、类名等可推导项），`[TODO: ...]` 留给人填（描述、标签等语义项）。前者保证命名约定不可违反，后者配合 L0 校验拦截未填充的包（`scripts/init.py:7`）——脚手架与校验引擎构成一对"生成-验收"闭环。

## 二、内部结构

init.py 是单文件、零第三方依赖的 argparse 脚本，结构四段：**路径与常量**（`scripts/init.py:24-27`，`NAME_RE` 正则强制 kebab-case 插件名，与 manifest.id 合法域对齐）；**命名转换**（`_pascal()` `scripts/init.py:34-35` 把 `word-count` 转 `WordCount`，`_snake()` `scripts/init.py:38-39` 连字符转下划线）；**占位符替换引擎** `_substitute()`（`scripts/init.py:42-45`，朴素的双花括号 `str.replace`）；**main 主流程**（`scripts/init.py:48-121`，校验名字 → 查重目录 → 复制 manifest/README → 按参数生成组件 → 打印指引）。

五类占位符的完整清单：

| 占位符 | 出现位置 | 替换值来源 |
|---|---|---|
| `{{PLUGIN_ID}}` | manifest.json:4、README.md:1 | 命令行位置参数（`scripts/init.py:67`） |
| `{{SKILL_NAME}}` | components/SKILL.md:2,6 | `--skill NAME` 原样（`scripts/init.py:81`） |
| `{{CLASS_NAME}}` | tool/rail 模板 class 行 | `_pascal(_snake(name))` 派生（`scripts/init.py:88,101`） |
| `{{TOOL_ID}}` | tool_template.py:23-24 | snake 化 stem（`scripts/init.py:89`） |
| `[TODO: ...]` | 全部模板 | 留给人工，L0 校验兜底 |

模板树五个文件各司其职：`manifest.json` 除 `{{PLUGIN_ID}}` 外全部字段预填 `[TODO]`，唯独 `"source": "local"`（`templates/plugin-template/manifest.json:16`）和 `"avatar": ""` 是默认实值；`README.md` 模板是双语一句话描述 + 核心能力 + 组件清单三段式；`components/` 三个组件模板只在显式传参时才被复制进目标包。

两个组件模板对应插件的两类 Python 组件。tool 模板（`templates/plugin-template/components/tool_template.py`）继承 `openjiuwen.core.foundation.tool.Tool`（第 14 行 import），构造函数经 `ToolCard` 声明能力——`id/name` 用 `{{TOOL_ID}}`（`tool_template.py:23-24`），`input_params` 是合法 JSON Schema（`tool_template.py:26-35`），`invoke` 返回 `{"success": ..., ...}`，`stream` 默认包装 invoke 单次 yield（`tool_template.py:39-44`）。docstring 第 6-8 行把约束写死：**无参构造、id/name 必须显式设置、禁止构造函数注入运行时对象**——这三条同时是 validate.py L1 静态校验的检查项，模板注释与校验规则一一呼应。rail 模板（`templates/plugin-template/components/rail_template.py`）继承 `openjiuwen.harness.rails.base.DeepAgentRail`（第 14 行），实现 `init/uninit` 生命周期挂载（`rail_template.py:24-28`），第 30-35 行以注释列出全部八种钩子（before/after_invoke、before/after_model_call、before/after_tool_call、before/after_task_iteration），要求"至少实现一个"。SKILL.md 模板（`templates/plugin-template/components/SKILL.md`）是 frontmatter（`name: {{SKILL_NAME}}` + `description`，第 1-4 行）加"目标 / 工作流 / 验收标准"三节正文——frontmatter description 是技能触发机制依赖的语义锚，第 3 行 TODO 注释明言"触发机制依赖这句话"。

## 三、外部连接

- **上游**：开发者手工调用（Usage 见 `scripts/init.py:9-11`），没有任何脚本调用它——纯入口。
- **下游 validate.py**：指引第二条就是 `python scripts/validate.py --only <name>`（`scripts/init.py:115-117`），并特意注明"默认含 L2 热加载，需 jiuwenswarm 运行环境"——脚手架在生成时就把 L2 的环境要求预警给开发者。
- **下游 tests/**：指引第三条要求补 `tests/plugins/<name>/` 行为测试（`scripts/init.py:118`）。
- **下游 catalog.py**：指引第四条 `catalog.py 更新目录清单后提 PR`（`scripts/init.py:119`）——新插件必须经 catalog 登记才能进发布线。
- **模板内链接**：README 模板硬链 `docs/plugin-spec.md`（`templates/plugin-template/README.md:20`），每个新生成包自动携带规范入口。
- **跨仓同源**：与 jiuwenswarm 主仓 plugin-creator 输出同源（`scripts/init.py:6`），改模板需两头同步，这是隐性维护契约。

图谱视角的事实：init.py 只被 `tests/scripts/test_init.py` 引用（conftest.py 把 scripts/ 注入 sys.path，`tests/conftest.py:10-12`），与 scripts/ 下其他脚本之间没有 import 边——scripts/ 八个脚本是"兄弟孤岛"，仅靠命令行指引串联成流水线。这是刻意的松耦合：每个脚本可独立执行、独立测试。

## 四、数据流

一次 `init.py my-plugin --skill usage-guide --tool counter --rail auditor` 的完整数据流：

1. **名字校验**：`my-plugin` 过 `NAME_RE`（`scripts/init.py:59-61`），失败报"必须是 kebab-case"退出 1；随后检查 `plugins/my-plugin` 不存在（`scripts/init.py:62-65`），存在即拒绝——**绝不覆盖已有包**。
2. **基础层复制**：构建 `mapping = {"PLUGIN_ID": args.name}`（`scripts/init.py:67`），遍历 `manifest.json` 与 `README.md` 两个模板（`scripts/init.py:69-71`），读入 → 替换 → 写入目标目录。
3. **skill 分支**（`scripts/init.py:75-84`）：`--skill usage-guide` 生成 `skills/usage-guide/SKILL.md`，替换 `{{SKILL_NAME}}`。skill 名**不做 kebab/snake 转换**，原样作目录名。
4. **tool 分支**（`scripts/init.py:86-97`）：`--tool counter` 先 `_snake` 得 stem，派生三值——类名 `CounterTool`、tool_id `counter`、文件名 `counter_tool.py`（`scripts/init.py:87-90`），替换 `{{CLASS_NAME}}` 与 `{{TOOL_ID}}`。
5. **rail 分支**（`scripts/init.py:99-109`）：`--rail auditor` 同样派生 `AuditorRail`，但模板只需 `{{CLASS_NAME}}` 一个变量——rail 无 id 声明，manifest 里 rail 条目按 file+class 定位（见 example-plugin manifest 的 rails 段）。
6. **收尾指引**：打印四步指引（`scripts/init.py:111-120`），把 validate → tests → catalog 的后续流水线串给开发者。

输出全部走 `write_stdout()` 即裸 `os.write(1, ...)`（`scripts/init.py:30-31`）而非 print——配合 main 开头的 `sys.stdout.reconfigure(encoding="utf-8", errors="replace")`（`scripts/init.py:49-50`），这是 Windows GBK 控制台下中文输出不炸的双重保险：reconfigure 处理主流场景，os.write 兜底 reconfigure 不可用的旧 Python。

## 五、设计决策与权衡

1. **朴素 replace 而非 Jinja2/string.Template**：模板五个、变量五个，replace 零依赖足够（`scripts/init.py:42-45`）。代价是模板不能出现字面 `{{KEY}}`——本仓无此需求。这与全仓"纯 stdlib"基调一致（连 web-to-markdown 插件都 342 行零依赖）。
2. **`{{VAR}}` 与 `[TODO]` 双层的职责切分**：能从命令行推导的（id、类名、tool id）机器替换，杜绝命名不一致；不能推导的（中文描述、标签）留 TODO，由 validate.py L0 扫 `[TODO` 拦截（见 04 篇）。**把"可机检的约定"前移到生成期、把"需人判断的语义"后置到校验期**，是这套脚手架最核心的分层。
3. **manifest 预填三组双语数组**：tags 3 项、quick_inputs 3 项、`default_init_input` 必须与 `quick_inputs[0]` 相同（`templates/plugin-template/manifest.json:19-20,38` 的 TODO 注释互相引用）——Hub 展示字段结构在模板期锁死。
4. **组件模板放 components/ 子目录**：manifest/README 每包必选，skill/tool/rail 可选三选 N，子目录天然表达"可选"，init.py 按需取用（`scripts/init.py:73`），不给纯 skill 包塞无用 py 文件。
5. **拒绝覆盖已有目录**（`scripts/init.py:63-65`）：脚手架场景下覆盖几乎必然是事故，宁可直接失败。
6. **冗余的代价**：模板 docstring 的约束（无参构造等）与 validate.py 检查规则是两份平行真值，改规范要同时改 plugin-spec.md、模板注释、validate.py 三处——本质是接受冗余换取新手在模板文件里就能看到全部约束。

## 六、新人提示与坑

1. **插件名一旦定了别改**：manifest.id 与目录名、README 标题由 `{{PLUGIN_ID}}` 一次性注入三处，手改 id 会导致不一致被 L0 拦截。仓根 `renames.json:3` 明确"id 一经发布不可变；确需改名时新建插件并在此登记"——注意 renames.json 目前为空且**没有任何脚本消费它**（publish 预留），别指望自动迁移。
2. **`--tool` 名字会被 snake 化**：传 `--tool word-count` 得到 `word_count_tool.py` + `WordCountTool` + id `word_count`（`scripts/init.py:87-89`）；但 `--skill` 不转换，传什么目录名就是什么。
3. **[TODO] 一个都不能留**：包括看似无害的 category、display_name。生成后第一件事是全文搜 `[TODO`。
4. **L2 热加载需 jiuwenswarm 运行环境**：init.py 指引已预警（`scripts/init.py:116-117`）。本地没有 openjiuwen SDK 时可先跳过 L2 只跑 L0/L1（见 04 篇）。
5. **坑：模板 README 相对链接**：`templates/plugin-template/README.md:20` 的 `../../docs/plugin-spec.md` 在生成后指向仓根 docs/，是通的；若把生成目录挪出 plugins/ 即断链。
6. **同源维护提醒**：改本仓模板时同步检查 jiuwenswarm 主仓 plugin-creator（`scripts/init.py:6`），两边漂移会让"主仓生成 → 贡献进本仓"的包过不了校验。
7. **图谱/依赖视角**：找 init.py 的调用方别在 scripts/ 里找 import——它只被 tests/scripts/test_init.py 导入测试，生产路径是纯 CLI。
