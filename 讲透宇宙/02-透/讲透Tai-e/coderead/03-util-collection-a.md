<!-- coderead unit 03 | files: 24 个 | 全量深读 2026-10-13 -->

# coderead 03 · util/collection 前半：集合基类族与内存优化容器

## 1. 包职责与架构位置

`pascal.taie.util.collection` 是 Tai-e 的 L1 基础设施层，本单元覆盖字母序前 24 个文件：集合扩展接口的抽象骨架族（`AbstractSetEx`/`AbstractMultiMap`/`AbstractTwoKeyMap` 等）与 Tai-e 最有特色的**内存优化混合数据结构**——singleton/small/large 三态自动升级的 `AbstractHybridMap`/`AbstractHybridSet` 家族、索引驱动的 `IndexMap`/`IndexerBitSet`、位集抽象 `IBitSet`/`AbstractBitSet`/`GenericBitSet`。静态分析负载"绝大多数集合极小、极少数巨大"，JDK 容器表头开销不可接受，故空/单元素集仅占一个引用位、小集用 ArrayList 线性存、超阈值自动升级哈希/位集——Tai-e（ISSTA 2023）内存性能贡献的一环。工厂 `Maps`/`Sets` 与 `RegularBitSet`/`SparseBitSet`/`Views` 等属第 4 单元。

## 2. 逐类深读

#### AbstractBitSet AbstractBitSet.java:32
`IBitSet` 骨架。核心设计：**双集合运算（intersects/contains/andNot/or/xor/orDiff）全部迭代参数集的置位位、回调本对象单比特操作**——如 `intersects`（AbstractBitSet.java:56）把 Action 喂给 `set.iterateBits`，无需知道对方类型即可支持异构位集运算，代价是 O(参数集基数)。`OrDiffAction`（:145）OR 同时收集新增位为 diff 集；`ChangeAction`（:181）统一携带 changed 标志。`setTo`（:195）= clear+or。`and` 由子类按字实现。

#### AbstractHybridMap AbstractHybridMap.java:56
三态混合 Map 骨架。状态由 `singletonKey`/`singleton_value`（:72/:77）、`map`（:82）、`isLargeMap`（:87）编码，不变量"singletonKey 与 map 至多一个非 null"（:59）。`put`（:174）是三态核心：singleton 命中原地替换（:177）；singleton 冲突先 `upgradeToSmallMap`（:195，新建 `ArrayMap<>(threshold)`）；map 态下 `size()+1 > getThreshold()` 则 `upgradeToLargeMap(threshold*2)`（:185-186）。阈值默认 8（:67），覆写点 `getThreshold()`（:108）。`putAll`（:220）批量预判：`maxNewSize==1` 落 singleton（:228），超阈值直接升大且容量 `maxNewSize+threshold`（:237），入参先逐 key 判空防半写（:242）。易错点：只禁 null key（:175），value 为 null 时 `containsValue` singleton 分支 NPE（:151）。

#### AbstractHybridSet AbstractHybridSet.java:52
对称的 Set 骨架：`singleton`（:68）、`set`（:73）、`isLargeSet`（:78），同样至多一个非 null（:55）。`add`（:117）：singleton 相等返回 false；冲突先 `upgradeToSmallSet`（:135，new `ArraySet<>(threshold)`）；set 态 `size()+1 > 8`（:63）触发 `upgradeToLargeSet(threshold*2)`（:126-127）。`addAll`（:158）批量预判同 Map 版（:167/:181）。`iterator`（:241）singleton 态带 remove（:262）。`removeAll`（:293）覆写为逐元素 remove（绕过 `AbstractSet.removeAll` 启发式）。

#### AbstractMultiMap AbstractMultiMap.java:35
`MultiMap`（一键多值，接口在第 4 单元）骨架。视图走"transient 缓存+惰性构建"：`entrySet()`（:57）缓存于 :54 并包 unmodifiable，其 `contains`（:69-75）翻译为 `this.contains(k,v)`；子类只需实现 `entryIterator`（:89）。`values()`（:97）经 `Views.toMappedCollection` 派生。

