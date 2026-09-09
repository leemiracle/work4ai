# Lean4 项目详细分析

## 一、GitHub 热门项目排名（2025）

### 🔥 Top 10 核心项目

| 排名 | 项目 | Stars | 描述 | 分类 |
|------|------|-------|------|------|
| 1 | leanprover/lean4 | 7.6k | Lean 4 语言核心 | 编译器 |
| 2 | leanprover-community/mathlib4 | 3.1k | 数学标准库 | 数学库 |
| 3 | lean-dojo/LeanCopilot | 1.3k | AI 证明助手 | AI/ML |
| 4 | AeneasVerif/aeneas | 656 | Rust 验证工具 | 验证 |
| 5 | leanprover/cslib | 452 | 计算机科学库 | CS |
| 6 | leanprover-community/batteries | 369 | 扩展标准库 | 工具 |
| 7 | lean-dojo/LeanDojo | 784 | Lean 交互工具 | ML |
| 8 | Julian/lean.nvim | 496 | Neovim 支持 | 编辑器 |
| 9 | leanprover-community/physlib | 525 | 物理库 | 物理 |
| 10 | Crispher/MathlibExplorer | 614 | 可视化工具 | 工具 |

### 📊 按语言分类

```
Lean 项目总计: 512 个
├── 纯 Lean: 244 个 (47.7%)
├── Python: 35 个 (6.8%)
├── JavaScript: 24 个 (4.7%)
├── TypeScript: 10 个 (2.0%)
├── Shell: 16 个 (3.1%)
└── 其他: 183 个 (35.7%)
```

---

## 二、项目分类详解

### 1️⃣ 数学形式化项目

#### mathlib4 - 数学标准库
- **Stars**: 3.1k
- **贡献者**: 300+
- **代码行数**: 1M+
- **内容**: 代数、分析、拓扑、概率、CS
- **文档**: https://leanprover-community.github.io/mathlib4_docs

**主要模块**:
```
Mathlib/
├── Algebra/          # 代数结构
│   ├── Group/       # 群论
│   ├── Ring/        # 环论
│   └── Field/       # 域论
├── Analysis/         # 分析
│   ├── Special/     # 特殊函数
│   └── Calculus/    # 微积分
├── Topology/         # 拓扑
├── Probability/      # 概率
└── NumberTheory/     # 数论
```

#### FLT - 费马大定理
- **组织**: ImperialCollegeLondon
- **领导者**: Kevin Buzzard
- **目标**: 完整形式化 Wiles 证明
- **意义**: 展示 Lean 处理前沿数学的能力

#### PhysLean - 物理库
- **Stars**: 525
- **目标**: 物理定理数字化
- **内容**: 力学、电磁学、量子

### 2️⃣ 验证与安全项目

#### Cedar (AWS)
- **用途**: AWS 授权策略验证
- **特点**: 零运行时开销
- **验证**: 差分测试 + 形式证明
- **应用**: Amazon Verified Permissions

#### Aeneas - Rust 验证
- **Stars**: 656
- **创新**: 利用 Rust 类型系统消除内存推理
- **输出**: Lean/F*/Coq 证明
- **应用**: 安全关键系统

#### zkLean - 零知识证明
- **类型**: DSL
- **应用**: 区块链、密码学
- **特点**: 可验证的 ZK 电路

### 3️⃣ AI/ML 集成项目

#### LeanCopilot
- **Stars**: 1.3k
- **功能**: LLM 辅助定理证明
- **模型**: 支持多种 LLM
- **集成**: 直接在 Lean 中使用

**使用示例**:
```lean
import LeanCopilot

-- 让 AI 建议证明步骤
example (n : Nat) : n + 0 = n := by
  suggest_tactics  -- AI 建议战术
```

#### LeanDojo
- **Stars**: 784
- **功能**: Lean 与 ML 的接口
- **提取**: 定理、证明数据
- **交互**: 编程式控制 Lean

#### AlphaProof (DeepMind)
- **技术**: RL + 形式化数学
- **成就**: IMO 级别证明
- **架构**: Lean + 深度学习

### 4️⃣ 开发工具

#### Loogle - 引理搜索
- **URL**: https://loogle.lean-lang.org
- **功能**: 按类型搜索引理
- **用法**: `Nat → Nat → Prop`

#### PaperProof - 可视化
- **类型**: VS Code 扩展
- **效果**: 纸笔风格证明界面
- **特点**: 直观显示证明结构

#### lean.nvim
- **Stars**: 496
- **功能**: Neovim 支持
- **特性**: Tree-sitter 高亮

### 5️⃣ 教育资源

#### NNG4 - 自然数游戏
- **URL**: https://adam.math.hhu.de/#/g/leanprover-community/NNG4
- **类型**: 互动游戏
- **目标**: 零基础入门

#### Mathematics in Lean
- **URL**: https://leanprover-community.github.io/mathematics_in_lean/
- **内容**: 实战数学形式化
- **级别**: 进阶

#### TPIL - 定理证明
- **URL**: https://lean-lang.org/theorem_proving_in_lean4/
- **内容**: 依赖类型理论
- **级别**: 基础

---

## 三、学习路径推荐

### 🎯 初学者路径（4周）

