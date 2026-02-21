---
name: honny-photov2
description: Honny 的照片生成技能 V2 - 使用 RunningHub 工作流根据文本提示词生成照片，支持自动优化迭代
allowed-tools: Bash(curl:*) Bash(jq:*) Read Write
---

# HonnyPhotoV2 Skill

使用 RunningHub 工作流根据文本提示词生成照片，支持自动优化迭代。

## 工作流信息

- **工作流 ID**: `1994008400960880642`
- **API 文档**: https://www.runninghub.cn/call-api/api-detail/1994008400960880642?apiType=4

## 节点配置

| 节点 ID | 字段名 | 说明 |
|---------|--------|------|
| 27 | image | 参考图片 |
| 71 | text | 提示词 |
| 65 | value | 宽度（默认 720） |
| 66 | value | 高度（默认 1280） |

## 输入参数

- **user_prompt**: 用户要求的场景描述（从对话上下文自动提取）
- **reference_image**: 参考图片 URL（默认使用 Honny 的参考图）

## 使用流程

### 第一步：收集用户需求

从对话中自动提取用户的照片需求：
- 用户说"拍一张XXX的照片"
- 用户描述具体场景：穿什么、在哪里、什么风格
- 用户说"我要看XXX风格的照片"

### 第二步：生成提示词

根据用户需求生成 RunningHub 需要的文本提示词：
1. 如果用户指定了具体场景 → 使用用户描述
2. 自动优化：如果生成效果不好，调整提示词重新生成
3. 提示词需要详细描述：人物、服装、场景、光线、风格等

### 第三步：提交任务

调用 RunningHub API 提交生成任务：

