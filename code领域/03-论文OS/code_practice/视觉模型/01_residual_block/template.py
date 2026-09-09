import torch
import torch.nn as nn

class ResidualBlock(nn.Module):
    """
    残差块实现
    
    学习任务:
    1. 理解残差连接的作用
    2. 实现标准残差块
    3. 实现带bottleneck的残差块
    """
    
    def __init__(self, in_channels, out_channels, stride=1):
        super().__init__()
        self.in_channels = in_channels
        self.out_channels = out_channels
        self.stride = stride
        
        # TODO 1: 实现标准残差块
        # 提示: 两个3x3卷积层，每个后面接BatchNorm和ReLU
        self.conv1 = nn.Conv2d(in_channels, out_channels, 3, stride=stride, padding=1, bias=False)
        self.bn1 = nn.BatchNorm2d(out_channels)
        self.relu = nn.ReLU(inplace=True)
        self.conv2 = nn.Conv2d(out_channels, out_channels, 3, stride=1, padding=1, bias=False)
        self.bn2 = nn.BatchNorm2d(out_channels)
        
        # TODO 2: 理解shortcut的作用
        # 提示: 当输入输出维度不同时，需要通过1x1卷积调整
        self.shortcut = nn.Sequential()
        if stride != 1 or in_channels != out_channels:
            self.shortcut = nn.Sequential(
                nn.Conv2d(in_channels, out_channels, 1, stride=stride, bias=False),
                nn.BatchNorm2d(out_channels)
            )
    
    def forward(self, x):
        """
        前向传播
        
        Args:
            x: 输入张量 [batch_size, in_channels, H, W]
        
        Returns:
            输出张量 [batch_size, out_channels, H', W']
        """
        # TODO 3: 实现残差连接
        # 提示: F(x) + x，其中F是残差函数
        identity = x
        
        out = self.conv1(x)
        out = self.bn1(out)
        out = self.relu(out)
        
        out = self.conv2(out)
        out = self.bn2(out)
        
        # 添加残差连接
        out += self.shortcut(identity)
        out = self.relu(out)
        
        return out

class BottleneckBlock(nn.Module):
    """
    Bottleneck残差块（用于深层网络）
    
    优点: 减少参数数量，降低计算量
    """
    
    def __init__(self, in_channels, out_channels, stride=1, expansion=4):
        super().__init__()
        hidden_channels = out_channels // expansion
        
        # TODO 4: 实现Bottleneck结构
        # 1x1 -> 3x3 -> 1x1 卷积
        self.conv1 = nn.Conv2d(in_channels, hidden_channels, 1, bias=False)
        self.bn1 = nn.BatchNorm2d(hidden_channels)
        self.conv2 = nn.Conv2d(hidden_channels, hidden_channels, 3, stride=stride, padding=1, bias=False)
        self.bn2 = nn.BatchNorm2d(hidden_channels)
        self.conv3 = nn.Conv2d(hidden_channels, out_channels, 1, bias=False)
        self.bn3 = nn.BatchNorm2d(out_channels)
        
        self.relu = nn.ReLU(inplace=True)
        
        # TODO 5: 理解expansion参数的作用
        # 提示: Bottleneck通常会扩展通道数
        self.shortcut = nn.Sequential()
        if stride != 1 or in_channels != out_channels:
            self.shortcut = nn.Sequential(
                nn.Conv2d(in_channels, out_channels, 1, stride=stride, bias=False),
                nn.BatchNorm2d(out_channels)
            )
    
    def forward(self, x):
        identity = x
        
        out = self.conv1(x)
        out = self.bn1(out)
        out = self.relu(out)
        
        out = self.conv2(out)
        out = self.bn2(out)
        out = self.relu(out)
        
        out = self.conv3(out)
        out = self.bn3(out)
        
        out += self.shortcut(identity)
        out = self.relu(out)
        
        return out

# 测试代码
if __name__ == '__main__':
    # 测试标准残差块
    x = torch.randn(2, 64, 32, 32)
    block = ResidualBlock(64, 128, stride=2)
    out = block(x)
    print(f'✅ ResidualBlock测试通过: {x.shape} -> {out.shape}')
    
    # 测试Bottleneck
    bottleneck = BottleneckBlock(256, 512, stride=2)
    out2 = bottleneck(torch.randn(2, 256, 32, 32))
    print(f'✅ BottleneckBlock测试通过: {out2.shape}')
