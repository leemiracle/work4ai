#!/bin/bash
# AI增强个人能力系统 - 主启动脚本

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印带颜色的文本
print_info() {
    echo -e "${BLUE}$1${NC}"
}

print_success() {
    echo -e "${GREEN}$1${NC}"
}

print_warning() {
    echo -e "${YELLOW}$1${NC}"
}

print_error() {
    echo -e "${RED}$1${NC}"
}

# 显示菜单
show_menu() {
    echo ""
    echo "========================================"
    echo "  AI增强个人能力系统"
    echo "========================================"
    echo ""
    echo "  1. 快速开始"
    echo "  2. 每日认知训练"
    echo "  3. 问题定义辅助"
    echo "  4. 能力评估"
    echo "  5. 查看所有模型"
    echo "  6. 系统状态"
    echo "  7. 退出"
    echo ""
    echo "========================================"
}

# 快速开始
quick_start() {
    print_info "【快速开始】"
    echo ""
    
    # 检查API密钥
    if [ -z "$GLM_API_KEY" ]; then
        print_warning "未设置 GLM_API_KEY 环境变量"
        echo ""
        echo "请先设置API密钥："
        echo "  export GLM_API_KEY='your-api-key-here'"
        echo ""
        return
    fi
    
    print_success "✓ API密钥已配置"
    echo ""
    
    # 显示文档路径
    print_info "核心文档："
    echo "  1. README.md - AI增强系统总览"
    echo "  2. QUICKSTART.md - 快速开始指南"
    echo "  3. AI-ENHANCED-SYSTEM.md - AI工作流详解"
    echo ""
    
    print_info "推荐阅读顺序："
    echo "  第1天: README.md → QUICKSTART.md"
    echo "  第2天: AI-ENHANCED-SYSTEM.md"
    echo "  第3天: capability-metrics/problem-definition.md"
    echo ""
    
    print_info "立即开始："
    echo "  每日训练: python ai-tools/workflows/daily_cognitive_trainer.py --interactive"
    echo "  能力评估: python ai-tools/workflows/capability_assessment.py --list"
    echo ""
}

# 每日认知训练
daily_training() {
    print_info "【每日认知训练】"
    echo ""
    
    # 检查API密钥
    if [ -z "$GLM_API_KEY" ]; then
        print_error "错误: 未设置 GLM_API_KEY 环境变量"
        echo "请先设置: export GLM_API_KEY='your-api-key-here'"
        return
    fi
    
    print_info "运行每日认知训练工具..."
    echo ""
    
    # 检查Python环境
    if ! command -v python3 &> /dev/null; then
        print_error "错误: 未找到 python3"
        return
    fi
    
    # 运行训练工具
    python3 ai-tools/workflows/daily_cognitive_trainer.py --interactive
}

# 问题定义辅助
problem_definition() {
    print_info "【问题定义辅助】"
    echo ""
    
    # 检查API密钥
    if [ -z "$GLM_API_KEY" ]; then
        print_error "错误: 未设置 GLM_API_KEY 环境变量"
        echo "请先设置: export GLM_API_KEY='your-api-key-here'"
        return
    fi
    
    print_info "运行问题定义辅助工具..."
    echo ""
    
    # 检查Python环境
    if ! command -v python3 &> /dev/null; then
        print_error "错误: 未找到 python3"
        return
    fi
    
    # 运行问题定义工具
    python3 ai-tools/workflows/problem_definition_assistant.py --interactive
}

# 能力评估
capability_assessment() {
    print_info "【能力评估】"
    echo ""
    
    # 检查API密钥
    if [ -z "$GLM_API_KEY" ]; then
        print_warning "未设置 GLM_API_KEY 环境变量（某些功能可能不可用）"
        echo ""
    fi
    
    print_info "列出所有能力..."
    echo ""
    
    # 检查Python环境
    if ! command -v python3 &> /dev/null; then
        print_error "错误: 未找到 python3"
        return
    fi
    
    # 运行能力评估工具
    python3 ai-tools/workflows/capability_assessment.py --list
    echo ""
    
    print_info "交互式评估:"
    echo "  python3 ai-tools/workflows/capability_assessment.py --interactive"
    echo ""
}

# 查看所有模型
show_models() {
    print_info "【GLM模型清单】"
    echo ""
    
    # 检查Python环境
    if ! command -v python3 &> /dev/null; then
        print_error "错误: 未找到 python3"
        return
    fi
    
    # 运行模型管理器
    python3 ai-tools/utils/glm_models.py
}

# 系统状态
system_status() {
    print_info "【系统状态】"
    echo ""
    
    # 检查目录结构
    print_info "目录结构:"
    echo ""
    
    dirs=(
        "ai-tools"
        "capability-metrics"
        "mental-models"
        "practices"
        "learning-log"
        "cases"
        "reviews"
    )
    
    for dir in "${dirs[@]}"; do
        if [ -d "$dir" ]; then
            count=$(find "$dir" -name "*.md" -o -name "*.py" 2>/dev/null | wc -l)
            print_success "  ✓ $dir ($count 文件)"
        else
            print_warning "  ✗ $dir (不存在)"
        fi
    done
    
    echo ""
    
    # 统计文件
    print_info "文件统计:"
    echo ""
    
    total_md=$(find . -name "*.md" 2>/dev/null | wc -l)
    total_py=$(find . -name "*.py" 2>/dev/null | wc -l)
    
    echo "  Markdown 文件: $total_md"
    echo "  Python 文件: $total_py"
    echo "  总计: $((total_md + total_py)) 个文件"
    echo ""
    
    # 检查API密钥
    print_info "API配置:"
    echo ""
    
    if [ -n "$GLM_API_KEY" ]; then
        print_success "  ✓ GLM_API_KEY 已配置"
    else
        print_warning "  ✗ GLM_API_KEY 未配置"
        echo ""
        echo "  设置方法:"
        echo "    export GLM_API_KEY='your-api-key-here'"
        echo ""
    fi
}

# 主循环
main() {
    # 检查是否在knowledge-base目录
    if [ ! -f "README.md" ]; then
        print_error "错误: 请在 knowledge-base 目录下运行此脚本"
        exit 1
    fi
    
    # 显示欢迎信息
    echo ""
    print_success "欢迎来到 AI增强个人能力系统！"
    echo ""
    echo "本项目整合了24个核心能力指标、57+个思维模型、"
    echo "30天认知训练计划和60+个GLM AI模型，"
    echo "帮助你从执行者转型为判断者。"
    echo ""
    
    # 主循环
    while true; do
        show_menu
        read -p "请选择 (1-7): " choice
        
        case $choice in
            1)
                quick_start
                ;;
            2)
                daily_training
                ;;
            3)
                problem_definition
                ;;
            4)
                capability_assessment
                ;;
            5)
                show_models
                ;;
            6)
                system_status
                ;;
            7)
                print_info "再见！祝你能力提升之旅顺利！"
                exit 0
                ;;
            *)
                print_error "无效选择，请重新输入"
                ;;
        esac
        
        echo ""
        read -p "按回车继续..."
    done
}

# 运行主函数
main "$@"