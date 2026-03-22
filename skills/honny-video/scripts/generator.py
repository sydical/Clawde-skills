#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import json
import time
import requests
from datetime import datetime

# 配置
SKILL_DIR = os.path.dirname(os.path.abspath(__file__))
WORKFLOW_ID = os.environ.get('WORKFLOW_ID', '2016727774387511297')
MEMORY_DIR = os.path.expanduser('~/data/disk/workspace/memory')
MAX_RETRIES = int(os.environ.get('MAX_RETRIES', '5'))
RETRY_DELAY_MS = int(os.environ.get('RETRY_DELAY_MS', '60000'))
POLL_INTERVAL = int(os.environ.get('POLL_INTERVAL', '60'))  # 轮询间隔（秒）


class HonnyVideo:
    """Honny Video 生成器 - 图生视频"""
    
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://www.runninghub.cn"
        self.run_url = f"{self.base_url}/openapi/v2/run/ai-app/{WORKFLOW_ID}"
        self.query_url = f"{self.base_url}/openapi/v2/query"
        
    def get_headers(self):
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
    
    def get_today_memory_file(self):
        """获取当天记忆文件"""
        today = datetime.now().strftime("%Y-%m-%d")
        return os.path.join(MEMORY_DIR, f"{today}.md")
    
    def get_reference_from_memory(self):
        """从记忆获取参考图 URL"""
        memory_file = self.get_today_memory_file()
        if not os.path.exists(memory_file):
            return None
        
        with open(memory_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 查找参考图 URL
        for line in content.split('\n'):
            if '参考图URL' in line:
                parts = line.split('http')
                if len(parts) > 1:
                    return 'http' + parts[1].split()[0]
        return None
    
    def submit_task(self, image_url, prompt):
        """提交图生视频任务"""
        print(f"🎬 正在提交视频生成任务...")
        print(f"📷 图片: {image_url[:60]}...")
        print(f"📝 提示词: {prompt}")
        
        payload = {
            "nodeInfoList": [
                {
                    "nodeId": "106",
                    "fieldName": "image",
                    "fieldValue": image_url,
                    "description": "传图"
                },
                {
                    "nodeId": "6",
                    "fieldName": "text",
                    "fieldValue": prompt,
                    "description": "言出法随"
                }
            ],
            "instanceType": "default",
            "usePersonalQueue": "false"
        }
        
        # 带重试机制
        for attempt in range(MAX_RETRIES):
            response = requests.post(
                self.run_url, 
                headers=self.get_headers(), 
                data=json.dumps(payload),
                timeout=30
            )
            
            if response.status_code != 200:
                print(f"❌ 请求失败: {response.status_code}")
                time.sleep(RETRY_DELAY_MS / 1000)
                continue
            
            result = response.json()
            
            # 检查队列是否满 (errorCode 421)
            if result.get('errorCode') == '421':
                wait_seconds = RETRY_DELAY_MS / 1000
                print(f"⏳ 队列已满，{wait_seconds}秒后重试 ({attempt + 1}/{MAX_RETRIES})...")
                time.sleep(RETRY_DELAY_MS / 1000)
                continue
            
            if result.get('errorCode'):
                print(f"❌ API错误: {result.get('errorMessage')}")
                return None
            
            if result.get('taskId'):
                task_id = result['taskId']
                print(f"✅ 任务ID: {task_id}")
                return task_id
        
        print(f"❌ 提交失败，已重试{MAX_RETRIES}次")
        return None
    
    def wait_for_result(self, task_id, max_wait=600, auto_download=True):
        """等待视频生成完成
        
        Args:
            task_id: 任务ID
            max_wait: 最大等待时间（秒）
            auto_download: 是否自动下载视频到本地
        """
        print(f"⏳ 等待生成中（每{POLL_INTERVAL}秒查询进度）...")
        start_time = time.time()
        last_progress = 0
        
        while time.time() - start_time < max_wait:
            response = requests.post(
                self.query_url,
                headers=self.get_headers(),
                data=json.dumps({"taskId": task_id}),
                timeout=30
            )
            
            if response.status_code != 200:
                time.sleep(POLL_INTERVAL)
                continue
            
            result = response.json()
            
            # 检查是否有 data 字段
            if 'data' not in result:
                time.sleep(POLL_INTERVAL)
                continue
            
            data = result['data']
            status = data.get('status')
            progress = data.get('progress', 0)
            
            # 只在进度变化时打印
            if progress != last_progress:
                elapsed = time.time() - start_time
                print(f"⏳ 进度: {progress}% ({elapsed:.0f}秒)")
                last_progress = progress
            
            if status == "SUCCESS":
                elapsed = time.time() - start_time
                print(f"✅ 生成完成！耗时: {elapsed:.1f}秒")
                
                outputs = data.get('outputs', [])
                if outputs and len(outputs) > 0:
                    video_url = outputs[0].get('url')
                    
                    # 自动下载视频
                    if auto_download and video_url:
                        local_path = self.download_video(video_url, task_id)
                        return {
                            "video_url": video_url,
                            "local_path": local_path
                        }
                    return video_url
                return None
            
            elif status == "FAILED":
                error = data.get('errorMessage', '未知错误')
                print(f"❌ 生成失败: {error}")
                return None
            
            else:
                time.sleep(POLL_INTERVAL)
        
        print("⏰ 等待超时")
        return None
    
    def download_video(self, video_url, task_id):
        """下载视频到本地"""
        try:
            print(f"📥 正在下载视频...")
            
            output_dir = os.path.join(SKILL_DIR, "outputs")
            os.makedirs(output_dir, exist_ok=True)
            
            # 生成文件名
            filename = f"video_{task_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4"
            output_path = os.path.join(output_dir, filename)
            
            # 下载视频
            response = requests.get(video_url, timeout=300, stream=True)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            
            with open(output_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total_size > 0:
                            pct = downloaded * 100 / total_size
                            if downloaded % (1024 * 1024 * 10) == 0:  # 每10MB打印一次
                                print(f"📥 下载进度: {pct:.1f}%")
            
            print(f"✅ 视频已保存到: {output_path}")
            return output_path
            
        except Exception as e:
            print(f"❌ 下载失败: {e}")
            return None
    
    def generate(self, image_url, prompt, auto_download=True):
        """生成视频
        
        Args:
            image_url: 参考图URL
            prompt: 提示词
            auto_download: 是否自动下载视频到本地
        """
        # 1. 提交任务
        task_id = self.submit_task(image_url, prompt)
        if not task_id:
            return None
        
        # 2. 等待结果（自动下载）
        result = self.wait_for_result(task_id, auto_download=auto_download)
        
        # 处理返回结果
        if isinstance(result, dict):
            return {
                "video_url": result.get("video_url"),
                "local_path": result.get("local_path"),
                "prompt": prompt,
                "task_id": task_id
            }
        else:
            return {
                "video_url": result,
                "local_path": None,
                "prompt": prompt,
                "task_id": task_id
            }


def main():
    """测试"""
    api_key = os.environ.get('RUNNINGHUB_API_KEY')
    if not api_key:
        print("❌ 请设置 RUNNINGHUB_API_KEY 环境变量")
        sys.exit(1)
    
    generator = HonnyVideo(api_key)
    
    # 测试生成
    prompt = "一个女孩在玩耍"
    image_url = "test_image_url.png"
    
    result = generator.generate(image_url, prompt)
    
    if result and result.get('video_url'):
        print(f"\n🎉 生成成功!")
        print(f"🎥 视频: {result['video_url']}")
    else:
        print("\n❌ 生成失败")


if __name__ == '__main__':
    main()
