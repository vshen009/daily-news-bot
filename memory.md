# 项目记忆文档

## 项目概述
**项目名称**: 定制每日财经新闻
**所有者**: Vincent (产品经理，非程序员)
**项目目标**: 每日自动抓取、翻译并生成财经新闻HTML报告

## 技术栈
- **语言**: Python
- **API**: Claude API (通过智谱AI代理)
- **部署**: Vercel
- **版本控制**: Git (main分支受保护)

## 重要配置

### API配置
- **提供商**: 智谱AI代理
- **Base URL**: https://open.bigmodel.cn/api/anthropic
- **模型**: claude-3-5-sonnet-20241022
- **配置文件**: news_bot/.env

### 新闻源配置
**国内媒体** (5个):
1. 新华社 - 优先级1
2. 财新网 - 优先级2
3. 21世纪经济报道 - 优先级3
4. 证券时报 - 优先级4
5. 第一财经 - 优先级5

**国际媒体** (5个):
1. 华尔街日报 - 优先级1
2. 彭博社 - 优先级2
3. CNBC - 优先级3
4. MarketWatch - 优先级4
5. Yahoo财经 - 优先级5

**板块划分**:
- 国内金融: 5个国内媒体源
- 亚太日本: 5个国际媒体源（翻译）
- 美欧动态: 5个国际媒体源（翻译）

### 系统参数
- 每个板块筛选数量: 5条
- 新闻最大时效: 48小时
- 翻译方式: Claude API
- 摘要长度: 150字符
- 输出格式: {date}.html
- 输出目录: public/

## Git工作流规范

### ⚠️ 重要约束
- ❌ main分支受保护，必须通过PR合并
- ❌ 绝对禁止force-push到main
- ❌ 分支和tag不能同名
- ✅ 所有改动都要通过feature分支

### 标准流程
```bash
# 1. 创建功能分支
git checkout -b feature/描述

# 2. 提交改动
git add .
git commit -m "✨ 描述"

# 3. 推送分支
git push origin feature/描述

# 4. 创建并合并PR
gh pr create --title "标题" --body "描述"
gh pr merge --squash --delete-branch
```

## 项目结构
```
定制每日财经新闻/
├── public/              # HTML输出目录（Vercel部署）
│   └── YYYY-MM-DD.html  # 每日新闻报告
├── news_bot/
│   ├── config/
│   │   └── sources.yaml # 新闻源配置
│   ├── src/
│   │   └── config.py    # 主配置文件
│   ├── .env             # 环境变量（已gitignore）
│   └── .env.example     # 环境变量模板
├── docs/                # 文档目录
├── index.html           # 首页
├── vercel.json          # Vercel配置
├── README.md            # 项目说明
└── GIT_WORKFLOW.md      # Git工作流规范
```

## 最近变更记录

### 2026-01-26 - 数据库去重优化（重大更新）
**目标**: 减少AI API调用和token使用，实现新闻数据持久化

**核心改进**:
1. ✅ 创建数据库模块 (`news_bot/src/database.py`)
   - 去重逻辑：中文用title，英文用title_original
   - 唯一约束：UNIQUE(title, title_original)
   - 数据库表结构：包含所有新闻字段、AI评论、翻译信息

2. ✅ 数据迁移 (`news_bot/data/migration/`)
   - 成功迁移3条历史记录到新表结构
   - 备份文件：backup_*_news.db

3. ✅ 主流程优化 (`news_bot/main.py`)
   - 去重检查：分离新新闻和缓存新闻
   - 只对新新闻调用翻译API
   - 只为新新闻生成AI评论
   - 缓存新闻复用已有数据

4. ✅ 配置和模型更新
   - `config.py`: 添加DATABASE_PATH配置
   - `models.py`: NewsArticle添加id字段
   - `ai_comment.py`: 添加generate_comment单条评论函数

**预期效果**:
- API调用减少70-85%
- AI评论可复用
- 数据永久保存

**文件清单**:
- 新建：`news_bot/src/database.py`
- 新建：`news_bot/data/migration/run_migration.py`
- 修改：`news_bot/src/config.py`
- 修改：`news_bot/src/models.py`
- 修改：`news_bot/main.py`
- 修改：`news_bot/src/ai_comment.py`

**已知问题**:
- 智谱AI代理有并发限制（429错误），需要控制请求速率
- 建议添加请求间隔或使用批量处理

### 2026-01-26 - 早期工作
- 修改了 news_bot/src/config.py
- 生成了新的HTML报告文件
- 创建了 run_bot.sh 和 run_simple.py（未跟踪）
- 当前分支: feature/optimize-data-processing

### 已知问题
- run_bot.sh 和 run_simple.py 未提交到仓库
- memory.md 需要持续更新

## 下一步计划
- [ ] 提交当前分支的改动
- [ ] 整理run_bot.sh和run_simple.py
- [ ] 定期更新memory.md
