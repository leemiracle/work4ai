# 02 PyTorch 内部：autograd / SDPA 后端 / torch.compile

> PyTorch 不是黑盒, 而是【自动微分 + 动态调度 + 算子融合】的工程系统。
> 配套实验: `experiments/02_pytorch_internals.py` (CPU 验证)
> 核心洞察: PyTorch 的所有优化都指向同一目标——**减少 HBM 读写** (01 篇主旋律)。

---

## 一、autograd: define-by-run 自动微分

### 原理 (三层)
1. **前向记录**: 每个算子执行时, 生成一个 backward 节点挂在输出的 `grad_fn` 上 → 形成 DAG (有向无环图)
2. **反向遍历**: 从 loss 出发, 按**拓扑序逆序**遍历 DAG
3. **链式法则**: 每个节点用局部导数 × 上游梯度, 累加到输入

### 实验1 实测
```
计算: x → y=2x → z=sum(y) → w=z²+1
  y.grad_fn = MulBackward0    ← 前向时自动生成
  w.grad_fn = AddBackward0 → next_functions[0] = MulBackward0  ← DAG 链
反向: x.grad = -2.902  (手算 2z·1·2 = 2·(-0.726)·2 = -2.902 ✓)
```

> **define-by-run**: 你写的是前向 Python 代码, PyTorch **边执行边建图**。这让调试很自然 (能 print/断点), 区别于 TF1 的"先建图后执行"。

### 实验2: 手写 autograd (50 行 numpy 复刻)
我写了个 `Tensor` 类, 实现 `+` `*` `relu` + 拓扑排序 backward。结果**与 PyTorch 逐位一致**:
```
手写 autograd x1.grad = [64, -2]   ==  PyTorch x1.grad = [64, -2]
```
> 这就是 autograd 的全部秘密: 每个 op 定义局部反向函数, 拓扑排序后逆序调用。**没有魔法, 只有链式法则 + DAG。**

---

## 二、SDPA: 多后端调度器 (不是单一实现)

`F.scaled_dot_product_attention` 是个**调度器**, 根据输入自动选最优实现:

| 后端 | 适用 | 本质 |
|------|------|------|
| **FlashAttention** | GPU, 最快 | tiling + online softmax (01 篇) |
| memory-efficient | 省显存备选 | 另一种分块 |
| **math** | CPU fallback, 最兼容 | 朴素 softmax(QK^T)V |
| cudnn_attention | NVIDIA cuDNN | 硬件专用 |

**实验3 实测** (CPU): flash/math 后端可用, cudnn/mem_efficient 不可用 (无 GPU)。

> 这就是为什么 mini-GPT 用 `F.scaled_dot_product_attention(..., is_causal=True)` 而非手写——它**自动选最快的可用后端**, 有 GPU 就用 Flash, 没 GPU fallback math。**永远不要手写 softmax(QK^T)V 再搬显存** (01 篇: 那是最慢的写法)。

---

## 三、torch.compile: 图捕获 + 算子融合

### 做两件事
1. **图捕获**: 把 Python 动态执行 trace 成静态计算图 (TorchDynamo)
2. **算子融合 (fusion)**: 把多个逐元素算子合并成 1 个 kernel

### 融合的本质 (连接 01 篇)
```
朴素: y = relu(x*2 + 1)
  x → 读HBM → ×2 → 写HBM → 读HBM → +1 → 写HBM → 读HBM → relu → 写HBM  (6次HBM)
融合: 
  x → 读HBM → [×2,+1,relu 在寄存器一次完成] → 写HBM  (2次HBM)
```
**和 FlashAttention 同理**: 减少 HBM 读写次数 = 加速。

### 实验4 实测 (CPU)
```
eager:    5.6 ms / 100 次
compiled: 11.6 ms / 100 次  → 0.48× (CPU 上反而慢!)
```
> **诚实结论**: torch.compile 的收益**主要在 GPU** (融合省 HBM 读写, 加速 2-5×)。CPU 上编译开销 > 融合收益, 反而变慢。这符合 01 篇的洞察——优化的本质是减少 HBM 读写, 而 CPU 的"HBM"(DRAM) 慢的惩罚没那么大, 融合收益不显。

---

## 四、统一的系统视角

| 机制 | 解决什么 | 共同目标 |
|------|---------|---------|
| autograd | 自动求导 | 让你专注写前向 |
| SDPA 调度 | 选最快 attention kernel | 减 HBM 读写 |
| torch.compile | 算子融合 | 减 HBM 读写 |
| FlashAttention (01) | attention 不物化 n×n | 减 HBM 读写 |

> **所有现代深度学习系统的优化, 本质都在打一场仗: 让数据尽量留在快的存储 (SRAM/寄存器), 少搬运到慢的存储 (HBM)。** 这是 01 篇的延伸, 也是 ezyang 博客的核心主题。

---

## 参考文献
- Paszke et al. 2017, *Automatic Differentiation in PyTorch* (autograd)
- ezyang 2026, *Autograd and Mutation* (autograd 内部细节, 12 篇资源库)
- PyTorch 2.0, *torch.compile* (TorchDynamo + TorchInductor)
- Ansel et al. 2024, *PyTorch 2: Faster Machine Learning Through Dynamic Compilation*
