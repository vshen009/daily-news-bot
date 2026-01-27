# Vercel 自定义域名国内访问部署方案

> **目标**: 解决国内 DNS 污染问题,使用自己的域名 `news.ai.0814.host` 稳定访问 Vercel 部署的财经新闻网站

---

## 📋 问题分析

### 国内访问 Vercel 的挑战

**DNS 污染问题**:
- **Vercel 官方域名**: `*.vercel.app`
- **问题**: 在中国大陆可能被 DNS 污染或限制访问
- **现象**: 无法访问、访问缓慢、间歇性连接失败

**为什么需要自定义域名?**
- ✅ 绕过限制 - 自定义域名不在黑名单中
- ✅ 提升稳定性 - 避免官方域名的访问问题
- ✅ 专业性 - 使用自己的域名更专业
- ✅ SEO 优化 - 有利于搜索引擎收录

---

## 🎯 解决方案对比

### 方案 A: 直接 CNAME 到 Vercel ⭐

**原理**: DNS CNAME 记录直接指向 Vercel

**优点**:
- ✅ 配置简单,5 分钟完成
- ✅ Vercel 自动提供免费 SSL 证书
- ✅ 证书自动续期
- ✅ 完全免费

**缺点**:
- ⚠️ 可能偶尔不稳定 (取决于 Vercel 在国内的连通性)

**适用场景**: 个人项目、测试环境、预算有限

---

### 方案 B: Cloudflare 反向代理 ⭐⭐⭐ (推荐)

**原理**: 域名 → Cloudflare CDN → Vercel

**优点**:
- ✅ **国内访问速度快** (Cloudflare 有国内节点)
- ✅ **免费 SSL 证书**
- ✅ **DDoS 防护**
- ✅ **缓存加速**
- ✅ **隐藏真实服务器 IP**

**缺点**:
- ⚠️ 需要将域名 DNS 托管到 Cloudflare
- ⚠️ 配置稍复杂

**适用场景**: 生产环境、面向国内用户、需要稳定访问

---

| 方案 | 难度 | 成本 | 国内速度 | 稳定性 | 推荐度 |
|------|------|------|----------|--------|--------|
| A. 直接CNAME | ⭐ 简单 | 免费 | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ |
| B. Cloudflare | ⭐⭐ 中等 | 免费 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |

---

## 🚀 方案 A: 直接 CNAME 到 Vercel

### 架构

```
news.ai.0814.host → cname.vercel-dns.com → Vercel
```

---

### 步骤 1: 在 Vercel 添加域名

1. 访问 https://vercel.com 登录
2. 选择项目: `financial-news`
3. 点击 **Settings** → **Domains**
4. 输入域名: `news.ai.0814.host`
5. 点击 **Add**

Vercel 会显示 DNS 配置:
```
Type: CNAME
Name: news
Value: cname.vercel-dns.com
```

---

### 步骤 2: 配置域名 DNS

登录域名注册商 (如 GoDaddy/Namecheap/阿里云),添加 DNS 记录:

| 类型  | 名称 | 值                    | TTL  |
|------|------|-----------------------|------|
| CNAME| news | cname.vercel-dns.com  | 600  |

**重要**: 不要开启 CDN/Proxy (橙色云朵),使用 DNS Only (灰色云朵)

---

### 步骤 3: 等待 DNS 生效

**传播时间**: 通常 5-30 分钟 (最多 48 小时)

**检查 DNS**:
```bash
# Mac/Linux
dig news.ai.0814.host CNAME

# Windows
nslookup news.ai.0814.host
```

**期望输出**:
```
news.ai.0814.host.  600  IN  CNAME  cname.vercel-dns.com.
```

**在线工具**: https://dnschecker.org

---

### 步骤 4: Vercel 自动配置 SSL

DNS 生效后,Vercel 会:
1. 自动检测 DNS 记录
2. 自动申请 Let's Encrypt SSL 证书
3. 自动配置 HTTPS

Vercel Dashboard 状态:
```
Configuration: ✓ Valid Configuration
Certificate:  ✓ Issued by Let's Encrypt
```

