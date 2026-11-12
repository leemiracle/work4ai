# 03 probes 探测族：Mixin 组合与四层基类

## 角色定位

`garak/probes/` 是攻击/测试用例层：每个 Probe 封装一种探测手法（越狱、编码绕过、注入、泄露、多轮诱导），产出 Attempt 流交 generator。图谱 L02「probes 探测族」是最大插件家族——全仓 inherits 边 227 条（图谱统计）绝大多数指向本目录基类，`grep "class.*Probe" garak/probes/*.py` 计 155 处。设计核心：一个 `Probe` 基类 + 三个场景变体（TreeSearch/Iterative/Intent）+ 元类/Mixin 组合；所有子类经 `probes/__init__.py:1` 的 `from .base import *` 星号链获得 `garak.probes.Probe` 统一引用名。

## 内部结构

**Probe 基类**（`probes/base.py:31`，继承 Configurable）是声明式模板，类属性即元数据：`doc_uri`（:35）、`lang` BCP47（:37）、`active`（:39，**默认 False**）、`tags` MISP（:41）、`goal`（:43）、`intent` trait 代码（:49，具体探针必填，payload intent 优先）、`primary_detector/extended_detectors`（:53-55）、`modality`（:64）、`tier`（:68）。构造器（:75-145）：配置装载、`recommended_detector`→`primary_detector` 迁移（:87-106，0.9.0.6 起废弃）、langprovider 双向实例化（:121/:146-158）、triggers 本地化（:122-145，类型错抛 PluginConfigurationError :142-144）。

执行链：`_mint_attempt`（:217-280）统一包装 str/Message/Conversation，system_prompt 前置（:226-232），payload intent 覆盖（:263）；`probe()`（:385-470）prompts 深拷贝→langprovider 本地化（:402-425）→跨语言原文存 `notes["pre_translation_prompt"]`（:430-455）→逐 seq 铸 attempt（:457）→buff hook（:460-461）→`_execute_all`；`_execute_all`（:321-383）在 `parallelisable_attempts` 且 `generator.parallel_capable` 时走 `Pool.imap_unordered`（:332-369），errno 24 转 GarakException 并提示 ulimit（:359-363），两路径统一完成即写 reportfile（:351-354）；`_execute_attempt`（:309-319）precall→generate→untransform→postprocess→清史→deepcopy；`_postprocess_attempt`（:282-307）输出 lang 回填+反向翻译（:290-306）。

**三个场景基类**：`TreeSearchProbe`（:483-688）树搜索机，五个抽象节点操作（:496-522）+ `per_generation_threshold/per_node_threshold/strategy`（:488-494）；`probe()` 循环内**自带 detector**（:531/:605）评分，均值过阈值才扩子节点（:649-663），节点分写 `entry_type:"tree_data"` 行（:634-646），结束换 `always.Passthru` 防重复检测（:676-678）。`IterativeProbe`（:691-843）多轮：`max_calls_per_conv=10`（:714），BFS 扩张（:802-809），超 `soft_probe_prompt_cap` 提前终止（:796-799），每轮顺带生成下轮 attempts 入队（:836-843）。`IntentProbe`（:846-953）意图轴：构造期三步 populate（:862-864），`_prune_data` 重写为**按 intent 均衡剪枝**（:874-904），空 intent 时 no-op（:947-953）。

**Mixin/元类范式**：`probes/dan.py:28` 的 `DANProbeMeta` 从类名推断 `prompt_file` 并注册 tags；`AutoDANCached/AutoDAN`（:352/:367）以 `class X(garak.probes.Probe, metaclass=DANProbeMeta, tier=..., prompt_file=...)` 声明式组合。

## 外部连接

- **被 harness 驱动**：`harnesses/probewise.py:82-87` 逐 probe load_plugin 并取 `primary_detector`（:98-101）与 `extended_detectors`（:102-107）；pxd 无视推荐做全组合。
- **依赖 generator**：`probe()` 首行 `self.generator = generator`（`probes/base.py:389`）；GCG/BEAST 要求特定形态（`probes/suffix.py:129-134` 校验必须是 huggingface.Pipeline）。
- **依赖 detector**：primary_detector 字符串由 harness 拼 `load_plugin("detectors."+name)`（`harnesses/probewise.py:16-19`）；默认哨兵 `["always.Fail"]`（`probes/base.py:51`）——没配 detector 全量报 FAIL 提醒作者。
- **依赖服务**：langservice/intentservice 由 harness 启动期装载（`harnesses/base.py:23-40`）。
- **星号链**：`probes/__init__.py:1-2` 仅两行——`from .base import *` + `from ._tier import Tier`；改 base 导出名影响全部 60+ 模块。

## 数据流

```
harness: load_plugin("probes.dan.Dan_11_0") → Probe.__init__（配置/迁移/本地化）
  → probe(generator): prompts → langprovider → Message(lang=target_lang)
  → _mint_attempt ×N（seq 对齐；跨语言另存 pre_translation_prompt）
  → _buff_hook（裂变）→ _execute_all（Pool 或串行）
    单 attempt: precall → generate → (untransform) → postprocess → report.jsonl
  → attempts_completed → harness 交 detector 打分
```

TreeSearchProbe 例外：detector 在搜索循环内自调用，返回时已带分（`probes/base.py:605-608`）。

## 设计决策

1. **active=False 默认保守**：不显式声明就不被 `probes.*` 通配选中（`_selection.py:49` 只取 active）。动态攻击类几乎全 active=False，配对 Cached 版 active=True（`suffix.py:47 GCGCached` vs :105 GCG）。
2. **模板方法模式**：`probe()` 骨架不动，变化点全下沉钩子——IterativeProbe 只重写 `_postprocess_attempt`（`probes/base.py:836`）即完成多轮语义。
3. **树搜索自带 detector 是性能取舍**：循环内检测（`probes/base.py:605`）免整树后全量检测；代价是与 primary_detector 强绑定，结束换 Passthru（`probes/base.py:678`）保接口不变。
4. **errno 24 专项处理**（`probes/base.py:359-363`）：Pool 最常见崩溃源给了人话修复提示。
5. **deprecated 字段构造期迁移**而非报错（`probes/base.py:87-106`）：兼容成本压在基类一处。

## 新人提示

- 新探针最小清单：继承 `garak.probes.Probe`，设 `prompts/goal/primary_detector/tags/tier/active/intent`——缺 `active=True` 永远不跑；缺 primary_detector 静默落 `always.Fail` 全 FAIL。
- 选基类：静态提示集→Probe；模型反馈循环→IterativeProbe；概念树遍历→TreeSearchProbe；按意图轴扫 typology→IntentProbe。
- docstring 首行写人话描述——`--list_probes -v` 的表直接读它（`probes/base.py:117-120`）。
- 多进程下探针被 pickle，不可序列化属性须挂 `_unsafe_attributes`（`configurable.py:29`）。
- tier 语义：`tier:1` 只含 tier 1，`tier:9` 才含 UNLISTED——最小扫描 `--spec "tier:1"`。
