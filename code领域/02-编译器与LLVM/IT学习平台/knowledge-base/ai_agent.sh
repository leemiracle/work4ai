#!/bin/bash
# AI智能体系统启动脚本

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
NC='\033[0m' # No Color

# 打印带颜色的标题
print_title() {
    echo -e "${CYAN}╔─────────────────────────────────────────────────────────────────╗${NC}"
    echo -e "${CYAN}║${NC}             ${GREEN}AI智能体系统${NC}                          ${CYAN}║${NC}"
    echo -e "${CYAN}╚─────────────────────────────────────────────────────────────────╝${NC}"
    echo ""
}

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

# 检查依赖
check_dependencies() {
    print_info "【检查依赖】"
    
    # 检查Python
    if ! command -v python3 &> /dev/null; then
        print_error "错误: Python3 未安装"
        exit 1
    fi
    
    print_success "✓ Python3 已安装: $(python3 --version)"
    
    # 检查API密钥
    if [ -z "$GLM_API_KEY" ]; then
        print_warning "警告: GLM_API_KEY 环境变量未设置"
        echo ""
        echo "设置方法:"
        echo "  export GLM_API_KEY='your-api-key-here'"
        echo ""
        read -p "是否现在设置? (y/n): " set_key
        if [ "$set_key" == "y" ]; then
            read -p "请输入API密钥: " api_key
            export GLM_API_KEY="$api_key"
            echo "  export GLM_API_KEY=\"$api_key\" >> ~/.bashrc"
            print_success "✓ GLM_API_KEY 已设置"
        fi
    else
        print_success "✓ GLM_API_KEY 已配置"
    fi
    
    echo ""
}

# 显示主菜单
show_main_menu() {
    echo ""
    print_title
    echo "  ${MAGENTA}主菜单${NC}"
    echo "  ┌───────────────────────────────────────────────┐"
    echo "  │ 1. ${GREEN}交互式模式${NC}         ${MAGENTA}│${NC}"
    echo "  │ 2. ${BLUE}批处理模式${NC}            ${MAGENTA}│${NC}"
    echo "  │ 3. ${CYAN}查看系统状态${NC}          ${MAGENTA}│${NC}"
    echo "  │ 4. ${YELLOW}配置向导${NC}             ${MAGENTA}│${NC}"
    echo "  │ 5. ${RED}退出${NC}                    ${MAGENTA}│${NC}"
    echo "  └───────────────────────────────────────────────┘"
    echo ""
}

# 交互式模式
interactive_mode() {
    print_info "【交互式模式】"
    echo ""
    cd ai-agent
    python3 main.py --interactive
}

# 批处理模式
batch_mode() {
    print_info "【批处理模式】"
    echo ""
    
    echo "请提供任务文件路径 (JSON格式):"
    read -p "> " tasks_file
    
    cd ai-agent
    python3 main.py --batch "$tasks_file"
}

# 查看系统状态
show_status() {
    print_info "【系统状态】"
    echo ""
    cd ai-agent
    python3 main.py --status
}

# 显示所有模型
show_models() {
    print_info "【GLM模型】"
    echo ""
    cd ai-agent
    python3 ../ai-tools/utils/glm_models.py
}

# 配置向导
config_wizard() {
    print_info "【配置向导】"
    echo ""
    
    echo "1. API配置"
    print "   - 配置GLM API密钥"
    print "   - 测试API连接"
    
    echo ""
    echo "2. 智能体配置"
    print "   - 配置智能体数量"
    print "   - 配置工作流"
    print "   - 配置记忆系统"
    
    echo ""
    echo "是否现在配置API密钥? (y/n): "
    read -p " config_api
    
    if [ "$config_api" == "y" ]; then
        echo ""
        print "请输入GLM API密钥:"
        read -s api_key
        
        echo "export GLM_API_KEY=\"$api_key\"" >> ~/.bashrc
        export GLM_API_KEY="$api_key"
        
        print_success "✓ API密钥已配置并保存到 ~/.bashrc"
        echo ""
        echo "请执行: source ~/.bashrc 使配置生效"
    fi
}

