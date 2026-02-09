#!/bin/bash

# 每日新闻机器人 - 本地开发调试脚本
# 功能：
# 1. 清空 public 下面的所有 HTML 文件
# 2. 启动临时服务器，调试本地 public 下的页面
# 3. 运行 main.py（只刷新 HTML / 执行全功能 / 运行测试参数）

cd "$(dirname "$0")"

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 清空 public 目录下的 HTML 文件
clear_public_html() {
    echo -e "${YELLOW}🗑️  清空 public 目录下的 HTML 文件...${NC}"
    rm -f public/*.html
    echo -e "${GREEN}✅ 已清空 $(ls public/*.html 2>/dev/null | wc -l) 个 HTML 文件${NC}"
}

# 启动本地服务器
start_local_server() {
    echo -e "${BLUE}🌐 启动本地服务器...${NC}"
    echo -e "${GREEN}✅ 服务器已启动：http://localhost:8080${NC}"
    echo -e "${GREEN}✅ 局域网访问：http://192.168.123.107:8080${NC}"
    echo -e "${YELLOW}按 Ctrl+C 停止服务器${NC}"

    cd public
    python3 -m http.server 8080 --bind 0.0.0.0
    cd ..
}

# 运行 main.py - 只刷新 HTML
run_html_only() {
    echo -e "${BLUE}🔄 只刷新 HTML（不抓取新数据）...${NC}"
    cd news_bot
    python main.py --html-only --days 30
    cd ..
    echo -e "${GREEN}✅ HTML 刷新完成${NC}"
}

# 运行 main.py - 执行全功能
run_full_function() {
    echo -e "${BLUE}📰 执行全功能（抓取新闻并生成 HTML）...${NC}"
    cd news_bot
    python main.py
    cd ..
    echo -e "${GREEN}✅ 全功能执行完成${NC}"
}

# 运行 main.py - 测试参数
run_test_mode() {
    echo -e "${BLUE}🧪 运行测试模式（每个源只抓1条新闻）...${NC}"
    cd news_bot
    python main.py --test
    cd ..
    echo -e "${GREEN}✅ 测试模式完成${NC}"
}

# 显示主菜单
show_menu() {
    echo ""
    echo -e "${GREEN}════════════════════════════════════════${NC}"
    echo -e "${GREEN}   每日新闻机器人 - 本地开发调试菜单${NC}"
    echo -e "${GREEN}════════════════════════════════════════${NC}"
    echo ""
    echo -e "${BLUE}1.${NC} 清空 public 目录下的 HTML 文件"
    echo -e "${BLUE}2.${NC} 启动本地服务器（调试页面）"
    echo -e "${BLUE}3.${NC} 只刷新 HTML（不抓取新数据）"
    echo -e "${BLUE}4.${NC} 执行全功能（抓取新闻并生成 HTML）"
    echo -e "${BLUE}5.${NC} 运行测试模式（每个源只抓1条）"
    echo ""
    echo -e "${YELLOW}0 或 Q${NC} - 退出脚本"
    echo -e "${GREEN}════════════════════════════════════════${NC}"
    echo ""
}

# 主循环
while true; do
    clear
    show_menu
    read -p "请选择功能 [0-5]: " choice

    case $choice in
        1)
            clear_public_html
            read -p "按 Enter 键继续..."
            ;;
        2)
            start_local_server
            read -p "按 Enter 键继续..."
            ;;
        3)
            run_html_only
            read -p "按 Enter 键继续..."
            ;;
        4)
            run_full_function
            read -p "按 Enter 键继续..."
            ;;
        5)
            run_test_mode
            read -p "按 Enter 键继续..."
            ;;
        0|q|Q)
            echo -e "${GREEN}👋 再见！${NC}"
            exit 0
            ;;
        *)
            echo -e "${RED}❌ 无效选择，请重新输入${NC}"
            sleep 1
            ;;
    esac
done
