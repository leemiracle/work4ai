# veRL-SGLang Dev Release

## 问题背景

对于 veRL 而言，inference engine 需要支持 SPMD，具体的 motivation 可以参考此[链接](https://github.com/vllm-project/vllm/issues/11400)。SGLang 团队已经 merge 了相关 PR，可以参考[此处](https://github.com/sgl-project/sglang/commit/e3e0bc50a9d9644a183bc6dbb55919232196971d)。

这是  veRL 团队和 SGLang 团队开发的 dev release，旨在将 SGLang 接入 veRL 的训练流程中。会在近期完成合并，欢迎大家尝鲜、体验并且提供反馈。

## 环境配置

### 使用新的虚拟环境

```bash
python3 -m venv ~/.python/verl-sglang
source ~/.python/verl-sglang/bin/activate
python3 -m pip install --upgrade pip
python3 -m pip install --upgrade uv
```

### 安装 dev 分支的 veRL

```bash
cd ~
git clone https://github.com/volcengine/verl verl-sglang
cd verl-sglang
git pull --no-ff
python3 -m uv pip install .
```

### Install SGLang Main Branch From Github Source

这里需要从github安装最新的 SGLang main branch：

```bash
# Install latest SGlang from main branch
python3 -m uv pip install "sglang[all] @ git+https://github.com/sgl-project/sglang.git/@main#egg=sglang&subdirectory=python" --find-links https://flashinfer.ai/whl/cu124/torch2.5/flashinfer-python
```

按照上述流程，很有可能缺少 `flash-attn`，这里建议手动安装：

```bash
python3 -m uv pip install wheel
python3 -m uv pip install packaging
python3 -m uv pip install flash-attn --no-build-isolation --no-deps
```

这个过程可能出现若干问题，这里列出一些常见问题和解决方法：

1. **vllm dependency 冲突**

`ERROR: pip’s dependency resolver does not currently take into account all the packages that are installed. This behaviour is the source of the following dependency conflicts. verl 0.2 requires vllm<=0.6.3, but you have vllm 0.7.2 which is incompatible.`

实际上，verl-SGLang 发行版不需要 vllm 兼容，可以直接忽视。

2. **安装 flash_attn 时出现 CUDA ERROR**

如果出现 `CUDA ERROR`，尝试修改 `CUDA_HOME` 和 `LD_LIBRARY_PATH` 到本地的 cuda，我这里是 `12.1`。

```bash
export CUDA_HOME=/usr/local/cuda-12.1
```

3. `from torch._C import *` 报错，`undefined symbol:  __nvJitLinkComplete_12_4, version libnvJitLink.so.12`

这个太经典了，torch 各种 symbol 不匹配，我一般的解决方案如下：

```bash
# 查询自己的 python 路径
which python
# 输出为 /data/chayenne/.python/verl-sglang/bin/python
```

```bash
# 接着找到 nvjitlink 的路径，操作类似

ls /data/chayenne/.python/verl-sglang/lib64/python3.10/site-packages/nvidia/nvjitlink/lib/
```

```bash
# 把 nvjitlink 的路径添加到 LD_LIBRARY_PATH 中

export LD_LIBRARY_PATH=/data/chayenne/.python/verl-sglang/lib64/python3.10/site-packages/nvidia/nvjitlink/lib/:$LD_LIBRARY_PATH
```

成功安装后，可以检测下相关库的配置，仅做参考：

- sglang 0.4.3.post2 
- torch 2.5.1
- flashinfer_python 0.2.2.post1+cu124torch2.5
- verl 0.2.0.dev0
- ray 2.43.0
- flash-attn 2.7.4.post1  

<!-- ### 安装 megatron 作为 veRL 的 training engine

veRL 目前也支持使用 Megatron 作为 training engine，使用下面的命令安装 dev 版本的 megatron：

```bash
# 安装 Megatron-LM 到当前路径
git clone -b core_v0.4.0_verl https://github.com/eric-haibin-lin/Megatron-LM

# 将 Megatron-LM 添加到 PYTHONPATH
export PYTHONPATH=$PYTHONPATH:$(pwd)/Megatron-LM
```

需要配套安装 [Transformer Engine 1.7](https://github.com/NVIDIA/TransformerEngine)：

```bash
pip3 install git+https://github.com/NVIDIA/TransformerEngine.git@v1.7
```

安装时编译可能遇到一些问题：

1. **could not find cudnn**

```bash
CMake Error at /tmp/pip-req-build-s96o7cy6/3rdparty/cudnn-frontend/cmake/cuDNN.cmake:3 (find_path):
  Could not find CUDNN_INCLUDE_DIR using the following files: cudnn.h
Call Stack (most recent call first):
  CMakeLists.txt:33 (include)
```

[官方的 find path 函数](https://github.com/NVIDIA/cudnn-frontend/blob/1b0b5eac540b7f8fd19b18f1e6b8427c95503348/cmake/cuDNN.cmake)可以看到具体可用的查找方式，手动指定 `cudnn` 的安装路径给 `CUDNN_PATH` 即可，例如：

```bash
export CUDNN_PATH=/usr/local/cuda/cuda-12/cudnn/v8.9.7.29
```

`CUDNN_PATH` 路径下需要可以找到 `include/cudnn.h`。

2. **GCC版本大等于8.1**

参考[这个issue](https://github.com/NVIDIA/TransformerEngine/issues/1270)。编译需要支持 C++17 的 filesystem 头文件，transformer engine 团队内部使用 GCC 13.2.0 进行编译，可以参考下面的命令安装 GCC 13：

```bash
sudo apt update
sudo add-apt-repository ppa:ubuntu-toolchain-r/test
sudo apt update
sudo apt install gcc-13 g++-13
sudo update-alternatives --install /usr/bin/gcc gcc /usr/bin/gcc-13 60
sudo update-alternatives --install /usr/bin/g++ g++ /usr/bin/g++-13 60
``` -->

## 8 卡测试 SGLang

准备一台 8 卡机器，注意对拍默认会使用 `wandb` 和环境变量 `WANDB_API_KEY` 记录训练 metrics。8 x H100 上耗时约 4h。

使用前需要配置好 `WANDB_API_KEY`，可以参考[这个过程](https://community.wandb.ai/t/where-can-i-find-the-api-token-for-my-project/7914)。

```bash
export WANDB_API_KEY={YOUR_WANDB_API_KEY}

# 定义这个时间戳函数
function now() {
    date '+%Y-%m-%d-%H-%M'
}
```

可以直接运行来进行对拍：

```bash
python3 examples/data_preprocess/gsm8k.py
python3 examples/data_preprocess/math_dataset.py
mkdir log
bash examples/ppo_trainer/rollout_callibration.sh sglang $(now)
```

<!--

### vLLM

注意，vllm 和 sglang 是有依赖冲突的，直接从 verl main branch 安装 vllm 依赖的 verl，然后进行对拍。这里用的是 vllm 0.6.3。

```bash
cd ~
python3 -m venv ~/.python/verl-vllm
source ~/.python/verl-vllm/bin/activate
python3 -m pip install --upgrade pip
python3 -m pip install --upgrade uv
git clone https://github.com/volcengine/verl.git
cd verl
python3 -m uv pip install .
python3 -m uv pip install flash-attn --no-build-isolation
```

安装 verl-vllm 后，继续运行如下指令来测试 PPO 功能：

```bash
mkdir log
bash ~/verl-sglang/examples/ppo_trainer/rollout_callibration.sh vllm $(now)
```
-->
