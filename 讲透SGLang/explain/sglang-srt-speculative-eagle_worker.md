# 深度解析：`python/sglang/srt/speculative/eagle_worker.py`

> 源码: python/sglang/srt/speculative/eagle_worker.py @ commit ec075d8bc

EAGLE（Extrapolation Algorithm for Greater Language-model Efficiency）投机解码的核心思想是：用一个极轻量的 draft 模型（单层 decoder + 动态获取 target 的 hidden states）自回归地"猜"出 k 个候选 token。与朴素链式猜测不同，EAGLE 每一步保留 top-k 个分支，最终把所有分支按累积概率选出一棵**草稿树**（draft tree），再让 target 模型**一次 forward** 并行验证整棵树（通过 tree mask 让每个候选只 attend 自己的祖先链），从树根出发取**最长被接受的路径前缀**。

每轮 decoding 至少产出一个由 target 亲自采样的 bonus token，因此输出分布与不投机时完全一致（lossless）——收益公式是「一次 target forward 换 E[接受数]+1 个 token」。

在 SGLang 的架构中，`EAGLEWorker` 是投机解码的**总指挥**：
- 它继承自 `TpModelWorker`（即它自己就是一个跑 draft 模型的 TP worker），同时持有 `target_worker` 引用；
- 把「draft 多步建树 → target 树验证 → draft 状态重整（extend）」编排成一个完整的 `forward_batch_generation`；
- Scheduler 启动时用 `spec_algorithm.create_worker()` 造出它并直接以 `self.model_worker = self.draft_worker` 挂载（`scheduler.py:754-777`），所以调度器对投机解码完全无感——所有批次的 forward 都先进这个文件。

注意：本文件是 **v1（非 overlap schedule）** 路径；当 overlap schedule 开启时（默认），`create_worker` 会分派到 `eagle_worker_v2.py` 的 `EAGLEWorkerV2`（`spec_info.py:206-214`），但三阶段编排逻辑同源，v1 是理解全部 EAGLE 系实现的基线。

---

## 一、核心类与函数

### 1.0 文件地图（方法速查）

| 方法 | 行号 | 职责 |
|---|---|---|
| `__init__` | L98 | 双模型装配、权重共享、backend/图初始化 |
| `init_attention_backend` | L254 | draft 的 decode/extend 两套 attention backend |
| `init_cuda_graphs` | L273 | draft 多步图 + draft-extend 图捕获 |
| `apply_runtime_state` | L320 | 自适应投机：热切换 (steps, draft_tokens) |
| `build_adaptive_runtime_state` | L353 | 预捕获一组配置的完整组件 |
| `forward_batch_generation` | L450 | **总入口**：extend/decode 两条编排路径 |
| `forward_target_extend` | L559 | 阶段⓪：target prefill（capture FULL hidden） |
| `_draft_preprocess_decode` | L593 | 阶段①前置：draft KV scratch 分配 |
| `_draft_preprocess_idle` | L732 | idle 批的空输入安装 |
| `draft` | L746 | 阶段①编排：多步建树 + 建树 kernel |
| `draft_forward` | L836 | 阶段①循环体：steps 次自回归（cuda 图本体） |
| `verify` | L928 | 阶段②编排：TARGET_VERIFY + 采样验证 |
| `_mamba_verify_update` | L1019 | 混合架构的 mamba 状态回拨 |
| `forward_draft_extend` | L1101 | 阶段③（prefill 变体）：draft prefill + 输入轮转 |
| `forward_draft_extend_after_decode` | L1141 | 阶段③：验证后 draft 重整（三段式） |
| `capture_for_decode` | L1267 | softmax+topk 结果写回 EagleDraftInput |
| `update_weights_from_tensor` | L1274 | 权重热更新（draft 先、target 后） |
| `get_last_loc_large_page_size_top_k_1` | L1293 | 大页 topk=1 的末槽定位（torch.compile） |

### 1.1 `EAGLEWorker(TpModelWorker)` 类总览（L96）

一个 worker，两份模型权重，三个执行阶段：

| 阶段 | 模型 | ForwardMode | 本文件入口 |
|---|---|---|---|
| ① draft 建树 | draft（`self.model_runner`） | `DECODE`（每步 bs×topk 个 token） | `draft()` / `draft_forward()` |
| ② target 验证 | target（`self.target_worker`） | `TARGET_VERIFY` | `verify()` |
| ③ draft 重整 | draft | `DRAFT_EXTEND` | `forward_draft_extend*()` |

三个控制全行为的超参（L112-114）：
- `speculative_num_steps`（下文记 `steps`）：draft 自回归步数；
- `speculative_eagle_topk`（`topk`）：每步保留的分支数；
- `speculative_num_draft_tokens`（`draft_token_num`）：树的总节点数 = 每轮验证的 token 数（含 1 个 bonus token）。

三者需满足 `draft_token_num ≤ steps × topk² + 1` 的候选池约束。模型未显式指定时由 `ServerArgs.auto_choose_speculative_params` 自动选取：
- LlamaForCausalLM 默认 `(steps=5, topk=4, draft_token_num=8)`；
- DeepSeek / GptOss / GLM-MoE 等 MTP 结构默认 `(3, 1, 4)`——topk=1 即退化成**链验证**。

### 1.2 `__init__`（L98-252）：双模型共享与初始化顺序

初始化顺序本身就是一份设计文档，几处关键决策：

