#!/usr/bin/env python3
"""
HonnyPhoto Skill - RunningHub 照片生成
工作流 ID: 2017821930283343873
按日期保存，7天后自动删除
"""

import os
import requests
import json
import time
import sys
from datetime import datetime, timedelta

# 配置
API_KEY = os.environ.get("RUNNINGHUB_API_KEY", "5a953faadf6b412b8d64b58b64f4a683")
WORKFLOW_ID = "2017821930283343873"
REFERENCE_IMAGE = "https://rh-images-switch-1252422369.cos.ap-guangzhou.myqcloud.com/input/openapi/bf114d2e5a62ab59f20f982ef98c358fa45dd68527813daeec46bd692e025519.jpg"
GENERATED_DIR = "/root/.clawde/workspace/users/honny/generated"
DAYS_TO_KEEP = 7  # 保留7天

# 默认姿势列表
DEFAULT_POSES = [
    "Standing with one hand on the waist and the other hanging naturally, legs apart",
    "Standing frontally with hands naturally near the sides, body slightly relaxed",
    "Standing sideways with one hand on the waist, hair flowing",
    "Raising both hands with palms open, making a greeting gesture",
    "Standing with one hand on the waist, body slightly turned to one side",
    "Squatting with hands near the knees, body leaning forward",
    "Grabbing hair with one hand, head slightly tilted",
    "Standing frontally with hands naturally at the sides, body posture relaxed",
    "Covering the mouth with one hand, making a slightly shy or surprised gesture"
]

def submit_task(pose_prompt):
    """提交生成任务"""
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
    
    print(f"Submitting task with prompt: {pose_prompt[:50]}...")
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
            time.sleep(5)
        else:
            print(f"Task failed: {result.get('errorMessage', 'Unknown error')}")
            return result

def optimize_prompt(original_prompt):
    """优化提示词（自动迭代）"""
    # 简单的优化策略：添加更多细节描述
    optimizations = [
        "posing gracefully, soft lighting, professional photography style",
        "looking at camera, confident smile, natural pose",
        "casual style, relaxed atmosphere, aesthetic composition"
    ]
    return f"{original_prompt}, {optimizations[len(original_prompt) % len(optimizations)]}"

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
                # 解析目录名（如 2026-02-21）
                folder_date = datetime.strptime(item, "%Y-%m-%d").date()
                if folder_date < cutoff_date:
                    print(f"Deleting old directory: {item}")
                    import shutil
                    shutil.rmtree(item_path)
            except ValueError:
                # 不是日期格式的目录，跳过
                pass

def get_today_dir():
    """获取今天的目录路径"""
    today = datetime.now().strftime("%Y-%m-%d")
    today_dir = os.path.join(GENERATED_DIR, today)
    os.makedirs(today_dir, exist_ok=True)
    return today_dir

def generate_photo(pose_prompt=None, max_retries=3, save_dir=None):
    """生成照片主函数"""
    
    # 如果没有提供姿势，使用默认姿势
    if not pose_prompt:
        pose_prompt = ". ".join(DEFAULT_POSES)
    
    # 使用今天的日期目录
    if save_dir is None:
        save_dir = get_today_dir()
    
    # 清理旧照片
    cleanup_old_photos()
    
    for attempt in range(max_retries):
        print(f"\n=== Attempt {attempt + 1}/{max_retries} ===")
        
        # 提交任务
        task_id = submit_task(pose_prompt)
        if not task_id:
            continue
        
        # 查询结果
        result = query_task(task_id)
        
        if result.get("status") == "SUCCESS" and result.get("results"):
            image_url = result["results"][0]["url"]
            print(f"Success! Generated image URL: {image_url}")
            
            # 下载图片
            os.makedirs(save_dir, exist_ok=True)
            timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
            filename = f"{timestamp}_{attempt+1}.png"
            filepath = os.path.join(save_dir, filename)
            
            img_response = requests.get(image_url)
            with open(filepath, "wb") as f:
                f.write(img_response.content)
            
            print(f"Image saved to: {filepath}")
            return filepath, image_url
        else:
            print(f"Attempt {attempt + 1} failed, trying to optimize...")
            pose_prompt = optimize_prompt(pose_prompt)
    
    print("All attempts failed!")
    return None, None

def main():
    """命令行入口"""
    if len(sys.argv) > 1:
        pose_prompt = " ".join(sys.argv[1:])
    else:
        pose_prompt = ". ".join(DEFAULT_POSES)
    
    print(f"Generating photo with prompt: {pose_prompt}")
    filepath, url = generate_photo(pose_prompt)
    
    if filepath:
        print(f"\n✓ Done! Image saved to: {filepath}")
        print(f"  URL: {url}")
    else:
        print("\n✗ Failed to generate image")

if __name__ == "__main__":
    main()
