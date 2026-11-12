# vllm/config/vllm.py — VllmConfig：config/ 包的总装车间与 pydantic 化配置中枢

> 源码：`vllm/config/vllm.py`（3672 行）｜vllm/config/ 包共 36 个文件｜vLLM 2026-10-28 @06e172b5cf

## ① 角色定位

`vllm.py` 在 vLLM 分层最底层的**配置层**，但已不是孤胆文件：`vllm/config/` 目录化后拆出 model/parallel/scheduler/cache/compilation/kernel/attention 等 30 余个子配置模块，本文件承担"总装"角色——`VllmConfig`（vllm/config/vllm.py:349）把 34 个字段（30 个子配置对象+4 个顶层标量）聚合为全引擎唯一的配置聚合根，EngineCore/Executor/ModelRunner 拿到手的都是同一实例。2026-09→10 两个形态级变化：一是子配置激增（attention_config:372、kernel_config:380、engram_config:376、aux_output_config:374、watermark_config:386、watchdog_config:451 全是新面孔）；二是基座换成 **pydantic dataclass**——`@config(config=ConfigDict(arbitrary_types_allowed=True))` 装饰（vllm/config/vllm.py:348，装饰器在 vllm/config/utils.py:52，默认 `extra="forbid"`），并新增 `@model_validator(mode="after")`（:3422/:3452/:3466）。

## ② 内部结构

文件四段：**融合谓词与 O0-O3 预设**（157-345）、**VllmConfig 类体**（349-3564）、**进程级上下文**（3567-3645）、**层查询工具**（3651-3672）。

模块级符号：`DEFAULT_BREAKABLE_CUDAGRAPH_ARCHITECTURES`（:76）+ 平台感知的 `default_breakable_cudagraph_architectures()`（:112，ROCm 只留 DeepseekV41）——"可打断 CUDA graph"是新 infra；`OptimizationLevel`（:132）与 `PerformanceMode`（:147，balanced/interactivity/throughput）双轴；8 个 `enable_*_fusion` 谓词（:157-252）；四张预设字典 `OPTIMIZATION_LEVEL_00..03`（:255-338）+ 映射表 `OPTIMIZATION_LEVEL_TO_CONFIG`（:340），O1 起开 flashinfer autotune，O2/O3 开 FULL_AND_PIECEWISE cudagraph。

`VllmConfig` 字段三分：default_factory 的必有配置 18 个；`None` 表特性关闭的可选配置 12 个（engram/lora/speculative/watermark/diffusion/quant/kv_transfer/kv_events/ec_transfer/reasoning/weight_transfer/model）；标量 4 个（instance_id、optimization_level 默认 O2（:435）、performance_mode（:441）、shutdown_timeout（:454））。方法重镇：`compute_hash`（:460，递归聚合子配置 hash 出 10 位指纹）；`__post_init__`（:1510，约 830 行校验/派生管线）；派生 property 族（:578-767）——`max_concurrent_batches`:588、`num_speculative_tokens`:612、`num_lookahead_tokens`:626、`num_prefill_lookahead_tokens`:655、`uniform_decode_query_len`:695、`use_v2_model_runner`:731、`needs_dp_coordinator`:873；以及 `_set_max_num_scheduled_tokens`（:2342）、`_set_cudagraph_sizes`（:2399）、`_set_compile_ranges`（:2659）、`try_verify_and_update_config`（:2736）、`validate_block_size`（:3391）。

## ③ 外部连接

- **依赖**：相对导入 config 包 29 个子配置模块（:31-59）；运行时惰性 import `current_platform`（:25；:1826 `apply_config_platform_defaults` 与 :2068 `check_and_update_config` 两个平台 hook）、`vllm.v1.executor.abstract.Executor`（:1641 查 executor 能力）、`KVConnectorFactory`（:1256/:2261）、`ModelRegistry`+`MODELS_CONFIG_MAP`（:2749）。仍是纯配置层——不 import 模型执行代码，保证跨进程安全序列化。
- **被依赖**：`config/__init__.py`（160 行）re-export 全部符号给全仓；模型层 custom ops 运行期经 `get_current_vllm_config()`（:3631）查询；`get_cached_compilation_config()`（:3626）是新加热路径缓存，`set_current_vllm_config`（:3572）进出上下文都 `cache_clear()`（:3591/:3622）防串味。

## ④ 数据流

