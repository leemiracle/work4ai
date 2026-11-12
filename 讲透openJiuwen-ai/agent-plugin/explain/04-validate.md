# 04 · validate.py：规范如何被机器执行（校验引擎全解）

## 一、角色定位

`scripts/validate.py`（1008 行，全仓最大文件）是插件规范的**机器执行者**：docs/plugin-spec.md 用自然语言写"必须"，validate.py 用代码回答"怎么判"。docstring（`scripts/validate.py:4-16`）定义三层校验架构——**L0 规范与质量**（占位符残留、展示字段不全，"不影响加载，影响成品"）、**L1 静态校验**（加载阻塞项，纯 stdlib 的 json/ast/文件系统）、**L2 热加载**（子进程跑 hot_load_worker.py 真实加载链）。三层是**漏斗关系**：L0/L1 都通过才执行 L2（L12、主流程 L973-975）——便宜的检查先跑，贵的真 import 只给静态干净的包。

它的血统注明在 L14-16：L0/L1 检查逻辑**移植自 jiuwenswarm 主仓的 plugin-creator/scripts/validate_plugin.py**，本仓维护"仓库级版本"（多包扫描、--only、--require-hot-load），注释承认"规范变更需两处同步"——与 init.py 的模板同源一样，这是双仓镜像维护契约的另一半。它是贡献流水线的守门人：本地跑它是 CONTRIBUTING 的必经步骤，CI（pr_check）也以它为内核。

## 二、内部结构

单文件四大区，由横幅注释分隔：

**公共设施（L105-207）**：`write_stdout()`（L105-107，与 init.py 同款的 os.write 输出）；核心数据结构 `Layer`（L110-162）——每层校验一个实例，`errors`（阻塞，二元组 `(msg, fix)` L121-122）、`warnings`（提示）、`notes`（事实陈述）三档分级；`skip_reason/skip_fix`（L118-119）让"跳过"成为一等状态；`status` property 三值 PASS/FAIL/SKIP（L138-142）；`render()`（L144-162）把三层结果渲染成 `---- 层名 ----` + `x/!/.` 前缀行。**每条 error 都携带 fix 修复建议**是全引擎的统一风格。路径解析 `_resolve_declared_path()`（L182-207）按加载器规则执行四连判：非空 → 必须相对路径（L189-194）→ 不得越出包根 `is_relative_to(pkg)`（L195-198）→ 存在且类型正确（L199-206）。

**L0 区（L211-332）**五个检查函数：`_check_todo_residue()`（L215-231）rglob 扫 `.md/.py/.json` 三后缀（L51），跳 `__pycache__/.git/.state`（L52），命中 `[TODO` 报错并展示前 5 个行号；`_check_i18n()`（L234-240）en/zh 双语非空；`_check_default_init_consistency()`（L243-255）强制 `default_init_input` 与 `quick_inputs[0]` 逐语言相等；`_check_legacy_camel_keys()`（L258-275）对七个历史 camelCase 键名（映射表 L58-66）递归检查（深入 tools/rails/mcps 条目）；`_check_display_fields()`（L278-324）是大杂烩——三个 i18n 字段（L54）、tags/quick_inputs **恰好 3 项**（L55, L283-291）、display_description.zh 的 40-50 字建议只给 warning（L299-302）、id/name/description/category 非空、六禁字段 `persona/agent_card/model/subagents/memories/rubrics`（L67-74, L319-324）。`_check_quality()`（L327-332）收口并查 README.md 存在。

**L1 区（L334-765）**分两段。AST 辅助段（L339-436）是微型静态分析器：`_contains_package_path()`（L394-399）识别 `__file__` 及包路径变量；`_open_mode_is_write()`（L402-408）认 `w/a/x/+` 写标志；`_is_package_path_write()`（L420-436）覆盖四种写形态——内置 `open(path, mode)`（L423-428）、`Path.write_text/mkdir/touch` 接收者写（L88-93, L429-430）、`Path.open(mode)`（L431-433）、`save/to_csv/to_json` 参数写（L94-102, L434-435）。核心 `_check_runtime_path_policy()`（L439-482）做**污点传播**：从 `__file__` 赋值链收集包路径变量（L457-460），拦三类——`FORBIDDEN_ROOT_NAMES` 自定义根目录变量（L75-80, L451-455）、`Path.cwd()/os.getcwd()`（L411-417, L463-472）、包内路径写文件（L473-482），fix 文案按 Tool/Rail 分叉（L464-468）。

