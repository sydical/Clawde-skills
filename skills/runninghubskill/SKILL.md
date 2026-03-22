# RunningHub Image Generation Skill

## 功能概述

通过 RunningHub 云端 ComfyUI 平台调用 AI 工作流生成图像。

**API 文档**: https://www.runninghub.cn/call-api/api-detail/2001898176946814977?apiType=4

## 环境配置

```bash
export RUNNINGHUB_API_KEY="你的API KEY"
export RUNNINGHUB_WORKFLOW_ID="工作流ID"
```

或在 skill 配置中设置：

```json
{
  "config": {
    "apiKey": "你的API KEY",
    "workflowId": "2001898176946814977"
  }
}
```

## 使用方法

### 完整参数

```
runninghubskill \
  --nodeInfoList '[{"nodeId": "77", "fieldName": "image", "fieldValue": "xxx.png"}]' \
  --workflowId "2001898176946814977" \
  --instanceType "default" \
  --poll_interval 5 \
  --timeout 300
```

## 参数说明

| 参数 | 类型 | 必需 | 默认值 | 说明 |
|------|------|:----:|--------|------|
| `nodeInfoList` | array | ✅ | - | 节点参数列表 |
| `workflowId` | string | ❌ | 配置值 | 工作流 ID |
| `instanceType` | string | ❌ | "default" | 实例类型 (default/plus) |
| `usePersonalQueue` | boolean | ❌ | false | 是否使用个人队列 |
| `poll_interval` | number | ❌ | 5 | 轮询间隔 (秒) |
| `timeout` | number | ❌ | 300 | 超时时间 (秒) |

## nodeInfoList 参数格式

```json
[
  {
    "nodeId": "77",
    "fieldName": "image",
    "fieldValue": "bda1d8aedec56be3899ddb86db33aed5a6bbaba8ddf1504334c73cf1182fe992.png",
    "description": "人物参考图"
  }
]
```

## 返回结果

成功时返回：
```json
{
  "success": true,
  "task_id": "xxx",
  "status": "completed",
  "images": [
    {"url": "https://...", "type": "png"}
  ],
  "elapsed_seconds": 45
}
```

## 辅助函数

- `submitTask()` - 仅提交任务
- `queryTask()` - 查询任务状态

## 注意事项

1. **工作流必须先在网页端运行成功一次**
2. `poll_interval=0` 或 `timeout=0` 时只提交不等待
3. 认证: `Authorization: Bearer {API_KEY}`
