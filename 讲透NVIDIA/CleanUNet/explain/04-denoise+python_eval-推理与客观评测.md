# 04 · denoise.py + python_eval.py —— 推理与客观评测

> 锚均从源码核实（commit 9487a8db）。denoise.py 骨架改编自 waveglow（denoise.py:1，BSD-3）；python_eval.py 为本仓自写。

## 角色定位

这对文件构成 CleanUNet 的**下游出口**：denoise.py 把训练产物变成 enhanced wav，python_eval.py 把 wav 变成 PESQ/STOI 分数。两者零 import 关联，靠文件系统与命名约定衔接（denoise 写 `enhanced_fileid_*.wav`，评测按同名模式读回）。

## 内部结构

**denoise.py**（157 行）核心是 denoise()（denoise.py:54-124）：
- 配置读取自 global train_config/trainset_config/network_config（denoise.py:67/71/81，`__main__` L141-147 注入——与 train.py 同款隐式耦合）。
- 数据：deepcopy 训练集配置并把 crop_length_sec 置 0（denoise.py:71-72），batch_size=1 全长推理（L73-78）。
- 权重：ckpt_iter 三态——'max' 走 find_max_epoch（L86-87）、'pretrained' **保持字符串**拼出 pretrained.pkl 路径（L88-90，与 exp/*/checkpoint/ 的 git-lfs 权重对齐）、数字直接 int；load_state_dict 后 net.eval()（L91-93）。
- 输出目录：pretrained 单独命名，数字迭代按 `{}k` 缩写（denoise.py:96-99）；dump=False 时收集 clean/generated 波形返回（L121-122）供外部调用评测。
- 推理循环：sortkey 规范文件名（denoise.py:108）→ sampling 前向（L114）→ scipy wavwrite 落盘（L117-119）。
- `__main__`（denoise.py:127-157）：仅 subset=='testing' 时执行 dump=True（L152-156）。

**python_eval.py**（60 行）：evaluate_dns()（python_eval.py:19-40）遍历**硬编码 range(300)**（L23，DNS no-reverb 测试集即 300 条，README.md:55-56）→ 读 clean 与目标 wav（L25-29）→ pesq 宽/窄带 + stoi 按样本长度加权累计（L35-38）→ 异常静默 continue（L30-31）；主程序除总长度打印均分（L58-60）。

## 外部连接

denoise.py import 三路（denoise.py:49-51）：dataset 加载器、util 四函数（rescale/find_max_epoch/print_size/sampling）、network 主模型；运行时 depends_on 两个 pretrained.pkl（git-lfs 指针，实体各 184336765B≈176MB）。python_eval.py 只依赖第三方 pesq/pystoi/scipy（python_eval.py:13-16），与仓内零 import——图谱中它是孤立叶子节点，仅被 README（L87）与 Dockerfile（pesq/pystoi 安装行）关联。

## 数据流

推理：DistributedSampler 关闭的 batch=1 DataLoader → noisy_audio.cuda() → sampling()（util.py:173-178 的 @torch.no_grad 包装）→ CleanUNet.forward 内部完成 std 归一化/补齐/编解码/反归一化 → generated_audio 挤回 numpy 写 16kHz wav（denoise.py:117-119）。评测：enhanced 目录 + 测试集 clean 目录 → 逐条 PESQ(16000, wb/nb)/STOI → 长度加权平均（python_eval.py:35-38，result 累加 指标×length，count 累加 length）。

## 设计决策

1. **ckpt_iter='pretrained' 字符串特判**（denoise.py:88-96）：避免 int() 转换毁掉特殊文件名，分支逻辑绕但正确——L88 先排除 pretrained 再转 int，L96 再按 pretrained 选目录名。
2. **batch=1 + 不裁剪**（denoise.py:71-78）：推理长度任意（模型内 padding 兜底，network.py:329），测试不需要 shuffle。
3. **加权而非简单平均**（python_eval.py:35-38）：长样本贡献更多，避免短片段主导均值——比多数开源评测脚本讲究。
4. **300 硬编码**（python_eval.py:23）：换测试集必须改代码，是微仓的偷懒但与 README 的数据准备流程（fileid_0..299）自洽。
5. **dump 开关**（denoise.py:63/116-122）：dump=False 返回波形对，给未来集成评测留了函数式接口。

## 新人提示

**头号陷阱（subset 契约错位）**：denoise.py:133-134 argparse choices=['training','testing','validation']，但 dataset.py:33 断言只放行 training/testing——传 -subset validation 会在数据集构造处 AssertionError 崩溃，这是两文件各自演化的缝隙。用 pretrained 权重先 `git lfs pull`（README.md:69），否则 torch.load 读到的是 3 行 lfs 指针文本直接炸。评测前确认 enhanced 目录名：pretrained 与数字迭代（如 100k）命名不同（denoise.py:96-99）。评测链三件套顺序：denoise.py → 得目录 → python_eval.py -e 指目录 -t 指测试集（README.md:87）。注意 README.md:89 说"1 GPU is used for evaluation"实为笔误——python_eval.py 全程 CPU。

（不计空格约 2250 字符，锚 40+）
