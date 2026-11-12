# 06 · hot_load_worker + pr_check：L2 真加载与 CI/本地等价门禁

## 一、角色定位

这两个脚本回答同一个问题的两面：**插件代码在真实宿主里到底能不能跑起来**。`scripts/hot_load_worker.py`（223 行）是 L2 校验的执行体——在一次性子进程里真 import 插件模块、真实例化类、真验证继承链，模拟 jiuwenswarm 运行时的加载链（docstring L6-11 明言加载方式对齐运行时 `meta_elements._load_class_from_file`，但"不拉起完整 harness"）。`scripts/pr_check.py`（267 行）是 CI 门禁的**本地等价命令**——五步检查（结构、L0/L1、catalog、密钥扫描、单测）恰好等于 `.github/workflows/pr-quality.yml` 的 quality-gate job，工作流注释直接写"本地等价命令：python scripts/pr_check.py"（`pr-quality.yml:4`）。

两者的关系是"深验证"与"广门禁"：worker 被 validate.py 的 L2 以子进程拉起（见 04 篇），pr_check 则编排 validate/catalog 加上自己独有的结构与密钥检查。而把它们连在一起的是一条**现实约束**：openjiuwen SDK 未发布公开 pip，CI 装不上运行时——所以 L2 被隔离在可选 job 里，靠仓库变量开关，工作流里留着显式 TODO（`pr-quality.yml:48-52`）。

## 二、内部结构

**hot_load_worker.py 四段**。协议段：`_result()`（L51-65）产出统一的 `{status, errors, notes, skip_reason, skip_fix}` dict；exit code 三值 0/1/2 对应 pass/fail/skip（L15-18, L219）。命名空间段 `_ensure_package_namespace()`（L68-86）：手工合成父包 `ModuleType(_HARNESS_NAMESPACE)` 并把 `__path__` 指向 plugins/ 目录（L77-79），再合成 `openjiuwen.extensions.harness.<pkg>` 子包（L80-85）——插件模块由此获得与运行时一致的 **canonical 模块名**（L42-43 注释对齐 `_canonical_extension_module_name`）。注释 L71-73 解释了为什么敢做进程级永久设置：worker 是一次性子进程，不需要快照回滚。加载段 `_load_module()`（L89-123）：越根检查（L93-94）→ dotted 模块名拼接（L95-96）→ `importlib.util.spec_from_file_location`（L97）→ **临时注入 sys.path** 两条（文件目录 + 包根，L104-108，注释对齐运行时 `_temporary_sys_path`，支持 `import helper` 同目录绝对导入）→ `exec_module`（L111）→ **finally 强制清理**（L112-122）：移除临时 path、回收经临时路径载入的包外模块——L115-122 的注释点名防"同包不同子目录的同名模块串扰"。校验段：`_check_tool_instance()`（L126-131）isinstance 验 Tool 继承链；`_check_rail_instance()`（L134-149）除 isinstance 验 DeepAgentRail 外，还按 `RAIL_HOOK_METHODS` 八钩子清单（L31-40）逐个判定"callable 且实现体不是基类原版"（L139-144）——**零真钩子直接 fail**（L145-148）。`run()`（L152-204）编排：`import openjiuwen` 探测（L153-163），任何异常归 skip 且 fix 写明"在 jiuwenswarm 运行环境执行（主仓 .venv），或安装 openjiuwen 后重跑"（L159-162）；随后按 manifest 的 tools/rails 两段循环加载-实例化-校验（L176-191），**单组件失败不阻断其余检查**（L192-198 全收进 errors）；零代码组件只记 note（L202-203）。

**pr_check.py 四段**。检查结果类 `CheckResult`（L60-76，ok/skipped/lines 三态）。结构检查 `check_structure()`（L84-105）：plugins/ 必须扁平一层——根下出现任何**文件**即 fail（L93-94），目录名 kebab（L97-98）、每目录必有 manifest.json（L99-100）、零包也 fail（L101-102）。密钥扫描 `scan_secrets()`（L145-162）配五条保守正则（L37-49）：PEM 私钥头、AWS `AKIA` 前缀、GitCode PAT、GitHub `gh[pousr]_` token、以及"凭据字面量"键值对模式（`api_key = "..."` 形态，L43-48）；扫描对象优先 `git ls-files` 跟踪文件（L114-121），非 git 环境退化为 rglob（L131-142）；零命中时 note 提醒"保守规则；建议 CI 叠加 gitleaks"（L161）。子进程步骤 `run_step()`（L170-193）：600s 超时、stdout 尾 3 行做 note、失败时 stderr 尾 3 行进 fail 行——**日志摘要而非全文**，门禁输出保持可读。`run_tests()`（L196-215）：pytest 不存在记 SKIP 不失败（L208-211），CI 侧的 job 会先 `pip install pytest`（`pr-quality.yml:26-27`）。`main()`（L223-263）五步固定顺序编排（L231-243），失败与成功的收尾输出都追加同一句提示：L2 热加载另需 openjiuwen 环境、用 `validate.py --require-hot-load`（L252-262）。

