# 讲透 Judges-Verdict

> NVIDIA 的 LLM-as-Judge 评测框架：用 26 个主流裁判模型对同一批生成答案打分，量化裁判自身的一致性与质量。Python 3.12+，LiteLLM 官方支持路线。

## 全链状态表（2026-11-08）

| 阶段 | 状态 | 产出 |
|---|---|---|
| 批分析 | ✅ 4 批 | 44 节点 / 83 边（intermediate，已 finalize 清理） |
| merge | ✅ 零丢失 | 无悬空边，imports recovery 0 |
| layers/tour | ✅ | 9 层 / 12 步 |
| finalize | ✅ validator 0/0 | knowledge-graph.json（44n/83e） |
| fingerprints | ✅ | 19 files @ dfbcd5ee |
| onboarding | ✅ | ONBOARDING.md 4971 字 / 30 锚 |
| explain | ✅ 3 篇 | judge-config-manager（2480 字/26 锚）/ llm-judge-scoring（2474 字/27 锚）/ litellm-ragas-wrapper（2459 字/23 锚） |
| 锚终验 | ✅ 真坏 0 | 114 锚全好（onboard 33/33 + explain 81/81） |

图谱在仓内 `/usr-data/data2/repos/agent-repos/NVIDIA/Judges-Verdict/.understand-anything/knowledge-graph.json`。

## 源码甄别（写作期实证，非 README 口径）

1. **utils/__init__.py 的 `__all__ = ["llm_score_utils"]` 是陈旧声明**——该模块不存在，目录内实际文件是 `litellm_ragas_wrapper.py`；星号导入形同虚设。
2. **两个 notebook 均为 119 字节 0 cells 空壳占位**（`notebooks/01_Quick_Start_Example.ipynb`、`02_Analyze_Results.ipynb`）——README 若指向 notebook 教程，实际无可读内容。
3. **`scripts/data_prep.py` 的 datasets 依赖是函数体 try-import + 自动 pip install**——不是声明式依赖，离线环境会现场联网装包。
4. `.flake8` 被 scanner 归类 code/unknown，按实质为 config 节点（120 字符行宽对齐 black）。
5. 评分引擎 `run_judge_evaluations` 207 行为断点续跑设计（每 trial 立即写 checkpoint）+ 对 o1/o3 模型 monkey-patch 温度。

## 阅读路线

新人按 `onboarding/ONBOARDING.md` 八节走；深读按 explain 三篇：配置心脏 judge_config_manager.py → 评分主链路 llm_judge_scoring.py → LiteLLM 直连适配 litellm_ragas_wrapper.py。