**共享 `req_to_token_pool` 与 `token_to_kv_pool_allocator`（L137-141）**：draft 与 target 的 KV cache 数据池各自独立（层数/宽度不同），但**槽位分配器共享**——同一个 slot id 在两个池中都有效，`req_to_token` 映射表只有一张。这是 EAGLE 能做「draft 先写、target 后写、验证后精确回收」的内存基础。

**context length 对齐（L130-131）**：draft 的 `context_length` 被强制改为 target 的 `context_len`，防止 draft config 里较短的上下文在长序列上越界。

**临时关掉 cuda graph（L133-136）**：`super().__init__()`（即 `TpModelWorker` 构造，会加载 draft 模型权重）期间 `disable_cuda_graph=True`，draft 的图留到 `init_cuda_graphs()`（L273）单独捕获——因为 draft 图需要 embed/head 共享完成后再捕。

**hot token id（L143-156）**：EAGLE3 的 draft 只在"热词表"上预测；若用户另给了 `speculative_token_map`（针对普通 EAGLE 的词表裁剪），L201-205 直接把 target 的 `lm_head` 权重行切片成小词表矩阵——**裁词表而不是加映射**，省一次 gather。

**embed / lm_head 共享（L182-208）**：EAGLE 的 draft 模型没有自己的 embedding 和 lm_head，直接调用 `target_worker.model_runner.model.get_embed_and_head()` 拿到 target 的两份权重 `set_embed_and_head` 给 draft。既省显存又保证词空间严格一致。EAGLE3 例外路径：多数 EAGLE3 draft 自带 lm_head（除非模型声明 `load_lm_head_from_target`，如 gpt-oss-120b-Eagle3，此时走 L187-191 分支）。

**EAGLE3 的 aux hidden（L217-225）**：`eagle_use_aux_hidden_state=True` 时 draft 消费 target 的**多层** hidden states 拼接（`num_aux` 层 × `target_hidden_size`），对应 `eagle_info.EagleDraftExtendInput.hidden_size_for()` 中的宽度放大逻辑。

**adaptive speculative（L123-128, L233-246）**：可选的 `AdaptiveController` 允许运行时在多组 `(steps, draft_token_num)` 配置间热切换，每组配置预捕获一套 attention backend + cuda graph（`SpecRuntimeState`），见 `apply_runtime_state()`（L320-352）。其 `on_verify_complete()` 回调（L546-549）以每轮真实接受率为信号调整树大小。

### 1.3 `init_attention_backend` / `init_cuda_graphs`（L254-318）

- draft 需要**两套** attention backend（L254-271）：`draft_attn_backend` 服务多步自回归 decode（内部按步数克隆了 `steps` 份 backend，`draft_forward` 每步换一份，见 L895-897）；`draft_extend_attn_backend` 服务变长的 DRAFT_EXTEND（尊重 `speculative_attention_mode` 设置）。
- cuda graph 也是两份（L273-318）：
  - `EAGLEDraftCudaGraphRunner` 把**整个多步 draft 循环**（含 topk、树信息收集）捕成一张图；
  - `EAGLEDraftExtendCudaGraphRunner` 捕 draft-extend；
  - target 验证走普通 `CudaGraphRunner`（`TARGET_VERIFY` 模式的定长 `bs × draft_token_num` 形状）。

### 1.4 `forward_batch_generation`（L450-557）：总入口，一个 batch 的编排

这是 Scheduler 每轮调用的唯一入口（`scheduler.py:2949/2992`）。按 batch 状态分两条路。

**extend 路径（L462-486）**——prefill / 混合 batch：

1. `forward_target_extend()`（L559-591）：target 跑 prefill，`capture_hidden_mode=FULL` 拿到**全部 token 的 hidden states**（draft prefill 需要它们逐 token 对齐），同时产出第一个 next_token_ids；
2. `forward_draft_extend()`（L1101-1139）：用 hidden states + token ids 给 draft 做 prefill（详见 1.8），结束后 `capture_for_decode()` 把 draft 的最后 hidden 和 topk 结果存进 `EagleDraftInput`，挂在 `batch.spec_info` 上等下一轮 decode 用；
3. 直接返回 `GenerationBatchResult`（`num_correct_drafts=0`——prefill 轮没有验证）。

**decode 路径（L487-557）**——三阶段全流程：

```python
verify_input = self.draft(batch)            # ① draft 建树（产出 EagleVerifyInput）
batch.spec_info = verify_input
verify_output = self.verify(batch)          # ② target 验证（产出 EagleVerifyOutput）
batch.spec_info = draft_extend_input
next_draft_input = self.forward_draft_extend_after_decode(batch)  # ③ draft 重整
batch.spec_info = next_draft_input          # 下一轮 draft 的输入就位
```

三阶段之间 `batch.spec_info` 的类型轮换是整个实现的**状态机主线**：

```
EagleDraftInput → EagleVerifyInput → EagleDraftExtendInput → EagleDraftInput → …
```

注意 L526-540 的分支：若 DP attention 开启或还有未完成请求，跑阶段③；若全 batch 结束，安装一个"idle"的 `EagleDraftInput`（L540, `_draft_preprocess_idle`），保证 scheduler 的 merge/filter 操作永远看到形状良定义的空张量而不是 `None`——这是 idle stub 设计的核心动机。

最终返回的 `GenerationBatchResult`（managers/utils.py:26）携带：
- `next_token_ids=accept_tokens`：本轮全部被接受 token 的扁平张量；
- `num_correct_drafts_per_req_cpu`：每请求接受数，供 scheduler 侧统计/finish 判断；
- `can_run_cuda_graph`：目标 forward 是否走了图。