# 显示系统架构
show_architecture() {
    print_info "【系统架构】"
    echo ""
    
    echo "┌─────────────────────────────────────────────────────────────┐"
    echo "│ ${GREEN}用户接口${NC}                                     │"
    echo "├─────────────────────────────────────────────────────────────┤"
    echo "│  ${BLUE}协调器${NC} (${CYAN}Orchestrator${NC})                 │"
    echo "├─────────────────────────────────────────────────────────────┤"
    echo "│                                                     │"
    echo "│  ┌─────────┬─────────┬─────────┬─────────┐      │"
    echo "│  │${GREEN}训练器${NC}  │${BLUE}分析器${NC}  │${YELLOW}研究者${NC}│${MAGENTA}规划器${NC}│${RED}执行器${NC}│      │"
    echo "│  └─────────┴─────────┴─────────┴─────────┘      │"
    echo "└─────────────────────────────────────────────────────────────┘"
    echo ""
    
    echo "智能体功能:"
    echo "  ${GREEN}训练器${NC}: 负责每日认知训练和能力提升"
    echo "  ${BLUE}分析器${NC}: 负责深度分析和洞察生成"
    echo "  ${YELLOW}研究者${NC}: 负责信息搜索和资料收集"
    echo "  ${MAGENTA}规划器${NC}: 负责任务分解和执行计划"
    echo "  ${RED}执行器${NC}: 负责具体任务执行"
    echo ""
}

# 显示工作流
show_workflows() {
    print_info "【工作流】"
    echo ""
    
    echo "工作流1: 能力提升"
    echo "  步骤1: 分析当前能力水平 (analyzer)"
    echo "  步骤2: 创建训练计划 (planner)"
    echo "  步骤3: 执行训练 (executor)"
    echo "  步骤4: 研究相关资料 (researcher)"
    echo ""
    
    echo "工作流2: 问题解决"
    echo "  步骤1: 深度分析问题 (analyzer)"
    echo "  步骤2: 制定解决方案 (planner)"
    echo "  步骤3: 执行解决方案 (executor)"
    echo "  步骤4: 研究相关案例 (researcher)"
    echo ""
    
    echo "工作流3: 自定义"
    echo "  用户自定义多智能体协作工作流"
    echo ""
}

# 显示快速开始
show_quickstart() {
    print_info "【快速开始】"
    echo ""
    
    echo "第1步: 配置API密钥"
    echo "  $ export GLM_API_KEY='your-api-key-here'"
    echo ""
    
    echo "第2步: 运行交互式模式"
    echo "  $ ./ai_agent.sh"
    echo "  选择 '1. 交互式模式'"
    echo ""
    
    echo "第3步: 选择工作流"
    echo "  选择 '1. 能力提升' 或 '2. 问题解决'"
    echo ""
    
    echo "第4步: 与智能体交互"
    echo "  智能体会引导你完成任务"
    echo ""
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
    print_success "🚀 欢迎来到 AI智能体系统！"
    echo ""
    print "这是一个由多个AI智能体组成的协作系统，"
    echo "帮助你系统化提升个人能力，从执行者转型为判断者。"
    echo ""
    print "核心特性:"
    echo "  ✓ 6个专业智能体 (训练器、分析器、研究者、规划器、执行器、协调器)"
    echo "  ✓ 多智能体协作工作流"
    echo "  ✓ 60+个GLM模型支持"
    echo "  ✓ 记忆系统和上下文管理"
    echo "  ✓ 自动任务分解和执行"
    echo ""
    
    # 检查依赖
    check_dependencies
    
    # 主循环
    while true; do
        show_main_menu
        read -p "请选择 (1-5): " choice
        
        case $choice in
            1)
                    interactive_mode
                    ;;
            2)
                    batch_mode
                    ;;
            3)
                    show_status
                    ;;
            4)
                    echo ""
                    echo "选择配置选项:"
                    echo "  1. 显示系统架构"
                    echo "  2. 显示工作流"
                    echo   3. 显示快速开始"
                    echo "  4. 配置API密钥"
                    echo "  5. 返回主菜单"
                    echo ""
                    
                    read -p "请选择 (1-5): " sub_choice
                    
                    case $sub_choice in
                        1)
                            show_architecture
                            ;;
                        2)
                            show_workflows
                            ;;
                        3)
                            show_quickstart
                            ;;
                        4)
                            config_wizard
                            ;;
                        5)
                            ;;
                        *)
                            print_error "无效选择"
                            ;;
                    esac
                    ;;
            5)
                    print_success "再见！祝你能力提升之旅顺利！"
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