# tile_kernels/config.py 精讲

> 原文件：`tile_kernels/config.py`（29 行）

## ① 角色定位

全仓最短却被引用最广的文件——**设备能力查询与 SM 配额中心**。六个算子域（moe/quant/transpose/engram/mhc/gating）的内核在规划 grid 与 shared memory 时都要回答："这块卡有多少 SM？允许我用几个？"答案统一从这里拿。`set_num_sms` 是限制内核占用的全局开关，让 TileKernels 与其他组件共卡时能划清资源边界。

## ② 内部结构

四个函数 + 一个模块级全局，29 行无冗余：

- **`get_device_num_sms()`**（7-10 行）：`functools.lru_cache(maxsize=None)` 包裹，首次经 `torch.cuda.get_device_properties(torch.cuda.current_device())` 取 `multi_processor_count`，此后永不再查。
- **`set_num_sms(num_sms)`**（13-16 行）：写全局 `_num_sms`，`assert 0 < num_sms <= get_device_num_sms()`——只能往下限，不能凭空造 SM。
- **`get_num_sms()`**（19-23 行）：`_num_sms == 0`（哨兵）时回落真实设备 SM 数，否则返回限额。
- **`get_max_smem_per_sm()`**（26-29 行）：同样 lru_cache，取 `shared_memory_per_multiprocessor`。

## ③ 外部连接

全仓十个文件直接调用：`engram/engram_gate_kernel.py`（persistent block 估算）、`moe/` 四内核（get_fused_mapping/group_count/aux_fi/inplace_unique）、`quant/swiglu_forward_and_per_token_cast_kernel.py`、`modeling/mhc/ops/` 两处、`tile_kernels/__init__.py`（re-export 公共 API）。典型消费方式见 engram（502 行）：`get_engram_gate_fwd_kernel(..., get_num_sms(), ...)` 把 SM 数作为 JIT 编译期参数传入工厂——**设备几何直接参与代码生成**；`get_max_smem_per_sm` 驱动占用估算（45 行 `blocks_per_sm = min(max_smem // smem_bytes, 16)`）。

## ④ 数据流

纯控制流配置，无张量。生命周期：import 时不做 CUDA 调用（惰性）；首次内核启动触发 `get_num_sms()` → 驱动查询 → lru_cache 固化；此后 `set_num_sms(64)` 生效于**下一次** `get_num_sms()`，各工厂以 64 为分母算 grid/persistent blocks，已在运行的老内核不受影响（编译时已固化）。注意 `current_device()` 语义：lru_cache 键为空，**多卡进程里只会缓存第一次查到的卡**。

## ⑤ 设计决策

- **lru_cache 而非模块级常量**：设备属性查询要走 CUDA driver，每个内核工厂查一次会在 JIT 场景被放大；无键缓存把成本摊销到一次。
- **`_num_sms = 0` 哨兵而非 None**：int 全局在 CPython 读写原子，免锁；0 不是合法 SM 数（assert 强制 >0），语义无歧义。
- **限额而非亲和**：`set_num_sms` 只管"用多少"不管"用哪几个"——TileLang 内核用 persistent grid + `ceildiv(num_tokens, num_persistent_blocks)` 自行切分（见 engram 86-88 行），SM 数就是切分分母，天然实现配额。
- **与 JIT 的顺序契约**：SM 数在工厂调用时读入并特化，"先 set 再建内核"才生效——文档没写但代码路径决定。

## ⑥ 新人提示

1. 想看内核实际用了几个 SM：`set_num_sms(8)` 后建内核，配 `TK_PRINT_KERNEL_SOURCE=1` 看生成代码里的 grid 常数。
2. 多 GPU 服务进程别依赖这里的缓存——应在每进程绑单卡（仓库测试插件正是用 `CUDA_VISIBLE_DEVICES`，见 `tests/pytest_benchmark_plugin.py` 67-71 行）。
3. 新增设备属性查询（L2 大小、寄存器数等）照抄同款三行 lru_cache 即可，别引配置框架——这个文件是"共享基建保持极简"的样板。