**batch 结果如何回写 Scheduler**（两处分工）：
- token 级别的 `req.output_ids.append(id)`、`req.kv_committed_len`、`req.update_finish_state()`、接受率直方图等在 `EagleVerifyInput.verify()` 内部直接写进 `Req` 对象（eagle_info.py:457-496）；
- batch 级别的 `seq_lens`/`out_cache_loc`/`req_to_token` 修正同样在 verify 内完成。

scheduler 拿到结果后只做输出转发与 filter——投机解码的重量级状态管理全部下沉到 worker/spec_info 层。

### 1.5 `_draft_preprocess_decode`（L593-730）：draft KV 的"scratch"分配

阶段①的前置，做四件事：

**① 惩罚累积（L603-607）**：把上一轮的 `bonus_tokens` 累进 penalizer（frequency/presence penalty 的投机解码"松弛版"——注释 L604 明言 relaxed version）。

**② 分配 draft KV 槽（L609-680）**：为每请求分配 `steps × topk` 个槽。`page_size==1` 走 `alloc_token_slots(backup_state=True)`；大页场景分两支：
- topk==1：`get_last_loc_large_page_size_top_k_1`（L1293，一个 `torch.compile(dynamic=True)` 包装的函数）；
- topk>1：`get_last_loc_large_page_size_large_top_k`，需要把每请求最后不完整的页**复制 topk 份**让各分支从页对齐处生长，L715-719 的 `move_kv_cache` 完成复制。

槽布局注释在 L610-612（iter-major）：

```
[       topk 0         ] [       topk 1         ]
[iter=0, iter=1, iter=2] [iter=0, iter=1, iter=2]
```

`draft_forward` 里再 reshape/permute 成 step-major（L852-857）。

**③ `assign_draft_cache_locs` Triton kernel（L696-713）**：把分配的槽写入 `req_to_token` 表的树状区域。source 注释 L634-641 画出了大页下的布局：

```
| -------- | -- xxxx .. | -- xxxx .. | -- xxxx .. |
   prefix      topk = 0     topk = 1    topk = 2
```
（`-` 前缀 token，`x` draft token，`.` padding）

**④ 立即 `restore_state(token_to_kv_pool_state_backup)`（L730）**：分配完马上把 allocator 状态回滚到分配前！这是本文件最微妙的一行——draft KV 槽是**一次性的 scratch 空间**：本轮 draft 写入的数据生命周期只到 verify 结束（下一轮 draft 从新分配的槽重新写起），allocator 不为其记账，槽位自然回收循环使用。真正进入记账的是 verify 阶段 target 分配的那 `bs × draft_token_num` 个槽。

L615/721 的两处 `TODO: We only need steps-1 * topk cache loc` 指出最后一步的 forward 不需要 KV 写入，这是已知的优化空间。

另注意 L729：`spec_info.positions = batch.seq_lens.repeat_interleave(topk)`——draft 树第一层 topk 个分支的初始位置都是当前序列长度（同层同位，这正是 tree mask 存在的原因）。

### 1.6 `draft()`（L746-834）与 `draft_forward()`（L836-922）：多步自回归建树

`draft()` 是阶段①的编排：
- idle batch → 装 idle 输入（L748-749）；
- 构造 `ForwardBatch`（`num_tokens_per_req = topk`，L762），能用 cuda graph 就 `cuda_graph_runner.replay()` 整图回放（L769-775，返回 `parent_list, top_scores_index, draft_tokens` 三元组），否则走 eager 的 `draft_forward`（L776-787）；
- **建树（L796-813）**：调 `build_tree_kernel_efficient()`（eagle_utils.py:101，CUDA 实现在 sgl-kernel）把「每步的分数/token/父节点」压成 target 验证所需的五件套：
  - `tree_mask`：每个候选 token 的注意力可见模式（前缀 + 祖先链）；
  - `positions`：每个候选的 RoPE 位置 = 祖先深度 + seq_len；
  - `retrieve_index / retrieve_next_token / retrieve_next_sibling`：树的儿子/兄弟链表，验证回溯用；
- 组装 `EagleVerifyInput`（L820-834）返回。

`draft_forward()`（L836-922）是树生长的循环体（cuda graph 捕的就是它）：

```python
for i in range(self.speculative_num_steps):          # L866
    input_ids, hidden_states, scores, tree_info = select_top_k_tokens(
        i, topk_p, topk_index, hidden_states, scores, self.topk)   # L867
    if i == self.speculative_num_steps - 1: break    # L875：最后一步只收集不再 forward
    forward_batch.input_ids = input_ids              # (bs*topk,)
    forward_batch.out_cache_loc = out_cache_loc[i]   # 每步一份槽
    with forward_context(ForwardContext(attn_backend=...attn_backends[i])):  # L895
        logits_output = self.draft_model_runner.forward(
            forward_batch, skip_attn_backend_init=True)
    probs = torch.softmax(logits_output.next_token_logits, dim=-1)
    topk_p, topk_index = fast_topk(probs, self.topk, dim=-1)      # L903-904
    forward_batch.positions.add_(1)                   # L916：整批位置 +1（同一层同位）
```

三个要点：

**`select_top_k_tokens`（spec_utils.py:582）**：
- 第 0 步（`_first`，L525）直接展开 `topk_index` 并把 `hidden_states` `repeat_interleave(topk)` 复制给各分支，父节点记 -1（挂在 bonus 根上）；
- 后续步（`_later`，L546）计算**累积分数** `scores.unsqueeze(2) * topk_p.view(-1, topk, topk)` 得到 topk² 个候选再选 topk，`topk_cs_index + (topk_sq*(i-1) + topk)` 把局部索引映射到扁平候选池的全局索引。

