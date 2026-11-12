# 04 · Python 双世代绑定：cffi 到 pybind11 的换代现场

## 角色定位

`pytorch/` 与 `pytorch1.0/` 是同一套 Python API 的两代底座：前者是 PyTorch 0.4 世代的 cffi 方案，后者是 PyTorch 1.0 之后的 pybind11 方案。两代 `dataset.py`/`loader.py` 几乎同构（395 行 vs 385 行），换的只是 C 桥——这使得本仓成为研究"绑定技术换代"的完整标本：上层 API 不动，底座整体替换。

## 内部结构

**cffi 世代的构建链是三段接力**：`pytorch/Makefile:6-7` 用 `gcc -E -P -DCFFI` 把 `VideoLoader.h`+`PictureSequence.h` 预处理成纯 C 声明的 `nvvl_generated.h`——这依赖头文件顶部的 CFFI 宏分支（`include/PictureSequence.h:3-10`，用前置声明顶掉 `<cuda_runtime.h>`）；`pytorch/build.py:16` 用 `torch.utils.ffi.create_extension`（0.4 时代 API，`build.py:30` 构建时还会 subprocess 调 make 生成头）；`pytorch/setup.py:20-32` 用猴子补丁给四个 setuptools 命令类动态加 `--with-nvvl/--system-nvvl` 选项而非子类化，`run_build` 现场对源码仓跑 cmake+make（`:34-58`）。C 桥本体薄到只有 8 行：`pytorch/nvvl/src/nvvl_th.c:6-8` 借 THCState 把 torch 当前流传给 `nvvl_sequence_stream_wait`。**pybind11 世代**则一个文件做完：`pytorch1.0/src/nvvl_th.cpp:11` `PYBIND11_MODULE(_nvvl, m)` 导出三枚举（`:12-29`）、LayerDesc 16 字段 def_readwrite（`:37-52`）、Float/Half/Byte 三种 Layer 类——数据指针用 `set_data(int64_t)` 传整型地址（`:60-62,68-70,76-78`）、set_layer 三个模板重载（`:82-93`）、wait_stream 仍借 THCState（`:97-99`，注意 1.0 世代还没甩掉 THC）、VideoLoader 八方法（`:123-132`）；setup 换 `torch.utils.cpp_extension.CUDAExtension`（`pytorch1.0/setup.py:8-9`）。

## 外部连接

向下链 `libnvvl.so`（setup 的 run_build 自动 cmake 源码仓，`pytorch/setup.py:47-58`；`runtime_library_dirs=["$ORIGIN"]` 让 .so 跟包走，`:56`）。向上给 `examples/pytorch_superres/` 训练工程与 `pytorch/test/benchmark.py` 基准供数据。`pytorch/nvvl/__init__.py:1-2` 导出 VideoDataset/VideoLoader/ProcessDesc 三件套，另暴露便捷函数 `video_size_from_file`（`:4`）。

## 数据流

训练侧一次 epoch 的流动：`VideoDataset.__init__`（`pytorch/nvvl/dataset.py:186`）创建 loader（`:212`）、逐文件 `nvvl_frame_count` 建帧数索引并把可采样数算成 `count - sequence_length + 1`（`:218-223`）、`nvvl_video_size` 取尺寸（`:228`）、把 desc 的 width/height/count 默认值回填（`:240-247`）。`VideoLoader`（`pytorch/nvvl/loader.py:7`）迭代开始把全部样本索引 `_read_sample` 压进 C 层（`:118-125`），再按 `buffer_length=3` 先行 receive 三批（`:127-128`）填满双 deque（tensor_queue/batch_size_queue，`:77-79`）；`__next__` 每弹出一批前先补一发 `_receive_batch` 保持流水线满载（`:105-107`）——预取深度就是这么来的。`_start_receive` 里 ProcessDesc 的声明式参数被翻译成 `nvvl_set_layer` 调用，stride 按 dimension_order（默认 "fchw"，`dataset.py:73`）现场映射（`:324-325`）。

## 设计决策

(1) **`-DCFFI` 预处理戏法**：不维护两份头，让 cffi 直接吃 C++ 头的 C 子集——2016-2018 年 ctypes/cffi 生态的标准操作，`gcc -E -P` 去掉注释与指令后剩下的就是可 parse 的声明。(2) **猴子补丁 setup.py**（`pytorch/setup.py:70-71` 直接替换命令类方法）：非常规但有效，避免了复制四个命令类的样板；pytorch1.0 版沿用到 CUDAExtension（`pytorch1.0/setup.py:21-38`）。(3) **ProcessDesc 的属性魔法**：重载 `__getattribute__/__setattr__` 把未知属性转发给内部 `_desc`（cffi 结构体），已知属性（如 dimension_order）留在 Python 侧（`dataset.py:131-143`）——用一个类同时充当"用户配置对象"和"C 结构体视图"，代价是任何拼写错误都静默落进 C 结构体。(4) **int64 传指针**（pybind11 侧 set_data）：Python 侧 `tensor.data_ptr()` 是整数，绕开 pybind11 对裸指针的所有权麻烦——笨但稳。

## 新人提示

今天装这仓直接用 `pytorch1.0/`，但 THC 头在 PyTorch 1.11+ 已删除，nvvl_th.cpp 的 `THCState_getCurrentStream`（`pytorch1.0/src/nvvl_th.cpp:97-99`）需替换为 `c10::cuda::getCurrentCUDAStream`——这是把本仓移植到现代 PyTorch 的第一刀。读 loader.py 先看 `__iter__`/`__next__` 的预取配合（`pytorch/nvvl/loader.py:100-116`），"tensor_queue 空但 samples_left>0"的断言（`:102`）能帮你定位消费顺序错误。两代 dataset.py 的差异极小，diff 一遍（395 vs 385 行）就是一次绑定换代的完整影响面测量。benchmark 里 `--sleep` 参数是人工调的"模拟训练消耗"节拍（`pytorch/test/run_docker_test.sh`），对比数据加载器时要意识到它在模拟而非真实训练。
