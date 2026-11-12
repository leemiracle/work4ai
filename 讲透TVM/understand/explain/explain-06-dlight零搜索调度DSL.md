# explain-06 · dlight 零搜索调度 DSL：python/tvm/s_tir/dlight/

## 角色定位

dlight 是 TVM 的**轻量规则式调度器**——包 docstring 一句话定调："DLight package provides efficient schedules out-of-box"（`dlight/__init__.py` L18）。与 meta_schedule 的海量搜索（explain-07）相对，dlight 用**专家规则 + 静态分析**在零测量开销下直接生成调度：识别出 GEMV 就套 GEMV 模板、识别出 reduction 就套 reduction 模板。这对 fork 尤其重要——LLM 推理的 decode 阶段以 GEMV/batch 小的 matmul 为主，dlight 的 gemv 规则正是为 LLM 工作负载设计的第一等公民。三条产品线：`gpu/`（gemv/matmul/reduction/rmsnorm/general_reduction/transpose/fallback）、`cpu/`、`adreno/`（手机 GPU），共用 `base/` 的规则协议与 `analysis/` 的结构识别。

## 内部结构

**规则协议**（`base/schedule_rule.py`）：全部协议浓缩在一个类里。`ScheduleRule.apply(func, target, tunable)`（L36-59）返回三态——`None` 表示"此规则不适用，请试下一条"，单个 `Schedule`，或调度列表；docstring L28-33 规定 `tunable=True` 时允许返回含可调指令的调度（留给下游测量挑），`tunable=False` 则必须直接给出确定调度。`from_callable` 装饰器（L61-106）让一行函数升格为规则类；`is_target_available`（L108-121）默认恒真，被 `gpu/base.py` 的 `GPUScheduleRule` 覆盖为 `'"gpu" in target.keys'`（gpu/base.py L24-31）——**规则的目标过滤靠子类化而非配置**。

**结构识别层**（`analysis/common_analysis.py`）：`normalize_prim_func(sch)`（L289 起）把 PrimFunc 归一化成一串 `SBlockInfo`（每个 block 的空间/归约迭代、读写分析）；`SBlockInfo.is_gemv()`（L271）、`is_broadcast_epilogue`（L444）、`get_max_shared_memory_per_block`（L376）提供判定原语。`analysis/gemv.py` 的 `is_gemv`（L62）返回参与 GEMV 的向量输入 buffer 列表或 None。

**旗舰规则 GEMV**（`gpu/gemv.py`，691 行，本包最重文件）：`apply`（L40-86）是标准漏斗——L46-47 非 PrimFunc 或目标不可用即 None；L49-50 归一化 + 内联连续空间块；L53-60 只接受"1 个主 block（可选 1 个 injective epilogue）"的形态；L63-66 循环数必须是 2 或 3（`[B,S,R]=[B,S,R]*[B,R]` 或 `[S,R]=[S,R]*[R]` 两种 LLM 常见形态注释在 L64-65）；L68-70 `is_gemv` 判定不过即退出。然后分两路（L76-86）：内层归约走 `sch_inner_reduction`，外层归约走 `sch_outer_reduction`，后者失败再降级 `sch_outer_reduction_fallback`（L83-85，仅 Adreno）。

`sched_inner_reduction`（L88-428）是规则的本体，内嵌 `apply` 闭包（L105-306）接受 13 个 tile 参数，用 explain-05 的原语序列拼出完整 GPU 调度：两次 rfactor（L122-136，先把归约拆成 tx×vec_c 再拆到 tx）、`sch.split/reorder/bind` 三连（L139-145，blockIdx.x + threadIdx.y/x）、`vectorize`（L145）、cache_read 到 local/shared（L167、L185）、shared 内存预算检查（L147-165：累加 vector buffer 字节数，无 warp shuffle 时还要加 TS×TR 的 allreduce 缓冲，超过 `max_smem` 就放弃 LOAD_V_SHARED）、两级 `decompose_reduction`（L249-250）、`set_scope` 到 local（L252-253）、pragma 注记 unroll（L257-273）、epilogue 处理（L286-304）。而**参数选择**在闭包外（L308-411）：按 target.kind.name 查六张专家表——cuda（L322-332：VEC_C=4、TS/TR=16/32、SUPPORT_WARP_SHUFFLE=True）、metal（L333-347，注释自曝"M2 Ultra 上为 7B 模型调的"）、rocm（L348-362，L350-353 TODO 注明 rocm shared 读写 dtype 不一致的问题）、android/adreno opencl（L363-371）、vulkan（L372-383）、mali（L384-389）、默认兜底（L390-395）；L397-401 再按 `max_num_threads` 硬上限对分缩 TS/TR；L403-411 用 `get_max_factor` 从循环长度反推 TILE_R/VEC_C（保证整除）。