累积分数是 EAGLE 树剪枝的核心：**全局最优的 draft_token_num-1 条路径**，而非每步贪心。

**每步一个独立 attention backend 实例（L895-897）**：多步循环共享同一个 `ForwardBatch`，各步的 KV 写入位置不同，靠 `attn_backends[i]` 区分元数据；`forward_context` 上下文让模型层（RadixAttention）读到正确的 backend，绕过 runner 的默认初始化（`skip_attn_backend_init=True`）。L891-894 的注释解释了为何需要外层包装：`_forward_raw` 在已有活跃 context 时对 attn_backend 一半是 no-op，必须靠这层 wrap 才能到达 RadixAttention。

**`organize_draft_results`（eagle_utils.py:73，L918-920 调用）**：把各步的 `score_list/token_list/parents_list` 拼接后 `torch.topk(score_list, num_draft_token-1)` 选出最终树节点（索引排序保证路径前缀有序），产出 `parent_list / top_scores_index / draft_tokens`。

热词表场景（L849-850, L911-912）：`topk_index = self.hot_token_id[topk_index]` 把小词表 id 映射回全词表。

### 1.7 `verify()`（L928-1017）：target 一次 forward 验证整树

worker 侧的编排（真正的验证算法在 `EagleVerifyInput.verify()`，见第二节）：

1. **L930-938**：`prepare_for_verify()`（eagle_info.py:123）分配 target 的 `bs × draft_token_num` 个 KV 槽、写 `req_to_token`、把 `batch.input_ids` 设为展平的 draft tokens；`forward_mode` 切到 `TARGET_VERIFY`；`num_tokens_per_req = steps + 1`（注意：**不是** draft_token_num，这个值只用于 DP attention 的全局 token 记账）。
2. **L940-945**：grammar（结构化输出）场景先把 `retrieve_next_token/sibling`、draft_tokens 拷到 CPU——为的是与 GPU forward 重叠。
3. **L948-955**：target forward，`is_verify=True` 让 `TpModelWorker.forward_batch_generation` 跳过常规采样（tp_worker.py:486-488）——验证采样由 spec 侧接管。
4. **L957-975**：grammar 的 `generate_token_bitmask`（L961 注释明言 overlap CPU ops with the forward pass）：基于树的 DFS 遍历（`traverse_tree`）为每个候选节点生成合法词掩码，并覆盖上一阶段的旧 mask（L973-975 的 NOTE 记录了不复盖会出错的坑）。
5. **L980-987**：调 `spec_info.verify(...)`（核心，见 2.3），返回 `EagleVerifyOutput`。
6. **L989-997**：用 `res.accept_indices` 把 `logits_output.next_token_logits / hidden_states` **就地裁剪**到只剩被接受位置——下游（logprob、scheduler 输出处理）看到的就是"干净"的每 token 一行。
7. **L999-1006**：混合架构（mamba/hybrid_gdn/lightning）需要额外把 mamba 状态回拨到最后被接受步（`_mamba_verify_update`）。
8. **L1008-1009**：需要 logprob 时补算（`add_output_logprobs_for_spec_v1`）。
9. **L1011-1014**：`forward_mode` 切回 `DECODE`（供 scheduler 正常推进状态）。

### 1.8 `forward_draft_extend*()`：阶段③，draft 的状态重整

EAGLE 的 draft 模型输入是 `[embed(token), hidden_state]` 的拼接，**每个被接受的 token 都必须让 draft 重新过一遍**才能得到下一轮的干净起点。两个变体：

**`forward_draft_extend()`（L1101-1139，prefill 后调用）**：输入是 target prefill 的全量 hidden states + 采样的 next_token_ids。
- L1123 的 `apply_eagle_prefill_input_rotation()`（eagle_utils.py:50）做**输入轮转**：`[t_0..t_{n-1}] → [t_1..t_{n-1}, t_n]`——把"位置 i 的 hidden"对齐到"位置 i+1 的标签"，这正是 EAGLE 链式预测（用上一层特征预测下一 token）的对齐基础。实现是整张量左移 + 段尾 scatter，一个 kernel 完成。
- 结束后 `capture_for_decode()`（L1267-1272）把最后 hidden + topk 结果写进 `EagleDraftInput`。

**`forward_draft_extend_after_decode()`（L1141-1265，verify 后调用）**：变长 extend（每请求 `num_accept_tokens` 个 token），三段式：

- **Phase 1（L1174-1180）**：`prepare_extend_after_decode()`（eagle_info.py:944）把 `input_ids/seq_lens/req_pool_indices` 从 `EagleDraftExtendInput` 拷回 batch，一个 Triton kernel（`create_extend_after_decode_spec_info`）写：
  - `positions` = `seq_lens - num_accept + arange`（被接受 token 的真实历史位置）；
  - `bonus_tokens`（每请求最后一个被接受 token——它就是下一轮 draft 树的根）。
- **Phase 2（L1199-1234）**：draft extend forward。cuda graph 路径直接从 `logits_output` 读图内预计算的 `topk_p/topk_index`（L1208-1211）；eager 路径用 `forward_context` 发布 `draft_extend_attn_backend`（L1221-1227，不改 runner 属性，避免竞争），然后 inline softmax+topk。
- **Phase 3（L1241-1265)**：用 extend 输出的 `topk_p/topk_index/hidden_states` + Phase 1 的 `bonus_tokens` 组装下一轮 `EagleDraftInput`，然后**恢复**被 Phase 1 改掉的 batch 字段（`seq_lens/req_pool_indices/return_logprob`，L1147-1150 backup、L1255-1264 restore）。

