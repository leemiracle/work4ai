# Lean4 仓库管理指南

## 🎯 你的选择

基于你的需求，我提供以下方案：

---

## 📊 方案对比

| 方案 | mathlib4 | 其他仓库 | 占用空间 | 同步速度 | 推荐度 |
|------|----------|----------|----------|----------|--------|
| **A. 混合管理** | 记录信息 | Submodule | ~200MB | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| B. 全部Submodule | Submodule | Submodule | ~1.2GB+ | ⭐⭐ | ⭐⭐ |
| C. 全部记录信息 | 记录信息 | 记录信息 | 最小 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| D. 全部忽略 | 忽略 | 忽略 | 最小 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |

---

## ✅ 推荐方案：混合管理（方案A）

### 为什么推荐？

1. **mathlib4太大**（1GB+），不适合submodule
2. **其他仓库较小**，适合作为submodule
3. **便于同步**，在其他电脑快速设置

### 如何实现？

```bash
# 1. 添加核心submodule（已准备好脚本）
./setup_core_submodules.sh

# 2. mathlib4信息记录在 LEAN4_REPOSITORIES.md
# 包含克隆命令、说明等

# 3. 提交到Git
git add .
git commit -m "chore: Setup Lean4 dependency management"
git push
```

### 在其他电脑使用

```bash
# 克隆主项目
git clone --recursive git@github.com:leemiracle/lean4ai.git

# 查看mathlib4克隆说明
cat LEAN4_REPOSITORIES.md

# 按需克隆mathlib4
cd ~/lean4-projects
git clone https://github.com/leanprover-community/mathlib4.git
```

---

## 📋 各仓库详情

### ✅ 作为Submodule（推荐）

| 仓库 | 大小 | 用途 | 频率 |
|------|------|------|------|
| batteries | ~50MB | 扩展标准库 | 高 |
| quote4 | ~10MB | 元编程 | 高 |
| repl | ~5MB | 交互式环境 | 高 |
| ProofWidgets4 | ~20MB | 可视化 | 高 |
| aesop | ~20MB | 自动化 | 高 |
| duper | ~20MB | 自动证明 | 中 |
| LeanProject | ~5MB | 项目模板 | 中 |

### 📝 记录信息（不作为Submodule）

| 仓库 | 大小 | 用途 | 说明 |
|------|------|------|------|
| mathlib4 | ~1GB+ | 数学库 | 太大，单独管理 |

---

## 🚀 立即执行

我已经准备好了所有脚本，你只需要运行：

```bash
# 方案A：混合管理（推荐）
./setup_core_submodules.sh
```

这会：
1. ✅ 添加6个核心仓库为submodule
2. ✅ 记录mathlib4信息
3. ✅ 更新.gitignore
4. ✅ 准备提交

---

## ❓ 常见问题

### Q: 为什么不把mathlib4作为submodule？
A: 太大（1GB+），克隆慢，且更新频繁。单独管理更灵活。

### Q: 其他电脑怎么获取完整环境？
A:
```bash
git clone --recursive git@github.com:leemiracle/lean4ai.git
# 然后按需克隆mathlib4
```

### Q: 如何更新submodule？
A:
```bash
git submodule update --remote
# 或
git submodule foreach git pull origin master
```

### Q: 如何临时克隆mathlib4？
A:
```bash
# 查看说明
cat LEAN4_REPOSITORIES.md
# 按说明克隆
git clone https://github.com/leanprover-community/mathlib4.git
```

---

## 📞 需要帮助？

- **问题1**: 执行 `./setup_core_submodules.sh`
- **问题2**: 查看此文件
- **问题3**: 查看项目Issues

---

*最后更新：2025-03*
