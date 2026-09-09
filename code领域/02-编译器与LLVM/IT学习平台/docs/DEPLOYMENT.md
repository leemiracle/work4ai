# 部署指南

本指南介绍如何在不同环境中部署IT学习与项目管理平台。

## 目录

- [开发环境部署](#开发环境部署)
- [生产环境部署](#生产环境部署)
- [Docker部署](#docker部署)
- [云平台部署](#云平台部署)
- [故障排查](#故障排查)

---

## 开发环境部署

### 前置要求

- Python 3.9+
- Node.js 16+
- Git

### 步骤

#### 1. 克隆仓库

```bash
git clone <repository-url>
cd it-learning-platform
```

#### 2. 后端设置

```bash
cd backend

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 配置环境变量（可选）
export DATABASE_URL="sqlite:///./data/database.db"
export SECRET_KEY="your-secret-key-here"

# 初始化数据库
python -c "from core.database import init_db; init_db()"

# 启动后端
python main.py
```

后端将在 `http://localhost:8000` 启动

#### 3. 前端设置

```bash
cd frontend

# 安装依赖
npm install

# 配置API地址（可选）
echo "REACT_APP_API_URL=http://localhost:8000/api/v1" > .env

# 启动开发服务器
npm start
```

前端将在 `http://localhost:3000` 启动

#### 4. CLI工具（可选）

```bash
cd cli

# 安装依赖
pip install -r requirements.txt

# 测试CLI
python main.py --help
```

---

## 生产环境部署

### 系统要求

- Ubuntu 20.04+ / CentOS 8+ / macOS
- Python 3.9+
- Node.js 16+
- Nginx
- PostgreSQL (推荐) 或 SQLite

### 步骤

#### 1. 系统准备

```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装Python和Node.js
sudo apt install python3 python3-pip nodejs npm -y

# 安装Nginx
sudo apt install nginx -y

# 安装PostgreSQL (可选)
sudo apt install postgresql postgresql-contrib -y
```

#### 2. 后端部署

```bash
# 克隆代码
git clone <repository-url> /opt/it-learning-platform
cd /opt/it-learning-platform/backend

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 配置生产环境变量
cat > .env << EOF
DEBUG=false
DATABASE_URL=postgresql://user:password@localhost/itlearning
SECRET_KEY=your-production-secret-key
CORS_ORIGINS=["https://your-domain.com"]
EOF

# 初始化数据库
python -c "from core.database import init_db; init_db()"

# 创建systemd服务
sudo tee /etc/systemd/system/it-learning-backend.service > /dev/null << EOF
[Unit]
Description=IT Learning Platform Backend
After=network.target

[Service]
User=www-data
WorkingDirectory=/opt/it-learning-platform/backend
Environment="PATH=/opt/it-learning-platform/backend/venv/bin"
ExecStart=/opt/it-learning-platform/backend/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# 启动服务
sudo systemctl daemon-reload
sudo systemctl enable it-learning-backend
sudo systemctl start it-learning-backend
```

#### 3. 前端部署

```bash
cd /opt/it-learning-platform/frontend

# 安装依赖
npm install

# 构建生产版本
npm run build

# 配置Nginx
sudo tee /etc/nginx/sites-available/it-learning-platform > /dev/null << EOF
server {
    listen 80;
    server_name your-domain.com;

    location / {
        root /opt/it-learning-platform/frontend/build;
        try_files $uri /index.html;
    }

    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    location /docs {
        proxy_pass http://localhost:8000;
    }
}
EOF

# 启用站点
sudo ln -s /etc/nginx/sites-available/it-learning-platform /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

#### 4. SSL配置（Let's Encrypt）

```bash
# 安装certbot
sudo apt install certbot python3-certbot-nginx -y

# 获取SSL证书
sudo certbot --nginx -d your-domain.com

# 自动续期
sudo certbot renew --dry-run
```

---

## Docker部署

### Docker Compose部署

#### 1. 创建docker-compose.yml

```yaml
version: '3.8'

services:
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://postgres:password@db:5432/itlearning
      - SECRET_KEY=your-secret-key
    depends_on:
      - db
    volumes:
      - ./data:/app/data

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "80:80"
    depends_on:
      - backend

  db:
    image: postgres:14
    environment:
      - POSTGRES_DB=itlearning
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

volumes:
  postgres_data:
```

#### 2. 创建后端Dockerfile

```dockerfile
# backend/Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### 3. 创建前端Dockerfile

```dockerfile
# frontend/Dockerfile
FROM node:18-alpine as build

WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/build /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

#### 4. 部署

```bash
# 构建和启动
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

---

## 云平台部署

### AWS部署

#### 1. EC2实例

- 选择Ubuntu 20.04 LTS
- 实例类型: t3.medium (推荐)
- 配置安全组: 开放80, 443, 22端口

#### 2. RDS数据库

- 创建PostgreSQL实例
- 配置VPC和子网
- 获取连接字符串

#### 3. Elastic Beanstalk（可选）

```bash
# 安装EB CLI
pip install awsebcli

# 初始化应用
eb init it-learning-platform

# 部署
eb create production-env
```

### Google Cloud Platform

#### 1. Cloud Run

```bash
# 构建并推送镜像
gcloud builds submit --tag gcr.io/PROJECT_ID/backend

# 部署
gcloud run deploy backend --image gcr.io/PROJECT_ID/backend --platform managed
```

#### 2. Cloud SQL

- 创建PostgreSQL实例
- 配置连接
- 使用Cloud SQL Proxy

### Azure

#### 1. Azure App Service

```bash
# 创建资源组
az group create --name it-learning-rg --location eastus

# 创建App Service
az webapp up --name it-learning-app --resource-group it-learning-rg
```

---

## 监控和日志

### 应用监控

```bash
# 查看应用日志
sudo journalctl -u it-learning-backend -f

# Nginx日志
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

### 性能监控

- 使用Prometheus + Grafana
- 集成APM工具（New Relic, Datadog）
- 监控关键指标：响应时间、错误率、资源使用

---

## 备份策略

### 数据库备份

```bash
# PostgreSQL备份
pg_dump -U postgres -d itlearning > backup_$(date +%Y%m%d).sql

# 自动备份脚本（cron）
0 2 * * * pg_dump -U postgres -d itlearning > /backups/db_$(date +\%Y\%m\%d).sql
```

### 文件备份

```bash
# 备份上传的文件
tar -czf data_backup_$(date +%Y%m%d).tar.gz ./data
```

---

## 故障排查

### 常见问题

#### 1. 后端无法启动

```bash
# 检查端口占用
sudo lsof -i :8000

# 检查日志
sudo journalctl -u it-learning-backend

# 检查数据库连接
psql -U postgres -d itlearning
```

#### 2. 前端无法连接后端

```bash
# 检查后端状态
curl http://localhost:8000/health

# 检查CORS配置
# 查看后端CORS_ORIGINS设置

# 检查Nginx配置
sudo nginx -t
```

#### 3. 数据库连接失败

```bash
# 检查PostgreSQL状态
sudo systemctl status postgresql

# 检查连接字符串
echo $DATABASE_URL

# 测试连接
psql -U postgres -d itlearning
```

#### 4. 权限问题

```bash
# 检查文件权限
ls -la /opt/it-learning-platform

# 修复权限
sudo chown -R www-data:www-data /opt/it-learning-platform
```

### 日志分析

```bash
# 查看错误日志
sudo grep "ERROR" /var/log/nginx/error.log | tail -20

# 查看应用错误
sudo journalctl -u it-learning-backend | grep -i error
```

---

## 性能优化

### 后端优化

1. 使用Gunicorn或Uvicorn Workers
2. 启用数据库连接池
3. 配置缓存（Redis）
4. 使用CDN加速静态资源

### 前端优化

1. 启用Gzip压缩
2. 配置浏览器缓存
3. 使用CDN
4. 代码分割和懒加载

### 数据库优化

1. 创建适当的索引
2. 优化查询语句
3. 定期VACUUM和ANALYZE
4. 考虑读写分离

---

## 安全建议

1. **使用HTTPS**: 配置SSL证书
2. **定期更新**: 保持系统和依赖最新
3. **防火墙**: 限制不必要的端口访问
4. **认证**: 实现强认证机制
5. **备份**: 定期备份并测试恢复
6. **监控**: 设置异常告警

---

## 扩展部署

### 水平扩展

1. 使用负载均衡器
2. 部署多个应用实例
3. 使用共享数据库
4. 配置会话存储（Redis）

### 垂直扩展

1. 增加服务器资源
2. 优化数据库性能
3. 使用缓存层

---

**最后更新**: 2026-02-13
