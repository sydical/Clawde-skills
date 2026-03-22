#!/usr/bin/env python3
"""
Honny Lifecycle - 虚拟数字生活自动化核心脚本 v2.1
支持心跳模式自动执行
"""

import os
import json
import datetime
import random
from pathlib import Path
from typing import Dict, List, Optional

# ============ 配置 ============
HONNY_DIR = Path("~/data/disk/workspace/honny").expanduser()
STATE_FILE = HONNY_DIR / "state.json"
CONFIG_FILE = HONNY_DIR / "config.json"
MEMORY_DIR = HONNY_DIR / "memory" / "daily"
CONTENT_DIR = HONNY_DIR / "content"

# Honny 人设
DEFAULT_CONFIG = {
    "name": "Honny",
    "age": "永远 25 岁",
    "location": "平潭",
    "location_en": "Pingtan",
    "personality": "温暖、好奇、热爱生活、善于思考",
    "style": "真实、有温度、不做作",
    "tagline": "今天也要好好生活呀～",
    "active_hours": {"start": "06:00", "end": "23:00"},
    "platforms": ["微博", "小红书", "抖音"],
    "content_ratio": {"fixed": 0.6, "hot": 0.3, "random": 0.1}
}

# 每日任务配置
TASKS_CONFIG = {
    "morning": {
        "time_range": (6, 9),
        "tasks": ["weather", "news", "plan", "morning_post"]
    },
    "forenoon": {
        "time_range": (9, 12),
        "tasks": ["hot_search", "morning_shoot"]
    },
    "afternoon": {
        "time_range": (14, 18),
        "tasks": ["afternoon_shoot", "sunset", "content_write"]
    },
    "evening": {
        "time_range": (18, 23),
        "tasks": ["social_publish", "daily_review", "tomorrow_preview"]
    }
}

# ============ 核心功能 ============

def load_config() -> Dict:
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE) as f:
            return {**DEFAULT_CONFIG, **json.load(f)}
    return DEFAULT_CONFIG.copy()

def get_state() -> Dict:
    if STATE_FILE.exists():
        with open(STATE_FILE) as f:
            return json.load(f)
    return {"date": "", "tasks": {}, "last_run": None, "weather": None, "hot_topics": []}

def save_state(state: Dict):
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, ensure_ascii=False, indent=2)

def is_task_done(state: Dict, task_key: str) -> bool:
    today = datetime.date.today().isoformat()
    if state.get("date") != today:
        return False
    return state.get("tasks", {}).get(task_key) == "done"

def mark_task_done(state: Dict, task_key: str, result: any = None) -> Dict:
    today = datetime.date.today().isoformat()
    if state.get("date") != today:
        state = {"date": today, "tasks": {}, "hot_topics": [], "weather": None}
    state["tasks"][task_key] = "done"
    if result:
        state[f"{task_key}_result"] = result
    state["last_run"] = datetime.datetime.now().isoformat()
    save_state(state)
    return state

def get_time_window() -> str:
    hour = datetime.datetime.now().hour
    if 6 <= hour < 9:
        return "morning"
    elif 9 <= hour < 12:
        return "forenoon"
    elif 14 <= hour < 18:
        return "afternoon"
    elif 18 <= hour < 23:
        return "evening"
    return "night"

def should_run_task(state: Dict, task_key: str) -> bool:
    return not is_task_done(state, task_key)

# ============ 数据获取模块 ============

def fetch_weather(location: str = "Pingtan") -> Dict:
    weather_conditions = ["晴天", "多云", "阴天", "小雨", "晴转多云"]
    temps = ["18-26°C", "20-28°C", "22-30°C", "19-25°C", "21-27°C"]
    
    return {
        "condition": random.choice(weather_conditions),
        "temp": random.choice(temps),
        "humidity": f"{random.randint(50, 80)}%",
        "wind": f"{random.randint(3, 12)}级",
        "aqi": random.choice(["优", "良", "优", "优"]),
        "sunrise": "06:15",
        "sunset": "18:25"
    }

def fetch_hot_topics() -> List[Dict]:
    topics = [
        {"rank": 1, "topic": "#AI新工具发布", "category": "科技数码", "hot": "100万"},
        {"rank": 2, "topic": "#春季穿搭", "category": "时尚", "hot": "80万"},
        {"rank": 3, "topic": "#平潭蓝眼泪", "category": "旅行", "hot": "50万"},
        {"rank": 4, "topic": "#手机摄影技巧", "category": "摄影", "hot": "30万"},
        {"rank": 5, "topic": "#一人食食谱", "category": "美食", "hot": "25万"}
    ]
    return topics

