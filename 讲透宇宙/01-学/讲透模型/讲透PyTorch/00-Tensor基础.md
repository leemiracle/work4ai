# 00 · Tensor 基础

> Tensor 是 PyTorch 的一切的地基。但它不只是 numpy——它是"会记梯度、能上 GPU、与 autograd 集成"的数组。本章讲三个新手最容易踩坑的点：**视图（共享内存）、广播、dtype/device**。

---

## 一、Tensor 是什么

`Tensor = numpy ndarray + 梯度跟踪 + GPU + autograd 集成`。

```python
x = torch.tensor([[1.,2.],[3.,4.]])
# 三个核心属性:
x.shape    # 形状 (torch.Size)
x.dtype    # 数据类型 (默认 float32, 深度学习标准)
x.device   # 所在设备 (cpu/cuda)
```

> 默认 **float32**：深度学习的标准精度。float64 太慢（除非数值验证），float16/bfloat16 在 GPU 上用于加速（见 05 章）。

---

## 二、视图（view/reshape）：共享内存的本质 ⚠️ 最大坑

```python
x = torch.arange(12.)
y = x.view(3, 4)      # view 共享内存
y[0,0] = 999
print(x[0])           # 999! 改 y 影响 x —— 它们是同一块内存
```

**view/reshape 不是拷贝，是同一块内存的"另一种看法"**（省内存的关键）。想要独立副本必须 `.clone()`。

> numpy 互转（`from_numpy`/`numpy()`）也**共享内存**——改一个另一个变。

---

## 三、广播（Broadcasting）：形状不同也能算

从右往左对齐维度，为 1 或相等的轴可"复制广播"。

```python
A = torch.ones(3, 4)
b = torch.tensor([10.,20.,30.,40.])   # (4,)
A + b    # (3,4): b 被复制 3 次加到每行
```

**经典坑**：`(3,1) + (1,4)` 得到 `(3,4)`——本意可能不同，但广播让它"成功了"，调试形状错误先查广播。

---

## 四、dtype 与精度

| dtype | 字节 | 用途 |
|-------|------|------|
| float32 | 4 | **默认**，训练标准 |
| float16/bfloat16 | 2 | GPU 加速（AMP，见 05 章）|
| float64 | 8 | 数值验证（太慢，别训练用）|
| int8 | 1 | 量化（见 10 实验与激活函数04章）|

---

## 五、device：CPU vs GPU

```python
x = x.to("cuda")      # 迁移
# 铁律: 参与运算的 tensor 必须在同一设备, 否则报错
```

模型和数据都要搬到同一设备。跨设备操作禁止。

---

## 六、实验实证

跑 `experiments/00_tensor_basics.py` 看：view 改视图影响原数据、广播规则、dtype 内存占用。

---

## 📌 下一步

进入 [01-Autograd](01-Autograd与计算图.md)：tensor 怎么"记梯度"——计算图与反向传播。

## 🔬 深度阅读（挖到框架内核）
- **ezyang "PyTorch internals"**（blog.ezyang.com）— Tensor 在 PyTorch 整体架构里的位置，一篇讲清。
- **PyTorch 官方 "A Tour of PyTorch Internals"** — 官方版内部导览。
- **Kieran Didi "How does PyTorch implement a linear layer?"** — 从源码追踪 `addmm`：dispatcher → `native_functions.yaml` → codegen → structured kernels，是读 PyTorch 源码的入门钥匙。
- **PyTorch Developer Podcast**（ezyang 主持）— 有专门讲 native functions / codegen 的单集。

## ✍️ 练习

1. `x.view(3,4)` 和 `x.reshape(3,4)` 区别？何时 reshape 会拷贝？
2. `(3,1)+(1,4)` 为什么得 `(3,4)`？这会引发什么 bug？
3. 默认 float32，为何训练不用 float64？
4. `torch.from_numpy(n)` 后改 tensor，numpy 数组会变吗？为什么？

---

## 费曼回炉记录（L2 自检 · 已迭代）

- **F2 卡壳点**：
  - **卡点 A**：新手最大坑——长期以为 `y = x.view(3,4)` 是把 x 复制成 3x4 形状的新数组。直到 debug 时改了 y 的一个元素、x 居然也变了，才发现 **view/reshape 共享内存**，它只是"同一块数据的另一种看法"。这是 PyTorch 省内存的关键设计，但也最容易踩。想要独立副本必须 `.clone()`。同样地，`torch.from_numpy()` 也是共享内存的。
  - **卡点 B**：广播规则一直靠"直觉"瞎试，`(3,1)+(1,4)` 居然得 `(3,4)` 让我愣了很久。重读第 3 节才钉死规则：**从右往左对齐维，为 1 或相等的轴可复制广播**。这个"成功了"的形状其实可能掩盖 bug——本意可能完全不同，但广播让它"跑通了"。形状错误调试，先查广播。

- **F3 术语翻译**：
  - "视图（View）" → **同一块数据换个长方形的形状来看**——没有拷贝，改一个另一个跟着变。
  - "广播（Broadcasting）" → **形状不同的数组也能一起算**——把"为 1"的那个维度假装复制几次，凑成能对齐的形状。
  - "dtype" → **每个数用几个字节存**——float32 用 4 字节（训练标准），float16 用 2 字节（GPU 加速），float64 用 8 字节（数值验证用，训练太慢）。

- **F4 回炉**：
  - **v1（错误直觉）**：以为 `y = x.view(3,4)` 之后 y 是 x 的拷贝，改 y 不影响 x。
  - **v2（修正后）**：钉死"view/reshape/from_numpy 都是**共享内存**的视图操作"——第 2 节那个实验里 `y[0,0]=999` 后 `x[0]` 也变 999，这就是共享内存的实证。diff 在于把 tensor 操作分成两类：**视图类**（view/reshape/transpose，省内存但共享数据）vs **拷贝类**（clone/contiguous，独立内存）。该用哪类取决于"你希不希望改一个影响另一个"。

<!--
元理论引用：故事即世界迭代器-元理论.md §断言 3
L2 不达标 = KL 散度未修复 = 章节在漂移而非迭代
-->
