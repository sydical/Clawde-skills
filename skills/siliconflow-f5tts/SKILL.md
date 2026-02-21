---
name: siliconflow-f5tts
description: |
  硅基流动 F5-TTS 语音合成技能。使用 F5-TTS 模型将文本转换为语音。
  适用于：(1) 语音合成 (2) 文本转语音 (3) 有声内容创作 (4) AI 配音。
  注意：需要用户提供硅基流动 API Key。
---

# 硅基流动 F5-TTS 语音合成

## 概述

本技能调用硅基流动 (SiliconFlow) 的 F5-TTS 模型，将文本转换为语音。

## 使用前提

1. **获取 API Key**
   - 访问 https://cloud.siliconflow.cn
   - 注册账号
   - 在"API Keys"页面创建密钥
   - **必须将 API Key 告知 AI**，AI 不会主动询问

2. **API Key 存储**
   - 用户需要使用时，直接提供 API Key
   - AI 会临时使用该 Key 进行调用

## 使用方法

### 基本调用

当用户说"帮我把这段话转为语音"、"生成语音"、"文字转语音"等时：

1. **确认 API Key**
   - 如果用户未提供 API Key，询问："请提供你的硅基流动 API Key"

2. **获取文本**
   - 询问用户要转换为语音的文本内容

3. **调用 API**
   - 使用脚本生成语音

### 示例对话

```
用户：帮我把"你好世界"转成语音
AI：请提供你的硅基流动 API Key
用户：sk-xxxxxxx
AI：好的，正在为你生成语音...
（调用 API）
AI：语音已生成！[发送音频文件]
```

## API 调用

### 端点

```
POST https://api.siliconflow.cn/v1/audio/tts
```

### 请求头

| 头字段 | 值 |
|--------|-----|
| Authorization | Bearer {API_KEY} |
| Content-Type | application/json |

### 请求体

```json
{
  "model": "F5-TTS",
  "input": "要转换的文本",
  "voice": "预留字段，可为空"
}
```

## Python 脚本

已在 `scripts/tts.py` 中实现调用逻辑：

```bash
python3 /root/.openclaw/workspace/skills/siliconflow-f5tts/tts.py "API_KEY" "文本内容"
```

### 输出

- 生成的音频文件保存为 `output.mp3`
- 返回文件路径给用户

## 注意事项

1. **API Key 安全**
   - 不要将用户的 API Key 保存到任何文件
   - 仅在内存中使用
   - 使用后及时释放

2. **费用**
   - F5-TTS: ¥1 / 1M tokens
   - 请提醒用户关注配额

3. **文本限制**
   - 单次请求文本长度建议在 1000 字以内
   - 过长文本建议分段处理

4. **音频格式**
   - 默认输出 MP3 格式

## 快速参考

| 场景 | 操作 |
|------|------|
| 首次使用 | 询问 API Key |
| 已有 Key | 直接调用 |
| 生成语音 | 执行 tts.py |
| 发送用户 | 使用 <qqimg> 或直接发送文件 |
