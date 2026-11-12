# 07 · 数据流求解器：WorkListSolver 与 InterSolver

<!-- source: knowledge-graph tour step 7 | files: src/main/java/pascal/taie/analysis/dataflow/solver/WorkListSolver.java, src/main/java/pascal/taie/analysis/dataflow/inter/InterSolver.java -->

### 角色定位

L7 层「程序图与数据流分析」里，CFGBuilder/ICFG 只负责把 IR 组织成图；让 fact 在图上流动到不动点的引擎是两个求解器：`WorkListSolver`（src/main/java/pascal/taie/analysis/dataflow/solver/WorkListSolver.java:38）管过程内，`InterSolver`（src/main/java/pascal/taie/analysis/dataflow/inter/InterSolver.java:38，在 inter/ 下）管过程间。

这是全仓框架与 client 分离最纯粹的典范：求解器对 fact 内容一无所知，只经 `DataflowAnalysis` 接口驱动一切（src/main/java/pascal/taie/analysis/dataflow/analysis/DataflowAnalysis.java:34）——学生作业只实现 analysis、复用求解器。装配链极短：AnalysisDriver 取 CFG→makeAnalysis→`getSolver().solve`（AnalysisDriver.java:44-48）。WorkListSolver 包私有，外界只能经静态单例 SOLVER 取用（Solver.java:40）。

### 内部结构

**过程内五元组**（DataflowAnalysis.java:39-65）：`isForward` / `newBoundaryFact` / `newInitialFact` / `meetInto` / `transferNode`——后两者就地改 target/out，后者返回是否变化；边传输对 needTransferEdge/transferEdge 基类默认关闭（AbstractDataflowAnalysis.java:42-48）。

前向主循环（WorkListSolver.java:92-124）：worklist 是按 `cfg.getIndex` 升序的 NavigableSet（:85-86），而 StmtCFG 的 index 就是 IR 语句序加一（src/main/java/pascal/taie/analysis/graph/cfg/StmtCFG.java:51-59），poll 序天然近似拓扑序、直线代码一遍收敛。每次 poll：入度>1 时把各入边源的 out（按需过 transferEdge）逐个 meetInto 现有 in（:97-105）；入度=1 需边传输则覆盖式算新 in（:108-111），否则读已别名的 in；transferNode 后 changed 才把后继压回（:120-122）。后向完全镜像，序取负 index（:172-173）。

**过程间**：InterDataflowAnalysis 砍掉 getCFG/needTransferEdge，transferEdge 对每条 ICFG 边无条件执行（InterDataflowAnalysis.java:73）。InterSolver 给全部 entry 方法入口节点 boundary fact、其余节点 fresh initial fact（InterSolver.java:61-76），主循环对每个节点先无差别 meet 全部入边（:85-88）再 transferNode（:90）。两个后门：`propagate` 让 analysis 主动把节点塞回 worklist（:97-99），`getOutFact` 读求解中途状态（:101-103）。

### 外部连接

上游消费两张图：过程内 `ir.getResult(CFGBuilder.ID)`（AnalysisDriver.java:45），过程间 `World.get().getResult(ICFGBuilder.ID)`（AbstractInterDataflowAnalysis.java:122）。下游走 IR 结果缓存通道：NullPointerDetection 取 IsNullAnalysis 结果（src/main/java/pascal/taie/analysis/bugfinder/nullpointer/NullPointerDetection.java:52），而 IsNullAnalysis 本身是 AnalysisDriver 子类（IsNullAnalysis.java:56）——bugfinder 族既消费数据流结果、也跑在同一求解器上。DeadCodeDetection 消费 const-prop（DeadCodeDetection.java:73），依赖在配置表声明（src/main/resources/tai-e-analyses.yml:138）。

### 数据流

对 `x=1; if(c) x=2; use(x)`：CFG 为 entry→s0(x=1)→s1(if c)→[IF_TRUE]→s2(x=2)→s3(use x)→exit，s1 另有 IF_FALSE 边直达 s3。初始化（WorkListSolver.java:41-68）：entry 拿 boundary fact——常量传播给 int 参数赋 NAC（ConstantPropagation.java:84）；s0/s1/s2 均单前驱且无需边传输，in 直接**别名**前驱的 out 对象（:55-61）；只有双前驱的 s3 拿 fresh newInitialFact——对 CP 是空 CPFact 即全 UNDEF/top（「缺席即 UNDEF」稀疏实现，CPFact.java:45-49）。

