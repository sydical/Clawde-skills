# honny-publisher - 小红书发布器 v2.0

> 集成登录、搜索、推荐、发布功能，基于 xiaohongshu-mcp 优化

## 功能

| 功能 | 说明 |
|------|------|
| 🔐 **登录** | 二维码扫码登录创作平台 |
| ✅ **状态检查** | 检查登录状态 |
| 🔍 **搜索** | 关键词搜索，支持排序筛选 |
| 📰 **推荐** | 获取首页推荐内容 |
| 📝 **详情** | 获取笔记详细信息 |
| 👤 **用户** | 获取个人资料 |
| 📤 **发布** | 发布图文笔记 |

## 安装依赖

```bash
pip install playwright
playwright install chromium
```

## 使用方法

### 1. 登录

```bash
python3 honny_publisher.py login
```

### 2. 检查登录状态

```bash
python3 honny_publisher.py check
```

### 3. 搜索内容

```bash
python3 honny_publisher.py search <关键词>
# 示例
python3 honny_publisher.py search AI
python3 honny_publisher.py search 美食
```

### 4. 获取推荐

```bash
python3 honny_publisher.py feed
```

### 5. 获取用户信息

```bash
python3 honny_publisher.py profile
```

### 6. 获取笔记详情

```bash
python3 honny_publisher.py detail <笔记URL>
```

### 7. 发布图文

```python
from honny_publisher import publish_image

publish_image(
    title="我的第一条笔记",
    content="这是笔记正文内容",
    images=["/path/to/image1.jpg", "/path/to/image2.jpg"],
    tags=["AI", "科技", "数码"]
)
```

## 会话存储

- 会话文件: `~/.honny-publisher/sessions/xhs.json`
- 二维码: `~/.honny-publisher/sessions/qr.png`

## 与 xiaohongshu-mcp 对比

| 特性 | honny-publisher | xiaohongshu-mcp |
|------|-----------------|-----------------|
| 语言 | Python | Go |
| 浏览器 | Playwright | Rod |
| 登录 | creator.xiaohongshu.com | xiaohongshu.com |
| 发布 | 创作平台 | 创作平台 |
| 搜索 | 网页抓取 | API |

## 注意事项

1. 首次使用需要扫码登录
2. 服务器环境可能被小红书拦截，建议本地运行
3. 会话有效期约 30 天，过期需重新登录
4. 发布建议使用 xiaohongshu-mcp（更稳定）
