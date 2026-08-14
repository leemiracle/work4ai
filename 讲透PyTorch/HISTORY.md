# 讲透PyTorch · 思想史

> 所有其他章节讲"PyTorch 怎么用"，本文问"**为什么是 PyTorch 赢了**"——这需要一部深度学习框架的思想史。从 1987 年 Lush 到 2026 年 JAX，框架的兴衰史不是技术优劣的线性叙事，而是**研究范式、开发者体验、公司政治、历史偶然**交织的复杂动力学。

---

## 0. 方法论

> 承接 [`讲透AI历史/00-为什么学AI历史`](../讲透AI历史/00-为什么学AI历史.md) 的思想史方法论。

**年代史**（教科书做法）：Lush 1987 → Torch 2002 → Theano 2010 → Caffe 2013 → TensorFlow 2015 → PyTorch 2016 → JAX 2018 → PyTorch 2.0 2022。

**问题**：这不告诉你"为什么是 PyTorch 赢了"、"为什么 Google 投入两个框架（TF + JAX）都没拿下研究社区"、"为什么静态图先出现但最终输给动态图"。

**思想史**（本文做法）——问五个核心问题：

1. **为什么此时此地？** 为什么 2016 年而不是 2006 年出现 eager 框架？
2. **为什么这个赢？** PyTorch 的胜利是技术必然还是历史偶然？
3. **为什么那个输？** MXNet/Caffe/Theano 的失败教训是什么？
4. **谁影响了谁？** Torch→PyTorch 的血脉、Autograd→JAX 的血脉。
5. **当前的偶然性**：如果 HuggingFace 当年选了 TF 后端，今天格局会怎样？

> 🎯 **博士级核心**：框架史 = **eager（命令式）vs symbolic（声明式）的范式之争**——这不是技术细节，是**计算范式的哲学分歧**，堪比编程语言中命令式 vs 函数式的百年论战。

---

## 1. 前夜：Lush / Torch 2002

### 1.1 Lush（1987）——一切的开端

1987 年，Yann LeCun 和 Léon Bottou 在 AT&T Bell Labs 开发了一种叫 **Lush** 的语言——一个 Lisp 方言，专为数值计算和机器学习设计。LeCun 1989 年发明的 LeNet（第一个卷积神经网络）就是在 Lush 的前身 `SN3` 上实现的。

**思想史意义**：Lush 确立了一个深刻的设计哲学——**ML 需要一种"可微分"的语言**，计算即图、梯度即反向遍历图。这个思想贯穿了之后所有框架。但 Lush 用的是 Lisp，注定了它只能在小圈子里流行。

### 1.2 Torch（2002）——框架的雏形

2002 年，Ronan Collobert 和 Samy Bengio 在瑞士 IDIAP 研究所（隶属于 EPFL）发布了 **Torch**。核心设计：

- **Lua** 脚本层 + **C/C++** 计算核心
- Tensor 操作 + 可微分计算图
- 模块化的 `nn` 库（`nn.Module` 概念的鼻祖）

Torch 在 2000s 被DeepMind、Facebook AI、Twitter 等大量使用。LeCun 在 NYU、Hinton 在 Toronto 都用过它。

**为什么是 Lua 而不是 Python？** 2002 年，Python 还没有 NumPy（2006 年才合并 Numarray/Numarray），科学计算生态几乎为零。Lua 嵌入 C 极其简单，是当时合理的工程选择。但这个选择成了 Torch 后来最大的包袱——**研究者不想学一门新的脚本语言**。

> 🎯 **路径依赖第一课**：Torch 选择了 Lua（2002 年的合理选择），但这个选择在 Python 科学计算生态爆发后（2006-2010）成了致命缺陷。**技术选型的时间窗口比选型本身更重要**。

---

## 2. Theano / Caffe 时代（2010-2015）

### 2.1 Theano（2007-2010）——符号微分的革命

Theano 由蒙特利尔大学 MILA 实验室（Yoshua Bengio 组）的 Frédéric Bastien、James Bergstra、Olivier Breuleux、Pascal Lamblin 等人开发，2007 年开始，2010 年前后公开发布。

**核心思想**：用 Python 写数学表达式，Theano 自动构建计算图并**符号求导**。这意味着你只需要写前向传播，梯度自动计算——这是**自动微分（autodiff）在深度学习中的第一次系统化落地**。

Theano 的设计哲学是 **define-then-run**（先定义计算图，再执行）：

```python
# Theano 风格（伪代码）
x = T.matrix('x')
y = T.matrix('y')
z = T.dot(x, y) + T.sum(x)
f = theano.function([x, y], z)  # 编译成计算图
result = f(data_x, data_y)       # 执行
```

**优点**：自动求导、符号优化、GPU 支持。
**缺点**：调试地狱——报错指向编译后的 C 代码而非你的 Python 代码；编译慢。

Theano 是当时学术界最流行的框架——Bengio 组几乎所有论文都用它。但它有致命的工程问题：**性能优化不够激进**、**文档差**、**部署支持弱**。

> 🎯 **Theano 的遗产**：虽然 Theano 本身"死"了（2017 年宣布停止开发），但它的核心设计——**自动微分 + Python 前端 + 计算图**——被 TensorFlow 和 PyTorch 同时继承。Theano 是"**思想之父**"，虽然不是"**产品之胜**"。

### 2.2 Caffe（2013）——工程化的胜利

2013 年，UC Berkeley 的博士生 Yangqing Jia 在贾扬清的 BVLC 实验室开发了 **Caffe**。

Caffe 的哲学与 Theano 截然相反：

- **C++ 核心**，不依赖 Python（只提供 Python 绑定）
- **配置文件驱动**：网络结构用 `prototxt` 定义，不需要写代码
- **CNN 专用**：内置卷积、池化等标准层，开箱即用
- **速度极快**：精调的 C++/CUDA 内核

Caffe 是 ImageNet 时代的王者——AlexNet、VGG、GoogLeNet、ResNet 的原始论文都用 Caffe 复现。

**为什么 Caffe 后来衰落了？** 因为它是**声明式配置**——网络结构写在一堆 `.prototxt` 文件里。当你想写一个 Caffe 没有内置的新层，必须回到 C++ 源码加 `Layer` 类、重新编译。这在 2013 年的"标准 CNN"时代没问题，但在 2015 年 Transformer 出现、模型开始有复杂控制流时，成了致命瓶颈。

