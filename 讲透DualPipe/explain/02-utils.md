# DualPipe/dualpipe/utils.py 精讲——WeightGradStore 与张量切分

> 原文件：`DualPipe/dualpipe/utils.py`（80 行，一个类 + 四个函数）

## 一、角色定位

utils.py 是 DualPipe 的共享工具箱，80 行装了三样东西：**WeightGradStore**（零气泡流水线的关键机构——把"权重梯度计算"从反向传播中剥离、延迟、成批重新调度）、**run_backward**（绕过 `torch.autograd.backward` 的直接引擎调用，服务于流水线中间 stage 的反传语义）、**scatter/gather/chunk/cat**（micro-batch 的切分与重组）。没有这个文件，dualpipe.py 里的 W chunk、B chunk 就少了一半意义。

## 二、内部结构

**WeightGradStore**（类变量实现的全局单例语义）：
- `enabled: bool`——开关；`cache: List[Callable]`——暂存当前 chunk 的权重梯度闭包；`funcs_queue = queue.Queue()`——已封存的批次队列。
- `put(func)`：追加闭包进 cache；`flush()`：cache 整批入队并清空；`pop()`：FIFO 取一批逐个执行（空队列直接 assert "Pop empty queue."）；`clear()`：全部复位。

**run_backward(tensors, grad_tensors)**：直接调 `Variable._execution_engine.run_backward`，kwargs 固定为 `keep_graph=False, create_graph=False, allow_unreachable=True, accumulate_grad=True`。

**张量工具**：`chunk_tensor(x, chunks, dim)`（None 透传出等长 None 列表；否则 `tensor_split`）；`cat_tensor(x, dim)`（单元素解包、全 None 断言、其余 `torch.cat`）；`scatter(inputs, chunks, dim)`（单 tensor 包成元组 → 逐元素 chunk → `zip(*...)` 转置成"每个 micro-batch 一个输入元组"；全空输入生成 `[() for _ in range(chunks)]` 占位）；`gather(micro_outputs, dim)`（逆操作：zip 转置 + 逐列 cat）。

## 三、外部连接

WeightGradStore 在 dualpipe.py 的五个位置被消费：`_reset_states()` 开局 `clear()`；`_backward_compute_chunk` 里 `enabled = enable_zb` 分段开关、chunk 结束 `flush()` 成批封存；`_weight_chunk` 里 `pop()` 执行一个 W chunk；`step()` 末尾 `assert funcs_queue.empty()` 校验收支平衡。`run_backward` 是 `_backward_compute_chunk` 非 last-stage 路径的入口：`outputs` 与 `output_grads` 先 zip 过滤掉 `g is None` 的槽位再传入。scatter/gather 只在 `step()` 首尾两端使用（中间 rank 无输入数据）。`__init__.py` 把四个符号全部重导出，是包的公共面。

## 四、数据流

**零气泡数据流**：用户模型的 hook（examples 里有范例）在反向图执行到权重梯度节点时，不就地计算，而是 `WeightGradStore.put(closure)` 把计算封成闭包入队 → 一个 chunk 反传结束，dualpipe 调 `flush()` 把这批闭包整体搬进队列 → 调度器把 W chunk 安排到空闲时隙时 `_weight_chunk` 调 `pop()` 逐个执行。B 与 W 的分离让 `F&B` 融合核有隙可插——气泡公式 `(PP/2-1)(F&B+B-3W)` 里每个 W 都是纯赚。

**数据切分流**：`step()` 里首/尾 rank 的 inputs（tuple 或单 tensor）经 scatter 变成 `half_num_chunks` 个 micro-batch（每个是各输入列的切片元组）；反传产出的 `input_grads` 与 outputs 同构嵌套；末端 `gather(self.output_chunks[...], batch_dim)` 把各 micro-batch 输出按列 cat 回整 batch，单输出自动解包。

## 五、设计决策

- **为什么绕过 torch.autograd.backward**：流水线中间 stage 需要的是"对指定输出张量施加外部梯度做反传"，而非"对标量 loss 求导"；标准 API 不提供这个组合。`keep_graph=False` 表示 chunk 反传一次即弃（激活随即可释放），`allow_unreachable=True` 容忍图中存在不可达分支，`accumulate_grad=True` 保证参数梯度跨 micro-batch 累加。
- **类变量而非实例字段**：WeightGradStore 必须被"用户模型内部的 hook"和"调度器"两端看见，全局类属性免去向每个 module 传递引用的侵入。
- **put/flush 两级攒批**：pop 的粒度 = 一个 chunk 的全部权重梯度闭包，恰好填满一个 W chunk 的调度时隙；若只有一级结构，W chunk 的边界就无法与 chunk 对齐。
- **None 语义贯穿切分**：labels 只存在于首尾 rank、且只有 criterion 非 None 时有意义，中间 rank 的输入是全 None——scatter 仍生成等数量 micro-batch 保持两端节拍同步，cat_tensor 的全 None 断言则防御性收口。
- **queue.Queue 的选择**：虽然本库单线程使用，但 Queue 自带锁，用户把 hook 放到多线程自定义核里时依然安全。

## 六、新人提示

动 WeightGradStore 前记住 `step()` 末尾的 empty 断言——任何 put/flush/pop 不平衡都会在那里炸而不是当场炸，排查要看 put 与 flush 的配对。接自己的模型：hook 里 `WeightGradStore.put(lambda: 真正的梯度计算)`，并保证闭包捕获的是延迟执行所需的全部上下文（example_dualpipe.py 的写法最稳）。scatter 的 chunks 必须两端一致（dualpipe.py 里都是 half_num_chunks）；tensor_split 允许不整除（尾批略小），但对齐切分能让各 micro-batch 计时更均匀、重叠更充分。
