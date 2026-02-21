#!/usr/bin/env python3
"""
HonnyPhotoV2 Skill - RunningHub 照片生成 V2
工作流 ID: 1994008400960880642
根据文本提示词生成照片，支持自动优化迭代
"""

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
    
    save_dir = get_today_dir()
    cleanup_old_photos()
    
    for attempt in range(max_retries):
        print(f"\n=== Attempt {attempt + 1}/{max_retries} ===")
        
        task_id = submit_task(prompt, width, height)
        if not task_id:
            continue
        
        result = query_task(task_id)
        
        if result.get("status") == "SUCCESS" and result.get("results"):
            image_url = result["results"][0]["url"]
            print(f"Success! Generated image URL: {image_url}")
            
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