---

### 步骤 5: 测试访问

**浏览器访问**:
- https://news.ai.0814.host

**检查证书**: 点击地址栏锁图标
- 颁发者: Let's Encrypt
- 域名: news.ai.0814.host
- 有效期: 90 天 (自动续期)

**国内测速**:
- https://www.itdog.cn/http.html
- https://ce.baidu.com/index/batch

---

### 故障排查

**问题 1: DNS 未生效**
```bash
# 清除本地 DNS 缓存
Mac/Linux:
sudo dscacheutil -flushcache
sudo killall -HUP mDNSResponder

Windows:
ipconfig /flushdns
```

**问题 2: Vercel 未检测到 DNS**
1. 检查 DNS 记录是否正确
2. 确认 CNAME 目标是 `cname.vercel-dns.com`
3. 等待 10-30 分钟后刷新 Vercel Dashboard

**问题 3: 国内访问缓慢**
→ 切换到方案 B (Cloudflare)

---

## 🌟 方案 B: Cloudflare 反向代理 (推荐)

### 架构

```
用户 → news.ai.0814.host → Cloudflare CDN → Vercel
```

---

### 步骤 1: 将域名迁移到 Cloudflare

**1.1 注册 Cloudflare**

1. 访问 https://dash.cloudflare.com/sign-up
2. 使用邮箱注册 (免费)
3. 验证邮箱

**1.2 添加站点**

1. 登录 Cloudflare Dashboard
2. 点击 **"Add a Site"**
3. 输入域名: `ai.0814.host`
4. 选择 **Free Plan**
5. 点击 **"Continue"**

**1.3 更换域名服务器**

Cloudflare 会提供两个 NS 记录:
```
NS1: xxx.ns.cloudflare.com
NS2: yyy.ns.cloudflare.com
```

**操作**:
1. 登录原域名注册商
2. 修改域名服务器 (Nameservers) 为 Cloudflare 的 NS
3. 保存更改

**等待时间**: 2-24 小时 (通常 2-6 小时)

---

### 步骤 2: 在 Cloudflare 配置 DNS

添加 CNAME 记录:

| 类型  | 名称 | 内容                      | Proxy 状态 |
|------|------|--------------------------|-----------|
| CNAME| news | cname.vercel-dns.com | ✅ Proxied (橙色云朵) |

**重要**: 开启代理 (橙色云朵),启用 CDN 和 DDoS 防护

**验证 DNS**:
```bash
dig news.ai.0814.host CNAME

# 期望输出 (指向 Cloudflare)
news.ai.0814.host.  IN  CNAME  xxx.cloudflare.net.
```

---

### 步骤 3: 在 Vercel 添加域名

同方案 A 步骤 1:
- 在 Vercel 添加域名: `news.ai.0814.host`
- 获取 CNAME 目标: `cname.vercel-dns.com`

---

### 步骤 4: Cloudflare SSL 配置

**4.1 加密模式**

1. Cloudflare Dashboard → **SSL/TLS** → **Overview**
2. 设置加密模式为 **"Full"** 或 **"Full (strict)"**

```
Flexible: 用户 → CF (HTTPS) → Vercel (HTTP)
Full:      用户 → CF (HTTPS) → Vercel (HTTPS) ✅ 推荐
```

**4.2 Edge Certificates**

在 **SSL/TLS → Edge Certificates** 中:
- ✅ Always Use HTTPS: 开启
- ✅ Automatic HTTPS Rewrites: 开启
- ✅ Universal SSL: 开启 (免费)

---

### 步骤 5: 测试访问

**检查响应**:
```bash
# 检查 HTTPS
curl -I https://news.ai.0814.host

# 检查 Cloudflare 响应头
curl -I https://news.ai.0814.host | grep -i "cf-"

# 期望输出:
# cf-ray: xxx-xxx
# cf-cache-status: HIT/MISS
```

**国内速度测试**:
- https://www.itdog.cn/http.html
- 输入: `https://news.ai.0814.host`
- 选择多个测试节点

