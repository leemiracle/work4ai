#!/usr/bin/env python3
"""
tinytorch/save_load.py — 模型保存/加载（参照 torch.save / torch.load）

功能：
  save(model, path)     — 序列化模型参数到 JSON
  load(model, path)     — 从 JSON 恢复参数
  state_dict(model)     — 提取参数字典
  load_state_dict(model, state) — 加载参数字典
"""
import json
from .tensor import Value
from .nn import Module

def state_dict(model: Module) -> dict:
    """提取模型参数（参照 torch.nn.Module.state_dict）"""
    params = model.parameters()
    return {
        "num_params": len(params),
        "data": [p.data for p in params],
        "grads": [p.grad for p in params],
    }

def load_state_dict(model: Module, state: dict):
    """加载参数（参照 torch.nn.Module.load_state_dict）"""
    params = model.parameters()
    data = state["data"]
    for i, p in enumerate(params):
        if i < len(data):
            p.data = data[i]
    return model

def save(model: Module, path: str):
    """保存模型到 JSON 文件（参照 torch.save）"""
    state = state_dict(model)
    with open(path, 'w') as f:
        json.dump(state, f)
    return path

def load(model: Module, path: str):
    """从 JSON 文件加载模型（参照 torch.load）"""
    with open(path) as f:
        state = json.load(f)
    load_state_dict(model, state)
    return model

def count_parameters(model: Module) -> int:
    """参数计数（参照 sum(p.numel() for p in model.parameters())）"""
    return len(model.parameters())

def model_summary(model: Module):
    """模型摘要（参照 torchsummary）"""
    params = count_parameters(model)
    trainable = sum(1 for p in model.parameters())
    print(f"  Model Summary")
    print(f"  {'─'*40}")
    print(f"  Parameters:     {params}")
    print(f"  Trainable:      {trainable}")
    print(f"  Memory (FP32):  {params * 4 / 1024:.1f} KB")
    print(f"  Memory (BF16):  {params * 2 / 1024:.1f} KB")