分项检查段：`_check_no_arg_init()`（L485-501）无参构造；`_check_tool_card()`（L504-556）找字面量 `ToolCard(...)`，查 id/name 显式（L520-522）、input_params 必含 `"type": "object"`（L535-546）、properties 禁出现 `output_root/absolute_path` 等产物根参数（L81-87, L547-555）；`_load_declared_class()`（L558-591）解析 file+class 声明，语法错误带行号上报（L573-574），**找不到类时把文件内实际定义的类名列出来**（L587-590）；`_check_manifest_basics()`（L599-629）查 kebab 目录名、package_type=plugin、source=local、id==目录名（L619-623）、空数组禁止（L624-629）；`_check_skill_dir()`（L658-682）正则抽 YAML frontmatter（L669），强制 name == skill 目录名（L674-680）；`_check_tools()`（L713-736）与 `_check_rails()`（L739-756）串起基类检查（`_has_base(cls, "Tool")` L722 / `"Rail"` L748）与全部分项。

**L2 与 CLI 区（L792-1004）**：`validate_hot_load()`（L835-882）见下节数据流；`resolve_targets()`（L900-920）合并位置参数与 `--only`，裸名自动补 plugins/ 前缀（L908-911）；`_plugin_verdict()`（L923-928）输出三态；`main()`（L931-1004）编排并打 Summary。

## 三、外部连接

- **上游调用者**：CONTRIBUTING 本地流程、CI 工作流 `.github/workflows/pr-quality.yml`（经 pr_check.py 转入，见 06 篇）、build.py/publish.py 发布前把关。
- **下游子进程**：L2 经 `subprocess.run([sys.executable, HOT_LOAD_WORKER, pkg])`（L845-855）拉起 hot_load_worker.py，**主脚本绝不 import openjiuwen**（L793 区头注释）——L0/L1 在无 SDK 环境完整可用，"纯静态"与"需运行时"两类检查被隔离在两个进程。
- **同源镜像**：jiuwenswarm 主仓 validate_plugin.py（L14-16），改规范两处同步。
- **被测试**：`tests/scripts/test_validate.py` 经 conftest 的 sys.path 注入直接 import 本模块。
- **规范文档**：docs/plugin-spec.md 的每条"必须"在此有对应 error + fix；docs/review-checklist.md 是人肉评审版，与机器版互补。

## 四、数据流

一次 `validate.py --only my-plugin` 的流程：

1. **目标解析**（L959-962）：`--only my-plugin` → `plugins/my-plugin`，不存在即报错退出。
2. **L0+L1 一趟跑完**（`validate_static()` L773-789）：读 manifest.json（缺文件 error "先运行 scripts/init.py 初始化包目录"，L779-781），然后 `_check_quality` 与 `_check_structure` **全量报错不短路**（L774 docstring）。
3. **L2 门禁**（L970-977）：`--no-hot-load` 显式 skip（L970-972）；L0/L1 有 error 则 L2 skip "先修完 L0/L1 的错误再重跑"（L973-975）；否则进 `validate_hot_load`。
4. **L2 子进程协议**（L835-882）：`subprocess.run` 捕获 stdout/stderr，超时 120s（L43, L856-861）；`_parse_worker_stdout()`（L821-832）**从后往前**找最后一行可解析 JSON——worker 输出协议是"人读日志 + 末行机器 JSON"双轨；拿不到 JSON 时截 stderr 尾部 300 字附在 skip 消息，fix 明说"**这不是包的问题**，请检查 openjiuwen 运行环境"（L875-878）。`_apply_worker_result()`（L797-818）把 worker 的 status/errors/notes 灌回 Layer，未知 status 一律归 skip（L814-818）而非 fail。
5. **裁决与退出码**（L979-1004）：逐包三态（L923-928：任一层 error → FAIL；无 error 但 L2 SKIP → PARTIAL）。有 FAIL → exit 1；仅 PARTIAL → 默认 **exit 0**（L999-1002），`--require-hot-load` 时升级为 1（L994-998）。

