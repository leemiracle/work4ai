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
