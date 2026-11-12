# EXPLAIN-06 · modelopt/onnx：图级 Q/DQ 量化与"基准反馈搜索插入点"的 autotune

## 一、角色定位

`modelopt/onnx/` 是第三条量化战线：输入**已导出的 ONNX 模型**（无 Q/DQ）+校准数据，输出显式携带 QuantizeLinear/DequantizeLinear 节点的 ONNX，供 TensorRT/ORT 等图编译器消费。与 torch 线（伪量化模块树）不同，操作对象是计算图——量化决策单位不是"某个 Linear"，而是"哪条边、哪个算子的输入输出该插 Q/DQ"。

本线最有代表性的是 `autotune/`：**用真实 TensorRT 基准的延迟反馈搜索 Q/DQ 插入点**。传统 PTQ 按算子类型+经验规则静态插点，但 TRT 融合行为高度依赖图结构——某个 Q/DQ 可能让融合失败反而变慢。autotune 把插入点组合当超参，每个候选真建引擎测延迟留最快的。CLI 措辞即契约："calibrated Q/DQ is retained only when it meets the 1.02x performance threshold; otherwise the output has no Q/DQ"（`__main__.py:384-386`）。

## 二、内部结构

### CLI：quantization/__main__.py（595 行）

四组参数：**模式与校准**——`--quantize_mode` int8/int4/fp8（`:119`）；`--calibration_method` 按模式分流（int8/fp8 用 entropy/max，int4 用 awq_clip/rtn_dq）；`--calibration_eps` 执行提供者优先级默认 `["cpu","cuda:0","trt"]`（`:160`），支持 NvTensorRtRtx（TensorRT-RTX）；`--calibrate_per_node` 逐节点校准压显存。**形状 profile**——动态形状须给 min/opt/max 三档：`--input_shapes_profile` 接内联 JSON 或文件，"列表必须与 --calibration_eps 一一对应同序"（`:102-107`），解析器强校验类型（`:34`）；不传可 `--model_id` 从 HF config 推断。**图手术旋钮**——支持正则的 `--nodes_to_quantize/exclude`、`--dq_only`（权重真量化只留 DQ）、`--disable_mha_qdq`、`--opset`（默认按模式取 19/21/23，`:361-365`）。**autotune 组**（`:378-480`）——三档预设经 `apply_mode_presets`（`:484`）展开：quick=30 方案/10 预热/50 计时、default=50/50/100、extensive=200/50/200（`autotune/utils.py:28-33`），`StoreWithExplicitFlag`（`:36`）保证显式参数覆盖预设；另有 crash-resume 状态文件、pattern cache 热启动、trtexec 开关。`main()`（`:501`）两处安全设计：默认拒绝 >2GB ONNX 输入（防 DoS；profile JSON 限 1MB 同理，`:60-81`）；校准 npz 默认 `allow_pickle=False` 防 RCE。

### 图级量化主流程：quantize.py（961 行）

默认算子表：INT8 量化 Add/Conv/Gemm/MatMul 等十一种、INT4 只做 Gemm/MatMul、FP8 做 Conv/Gemm/MatMul（`quantize.py:25-28`）。入口 `quantize()`（`:466`）：加载→`_preprocess_onnx`→MHA 保护（按 head_size/seq_len 经验规则排除）→三路分发：`quantize_func = quantize_int8 if quantize_mode=="int8" else quantize_fp8`（`:854`）——fp8 复用 int8 框架仅 scale/dtype 语义不同；int4 走独立 `quantize_int4`（`:888`，AWQ 系列）；autotune 开启则完全绕过静态规则。`int8.py`/`fp8.py`/`int4.py` 实现各模式校准与落图，`qdq_graph.py` 是共享图操作底座。`fp8.py` 的 `int8_to_fp8`（`:55`）很巧妙：max 校准的 INT8 模型直接转 FP8，scale 公式 `int8_scale*448.0/127.0`（`:75-79`），校准基建完全复用。

### autotune/（14 文件，本线精华）

