---
name: honny-photo
description: Honny 的照片生成技能 - 使用 RunningHub 工作流生成指定姿势的照片
allowed-tools: Bash(curl:*) Bash(jq:*) Read Write
---

# HonnyPhoto Skill

使用 RunningHub 工作流生成指定姿势的照片，支持自动优化迭代。

## 工作流信息

- **工作流 ID**: `2017821930283343873`
- **API 文档**: https://www.runninghub.cn/call-api/api-detail/2017821930283343873?apiType=4

## 节点配置

| 节点 ID | 字段名 | 说明 |
|---------|--------|------|
| 166 | image | 参考图片 |
| 182 | value | 姿势提示词 |

## 输入参数

- **user_prompt**: 用户要求的姿势或场景描述（从对话上下文自动提取）
- **reference_image**: 参考图片 URL（默认使用 Honny 的参考图）

## 默认姿势提示词

如果用户没有指定具体姿势，可以使用以下默认提示词：

```
Standing with one hand on the waist and the other hanging naturally, legs apart. Standing frontally with hands naturally near the sides, body slightly relaxed. Standing sideways with one hand on the waist, hair flowing. Raising both hands with palms open, making a greeting gesture. Standing with one hand on the waist, body slightly turned to one side. Squatting with hands near the knees, body leaning forward. Grabbing hair with one hand, head slightly tilted. Standing frontally with hands naturally at the sides, body posture relaxed. Covering the mouth with one hand, making a slightly shy or surprised gesture.
```

## 使用流程

### 第一步：收集用户需求

从对话中自动提取用户的照片需求：
- 用户说"换件衣服"、"换个姿势"、"摆个姿势"
- 用户描述具体场景：穿什么衣服、在哪里、什么姿势
- 用户说"我要看照片"、"发一张"

### 第二步：生成提示词

根据用户需求生成 RunningHub 需要的姿势提示词：
1. 如果用户指定了具体姿势 → 使用用户描述
2. 如果用户只说"换衣服" → 使用默认姿势列表
3. 自动优化：如果生成效果不好，调整提示词重新生成

### 第三步：提交任务

调用 RunningHub API 提交生成任务：

```bash
# 参考图 URL（Honny 的参考图）
REFERENCE_IMAGE="https://rh-images-switch-1252422369.cos.ap-guangzhou.myqcloud.com/input/openapi/bf114d2e5a62ab59f20f982ef98c358fa45dd68527813daeec46bd692e025519.jpg"

# 姿势提示词
POSE_PROMPT="用户指定的姿势描述"

# 提交任务
curl -X POST "https://www.runninghub.cn/openapi/v2/run/ai-app/2017821930283343873" \
  -H "Authorization: Bearer $RUNNINGHUB_API_KEY" \
  -H "Content-Type: application/json" \
  -d "{
    \"nodeInfoList\": [
      {
        \"nodeId\": \"166\",
        \"fieldName\": \"image\",
        \"fieldValue\": \"$REFERENCE_IMAGE\"
      },
      {
        \"nodeId\": \"182\",
        \"fieldName\": \"value\",
        \"fieldValue\": \"$POSE_PROMPT\"
      }
    ],
    \"instanceType\": \"default\"
  }"
```

### 第四步：查询结果

任务提交后，每 1 分钟查询一次状态：

```bash
curl -X POST "https://www.runninghub.cn/openapi/v2/query" \
  -H "Authorization: Bearer $RUNNINGHUB_API_KEY" \
  -H "Content-Type: application/json" \
  -d "{\"taskId\": \"$TASK_ID\"}"
```

**自动检查机制**：
- 每 1 分钟自动查询一次任务状态
- 任务完成后立即下载图片并发送给用户
- 无需手动检查

### 第五步：根据上下文生成提示词

从对话中自动提取用户需求，生成提示词：
- 用户描述的场景（如"泳装"、"职业装"等）
- 每个换行符代表生成一张不同的图片
- 可以一次生成多张不同姿势/表情的照片

