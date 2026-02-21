#!/usr/bin/env python3
"""
SiliconFlow TTS 语音合成脚本
支持上传参考音频进行克隆
用法: 
  python3 tts.py "API_KEY" "文本内容" [输出文件] --upload "音频文件" "音频文字内容"
"""

import os
import sys
import requests
import json
import base64

API_BASE = "https://api.siliconflow.cn"

def upload_voice(api_key: str, audio_file: str, text: str, model: str = "fishaudio/fish-speech-1.5") -> str:
    """
    上传参考音频，返回 voice_id
    """
    url = f"{API_BASE}/v1/uploads/audio/voice"
    headers = {"Authorization": f"Bearer {api_key}"}
    
    print(f"上传参考音频: {audio_file}")
    print(f"对应文字: {text}")
    
    with open(audio_file, "rb") as f:
        files = {"file": (os.path.basename(audio_file), f, "audio/wav")}
        data = {
            "model": model,
            "text": text,
        }
        
        resp = requests.post(url, headers=headers, files=files, data=data, timeout=120)
    
    print(f"上传响应: {resp.status_code}")
    
    if resp.status_code == 200:
        result = resp.json()
        print(f"上传成功: {json.dumps(result, indent=2)}")
        
        # 获取 voice_id - 可能是 uri 字段
        voice_id = result.get("uri") or result.get("voice_id")
        
        if voice_id:
            print(f"✅ 获得 voice_id: {voice_id}")
            return voice_id
        else:
            raise Exception(f"未获取到 voice_id: {result}")
    else:
        raise Exception(f"上传失败: {resp.text}")


def tts(api_key: str, text: str, voice_id: str, output_file: str = "output.mp3", model: str = "fishaudio/fish-speech-1.5") -> str:
    """
    使用 voice_id 进行 TTS 合成
    """
    url = f"{API_BASE}/v1/tts"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": model,
        "input": text,
        "voice": voice_id
    }
    
    print(f"调用 TTS 合成...")
    print(f"文本: {text}")
    print(f"voice_id: {voice_id}")
    
    resp = requests.post(url, headers=headers, json=data, timeout=120)
    print(f"TTS 响应: {resp.status_code}")
    
    if resp.status_code == 200:
        result = resp.json()
        
        # 提取音频数据
        audio = None
        if "data" in result:
            data_obj = result["data"]
            if isinstance(data_obj, dict):
                audio = data_obj.get("audio") or data_obj.get("audio_base64")
        
        if audio:
            # 清理 base64 字符串
            audio = audio.strip()
            if "," in audio:
                audio = audio.split(",")[1]
            
            audio_bytes = base64.b64decode(audio)
            
            with open(output_file, "wb") as f:
                f.write(audio_bytes)
            
            size = os.path.getsize(output_file)
            print(f"✅ 语音合成成功: {output_file} ({size} bytes)")
            return output_file
        else:
            raise Exception(f"未获取到音频: {result}")
    else:
        raise Exception(f"TTS 失败: {resp.text}")


def main():
    if len(sys.argv) < 4:
        print("""
用法:
  python3 tts.py "API_KEY" "要合成的文本" output.mp3 --upload "参考音频.mp3" "音频文字内容"

参数说明:
  1. API_KEY      - 硅基流动 API Key
  2. 要合成的文本  - 需要转为语音的文字
  3. output.mp3   - 输出文件路径 (可选，默认 output.mp3)
  4. --upload     - 上传参考音频并合成
  5. 参考音频.mp3 - 参考音频文件路径
  6. 音频文字内容 - 参考音频对应的文字内容

示例:
  python3 tts.py "sk-xxx" "你好世界" "/root/result.mp3" --upload "/tmp/voice.wav" "这是参考音频的文字"
        """)
        sys.exit(1)
    
    api_key = sys.argv[1]
    text = sys.argv[2]
    output_file = "output.mp3"
    audio_file = None
    audio_text = None
    
    # 解析参数
    i = 3
    while i < len(sys.argv):
        if sys.argv[i] == "--upload" and i + 2 < len(sys.argv):
            audio_file = sys.argv[i + 1]
            audio_text = sys.argv[i + 2]
            i += 3
        else:
            output_file = sys.argv[i]
            i += 1
    
    if not audio_file or not audio_text:
        print("错误: 需要提供 --upload 参数和音频文件路径及文字内容")
        sys.exit(1)
    
    try:
        # 1. 上传参考音频
        voice_id = upload_voice(api_key, audio_file, audio_text)
        
        # 2. 使用 voice_id 进行 TTS
        result_file = tts(api_key, text, voice_id, output_file)
        
        print(f"SUCCESS:{result_file}")
        
    except Exception as e:
        print(f"ERROR:{e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
