#!/usr/bin/env python3
"""
tinytorch/train.py — 训练循环 + DataLoader + 评估

参照：PyTorch Lightning / nanoGPT train.py / Keras model.fit
csdiy 对应：nanoGPT精读(train.py) + tinyml

核心：
  DataLoader  — mini-batch 采样
  Trainer     — 封装训练循环（前向→损失→反向→更新→日志）
  metrics     — accuracy / perplexity
"""
import random, math, time
from .tensor import Value, zero_grad

class DataLoader:
    """数据加载器（参照 PyTorch DataLoader）"""
    def __init__(self, X, y, batch_size=32, shuffle=True):
        self.X = list(X)
        self.y = list(y)
        self.bs = batch_size
        self.shuffle = shuffle
    def __iter__(self):
        indices = list(range(len(self.X)))
        if self.shuffle:
            random.shuffle(indices)
        for i in range(0, len(indices), self.bs):
            batch = indices[i:i + self.bs]
            yield [self.X[j] for j in batch], [self.y[j] for j in batch]
    def __len__(self):
        return (len(self.X) + self.bs - 1) // self.bs

class Trainer:
    """训练器（参照 PyTorch Lightning / Keras model.fit）

    用法：
        trainer = Trainer(model, optimizer, loss_fn, epochs=100)
        trainer.fit(dataloader)
    """
    def __init__(self, model, optimizer, loss_fn, epochs=100, lr_scheduler=None, verbose=True):
        self.model = model
        self.optimizer = optimizer
        self.loss_fn = loss_fn
        self.epochs = epochs
        self.scheduler = lr_scheduler
        self.verbose = verbose
        self.history = {'loss': [], 'acc': [], 'lr': []}

    def fit(self, dataloader, val_loader=None):
        """训练循环（参照 nanoGPT train.py 的主循环）"""
        for epoch in range(self.epochs):
            # ─── 训练阶段 ───
            self.model.train()
            total_loss = 0
            total_correct = 0
            total_samples = 0

            for batch_x, batch_y in dataloader:
                self.optimizer.zero_grad()

                batch_loss = Value(0.0)
                for x, y in zip(batch_x, batch_y):
                    # 前向传播
                    logits = self.model([Value(xi) for xi in x])
                    # 计算损失
                    if self.loss_fn == 'classification':
                        from .loss import cross_entropy
                        loss = cross_entropy(logits, y)
                    else:
                        from .loss import mse_loss
                        loss = mse_loss(logits, [y])
                    batch_loss = batch_loss + loss

                    # 统计 accuracy
                    if self.loss_fn == 'classification':
                        pred = max(range(len(logits)), key=lambda i: logits[i].data)
                        if pred == y:
                            total_correct += 1
                    total_samples += 1

                # 反向传播
                avg_loss = batch_loss * (1.0 / len(batch_x))
                avg_loss.backward()

                # 参数更新
                self.optimizer.step()
                total_loss += avg_loss.data

            # ─── 记录 ───
            avg = total_loss / max(1, len(dataloader))
            acc = total_correct / max(1, total_samples) if self.loss_fn == 'classification' else 0
            lr = self.optimizer.lr
            if self.scheduler:
                lr = self.scheduler.step()

            self.history['loss'].append(avg)
            self.history['acc'].append(acc)
            self.history['lr'].append(lr)

            if self.verbose and (epoch % max(1, self.epochs // 10) == 0 or epoch == self.epochs - 1):
                msg = f"  epoch {epoch:4d}  loss={avg:.6f}"
                if self.loss_fn == 'classification':
                    msg += f"  acc={acc:.2%}"
                msg += f"  lr={lr:.6f}"
                print(msg)

        return self.history

    def predict(self, x):
        """推理（参照 PyTorch model.eval() + model(x)）"""
        self.model.eval()
        logits = self.model([Value(xi) for xi in x])
        return [l.data for l in logits]


def accuracy(model, X, y):
    """计算准确率"""
    model.eval()
    correct = 0
    for xi, yi in zip(X, y):
        logits = model([Value(v) for v in xi])
        pred = max(range(len(logits)), key=lambda i: logits[i].data)
        if pred == yi:
            correct += 1
    return correct / len(X)
