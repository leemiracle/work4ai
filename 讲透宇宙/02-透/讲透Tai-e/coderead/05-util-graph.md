<!-- coderead unit 05 | files: 15 个 | 全量深读 2026-10-13 -->

# 第 5 单元：util/graph 图算法族——Tai-e 的 L1 图基础设施

## 1. 包职责与架构位置

`pascal.taie.util.graph` 是与 IR/分析语义完全解耦的**纯图算法库**：节点类型以泛型 `N` 透传，15 个类分四层——

- **抽象层**：`Graph`/`Edge`/`IndexedGraph` 定义全仓唯一的图 SPI。上层图全部落在这套 SPI 上：`CFG extends IndexedGraph`（CFG.java:36）、`CallGraph extends Graph`（CallGraph.java:38）、`ICFG extends Graph`（ICFG.java:33）、`PointerFlowGraph implements Graph`（PointerFlowGraph.java:39）。
- **实现/视图层**：`SimpleGraph`（可变邻接表）、`ReverseGraph`（反向活视图）、`MergedSCCGraph`+`MergedNode`（SCC 凝聚图）。
- **算法层**：`SCC`（Tarjan）、`Dominators`（CHK 支配树+支配边界）、`TopologicalSorter`（DFS 拓扑序）、`Reachability`（双向可达性）。
- **可视化层**：`DotDumper`+`DotAttributes`，被 CFGDumper.java:49、CallGraphs.java:102、TFGDumper.java:48 等五处消费。

典型消费链：IR 构建期建 `Dominators`（BytecodeIRBuilder.java:61），SSA 变换用其支配边界插 phi（SSATransform.java:238）；`TopologicalSolver` 用 `MergedSCCGraph`+`TopologicalSorter` 做调用图凝聚+逆拓扑传播（TopologicalSolver.java:81/188）；`AnalysisPlanner` 用 `SimpleGraph`+`SCC`+`TopologicalSorter` 排分析依赖（AnalysisPlanner.java:257）。设计取向**接口极简**：`Graph` 仅 3 个抽象方法，其余 default 兜底。

## 2. 逐类深读

#### Graph Graph.java:37

有向图 SPI，`extends Iterable<N>, Serializable`。抽象方法仅 `getPredsOf`（Graph.java:64）、`getSuccsOf`（Graph.java:69）、`getNodes`（Graph.java:104）三个。default 方法族构成兜底语义：`hasNode`/`hasEdge` 委托点集/邻接集 contains（Graph.java:50）——**O(出度) 而非 O(1)**，热路径子类应覆盖；`nodeCount`（Graph.java:109）与已废弃的 `getNumberOfNodes`（Graph.java:117）并存，是接口演进迁移样板。最关键的是 `getInEdgesOf`/`getOutEdgesOf`（Graph.java:74/89）：用 `Views.toMappedSet` 把邻接点集**即时映射**为无存储的 `SimpleEdge` 视图，每次遍历重新构造边对象——上层图要暴露富边类型（携带 kind/异常集）必须协变覆盖，先例即 CFG 返回 `Set<CFGEdge<N>>`（CFG.java:67/73）。`iterator`（Graph.java:123）复用 `getNodes().iterator()`。

#### Edge Edge.java:32

极小边 SPI：`source()`（Edge.java:37）与 `target()`（Edge.java:42），外加 `Serializable`。不带权重、不带 kind——富边语义由子接口（CFGEdge/ICFGEdge/PointerFlowEdge）自行扩展。`Graph.hasEdge(Edge)`（Graph.java:57）解包回点对比较，边对象身份从不参与图结构判定。

#### AbstractEdge AbstractEdge.java:27

边实现公共基类，`source`/`target` 为 `protected final`（AbstractEdge.java:32/37）。**equals 采用严格 `getClass()` 比较**（AbstractEdge.java:59）——不同边子类即使端点相同也不相等；`hashCode` 用 `Hashes.hash(source, target)`（AbstractEdge.java:67）。子类若增加字段（如边的 kind）必须重写 equals/hashCode，否则"同端点不同 kind"的两条边会被判等。

#### SimpleEdge SimpleEdge.java:25

一行 record 实现（SimpleEdge.java:25）。record 生成的 equals 同样**类型严格**，故 Graph.java:75 边视图产出的 `SimpleEdge` 与真实边对象（如 CFGEdge）**永不相等**。集成时比较边一律用 `source()/target()` 点对。

#### SimpleGraph SimpleGraph.java:37

