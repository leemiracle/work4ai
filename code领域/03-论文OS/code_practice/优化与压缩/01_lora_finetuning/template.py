"""
LoRA微调实现

学习任务:
1. 理解LoRA的原理
2. 实现LoRA层
3. 应用LoRA到预训练模型
"""

import torch
import torch.nn as nn

# TODO 1: 实现LoRA层
class LoRALayer(nn.Module):
    """
    低秩适应（Low-Rank Adaptation）层
    
    核心思想: 通过低秩矩阵分解来更新模型参数，减少参数量
    """
    
    def __init__(self, in_features: int, out_features: int, rank: int = 4, alpha: float = 1.0):
        super().__init__()
        self.in_features = in_features
        self.out_features = out_features
        self.rank = rank
        self.alpha = alpha
        
        # TODO: 理解为什么rank通常很小（如4、8、16）
        # A: [rank, in_features], B: [out_features, rank]
        self.lora_A = nn.Parameter(torch.randn(rank, in_features))
        self.lora_B = nn.Parameter(torch.zeros(out_features, rank))
        
        self.scaling = self.alpha / self.rank
        
        # 初始化
        nn.init.kaiming_uniform_(self.lora_A, a=5 ** 0.5)
        nn.init.zeros_(self.lora_B)
    
    def forward(self, x):
        """
        前向传播
        
        Args:
            x: 输入张量 [batch_size, ..., in_features]
        
        Returns:
            输出张量 [batch_size, ..., out_features]
        """
        # TODO: 实现LoRA前向传播
        # 提示: Wx = (W_0 + BA)x = W_0x + B(Ax)
        result = x @ self.lora_A.T  # [batch_size, ..., rank]
        result = result @ self.lora_B.T  # [batch_size, ..., out_features]
        return result * self.scaling

# TODO 2: 将LoRA应用到线性层
class LinearWithLoRA(nn.Module):
    def __init__(self, in_features, out_features, rank=4, alpha=1.0):
        super().__init__()
        self.linear = nn.Linear(in_features, out_features)
        self.lora = LoRALayer(in_features, out_features, rank, alpha)
    
    def forward(self, x):
        # TODO: 冻结原始权重，只训练LoRA参数
        return self.linear(x) + self.lora(x)

# TODO 3: 实现LoRA模型包装器
class LoRAModelWrapper(nn.Module):
    """
    为预训练模型添加LoRA适配器
    """
    
    def __init__(self, base_model, target_modules: List[str] = None):
        super().__init__()
        self.base_model = base_model
        self.target_modules = target_modules or ['q_proj', 'v_proj']
        
        # TODO: 为目标模块添加LoRA层
        # 提示: 替换原始的nn.Linear为LinearWithLoRA
        self._apply_lora()
    
    def _apply_lora(self):
        # TODO: 实现LoRA应用逻辑
        # 遍历模型的所有模块，找到目标模块并替换
        pass
    
    def forward(self, *args, **kwargs):
        return self.base_model(*args, **kwargs)
    
    def save_lora_weights(self, path: str):
        """
        只保存LoRA权重（节省空间）
        """
        # TODO: 实现LoRA权重保存
        pass
    
    def load_lora_weights(self, path: str):
        """
        加载LoRA权重
        """
        # TODO: 实现LoRA权重加载
        pass

# 测试代码
if __name__ == '__main__':
    # 测试LoRA层
    x = torch.randn(2, 768)
    lora = LoRALayer(768, 768, rank=4)
    output = lora(x)
    print(f'✅ LoRA层测试通过: {x.shape} -> {output.shape}')
    
    # 测试带LoRA的线性层
    linear_lora = LinearWithLoRA(768, 768, rank=4)
    output2 = linear_lora(x)
    print(f'✅ LinearWithLoRA测试通过: {output2.shape}')