## 三、外部连接

- **worker ↔ validate.py**：被 `validate_hot_load()` 以 `subprocess.run([sys.executable, HOT_LOAD_WORKER, pkg])` 拉起（`validate.py:845`），120s 超时与"末行 JSON"协议由父侧配合（04 篇详述）。worker 不 import validate——单向依赖。
- **worker ↔ openjiuwen 运行时**：两处硬引用——探测 import（L154）与两个基类 isinstance（L127, L135）。加载链三处注释对齐运行时函数名（`_load_class_from_file` L6、`_temporary_extension_alias` L71、`_temporary_sys_path` L102）——**worker 是运行时加载逻辑的镜像复刻**，运行时改加载行为 worker 必须跟。
- **worker ↔ 行为测试的镜像**：`_check_rail_instance` 的"钩子必须非基类原版"判定（L139-144）与 `tests/plugins/example-plugin/test_example_plugin.py:87-94` 的 `test_rail_hooks_are_overridden` 是同一逻辑的两份实现（一个面向 CI 加载链、一个面向 pytest）。
- **pr_check ↔ CI 工作流**：`.github/workflows/pr-quality.yml` 的 quality-gate job 直接跑 `python scripts/pr_check.py`（L29-30）——**CI 不是重新实现门禁而是调用本地同一命令**，等价性由共享代码保证。可选的 hot-load job（L32-55）由仓库变量 `ENABLE_HOT_LOAD == 'true'` 开关（L36），内容是 `validate.py --require-hot-load`（L55），其 `pip install openjiuwen` 步骤挂着 TODO（L50-52）。
- **pr_check → validate/catalog**：subprocess 调用，参数分别是 `--no-hot-load`（L235）与 `--check`（L239）——门禁刻意选"本地可复现"的参数组合。

## 四、数据流

**L2 一次热加载的完整旅程**（worker 视角）：

1. **环境探测**（L153-163）：`import openjiuwen` 失败 → 返回 skip + exit 2，父进程把它渲染成 Layer.skip"openjiuwen 运行时不可用"。这是无 SDK 本地最常见的 L2 出口。
2. **命名空间合成**（L174 → L68-86）：把 `plugins/my-plugin` 注册成 `openjiuwen.extensions.harness.my-plugin` 合成包。此后插件内若写 `from .helper import VALUE`，相对导入按合成 `__path__` 解析成功。
3. **逐组件加载**（L176-191）：取 manifest tools/rails 段的 file+class → `_load_module` 真执行模块顶层代码（import、常量、类定义）→ `getattr(module, class_name)` → `cls()` **无参实例化**（L190，正是规范"无参构造"的存在意义）→ checker 验证继承链与钩子。
4. **隔离清理**（L112-122 finally）：每个组件加载后恢复 sys.path，并回收临时路径引入的模块——保证同一 worker 进程里多组件、多包加载互不污染。
5. **末行 JSON 交卷**（L216-217）：结果序列化打印，父进程 `_parse_worker_stdout` 倒序取末行解析。errors 二元组结构与 validate 的 `(msg, fix)` 对齐。

**pr_check 一次门禁的数据流**（L231-243）：五步顺序执行、结果聚合、单表汇总——`[PASS/FAIL/SKIP] 步骤名` 每步三行摘要（L245-251），任一 fail 即 exit 1。CI 上 quality-gate 以 exit code 定 PR 红绿；本地开发者同一命令零环境差异。密钥扫描的特殊性：扫描面=git 跟踪文件（未 add 的新文件不扫），命中即 fail 并展示片段前 24 字符（L159）——只证"疑似"，不做确定性判定。

## 五、设计决策与权衡