错误信息的流转：L1 每条 error 是 `(msg, fix)` 二元组，render 时 `x msg` + `-> fix` 两行（L154-157）；L2 worker 的 errors 数组保持同构（L805-811）——**协议在进程边界上仍保持"错误+修复建议"契约**。

## 五、设计决策与权衡

1. **三态裁决 PASS/FAIL/PARTIAL 是本引擎的灵魂**：本地没装 openjiuwen 是常态，把"L2 没跑"当失败会逼所有人装 SDK，当通过又会放过真问题。PARTIAL + 默认 exit 0 + CI 侧 `--require-hot-load` 升级——**同一份代码，本地宽松、流水线严格**，用调用方参数而非分叉脚本实现双模式。
2. **环境故障归 SKIP 不归 FAIL**（L856-878）：超时、worker 崩溃、无 JSON 全部 skip，文案显式"这不是包的问题"。归因哲学：校验器只对包质量负责不对环境负责——两类失败混在一起会让 CI 红得莫名其妙。
3. **AST 静态分析而非 import 检查**：L1 全程 `ast.parse` 不执行插件代码（L572），恶意/损坏代码不会在校验期执行。代价：只能查"字面量形态"——ToolCard 经变量中转就查不到，此时降级 warning"无法静态检查"（L513-517, L530-533），**诚实声明能力边界**而非漏报；污点传播只追一层赋值链（L457-460），`joinpath` 拼接可绕过——注释自嘲"不做复杂静态分析"（L440）。
4. **全量报错不短路**（L774）：对比常见 linter 首错即停，这里一次列全——贡献者提 PR 前修一轮即走。
5. **error/warning 分级**：40-50 字建议（L299-302）、ToolCard 非字面量（L531-533）只 warn 不拦——"硬规范"与"软建议"分级，warning 不进 FAIL 判定（L924 只看 errors）。
6. **fix 文案随组件类型分叉**（L464-468, L474-478）：同一种"写文件"违规，Tool 提示"入参显式传入"、Rail 提示"get_workspace()"——错误消息本身承载规范教学。
7. **多包仓库级扩展**：主仓版校验单包，本仓版加 `iter_repo_plugins()`（L890-897）、`--only` 可重复（L943-948）、目标去重（L905-919），L14-16 注释把这组差异明示为"仓库级版本"的增量。

## 六、新人提示与坑

1. **本地 PARTIAL ≠ 通过**：`RESULT: PARTIAL` 且 exit 0 只是"L2 没跑"，CI 会用 `--require-hot-load` 把它变红。发布前务必在有 openjiuwen 的环境跑一次全量。
2. **tags/quick_inputs 必须"恰好 3 个"**（L288-291）：写 2 个或 4 个都 error——Hub 渲染硬约定，模板期就锁死（见 01 篇）。
3. **camelCase 旧键名报错**：`_check_legacy_camel_keys` 报"字段名应为 'display_name'，当前是旧名 'displayName'"（L266-269）。映射表 L58-66 里 `defaultInitPrompt` 也指向 `default_init_input`——直接用 snake_case 新名。
4. **skill 的 frontmatter name 必须逐字符等于目录名**（L677-680）。正则（L674）带引号也只取无空格段——name 里别带空格。
5. **空数组是 error**（L624-629）：`"rails": []` 不写即可，写了反而错。"没有能力"与"声明了空能力"语义不同。
6. **AST 检查的绕过不是漏洞是边界**：ToolCard 藏进函数返回、路径经 `os.path.join` 拼接，L1 查不到——但 L2 热加载真刀真枪，运行时行为逃不掉。L1 是"廉价的确定性"，L2 是"昂贵的真实性"，互补而非互替。
7. **给 worker 加输出要守协议**：worker stdout 最后一行必须是单行 JSON dict（L821-832 倒序解析）；日志放前面的行，JSON 行后别再 print。
8. **改动 L0/L1 记得同步主仓**（L16）——两仓校验漂移的后果是"主仓能过、本仓被拦"的幽灵差异。
