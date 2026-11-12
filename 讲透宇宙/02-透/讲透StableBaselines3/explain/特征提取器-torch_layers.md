# 特征提取器 torch_layers.py——观测进入网络的第一公里

> 源码：`stable_baselines3/common/torch_layers.py`（commit b2878f4，全文 352 行）
> 姊妹篇：policy 侧如何消费这些 extractor 见《策略网络基类-policies.md》

## 一、角色定位

RL 环境吐出来的观测千姿百态：一维状态向量、RGB 图像、`Dict(image=..., vector=...)` 混合体。而 policy 的 trunk（MLP 或分布头）只吃固定维度的平直向量。`torch_layers.py` 就是这两者之间的**适配层**：把任意形态的观测压成一个 `features_dim` 维向量，并把这个维度数提前报告给上层，让 `action_net`/`value_net`/`create_mlp` 能在构造期就确定形状——这是 PyTorch 静态构图范式下必须"先知维度"的解法。

文件总共 7 个成员，可分三组：

- **协议**：`BaseFeaturesExtractor`（torch_layers.py:L11）——所有提取器的抽象基类；
- **具体提取器**：`FlattenExtractor`（L31，向量的占位提取器）、`NatureCNN`（L47，图像 CNN）、`CombinedExtractor`（L264，Dict 多模态聚合）；
- **网络构建辅助**：`create_mlp`（L108，MLP 工厂函数）、`MlpExtractor`（L184，on-policy 双腿 MLP）、`get_actor_critic_arch`（L314，off-policy net_arch 解析）。

> **勘误（常见误解）**：不少二手资料把这个文件里的 CNN 提取器称作 `NatureDQNChannelsExtractor`。经 `git log -S` 检索，本仓**任何历史版本都不存在该类名**——它自始就叫 `NatureCNN`（结构上指 DQN Nature 论文的卷积前端）。旧名很可能与其他库或记忆偏差混淆。

## 二、内部结构

### BaseFeaturesExtractor：一个属性的协议

这个"协议"薄到只有一个 property（torch_layers.py:L25-28）：`features_dim` 返回构造时存下的 `_features_dim`。构造函数（L19-23）只有两个动作：`assert features_dim > 0` 与把 observation_space 存为 `_observation_space`。

但薄不等于不重要。整个 SB3 的维度协商都建立在"**提取器在 `__init__` 内就能算出自己输出维度**"这条契约上：`BaseModel._update_features_extractor`（policies.py:L115）拿 `features_extractor.features_dim` 塞进网络构造参数；`ActorCriticPolicy.__init__` 在 policies.py:L508 立即读取它。这决定了所有子类的实现纪律——维度推断逻辑必须放在 `__init__`（静态从 space 推，或跑一次 dummy forward），而不是等第一次真数据。observation_space 前缀下划线（L22）也在暗示：space 只是构造期素材，提取器不应在 forward 里回头查 space。

### FlattenExtractor：占位符

向量化观测（Box 一维）根本不需要"提取"，`FlattenExtractor`（L31-44）就是诚实的那句话：`get_flattened_obs_dim(observation_space)` 算平直维度（来自 preprocessing.py），`nn.Flatten()` 兜住非一维的边角（如 Box 二维矩阵观测），forward 一行转发（L43-44）。`MlpPolicy` 默认走它（policies.py:L461），即"flatten + 后续 MLP"的默认管线。

### NatureCNN：DQN Nature 论文的卷积前端

`NatureCNN`（torch_layers.py:L47-105）是图像观测的默认提取器，结构完全复刻 Mnih et al. 2015《Human-level control through deep reinforcement learning》：

- 三个卷积层（L88-96）：`Conv2d(C→32, 8×8, stride 4)` → ReLU → `Conv2d(32→64, 4×4, stride 2)` → ReLU → `Conv2d(64→64, 3×3, stride 1)` → ReLU → Flatten。这三个 kernel/stride 组合是 2015 年调参调出来的"经典配方"，8/4-4/2-3/1 的感受野阶梯专为 84×84 Atari 帧设计；
- 一个全连接层（L102）：`Linear(n_flatten, 512)` + ReLU，512 即默认 `features_dim`（L66）。

两道构造期断言值得注意：L69-72 要求 observation_space 是 Box；L76-86 的 `is_image_space` 检查（含 dtype uint8、值域 [0,255]、`check_channels=False`）失败时会抛出一段**教学级错误信息**——提示"你可能把 CnnPolicy 用在了向量观测上"并链接 env_checker 与 `normalize_images=False` 的文档。SB3 的错误消息设计哲学在这个 assert 里体现得很充分：不只报错，还猜你下一步会犯什么。