主循环：s0 的 transferNode 复制 in 中除 x 外的变量、x 求值为 c1 写进 out（ConstantPropagation.java:118-135）；s1 非定义语句走 `out.copyFrom(in)`（:134），out={c:NAC, x:c1}；s2 传输后 out={c:NAC, x:c2}；s3 双前驱，先 meet s1 的 out 得 `meetValue(c1, UNDEF)=c1`（:103-115），再 meet s2 的 out，两常数不等→NAC（:110-113）。终态 s3.in={c:NAC, x:NAC}：两路径给出不同常数，must-analysis 精度塌缩到格底，use(x) 处 x 非常数。全程零拷贝，唯一契约是 transferEdge 不得改入参（DataflowAnalysis.java:74-75）。

### 设计决策

**meet 半格抽象而不声明 lattice**：Tai-e 没有 Lattice 接口——求解器只要求 meetInto 单调收敛、transferNode 能报 changed，格结构隐含在 client 里：meetValue 求最大下界 :103-115、joinValue 求最小上界 :187-199，方向相反并存。多前驱节点的 in 从不清零、只增量 meet（WorkListSolver.java:97-105），正确性押在单调性上。

**fact 别名共享**：单前驱节点的 in 与前驱 out 是同一对象，前驱 transferNode 直接驱动后继 in，省一次 meet 加拷贝（:55-61）；代价是 client 不能假设 in/out 私有。InterSolver 放弃此优化——ICFG 节点前驱普遍多个（call 边加 call-to-return 边），收益太小。

**过程间边分四类**（Normal/Call/CallToReturn/Return，ICFGEdge.java:36），由 AbstractInterDataflowAnalysis 按具体类型分派（AbstractInterDataflowAnalysis.java:98-108）。以 InterConstantPropagation 为例：call-to-return 边 kill invoke 的 LHS（InterConstantPropagation.java:314-325），防局部变量携旧值飞越被调方法；call 边传实参→形参（:328-350，跳过 InvokeDynamic 等 :333-335）；return 边把多个返回值 meet 成一个写 LHS（:358-361）。这是 IFDS/IDE 的 super graph 形态——整个 ICFG 一张图跑 worklist、不做调用栈上下文区分。alias-aware 模式演示 propagate 后门：StoreField 传输发现字段值流向别名 load 点，直接 `solver.propagate(load)` 拉远端节点回 worklist（:293-295），并经 `solver.getOutFact` 读求解中途状态（:252-253）。另一处不对称：isForward 在接口里存在（InterDataflowAnalysis.java:38）但 InterSolver 只实现前向。

### 新人提示

新分析最小五步：① 选 fact 表示与方向——集合型用 `SetFact`（union 即 meet，src/main/java/pascal/taie/analysis/dataflow/fact/SetFact.java:108-110），映射型参考 CPFact；② 继承 AnalysisDriver，makeAnalysis 返回内部 Analysis（模板 ReachingDefinition.java:44-47）；③ 实现五元组，需边精化才覆写 needTransferEdge/transferEdge；④ 在 tai-e-analyses.yml 注册 id/analysisClass/requires（const-prop 条目在 :114）；⑤ `-a <id>` 运行即可。

三个易错点：**meet 单位元**——may-analysis（RD/LV）的 newInitialFact 必须是空集 ⊥、meet 是 union（ReachingDefinition.java:97-99）；must-analysis（CP）必须是全 UNDEF 的 ⊤、meet 向格底走，写反会把 sound 变 unsound。**boundary 语义**——CP 给参数 NAC 而非 UNDEF（ConstantPropagation.java:84），「必有值但未知」≠「未赋值」。**kill/gen 顺序**——RD 先 `out.set(in)` 再 kill 再 gen（:102-114），检测 changed 须先拷旧 out（:103）。

最后钉一个常见误解：**pta 不是数据流框架的 client**。pta/core/solver 零 import dataflow（grep 实证），自有基于指针图的 worklist。依赖方向相反——inter-const-prop 的 alias-aware 消费 PointerAnalysisResult（InterConstantPropagation.java:132），配置 `inter-const-prop requires: [icfg, pta(alias-aware=true)]`（tai-e-analyses.yml:130）。pta 是数据流的上游精度供应商而非下游。