```
EngineArgs.create_engine_config() → 组装子配置
  → VllmConfig(**sub_configs) @:349
    → __post_init__ @:1510 管线：
      ① instance_id=time.time_ns() @:1513
      ② _limit_max_model_len_to_draft @:1541 → try_verify_and_update_config
         @:1542（模型注册表钩子可改写 config，Hybrid 挂 :2768）
      ③ async_scheduling 三态仲裁 @:1669-1720（显式开启→硬失败；
         None→按 executor/PP/spec 方法自动定；pooling 默认关）
      ④ enforce_eager → CompilationMode.NONE @:1767
      ⑤ _maybe_enable_breakable_cudagraph @:1794
      ⑥ apply_config_platform_defaults @:1826
      ⑦ O0-O3 预设回填 @:1855 + _maybe_disable_dynamic_sd_* @:1863
      ⑧ _set_max_num_scheduled_tokens @:1949 → _set_cudagraph_sizes @:2014
      ⑨ 平台终审 check_and_update_config @:2068
      ⑩ MRV2/MRV1 分叉校验 @:2093 → _set_compile_ranges @:2105
      ⑪ set_splitting_ops_for_v1 @:2162 → HMA 三态 @:2229-2295
  → 序列化 spawn 进 EngineCore
  → 运行期 compute_hash()=编译缓存 key；模型前向包在
    set_current_vllm_config 上下文内（CustomOp 借 :3631 读配置分派）
```

## ⑤ 设计决策

1. **pydantic 换代**：`extra="forbid"` 让拼错字段名在构造期就炸；代价是 `@model_validator` 与 `__post_init__` 并存（:3422 三个 validator 管 nvfp4×MLA、mamba block_size、ReplaySSM），要找齐两处校验入口。
2. **"唯一事实源"property 族**：`num_lookahead_tokens`（:626）docstring 明言"消费者必须读此 property 而非自行推导"，否则 scheduler 与 warmup 会漂移；`uniform_decode_query_len`（:695）特意**不**从 KV 预留槽推导（DFlash 预留 n+1 但验证 1+n，EAGLE 预留 n 验证 1+n——差一个请求宽度就是事故）。
3. **hash 只纳入影响计算图的因素**：`compute_hash` 警告注释（:461）不变；`quant_config` 跳过（:541，已由 model_config.quantization 覆盖）；`additional_config` 支持 dict→json 或 `SupportsHash` 协议（:560-568）给平台留口。
4. **MRV2 成为默认分叉轴**：`use_v2_model_runner`（:731）先看 HiSparse/watermark 硬性要求，再看 env，再扫 V2（:3054）与 V1（:3090）不支持清单——dspark/xpress/adaptive verification/diffusion 已是 V2-only，`_validate_v1_model_runner`（:3333）对不支持项直接 raise。
5. **cudagraph 尺寸推导精细到投机解码分层**：`_set_cudagraph_sizes`（:2399）里 uniform decode 尺寸按 request-count 网格而非 token 网格（:2472 注释算账：token 网格 581 个尺寸 vs 100 个）；动态投机解码按 tier 取最宽 batch（:2505-2540）；`interactivity` 模式 1..32 全覆盖（:2574）。
6. **防漂移的校验顺序**：平台 hook 分"改默认"（:1826）与"终审"（:2068）两次插入；async_scheduling 仲裁在第一个 hook 前、最终 assert（:2168-2179）在所有 mode 更新后——顺序本身就是协议。

## ⑥ 新人提示

- 读法：先读 :356-458 字段声明 → :1510 起按管线段号跳读，别顺序啃 830 行。
- **加字段三连**：加字段 → 判断是否进 `compute_hash`（:460）→ 补 `__post_init__` 或 `@model_validator` 校验；pydantic 化后再加一条——字段类型要能过 :348 的 ConfigDict 校验。
- `optimization_level` 默认已是 O2（:435），`-O0` 仍是排查启动问题第一手段（等价 :1767 enforce_eager 路径）。
- `max_num_batched_tokens`（输入预算）vs `max_num_scheduled_tokens`（:2342 派生的调度预算）仍是最易混的一对；后者带 spec-decode 下限与 8192 告警。
- `instance_id` 在 :1513 被 time_ns() 覆盖、:2207 又可能被 random_uuid()[:5] 覆盖——只当 profiler 命名用；用户显式给的 `cudagraph_capture_sizes` 优先（:2561 分支）。