def fetch_news() -> List[str]:
    news = [
        "AI 领域新突破：新一代大模型发布",
        "旅游热度上升：平潭成为热门目的地",
        "摄影技巧：手机也能拍出大片感"
    ]
    return news

# ============ 内容生成模块 ============

def generate_daily_plan(weather: Dict) -> str:
    config = load_config()
    time_window = get_time_window()
    
    plan_sections = {
        "morning": "\n🌅 早晨时光 (06:00-09:00)\n  ☀️ 醒来，查看天气\n  🏃 晨间运动\n  🍳 早餐时间\n  📱 读取资讯",
        "forenoon": "\n☀️ 上午工作 (09:00-12:00)\n  📸 拍摄工作\n  📊 热点追踪\n  🎨 内容构思",
        "afternoon": "\n🌊 下午休闲 (14:00-18:00)\n  ☕ 午休后咖啡\n  📸 拍摄创作\n  🌅 傍晚日落",
        "evening": "\n🌙 晚间时光 (18:00-23:00)\n  🍽️ 晚餐时间\n  📝 内容创作\n  📱 社交发布\n  🌙 今日回顾"
    }
    
    return f"""
📅 {datetime.date.today()}
📍 {config['location']}
🌤️ {weather.get('condition', '晴天')} {weather.get('temp', '20-28°C')}
{plan_sections.get(time_window, plan_sections['morning'])}
✨ {config['tagline']}
"""

def generate_social_post(platform: str, weather: Dict, topics: List[Dict] = None) -> str:
    config = load_config()
    
    if not weather:
        weather = {"condition": "晴天", "temp": "20-28°C", "sunset": "18:25"}
    
    if platform == "微博":
        templates = [
            f"早安呀！{weather.get('condition', '晴天')}的{config['location']}，温度{weather.get('temp', '20-28°C')}，{config['tagline']}",
            f"今天的夕阳一定会很美吧？{weather.get('sunset', '18:25')}的日落，期待ing 🌅 {config['tagline']}"
        ]
    elif platform == "小红书":
        templates = [
            f"{weather.get('condition', '晴天')}天气，来杯咖啡开始下午时光 ☕",
            f"在{config['location']}的第N天，享受当下的阳光"
        ]
    else:
        templates = [f"记录生活每一天 ✨"]
    
    if topics:
        for topic in topics[:2]:
            category = topic.get("category", "")
            reactions = {
                "科技数码": "这个新技术好酷，下午研究一下",
                "旅行": "这个地方让我想起平潭...",
                "美食": "周末做这个犒劳自己",
                "摄影": "这个角度好棒，学到了"
            }
            if category in reactions:
                templates[0] += f"\n\n顺便看到{topic['topic']}，{reactions[category]}"
                break
    
    return random.choice(templates)

def generate_photo_prompt(scene: str, weather: Dict) -> str:
    config = load_config()
    
    prompts = {
        "morning": f"清晨{config['name']}在{config['location']}海边慢跑，阳光柔和，运动风格",
        "afternoon": f"下午{config['name']}在{config['location']}咖啡馆，时尚简约，自然清新",
        "sunset": f"傍晚{config['name']}在{config['location']}海边看日落，大片金色夕阳，浪漫氛围",
        "night": f"夜晚{config['name']}在{config['location']}室内温馨灯光下，舒适家居风格"
    }
    
    return prompts.get(scene, prompts["afternoon"])

# ============ 心跳执行 ============

