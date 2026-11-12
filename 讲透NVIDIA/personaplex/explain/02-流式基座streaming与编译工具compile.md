# 02 · streaming.py + compile.py：流式基座与低延迟编译工具箱

> 锚点基线：`moshi/moshi/modules/streaming.py`（630 行）、`moshi/moshi/utils/compile.py`（308 行）。前者是全模型分帧推理的"状态协议"，后者是 torch.compile/CUDA graph 的"驯服层"。

## ① 角色定位

`streaming.py` 定义了本仓所有可流式组件的统一 API：`StreamingModule`（streaming.py:262）。Mimi 的每一层卷积、每个 Transformer、乃至顶层的 `MimiModel`/`LMGen`，都继承它，靠"进入流式上下文→持有内部状态→逐帧喂入"的协议工作。没有这层抽象，全双工语音的 80ms 级延迟无从谈起。

`compile.py` 则解决另一个问题：逐帧推理时每步只有 1 帧张量，kernel launch 与编译开销占比极高。它提供 `torch_compile_lazy`（惰性编译）、`CUDAGraphed`（图捕获重放）与开关体系（`NO_TORCH_COMPILE`/`NO_CUDA_GRAPH` 环境变量），是服务端延迟的隐形功臣。两文件血缘不同（streaming.py 头上叠着 Kyutai 与 Meta audiocraft 双版权头，streaming.py:22-30），但服务里必须配合使用：状态在 CPU 侧管理，图在 GPU 侧重放。

## ② 内部结构

### streaming.py

- `Resetable` Protocol（streaming.py:47-49）：状态只需实现 `reset()`；`State = TypeVar("State", bound=Resetable)`（streaming.py:52）。
- `StreamingModule`（streaming.py:262-418）：核心三件——`_streaming_state` 槽位与 `_streaming_propagate` 开关（streaming.py:286-289）、`_apply_named_streaming` 递归遍历器（streaming.py:298-314，遇 `propagate=False` 的子模块即剪枝不深入）、抽象 `_init_streaming_state(batch_size)`（streaming.py:328-329）。
- 生命周期四入口：`streaming(batch_size)` 上下文管理器（streaming.py:334-342，退出自动置 None）、`streaming_forever(batch_size)`（streaming.py:331-332，**server.py:115-117 与 offline.py:226-228 的用法**——一次进入永不退出，靠 `reset_streaming()` 复位）、`reset_streaming()`（streaming.py:344-355）、`is_streaming` 属性（streaming.py:291-293）。
- 状态持久化五件套：`get_streaming_state`/`save_streaming_state`（safetensors 张量 + json 元数据双文件，streaming.py:357-391，经 `_flatten_streaming_state` streaming.py:195-229 递归展平）、`set_streaming_state`/`set_streaming_state_inplace`/`load_streaming_state`（streaming.py:232-259、393-418）——支持把一段对话状态存盘再热恢复。
- 三个具体示范组件：`StreamingAdd`（streaming.py:444-461，两条长度不同的残差支路按最小长度对齐相加，多出的尾部缓存到 `previous_x/previous_y`）；`RawStreamingConv1d`（streaming.py:472-511）；`RawStreamingConvTranspose1d`（streaming.py:522-570）。
- `RawStreamingConv1d.forward` 的步进算法：非流式直接父类卷积（streaming.py:487-488）；流式下先拼 `previous` 缓存（streaming.py:491-493），按 `num_frames = floor((T - kernel)/stride) + 1` 算出可出的完整帧（streaming.py:497），只送 `(num_frames-1)*stride + kernel` 长度进卷积（streaming.py:504-505），尾部 `input[..., offset:]` 留作下帧缓存（streaming.py:502）。kernel 已按 dilation 折算（streaming.py:486）。
- `RawStreamingConvTranspose1d` 的对偶：右端 `invalid_steps = kernel - stride` 个点会与下帧重叠，必须扣留为 `partial`（streaming.py:566-568）；下帧算完把 partial 加回，**带 bias 时要先减一份 bias** `out[..., :PT] += partial - self.bias[:, None]`（streaming.py:558-561），否则 bias 被计两次——这是全文件最精妙的一行。
- 文件尾自带等价性测试 `test()`（streaming.py:573-625）：kernel{1..16}×stride{1..9}×chunk{1,3,5,8} 全组合，流式分段输出与整段输出相对误差 ≤ 1e-6（streaming.py:618-619、624-625）。

### compile.py

- `no_compile()` 上下文（compile.py:45-55）+ 模块级 `_compile_disabled`（compile.py:42）：局部关编译。Mimi 的 SEANet 编解码器默认就在这个罩子里跑（compression.py:290-295 的 `_context_for_encoder_decoder`）。
- `torch_compile_lazy`（compile.py:58-75）：`NO_TORCH_COMPILE` 环境变量直接返回原函数（compile.py:62）；否则首次调用才 `torch.compile`（compile.py:71-72）——注释明言是为避免 Dora 场景下编译进程池污染 stderr（compile.py:59-61）。SEANet 的 `forward` 都用它装饰（seanet.py:260、413）。
- `Checkpoint`/`simple_checkpoint`（compile.py:78-166）：自研 activation checkpointing，兼容 FSDP 与 torch.compile（绕开 pytorch#97436，注释见 compile.py:145-147）；推理服务不用它，训练侧遗产。
- `CUDAGraphed`（compile.py:210-301）：核心类。`__call__` 先过三重闸（disable / 环境开关 / 已在图中，compile.py:244-245）；首次捕获前先空跑 `warmup_steps` 次让 torch.compile 完成（compile.py:293-295）；捕获时 `_clone_tensors` 复制入参保证独占（compile.py:286-289），捕获后立刻 `replay()` 让它真正执行（compile.py:290-291）；稳态路径 `_match_values_copy_tensors` 逐参校验形状/标量值后把新数据拷进静态入参再 replay（compile.py:255-279、296-301）。命名参数一律拒绝（compile.py:242-243）。
- 工厂 `cuda_graph(func, warmup_steps)`（compile.py:304-308）；`asdict()` 返回空 dict（compile.py:238-239）——**这是为了让 CUDAGraphed 也能装进 streaming state 的展平协议**，妙手。

