# veRL-multiturn-rollout Release

## Environment Setup

### Create a New Docker Container

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

To restart the container after exiting from it:

```bash
docker start -i sglang_{your-name}
```

### Update Python

```bash
apt update
apt install -y python3.10 python3.10-venv
python3 -m ensurepip --upgrade
```

### Use Python Virtual Environment

```bash
# Create a virtual environment
python3 -m venv ~/.python/veRL-multiturn-rollout

# Activate the virtual environment
source ~/.python/veRL-multiturn-rollout/bin/activate

# Install uv
python3 -m pip install uv
```

### Clone the veRL Main Repository

```bash
cd ~
git clone https://github.com/volcengine/verl.git
cd verl
```

### Set Up the Python Environment

```bash
# Install SGLang
python3 -m uv pip install -e ".[sglang]"

# Manually install flash-attn
python3 -m uv pip install wheel
python3 -m uv pip install packaging
python3 -m uv pip install flash-attn --no-build-isolation --no-deps

# Install veRL
python3 -m uv pip install .
python3 -m uv pip install -r ./requirements.txt
```

## 8-GPU SGLang Test

### Set Up Your `WANDB_API_KEY` Before Running

Refer to [this guide](https://community.wandb.ai/t/where-can-i-find-the-api-token-for-my-project/7914) if you're not sure where to find your API token.

```bash
export WANDB_API_KEY={YOUR_WANDB_API_KEY}

# Define a timestamp function
function now() {
    date '+%Y-%m-%d-%H-%M'
}
```

### Download the Dataset

```bash
python3 ./examples/data_preprocess/gsm8k_multiturn_w_tool.py
```

### Run

```bash
# First make sure the now() function is available in current shell
# Create logs directory if it doesn't exist
mkdir -p logs

# Set GPUs and run with better log organization
export CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7

nohup bash examples/sglang_multiturn/run_qwen2.5-3b_gsm8k_multiturn.sh trainer.experiment_name=qwen2.5-3b_rm-gsm8k-sgl-multiturn-$(now) > logs/gsm8k-$(now).log 2>&1 &
```

