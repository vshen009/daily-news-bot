#!/bin/bash
# Git 工作流程辅助脚本 - 测试版本
# 使用方法：source git-workflow-test.sh
# 与原版本区别：运行 test_e2e.py 而不是 main.py

# 颜色定义
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 打印函数
print_info() {
    echo -e "${BLUE}➜ $1${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

# 1. 开始新功能（feature分支）
new_feature() {
    if [ -z "$1" ]; then
        print_error "请提供功能描述"
        echo "使用方法: new_feature <功能描述>"
        echo "示例: new_feature 添加用户登录"
        return 1
    fi

    print_info "开始新功能: $1"

    # 确保在main分支
    current_branch=$(git branch --show-current)
    if [ "$current_branch" != "main" ]; then
        print_warning "当前不在main分支，切换到main..."
        git checkout main
    fi

    # 更新main
    print_info "更新main分支..."
    git pull origin main

    # 创建feature分支
    branch_name="feature/$(echo $1 | tr ' /' '_' | tr '[:upper:]' '[:lower:]')"
    print_info "创建feature分支: $branch_name"
    git checkout -b $branch_name

    print_success "✨ feature分支已创建: $branch_name"
    print_info "现在可以开始开发了！"
}

# 2. 开始Bug修复（fix分支）
new_fix() {
    if [ -z "$1" ]; then
        print_error "请提供Bug描述"
        echo "使用方法: new_fix <Bug描述>"
        echo "示例: new_fix 登录超时"
        return 1
    fi

    print_info "开始修复Bug: $1"

    current_branch=$(git branch --show-current)
    if [ "$current_branch" != "main" ]; then
        print_warning "当前不在main分支，切换到main..."
        git checkout main
    fi

    print_info "更新main分支..."
    git pull origin main

    branch_name="fix/$(echo $1 | tr ' /' '_' | tr '[:upper:]' '[:lower:]')"
    print_info "创建fix分支: $branch_name"
    git checkout -b $branch_name

    print_success "🐛 fix分支已创建: $branch_name"
    print_info "现在可以修复Bug了！"
}

# 3. 提交改动
git_commit() {
    if [ -z "$1" ]; then
        print_error "请提供commit message"
        echo "使用方法: git_commit <提交信息>"
        echo "示例: git_commit ✨ 添加用户登录功能"
        return 1
    fi

    print_info "提交改动: $1"
    git add .
    git commit -m "$1"
    print_success "已提交"
}

# 4. 运行端到端测试
run_test() {
    print_info "运行端到端测试 (test_e2e.py)..."

    # 检查是否在 news_bot 目录
    if [ -f "test_e2e.py" ]; then
        # 已经在 news_bot 目录
        python3 test_e2e.py
    elif [ -f "news_bot/test_e2e.py" ]; then
        # 在项目根目录
        cd news_bot
        python3 test_e2e.py
        cd ..
    else
        print_error "找不到 test_e2e.py 文件"
        print_info "请确保在项目根目录或 news_bot 目录下运行"
        return 1
    fi

    if [ $? -eq 0 ]; then
        print_success "✅ 端到端测试通过"
    else
        print_error "❌ 端到端测试失败"
        return 1
    fi
}

# 5. 提交并测试（合并操作）
commit_and_test() {
    if [ -z "$1" ]; then
        print_error "请提供commit message"
        echo "使用方法: commit_and_test <提交信息>"
        echo "示例: commit_and_test '✨ 添加用户登录功能'"
        return 1
    fi

    print_info "提交改动: $1"
    git add .
    git commit -m "$1"
    print_success "已提交"

    print_info "运行端到端测试..."
    run_test
}

# 6. 推送并创建PR
create_pr() {
    current_branch=$(git branch --show-current)

    if [ "$current_branch" = "main" ]; then
        print_error "不能在main分支创建PR！"
        print_info "请先创建feature分支"
        return 1
    fi

    print_info "推送分支: $current_branch"
    git push origin $current_branch

    if [ -z "$1" ]; then
        print_warning "未提供PR标题，使用分支名"
        title=$(echo $current_branch | sed 's/^[feature|fix|hotfix]\///' | tr '_' ' ')
    else
        title="$1"
    fi

    print_info "创建PR: $title"
    gh pr create --title "$title" --body "通过自动化脚本创建的PR

🧪 测试方式：运行 test_e2e.py 进行端到端测试"

    print_success "✨ PR已创建"
}

# 7. 合并PR
merge_pr() {
    current_branch=$(git branch --show-current)

    if [ "$current_branch" != "main" ]; then
        print_warning "当前不在main分支"
        read -p "是否切换到main分支？(y/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            git checkout main
        else
            print_info "取消操作"
            return 1
        fi
    fi

    print_info "查看当前PR列表..."
    gh pr list

    read -p "请输入要合并的PR编号: " pr_number

    if [ -z "$pr_number" ]; then
        print_error "未输入PR编号"
        return 1
    fi

    print_info "合并PR #$pr_number..."
    gh pr merge $pr_number --squash --delete-branch

    print_success "✅ PR已合并"
    print_info "更新本地main分支..."
    git pull origin main
}

# 8. 查看工作状态
git_status() {
    echo -e "${BLUE}=== Git 工作状态 ===${NC}"
    echo ""
    echo -e "${GREEN}当前分支:${NC} $(git branch --show-current)"
    echo -e "${GREEN}未提交的改动:${NC}"
    git status --short
    echo ""
    echo -e "${GREEN}最近的提交:${NC}"
    git log --oneline -3
    echo ""
    echo -e "${GREEN}未推送的提交:${NC}"
    git log origin/main..HEAD --oneline 2>/dev/null || echo "无"
    echo ""
}

# 9. 快速完成一个功能（从创建到合并）
complete_feature() {
    if [ -z "$1" ]; then
        print_error "请提供功能描述"
        echo "使用方法: complete_feature <功能描述> [PR标题]"
        echo "示例: complete_feature 添加用户登录 '实现用户登录功能'"
        return 1
    fi

    print_info "=== 完整功能开发流程（测试版）==="
    print_info "功能描述: $1"

    # 1. 创建分支
    new_feature "$1"

    # 2. 提示用户进行开发
    echo ""
    print_warning "请进行代码修改..."
    read -p "修改完成后按回车继续..."

    # 3. 提交
    echo ""
    read -p "请输入提交信息: " commit_msg
    git_commit "${commit_msg:-✨ $1}"

    # 4. 运行测试
    echo ""
    print_info "运行端到端测试..."
    run_test

    if [ $? -ne 0 ]; then
        print_error "测试失败，请修复后重新提交"
        return 1
    fi

    # 5. 推送并创建PR
    echo ""
    pr_title="${2:-$(echo $1 | tr '_' ' ')}"
    create_pr "$pr_title"

    # 6. 提示合并
    echo ""
    print_warning "请在GitHub上审核PR，然后运行 merge_pr 合并"
}

# 10. 检查是否在main分支
check_main_branch() {
    current_branch=$(git branch --show-current)
    if [ "$current_branch" = "main" ]; then
        print_warning "⚠️  您当前在main分支！"
        print_info "如果需要修改代码，请先创建feature分支"
        echo ""
        read -p "是否创建新的feature分支？(y/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            read -p "请输入功能描述: " feature_desc
            new_feature "$feature_desc"
        fi
    else
        print_success "✓ 在feature分支: $current_branch"
    fi
}

# 导出函数
export -f new_feature
export -f new_fix
export -f git_commit
export -f run_test
export -f commit_and_test
export -f create_pr
export -f merge_pr
export -f git_status
export -f complete_feature
export -f check_main_branch

# 使用提示
echo ""
print_success "Git 工作流程辅助函数已加载（测试版本）！"
echo ""
print_info "可用命令:"
echo "  new_feature <描述>    - 创建新功能分支"
echo "  new_fix <描述>        - 创建Bug修复分支"
echo "  git_commit <信息>     - 提交改动"
echo "  run_test              - 运行端到端测试 (test_e2e.py)"
echo "  commit_and_test <信息> - 提交并运行测试"
echo "  create_pr [标题]      - 推送并创建PR"
echo "  merge_pr              - 合并PR"
echo "  git_status            - 查看工作状态"
echo "  check_main_branch     - 检查是否在main分支"
echo "  complete_feature <描述> - 完整功能流程（包含测试）"
echo ""
print_info "使用示例:"
echo "  new_feature 添加用户登录"
echo "  ... 进行开发 ..."
echo "  commit_and_test '✨ 实现登录功能'"
echo "  create_pr '用户登录功能'"
echo "  ... 在GitHub审核 ..."
echo "  merge_pr"
echo ""
print_info "🧪 与原版本区别："
echo "  - 使用 test_e2e.py 替代 main.py 进行测试"
echo "  - 新增 run_test 命令单独运行测试"
echo "  - 新增 commit_and_test 命令提交后自动测试"
echo "  - complete_feature 流程中包含测试步骤"
echo ""
