# MatX streaming 流式处理与 file_io：有状态分段执行

## 一、角色定位

`include/matx/streaming/`（5 头）解决"数据比显存大/数据是连续到达的"场景：把卷积、多相重采样、信道化三个有状态变换封装成流式对象——构造一次、反复 `feed()` 喂数据段、终了 `flush()` 冲出尾部。与一次性 transforms（要求整批数据在手）互补，面向雷达脉冲流、通信基带、实时信号。`file_io/`（2 头）则是持久化面：file_io.h 通用张量读写 + tiff.h 图像读取。

## 二、内部结构

### 2.1 底座：stream_detail.h 的两个原语

- `StreamSlicePlan`（stream_detail.h:47）：`{lo, cnt}` 输出窗口计划——一次 feed/flush 拥有哪些输出块。注释言明它"仅从尺寸计算（无段数据）"，因此 feed 可在跑段算子**之前**先验证输出缓冲，这是防御性设计。
- `SegmentLifecycleGuard`（:59）：RAII 卫兵，构造跑 PreRun（物化临时）、析构跑 PostRun，异常路径也不泄漏临时内存/半跑生命周期——把 BaseOp 的 PreRun/PostRun 协议（base_operator.h:276/:282）延伸到分段执行。

### 2.2 Conv1DStream：三模式共享一个因果引擎

conv1d_stream.h 头注释（:38-49）是权威设计文档：FULL/SAME/VALID 三模式不写三套代码，而是**同一 VALID 因果引擎 + 不同 skip/flush_len 配方**（:43 的表格：FULL 丢弃 0、flush_len=L-1；SAME flush_len=L-1-L/2 :135；VALID flush_len=0 :139）。构造期固定：`Conv1DStreamParams`（:83，含 `matxConvCorrMode_t mode` :91 默认 SAME），static_assert 限定 CUDA/host 执行器与 1D 滤波器（:112/:113）。工厂 `make_conv1d_stream<float>(h, {.mode=...}, exec)`（:436）。

核心 API：`index_t feed(const InOp&, OutTensor&)`（:244）——static_assert 链完备（1D 输入 :246、值类型匹配 :248、可写输出 :250/:252），已 flush 再 feed 抛异常提示 reset()（:256）；返回本次产出样本数。`index_t flush(OutTensor&)`（:335）补发尾部（:49 注释：`[retain | zeros(flush_len)]` 的补零卷积）。`reset()`（:323 一带）重启流。**输出缓冲 sizing 契约**：`max(new_len, flush_len_)`（:200）——feed 段长与 flush 尾长的较大者就是输出上界（:188-195 注释，Informational 口径，调用方不据它 resize，但缓冲必须 ≥ 它）。

### 2.3 ResamplePolyStream / ChannelizePolyStream

resample_poly_stream.h（类 :96）与 channelize_poly_stream.h（类 :94，477 行）同构：多相滤波器的流式化——重采样要跨段保持相位对齐（:122 注释讨论"前段样本窗口是否伸进新数据"），信道化按输出块（时间步）划分归属（channelize_poly_stream.h:42 注释"computing only the output blocks this feed owns"）。两者都有 OutputUpperBound 语义文档（resample :170、channelize :177-184）与工厂（channelize :470 `make_channelize_poly_stream`）。streaming.h 是汇总入口。

### 2.4 file_io：能读什么

file_io.h（367 行）提供张量二进制/文本读写；**甄别点**：CSV 读取的 cuDF 实现整段被注释保留（file_io.h:70-98 `read_csv` 注释体，:75 起函数签名被注释），编译期用 cuDF 但当前版本禁用——文档若宣称支持 CSV 读，以源码为准：走注释内的路径需自行解封并接 GetcuDF。tiff.h（模板 :78 一带）在 MATX_EN_NVTIFF 下读 TIFF 图像为张量。

## 三、外部连接

- **向上**：流式对象吃任意 BaseOp 段输入（feed 参数是 `const InOp&`，conv1d_stream.h:244——生成器/表达式皆可作段源）；
- **向内**：复用 kernels/conv.cuh 的 VALID 引擎（conv1d_stream.h:48 点名）、kernels/resample_poly.cuh 与 channelize_poly.cuh；
- **横向**：examples/streaming.cu 是官方用法示范；test/00_transform/StreamingConv/StreamingResample/StreamingChannelize 三测覆盖（文件名见目录）；examples/simple_radar_pipeline.cu 的连续脉冲处理是真实负载原型。

## 四、数据流

以 SAME 模式流式卷积为例：构造 `make_conv1d_stream(h, {.mode=SAME}, exec)` → 循环 `feed(chunk, out)`：StreamSlicePlan 算本段输出窗（lo/cnt）→ SegmentLifecycleGuard 起 PreRun → 保留态（前 L-1 样本）拼新段跑 VALID 卷积 → 丢弃前导 skip（:261 注释"drop the leading d"）→ PostRun → 返回产出数 → 数据终了 `flush(out)` 补 L-1-L/2 个尾样本 → 需要再来一条流就 reset()。全程只有用户缓冲 + 引擎保留态两个驻留内存，段长任意。

## 五、设计决策

1. **一引擎三模式**：VALID 引擎 + skip/flush_len 参数化消灭三份近重复代码，与一次性 conv 的模式语义精确对齐（:48 注释强调 s 与一-shot SAME 偏移一致）。
2. **异常安全优先**：SegmentLifecycleGuard 保证 throw 不留半跑状态；:323 注释连"flush 自身抛异常后如何 reset"都规定了。
3. **契约上界而非精确输出数**：输出数依赖相位/段长，库只承诺上界（:170/:177），把 resize 责任留调用方——避免每段同步查精确数的开销。
4. **一个对象一条流**（conv1d_stream.h:100）：执行器在构造期绑定，多流需多对象——状态隔离换线程安全推理的简单性。
5. **file_io 克制**：只保二进制/文本核心，CSV/cuDF 通路注释禁用——IO 面越窄，header-only 的依赖膨胀越小。

## 六、新人提示

1. feed 后检查返回值（本次产出数），输出张量按上界分配、按返回值截取使用；
2. 已 flush 再 feed 是错误（:256），要么 reset 重来要么新建对象；
3. 滤波器长度超过直接卷积上限会构造期抛异常（:116/:122 附近），大核考虑 FFT 卷积（examples/fft_conv.cu）；
4. 写新流式变换的最短路径：拷 conv1d_stream.h，替换段算子（feed 内的核心计算）与 flush_len 推导，StreamSlicePlan/Guard 直接复用；
5. 想读 CSV：先确认版本（file_io.h:75 注释体），当前需自己解封 cuDF 路径或宿主侧预转换。

*锚清单：stream_detail.h:47/59、conv1d_stream.h:38/41/43/48-49/80/83/88/91/95/100/105/107/112-113/116/122/126/128/130/135/139/180/188-195/200/207/214/224/244/246/248/250/252/256/259/261/323/335/436、resample_poly_stream.h:96/122/162/170-174、channelize_poly_stream.h:42/94/169/177-184/197/470/477、file_io.h:70/75/78/83/93-98、tiff.h:78、base_operator.h:276/282、examples/streaming.cu。*
