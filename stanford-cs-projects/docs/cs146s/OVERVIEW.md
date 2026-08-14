# CS146S: The Modern Software Developer

> Stanford University, Autumn 2026
> 领域: 软件工程实践 / DevOps
> Prerequisites: CS106B 或同等编程经验
> Units: 1-2
> Difficulty: ⭐⭐

---

## 📚 定位

从"能写代码"到"能交付软件"——掌握现代开发工作流：Git、CI/CD、容器化、云部署。

---

## 🎯 学习目标

- 理解现代软件开发生命周期（SDLC）
- 掌握 Git 工作流与代码评审
- 能配置 CI/CD 管道
- 理解容器化（Docker）与编排（K8s）

---

## 📅 核心模块

### Module 1: 版本控制
- Git 核心概念（commit / branch / merge）
- 分支策略（Git Flow / Trunk-based）
- Pull Request 与代码评审
- 解决合并冲突

### Module 2: 测试与质量
- 单元测试 / 集成测试 / E2E
- 测试覆盖率与 TDD
- 静态分析（Lint / Type Check）
- 代码质量指标

### Module 3: CI/CD
- 持续集成理念
- GitHub Actions / GitLab CI
- 管道设计：Lint → Test → Build → Deploy
- 蓝绿部署 / 金丝雀发布

### Module 4: 容器化
- Docker 基础（镜像 / 容器 / Dockerfile）
- 容器编排：Kubernetes 基础
- 微服务架构
- 服务网格

### Module 5: 云与可观测性
- 云服务模型（IaaS / PaaS / SaaS）
- 日志 / 指标 / 追踪
- 监控与告警
- 事件响应

---

## 💻 项目代码

📁 `supplementary/undergrad_projects.py::cs146s_demo`

**实现内容**:
1. ✅ 5 阶段 CI/CD 管道模拟
2. ✅ Lint → Test → Build → Scan → Deploy
3. ✅ 管道失败处理与工具链展示

**运行**:
```bash
cd supplementary
python3 undergrad_projects.py
```

**输出示例**:
```
[Lint]   ruff check .       → ✅
[Test]   pytest tests/      → ✅
[Build]  docker build .     → ✅
[Scan]   trivy image app    → ✅
[Deploy] kubectl apply      → ❌ FAIL
⚠️ Pipeline halted
关键: Git / GitHub Actions / Docker / K8s / Trivy
```

---

## 📊 关键概念

| 概念 | 说明 |
|------|------|
| **CI/CD** | 持续集成 + 持续部署 |
| **Docker** | 容器化，环境一致性 |
| **Kubernetes** | 容器编排，自动扩缩容 |
| **代码评审** | PR 是质量与知识的桥梁 |
| **可观测性** | 日志 + 指标 + 追踪三支柱 |

---

## 🎯 适用人群

| 角色 | 推荐 |
|------|------|
| **即将实习/工作** | 工程实践必备 |
| **CS106B 后实践** | 从课堂到工业的桥梁 |
| **DevOps 方向** | 入门基础 |
| **创业者** | 自己搭建基础设施 |

---

## 🚀 扩展方向

1. 阅读 *The Phoenix Project*（DevOps 小说）
2. 阅读 *Accelerate*（DORA 指标研究）
3. 实战：为自己的项目配置完整 CI/CD
4. 进阶：CS309A（云计算）

---

**对应代码**: `supplementary/undergrad_projects.py::cs146s_demo`
