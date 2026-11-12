# 讲透 Isaac-GR00T（NVIDIA Isaac GR00T N1.7）

> 仓库：`/usr-data/data2/repos/agent-repos/NVIDIA/Isaac-GR00T`（commit `51d4c89f`，2026-11-07 全链完成）
> NVIDIA Isaac GR00T N1.7——开源 VLA（视觉-语言-动作）机器人基础模型的微调/推理/评测/部署框架：Qwen3-VL 骨干 + flow matching DiT 动作头 + GR00T 风味 LeRobot v2 数据体系。

## 全链状态表

| 阶段 | 状态 | 产物与指标 |
|---|---|---|
| prepare（scan/batches） | ✅ | 323 文件 / 29 批（batches.json，186 py） |
| 批分析（file-analyzer ×29 批） | ✅ | 40 个批产物文件（b1-b6/b26-b29 派 7 组子代理，b7-b25 主会话直做）；imports 对账 254 scanner 条全保留 + ast 手扫补 ~80 条（延迟 import/sys.path 注入/ipynb 零覆盖盲区） |
| 终验 | ✅ | json.load 40/40；唯一 ID 1017；文件覆盖 323/323（补漏 examples/DROID/README.md 后全绿） |
| merge | ✅ | `assembled-graph.json` 1017n/1769e；丢 2 边（缺 function 节点）已回补 → **1018n/1771e** |
| layers | ✅ | 14 层（仓基座→数据→模型→训练→推理→评测→部署→示例→测试→文档），323/323 恰好一层、零重复零遗漏（主会话独立复核） |
| tour | ✅ | 16 步新人导览，73 节点引用全部有效 |
| finalize | ✅ | `knowledge-graph.json` **1018 节点 / 1771 边 / 14 层 / 16 步**，validator **0 issues 0 warnings**，fingerprints **323 文件 @51d4c89f** |
| onboarding | ✅ | `onboarding/ONBOARDING.md`——8 节 9984 字（不计空格）95 锚 |
| explain | ✅ | `explain/` 8 篇 ×2500-4800 字，合计 38,259 字符 / **421 锚**（148 路径形+273 裸 `:N` 形，界内校验 0 坏，语义抽验 24/24 命中） |

产物入口：`onboarding/ONBOARDING.md`（上手总览）→ `explain/01..08`（核心文件精讲）→ 仓内 `.understand-anything/knowledge-graph.json`（图谱本体）。

## explain 索引

| 篇 | 主题 | 覆盖文件 |
|---|---|---|
| 01 | N1.7 模型主管线 | gr00t/model/gr00t_n1d7/gr00t_n1d7.py（骨干+动作头+RTC） |
| 02 | DiT 流匹配动作头 | modules/dit.py + embodiment_conditioned_mlp.py |
| 03 | Qwen3-VL 骨干封装 | modules/qwen3_backbone.py（gated/RoPE/channels_last） |
| 04 | Processor 与 Collator | processing_gr00t_n1d7.py（归一化/逆变换/VLM 桥） |
| 05 | 数据契约层 | data_config + embodiment_tags + so100_config + types.py |
| 06 | 数据加载管线 | lerobot_episode_loader + factory + sharded_*（种子不变式） |
| 07 | 训练入口 | launch_finetune + experiment.run + Gr00tTrainer + DeepSpeed 分流 |
| 08 | 策略推理与服务化 | gr00t_policy + run_gr00t_server + server_client（pickle 边界） |

## 源码级甄别清单（22 条，全部锚定实证）

**架构与命名**
1. `gr00t/__init__.py` 388 行**不是包 barrel**，是测试期对 HF transformers 的 monkey patch 集合（零业务导出）——别当 API 入口。
2. `scripts/deployment` 不是 Python 包，内部靠 `sys.path` 前插**裸名互导**（`from _trt_contract import ...`），测试同姿势（b28 实证 37 条 imports 全靠 AST 重建——scanner 对该模式 batchImportData 42 文件 41 空）。
3. `trt_model_forward.py` 三个前向分工命名易混：`tensorrt_forward`=TRT ViT+PyTorch LLM、`llm_trt_forward`=PyTorch ViT+TRT LLM、`full_trt_forward`=双 TRT。
4. `embodiment_configs.py` 对 ActionFormat 等符号是 **re-export**，实定义在 `gr00t/data/types.py`。
5. `tests/test_support/` 是顶层包（tests/ 在 sys.path），`conftest.py:70` 有函数体延迟 import。
6. `docker/build.sh` 的 thor/orin profile 指向 `scripts/deployment/{thor,orin}/Dockerfile`——**仓内不存在，死分支**（仅 jetson/spark 存在）；`tools/check_manifest_alignment.py` 引用的 `{orin,thor}/pyproject.toml` 磁盘存在但 scanner 未收录（图谱缺口）。
7. `activate_orin.sh`/`activate_thor.sh` 头注释残留 "activate_jetpack72.sh" 字样（复制未改名，代码正确）。
8. `setup_RoboCasa.sh` 是 robocasa/robocasa365 **双变体统一安装器**（依赖矩阵互斥：fork 变体 mujoco 3.2.6+numpy 1.26.4 vs 365 变体 numpy 2.2.5+mujoco 3.3.1），`setup_RoboCasa365.sh` 仅设 ROBOCASA_SETUP_VARIANT 后 exec 转发。

