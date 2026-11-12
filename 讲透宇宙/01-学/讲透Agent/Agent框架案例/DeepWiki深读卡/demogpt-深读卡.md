# demogpt 深读卡 —— "描述即应用"的 Streamlit 生成器：plan-based 管线把自然语言变成 LangChain 应用

> **定位**：melih-unsal 出品的开源系统（2023）：输入一句自然语言指令，自动生成可运行的 LangChain+Streamlit 应用——LCEL 代码、UI、依赖全包，主打"零代码创建 LLM 应用"。核心是 **plan-based pipeline**：指令→计划→代码→自精炼（self-refinement）的多阶段变换，是"text-to-app"早期代表（与 GPT-Engineer 同期同思潮）。
> **本地**：`repos/demogpt`（melih-unsal/DemoGPT）｜**深读**：deepwiki 24 子页归档 `deepwiki/demogpt/full.md`（2026-08-21）

## 一、组件栈（DeepWiki 蒸馏）

| 层 | 职责 | 关键实体 |
|---|---|---|
| 交互层 | 指令输入与应用预览 | Streamlit host UI |
| 计划层 | 指令→开发计划 | plan-based pipeline 第一阶段 |
| 生成层 | 计划→LangChain 代码+Streamlit UI | code generation（文档处理/聊天/搜索三类模板） |
| 精炼层 | 生成代码自纠错 | self-refinement loop |
| 运行时 | 生成的应用即跑 | 生成的 Streamlit app（requirements 自带） |

## 二、核心机制

1. **plan-based pipeline**：不一次性生成整个应用，而是先产结构化开发计划，再按计划逐阶段生成（指令→plan→代码→UI）——与 gpt-pilot 的 epic/task/step 分解同思想，轻量版。
2. **self-refinement**：生成代码经运行校验，失败信息回喂 LLM 修正再生成——生成-验证-修复闭环的最小实现。
3. **模板化能力域**：支持的应用类型收敛在文档处理/chat/web search 等成熟模板——用"能力模板"换生成可靠性（对比完全自由生成的 GPT-Engineer）。

## 三、与讲透系列的对位

| demogpt 概念 | 讲透系列对应概念 |
|---|---|
| plan-based pipeline | 讲透Agent/03 §规划（先计划后生成） |
| self-refinement | 讲透Agent/00 §自纠错循环 |
| 模板约束生成 | 讲透代码生成 §约束换可靠 |

## 四、关键入口

```
demogpt/              # 核心包（pipeline 阶段）
app.py                # Streamlit 宿主 UI
prompts/              # 各阶段提示词
```

## 五、深读子页地图（24 页精选 4）

Overview（管线 mermaid）｜Features and Capabilities｜System Architecture｜pipeline/refinement 章节。

## 六、与"我们"的关系（一句话）

"自然语言→完整可跑应用"教学的最小标本——管线短、代码少，适合讲透代码生成章做"text-to-app 潮流"的开场案例（对照 gpt-pilot 重量级实现）。

---
生成：2026-08-21 · deepwiki 24 页全归档
