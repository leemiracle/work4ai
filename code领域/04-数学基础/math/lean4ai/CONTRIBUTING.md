# 贡献指南

感谢你考虑为 Lean4 AI 知识库做出贡献！ 🎉

---

## 📋 目录

- [行为准则](#行为准则)
- [我能做什么贡献？](#我能做什么贡献)
- [如何贡献](#如何贡献)
- [开发流程](#开发流程)
- [提交规范](#提交规范)
- [文档写作规范](#文档写作规范)

---

## 行为准则

### 我们的承诺

为了营造一个开放和友好的环境，我们承诺：

- 使用包容性语言
- 尊重不同的观点和经验
- 优雅地接受建设性批评
- 关注对社区最有利的事情
- 对其他社区成员表示同理心

---

## 我能做什么贡献？

### 📚 改进文档

文档改进是最简单也是最有价值的贡献方式：

- 修正拼写错误
- 改进解释
- 添加示例
- 翻译文档
- 更新过时信息

### 🔍 报告Bug

发现错误？请创建Issue：

1. 使用清晰的标题描述问题
2. 详细描述复现步骤
3. 说明期望行为和实际行为
4. 附上相关截图或代码

### 💡 提出新功能

有好的想法？我们很乐意听取：

1. 先搜索是否已有类似建议
2. 清晰描述功能和使用场景
3. 说明为什么这个功能有用

### 📝 贡献内容

#### 知识词典扩展

欢迎扩展词典内容：

**AI知识词典**
- 新增模型介绍
- 更新技术细节
- 添加新论文解读
- 补充代码示例

**物理学词典**
- 新增领域（如凝聚态、天体物理）
- 深化现有内容
- 添加数学推导
- 补充实验验证

#### 内容要求

- **准确性**: 确保内容科学准确
- **易懂性**: 使用费曼学习法解释
- **完整性**: 包含历史、原理、应用
- **引用**: 标注论文和资料来源

---

## 如何贡献

### 1. Fork 仓库

点击 GitHub 页面右上角的 "Fork" 按钮。

### 2. 克隆到本地

```bash
git clone git@github.com:你的用户名/lean4ai.git
cd lean4ai
```

### 3. 添加上游仓库

```bash
git remote add upstream git@github.com:leemiracle/lean4ai.git
```

### 4. 创建分支

```bash
git checkout develop
git pull upstream develop
git checkout -b feature/你的功能名称
```

### 5. 进行修改

编辑文件，添加内容。

### 6. 提交更改

```bash
git add .
git commit -m "feat: 简短描述"
```

### 7. 推送到GitHub

```bash
git push origin feature/你的功能名称
```

### 8. 创建Pull Request

1. 访问你 fork 的仓库页面
2. 点击 "Compare & pull request"
3. 填写PR标题和描述
4. 提交PR

---

## 开发流程

### 分支策略

```
master (生产)
  ↑
  └── develop (开发)
        ↑
        ├── feature/xxx (功能)
        ├── fix/xxx (修复)
        └── docs/xxx (文档)
```

### 代码审核

所有PR都需要经过审核：

1. 至少1位审核者批准
2. 通过所有检查
3. 没有冲突
4. 符合规范

---

## 提交规范

### 提交信息格式

```
<类型>: <简短描述>

<详细描述>（可选）
```

### 类型

| 类型 | 说明 | 示例 |
|------|------|------|
| `feat` | 新功能 | feat: 添加量子场论词典 |
| `fix` | Bug修复 | fix: 修正公式错误 |
| `docs` | 文档更新 | docs: 更新README |
| `style` | 格式调整 | style: 统一标题格式 |
| `refactor` | 重构 | refactor: 重组词典结构 |
| `test` | 测试 | test: 添加测试用例 |
| `chore` | 杂项 | chore: 更新依赖 |

### 示例

```bash
# 好的提交
git commit -m "feat: 添加凝聚态物理词典"
git commit -m "fix: 修正薛定谔方程的符号错误"
git commit -m "docs: 更新量子计算部分的内容"

# 不好的提交
git commit -m "更新"
git commit -m "修复"
git commit -m "123"
```

---

## 文档写作规范

### Markdown格式

```markdown
# 一级标题（文件标题）

## 二级标题（主要章节）

### 三级标题（子章节）

**粗体** 用于强调重要内容
*斜体* 用于术语

- 无序列表项1
- 无序列表项2

1. 有序列表项1
2. 有序列表项2

`代码` 用于代码片段
```

### 费曼学习法

解释概念时遵循：

1. **简单类比**: 用日常事物类比
2. **避免术语**: 少用专业术语
3. **层层深入**: 从简单到复杂
4. **举例说明**: 提供具体例子

示例：
```markdown
### 量子纠缠

**费曼解释**: 两个粒子的命运"绑定"在一起，
无论相距多远。就像一对魔法骰子，
掷出一个6，另一个也一定是6。
```

### 内容结构

每个概念包含：

1. **费曼解释** - 通俗描述
2. **数学表述** - 公式（可选）
3. **物理意义** - 原理说明
4. **应用** - 实际应用
5. **参考文献** - 论文链接（可选）

---

## 📚 资源

### 学习资源

- [Git教程](https://git-scm.com/book/zh/v2)
- [Markdown指南](https://www.markdownguide.org/)
- [GitHub Flow](https://guides.github.com/introduction/flow/)

### 相关项目

- [Lean4](https://github.com/leanprover/lean4)
- [Mathlib4](https://github.com/leanprover-community/mathlib4)
- [LeanDojo](https://leandojo.org/)

---

## 🙏 感谢

感谢所有贡献者的付出！

### 贡献者

查看所有贡献者：https://github.com/leemiracle/lean4ai/graphs/contributors

---

## 📞 联系方式

- **Issues**: https://github.com/leemiracle/lean4ai/issues
- **Pull Requests**: https://github.com/leemiracle/lean4ai/pulls

---

*本贡献指南基于 [CONTRIBUTING-template](https://github.com/nayafia/contributing-template) 制作*

*最后更新: 2025-03-26*
