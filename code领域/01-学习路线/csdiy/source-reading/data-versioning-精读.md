# Data Versioning 精读：DVC / Git-LFS / Delta Lake

> 参照：DVC / Git-LFS / Delta Lake / LakeFS / HuggingFace Datasets
>
> csdiy 对应：data-pipeline精读 + tinygit + tinydb

---

## 一、为什么 ML 需要数据版本控制

```
传统 Git: 版本控制代码 → .py 文件 <1MB
ML 需求: 版本控制数据 → .csv/.parquet/.pt 文件 1GB-10TB

Git 的限制:
  • 单文件 >100MB 慢
  • .git 目录膨胀（数据变更频繁）
  • 无法 diff 二进制文件（模型权重）

→ 需要专门的数据版本控制工具
```

---

## 二、DVC（Data Version Control）

### 核心思想：Git 管代码 + DVC 管数据

```
# 代码用 Git
git add train.py && git commit -m "update training"

# 数据用 DVC
dvc add data/train.csv          # 记录数据版本
dvc push                        # 上传到远程存储 (S3/GCS/SSH)
git add data/train.csv.dvc      # 记录数据的"指针"
git commit -m "update dataset v2"

# 恢复特定版本的数据
git checkout v1.0
dvc checkout                    # 自动下载对应版本的数据
```

### DVC 架构

```
本地:
  data/train.csv       → 实际数据（.gitignore）
  data/train.csv.dvc   → DVC 元文件（MD5 + size + path）

远程:
  S3/GCS/SSH → 存储去重的数据块

Git 只跟踪 .dvc 文件（小文本文件）→ .git 不膨胀
```

---

## 三、HuggingFace Datasets（ML 数据的 Git）

```python
from datasets import load_dataset

# 加载特定版本
ds = load_dataset("imdb", revision="1.0.0")  # 版本号

# 加载特定 commit
ds = load_dataset("imdb", revision="a1b2c3d")  # git commit hash

# 推送自己的数据集
ds.push_to_hub("my-company/my-dataset", private=True)

# HF Hub 自动版本控制:
  # 每个 push = 一次 commit
  # 每个 tag = 一个版本
  # 支持数据 diff（文本数据）
```

---

## 四、Delta Lake（数据湖的 ACID）

### 问题

```
传统数据湖（S3 上的 Parquet）:
  ❌ 无 ACID（并发写入冲突）
  ❌ 无版本（无法回滚）
  ❌ Schema 演进困难

Delta Lake = Parquet + 事务日志
```

### 架构

```
_delta_log/           → 事务日志（JSON）
  00000000000000000000.json   → Version 0
  00000000000000000001.json   → Version 1 (append)
  00000000000000000002.json   → Version 2 (update)

part-00000-xxx.parquet → 实际数据

→ 日志记录每个版本的文件状态
→ 支持时间旅行: SELECT * FROM table VERSION AS OF 5
```

---

## 五、模型权重版本控制

### 问题

```
训练过程中:
  checkpoint-1000.pt → 14GB (7B FP32)
  checkpoint-2000.pt → 14GB
  checkpoint-3000.pt → 14GB
  → 3 个 checkpoint = 42GB

Git/DVC 无法高效处理（太多大文件）
```

### 解法

```
① HuggingFace Hub:
  model.safetensors → 自动版本控制 + CDN 分发

② Weights & Biases:
  wandb.log_artifact("model", type="checkpoint")
  → 自动去重（只存 diff）→ 省 10x 存储

③ DVC + 外部存储:
  dvc add model_v1.pt
  dvc push  → S3

④ Git-LFS:
  git lfs track "*.pt"
  → Git 管理 LFS 指针 + LFS server 管理大文件
```

---

## 六、ML 实验追踪（Reproducibility）

```python
# W&B / MLflow 追踪
import wandb
wandb.init(project="my-llm")

# 记录完整实验配置
config = {
    "model": "llama-7b",
    "dataset": "my-dataset@v2.3",  # 数据版本
    "lr": 3e-4,
    "epochs": 10,
    "quantization": "int8",
}
wandb.config.update(config)

# 记录指标
for epoch in range(10):
    loss = train_epoch()
    wandb.log({"loss": loss, "epoch": epoch})

# 保存模型（自动版本控制）
wandb.log_artifact("model.pt", type="model", aliases=["latest", "best"])
```

### 完整可复现链路

```
实验 ID: abc123
  ├── Code: git@commit:def456
  ├── Data: dataset@v2.3 (DVC hash:789xyz)
  ├── Model: model.pt (W&B artifact)
  ├── Config: lr=3e-4, batch=32, fp16
  └── Environment: docker@tag:latest

→ 给定实验 ID → 能完全复现训练
```

---

## 七、各工具对比

| 工具 | 管什么 | 大小限制 | 版本回滚 | 适用 |
|------|--------|---------|---------|------|
| Git | 代码 | <100MB | ✅ | 源码 |
| Git-LFS | 大文件 | ~5GB | ✅ | 模型权重 |
| DVC | 数据/模型 | 无限 | ✅ | ML 数据 |
| HF Hub | 数据集/模型 | 无限 | ✅ | NLP 模型 |
| Delta Lake | 结构化数据 | 无限 | ✅ | 数据湖 |
| W&B | 实验全链路 | 无限 | ✅ | 实验追踪 |
| LakeFS | 数据湖 | 无限 | ✅ | 大规模数据 |

---

## 八、一句话总结

> DVC = Git 管代码 + DVC 管数据（指针 + 远程存储）。
> Delta Lake = Parquet + 事务日志 → ACID + 时间旅行。
> W&B = 代码 + 数据 + 模型 + 配置的完整实验追踪。
>
> **可复现性 = 数据版本 + 代码版本 + 模型版本 + 环境版本。**

---

*配套：[data-pipeline精读](data-pipeline-精读.md) | [tinygit](../projects/tinygit/main.py) | [tinydb](../projects/tinydb/main.py)*