#### AbstractSetEx AbstractSetEx.java:30
`SetEx`（Set+Copyable+增强运算）骨架。`copy()`（:34）= newSet+addAll；`addAllDiff`（:41）把 c 逐个 add、新加入者收集为 diff 集——差分传播基础原语。两者依赖工厂 `newSet()`（:58），**默认抛 UnsupportedOperationException：子类不覆写则运行时才爆炸**。`hasOverlapWith`（:63）= !Collections.disjoint。

#### AbstractTwoKeyMap AbstractTwoKeyMap.java:38
`TwoKeyMap` 骨架。`get(k1,k2)`（:67）两级查找：`get(k1)` 拿二级 Map 再 `.get(k2)`；`containsKey` 重载（:46/:51）都基于 get 判 null，故**子类必须保证 value 非 null**（:43）。三视图缓存 entrySet（:75）/`twoKeySet()`（:119，Pair 视图）/values（:142）；子类只需实现 `entryIterator`（:111）。

#### AbstractTwoKeyMultiMap AbstractTwoKeyMultiMap.java:34
与上同构但 value 是集合：entrySet 缓存（:41-51）、`EntrySet.contains` 翻译为三元组 contains（:59）、抽象 `entryIterator`（:76）。`equals`（:84）按 `twoKeySet()` 逐双键比较 value 集合（:100）。

#### ArrayMap ArrayMap.java:43
基于 `ArrayList<Entry<K,V>>`（:51）的微型 Map，**get/put/remove 全 O(n)**（`getEntry` 线性扫描 :135；`put` :106 先查后尾插；`remove` :119 定位后左移）。构造链 :60-72 关键在 `fixedCapacity`：默认 `ArrayMap(8,true)` 容量钉死，`ensureCapacity`（:144）超容量抛 `TooManyElementsException`（:146）——Hybrid 家族护栏：`newSmallMap`（AbstractHybridMap.java:115）以 threshold 建 fixed ArrayMap，升级判断先于 put 不可能溢出。TODO（:40-41）指向 remove 空洞复用。

#### ArraySet ArraySet.java:41
ArrayMap 的 Set 对偶：`ArrayList<E>`（:48）+ `fixedCapacity`（:52）。`add`（:106）先 contains（O(n)）去重再 `ensureCapacity`（:186）尾插。特殊构造器（:73）**直接接管调用方 ArrayList**（须自证无重复）。`addAllDiff`（:164）在 c 非 Set 时经 `Sets.newHybridSet()`（:174）过滤重复。

#### CollectionUtils CollectionUtils.java:40
集合静态工具。`findFirst`（:51）谓词首中；`getFirst`（:64）裸 `iterator().next()`，空集合即抛 NSEE；`toString`（:107）输出**按字符串排序**——专为分析结果比对设计；`toSet`（:114）非 Set 入参转 HybridSet。

#### GenericBitSet GenericBitSet.java:55
把 `IBitSet` 适配成 `java.util.Set<E>` 的抽象基类：`bitSet`（:58）经 `IBitSet.newBitSet(isSparse)`（:61）选实现。四个抽象方法构成对象↔索引契约：`getIndex`/`getElement`（:258/:263）、上下文 `getContext`（:253）、`newSet`（:238）。不变量 `e.equals(getElement(getIndex(e)))` 由 `checkInvariant`（:85）以 **assert** 校验——生产 `-da` 下静默失效，跨上下文（不同 Indexer 复用同一索引段）混用无声出错，本类最大暗坑。批运算快路径（:90/:100/:110/:120）在对方同为 GenericBitSet 且 `checkContext`（:147，同样仅 assert）通过后直达位运算。`hashCode`（:214）混入 context。

#### HybridBitSet HybridBitSet.java:50
`AbstractHybridSet` 的位集升级版：携带 `Indexer<E>`（:53）与 `isSparse`（:55），`newLargeSet`（:63）无视容量参数返回 `IndexerBitSet<>(indexer, isSparse)`。覆写四批运算（:68/:79/:90/:101）：双方 set 都已是 GenericBitSet 时直达位运算。`addAllDiff`（:112）大集合快路径：对方是 large HybridBitSet 时 `otherSet.copy()` 拷贝再集合差（:129-132），一步把 this 与 diff 同时置大（:138）。**Javadoc 警告（:35-46）**：IndexerBitSet 与 HybridBitSet 互相批运算退化为逐元素迭代。

