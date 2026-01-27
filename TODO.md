# 📋 待办任务清单

## 🔴 高优先级

### 1. 🎨 重新设计HTML模板 - 移除三个板块结构

**文件**: `news_bot/templates/daily_news.html`

**当前状态**:
- 模板分为三个板块：国内金融、亚太日本、美国欧洲
- 代码中临时使用平均分配方案（所有global新闻平均分配到3个板块）

**需要修改的内容**:

#### 1.1 移除板块标题
```html
<!-- 需要删除或修改 -->
<section class="section">
    <div class="section-header">
        <div class="section-number">01</div>
        <h2 class="section-title">中国经济 · Domestic Finance</h2>
    </div>
    ...
</section>

<!-- 改为单一板块 -->
<section class="section">
    <div class="section-header">
        <h2 class="section-title">全球财经日报 · Global Financial Daily</h2>
    </div>
    ...
</section>
```

#### 1.2 修改模板变量
```jinja2
<!-- 当前模板接收3个变量 -->
{% if domestic_news %}...{% endif %}
{% if asia_news %}...{% endif %}
{% if useu_news %}...{% endif %}

<!-- 需要改为单一变量 -->
{% for article in articles %}
    ...
{% endfor %}
```

#### 1.3 调整样式
- 移除板块编号（01, 02, 03）
- 统一卡片布局
- 可能需要调整响应式断点

#### 1.4 同步修改HTML生成器
**文件**: `news_bot/src/html_generator.py`

```python
# 当前代码（第24-70行）
# 临时方案：平均分配到3个板块

# 需要改为
html = template.render(
    date=date_str,
    articles=articles,  # 直接传递所有新闻
    total_articles=len(articles)
)
```

---

## 🟡 中优先级

### 2. 🗄️ 数据库清理（可选）

**背景**: Category枚举已从3个值改为1个值（global），历史数据中可能有旧值

**选项**:
- **选项A**: 保留历史数据不变（推荐，不影响新数据）
- **选项B**: 迁移历史数据的category字段
  ```sql
  UPDATE news_articles SET category = 'global' WHERE category IN ('domestic', 'asia_pacific', 'us_europe');
  ```

---

### 3. 📝 更新文档

**需要更新的文件**:
- `README.md` - 移除"三个板块"的描述
- `CLAUDE.md` - 更新项目架构说明

---

## 🟢 低优先级

### 4. 🔧 优化配置文件注释

**文件**: `news_bot/config/sources.yaml`

```yaml
# 当前注释（已过时）
# ========== 国内媒体 - 用于"国内金融"板块 ==========
# ========== 国际媒体 - 用于"亚太日本"和"美欧动态"板块 ==========

# 建议改为
# ========== 数据源配置（统一为global分类）==========
```

---

### 5. 🧪 测试用例更新

如果项目有测试代码，需要更新：
- 移除板块相关的断言
- 测试新的单一分类逻辑

---

## ✅ 已完成的修改

- [x] Category枚举改为单一值（GLOBAL）
- [x] 所有数据源category设为"global"
- [x] 移除main.py中的板块平衡逻辑
- [x] 移除ai_comment.py中的category_map
- [x] 修改config.py中的TOP_NEWS_COUNT配置
- [x] 临时修改html_generator.py（平均分配方案）

---

## 📅 修改时间线

**2026-01-27**:
- ✅ 完成方案B的核心代码修改
- ⏳ HTML模板待重新设计（待定）

---

## 💡 设计建议

### 新HTML模板结构

```html
<!-- 推荐设计 -->
<main class="container">
    <section class="news-section">
        <header class="section-header">
            <h1>全球财经日报 · Global Financial Daily</h1>
            <p class="date">{{ date }}</p>
        </header>

        <!-- Featured News（头条） -->
        {% if articles[0] %}
        <article class="featured-news">
            ...
        </article>
        {% endif %}

        <!-- Regular News List -->
        <div class="news-grid">
            {% for article in articles[1:] %}
            <article class="news-card">
                ...
            </article>
            {% endfor %}
        </div>
    </section>
</main>
```

---

**最后更新**: 2026-01-27
**状态**: 等待用户确认后执行HTML模板修改
