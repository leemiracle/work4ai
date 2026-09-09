# Docker · 场景速查

> 命令原文 + 一句话场景。容器起不来先看 logs，磁盘满了先 system prune。

## 🚨 最常用 5 条
```bash
docker ps                            # 看在跑的容器（-a 含已停止的）
docker images                        # 看本地有哪些镜像
docker run -it ubuntu:22.04 bash     # 起一个容器并进去开 shell
docker build -t myapp:1.0 .          # 用当前目录 Dockerfile 构建镜像
docker logs -f <容器名/ID>            # 实时看容器日志（排错第一步）
```

---

## 容器：起 / 停 / 进 / 拷贝
```bash
docker run -d --name web -p 8080:80 nginx        # 后台起 nginx，宿主 8080 映射到容器 80
docker run -it --rm alpine sh                    # 临时进 alpine，退出即删（--rm）
docker run -v $(pwd):/app -w /app node:18 npm install   # 把当前目录挂进去跑命令
docker run --gpus all pytorch/pytorch            # 容器里用 GPU（深度学习）
docker start <容器>                              # 启动已停止的容器
docker stop <容器>                               # 停止容器
docker restart <容器>                            # 重启
docker exec -it <容器> bash                      # 进入正在运行的容器开 bash
docker exec -it <容器> sh                        # 容器没装 bash（alpine）用 sh
docker cp <容器>:/path/file ./                   # 从容器里拷文件出来
docker cp ./file <容器>:/path/                   # 往容器里拷文件
docker rm <容器>                                 # 删除已停止的容器（-f 强删运行中的）
```

## 镜像：构建 / 清理
```bash
docker build -t myapp .                          # 当前目录 Dockerfile 构建
docker build -f Dockerfile.prod -t myapp:prod .  # 指定 Dockerfile 文件
docker build --no-cache -t myapp .               # 不用缓存（构建结果不对时强制全新）
docker pull nginx:1.25                           # 拉镜像
docker rmi nginx                                 # 删镜像
docker image prune -a                            # 删除所有未被容器使用的镜像（省磁盘）
docker tag myapp:latest myapp:v1.0               # 给镜像打标签
docker save myapp:1.0 -o myapp.tar               # 导出镜像成文件（离线传）
docker load -i myapp.tar                         # 从文件载入镜像
```

## 日志 / 资源排查（容器跑挂了先看这些）
```bash
docker logs <容器>                               # 看全部日志
docker logs -f --tail 100 <容器>                 # 实时跟踪最后 100 行
docker ps -a                                     # 看所有容器（含已退出的，看 STATUS）
docker inspect <容器>                            # 容器完整配置（IP、挂载、环境变量）
docker stats                                     # 实时看各容器 CPU/内存/网络
docker top <容器>                                # 看容器里的进程
docker events                                    # 实时看 docker 守护进程事件
# 常见退出码：0 正常 / 137 被OOM杀 / 139 段错误 / 1 程序报错
```

## 清理磁盘（Docker 占满磁盘救命）
```bash
docker system df                                # 看 docker 各类资源占多少空间
docker system prune -a --volumes                # 一键清：无容器镜像、停的容器、无用网络、无用卷（慎用）
docker container prune                          # 只删已停止的容器
docker image prune -a                           # 只删无用镜像
docker volume prune                             # 只删无用卷（数据会丢，确认后再删）
docker builder prune                            # 清构建缓存
```

## Volume：持久化数据
```bash
docker volume create mydata                      # 创建命名卷
docker run -v mydata:/data alpine                # 用命名卷（数据持久，删容器不丢）
docker run -v /home/me/data:/data alpine         # 绑定挂载宿主目录（改代码热生效）
docker volume ls                                 # 列出所有卷
docker volume inspect mydata                     # 看卷实际存在宿主哪个路径
docker run --tmpfs /tmp                          # 用内存做临时目录（快，重启即失）
```

## 网络
```bash
docker network ls                                # 列出网络
docker network create mynet                      # 创建自定义网络
docker run -d --name db --network mynet postgres # 容器加入网络后，容器间可用名字互访
# 同一网络里，容器 web 可直接 ping db（DNS 自动解析容器名）
docker run --network host nginx                  # 用宿主网络（无端口映射，性能好但无隔离）
docker run -p 127.0.0.1:5432:5432 postgres       # 只让本机访问，不对外暴露
```

## Dockerfile 最小模板
```dockerfile
# 单阶段：最简单的应用
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --production
COPY . .
EXPOSE 3000
CMD ["node", "server.js"]
```

## 多阶段构建（镜像瘦身：编译器和源码不进最终镜像）
```dockerfile
# 阶段1：编译
FROM golang:1.21 AS builder
WORKDIR /src
COPY . .
RUN CGO_ENABLED=0 go build -o app -ldflags="-s -w" .

# 阶段2：运行（最终镜像极小）
FROM alpine:latest
COPY --from=builder /src/app /app
ENTRYPOINT ["/app"]
```
```bash
docker build -t myapp .        # 只把最后 FROM 的层打包进最终镜像
```

## docker compose：多容器一键起
```yaml
# docker-compose.yml
services:
  web:
    build: .
    ports: ["8080:3000"]
    volumes: ["./src:/app/src"]
    depends_on: [db]
  db:
    image: postgres:16
    environment:
      POSTGRES_PASSWORD: secret
    volumes: ["dbdata:/var/lib/postgresql/data"]
volumes:
  dbdata:
```
```bash
docker compose up -d              # 后台起整套
docker compose up -d --build      # 重新构建镜像再起
docker compose logs -f web        # 跟踪某服务日志
docker compose down               # 停并删容器（-v 连卷一起删）
docker compose ps                 # 看这套服务状态
```

## 常见排坑
```bash
# 端口被占
docker run -p 8080:80 ...          # 报 bind: address already in use → 换个宿主端口或杀占用进程

# 容器一启动就退出
docker logs <容器>                  # 多半是程序报错 / CMD 写错 / 前台没顶住

# 构建缓存导致没更新代码
docker build --no-cache .          # COPY 的内容变了但缓存没失效，强制重建

# 想看完整构建过程
docker build --progress=plain .    # 不折叠输出，看每步到底干了啥

# permission denied（访问宿主文件）
docker run -u $(id -u):$(id -g) ...# 用宿主用户身份跑，避免 root 写出的文件改不动

# 进不了容器（没有 bash）
docker exec -it <容器> sh          # 精简镜像用 sh，再不行用 docker export 看文件
```
