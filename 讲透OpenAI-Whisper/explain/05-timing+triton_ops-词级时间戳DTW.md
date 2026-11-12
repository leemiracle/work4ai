# 05 · timing.py + triton_ops.py：词级时间戳与 DTW 对齐

## 角色定位

timing.py（388 行）实现论文 3.6 节的**词级时间戳**：给定一个 30 秒窗已生成的 token 序列，为其中每个词算出秒级 start/end。triton_ops.py（117 行）是其中两个数值热点的 CUDA 加速版。触发条件只有一处——`transcribe(word_timestamps=True)`（whisper/transcribe.py:50,401-411）。注意任务书写 "timing+dtw"：dtw 不是独立文件，dtw_cpu/dtw_cuda/dtw 三个函数都在 timing.py 内（whisper/timing.py:82,108,141），配合 tests/test_timing.py 的手写 DP 对照验证。

这是全仓数值上最精巧的部分：**它从训练好的模型里"偷"出对齐信息**——不微调、不额外标注，靠交叉注意力的 QK 权重矩阵 + 动态时间规整（DTW）完成文本-音频对齐。

## 内部结构

**timing.py 四个层次**：

1. **基础设施**：`median_filter`（whisper/timing.py:19-54）沿时间维中值滤波，CUDA 先试 triton、失败告警回退到 `unfold+sort` 的 PyTorch 实现（whisper/timing.py:36-49，注释引 PyTorch issue 51450：sort 比 torch.median 快）；`WordTiming` dataclass（whisper/timing.py:154-160）承载 word/tokens/start/end/probability 五元组。
2. **DTW 三件套**：`backtrace`（whisper/timing.py:57-79，numba jit）从 trace 矩阵回溯路径；`dtw_cpu`（whisper/timing.py:82-105，`@numba.jit(nopython=True, parallel=True)`）标准双循环 DP，代价取三邻居最小；`dtw_cuda`（whisper/timing.py:108-138）先把矩阵**斜置 skew** 成 (N+M, M) 布局（whisper/timing.py:114-117），使同一条反对角线上的元素内存连续，然后一个块按 k=i+j 逐对角线推进；`dtw` 调度器按 x.is_cuda 分发并兜底（whisper/timing.py:141-151）。
3. **find_alignment（whisper/timing.py:163-242）核心算法五步**：
   - 构造重解码序列 `[sot_sequence, notimestamps, text_tokens, eot]`（whisper/timing.py:176-183）——用 without_timestamps 模式重跑一次前向；
   - 对解码器每层 cross_attn 装 forward hook 抓 QK 权重（whisper/timing.py:186-192，lambda 闭包用 `index=i` 惰性捕获修正常见坑）；在 `disable_sdpa()` 上下文里执行（whisper/timing.py:194-197），因为 SDPA 快路径不返回注意力权重（whisper/model.py:131-135），必须强制手写路径（whisper/model.py:137-144）；
   - 同一次前向顺带取每个 text token 的生成概率（whisper/timing.py:198-201，供词级 probability 字段）；
   - 权重后处理：按 alignment_heads 稀疏索引抽头（whisper/timing.py:207）、截到 num_frames//2（whisper/timing.py:208，音频 token 是 mel 帧一半）、softmax 后按 token 维标准化再中值滤波（whisper/timing.py:209-212）、对头取平均得 text×audio 矩阵（whisper/timing.py:214-215）；
   - `dtw(-matrix)` 对负矩阵规整（负号使"最大化注意力"变"最小化代价"，whisper/timing.py:216），jumps 检测 text_indices 中文本边界跳变处取音频时间（whisper/timing.py:228-231），`split_to_word_tokens`（whisper/timing.py:218，见 tokenizer 篇）把 token 聚成词，按词边界切 start/end（whisper/timing.py:226-235）。
4. **后处理**：`merge_punctuations`（whisper/timing.py:245-276）双向扫描把孤立标点并回前后词；`add_word_timestamps`（whisper/timing.py:279-389）是唯一被 transcribe 调用的入口——调 find_alignment 后做两轮"hack"修正：词长超 2×中值时在句读边界截断（whisper/timing.py:309-317，注释自认应由 VAD 替代，whisper/timing.py:307-308），段首/段尾词与 segment 级时间戳互相校准（whisper/timing.py:364-384），最后把 words 数组写回每个 segment（whisper/timing.py:388）。

