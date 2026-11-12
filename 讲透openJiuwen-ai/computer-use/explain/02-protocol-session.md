# 02 · protocol/records + observation/model + session/state——公共协议词汇与会话状态属主

## 一、角色定位

这三个文件构成引擎的**词汇层与状态层**，各自回答一个问题。`protocol/records.py`（200 行）：native 查询结果在 wire 边界上长什么样——全文件只有 `TypedDict`/`TypeAlias` 声明，**零函数零逻辑，100% 纯类型契约**。`protocol/observation/model.py`（369 行）：三平台（`Backend = Literal["macos","windows","linux"]`，model.py:20）事实归一化后，引擎内部流转的不可变观察图长什么样。`session/state.py`（61 行）：一个 App 会话在两次调用之间记住了什么——`AppState` 是会话侧唯一的可变状态属主。`protocol/__init__.py` docstring 给出包级铁律："Strict validation for the native protocol; no desktop or MCP dependencies"——协议层不认识上层表现层。

## 二、内部结构

**records.py：10 个 TypedDict + 2 个 TypeAlias**。`Record`（L15）开放属性字典；`FactNode`（L35）单对象原始事实（`node`/`requestedFields`/`values`/`fieldStatus`/`actions`，L46-50）；`NativeRelation`（L53）一页关系读（`certainty`/`state`/`cursor` 等，cursor 为 NotRequired L73-76）；`FactCollection`（L79）有界采集顶层容器（`nodes`/`relations`/`unread`/`stopReasons`/`changeToken`，L96-106）；`ApplicationInfo`（L109）/`SurfaceInfo`（L133，`parentState: Literal["known","none","unknown"]` L157）；`NativeDirectory`（L163）目录变体别名；`RelationPage`（L172）/`TextPage`（L186，`next` 为 None 表示读完 L199）。

**observation/model.py：不可变记录族**。地基：`_freeze`（L29-42，递归冻结为 `MappingProxyType`/tuple，L34-35 环检测直接 ValueError）、`_equal`（L45-61，NaN 对等 L50、bool 严格类型 L59-60）、`_Immutable` 基类（L64-82：`__eq__` 逐字段 `_equal`、`__hash__=None`、`__deepcopy__` 返回自身 L76-78、`__post_init__` 冻结全部字段 L80-82）。其上 20 个 frozen dataclass：`ReadRef`（L101，`consistency: captured|live` L107）；`ReadIssue`（L113，十态失败词表 L118-129，`alternatives`"冲突证据，非自动择优结果" L132）；`CoordinateSpace`（L135，单位×六原点×y 方向×`to_parent` 六元参数 L150）；`Action`（L173，`kind` 归一失败即 custom L177）；`TextInfo`（L222，`source`"不能按相同字符串合并" L226）；`States`（L243，21 状态槽，"None never means false" L245）；`Relation`（L268，`evidence: reported|verified|candidate` L282）；`NativeNode`（L332）；`NativeObservation`（L357，`interval_ns` 采集时间区间 L364）。

**state.py：AppState**（L16-55）13 字段：`selector` 原始选择符、`running` 确认的运行身份、`selection` 固定工作窗口、`observation: object | None`（L39 注释"the read branch owns its definition"——本层刻意不认识其结构）、`query_target`/`query_scope_kind` 后续查找的精确 native 作用域、`directory` 窗口目录、`refs: OrderedDict` 编号→元素快照（L43）、`windows`、`delivered`/`delivered_pixels` 交付纪元、`capture_expired` 坐标过期位（L45-47）。

## 三、外部连接