> 🎯 **Caffe 的教训**：**框架的抽象层级决定其寿命**。Caffe 的抽象太低（配置文件 + 固定 Layer 类型），适应不了模型复杂度的指数增长。框架必须有足够的**表达力**让研究者用脚本语言定义任意计算。

### 2.3 这个时代的格局（2013-2015）

| 框架 | 语言 | 范式 | 主要用户 | 优势 | 致命弱点 |
|------|------|------|---------|------|---------|
| Theano | Python | define-then-run | 学术界（MILA 系） | 自动求导 | 性能差、调试地狱 |
| Caffe | C++/prototxt | 配置文件 | CV 学术界 | 极快 | 扩展性差 |
| Torch | Lua/C | define-by-run | 工业界（DeepMind/Meta） | 灵活 | Lua 小众 |

三方各有软肋，谁也没有绝对统治力。这个僵局被一个变量打破：**Google Brain 决定做自己的框架**。

---

## 3. 第一次范式转移：TensorFlow 2015（symbolic / eager 之争）

### 3.1 TensorFlow 的诞生

2015 年 11 月，Google 开源了 **TensorFlow**——由 Google Brain 团队的 Martín Abadi、Ashish Agarwal、Paul Barham 等人开发。TF 基于 Google 内部的 **DistBelief**（2011 年的第一代系统），继承了"**静态计算图 + 分布式训练**"的设计哲学。

TF 一发布就**爆炸性增长**——2015 年底到 2016 年，GitHub star 数从 0 飙到 5 万+。原因：

1. **Google 的品牌背书**——"Google 用的东西肯定好"
2. **分布式训练原生支持**——当时没有框架能轻松做多机多卡
3. **TensorBoard 可视化**——第一个像样的训练可视化工具
4. **部署生态**（TF Serving）——训练→部署完整链路

### 3.2 静态图的诅咒

TF 1.x 采用 **define-then-run** 范式：

```python
# TF 1.x 风格
x = tf.placeholder(tf.float32, [None, 784])
W = tf.Variable(tf.zeros([784, 10]))
y = tf.nn.softmax(tf.matmul(x, W))
with tf.Session() as sess:
    sess.run(tf.global_variables_initializer())
    result = sess.run(y, feed_dict={x: data})  # 才真正执行
```

**优点**（从系统工程师角度）：编译器看全图，能做激进的优化（常量折叠、内存复用、自动并行化）；部署时图可以序列化到任何语言。

**缺点**（从研究者角度）：

1. **调试地狱**：想 print 一个中间值？你不能——图还没执行。必须 `sess.run()` 才能拿到值。
2. **控制流笨拙**：想写一个 if/else？用 `tf.cond()`。想写 for 循环？用 `tf.while_loop()`。这些"图操作"和 Python 原生控制流不兼容。
3. **Session 概念难以理解**：初学者最大的困惑是"为什么我定义了变量却不能直接看它的值？"

> 🎯 **思想史核心洞察**：TF 的失败不是因为"技术差"——它的静态图在**系统优化**层面确实更强。它失败是因为**忽略了一个关键变量：研究者的体验**。研究者每天做的事情是"试新想法→看结果→调代码→再试"，这个循环的**速度**比绝对性能重要 10 倍。TF 优化了错误的指标。

### 3.3 Keras——救不了的简化

2015 年 3 月，Google 工程师 François Chollet 发布了 **Keras**——一个在 TF/Theano/CNTK 之上的高级 API：

```python
# Keras 风格
model = Sequential([Dense(512, activation='relu'), Dense(10, activation='softmax')])
model.compile(optimizer='adam', loss='categorical_crossentropy')
model.fit(x_train, y_train)  # 一行训练！
```

Keras 极大降低了入门门槛，在 2016-2018 年成为最流行的高层 API。但 Keras 有根本局限：**它封装了 TF 的复杂性，也封装了 TF 的灵活性**。想做任何非标准操作（自定义损失、复杂架构），就必须穿透 Keras 到达 TF 的底层 API——而这个底层 API 就是 TF 的地狱。

> 🎯 **Keras 的悖论**：越是把复杂性藏起来，用户遇到不藏得住的场景时就越痛苦。Keras 证明了一个框架设计原则——**简单性不能靠隐藏复杂性实现，必须从根本上简化复杂性**。这正是后来 PyTorch 的哲学。

---

## 4. 第二次范式转移：PyTorch 2016

### 4.1 PyTorch 的诞生

2016 年初，Facebook AI Research（FAIR）的 **Soumith Chintala**、**Adam Paszke**、**Sam Gross** 等人开始了一个新项目：把 Torch 的计算核心（Caffe2 的 tensor 库 + ATen）移植到 Python 前端，保留 Torch 的 **define-by-run**（eager）哲学。

2017 年 1 月，**PyTorch 0.1** 发布。核心设计决策：

1. **Python 优先**——不是 Lua、不是 C++、不是配置文件
2. **Eager 执行（define-by-run）**——每次 `forward` 就是普通 Python 执行
3. **动态计算图**——每次前向都构建新图，支持任意 Python 控制流
4. **Autograd**——自动微分引擎，但**在 eager 模式下工作**

```python
# PyTorch 风格
x = torch.randn(100, 784, requires_grad=True)
W = torch.zeros(784, 10, requires_grad=True)
y = torch.softmax(x @ W, dim=1)  # 直接执行！可以 print、可以 debug
loss = F.cross_entropy(y, labels)
loss.backward()  # 自动求导
print(W.grad)     # 直接看梯度！
```

### 4.2 为什么 PyTorch "赢"了

PyTorch 从 2017 到 2019 年完成了一次奇迹般的逆转。NeurIPS 论文中使用 PyTorch 的比例从 2017 年的 ~10% 飙升到 2019 年的 ~70%，同时 TF 从 50% 跌到 ~20%。

**原因不是 PyTorch 更快或更强大**——TF 1.x 在生产部署、分布式训练上依然更强。原因是一个朴素的事实：

> **研究者第一关心的是"我的代码好不好调"，不是"跑得多快"。**

PyTorch 的 eager 模式意味着：

- `print(tensor)` 直接看值——TF 1.x 做不到
- Python 断点（`pdb.set_trace()`）直接在 `forward` 里下——TF 1.x 做不到
- `if`/`for` 写原生 Python——TF 1.x 要写 `tf.cond`
- 错误信息指向你的 Python 代码——TF 1.x 指向编译后的 C++

