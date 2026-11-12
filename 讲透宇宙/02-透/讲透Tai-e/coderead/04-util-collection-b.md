<!-- coderead unit 04 | files: 23 个 | 全量深读 2026-10-13 -->

# 第 4 单元：util/collection 后半（M–V 字母序 23 文件）

## 1. 包职责与架构位置

本单元是 `pascal.taie.util.collection` 字母序后半（MapEntry → Views，23 文件、5147 行），四条主线：①**位图底座**——`RegularBitSet`/`SparseBitSet` 是 `IBitSet`（IBitSet.java:41）的两大直接实现，pta points-to set 的性能底座（传播循环每轮都做集合并运算的性能关键路径）；`SparseIntSet` 是另一物种（经典 Briggs-Torczon sparse set），勿混淆。②**MultiMap/TwoKeyMap 族**——K→值集、K1,K2→V、K1,K2→值集三层接口+实现+只读包装+`Maps` 工厂，是 class hierarchy/call graph/CSManager 键值表的标准载体。③**通用集合件与契约**——Pair/Triple/UnionFindSet/SetQueue/Views 等多为零依赖可整文件搬走，外加 SetEx、TooManyElementsException 两个契约件。

组装链（本单元在最底层）：pta 差量传播 `DefaultSolver.java:354` → `HybridBitSet.addAllDiff`（HybridBitSet.java:112，稀疏/稠密调度）→ `GenericBitSet.addAllDiff` → 本单元 `RegularBitSet.orDiff`（RegularBitSet.java:474）/`SparseBitSet.orDiff`（SparseBitSet.java:792）。HybridBitSet/GenericBitSet/IndexerBitSet/AbstractBitSet 属前半单元。

## 2. 逐类深读

#### MapEntry MapEntry.java:35
可变 `Map.Entry` 实现；hashCode 委托 `Hashes.safeHash`。

#### MapMapTwoKeyMap MapMapTwoKeyMap.java:41
`TwoKeyMap` 标准实现（"map of maps"）：put 经 computeIfAbsent 惰性建二级表并手计数 size；remove(key1,key2) 在二级 map 清空后**级联删除一级 key**（MapMapTwoKeyMap.java:105），保证 keySet 无空键。

#### MapMultiMapTwoKeyMultiMap MapMultiMapTwoKeyMultiMap.java:39
`TwoKeyMultiMap` 实现（"map of multimaps"）。三个细节：①`get(key1)` 缺失时**每次新建**空 MultiMap（MapMultiMapTwoKeyMultiMap.java:96）——非单例、非 null（TwoKeyMap.get(key1) 缺失返回 null）；②remove 级联摘除空 multimap；③twoKeySet() 的 size() 遍历求和非 O(1)。

#### MapSetMultiMap MapSetMultiMap.java:45
`MultiMap` 标准实现（key→value-set）。get 缺失返回 `Set.of()`、存在返回 unmodifiable 视图；写入惰性建集、值集清空级联删键。**hashCode = backing map 的 hashCode**（MapSetMultiMap.java:238）——值集工厂选 TreeSet/HashSet 会改变 equals/hashCode 语义。

#### Maps Maps.java:41
Map/MultiMap/TwoKeyMap 族总工厂。路由：`newMap(int)` 容量 ≤ `ArrayMap.DEFAULT_CAPACITY`=8 → ArrayMap，否则 HashMap（Maps.java:57）——小容量走数组线性扫描省哈希开销。MultiMap 工厂族默认值集工厂 `Sets::newHybridSet`。全仓换默认容器从此一处切入。

#### MultiMap MultiMap.java:61
核心接口：K→无重复值集，null 键值全禁。get 返回 unmodifiable 视图；removeAll(key) 后 key 从 keySet 消失。勘误钉版：MultiMap.java:83 javadoc 语序颠倒，实现实际是**缺失返回空集、存在返回视图**，以实现为准。

#### MultiMapCollector MultiMapCollector.java:34
把 MultiMap 接入 Stream 的 Collector。combiner 是**破坏性合并** `m1.putAll(m2)`（MultiMapCollector.java:82）——并行流语义正确但合并 O(m2)。消费方：JClass、SinkHandler。