最有趣的是 L98-100 的形状推断技巧：

```python
with th.no_grad():
    n_flatten = self.cnn(th.as_tensor(observation_space.sample()[None]).float()).shape[1]
```

**用一次真前向来算 Flatten 后的维度**，替代手写 `((84-8)/4+1)` 这类易错的卷积输出公式。observation_space 自带 `sample()`，天然是免费的 dummy 数据源。任何自定义 CNN 提取器都建议照抄这两行。

输入约定在 L74-75 的注释里：假定 CxHxW（channel-first），HWC→CHW 的转置由 preprocessing/wrapper 层完成，提取器不做。

### create_mlp：MLP 工厂

`create_mlp`（torch_layers.py:L108-181）返回一个 `nn.Module` 列表（不是 Sequential，由调用方组装），签名五个关键参数：

- `input_dim/output_dim/net_arch`：`net_arch=[256, 256]` 表示两个隐藏层；**`output_dim > 0` 才追加输出层**（L172），`output_dim=-1` 表示"无输出头"——SAC 的 actor 正是这么用的（sac/policies.py:L85 `create_mlp(features_dim, -1, net_arch, activation_fn)`，先造 latent 网，再手接 `self.mu`/`self.log_std` 线性头）；
- `squash_output`（L179-180）：末尾追加 `nn.Tanh()`，off-policy 确定性 actor（DDPG/TD3/SAC）靠它把动作压进 (-1,1)；
- `with_bias` 与一对扩展插槽 `pre_linear_modules/post_linear_modules`（L132-140 的 docstring 详述放置规则）：pre 层（如 BatchNorm，吃 input_dim 构造）加在每个 Linear **前**且输出层前也加（L175-176）；post 层（如 Dropout/LayerNorm，吃该层输出维构造）加在 Linear 后、激活前，但**输出层后不加**（L172-178 的循环里只有 pre 与 Linear）。这套规则让注入正则化层不必改函数体。

组装逻辑三段：首层（L148-159，net_arch 非空才建）、中间层循环（L161-170）、可选输出层（L172-178）。`net_arch=[]` 且 `output_dim>0` 时直接 `Linear(input_dim, output_dim)`（L173 的 `last_layer_dim = input_dim` 兜底）——线性策略的写法。

### MlpExtractor：on-policy 的双腿 MLP

`MlpExtractor`（torch_layers.py:L184-261）是 PPO/A2C 专属的 actor/critic 双腿网络。`net_arch` 两种形态（L224-229）：dict `dict(pi=[64,64], vf=[64,64])` 各自独立；纯 list 则两腿同构（`pi_layers_dims = vf_layers_dims = net_arch`，L229）。注意 SB3 v1.8.0 起**没有共享隐藏层**——两腿从 feature_dim 起就是分开的 Linear（L231-239），`forward` docstring 里那句"If all layers are shared, then latent_policy == latent_value"（L253-254）是历史残留表述，当前实现两条 Sequential 各自独立参数（L247-248），仅当 net_arch 两条都为空时都退化成 Identity 才数值相等。双腿末端维度 `latent_dim_pi/latent_dim_vf`（L242-243）上报给 policy 去建 action_net 和 value_net（policies.py:L594、L609）。

三个前向入口（L250-261）：`forward` 返回 tuple（两腿一起走），`forward_actor`/`forward_critic` 单腿走——这个拆分正对应 policies.py 里共享/不共享 extractor 时的两种调用方式（policies.py:L647 与 L650-651）。

### CombinedExtractor：Dict 观测的多模态聚合

`CombinedExtractor`（torch_layers.py:L264-311）处理 `spaces.Dict`，策略是"**每 key 一个子提取器，向量拼接**"：

- 构造期遍历 `observation_space.spaces`（L292-299）：子空间是图像 → 塞一个 `NatureCNN(subspace, features_dim=cnn_output_dim)`（默认 256，L283），累计 256 维；否则 → 塞一个裸 `nn.Flatten()`，累计 `get_flattened_obs_dim(subspace)`；
- 子模块装进 `nn.ModuleDict`（L301）保证参数正确注册；
- `forward`（L306-311）逐 key 过各自提取器，`th.cat(encoded_tensor_list, dim=1)` 拼接。

构造里有个自嘲式注释：L286-287 `# TODO ... so put something there. This is dirty!`——父类构造要求 features_dim，但总维度要遍历完才知道，于是先传 1 占位，算完 total_concat_size 再在 L304 手动改写 `self._features_dim`。这暴露了 BaseFeaturesExtractor 协议的一个小裂缝：`_features_dim` 是约定私有的，子类为了延迟定维不得不越权直写。自定义提取器如果也遇到"维度后期才知"，这是仓内先例。

