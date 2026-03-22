---
name: scrapling-article-fetch
description: 使用 Scrapling + html2text 从 URL 抓取可读正文（含图片），按优先级选择器提取并按字符数截断；随后自动写入飞书文档并返回文档链接。适用于用户发送文章/博客/新闻链接（尤其是微信公众号 mp.weixin.qq.com）并希望快速验收正文内容的场景。
---

将文章正文抓取为 Markdown，并按需要写入飞书文档供用户验收。

## 前提条件

1. Python 3.10+。
2. 运行环境满足以下其一：
   - 推荐：已安装 `uv`
   - 备选：可用的 `venv + pip`
3. 机器可访问目标 URL。
4. 如需写飞书文档，默认直接使用 skill 内脚本按"当前 agent 身份"直连 Feishu OpenAPI；不要手动传 `app_id` / `app_secret`。

## 环境检查（必须先做）

在真正抓取前，先检查当前环境是否具备 Python。不要假设系统一定有 `python` 别名；统一先跑 wrapper：

```bash
bash ~/.openclaw/skills/scrapling-article-fetch/scripts/run_pipeline.sh
```

这个 wrapper 会优先选 `python3`，其次 `python`，避免再次出现"环境有 Python，但入口命令写死导致误判"的问题。

执行规则：
- 若 `python_ok=true`：继续执行抓取。
- 若没有 Python 或版本低于 3.10：先提醒用户安装，或在征得用户同意后再帮装；不要直接跳过检查硬跑。
- 若没有 `uv` 但有可用 Python：可以继续，只是改用 `venv + pip` 方案。

## 执行命令（抓取）

在受管控 Python 环境中，优先使用 `uv`：

```bash
uv run --with 'scrapling[fetchers]' --with html2text python ~/.openclaw/skills/scrapling-article-fetch/scripts/scrapling_fetch.py <url> [max_chars]
```

默认 `max_chars=30000`。

## 抓取规则

脚本必须按以下逻辑执行：

1. 使用 `Fetcher.get()` 拉取页面 HTML。
2. 如果域名是微信公众号（`mp.weixin.qq.com`），优先尝试：
   - `#js_content`
   - `.rich_media_content`
   - `.rich_media_area_primary`
3. 再尝试通用选择器：
   - `article`
   - `main`
   - `.post-content`
   - `[class*="body"]`
4. 用 `html2text` 转为 Markdown。
5. 默认保留链接和图片。
6. 清理常见微信尾部噪音（扫码提示、授权弹窗等文案）。
7. 按 `max_chars` 截断。
8. 若未命中正文容器，回退为整页 HTML 转换结果。

## 使用示例

```bash
# 抓取文章
uv run --with 'scrapling[fetchers]' --with html2text python ~/.openclaw/skills/scrapling-article-fetch/scripts/scrapling_fetch.py https://mp.weixin.qq.com/s/xxx

# 输出 JSON 格式
uv run --with 'scrapling[fetchers]' --with html2text python ~/.openclaw/skills/scrapling-article-fetch/scripts/scrapling_fetch.py https://mp.weixin.qq.com/s/xxx --json
```

## 输出格式

JSON 输出示例：
```json
{
  "title": "文章标题",
  "cover_url": "https://...",
  "markdown": "文章正文..."
}
```

## 备注

- 如果页面高度依赖 JS 导致抓取为空，后续可切换 DynamicFetcher 变体。
- 输出格式保持稳定，便于与原文逐段对照验收。
