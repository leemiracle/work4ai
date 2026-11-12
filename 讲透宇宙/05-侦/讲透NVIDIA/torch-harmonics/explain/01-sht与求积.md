# 01 · sht.py / legendre.py / quadrature.py / fft.py——SHT 心脏与预计算缓存体系

> 源文件：`torch_harmonics/sht.py`（628）+ `torch_harmonics/legendre.py`（424）+ `torch_harmonics/quadrature.py`（643）+ `torch_harmonics/fft.py`（96），合计 1791 行。图谱（625 节点/1206 边@c66375cf）中 sht.py 是核心枢纽，DISCO/attention/分布式层/示例模型都落到这组原语上。

## ① 角色定位：这个子系统解决什么问题

球面没有平移不变性，普通卷积/FFT 定义不出来，出路是变到球谐系数域操作后再变回。分解很干净：**SHT = 经度 FFT × 余纬 Legendre 求积**，两轴解耦。`sht.py` 把两半拼成四个 nn.Module；`legendre.py` 生成关联 Legendre 表（含导数版），`quadrature.py` 提供四种求积网格，`fft.py` 是修正 pad/truncate 语义的薄包装。重活全在 `__init__` 预计算，forward 只剩一次 FFT + 一次 einsum。

## ② 内部结构：关键类/函数与行号锚

**四层 nn.Module 体系**：`RealSHT`（`torch_harmonics/sht.py:42`）→ `InverseRealSHT`（`torch_harmonics/sht.py:187`）→ `RealVectorSHT`（`torch_harmonics/sht.py:330`）→ `InverseRealVectorSHT`。标量对与矢量对同骨架，矢量版仅把表换成导数表、单收缩变四组实虚交叉 einsum。

**权重折叠与收缩排布**：构造期 `truncate_sht` 定 lmax/mmax（`torch_harmonics/sht.py:131`），2π 常数、求积权重、Legendre 表 einsum 合成单张 weights（`torch_harmonics/sht.py:140`），clm 因子（`torch_harmonics/legendre.py:41`）融入表内。权重布局 `(mmax, lmax, nlat)`，einsum `"...mk,mlk->...lm"`（`torch_harmonics/sht.py:178`）收缩维 k 两侧 stride-1；逆变换 permute 成 `(mmax, nlat, lmax)`（`torch_harmonics/sht.py:283`）让 l 落快速轴——系数 (l,m) 布局由此锚定。

**Legendre 主循环**（`torch_harmonics/legendre.py:139-174`）：三项递推流式生成——扇形种子递进、固定 l 的所有 m 向量化成单条算式、窗口只携前两度，工作集 O(m·k) 而非 O(m·l·k)；csphase 奇数 m 行取负。

**双入口缓存**：裸函数 `legpoly`/`dlegpoly` 接任意节点；缓存入口 `_precompute_legpoly`（`torch_harmonics/legendre.py:185`）按标量网格键缓存——docstring 自白（`torch_harmonics/legendre.py:203-208`）：**张量按 identity 哈希，同分辨率两层各建的等值节点张量无法互相复用**，改标量键后共享一张表。`dlegpoly` 输出读 m±1 与 l+1 邻值，先请求 halo 加宽表（`torch_harmonics/legendre.py:305`）。

**求积网格族**：`precompute_latitudes`（`torch_harmonics/quadrature.py:110`）分发 Gauss-Legendre/Lobatto/Clenshaw-Curtis/梯形四种规则，全在 cosθ 域构造再 `arccos`+flip，sinθ Jacobi 吸收进权重；`QuadratureS2`（`torch_harmonics/quadrature.py:508`）包成球面积分 Module；`irfft` 变换前把 DC/Nyquist 虚部置零强制 Hermitian（`torch_harmonics/fft.py:81-84`）。

## ③ 外部连接：与哪些子系统互依

向上 `spectral_convolution.py`、`disco/`、`attention/`、`distributed/` 与 examples 五模型全部 import 这四个文件。`compute_theta_cutoff`（`torch_harmonics/quadrature.py:169`）被 DISCO/attention 消费——网格最大间距决定局域算子支撑半径。

## ④ 数据流：一次典型调用的路径

以 `RealSHT(128,256)` 为例：构造期 `precompute_latitudes(128)` 命中缓存 → lmax=65、mmax=129 → 折叠合并成 `(129,65,128)` 权重 buffer。forward 先 `rfft(x, nmodes=mmax)` 沿经度（`torch_harmonics/sht.py:169`），transpose 使 nlat 落末维、实虚拆开，双 einsum 收缩出 `(...,65,129)`，complex 前强制 contiguous；反向全程原生可微，autograd 自动回传。

## ⑤ 设计决策：为什么这么设计

**为什么激进折叠权重？** 2π 常数、求积权重、Legendre 值、矢量版 `1/(l(l+1))` 因子全并进单张 weights——预计算是一次性成本，forward 是每步成本，折叠本身精确等价。

**为什么 forward 末尾死磕 contiguous？** `torch_harmonics/sht.py:181-184` 给出因果链：`...lm` 输出 l 是 stride-1、m 慢，inductor 的 aten.complex meta 预测连续布局，`torch.compile` 下触发 assert_size_stride；矢量版分量先在**实空间** stack 再做唯一一次 complex（`torch_harmonics/sht.py:482-483`），因为 complex cat 无法生成 Triton 内核。

## ⑥ 新人提示：坑/入口/阅读顺序

- **阅读顺序**：`legpoly` 递推 → 网格分发 → `torch_harmonics/sht.py:42` RealSHT 全文（其余三类的模板）。
- **截断规则会变**：v0.9.0 起 equiangular 默认 lmax 改 (nlat+1)//2，依赖旧默认须显式传 lmax；cuFFT 在 fp16/bf16 下还要求 nlon 是 2 的幂（`torch_harmonics/sht.py:96-107` 有标准写法）。
- **mmin/lmin/kmin 是分布式专用**：`torch_harmonics/legendre.py:194-197` 限制"存哪些"而非"算哪些"（递推必须从头走）；kmin/kmax 才是真省算——分片层靠它只建本 rank 表块。
