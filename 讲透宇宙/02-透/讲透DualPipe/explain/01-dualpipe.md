# DualPipe/dualpipe/dualpipe.py 精讲——双向流水线引擎

> 原文件：`DualPipe/dualpipe/dualpipe.py`（440 行，单类）

## 一、角色定位

dualpipe.py 是 DeepSeek-V3 技术报告提出的**双向流水线并行（bidirectional pipeline parallelism）参考实现**：把 PP ranks 从中间一分为二，micro-batch 同时从首尾两端注入，前向与反向在各 rank 上交错执行，令通信时段与计算时段完全重叠，从而把流水线气泡压到 `(PP/2-1)(F&B+B-3W)`（对比 1F1B 的 `(PP-1)(F+B)`），代价是参数双倍、激活 `PP+1` 份（README 对比表）。全文件只有一个 `DualPipe(nn.Module)` 类，但它是整个仓库的灵魂。

## 二、内部结构

- **构造期**：`modules` 二元组（本 rank 的两个 stage 模块）、`batch_dim`、`process_group`；`rank_mapping` 维护 group rank ↔ 实际 pp rank 的双向映射（`rank_inverse_mapping`），从而算出 `prev_rank/next_rank/first_rank/last_rank`；`is_in_second_half`、`is_middle_rank` 两个身份位；`overlapped_forward_backward` 探测——两模块同型且类实现了该静态方法时，启用用户自定义的前反向融合核（custom kernel overlap 的挂钩点）。
- **状态四元组**：`input_chunks/output_chunks/input_grad_chunks/output_grad_chunks` 全是 `Tuple[List, List]`——索引 0/1 即 phase 0/1 两个方向各自的 chunk 队列；外加 `labels/loss_chunks/criterion`、六个 chunk 游标（f/b × 当前/发送/接收）、`comm_ops`（P2POp 批量缓冲）、`to_free`（待释放张量）。
- **方法三层**：计算原语 `_forward_compute_chunk`/`_backward_compute_chunk(enable_zb)`/`_forward_backward_compute_chunk`（融合版：pre-forward + pre-backward 取好两边数据，一次调用 module 的 overlap 核）；通信原语 `_recv/_send_forward/backward` + `_commit_and_wait_comm`（`dist.batch_isend_irecv` 批量提交并等待）；调度原语 `_forward_chunk/_backward_chunk/_forward_backward_chunk/_weight_chunk` 把"收-算-发"组装成一步；顶层 `step()` 是八阶段调度程序。

## 三、外部连接

`comm.py` 提供全局 `set_p2p_tensor_shapes/set_p2p_tensor_dtype`（step 前 assert 必须已设）与 `append_irecv/append_isend`：irecv 按预声明 shapes 用 `torch.empty` 预分配接收缓冲，再包成 `dist.P2POp` 攒批。`utils.py` 供给 `WeightGradStore`（零气泡权重梯度延迟）、`run_backward`、`scatter/gather`（micro-batch 切分/重组）。`dualpipev.py` 是 cut-in-half 变体 DualPipeV：删除 `is_in_second_half` 翻转，改为 last rank 上把 phase 0 输出 `detach().requires_grad_()` 后直接喂进 phase 1 输入——流水线在末 rank 折叠成 V 形，设备数减半而气泡与内存指标不变。`examples/` 下两份端到端示例用 `ref_step` 串行参照逐一比对输出/损失/梯度。

## 四、数据流

`step()` 入口：`scatter` 把 inputs/labels 各切 `half_num_chunks` 份（首 rank 的 input 进 phase0、labels 进 phase1；尾 rank 相反——注意 labels 与对端 input 配对的约定）；随后八阶段：

1. `nF0`：预热本方向前向；2. `nF0F1`：两方向前向交替；3. `nB1W1F1`：反向+权重梯度+前向混合（零气泡启动段）；4. 主循环 `nF0B1F1B0`：`_forward_backward_chunk(0,1)` + `(1,0)` 成对执行——一个方向的前向与另一方向的反向在同一函数里融合；5. `nB1F1B0`：排空一侧前向；6. `nB1B0`：双方向反向收尾（`enable_zb` 按 `half_rank` 奇偶在中途开启）；7. `nWB0`：排空权重梯度队列；8. `nW`：清空 WeightGradStore（末尾 `assert funcs_queue.empty()`）。

**phase 异或是灵魂**：每个计算/通信原语第一行 `phase ^= self.is_in_second_half`——后半 rank 的 phase0 语义翻转为反向。同一份调度代码在两端对称运行，这就是"双向"的实现本质。通信重叠模式：`_recv_*` 先把请求 append 进 `comm_ops` → `_commit_and_wait_comm` 批量等待上一轮收发完成并释放 `to_free` → 计算当前 chunk → `_send_*` 把新请求继续 append，下一轮才真正等待。

## 五、设计决策

- **双向对称代替单向填充**：首尾各注一半 batch，中间相遇——气泡减半的来源；约束 `num_ranks % 2 == 0`、`num_chunks >= num_ranks * 2` 且偶数。
- **零气泡（ZB）按需启停**：`WeightGradStore.enabled = enable_zb` 分段开关，`flush()` 把一个 chunk 的权重梯度闭包成批入队，`_weight_chunk` 按 FIFO `pop()` 执行——W 从 B 中剥离成独立可调度单元，这就是气泡公式里 `-3W` 的来源。
- **middle rank 特判**：step_4 首轮中间两 rank 不做融合（"We don't overlap these two chunks to further reduce bubble size"，注释原文），用四个显式 send 排布通信序。
- **内存卫生**：`_free_tensors` 把已发送张量 `tensor.data = torch.Tensor()` 置空并断言 `tensor._base is None`（stage 边界禁止 view 张量——否则接收端/释放逻辑都会错）。
- **rank_mapping 解耦**：逻辑 pp 拓扑与通信组序号分离，便于把相邻 stage 映到同节点（NVLink 域）。

## 六、新人提示

读 `step()` 前记两条不变量：chunk 严格按 phase 有序消费（游标只增），通信永远"先提交、后等待"。`forward_only = not torch.is_grad_enabled()`——no_grad 下自动退化为推理路径。接自己模型时：实现 `overlapped_forward_backward` 静态方法可获得自定义 overlap 核收益；参考 example_dualpipe.py 里 WeightGradStore.put 的 hook 用法。调 `num_chunks` 记住下限是 2×ranks，且越大气泡占比越低但激活内存越高。