**发现**：`QDQAutotuner`（`autotuner.py:26`）在 initialize 时自动搜索区域（`:82-104`）：`CombinedRegionSearch` 先自底向上按张量发散/收敛分区、再自顶向下细化出层级（`region_search.py:450/732/999`），产出 LEAF/COMPOSITE/ROOT 三类 region 树，摊平后 **LEAF 优先**进入画像（`autotuner.py:111`）。**分组**：`RegionPattern`（`region_pattern.py:33`）给 region 算结构签名（拓扑+算子类型），同签名共享搜索结论——32 层同构 decoder layer 只调优一次，是搜索空间压缩的关键；`PatternCache` 可跨模型热启动。**插入点三形态**（任务书"三种形态"吻合）：`NodeInputInsertionPoint`（节点输入，`insertion_points.py:100`）、`ChildRegionInputInsertionPoint`（子区域输入边界，`:170`）、`ChildRegionOutputInsertionPoint`（子区域/节点输出边界，`:233`）；坐标是 pattern-相对而非绝对节点名——"pattern-relative indices...enables insertion scheme reuse across all regions matching the same pattern"（`:100-106`）；解析成绝对 `ResolvedInsertionPoint`（`:75`）才落图；`_MUTATION_SPECS` 按这三类组织变异（`autotuner_base.py:58-70`）。**搜索循环**：`generate()`（`:278`）从 top-10 方案随机取一个变异（增删插入点）、哈希去重；方案经 `export_qdq_onnx` 真插成候选模型；`submit(latency_ms)`（`:637`）首个有效延迟作 baseline，之后每次算 speedup、按延迟排序维护最优并同步 pattern cache（`:705-710`）；`save_state/load_state`（`:715/763`）YAML 崩溃恢复。**基准双路**：`TrtExecBenchmark`（`benchmark.py:147`）fork trtexec 子进程、正则抓 `Latency:.*median`（`:181`）；`TensorRTPyBenchmark`（`:308`）走 TRT Python API；`init_benchmark_instance`（`workflows.py:84`）二选一，`benchmark_onnx_model`（`:39`）失败返 `float("inf")` 不抛异常（搜索循环不能被坏方案打断）。**落图**：`export_qdq_onnx`（`export_utils.py:315`）把赢家方案真实转成 Q/DQ 节点；FP8 先按 INT8 构建、`needs_fp8_conversion` 时再整图转换（`:321-346`）；zero-point 越界即抛错（`:77-97`）。**终局守门**：`_apply_autotune_final_guard`（`quantize.py:417-464`）把"Q/DQ 候选"与"无 Q/DQ 基线"各建引擎端到端实测，`keep_candidate = _has_qdq_site and speedup >= threshold`（`:450`），不达标回退基线并警告——搜索期赢家须再赢一次对拍，防引擎构建抖动假阳性；`performance_threshold` 默认 1.02（`common.py:828`）。

### 外围：graph_surgery/ + trt_utils + op_types

`graph_surgery/` 独立 CLI 五个子命令（`graph_surgery/__main__.py:16-55`）：`replace-gqa`（MHA 换 GQA 等效子图，1513 行的 `gqa_replacement.py`）、`add-cross-kv`（encoder 加 cross-attention KV cache，Whisper 场景）、`convert-bf16`、`transpose-dq`（量化权重列主序转置）、`analyze`。`trt_utils.py` 封装 TRT 插件管理（lief 检查 .so 静态链接，`:46`）。`op_types.py` 是纯函数算子分类表——几十个谓词（`:18-58`），供 autotune 判可插点、graph_surgery 判透明算子。

## 三、外部连接

上游：torch 线经 `modelopt.onnx.export` 或用户 `torch.onnx.export` 产出输入模型。下游：TensorRT（autotune 基准环境与部署目标，双通道）、ONNX Runtime（校准执行环境；`get_ort_quantization_config`（`autotuner_base.py:482`）产出 ORT config 供普通量化路径复用搜索结论）、TensorRT-RTX。TRT 是硬依赖但有守卫：`benchmark.py:38` 的 `TRT_AVAILABLE=find_spec("tensorrt")`，`autotune/__init__.py:44-50` 导入失败仅告警。

## 四、数据流

标准 int8/fp8：ONNX(fp32)→按 eps 优先级起 ORT 会话跑校准收集 per-tensor range（或读 cache）→静态规则选点→插 Q/DQ（权重侧 Q 折叠进 initializer 即提前量化）→可选 `dq_only` 去 Q→fp16/bf16 混合精度→opset 对齐→输出。

autotune：ONNX→region 两阶段分区→pattern 签名分组→每 pattern 循环{变异生成方案→插成候选模型→基准测延迟→submit 更新排名/cache}→收敛→汇总赢家落成完整 Q/DQ 图→**final guard 端到端对拍**（speedup≥1.02 才保留）→输出。崩溃可从 `autotuner_state.yaml` 断点续跑。

## 五、设计决策

- **测量优先于规则**：静态规则是低成本兜底，autotune 是高收益升级；两者共用 Q/DQ 落图工具，方案可互相导入（`--autotune_qdq_baseline` 把预量化模型当热启动）。
- **pattern-相对坐标**：一次搜索结论按结构签名复用到所有同构 region——把组合搜索从"全图指数级"压到"每 pattern 数十次基准"。
- **防御性默认**：2GB/1MB 上限、pickle 禁用、基准失败返 inf、final guard 强制复测——失败路径都有良好降级。
- **INT8 框架承载 FP8**：FP8 复用 INT8 全部基建，只在 scale 换算与 dtype 分叉；autotune 的 FP8 候选也"先 INT8 后整图转换"（`export_utils.py:333`）。

## 六、新人提示

1. **先跑 `--autotune quick` 摸底**：extensive 每 region 200 方案动辄数小时；quick 通常够找到大部分收益。`--autotune_output_dir` 指大盘，state/pattern cache 都在里面。
2. **看懂日志里的 "not quantized"**：final guard 回退时产物就是无 Q/DQ 的 fp16 模型——这是契约不是 bug（宁可不量化也不变慢）；若预期应有加速，查 `logs/calibrated_baseline.log` 的构建精度配置。
3. **动态形状必须给 profile**：min/opt/max 与 `--calibration_eps` 一一对应，缺档 TRT 构建失败或测出误导性延迟。
4. **自定义算子走 TRT EP**：含 custom op 时 EP 自动加 `trt` 并需 `--trt_plugins` 指 .so——TrtExecBenchmark 自动追加 `--staticPlugins`（`benchmark.py:193-197`）。
5. **改插入点类型要动四处**：三个 dataclass、`_MUTATION_SPECS`、`RegionPattern` 签名、序列化 schema 按三形态对齐，漏改一处会让 pattern cache 旧条目反序列化失败。
