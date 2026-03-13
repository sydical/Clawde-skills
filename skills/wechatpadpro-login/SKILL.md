---
name: wechatpadpro-login
description: 通过WeChatPadPro生成微信登录二维码并通过QQ发送到指定用户，登录成功后发送通知
metadata:
  openclaw:
    emoji: "💬"
    category: "utility"
    tags: ["wechat", "login", "qrcode", "qq", "wechatpadpro"]
    commands:
      - /wechat-login
      - 微信登录
---

# WeChatPadPro Login

通过WeChatPadPro生成微信登录二维码并通过QQ发送到指定用户，登录成功后发送通知。

## 功能

- 📱 生成微信登录二维码
- 📤 通过QQ发送二维码图片给指定用户
- ✅ 登录成功后自动通知

## 使用方法

在对话中输入以下命令触发：

```
/wechat-login
```

或直接说 "微信登录"

## 执行流程

1. **检查登录状态** - 技能会检查微信是否已登录
2. **已登录** - 告知用户当前登录状态
3. **未登录** - 生成二维码并发送给QQ用户

## 登录成功后

技能会检测到登录状态并通知：

- 登录用户
- 登录时间

## 配置

- 通知QQ: `4515644` (可通过环境变量 `WECHAT_NOTIFY_QQ` 修改)
- WeChatPadPro API: `http://localhost:8080` (可通过环境变量 `WECHAT_API_URL` 修改)
- ADMIN_KEY: `wechatpad123` (可通过环境变量 `WECHAT_ADMIN_KEY` 修改)
