# Git 工作流程规范

> 本项目遵循统一的 Git 工作流程规范

---

## 📍 完整规范文档

**详细的 Git 工作流程规范请查看项目根目录：**
👉 **[../../CLAUDE.md](../../CLAUDE.md#git工作流程---避免错误的正确方法)**

根目录包含：
- ✅ 完整的工作流程规范
- ✅ 常见错误原因分析
- ✅ 常见问题解决方法
- ✅ 提交前检查清单

---

## 🚀 快速开始

### 1. 创建新分支

```bash
# 确保在最新的 main 分支
git checkout main
git pull origin main

# 创建 feature 分支
git checkout -b feature/your-feature
```

### 2. 提交改动

```bash
# 添加修改的文件
git add .

# 提交（使用 emoji 前缀）
git commit -m "✨ Description of changes"

# 推送到远程
git push origin feature/your-feature
```

### 3. 创建 PR

```bash
# 使用 GitHub CLI
gh pr create --title "Title" --body "Description"

# 或通过网页创建
# https://github.com/vshen009/claude-code-projects/compare/main...feature/your-feature
```

---

## ⚠️ 核心原则（最重要）

### ❌ 绝对禁止

1. **永远不要直接修改 main 分支**
   - 所有改动都要通过 feature 分支
   - 通过 PR 合并到 main

2. **永远不要 force-push 到 main**
   - 会丢失历史记录
   - 违反分支保护规则

### ✅ 正确做法

1. 所有改动通过 feature 分支
2. 通过 PR 合并到 main
3. 使用 merge（不用 rebase）

---

## 🎯 分支命名规范

```bash
feature/新增功能描述    # 新功能
fix/修复问题描述        # Bug修复
hotfix/紧急修复描述     # 紧急修复
release/vX.X.X         # 版本发布
docs/文档更新          # 文档修改
refactor/重构描述      # 代码重构
```

---

## 📝 提交信息规范（Emoji 前缀）

```bash
✨ feat:     新功能
🐛 fix:      修复bug
📝 docs:     文档更新
♻️ refactor: 代码重构
🎨 style:    代码格式调整
⚡ perf:     性能优化
✅ test:     测试相关
🚀 release:  发布版本
🔧 chore:    构建/工具链更新
```

**示例：**
```bash
git commit -m "✨ 添加用户登录功能"
git commit -m "🐛 修复分红计算错误"
git commit -m "📝 更新 API 文档"
```

---

## 🔧 常见问题速查

| 问题 | 解决方法 |
|------|---------|
| `refspec main matches more than one` | `git tag -d main` |
| 分支保护规则冲突 | 使用 PR 合并 |
| rebase 冲突 | `git rebase --abort` |
| 远程有新提交 | `git pull origin main` |

---

## 🔄 两台电脑协作提示

1. **开始工作前先 pull**
   ```bash
   git pull origin main
   ```

2. **不要在不同电脑上使用相同分支名**
   - 电脑 A: `feature/add-dashboard`
   - 电脑 B: `feature/add-mobile-view`

3. **定期同步 main 分支**
   ```bash
   git checkout main
   git pull origin main
   ```

---

## 📚 相关资源

- **完整规范**: [../../CLAUDE.md](../../CLAUDE.md)
- **使用记录**: [../../memory.md](../../memory.md)
- [GitHub Flow](https://docs.github.com/en/get-started/quickstart/github-flow)

---

**最后更新**: 2026年1月25日
**维护者**: Vincent
**适用项目**: 定制每日财经新闻