**论文实验的生命周期是"天"不是"周"**——每个 idea 要试 10-100 次。如果每次调试省 30 分钟，100 次就是 50 小时。研究者用脚投票了。

### 4.3 与 Torch 7 的关系

PyTorch 不是从零写的——它**继承了 Torch 的血脉**：

- **ATen**（C++ tensor 库）来自 Caffe2/Torch
- **`nn.Module`** 概念直接来自 Torch 的 `nn` 库
- **设计哲学**（define-by-run）来自 Torch

PyTorch 的名字 = **Python + Torch**。它的本质是：**Torch 的灵魂 + Python 的身体**。Sam Gross 做了大量底层 C++ 工作，把 Lua 接口替换成 Python 绑定。

> 🎯 **路径依赖第二课**：PyTorch 不是"全新发明"，是"**正确语言 + 正确时机 + 已验证哲学**"。Torch 2002 年就证明了 define-by-run 的有效性，只是选错了语言。PyTorch = Torch 的"语言迁移"。

---

## 5. TF vs PyTorch 大战

### 5.1 时间线

| 时间 | TF 份额（NeurIPS） | PyTorch 份额 | 关键事件 |
|------|-------------------|-------------|---------|
| 2016 | ~15%（Theano 为主） | 0% | TF 发布 |
| 2017 | ~50% | ~10% | PyTorch 发布 |
| 2018 | ~45% | ~30% | TF 2.0 宣布 eager；HuggingFace 选 PyTorch |
| 2019 | ~20% | ~70% | **逆转完成** |
| 2020 | ~10% | ~80% | TF 2.x 未能挽回 |

### 5.2 Google 的应对：TF 2.0（2019）

面对 PyTorch 的攻势，Google 在 2019 年发布了 **TensorFlow 2.0**，做出了根本性的让步：

- **默认 eager 执行**（`tf.function` 装饰器才进入图模式）
- **Keras 成为一等公民**（不再是可选的高层 API）
- **删除了大量 TF 1.x API**（`Session`、`placeholder`、`feed_dict` 全部废弃）

**问题**：TF 2.0 的 eager 不是真正的 eager——它是**"eager 的外观 + 图模式的内核"**。`@tf.function` 装饰器会在背后用 `AutoGraph` 把 Python 代码转成计算图，导致：

1. **隐式行为**：同一段代码有没有 `@tf.function` 行为完全不同
2. **调试反而更难**：eager 和 graph 两种模式切换，报错信息混乱
3. **生态迁移成本**：TF 1.x → 2.0 的迁移是**破坏性的**，大量代码要重写

> 🎯 **TF 2.0 失败的本质**：你不能用"加一层 eager 壳"来修复一个"以静态图为根基"的系统。PyTorch 从第一天就是 eager-native，每一个 API、每一个数据结构都为 eager 设计。TF 2.0 是**后天改造**，基因不对。

### 5.3 为什么 Google 输了

Google 拥有：无限资源、顶级工程师、DistBelief 十年积累、TensorBoard、TFX 全栈、TPU 硬件。为什么输了？

**三个原因**：

1. **研究者 vs 工程师的优先级冲突**：TF 优先服务 Google 内部的生产系统（广告、搜索、翻译），研究者需求排第二。PyTorch 优先服务 FAIR 研究者，生产需求后来才追。
2. **API 稳定性**：TF 从 1.x → 2.0 是破坏性变更。PyTorch 从 0.1 → 1.14 几乎完全向后兼容。研究者最恨的就是"半年前的代码跑不了了"。
3. **社区策略**：Google 试图控制 TF 的一切（官方教程、认证、Cloud）。PyTorch 社区更开放——第三方库（fast.ai、HuggingFace、Detectron2）反而是卖点。

> 🎯 **博士级洞察**：框架战争的本质不是"哪个框架更好"，而是"**谁来定义更好的标准**"。研究者用脚投票，他们的标准是"调试体验"而非"系统性能"。Google 把 TF 当系统软件来做，Meta 把 PyTorch当研究工具来做——**受众定位错了，技术再强也赢不了**。

---

## 6. 第三次范式转移：HuggingFace + PyTorch 生态（2018-）

### 6.1 HuggingFace Transformers——"PyTorch 生态的 App Store"

2018 年，HuggingFace 发布了 `pytorch-pretrained-bERT`（后改名 `transformers`）。这个库做了三件事：

1. **把 BERT 等模型的开源复现做到"一行代码下载、一行代码推理"**
2. **统一 API**：所有模型用相同的接口（`from_pretrained()` / `save_pretrained()`）
3. **模型仓库**：任何人可以上传/下载预训练模型

关键决策：**最初只支持 PyTorch 后端**。这意味着：

- 所有想用 BERT/GPT 的研究者**必须装 PyTorch**
- 所有新模型的社区复现**默认用 PyTorch**
- HuggingFace 成了 PyTorch 生态的"杀手级应用"

> 🎯 **HuggingFace 的乘数效应**：2018 年 BERT 发布后，NLP 进入了"预训练 + 微调"范式。HuggingFace 让这个范式的工程成本趋近于零——而它绑定 PyTorch。这不是技术决策，是**生态战略**——HuggingFace 团队认为 PyTorch 的 eager + 动态图更适合快速复现新模型。

### 6.2 PyTorch Lightning（2018）

2018 年，William Falcon 发布了 **PyTorch Lightning**——一个在 PyTorch 之上的"研究框架"：

- 封装训练循环（`Trainer`）
- 封装分布式（DDP/FSDP）
- 封装日志/检查点/mixed precision
- **保持研究者完全控制模型代码**（`LightningModule`）

Lightning 的哲学和 Keras 完全不同：Keras 隐藏复杂性，Lightning **抽象样板代码但保留灵活性**。研究者只需要写 `training_step()`、`configure_optimizers()`，其余由 Lightning 处理。

### 6.3 ONNX（2017）——"统一部署层"

2017 年 9 月，Facebook 和 Microsoft 联合发布了 **ONNX**（Open Neural Network Exchange）——一个跨框架的模型表示格式。

**初衷**：不管你用 TF/PyTorch/MXNet/Caffe2 训练，都可以导出成 ONNX，然后在任何推理引擎（ONNX Runtime、TensorRT、CoreML）上运行。