**入口装配**（`dlight/__init__.py`）：L20-22 装载三条产品线，L23-33 导出 `ApplyDefaultSchedule`（relax pass 形式的总入口，把 IRModule 里每个 PrimFunc 依次过规则表）与 `try_inline` 工具。

## 外部连接

- **下游原语**：所有规则直接消费 explain-05 的 `s_tir.Schedule` API（split/fuse/rfactor/bind/cache_read/decompose_reduction/annotate），dlight 本质上是"调度原语序列的专家模板库"。
- **relax 集成**：`ApplyDefaultSchedule` 挂进 relax 编译管线，作为 meta_schedule 之外的低成本默认路径；`benchmark/` 子包（extract.py/bench.py）提供与 meta_schedule 对齐的评测工具。
- **对照线**：meta_schedule（explain-07）的 `schedule_rule/` 目录是"搜索空间生成规则"，与 dlight 的"直接生成调度规则"同名不同物——前者产候选空间，后者直接产答案。
- **LLM 线呼应**：GEMV 形态判定覆盖 decode 期 `W[m,n]·x[n]`；`gpu/matmul.py` 覆盖 prefill 期 GEMM；`rmsnorm.py` 直接对应 LLM 的 RMSNorm 算子。

## 数据流

一次 `ApplyDefaultSchedule`：取 PrimFunc → `normalize_prim_func` 得 block 序列 → 按规则表顺序（通常 gemv→matmul→reduction→fallback）逐个 `apply`，第一条返回非 None 者胜出 → 规则内部先做结构判定（漏斗式提前退出，全部纯静态零测量）→ 选定 tile 参数（查表 + 循环长度整除性反推）→ 发射原语序列改写 IR → 产出最终 Schedule（无 tunable 指令，不需要 database）。整体耗时毫秒级，对比 meta_schedule 的分钟~小时级测量。

## 设计决策

1. **None 三态协议**：规则不适用地物（land不匹配）就静默让位，规则表因此可自由扩展、顺序即优先级——把"调度策略选择"做成责任链。
2. **静态分析换测量**：tile 参数全部由"查表 + 整除性约束求解（get_max_factor）"决定，牺牲一点峰值性能换取零调优时间——服务"开箱即用"的 LLM 部署场景。
3. **参数表外置**：target 专家知识与调度结构（apply 闭包）分离，新增后端=加一张表（对照 L590-592：外层归约只支持 adreno/metal，其余 target 直接 return None）。
4. **硬件约束做硬闸**：max_num_threads 对分缩（L397-401）、shared 内存预算核算（L147-165）在发射前完成，规则永不产出超限调度。
5. **fallback 链**（L81-85）：主路径失败降级简化模板——比直接放弃更符合"out-of-box"承诺。

## 新人提示

- 调试"为什么我的算子没被 dlight 优化"：在 apply 漏斗的每个 return None 处打断点/加打印（L47/51/60/66/70/77），绝大多数卡在 normalize 后 block 数不符或 is_gemv 判定。
- `# ruff: noqa: E741`（gemv.py L17）说明文件里大量 `l` 变量名是明知故犯——读 `l = sch.get_loops(block=V_shared)[-1]`（L187）这类代码别按常规风格期待。
- 新增自定义规则：`ScheduleRule.from_callable`（schedule_rule.py L88-91 示例）三行起步，再考虑继承 GPUScheduleRule 获得目标过滤。
- gemv.py L334 的注释"tuned on M2 Ultra for 7B"提示这些魔法数来自具体 LLM 实测——改参数前先跑 `benchmark/` 建立基线。
