# User Introduction

---

My name is Vincent, I'm a product manager and I don't know how to code at all.

Vincent is exploring how to use Claude Code, please help him as much as you can.

Vincent prefers to communicate in Chinese.

# Memory

---

memory.md contains my memories of using Claude Code.

You need to write to it.

Every time you start, you must read memory.md in the current folder to check previous records.

Every time there's a major change, you also need to record important information to memory.md.



## 🚨 Git工作流程 - 避免错误的正确方法

### ❌ 常见Git错误原因分析

#### 问题1: main分支引用冲突

```
error: src refspec main matches more than one
error: dst refspec main matches more than one
```

**根本原因**：

- 同时存在名为 `main` 的分支和tag
- Git无法区分引用目标
  **解决方法**：
  
  ```bash
  # 删除本地main tag
  git tag -d main
  # 检查是否还有其他冲突引用
  git show-ref
  ```
  
  #### 问题2: 分支保护规则冲突
  
  ```
  remote: error: GH013: Repository rule violations found for refs/heads/main
- Changes must be made through a pull request
- Cannot force-push to this branch
  ```
  **根本原因**：
- main分支有保护规则
- 必须通过PR合并，不能直接推送
  **正确工作流程**：
  
  ```bash
  # 1. 在新分支工作
  git checkout -b feature/your-feature-name
  # 2. 提交改动
  git add .
  git commit -m "Your commit message"
  # 3. 推送分支
  git push origin feature/your-feature-name
  # 4. 创建PR（通过GitHub CLI或网页）
  gh pr create --title "PR Title" --body "PR Description"
  # 5. 合并PR
  gh pr merge --squash --delete-branch
  ```
  
  #### 问题3: rebase冲突
  
  ```
  error: could not apply xxx
  CONFLICT (modify/delete): xxx
  ```
  
  **根本原因**：
- 本地和远程历史分叉
- 试图rebase时产生冲突
  **解决方法**：
  
  ```bash
  # 中止rebase
  git rebase --abort
  # 或者使用merge方式
  git pull origin main --no-rebase
  ```

---

### ✅ 正确的Git工作流程

#### 场景1: 修改现有功能（小改动）

```bash
# 1. 确保在最新的main分支
git checkout main
git pull origin main
# 2. 创建feature分支
git checkout -b feature/short-description
# 3. 进行修改
# ... 编辑文件 ...
# 4. 提交改动
git add .
git commit -m "✨ Description of changes"
# 5. 推送分支
git push origin feature/short-description
# 6. 创建并合并PR
gh pr create --title "Title" --body "Description"
gh pr merge --squash --delete-branch
```

#### 场景2: 重大更新（新版本Release）

```bash
# 1. 创建release分支
git checkout -b release/v1.7.0
# 2. 进行重大修改
# ... 更新版本号、修改代码等 ...
# 3. 提交所有改动
git add .
git commit -m "🚀 Release v1.7.0 - Major update"
# 4. 推送分支
git push origin release/v1.7.0
# 5. 创建PR详细说明
gh pr create --title "🚀 Release v1.7.0" --body "Detailed release notes"
# 6. 合并前检查清单
# - [ ] 所有文件已提交
# - [ ] 版本号已更新
# - [ ] README已同步更新
# - [ ] 测试通过
# 7. 合并PR
gh pr merge --squash --delete-branch
# 8. 创建GitHub Release
gh release create v1.7.0 --title "v1.7.0" --notes "Release notes"
```

#### 场景3: 紧急hotfix（需要直接修改main）

```bash
# 注意：由于分支保护，还是需要通过PR
# 1. 创建hotfix分支
git checkout -b hotfix/critical-issue
# 2. 快速修复
# ... 修复问题 ...
# 3. 提交并推送
git add .
git commit -m "🐛 Hotfix: Critical issue"
git push origin hotfix/critical-issue
# 4. 加急处理PR
gh pr create --title "🐛 Hotfix" --body "Critical fix"
gh pr merge --squash --delete-branch
```

---

### 🔧 Git常用问题解决速查表

| 错误信息                                 | 原因       | 解决方法                   |
| ------------------------------------ | -------- | ---------------------- |
| `refspec main matches more than one` | 分支和tag同名 | `git tag -d main`      |
| `repository rule violations`         | 分支保护     | 使用PR合并                 |
| `fetch first`                        | 远程有新提交   | `git pull origin main` |
| `could not apply`                    | rebase冲突 | `git rebase --abort`   |
| `Changes not staged for commit`      | 文件未暂存    | `git add .`            |
| `nothing to commit`                  | 无改动      | 检查是否已提交                |

---

### 📋 Git提交前检查清单

#### 每次提交前

- [ ] 确认在正确的分支（feature分支，不是main）
- [ ] 检查`git status`确认改动文件
- [ ] 确认提交信息遵循规范
- [ ] 测试改动是否正常工作
  
  #### 推送前
- [ ] 确认分支名称清晰描述功能
- [ ] 检查是否有敏感信息
- [ ] 确认远程分支存在
  
  #### PR合并前
- [ ] 检查PR描述是否完整
- [ ] 确认没有merge冲突
- [ ] 验证CI/CD是否通过

---

### 🎯 分支命名规范

```
feature/新增功能描述
fix/修复问题描述
hotfix/紧急修复描述
release/vX.X.X
docs/文档更新
refactor/重构描述
```

---

### 🚨 绝对禁止的操作

1. ❌ **永远不要直接修改main分支**
   - 所有改动都要通过feature分支
   - 通过PR合并到main
2. ❌ **永远不要force-push到main**
   - 会丢失历史记录
   - 违反分支保护规则
3. ❌ **不要在tag和分支使用相同名称**
   - 导致引用冲突
   - Git无法区分目标
4. ❌ **不要在pull时使用rebase**
   - 容易产生冲突
   - 使用merge更安全

---