L1159-1172 处理空输入（全 idle 或全 finished）：`batch.copy()` + `prepare_for_idle()` + idle stub，注释里标了两类 stub 来源。

### 1.9 `_mamba_verify_update`（L1019-1099）：混合架构的状态回拨

mamba/线性注意力架构的 state 是"整条序列一个状态"，树验证会在多个分支上写出多个候选 state，必须回拨到**最后被接受 token 所在步**的状态。核心推导（L1057-1071 的注释非常详尽）：

```
accept_indices=[0,2,3,4,5,7,9,10,11], num_accept_tokens=[4,3,2]
cumulative_num_accept_tokens=[4,7,9]
first_token_indices_per_req = [0,5,10]   ← 每 req 在扁平 accept 流的起点
last_token_indices_per_req  = [4,9,11]   ← 每 req 最后接受 token 的扁平位置
last_correct_step_indices   = [4,4,1]    ← 每 req 正确 mamba state 所在的步偏移
```

topk>1 时用 `retrieve_next_token/sibling` 链表语义从 `accept_indices` 反解；topk==1 时直接等于 `num_correct_drafts`（L1071）。若开了 mamba track interval（L1073-1092），还要在跨越追踪点处记录中间 state（`mamba_steps_to_track`），供回溯/换出恢复用。最后调 `attn_backend.update_mamba_state_after_mtp_verify()`（L1094-1099）落地。

### 1.10 自适应投机与其他成员

- `apply_runtime_state()`（L320-352）：原子替换 steps/draft_tokens/draft backend/draft 图/target backend/target 图/extend backend/extend 图 + 同步 server_args——一次热切换不动正在飞的 batch。
- `build_adaptive_runtime_state()`（L353-408）+ `_override_worker_state()`（L410-444）：在受保护的上下文里临时改 worker/server_args 状态去捕获新配置的整套组件，打包成不可变 `SpecRuntimeState`。
- `update_weights_from_tensor()`（L1274-1290）：权重热更新时先更 draft 再更 target。
- `clear_cache_pool()`（L924-926）：空操作——allocator 与 target 共享，生命周期由 target 侧管理。
- `draft_model_runner` property（L446-448）：`self.model_runner` 的别名，提醒读者"本 worker 的 model_runner 跑的是 draft"。

---

## 二、端到端时序：一个 batch 的完整走读（worked example）

**配置**：`steps=5, topk=4, draft_token_num=8`（Llama 默认），`bs=2`，`page_size=1`，`hidden_size=4096`，`vocab_size=128256`。请求 R0/R1 的 prompt 长度分别为 10、12（`seq_lens=[10,12]`，`seq_lens_sum=22`）。

### Step 0：prefill 轮（extend 路径，L462-486）

```
target prefill : input_ids (10+12=22,)
                 → hidden_states (22,4096)   [capture FULL]
                 → next_token_ids (2,)        （R0→t10, R1→t12）

draft prefill  : 输入轮转 [t1..t9|t10, t11..t11|t12] → draft forward (22 tokens)
                 → 最后 hidden (2,4096) → softmax → topk

EagleDraftInput: topk_p (2,4) | topk_index (2,4)
                | hidden_states (2,4096) | bonus_tokens (2,)
                 （batch.spec_info ← 该对象，跨轮存活）
```

### Step 1：draft 建树（`draft()` → `draft_forward()`）

**预分配（`_draft_preprocess_decode`）**：

```
out_cache_loc (40,) = 2 reqs × 4 branches × 5 iters   ← scratch，restore_state 不记账
positions (8,) = [10,10,10,10, 12,12,12,12]           ← 第一层同位
```

**多步循环（cuda graph 一张图回放）**：

```
i=0: input_ids (8,) = topk_index.flatten()
     hidden_states (8,4096) = repeat_interleave(4)     ← 每分支复制根 hidden
     forward → logits (8,128256) → topk_p/topk_index (2,4)
     score_list[0] (2,1,4)   token_list[0] (2,4)   parents_list[0] (2, topk+1)

i=1..3: 候选 4×4=16 个/req，累积分数 topk 选 4
     score_list[i] (2,4,4)   token_list[i] (2,16)   parents_list[i] (2,4)

i=4: 只收集 tree_info，不再 forward（L875）
     每步 positions.add_(1)：第二层全在位置 11/13，第三层 12/14 ……
```

候选池总量 = `topk + (steps-1)·topk² = 4 + 4×16 = 68`。

**剪枝（`organize_draft_results`）**：

```
score_list cat → (2, 68) → topk(score, k=7) → top_scores_index (2,7)   [排序]
draft_tokens (2,7)      ← 全局累积分数最优的 7 个节点
parent_list (2,17)      ← 对应父节点（首层父=-1 挂 bonus 根）
```

**建树（`build_tree_kernel_efficient`）**：

```
draft_tokens_flat = cat(bonus (2,1), draft_tokens (2,7)).flatten() → (16,)
tree_mask  (seq_lens_sum*8 + 8*8*2 = 176+128 = 304,) bool   ← FULL_MASK 模式
positions  (16,)      ← 每节点 = seq_len + 树深度
retrieve_index / retrieve_next_token / retrieve_next_sibling  各 (2,8)，初值 -1
```

