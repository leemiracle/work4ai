# 练习题 · 讲透反向传播

> 「输出倒逼输入」。按章节组织，⭐ 推荐必做。建议先跑对应实验再答题。

---

## 00-02 · 原理

**Q0.1** ⭐ 数值微分为何不能用于训练大模型？O(n) 还是 O(N) 决定它的代价？

**Q1.1** ⭐ 用一句话区分"链式法则"和"反向传播"。反传一次算出的 $J^\top\bar v$ 里 $\bar v$ 是什么？

**Q1.2** 跑 `01_autograd_from_scratch.py`，给 Value 加 sigmoid 节点，与 torch 对拍。

**Q2.1** ⭐ 为什么深度学习用反向模式而非前向模式？用 $m,n$ 解释。

**Q2.2** O(N) 证明里，"算 $J_i^\top\bar v$ 与前向 $c_i$ 同量级"——为什么？

---

## 03-04 · VJP 与手算

**Q3.1** ⭐ 为什么 `grad.shape` 必然等于 `param.shape`？用 VJP 维度规则解释。

**Q3.2** `z=Wx`，写出 $\partial L/\partial W$ 和 $\partial L/\partial x$，验证互为转置对偶。

**Q4.1** ⭐ batch=5 时，$b$ 的梯度为什么要 `.sum(axis=1)`？

**Q4.2** 把 MLP 的 ReLU 换 sigmoid，重写第 3 步反传。

**Q4.3** 跑实验03，故意把 `dL_dW2 = dL_dyhat @ a1`（漏转置），看与 autograd 差多少。

---

## 05-06 · 计算图与故障

**Q5.1** ⭐ 为什么每步要 `zero_grad()`？梯度为何累积？

**Q5.2** 写一个自定义 `torch.autograd.Function`（如 MyReLU），用 gradcheck 验证。

**Q6.1** ⭐ sigmoid 深层为何训不动？ReLU + 残差如何救场？

**Q6.2** 梯度裁剪能解决梯度消失吗？为什么？

---

## 07 · 各种梯度

**Q7.1** ⭐ 反传算出的梯度经 Momentum 和 Adam 加工后有何不同？跑实验06。

**Q7.2** 梯度惩罚（WGAN-GP）里的梯度是对参数还是对输入？

---

## 08-09 · 边界与未来

**Q8.1** ⭐ 为什么反传把 in-place 等价看待为纯计算？

**Q8.2** version counter 解决什么问题？view 的 CopySlices 做了什么？

**Q9.1** ⭐ reparameterization 如何让"采样"可微？写 VAE 的重参数化。

**Q9.2** Forward-Forward 绕过了反传的哪个约束？

---

## 综合项目（挑战）

**P.1** ⭐⭐ 用实验01 的手写 Value 类，实现一个 `matmul`（矩阵乘）节点（需要 Value 支持向量/矩阵），与 torch 对拍。

**P.2** ⭐⭐⭐ 从零实现一个 1→16→16→1 的 MLP（不用 torch，纯 Value + numpy 前向），在 make_moons 上训练分类，记录 loss 曲线。这是"理解反传"的毕业项目。

**P.3** ⭐⭐ 实现梯度检查器（不调 gradcheck）：对实验03 的每个手算梯度，用中心差分独立验证。

---

## 自测清单（全部能答 = 讲透）

- [ ] 能区分链式法则 vs 反传（后者是反向模式 AD）
- [ ] 能解释为什么 $m\ll n$ 让反向模式胜出
- [ ] 能证明反传代价 O(N)
- [ ] 能用 VJP 解释 grad.shape == param.shape
- [ ] 能手算一个 2 层 MLP 的完整反传
- [ ] 知道 zero_grad/retain_graph/detach/no_grad 的用途
- [ ] 能解释梯度消失/爆炸的连乘根因 + 残差为何救场
- [ ] 知道 Momentum/Adam 如何加工原始梯度
- [ ] 能解释 in-place/version counter/CopySlices/rebase
- [ ] 知道 reparameterization/forward-forward 等绕过/替代范式
