# 01 — 规范精读：SKILL.md 解剖

> 「讲透 Skills」第二篇。逐字段拆解 [Agent Skills 正式规范](https://agentskills.io/specification)（2025-12-18 开放标准，一手核实 2026-08-25）。写 skill 前的必读手册。

---

## 1. 目录结构：一个最小单元和三个可选抽屉

```
skill-name/
├── SKILL.md          # 唯一必须：元数据 + 指令
├── scripts/          # 可选：可执行代码（确定性任务交给真代码）
├── references/       # 可选：按需加载的文档
├── assets/           # 可选：输出用的静态资源（模板/图标/数据表）
└── ...               # 任意其他文件（规范不禁止）
```

三个抽屉的分工哲学：

| 抽屉 | 装什么 | 进上下文吗 | 典型例子（anthropics/skills 实测） |
|---|---|---|---|
| `scripts/` | 可执行代码 | **不进**——agent 直接 spawn 进程跑 | pdf 的文本抽取、xlsx 的电子表格操作 |
| `references/` | 详细文档 | 按需读（正文里指路） | FORMS.md 表单模板、各云平台部署手册 |
| `assets/` | 静态资源 | 按需用 | PPT 模板、品牌图标、JSON schema |

> **scripts/ 是官方"杀器"**：官方文档 skills（docx/pdf/pptx/xlsx，Claude 文档能力的生产引擎）的核心逻辑全是 Python 脚本——agent 负责"决定何时调"，代码负责"精确执行"。LLM 模拟 Excel 操作是灾难，spawn 一个 openpyxl 脚本是毫秒级精确。

## 2. YAML frontmatter：2 个必填 + 4 个可选 + 1 个实验性

### `name`（必填）—— 64 字符的身份证

| 约束 | 说明 |
|---|---|
| 1-64 字符 | 超长直接不合规 |
| 只许 `a-z 0-9 -` | 小写字母/数字/连字符（**大写非法**） |
| 不能 `-` 开头/结尾 | `-pdf` ✗ |
| 不能连续 `--` | `pdf--processing` ✗ |
| **必须与父目录同名** | `pdf-processing/SKILL.md` 里只能写 `name: pdf-processing` |

### `description`（必填）—— 1024 字符的检索键

规范原文给了好/坏对照：

```
✅ Good: "Extracts text and tables from PDF files, fills PDF forms, and merges
   multiple PDFs. Use when working with PDF documents or when the user
   mentions PDFs, forms, or document extraction."
❌ Poor: "Helps with PDFs."
```

三条要求：①说清做什么 ②说清**何时用**（触发场景）③包含 agent 能匹配任务的关键词。**这是 skill 被用起来的唯一机制**——深度展开见 [03](03-路由与触发-description即检索键.md)。

### 可选字段（按使用频率排序）

| 字段 | 约束 | 何时用 |
|---|---|---|
| `license` | 短字符串或指向打包的 LICENSE 文件 | 开源发布时（如 `Apache-2.0`） |
| `metadata` | string→string 的任意 map | 版本号/作者等扩展信息（客户端自定义） |
| `compatibility` | ≤500 字符 | **只在有硬环境要求时写**（如 "Requires Python 3.14+ and uv"）。多数 skill 不需要 |
| `allowed-tools` | 空格分隔的工具白名单（**实验性**） | 如 `Bash(git:*) Bash(jq:*) Read`——预授权工具，支持度因实现而异 |

> 规范设计哲学：**必填最小化（2 字段），扩展点全部可选**。metadata 是给客户端留的逃生舱——规范不认识的自定义键都塞这里，避免各家私扩字段导致分裂。

## 3. 正文：没有格式限制，但有两条软约束

Markdown 正文就是给 agent 的指令。规范"无格式限制"，但官方最佳实践强烈建议：

1. **≤500 行**。超过就拆——详细内容移入 `references/`，正文里留指路句（"详见 references/REFERENCE.md"）。
2. **文件引用一层深**。`references/` 里的文件不要再引用 `references/` 里的另一个文件——避免 agent 递归跳转迷路。

推荐章节结构（规范建议）：步骤化指令 / 输入输出示例 / 常见边界情况。

## 4. 渐进披露：规范的灵魂条款

```
第1层  元数据     name + description     启动时常驻（全部 skills 共 ~100 tok/个）
第2层  正文       SKILL.md body          触发时才装（建议 <5000 tokens）
第3层  资源       scripts/references/assets  按需，甚至不进上下文（直接执行）
```

这不是实现细节，是**规范正文规定的加载模型**。它回答了"装 100 个 skill 会不会撑爆上下文"——不会，常驻代价只有第 1 层。完整经济学分析 → [02](02-渐进披露与上下文经济学.md)。

## 5. 验证：skills-ref

规范自带官方校验器（[agentskills/agentskills 仓](https://github.com/agentskills/agentskills) 的 `skills-ref` 库）：

```bash
npx skills-ref validate ./my-skill
# 检查：frontmatter 合法性、name 命名规范、必填字段
```

本站实验室的 [E3](experiments/03_spec_validator.py) 是它的本地复刻（纯 Python，验证 name/description 全部约束）——写完 skill 过一道，避免 marketplace 上架被拒。

## 6. 一个完整合规样例（可直接抄）

```
math-olympiad/
├── SKILL.md
│   ---
│   name: math-olympiad
│   description: Solves olympiad math problems with rigorous step-by-step
│     proofs. Use when the user asks competition math, algebraic inequalities,
│     number theory, or combinatorics problems that require proofs, not just
│     numeric answers.
│   license: MIT
│   metadata:
│     author: your-name
│     version: "1.0"
│   ---
│   # Math Olympiad Solver
│   ## 方法
│   1. 判断领域（代数/数论/组合/几何）
│   2. 按 references/STRATEGIES.md 的分领域策略选主攻方向
│   3. 数值实验用 scripts/sagemath_check.py 验证猜想
│   ## 边界
│   - 计算题（不需要证明）→ 直接算，不用本 skill 的证明框架
├── scripts/
│   └── sagemath_check.py
└── references/
    ├── STRATEGIES.md
    └── INEQUALITIES.md
```

## 7. 批判视角：规范的三个留白

1. **无签名/无校验和机制**——恶意 skill（scripts/ 里的任意代码）是真实威胁，规范只靠"贡献者自律 + 平台审核"。装第三方 skill 前先读 scripts/，就像装 npm 包前看 postinstall。
2. **allowed-tools 还是实验性**——工具白名单本该是安全边界，但"各实现支持度不一"意味着不能依赖它做防护。
3. **40+ 实现语义漂移**——同一 SKILL.md 在不同 agent 里的触发行为、资源加载时机有差异（openclaw 的 42 挂点实测就是证据）。跨工具发布的 skill 要在目标工具里实测。

## ✍️ 练习

1. 给 00 章练习 1 里你写的 skill 加上 `license` + `metadata` + 一个 `references/` 文件，保持正文 <100 行。
2. 故意写 5 个不合规的 name（大写/双连字符/超 64 字符/首尾连字符/与目录不同名），然后用 E3 脚本验证你能否全部抓住。
3. （思考）为什么规范强制"必须与父目录同名"？（提示：文件系统是 skill 的真身，SKILL.md 里的 name 是元数据镜像——两处不一致时信谁？）

---

**下一篇**：[02 — 渐进披露与上下文经济学](02-渐进披露与上下文经济学.md)
