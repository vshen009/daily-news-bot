# 新闻卡片底部布局 - 需求文档

## 📋 需求概述

优化 `daily_news.html` 模板中新闻卡片底部布局，增加用户交互功能，提升信息展示质量。

---

## 🎯 核心需求

### 1. 显示内容（4个信息项）

| # | 信息项 | 说明 | 数据来源 |
|---|--------|------|----------|
| 1 | **发布时间** | 相对时间格式（如"5分钟前"、"2小时前"） | `article.published_date` 计算得出 |
| 2 | **新闻来源** | 显示 `source` 和 `source_original` | `article.source` / `article.source_original` |
| 3 | **分享按钮** | 点击触发提示 | 固定功能 |
| 4 | **阅读全文** | 点击跳转到原文 | `article.url` |

---

## 📐 设计规范

### 信息显示顺序
```
[发布时间] [新闻来源] ............ [分享按钮] [阅读全文]
    ↓              ↓                        ↓           ↓
  左侧           左侧                    右侧         右侧
```

**布局对齐**：左右分布
- **左侧**：发布时间 + 新闻来源
- **右侧**：分享按钮 + 阅读全文按钮

---

## 🎨 视觉设计

### 按钮样式：药丸式标签（Pill Badge）

```css
.pill-button {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 6px 12px;
    border-radius: 20px;  /* 圆角药丸形状 */
    font-size: 12px;
    font-weight: 500;
    transition: all 150ms cubic-bezier(0.4, 0, 0.2, 1);
}
```

### 四个元素的具体样式

| 元素 | 背景色 | 文字色 | 悬停效果 | 图标 |
|------|--------|--------|----------|------|
| **发布时间** | `#f1f5f9` | `#64748b` | 背景变深 `#e2e8f0` | ⏰ 时钟图标 |
| **新闻来源** | `rgba(255, 107, 107, 0.15)` | `#e63946` | 背景加深 | 📰 文章图标 |
| **分享按钮** | `#f1f5f9` | `#64748b` | 背景变深 + 缩放 | 🔗 分享图标 |
| **阅读全文** | `#f1f5f9`（浅灰） | `#64748b`（灰色） | 背景变深 + 缩放 | ↗️ 外部链接图标 |

---

## 🖼️ SVG 图标规范

### 统一风格：线性图标（Line Icons）

**规格：**
- `viewBox="0 0 24 24"`
- `stroke-width="2"`
- `stroke="currentColor"`
- `fill="none"`
- `stroke-linecap="round"`
- `stroke-linejoin="round"`

**图标定义：**

#### 1. 发布时间 - ⏰ 时钟
```html
<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
    <path stroke-linecap="round" stroke-linejoin="round" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
</svg>
```

#### 2. 新闻来源 - 📰 文章
```html
<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
    <path stroke-linecap="round" stroke-linejoin="round" d="M19 20H5a2 2 0 01-2-2V6a2 2 0 012-2h10a2 2 0 012 2v1m2 13a2 2 0 01-2-2V7m2 13a2 2 0 002-2V9a2 2 0 00-2-2h-2m-4-3H9M7 16h6M7 8h6v4H7V8z" />
</svg>
```

#### 3. 分享按钮 - 🔗 分享
```html
<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
    <path stroke-linecap="round" stroke-linejoin="round" d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.368 2.684 3 3 0 00-5.368-2.684z" />
</svg>
```

#### 4. 阅读全文 - ↗️ 外部链接
```html
<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
    <path stroke-linecap="round" stroke-linejoin="round" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
</svg>
```

---

## ⚡ 交互行为

### 1. 发布时间（仅展示）
- 无点击交互
- 悬停效果：背景色加深

### 2. 新闻来源（可点击）
- 点击：跳转到 `article.url`
- 悬停：背景色加深 + `cursor: pointer`
- 新标签页打开：`target="_blank" rel="noopener noreferrer"`

### 3. 分享按钮
- 点击：触发 Toast 提示
- **Toast 提示文案**："分享功能正在开发中..."
- 悬停：背景色加深 + `transform: scale(1.05)`

