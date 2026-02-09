# 图片分享功能 - 技术实施文档

**项目**: Daily News Bot
**功能**: 单条新闻卡片生成精美图片，支持长按保存分享
**文档版本**: v3.0 Final
**创建时间**: 2025-02-09
**面向人群**: Code X（开发者）

---

## 📋 目录

1. [技术选型](#技术选型)
2. [依赖安装](#依赖安装)
3. [核心代码实现](#核心代码实现)
4. [完整测试页面代码](#完整测试页面代码)
5. [集成到主模板](#集成到主模板)
6. [性能优化](#性能优化)
7. [错误处理](#错误处理)
8. [测试检查清单](#测试检查清单)

---

## 技术选型

### 一、技术栈

#### 前端生成方案（已确认）
```
用户点击"图片"按钮
  ↓
显示Toast: "正在生成图片..."
  ↓
创建隐藏的DOM容器（1080px宽，自适应高）
  ↓
按照"社论风"填充内容
  ↓
使用html2canvas渲染
  ↓
生成图片DataURL
  ↓
弹出居中预览
  ↓
用户长按保存（手机原生功能）
```

#### 核心库
- **html2canvas**: v2.0.0+（将DOM转换为canvas）
- **qr-code-styling**: 最新版（生成带爱马仕橙点缀的二维码）
- **无需后端**: 纯前端实现

---

## 依赖安装

### 一、CDN 引入（测试页面推荐）

```html
<!-- html2canvas -->
<script src="https://cdn.jsdelivr.net/npm/html2canvas@2.0.0/dist/html2canvas.min.js"></script>

<!-- qr-code-styling -->
<script src="https://cdn.jsdelivr.net/npm/qr-code-styling@1.5.0/lib/qr-code-styling.js"></script>

<!-- Font Awesome (图标) -->
<link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">

<!-- Google Fonts -->
<link href="https://fonts.googleapis.com/css2?family=Noto+Serif+SC:wght@700;900&family=Noto+Sans+SC:wght@500;700&family=Oswald:wght@500;700&display=swap" rel="stylesheet">
```

### 二、NPM 安装（主项目推荐）

```bash
npm install html2canvas qr-code-styling
```

---

## 核心代码实现

### 一、html2canvas 配置

```javascript
const html2canvasConfig = {
  scale: 2,                    // 2倍清晰度（Retina屏幕适配）
  useCORS: true,               // 支持跨域图片
  backgroundColor: '#e5e0d8',  // 报纸米色背景
  logging: false,              // 关闭日志输出
  allowTaint: false,           // 安全模式
  imageTimeout: 10000,         // 图片加载超时10秒
  removeContainer: true        // 生成后删除临时容器
};
```

### 二、二维码生成（带爱马仕橙点缀）

```javascript
// 使用 qr-code-styling 库
import QRCodeStyling from 'qr-code-styling';

function generateQRCode(url, containerId) {
  const qrCode = new QRCodeStyling({
    width: 150,
    height: 150,
    type: 'svg',
    data: url,  // 直接使用传入的URL（当前页面URL）
    dotsOptions: {
      color: '#000000',
      type: 'dots'
    },
    backgroundOptions: {
      color: '#ffffff',
    },
    cornersSquareOptions: {
      type: 'extra-rounded',
      color: '#c17c4a' // 爱马仕橙四角
    },
    cornersDotOptions: {
      type: 'dot',
      color: '#c17c4a' // 爱马仕橙定位点
    }
  });

  qrCode.append(document.getElementById(containerId));
  return qrCode;
}
```

**使用方式**:
```javascript
// 直接使用当前页面URL
const qrUrl = window.location.href;
generateQRCode(qrUrl, 'qrcode-container');
```

**说明**:
- 用户在哪个页面（如 `2025-02-09.html`），二维码就链接到哪个页面
- 无需日期处理，简单可靠

### 三、字体预加载

```javascript
// 确保字体加载完成再生成
async function waitForFonts() {
  await document.fonts.load('900 64px "Noto Serif SC"');
  await document.fonts.load('700 18px "Oswald"');
  await document.fonts.load('500 28px "Noto Sans SC"');
  await document.fonts.ready;

  // 额外等待500ms确保字体完全渲染
  await new Promise(resolve => setTimeout(resolve, 500));
}
```

### 四、图片生成主函数

```javascript
/**
 * 生成新闻分享图片
 * @param {Object} newsData - 新闻数据
 * @param {string} newsData.title - 标题
 * @param {string} newsData.content - 摘要
 * @param {string} newsData.source - 来源
 * @param {string} newsData.publish_time - 发布时间
 * @param {string} newsData.url - 链接
 * @param {Array} [newsData.core_elements] - 核心要素（可选，未来功能）
 * @note 当前版本不包含核心要素区，该功能计划在后续版本实现
 */
async function generateShareImage(newsData) {
  let container = null;

  try {
    // 1. 显示loading状态
    showToast('正在生成图片，请稍候...');

    // 2. 等待字体加载
    await waitForFonts();

    // 3. 创建隐藏的DOM容器
    container = document.createElement('div');
    container.style.position = 'absolute';
    container.style.left = '-9999px';
    container.style.top = '0';
    container.style.width = '1080px';
    container.style.background = '#e5e0d8';
    document.body.appendChild(container);

    // 4. 填充新闻内容
    container.innerHTML = createNewsCardHTML(newsData);

    // 5. 生成二维码（直接链接到当前页面）
    const qrUrl = window.location.href;
    generateQRCode(qrUrl, 'qrcode-container');

    // 6. 等待二维码渲染完成
    await new Promise(resolve => setTimeout(resolve, 500));

    // 7. 使用html2canvas渲染
    const canvas = await html2canvas(container, html2canvasConfig);

    // 8. 转换为JPG格式
    const imageData = canvas.toDataURL('image/jpeg', 0.85);

    // 9. 删除临时容器
    if (container && container.parentNode) {
      document.body.removeChild(container);
    }

    // 10. 显示预览
    showPreview(imageData);

    showToast('图片已生成');

  } catch (error) {
    console.error('生成图片失败:', error);

    // 确保容器被删除
    if (container && container.parentNode) {
      document.body.removeChild(container);
    }

    showToast('图片生成失败，请尝试长按截图分享');
  }
}
```

**说明**:
- 使用 `try-catch-finally` 确保容器一定会被删除
- 即使生成失败，也不会留下DOM垃圾

### 五、创建新闻卡片HTML

```javascript
function createNewsCardHTML(newsData) {
  const { title, content, source, publish_time } = newsData;

  // 计算相对时间
  const timeAgo = formatTimeAgo(publish_time);

  // 核心要素区（未来功能，当前版本不实现）
  // const coreElementsHTML = core_elements && core_elements.length > 0 ? `...` : '';

  return `
    <div class="news-share-card" style="width: 1080px; background: #e5e0d8; padding: 60px; border-radius: 16px;">
      <!-- Header -->
      <div class="news-header">
        <h1 class="news-title">${escapeHtml(title)}</h1>
        <div class="news-meta">来源: ${source.toUpperCase()} | ${timeAgo}</div>
        <div class="news-divider"></div>
      </div>

      <!-- News Lead -->
      <div class="news-lead">
        ${escapeHtml(content)}
      </div>

      <!-- 未来功能：核心要素区 -->
      <!-- Core Elements (计划在后续版本实现) -->

      <!-- Footer -->
      <div class="news-footer">
        <span class="footer-text">Shared by 文森特</span>
        <div id="qrcode-container"></div>
      </div>
    </div>

    <style>
      @import url('https://fonts.googleapis.com/css2?family=Noto+Serif+SC:wght@700;900&family=Noto+Sans+SC:wght@500;700&family=Oswald:wght@500;700&display=swap');

      .news-share-card {
        font-family: 'Noto Sans SC', sans-serif;
      }

      .news-title {
        font-family: 'Noto Serif SC', serif;
        font-weight: 900;
        font-size: 64px;
        line-height: 0.85;
        color: #2c241b;
        margin-bottom: 16px;
        display: -webkit-box;
        -webkit-line-clamp: 2;
        -webkit-box-orient: vertical;
        overflow: hidden;
      }

      .news-meta {
        font-family: 'Oswald', sans-serif;
        font-weight: 700;
        font-size: 18px;
        color: #c17c4a;
        text-transform: uppercase;
      }

      .news-divider {
        border-bottom: 4px solid #2c241b;
        margin: 24px 0;
      }

      .news-lead {
        background: #ece8e1;
        border-left: 4px solid #c17c4a;
        padding: 32px;
        margin: 32px 0;
        font-weight: 500;
        font-size: 28px;
        color: #2c241b;
        line-height: 1.6;
        display: -webkit-box;
        -webkit-line-clamp: 6;
        -webkit-box-orient: vertical;
        overflow: hidden;
      }

      <!-- 未来功能：核心要素区样式 -->
      <!--
      .core-elements {
        background: #ffffff;
        border: 1px solid #dcd6ce;
        border-radius: 8px;
        padding: 20px;
        margin-top: 24px;
        display: flex;
        gap: 32px;
      }
      -->

      .news-footer {
        display: flex;
        justify-content: flex-end;
        align-items: center;
        gap: 16px;
        border-top: 2px solid #dcd6ce;
        padding-top: 24px;
        margin-top: 32px;
      }

      .footer-text {
        font-weight: 500;
        font-size: 20px;
        color: #94A3B8;
      }

      #qrcode-container {
        width: 150px;
        height: 150px;
      }
    </style>
  `;
}
```

### 六、显示预览

```javascript
function showPreview(imageData) {
  // 创建或更新预览容器
  let previewContainer = document.getElementById('image-preview-container');

  if (!previewContainer) {
    previewContainer = document.createElement('div');
    previewContainer.id = 'image-preview-container';
    previewContainer.style.cssText = `
      position: fixed;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
      background: rgba(0, 0, 0, 0.8);
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      z-index: 10000;
    `;

    // 顶部提示
    const tip = document.createElement('div');
    tip.textContent = '长按图片保存到相册';
    tip.style.cssText = `
      color: white;
      font-size: 16px;
      margin-bottom: 20px;
    `;
    previewContainer.appendChild(tip);

    // 图片容器
    const imgContainer = document.createElement('div');
    imgContainer.style.cssText = `
      max-width: 90%;
      max-height: 80%;
      overflow: auto;
    `;
    previewContainer.appendChild(imgContainer);

    // 关闭按钮
    const closeBtn = document.createElement('button');
    closeBtn.textContent = '关闭';
    closeBtn.style.cssText = `
      margin-top: 20px;
      padding: 12px 32px;
      background: white;
      border: none;
      border-radius: 8px;
      font-size: 16px;
      cursor: pointer;
    `;
    closeBtn.onclick = closePreview;
    previewContainer.appendChild(closeBtn);

    // 点击遮罩关闭
    previewContainer.onclick = (e) => {
      if (e.target === previewContainer) {
        closePreview();
      }
    };

    document.body.appendChild(previewContainer);
  }

  // 更新图片
  const img = previewContainer.querySelector('img') || document.createElement('img');
  img.src = imageData;
  img.style.cssText = `
    max-width: 100%;
    height: auto;
    border-radius: 8px;
  `;

  const imgContainer = previewContainer.children[1];
  imgContainer.innerHTML = '';
  imgContainer.appendChild(img);

  previewContainer.style.display = 'flex';
}

function closePreview() {
  // 防止重复关闭
  if (closePreview.isClosing) return;
  closePreview.isClosing = true;

  const previewContainer = document.getElementById('image-preview-container');
  if (previewContainer) {
    // 淡出动画
    previewContainer.style.opacity = '0';
    previewContainer.style.transition = 'opacity 300ms ease-in-out';

    setTimeout(() => {
      previewContainer.style.display = 'none';
      closePreview.isClosing = false;
    }, 300);
  }
}

// 初始化标志
closePreview.isClosing = false;
```

### 七、工具函数

```javascript
// 格式化时间
function formatTimeAgo(dateString) {
  if (!dateString) return '未知时间';

  const now = new Date();
  const past = new Date(dateString);
  const diffMs = now - past;
  const diffMins = Math.floor(diffMs / 60000);
  const diffHours = Math.floor(diffMs / 3600000);

  if (diffMins < 1) return '刚刚';
  if (diffMins < 60) return `${diffMins}分钟前`;
  if (diffHours < 24) return `${diffHours}小时前`;

  const month = past.getMonth() + 1;
  const day = past.getDate();
  return `${month}月${day}日`;
}

// HTML转义
function escapeHtml(text) {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}

// Toast提示
function showToast(message) {
  let toast = document.querySelector('.toast');
  if (!toast) {
    toast = document.createElement('div');
    toast.className = 'toast';
    toast.style.cssText = `
      position: fixed;
      bottom: 24px;
      left: 50%;
      transform: translateX(-50%) translateY(100px);
      background: rgba(30, 41, 59, 0.95);
      color: #f8fafc;
      padding: 12px 24px;
      border-radius: 8px;
      font-size: 14px;
      box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3);
      opacity: 0;
      transition: all 250ms cubic-bezier(0.4, 0, 0.2, 1);
      z-index: 10001;
    `;
    document.body.appendChild(toast);
  }

  toast.textContent = message;
  toast.style.opacity = '1';
  toast.style.transform = 'translateX(-50%) translateY(0)';

  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transform = 'translateX(-50%) translateY(100px)';
  }, 3000);
}
```

---

## 完整测试页面代码

### 测试页面完整代码 (`test-share.html`)

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>图片分享功能测试</title>

    <!-- 依赖库 -->
    <script src="https://cdn.jsdelivr.net/npm/html2canvas@2.0.0/dist/html2canvas.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/qr-code-styling@1.5.0/lib/qr-code-styling.js"></script>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Noto+Serif+SC:wght@700;900&family=Noto+Sans+SC:wght@500;700&family=Oswald:wght@500;700&display=swap" rel="stylesheet">

    <style>
        body {
            font-family: 'Noto Sans SC', sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background: #f5f5f5;
        }

        header {
            text-align: center;
            margin-bottom: 40px;
        }

        .news-card {
            background: white;
            border-radius: 12px;
            padding: 24px;
            margin-bottom: 20px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }

        .news-card h2 {
            margin: 0 0 12px 0;
            color: #2c241b;
        }

        .news-card p {
            color: #64748B;
            line-height: 1.6;
        }

        .generate-btn {
            background: #c17c4a;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 8px;
            cursor: pointer;
            font-size: 14px;
            transition: all 0.2s;
        }

        .generate-btn:hover {
            background: #a36239;
            transform: scale(1.05);
        }

        .generate-btn:disabled {
            opacity: 0.6;
            cursor: not-allowed;
        }
    </style>
</head>
<body>
    <header>
        <h1>📰 图片分享功能测试</h1>
        <p>共3条测试新闻，点击"生成图片"按钮测试效果</p>
    </header>

    <main>
        <!-- 新闻1 -->
        <article class="news-card">
            <h2>美联储维持利率不变</h2>
            <p>美联储FOMC会议决定将基准利率维持在5.25%-5.5%区间，符合市场预期。点阵图显示年内仍有降息空间。</p>
            <div class="news-meta">来源: Bloomberg | 2小时前</div>
            <button class="generate-btn" onclick="testGenerateImage(1)">生成图片</button>
        </article>

        <!-- 新闻2 -->
        <article class="news-card">
            <h2>中国央行宣布下调存款准备金率0.5个百分点释放长期资金约1万亿元人民币支持实体经济发展</h2>
            <p>中国人民银行宣布决定下调金融机构存款准备金率0.5个百分点（不含已执行5%存款准备金率的金融机构）。本次下调后，大型金融机构存款准备金率为8.5%，中小金融机构为6.5%。此次降准释放长期资金约1万亿元，旨在保持银行体系流动性合理充裕，支持实体经济发展。</p>
            <div class="news-meta">来源: 新华社 | 5小时前</div>
            <button class="generate-btn" onclick="testGenerateImage(2)">生成图片</button>
        </article>

        <!-- 新闻3 -->
        <article class="news-card">
            <h2>日元跌至160关口</h2>
            <p>受美联储降息预期与日本央行政策分歧影响，日元汇率跌至160关口，创34年新低。市场预期日本央行可能干预汇市。</p>
            <div class="news-meta">来源: Reuters | 1小时前</div>
            <button class="generate-btn" onclick="testGenerateImage(3)">生成图片</button>
        </article>
    </main>

    <script>
        // 测试数据
        const testData = [
            {
                title: "美联储维持利率不变",
                content: "美联储FOMC会议决定将基准利率维持在5.25%-5.5%区间，符合市场预期。点阵图显示年内仍有降息空间。",
                source: "Bloomberg",
                publish_time: "2025-02-09T10:00:00"
            },
            {
                title: "中国央行宣布下调存款准备金率0.5个百分点释放长期资金约1万亿元人民币支持实体经济发展",
                content: "中国人民银行宣布决定下调金融机构存款准备金率0.5个百分点（不含已执行5%存款准备金率的金融机构）。本次下调后，大型金融机构存款准备金率为8.5%，中小金融机构为6.5%。此次降准释放长期资金约1万亿元，旨在保持银行体系流动性合理充裕，支持实体经济发展。",
                source: "新华社",
                publish_time: "2025-02-09T07:00:00"
            },
            {
                title: "日元跌至160关口",
                content: "受美联储降息预期与日本央行政策分歧影响，日元汇率跌至160关口，创34年新低。市场预期日本央行可能干预汇市。",
                source: "Reuters",
                publish_time: "2025-02-09T11:00:00",
                core_elements: [
                    { icon: "fa-chart-line", label: "跌幅", value: "-0.6%" },
                    { icon: "fa-money-bill", label: "汇率", value: "160.25" },
                    { icon: "fa-calendar", label: "时间", value: "34年新低" }
                ]
            }
        ];

        // 测试生成图片
        async function testGenerateImage(index) {
            const newsData = testData[index - 1];
            await generateShareImage({
                ...newsData,
                url: window.location.href  // 直接使用当前页面URL
            });
        }

        // 在这里粘贴上面核心代码实现中的所有函数
        // ...
    </script>
</body>
</html>
```

---

## 集成到主模板

### 修改 `daily_news.html`

#### 1. 添加依赖（在`<head>`中）

```html
<!-- 图片分享功能依赖 -->
<script src="https://cdn.jsdelivr.net/npm/html2canvas@2.0.0/dist/html2canvas.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/qr-code-styling@1.5.0/lib/qr-code-styling.js"></script>
```

#### 2. 修改"图片"按钮（约第1051行）

```html
<!-- 旧代码 -->
<button class="footer-pill pill-share" onclick="showShareToast(event)" aria-label="图片">
    <svg class="pill-icon" xmlns="http://www.w3.org/2000/svg" width="14" height="14" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
        <path stroke-linecap="round" stroke-linejoin="round" d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.368 2.684 3 3 0 00-5.368-2.684z" />
    </svg>
    <span class="pill-text">图片</span>
</button>

<!-- 新代码 -->
<button class="footer-pill pill-share" onclick="handleShareImage(event, this)" aria-label="生成图片">
    <svg class="pill-icon" xmlns="http://www.w3.org/2000/svg" width="14" height="14" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
        <path stroke-linecap="round" stroke-linejoin="round" d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.368 2.684 3 3 0 00-5.368-2.684z" />
    </svg>
    <span class="pill-text">图片</span>
</button>
```

#### 3. 添加处理函数

```javascript
/**
 * 处理图片分享按钮点击
 */
async function handleShareImage(event, button) {
    event.stopPropagation();
    event.preventDefault();

    const card = button.closest('.news-card');
    if (!card) {
        showToast('获取新闻信息失败');
        return;
    }

    // 提取新闻数据
    const newsData = {
        title: card.querySelector('.news-title')?.textContent.trim() || '',
        content: card.querySelector('.news-excerpt')?.textContent.trim() || '',
        source: card.querySelector('.pill-source .pill-text')?.textContent.trim() || '',
        publish_time: card.querySelector('.pill-time')?.getAttribute('data-published-date') || '',
        url: window.location.href
    };

    // 禁用按钮，显示loading
    button.disabled = true;
    const originalText = button.querySelector('.pill-text').textContent;
    button.querySelector('.pill-text').textContent = '生成中...';

    try {
        await generateShareImage(newsData);

        // 成功后恢复按钮
        button.querySelector('.pill-text').textContent = originalText;
        button.disabled = false;
    } catch (error) {
        console.error('生成图片失败:', error);
        showToast('图片生成失败，请重试');

        button.querySelector('.pill-text').textContent = originalText;
        button.disabled = false;
    }
}
```

---

## 性能优化

### 一、图片质量和文件大小

```javascript
const imageData = canvas.toDataURL('image/jpeg', 0.85);
```

**预估规格**:
- **格式**: JPG/JPEG
- **文件大小**: 约 200-500KB（根据内容长度）
- **质量**: 0.85（平衡清晰度和文件大小）
- **适用场景**: 微信分享、社交媒体上传

### 二、生成速度预估

| 设备类型 | 预估时间 | 说明 |
|---------|---------|------|
| **Desktop (Chrome/Firefox)** | 2-3秒 | CPU性能好，渲染快 |
| ** Laptop** | 3-4秒 | 性能中等 |
| **Mobile (iOS Safari)** | 4-6秒 | 移动设备性能受限 |
| **Mobile (Android Chrome)** | 4-6秒 | 取决于设备性能 |

**影响因素**:
- 网络速度（字体加载）
- 内容长度（摘要越长越慢）
- 设备性能（CPU/内存）
- 浏览器类型

### 二、生成速度优化

#### 1. 简化DOM结构
```javascript
// 避免复杂的嵌套和过多的阴影
container.innerHTML = createNewsCardHTML(newsData);
```

#### 2. 预加载字体
```javascript
// 在页面加载时预加载字体
window.addEventListener('load', () => {
  waitForFonts();
});
```

#### 3. 设置超时
```javascript
// 10秒超时保护
const timeoutPromise = new Promise((_, reject) => {
  setTimeout(() => reject(new Error('生成超时')), 10000);
});

await Promise.race([
  html2canvas(container, config),
  timeoutPromise
]);
```

### 三、内存管理

```javascript
// 生成后立即删除临时DOM
document.body.removeChild(container);

// 释放Canvas对象
canvas.width = 0;
canvas.height = 0;
```

---

## 错误处理

### 一、完整的错误处理

```javascript
async function generateShareImage(newsData) {
  try {
    // ... 生成逻辑
  } catch (error) {
    console.error('生成图片失败:', error);

    // 根据错误类型给出不同提示
    if (error.message.includes('超时')) {
      showToast('生成超时，请稍后重试');
    } else if (error.message.includes('字体')) {
      showToast('字体加载失败，请刷新页面重试');
    } else {
      showToast('图片生成失败，请尝试长按截图分享');
    }
  }
}
```

### 二、降级方案

```javascript
// 检测浏览器支持
if (typeof html2canvas === 'undefined') {
  showToast('您的浏览器不支持图片生成，请截图分享');
  return;
}

// 检测Canvas支持
if (!document.createElement('canvas').toDataURL) {
  showToast('您的浏览器不支持图片生成，请升级浏览器');
  return;
}
```

---

## 测试检查清单

### 功能测试

- [ ] 点击"图片"按钮能触发生成
- [ ] Toast显示"正在生成图片..."
- [ ] 3-5秒后弹出预览
- [ ] 预览图片居中显示
- [ ] 关闭按钮能关闭预览
- [ ] 点击遮罩能关闭预览
- [ ] 长按图片能保存（手机）

### 视觉测试

- [ ] 标题字体正确（Noto Serif SC 900）
- [ ] 来源/时间颜色正确（爱马仕橙）
- [ ] 摘要背景正确（浅米色）
- [ ] 二维码有爱马仕橙点缀
- [ ] 页尾显示"Shared by 文森特"
- [ ] 整体背景为报纸米色

### 兼容性测试

- [ ] Chrome Desktop ✅
- [ ] Safari Desktop ✅
- [ ] iOS Safari ✅
- [ ] Android Chrome ✅
- [ ] 微信内置浏览器 ✅

### 边界测试

- [ ] 超长标题（截断为2行）
- [ ] 超长摘要（截断为6行）
- [ ] 网络断开（显示友好提示）
- [ ] 字体加载失败（降级处理）

---

## 开发步骤

### 第一步：创建测试页面

```bash
mkdir -p share-test
# 创建 test-share.html（使用上面的完整代码）
```

### 第二步：本地测试

```bash
# 在 share-test 目录下启动简单HTTP服务器
python3 -m http.server 8000
# 或
npx serve
```

访问 `http://localhost:8000/test-share.html`

### 第三步：集成到主模板

1. 在 `daily_news.html` 中添加依赖
2. 添加核心函数
3. 修改"图片"按钮

### 第四步：部署测试

1. 提交代码
2. 部署到 Vercel
3. 在真实环境中测试

---

## 附录

### 常见问题

**Q: 生成速度慢？**
A: 优化DOM结构，预加载字体，设置超时保护。

**Q: 二维码不显示？**
A: 检查 qr-code-styling 库是否正确加载，等待500ms让二维码渲染完成。

**Q: 字体不正确？**
A: 确保Google Fonts正确加载，使用 `document.fonts.ready` 等待。

**Q: 图片质量差？**
A: 提高 `scale` 参数到2或3，但会增加生成时间。

**Q: 内存占用高？**
A: 生成后立即删除临时DOM和Canvas对象。

---

**文档版本**: v3.0 Final
**最后更新**: 2025-02-09
**维护人**: Code X
