# csrc/api/sparse_decode.h 精讲

> 原文件：`csrc/api/sparse_decode.h`（495 行）

## ① 角色定位

稀疏解码的 **C++ 分派中枢**。pybind11 把 Python 张量送进来后，本文件负责：全量输入校验、按架构与头数挑选实现类、编排"调度元数据 → 主内核 → combine"三段流水。主函数是 `sparse_attn_decode_interface`（183 行）。

## ② 内部结构

- **`DecodeFeatures` 枚举**（14-28 行）：能力面拆成可组合特征——`HEAD_64/HEAD_128`、`HEAD_DIM_576/512`、`V32/MODEL1_KVCACHE_FORMAT`、`ATTN_SINK`、`TOPK_LENGTH`、`EXTRA_*`。
- **实现类四件套**（继承 `DecodeImplBase`，`DECLARE_SUPPORTED_FEATURES` 声明能力集，`get_meta(h_q,s_q)` 返回 `{num_sm_parts, fixed_overhead_num_blocks, block_size_topk}`）：
  - `Decode_Sm90_Impl`：Hopper 全特性，经双层模板分派调 sm90 sparse_fp8 内核；
  - `Decode_Sm100_Head64_Impl`：Blackwell 64 头；
  - `Decode_Sm100_Head64x2_Impl`（112-153 行）：**跑两遍 head64 拼出 head128**——V3.2 形状（h=128, d_qk=576）在 SM100f 无原生内核，把 q/lse/out 等指针按 stride 平移 64 头再跑第二遍；
  - `Decode_Sm100_Head128_Impl`：d_qk=512 原生路径，调 sm100 head128 的 phase1 内核。

## ③ 外部连接

上游是 `api.cpp` 的 pybind 绑定；下游拉起 sm90/sm100 内核与共享层 scheduler/combine 两个 kernel。`SparseAttnDecodeParams` 与 `ModelType::{V32, MODEL1}` 定义在 `csrc/params.h`；校验宏来自 kerutils 子模块。

## ④ 数据流

① 架构探测 + 断言（`h_kv==1`、`d_qk∈{576,512}`、`d_v==512`）；② dtype——q 必须 bf16，**kv 接受 fp8_e4m3fn/int8/uint8**（260 行，裸字节视角）；③ 布局（末维连续、block 内 contiguous）；④ FP8 字节数自检（288-305 行）：V3.2 风格 `512+64*2+(512/128)*4=656` B/token，MODEL1 风格 `448+64*2+(448/64)*1+1=584` B/token；⑤ 收集 features；⑥ new 对应 impl 取 meta（`is_sm100f()` 按 h_q/d_qk 细分，`is_sm90a()` 走 Sm90）；⑦ 组装 params（裸指针 + 收窄步长）；⑧ 元数据缺失则分配 int32 并跑 scheduler kernel；⑨ 分配 split-KV 缓冲（`b + num_sm_parts`，455 行）；⑩ `impl->run` + combine；⑪ 返回 `{out, lse.transpose, 元数据, num_splits}`。

## ⑤ 设计决策

- **注册式分派**：选择逻辑集中一段 if-else，新增架构只需加 Impl 类；`num_sm_parts` 公式随实现自报——Sm90 用 `num_sms/s_q/(h_q/64)`，Sm100 Head64 用 `num_sms/s_q`，Head128 用 `num_sms/s_q/2` 且 fixed_overhead 从 5 降到 3。
- **元数据外置缓存**：`tile_scheduler_metadata` 以 optional 传入，命中则跳过 scheduler kernel（419 行），与 Python 层 `FlashMLASchedMeta` 复用闭环。
- **Head64x2 指针平移**：不做张量切片（免新分配），只挪裸指针并重设 `h_q=64`，零拷贝。
- **`b + num_sm_parts` 总缓冲**：每序列至多被 num_sm_parts 个 SM 各持一个 split，加 b 保证不越界。

## ⑥ 新人提示

1. 先读 183 行接口函数的签名注释（张量契约清单），再跳 362 行分派表；中间是防御性检查，可后读。
2. 改 `bytes_per_token` 公式必须同步 Python docstring 与 `params.h`，三处一致才是协议。
3. `delete impl` 是裸指针管理，提前 return 会泄漏。
