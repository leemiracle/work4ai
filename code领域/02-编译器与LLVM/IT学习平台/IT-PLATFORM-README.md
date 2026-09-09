# IT Learning & Project Management Platform

一个综合性的IT学习与项目管理平台，整合知识库、学习管理、项目管理和协作功能。

## 项目特性

### 核心功能

- **知识库管理** - Markdown笔记、文档分类、知识图谱、全文搜索
- **学习管理** - 课程管理、技能树、学习进度跟踪、学习计划制定
- **项目管理** - 项目创建、任务分配、里程碑管理、团队协作
- **多端支持** - Web应用、CLI工具、桌面应用

### 技术亮点

- 模块化架构，易于扩展
- 统一API，支持多种客户端
- 轻量级部署，本地优先
- 类型安全，自动文档生成

## 快速开始

### 安装依赖

#### 后端
```bash
cd backend
pip install -r requirements.txt
```

#### 前端
```bash
cd frontend
npm install
```

#### CLI工具
```bash
cd cli
pip install -r requirements.txt
```

### 运行项目

#### 后端服务
```bash
cd backend
python main.py
```

服务将在 `http://localhost:8000` 启动

API文档: `http://localhost:8000/docs`

#### 前端应用
```bash
cd frontend
npm run dev
```

应用将在 `http://localhost:3000` 启动

#### CLI工具
```bash
cd cli
python main.py --help
```

## 项目结构

```
it-learning-platform/
├── backend/           # 后端服务 (FastAPI)
├── frontend/          # Web前端 (React + TypeScript)
├── cli/               # CLI工具 (Python + Click)
├── desktop/           # 桌面应用 (Electron)
├── knowledge-base/    # 知识库内容
├── data/              # 数据存储
├── docs/              # 文档
└── tests/             # 测试
```

详细架构请参考 [ARCHITECTURE.md](./ARCHITECTURE.md)

## 功能模块

### 知识库模块

- 创建和管理Markdown笔记
- 标签和分类系统
- 笔记之间的关联和引用
- 全文搜索功能

### 学习管理模块

- 创建和管理课程
- 技能树可视化
- 学习进度跟踪
- 学习计划制定和执行

### 项目管理模块

- 项目创建和管理
- 任务分配和跟踪
- 里程碑管理
- 团队协作和沟通

## 开发指南

### 代码规范

- 后端: Python PEP 8
- 前端: ESLint + Prettier
- Git: Conventional Commits

### 测试

```bash
# 运行所有测试
pytest

# 运行单元测试
pytest tests/unit

# 运行集成测试
pytest tests/integration
```

### 文档

- API文档自动生成: `/docs`
- 项目架构: [ARCHITECTURE.md](./ARCHITECTURE.md)
- 计划方法论: [docs/planning-methodology.md](./docs/planning-methodology.md)

## 部署

### Docker部署

```bash
docker-compose up -d
```

### 手动部署

详见 [部署指南](./docs/deployment.md)

## 贡献指南

欢迎贡献！请查看 [CONTRIBUTING.md](./CONTRIBUTING.md)

## 许可证

Apache License 2.0

## 联系方式

- Issues: [GitHub Issues](https://github.com/llvm/llvm-project/issues)
- Discussions: [Discourse](https://discourse.llvm.org/)

---

**状态**: 开发中
**版本**: 0.1.0