#### Pair Pair.java:27
`record Pair<T1,T2>` + Serializable。全仓 31 文件的基础积木，含 TwoKeyMap.twoKeySet 的键类型。

#### RegularBitSet RegularBitSet.java:33
**稠密位图**：`long[] words` + wordsInUse 逻辑长度，几乎是 `java.util.BitSet` 克隆但所有写方法返回 changed。核心机制：①**不变量**（RegularBitSet.java:81-85，assert）：最高有效字非零、wordsInUse 界内、其上全零，每个写操作末尾 checkInvariants()；②扩容取 max(2×len, required)；set 返回 `oldWord != newWord`（RegularBitSet.java:134）、clear 越界字不扩容直接 false；③**双态分派**：同型走字级快路径、异型回退 AbstractBitSet 逐位 iterateBits（AbstractBitSet.java:125）。特例：**`and` 异型直接抛 UnsupportedOperationException**（RegularBitSet.java:363）——AND 需反向清理 this 中 other 没有的位；SparseBitSet.and 同抛。跨型 AND 是 IBitSet 族既定边界。

`or` 无需 recalculateWordsInUse（RegularBitSet.java:468 注释：OR 只增不减）。**`orDiff`**（RegularBitSet.java:474-503）：从 other 高位字向低位扫，`diffWord = otherWord & ~oldWord`（RegularBitSet.java:492），首个非零时把 diff 的 wordsInUse 一次顶到位，差集紧凑。copy() 压缩复制（RegularBitSet.java:681）；equals 只认同类型。

#### SetEx SetEx.java:35
`Set`+`Copyable` 扩展接口，仅两方法：`addAllDiff(c)`（SetEx.java:44）——并入 c 并返回 c 中原不在本集的差集（差量传播正宗入口）；hasOverlapWith——判交集非空。ArraySet/IndexerBitSet/HybridBitSet 都实现。

#### SetQueue SetQueue.java:36
去重队列：LinkedHashSet 作 backing，poll 取插入序最早元素。易错点钉版：继承 AbstractQueue 契约——offer 对已在队元素返回 false，故 **`add()` 重复元素抛 IllegalStateException**，必须用 `offer`。消费方：InterSolver（InterSolver.java:79）。

#### Sets Sets.java:36
Set 工厂，与 Maps 对称：`newSet(int)` 容量 ≤ `ArraySet.DEFAULT_CAPACITY`=8 → ArraySet（Sets.java:54）；newHybridSet → HybridHashSet（小数组大哈希、不含 indexer）。

#### SparseBitSet SparseBitSet.java:43
**三层稀疏位图**（源自 brettwooldridge/SparseBitSet）：`long[][][] table`（SparseBitSet.java:155）= level1 table → level2 area → level3 block（long[32]）。LEVEL3=LEVEL2=5 锁死（**Do not change!**，SparseBitSet.java:66），LEVEL1=15 推导。核心思想：**连续零区不分配对象**——读三级判 null 短路，写 getOrCreateBlock 惰性建块（SparseBitSet.java:1016），resize 按 2 的幂扩表。

**运算骨架 `iterateBlocks`**（SparseBitSet.java:1099）：只迭代 **other 侧非 null block**，每块回调 BlockAction.accept；action 返回 selfBlock 是否归零，归零则把 self 的块/区置 null（惰性回收）。子类族：Or/AndNot/Xor/Intersects（短路）/Contains（判 `(selfWord|iteratedWord)!=selfWord`）。**`and` 是唯一不走骨架的运算**（SparseBitSet.java:597）——AND 还需遍历 this 的非 null 块。**`orDiff`**（SparseBitSet.java:792）：仅在字变化时写差集 `diffBlock[w3] = iteratedWord & ~selfWord`（SparseBitSet.java:834，selfWord 为 OR 前旧值），diff 块按需创建——差集只含新增的稀疏块。

**State 惰性缓存**：isEmpty/length/size/cardinality/hashCode 全先 updateState()（SparseBitSet.java:1239）——invalid 时全扫并顺带把全零块归一化为 null；写操作只置 state.valid=false，代价后移；clear(bitIndex) 有意不检查块归零，残留全零块等下次运算回收。

