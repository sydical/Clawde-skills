# RunningHub Image Generation Skill

## 📋 目录

- [简介](#简介)
- [安装](#安装)
- [配置](#配置)
- [使用方法](#使用方法)
- [示例](#示例)
- [辅助函数](#辅助函数)
- [常见问题](#常见问题)

## 简介

通过 RunningHub 云端 ComfyUI 平台调用 AI 工作流生成图像。

### API 文档

https://www.runninghub.cn/call-api/api-detail/2001898176946814977?apiType=4

## 安装

```bash
cp -r runninghubskill ~/.openclaw/workspace/skills/
```

## 配置

### 获取凭证

1. 登录 [RunningHub](https://www.runninghub.cn)
2. 头像 → 「API 控制台」获取 **API KEY**
3. 打开目标工作流，复制 **工作流 ID**

### 配置方式

#### 环境变量

```bash
export RUNNINGHUB_API_KEY="your-api-key"
export RUNNINGHUB_WORKFLOW_ID="your-workflow-id"
```

#### Skill 配置

```json
{
  "config": {
    "apiKey": "your-api-key",
    "workflowId": "your-workflow-id"
  }
}
```

## 使用方法

### 基础调用

```python
result = await skill("runninghubskill", {
  "nodeInfoList": [
    {
      "nodeId": "77",
      "fieldName": "image",
      "fieldValue": "参考图文件名.png"
    }
  ]
})
```

### 完整参数

```python
result = await skill("runninghubskill", {
  "nodeInfoList": [
    {
      "nodeId": "77",
      "fieldName": "image",
      "fieldValue": "xxx.png",
      "description": "人物参考图"
    }
  ],
  "workflowId": "2001898176946814977",
  "instanceType": "default",
  "usePersonalQueue": False,
  "poll_interval": 5,
  "timeout": 300
})
```

## 示例

### 示例 1：图生图

```python
result = await skill("runninghubskill", {
  "nodeInfoList": [
    {
      "nodeId": "77",
      "fieldName": "image",
      "fieldValue": "bda1d8aedec56be3899ddb86db33aed5.png"
    }
  ],
  "instanceType": "plus"  # 使用更高配的 GPU
})

print(result)
# {
#   "success": true,
#   "task_id": "2013508786110730241",
#   "status": "completed",
#   "elapsed_seconds": 45,
#   "images": [
#     {"url": "https://rh-images-xxx.cos.ap-beijing.myqcloud.com/xxx.png", "type": "png"}
#   ]
# }
```

### 示例 2：仅提交任务（不等待）

```python
# 设置 poll_interval=0 或 timeout=0 只提交不等待
result = await skill("runninghubskill", {
  "nodeInfoList": [...],
  "poll_interval": 0  # 只提交
})

# 返回:
# {
#   "task_id": "xxx",
#   "status": "RUNNING",
#   "query_url": "https://www.runninghub.cn/openapi/v2/query"
# }
```

### 示例 3：查询任务状态

```python
# 方法 1: 使用辅助函数
status = await queryTask("task_id")

# 方法 2: 手动查询
import requests

response = requests.post(
    "https://www.runninghub.cn/openapi/v2/query",
    json={"taskId": "task_id"},
    headers={"Authorization": "Bearer your-api-key"}
)

print(response.json())
# {
#   "taskId": "xxx",
#   "status": "SUCCESS",
#   "results": [
#     {"url": "https://...", "outputType": "png"}
#   ]
# }
```

## 辅助函数

### `submitTask(params, config)`

仅提交任务，不等待结果。

```python
result = await submitTask({
  "nodeInfoList": [...],
  "workflowId": "xxx"
})
```

### `queryTask(taskId, config)`

查询任务状态。

```python
status = await queryTask("task_id")
# 返回: {success, status, results, usage, ...}
```

## 返回值说明

| 字段 | 类型 | 说明 |
|------|------|------|
| `success` | boolean | 是否成功 |
| `task_id` | string | 任务 ID |
| `status` | string | 状态: RUNNING/QUEUED/SUCCESS/FAILED/timeout |
| `images` | array | 生成的图像列表 |
| `results` | array | 完整输出结果 |
| `elapsed_seconds` | number | 耗时（秒） |
| `usage` | object | 消耗信息 |

## 常见问题

### Q: 如何获取节点 ID？

A: 在 RunningHub 工作流页面，点击节点会显示节点 ID。或者查看 API 文档页面。

### Q: TOKEN_INVALID 错误？

A:
1. API KEY 必须是 32 位字符串
2. 工作流必须在网页端成功运行过至少一次
3. 检查 Authorization 格式: `Bearer {API_KEY}`

### Q: 如何提高生成速度？

A:
- 使用 `instanceType: "default"` (24G显存) 比 `"plus"` 更快排队
- `usePersonalQueue: false` 使用共享队列
- 避开高峰期提交任务

### Q: 图像 URL 过期？

A: RunningHub CDN 链接有效期为 1 天。建议及时下载保存。

## ⚠️ 重要提醒

1. **工作流必须先在网页端成功运行一次**
2. **API Key 安全**：不要分享给他人或提交到公开仓库
3. **费用监控**：关注 RunningHub 账户余额
4. **内容合规**：遵守 RunningHub 使用条款