**现实**：ONNX 成功地成为了**部署标准**（至今仍是），但从未实现真正的**框架互操作**——没有人"在 TF 里训练然后导到 PyTorch 里继续训练"。ONNX 的价值被收窄到了"训练→部署"的单向通道。

> 🎯 **ONNX 的反常识**：它最初想做"框架间的 Rosetta Stone"，结果成了"部署的 lingua franca"。**技术在落地时往往偏离其设计目标**——这本身就是路径依赖的一个案例。

### 6.4 其他生态组件

| 年份 | 项目 | 作用 |
|------|------|------|
| 2018 | fast.ai | PyTorch 之上的教学框架（Jeremy Howard）|
| 2018 | Detectron2 | FAIR 的目标检测框架 |
| 2019 | vLLM | LLM 高吞吐推理（后转入 PyTorch Foundation）|
| 2020 | PyTorch Geometric | 图神经网络事实标准 |
| 2021 | timm | CV 模型全集（Ross Wightman）|

---

## 7. 第四次范式转移：JAX 函数式（2018-）

### 7.1 JAX 的起源

JAX 的前身是 **Autograd**（2014-2016）——Dougal Maclaurin 和 Matthew Johnson 在 Harvard 时开发的一个 Python 自动微分库。Autograd 的核心思想：**用 Python 的 trace 机制对**任何** NumPy 代码做自动求导**——不需要计算图，不需要 define-then-run。

2018 年，Google 的 Chris Leary、Roy Frostig、Matthew Johnson、Dougal Maclaurin 在 Autograd 基础上开发了 **JAX**（Just After eXecution）。核心设计：

```python
# JAX 风格——纯函数式
def loss_fn(params, x):
    return jnp.mean((model(params, x) - y) ** 2)

grad_fn = jax.grad(loss_fn)      # 对 loss_fn 自动求导
grad_fn = jax.jit(grad_fn)       # JIT 编译
grad_fn = jax.vmap(grad_fn)      # 自动向量化
```

**JAX 的四大基石**：

1. **`grad`**：自动微分（对**任何**可微函数）
2. **`jit`**：即时编译（XLA 后端）
3. **`vmap`**：自动向量化（把单样本函数变成批量函数）
4. **`pmap`**：自动并行化（跨设备）

### 7.2 JAX vs PyTorch——哲学分歧

| 维度 | PyTorch | JAX |
|------|---------|-----|
| 范式 | 面向对象 + 命令式 | 函数式 + 声明式 |
| 状态 | 可变（`nn.Module` 持有参数）| 不可变（参数是显式传入的 pytree）|
| 控制流 | 原生 Python if/for | `lax.cond` / `lax.scan`（结构化控制流）|
| 求导 | `loss.backward()`（原地写梯度）| `jax.grad(f)`（返回新函数）|
| 心智模型 | "我有一个有状态的对象" | "我有一个纯函数 + 参数" |

**JAX 的核心洞察**：如果你把计算写成**纯函数**（输入→输出，无副作用），那么：

- **求导**就是函数变换（`grad(f)` 返回新函数）
- **编译**就是函数优化（`jit(f)` 返回编译后的函数）
- **并行**就是函数映射（`pmap(f)` 返回分布式函数）
- **向量化**就是函数提升（`vmap(f)` 返回批量函数）

四种能力统一在"函数变换"这一个概念下——这是**函数式编程的优雅**。

### 7.3 Flax 与 Optax

JAX 本身只是一个底层的 NumPy + autodiff + transform 库——它没有 `nn.Module`、没有优化器、没有数据加载器。这意味着你需要高层库：

- **Flax**（2020，Google）：神经网络库（`linen.Module`），提供 `nn.Module` 的函数式版本——**参数是外部的，模块是无状态的**
- **Optax**：梯度处理和优化器库
- **Distrax**：概率分布
- **Chex**：测试工具

### 7.4 JAX 在前沿实验室的崛起

虽然 JAX 在学术界整体份额远低于 PyTorch（~5-10% vs ~80%），但它在**前沿实验室**中拥有极高的使用率：

- **Google DeepMind**：内部主力框架，AlphaFold/AlphaCode/Gemini 训练用 JAX
- **Google Research**：PaLM/Gemini 用 JAX（配合 TPU）
- **Anthropic**：Claude 的部分训练基础设施用 JAX
- **xAI**：Grok 使用 JAX

**原因**：在**超大规模训练**（千亿参数）场景下，JAX 的 `pmap`/`pjit` + TPU/XLA 组合比 PyTorch 的分布式更易用。PyTorch 的 DDP/FSDP 需要手动管理通信，而 JAX 的 SPMD（Single Program Multiple Data）编译器可以**自动推导分片策略**。

> 🎯 **JAX 的悖论**：研究社区整体选择了 PyTorch（因为简单），但**最前沿的实验室选择了 JAX**（因为可组合性）。这说明"最好用"和"最强大"不是同一个维度——**研究社区的选型标准 ≠ 前沿实验室的选型标准**。

---

## 8. 第五次范式转移：PyTorch 2.0 / Compile（2022-）

### 8.1 PyTorch 的"静态图回归"

2022 年 12 月，PyTorch 团队宣布了 **PyTorch 2.0**（2023 年 3 月正式发布）。核心特性：**`torch.compile`**。

这看似是一个普通的版本升级，实际上是一次**范式转移**：PyTorch 在保持 eager 接口的同时，在背后引入了**图捕获 + 编译优化**——也就是 PyTorch 曾经反对的"静态图"技术。

### 8.2 技术架构：TorchDynamo + Inductor

```
Python 代码 → TorchDynamo（字节码跟踪）→ FX 静态图 → AOTAutograd（前向+反向联合优化）→ TorchInductor（代码生成）→ Triton kernel / C++
```

- **TorchDynamo**：用 `sys.settrace` 在运行时跟踪 Python 字节码，在不改变用户代码的前提下抓取计算图
- **AOTAutograd**：把前向图和反向图一起优化（eager 模式下做不到的）
- **TorchInductor**：后端代码生成器，GPU 生成 Triton kernel，CPU 生成 C++/OpenMP

### 8.3 为什么这是"范式转移"

PyTorch 2.0 的本质是**黑格尔辩证法的合题**：

```
正题：Theano/TF（静态图，优化强但调试差）
反题：PyTorch 0.1-1.x（动态图，调试好但优化弱）
合题：PyTorch 2.0（动态图接口 + 静态图优化，eager 外观 + compile 内核）
```