#### HybridHashMap HybridHashMap.java:32
最简 Hybrid 具体类：仅实现 `newLargeMap`（:49）返回 `new HashMap<>(initialCapacity)`，其余全继承。经 `Maps.newHybridMap()` 供给全仓。

#### HybridHashSet HybridHashSet.java:33
`newLargeSet` → HashSet（:50-52），并覆写 `newSet()`（:55）使 copy/addAllDiff 可用。`Sets.newHybridSet()` 的默认后端。

#### HybridIndexableSet HybridIndexableSet.java:33
面向 `E extends Indexable`（对象自带 `getIndex()`，Indexable.java:35-40）的混合集：`newLargeSet`（:43）→ `IndexableSet<>(isSparse)`。**反例警示：未覆写 `newSet()`，继承 `AbstractSetEx.newSet()`（AbstractSetEx.java:58）抛 UnsupportedOperationException——调 copy()/addAllDiff() 崩溃**。唯一消费者 PTA `AbstractPointer.java:44`（PFG 后继稀疏位集，恰好绕开此坑）。

#### HybridLinkedHashSet HybridLinkedHashSet.java:32
`newLargeSet` → LinkedHashSet（:36-38）保大集合迭代序；`newSet`（:41）补齐工厂。`Sets.newHybridOrderedSet()` 的后端。

#### IBitSet IBitSet.java:41
位集总接口。重造动机（:33-39）：JDK Set API 不满足分析需求——**变更型 API 一律返回 boolean changed**（set :54、clear :73、and :209、or :230、xor :258），并补 `orDiff`（:241，OR 同时返回差集，增量传播原语）、`intersects/contains`（:177/:197）、`setTo`（:265）。`iterateBits(Action)`（:275）是跨实现运算回调协议。静态工厂 `newBitSet(isSparse)`（:352）分流 SparseBitSet/RegularBitSet（第 4 单元）。

#### ImmutableMapEntry ImmutableMapEntry.java:25
包私有：继承 `MapEntry`（第 4 单元）仅把 `setValue` 改抛 UnsupportedOperationException（:31-34）。

#### IndexMap IndexMap.java:58
索引驱动 Map：**不存 key，只存 `V[] values`（:65）**，`Indexer<K>`（:63，Indexer.java:41-52）负责对象↔索引，`values[index]==null` 即缺席——故禁 null value（:61）。定位"size 接近全集的稠密 Map"（:50）。`get`（:109）O(1)；`put`（:115）负索引抛 IllegalArgumentException（:127），`ensureCapacity`（:132）按 `max(index+1, 1.5×old)` 扩。迭代**沿数组线性扫非 null 槽**（`nextNonNull` :234，O(capacity) 而非 O(size)）。内部 MapEntry（:276）key 经 `indexer.getObject` 物化（:284）、setValue 抛 UOE（:299）。前置：indexer 生命周期内稳定。

#### IndexableSet IndexableSet.java:46
`E extends Indexable` 的"半功能"位集 Set：只存索引位（:48），contains/add/remove（:55/:60/:65）经 `i.getIndex()` 直达位操作。**`iterator()` 直接抛 UnsupportedOperationException（:70-72）**——无法枚举元素，只适合存在性检查（完整功能用 `IndexerBitSet`，:37-38）。继承 AbstractSetEx 为充当 Hybrid 的 large set。

#### IndexerBitSet IndexerBitSet.java:36
`GenericBitSet` 标准落地：Indexer 本身即上下文（:47-49），`getIndex/getElement`（:52/:57）纯委托。`newSet`（:62）保持稀疏/常规一致（:63）。全仓 9 处直接使用，典型构造见 LiveVariable.java:80。

#### IntList IntList.java:28
极简 primitive int 列表（避开装箱）：`int[]`（:30）+ size（:31），`add`（:39）容量翻倍（:45），`get`（:53）越界抛 IOOBE。无 remove/迭代 API，只服务 Dominators/SSA 内部算法。

