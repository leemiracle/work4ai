# 03 · petr-trt 与 constantization：把动态计算冻成常量

## 角色定位

petr-trt 是双子项目的另一半：PETRv1/v2（位置嵌入变换 3D 检测）的 TRT 部署案例。它与 vad-trt 共享 app/lib 同构三件套与 bev_deploy 工具库（见 02 篇），独有贡献是 **constantization 导出手法**——把数据相关的动态计算首帧固化、后续帧复用，换取静态图可导出。这个手法在本仓 v1/v2 两代导出线中反复出现，是「时序模型静态化」的第二条路线（vad 走拆双图，petr 走冻结常量）。

## 内部结构

导出线 v1/v2 完全平行四件套：`export_eval/v1/v1_patch.py`（224 行）→ `v1_export_to_onnx.py`（分 backbone/head 两段导出）→ `v1_save_data.py`（落参考数据）→ `v1_evaluate_trt.py`（对拍）；v2 目录同构四件，`v2_patch.py` 252 行多出时序特征处理。

constantization 的范本在 `v1_patch.py:36` `constantization_PETRv1Head_forward`：函数第一次执行时把七个数据相关量算出来**缓存在函数属性上**——masks（v1_patch.py:65）、coords_position_embeding（:69）、sin_embed（:75，`detach().clone()` 脱图拷贝）、pos_embed（:96）、query_embeds（:100）、reference_points（:103）；后续帧直接复用（:167 `pos_embed + constantization_PETRv1Head_forward.sin_embed`）。文件其余部分（pos2posemb3d 等 :22-33 的纯函数）是重写版 head 前向的配套实现。挂接点在导出脚本 `v1_export_to_onnx.py:252`——`ch.hooks["PETRv1.pts_bbox_head.forward"]._patch(constantization_PETRv1Head_forward)` 经 bev_deploy hook 框架替换原前向（main 于 v1_export_to_onnx.py:117，:267 的 AutoInspectHelper 完成最终导出）。v2 完全同构：`v2_patch.py:36` `constantization_PETRv2Head_forward`（:54 masks、:66 sin_embed、:89 query_embeds）。

C++ 侧 `app/petrv1.cpp`（234 行）与 `app/petrv2.cpp`（245 行）同构：main 均起于 petrv1.cpp:46 / petrv2.cpp:46，读 `app/demo/v1_config.json`（v1_config.json:3-4 的 warm_up/n_frames 计数、:24 起 head 输入 mlvl_feats 由 backbone out.0 供给）→ backbone+head 双引擎 → 可视化。共享库与 vad 逐行同构：`app/lib/net.h:81` Enqueue、net.h:92 EnableCudaGraph、net.h:109 validate；`app/lib/tensor.h:45-139` struct Tensor；`app/lib/utils.h`（78 行计时/文件工具）；`app/lib/visualize.cu` 696 行。

## 外部连接

对上游 PETR 仓的改动极小——`patch.diff` 仅 30 行（petr-trt 目录根，patch.diff:1 起改的是 petr_vovnet_gridmask_p4_800x320.py 训练配置），与 uniad 的 7560 行大补丁形成极端对照：PETR 架构本身 TRT 友好（无复杂动态控制流），补丁只做点状修整。bev_deploy 工具库（petr 版）承担 MSDA 等算子的 hook/重建（见 02 篇）；dockerfile（无扩展名小写文件）装 nvcr pytorch:22.12-py3 + mmcv 栈。v1/v2 的差异本质是上游模型差异：v2 引擎带时序输入，config 同构但指向 v2 引擎与 viz_v2。

## 数据流

PyTorch checkpoint → v1_patch 应用（constantization 替换 head 前向）→ backbone/head 两段 ONNX → trtexec 双引擎 → app 读 config 六路图像 → backbone 引擎出 mlvl_feats → head 引擎（query_embeds/pos_embed 等已冻结在图内）→ 输出 bbox → visualize.cu 绘制；v1_save_data 落的参考数据供 net.h:109 validate 与 evaluate_trt 对拍。

## 设计决策

为什么冻结而非每帧重算？pos_embed/query_embeds 只依赖相机内外参与锚点 query——推理期间恒定，属于「数据相关但时间无关」的计算。每帧重算会引入 Gather/Scatter 类动态形状节点阻断导出；冻结后这部分从图中消失，head 成为纯静态图。代价：换相机标定或分辨率需重导出。与 vad 的双图法相比，constantization 更彻底（常量直接织进权重图），适用条件更窄（要求被冻量真恒定）。

## 新人提示

读 v1_patch.py:36-170 一段即可掌握手法全貌，重点看 :75 的 `detach().clone()`（防常量跟踪进自动求导图）；迁移到自己的模型时先审计哪些量「数据相关但恒定」。app 双引擎链的接线在 v1_config.json 里（head 输入索引 backbone out.0），改网络结构先改 config 再改代码。注意 petr 的 app/lib 与 vad 逐行同构，bugfix 需双向同步——仓库历史证明这种同步并不可靠（visualize.cu 两份 696 行现仍一致，属幸存者）。
