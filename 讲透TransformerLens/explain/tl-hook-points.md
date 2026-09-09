# tl-hook-points · hook_points.py 精讲（451 行）

> 目标文件：`transformer_lens/hook_points.py` · 图谱定位：全库基石，legacy 与 v3 双系统共用的钩子机制。

## 1. 角色定位

hook_points.py 回答一个根本问题：**如何在不改变模型数学的前提下，让任意中间激活可观察、可修改？** 答案是 `HookPoint`——forward 恒等（`return x`）的哑 nn.Module，包住任何中间激活就获得标准化的 PyTorch hook 挂载点。整个 TransformerLens"一切激活皆可干预"的哲学落地就是这 451 行。灵感来自 Anthropic transformer-circuits 团队的 Garcon 工具（docstring 与 README 双重确认）。它同时服务两套系统：legacy 的 HookedTransformer 在组件里显式插入 HookPoint，v3 的 TransformerBridge 靠扫描模型把它注入 HF 原生模块——名副其实的双系统地基。

## 2. 内部结构

- **LensHandle**（dataclass）：钩子句柄元信息——`hook`（RemovableHandle）、`is_permanent`（永久 or 上下文级）、`context_level`（上下文层级，支持嵌套弹栈）、`user_hook`（用户原函数，供 reset 重装）。
- **HookPoint**（主类）：`fwd_hooks/bwd_hooks` 两个 LensHandle 列表、`ctx` 字典（hook 间通信黑板）、`name`（根模块 setup() 时命名，如 blocks.0.attn.hook_q）、`hook_conversion`（可选形状转换器）、`backward_scale`。
- **核心方法**：`add_hook(hook, dir, is_permanent, level, prepend, alias_names)` 是心脏——把用户签名 `fn(activation, hook)` 包装成 PyTorch fwd/bwd hook；`add_perma_hook` 即 `is_permanent=True`；`remove_hooks` 按 level 精确清理；`layer()` 从名字解析层号；`enable_reshape` 挂 BaseTensorConversion。
- **辅助类**：`_AliasedHookPoint`（兼容模式下同一钩子按多别名各触发一次）、`_ScaledGradientTensor`（绕 PyTorch backward hook 梯度求和 bug）、`HookIntrospectionMixin`（list_hooks 内省，经 `hook_dict` 同时适配 HT 与 Bridge）。

## 3. 外部连接

上游仅依赖 torch + `BaseTensorConversion`。下游即全库：HookedRootModule/HookedTransformer 用它搭 legacy 组件；generalized_components 的 47 个 bridge 组件全数继承这套语义；bridge.py 的 `_scan_existing_hooks` 靠扫描 HookPoint 建注册表。HookedRootModule 已在 3.0 迁出，从这里 import 触发 DeprecationWarning（文件尾 `__getattr__` 兜底）。

## 4. 数据流

前向：张量 x 经 `HookPoint.forward(x)` 恒等返回，但注册在该模块上的 `full_hook` 被触发——`module_output` 即激活值。若 `dir=="bwd"`，module_output 是 `(grad,)` 元组需解包并按需包 `_ScaledGradientTensor`；若 `hook_conversion` 存在则先 `convert()`（如融合 QKV 重塑为按头形状）；然后按 `alias_names` 循环（或单次）调用 `hook(value, hook=point)`——**返回 None=只观察，返回张量=替换激活**（干预的实现）；返回值再经 `revert()` 反转换回原始布局，backward 情形重新包元组交还 PyTorch。`ctx` 字典让同一 run 内多个钩子共享状态（如先存后取做 patching）。

## 5. 设计决策

① **哑模块而非 monkey-patch**：恒等层不改计算图，换来钩子语义与 PyTorch 完全兼容（benchmarks 层专门量化注册开销）。② **返回值即干预**：观察与干预统一为"是否返回"，比两套 API 简单一个数量级。③ **context_level 栈**：嵌套的 run_with_hooks/run_with_cache 各自只清理自己层级的钩子，避免误伤。④ **alias_names 机制**：v3 双命名下一个物理钩子按多个逻辑名各触发一次，是双系统粘合剂。⑤ **partial 的 repr 定制**：缓存大张量的 partial repr 极慢，定制 `__name__` 在海量 hook 注册时是真实性能差异。⑥ **backward_scale 包装 sum 而非逐元素**：注释明说绕 PyTorch bug——"在哪一层修"的精准工程判断。

## 6. 新人提示

- 十行脚本体会核心：`hp = HookPoint(); hp.add_hook(lambda v, hook: v*0)` 手动 forward——"返回张量=替换"。
- 钩子第二参数是 `hook=` 关键字；`hook.name` 拿全名、`hook.layer()` 拿层号，循环注册的标准姿势。
- 第一大坑：临时钩子 reset 后消失，永久钩子（steering 用）跨 run 存活——叠加注册会指数放大效果。
- 读 HookedRootModule.run_with_cache 前先读懂 add_hook：前者只是后者的批量编排。
