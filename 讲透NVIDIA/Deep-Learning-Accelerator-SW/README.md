# 讲透 NVIDIA/Deep-Learning-Accelerator-SW

NVIDIA DLA 软件栈配套仓（算子重建 / 模型准备 / QDQ 量化翻译 / cuDLA 双模式样例）的知识基座。

## 全链状态

| 阶段 | 状态 | 产物 |
|---|---|---|
| deepwiki | 不适用 | 该仓未被 DeepWiki 收录（MCP not found）；本地源码即唯一知识源 |
| understand 图谱 | ✅ 完成 | 仓内 `.understand-anything/knowledge-graph.json`：**94 节点 / 151 边 / 10 层 / 15 步 tour**，validator 0 issues 0 warnings，fingerprints 51 文件 @25a39b07 |
| onboarding | ✅ 完成 | `onboarding/ONBOARDING.md`（6480 字符 / 48 锚 / 8 节） |
| explain | ✅ 完成 | `explain/` 5 篇（合计 9663 字符 / 73 锚，锚终验 121/121 全好含 onboard） |

## explain 索引

| 篇 | 主题 | 字符/锚 |
|---|---|---|
| 01 | 算子重建框架：Operator 黄金循环与三个基类 | 2020/20 |
| 02 | GRU 重建：RNN 循环展开成 Conv 积木（508 行天花板） | 1604/16 |
| 03 | QDQ Translator：QAT 图到 DLA 部署图的翻译层 | 2092/15 |
| 04 | 模型准备工具链：垂直/水平融合图手术 | 1798/8 |
| 05 | cuDLA 双模式样例：CUDA 协同 vs NvSci 独立 | 2149/14 |

## 图谱速览

10 层：L01 文档基座 → L02 算子框架基座（Operator/BinaryOperator/IndexSelectionOperator）→ L03 注册与测试 → L04 布尔/一元算子 → L05 张量重排 → L06 索引选择 → L07 GRU → L08 模型准备 → L09 QDQ 翻译器 → L10 cuDLA 样例。15 步 tour 从"为什么存在这个仓"走到"NvSci 内存协调"。

## 源码级勘误/钉版（本轮甄别）

1. `operators/test.py` 裸名不匹配 merge 工具 `test_`/`_test` 判定 → registry→test 的 tested_by 边被误判 prod↔prod 丢弃，测试语义保留在 imports 边（工具约定错位，非数据错误）；
2. `operators/__init__.py` 与 `operators/common/__init__.py` 是重复的 seed+logging 初始化（历史遗留双份，0xdeadbeef 种子各写一次）；
3. `.cu` 文件 tree-sitter 零提取（main.cu 提取 fn=0），本轮手扫补齐 3 函数（printTensorDesc/cleanUp/main）；main.cpp 提取 5 函数有效；
4. Makefile 按语义归 config 节点（build-system tags），规范映射表 infra→service 对 Makefile 语义失真；
5. operators/README.md 支持矩阵双列（TensorRT 暴露 vs DLA SW 原生）是软硬两栈版本解耦的一手证据（Acos：DLA SW 3.14.0 已 Native、TRT 列仍 RFE）。

完成于 2026-11-07（understand 全链单轮，7 批 51 文件零重派）。
