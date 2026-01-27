# GitHub Actions + Vercel 自动部署完整指南

> **目标**: 每天9:00自动抓取财经新闻，生成HTML报告，并通过Vercel自动部署到网站

---

## 📋 目录

1. [前置准备](#前置准备)
2. [配置GitHub Secrets](#配置github-secrets)
3. [设置GitHub Actions](#设置github-actions)
4. [配置Vercel](#配置vercel)
5. [测试和验证](#测试和验证)
6. [日常维护](#日常维护)
7. [常见问题](#常见问题)

---

## 前置准备

### ✅ 检查清单

开始前，请确认以下条件：

- [ ] 已有GitHub账号
- [ ] 已有Vercel账号（可用GitHub账号登录）
- [ ] 项目代码已推送到GitHub仓库
- [ ] 已安装Python 3.10+（本地测试用）
- [ ] 已配置智谱AI的Claude API密钥

### 🔧 本地测试（可选但推荐）

在配置自动部署前，建议先在本地测试运行一次：

```bash
# 进入项目目录
cd 定制每日财经新闻

# 进入news_bot目录
cd news_bot

# 安装依赖
pip install -r requirements.txt

# 运行新闻抓取
python run_simple.py
```

如果看到 `✓ 所有任务完成！` 说明系统运行正常。

---

## 配置GitHub Secrets

GitHub Secrets用于安全存储敏感信息（如API密钥）。

### 步骤1: 进入GitHub仓库

1. 打开浏览器，访问你的GitHub仓库
2. 点击仓库页面上方的 **Settings**（设置）标签

### 步骤2: 添加Secrets

1. 在左侧菜单找到 **Secrets and variables** → **Actions**
2. 点击 **New repository secret** 按钮
3. 添加以下两个Secret：

#### Secret 1: ANTHROPIC_API_KEY

```
Name: ANTHROPIC_API_KEY
Secret: 623b42e4e26b4ad18dd671bcfa0a33bd.7HFI8W0gfZtAwBBL
```

#### Secret 2: ANTHROPIC_BASE_URL

```
Name: ANTHROPIC_BASE_URL
Secret: https://open.bigmodel.cn/api/anthropic
```

### ✅ 验证Secrets

添加完成后，你应该看到两个Secret：
- ✓ ANTHROPIC_API_KEY
- ✓ ANTHROPIC_BASE_URL

---

## 设置GitHub Actions

### 步骤1: 确认Workflow文件

项目中已创建workflow配置文件：
```
.github/workflows/daily-news.yml
```

### 步骤2: 提交Workflow文件到仓库

```bash
# 确保在项目根目录
cd 定制每日财经新闻

# 检查当前分支
git branch

# 如果在feature分支，先创建新分支提交workflow
git checkout -b feature/github-actions-deployment

# 添加workflow文件
git add .github/
git add docs/deployment-guide.md

# 提交
git commit -m "✨ 添加GitHub Actions自动部署配置"

# 推送分支
git push origin feature/github-actions-deployment
```

### 步骤3: 创建Pull Request

```bash
# 使用GitHub CLI创建PR
gh pr create --title "✨ 添加GitHub Actions自动部署" --body "实现每日自动抓取新闻并部署"
```

或者通过GitHub网页：
1. 访问仓库页面
2. 点击 **Compare & pull request**
3. 填写标题和描述
4. 点击 **Create pull request**
5. 点击 **Merge pull request**
6. 点击 **Confirm merge**

### 步骤4: 启用GitHub Actions

1. 在GitHub仓库页面，点击 **Actions** 标签
2. 如果提示"Enable workflows"，点击启用
3. 你应该能看到 `daily-news.yml` workflow

---

## 配置Vercel

### 步骤1: 导入项目到Vercel

1. 访问 [vercel.com](https://vercel.com)
2. 登录账号（建议用GitHub登录）
3. 点击 **Add New** → **Project**
4. 导入你的GitHub仓库

### 步骤2: 配置项目设置

在Vercel项目配置页面：

**Build and Output Settings**:
- Framework Preset: **Other**
- Build Command: 留空（不需要构建）
- Output Directory: `public`
- Install Command: 留空

**Environment Variables**:
不需要设置（静态文件部署）

### 步骤3: 部署设置

- Root Directory: 留空或设置为 `.`
- 其他设置保持默认

### 步骤4: 点击Deploy

点击 **Deploy** 按钮，等待首次部署完成。

---

## 测试和验证

### 测试1: 手动触发GitHub Actions

1. 在GitHub仓库页面，点击 **Actions** 标签
2. 选择 **每日财经新闻生成** workflow
3. 点击右侧的 **Run workflow** 按钮
4. 确认运行

### 测试2: 检查执行结果

等待几分钟后，检查：

**GitHub Actions**:
- Actions页面显示绿色✓表示成功
- 点击进入查看详细日志

**Git仓库**:
- main分支应该有新的提交：`📰 每日新闻更新 - YYYY-MM-DD`
- public目录下应该有新的HTML文件

**Vercel**:
- 访问Vercel仪表板
- 应该看到新的部署正在进行或已完成
- 点击部署查看预览

### 测试3: 访问网站

1. 在Vercel仪表板找到你的域名（如 `your-project.vercel.app`）
2. 访问 `https://your-project.vercel.app/2026-01-26.html`（替换为最新日期）
3. 检查新闻页面是否正常显示

---

## 日常维护

### 📅 自动运行时间

Workflow配置为每天 **UTC 1:00** 运行，对应：
- **北京时间上午9:00**（冬令时）
- **北京时间上午8:00**（夏令时，美国3月-11月）

### 📊 监控执行状态

**方法1: GitHub Actions**
- 定期查看 Actions 标签页
- 红色✗表示失败，需检查日志

**方法2: 邮件通知**
- GitHub会发送执行结果邮件
- 建议在GitHub设置中启用Actions通知

**方法3: Vercel仪表板**
- 查看部署历史
- 绿色✓表示部署成功

### 🔧 修改运行时间

如需更改运行时间，编辑 `.github/workflows/daily-news.yml`:

```yaml
on:
  schedule:
    - cron: '0 1 * * *'  # UTC时间，可根据需要调整
```

**Cron格式说明**:
```
分钟 小时 日 月 星期
*    *    *  *   *
```

例如：
- `0 1 * * *` = 每天UTC 1:00（北京时间9:00）
- `0 2 * * *` = 每天UTC 2:00（北京时间10:00）
- `0 1 * * 1-5` = 每周一到周五UTC 1:00

### 📝 查看运行日志

1. GitHub仓库 → Actions
2. 点击具体的运行记录
3. 展开查看详细日志
4. 如有错误，日志会显示红色错误信息

---

## 常见问题

### ❌ 问题1: GitHub Actions失败

**错误**: `ENAMETOOLONG` 或文件名过长

**解决方案**:
- 已在 `run_simple.py` 中设置 `os.environ['TMPDIR'] = '/tmp'`
- 如仍有问题，检查Python版本是否为3.10+

### ❌ 问题2: API密钥错误

**错误**: `配置验证失败: 未设置 ANTHROPIC_API_KEY`

**解决方案**:
1. 检查GitHub Secrets是否正确添加
2. 确认Secret名称完全一致（区分大小写）
3. 重新运行workflow测试

### ❌ 问题3: Vercel不自动部署

**原因**: Vercel需要时间检测到GitHub更新

**解决方案**:
1. 等待1-2分钟
2. 在Vercel手动触发 redeploy
3. 检查Vercel是否正确连接到GitHub仓库

### ❌ 问题4: HTML文件404

**原因**: 文件未正确生成或路径错误

**解决方案**:
1. 检查Actions日志确认文件已生成
2. 确认vercel.json路由配置正确
3. 清除Vercel缓存重新部署

### ❌ 问题5: 新闻抓取失败

**可能原因**:
- RSS源访问受限
- 网络超时
- API配额用尽

**解决方案**:
1. 查看Actions日志定位具体错误
2. 检查RSS源是否可访问
3. 增加超时时间配置

---

## 🎉 完成！

恭喜！你已经完成了：

- ✅ GitHub Secrets配置
- ✅ GitHub Actions自动运行设置
- ✅ Vercel自动部署配置
- ✅ 测试验证

现在系统将每天自动运行，无需手动干预！

### 📌 快速访问链接

- **GitHub仓库**: [你的仓库地址]
- **GitHub Actions**: [你的仓库地址]/actions
- **Vercel仪表板**: [vercel.com/dashboard](https://vercel.com/dashboard)
- **网站**: [你的Vercel域名]

---

## 📞 获取帮助

如有问题：

1. **查看文档**: 项目根目录的 `README.md`
2. **检查日志**: GitHub Actions页面
3. **提交Issue**: 在GitHub仓库创建Issue
4. **查看记忆**: `memory.md` 文件

---

**最后更新**: 2026-01-26
**文档版本**: v1.0