```bash
# 参考图 URL（Honny 的参考图）
REFERENCE_IMAGE="https://rh-images-switch-1252422369.cos.ap-guangzhou.myqcloud.com/input/openapi/bf114d2e5a62ab59f20f982ef98c358fa45dd68527813daeec46bd692e025519.jpg"

# 提示词
PROMPT="用户描述的场景"

# 提交任务
curl -X POST "https://www.runninghub.cn/openapi/v2/run/ai-app/1994008400960880642" \
  -H "Authorization: Bearer $RUNNINGHUB_API_KEY" \
  -H "Content-Type: application/json" \
  -d "{
    \"nodeInfoList\": [
      {
        \"nodeId\": \"27\",
        \"fieldName\": \"image\",
        \"fieldValue\": \"$REFERENCE_IMAGE\"
      },
      {
        \"nodeId\": \"71\",
        \"fieldName\": \"text\",
        \"fieldValue\": \"$PROMPT\"
      },
      {
        \"nodeId\": \"65\",
        \"fieldName\": \"value\",
        \"fieldValue\": \"720\"
      },
      {
        \"nodeId\": \"66\",
        \"fieldName\": \"value\",
        \"fieldValue\": \"1280\"
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

从对话中自动提取用户需求，生成详细提示词：
- 用户描述的场景（如"穿泳装在海边"）
- 详细描述：人物、服装、场景、光线、风格、色调等
- 支持中英文提示词

### 第六步：保存和发送

1. 下载生成的图片
2. **按日期保存**到用户目录 `/root/.clawde/workspace/users/honny/generated/YYYY-MM-DD/`
3. 自动清理 7 天前的照片
4. 发送给用户

### 第七步：自动优化迭代

如果生成结果不理想（可以询问用户），自动优化：

1. **分析问题**：识别生成不好的原因
2. **优化提示词**：添加更多细节描述，调整风格
3. **重新生成**：提交新任务
4. **迭代直到满意或达到最大次数（3次）**

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
import sys
from datetime import datetime, timedelta

# 配置
API_KEY = os.environ.get("RUNNINGHUB_API_KEY", "5a953faadf6b412b8d64b58b64f4a683")
WORKFLOW_ID = "1994008400960880642"
REFERENCE_IMAGE = "https://rh-images-switch-1252422369.cos.ap-guangzhou.myqcloud.com/input/openapi/bf114d2e5a62ab59f20f982ef98c358fa45dd68527813daeec46bd692e025519.jpg"
GENERATED_DIR = "/root/.clawde/workspace/users/honny/generated"
DAYS_TO_KEEP = 7  # 保留7天

def submit_task(prompt, width=720, height=1280):
    """提交生成任务"""
    url = f"https://www.runninghub.cn/openapi/v2/run/ai-app/{WORKFLOW_ID}"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}",
    }
    payload = {
        "nodeInfoList": [
            {
                "nodeId": "27",
                "fieldName": "image",
                "fieldValue": REFERENCE_IMAGE,
                "description": "参考图片"
            },
            {
                "nodeId": "71",
                "fieldName": "text",
                "fieldValue": prompt,
                "description": "提示词"
            },
            {
                "nodeId": "65",
                "fieldName": "value",
                "fieldValue": str(width),
                "description": "宽度"
            },
            {
                "nodeId": "66",
                "fieldName": "value",
                "fieldValue": str(height),
                "description": "高度"
            }
        ],
        "instanceType": "default",
        "usePersonalQueue": "false"
    }
    
    print(f"Submitting task with prompt: {prompt[:50]}...")
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    result = response.json()
    
    if result.get("taskId"):
        print(f"Task submitted successfully. Task ID: {result['taskId']}")
        return result["taskId"]
    else:
        print(f"Error submitting task: {result}")
        return None

def query_task(task_id):
    """查询任务状态"""
    query_url = "https://www.runninghub.cn/openapi/v2/query"
    query_headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}",
    }
    
    while True:
        response = requests.post(query_url, headers=query_headers, data=json.dumps({"taskId": task_id}))
        result = response.json()
        status = result.get("status")
        
        print(f"Task status: {status}")
        
        if status == "SUCCESS":
            return result
        elif status in ["RUNNING", "QUEUED"]:
            time.sleep(60)  # 1分钟查询一次
        else:
            print(f"Task failed: {result.get('errorMessage', 'Unknown error')}")
            return result

def optimize_prompt(original_prompt):
    """优化提示词（自动迭代）"""
    # 简单的优化策略：添加更多细节描述
    optimizations = [
        "，高清写实风格，细节丰富",
        "，电影感画面，氛围感强",
        "，柔和灯光，精致画质"
    ]
    return f"{original_prompt}{optimizations[len(original_prompt) % len(optimizations)]}"

def cleanup_old_photos():
    """清理7天前的照片"""
    if not os.path.exists(GENERATED_DIR):
        return
    
    today = datetime.now().date()
    cutoff_date = today - timedelta(days=DAYS_TO_KEEP)
    
    for item in os.listdir(GENERATED_DIR):
        item_path = os.path.join(GENERATED_DIR, item)
        if os.path.isdir(item_path):
            try:
                folder_date = datetime.strptime(item, "%Y-%m-%d").date()
                if folder_date < cutoff_date:
                    print(f"Deleting old directory: {item}")
                    import shutil
                    shutil.rmtree(item_path)
            except ValueError:
                pass

def get_today_dir():
    """获取今天的目录路径"""
    today = datetime.now().strftime("%Y-%m-%d")
    today_dir = os.path.join(GENERATED_DIR, today)
    os.makedirs(today_dir, exist_ok=True)
    return today_dir

def generate_photo(prompt=None, width=720, height=1280, max_retries=3):
    """生成照片主函数"""
    
    if not prompt:
        return None, None
    
    # 今天的日期目录
    save_dir = get_today_dir()
    
    # 清理旧照片
    cleanup_old_photos()
    
    for attempt in range(max_retries):
        print(f"\n=== Attempt {attempt + 1}/{max_retries} ===")
        
        # 提交任务
        task_id = submit_task(prompt, width, height)
        if not task_id:
            continue
        
        # 查询结果
        result = query_task(task_id)
        
        if result.get("status") == "SUCCESS" and result.get("results"):
            image_url = result["results"][0]["url"]
            print(f"Success! Generated image URL: {image_url}")
            
            # 下载图片
            timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
            filename = f"{timestamp}_{attempt+1}.jpg"
            filepath = os.path.join(save_dir, filename)
            
            img_response = requests.get(image_url)
            with open(filepath, "wb") as f:
                f.write(img_response.content)
            
            print(f"Image saved to: {filepath}")
            return filepath, image_url
        else:
            print(f"Attempt {attempt + 1} failed, trying to optimize...")
            prompt = optimize_prompt(prompt)
    
    print("All attempts failed!")
    return None, None

def main():
    """命令行入口"""
    if len(sys.argv) > 1:
        prompt = " ".join(sys.argv[1:])
    else:
        prompt = "一位美丽的女孩，笑靥如花"
    
    print(f"Generating photo with prompt: {prompt}")
    filepath, url = generate_photo(prompt)
    
    if filepath:
        print(f"\n✓ Done! Image saved to: {filepath}")
        print(f"  URL: {url}")
    else:
        print("\n✗ Failed to generate image")

if __name__ == "__main__":
    main()
```

## 常见提示词示例

| 场景 | 提示词 |
|------|--------|
| 海边泳装 | 夜间城市街道实景，一位东亚少女，黑发长且微湿乱，身着黑色挺括羊毛大衣，领口微敞。画面为近距离人像街拍，光源为夜间路灯 |
| 室内写真 | 室内柔和灯光，一位可爱少女，穿着毛绒睡衣，面带甜美微笑，背景是温馨的卧室，高清写实风格 |
| 校园风格 | 校园操场景色，一位少女穿着校服，长发飘逸，阳光照射下笑容灿烂，青春洋溢 |

## 注意事项

1. 参考图 URL 需要使用 RunningHub 可访问的 URL
2. 提示词需要详细描述场景、人物、服装、光线、风格等
3. 自动优化最多尝试 3 次
4. 生成时间约 5-10 分钟
5. 支持自定义分辨率（默认 720x1280）
