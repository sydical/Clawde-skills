# HEARTBEAT.md - Honny 数字生活心跳

> 心跳机制已配置完成！

## 心跳执行

每次心跳触发时，会自动执行当前时段的未完成任务。

## 命令

```bash
# 手动触发心跳（测试用）
python3 ~/data/disk/workspace/skills/honny-lifecycle/honny-lifecycle.py heartbeat

# 查看状态
python3 ~/data/disk/workspace/skills/honny-lifecycle/honny-lifecycle.py status

# 查看今日计划
python3 ~/data/disk/workspace/skills/honny-lifecycle/honny-lifecycle.py plan
```

## 自动任务时段

| 时段 | 时间 | 任务 |
|------|------|------|
| 🌅 早晨 | 06:00-09:00 | 天气、资讯、计划、早安 |
| ☀️ 上午 | 09:00-12:00 | 热点、拍摄 |
| 🌊 下午 | 14:00-18:00 | 拍摄、日落、内容 |
| 🌙 晚间 | 18:00-23:00 | 发布、回顾、预告 |

## 活跃时间
- 开始: 06:00
- 结束: 23:00
- 心跳间隔: 30分钟

## 状态
- 已测试: ✅
- 心跳模式: ✅
- 任务执行: ✅