**期望结果**:
- 国内主要城市: < 500ms
- 国外: < 200ms

---

## 🎯 推荐决策流程

```
开始
  ↓
是否面向国内用户?
  ├─ 是 → 方案 B (Cloudflare) ⭐
  └─ 否 → 方案 A (直接CNAME)
  ↓
需要极致稳定性?
  ├─ 是 → 方案 B (Cloudflare)
  └─ 否 → 测试方案 A,不行再切 B
```

**推荐**: 方案 B (Cloudflare)
- 免费
- 国内访问快
- 稳定可靠
- 安全防护

---

## ✅ 检查清单

### 方案 A (直接CNAME)

- [ ] Vercel 项目已部署
- [ ] 在 Vercel 添加自定义域名
- [ ] 在域名注册商添加 CNAME 记录
- [ ] DNS 生效 (使用 dig/nslookup 检查)
- [ ] Vercel SSL 证书已颁发
- [ ] HTTPS 访问测试成功
- [ ] 国内访问测试成功

### 方案 B (Cloudflare)

- [ ] Cloudflare 账户已创建
- [ ] 域名已迁移到 Cloudflare (NS 服务器已更改)
- [ ] DNS 记录已配置 (开启代理/橙色云朵)
- [ ] Vercel 添加自定义域名
- [ ] Cloudflare SSL/TLS 已配置 (Full 模式)
- [ ] 国内访问速度测试 (< 500ms)
- [ ] 验证 Cloudflare 响应头 (cf-ray)

---

## 🔧 常见问题 FAQ

### Q1: 方案 A 在国内完全无法访问怎么办?

**A**: 切换到方案 B (Cloudflare):
1. 将域名迁移到 Cloudflare
2. 开启 CDN 代理 (橙色云朵)
3. 无需修改 Vercel 配置

---

### Q2: Cloudflare 免费版有限制吗?

**A**: 免费版功能:
- ✅ 无限带宽
- ✅ 无限请求数
- ✅ DDoS 防护
- ✅ 免费 SSL
- ⚠️ 无图片优化 (付费功能)
- ⚠️ 无移动优化 (付费功能)

对于财经新闻网站,免费版完全够用!

---

### Q3: 如何监控访问速度?

**A**: 推荐工具:

1. **国内测速**
   https://www.itdog.cn/http.html

2. **Google PageSpeed**
   https://pagespeed.web.dev/

3. **GTmetrix**
   https://gtmetrix.com/

4. **Uptime 监控**
   https://uptimerobot.com/

---

### Q4: 两个方案可以切换吗?

**A**: 可以!
- **A → B**: 将域名迁移到 Cloudflare,开启代理
- **B → A**: 关闭 Cloudflare 代理,改为 DNS Only

无需修改 Vercel 配置。

---

## 📚 参考资源

### 官方文档
- Vercel 自定义域名: https://vercel.com/docs/custom-domains
- Cloudflare DNS: https://developers.cloudflare.com/dns/
- Cloudflare SSL: https://developers.cloudflare.com/ssl/

### 工具
- DNS 检查: https://dnschecker.org
- SSL 测试: https://www.ssllabs.com/ssltest/
- HTTP 状态: https://httpstatus.io/

### 社区
- Vercel 社区: https://github.com/vercel/vercel/discussions
- Cloudflare 社区: https://community.cloudflare.com/

---

## 📝 实施记录

### 2026-01-25

- ✅ 创建部署方案文档 v2.0 (优化版)
- ✅ 移除方案 C (国内服务器)
- ✅ 精简内容,保留核心步骤
- 📝 待实施: 选择方案 A 或 B 并配置

### 下一步行动

1. Vincent 确认选择方案 A 或 B
2. 按照对应步骤执行
3. 测试国内访问速度
4. 记录实际效果并更新文档

---

**文档版本**: v2.0
**最后更新**: 2026-01-25
**维护者**: Vincent

**Generated with [Claude Code](https://claude.ai/code)**
**Co-Authored-By: Claude <noreply@anthropic.com>**
