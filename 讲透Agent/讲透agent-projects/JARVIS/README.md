# 讲透 JARVIS（microsoft/JARVIS，25.5k star）

微软 HuggingGPT 论文官方仓全链知识基座：图谱 + ONBOARDING + explain 6 篇（2026-11-02）。

| 链路 | 终态 |
|---|---|
| 图谱 | **188n/297e/13层/16步tour**，validator 0 issues 0 warnings，fingerprints 88 文件@7624cf38 |
| onboarding | ONBOARDING.md 6477 字 8 节 71 锚 |
| explain | 6 篇（awesome_chat 四阶段/模型服务/prompt 资产/web 前端/EasyTool/TaskBench），217 锚独立终验 **0 坏**，内容抽验 10 处全命中 |
| NOTES-DIGEST | 9 条批阶段甄别笔记 |
| 图谱位置 | 仓内 `.understand-anything/knowledge-graph.json`（/usr-data/data2/repos/agent-repos/microsoft/JARVIS） |

## 三子项目结构

HuggingGPT 本体（任务规划→模型选择→模型执行→响应生成四阶段 LLM agent，awesome_chat.py 核心）+ EasyTool（工具指令基准执行器）+ TaskBench（任务级数据生成与推理评测）。

## 源码级勘误精华（10 条全清单见 ONBOARDING）

- **taskbench/evaluate.py:60-62 匈牙利图匹配是死代码**（零调用；实际指标全是 "No Matching" 直接集合 F1；"图编辑距离"实为 Levenshtein 工具 id 序列相似度 evaluate.py:528-536）——推翻图谱摘要说法
- **taskbench/inference.py:161 默认参数首跑必 NameError**；run_gradio_demo.py:59/:68 `uuid.uuid4()[:4]` TypeError（UUID 不可切片）
- evaluate.py:415-423 参数指标变量交叉（P/R 镜像，binary F1 靠对称性幸存）；models_server.py:504 恒假条件死分支
- TaskBench README 称 28271 样本，盘上三域实数 17331 条（7458+5555+4318）
- easytool toolbench_retrieve.py 与 toolbench.py 90% 同构（diff 实证）；funcQA.py:539/:623 depend_id=[1] 硬编码

## explain 索引

01 awesome_chat 四阶段核心引擎 · 02 models_server 本地模型服务与显存互斥 · 03 prompt 资产与 LLM 输出解析（while True+eval 重试） · 04 web 前端 Gradio+Vue 链路 · 05 EasyTool 工具指令与四基准执行器 · 06 TaskBench 数据生成与推理评测
