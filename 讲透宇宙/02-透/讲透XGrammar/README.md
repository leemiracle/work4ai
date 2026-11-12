# 讲透 XGrammar · 深度知识库

> 基于 DeepWiki 全量文档 + understand-anything 中文知识图谱 + 核心源码深解的 XGrammar 学习知识库。
> 生成于 2026-09-05，对应源码 commit `c30554f7`（2026-09-02）。

## 这是什么

XGrammar 是高效灵活可移植的**语法引导生成库**（grammar-guided generation for LLMs）：EBNF / JSON Schema / 正则 / 结构标签多格式输入统一编译为 per-rule FSM 与 adaptive token mask，Earley 解析器运行时校验并生成 token 级 bitmask 约束 LLM 采样，CPU/CUDA/Triton 多后端。被 vLLM / SGLang / MLC-LLM / TensorRT-LLM 等主流推理引擎集成。

| 场景 | 用哪部分 | 怎么用 |
|---|---|---|
| 新人系统上手 | `onboarding/ONBOARDING.md` | 从头读：项目总览→12 层架构→11 个关键概念→15 步学习路径→文件地图→复杂度热点 |
| 按图索骥查专题 | `deepwiki/`（64 页） | 查 `deepwiki/INDEX.md`，按章节号直达 |
| 啃核心源码 | `explain/`（6 篇） | 每篇一个核心文件的深度解析：角色定位→内部结构→外部连接→数据流→设计决策→新人提示 |
| 交互式探索 | 知识图谱（仓内） | 1305 节点/1788 边/12 层/15 步导览全中文图谱，位于 `~/ai/xgrammar/.understand-anything/knowledge-graph.json`，用 `/understand-chat`、`/understand-dashboard` 交互查询 |

## 目录结构

```
讲透XGrammar/
├── README.md                  # 本文件
├── deepwiki/                  # DeepWiki 全量抓取（64 页 + INDEX.md + _coverage-check.md）
├── onboarding/
│   └── ONBOARDING.md          # 新人上手指南（5975 字，8 节，源码交叉验证）
└── explain/                   # 6 篇核心文件深解
    ├── xgrammar-grammar.md            # CSR 语法表示 + 五工厂入口
    ├── xgrammar-compiler-functors.md  # 22 个编译 pass + 双级缓存
    ├── xgrammar-fsm.md                # FSM 族 + NFA→DFA→Minimize（1996 行核心）
    ├── xgrammar-earley-matcher.md     # Earley 运行时 + bitmask + 投机回滚
    ├── xgrammar-tokenizer-mask.md     # 词表分析 + adaptive mask 三模式
    └── xgrammar-python-api.md         # XGRObject FFI 四件套
```

## 推荐阅读路径

```
ONBOARDING.md（1h，全局观）
   ↓ 查概念细节
deepwiki/ 对应章节
   ↓ 啃 C++ 核心
explain: grammar → compiler-functors → fsm → earley-matcher
   ↓ 补运行时外围
explain: tokenizer-mask → python-api
   ↓ 想动手时
知识图谱交互探索
```

## 生成方式

- DeepWiki：64 页 100% 覆盖（直连抓取 + prose-custom 提取）
- 图谱：understand-anything 流水线（scan 246 文件 → 21 批 → 1305 节点/1788 边 → 12 层 → 15 步导览 → 校验 0 issues → fingerprints 基线）
- 指南与深解：图谱 + 源码只读交叉验证
