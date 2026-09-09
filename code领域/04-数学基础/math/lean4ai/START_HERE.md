# Lean4 快速开始指南

## 环境状态

- [x] Lean 4.28.0
- [x] Lake 5.0.0
- [x] VS Code + Lean4 扩展
- [x] 代理配置 (172.22.208.1:7890)

## 学习路径

### 1. 在线游戏（推荐第一步）
- **Natural Number Game**: https://adam.math.hhu.de/#/g/leanprover-community/NNG4
- **Lean Game Server**: https://adam.math.hhu.de

### 2. 官方教程
- **Theorem Proving in Lean 4**: https://lean-lang.org/theorem_proving_in_lean4/
- **Mathematics in Lean**: https://leanprover-community.github.io/mathematics_in_lean/
- **Functional Programming in Lean**: https://lean-lang.org/functional_programming_in_lean/

### 3. 参考文档
- **Mathlib4 文档**: https://leanprover-community.github.io/mathlib4_docs
- **Lean 语言参考**: https://lean-lang.org/doc/reference

## 常用命令

```bash
# 创建新项目
lake new 项目名

# 构建项目
lake build

# 更新依赖
lake update

# 搜索引理（需安装 loogle）
loogle " Nat -> Nat -> Prop "

# 运行程序
./.lake/build/bin/项目名
```

## 项目结构

```
my_project/
├── lakefile.toml      # 包配置
├── lean-toolchain     # 版本锁定
├── MyProject/
│   └── Basic.lean    # 源代码
├── MyProject.lean    # 库入口
└── Main.lean         # 程序入口
```

## 热门项目

| 项目 | 用途 | 链接 |
|------|------|------|
| mathlib4 | 数学库 | github.com/leanprover-community/mathlib4 |
| Loogle | 引理搜索 | github.com/nomeata/loogle |
| PaperProof | 证明可视化 | github.com/Paper-Proof/paperproof |
| LeanCopilot | AI 辅助 | github.com/lean-dojo/LeanCopilot |

## 社区

- **Zulip**: https://leanprover.zulipchat.com
- **GitHub**: https://github.com/leanprover-community
- **YouTube**: Lean Prover Community

## 下一步

1. 完成自然数游戏（1-2天）
2. 阅读 TPIL 前 3 章
3. 克隆 mathlib4 并探索
4. 加入 Zulip 社区