唯一可变图实现，三容器：`nodes` Set、`preds`/`succs` 双向 MultiMap（SimpleGraph.java:39-43）。`addEdge` 自动补齐两端节点（SimpleGraph.java:68-73）；`getNodes` 返回不可变视图；`getInDegreeOf` 覆盖为直查 preds 尺寸以绕开边视图构造（SimpleGraph.java:104）。**易错点：`removeNode`（SimpleGraph.java:79-83）存在悬挂边缺陷**——只清以该节点为 key 的两张邻接表，其他节点邻接集中**以该节点为 value 的残留不清理**：删 Y 后 `succs.get(X)` 仍含 Y，`hasEdge(X,Y)` 为 true 而 `hasNode(Y)` 为 false，与 Javadoc 声明（SimpleGraph.java:76）不符。主仓目前只有 `removeEdge` 被调用（AnalysisManager.java:232），未踩雷；二次开发做图收缩必须先修此处。

#### IndexedGraph IndexedGraph.java:32

`extends Graph<N>, Indexer<N>` 的交叉接口，追加 `getEntry()`（IndexedGraph.java:37）。语义是"带入口、可编号"的图——`Dominators` 靠编号把节点运算降为 `int[]` 数组运算、靠入口定义支配关系；`Indexer` 不变量为 `e.equals(getObject(getIndex(e)))`。仓内唯一实现是 `BytecodeCFG implements IndexedGraph<BytecodeBlock>`（BytecodeCFG.java:53）。

#### ReverseGraph ReverseGraph.java:32

反向**活视图**：不拷贝数据，只持原图引用。`hasEdge` 翻转实参（ReverseGraph.java:41），`getPredsOf`/`getSuccsOf` 互换（ReverseGraph.java:46-52），`getNodes` 直通，原图后续变更实时可见。它不覆盖边访问器，经 default 拿到的是反转语义下的 SimpleEdge 视图；DotDumper 的 `getEdgeRep` 用 `source()->target()` 拼接（DotDumper.java:163），在反转图上自然输出反向箭头。

#### Reachability Reachability.java:40

双向可达性查询+缓存，两张惰性 MultiMap（Reachability.java:47/52）。`reachableNodesFrom`（Reachability.java:61）迭代 DFS，`visited.add` 成功才扩展后继。**返回集包含 source 自身**（首帧即压入起点）。`nodesCanReach`（Reachability.java:83）对称地沿 `getPredsOf` 反向遍历。**不变量：缓存永不失效**——对象生命周期内底层图不可再变更；`TFGBuilder` 用它过滤污点流图源汇连通性（TFGBuilder.java:241）。

#### SCC SCC.java:43

Tarjan 强连通分量，**显式栈迭代版**（注释明言防大图栈溢出，SCC.java:70-71）。结果存 `componentList`/`trueComponentList`。核心循环用 `WorkEntry`（node+succs 的 ListIterator 快照，SCC.java:150）模拟递归：未访问后继先 `succIter.previous()` 回退再压栈；已访问后继按 index 分类——前向边合并 low（SCC.java:102-104），在栈中则回边取 index 下界（SCC.java:105-107）。`collectSCC`（SCC.java:119）弹栈至根后 **reverse**（SCC.java:129），使"与外部前驱相连的节点排在分量前部"——该顺序是下游栈 phi 解析正确性的前提。`getTrueComponents`（SCC.java:65）只返回真 SCC：size>1 或单节点自环（SCC.java:131-138）。`validate`（SCC.java:145）用 assert 核对，**仅 -ea 生效**。复杂度 O(V+E)。

#### MergedNode MergedNode.java:37

凝聚图节点：`nodes` 为 `List.copyOf`（MergedNode.java:49，构造断言非空），`preds`/`succs` 用 hybrid set（MergedNode.java:41-43），hashCode 构造期缓存（MergedNode.java:45），equals 先比缓存 hash 再比 nodes（MergedNode.java:82-83）。**包内可变、包外只读**：`addPred/addSucc`（MergedNode.java:53/61）包私有，外部无法手工改凝聚图结构。

#### MergedSCCGraph MergedSCCGraph.java:38

SCC 凝聚图（condensation），`implements Graph<MergedNode<N>>`。构造期 `init`（MergedSCCGraph.java:46）全量完成：跑 `SCC`（MergedSCCGraph.java:50），每分量包装成 MergedNode 并建原节点→凝聚节点映射（MergedSCCGraph.java:51）；再二次遍历所有后继建跨分量边，滤自环（MergedSCCGraph.java:56-64）。**产物必为 DAG**——任何循环依赖问题经它转化为拓扑可解问题。访问器全包 unmodifiable。消费范式见 TopologicalSolver.java:81-188 与 ObjectAllocationGraph.java:81。

