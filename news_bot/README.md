# 定制每日财经新闻 - 自动化抓取系统

## 📖 项目简介

这是一个自动化财经新闻抓取系统，可以：
- 从国内外主流财经媒体自动抓取新闻
- 自动翻译英文新闻成中文
- 使用Claude AI生成专业评论
- 自动生成精美的HTML日报

**当前状态**: MVP测试版（2-3个新闻源）
**部署平台**: [Vercel](https://vercel.com)

---

## 🚀 快速开始

### 1. 环境要求

- Python 3.10 或更高版本
- Claude API密钥（[获取地址](https://console.anthropic.com/)）

### 2. 安装依赖

```bash
# 进入项目目录
cd news_bot

# 创建虚拟环境（推荐）
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# 或
venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt
```

### 3. 配置API密钥

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑.env文件，填入你的Claude API密钥
# ANTHROPIC_API_KEY=sk-ant-xxxxx
```

### 4. 运行测试

```bash
# 生成HTML日报
python main.py
```

### 5. 查看结果

生成的文件保存在 `public/` 目录：
- `YYYY-MM-DD.html` - HTML版本（简洁命名）

用浏览器打开即可查看（支持PC、Mac、手机等各种设备）！

---

## 🌐 部署到 Vercel

### 方式一：通过 GitHub 自动部署（推荐）

1. **将代码推送到 GitHub**
   ```bash
   git add .
   git commit -m "Initial commit"
   git push origin main
   ```

2. **在 Vercel 导入项目**
   - 访问 [vercel.com](https://vercel.com)
   - 点击 "New Project"
   - 导入你的 GitHub 仓库
   - Vercel 会自动检测 `vercel.json` 配置

3. **配置环境变量**
   - 在 Vercel 项目设置中添加环境变量：
     - `ANTHROPIC_API_KEY`: 你的 Claude API 密钥

4. **部署完成**
   - Vercel 会自动部署
   - 访问 `https://your-project.vercel.app` 查看结果

### 方式二：通过 Vercel CLI 部署

```bash
# 安装 Vercel CLI
npm i -g vercel

# 登录 Vercel
vercel login

# 部署
vercel

# 生产环境部署
vercel --prod
```

### 手动生成新内容

由于新闻抓取需要运行 Python 脚本，你可以：

**方案 A：本地生成 + 自动部署**
```bash
# 本地生成新闻
python main.py

# 提交到 GitHub
git add public/
git commit -m "Update: $(date +%Y-%m-%d)"
git push

# Vercel 自动部署新内容
```

**方案 B：使用 GitHub Actions 定时运行**

创建 `.github/workflows/daily-news.yml`：

```yaml
name: Daily News Generator

on:
  schedule:
    - cron: '0 2 * * *'  # 每天上午10:00（UTC+2）
  workflow_dispatch:      # 支持手动触发

jobs:
  generate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'

      - name: Install dependencies
        run: |
          cd news_bot
          pip install -r requirements.txt

      - name: Generate news
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
        run: |
          cd news_bot
          python main.py

      - name: Deploy to Vercel
        run: vercel --prod --token=${{ secrets.VERCEL_TOKEN }}
```

---

## 📁 项目结构

```
news_bot/
├── main.py                    # 主程序入口
├── requirements.txt           # Python依赖
├── .env.example              # 环境变量模板
├── config/
│   └── sources.yaml          # 新闻源配置（测试版：2-3个源）
├── src/
│   ├── models.py             # 数据模型
│   ├── config.py             # 配置管理
│   ├── scraper.py            # 新闻抓取器
│   ├── translator.py         # 翻译模块（Claude API）
│   ├── ai_comment.py         # AI评论生成器
│   └── html_generator.py     # HTML生成器
├── templates/
│   └── daily_news.html       # 响应式HTML模板（适配所有设备）
├── public/                   # 输出目录（生成的HTML，Vercel自动部署）
└── logs/                     # 日志目录
```

---

## ⚙️ 配置说明

### 新闻源配置

编辑 `config/sources.yaml`：

```yaml
sources:
  - name: "新华社"
    english_name: "Xinhua"
    url: "http://www.xinhuanet.com/fortune/"
    rss: "http://www.xinhuanet.com/fortune/news_fortune.xml"
    language: "zh"
    category: "domestic"
    priority: 1
    enabled: true

  - name: "Bloomberg"
    english_name: "Bloomberg"
    url: "https://www.bloomberg.com/markets"
    rss: "https://feeds.bloomberg.com/markets/news.rss"
    language: "en"
    category: "us_europe"
    priority: 1
    enabled: true
    translate: true  # 英文源需要翻译
```

**参数说明**:
- `category`: 板块分类
  - `domestic`: 国内金融
  - `asia_pacific`: 亚太日本
  - `us_europe`: 美国欧洲
- `language`: `zh`中文 / `en`英文
- `translate`: 英文源设为 `true`

---

## 💰 成本估算

**每日成本**:
- Claude API: ~$0.11/天 (约0.8元)
  - 翻译：15条 × 1000 token = 15,000 token
  - AI评论：15条 × 500 token = 7,500 token
  - 总计：22,500 token ≈ $0.11

**每月成本**: 约 $3.3 (24元人民币)

**Vercel 托管**: 免费版足够使用（100GB 带宽/月）

---

## 🔧 常见问题

### 1. API密钥在哪获取？

访问 https://console.anthropic.com/ 注册并创建API密钥

### 2. 如何添加更多新闻源？

编辑 `config/sources.yaml`，按照格式添加即可

### 3. 生成的HTML在哪里？

保存在 `public/` 目录下，文件名格式：`YYYY-MM-DD.html`

**Vercel 部署后**: 访问 `https://your-project.vercel.app/YYYY-MM-DD.html`

### 4. 如何设置自动运行？

使用 GitHub Actions（推荐）：
- 在 GitHub 仓库设置中添加 `ANTHROPIC_API_KEY` 和 `VERCEL_TOKEN` 密钥
- 创建 `.github/workflows/daily-news.yml` 文件（见上文）
- 每天自动生成并部署

### 5. 新闻源抓取失败怎么办？

- 检查网络连接
- 查看日志文件：`logs/news_bot_YYYY-MM-DD.log`
- 尝试禁用该新闻源（设置 `enabled: false`）

### 6. Vercel 如何访问历史新闻？

Vercel 会部署 `public/` 目录下的所有 HTML 文件，访问格式：
- `https://your-project.vercel.app/2026-01-25.html`
- `https://your-project.vercel.app/2026-01-24.html`

---

## 📊 当前限制

**MVP测试版**:
- ✅ 支持2-3个新闻源（新华社、财新网、Bloomberg）
- ✅ RSS抓取
- ✅ Claude翻译和AI评论
- ✅ 生成HTML
- ✅ Vercel 自动部署
- ❌ 暂不支持HTML解析（备用方案）
- ❌ 暂不支持人工筛选

---

## 🎯 下一步计划

**Phase 1.5**: 扩展新闻源到10个
**Phase 2**: 添加更多国际媒体
**Phase 3**: 实现历史归档功能
**Phase 4**: 优化SEO和分享功能

---

## 📝 更新日志

### v0.2.0 (2026-01-25) - Vercel部署优化
- ✅ 移除 Docker 和 Nginx 依赖
- ✅ 简化为 Vercel 部署
- ✅ 优化项目结构
- ✅ 输出目录改为 public/

### v0.1.0 (2026-01-25) - MVP测试版
- ✅ 基础抓取功能
- ✅ Claude翻译集成
- ✅ AI评论生成
- ✅ HTML生成
- ✅ 配置文件系统

---

## 📞 支持

如有问题，请查看：
- 项目需求文档：`../项目需求文档.md`
- 实施计划：`../实施计划.md`
- [Vercel 文档](https://vercel.com/docs)

---

**Happy Coding! 🎉**