kernel 依据 parent 拓扑重建三件事：attention 掩码（每个候选只能看见「真实前缀 + 树内祖先链」）、RoPE 位置、以及**验证回溯链表**——`retrieve_next_token[i]` 是节点 i 的首选儿子、`retrieve_next_sibling[i]` 是下一个兄弟，二者让验证 kernel 沿"最长接受路径"线性回溯。

一个 8 节点树的示意（bonus 为根，3 层深度）：

```
        bonus(t13)                    ← predict 的保底采样位
        /      \
     c0         c1                   ← 层1（位置 14）
    /  \          \
  c2    c3         c4                ← 层2（位置 15）
  /       \
c5         c6  c7                    ← 层3（位置 16）
```

**产出 `EagleVerifyInput`** 挂上 `batch.spec_info`（L501）。

### Step 2：target 验证（`verify()` → `EagleVerifyInput.verify()`）

```
prepare_for_verify: alloc 16 个 target KV 槽（正式记账）；req_to_token 每 req 写 8 格
forward_mode = TARGET_VERIFY
target forward: input_ids (16,) → logits (16,128256), hidden (16,4096)  ← 一次 forward！
```

验证采样（eagle_info.py:335-407，全 greedy 时走 `verify_tree_greedy` kernel）：

```
target_predict = argmax(logits) → (2,8)      ← 树上每节点 target 的偏好
predict (17,)     ← 16 个候选位 + 1 个 bonus 位（predict[16] 存树根处的 target 采样）
accept_index (2,6)   初值 -1     ← spec_steps+1 列：一条路径最多 5 draft + 1 bonus
num_correct_drafts (2,)
```

kernel 输出示例：R0 接受 3 个 draft（路径 c0→c2→c5，全对，bonus 落袋）：

```
accept_index[0] = [i(c0), i(c2), i(c5), i_bonus, -1, -1]   → n=3
accept_index[1] = [i_bonus', -1, -1, -1, -1, -1]           → n=0（R1 首节点即被拒）
```

采样路径（非 greedy）用 `tree_speculative_sampling_target_only`（L350-407）：target probs 经 temperature/top-k/top-p renorm 后与 draft probs 做拒绝采样；两个 threshold（`speculative_accept_threshold_single/acc`，默认 1.0）允许牺牲无偏性换更高接受率；TP>1 时 L409-421 **broadcast `predict/accept_index/num_correct_drafts`**，消除浮点非确定性导致的多 rank 采样分叉。

**结果回写与 KV 结算（eagle_info.py:448-594）**：

```
逐 req 逐 token: req.output_ids.append(id)；req.update_finish_state()
                 finished → accept_index[i, j+1:] = -1 截断（后续 token 不再上交）
                 req.kv_committed_len += num_accept
                 req.spec_verify_ct += 1（接受率直方图统计）

accept_index != -1 → flat，accept_tokens = predict[accept_index]   例：(4+1, 1+1)=(6,)
evict_mask: 未被接受的目标槽 → token_to_kv_pool_allocator.free(...)   ← KV 回收
topk>1 & page>1 时额外把被接受 KV move_kv_cache 搬到页对齐连续区（L534-577）

batch.out_cache_loc = out_cache_loc[accept_index]   ← 只留正式 KV
batch.seq_lens += num_correct_drafts + 1            → [14,14]（例：R0 +4，R1 +2）

EagleDraftExtendInput{ hidden_states[accept_index] (6,4096),
                       input_ids=accept_tokens (6,),
                       num_accept_tokens_cpu=[4,2], ... }
```

worker 侧裁剪（L989-997）：`logits_output.next_token_logits (16,vocab) → (6,vocab)`。

### Step 3：draft 重整（`forward_draft_extend_after_decode`）

```
positions = [10,11,12,13,  12,13]     ← 被接受 token 的真实历史位置
                                        （R0 接受了 t10..t13，R1 接受了 t12..t13）
bonus_tokens = [t13, t13]              ← 每请求最后一个接受 token = 新 draft 树的根
draft extend forward: 6 tokens（变长）
→ topk_p (2,4) / topk_index (2,4) / hidden_states (2,4096)
→ 下一轮 EagleDraftInput 组装完毕，batch.spec_info ← 它，batch 字段 restore
```

### Step 4：返回与循环

```
GenerationBatchResult{
  next_token_ids = accept_tokens (6,),        ← scheduler 输出处理直接消费
  num_correct_drafts_per_req_cpu = [3, 0],
  can_run_cuda_graph = True/False }

→ scheduler process_batch_result → filter finished reqs → 下一轮 decode 回到 Step 1
```

每轮净产出 `E[#accept] = E[num_correct_drafts] + 1 ≥ 1` 个 target-分布 token，target forward 恒为一次。

---

## 三、与其他模块的交互

### 3.1 `eagle_info.py`：spec_info 数据结构族（状态机的载体）

| 类 | 角色 | 关键字段 |
|---|---|---|
| `EagleDraftInput`（L702） | 阶段①输入，**跨轮存活** | `topk_p/topk_index (b,topk)`、`hidden_states (b,H)`、`bonus_tokens (b,)` |
| `EagleVerifyInput`（L72） | 阶段②输入（建树产物） | `draft_token/custom_mask/positions`、`retrieve_*` 链表、`spec_steps/topk/draft_token_num` |
| `EagleDraftExtendInput`（L838） | 阶段③输入（验证产物） | `hidden_states[accept]`、`input_ids=accept_tokens`、`num_accept_tokens_cpu`、kernel 写入的 `positions/bonus_tokens` |
| `EagleVerifyOutput`（L1012） | verify 返回值 | `accept_tokens`、`accept_indices`、`num_correct_drafts_per_req_cpu`、`draft_extend_input` |

