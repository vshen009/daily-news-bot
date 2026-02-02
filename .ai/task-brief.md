# 任务简报

## 当前任务

**日期**：2026-02-02
**任务**：将"阅读全文"功能替换为"转发"功能
**优先级**：中
**预计耗时**：15 分钟

## 背景

当前新闻卡片底部的"阅读全文"按钮功能：点击跳转到新闻原文链接。

**需求变更**：
- 用户希望能够快速分享新闻内容到社交媒体/通讯软件
- 需要将新闻内容格式化为易读的纯文本
- 一键复制，方便粘贴到微信、Telegram、邮件等平台

## 技术方案

### 功能设计

#### 1. 按钮文字和图标
- **当前**：`阅读全文` + 外链图标
- **修改为**：`转发` + 分享图标（保持不变）

#### 2. 复制内容格式（纯文本）

```
{中文标题}
{英文标题（如有）}

{新闻内容（纯文本，去除 Markdown 格式）}

【来源】{来源名称}
【原文链接】{URL}

更多新闻 查看 news.ai.0814.host
```

**示例**：
```
美联储宣布加息25个基点，美股三大指数集体收涨
Federal Reserve raises interest rates by 25bps

美联储今日宣布加息25个基点，符合市场预期。鲍威尔表示，通胀压力正在缓解，未来可能暂停加息。美股三大指数集体收涨，道指涨0.38%，标普500涨0.45%...

【来源】Bloomberg
【原文链接】https://www.bloomberg.com/news/articles/2025-02-02/fed-raises-rates

更多新闻 查看 news.ai.0814.host
```

#### 3. 交互流程
1. 用户点击"转发"按钮
2. JavaScript 收集新闻卡片的所有数据
3. 格式化为纯文本（去除 Markdown 符号）
4. 写入剪贴板（使用 `navigator.clipboard.writeText()`）
5. 显示 Toast 提示："新闻内容已经复制"
6. 1.5 秒后自动隐藏提示

#### 4. 边界情况处理
- **纯中文新闻**：不显示英文标题部分（自动跳过）
- **无英文标题**：只显示中文标题
- **空标题**：显示"无标题"占位符
- **内容包含 Markdown**：转换为纯文本（去除 `**`、`#`、`-` 等符号）

### 实现步骤

#### 文件修改
**目标文件**：`news_bot/templates/daily_news.html`

#### 修改点 1：按钮文字（第 1016 行）
```html
<!-- 修改前 -->
<span class="pill-text">阅读全文</span>

<!-- 修改后 -->
<span class="pill-text">转发</span>
```

#### 修改点 2：JavaScript 功能（第 1006-1017 行）
```html
<!-- 修改前 -->
<a href="{{ article.url }}" target="_blank" rel="noopener noreferrer"
   class="footer-pill pill-read-more" onclick="event.stopPropagation();">
    ...
    <span class="pill-text">阅读全文</span>
</a>

<!-- 修改后 -->
<button class="footer-pill pill-share" onclick="copyNewsContent(event, this)">
    ...
    <span class="pill-text">转发</span>
</button>
```

#### 修改点 3：JavaScript 实现（新增函数）

在 `<script>` 标签中添加以下函数：

```javascript
/**
 * 复制新闻内容到剪贴板
 * @param {Event} event - 点击事件
 * @param {HTMLElement} button - 点击的按钮元素
 */
function copyNewsContent(event, button) {
    event.stopPropagation();
    event.preventDefault();

    // 获取新闻卡片元素
    const card = button.closest('.news-card');

    // 提取数据
    const chineseTitle = card.querySelector('.news-title')?.textContent.trim() || '无标题';
    const englishTitleEl = card.querySelector('.news-title-original');
    const englishTitle = englishTitleEl ? englishTitleEl.textContent.trim() : null;
    const content = card.querySelector('.news-excerpt')?.textContent.trim() || '';
    const source = card.querySelector('.pill-source .pill-text')?.textContent.trim() || '未知来源';
    const link = card.querySelector('.pill-source')?.getAttribute('href') || '';

    // 构建复制文本
    let copyText = chineseTitle;

    if (englishTitle) {
        copyText += '\n' + englishTitle;
    }

    copyText += '\n\n' + content + '\n\n';
    copyText += '【来源】' + source + '\n';
    copyText += '【原文链接】' + link + '\n\n';
    copyText += '更多新闻 查看 news.ai.0814.host';

    // 复制到剪贴板
    navigator.clipboard.writeText(copyText).then(() => {
        showToast('新闻内容已经复制');
    }).catch(err => {
        console.error('复制失败:', err);
        showToast('复制失败，请重试');
    });
}

/**
 * 显示 Toast 提示
 * @param {string} message - 提示文字
 */
function showToast(message) {
    let toast = document.querySelector('.toast');
    if (!toast) {
        toast = document.createElement('div');
        toast.className = 'toast';
        document.body.appendChild(toast);
    }

    toast.textContent = message;
    toast.classList.add('show');

    setTimeout(() => {
        toast.classList.remove('show');
    }, 1500);
}
```

