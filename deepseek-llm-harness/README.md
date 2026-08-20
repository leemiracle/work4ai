# deepseek-llm-harness

> DeepSeek 引擎 + 六组件骨架 + **LLM 算法研究与应用领域插件**（2026-08-20 新建）。
> 家族第四成员：kernel（运行时验证）→ rust（编译期验证）→ rl（学习方向验证）→ **llm（生成质量验证）**。

## 定位

- **算法研究侧**：训练/微调/评测代码的可信闭环（防静默退化——数据泄漏、tokenizer 漂移、评测作弊）
- **应用侧**：prompt/RAG/微调/agent 四种模式的工程纪律

## LLM 版金字塔（为什么变形）

| 层 | 关注 | LLM 特有失败模式 |
|---|---|---|
| L3 生成冒烟 | 真加载+真生成+PPL 自检（**三级降级诚实标注**：A 真生成/B tokenizer/C 配置） | 模型坏了还在跑管线 |
| L4 最小评测 | PPL+重复率健全性 | "提升"实为退化 |

governance 三病 LLM 形态：Goodhart = **评测作弊**（judge prompt/评测集/跳评测）；盲区 = tokenizer+数据管线；冲突 = 模型/checkpoint 目录。

## 本机实测（2026-08-20）

```
python3 tools/llm_smoke.py
→ [L3] 模式 A（真生成）: 生成='在机器学习和深度学习中，损失函数是衡量模型预测结果与真实目标之间的差异' NLL=4.960
→ SMOKE PASS（模式A：真加载+真生成+NLP 统计健全）
```

## 快速开始

```bash
python3 llm_host.py --self-test
python3 tools/llm_smoke.py
python3 tools/llm_eval.py --texts your.txt
export KH_API_KEY=... LLM_PROJECT=/path/to/exp
python3 llm_host.py --task "给 SFT 数据管线补泄漏检查并过 L2-L4"
```

## 结构

```
llm_host.py          宿主：六组件 + cascade，LLM 工具表
engines/ hooks/ governance/    与家族复用（hooks 为 LLM 特化版：拦权重进 git/删模型/hf 上传/手编评测集）
tools/llm_lint.sh / llm_test.sh   L1/L2
tools/llm_smoke.py   L3 生成冒烟（三级降级；模式A实测通过）
tools/llm_eval.py    L4 PPL+重复率（--texts）
knowledge/llm_knowledge.md   算法谱系+应用模式卡+本地环境锚点
AGENTS.md            LLM 研究契约（tokenizer 是合同/评测集只读/同预算对比）
```