三者都继承 `SpecInput`（spec_info.py:253），用 `SpecInputType` 枚举（EAGLE_DRAFT / EAGLE_DRAFT_EXTEND / EAGLE_VERIFY）让 attention backend 与 ForwardBatch padding 逻辑**无需 isinstance 硬编码**即可分派阶段（`is_draft_input()/is_verify_input()` 协议）。

`EagleDraftInput` 还实现 `filter_batch/merge_batch`（L778/L807）——scheduler 的批合并/过滤会透传到 spec 状态；idle stub（`create_idle_input`）保证空批时字段仍是形状合法的空张量。L783-792 的 strict check 分支处理"verify 已按 unfinished 过滤 vs scheduler 再过滤一次"的双重过滤竞态。

`EagleVerifyInput.verify()`（L242-698）是**最重的方法**：采样（greedy / tree spec sampling）、逐 token finish 检查、KV 结算（三分支：page=1 / topk=1 / 通用）、以及 finished 与 unfinished 两套 `EagleVerifyOutput` 组装路径（L618-698 的 has_finished 分支要同时处理已结束请求的 out_cache_loc 对齐与幸存请求的 draft-extend 输入切片）。

### 3.2 Scheduler / TpModelWorker：控制流反转

- Scheduler 持有 `self.model_worker = self.draft_worker`（scheduler.py:774-777），每个 running batch 的 forward 调用都进入 `EAGLEWorker.forward_batch_generation`；
- worker 内部再以"反向"调用 target（`self.target_worker.forward_batch_generation(batch, is_verify=True)`，L949）；
- `GenerationBatchResult`（managers/utils.py:26）是两 worker 间的统一信封，`num_correct_drafts_per_req_cpu/accept_lens` 等字段专供 scheduler 侧做 finish 判断与指标统计；
- batch 的 `spec_info` 字段是 scheduler 与 worker 的共享状态槽：scheduler 的 merge/filter 会操作它，worker 每阶段替换它。

### 3.3 cuda graph 协同：三个图运行器

| 运行器 | 捕获内容 | 形状约定 |
|---|---|---|
| `EAGLEDraftCudaGraphRunner` | **整个** `draft_forward` 多步循环（含 select_top_k_tokens、softmax+topk） | 恒定 `bs × topk` tokens/步，输入靠静态 buffer 拷入（`buffers.topk_p/topk_index/hidden_states/out_cache_loc`），replay 前按 capture_bs padding |
| `EAGLEDraftExtendCudaGraphRunner` | draft-extend 变长 forward | 按 `(bs, max_accept_len)` 分档捕获；replay 后直接从 `logits_output` 读出 `topk_p/topk_index`（L1208-1211，图内预计算） |
| `CudaGraphRunner`（target 共用） | `TARGET_VERIFY` 定长 forward | `bs × draft_token_num` tokens，树 mask 走 padded `cuda_graph_custom_mask` |

图友好性是数据结构设计的隐性约束：`num_tokens_per_req`、`retrieve_*` 定长 `(bs, draft_token_num)`、idle stub 全空张量，都是为了让 merge/filter/pad 之后形状仍落在捕获档位内。

### 3.4 模型侧：EAGLE head 与 hidden states 管线

- target 模型实现 `get_embed_and_head()`（如 deepseek_v2.py:2637 等），draft 模型实现 `set_embed_and_head()` / `set_embed()`；L182-208 的共享已述。draft forward 的输入拼接 `[embed(ids), hidden_states]`、EAGLE3 的多层 aux hidden 拼接，都在各模型文件（如 `models/eagle.py`、DeepSeek MTP 头）内完成。
- hidden 的捕获深度由 `CaptureHiddenMode` 控制：
  - target verify 阶段 `FULL`（draft-extend 需要每个被接受位置的 hidden，L815-819）；
  - draft 阶段 `LAST`（只要最后 hidden，L756-761）；
  - STANDALONE（无 hidden 依赖的普通 LLM draft）一律 `NULL`。
- `spec_hidden_size` / `EagleDraftExtendInput.hidden_size_for()`（eagle_info.py:887-912）：EAGLE3 aux 模式下 extend 阶段宽度 = `target_hidden × num_aux`，decode 阶段 = draft 自链宽度——两个阶段 hidden 宽度不同，是该文件里"decode/extend 用不同 dataclass"的根本原因之一。`get_draft_hidden_dim()`（eagle_utils.py:258）是同一逻辑在模型侧的镜像。

### 3.5 attention backend 侧

- 阶段②的树注意力：`EagleVerifyInput.generate_attn_arg_prefill()`（eagle_info.py:184）为 flashinfer 类 backend 生成 `qo_indptr/cum_kv_seq_len/custom_mask`（L225-238 还处理 cuda graph 下 mask padding 的 FIXME）；Triton backend 直接读 `spec_info.custom_mask`（triton_backend.py:407）。
- tree mask 的三种形态由 `TreeMaskMode`（eagle_utils.py:95）区分：`FULL_MASK`（完整 q×k 布尔）/ `QLEN_ONLY`（只压 query 内三角）/ `QLEN_ONLY_BITPACKING`（位压缩），支撑不同 backend 的效率取舍。
- `draft_attn_backend` 的多实例结构（`attn_backends[i]`）由 `DraftBackendFactory`（draft_utils.py:10）创建，支持 triton/flashinfer/fa3/fa4/aiter/dsa 等全谱系；L891-897 的 `forward_context` 是把"第 i 步 backend"注入模型层的正式通道。

