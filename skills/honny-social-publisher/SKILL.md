---
name: honny-social-publisher
description: 同时发布内容到微博、小红书、得物和抖音，使用真实 Chrome 浏览器绕过反机器人检测。支持文字、图片、视频、预览模式和实际发布。当用户需要发布微博、发微博、weibo post、发布小红书、发小红书、得物发布、发得物、抖音发布、发抖音时使用此 skill。
---

# 社交平台发布工具（支持抖音）

使用真实 Chrome 浏览器同时发布到微博、小红书、得物和抖音，支持文字、图片和视频。

## 脚本目录

所有脚本位于 scripts/ 子目录。

## 前置要求

- Google Chrome 或 Chromium 已安装
- bun 已安装
- 首次运行：在打开的浏览器窗口中登录各平台

## 安装依赖

```bash
cd ${SKILL_DIR}
npm install
```

## 发布到抖音

```bash
# 预览模式（发布视频）
npx -y bun ${SKILL_DIR}/scripts/douyin-publisher.ts "精彩视频介绍" --video ./video.mp4

# 带图片（图文作品）
npx -y bun ${SKILL_DIR}/scripts/douyin-publisher.ts "图文分享" --image ./photo.png

# 带话题
npx -y bun ${SKILL_DIR}/scripts/douyin-publisher.ts "新视频上线" --video ./video.mp4 --topic 搞笑 --topic 宠物

# 实际发布
npx -y bun ${SKILL_DIR}/scripts/douyin-publisher.ts "抖音上新！" --video ./video.mp4 --submit
```

## 发布到得物

```bash
# 预览模式（不发布）
npx -y bun ${SKILL_DIR}/scripts/dewu-publisher.ts "得物上新！"

# 带图片
npx -y bun ${SKILL_DIR}/scripts/dewu-publisher.ts "好物分享！" --image ./photo.png

# 实际发布
npx -y bun ${SKILL_DIR-publisher.ts "得物上新！"}/scripts/dewu --image ./photo.png --submit
```

## 发布到微博

```bash
# 预览模式（不发布）
npx -y bun ${SKILL_DIR}/scripts/social-publisher.ts --weibo "你好，微博！"

# 带图片
npx -y bun ${SKILL_DIR}/scripts/social-publisher.ts --weibo "看这张图！" --image ./photo.png

# 实际发布
npx -y bun ${SKILL_DIR}/scripts/social-publisher.ts --weibo "发布微博！" --image ./photo.png --submit
```

## 发布到小红书

```bash
# 预览模式（不发布）
npx -y bun ${SKILL_DIR}/scripts/social-publisher.ts --xhs "你好，小红书！" --image ./photo.png

# 实际发布
npx -y bun ${SKILL_DIR}/scripts/social-publisher.ts --xhs "发布小红书！" --image ./photo.png --submit
```

## 同时发布到多个平台

```bash
# 预览模式
npx -y bun ${SKILL_DIR}/scripts/social-publisher.ts --weibo "你好！" --xhs "你好！" --dewu "上新！" --douyin "抖音见！"

# 实际发布
npx -y bun ${SKILL_DIR}/scripts/social-publisher.ts --weibo "微博" --xhs "小红书" --dewu "得物" --douyin "抖音" --image ./photo.png --video ./video.mp4 --submit
```

## 参数说明

| 参数 | 描述 |
|------|------|
| `--weibo <text>` | 微博内容 |
| `--xhs <text>` | 小红书内容 |
| `--dewu <text>` | 得物内容 |
| `--douyin <text>` | 抖音内容 |
| `--image <path>` | 图片路径（可重复多个） |
| `--video <path>` | 视频路径（可重复，抖音专用） |
| `--topic <topic>` | 话题标签（可重复多个） |
| `--submit` | 实际发布（默认：仅预览） |
| `--profile <dir>` | 自定义 Chrome 配置目录 |

## 注意事项

- 首次运行需要手动登录各平台（会话会保存）
- 总是先用预览模式确认，再使用 --submit
- 小红书至少需要 1 张图片
- 微博普通帖子限制 2000 字
- 得物推荐使用图片，图片能提高曝光率
- 抖音建议上传视频，也可以发图片作品
- 支持 macOS、Linux 和 Windows

## 预览模式 vs 发布模式

- **预览模式**（默认）：打开浏览器让你确认内容，不会真正发布
- **发布模式**（加 `--submit`）：确认后自动点击发布按钮
