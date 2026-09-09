import torch
import torch.nn as nn
import torch.nn.functional as F

class DDPM(nn.Module):
    """
    扩散概率模型（DDPM）实现
    
    学习任务:
    1. 实现前向扩散过程（添加噪声）
    2. 实现反向去噪过程
    3. 实现U-Net架构的denoising model
    """
    
    def __init__(self, in_channels=3, hidden_dim=128, num_timesteps=1000):
        super().__init__()
        self.num_timesteps = num_timesteps
        self.in_channels = in_channels
        
        # TODO 1: 实现U-Net denoising model
        # 提示: 使用编码器-解码器架构，添加跳跃连接
        self.denoising_model = self._build_unet(in_channels, hidden_dim)
        
        # 预计算噪声调度（beta）
        # TODO 2: 理解噪声调度的作用
        self.register_buffer('betas', self._get_betas(num_timesteps))
        self.register_buffer('alphas', 1 - self.betas)
        self.register_buffer('alphas_cumprod', torch.cumprod(self.alphas, dim=0))
    
    def _build_unet(self, in_channels, hidden_dim):
        # TODO: 实现U-Net架构
        return nn.Sequential(
            nn.Conv2d(in_channels, hidden_dim, 3, padding=1),
            nn.ReLU(),
            # ... 更多层
        )
    
    def _get_betas(self, num_timesteps):
        # TODO: 实现beta调度（线性、余弦等）
        return torch.linspace(0.0001, 0.02, num_timesteps)
    
    def q_sample(self, x_start, t, noise=None):
        """
        前向扩散过程：q(x_t | x_0)
        
        Args:
            x_start: 原始图像
            t: 时间步
            noise: 噪声（如果为None则随机生成）
        
        Returns:
            加噪后的图像
        """
        # TODO 3: 实现前向扩散公式
        # 提示: x_t = sqrt(alpha_bar_t) * x_0 + sqrt(1 - alpha_bar_t) * epsilon
        if noise is None:
            noise = torch.randn_like(x_start)
        
        alpha_bar_t = self.alphas_cumprod[t].view(-1, 1, 1, 1)
        sqrt_alpha_bar = torch.sqrt(alpha_bar_t)
        sqrt_one_minus_alpha_bar = torch.sqrt(1 - alpha_bar_t)
        
        return sqrt_alpha_bar * x_start + sqrt_one_minus_alpha_bar * noise
    
    def p_sample(self, x_t, t):
        """
        反向去噪过程：p(x_{t-1} | x_t)
        
        Args:
            x_t: 当前噪声图像
            t: 时间步
        
        Returns:
            去噪后的图像
        """
        # TODO 4: 实现反向去噪过程
        # 提示: 预测噪声，然后使用公式计算x_{t-1}
        with torch.no_grad():
            predicted_noise = self.denoising_model(x_t, t)
            # ... 实现去噪步骤
            return x_t
    
    def forward(self, x):
        # TODO 5: 实现训练循环
        # 1. 随机采样时间步t
        # 2. 添加噪声得到x_t
        # 3. 预测噪声
        # 4. 计算损失
        pass

# 测试代码
if __name__ == '__main__':
    model = DDPM()
    x = torch.randn(2, 3, 32, 32)
    t = torch.randint(0, 1000, (2,))
    
    # 测试前向扩散
    x_t = model.q_sample(x, t)
    print(f'✅ q_sample测试通过: {x_t.shape}')
    
    # 测试反向去噪
    x_prev = model.p_sample(x_t, t)
    print(f'✅ p_sample测试通过: {x_prev.shape}')
