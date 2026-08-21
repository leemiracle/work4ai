# 练习题 · 讲透 PyTorch

> 「输出倒逼输入」。按章节组织。带 ⭐ 推荐必做。建议先跑对应实验再答题。

---

## 基础（00-02）

**Q00.1** ⭐ `x.view(3,4)` 改了，`x` 会变吗？为什么？何时用 `.clone()`？

**Q01.1** ⭐ （核心）跑 `experiments/01_autograd_from_scratch.py`，用自己的话解释 `loss.backward()` 底层做了什么（拓扑排序 + 链式法则）。

**Q01.2** 为什么 `optimizer.zero_grad()` 不能省？梯度为何累积？

**Q02.1** `torch.save(model)` vs `torch.save(model.state_dict())`，为何推荐后者？

**Q01.3** ⭐ 用一句话区分"链式法则"和"反向传播"。反传一次算出的 $J^\top\bar v$ 里 $\bar v$ 是什么？为什么最终取 1？

**Q01.4** ⭐ 为什么深度学习用反向模式而非前向模式？用 $m,n$ 解释。O(N) 证明里"算 $J_i^\top\bar v$ 与前向 $c_i$ 同量级"——为什么？

**Q01.5** ⭐ 为什么 `grad.shape` 必然等于 `param.shape`？用 VJP 维度规则解释。任何"梯度形状对不上"的报错根源是什么？

**Q01.6** 跑 `experiments/15_mlp_by_hand.py`，故意把 `dL_dW2 = dL_dyhat @ a1`（漏转置），看与 autograd 差多少，体会"形状一致≠数值正确"。

---

## 训练（03-05）

**Q03.1** ⭐ 记录 loss 为何必须 `.item()`？不用的后果？

**Q03.2** 推理为何必须 `torch.no_grad()`？浪费什么？

**Q03.3** ⭐ 梯度累积时 loss 为何要除以 ACCUM_STEPS？

**Q04.1** `num_workers>0` 为何加速？代价是什么？

**Q05.1** ⭐ fp16 为何梯度下溢？bf16 为何不会？

**Q03.4** ⭐ sigmoid 深层为何训不动？ReLU + 残差如何救场？梯度裁剪能解决消失吗（为什么）？

**Q03.5** 反传算出的"原始梯度"经 Momentum 和 Adam 加工后有何不同？（跑 `experiments/18_optimizer_gradients.py`）

**Q11.1** ⭐ MSE + sigmoid 为何梯度消失？CE + sigmoid 的梯度为何是 $\hat{y}-y$？

**Q11.2** 为什么多分类永远用 `CrossEntropyLoss` 而非手动 softmax+NLL？AdamW 把 weight decay 解耦解决了什么？

---

## 性能与编译（06-07）

**Q06.1** ⭐ （核心）实验05 compile 在 CPU 上 0.72×（负收益），但实验07 显示算子从 120→85。怎么调和？

**Q06.2** 什么场景 compile 会翻车（recompile/graph break）？

**Q07.1** 自定义 `Function` 的 `forward`/`backward` 对应手写 autograd（实验01）的什么？

**Q07.2** ONNX 导出 + ORT 为何比 PyTorch eager 部署更通用？

---

## 现代 2.x（08）

**Q08.1** ⭐ SDPA 为何比手写 `softmax(QK^T/√d)` 省显存？

**Q08.2** torch.export 为何取代 TorchScript？2.10 发生了什么？

**Q08.3** ⭐ DTensor 的三种 placement（Replicate/Shard/Partial）分别对应什么集合通信？

**Q08.4** FSDP2 和 TP 各解决什么问题？为何 LLM 训练要组合？

---

## 生态（09）

**Q09.1** ⭐ 新项目做 NLP，该用 torchtext 还是 HuggingFace？为什么？

**Q09.2** torchtune 还能用来微调 LLM 吗？现在主流替代是什么？

**Q09.3** 部署到手机该用 TorchScript 还是 ExecuTorch？

---

## 综合项目（挑战）

**P.1** ⭐⭐ 用实验01 的手写 autograd，加一个 `tanh` 节点和一个 `matmul`（矩阵乘）节点，对拍 `torch.autograd`。

**P.2** ⭐⭐⭐ 写一个完整的训练脚本（Dataset→DataLoader→Module→训练循环含AMP+调度器+梯度累积→保存），在 make_moons 上训练，再用 ONNX 导出 + ORT 推理验证。这是"独立搭模型"的毕业项目。

**P.3** ⭐⭐ 用 `torch.export` 导出一个模型，对比它和 eager 的输出与速度；再查 torch.export 能否捕获带 if 控制流的模型（graph break 体验）。

**P.4** ⭐⭐⭐ 从零实现一个 1→16→16→1 的 MLP（**不用 torch，纯实验01 的 Value 类 + numpy 前向**），在 make_moons 上训练分类，记录 loss 曲线。这是"理解反传本身（而非只会调 API）"的毕业项目。

---

## 自测清单（全部能答 = 讲透）

- [ ] 能解释 `loss.backward()` 的底层（计算图 + 链式法则 + 拓扑排序）
- [ ] 能区分链式法则 vs 反传（后者是反向模式 AD），证明反传代价 O(N)
- [ ] 能用 VJP 解释 grad.shape == param.shape，手算一个 2 层 MLP 的完整反传
- [ ] 知道 `zero_grad`/`no_grad`/`detach`/`requires_grad_` 各自用途
- [ ] 能写出黄金 5 步训练循环 + 三个常见 bug
- [ ] 能解释梯度消失/爆炸的连乘根因 + 残差为何救场
- [ ] 会选损失函数（MLE 统一视角：MSE/MAE/CE 的噪声假设）和优化器（SGD→AdamW 演化）
- [ ] 会用 Dataset/DataLoader/Sampler/collate
- [ ] 懂 AMP（autocast + GradScaler，bf16 vs fp16）
- [ ] 能解释 compile 三段流水线 + 算子融合 + 何时翻车
- [ ] 知道 torch.export 取代 TorchScript、AOTInductor 部署
- [ ] 会用自定义 Function 接入 autograd
- [ ] 能走通 ONNX 导出 + ORT 推理
- [ ] 能解释 in-place/version counter/CopySlices/rebase（autograd+mutation 边界）
- [ ] 知道 reparameterization/forward-forward 等绕过/替代范式
- [ ] 知道 2.x 现代特性：SDPA/FlexAttention/DTensor/FSDP2/torchao
- [ ] 知道生态里哪些库废弃了（torchtext/torchtune/TorchScript）及替代
