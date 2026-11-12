# =============================================================================
# 模块定位：Dockerfile —— KNighter 官方容器镜像（Docker Hub: knighterhub/knighter）
# 论文映射：论文 §5 实验环境（Ubuntu 20.04 工作站 64 核 + LLVM 18.1.8 + Linux 内核），
#           官方镜像选 Ubuntu 22.04 以获得更好的 LLVM 18 兼容性。
# 管线角色：镜像只装"系统依赖 + Python 依赖 + 仓库本体"；LLVM 与内核源码体积过大，
#           由容器内 python3 scripts/init_docker.py 首次启动时下载/编译——该脚本硬编码
#           落到 /app/llvm 与 /app/linux（init_docker.py:11-12，生成配置里 LLVM_dir/linux_dir
#           也是 /app/*）；docker-compose.yml 里的 /data/* 环境变量是另一套不生效的约定。
# =============================================================================
# 用 Ubuntu 22.04 基础镜像：与 LLVM 18.1.8 的兼容性更好
FROM ubuntu:22.04

# 环境变量：非交互安装 / Python 实时刷输出 / 不写 .pyc（容器内保持干净）
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# 系统依赖：编译工具链（LLVM/内核都要从源码编）+ 内核构建依赖（flex/bison/libelf/libssl...）
# + clang/llvm（系统版，主要提供基础工具）+ zsh/vim 等交互工具
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    git \
    python3 \
    python3-pip \
    python3-dev \
    wget \
    unzip \
    curl \
    ninja-build \
    clang \
    libclang-dev \
    llvm \
    llvm-dev \
    lld \
    libc6-dev \
    binutils \
    zlib1g-dev \
    libncurses5-dev \
    libxml2-dev \
    libedit-dev \
    libffi-dev \
    zsh \
    flex \
    libncurses-dev \
    bison \
    libssl-dev \
    libelf-dev \
    libdw-dev \
    dwarves \
    bc \
    vim \
    xz-utils \
    tar \
    cpio \
    && rm -rf /var/lib/apt/lists/*

# 装 Oh My Zsh 美化交互 shell（纯体验向，与管线无关）
RUN sh -c "$(curl -fsSL https://raw.github.com/ohmyzsh/ohmyzsh/master/tools/install.sh)" "" --unattended

# zsh 设为默认 shell
RUN chsh -s $(which zsh)

# 配置主题 bira + 常用插件（git/python/docker 补全等）
RUN sed -i 's/ZSH_THEME="robbyrussell"/ZSH_THEME="bira"/' ~/.zshrc \
    && sed -i 's/plugins=(git)/plugins=(git python pip docker docker-compose colored-man-pages command-not-found)/' ~/.zshrc

# 工作目录 /app（仓库代码的落点）
WORKDIR /app

# 先拷 requirements.txt 单独装 Python 依赖（利用 docker layer 缓存，改代码不重装依赖）
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# 拷贝项目本体
COPY . .

# 初始化 git submodule（tree-sitter-cpp 语法库）；兼容"从 zip 解压而非 git clone"的场景——
# 非 git 仓时直接 git clone tree-sitter-cpp 补齐（COMMON-ISSUES.md 记录了它的 scanner.c
# static_assert 编译坑，必要时注释掉那两行）
RUN if [ -d .git ]; then \
        git submodule update --init --recursive; \
    else \
        echo "Not a git repo, checking tree-sitter-cpp..."; \
        if [ ! -d "src/kparser/tree-sitter-cpp/.git" ]; then \
            echo "Setting up tree-sitter-cpp..."; \
            cd src/kparser && \
            rm -rf tree-sitter-cpp && \
            git clone https://github.com/tree-sitter/tree-sitter-cpp.git; \
        else \
            echo "tree-sitter-cpp already exists"; \
        fi; \
    fi

# 回到主工作目录
WORKDIR /app

# 默认命令：进 zsh 交互（实际任务用 docker-compose.yml 里 command 覆盖）
CMD ["/bin/zsh"]
