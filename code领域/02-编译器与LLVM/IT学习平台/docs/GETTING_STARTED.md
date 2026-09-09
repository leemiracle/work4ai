# 快速开始指南

## 项目概述

这是一个综合性的IT学习与项目管理平台，整合了知识库、学习管理、项目管理和协作功能。

## 环境要求

- Python 3.9+
- Node.js 16+
- npm 或 yarn

## 安装步骤

### 1. 克隆项目

```bash
git clone <repository-url>
cd it-learning-platform
```

### 2. 安装后端依赖

```bash
cd backend
pip install -r requirements.txt
```

### 3. 安装CLI依赖

```bash
cd ../cli
pip install -r requirements.txt
```

### 4. 安装前端依赖

```bash
cd ../frontend
npm install
```

## 运行项目

### 启动后端服务

```bash
cd backend
python main.py
```

后端服务将在 `http://localhost:8000` 启动

访问 API 文档: `http://localhost:8000/docs`

### 启动前端应用

```bash
cd frontend
npm start
```

前端应用将在 `http://localhost:3000` 启动

### 使用CLI工具

```bash
cd cli
python main.py init           # 初始化数据库
python main.py status         # 查看平台状态
python main.py notes list     # 列出所有笔记
python main.py projects list  # 列出所有项目
```

## 功能模块

### 知识库

- 创建和管理Markdown笔记
- 标签和分类系统
- 笔记之间的关联和引用
- 全文搜索功能

### 学习管理

- 课程管理
- 技能树可视化
- 学习进度跟踪
- 学习计划制定

### 项目管理

- 项目创建和管理
- 任务分配和跟踪
- 里程碑管理
- 时间记录

## API 端点

### 知识库

```
POST   /api/v1/notes          - 创建笔记
GET    /api/v1/notes          - 获取笔记列表
GET    /api/v1/notes/{id}     - 获取笔记详情
PUT    /api/v1/notes/{id}     - 更新笔记
DELETE /api/v1/notes/{id}     - 删除笔记
```

### 学习管理

```
POST   /api/v1/learning/courses      - 创建课程
GET    /api/v1/learning/courses      - 获取课程列表
POST   /api/v1/learning/skills       - 创建技能
GET    /api/v1/learning/skills       - 获取技能列表
```

### 项目管理

```
POST   /api/v1/projects       - 创建项目
GET    /api/v1/projects       - 获取项目列表
POST   /api/v1/projects/tasks - 创建任务
GET    /api/v1/projects/tasks - 获取任务列表
```

## 开发指南

### 后端开发

- FastAPI 框架
- SQLAlchemy ORM
- Pydantic 数据验证

### 前端开发

- React + TypeScript
- Ant Design 组件库
- Redux Toolkit 状态管理

### 代码规范

- 后端: Black + MyPy
- 前端: ESLint + Prettier

## 测试

```bash
# 后端测试
cd backend
pytest

# 前端测试
cd frontend
npm test
```

## 部署

### Docker 部署

```bash
docker-compose up -d
```

### 手动部署

详见 [部署指南](./DEPLOYMENT.md)

## 常见问题

### 1. 后端启动失败

检查依赖是否正确安装：
```bash
cd backend
pip install -r requirements.txt
```

### 2. 前端无法连接后端

确保后端服务在 `http://localhost:8000` 运行

### 3. 数据库错误

运行初始化命令：
```bash
cd cli
python main.py init
```

## 下一步

- 查看 完整文档（`./ARCHITECTURE.md`）
- 阅读 [API 文档](http://localhost:8000/docs)
- 探索 [知识库](../knowledge-base/)
- 学习 [计划方法论](../docs/planning-methodology.md)

## 支持

- 提交 Issue: GitHub Issues
- 文档: docs/
- 示例: examples/

---

祝您学习愉快！
