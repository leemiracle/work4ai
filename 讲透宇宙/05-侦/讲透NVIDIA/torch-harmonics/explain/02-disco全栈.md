# 02 · disco 全栈——卷积张量三形态与 sm90/sm100 双代 tensor core

> 源文件：`torch_harmonics/disco/convolution.py`（1012）+ `torch_harmonics/disco/optimized/disco_optimized.py`（1253）+ kernels_cuda 四件（529/392/649/118），共 3953 行。图谱定位：性能引擎。

## ① 角色定位：这个子系统解决什么问题

DISCO（Ocampo 2023）在球面定义紧支撑滤波器卷积：滤波器=可学习基函数线性组合，稀疏求积在网格上算。核心是稀疏卷积张量 Ψ（基函数在旋转后格点的取值）；经度等距使 Ψ 与输出经度无关（p-shift 对称）。看点是**三形态 + 双代内核**：稠密参考（测试）→ CSR（通用）→ kpacked（tensor core 专用）。

## ② 内部结构：关键类/函数与行号锚

**Ψ 的构造**：`_precompute_convolution_tensor_s2`（`torch_harmonics/disco/convolution.py:236`）@lru_cache，按 YZY Euler 角旋转收集支撑非零。关键优化是 `latitude_support_band` 限带（`torch_harmonics/disco/convolution.py:341`）：只在与输出纬度相距 cutoff 内的输入环求值，O(nlat_out·nlat_in·nlon_in) 砍到 O(nlat_out·band·nlon_in)，band 是支撑超集。

**三形态与 forward 分派**：`DiscreteContinuousConvS2`（`torch_harmonics/disco/convolution.py:484`）构造期把 COO 排成 idx+vals buffer，再派生 CSR（preprocess_psi）/split-CSR/kpacked；forward 五级分派（`torch_harmonics/disco/convolution.py:705`）：fused kpacked → fused CSR → save-x kpacked → save-x CSR → 裸收缩+einsum。

**kpacked 布局与双层设备判定**：`_maybe_kpack_psi`（`torch_harmonics/disco/optimized/disco_optimized.py:92`）把 [K,Ho,NBR_PAD] 稠密 pack 压成 blocked-CSR，每邻居携带全部 K_pad 值，docstring 点明：**块布局让收缩维 nz 落进 MMA 的 N 维**。判定分两层：`_kpacked_build_available`（`torch_harmonics/disco/optimized/disco_optimized.py:47`）问编译期是否编出内核，`_kpacked_supported_on_device`（`torch_harmonics/disco/optimized/disco_optimized.py:74`）forward 期问设备并查副版本——sm_100a cubin 不向前兼容，Rubin 10.7 会骗过 major==10（`torch_harmonics/disco/optimized/disco_optimized.py:70`）。

**双代内核**：sm90 版 `disco_fwd_dense_kpacked_wgmma_blk_k`（`torch_harmonics/disco/optimized/kernels_cuda/disco_cuda_fwd_dense_kpacked_sm90.cu:165`）128 线程、8×8 tile、A/B SMEM staging、`wgmma.mma_async m64nNk16`；sm100 版 `disco_fwd_dense_kpacked_tcgen05_blk_k`（`torch_harmonics/disco/optimized/kernels_cuda/disco_cuda_fwd_dense_kpacked_sm100.cu:80`）文件头 :37-55 对照表讲清唯一差异：wgmma→tcgen05.mma、累加器→TMEM、fence/commit/wait→mbarrier。共享底座 ptx.cuh 按 __CUDA_ARCH__ 条件编译；`gather_window_rt`（`torch_harmonics/disco/optimized/kernels_cuda/disco_cuda.cuh:84`）推导半字 gather 的 word 偏移：P=1 需 5 word、P=2 需 8 word。

## ③ 外部连接：与哪些子系统互依

向上，SFNO/S2UNet/S2Segformer 用它做主算子，`distributed/distributed_convolution.py` 包装做极向分片。`attention/` 是同一架构的第二次 instantiation——同一 ψ 邻域换 QK^T·V 聚合（见 03 篇）。

## ④ 数据流：一次典型调用的路径

以 H100、bf16、K=16 为例：构造期 Ψ 缓存命中 → COO → CSR → pack → blocked-CSR（K_pad=16）。forward 期六条件全过 → fused 路径进 autograd 域发射 sm90 WGMMA；反向域内重算换 K× 显存。

## ⑤ 设计决策：为什么这么设计

**为什么 Ψ 要三个形态？** 稠密 O(K·Ho·Hi·Wi) 只活在测试里；CSR 处处正确兜底；kpacked 用 16 字节对齐块布局换 tensor core 吞吐。

**为什么 build-time 与 device-time 判定分离？** kpacked buffer 原本 pad 到 NBR_PAD（`torch_harmonics/disco/convolution.py:624` 注释：极点行决定，半度 ~33MB、最高 ~274MB），模块常 CPU 构造后 .to(device)，构造期判设备会白丢内核；blocked-CSR 压缩后收回 ~2MB/~16MB。

**"TRIED AND REJECTED" 注释块**（`torch_harmonics/disco/optimized/kernels_cuda/disco_cuda_fwd_dense_kpacked_sm90.cu:97-137`）：五个被否方案全带实测数字（3.34 vs 3.13ms 等），"验证过位级一致才计时"；TMEM 对齐等 Blackwell 特有约束也是双代分文件的原因。

## ⑥ 新人提示：坑/入口/阅读顺序

- **阅读顺序**：`convolution.py:236` → `:705` 分派链 → `disco_optimized.py:92` → `_sm90.cu` 文件头（教材）。
- **kpacked 不生效先查六条件**：最常翻车的是 K_pad 不在 {8,16} 与 nlon_out 不被 8 整除；静默回退 CSR，只能靠 profiler 看内核名。
- **架构后缀 a 不能省**：sm_100a 的 a 是 arch-conditional 标记，普通 sm_100 编不出 feature 宏；Rubin 10.7 落 CSR。
