# Git 工作流程指南

## 🌿 分支策略

### 主要分支

| 分支 | 用途 | 保护 |
|------|------|------|
| `master` | 生产分支，只包含稳定版本 | ✅ 受保护 |
| `develop` | 开发分支，日常开发在此进行 | ⚠️ 需要审核 |

### 功能分支命名规范

```
feature/功能名称    - 新功能
fix/问题描述        - Bug修复
docs/文档描述       - 文档更新
refactor/重构描述   - 代码重构
test/测试描述       - 测试相关
```

---

## 📋 工作流程

### 1. 开始新功能

```bash
# 切换到develop分支
git checkout develop

# 拉取最新代码
git pull origin develop

# 创建功能分支
git checkout -b feature/新功能名称

# 开始开发...
```

### 2. 提交代码

```bash
# 查看修改
git status

# 添加文件
git add .

# 提交（使用规范的提交信息）
git commit -m "feat: 添加新功能描述"

# 推送到远程
git push origin feature/新功能名称
```

### 3. 创建Pull Request

1. 访问 GitHub 仓库
2. 点击 "Compare & pull request"
3. 填写PR描述
4. 等待审核

### 4. 合并到develop

```bash
# PR审核通过后，合并到develop
git checkout develop
git pull origin develop
git merge --no-ff feature/新功能名称
git push origin develop

# 删除功能分支
git branch -d feature/新功能名称
git push origin --delete feature/新功能名称
```

---

## 📝 提交信息规范

### 格式

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Type类型

| 类型 | 说明 | 示例 |
|------|------|------|
| `feat` | 新功能 | `feat: 添加量子计算词典` |
| `fix` | Bug修复 | `fix: 修复公式显示错误` |
| `docs` | 文档更新 | `docs: 更新README` |
| `style` | 格式调整 | `style: 统一Markdown格式` |
| `refactor` | 重构 | `refactor: 重构词典结构` |
| `test` | 测试 | `test: 添加单元测试` |
| `chore` | 构建/工具 | `chore: 更新.gitignore` |

### 示例

```bash
# 好的提交
git commit -m "feat: 添加量子场论词典

- 包含QED、QCD基础内容
- 添加费曼图解释
- 更新索引文件

Closes #123"

# 不好的提交
git commit -m "update"
git commit -m "fix bug"
```

---

## 🔒 分支保护规则

### master分支

- ❌ 禁止直接推送
- ✅ 必须通过PR合并
- ✅ 需要至少1个审核
- ✅ 必须通过CI检查

### develop分支

- ⚠️ 建议通过PR合并
- ✅ 可选审核

---

## 🛠️ 常用命令

### 日常操作

```bash
# 查看状态
git status

# 查看历史
git log --oneline --graph --all

# 查看远程仓库
git remote -v

# 同步所有分支
git fetch --all

# 暂存工作
git stash
git stash pop
```

### 分支操作

```bash
# 查看所有分支
git branch -a

# 创建分支
git checkout -b 分支名

# 切换分支
git checkout 分支名

# 删除本地分支
git branch -d 分支名

# 删除远程分支
git push origin --delete 分支名
```

### 回滚操作

```bash
# 撤销工作区修改
git checkout -- 文件名

# 撤销暂存
git reset HEAD 文件名

# 回退提交（保留修改）
git reset --soft HEAD~1

# 回退提交（丢弃修改）
git reset --hard HEAD~1

# 查看操作历史
git reflog
```

---

## 📊 项目管理

### 里程碑 (Milestones)

用于追踪大版本或重要更新

1. 访问 GitHub → Issues → Milestones
2. 创建里程碑，设置截止日期
3. 将Issues关联到里程碑

### Issues管理

#### 标签 (Labels)

| 标签 | 用途 |
|------|------|
| `bug` | Bug报告 |
| `enhancement` | 功能增强 |
| `documentation` | 文档相关 |
| `good first issue` | 适合新手 |
| `help wanted` | 需要帮助 |
| `priority: high` | 高优先级 |

#### Issue模板

```markdown
## 描述
[问题的详细描述]

## 复现步骤
1. 步骤1
2. 步骤2
3. 步骤3

## 期望行为
[应该发生什么]

## 实际行为
[实际发生了什么]

## 截图
[如有必要，添加截图]

## 环境
- OS: [操作系统]
- Version: [版本号]
```

---

## 🔄 GitHub Actions (可选)

### CI/CD工作流

创建 `.github/workflows/ci.yml`:

```yaml
name: CI

on:
  push:
    branches: [ master, develop ]
  pull_request:
    branches: [ master, develop ]

jobs:
  build:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: 检查Markdown格式
      run: |
        # 添加你的检查脚本
        
    - name: 检查链接
      run: |
        # 添加链接检查
```

---

## 📈 项目统计

```bash
# 查看贡献者
git shortlog -sn

# 查看文件变更统计
git log --stat

# 查看代码行数统计
git ls-files | xargs wc -l

# 查看提交频率
git log --pretty=format:"%ad" --date=short | sort | uniq -c
```

---

## 🎯 最佳实践

### 提交频率
- ✅ 小步提交，频繁推送
- ✅ 每个提交只做一件事
- ❌ 避免大批量提交

### 提交信息
- ✅ 清晰描述做了什么
- ✅ 说明为什么这样做
- ❌ 避免模糊的描述

### 分支管理
- ✅ 及时删除已合并的分支
- ✅ 保持分支结构清晰
- ❌ 避免长期存在的功能分支

### 代码审核
- ✅ 认真审核每个PR
- ✅ 提供建设性反馈
- ❌ 不要急于合并

---

## 📞 需要帮助？

- Git官方文档: https://git-scm.com/doc
- GitHub文档: https://docs.github.com
- 项目Issues: https://github.com/leemiracle/lean4ai/issues

---

*最后更新: 2025-03-26*