`cnn_output_dim=256` 默认值的选择（docstring L272-273 "to avoid exploding network sizes"）：把每个 CNN 分支压到固定 256，避免多图像 key 时拼接维度爆炸，代价是截断了 NatureCNN 原生 512 维的表达——多模态场景下的一个隐性容量上限。

### get_actor_critic_arch：off-policy 的 net_arch 翻译器

`get_actor_critic_arch`（torch_layers.py:L314-351）是唯一不定义网络的成员：把 SAC/TD3/DDPG 的 `net_arch` 翻译成 `(actor_arch, critic_arch)`。list 直接两份同用（L344-345）；dict 必须同时含 `pi` 和 `qf` 键（L348-349 的双 assert）。docstring 的 note（L336-338）说清了与 on-policy 的关键差异：**off-policy 不允许 actor/critic 共享层**（除 extractor 外），原因是 target network 的存在——共享参数会让 target 的"冻结"语义被破坏。

## 三、外部连接

**上游消费者**：`policies.py` 是最大客户——L25-32 一次性导入 `BaseFeaturesExtractor/CombinedExtractor/FlattenExtractor/MlpExtractor/NatureCNN/create_mlp` 六件。`BaseModel.__init__` 存 extractor 类（policies.py:L67 默认 FlattenExtractor），`make_features_extractor`（policies.py:L118-120）实例化；L93-94 的自动注入把 `normalized_image=True` 塞进 kwargs，落点就是 NatureCNN/CombinedExtractor 的同名构造参数（torch_layers.py:L67/L284）。`ActorCriticPolicy._build_mlp_extractor`（policies.py:L578-583）把 net_arch/activation_fn 交给 MlpExtractor。

**算法侧**：DQN 的 Q 网络默认 `net_arch=[64, 64]`（dqn/policies.py:L50、L138）并用 `create_mlp(self.features_dim, action_dim, ...)` 直接造头（dqn/policies.py:L56）——"MlpPolicy 两层 64"的另一半出处；on-policy 的两层 64 则是 policies.py:L496-500 的 `dict(pi=[64,64], vf=[64,64])`。SAC/TD3 的 actor 用 `create_mlp(..., -1, ...)` 造 latent 网再接 mu 头（sac/policies.py:L85-101）；`get_actor_critic_arch` 的调用方在 sac/td3 的 `NetArchitecture` 类里。

**底层依赖**：`preprocessing.py` 的 `get_flattened_obs_dim/is_image_space`（torch_layers.py:L6）、`type_aliases.TensorDict`（L7）、`utils.get_device`（L8，MlpExtractor 构造里显式 `.to(device)`，L247-248——这是文件里唯一主动搬设备的地方，其余模块靠 policy 容器的 `.to()` 连带迁移）。

## 四、数据流

以 `MultiInputPolicy`（PPO + Dict 观测，含 `image` 与 `state` 两个 key）一次前向为例：

1. **观测预处理**（policies.py:L130 `preprocess_obs`）：图像 key 被 `/255` 归一化（若 normalize_images=True）并保证 channel-first，向量 key 原样；
2. **CombinedExtractor.forward**（torch_layers.py:L306-311）：`observations["image"]`（shape `(B, 3, H, W)`）过 NatureCNN——三卷积到 `(B, 64, c1, c2)`、Flatten 成 `(B, n_flatten)`、Linear 到 `(B, 256)`（构造期 L100 那次 dummy forward 算出的 n_flatten 在此生效）；`observations["state"]` 过 `nn.Flatten()` 保持 `(B, dim)`；
3. **拼接**：`th.cat(..., dim=1)` → `(B, 256 + dim)`，这个 `total_concat_size` 就是 L304 写入的 features_dim；
4. **进入 trunk**：MlpExtractor 两腿各自 `[64, 64]` Linear+Tanh（policies.py:L496-500 的默认），得到 `latent_pi (B,64)`、`latent_vf (B,64)`；
5. **出头**：`action_net(latent_pi)` 进分布、`value_net(latent_vf)` 出标量。

维度链条完全在构造期闭合：`observation_space → get_flattened_obs_dim/NatureCNN 推断 → _features_dim → MlpExtractor 输入 → latent_dim_pi/vf → action_net/value_net 输入`。整条链没有任何运行期动态 shape 推断（除了 NatureCNN 构造期那一次），这是"space 先行"设计的完整闭环。

`create_mlp` 的数据流则是纯列表装配：`[Linear, act, Linear, act, ..., Linear(可选), Tanh(可选)]`，无状态无分支，调用方拿列表组 `nn.Sequential`（如 ContinuousCritic，policies.py:L966-967）。