#### Toast 样式
```css
.toast {
    position: fixed;
    bottom: 24px;
    left: 50%;
    transform: translateX(-50%) translateY(100px);
    background: rgba(30, 41, 59, 0.95);
    color: white;
    padding: 12px 24px;
    border-radius: 8px;
    font-size: 14px;
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3);
    opacity: 0;
    transition: all 250ms cubic-bezier(0.4, 0, 0.2, 1);
    z-index: 10000;
}

.toast.show {
    transform: translateX(-50%) translateY(0);
    opacity: 1;
}
```

### 4. 阅读全文按钮
- 点击：跳转到 `article.url`
- 新标签页打开：`target="_blank" rel="noopener noreferrer"`
- 悬停：背景色加深 + `transform: scale(1.05)`

---

## 📱 响应式设计

### 桌面端（≥768px）
```
[时间] [来源] ..................... [分享] [阅读全文]
```

### 移动端（<768px）
```
[时间] [来源]
............ [分享] [阅读全文]
```
或（如果空间允许）：
```
[时间] [来源] ... [分享] [阅读全文]
```

---

## 🧩 HTML 结构（待实现）

```html
<div class="news-footer">
    <!-- 左侧：时间 + 来源 -->
    <div class="footer-left">
        <span class="footer-pill pill-time">
            <svg class="pill-icon">...</svg>
            <span class="pill-text">5分钟前</span>
        </span>
        <a href="{{ article.url }}" class="footer-pill pill-source">
            <svg class="pill-icon">...</svg>
            <span class="pill-text">{{ article.source }}</span>
        </a>
    </div>

    <!-- 右侧：分享 + 阅读全文 -->
    <div class="footer-right">
        <button class="footer-pill pill-share" onclick="showShareToast(event)">
            <svg class="pill-icon">...</svg>
            <span class="pill-text">分享</span>
        </button>
        <a href="{{ article.url }}" target="_blank" rel="noopener noreferrer"
           class="footer-pill pill-read-more"
           style="background: #f1f5f9; color: #64748b;">
            <svg class="pill-icon">...</svg>
            <span class="pill-text">阅读全文</span>
        </a>
    </div>
</div>
```

---

## ⏰ 时间格式化逻辑

需要在 JavaScript 中实现相对时间计算：

```javascript
function formatTimeAgo(dateString) {
    const now = new Date();
    const past = new Date(dateString);
    const diffMs = now - past;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return '刚刚';
    if (diffMins < 60) return `${diffMins}分钟前`;
    if (diffHours < 24) return `${diffHours}小时前`;
    if (diffDays < 7) return `${diffDays}天前`;
    return dateString; // 超过7天显示原始日期
}
```

---

## 🎨 参考设计

最接近：**选项 E（药丸式标签布局）**
- 使用药丸圆角样式
- 所有元素都是独立的 pill 按钮
- 左右分布布局
- 精美的 SVG 线性图标

---

## ✅ 验收标准

- [ ] 四个信息项按正确顺序显示
- [ ] 时间格式为相对时间（X分钟前）
- [ ] 图标风格与主题切换按钮一致（线性，24x24, stroke-width=2）
- [ ] 分享按钮点击触发 Toast 提示
- [ ] 阅读全文按钮在新标签页打开
- [ ] 悬停效果流畅（150ms transition）
- [ ] 响应式布局在移动端正常显示
- [ ] 所有交互元素有 cursor: pointer
- [ ] 符合 WCAG 可访问性标准（对比度 ≥ 4.5:1）

---

## 📝 备注

- **颜色变量**：复用现有的 CSS 变量（`--accent-blue`, `--accent-indigo` 等）
- **过渡动画**：使用现有的 `--transition-fast` (150ms)
- **字体大小**：与现有卡片内容保持一致（12-13px）
- **Z-index**：Toast 提示使用 `z-index: 10000` 确保在最顶层

---

**文档创建时间**：2026-02-01
**状态**：待实现
