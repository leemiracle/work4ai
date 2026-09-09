
import torch
import torch.nn as nn

class MultiHeadAttention(nn.Module):
    """
    多头注意力机制实现
    
    学习任务:
    1. 理解Q、K、V的计算
    2. 实现缩放点积注意力
    3. 实现多头并行计算
    """
    
    def __init__(self, d_model, num_heads):
        super().__init__()
        assert d_model % num_heads == 0, "d_model must be divisible by num_heads"
        
        self.d_model = d_model
        self.num_heads = num_heads
        self.head_dim = d_model // num_heads
        
        # TODO 1: 理解为什么需要三个线性投影？
        # 提示: Q(query)、K(key)、V(value)分别用于计算注意力权重和值
        self.qkv_proj = nn.Linear(d_model, 3 * d_model)
        self.out_proj = nn.Linear(d_model, d_model)
    
    def forward(self, x, mask=None):
        """
        前向传播
        
        Args:
            x: 输入张量 [batch_size, seq_len, d_model]
            mask: 可选的掩码张量
        
        Returns:
            输出张量 [batch_size, seq_len, d_model]
        """
        batch_size, seq_len, _ = x.shape
        
        # TODO 2: 一次性计算Q、K、V，为什么这样效率高？
        qkv = self.qkv_proj(x)
        q, k, v = qkv.chunk(3, dim=-1)
        
        # TODO 3: 理解reshape和transpose的作用
        # 提示: 将多头注意力头分离出来，便于并行计算
        q = q.view(batch_size, seq_len, self.num_heads, self.head_dim).transpose(1, 2)
        k = k.view(batch_size, seq_len, self.num_heads, self.head_dim).transpose(1, 2)
        v = v.view(batch_size, seq_len, self.num_heads, self.head_dim).transpose(1, 2)
        
        # TODO 4: 实现缩放点积注意力
        # 提示: 使用sqrt(head_dim)进行缩放，防止梯度消失
        attn = torch.matmul(q, k.transpose(-2, -1)) / (self.head_dim ** 0.5)
        
        # TODO 5: 如果需要，应用mask（例如在解码器中）
        if mask is not None:
            attn = attn.masked_fill(mask == 0, float('-inf'))
        
        attn = torch.softmax(attn, dim=-1)
        
        # TODO 6: 计算加权和
        out = torch.matmul(attn, v)
        
        # TODO 7: 将多头结果合并回原始形状
        out = out.transpose(1, 2).contiguous().view(batch_size, seq_len, self.d_model)
        return self.out_proj(out)

# 测试代码
if __name__ == "__main__":
    # 创建测试输入
    batch_size, seq_len, d_model = 2, 10, 512
    num_heads = 8
    
    x = torch.randn(batch_size, seq_len, d_model)
    
    # 创建注意力层
    mha = MultiHeadAttention(d_model, num_heads)
    
    # 前向传播
    output = mha(x)
    
    print(f"输入形状: {x.shape}")
    print(f"输出形状: {output.shape}")
    print(f"✅ 测试通过！")