PyTorch 2.0 用**运行时图捕获**（Dynamo）实现了"eager 的易用性 + symbolic 的性能"——这是 Theano 时代就想做但做不到的事（当时没有字节码跟踪技术）。

> 🎯 **思想史洞察**：eager vs symbolic 不是"谁对谁错"，而是"**哪个更基础的抽象层**"。PyTorch 2.0 证明了：**正确的架构是 eager 在底层、compile 在上层**——用户看到 eager，编译器看到 graph。TF 的错误是搞反了：graph 在底层，eager 是后来加的壳。

### 8.4 Karpathy 的 micrograd / tinygrad

2020 年，Andrej Karpathy 发布了 **micrograd**——一个约 100 行 Python 代码的自动微分引擎。同一年，George Hotz（comma.ai 创始人）发布了 **tinygrad**——一个极简的深度学习框架。

这两个项目的思想史意义：

1. **micrograd** 证明了 autograd 的核心（反向传播 + 计算图）可以用 <100 行讲清楚——**框架的本质极简**，复杂度来自工程而非原理
2. **tinygrad** 试图用极简设计挑战 PyTorch/TF 的臃肿——虽然未成主流，但影响了框架社区的"减法"思潮

> 🎯 **micrograd 的哲学**：Karpathy 说"**如果你不能手写一个 autograd，你就没真正理解深度学习**"。这与本系列 [01-Autograd](01-Autograd与计算图.md) 的精神完全一致——90 行手写 autograd 看穿计算图。

---

## 9. 2026 框架生态现状

### 9.1 格局图

```
                    研究社区（学术论文）
                    ┌─────────────┐
                    │  PyTorch    │ ~80%
                    │  JAX        │ ~10%
                    │  TF/Keras   │ ~5%
                    │  其他       │ ~5%
                    └─────────────┘

                    前沿实验室（千亿模型）
                    ┌─────────────┐
                    │  JAX+TPU    │ Google/DeepMind/Anthropic
                    │  PyTorch+GPU│ Meta/Mistral/多数实验室
                    └─────────────┘

                    生产部署
                    ┌─────────────┐
                    │  ONNX       │ 跨框架部署标准
                    │  TF Serving │ Google 生态
                    │  PyTorch export | 新兴
                    │  TensorRT   │ NVIDIA GPU 部署
                    └─────────────┘
```

### 9.2 2024-2026 关键事件

| 时间 | 事件 | 意义 |
|------|------|------|
| 2023 | PyTorch Foundation 成立（Linux Foundation 托管）| 从 Meta 项目变为社区项目 |
| 2024 | **TorchTitan** 发布 | 大规模 LLM 训练参考实现（FSDP2/TP）|
| 2024 | **TorchTune**（后转社区维护）| LLM 微调（LoRA/QLoRA）|
| 2024 | **JAX 在 Anthropic 内部广泛使用** | Claude 训练基础设施 |
| 2025 | PyTorch 2.10：TorchScript 正式废弃 | 2.x 编译化完成 |
| 2025 | **Keras 3.0** 支持多后端（JAX/TF/PyTorch）| Keras 的"后端中立"策略 |
| 2026 | **DTensor 重构**（ezyang 博客揭示）| PyTorch 分布式向 JAX SPMD 学习 |

### 9.3 当前趋势

1. **PyTorch 编译化**：`torch.compile` → `torch.export` → AOTInductor，从 JIT 走向 AOT
2. **JAX 工程化**：Flax/Optax 成熟，jax.ai 生态扩展，但入门门槛仍高
3. **融合趋势**：Keras 3 多后端、ONNX 持续扩展、PyTorch DTensor 学习 JAX SPMD
4. **LLM 专用工具链**：vLLM（推理）、torchtitan（训练）、lit-gpt（微调）从通用框架中独立

---

## 10. 思想史反思：五个反常识

### 反常识 1：Eager 赢了，但 Eager 是"理论上更差"的范式

静态图（symbolic）在**编译优化**上严格优于动态图（eager）——这是编译器理论的基本共识。静态图能做常量折叠、内存复用、自动并行、全局优化；动态图什么都做不了（每次都是新图）。

**那为什么 eager 赢了？** 因为**研究者的循环时间**比训练时间更重要。一个 idea 从代码到结果：

- TF 1.x：写图 → 编译 → 调试报错（指向 C++）→ 修代码 → 重新编译 → ~1 天
- PyTorch：写 Python → 直接跑 → print 看 → 改 → ~1 小时

**博士级教训**：技术优越性 ≠ 用户选择。**"好调试"比"好优化"重要 10 倍**——除非你的用户是生产工程师。PyTorch 2.0 的 compile 正是在不牺牲调试体验的前提下，把优化"偷偷加回来"。

### 反常识 2：Google 投了两个框架（TF + JAX），两个都没赢

Google 拥有：TF（生产级框架）+ JAX（研究级框架）+ TPU（专用硬件）+ 无限资源。但它没有拿下研究社区。

**原因**：**TF 和 JAX 定位分裂**。TF 面向生产，JAX 面向研究——但研究者既要做研究又要发论文做开源，JAX 门槛太高（函数式 + TPU 优先），TF 调试太痛苦。两个框架**没有一个是"恰好好用的"**。

而 PyTorch **恰好是研究者想要的那个甜蜜点**——够灵活、够好调、够 Pythonic。Meta 不需要两个框架，只需要一个**做对的**。

> 🎯 **战略洞察**：资源不是优势，**聚焦**才是。Google 的"双框架策略"分散了社区注意力；Meta 的"单框架 + 极致研究者体验"聚焦了社区共识。

### 反常识 3：ONNX 没有实现"框架统一"，但实现了"部署统一"

ONNX 的设计目标是：任何框架训练 → ONNX → 任何引擎推理。**前半句实现了**（TF/PyTorch/MXNet 都能导出 ONNX），**后半句也实现了**（ONNX Runtime/TensorRT/CoreML 都能跑 ONNX）。

但人们期待的"框架互操作"（TF 训练 → PyTorch 继续训练）从未发生——因为**训练是一个有状态的、框架耦合的过程**，而推理是一个无状态的、标准化的过程。ONNX 适合后者，不适合前者。

> 🎯 **教训**：**抽象层次决定可行性**。部署可以标准化（因为计算图已确定），训练不能标准化（因为梯度流、优化器状态、分布式策略都耦合到框架内部）。