易错点钉版：①**`clear(int)` 恒返回 true**（SparseBitSet.java:226-234 两分支都 return true）——违反 IBitSet.java:73 "返回是否 changed" 契约（RegularBitSet 正确，RegularBitSet.java:168）；经 GenericBitSet.remove 透传，sparse 模式 IndexerBitSet.remove 恒报 changed——上层剪枝退化为不剪枝（正确性无损）。②序列化自定义：只写非零 (wordIndex,word) 对 + 三重校验。③copy() 走 `new SparseBitSet().or(this)`（SparseBitSet.java:952），运算复制非深拷。

#### SparseIntSet SparseIntSet.java:48
经典 sparse set：BitSet membership（O(1) 测试）+ IntList elements（O(k) 插入序迭代）双结构同写；构造需 maxValue 定容量。javadoc 明确警告勿与 SparseBitSet 混淆（SparseIntSet.java:45）。**无 remove/clear——只增集合**。消费方：Dominators。

#### Streams Streams.java:31
`concat(varargs)`（Streams.java:47）右折叠 `Stream.concat` 实现 N 路惰性拼接；toString 按字符串排序 join（测试断言用）。

#### TooManyElementsException TooManyElementsException.java:29
定容集合（ArraySet/ArrayMap）超容抛的 RuntimeException——把"固定容量"从静默行为升级为显式异常。

#### Triple Triple.java:25
`record Triple<T1,T2,T3>`。注意无 Serializable。

#### TwoKeyMap TwoKeyMap.java:61
二级键 map 接口，null 键值全禁。default：forEach/getOrDefault×2/computeIfAbsent；Entry 是 record。**钉版 API 遗留：`replaceALs`（TwoKeyMap.java:135）**——ALs 的 L 大写是历史拼写错误，公共接口不能顺手修（会 break 全部调用方）。

#### TwoKeyMultiMap TwoKeyMultiMap.java:58
TwoKeyMap 多值版：get(key1,key2) 返回值集视图、get(key1) 返回 MultiMap 视图；entrySet 复用 TwoKeyMap.Entry 保持三元组统一。方法面刻意小于 TwoKeyMap。

#### UnionFindSet UnionFindSet.java:32
并查集：union 按 rank 合并，findRootEntry **递归**路径压缩（UnionFindSet.java:107），AtomicInteger 维护连通分量数。两个易错点：①对不存在的元素 union/find 直接 NPE——只能查构造时传入的元素（UnionFindSet.java:44 全量预插）；②rank 保证树高 O(log n)，递归深栈安全。消费方：Mahjong 堆合并（Mahjong.java:63）。

#### UnmodifiableMultiMap UnmodifiableMultiMap.java:35
MultiMap 只读包装（包私有，经 Maps.unmodifiableMultiMap 进入）：7 个写方法全抛 UnsupportedOperationException（UnmodifiableMultiMap.java:64）；三个视图 transient 惰性缓存；equals/hashCode 全委托原集。

#### UnmodifiableTwoKeyMultiMap UnmodifiableTwoKeyMultiMap.java:33
同款只读包装：写方法抛异常，twoKeySet/entrySet 惰性缓存。

#### Views Views.java:42
零拷贝视图工厂，四个入口，**每个都把不变量外包给调用方**（各有 WARNING）：①toMappedCollection（Views.java:61）——迭代时才 apply mapper；不传 contains 时退化为 `super::contains`，**忽略 mapper 反向判断**。②toMappedSet——**不保证唯一性**。③toFilteredCollection（Views.java:228）——FilteredIterator 用 `next==null` 作哨兵，**backing 含 null 元素时迭代提前终止**。④toCombinedSet（Views.java:320）——直接拼接两 set，**不查重**（要求两 set 不相交）。全是活视图（backing 变则视图变）。

## 3. 修改热点（二次开发）

