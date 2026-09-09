"""
配置文件 - LLM聊天机器人
"""

class Config:
    """项目配置"""
    
    # 模型配置
    MODEL_NAME = "LLM聊天机器人"
    
    # 训练配置
    BATCH_SIZE = 32
    LEARNING_RATE = 1e-4
    NUM_EPOCHS = 10
    
    # 路径配置
    DATA_DIR = "data"
    MODEL_DIR = "models"
    LOG_DIR = "logs"
    CHECKPOINT_DIR = "checkpoints"
    
    # 其他配置
    DEVICE = "cuda"  # 或 "cpu"
    RANDOM_SEED = 42


# TODO: 根据项目需求添加更多配置项
