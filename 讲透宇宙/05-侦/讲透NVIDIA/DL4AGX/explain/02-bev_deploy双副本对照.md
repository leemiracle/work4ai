# 02 · bev_deploy 双副本：同源工具库的漂移实例库

## 角色定位

`bev_deploy` 是 vad-trt 与 petr-trt 各持一份的**同源 Python 工具库**，负责「追踪 PyTorch 模型调用 → 重建 TRT 可导等价模块」。两副本已漂移，是 DL4AGX 里研究共享库 fork 演化的天然标本（图谱 L03 专题层）。vad 版在 `AV-Solutions/vad-trt/export_eval/bev_deploy/`，petr 版在 `AV-Solutions/petr-trt/export_eval/bev_deploy/`，子包结构同款：hook（追踪）+ patch（算子手术）+ trt（推理对拍），vad 版独多 infer_shape。

## 内部结构

hook 框架核心 `hook/hook.py`：`Hook` 以 `functools.wraps` 包装目标 callable（vad 版 hook.py:99-135 的 `_wrap`/`wrap` 阶梯），捕获入出参；`HookHelper` 按类名单挂接，seen_classes 集合防重复。patch 侧 `patch/inspect.py` 是重建器：`InspectHelper`（vad 版 inspect.py:42）、`StatefulInspectHelper`（inspect.py:137）、`StatefulModuleTrt` 系包装类（inspect.py:158 起）、`AutoArg/AutoConst/AutoModule` 参数替身族（inspect.py:175-200）、`AutoStatufulModule`（inspect.py:491）——这套 Auto* 家族把被 hook 捕获的动态执行痕迹重写成静态可导图。

**双副本最有教学价值的漂移点**（全部可 diff 实证）：
- 拼写：vad `patch/inspect.py:158` `class StaefulModuleTrt`（少 t，上游拼写原样保留）；petr `patch/inspect.py:146` `class StatefulModuleTrt`（已修正）。但 petr 只修了这一处——`AutoStatufulModule` 在 vad:491 / petr:482 **两版都拼错**。
- petr hook.py 增量：`functools.partial` 函数名解包（petr hook.py:87-92）；空 args 防护从 TODO 注释（vad hook.py:104-105）落地为 `if len(args) != 0`（petr hook.py:111-113）；意外 self 替换时 `p.requires_grad = False` 兜底（petr hook.py:124-133）；挂接类目补 BatchNorm1d/Conv1d（petr hook.py:229/231）。
- `hook/traceable_dict.py`：petr 版 :33 多一个 `update` 方法。
- vad 版独有 `infer_shape/` 子包（inspect.py:38 引用 `from bev_deploy.infer_shape import infer`），petr 版已砍掉该依赖。

## 外部连接

vad 版 inspect.py 头部 `import inspect`（inspect.py:18，petr 版同位 L18）——注意这是标准库导入而非自引用，静态解析器会把 `import inspect` 误连到同名本文件（自环边），读图时须排除。patch 注册面：`patch/custom_op.py` 的 register + custom_handler 闭包工厂两版同构；vad 版独有 `patch/bevformer/ms_deform_attn.py`（BEVFormer 系 MSDA 处理器，vad-trt 插件三家族的导出对端）；petr 版 `patch/custom_aten.py` 无 `infer_grid_sample`（vad 版有）。两副本最终都服务各自宿主的 export 脚本（vad 的 patch_head.py:85 `G_HANDLERS` 注册表即其消费点之一）。

## 数据流

宿主 export 脚本 import bev_deploy → HookHelper 挂接模型 forward 链 → Hook 捕获每层入出参（`hook/stack.py` 的 StackManager 标注嵌套层级，`hook/args.py` 的 ArgWalker/CompactJSONEncoder 序列化，`hook/cache.py` 提供缓存与回调）→ inspect.py 拿捕获重建 StatefulModuleTrt → custom_op/custom_aten 把难导算子替换为 `custom_op::` 命名空间插件调用 → 产出静态 ONNX → `trt/inference.py` 与 PyTorch 对拍。

## 设计决策

为什么拷贝而非抽公共包？案例集定位下每个子项目需独立可运行（README 各自闭环），且两项目上游依赖代际不同（vad 的 mmcv 栈与 petr 有差），fork 后各自演化成本低于维护抽象层。漂移方向也说明 fork 语义：petr 版是**后续维护版**（修拼写、加防护、扩类目），vad 版保留更接近共同祖先的形态（infer_shape 依赖、TODO 注释）。「修一处留一处」的 AutoStatufulModule 则暴露人工同步的极限。

## 新人提示

对比阅读法：`diff -r` 两份 bev_deploy 是理解全库最快的路径，差异即演化史。改 hook.py 时先确认你要改哪份副本（或两份都改）——没有同步机制。写新导出案例时可把 petr 版当基线（防护更全），但 MSDA 类 BEVFormer 算子的处理器只在 vad 版有（`patch/bevformer/ms_deform_attn.py`）。`import inspect` 自环误解析在图谱里表现为 inspect.py 上的可疑自边，属工具盲区非代码问题。