## ③ 外部连接

- `streaming()` 上下文的三个活跃消费者：server.py:115-117 与 offline.py:226-228 的 `streaming_forever`（Mimi×2 + LMGen），以及 lm.py:1142 的 `with lm_model.depformer.streaming(B)`——Depformer 每个时间步进出一次上下文，状态即用即弃。
- `CUDAGraphed` 的三个消费点：lm.py:720-722（`graphed_main`=主 Transformer 前向、`graphed_embeddings`=嵌入回放、`graphed_depth`=Depformer 单步）；compression.py:228-230（Mimi 编解码侧的 `encoder_transformer`/`decoder_transformer`，非 cuda 设备自动 disable）。
- `RawStreamingConv1d/ConvTranspose1d` 被 conv.py:146-148/170-172 的 `NormConv1d/NormConvTranspose1d` 包一层 weight_norm，再被 seanet.py/resample.py 组网；`StreamingAdd` 只在 SEANetResnetBlock 的残差汇合处使用（seanet.py:98、114-115）。
- 环境开关消费链：`docker-compose.yaml:9` 注入 `NO_TORCH_COMPILE=1` → compile.py:62 生效 → 容器部署里 torch.compile 整体关闭，只剩 CUDA graph 在扛延迟。

## ④ 数据流

以一帧 1920 样本 PCM 进 Mimi 编码器为例：`MimiModel.encode` → SEANet 各级 `StreamingConv1d.forward`（conv.py:253-275）：流式分支首帧由 `state.padding_to_add` 注入因果左 padding（conv.py:272-274），随后交给 `RawStreamingConv1d`：拼接 previous 缓存 → 算 num_frames → 卷积 → 尾部落回缓存（streaming.py:491-511）。逐层下采样后到 RVQ/Transformer，后者同理用自己的 streaming state。整个链条里"状态"沿 `_apply_named_streaming` 的命名树生长：`reset_streaming()` 一次调用即可让全树复位（server.py:265-267 每会话开始时对三个组件各调一次）。

CUDA graph 侧的数据流是"静态缓冲区复制"：调用方每帧把新张量交给 `CUDAGraphed.__call__` → 拷进捕获时的 `_args` 原地 → `graph.replay()` → 返回捕获时的 `_output`（同一块显存，内容已更新）。形状一变即 ValueError（compile.py:266-269），`reset()` 可强制重捕获（compile.py:230-236）。

## ⑤ 设计决策

- **状态协议而非张量协议**：`StreamingModule` 只约定"有状态、可复位、可命名传播"，不约束状态内容（dict/dataclass/嵌套皆可，streaming.py:112-119 分派）。这让卷积缓存、KV cache、LMGen 的环形 token cache 能共用一套进入/退出/复位/持久化机制。
- **propagate 剪枝**：`set_streaming_propagate(False)` + 子模块自管生命周期（lm.py:348 对 Depformer 设 false），父模块 `_apply_named_streaming` 就不会重复初始化它——Depformer 的状态以"每步一个独立序列"存在，与主干的"一条长流"语义不同，必须切开。
- **图捕获与流式状态解耦**：CUDA graph 捕获的是无状态前向计算，流式状态在图外由 Python 持有，每步以拷贝方式喂图。代价是每次 replay 前的逐参校验（compile.py:255-279），收益是图永不失效、状态可以随便 reset。
- **`streaming_forever` + `reset_streaming` 的组合**：比反复进出上下文省掉了状态重建（KV cache 张量反复分配释放会打爆 allocator），服务端只需在会话边界复位——这是长服务进程的正确姿势。

## ⑥ 新人提示（坑与勘误）

1. **`stride > kernel_size` 直接断言失败**（streaming.py:476-478、529-531）：上/下采样比率设计时必须满足 `stride <= kernel`，否则缓存逻辑不成立。SEANet 全程用 `kernel = 2*ratio`（seanet.py:231/365），天然安全。
2. **ConvTranspose 的 bias 双计陷阱**：自己复刻流式转置卷积时，忘记 streaming.py:559 的 `- self.bias[:, None]` 修正，输出会在重叠帧上系统性偏移一个 bias。
3. **`StreamingContainer` 的 `_NullState`**（streaming.py:421-431）不代表"无状态"，而是"容器自身无状态、子模块各有状态"——SEANetEncoder/LMModel 都是它。
4. **CUDAGraphed 不支持 kwargs**（compile.py:242-243）也不支持嵌套结构入参；给被图化的函数加参数必须同步改所有调用点，且标量参数值改变会触发 `source != target` 校验失败（compile.py:276-279）——LMGen 把温度/top_k 放在 `self` 上、`sample_token` 在图外调用，正是为了绕开这一限制。
5. **`NO_TORCH_COMPILE=1` 是 Docker 默认**（docker-compose.yaml:9）：容器里 SEANet 的 `@torch_compile_lazy` 全部退化为裸函数，性能调优别在容器外测完就外推。
6. streaming.py 的 `save/load_streaming_state` 在本仓**没有任何调用方**（grep 实证）——是上游 Kyutai 为对话状态持久化预留的能力，在本发行版里是休眠资产，可作二次开发切入点。
