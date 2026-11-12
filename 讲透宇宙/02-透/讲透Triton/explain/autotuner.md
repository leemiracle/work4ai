# python/triton/runtime/autotuner.py — @triton.autotune：运行时多配置基准与缓存

## 1. 角色定位

13 层架构中属 **runtime-backends（运行时与后端抽象层）**，紧邻 jit.py。513 行：`@triton.autotune` 把 JITFunction 包装成 `Autotuner`，让多个 `Config`（BLOCK_SIZE/num_warps/num_stages 组合）在真实硬件实测耗时、按 key 缓存最优者。它不参与编译，只搜索"选哪个编译变体"。

## 2. 内部结构

- **Autotuner**（L19）：`__init__`（L21）装配 configs/prune_configs_by/reset_to_zero/restore_value/hooks；老接口 warmup/rep/use_cuda_graph 已废弃（L104-125）。
- **`_bench`**（L133）：`kernel_call` 闭包（L150-166，pre_hook → fn.run → post_hook）→ `do_bench(..., quantiles=(0.5,0.2,0.8))`（L169）取中位数；编译期失败返回三倍 inf（L170-173）——淘汰而非崩溃。
- **`run`**（L217）：缓存键 = key 参数值 + 带 dtype 实参的 dtype 串（L221-227）；miss 时 `prune_configs`（L284）两级剪枝：`early_config_prune`（L286）→ `perf_model`+`top_k` 截断（L291-312）；仅剩 1 个 config 时跳过基准（L232-235）。
- **`check_disk_cache`**（L175）：sha256(triton_key+backend hash+fn.cache_key+环境变量+key+configs)（L188-195）读 JSON timings；pre_hook 不可序列化则放弃（L177）。**Config**（L328）/工厂 `autotune`（L409）；**Heuristics**（L478）为零成本按函数算元参数的轻量替代。

## 3. 外部连接

图谱出边 imports：`jit.py`、`driver.py`、`cache.py`、`errors.py`、`knobs.py`；延迟引 `triton.testing.do_bench`（L118）。入边仅 `runtime/__init__.py` 与 `compiler/compiler.py`。`knobs.autotuning`（knobs.py L383-386）：`TRITON_CACHE_AUTOTUNING`、`TRITON_PRINT_AUTOTUNING`、`listener`（L253-264 回调 best_config/timings）。

## 4. 数据流

首次调用 `kernel[grid](x, N)`：

1. `run`（L217）绑定 nargs；configs>1 才调优，否则直取唯一 config（L267-268）。
2. 构造 key（L223-227）；`self.cache` 命中 → 直跳第 6 步。
3. `prune_configs`（L230）：early_config_prune 剔形状非法配置，perf_model 留 top_k。
4. `benchmark`（L238-246）：逐 config 调 `_bench`——首次触发该变体 JIT 编译后计时；bench 期间 `_pre_hook`（L59-70）zero/clone 保护输出张量，`_post_hook`（L77-82）还原，结束再复位（L245）。
5. `builtins.min(timings)`（L243）入 `self.cache[key]`；cache_results 开时查/写磁盘（L248-249）。
6. 正式 launch（L276-280）：`fn.run(*args, **kwargs, **config.all_kwargs())`。同 key 后续零开销。

## 5. 设计决策

**为何运行时实测而非静态模型**：tile/warp/stage 最优解由 SM 数、shared memory、L2、tensor core 代际共同决定，解析模型误差大（同一 matmul 在 A100/H100 最优 config 差数倍）。三层可组合：`heuristics`（零成本公式）→ `perf_model` 粗筛 → `do_bench` 实测（中位数抗抖动）；bench 时机在"首次遇到该 key"（惰性），调优税只摊给真实形状。**失败返回 inf 而非抛错**（L170-173）：激进配置安全参与竞争。**reset_to_zero/restore_value**：bench 跑多遍污染累加型输出，交用户声明式修复（L427-430）。**磁盘缓存键纳入 backend hash 与环境变量**（L188-194）防跨架构错配。**Heuristics 并存**：形状可推导参数不付 bench 税；工业库更彻底——triton_kernels 弃 autotune 改查表（见 triton-kernels.md）。

## 6. 新人提示

切入点：`python/test/unit/runtime/test_autotuner.py` + `tutorials/03-matrix-multiplication.py`；`TRITON_PRINT_AUTOTUNING=1` 看 bench 耗时与 best config（L270-272）。易错点：① key 漏写参数 → 换形状复用错配置（dtype 自动追加 L224-226，标量形状值不会）；② 累加型 kernel 忘 reset_to_zero → 输出被 bench 污染；③ stride 实参不标 `do_not_specialize` → 每个奇偶 stride 触发重调优；④ 磁盘缓存默认关，CI 复用需开 cache_results 或环境变量。