### 反常识 4：HuggingFace（一个创业公司）比框架本身更决定格局

2018 年 HuggingFace 选择 PyTorch 作为 `transformers` 的唯一后端。这个**一个商业决策**，可能比 PyTorch 本身的技术决策更深刻地改变了框架格局。

原因：NLP 研究者在 2018-2020 年**必须**用 HuggingFace（没有替代品）→ 必须用 PyTorch → PyTorch 份额飙升 → 新模型默认 PyTorch 复现 → 正反馈循环。

**如果一个创业公司的后端选择能决定一个框架的胜负，说明框架竞争已经进入了"生态阶段"**——不是"谁的核心更好"，而是"谁的生态更繁荣"。

### 反常识 5：PyTorch 2.0 证明了"eager 赢了"但不代表"eager 是终局"

PyTorch 2.0 的 `torch.compile` 本质上是**把静态图优化"走私"进 eager 框架**。这说明：

- **Eager 是正确的用户接口**（调试体验好）
- **Symbolic 是正确的编译器接口**（优化能力强）
- **终极方案 = Eager 外观 + Symbolic 内核**

这不是 PyTorch 的发明——JAX 从第一天就是这个架构（Python 函数 + XLA 编译）。**PyTorch 2.0 在架构上"追上了" JAX**，只是用了不同的实现路径（Dynamo 字节码跟踪 vs JAX 的函数式 trace）。

> 🎯 **博士级洞察**：框架史的终局不是"eager vs symbolic"，而是**"eager 作为语法糖，编译器作为运行时"**。这和编程语言的演化一模一样——Python 是解释型的外观，但 PyPy/Numba/Cython 在背后做 JIT 编译。

---

## 11. 关键人物 / 机构谱系

### 11.1 血统图

```
Lush (1987)                    Autograd (2014)
  LeCun/Bottou                    Maclaurin/Johnson
     │                               │
  Torch (2002)                   JAX (2018)
  Collobert/Bengio              Frostig/Leary/Google
     │                               │
  ┌──┴──┐                        Flax (2020)
  │     │                        Google
  │  Caffe2                       │
  │  Jia/Meta                  当前：Google/DeepMind/Anthropic
  │     │
  └──┬──┘
     │
  PyTorch (2017)
  Chintala/Paszke/Gross
     │
  ┌──┴──────────────┐
  │                 │
  HuggingFace     PyTorch 2.0 (2023)
  (2018)          compile/Dynamo
  Wolf et al.     Ansel et al.

Theano (2007)        TensorFlow (2015)
  Bergstra/Bastien     Abadi/Google
  Bengio/MILA            │
     │                 Keras (2015)
     └→ 影响 →        Chollet
       TF + PyTorch      │
                        TF 2.0 (2019) → 失败
```

### 11.2 关键人物

| 人物 | 贡献 | 机构 |
|------|------|------|
| Yann LeCun | Lush → Torch 的血脉源头 | NYU/Meta |
| Léon Bottou | Lush 联合开发 | Meta/INRIA |
| Ronan Collobert | Torch 创始人 | IDIAP/NYU |
| Yoshua Bengio | Theano + Torch 学术背书 | MILA |
| James Bergstra | Theano 架构设计 | MILA |
| Frédéric Bastien | Theano 核心实现 | MILA |
| Yangqing Jia | Caffe 创始人 | UC Berkeley/Google |
| Martín Abadi | TensorFlow 论文一作 | Google |
| François Chollet | Keras 创始人 | Google |
| **Soumith Chintala** | PyTorch 联合创始人/社区领袖 | Meta |
| **Adam Paszke** | PyTorch 核心架构/Autograd | Meta |
| Sam Gross | PyTorch C++ 底层/ATen | Meta |
| William Falcon | PyTorch Lightning | Lightning AI |
| Thomas Wolf | HuggingFace Transformers | HuggingFace |
| **Roy Frostig** | JAX 核心开发者 | Google |
| **Chris Leary** | JAX 核心开发者 | Google |
| Andrej Karpathy | micrograd | OpenAI/Tesla/Eureka Labs |
| Edward Yang (ezyang) | PyTorch 内核/dispatcher/DTensor | Meta |

---

## 12. 失败方向（MXNet 等）

### 12.1 MXNet——"性能最好的失败者"

MXNet 由 Chen Tianqi（李沐）等人于 2015 年开发，2016 年被 AWS 选为官方深度学习框架。

**优势**：

- 多语言前端（Python/R/Scala/Julia/Perl/...）
- 分布式性能极好（参数服务器原生支持）
- 内存效率高
- AWS 背书

**为什么失败**：

1. **文档和社区**——MXNet 的文档质量远低于 TF/PyTorch，社区也小
2. **API 不稳定**——`gluon` API 变来变去，研究者不敢依赖
3. **AWS 定位错**——AWS 用户是工程师不是研究者，但框架战争是研究者决定的
4. **两面夹击**——被 TF（工业）和 PyTorch（学术）同时挤压

> 🎯 **MXNet 的教训**：**技术性能不是框架成功的关键**——MXNet 在 2016 年的分布式 benchmark 中经常第一，但研究社区不在乎。**社区 > 文档 > API 稳定性 > 性能**，这个优先级是反直觉的。

### 12.2 Caffe2——"被合并的下一代"

Caffe2 是 Yangqing Jia 离开 Berkeley 去 Facebook 后开发的 Caffe 继任者。但 Caffe2 还没来得及独立成长，就被合并进了 PyTorch（PyTorch 1.0 = PyTorch 0.4 + Caffe2 的底层）。Caffe2 的 C++ tensor 库成为了 PyTorch 的 ATen 基础。

### 12.3 Theano——"被遗忘的先驱"

Theano 在 2017 年宣布停止开发。它的思想活在了 TF 和 PyTorch 中，但项目本身消亡了。

**原因**：MILA 团队是学术组而非工程团队——他们没有资源维护一个工业级框架。Theano 的性能优化、GPU 支持、工程质量都跟不上 Google/Meta 的投入。

> 🎯 **Theano 的命运**：**学术界的框架无法与工业界的框架竞争**——框架需要全职工程师持续维护，学术组做不到。这和操作系统史一样——学术界的 Sprite/Amoeba 被工业界的 Linux/Windows 取代。

### 12.4 Chainer——"PyTorch 的日本前辈"

