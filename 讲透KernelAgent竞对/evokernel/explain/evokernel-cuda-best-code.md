# EvoKernel CUDA best_code 深解：两例 NCU 引导迭代的最终存活者

> 对象：`ops-attention-cuda-ncu/10_AdaptiveAttention/best_code.py`（466 行）与 `ops-kernelbench-cuda-ncu/100_ConvTranspose3d_Clamp_Min_Divide/best_code.py`（353 行）。各配 `result.json` 一份。

## 一、角色定位："best" 意味着什么

EvoKernel 的 CUDA-NCU 两个目录（79 个 attention + 250 个 KernelBench）不是一次性生成的静态答案，而是**迭代 NCU 引导选优过程的最终导出快照**。`result.json` 里的 `outer_iter` 是关键证据：

- 10_AdaptiveAttention：`outer_iter: 26`，`inner_iter: 1`，compiled/correctness 双 true，mean=9.492ms（5 trials，std=0.019，波动仅 ±0.3%）；
- 100_ConvTranspose3d_Clamp_Min_Divide：`outer_iter: 27`，mean=20.949ms（std=0.014，波动 ±0.15%）。

即：这两个 kernel 分别是**第 26 轮与第 27 轮外层迭代后仍存活、通过正确性校验、性能进入稳态的版本**。同目录 manifest 汇总显示 attention 集正确率 97.5%（77/79）、KernelBench 集 100%（250/250），说明"存活"是硬门槛而非默认结局。`best_code.py` 中残留的注释（如 "v3 improvements over baseline"、"Improvements vs baseline"）就是历代变体的层积化石——代码里能直接读到选择压力的痕迹：每个变体都带着上一轮 NCU 反馈催生的针对性修改（注释自述动机），淘汰者不导出。5 次试验的极小 std 还说明导出时性能已收敛，不是碰运气的单点峰值。

## 二、代码解剖

### 例 A：10_AdaptiveAttention（466 行）

**load_inline 结构**（L366-375）：`cpp_sources` 只放声明（L361-364），`cuda_sources` 放实现，`functions=["attn_fwd_gqa_kvhead_cuda"]` 导出单入口；编译旗标 `--use_fast_math -O3`。扩展名 `custom_adaptive_attention_ops_kvhead_v3_db` 中的 `v3_db`（double-buffer）就是迭代编号的物证。

**宏定义**（L27-30）：`CHECK_CUDA/CHECK_CONTIGUOUS/CHECK_FLOAT32` 三合一的 `CHECK_INPUT`——严格的三前置校验，这解释了 79 例中仅 2 例 correctness 失败的高通过率从入口就守住。

**双核函数分派**：
1. **D==64 快速路径** `gqa_kvhead_warp64_q2_fwd_f32_kernel`（L60-161，模板参数 `WARPS_PER_BLOCK`）：每 warp 处理 **2 条 query**（pair_row 解码 L82-89），32 lane 各管 head_dim 中的 2 维（`d0 = lane*2`，L101）。零共享内存、零 `__syncthreads()`——一行注释（L12-13）点明这是为了摊薄 K/V 加载并消掉屏障。在线 softmax（L131-149）每 j 步用 `fmaxf/__expf` 更新 running max m 与归一因子 l。
2. **通用回退路径** `gqa_kvhead_flash_db_fwd_f32_kernel`（L164-293）：双缓冲共享内存平铺（K0/V0/K1/V1 四段布局，L174-179），`load_tile` lambda（L213-223）先把下一 tile 预取进另一缓冲，再算当前缓冲——经典的 ping-pong 流水。

**launch 配置**（L318-355）：快路径 grid=(ceil(pair_rows/4), 1, Hkv)、block=128、smem=0；回退路径 grid=(ceil(rows/4), ceil(D/32), Hkv)、smem=4×16×D×4B。两核都挂 `__launch_bounds__(32*WARPS, 2)`（L61/L165）钉住每 SM 至少 2 block 的占用意图。

**Python 侧**（L378-466）：`GroupedQueryAttentionNew` 保持与参照完全一致的投影层；关键设计是 dropout 分叉（L410-417）——训练+dropout 时**退回 PyTorch 参照语义**（repeat_interleave + 两.matmul），推理路径才进 CUDA 核。`ModelNew` 的 router/动态批处理逻辑逐行复刻参照。

### 例 B：100_ConvTranspose3d_Clamp_Min_Divide（353 行）

**load_inline 结构**（L309-318）：导出双函数 `clamp_min_divide_cuda`（out-of-place）与 `clamp_min_divide_inplace_cuda`；扩展名 `..._v5_ilp_occ_nocontig` 直接编码了第 5 版的三个卖点：ILP、occupancy、免强制 contiguous。

**核函数四件套**：vec4 原地/非原地（L36-104，`float4` reinterpret + 2 路 unroll）+ 标量原地/非原地（L110-169，4 路 unroll 尾循环兜底）。

**launch 配置**（L171-206）：`pick_threads` 按规模选 128/256；`pick_blocks_occupancy` 用 `cudaOccupancyMaxActiveBlocksPerMultiprocessor` **在运行时查询设备**后取 [2,8] blocks/SM × SM 数，再被 `need`（元素覆盖）与 65535 上限夹逼——网格大小是设备函数而非硬编码。宿主侧（L208-258）做 16B 对齐 + n%4 检查（L235-237）决定 vec4/标量分派；除法预先换成乘 `1/divisor`（L225）。Python 侧（L345-353）优先走 in-place（conv 输出是新张量，inplace 安全），非常量布局才降级。