**triton_ops.py 两件套**：`dtw_kernel`（whisper/triton_ops.py:13-40）单 block 沿反对角线 k 迭代、`tl.debug_barrier()` 保证块内同步（whisper/triton_ops.py:21）、trace 按三邻居比较写 0/1/2（whisper/triton_ops.py:38-40）；`median_kernel`（whisper/triton_ops.py:43-103）是**源代码生成魔术**——模板 kernel 里埋 `LOAD_ALL_ROWS_HERE`/`BUBBLESORT_HERE`/`MIDDLE_ROW_HERE` 三个占位符，按 filter_width 动态替换成逐行加载与完整冒泡排序网络（whisper/triton_ops.py:62-95），再 `_unsafe_update_src` 热替换 JIT 源码（whisper/triton_ops.py:97-101）。`median_filter_cuda`（whisper/triton_ops.py:106-117）做包装。

## 外部连接

- 上游：transcribe.py 的 word_timestamps 分支（whisper/transcribe.py:401-411）；幻觉静音跳过也依赖词级时间（whisper/transcribe.py:419-472）。
- 对 model.py 的深度依赖：alignment_heads buffer（whisper/model.py:279-292 注入）、cross_attn 的 hook 点（whisper/model.py:156-159）、disable_sdpa 开关（whisper/model.py:71-78）——**没有 model.py 的这三处配合，词级时间戳无法实现**。
- 对 tokenizer.py：split_to_word_tokens 的中文 Unicode 切词（whisper/tokenizer.py:277-284）。
- 对 audio.py：`TOKENS_PER_SECOND=50` 把音频 token 序号换算成秒（whisper/timing.py:229、whisper/audio.py:22）。
- 测试：test_timing.py 用手写 DP 与 dtw_cpu 对照回溯路径。

## 数据流（一个 30s 窗）

```
segment tokens（已生成）+ mel_segment
→ 重解码 [sot…notimestamps, text, eot]         whisper/timing.py:176-197
→ hooks 收集 L 层 cross_attn QK (heads,n,1500)  whisper/timing.py:186-192
→ 选头/截半/标准化/中值滤波/头平均 → (n,1500)    whisper/timing.py:207-215
→ dtw(-matrix) → text_indices,time_indices     whisper/timing.py:216
→ 词边界 jumps → 每词 (start,end,probability)   whisper/timing.py:226-242
→ merge_punctuations + 时长 hack 校准           whisper/timing.py:319,309-317
→ segment["words"]=[{word,start,end,probability}…] whisper/timing.py:388
```

## 设计决策

1. **复用交叉注意力而非训练对齐头**：对齐信息本来就在注意力里，只需选对头（alignment_heads 以 base85 压缩存进 __init__.py:36-51，逐模型不同——这些头是 OpenAI 离线挑出的与时间对齐高相关的头，whisper/__init__.py:34-35 注释）。
2. **SDPA 与可解释性不可兼得**：快路径丢弃注意力权重，于是 disable_sdpa 作为逃生舱（whisper/model.py:71-78）——性能与可观测的经典权衡。
3. **DTW 反对角并行是教科书级并行化**：依赖只在 i-1/j-1/i-1,j-1，按对角线波前推进零同步开销；skew 布局让波前内存连续。
4. **CUDA kernel 源码生成**：filter_width 是编译期常量，用字符串替换生成展开的冒泡网络——丑但快，且 `lru_cache` 保证每宽度只生成一次（whisper/triton_ops.py:43）。
5. **所有 hack 都留了注释承认是 hack**：句读截断与段界校准（whisper/timing.py:307-308,344-345）两处都写明"应由基于 VAD 的更好分段取代"——诚实的技术债标记。

## 新人提示

- 词级时间戳不准时的调参顺序：medfilt_width（默认 7，whisper/timing.py:170）→ qk_scale（默认 1.0）→ 检查模型是否官方（本地模型用默认后半层头，whisper/model.py:279-283，精度会差）。
- CPU 上 word_timestamps 慢是正常的：DTW 双循环 + 每窗额外前向；triton 只救 CUDA。
- tests/test_timing.py 的手写 DP 是理解 DTW 回溯的最短路径，30 行。
- 不要在 SDPA 开启时试图自己抓注意力权重——qk 会是 None（whisper/model.py:135），这是最常见的新人坑。

## 勘误

1. 任务书称 "timing+dtw" 暗示 dtw 独立文件：实际 dtw_cpu/dtw_cuda/dtw 全在 timing.py（whisper/triton_ops.py 只有 CUDA kernel，无 Python 端 dtw）；本篇按源码归并。
2. `dtw_cuda` 断言 `M < BLOCK_SIZE=1024`（whisper/timing.py:108,111-112）——调用点 `dtw(-matrix)` 的 matrix 是 text×audio 布局，故 M=文本 token 数；一窗转写文本超过 1024 token 时 CUDA 路径会触发断言——**词级时间戳对超长窗口有隐性 1024 文本 token 上限**，docstring 未提。
3. 图谱摘要称 timing 的 median_filter "CPU 用 numpy 堆滑窗"：实现是 torch unfold+sort（whisper/timing.py:49），numpy 仅用于 DTW 矩阵回溯后处理，摘要不准。