```
Week 1: 基础
├── Day 1-2: 安装环境
├── Day 3-5: NNG4 游戏
└── Day 6-7: TPIL 第1-3章

Week 2: 进阶
├── TPIL 第4-6章
├── 基础战术
└── 简单证明练习

Week 3: 实践
├── Mathematics in Lean
├── mathlib 探索
└── 小项目尝试

Week 4: 深入
├── 特定领域选择
├── 社区参与
└── 贡献准备
```

### 📚 资源清单

#### 官方文档
| 资源 | 链接 | 用途 |
|------|------|------|
| 语言参考 | lean-lang.org/doc/reference | API 查询 |
| Mathlib 文档 | leanprover-community.github.io/mathlib4_docs | 库文档 |
| FPIL | lean-lang.org/functional_programming_in_lean | 函数式编程 |

#### 社区资源
| 平台 | 链接 | 活跃度 |
|------|------|--------|
| Zulip | leanprover.zulipchat.com | ⭐⭐⭐⭐⭐ |
| GitHub | github.com/leanprover-community | ⭐⭐⭐⭐⭐ |
| YouTube | Lean Prover Community | ⭐⭐⭐ |

---

## 四、实际应用案例

### 🏢 工业应用

#### AWS Cedar
```
场景: 云服务授权验证
方法:
  1. Lean 形式化模型
  2. 安全性质证明
  3. Rust 实现
  4. 差分测试验证
成果:
  - 生产环境使用
  - 零运行时开销
  - 形式化保证
```

#### Aeneas (Rust)
```
场景: Rust 程序验证
创新:
  - 利用所有权系统
  - 消除内存推理
  - 生成形式证明
流程:
  Rust → Aeneas → Lean/F* 证明
```

### 🔬 研究项目

#### 费马大定理
```
目标: 完整形式化 350 年证明
进度:
  - 基础代数结构 ✓
  - 椭圆曲线理论 (进行中)
  - 模形式理论 (进行中)
意义: 证明 Lean 可处理前沿数学
```

#### AlphaProof
```
技术: RL + 形式化数学
架构:
  - Lean 证明环境
  - 神经网络策略
  - 搜索算法
成就: IMO 竞赛级别
```

---

## 五、工具链配置

### 本地环境

```bash
# 1. 安装 elan
curl https://raw.githubusercontent.com/leanprover/elan/master/elan-init.sh | sh

# 2. 创建项目
lake new my_project math

# 3. 配置 VS Code
# 安装扩展: leanprover.lean4

# 4. 构建项目
lake build
```

### 项目结构模板

```
my_project/
├── lakefile.toml      # 包配置
├── lean-toolchain     # 版本: leanprover/lean4:v4.28.0
├── MyProject/
│   ├── Basic.lean    # 基础定义
│   ├── Lemmas.lean   # 引理
│   └── Main.lean     # 主定理
├── MyProject.lean    # 库入口
└── README.md
```

### mathlib4 依赖

```toml
# lakefile.toml
[[require]]
name = "mathlib"
scope = "leanprover-community"
rev = "master"
```

```bash
# 下载缓存（加速构建）
lake exe cache get
```

---

## 六、常见任务

### 搜索引理
```bash
# 使用 Loogle
https://loogle.lean-lang.org

# 查询示例
Nat → Nat → Prop     # 函数类型
List ?a → List ?a    # 多态
```

### 调试证明
```lean
-- 显示目标
#check my_theorem

-- 逐步证明
example : True ∧ False := by
  constructor
  · trivial        -- 第一子目标
  · contradiction  -- 第二子目标

-- 使用 suggest
example (n : Nat) : n + 0 = n := by
  suggest
```

### 代码风格
```lean
-- 命名规范
theorem add_comm (a b : Nat) : a + b = b + a := ...

-- 文档注释
/-- 添加两个自然数 -/
def add (a b : Nat) : Nat := a + b

-- 结构化证明
theorem my_theorem :
    P → Q → R := by
  intro hP hQ
  have h1 : ... := ...
  have h2 : ... := ...
  exact ...
```

---

## 七、社区参与

### 贡献流程

```
1. Fork mathlib4
2. 创建分支
3. 编写代码
4. 运行测试: lake test
5. 提交 PR
6. 等待审核
```

### 获取帮助

| 方式 | 响应时间 |
|------|----------|
| Zulip 实时聊天 | < 1小时 |
| GitHub Issues | 1-3天 |
| Stack Exchange | 1-7天 |

---

## 八、下一步行动

### ✅ 立即开始
1. [ ] 完成 NNG4 教程
2. [ ] 阅读 TPIL 前3章
3. [ ] 加入 Zulip 社区
4. [ ] 克隆 mathlib4 并探索

### 📈 进阶目标
1. [ ] 完成 MIL 教程
2. [ ] 贡献第一个 PR
3. [ ] 选择专业方向
4. [ ] 参与社区讨论

### 🎯 长期目标
1. [ ] 形式化一个定理
2. [ ] 开发工具/战术
3. [ ] 参与大型项目
4. [ ] 教授他人

---

**资源汇总**:
- 官网: https://lean-lang.org
- 包仓库: https://reservoir.lean-lang.org
- 在线编辑器: https://live.lean-lang.org
- 社区: https://leanprover.zulipchat.com