#### TopologicalSorter TopologicalSorter.java:40

DFS 拓扑排序，**前提 DAG**（Javadoc TopologicalSorter.java:36；有环不死循环但结果无拓扑意义）。三个公开构造器收敛到私有主构造器（TopologicalSorter.java:67-78）：先按 `preservedOrder` 逐个 visit（TopologicalSorter.java:69，与拓扑冲突时拓扑优先）；再以**出度为 0 的汇点**作种子（TopologicalSorter.java:70-73）——沿 preds 回溯的 DFS 中节点在所有前驱之后 append（TopologicalSorter.java:113），故 `sortedList` 天然"前驱在前"；`reverse=true` 整体反转得"后继在前"（TopologicalSorter.java:74），TopologicalSolver 逆拓扑传播用的正是该方向（TopologicalSolver.java:188）。`visit`（TopologicalSorter.java:93）同样迭代式防栈溢出，peek 即标记 visited（TopologicalSorter.java:103）。

#### Dominators Dominators.java:44

全包最重的算法类，实现 Cooper-Harvey-Kennedy《A Simple, Fast Dominance Algorithm》(2001)（Dominators.java:39）。前置条件 `IndexedGraph`+入口（Dominators.java:55）。构造器四连算（Dominators.java:124-138）：①`computePostOrder`（Dominators.java:140）递归 DFS 生成后序，`postOrder[i]` 存节点索引、`postIndex` 为逆映射，**不可达节点被截断丢弃**（Dominators.java:147-149），后续序列只覆盖可达子图；②`computeIDom`（Dominators.java:170）不动点迭代：入口 idom 自指（Dominators.java:173），按逆后序反复 `processNode`——取已处理前驱的 `intersect`（Dominators.java:205），无前驱或已收敛到入口的节点跳过（Dominators.java:192）；`intersect`（Dominators.java:214-228）双指针沿 idom 链上爬、`postIndex` 比较决定谁爬；③`computeDomTreeClock`（Dominators.java:230）从 iDom 反建支配树并递归打 in/out 时间戳（Dominators.java:241）——`dominates` 由此退化为 O(1) 区间判定（Dominators.java:285-289）；④`getDomFrontier`（Dominators.java:360）Cytron 支配边界算法，惰性且缓存：对每个**前驱数≥2 或即入口**的节点（入口特判因无伪入口，Dominators.java:376），沿每个前驱的 idom 链上爬至 `iDom[node]` 逐个登记 DF（Dominators.java:380）；`runner>=0` 守卫不可达前驱的 UNDEFINED=-1（Dominators.java:382）。工程细节：`dfsGraph` 是**递归**实现（Dominators.java:152），与全包迭代风格不一致，靠 IR 级 CFG 规模有限兜底；后继**逆序**遍历以逼近字节码顺序、利于行号传播。`getIDom` 包私有仅供测试（Dominators.java:347）。

#### DotAttributes DotAttributes.java:36

不可变 dot 属性集。内部 `MultiMap<String,String>` 支持同名多值（DotAttributes.java:43），`attrsString` 构造期预渲染（DotAttributes.java:48）。渲染规则：单值 `name=value`，多值 `name="v1,v2"`（DotAttributes.java:58）。三个组合子全部**返回新实例**：`update` 输入覆盖旧值（DotAttributes.java:76）、`add` 追加可产生多值（DotAttributes.java:95）、`of` 工厂空参数复用单例 EMPTY（DotAttributes.java:110）；参数奇偶校验（DotAttributes.java:77）兼顾隐式 null 检查。无 setter——定制全走"复制+改"。

#### DotDumper DotDumper.java:40