#### LazyArray LazyArray.java:34
惰性初始化定容数组：`get(index)`（:43）首次访问经抽象 `createElement()`（:57）造元素占槽；`contains(index)`（:53）只探测不创建。**容量固定不增长**（:38-40）。前端 SSA 与 Dominators 按索引开槽，稀疏场景零分配。

#### Lists Lists.java:39
List 工具：`map`（:48）流式映射返 unmodifiable；`asSet(List)`（:75）返回**由 list 支撑的 Set 视图**——唯一性是调用方责任（:66-68）；`concatDistinct`（:92）LinkedHashSet 归并去重。

## 3. 修改热点（二次开发）

1. **新增 Hybrid 实现**：继承 `AbstractHybridSet`/`AbstractHybridMap` 只需实现 `newLargeSet`/`newLargeMap`（AbstractHybridSet.java:114 / AbstractHybridMap.java:124）；Set 侧**必须**同时覆写 `newSet()`（否则 copy/addAllDiff 运行时抛异常，HybridIndexableSet.java 是反例）；随后挂进 `Sets.java:74-84` 或 `Maps.java:81-87` 工厂。
2. **三态 put 扩容**：单条 `AbstractHybridMap.put`（:174-193，升级条件 :185、新容量 `threshold*2` :186）；批量 `putAll`（:220-246，容量 `maxNewSize+threshold` :237）；Set 侧 `add`（:117-133）/`addAll`（:158-185）。改阈值覆写 `getThreshold()`（:108/:98）而非动 `SMALL_SIZE`；**阈值须与 newSmallMap/newSmallSet（:115/:105）传给 ArrayMap/ArraySet 的固定容量一致**，否则小态溢出即 TooManyElementsException。
3. **ArrayMap/ArraySet 闸门**：`ensureCapacity`（ArrayMap.java:144 / ArraySet.java:186）是唯一扩容检查点；实现 TODO（ArrayMap.java:40-41）的"remove 空洞复用"须同改 remove 与 add。
4. **新增位集**：实现 `IBitSet`（或继承 AbstractBitSet 只补单比特原语）后同步改 `IBitSet.newBitSet`（IBitSet.java:352）；`checkInvariant/checkContext`（GenericBitSet.java:85/:147）只是 assert，跨上下文防护需自行加运行时检查。
5. **IndexMap**：扩容集中 `ensureCapacity`（IndexMap.java:132-138）；entry 只读（:299）与 keySet（:304）直操作 values 数组。

## 4. 集成触点

- **工厂是全仓唯一推荐入口**：`Maps.newHybridMap/newSmallMap/newMultiMap/newTwoKeyMap`（Maps.java:53-117）与 `Sets.newHybridSet/newSmallSet/newHybridOrderedSet`（Sets.java:70-84）；`Maps.newMap`/`Sets.newSet`（:57/:54）按 `ArrayMap.DEFAULT_CAPACITY=8` 自动分流小/大实现，业务代码几乎不直接 new 混合容器。
- **指针分析主线**：`HybridBitPointsToSet.java:32-33` 以 `HybridBitSet<>(indexer, isSparse)` 为 delegate（PointsToSet 默认实现）；`ClassHierarchyImpl` 同用 HybridBitSet；PFG 后继用 HybridIndexableSet（AbstractPointer.java:44）。
- **数据流分析**：`ReachingDefinition.java:68-69,93`、`LiveVariable.java:80` 等以 `IndexerBitSet` 做 SetFact、以 `IndexMap`（配 `ir.getVarIndexer()`）做 var→facts 稠密映射。
- **前端 IR/SSA**：IR uses 用 ArraySet（Invoke.java:142、AbstractBinaryExp.java:64）；SSA 构造与 Dominators 消费 LazyArray 与 IntList。
- **可独立复用**：`IntList`/`LazyArray`/`Lists`/`CollectionUtils`/`ArrayMap`/`ArraySet` 仅依赖 JDK 与同包 MapEntry/TooManyElementsException，可整包拷出即用；位集三件套另需 `pascal.taie.util.Copyable`/`Hashes`；`IndexMap`/`IndexerBitSet`/`HybridBitSet`/`IndexableSet`/`HybridIndexableSet` 强绑 `Indexer`/`Indexable` 契约，复用需连 Indexer 体系带走。
