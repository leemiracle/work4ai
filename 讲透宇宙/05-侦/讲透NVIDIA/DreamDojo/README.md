# 讲透 DreamDojo

> NVIDIA DreamDojo——**Cosmos Predict2 世界模型训练/微调框架**（imaginaire 训练基础设施+text2world/video2world+Self-Forcing/DMD2 蒸馏+GR00T RL+LAM 双副本）。

## 全链状态表

| 阶段 | 状态 | 产出 |
|---|---|---|
| understand 图谱 | ✅ 2026-11-07 | 仓内 `.understand-anything/knowledge-graph.json`：**2088n/4968e/14 层/15 步 tour**，fingerprints 678@02f119b7 |
| onboarding | ✅ 2026-11-07 | `onboarding/ONBOARDING.md`（8 节 8788 字不计空格，94 锚） |
| explain 12 篇 | ✅ 2026-11-07 | `explain/01-12` 合计 **57962 字符**，抽验 72 锚 0 坏 |

## 战况（40 批）

四 worker 两波+末段。**两次数据事故零损失**：①batch 17-20 产物被并行 worker 清理动作误删（12:49-53 窗口）→tmp 生成器重跑恢复；②batch 25-32 同窗被清→w4 按上下文原样重建+**.bak 备份防线**（新钉版：多 worker 同目录时产出即备份）。终验抓出 54 个副本文件节点缺失（related 边发了但漏建副本自身节点）→补建至 678/678 全覆盖。

## 甄别精选（源码级实证）

1. **上游潜伏 bug**：`attention/frontend.py:421` 的 `key.reshape` 应为 `value.reshape`（上游未爆雷）
2. **CFG 公式不一致**：text2world(:508) vs video2world(:209) 两处实现
3. `torchtitan_utilts.py` 文件名拼写笔误（reason1/parallelisms/ 四处 import 沿用）
4. `CheckpointMode` 四处平行定义（非三处）；`ImaginaireTrainer` 双定义；`tokenizers/cosmos.py` 名实不符（实为 Wan VAE 配置表）
5. `Text2WorldModel`=`DiffusionModel` 别名（十处 import）
6. **LAM 双副本定性**：研究版=确定性均值编码器（lam.py:57 assert T==2）/生产版=完整后验采样训练工程
7. qwen2_vl/qwen2_5_vl=HF 移植+cp_mesh/DTensor 上下文并行魔改
8. 坑：eval/launch 脚本硬编码 /mnt/amlfs-01 内部 AMLFS 路径；start_gradio_app.sh 默认 GRADIO_APP 路径不存在；lam_project test.sh 引用 lam.yaml 不存在（实存 lam_0.yaml）；根 bin//pyrefly*.toml/conftest 等为 packages/cosmos-oss 字节级副本；guardrail 五过滤器全是占位桶；shared_meta 十 JSON 零 .py 引用

## 分层速览（14 层，680 文件节点）

入口构建(22) → 训练配方门面(30) → attention 四后端(41) → imaginaire 训练核心(115) → 数据与护栏(75) → predict2 网络(39) → 数据与条件(58) → 实验配置(72) → 推理蒸馏 Self-Forcing+DMD2(69) → reason1 VLM(29) → GR00T RL(16) → LAM 双副本(18) → packages(77) → 文档脚本副本(19)

*2026-11-07 · cuda-stack-第七轮会话（舰队认领）*