#### 修改点 4：删除旧的"分享"按钮（可选）

**选项 A**：删除原有的"分享"按钮（第 1006-1011 行）
- 理由：新"转发"功能已包含分享意图

**选项 B**：保留两个按钮
- "分享" → 未来的社交平台分享功能
- "转发" → 当前的一键复制功能

**推荐**：选项 B（保留两个按钮，互不干扰）

#### 修改点 5：按钮样式复用

复用现有的 `.pill-share` 样式（第 670-683 行），无需修改 CSS。

## 影响范围

### 受影响的文件
- ✏️ `news_bot/templates/daily_news.html`（仅此一个文件）

### 不受影响
- ❌ 数据库结构（无需变更）
- ❌ 后端 Python 代码（无需变更）
- ❌ CSS 样式（复用现有样式）
- ❌ 部署配置（无需变更）

### 功能影响
- ✅ 新增"转发"功能，提升用户分享体验
- ✅ 移除"阅读全文"链接（但保留"来源"链接）
- ✅ 不影响现有展开/收起交互
- ✅ 不影响主题切换功能

### 兼容性
- ✅ 现代浏览器：`navigator.clipboard.writeText()` 广泛支持
- ⚠️ HTTP 环境：需 HTTPS 或 localhost（生产环境已满足）
- ⚠️ 旧浏览器：可添加 fallback（使用 `document.execCommand('copy')`）

## 验收标准

### 功能测试
- [ ] 点击"转发"按钮，内容正确复制到剪贴板
- [ ] 粘贴后格式符合要求（标题、内容、来源、链接、固定结尾）
- [ ] Toast 提示"新闻内容已经复制"正确显示
- [ ] 1.5 秒后 Toast 自动消失
- [ ] 纯中文新闻（无英文标题）正常复制
- [ ] 原有"来源"链接仍可点击跳转

### 边界测试
- [ ] 空标题新闻显示"无标题"
- [ ] 空内容新闻不报错
- [ ] 复制失败时显示"复制失败，请重试"
- [ ] 点击"转发"不触发展开/收起交互

### 兼容性测试
- [ ] Chrome/Edge/Safari/Firefox 最新版本测试通过
- [ ] 移动端浏览器测试通过

### 代码规范
- [ ] Git commit message 使用 emoji 前缀
- [ ] 使用功能分支提交 PR
- [ ] JavaScript 添加 JSDoc 注释
- [ ] 无 console.log 调试代码

## 待办事项

- [ ] 创建功能分支 `feature/add-forward-button`
- [ ] 修改 HTML 模板（按钮文字 + JavaScript）
- [ ] 测试复制功能（手动复制粘贴测试）
- [ ] 测试边界情况（无英文标题、空内容等）
- [ ] 提交代码
- [ ] 创建 PR
- [ ] 本地预览验证

## 风险评估

**风险等级**：🟢 低风险

**可能的问题**：
1. **剪贴板 API 兼容性**
   - 现象：旧版浏览器不支持 `navigator.clipboard`
   - 概率：低（Vercel 生产环境用户使用现代浏览器）
   - 缓解：可添加 fallback 逻辑

2. **用户交互冲突**
   - 现象：点击"转发"误触发展开/收起
   - 概率：低（`event.stopPropagation()` 已阻止冒泡）
   - 缓解：充分测试所有点击场景

3. **内容格式问题**
   - 现象：Markdown 格式未完全清除
   - 概率：中（`.textContent` 已自动去除 HTML 标签）
   - 缓解：验证实际复制效果

**回滚方案**：
```bash
git revert <commit-hash>
# 或手动恢复：
# 1. 将"转发"改回"阅读全文"
# 2. 删除 copyNewsContent() 函数
# 3. 恢复 <a href> 链接结构
```

## 技术细节说明

### 为什么使用 `.textContent` 而非 `.innerHTML`？
- `.textContent` 自动去除 HTML 标签，获得纯文本
- 符合需求："转换为纯文本"

### 为什么需要 `event.stopPropagation()`？
- 阻止点击事件冒泡到父元素（`.news-card`）
- 避免误触发展开/收起交互

### 剪贴板 API 选择
- `navigator.clipboard.writeText()`（现代标准）
- 比 `document.execCommand('copy')` 更可靠
- 已被所有主流浏览器支持

---

**Created by**: Claude
**Status**: ⏳ 等待用户确认
