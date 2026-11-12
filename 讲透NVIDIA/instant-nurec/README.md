# 讲透 NVIDIA/instant-nurec

InstantNuRec：前馈 3DGS 自动驾驶场景重建（多相机驾驶日志→单次前馈可仿真 3D 高斯场景，arXiv 2607.14203）。

## 全链状态表

| 产物 | 状态 | 位置 |
|---|---|---|
| DeepWiki | ✅ 全量 | `deepwiki/` |
| understand 图谱 | ✅ 587n/1328e/12层/14步，validate 0 issues，fingerprints 140@f2ecafcd | 仓内 `.understand-anything/knowledge-graph.json` |
| ONBOARDING | ✅ 8 节 | `onboarding/ONBOARDING.md` |
| explain | ✅ 4 篇 | `explain/01~04` |
| 源码 | 本地 `/usr-data/data2/repos/agent-repos/NVIDIA/instant-nurec`，HEAD `f2ecafcd` | — |

explain 索引：01 backbone 与 blocks 模型核心 · 02 两阶段训练契约 · 03 传感器 SE3 与 lietorch 垫片 · 04 predict 导出五形态。

## 关键事实速览

- 单次前馈出分层 3DGS：静态层+动态层+天空 cubemap+逐相机 ISP 仿射；10–20s 场景约 1.5s，Waymo PSNR +2.01 dB（README.md:16）
- 感知底座 DAv3（Depth-Anything-3 ViT）+ DPT 密集头，每上下文像素一高斯；渲染走 gsplat 3DGUT（README.md:16、renderer.py:135）
- 训练两阶段：context（深度/RGB/法线/语义回归）→render（可微渲染，编码器冻结 Gaussian 头重init）（docs/TRAINING.md:25-57）
- 五形态导出：PLY/`.sky.npz+.png`/`.dynamic.npz`/`.render.png`/`.render.mp4`（run_inference.py:17-27）

## 勘误清单（源码级实证，≥6 条）

1. **本仓非语音工具（任务书推翻）**：源码全仓零语音/TTS/NLU 代码；实为前馈 3DGS 自动驾驶场景重建库（README.md:4，`instant_nurec/model/`、`primitives/`、`predict/` 全部围绕高斯图元与渲染）。
2. **本仓不依赖 lietorch**：`utils/se3.py:15-22` 是 lietorch API 子集的纯 torch 垫片——PyPI lietorch==0.8.2 硬钉 torch 2.6 与本仓 torch 2.7.0+cu128（pyproject.toml:24）冲突；说"用 lietorch 做位姿"是错的。
3. **公开检查点没有学习式天空头**：static_core.py:167 注释 "Public checkpoints intentionally omit the learned `sky.*` head"——天空 cubemap 由观测 RGB 推导（cubemap.py:206），不是网络输出。
4. **PLY 的 scale/density 是预激活值**：export_ply.py:47-52 逆激活硬编码（scale=log、density=logit）；下游消费须自行激活，直接当激活值用会得到错误几何。
5. **可训矩阵窄于推理矩阵**：三个 profile（pa-front/pa-multiview/pq-front）都能推理，但 standalone 训练只有 dense 前相机两阶段；point-query 变体被全模型组合**刻意拒绝**训练、TokenGS 不在公开训练路径（docs/TRAINING.md:11-16）。
6. **旧 TorchScript traced 包被拒载**：model/__init__.py:125-130 显式拒绝 legacy traced archive；DeepWiki 页名"jit-kelvin-adapter"易误导为 JIT 路径仍在，实际公开路径是 eager（KelvinStaticCore/KelvinInferenceModel）。
7. **编码器 FOV 是 pinhole 近似**：encoders.py:131 TODO 标记 F-Theta 相机当前也用 `_fov_wh_from_pinhole`（:100-106）近似，精确鱼眼 FOV 未进编码器。
8. **cli 的 8 处延迟 import 是刻意设计**：cli.py:216 注释钉版"keep argparse-only invocations cheap"，不是疏漏。
9. **run.sh 有自己的错误码**：`.ncore-path` 后缀非法 exit 65、输出目录不可写 exit 73——排查容器退出码时别只看 python 异常。

## 相关产物

- `deepwiki/`：DeepWiki 全量页（含 4.1 jit-kelvin-adapter 等——注意勘误 #6）
- 图谱导览 14 步与 ONBOARDING 8 节一一对应；批阶段甄别笔记 15 条见仓内 `.understand-anything/NOTES-DIGEST.md`
