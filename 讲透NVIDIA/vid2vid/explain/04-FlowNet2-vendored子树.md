# 04 · FlowNet2 vendored 子树：eval-only 参考流计算器与 Python2 化石层

## 角色定位

vid2vid 把 NVIDIA/flow'n'draft 上游 FlowNet2-PyTorch 整树 vendored 进 `models/flownet2_pytorch/`（含其独立训练栈 datasets/main/convert），但主链只通过一个 60 行的窄包装 `models/flownet.py:6` 消费它：FlowNet2 在这里不是训练对象，而是冻结的"真值光流探测器"，为 D 侧损失与判别输入提供参考流与置信度。

## 内部结构

包装层三步走：initialize 内延迟 import 上游三个符号（models/flownet.py:13-15：models/tools/Resample2d），`module_to_dict(flownet2_models)['FlowNet2'](fp16=opt.fp16)` 字符串路由实例化（models/flownet.py:18），load_state_dict 后立刻 eval()（models/flownet.py:20-21）。forward 全程 torch.no_grad()（models/flownet.py:26）。上游侧的最大 imprint 是 Python2 时代：convert.py shebang 即 python2.7 且 import caffe（models/flownet2_pytorch/convert.py:1-3，权重格式转换工具）；main.py:264 的 `d.cuda(async=True)` 中 async 是 Python 3.7+ 保留字，整文件无法被 Python3 解析（上游训练入口，主链不消费）。models/flownet2_pytorch/models.py:16 `from .networks.submodules import *` 星号导入——submodules 未定义 __all__，全部顶层符号泄漏进网络命名空间。

## 外部连接

调用链：train.py 每 epoch 先跑 flowNet 拿 (flow_ref, conf_ref)，D 侧 MaskedL1Loss 用 conf 加权（models/vid2vid_model_D.py:63-64）、时序判别器把 flow_ref 拼进输入通道（models/vid2vid_model_D.py:187-188）。权重文件 models/flownet2_pytorch/FlowNet2_checkpoint.pth.tar 由 `scripts/download_flownet2.py` 就位——但该脚本的 torch 版本分支（0.4.1 选不同 file_id）已整体 docstring 化（scripts/download_flownet2.py:5-11），现行只剩 `os.system('bash install.sh')` 单一路径（scripts/download_flownet2.py:18）。fp16 时上游 forward 边界 float/half 切换（models/flownet2_pytorch/models.py:28），文件头注释硬编码 'Parameter count = 162,518,834'（models/flownet2_pytorch/models.py:17）。

## 数据流

`compute_flow_and_conf`（models/flownet.py:43）：输入边长对齐 64 倍数（models/flownet.py:47，//64*64 截断+bilinear 缩放），双帧 cat 后过 FlowNet2 得 flow1；置信度不用网络头，而是 warp 重投影误差阈值化：`conf = (norm(im1 - resample(im2, flow1)) < 0.02)`（models/flownet.py:55）——光流可信处 warp 回去的图像应与原帧几乎一致；最后 flow/conf 双双 detach 返回（models/flownet.py:59），上游不产生任何梯度。

## 设计决策

其一，"重投影误差当置信度"是个精妙的零成本不确定性估计：不需要 FlowNet2 输出 conf 通道，几何自洽性直接量化可信度。其二，eval-only + detach（models/flownet.py:21/59）把参考流从对抗博弈中隔离——若光流可训练，生成器会学会欺骗光流而非提升画质。其三，vendored 整树而非 pip 依赖：2018 年 FlowNet2-PyTorch 无稳定包发布，且 vid2vid 需要改 fp16 路径；代价是化石层永久滞留（docker 里 cuda9.0 + torch0.4 环境，docker/Dockerfile:1，单阶段构建无 CMD，靠 docker/launch_docker.sh:5 的 nvidia-docker run 交互进入；Dockerfile 尾注自述 flownet2 下载脚本偶发需容器启动后重跑）。

## 新人提示

只需要参考流时读 flownet.py 全文即可（60 行）；不要试图 import 上游 datasets.py/main.py/convert.py——datasets.py 是上游独立训练数据层，vid2vid 的 data/ 包不消费它，main.py 在 Python3 下直接语法死亡。想换现代光流（RAFT 等）只需保持两个契约：输出 2 通道 flow 与 1 通道 conf、输入 64 倍数对齐，替换点就在 flownet.py:18 一行。星号导入意味着 submodules 里任何同名符号都可能遮蔽上游网络定义，排查"莫名改了行为"先查命名冲突。
