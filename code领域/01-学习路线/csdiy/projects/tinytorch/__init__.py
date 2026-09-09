"""tinytorch — 参照 micrograd + PyTorch 的深度学习框架"""
from .tensor import Value, tensor, zero_grad
from .nn import Module, Linear, Embedding, LayerNorm, Dropout, ReLU, Tanh, Sigmoid, Sequential, MLP
from .optim import Optimizer, SGD, Momentum, Adam, AdamW, CosineScheduler
from .loss import mse_loss, cross_entropy, binary_ce, focal_loss
from .train import DataLoader, Trainer
from .functional import softmax, sigmoid, relu, gelu, linear, embedding, dropout, layer_norm
from .save_load import save, load, state_dict, load_state_dict, count_parameters, model_summary

__version__ = "1.0.0"
__all__ = [
    # Tensor
    "Value", "tensor", "zero_grad",
    # Layers
    "Module", "Linear", "Embedding", "LayerNorm", "Dropout",
    "ReLU", "Tanh", "Sigmoid", "Sequential", "MLP",
    # Optimizers
    "Optimizer", "SGD", "Momentum", "Adam", "AdamW", "CosineScheduler",
    # Losses
    "mse_loss", "cross_entropy", "binary_ce", "focal_loss",
    # Training
    "DataLoader", "Trainer",
    # Functional
    "softmax", "sigmoid", "relu", "gelu", "linear", "embedding", "dropout", "layer_norm",
    # Save/Load
    "save", "load", "state_dict", "load_state_dict", "count_parameters", "model_summary",
]
