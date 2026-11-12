# 11 · examples/frameworks：框架集成示例体系

## ① 角色定位

examples/ 是 ClearML SDK 的"活文档"，顶层按场景分 16 个域（advanced/automation/cicd/clearml_agent/datasets/distributed/frameworks/hyperdatasets/optimization/pipeline/reporting/router/scheduler/services/storage）。其中 **frameworks/ 是体量最大的一块：21 个框架子目录、53 个 .py 文件**，使命是逐一验证"接入 ClearML 只需在脚本里加 `Task.init`"这一核心承诺——每个目录一个框架、一份独立 requirements.txt，脚本即最小可运行集成样例。值得注意的是目录构成并不仅限 ML 训练框架：除 pytorch/tensorflow/scikit-learn/xgboost/lightgbm/catboost/fastai/ignite/keras/megengine/huggingface/autokeras/kerastuner/openmmlab/pytorch-lightning/tensorboardx/matplotlib 外，还有 click/fire/hydra/jsonargparse 四个 **CLI/配置框架**目录——它们演示的是"命令行参数与配置文件如何被自动记录"，这是新人最容易忽略的半壁江山。

## ② 内部结构

以 **examples/frameworks/pytorch/** 为代表剖析（9 个脚本 + requirements.txt + notebooks/ 四子目录）：

- **pytorch_mnist.py**——入门代表。`pytorch_mnist.py:15` 定义 `Net`（Lenet-5 变体：conv1/conv2/fc1/fc2，pytorch_mnist.py:18-23）；`pytorch_mnist.py:37` `train()`，每 log_interval 批次用 `Logger.current_logger().report_scalar("train", "loss", ...)` 手动上报损失（pytorch_mnist.py:47-53）；`pytorch_mnist.py:60` `test()` 上报准确率与平均损失两个 series（pytorch_mnist.py:80、pytorch_mnist.py:86）；`pytorch_mnist.py:98` `main()`；**pytorch_mnist.py:101 `Task.init(project_name="examples", task_name="PyTorch MNIST train")` 位于 argparse 定义之前**——这个顺序保证命令行参数被自动捕获为 Task 超参；`pytorch_mnist.py:237` `torch.save(model.state_dict(), ...)` 落盘 checkpoint（框架集成会自动把它上传为输出模型）。
- 兄弟脚本各守一个专题：pytorch_matplotlib.py（matplotlib 图表自动捕获）、pytorch_tensorboard.py 与 pytorch_tensorboardx.py（TensorBoard/TensorBoardX 两种桥）、pytorch_model_update.py（模型上传与热更新，也是 pytorch-ignite 依赖的消费者）、pytorch_distributed_example.py（DDP 分布式）、pytorch_abseil.py（absl flags）、tensorboard_toy_pytorch.py。
- **requirements.txt**（目录级共享）：`clearml>=1.14.4`、`torch>=1.1.0`、`torchvision>=0.3.0`、`pytorch-ignite`、`tensorboardX`，并含按 Python 版本的条件依赖（如 `tensorboard<=2.11.2 ; python_version <= '3.7'`、protobuf 双版本分支）——示范"多版本兼容该怎么写依赖"。
- **notebooks/** 下分 audio/image/table/text 四类，是输入数据形态（音频/图像/表格/文本）的自动记录演示（如 image/ 下的 image_classification_CIFAR10.ipynb），与框架无关。
- **CLI 框架样例**：click/click_multi_cmd.py:1-17 在 `@click.group()` 装饰的命令里调 `Task.init`——展示 click 参数树的记录；hydra/ 带 config_files/ 子目录，展示配置快照随 Task 保存。

## ③ 外部连接（图谱边证据）

图谱对 pytorch_mnist.py 的建模极具代表性：OUT 边只有一条 imports——`file:clearml/__init__.py`；contains 边为 Net/train/test/main 四个顶层符号。**零内部模块依赖**是全 frameworks 目录的共同特征（grep 实证所有示例只 `from clearml import Task, Logger` 级别地引顶层 API）：示例体系故意只碰公共 API 面，等价于一份"SDK 对外契约"的可执行规格说明。对照 examples/router/http_router.py:33 用 `task.get_http_router()`（与 10 篇联动）——连最新特性也先落示例再落文档。

## ④ 数据流

以 mnist 为例的完整数据流：脚本启动 → `Task.init`（pytorch_mnist.py:101）触发 binding 层对 torch 的 patch 与进程挂钩 → argparse 解析时参数表被捕获为 Task configuration → 训练循环中 `Logger.report_scalar`（pytorch_mnist.py:47）显式上报 loss，同时 ResourceMonitor 后台采集 CPU/GPU 曲线 → `torch.save`（pytorch_mnist.py:237）产出的 checkpoint 被框架集成劫持上传（output_uri 目标）→ Web UI 汇聚为实验卡片。逆向数据流同样成立：在 UI 里 clone 该 Task 改 `batch_size`，或命令行 `clearml-task --script examples/frameworks/pytorch/pytorch_mnist.py --args batch_size=128 --queue ...`（09 篇的 CLI 消费同一 Task 元数据）即可远程复现。

## ⑤ 设计决策

1. **一框架一目录一 requirements**：每个目录可独立 `pip install -r` 后直接跑，CI 与用户复现成本最低。
2. **Task.init 前置于 argparse**：参数捕获依赖 init 时机，所有示例统一把 init 放 main() 第一行（pytorch_mnist.py:101 模式），这是隐式 API 契约的示范教学。
3. **手动与自动双轨展示**：mnist 同时展示手动 `report_scalar`（pytorch_mnist.py:47/pytorch_mnist.py:80）与自动捕获（matplotlib/模型 checkpoint），让用户看见两层 API 的边界。
4. **示例不进发布包**：setup.py 的 packages 只含 `clearml*`，examples 纯仓库资产，不随 pip 分发——示例与 SDK 版本同步演进但互不拖累。
5. **CLI/配置框架单独设目录**：click/fire/hydra/jsonargparse 与训练框架平级，宣示"实验可复现性包含参数与配置"的产品立场。

## ⑥ 新人提示（含勘误）

- **勘误 1**：huggingface/ 目录只有 transformers.ipynb 一个 notebook，**没有任何 .py**——按"找脚本学集成"的思路会扑空，直接开 notebook。
- **勘误 2**：tensorboard 集成有两个入口——tensorflow/ 目录里的 tensorboard_*.py（TensorFlow 原生）与独立的 tensorboardx/ 目录（第三方 tensorboardX 库），框架不同别混抄。
- **勘误 3**：keras/ 下有 legacy/ 子目录（旧版 Keras，keras_tensorboard.py + jupyter.ipynb），新代码应看 keras_v3.py；两代 API 差异大。
- **勘误 4**：pytorch/requirements.txt 里的 pytorch-ignite 不是 mnist 用的——它服务于 pytorch_model_update.py；requirements 是目录级而非脚本级。
- notebooks/ 按数据形态（audio/image/table/text）组织而非按框架，初看目录树容易误判成"四种框架"。
- 示例的 `Logger.current_logger()`（:47）与 `Task.current_task().get_logger()` 等价，前者是示例惯用的简写。
- examples/frameworks 共 21 目录 53 个 .py（find 实证），但分布极不均：pytorch 9 个、scikit-learn 2 个、huggingface 0 个——目录存在不等于示例丰富。
