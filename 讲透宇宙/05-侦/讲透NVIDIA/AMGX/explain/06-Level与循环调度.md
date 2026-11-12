# 06 · AMG_Level 与循环调度：FixedCycle 的 Dispatcher 策略化基座

## 角色定位

本篇讲运行期两条脊梁（图谱 L06，16 节点）：AMG_Level（include/amg_level.h+src/amg_level.cu）是三系层级公共骨架，持有矩阵、smoother、粗层向量与 next level 指针；cycles 目录的 FixedCycle 是 V/W/F/CG/CGF 五循环共用执行框架。批甄别的核心论断在此落地：FixedCycle 以 Dispatcher 模板参数注入 host/device 分发，是策略化基类设计（include/cycles/fixed_cycle.h:10 模板模板参数签名）。AMG_Solve 经 CycleFactory::generate（src/amg.cu:1110）在此展开递归下降-上升。

## 内部结构

AMG_Level 侧：构造即买 smoother（amg_level.cu:33）；`setup`（:64-87）只做 latency-hiding 的 interior/exterior 视图配置；`setup_smoother`（:90-129）支持 ThreadManager 异步队列（:124）；`transfer_from`（:37-61）是跨内存空间的"almost deep copy"（A.copy+向量+标志位，next 指针清零）。跨空间递归机关是 `AMG_GenerateNextCycles` 三特化（amg_level.h:218-316）：同空间直接 dispatcher.dispatch（:240）；host→device/device→host 临时拷贝 b/x、递归完拷回（:264-279/:300-315）；内联入口带默认 dispatcher 实参（amg_level.h:117）。AMG_LevelFactory 按 AlgorithmType 枚举注册（amg_level.cu:156-158）。Cycle 侧：Cycle_Base 定义 isASolvable/solveExactly 纯虚骨架（include/cycles/cycle.h:21-38），Cycle 的 host/device 特化只差异 solveExactly_1x1/4x4（:40-74）；FixedCycle::cycle（src/cycles/fixed_cycle.cu:25-248）是五循环共有循环体。

## 外部连接

上游：AMG_Setup 建层（amg.cu:91-92）；CycleFactory 注册 V/F/W/CG/CGF（core.cu:631-635），参数 cycle 默认 V。V/W/F/CG 的 X_Cycle 类是"构造即执行"薄壳（w_cycle.h:47-51 `this->cycle(...)`）。Dispatcher 实现各在 .cu：W=两次递归（w_cycle.cu:11-24）、F=W+V（f_cycle.cu:13-27）、V 单次（v_cycle.cu:11-22）、CG 用 DispatchAuxCG 做共轭梯度加速粗层校正（cg_cycle.cu:96-104）。下游消费 smoother、各系 restrictResidual/prolongateAndApplyCorrection、launchCoarseSolver（amg_level.cu:133-146）。显式实例化把 5 dispatcher×全精度铺开（fixed_cycle.cu:254-277）。

## 数据流

FixedCycle::cycle 单层时间线：isASolvable 小矩阵直接 solveExactly 返回（:54-58）→预平滑（presweeps 次 smoother->solve，tolerance 置 0 按次数迭代 :99-101；粗层且有 coarse solver 时 presweeps=0 :75-78；finest 层可被 finest_sweeps 覆盖 :83-86）→残差 axmb（:129）→restrictResidual（:149）→递归：下一层是最粗层则强制 V 型（:170-175），否则 CycleDispatcher 原样传下（:179）——W 的"两次递归"语义由 dispatch 里的两次构造传递→prolongateAndApplyCorrection（:189）→后平滑（:192-223，error_scaling>3 关后平滑 :212-215）。consolidation 向量递归前后 consolidate/unconsolidate（:154-158/:183-186）。smoothing_direction 挂矩阵参数供 GS 类辨前后向（:42-50/:70/:192）。

## 设计决策

Dispatcher 用模板模板参数而非虚函数表，host/device 双版本编译期静态分派（每个 X_CycleDispatcher 内含两个 dispatch 重载，w_cycle.h:19-27），递归链零虚调用——代价是实例化组合爆炸，靠 AMGX_FORALL_BUILDS 宏统一铺。F 循环实现成"W 后接 V"而非教科书标准 F 递归，是 GPU 简化近似。isNextCoarsest 强制 V 型收尾（:170-175）省掉最粗层 dispatch 开销。W 循环深层级复杂度 2^levels，粗层 DENSE_LU 直接解是必要护栏。cycle 是每 solver scope 的参数，PCG 预条件嵌 V/W（PCG_W.json）即 Krylov×MG 经典组合。

## 新人提示

先在脑内跑一遍两层 V 型例：presweep→restrict→generateNextCycles(dispatch)→最粗层 solveExactly/launchCoarseSolver→prolong→postsweep。改循环行为别动 FixedCycle（五循环共享），改各 Dispatcher 的 dispatch。finest_sweeps=-1 是"未启用"（:83 判 !=-1），0 与 -1 语义不同（0=真零次，-1=回退 presweeps）。presweeps=0 且 init cycle 时显式 fill 零（:103-106），否则 x 是垃圾。consolidation 的 root/非 root 分支（:161/:231）易踩——非 root 跳过递归但必须参与 unconsolidate 通信。调试用 Profile.tic/toc 区段与 convergence_analysis.cu 三段拆解。
