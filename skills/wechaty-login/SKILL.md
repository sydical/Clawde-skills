---
name: wechaty-login
description: 通过本地显示器生成微信登录二维码，登录成功后发送通知
metadata:
  openclaw:
    emoji: "💬"
    category: "utility"
    tags: ["wechat", "login", "qrcode", "vnc"]
    commands:
      - /wechat-login
      - 微信登录
---

# Wechaty Login

通过本地显示器生成微信登录二维码，用户扫码后登录成功。

## 功能

- 📱 生成微信登录二维码（保存到 /tmp/wechaty-qr.png）
- 🖥️ 通过 VNC 在显示器上查看二维码
- ✅ 登录成功后自动保存状态

## 使用方法

在对话中输入以下命令触发：

```
/wechat-login
```

或直接说 "微信登录"

## VNC 查看二维码

二维码已保存到 `/tmp/wechaty-qr.png`

你可以通过以下方式查看：
1. VNC 连接: `<服务器IP>:5900`
2. 查看图片文件: `/tmp/wechaty-qr.png`

## 登录成功后

系统会自动检测登录状态并保存：
- 登录用户
- 登录时间
