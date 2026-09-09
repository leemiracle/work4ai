#!/bin/bash
# AI Agent系统启动脚本

echo "========================================"
echo "    AI智能体系统"
echo "========================================"
echo ""
echo "这是一个由多个AI智能体组成的协作系统"
echo "帮助你系统化提升个人能力，从执行者转型为判断者"
echo ""

# 检查Python
if ! command -v python3 &> /dev/null; then
    echo "错误: Python3 未安装"
    exit 1
fi

echo "✓ Python3 已安装: $(python3 --version)"
echo ""

echo "可用命令:"
echo "  ./ai_agent/main.py --interactive  # 交互式模式"
echo "  ./ai_agent/main.py --status       # 查看系统状态"
echo "  ./ai_agent/main.py --models       # 查看所有模型"
echo ""

# 检查API密钥
if [ -z "$GLM_API_KEY" ]; then
    echo "⚠️  警告: GLM_API_KEY 环境变量未设置"
    echo ""
    echo "设置方法:"
    echo "  export GLM_API_KEY='your-api-key-here'"
    echo ""
    read -p "是否现在设置? (y/n): " set_key
    if [ "$set_key" == "y" ]; then
        read -p "请输入API密钥: " api_key
        export GLM_API_KEY="$api_key"
        echo "export GLM_API_KEY=\"$api_key\"" >> ~/.bashrc
        echo "✓ GLM_API_KEY 已配置并保存"
        echo ""
        echo "请执行: source ~/.bashrc 使配置生效"
    fi
else
    echo "✓ GLM_API_KEY 已配置"
fi

echo ""
echo "开始使用:"
echo "  cd ai-agent"
echo "  python3 main.py --interactive"
echo ""

echo "或者使用启动脚本:"
echo "  ./ai_agent.sh"
echo ""