1. **真 import 而非更深的静态分析**：L1 AST 已查过的项（继承、无参构造）在 L2 重新以**运行时真值**验证。静态分析永远存在"看起来对"的绕过（动态基类、条件导入），只有 exec 一遍才见真章——代价是必须付出子进程隔离与 120s 超时（防插件 import 期死循环拖死校验）。两层各付其能：L1 便宜且能全量，L2 昂贵但不可欺。
2. **canonical 模块名复刻**：把插件加载进 `openjiuwen.extensions.harness.*` 命名空间而非随便挂个名——插件里合法的相对导入、`__name__` 判断、模块级日志配置都按运行时形态走。**验证环境与生产环境的一致性优先于验证器的简单性**，这是 L2 三个"对齐运行时"注释（L6, L71, L102）的统一动机。
3. **skip 与 fail 的严格二分**：环境问题（import 不到 openjiuwen、目录不存在、usage 错误）一律 skip/exit 2；只有"包自身的加载/实例化错误"才 fail/exit 1（L15-18）。与 validate 的 PARTIAL 哲学同源——**校验结果必须可归因**，环境红和代码红混色会让贡献者无从下手。
4. **单组件失败不阻断**（L192-198）：一个包三个 tool 挂了一个，另两个照查——一次运行暴露全部问题，与 L1 的"全量报错"策略一致。
5. **CI/本地等价靠共享命令而非共享配置**：门禁逻辑只写一份（pr_check.py），工作流引用命令。对比"CI yaml 里重新拼步骤"的模式，永远不会出现"本地过 CI 红"的漂移。代价是 pr_check 必须自身保持零依赖（pytest 缺失只是 SKIP，L208-211）。
6. **密钥扫描的克制**：五条保守正则 + "建议叠加 gitleaks"（L161）——自研扫描只求拦低级失误，不与专业工具竞赛误报率。扫 git 跟踪文件（而非全盘）也与门禁职责对齐：门禁管"要进库的东西"。
7. **L2 进 CI 的开关化等待**：`ENABLE_HOT_LOAD` 变量开关 + TODO 注释（`pr-quality.yml:34-36, 50-52`）是"架构就绪、依赖未就绪"的标准处置——代码路径完整存在，基础设施（公开 wheel 源）到位后置一个布尔即激活，不需要改任何脚本。

## 六、新人提示与坑

1. **本地 pr_check 绿 ≠ 全链绿**：五步门禁不含 L2（docstring L14-15）。发布前在 jiuwenswarm 主仓 .venv 环境跑 `validate.py --require-hot-load` 才算闭环——输出里的两处提示（L256, L261）就是为此设计的。
2. **worker 的"钩子必须非基类原版"是硬闸**：rail 只写 `def before_invoke(self, ctx): return None` 会直接 fail（L145-148）——这与 example-plugin 测试（`test_example_plugin.py:87-94`）双重把关同一规范。判定逻辑是 `getattr(type(instance), name) is not getattr(DeepAgentRail, name)`（L143），别名/装饰器包装的钩子也认。
3. **插件里别依赖 `import helper` 这种同目录绝对导入**：虽然 worker 临时注入 sys.path 支持它（L104-108），但这依赖加载器的好意，且注释明言是"对齐运行时"的兼容行为——包内导入规范写法是相对导入 `from .helper import`。
4. **modules 串扰坑**：如果两个不同插件的 tools/ 目录里都有 `utils.py`，靠 L115-122 的 finally 回收避免互相顶替。自己写加载器复刻这段时漏掉回收，会撞上"第二个包 import 到第一个包的 utils"这类幽灵 bug。
5. **plugins/ 根下放文件直接 fail**（L93-94）：连 README 或 .gitignore 都不行——目录约定"plugins/ 扁平一层全是包"由结构检查硬执行。临时文件记得放包内或仓根。
6. **密钥扫描只扫 git 跟踪文件**：`git add` 之前的新文件不在扫描面（L114-121）——提交前先 add 再跑一次 pr_check 才是真覆盖；同理 `.env.example` 靠文件名特判纳入（L52），改名（如 env.sample）就漏扫。
7. **run_step 的 600s 超时是总预算**（L180）：pytest 大仓挂掉时门禁等满 10 分钟才报——本地调试可单独跑子命令（`validate.py --no-hot-load` 等）定位慢源。
8. **worker 改输出协议两头遭殃**：末行 JSON 字段（status/errors/notes/skip_reason/skip_fix）是父进程 `_apply_worker_result` 的契约（`validate.py:797-818`）；加字段安全，改字段名/类型会静默落进"未知 status → skip"分支（`validate.py:814-818`），把 fail 伪装成 skip。
