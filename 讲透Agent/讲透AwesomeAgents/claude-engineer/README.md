# 讲透 Doriandarko/claude-engineer

> A 层清库 · 2026-11-02 晨 · 一体 worker 全链（29 文件/4 批）

| 链路 | 状态 |
|---|---|
| 图谱 | 仓内 knowledge-graph.json：132n/209e/3层/6步，0 issues，fingerprints 29@0a9e4b30 |
| 综合讲透 | `讲透.md`：3999 字 38 锚（12/12 抽验命中） |

**一句话**：AutoGPT 2023→原生 tool_use 过渡世代的自主编程 agent，v2 单体双引擎与 v3 插件化两代同仓——ce3.py 的 pkgutil+importlib 动态装载（13 depends_on 补边）是图谱关键结构。

**勘误精选（6 条）**：ollama-eng.py 双重移植硬伤（L33 ollama.AsyncClient 却 L322 按 Anthropic SDK 调用必炸+L266 未定义变量）/requirements 三处漂移/pyproject scripts 指向不存在的 cev3 包/SystemPrompts 列 4 个不存在的工具/chat.js marked.parse 直接 innerHTML XSS 敞口/沙箱三形态安全性梯度（venv+setsid→e2b 云→裸 shell）。
