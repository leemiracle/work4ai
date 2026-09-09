# veRL-multiturn-rollout Release

## 环境配置

### 创建新的 docker

```bash
docker run \
    -it \
    --shm-size 32g \
    --gpus all \
    -v /models/shared/.cache:/root/.cache \
    --ipc=host \
    --network=host \
    --privileged \
    --name sglang_{your-name} \
    lmsysorg/sglang:dev \
    /bin/zsh
```

以后每次从 docker 里面 `exit` 出来，再用这个指令可以重启：

```bash
docker start -i sglang_{your-name}
```

### 更新 python

```bash
apt update
apt install -y python3.10 python3.10-venv
python3 -m ensurepip --upgrade
```

### 使用虚拟环境

```bash
# 创建虚拟环境
python3 -m venv ~/.python/veRL-multiturn-rollout

# 激活虚拟环境
source ~/.python/veRL-multiturn-rollout/bin/activate

# 安装 uv
python3 -m pip install uv
```

### clone veRL main 代码

```bash
cd ~
git clone https://github.com/volcengine/verl.git
cd verl
```

### 配置 python 环境

```bash
# 安装 SGLang
python3 -m uv pip install -e ".[sglang]"

# 手动安装 flash-attn
python3 -m uv pip install wheel
python3 -m uv pip install packaging
python3 -m uv pip install flash-attn --no-build-isolation --no-deps

# 安装 veRL
python3 -m uv pip install .
python3 -m uv pip install -r ./requirements.txt
```

## 8 卡测试 SGLang

### 使用前需要配置好 `WANDB_API_KEY`

可以参考[这个过程](https://community.wandb.ai/t/where-can-i-find-the-api-token-for-my-project/7914)。

```bash
export WANDB_API_KEY={YOUR_WANDB_API_KEY}

# 定义这个时间戳函数
function now() {
    date '+%Y-%m-%d-%H-%M'
}
```

### 下载数据集

```bash
python3 ./examples/data_preprocess/gsm8k_multiturn_w_tool.py
```

### 运行

```bash
# First make sure the now() function is available in current shell
# Create logs directory if it doesn't exist
mkdir -p logs

# Set GPUs and run with better log organization
export CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7

nohup bash examples/sglang_multiturn/run_qwen2.5-3b_gsm8k_multiturn.sh trainer.experiment_name=qwen2.5-3b_rm-gsm8k-sgl-multiturn-$(now) > logs/gsm8k-$(now).log 2>&1 &
```