## 五、设计决策

**决策一：提取器与 trunk 彻底解耦，用"单一输出维度"做接口。** `features_dim` 这一个 int 就是两层的全部契约——提取器内部是 CNN、Flatten 还是 ModuleDict 聚合，trunk 完全无感。收益是极强的组合自由：换 extractor 不动 trunk，换 trunk（改 net_arch）不动 extractor，自定义提取器只需守住"构造期报告维度"一条纪律。代价是表达力受限：接口只能吐**一个平直张量**，想让 policy 直接吃序列/树状/多尺度特征（现代多模态的 cross-attention 融合）就绕不开破约——CombinedExtractor 的"各自编码后 cat"是最朴素的晚期融合，信息交互只发生在拼接点之后的 MLP。对图像+向量这种弱耦合模态够用，对强耦合感知任务（如需要空间对齐的任务）是明显瓶颈，只能整个替换 CombinedExtractor。

**决策二：维度推断放在构造期，用 dummy forward 而非公式。** NatureCNN L98-100 选择"真跑一次"而非手算卷积输出尺寸，把"改变 kernel/stride/padding 组合就要重算公式"的维护负担归零。这是用一次构造期开销（对 84×84 输入约毫秒级）换正确性保险。批判地看它也有静默风险：`observation_space.sample()` 采的是合法随机观测，若 space 的 shape 声明与真实 env 输出不符（自定义 env 常见病），推断会"成功地"得出错误维度，错误推迟到第一次真 forward 才爆——报错点离病因很远。SB3 用 env_checker 工具弥补，但库内无强制。

**决策三：FlattenExtractor 作为默认（policies.py:L67），即"SB3 的默认假设是向量观测"。** 这个默认的选择意味深长：图像用户必须显式选 CnnPolicy/MultiInputPolicy，否则 NatureCNN 的断言（L76-86）会拦住并教学。把"贵的那条路"设为显式 opt-in、"平凡的路"设为默认，是 API 对新手梯度的一种排序——但反过来也意味着图像场景的 `MlpPolicy` 误用只能靠 assert 兜底，若用户传了形状合法却语义是图像的 Box 观测（比如已经 flatten 过的图像向量），库无法察觉，会安静地训练一个低效模型。

## 六、新人提示

1. **自定义提取器的最小实现**：继承 `BaseFeaturesExtractor`，`__init__` 里 `super().__init__(space, 算好的维度)`，实现 `forward`。维度算不出就抄 NatureCNN L98-100 的 dummy forward 惯用法。切记维度必须构造期可知——想"第一次 forward 时再定"在这个体系里行不通。
2. **CNN 报错先读报错全文**：torch_layers.py:L76-86 那段 assert 消息是 SB3 最有用的错误信息之一，"you are probably using CnnPolicy instead of MlpPolicy"的猜测十有八九是对的。
3. **net_arch 的三种方言别混**：on-policy 用 `dict(pi=, vf=)`（或共享 list）；off-policy 用 `list` 或 `dict(pi=, qf=)`（torch_layers.py:L348-349 强制双键）；`[dict(...)]` 旧写法在 policies.py:L485-493 已是废弃路径。`vf` 与 `qf` 一字之差对应两族算法，报错信息会直接指明。
4. **`create_mlp` 的 output_dim=-1 是"无头"暗号**：看到 SAC/TD3 actor 里传 -1，意思是只造隐藏层，动作头（mu/log_std）由算法层自建——`>0` 才有输出层，`0` 或负数都没有（L172 只判 `>0`）。
5. **CombinedExtractor 的 CNN 分支只有 256 维**：多模态任务若图像信息量大，记得传 `policy_kwargs=dict(features_extractor_kwargs=dict(cnn_output_dim=512))` 放宽，否则瓶颈不在 trunk 而在这个默认值。
6. **MlpExtractor 的空 net_arch 是合法的**：`dict(pi=[], vf=[])` 时两腿是 Identity，CNN policy（ActorCriticCnnPolicy）默认就是它（policies.py:L496-498）——此时 NatureCNN 的 512 维输出直接怼进 action_net/value_net。看到别人代码里 net_arch=[] 不要以为是 bug。

---
元数据：字数（中文字+英文词，不计空格）3585 ｜ 行号锚 89 处引用（全限定 torch_layers.py/policies.py/dqn|sac policies.py 等 ×31 + 上下文裸 L×58，逐条对源码核verified） ｜ 六节自查：角色定位✓ 内部结构✓ 外部连接✓ 数据流✓ 设计决策(3 条批判性权衡)✓ 新人提示✓
