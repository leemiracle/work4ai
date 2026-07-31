# 08 · PyTorch 真实反传边界：mutation、view 与 CopySlices ★

> 前面讲的是"理想纯计算图"的反传。但真实代码有 in-place 修改（`x += 1`）和视图别名（`y = x[0]; y.mul_(2)`）。反传怎么不崩？这是反传在工程里**最硬核、最少被讲清**的部分（PyTorch 核心开发者 ezyang 2026 才首次用英文系统描述）。

---

## 一、反传的根本立场：只为"纯计算"求导

**反传拒绝理解 in-place，它只为"隐式的纯前向图"求导。**

```python
y = x**2; y.mul_(2)   # in-place
```
被反传**等价看待**为：
```python
y = x**2; y2 = y*2    # 纯计算, 此后 y 换成 y2
```

机制两步：① mutation 时生成新反向节点；② **就地改 `y.grad_fn`** 指向它。

实验07 实测：纯计算版和 in-place 版反传结果**完全一致**（反传不为 in-place 单独建规则）。

## 二、version counter：检测"反传用到的值被改了"

反传的安全网：每个 tensor 有 version 计数器。in-place 改它就 +1。如果反传发现"我为这个节点存的输入 version 变了"，**拒绝算**（报错而非算错）。

实验07 演示：
```
y = x²; z = sum(y); y.add_(1)   # 在非leaf y 上in-place
z.backward()  -> RuntimeError: one of the variables needed for gradient
                computation has been modified by an inplace operation
```

> 这解释了常见报错"variable modified by inplace"的根因——反传检测到缓存失效。

## 三、View + Mutation：CopySlices（最难的部分）

`v = y[0]; v.mul_(2)` 只改 y 的一行。`y.grad_fn` 不能是普通 `MulBackward`（那相当于整个 y 乘2）。解法是 **`CopySlices`** 复合反向节点——把 `select_scatter→mul→select` 链打包成一个节点。

**ezyang 的点睛比喻**：视图本质是 **lens**（函数式编程的透镜），总有 putback 把修改 scatter 回 base。这个纯函数解释有反向，反向节点就是 CopySlices。

实验07 实测：view mutation 后梯度正确（第0行 4x，第1行 2x），`v.grad_fn` 显示 `AsStridedBackward0`（rebase 到新节点）。

## 四、rebase history 与惰性 rebase

- **rebase**：mutation 后，view 的 `grad_fn` 重挂到 base 的新 CopySlices 节点之上（避免重复算）。
- **多别名的惰性 rebase**（精妙设计）：`v1=y[0,:]; v2=y[:,0]; v1.mul_(2)` 时怎么知道要更新 v2？让 base 跟踪所有 view 的方案被否决（内存循环引用 + 多线程争用）。改用**惰性 rebase**：在 v2 的 `grad_fn` 记 parent version，访问时检查，过期按需重算。

> 🎯 **设计哲学**：PyTorch 选择"拒绝全局 view 跟踪表"，换来无锁、无循环引用、内存可控。代价是 rebase 的惰性 + version 机制。这是工程权衡典范——用一点算法复杂度换并发安全与内存简洁。

## 五、detach：断梯度但不断 version

`y.detach()` 把 tensor 摘下当普通数据（`requires_grad=False`），但**仍共享 version counter**。所以 detach 后 in-place 仍能被反传安全网检测到。

## 六、为什么这是"数学反传"到"PyTorch backward"的鸿沟

| 数学反传（理想）| PyTorch backward（工程）|
|--------------|----------------------|
| 纯函数、无 mutation | 必须处理 in-place、view 别名 |
| 梯度直接算 | 用 version counter 防过期 |
| 节点固定 | CopySlices + rebase + 惰性 rebase |

过了这层，才算真懂 PyTorch 的 `backward()`——它不只是 VJP，还解决了真实代码里 mutation/aliasing 带来的所有边界。

## 七、代码层

```bash
cd experiments && python3 07_mutation_views.py
```

演示：in-place 等价纯计算、version counter 报错、view 的 CopySlices 正确梯度、detach 行为。

---

## 📌 下一步

[09-边界与未来.md](09-边界与未来.md)：反传的局限——不可微操作怎么绕过、有没有替代反传的范式。

## ✍️ 练习

1. 为什么反传把 in-place 等价看待为纯计算？这给它带来什么简化？
2. version counter 解决什么问题？没有它会怎样？
3. `v = y[0]; v.mul_(2)`，为什么 `y.grad_fn` 不能是 `MulBackward`？CopySlices 做了什么？
4. detach 后 in-place 还会被反传检测到吗？为什么？
