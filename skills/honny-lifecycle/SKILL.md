# Honny Lifecycle Skill

> 虚拟数字生活自动化 v2.0

## 功能概述

Honny Lifecycle 是一个自动化数字生活管理系统，可以让 AI 助手模拟执行一个虚拟数字人"honny"的每日生活计划。

### 核心功能

| 功能 | 说明 |
|------|------|
| 天气数据获取 | 实时天气 + 日出日落 |
| 热点话题追踪 | 微博/小红书热搜 |
| 资讯聚合 | 行业早报 |
| AI 生图提示词 | 自动生成拍照提示词 |
| 社交文案生成 | 多平台文案 |
| 状态管理 | 每日任务进度跟踪 |
| 记忆系统 | 每日日志存储 |

## 触发方式

```
honny 今日计划 / 执行 Honny / honny status / honny 状态
```

## 命令行用法

```bash
# 查看今日计划
python3 honny-lifecycle.py plan

# 执行流水线
python3 honny-lifecycle.py run

# 查看状态
python3 honny-lifecycle.py status

# 重置状态（新一天）
python3 honny-lifecycle.py reset

# 查看配置
python3 honny-lifecycle.py config
```

## 每日流水线

### 早晨 (06:00-09:00)
- 天气检查
- 资讯早报
- 生成今日计划
- 早安发布

### 上午 (09:00-12:00)
- 热点追踪
- 拍摄创作

### 下午 (14:00-18:00)
- 下午拍摄
- 日落时分
- 内容创作

### 晚间 (18:00-23:00)
- 社交发布
- 今日回顾
- 明日预告

## 配置

配置文件: `~/data/disk/workspace/honny/config.json`

```json
{
  "name": "Honny",
  "location": "平潭",
  "location_en": "Pingtan",
  "personality": "温暖、好奇、热爱生活",
  "tagline": "今天也要好好生活呀～",
  "platforms": ["微博", "小红书", "抖音"]
}
```

## 状态文件

状态文件: `~/data/disk/workspace/honny/state.json`

存储每日任务完成进度和缓存数据。

## 依赖 Skills（可选集成）

- `weather` - 真实天气数据
- `honny-photov2` - AI 生图
- `honny-social-publisher` - 社交发布
- `snews-aggregator` - 资讯聚合
- `agent-reach` - 热点话题
- `humanize-ai-text` - 文案润色

## 文件结构

```
honny-lifecycle/
├── SKILL.md              # 本文档
└── honny-lifecycle.py   # 核心脚本

~/data/disk/workspace/honny/
├── config.json           # 配置文件
├── state.json           # 状态文件
├── PROJECT.md           # 方案文档
├── memory/daily/        # 每日日志
└── content/             # 生成内容
```

## 版本

- v2.0: 完整流水线实现
- v1.0: 基础框架
