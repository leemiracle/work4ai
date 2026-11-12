# 讲透 cosmos（NVIDIA/cosmos 全链知识库）

NVIDIA 世界模型 Cosmos 的评测+教程仓：evaluation/cosmos3（reasoner 推理评测：vendored VLMEvalKit fork）+ cookbooks 教程群 + SFT 配方群。**cosmos-framework 本体是外部 pip 包不在仓内**——理解本仓的第一关键。

| 环节 | 状态 | 产物与指标 |
|---|---|---|
| deepwiki | ✅ 2026-10-26 | TRUE_100 |
| understand 图谱 | ✅ 2026-11-05 | 3694n/8276e/16 层/16 步 tour；双 validator 0/0；fingerprints 1097 文件@3e3c6d61；图谱在仓内 `.understand-anything/knowledge-graph.json` |
| onboarding | ✅ 2026-11-05 | 8 节+勘误表，16530 字符（不计空格），37 锚终验全好 |
| explain | ✅ 2026-11-05 | 12 篇 57513 字符（不计空格），379 锚终验全好（35 歧义锚内容归位，行号零改动） |

## explain 索引（评测栈核心 6 + 教程训练 6）

01 run.py 推理管线 / 02 smp 基座 / 03 数据集基类框架 / 04 vlm wrapper 层 / 05 cosmos_reason 双后端 / 06 API 后端层 / 07 cosmos_eval 一键评测 / 08 generator 评测基准群 / 09 reasoner 六后端教程 / 10 cookbooks 三线教程 / 11 SFT 与蒸馏配方群 / 12 数据资产群

## 源码级勘误清单（12 条，全部行号锚实证）

1. **45 个公开版剥离 stub 数据集**（17 行 RuntimeError 骨架但仍在 dataset/__init__ 注册表；cv_bench.py stub 还会被 image_mcq.py 同名真实现遮蔽）
2. **6 本孤儿 SGLang notebook**（reasoner/transfer/audiovisual/action×3 全仓 README 零收录——批分析初判 2 本，onboard 轮全仓复核纠正为 6）
3. RELEASE.md 两条版本链接指向不存在的 release_notes/v0p1.md，且记录的是旧 cosmos 世代（2025-01）与本仓 Cosmos 3（2026-05）代差
4. Quickstart.md 引用 vlmeval/vlm/internvl_chat.py——实际已重组为 internvl/ 包（文档代差）
5. requirements.txt:48 注释与包名粘连吞掉 accelerate+python-box（'# acceleratepython-box'）；qwen-vl-utils 重复两条
6. score.py:439 __main__ 调用未定义的 main()（直接运行 NameError）；common_get_game_factory 无 else 分支触发 UnboundLocalError
7. nli_entailment.py:13 类型守卫疑似写反（正常输入恒 0 分）；number_rel_diff_ratio docstring min(0,..) 与实现 max(0,..) 不一致
8. FVD.py meter.update 用 'gt_video' 键但 calculate_score 消费 'pred_video_fvd'/'overall_video'（KeyError 隐患）；PSNR/SSIM_video 的 cv2 常量名与实际转换方向相反
9. eval() 注入面：maximum_set.py:24 与 worldsense/tempcompass/qbench_video/vdc 四处对模型输出裸 eval()（OmniDocBench 的 exec 未获证实）
10. llavabench.py `from ..smp.log` 相对层级错一级（上游迁移残留，评测路径 ImportError）——按语义目标发边
11. 数据资产：coastal_road_audio.json 与 car_driving.json 字节级完全相同；car_colliding.json 全仓零消费；droid tasks.parquet 任务文本为空；fractal tasks.parquet 有 __index_level_0__ pandas 索引泄漏列
12. URSA/OJA vendored 血统：URSA=Bytedance(2025) 模型本体+DeepSeek-VL(2023-24) 视觉塔内联拷贝；OLA=qwen2 底座（非论文原版 Qwen-1）+microsoft/unilm beats+LLaVA utils

## 流水线备注

- 2026-11-04~05 单仓全链：70 批两次 1308 复活零损失；onboard 轮纠正批分析 3 处结论（孤儿 notebook 6 非 2、AGENTS.md 引用有效系 dotfile 假阴性、stub 45 非 44）
- 字数口径=不计空格总字符；锚口径=anchor_verify（basename 消歧后全绿）
