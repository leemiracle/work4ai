# 11 · fixer 迁移族与 intents：配置演进引擎与意图存根

## 一、角色定位

`garak/resources/fixer/` 是**配置文件迁移引擎**：garak 插件改名后，用户手里的旧 YAML/JSON 配置靠它自动升级——`garak --fix`（cli.py:310 帮助文本）把加载的配置过一遍迁移链再写回（cli.py:586, 615-632）。`garak/intents/` 是意图体系的代码侧：3 行基类 + 存根 dataclass + 两个示例意图，配合 `garak/services/intentservice.py` 与 data/cas/ 数据构成"攻击意图" taxonomy 的运行面。两者共同点：都极小、都被更大的机制（_spec/services）牵着走。

## 二、内部结构

fixer/__init__.py（59 行）三件事：`Migration` 基类（:16-20，仅一个抛 NotImplementedError 的 `apply(config_dict)->dict`）；**运行时动态发现**（:24-42）——`sorted(os.listdir)` 按文件名序枚举包内模块（:26），inspect 取类成员后用 `Migration in klass.__bases__` 过滤（:38，只认**直接**继承），类名再排序（:33-41）；`migrate()`（:45-59）deepcopy 后顺序过链、配置有变才打日志。**文件名即执行序**：迁移脚本一律 `YYYYMMDD_描述.py` 命名，11 个文件从 20240628_gcg_rename 到 20260612_run_spec，时间戳天然全局有序。源码核实：**11 个迁移文件合计 29 个 Migration 子类**——20250224_lightweight_probe_defaults.py 一家 17 个（:8-253+，Figstep/GraphConn/Primes/… 批量搬家），20250220_unsafe_content_rename.py 与 20250925_model_target_nametype.py 各 2 个，其余各 1；图谱批阶段补建的"基类+12 子类"节点少于源码实况，是补建口径非全量。`_plugin.py:12-44` 的 `rename()` 助手是绝对主力：deepcopy 配置树按 path 下钻，遇到 plugins 层时连 `probe_spec`/`detector_spec`/`buff_spec` 三个逗号分隔列表也逐项改写（:19-38），三分支区分整体替换/类名后缀 sub/模块前缀替换——典型用法见 20250908_xss_rename.py:8-27（probe 与 detector 两侧同步 xss→web_injection，顺带 MdExfil20230929→PlaygroundMarkdownExfil 类改名）。最新的 20260612_run_spec.py 最重（60 行）：`MapLegacySelectionToSpec`（:32）把弃用的 probe_spec/buff_spec/probe_tags 收敛进统一 run.spec 语法；已显式设 run.spec 时旧键只丢不转（:45-47 注释）；`_reject_unknown_selectors`（:13-29）在迁移期就解析 spec、发现指向不存在插件直接抛 ValueError——防 --fix 产出运行期才炸的配置。

intents/base.py 的 `Intent` 基类是真 3 行（:10-12）：唯一契约 `stubs() -> Set[str]`（基类返回空集）。重量在 Stub 家族：`Stub`（:14-21，intent+content 双槽、可变但提供 hash/eq）；`TextStub`（:24-40，setter 强制 str 否则 TypeError）；`ConversationStub`（:43-83，str 自动包装成 Conversation，:80-83 的 from_textstub 支持 TextStub 升格）。两个实现：S003.py 的 Productkeys（:10 起，动词×关键词×产品三维笛卡尔积造产品密钥索词）、T999.py 的 Test（:12-17，单个 TextStub("test")）——**编码前缀 S=真实意图、T=测试意图**。

## 三、外部连接

fixer 上游：cli.py:586-632 的 --fix 分支（迁移后 diff 有变则 yaml.dump 提示）；测试 tests/resources/test_fixer.py:260+ 用 importlib 按字符串加载 20260612_run_spec 模块。fixer 下游：_spec.py 的 legacy_selection_spec/parse_spec_file（run_spec 迁移的语法后端）。intents 上游：intentservice.py:40 导入三种 Stub，:42 定位 cas 数据目录，:67/:76 两个装载器读 trait_typology.json（意图类型学）与 intent_detectors.json（意图→detector 映射），enabled()（:58-64）要求 _config 已加载；harnesses/base.py:243-253 在 IntentProbe 分支调 intentservice.get_detectors 按 intent 动态选 detector；probes/base.py:25 与 probes/grandma.py:25 直接消费 Stub/TextStub 做意图标注。意图编码同时被 report_digest.py:43-48 反查人名、被 evaluator 的 intents 分桶（evaluators/base.py:72-74）追踪——一条编码贯穿 存根生成→attempt 标注→eval 统计→digest 矩阵。

## 四、数据流

迁移流：用户旧配置 → cli 加载为 dict → fixer.migrate 按 29 个子类时间序逐个 apply（每步 deepcopy 保护原值）→ 变更回写提示。意图流：intent 编码（如 S003）→ intentservice 从 cas 数据/stub 目录或 Intent 子类取存根 → IntentProbe 用存根生成 attempt 并打 intent 标 → harness 按_intent 查 intent_detectors.json 选 detector → evaluator 按 intent 分桶计数 → digest 的 technique_intent_matrix 按 demon: 标签池化成技术×意图矩阵（report_digest.py:507-578）。

## 五、设计决策

1. **时间戳文件名当排序键**（fixer/__init__.py:26）：零注册表、零依赖声明，目录列表即迁移链——命名纪律就是架构。
2. **直接基类过滤**（:38）：`Migration in klass.__bases__` 拒绝隔代继承，迁移子类不许再被继承，防执行序歧义。
3. **迁移期校验**（20260612_run_spec.py:13-29）：把"运行时才发现插件不存在"提前到 --fix 时刻，错误信息直接给出修正示例。
4. **Intent 基类极简 3 行**：不定义数据、不定义加载，只约定 stubs() 契约——意图的实体在数据侧（cas JSON）而非代码侧。
5. **Stub 可变但可哈希**（base.py:60-66 注释自认 contentious）：方便放 set 去重，代价是构造后改内容会破坏哈希一致性。
6. **xss 改名迁移的对称性**（20250908_xss_rename.py）：probe 与 detector 两层四组 rename 一次做完——插件重命名必须配套迁移，否则用户配置静默失效。

## 六、新人提示

给插件改名的工作清单：新类名落地 + fixer 加 `YYYYMMDD_*.py`（用 `_plugin.rename` 别手写字典操作）+ 测试补 case + plugin_cache 重建（resources/rebuild_plugin_cache.sh 用 mtime 触发失效）。三个坑：① 迁移文件名日期必须晚于既有链尾，同名日会因排序不稳定；② Migration 子类 apply 是**静态风格但未声明 @staticmethod**（各文件 `def apply(config_dict)` 首参无 self，基类同款）——照抄现有写法即可，别"修正"它；③ intents 新增意图记得同步 trait_typology.json 与 intent_detectors.json 两份数据，缺后者时 harness 走 fallback 用 probe 自带 detector 名单并打 warning（harnesses/base.py:247-252）。
