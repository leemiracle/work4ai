# 03 · aggregation 聚合 AMG：selectors 与 coarseAgenerators 的 host/device 三层同构

## 角色定位

聚合 AMG 是 GPU 上最常用路线（图谱 L03，33 节点）：不区分 C/F，把邻近自由度聚成 aggregate，延拓隐式为分段常数（每聚合一个粗自由度），粗矩阵由 Galerkin 积生成。`Aggregation_AMG_Level_Base`（include/aggregation/aggregation_amg_level.h:35）组织两个可插拔组件：聚合 selector（怎么分组）与 coarseAgenerator（怎么算 R·A·P）。AMGX 是无平滑 plain aggregation——WARNING 明言 P 隐式、经 aggregates 数组使用（src/aggregation/aggregation_amg_level.cu:1965-1968）。

## 内部结构

骨架 src/aggregation/aggregation_amg_level.cu（2654 行，聚合线最大单元）；构造在头文件双工厂分配（aggregation_amg_level.h:67-68）。`createCoarseVertices`（:1945-1956）只做 m_selector->setAggregates（:1948）产出 m_aggregates 与聚合数（:1955）。`createCoarseMatrices`（:1960-2023）主装配：分布式先 setNeighborAggregates（:1983）或合并簿记 consolidationBookKeeping（:1979）→computeRestrictionOperator（:1994，按聚合计数直出 R 行偏移，host 版 fillRowOffsetsAndColIndices :323-359）→m_coarseAGenerator->computeAOperator（:1999）→prepareNextLevelMatrix 三变体分发（:1540-1552：full/diag/none）→m_next_level_size（:2016）。solve 期专用 kernel：restrictResidualKernel（:93）/prolongateAndApplyCorrectionKernel（:158），粗校正带 computeAlpha 缩放（:600）。selector 侧 10 文件三层同构（Base+host/device 特化）：size2 的 findStrongestNeighbour kernel 族（size2_selector.cu:74-303）+权重公式参数（:626，core.cu:468）；size8 两轮四点复合（1543 行）；multi_pairwise 多趟匹配-收缩（1818 行，passes 默认 3，core.cu:469）。

## 外部连接

上游同 classical：AMG_Setup 调 createCoarseVertices/createCoarseMatrices；AMG_LevelFactory 注册名 AGGREGATION（src/core.cu:628）。注册表：selector SIZE_2/SIZE_4/SIZE_8/MULTI_PAIRWISE/DUMMY/GEO/PARALLEL_GREEDY_SELECTOR（core.cu:638-644，后三个 not exposed）；coarseAgenerator LOW_DEG/HYBRID/THRUST（:655-657，默认 LOW_DEG）。R 结构被 generator 复用（:1999）。预设 AGGREGATION_* 11 份全走此路径。

## 数据流

setup：A→setAggregates 出 aggregates[]（每点所属聚合号）+分布式重编号（coarse_to_global :927）→R 的 CSR 结构（聚合为行、成员为列）→computeAOperator 以 R 为骨架稀疏积出 Ac。solve：限制一趟 scatter（r 累加进 rr[聚合号]，:93-107）；延拓一趟 gather（e[聚合号] 乘 alpha 加回 x，:158-167），块矩阵走 BlockDiaCsr 变体分派（:483-513）。与 classical 的显式 P·e 相比零索引开销——GPU 上快的原因。

## 设计决策

coarseAgenerator 是"同一算法三实现"：THRUST 纯原语（sort_by_row_and_column :98+reduce_by_key :126，正确性基准）、LOW_DEG 专用 kernel（一行/一聚合级并行）、HYBRID 混合（nnz 计数走 Thrust、数值填充走 custom kernel，hybrid_coarse_A_generator.cu:303，仅支持带 DIAG 且非零矩阵 :307-314）。R 与 selector 分离是历史优化，TODO（:1990）承认可合并。size2 的 host 路径 FatalError"not implemented on CPU"（size2_selector.cu:631-634）——聚合 selector 普遍 device-only。勘误：SerialCoarseAGeneratorFactory 头文件定义齐整（serial_coarse_A_generator.h:71）但注册表无 SERIAL 名（core.cu:655-657）——运行时选不到的死代码，图谱层摘要里的 serial 只存在于头文件。

## 新人提示

新问题先 SIZE_2（等参结构网格）或 MULTI_PAIRWISE（一般矩阵）；coarseAgenerator 默认 LOW_DEG，粗层巨大时看 print_grid_stats 再试 HYBRID。prepareNextLevelMatrix 三变体由矩阵属性驱动（diag 判定 :1548）。调试聚合质量用 print_aggregation_info（:1950-1953）与 aggregatesQuality2（:2020-2022）。块尺寸 6/7 等未注册值在 restrictResidual_4x4 分派链 FatalError（:513）——加新块尺寸要同时改 kernel 模板与分发。consolidation 只在多 GPU 细层过小时触发，先抓 destination_partitions→root→consolidateCoarseGridMatrix（:2006）。