### 第五步：自动优化迭代

如果生成结果不理想（可以询问用户），自动优化：

1. **分析问题**：识别生成不好的原因
2. **优化提示词**：调整姿势描述
3. **重新生成**：提交新任务
4. **迭代直到满意或达到最大次数（3次）**

### 第六步：保存和发送

1. 下载生成的图片
2. **按日期保存**到用户目录 `/root/.clawde/workspace/users/honny/generated/YYYY-MM-DD/`
3. 自动清理 7 天前的照片
4. 发送给用户

### 第七步：自动清理

- 每次生成新照片时，自动检查并删除 7 天前的目录
- 保留最新 7 天的照片

## 环境变量

- `RUNNINGHUB_API_KEY`: RunningHub API 密钥（已在配置中）
- `REFERENCE_IMAGE_URL`: 参考图 URL

## 技术实现

### Python 实现

```python
import os
import requests
import json
import time

API_KEY = os.environ.get("RUNNINGHUB_API_KEY", "5a953faadf6b412b8d64b58b64f4a683")
WORKFLOW_ID = "2017821930283343873"
REFERENCE_IMAGE = "https://rh-images-switch-1252422369.cos.ap-guangzhou.myqcloud.com/input/openapi/bf114d2e5a62ab59f20f982ef98c358fa45dd68527813daeec46bd692e025519.jpg"

def submit_task(pose_prompt):
    url = f"https://www.runninghub.cn/openapi/v2/run/ai-app/{WORKFLOW_ID}"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}",
    }
    payload = {
        "nodeInfoList": [
            {
                "nodeId": "166",
                "fieldName": "image",
                "fieldValue": REFERENCE_IMAGE,
                "description": "参考图片"
            },
            {
                "nodeId": "182",
                "fieldName": "value",
                "fieldValue": pose_prompt,
                "description": "姿势提示词"
            }
        ],
        "instanceType": "default",
        "usePersonalQueue": "false"
    }
    
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    result = response.json()
    return result.get("taskId")

def query_task(task_id):
    query_url = "https://www.runninghub.cn/openapi/v2/query"
    query_headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}",
    }
    
    while True:
        response = requests.post(query_url, headers=query_headers, data=json.dumps({"taskId": task_id}))
        result = response.json()
        status = result["status"]
        
        if status == "SUCCESS":
            return result
        elif status in ["RUNNING", "QUEUED"]:
            time.sleep(5)
        else:
            return result

def generate_photo(pose_prompt, max_retries=3):
    for attempt in range(max_retries):
        task_id = submit_task(pose_prompt)
        print(f"Task submitted: {task_id}")
        
        result = query_task(task_id)
        
        if result.get("status") == "SUCCESS" and result.get("results"):
            return result["results"][0]["url"]
        else:
            print(f"Attempt {attempt + 1} failed, trying to optimize...")
            pose_prompt = optimize_prompt(pose_prompt)
    
    return None
```

## 常见姿势提示词示例

| 场景 | 提示词 |
|------|--------|
| 日常站姿 | Standing with one hand on the waist and the other hanging naturally, legs apart |
| 正面照 | Standing frontally with hands naturally near the sides, body slightly relaxed |
| 侧身照 | Standing sideways with one hand on the waist, hair flowing |
| 招手 | Raising both hands with palms open, making a greeting gesture |
| 叉腰 | Standing with one hand on the waist, body slightly turned to one side |
| 蹲姿 | Squatting with hands near the knees, body leaning forward |
| 撩头发 | Grabbing hair with one hand, head slightly tilted |
| 捂嘴 | Covering the mouth with one hand, making a slightly shy or surprised gesture |

## 注意事项

1. 参考图 URL 需要使用 RunningHub 可访问的 URL
2. 姿势提示词可以用英文描述
3. 自动优化最多尝试 3 次
4. 生成时间约 5-10 分钟
