"""
实验 08 —— 数据管道: Dataset / DataLoader / Sampler / collate (训练必备)
对应文档: 04-数据管道.md
核心: 模型再好, 喂数据不对也白搭. PyTorch 数据管道是训练的"血液系统":
  1. Dataset: 定义"怎么取一条样本"
  2. DataLoader: 负责批量/打乱/并行加载/拼批
  3. Sampler: 控制采样顺序(类别均衡/加权等)
  4. collate_fn: 自定义"多条样本怎么拼成一个 batch"(如变长 padding)
跑法: python3 08_data_pipeline.py
"""
import torch
from torch.utils.data import Dataset, DataLoader, TensorDataset, WeightedRandomSampler
import numpy as np

print("=" * 66)
print("一、自定义 Dataset: 实现 __len__ 和 __getitem__ 即可")
print("=" * 66)
class SinDataset(Dataset):
    """合成数据集: x -> sin(x) + 噪声"""
    def __init__(self, n=200):
        self.x = torch.linspace(0, 6.28, n).unsqueeze(1)
        self.y = torch.sin(self.x) + 0.1*torch.randn(n, 1)
    def __len__(self):           # 数据集大小
        return len(self.x)
    def __getitem__(self, i):    # 取第 i 条样本 (返回 tensor)
        return self.x[i], self.y[i]

ds = SinDataset()
print(f"  数据集大小: {len(ds)}")
xi, yi = ds[0]
print(f"  ds[0]: x={xi.tolist()}, y={yi.tolist()}")
print("  => 任何数据(图片/文本/表格)只要实现这两个方法, 就能用 DataLoader")

print("\n" + "=" * 66)
print("二、DataLoader: 批量化 + 打乱 + 并行加载")
print("=" * 66)
dl = DataLoader(ds, batch_size=32, shuffle=True, num_workers=0)
batch_x, batch_y = next(iter(dl))    # 取一个 batch
print(f"  batch_size=32: x.shape={tuple(batch_x.shape)}, y.shape={tuple(batch_y.shape)}")
print(f"  每个 epoch 自动迭代: 共 {len(dl)} 个 batch")
# 训练循环标准写法
for step, (bx, by) in enumerate(dl):
    if step == 0:
        print(f"  训练循环里: for bx,by in dataloader: -> 每步拿到一个 batch")
        break
print("  关键参数:")
print("    batch_size: 每批样本数 (小batch泛化好但慢, 见'讲透泛化02章')")
print("    shuffle: 训练=True打乱(避免顺序偏差), 验证=False")
print("    num_workers: >0 用多进程并行加载(大数据/IO重时加速, 注意 fork 开销)")
print("    pin_memory=True: GPU 训练时加速 CPU->GPU 拷贝")
print("    drop_last: 训练时丢弃不满 batch_size 的最后一批(保证形状一致, 利于 compile)")

print("\n" + "=" * 66)
print("三、内置 TensorDataset: 现成数据最省事")
print("=" * 66)
X = torch.randn(100, 4); Y = torch.randint(0, 2, (100,))
tds = TensorDataset(X, Y)
tdl = DataLoader(tds, batch_size=16, shuffle=True)
bx, by = next(iter(tdl))
print(f"  TensorDataset + DataLoader: x={tuple(bx.shape)}, y={tuple(by.shape)}")
print("  => 已经是 tensor 的数据, 用 TensorDataset 一行搞定, 不用写类")

print("\n" + "=" * 66)
print("四、WeightedRandomSampler: 类别不均衡的救星")
print("=" * 66)
# 模拟不均衡: 90个类0, 10个类1
labels = torch.cat([torch.zeros(90), torch.ones(10)]).long()
# 给少数类更高采样权重
weights = torch.where(labels == 1, 9.0, 1.0)   # 类1 权重9x
sampler = WeightedRandomSampler(weights, num_samples=100, replacement=True)
imb_ds = TensorDataset(torch.randn(100, 4), labels)
imb_dl = DataLoader(imb_ds, batch_size=20, sampler=sampler)  # 注意:用sampler时shuffle必须False
sampled_labels = []
for _, by in imb_dl:
    sampled_labels.append(by)
sampled = torch.cat(sampled_labels)
print(f"  原始分布: 类0={int((labels==0).sum())}, 类1={int((labels==1).sum())} (严重不均衡)")
print(f"  加权采样后: 类0={int((sampled==0).sum())}, 类1={int((sampled==1).sum())} (接近均衡!)")
print("  => 检测/医疗/欺诈等少数类任务, WeightedRandomSampler 比过采样更高效")

print("\n" + "=" * 66)
print("五、collate_fn: 变长序列怎么拼 batch (NLP 必备)")
print("=" * 66)
class VarLenDataset(Dataset):
    def __init__(self):
        self.data = [torch.randn(torch.randint(3, 8, (1,)).item()) for _ in range(8)]
    def __len__(self): return len(self.data)
    def __getitem__(self, i): return self.data[i]

def pad_collate(batch):
    """把变长序列 pad 到等长, 返回 (padded, lengths)"""
    lens = torch.tensor([len(b) for b in batch])
    padded = torch.zeros(len(batch), lens.max().item())
    for i, b in enumerate(batch):
        padded[i, :len(b)] = b
    return padded, lens

vds = VarLenDataset()
vdl = DataLoader(vds, batch_size=4, collate_fn=pad_collate)
padded, lens = next(iter(vdl))
print(f"  原始: 4 条变长序列, 长度 {lens.tolist()}")
print(f"  pad 后成一个矩阵:\n{padded}")
print("  => collate_fn 让你能处理任意不规则数据(文本/图/点云), 这是 DataLoader 的灵活性所在")

print("\n核心洞察:")
print("  - Dataset(取一条) + DataLoader(拼批/打乱/并行) = PyTorch 数据管道的标准范式")
print("  - 覆盖所有场景: 内置TensorDataset / 自定义Dataset / Sampler采样 / collate变长")
print("  - 数据往往是训练瓶颈(IO/CPU), num_workers/pin_memory/prefetch 是加速旋钮")
