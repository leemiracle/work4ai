- 神经网络：卷积
https://cs231n.github.io/convolutional-networks/
- 代码：https://github.com/pytorch/examples/blob/main/mnist/main.py

from torch.optim.lr_scheduler import StepLR【调整优化器参数】

from torchvision import datasets, transforms【transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize((0.1307,), (0.3081,))
        ]) 数据预处理】