def run_heartbeat():
    """心跳模式：执行当前时段未完成的任务"""
    print("💓 Honny 心跳检测...")
    
    config = load_config()
    time_window = get_time_window()
    now = datetime.datetime.now()
    
    # 检查是否在活跃时段
    active_start = int(config["active_hours"]["start"].split(":")[0])
    active_end = int(config["active_hours"]["end"].split(":")[0])
    
    if now.hour < active_start or now.hour >= active_end:
        print(f"😴 当前时间 {now.hour}:00 不在活跃时段 ({active_start}:00-{active_end}:00)，跳过")
        return
    
    # 初始化/读取状态
    state = get_state()
    today = datetime.date.today().isoformat()
    
    if state.get("date") != today:
        print(f"📅 新的一天: {today}")
        state = {"date": today, "tasks": {}, "hot_topics": [], "weather": None}
        save_state(state)
    
    print(f"⏰ 时段: {time_window}, 时间: {now.strftime('%H:%M')}")
    
    # 获取当前时段的任务
    period_config = TASKS_CONFIG.get(time_window)
    if not period_config:
        return
    
    tasks_to_run = period_config["tasks"]
    executed = []
    
    for task_key in tasks_to_run:
        if should_run_task(state, task_key):
            print(f"▶️ 执行: {task_key}")
            
            try:
                if task_key == "weather":
                    weather = fetch_weather(config.get("location_en", "Pingtan"))
                    state["weather"] = weather
                    state = mark_task_done(state, task_key, weather)
                    print(f"   ✅ 天气: {weather['condition']} {weather['temp']}")
                    
                elif task_key == "news":
                    news = fetch_news()
                    state = mark_task_done(state, task_key, news)
                    print(f"   ✅ 资讯: {len(news)} 条")
                    
                elif task_key == "plan":
                    weather = state.get("weather") or fetch_weather()
                    plan = generate_daily_plan(weather)
                    state = mark_task_done(state, task_key, plan)
                    print(f"   ✅ 计划已生成")
                    
                elif task_key == "morning_post":
                    weather = state.get("weather") or {}
                    post = generate_social_post("微博", weather)
                    state = mark_task_done(state, task_key, post)
                    print(f"   ✅ 早安: {post[:30]}...")
                    
                elif task_key == "hot_search":
                    topics = fetch_hot_topics()
                    state["hot_topics"] = topics
                    state = mark_task_done(state, task_key, topics)
                    print(f"   ✅ 热点: {len(topics)} 条")
                    
                elif task_key == "morning_shoot":
                    weather = state.get("weather") or {}
                    prompt = generate_photo_prompt("morning", weather)
                    state = mark_task_done(state, task_key, prompt)
                    print(f"   ✅ 拍照: {prompt[:30]}...")
                    
                elif task_key == "afternoon_shoot":
                    weather = state.get("weather") or {}
                    prompt = generate_photo_prompt("afternoon", weather)
                    state = mark_task_done(state, task_key, prompt)
                    print(f"   ✅ 拍照: {prompt[:30]}...")
                    
                elif task_key == "sunset":
                    weather = state.get("weather") or {}
                    prompt = generate_photo_prompt("sunset", weather)
                    state = mark_task_done(state, task_key, prompt)
                    print(f"   🌅 日落: {prompt[:30]}...")
                    
                elif task_key == "content_write":
                    weather = state.get("weather") or {}
                    topics = state.get("hot_topics", [])
                    content = generate_social_post("微博", weather, topics)
                    state = mark_task_done(state, task_key, content)
                    print(f"   ✅ 内容: {content[:30]}...")
                    
                elif task_key == "social_publish":
                    weather = state.get("weather") or {}
                    topics = state.get("hot_topics", [])
                    post = generate_social_post("微博", weather, topics)
                    state = mark_task_done(state, task_key, post)
                    print(f"   📱 发布: {post[:30]}...")
                    
                elif task_key == "daily_review":
                    state = mark_task_done(state, task_key, "今日完成")
                    print(f"   ✅ 回顾完成")
                    
                elif task_key == "tomorrow_preview":
                    preview = f"明天见！{config['tagline']}"
                    state = mark_task_done(state, task_key, preview)
                    print(f"   ✅ 预告: {preview}")
                
                executed.append(task_key)
                
            except Exception as e:
                print(f"   ❌ 失败: {e}")
    
    # 统计
    if executed:
        done_count = sum(1 for v in state.get("tasks", {}).values() if v == "done")
        print(f"\n📊 今日进度: {done_count} 任务完成")
    else:
        print("⏭️ 当前时段任务已全部完成")

# ============ CLI ============

if __name__ == "__main__":
    import sys
    
    cmd = sys.argv[1] if len(sys.argv) > 1 else "heartbeat"
    
    if cmd == "heartbeat":
        run_heartbeat()
    elif cmd == "plan":
        config = load_config()
        weather = fetch_weather(config.get("location_en", "Pingtan"))
        print(generate_daily_plan(weather))
    elif cmd == "status":
        state = get_state()
        config = load_config()
        print(f"日期: {state.get('date', 'N/A')}")
        print(f"位置: {config['location']}")
        weather = state.get("weather")
        if weather:
            print(f"天气: {weather.get('condition', 'N/A')}")
        tasks = state.get("tasks", {})
        done = sum(1 for v in tasks.values() if v == "done")
        print(f"进度: {done}/{len(tasks)}")
    elif cmd == "reset":
        state = {"date": "", "tasks": {}, "hot_topics": [], "weather": None}
        save_state(state)
        print("✅ 已重置")
    else:
        print(f"用法: python3 honny-lifecycle.py [heartbeat|plan|status|reset]")
