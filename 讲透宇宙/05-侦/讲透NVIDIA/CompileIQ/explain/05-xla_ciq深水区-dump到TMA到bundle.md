# 05 · xla_ciq 深水区：XLA dump → TMA tile → ACF bundle

## 角色定位
`examples/compilers/xla_ciq_example/` 是仓内最大子项目（55 文件，src 约 3684 行），主线：读 XLA 编译 dump → 提取 TMA tensor map 布局 → 枚举合法 tile 替代 → 经 CompileIQ 调优 → 序列化为 protobuf bundle。定位是 **producer-side 示例**：`workflow.md` 责任表明言搜索算法归父包，本树只做解析、指纹与序列化，下游 XLA consumer 与指纹稳定性**不在**承诺范围。

## 内部结构
四个子包各司其职：`xla/dump.py`（170 行）——`inspect_dump`（`dump.py:47`）索引内核，`_index_ptx_kernels`（`dump.py:91`）扫 module.ptx，`_enrich_from_thunks`（`dump.py:101`）rglob thunk_sequence/metadata 文本，`_enrich_shapes_from_hlo`（`dump.py:133`）从 HLO 提形状；`xla/tensor_map.py`（308 行）——`TensorMapSpec`（`tensor_map.py:44`）值对象 + `from_hlo_shape`（`tensor_map.py:186`）把 HLO 行主序 shape 转 **CUDA innermost-first 序**（`tensor_map.py:11` 注释点破两者相反）；`search/` 子包——`ptx_meta.py`（198 行）用四组正则 `_ARRAY_RE`/`_SCALAR_RE`/`_ALIGN_RE`/`_MOV_PARAM_RE`（`ptx_meta.py:14-20`）纯文本解析 PTX 参数（入口 `inspect_ptx_entry` `ptx_meta.py:158`），`tensor_map_search.py`（271 行）枚举合法 TMA box；`bundle.py`（204 行）+ `fingerprint.py` 负责序列化与指纹。

## 外部连接
向上经 `search/compileiq_runtime.py`（743 行）的适配器调父包 Search；schema 源在子项目内 `schemas/xla_ciq_bundle.proto`（注意不在仓根 schemas/），`bundle.py:3-5` 给出再生命令 `python -m grpc_tools.protoc -I schemas --python_out=src/xla_ciq ...`；CI 的 run-examples job 专跑本子项目（mock reference example 与 protobuf binding check，`ci.yml:235-242`）。

## 数据流
dump 目录 → `inspect_dump` 出 KernelInfo（PTX 文件、thunk 元数据、形状）→ `from_hlo_shape` 出 TensorMapSpec（含 box/swizzle seed）→ `legal_box_sizes` 枚举候选 → RuntimeObjective 逐候选启动内核计时 → 最优布局编码进 `XlaCiqTuningBundle`（`bundle.py:19`）经 `encode_bundle`（`bundle.py:108`）落盘。

## 设计决策
三个教科书级决策：(1) **RuntimeObjective 的 pickle 契约**（`compileiq_runtime.py:54`，docstring："multiprocess workers cannot pickle nested defs"）——目标函数必须是模块级类，tensor map specs 以值对象嵌入（property `compileiq_runtime.py:77`），可 pickle 供多进程、可哈希供去重；(2) **空间爆炸控制**——joint ACF×tile 组合爆炸，`tensor_map_search.py:22-27` 注释明言只保留 seed box 及邻域，硬约束 `_TMA_ALIGN_BYTES = 16`（内轴 16 字节对齐，`tensor_map_search.py:19`）；(3) **seed 钉扎**——`choice` 无法置初值，`_index_knob`（`tensor_map_search.py:98-111`）改用 `range(..., seed_low=0, seed_high=0)` 把初始采样钉在已知能启动的 seed 布局。protoc 生成物 `xla_ciq_bundle_pb2.py`（52 行）**不建议手改**，改 schema 后重新生成。

## 新人提示
从 `workflow.md` 的责任表与 CLI 入手：`python -m xla_ciq.cli xla inspect <dump-directory>`。测试自带夹具（`tests/fixtures/xla_dump/module.ptx` 与 `sample.ptx`），16 个测试文件无需真 XLA 环境即可跑通解析链。
