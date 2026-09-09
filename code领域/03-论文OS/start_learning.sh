#!/bin/bash

# Paper-OS 学习启动脚本

echo "=========================================="
echo "Paper-OS 学习系统"
echo "=========================================="
echo ""

# 获取用户输入
echo "请选择学习路径："
echo "1) 初学者路径 (4-6周)"
echo "2) 中级路径 (8-12周)"
echo "3) 高级路径 (12-16周)"
echo "4) 查看所有路径状态"
echo ""
read -p "请输入选项 (1-4): " choice

PROJECT_ROOT="/home/lwz/learn-os/paper-os"
LEARNING_PATHS_DIR="$PROJECT_ROOT/learning_paths_by_report"

case $choice in
    1)
        echo ""
        echo "你选择了：初学者路径"
        echo "目标：掌握Transformer和ResNet基础"
        echo ""
        cd "$LEARNING_PATHS_DIR/初学者路径" || exit 1
        ;;
    2)
        echo ""
        echo "你选择了：中级路径"
        echo "目标：掌握LLM训练和推理优化"
        echo ""
        cd "$LEARNING_PATHS_DIR/中级路径" || exit 1
        ;;
    3)
        echo ""
        echo "你选择了：高级路径"
        echo "目标：掌握RAG、CoT等高级技术"
        echo ""
        cd "$LEARNING_PATHS_DIR/高级路径" || exit 1
        ;;
    4)
        echo ""
        echo "=========================================="
        echo "学习路径状态"
        echo "=========================================="
        echo ""
        cat "$LEARNING_PATHS_DIR/SUMMARY.md" | head -40
        echo ""
        exit 0
        ;;
    *)
        echo "无效的选项"
        exit 1
        ;;
esac

# 显示当前路径信息
echo ""
echo "=========================================="
echo "当前学习路径: $(pwd | xargs basename)"
echo "=========================================="
echo ""

# 显示目录结构
echo "📁 目录结构："
echo "  📚 papers/      - 论文资源"
echo "  💻 applications/ - 应用项目（符号链接）"
echo "  📝 notes/       - 学习笔记"
echo "  🎯 practice/    - 实践代码"
echo ""

# 显示论文列表
echo "📚 可用论文："
ls -1 papers/*.pdf 2>/dev/null | while read file; do
    echo "  - $(basename "$file")"
done
echo ""

# 显示应用列表
echo "💻 可用应用："
ls -l applications/ 2>/dev/null | grep "^l" | awk '{print "  - " $9 " → " $11}' | sed 's|.*/||'
echo ""

# 提示下一步
echo "=========================================="
echo "下一步建议："
echo "=========================================="
echo "1. 阅读papers/目录中的论文"
echo "2. 查看applications/目录中的应用代码"
echo "3. 在notes/目录中记录学习笔记"
echo "4. 在practice/目录中创建实践项目"
echo ""
echo "查看README.md了解更多信息："
echo "  cat README.md"
echo ""