- **records 的两头**：native 侧 `native/semantics.py` 定义 FactCollection 语义；interaction 侧 `read/facts/table.py`、`read/acquisition/reader.py`、`query/pipeline.py` 等消费。全仓 116 个文件 import protocol（records 或父包）。
- **归一化枢纽**：`protocol/observation/adapters/normalize.py` 承接 driver wire 事实（L401 `Adapter.__init__(wire, facts)`），L429 构造 `NativeObservation`；`codec.py` 的 `encode_observation/decode_observation`（observation/__init__.py L6-7 导出）被 `protocol/presentation.py` 与 `interaction/read/presentation/document.py` 消费——序列化只走 codec。
- **AppState 的唯一属主**：`session/bindings.py` 的 `SessionBindings`——`register`（L26-27）从 scope 的 `_nativeState` 恢复或新建 AppState；`state()`（L29-33）查不到 owner 即 `local_failure("unknown App", ..., "stale_target")`；`remember`（L103-106）写元素快照进 `state.refs` 并手写 LRU——超 8192 条 `popitem(last=False)` 淘汰最老；窗口目录 LRU 32 条（L63-64）。bindings.py docstring（L6-8）划清职责："This store never discovers windows, chooses a current modal or constructs public App wrappers"——发现与决策归 interaction controller。

## 四、数据流

读链路的词汇接力：driver 返回 wire dict → decoders 按 records.py 词汇解码为 `FactCollection`（`fieldStatus` 显式保留缺席/失败读，records.py:8）→ `adapters/normalize.py` 逐字段装配 `NativeNode` → `NativeObservation` 构造即被 `__post_init__` 深冻 → codec 编码交付 presentation/agent。

状态链路（一个 App 的生命周期）：用户给 `selector` → 观察后填 `running` → 选窗后固定 `selection` → 每次读刷新 `observation` 与 `directory` → 元素引用以十进制编号存入 `refs` → 交付模型时记录 `delivered`（capture id + epoch）；后续坐标操作前检查 `capture_expired`。跨调用的"记忆"全显式落在这 13 个字段里——没有隐藏缓存。

## 五、设计决策与权衡

1. **三态不说谎哲学**：`States` 的 None≠false（model.py:245）、`SurfaceInfo.parentState` 三值（L157）、`ReadIssue` 十态显式失败——agent 语境下把"未知/未读/失败"与"假"混同会造成误操作，这套词汇表把证据等级做进类型。
2. **records 用 TypedDict、observation 用 frozen dataclass**：records 是 JSON 形态的 wire 边界（编解码零转换）；observation 是域内值对象，需要等值比较、冻结与 Literal 词表收窄。各取所长，代价是 normalize 适配层的手工搬运（1100+ 行）。
3. **不可变性三件套**：环检测（L34-35）防共享图死循环；`__deepcopy__` 返回自身（L76-78）让观察零拷贝穿越 copy 边界；`__hash__=None`（L74）——含 NaN 对等语义的值无法提供自洽 hash，宁可禁用。
4. **observation 字段刻意退化成 object**（state.py:39）：会话层不依赖 read 分支的观察结构；TYPE_CHECKING 内 import `NativeDirectory as DirectoryFacts`（L58-60）同理——类型提示不构成运行时依赖。
5. **有界性入类型**：`FactCollection.unread`+`stopReasons`（records.py:104-105）、`Relation.offset/total`、`TextPage.next`——大 UI 树永远分页、永远可能不完整，协议从词汇上禁止"假装读全了"。

## 六、新人提示与坑

- **TypedDict 是 dict**：records 词汇运行时零校验、零属性访问——`fact["fieldStatus"]` 不是 `fact.fieldStatus`；真正校验在 protocol/observation/validation.py。
- **MappingProxyType 不可 json.dumps**：冻结后的观察走 `codec.py` 专用编码，别拿 `json.dumps` + `asdict`——会炸。
- **AppState 改字段合法**（普通 dataclass），但入口只有 SessionBindings 的方法，绕过它直接改 `state.refs` 会绕过 8192 LRU。
- **refs 淘汰是静默的**：老引用被挤出后 `element_snapshot`（bindings.py:108-118）抛 stale_target，模型侧需重新观察。
- **`state.scope()` 回退链**（bindings.py:38-40）：selection.root → application → selector，注释强调"清缓存不得把已绑定 App 变回查找"——排查作用域漂移先看这三层。
- **包名映射**：`computer_use.protocol.*` 实居 `computer_use_engine/protocol/`（setup.py:22 别名）。