Chainer（2015，Preferred Networks）是最早实现 define-by-run（动态图）的 Python 框架——比 PyTorch 早两年。PyTorch 的设计受 Chainer 直接影响。但 Chainer 只在日本流行，最终被 PyTorch 的全球生态压倒。

> 🎯 **Chainer 的教训**：**先发优势不是优势**。Chainer 比 PyTorch 早两年做动态图，但它没有 Meta 的资源、没有全球社区、没有 HuggingFace。**框架竞争是生态竞争，不是技术竞争**。

---

## 13. 路径依赖与偶然性

### 13.1 如果 Torch 当年选了 Python……

2002 年 Torch 选了 Lua。如果它选了 Python（像后来的 PyTorch），那么 PyTorch 可能根本不需要存在——Torch 7 可能就直接赢了。

**但 2002 年的 Python 没有科学计算生态**——NumPy 2006 年才出现。所以 Torch 选 Lua 是**当时的合理决策**，只是后来被 Python 生态的崛起超越了。

> 🎯 **路径依赖**：技术选型的时间窗口比选型本身重要。Torch 在 2002 年是对的，在 2012 年就错了。**对错的判断不能脱离历史语境**。

### 13.2 如果 HuggingFace 选了 TF……

2018 年 HuggingFace 选择 PyTorch 后端。如果它选了 TF（当时 TF 份额更高），那么：

- BERT/GPT 的社区复现会用 TF
- 研究者被迫用 TF 来用 HuggingFace
- TF 可能在 2019-2020 年守住份额
- PyTorch 可能不会爆炸性增长

**一个创业公司的后端选择，可能改变了框架战争的结局。** 这就是历史偶然性。

### 13.3 如果 PyTorch 没有 Soumith……

Soumith Chintala 是 PyTorch 的社区灵魂——他每天在 GitHub issues、PyTorch forums、Twitter 上回答问题、修复 bug、推动社区。如果没有他这种"社区第一"的文化，PyTorch 可能变成另一个"Caffe2"——技术好但没人用。

> 🎯 **偶然性**：框架成功需要技术 + 时机 + 社区领袖。三者缺一不可。Soumith 就是 PyTorch 的"Linus Torvalds"——不写最多代码，但是社区粘合剂。

### 13.4 如果 Google 在 2017 年就做了 TF Eager……

Google 在 2017 年其实有内部项目支持 eager（`tf.contrib.eager`），但没有作为一等公民推广。如果 Google 在 2017 年就把 TF 切成 eager-native（而不是等到 2019 年 TF 2.0），PyTorch 可能根本没有窗口期。

**Google 的犹豫给了 PyTorch 18 个月的窗口**——这 18 个月足够让 PyTorch 积累社区临界点。**速度就是一切**。

---

## 14. 开放问题

### Q1：JAX 会取代 PyTorch 吗？

**短答案（2026）**：不会。**长答案**：JAX 会在前沿实验室（千亿模型）领域持续增长，但在研究社区整体不会超过 PyTorch。原因：JAX 的函数式范式对大多数研究者来说门槛太高；PyTorch 2.0 的 compile 已经"走私"了 JAX 的优化能力。

**真正的威胁**：如果 AI 硬件从 GPU 转向 TPU/晶圆级芯片，JAX + XLA 的编译器优势会放大——到那时 JAX 可能逆袭。

### Q2：下一个框架范式是什么？

**候选答案**：

1. **编译器为中心**：框架变成前端，核心是编译器（XLA/Triton/MLIR）。PyTorch 2.0 正在走这条路。
2. **声明式训练**：不用写训练循环，声明"我要训练什么模型"→编译器生成最优训练程序。类似于 SQL 之于数据库。
3. **可微分编程**：整个程序（含控制流/IO/分布式）都是可微的——JAX 的终极愿景。
4. **框架消失**：当 `torch.compile` 足够强大时，用户不再关心"什么框架"——只写 Python，编译器处理一切。

### Q3：为什么没有"中国框架"成功？

百度 PaddlePaddle、华为 MindSpore、旷视 MegEngine 都存在，但国际研究社区几乎不用。

**原因**：

1. **英文社区主导**——论文/教程/GitHub 讨论都在英文社区，框架需要英文社区
2. **生态锁定**——HuggingFace/timm/fast.ai 都基于 PyTorch，新框架没有生态
3. **地缘政治**——2020 年后中美技术脱钩加速了中国框架的"内循环"

> 🎯 **博士级问题**：框架竞争本质是**生态竞争 + 文化竞争**。技术可以复制，生态和文化不能。

### Q4：框架会"消失"吗？

如果 `torch.compile` 最终能做到"任何 Python 代码自动编译成最优 GPU 代码"，那么"框架"的概念可能消失——你写的是 Python，编译器处理一切。PyTorch 退化成一个"Python 科学计算库"，而不是"深度学习框架"。

**这正是 JAX 的愿景**：JAX 的核心不是"框架"，而是"NumPy + 函数变换"。如果这条路走通，未来的"框架"会更像 NumPy（一个库）而不是 TF（一个系统）。

### Q5：eager vs symbolic 的哲学辩论会重演吗？

在**量子机器学习**、**神经符号计算**、**可微分物理模拟**等新领域，"声明式 vs 命令式"的辩论可能重演。每个新计算范式都需要重新回答："用户应该怎么描述计算？"

---

## 15. 配套资源

### 15.1 本项目内配套

| 资源 | 关联 |
|------|------|
| [01-Autograd 与计算图](01-Autograd与计算图.md) | eager/autograd 的技术实现——PyTorch 灵魂 |
| [06-编译与图模式](06-编译与图模式.md) | torch.compile 技术细节——PyTorch 2.0 范式转移 |
| [08-现代 PyTorch (2.x)](08-现代PyTorch(2.x特性).md) | export/SDPA/DTensor——当前前沿 |
| [09-PyTorch 生态全景](09-PyTorch生态全景.md) | 生态库分类/选型 |
| [10-PyTorch 内核精读](10-PyTorch内核精读.md) | dispatcher/autograd 边界——框架内核 |

### 15.2 外部资源