**热点一：换 points-to set 底层实现。** 接缝两层。底层位图层：实现 `IBitSet`（IBitSet.java:41），可只做单 bit/迭代，集合运算白嫖 AbstractBitSet 的 `iterateBits`（IBitSet.java:275）逐位回退，再照抄 RegularBitSet.java:359 的 instanceof 双态分派加字级快路径；注册点 `IBitSet.newBitSet(isSparse)`（IBitSet.java:352）。对象层：做 SetEx/AbstractSetEx 子类，或在 pta 的 PointsToSetFactory/DelegatePointsToSet 包装层替换——改动面最小。**契约红线**：①写方法必须如实返回 changed（SparseBitSet.clear 恒 true 是反面教材）；②跨型 and 抛异常是族内既定行为；③orDiff 必须"先取 set−this 差集、后 OR"（IBitSet.java:241），DefaultSolver 的传播终止性依赖 diff 空 ⇔ 无新事实。

**热点二：HybridBitSet 稀疏/稠密切换与 THRESHOLD。** 切换在 `AbstractHybridSet`：默认阈值 `SMALL_SIZE = 8`（AbstractHybridSet.java:63），getThreshold() 可覆写；元素数超阈即 upgradeToLargeSet(threshold*2)（AbstractHybridSet.java:126）。HybridBitSet 升级目标是 IndexerBitSet，构造透传的 isSparse（HybridBitSet.java:57）决定内部用 SparseBitSet 还是 RegularBitSet。调参影响：**调大** → 更多 pts 留在 ArraySet（无编号开销、无位图对象头；多数指针 pts 仅 1~3 个对象，位图纯浪费）；**调小** → 更早进位图（批量并/交字级并行，但每集合背 IndexerBitSet 对象+indexer 间接寻址）。pta 默认 isSparse=true（对象稀疏、位号跳跃大，null block 省内存）；若自建 indexer 按发现序连续编号（稠密），改 RegularBitSet 更快。

**热点三：MultiMap 值集工厂。** `Maps.newMultiMap` 族默认 `Sets::newHybridSet`；换值集类型同时改变性能曲线与 MapSetMultiMap.hashCode——集合要当 HashSet 键用时值集类型必须全链一致。TwoKeyMap.replaceALs 拼写是公共 API，修拼写=全仓 break。

## 4. 集成触点

**IBitSet 契约面**：单 bit 操作+四向扫描（next*/previous*，负索引抛异常）；批量运算（and/andNot/or/orDiff/xor/intersects/contains/setTo/clear）；状态查询（isEmpty/length/size/cardinality）。三处关键设计：①写操作返回 changed（差量剪枝依据）；②`Action<R>`+`iterateBits`（IBitSet.java:275）是异型运算通用桥——AbstractBitSet 用它实现跨型 or/andNot/xor/orDiff/intersects/contains 逐位回退；③`IBitSet.newBitSet(isSparse)`/`of(int...)` 工厂入口。

**Indexer 契约**：`pascal.taie.util.Indexer`（Indexer.java:41）——getIndex/getObject 双射，对象→位号唯一通道。IndexerBitSet 组合 Indexer 与 GenericBitSet 即得 Set\<E\> 语义位图集；HybridBitSet 需外部传 Indexer；GenericBitSet 要求同 context（=indexer）集合间运算才有意义。

**差量传播链**（位图族存在的主要理由）：`DefaultSolver.java:354` addAllDiff → DelegatePointsToSet → HybridBitSet.addAllDiff（HybridBitSet.java:112：双大集合走位级差量，否则逐元素）→ RegularBitSet.orDiff/SparseBitSet.orDiff。diff 非空才入队传播，是 solver 不做冗余功的关键。

**可独立复用**：Pair/Triple/Streams/SetQueue/UnionFindSet/SparseIntSet（依赖同包 IntList）/TooManyElementsException/Views 纯 JDK 依赖，可整文件拷走；Maps/Sets/MultiMapCollector 依赖同包 Hybrid 系与 ArrayMap/ArraySet；MapEntry 额外依赖 `pascal.taie.util.Hashes`。MultiMap/TwoKeyMap 族可整族搬，只需 SerializableSupplier/TriConsumer/TriFunction 三个小接口。

**消费方速查**：位图族 → IndexerBitSet/HybridBitSet 与 DefaultSolver 差量链；TwoKeyMap 族 → ClassHierarchyImpl、MapBasedCSManager、NodeManager 等；UnionFindSet → Mahjong.java:63；SparseIntSet → Dominators；SetQueue → InterSolver.java:79。改实现先跑 `src/test/java/pascal/taie/util/collection/` 对拍测试。
