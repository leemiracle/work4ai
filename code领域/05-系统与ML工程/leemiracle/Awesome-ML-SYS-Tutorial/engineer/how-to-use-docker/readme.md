## 1. 什么是 Docker？为什么要用 Docker

Docker 是一个软件。它能把环境打包成**镜像(image)**。使用者在**容器(container)**内运行镜像就有了一模一样的环境，无需手动配环境。

- 使用 pytorch 官方镜像，跑深度学习代码再也不用担心 python, CUDA, cuDNN 的版本兼容问题。


## 2. 安装 docker

请注意，sglang 的开发环境是 linux 系统

- 通常来讲，服务器管理员会预先安装 docker 软件，无需手动安装。你并不需要 sudo 权限来装软件


- 服务器上找不到 docker，可能使用 nerdctl 作为替代。nerdctl 完全兼容 docker 的命令。把指令替换成 nerdctl xxx 即可。
- 如果确实需要手动安装，可参考 [Install | Docker Docs](https://docs.docker.com/engine/install/) 或询问 G 老师

## 3. 下载 docker 镜像

绝大多数 docker 镜像被发布在 [Docker Hub ](https://hub.docker.com/)

请使用 sglang 官方镜像 [lmsysorg/sglang Tags | Docker Hub](https://hub.docker.com/r/lmsysorg/sglang/tags) 

```
# 下载镜像
# docker pull <image-name>
docker pull lmsysorg/sglang:latest
```

## 4. 在容器内运行 docker 镜像

下载的**镜像**相当于压缩包，我们要把镜像解压到**容器**运行。而**宿主机(host)**就是我们的服务器

运行容器的指令格式是：

```
docker run [OPTIONS] IMAGE [COMMAND]
```

- OPTIONS: 运行容器时附加的参数
- IMAGE: 镜像名
- COMMAND: 容器启动时运行什么指令
- notice: 镜像名 IMAGE 的位置必须在 OPTIONS 后面，在 COMMAND 前面

### 4.1 常用 OPTIONS（必读）

- `-it` 交互式终端
  - 有该参数你才能在 docker 里用交互式终端

- `--name <container-name>` 容器名
  - 有该参数才能识别出这个 docker 是谁的。
  - 命名规则请参考服务器准则，否则会被管理员认为是垃圾容器删除掉。

- `--shm-size <shared-memory-size>` 共享内存大小
  - 深度学习框架需要较大的内存，默认的 64MB 会导致崩溃，建议设置为 16g 及以上

- `--gpus all`  允许容器 access 哪些 gpu
  - 如无特殊需求，设置成 all 即可

- `-v <host-path>:<container-path>` 目录挂载

  将宿主机目录 `<host-path>` 的全部内容挂载到容器目录 `<container-path>` 。宿主机和 docker 容器会共享目录下所有的文件和文件夹。容器对内容修改对宿主机可见，反之亦然。

  - 该参数可以多次添加，通常用于映射代码工作区，数据集，模型文件，配置文件等。
  - 可映射工作区目录到容器内，在容器内运行代码，在宿主机进行开发。
  - 添加 ` -v ~/.cache/huggingface:/root/.cache/huggingface ` 映射宿主机的 Huggingface cache 到容器，容器可以复用宿主机的模型缓存，无需再次下载
  - linux 下 `pwd` 指令会输出当前目录路径。`-v` 配合 `$(pwd)` 来添加当前目录作为前缀（即运行 `docker run` 指令时的目录）。

组合起来是：

```
docker run -it --name <container-name> --shm-size 16g --gpus all -v <host-path>:<container-path> IMAGE
```

### 4.2 可选 OPTIONS

- `-p <host-port>:<container-port>` 端口映射
  - 将容器端口 `<container-port>` 映射到宿主机端口 `<host-port>` 。使得外部可以通过宿主机端口来访问容器内运行的服务。
  - 可多次添加。

- `--network host` 网络共享
  - 使容器直接使用宿主机的网络。共享 ip，端口，网络资源等。
  - 部分服务器在国内，添加 `--network host` 以共享网络代理。
  - 使用 `--network host` 时，`-p` 参数会被忽略。

- `-e <cv-name>=<cv-value>` 环境变量
  - 设置容器内环境变量`<cv-name>` 的值为 `<cv-value>` 。
  - 可多次添加。

- `--ipc=host` 进程间通信的命名空间共享
  - 可替代 `--shm-size` 

- `-d` 在后台运行容器，输入 exit 时容器不关闭
- `--rm` 容器关闭后自动删除

### 4.3 IMAGE

- 使用者：`docker pull lmsysorg/sglang:latest`
- 开发者：`docker pull lmsysorg/sglang:dev`
- 部分开发 issue 需要不同的镜像，请联系 issue 持有者

### 4.4 COMMAND

我们可以指定容器 run 或 restart 时执行的指令

一些常见 case：

- 在容器内启动会话。容器像一台虚拟机，可以输入指令，管理文件等。

```
docker run -it [other OPTIONS] <image-name> bash
```

- 在容器内启动 sglang server 服务（运行在容器的 30000 端口上），并映射到宿主机的 30000 端口，以供外部访问。
- 定义环境变量 HF_TOKEN 来指定模型名

```
docker run -p 30000:30000 --env "HF_TOKEN=hf_xxx"[other OPTIONS] <image-name> python3 -m sglang.launch_server [other paras]
```

## 5. 容器管理

### 5.1 查看容器

- `docker ps` 查看正在运行的容器
- `docker ps -a` 查看所有容器

### 5.2 关闭容器

退出会话，并关闭容器：

- 输入指令 `exit` 
- 或按下快捷键 Ctrl + D

退出会话，并保持容器在后台运行：

- 按下 Ctrl + P, 再 Ctrl + Q。在部分 ide 中会因为快捷键占用失效
- 或在 docker run 时添加参数 `-d`， `exit` 后不会关闭容器
- 或直接关闭当前终端

关闭容器：

- `docker stop <container-name>`

notice: COMMAND 运行完毕后容器会自动关闭。

### 5.3 重启容器

- `docker restart <container-name>`

### 5.4 附加容器

需要容器启动才能附加

- `docker exec -it <container-name> bash` 在容器启动交互式会话
- exec 的本质是在容器内执行命令，也可以用来修改环境变量。

### 5.5 删除容器

需要先停止容器：

- `docker rm <container-name>`
- 或在 docker run 时添加 `--rm`， 容器关闭后会被自动删除

## 6. 镜像构建

TODO

## 7. 镜像上传

TODO





