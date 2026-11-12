# 02 · main.py + models 包 — 双字典选模型与 ImageNet 对照实验线

> 源码：`main.py`（458 行）、`models/__init__.py`（2 行）、`models/pd_resnet.py`（232 行）、`models/pd_vgg.py`（220 行）· 图谱定位：4 层第 1/3 层「文档与训练入口层 + 分类骨干模型层」· main.py fanOut=15 为全仓最大

## 一、角色定位：一个入口跑两组受控实验

main.py 自述改编自 pytorch/examples 的 imagenet/main.py（main.py:10），差异只在头部注释里一句话：加入 partial conv based padding 的网络选项（main.py:12-15）。它的存在意义是**实验形态**：zero padding 基线与 partial conv 替换在完全相同的脚本、超参、数据管线下对跑，README.MD:108-114 的 5 次运行 × 4 种 padding 对比表就是其产出。`models/` 包是被它消费的弹药库：pd_resnet 五深度 + pd_vgg 八变体共 13 个工厂函数，全部由 2 行 barrel 汇出（models/__init__.py:1-2）。

## 二、内部结构：双字典机制是脊柱

**字典收集**（main.py:38-50）：`import torchvision.models as models_baseline`（:38）与 `import models as models_partial`（:39）并置；用同一过滤式（小写、非 dunder、callable）各收集名字（:42-48），`model_names = baseline + partial`（:50）喂给 `--arch` choices（:62-66，默认 resnet50）。**构造分派**（main.py:147-159）：`args.arch in models_baseline.__dict__` 先查基线，否则落 partial 字典——同名优先基线，pd 前缀保证无冲突。

**pd_resnet 改造范式**（models/pd_resnet.py）：骨架复刻 torchvision（自述 :9-10）——BasicBlock（:44-73）、Bottleneck（:76-112，expansion=4 :77）、PDResNet 主体（:115-171，7x7 stem :120、_make_layer :139-154）；全部 3x3 走 conv3x3 工厂（:38-41 返回 PartialConv2d），downsample 1x1 也是 PartialConv2d（:143-145）；初始化对 PartialConv2d 做 kaiming（:132-137）。五个工厂 pdresnet18-152（:174-231）只是 layers 配置不同（如 50 层 [3,4,6,3] :204）。

**pd_vgg 改造范式**（models/pd_vgg.py）：cfg 四配置表 A/B/D/E（:103-108），make_layers_pd 逐项建层（:85-98——数字项建 PartialConv2d+可选 BN+ReLU :92-96，'M' 建 MaxPool :89-90）；PDVGG 主体含 4096-4096-1000 三层 classifier（:53-61）与独立初始化（:71-82）；八个工厂（:111-220），pretrained 时关 init_weights（:117-118）。

## 三、外部连接：依赖图上的枢纽

main.py fanOut=15：下行依赖 models 包（经 :39 的 import 与 :149-159 的动态取用）、torchvision（datasets/transforms/models :35-38）、torch.distributed（:31）。models/__init__.py 的 2 行 star-import（models/__init__.py:1-2）把 pd_resnet:18-19 与 pd_vgg:19-22 两份 `__all__` 抬进包字典——双字典机制的一半功劳在这两行。并行包装分三形态：`--gpu` 单卡、`world_size>1` 走 DDP（main.py:140-144，gloo :98）、默认 DataParallel 且 VGG 系只拆 features（:175-179，classifier 不值得拆卡）。**loss.py 不在这条线上**——main.py 全文不 import 它（VGG16PartialLoss 是 inpainting 侧资产）。

## 四、数据流：一次训练的生命周期

ImageFolder 目录协议进数据（train/val 分开传，main.py:56-60）；训练增强 RandomResizedCrop(224)+水平翻转（:216-223），验证 Resize(256)/CenterCrop(224)（:234-242）；DDP 时挂 DistributedSampler（:225-228）并逐 epoch set_epoch（:259-260）。主循环（:258-288）：adjust_learning_rate 阶梯 0.1×/30 epoch（:261，实现 :432-436）→ train（:291-347：forward :311 → CrossEntropyLoss :312 → zero_grad/backward/step :321-323，纯 fp32）→ validate（:350-405，no_grad :359，返回 top1 :405）→ 判优存 model_best.pth.tar（:270-278，save_checkpoint :408-411），`epoch >= 94` 后每 epoch 另存快照（:281-288）——配合默认 100 epoch（:69-70）与 batch 192（:78），是"5 runs 挑 best 做统计"的实验设计。指标经 AverageMeter（:414-429）与 accuracy topk（:439-453）聚合，逐行镜像写进 loss.txt（:339-347、:389-396）。

## 五、设计决策与四颗雷

1. **为什么双字典而不写两份脚本**：受控变量法——同脚本内换 arch 即换 padding 方案，实验差异只剩算子本身；字典按名字过滤（:42-48）还自动继承 torchvision 新增模型。
2. **雷一：pd 系 `--pretrained` 必炸**——model_urls 全空串（models/pd_resnet.py:30-36、models/pd_vgg.py:28-36），`model_zoo.load_url('')`（如 :182）直接抛错；torchvision 真实 URL 被注释在 pd_vgg.py:37-44，真权重走 README.MD:102-105 的 Dropbox。能这样留空的底层依据是 PartialConv2d 与 Conv2d 参数名形状全等，torchvision 权重可手工 load_state_dict 迁移。
3. **雷二：forward 不传 mask**——PDResNet.forward(self, x)（models/pd_resnet.py:156）、BasicBlock 同（:57）、PDVGG 同（models/pd_vgg.py:65）。图谱摘要所谓"逐层传递 (x, mask) 二元组"不成立；分类线里 mask 是算子内部的全 1 静默通道。
4. **雷三：`--dist-url` 默认 `tcp://224.66.41.62:23456`**（main.py:96）是 NVIDIA 内网地址残留；雷四：pd_vgg 初始化用已废弃的无下划线 API（nn.init.kaiming_normal/constant/normal，models/pd_vgg.py:74-82），新版 PyTorch 已移除——同仓 pd_resnet.py:132-137 却是现代写法，两种年代并存，复现建议锁 2018 年代环境。

## 六、新人提示

- 读懂双字典只需三处：main.py:38-50（收集）、:62-66（choices）、:147-159（分派）——之后任何"再加一个模型族"的需求都是照抄这个模式。
- 跑通最小闭环不必 ImageNet：随便一个 folder 数据集 + `python main.py -a resnet50 --epochs 1` 与 `-a pdresnet50` 对比 loss 曲线即可验证环境。
- checkpoint 目录名由 `--ckptdirprefix + checkpoint_<arch>_<prefix>/` 拼出（main.py:115），做批量实验时用 prefix 区分 run，晚期快照（:281-288）就是为多 run 统计预留的。
- 想理解 partial conv 对精度的真实影响，直接读 README.MD:114 的指标说明（zero/pd/ref/rep 四后缀 + 5 runs 均值/stdev/diff），再回头核对训练脚本里唯一的自变量——arch。