可配置 dot 导出器，fluent 风格。7 个链式 setter（DotDumper.java:86-120）：`nodeToString`（节点 ID 渲染）、`nodeLabeler`/`edgeLabeler`（标签，返 null 即无）、`nodeAttributer`/`edgeAttributer`（属性）、两组全局属性。`dump`（DotDumper.java:122-142）骨架固定：`digraph G {` → 全局属性行 → 逐节点（走 `Graph.iterator`，DotDumper.java:132）→ 逐边（走 `getOutEdgesOf`，DotDumper.java:134）→ `dumpOthers` 钩子 → `}`。节点 ID 强制加引号，边渲染 `src -> tgt`（DotDumper.java:163），标签与属性合并进 `[...]`（`dumpElement`，DotDumper.java:176）。**扩展点两级**：setter 链零侵入（CFGDumper.java:49-75 完整范例：SimpleIndexer 编号+labeler 输出边 kind+exceptional 边标红）；要输出图外信息则子类覆写 `dumpOthers`（DotDumper.java:148），先例 TFGDumper（TFGDumper.java:48）。边对象来自 `getOutEdgesOf`，消费方 labeler 可安全 cast 富边类型——前提是该图覆盖了边访问器；SimpleGraph 传来的就是 SimpleEdge。

## 3. 修改热点（二次开发）

**加新图算法的接入惯例**。三条不成文规矩：①算法类不写静态工具方法，而是"构造器即计算+结果驻留"（SCC.java:48）或"惰性查询+缓存"（Reachability.java:61）二选一；②**必须迭代式实现**——SCC.java:70 与 TopologicalSorter.java:94 均留有"avoid stack overflow for large graph"注释，指针流图/调用图可达百万节点（Dominators 的递归 dfsGraph 是历史例外）；③算法只依赖 `getPredsOf/getSuccsOf/getNodes` 三抽象方法、不碰边对象，保证对任何 Graph 实现可用。照此写成 `new XxxAlgo<>(graph)` 即可无缝接入 ICFG/PointerFlowGraph/CallGraph。

**Graph 接口加方法的影响面**。全仓 31 个文件 import 本包。加方法**必须给 default 实现**且默认实现只准依赖既有三个抽象方法——`hasEdge(Edge)`（Graph.java:57）与 `nodeCount`（Graph.java:109）是零破坏先例；性能要紧处允许实现类覆盖（SimpleGraph.java:104）。废弃方法迁移样板是 `getNumberOfNodes`→`nodeCount`（Graph.java:117）：`@Deprecated`+default 转发+Javadoc 指向新名。

**DotDumper 扩展输出格式**。三档成本递增：lambda setter 链（零侵入）；子类覆写 `dumpOthers`（DotDumper.java:148）在 `}` 前注入任意行（TFGDumper 先例）；改输出方言（如 JSON）则复制 `dump` 主体改造（仅 20 行）。注意 `dump` 对 FileNotFoundException 只 warn 不抛（DotDumper.java:139），调用方无法感知导出失败。

**两处已知债务**：`SimpleGraph.removeNode` 悬挂边缺陷（SimpleGraph.java:79-83，修法：remove 前先遍历对端邻接集反向清理）；`Dominators.getDomFrontier` 的 SparseIntSet 分配性能 TODO（Dominators.java:361），指针分析加速可从此入手。

## 4. 集成触点

**外部项目复用 Graph/Edge 抽象**成本极低：`Graph`/`Edge`/`AbstractEdge`/`SimpleEdge`/`ReverseGraph`/`TopologicalSorter`/`SCC` 仅依赖 `pascal.taie.util.collection` 与 `Hashes` 等小工具，无 IR、无分析依赖，整包可平移。接入三步范式：①让自己的节点集合实现 `Graph<N>`（最少 3 个方法）；②算法即插即用（`new SCC<>(g)`、`new TopologicalSorter<>(g, true)`）；③`new DotDumper<N>().setNodeLabeler(...).dump(g, file)` 出图。仓内模板：TopologicalSolver.java:81+188（`MergedSCCGraph`+`TopologicalSorter` 组合处理循环调用）。

**两个集成陷阱**钉死：其一，`Graph`/`Edge` 都 `extends Serializable`（Graph.java:37/Edge.java:32），实现类的节点与字段必须可序列化，否则远程/缓存场景炸雷；其二，边对象身份不可依赖——default `getOutEdgesOf` 给的是一次性 SimpleEdge 视图（Graph.java:89），与图自有边类永不相等，比较边一律走 `source()/target()`，或协变覆盖边访问器（CFG.java:73 式）后用真实边类型。

**Dominators 复用**要求实现 `IndexedGraph`（多出 `getIndex/getObject/getEntry`），换来 int 数组级性能与 O(1) `dominates`；调用图无唯一入口时需先造伪入口。**DotDumper 是全仓统一可视化出口**：CFG/调用图/ICFG/数据流图/污点流图全部经它产 `.dot`；给新分析加调试视图时，复制 CFGDumper.java:49-75 的 setter 模板是最短路径。
