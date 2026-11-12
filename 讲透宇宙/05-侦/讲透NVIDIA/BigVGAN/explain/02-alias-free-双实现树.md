# 02 · alias_free_activation——双实现树（torch 纯净版 vs CUDA JIT 版）

## 角色定位

`alias_free_activation/` 是 BigVGAN 论文名字里 "alias-free" 的代码实体：一维激活的抗混叠包装（上采样→激活→下采样），改编自 junjun3518/alias-free-torch（Apache 2.0，torch/__init__.py:1）。树内两套实现共享同一接口 `Activation1d`：`torch/` 纯 PyTorch 可训练版与 `cuda/` JIT 编译的 fused 推理加速版，由 `use_cuda_kernel` 开关切换——这是"同一算子、两种实现、显式降级"的教科书结构。

## 内部结构

**torch 树三件**（共 ~230 行）：
- `torch/act.py:8` Activation1d：`UpSample1d(2)→act→DownSample1d(2)`（act.py:25-28），up/down_kernel_size 默认 12。
- `torch/filter.py`：`kaiser_sinc_filter1d`（filter.py:30-62）按 Kaiser 公式估 β（A>50/≥21/else 三档，filter.py:38-44）、`sinc` 条件定义（torch≥1.10 用内置，filter.py:9-24）、`LowPassFilter1d`（filter.py:65，replicate padding + 分组卷积 forward，filter.py:94-99）；滤波器经 `register_buffer` 持久化（filter.py:91）。
- `torch/resample.py`：UpSample1d 用 `conv_transpose1d` 补零上采样（resample.py:33-35）+ cutoff=0.5/ratio 低通（resample.py:23-25）；DownSample1d 直接复用 LowPassFilter1d 带 stride（resample.py:48-53）。

**cuda 树四件**：
- `cuda/activation1d.py:11` 模块级 `load.load()`——**import 即 JIT 编译**，这是全树最大的副作用。
- `FusedAntiAliasActivation`（activation1d.py:14-32）autograd 包装，`backward` 直接 `raise NotImplementedError`（activation1d.py:31）。
- `cuda/activation1d.py:35` 的 Activation1d 与 torch 版同构，多 `fused` 开关（activation1d.py:43）：False 回退纯 torch 组合（activation1d.py:55-59），True 走 fused（activation1d.py:74-76）。
- `cuda/load.py`：apex 式 JIT——清空 `TORCH_CUDA_ARCH_LIST` 防重编（load.py:11-14）、nvcc 版本探测（load.py:68-78）、CUDA≥11 加 sm_80（load.py:20-23）、固定 build 目录缓存（load.py:26-28）、`--use_fast_math` + half 宏（load.py:39-55）。`.cu` 内核 warp shuffle 做滤波累加（anti_alias_activation_cuda.cu:44 起），类型分派 `DISPATCH_FLOAT_HALF_AND_BFLOAT`（.cu:232）。

## 外部连接

bigvgan.py:19 静态导入 torch 版作默认；bigvgan.py:96/196/274 在 `use_cuda_kernel=True` 时**函数体内**延迟导入 cuda 版——不触发编译，保证无 nvcc 环境可跑。tests/test_activation.py:23-57 与 test_activation_snake_beta.py 做两实现一致性（差 ≤1e-3）。

## 数据流

torch 路径：`x [B,C,T]` → pad→conv_transpose1d(2x)→裁剪 → snake(x) → 低通 stride 2 卷积。fused 路径关键换算（activation1d.py:60-76）：kernel 内已烘焙 `expf`，线性 scale 的 alpha/beta 传参前取 log（activation1d.py:68-72）；Snake 无 beta，用 alpha 充当（activation1d.py:61-66）；上/下滤波器 buffer 直接传给 kernel（activation1d.py:74-76）。

## 设计决策

① kernel 硬编码 filter=12/replicate pad/logscale 三假设，docstring 直言"超参不同结果错误"（activation1d.py:16-18）——用专用换速度；② fused 只做 forward，训练永远走 torch 树；③ load.py 模块级副作用是双刃：首次 import 编译数分钟，build 目录缓存后秒级；④ 同名类+同签名让两树在 AMPBlock 内可无缝互换。

## 新人提示

排查"import 卡住/报 ninja 错"先看 cuda/activation1d.py:11；比对数值差跑 tests/test_activation.py；改 up_kernel_size 等超参时记得 fused 路径不适用。A100 上 fused 提速 1.5-3x（demo/app.py:281），速度表在 README.md:229-252。
