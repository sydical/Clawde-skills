---
tags:
  - OpenClaw
  - 配置指南
  - 效率
created: 2026-03-16
---

# OpenClaw 6个必开设置 + 4条必会指令

> 让你彻底掌控 AI 助手，省钱又高效

---

## 一、6个必开设置

### 1. 实时跟踪日志

```bash
openclaw logs --follow
```

**作用**：实时跟踪日志，显示 AI 每一步在做什么——思考、调用工具、执行命令、读取文件等完整过程。

> 有时候 AI 执行任务卡住了，或者不知道在干啥，看一眼日志就明白了。

| 命令 | 作用 |
|------|------|
| `openclaw logs` | 查看历史日志 |
| `openclaw logs --follow` | 实时跟踪日志（最常用） |
| `openclaw logs --json` | JSON 格式输出，信息更详细 |
| `openclaw gateway --verbose` | 启动网关时显示详细执行过程 |

---

### 2. 流式回复

```bash
openclaw config set channels.feishu.streaming true
```

**作用**：开启后，AI 回复会像打字一样逐字显示，而不是等全部生成完才一次性输出。

✅ **特别推荐**：体验流畅多了，不用干等。而且如果发现 AI 说错方向，还能立即打断。

---

### 3. 开启耗时显示

```bash
openclaw config set channels.feishu.footer.elapsed true
```

**作用**：每次回复末尾显示耗时（如"已完成·耗时 1m 54s"），让你清楚知道 AI 干了多久，心里有数。

💰 看着时间，就知道 Token 大概烧了多少。钱花在哪，一目了然。

---

### 4. 开启状态展示

```bash
openclaw config set channels.feishu.footer.status true
```

**作用**：显示"已读""正在思考""正在执行"等状态提示，交互更透明，不再对着空气干等。

⚠️ 这个挺重要，不然有时候你不知道 AI 是在思考还是卡死了。

---

### 5. 群聊@才回复

```bash
openclaw config set channels.feishu.requireMention true --json
```

**作用**：机器人加入群聊后，只有被@时才回复，避免群内消息刷屏干扰。

💡 如果你的群很活跃，这个一定要开，不然群里每条消息都触发 AI 回复，Token 烧得飞快。

---

### 6. 话题独立上下文

```bash
openclaw config set channels.feishu.threadSession true
```

**作用**：在飞书群聊的话题模式下，每个话题拥有独立上下文，互不干扰，支持多任务并行。

👥 这个特别适合团队使用。不同话题讨论不同事情，不会串。

---

## 二、4条必会快捷指令

这些指令在聊天窗口直接发送即可，无需命令行：

| 指令 | 作用 |
|------|------|
| `/stop` | 中止当前任务，AI 立即停止执行 |
| `/status` | 快速查看健康状态、上下文用量、Token 消耗 |
| `/compact` | 压缩上下文，清理历史对话，节省 Token |
| `/new` | 新建会话，开始全新对话 |

### 常用场景

- **AI 跑偏了** → `/stop` 立即打断
- **聊太长了** → `/compact` 清理历史，省 Token
- **开始新任务** → `/new` 避免旧上下文干扰

---

## 三、省钱进阶配置

除了上面那些基础设置，下面这些配置能帮你大幅降低 Token 消耗：

### 1. 上下文压缩模式

```bash
openclaw config set agents.defaults.compaction.mode "default"
```

**作用**：将旧对话自动压缩为摘要，而非原样保留。

📊 测下来，这个能省 **30-40% Token**。对话太长的时候特别有用。

---

### 2. 上下文修剪

```bash
openclaw config set agents.defaults.contextPruning.mode "cache-ttl"
openclaw config set agents.defaults.contextPruning.ttl "4h"
```

**作用**：自动清理过期的工具输出（比如几小时前读取的文件内容），避免无用信息占用上下文。

📉 预计能省 **20-30% Token**。开了之后，确实感觉消耗慢了。

---

## 总结

| 配置 | 效果 |
|------|------|
| 实时跟踪日志 | 掌控 AI 行为，不再懵圈 |
| 流式回复 | 体验流畅，可随时打断 |
| 耗时显示 | 知道钱花在哪 |
| 状态展示 | 知道 AI 在干什么 |
| @才回复 | 避免群聊刷屏 |
| 话题独立 | 多任务并行不串台 |
| 上下文压缩 | 省 30-40% Token |
| 上下文修剪 | 省 20-30% Token |

> 记住这些配置和指令，能省不少麻烦！

---

*文档创建于 2026-03-16*