| 资源 | 说明 |
|------|------|
| [PyTorch: An Imperative Style, High-Performance DL Library](https://papers.nips.cc/paper/9015-pytorch-an-imperative-style.pdf) | PyTorch 论文（NeurIPS 2019），设计哲学官方阐述 |
| [TensorFlow: A System for Large-Scale ML](https://www.tensorflow.org/) | TF 白皮书（Abadi et al.）|
| [Theano: A Python CPU/GPU Math Expression Compiler](http://www.iro.umontreal.ca/~lisa/pointeurs/theano_scipy2010.pdf) | Theano 论文（SciPy 2010）|
| [Karpathy · micrograd](https://github.com/karpathy/micrograd) | 100 行 autograd，理解框架本质 |
| [JAX: Deep Learning with...](https://jax.readthedocs.io/) | JAX 官方文档 |
| [Soumith Chintala: PyTorch origin story](https://soumith.ch/) | PyTorch 创始人的视角 |
| [Edward Yang (ezyang) Blog](https://blog.ezyang.com/) | PyTorch 内核开发者的深度博客 |
| [Papers with Code · Framework Trends](https://paperswithcode.com/) | NeurIPS/ICML 框架使用趋势 |

### 15.3 延伸阅读

- [讲透AI历史/00-为什么学AI历史](../讲透AI历史/00-为什么学AI历史.md)——思想史方法论
- [讲透AI历史/advanced/01-范式转移的库恩分析](../讲透AI历史/advanced/01-范式转移的库恩分析.md)——范式转移理论
- [讲透AI历史/advanced/03-路径依赖与偶然性](../讲透AI历史/advanced/03-路径依赖与偶然性.md)——历史偶然性

---

## 16. 费曼回炉（L2 自检）

### F1：三句话讲框架史

> 深度学习框架 20 年史 = **三个阶段的范式转移**：
> 1. **Symbolic 时代**（Theano/TF 1.x，2007-2018）：先建图再执行——优化强但调试地狱。
> 2. **Eager 时代**（PyTorch 0.1-1.x，2017-2022）：边跑边建图——调试好但优化弱。研究者用脚投票，eager 赢了。
> 3. **融合时代**（PyTorch 2.0 / JAX，2022-）：Eager 外观 + 编译器内核——鱼和熊掌兼得。

### F2：卡壳点记录

- **长期误解**：以为"PyTorch 赢是因为技术上更好"。纠正：PyTorch 赢是因为**研究者体验更好**，技术上的"更好"（静态图优化）反而属于 TF。框架竞争是**用户体验竞争**，不是技术竞争。
- **长期误解**：以为 JAX 和 PyTorch 是"同类竞争"。纠正：它们是**不同抽象层次**——PyTorch 是"框架"（有 Module、有优化器、有数据加载器），JAX 是"库"（NumPy + 函数变换）。它们服务的需求不同：PyTorch 服务"快速实验"，JAX 服务"极致优化 + 函数式纯度"。
- **长期误解**：以为框架战争已经结束。纠正：**PyTorch 赢了研究社区，但 JAX 赢了前沿实验室**。如果 AI 硬件格局变化（TPU/晶圆级），JAX 可能逆袭。

### F3：术语翻译

- **Eager（动态图/define-by-run）** → 每次 forward 就是普通 Python 执行，边跑边建图。**比喻**：即时编译的脚本语言（Python/JS）。
- **Symbolic（静态图/define-then-run）** → 先定义完整计算图再执行。**比喻**：提前编译的语言（C/Java）。
- **Autograd** → 自动微分引擎。**比喻**：Excel 的"自动重算"——你改了输入，所有依赖自动更新。
- **JIT / AOT 编译** → 即时编译（运行时）/ 提前编译（部署前）。**比喻**：同声传译（JIT）vs 翻译公司提前翻译好（AOT）。
- **SPMD（Single Program Multiple Data）** → JAX 的并行范式：写单设备代码，编译器自动分片到多设备。**比喻**：你写一份食谱，厨师长（编译器）自动安排 8 个厨师同时做。
- **Graph break** → Dynamo 跟踪 Python 字节码时遇到无法编译的代码，图被打断退回 eager。**比喻**：导航软件遇到没有地图的区域，退回人工驾驶。

### F4：迭代记录

- **v1 问题**：初稿把框架史写成"年代+技术特性"的流水账——Theano 做了 X，TF 做了 Y，PyTorch 做了 Z。这是**年代史**，不是思想史。
- **v2 修正**：重构为**"eager vs symbolic"的范式之争**贯穿全文。每个框架的兴衰都用这个轴线解释——Theano/TF 是 symbolic 极端，PyTorch 0.1 是 eager 极端，PyTorch 2.0/JAX 是融合。这把碎片化的事件编织成了一条**思想主线**。
- **v3 修正**：增加"五个反常识"和"路径依赖"章节——这不是知识补充，是**判断力训练**。读完不应该只记住"发生了什么"，而应该获得"**如何判断下一个框架竞争**"的能力。
---

> 🎮 **RL 视角**：框架演化 = RL 的 policy 搜索。eager 和 symbolic 是两个 policy，研究社区的"reward"是调试效率。PyTorch 2.0 的 compile 是 policy 的 value-based refinement——在已有 policy（eager）基础上加 value function（编译优化），而非从头换 policy。

---

### ✍️ 思考题

1. **方法论题**：如果用思想史视角分析"vLLM vs TensorRT-LLM"的推理框架竞争，你会关注哪些维度？
2. **反事实题**：如果 2018 年 HuggingFace 选择了 TensorFlow 后端，2020 年的框架格局会怎样？
3. **判断题**：JAX 会在 2030 年前在研究社区超过 PyTorch 吗？给出基于历史规律的预测 + 理由。
4. **批判题**：PyTorch 2.0 的 `torch.compile` 是"eager 赢了"还是"symbolic 赢了"？用辩证法分析。
5. **延伸题**：为什么中国框架（PaddlePaddle/MindSpore）在国际研究社区几乎不存在？用地缘政治 + 生态理论分析。

---

📌 **下一步**：

1. **想搞懂 autograd 本质** → [01-Autograd 与计算图](01-Autograd与计算图.md)（90 行手写复刻）
2. **想搞懂 compile 范式转移** → [06-编译与图模式](06-编译与图模式.md)
3. **想理解 2026 框架全景** → [09-PyTorch 生态全景](09-PyTorch生态全景.md)
4. **想挖到框架内核** → [10-PyTorch 内核精读](10-PyTorch内核精读.md)
5. **想回到更宏大的 AI 思想史** → [讲透AI历史](../讲透AI历史/README.md)