## 三、优化手法清单（逐条对行）

**例 A**：
1. **warp shuffle 归约**：`warp_reduce_sum`（L34-38）5 级 `__shfl_down_sync`，加 L125-126 `__shfl_sync` 广播回 lane0；
2. **向量化加载**：`ldg_f32x2` float2 + `__ldg` 只读缓存（L48-58，`__CUDA_ARCH__>=350` 条件编译），L103-105/117-118 使用；
3. **2-query-per-warp 摊薄**：一次 K/V 加载喂两条 query 的 dot（L120-121）；
4. **在线 softmax**（FlashAttention 式流式更新，L131-149），配 `#pragma unroll 1`（L112）刻意阻止编译器展开 j 循环以省寄存器；
5. **双缓冲共享内存平铺 + 预取**（L231-288）；
6. **float4 向量化 dot**（vec4_ok 分支 L256-264）；
7. **`__launch_bounds__` + 小 JTILE=16 提占用**（L337-338 注释自述）；
8. **除法换乘法 + 1e-9 防零**（L152/L157/L291）。

**例 B**：
1. **float4 向量化**（L46/L80 reinterpret）；
2. **ILP unroll**：vec4 每迭代跨 2×stride（L48-66），标量 4 路（L121-136）；
3. **grid-stride 循环**（L44-48 等）适配任意规模；
4. **occupancy 感知网格**（L177-198）；
5. **kernel 融合**：clamp_min+divide 融成单 kernel 单 launch（L11 注释明言 "no tail kernels"）；
6. **省除法**（mul=1/divisor）与**免无条件 contiguous 拷贝**（L218）；
7. **in-place 就地写**省一次全量显存读写。

两例共享的元手法：`--use_fast_math`+`-O3`、`__restrict__` 全量标注、宿主侧强校验。

## 四、与 pytorch-references 的对应关系

`pytorch-references/` 是任务的"考卷"，best_code 是"答卷"，接口契约严格对齐：

- **Attention/10_AdaptiveAttention.py**（152 行）：`GroupedQueryAttention` 用 `repeat_interleave` 把 KV 头扩展到 Q 头数再两 `torch.matmul` + `softmax`——best_code 的核心命题正是**消灭这次物化**（L8 注释 "without K/V expansion"）；Model 的 router（mean pooling→MLP→argmax→动态批分组）被逐行保留，保证数值路径等价、dropout 分支显式回退到参照实现。
- **KernelBench/level2/100_ConvTranspose3d_Clamp_Min_Divide.py**（35 行）：`ConvTranspose3d → torch.clamp(min) → x/divisor` 三步；best_code 保留 conv 本体交给 cuDNN，只把后两步 epilogue 融合进单 CUDA kernel。命名约定（ModelNew、get_inputs/get_init_inputs、模块签名）与参照一一对应，这是 KernelBench 式评测能直接替换调用的前提。

## 五、竞对启示：跨硬件迁移实验素材（技术事实）

这两份 best_code 是**经 NCU 引导、26/27 轮迭代、正确性收敛的成熟 CUDA 实现**，技术上具备作为跨硬件迁移实验素材的完整属性：(1) 每个优化点都带行号可定位、可单独拆除——例如把例 A 的双缓冲退化成单缓冲、或把例 B 的 vec4 路径禁用，即可构造"降级变体"；(2) 它们的优化决策依赖 CUDA 特有原语（warp shuffle、`__ldg`、float4 16B 对齐、occupancy API），迁移到其它编程模型时哪些能映射、哪些必须重写，本身就是可测的命题；(3) `result.json` 给出了 CUDA 侧的稳态性能锚点（9.492ms / 20.949ms，std<0.02），任何迁移后实现都有可直接对照的基线。同仓另有 910B（Ascend NPU）版本的同名任务目录，天然构成同任务双栈素材。与 oracle 真值表的关系由主会话补充，此处仅陈述技术事实。

## 六、新人提示

1. **先读 result.json 再读代码**：outer_iter 告诉你这份代码经历了多少轮选择压；extension name 里的版本后缀（v3_db/v5_ilp）是迭代史的活化石。
2. **例 A 的精华在分派结构**：D==64 特化 + 通用回退的双路径是"为最常见形状写专用核、为长尾保通用核"的范式模板，别只盯着快速路径。
3. **注意语义保真的边界处理**：has1 边界（L89/L106）、dropout 回退（L410）、1e-9 防零——这些"不起眼"的行正是 correctness=true 的真正来源。
4. **例 B 教的是工程成熟度**：对齐检查、规模分档、运行时 occupancy 查询、in-place 安全性论证，全是可直接抄进自己 kernel 的护栏代码。
5. **警惕 `--use_fast_math`**：两例都开了，`__expf` 快但有精度代价；做数值对齐实验时要意识到这一点。
6. 这些代码是 NCU 引导搜索的产物而非人写范本——偶尔有"防御性冗余"（如例 A L249 计算前仍 sync 一次），读时区分"必要同步"与"保险同步"。
