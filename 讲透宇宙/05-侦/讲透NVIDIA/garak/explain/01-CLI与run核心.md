# 01 CLI 与 run 核心：cli.py / _spec.py / _selection.py

## 角色定位

`garak/cli.py`（793 行）是扫描管线总入口：参数解析、配置分层装载、插件选择解析、分派 `probewise_run`/`pxd_run`，全部在这一个 `main()`（`cli.py:39`）里完成。它不做探测本身，而是把用户意图翻译成 `_config` 全局状态 + probes/detectors/buffs 三张名单。配套 `_spec.py`（选择语法）与 `_selection.py`（落地为具体插件名）是新世代选中轴：`--spec`（`cli.py:160-168`）一个 flag 取代已废弃的 `--probes/--probe_tags/--buffs`（`cli.py:169-203`）。图谱 L01「入口与核心运行时」层，全仓唯一被所有下游依赖的根。

## 内部结构

`main()` 六段直线流程：

1. **argparse 构建**（`cli.py:67-311`）：五组参数；插件类参数由 `_plugins.PLUGIN_CLASSES` 循环生成互斥组 `--{type}_option_file` 与 `--{type}_options`（`cli.py:205-220`）。
2. **配置装载**：`load_base_config`（`cli.py:59`）→ `load_config(args.config)`（`cli.py:334`）。
3. **CLI 覆盖提取**——最精巧段：第二个 `aux_parser`（`argument_default=SUPPRESS`，`cli.py:345`）重建「只含真正出现在命令行的参数」的命名空间，整体替换 `args`（`cli.py:386-389`），防配置文件值被 argparse 默认值反向冲掉；再按四张白名单路由进 `_config.{system,run,plugins,reporting}`（`cli.py:396-407`）。
4. **选择解析**：detectors 走旧 `detector_spec` 面（`cli.py:409-411`）；`--spec` 优先，legacy 三 flag 经 `legacy_selection_spec` 映射（`cli.py:413-444`）。
5. **校验**：`worker_count_validation` 封顶 `max_workers`（`cli.py:449-460`）；bootstrap 四连校验（`cli.py:473-494`）；`random.seed`（`cli.py:501-506`）。
6. **分派**：version/list_*/fix/report 等各自短路；`target_type` 存在才进扫描分支（`cli.py:651`），按 detector 是否显式给出选 `probewise_run`（探测自带 primary_detector）或 `pxd_run`（probe×detector 全矩阵）（`cli.py:763-774`）。

`_spec.py` 语法核心是 `Selector` dataclass（`_spec.py:38-56`）：`kind ∈ {plugin_path, none, tag, tier, intent}` + 极性。`_classify`（`_spec.py:164-204`）归一化裸 token：`all`/`*`→`probes.*`（`_spec.py:190-191`）、`<category>.all`→glob、`none` 为显式空选。`parse_spec_string`（`_spec.py:115-139`）拒绝选择器间空白——逗号免 shell 引号的取舍（`_spec.py:125-130`）。`_selection.resolve_spec`（`_selection.py:103-216`）四层落地：插件路径（无 include 默认全 active probes，`_selection.py:124-129`）→ tier 上限+tag AND（:131-138）→ buffs 并集无默认（:141-149）→ exclude 最后必胜（:151-168）。intent 独立轴，缺省注入 `"S"`（`_spec.py:30`）。

## 外部连接

- 上游：`pyproject.toml` console_script 与 `__main__.py` 指向 `cli:main`。
- 下游：`command.probewise_run/pxd_run`（`command.py:374-386`）→ harnesses；`ThresholdEvaluator`（`cli.py:740`）；`_plugins.load_plugin` 实例化 generator（`cli.py:744-746`）。
- 横向：大量写 `_config.transient`——`cli_args`（`cli.py:389`）、`intent_spec/active_probes`（`cli.py:713-716`）是 IntentService/harness 交接面。
- 错误面：`_check_selection`（`cli.py:678-705`）区分 rejected（未知选择器）与 inactive（模块存在但全 inactive，issue #830），`--skip_unknown` 时黄色 SKIP，否则 raise。

## 数据流

```
sys.argv → parse_args → 三层配置 merge 进 _config
  → aux_parser 提取 cli_args → 白名单路由
  → parse_spec_string → _config.run.spec (file dict, cli.py:423)
  → parse_spec_file + resolve_spec → Resolution{probes,buffs,intents,rejected,inactive}
  → parse_plugin_spec(detector_spec) → detector_names（cli.py:728-732）
  → ThresholdEvaluator + load_plugin(generator) → probewise_run | pxd_run
```

注意 `run.spec` 先 `to_file_dict()` 存配置形、扫描时 `parse_spec_file` 读回（`cli.py:675`）——同一 Spec 经两种 transport 往返，CLI 串与 YAML 语义严格一致。

## 设计决策

1. **延迟导入贯穿全文件**：`main()` 内重依赖全部函数体内 import（`cli.py:41-56` 起），`--version` 不触发插件体系加载（NOTES-DIGEST batch-49 钉版的仓风源头）。
2. **`--spec` wins**：新旧并存统一以 `--spec` 为准（`cli.py:428-431`）；`legacy_selection_spec`（`_spec.py:258-280`）同时服务 config shim、CLI、fixer 迁移——单一映射三消费。
3. **错误信息可操作**：`_empty_reason`（`_spec.py:81-104`）对空选择给出人话诊断（如 tier 上限卡掉显式 probe）；`tier:9` 默认（`_selection.py:22`）对应 UNLISTED。
4. **并行 hint**：generator 支持 `parallel_capable` 且未配置时打印提速提示（`cli.py:748-756`），25% 概率展示（`command.py:12`）。

## 新人提示

- 读 `main()` 先看 `cli.py:651-774` 扫描主分支建全局感，再回读参数段；中部 300 行命令分支与主流程无关。
- 调「probe 没被选中」：直接 `--list_probes --spec <你的spec>`（`cli.py:547-556`），走同一 `resolve_spec` 路径；`empty_reason` 会指出 tier/tag/exclude 哪个环节筛掉。
- `--deprefix` 是反向 flag（`action="store_false"`，`cli.py:119-123`）：加了反而关掉 deprefix。
- 改选择语法须同改 `_spec._classify` 与 `_selection` 解析层，两文件 docstring 明确分工（语法 vs 解析）。
- 新增命令 flag 必须同步登记 `command_options`（`cli.py:6`），否则 `cli_args` 补拷贝循环（`cli.py:381-382`）拿不到属性。
