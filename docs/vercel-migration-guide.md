# Vercel 项目迁移指南

## 从旧仓库迁移到新仓库

### 背景
项目已从 `claude-code-projects` 分离到独立仓库 `daily-news-bot`

### 当前部署状态
- ✅ 旧地址：`claude-code-projects` 中的 `定制每日财经新闻` 目录
- 🆕 新地址：`vshen009/daily-news-bot` 独立仓库

---

## 迁移步骤

### 方法1：通过 Vercel 网站界面（推荐）

#### 1. 登录 Vercel
访问 [vercel.com](https://vercel.com)

#### 2. 找到项目
进入您的 daily-news-bot 项目

#### 3. 更新 Git 仓库连接
1. 点击 **Settings**（设置）
2. 左侧菜单选择 **Git**
3. 点击 **Edit Git Repository**（编辑 Git 仓库）
4. 输入：`vshen009/daily-news-bot`
5. 点击 **Save**（保存）

#### 4. 更新根目录设置（重要！）
1. 在 **Settings** 中找到 **General**
2. 找到 **Root Directory**（根目录）设置
3. 修改为空（因为新仓库已经是最小结构）
4. 或删除 `定制每日财经新闻` 路径前缀

#### 5. 重新部署
1. 返回项目首页
2. 点击 **Redeploy**
3. 等待部署完成

---

### 方法2：通过 Vercel CLI

#### 安装 Vercel CLI（如果未安装）
```bash
npm i -g vercel
```

#### 登录
```bash
vercel login
```

#### 更新项目链接
```bash
# 进入项目目录
cd daily-news-bot

# 连接到现有项目
vercel link

# 更新 Git 设置
vercel git connect
```

---

## 验证部署

部署完成后，访问您的 Vercel 域名，检查：
- ✅ 首页正常显示
- ✅ 新闻列表正常加载
- ✅ 点击历史新闻可以正常跳转

---

## 常见问题

### Q1: 找不到 "Edit Git Repository" 选项？
**A**: 某些旧项目可能需要：
1. 删除当前 Vercel 项目
2. 重新从新仓库导入

### Q2: 根目录设置问题？
**A**:
- **旧仓库路径**：`定制每日财经新闻`
- **新仓库路径**：根目录（留空或 `./`）

### Q3: 环境变量需要重新设置吗？
**A**: 是的，需要在新项目中重新设置：
- `ANTHROPIC_API_KEY`
- 其他环境变量

---

## 部署后检查清单

- [ ] 首页显示正常
- [ ] 新闻列表加载正常
- [ ] 历史新闻链接可访问
- [ ] 环境变量已配置
- [ ] GitHub Actions 正常运行

---

## 新项目仓库信息

- **仓库地址**：https://github.com/vshen009/daily-news-bot
- **部署分支**：main（推荐）
- **构建命令**：无需构建（纯静态项目）
- **输出目录**：`public/`

---

## 备注

如果遇到问题，可以：
1. 删除旧的 Vercel 项目
2. 重新从 GitHub 导入新仓库
3. 配置环境变量
4. 部署完成