---

## 四、关键设计决策

**1. 树验证而非链验证（topk>1）**

链（topk=1，MTP 风格）每步只有一条路径，draft 长度受接受率指数衰减限制；树把同一深度上 top-k 条并行路径放进**同一次** target forward（代价仅是 mask 更复杂 + verify token 数变多），使"至少接受一条较好路径"的概率大增。实现上的代价是三处特判：
- draft 期的分支槽布局（`assign_draft_cache_locs`）；
- verify 期的 `retrieve_*` 回溯链表；
- `page_size>1 ∧ topk>1` 时最繁琐的 KV 复制/搬运（eagle_info.py:534-577：把接受的 KV `move_kv_cache` 到页对齐连续区，再 free 尾部）。

**2. accept 语义 = num_correct_drafts + 1（bonus token 保底）**

无论接受多少，树根处总有一个由 target 分布亲自采样的 token 落袋（`predict` 缓冲的 `bs*draft_token_num` 下标位即 bonus 槽），因此投机解码**无损**且每轮恒有产出。`accept_index` 直接索引 `out_cache_loc`（-1 为哨兵），一个数组同时编码了"接受了谁"与"KV 留给谁"。非 greedy 时用拒绝采样保证分布一致，TP>1 时 broadcast 消除 rank 间浮点分歧（eagle_info.py:409-421）。

**3. KV 回滚 = "draft 零记账 + target 精确结算"，不回滚计算**

- draft 多步写入的 KV 是 scratch（分配后立即 `restore_state`，不进 allocator 账本，下轮覆写）；
- target 验证槽严格记账，verify 后按 `evict_mask` free 未接受槽、接受槽原地转正（topk=1 或 page=1），或搬运对齐（topk>1 且 page>1）。

相比"先写后统一回滚"的方案，省掉了任何 KV 数据搬移的通用路径，把回滚成本压到一次位掩码 free。

**4. `batch.spec_info` 状态机驱动，而非 worker 内部持状态**

三个 dataclass 沿 `EagleDraftInput → EagleVerifyInput → EagleDraftExtendInput → EagleDraftInput` 轮换（L501/532/534），使 scheduler 的 merge/filter、attention backend 的阶段分派、cuda graph 的形状假设都挂在同一份类型化状态上；idle stub 确保空批/DP 空闲 rank 全链路形状合法。这让 v2（overlap）worker 能复用同一批数据结构重排时序。

**5. 一切为整图捕获让路**

- draft 多步循环（含 CPU-free 的 topk/树信息收集）一张图；
- draft-extend 一张图；
- 变长信息全部编码进张量（`retrieve_*` 定长、`num_tokens_per_req` 标量、`positions` 预计算），使投机解码的三个阶段都能零 CPU 同步地回放。

这也是为什么大量逻辑下沉为 Triton/CUDA kernel（`assign_draft_cache_locs`、`create_extend_after_decode_spec_info`、`build_tree_kernel_efficient`、`verify_tree_greedy`）。仅存的热点同步是 verify 内 `num_correct_drafts.cpu()`（L513，scheduler 需要 CPU 侧接受数）；文件中留有多处 TODO（如 L521 的布尔索引 device sync）表明仍在持续优化。

---

## 五、阅读建议

**1. 入口顺序**：`SpeculativeAlgorithm.create_worker`（spec_info.py:160）→ `EAGLEWorker.forward_batch_generation`（L450，全文地图）→ 三阶段方法。先读 eagle_info.py 各 dataclass 的 docstring（写得极好，特别是 `EagleDraftExtendInput` L838-880 的字段注释），再回头读 worker。

**2. 对照 v2**：生产默认走 overlap schedule，实际生效的是 `eagle_worker_v2.EAGLEWorkerV2`（阶段拆到独立 forward overlap 线程，`GenerationBatchResult.next_draft_input` 字段即为其接力通道）。读懂 v1 后，v2 的差异只剩"时序重排 + future_indices 引用追踪"。

**3. kernel 侧源码**：`sgl-kernel` 仓库中的 `build_tree_kernel_efficient`（树拓扑 → mask/positions/retrieve 链表）与 `verify_tree_greedy` / `tree_speculative_sampling_target_only`（回溯接受 + 拒绝采样）是理解树语义的最终依据。建议拿 `steps=2, topk=2, draft_token_num=4` 的微型配置手推一遍 `retrieve_next_token/sibling` 的回溯过程。

**4. 实验工具**：`scripts/playground/bench_speculative.py` 可扫参对比 `(steps, topk, draft_token_num)` 组合；环境变量 `SIMULATE_ACC_LEN`（eagle_info.py:423-431）可**强制固定接受长度**，用于隔离验证调度/内存逻辑；`speculative_accept_threshold_single/acc < 1.0` 可体验"有偏换吞吐"模式。

**5. 调试断言密度**：本文件布满 `maybe_detect_nan/inf/oob` 探针（如 L847, L901, L977）与 `assert isinstance(spec_info, ...)`，阅读时它们是最可靠的"不变量说明书"——每个断言都对应一次真实踩坑。

**6. 延伸阅读**：`multi_layer_eagle_worker.py`（每步独立 draft 模型）、`standalone_worker.py`（无 hidden 依赖的普通 LLM draft，`hidden_states=None` 分支）、`eagle_disaggregation.py`（PD 分离下 draft 状态跨机重建）都是本文件的变体，先精读本文件可事半功倍。