**模型与训练**
9. RTC（实时控制 inpainting/ramp）机制在仓内**无消费者**——`gr00t_policy.py:417` 调 `model.get_action` 不传 options（01 篇实证）。
10. `Qwen3Backbone` docstring 的 "generate n_queries" 是 **Eagle 骨干旧注释**残留，与 Qwen3-VL 实际机制无关。
11. `Gr00tTrainer` docstring 自称 "bypasses torch dataloader and makes data collator async"，实际返回标准 `torch.utils.data.DataLoader`（`trainer.py:218`）；`_PrefetchIterator`/`_BatchIterator` 全仓 grep **零调用=死代码**（真正的预取在数据集侧 ThreadPoolExecutor）。
12. resume 语义=**重播种 rank 对称**（`reset_seed(seed+global_step)`）而非跳数据——IterableDataset 不可 seek 的代价，代码三处明示"不可精确复现"。
13. Gr00tN1d7Processor 默认骨干 `nvidia/Cosmos-Reason2-2B`（gated repo，需 hf auth）；`Qwen3VLForConditionalGeneration` 是 try/except 可选依赖。
14. processor 默认 `max_state_dim=29` 是 N1.5 时代遗产值（04 篇）；普通 `DiT` 的 `encoder_attention_mask` 形参**未使用**（仅 AlternateVLDiT 用）。
15. DeepSpeed zero2/zero3 json 的真实消费方是 `base_config.py:155` `get_deepspeed_config`（不是 finetune 脚本）；json 内 batch/fp16 均为 "auto" 由 HF Trainer 注入。
16. transformers 最低版本两处口径不一（pyproject 4.57.3 vs 某检查脚本 4.52，01/03 篇实证）。

**数据与示例**
17. `examples/DROID/main_gr00t.py` 的旋转矩阵与 `compute_eef_9d` 是 `gr00t/data/state_action/droid_frame.py` 的**注释钉版镜像**（无 import 关系，audit 注释要求同步维护）——示例跑在无 gr00t 包的精简环境。
18. `examples/SimplerEnv/simpler_env.py` 的自指 import（`import simpler_env`）实为**外部 pip 包同名**，非仓内引用（禁自环丢弃）。
19. `episode_lengths` 口径=**内层 env-step**（n_env_steps）非宏步数（b5 甄别）。
20. `tests/examples/test_extra_augmentation.py` 名为 test 实为 argparse CLI 可视化工具（不被 pytest 收集）。
21. `tests/gr00t/eval/test_rollout_max_episode_steps.py` 不 import rollout_policy，而是 **ast.parse 读源码静态断言**（发 depends_on 非 imports）。
22. `MsgSerializer` 绕开 msgpack_numpy 高层封装自建安全链：后者 hook 链顺序会让伪造 `{nd:True}` 包先进 `pickle.loads`（`server_client.py:36-44`）——机器人网络接口的反序列化边界正面处理（08 篇）。

## 评测与硬件速查

- **评测环境**：LIBERO（franka）/SimplerEnv（WidowX+Google Robot）/robocasa(+365)（panda）四套，各自独立 venv 孤岛（SimplerEnv 唯一 py3.10，其余 3.12）；`external_dependencies/` 四子模块（.gitmodules）。
- **硬件矩阵**：x86/GB200=仓根 pyproject（torch 2.9，cu12/cu13 marker 分叉）；Jetson JetPack 7.2=CUDA 13.2；DGX Spark=CUDA 13.0；裸机用 `scripts/activate_*.sh`；主 Dockerfile 单文件双架构（aarch64 先 bootstrap torchcodec wheel）。
- **checkpoint**：基座 `nvidia/GR00T-N1.7-3B`（预训练 8 标签开箱即用），微调版 N1.7-DROID/-SimplerEnv-Bridge 等（posttrain 标签）；自定义本体走 `NEW_EMBODIMENT`。

> 口径说明：字数均为"不计空格总字符"；行号锚格式 `文件:行号`（含裸 `:N` 段内形式），全部于 commit 51d4c89f 界内校验。图谱支持增量（fingerprints 基线），后续上游更新可走 vLLM 轮"手术合并"范式。
