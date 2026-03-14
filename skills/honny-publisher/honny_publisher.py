#!/usr/bin/env python3
"""
honny-publisher - 小红书发布器 v2.0
基于 xiaohongshu-mcp 优化
"""

import json
import os
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

# 配置
SESSION_DIR = Path.home() / ".honny-publisher" / "sessions"
SESSION_FILE = SESSION_DIR / "xhs.json"
DATA_DIR = Path.home() / ".honny-publisher" / "data"

SESSION_DIR.mkdir(parents=True, exist_ok=True)
DATA_DIR.mkdir(parents=True, exist_ok=True)


def get_session():
    """获取已保存的会话"""
    if SESSION_FILE.exists():
        with open(SESSION_FILE) as f:
            return json.load(f)
    return None


def save_session(context, path=None):
    """保存会话"""
    save_path = path or SESSION_FILE
    context.storage_state(path=str(save_path))
    print(f"✅ 会话已保存: {save_path}")


def new_browser_context():
    """创建新的浏览器上下文"""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1920, "height": 1080}
        )
        return p, browser, context


def login(headless=True):
    """
    登录小红书（创作服务平台）
    使用 creator.xiaohongshu.com 避免被拦截
    """
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1920, "height": 1080}
        )
        page = context.new_page()
        
        # 尝试访问创作服务平台
        page.goto("https://creator.xiaohongshu.com")
        page.wait_for_timeout(3000)
        
        # 检查是否已登录
        if page.locator(".user-name").count() > 0 or page.locator(".user-info").count() > 0:
            print("✅ 已登录!")
            save_session(context)
            browser.close()
            return True
        
        if headless:
            # 保存二维码
            qr_path = SESSION_DIR / "qr.png"
            page.screenshot(path=str(qr_path), full_page=True)
            print(f"📱 二维码已保存: {qr_path}")
            print("请扫码登录（120秒内）...")
            
            # 等待登录 - 使用更长的超时
            for i in range(24):
                time.sleep(5)
                if page.locator(".user-name").count() > 0 or page.locator(".user-info").count() > 0:
                    print("✅ 登录成功!")
                    save_session(context)
                    browser.close()
                    return True
            print("❌ 登录超时")
        else:
            print("🌐 请在浏览器中登录...")
            page.wait_for_event("close", timeout=300000)
            save_session(context)
        
        browser.close()
        return False


def check_login():
    """检查登录状态"""
    session = get_session()
    if not session:
        print("❌ 未找到会话，请先运行 login")
        return False
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(storage_state=session)
        page = context.new_page()
        
        try:
            page.goto("https://creator.xiaohongshu.com", timeout=10000)
            page.wait_for_timeout(3000)
            
            # 检查多种登录元素
            logged_in = (
                page.locator(".user-name").count() > 0 or
                page.locator(".user-info").count() > 0 or
                page.locator(".avatar").count() > 0
            )
            
            browser.close()
            return logged_in
        except Exception as e:
            print(f"❌ 检查失败: {e}")
            browser.close()
            return False


def search(keyword, limit=10, sort_by="综合", note_type="不限"):
    """
    搜索小红书内容
    
    Args:
        keyword: 搜索关键词
        limit: 返回数量
        sort_by: 排序方式 (综合/最新/最多点赞/最多评论/最多收藏)
        note_type: 笔记类型 (不限/视频/图文)
    """
    session = get_session()
    if not session:
        print("❌ 未登录，请先运行 login")
        return []
    
    results = []
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(storage_state=session)
        page = context.new_page()
        
        try:
            # 使用搜索结果页面
            search_url = f"https://www.xiaohongshu.com/search_result?keyword={keyword}&type=51"
            page.goto(search_url)
            page.wait_for_timeout(5000)
            
            # 检查是否被拦截
            if "login" in page.url or "error" in page.url:
                print("⚠️ 需要重新登录")
                browser.close()
                return []
            
            # 获取搜索结果
            # 小红书搜索结果使用动态加载
            notes = page.locator(".note-item").all()[:limit]
            
            for note in notes:
                try:
                    title = note.locator(".title").inner_text()
                    author = note.locator(".author").inner_text()
                    link = note.locator("a").get_attribute("href")
                    
                    results.append({
                        "title": title,
                        "author": author,
                        "link": f"https://www.xiaohongshu.com{link}" if link else ""
                    })
                except:
                    pass
            
            browser.close()
            return results
            
        except Exception as e:
            print(f"❌ 搜索失败: {e}")
            browser.close()
            return []


def get_feed(limit=10):
    """
    获取首页推荐内容
    """
    session = get_session()
    if not session:
        print("❌ 未登录，请先运行 login")
        return []
    
    results = []
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(storage_state=session)
        page = context.new_page()
        
        try:
            page.goto("https://www.xiaohongshu.com/explore")
            page.wait_for_timeout(5000)
            
            if "login" in page.url or "error" in page.url:
                print("⚠️ 需要重新登录")
                browser.close()
                return []
            
            notes = page.locator(".note-item").all()[:limit]
            
            for note in notes:
                try:
                    title = note.locator(".title").inner_text()
                    author = note.locator(".author").inner_text()
                    link = note.locator("a").get_attribute("href")
                    
                    results.append({
                        "title": title,
                        "author": author,
                        "link": f"https://www.xiaohongshu.com{link}" if link else ""
                    })
                except:
                    pass
            
            browser.close()
            return results
            
        except Exception as e:
            print(f"❌ 获取推荐失败: {e}")
            browser.close()
            return []


def get_note_detail(url):
    """
    获取笔记详情
    """
    session = get_session()
    if not session:
        print("❌ 未登录，请先运行 login")
        return None
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(storage_state=session)
        page = context.new_page()
        
        try:
            page.goto(url, wait_until='networkidle')
            page.wait_for_timeout(3000)
            
            detail = {
                "title": "",
                "content": "",
                "author": "",
                "likes": "0",
                "collects": "0"
            }
            
            try:
                detail["title"] = page.locator(".title").inner_text()
            except:
                pass
            
            try:
                detail["content"] = page.locator(".content").inner_text()
            except:
                pass
            
            try:
                detail["author"] = page.locator(".author-name").inner_text()
            except:
                pass
            
            try:
                detail["likes"] = page.locator(".like-count").inner_text()
            except:
                pass
            
            try:
                detail["collects"] = page.locator(".collect-count").inner_text()
            except:
                pass
            
            browser.close()
            return detail
            
        except Exception as e:
            print(f"❌ 获取详情失败: {e}")
            browser.close()
            return None


def publish_image(title, content, images, tags=None):
    """
    发布图文笔记（创作服务平台）
    
    Args:
        title: 标题
        content: 正文内容
        images: 图片路径列表
        tags: 标签列表
    """
    session = get_session()
    if not session:
        print("❌ 未登录，请先运行 login")
        return False
    
    if not images:
        print("❌ 图片不能为空")
        return False
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(storage_state=session)
        page = context.new_page()
        
        try:
            # 访问发布页面
            page.goto("https://creator.xiaohongshu.com/publish/publish?source=official")
            page.wait_for_timeout(5000)
            
            # 点击上传图文 Tab
            try:
                page.locator("div.upload-content").wait_for(timeout=5000)
                page.locator("text=上传图文").click()
                page.wait_for_timeout(2000)
            except:
                print("⚠️ 点击上传图文失败，尝试直接上传")
            
            # 上传图片
            for i, img_path in enumerate(images):
                if not os.path.exists(img_path):
                    print(f"⚠️ 图片不存在: {img_path}")
                    continue
                
                try:
                    if i == 0:
                        # 第一张图片
                        file_input = page.locator(".upload-input")
                    else:
                        file_input = page.locator("input[type='file']").last
                    
                    file_input.set_input_files(img_path)
                    page.wait_for_timeout(2000)
                    print(f"✅ 上传图片 {i+1}/{len(images)}")
                except Exception as e:
                    print(f"⚠️ 上传图片失败: {e}")
            
            # 输入标题
            try:
                title_input = page.locator("input[placeholder*='标题']").first
                title_input.fill(title)
            except:
                print("⚠️ 输入标题失败")
            
            # 输入正文
            try:
                content_input = page.locator("textarea[placeholder*='正文']").first
                content_input.fill(content)
            except:
                print("⚠️ 输入正文失败")
            
            # 添加标签
            if tags:
                for tag in tags[:10]:  # 最多10个标签
                    try:
                        tag_input = page.locator("input[placeholder*='标签']").first
                        tag_input.fill(f"#{tag}")
                        tag_input.press("Enter")
                        page.wait_for_timeout(500)
                    except:
                        pass
            
            # 发布
            try:
                publish_btn = page.locator("button:has-text('发布')").first
                publish_btn.click()
                page.wait_for_timeout(3000)
                print("✅ 发布成功!")
            except:
                print("⚠️ 点击发布按钮失败")
            
            browser.close()
            return True
            
        except Exception as e:
            print(f"❌ 发布失败: {e}")
            browser.close()
            return False


def get_user_profile():
    """获取用户信息"""
    session = get_session()
    if not session:
        print("❌ 未登录，请先运行 login")
        return None
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(storage_state=session)
        page = context.new_page()
        
        try:
            page.goto("https://creator.xiaohongshu.com/profile")
            page.wait_for_timeout(3000)
            
            profile = {}
            
            try:
                profile["nickname"] = page.locator(".nickname").inner_text()
            except:
                pass
            
            try:
                profile["follows"] = page.locator(".follows").inner_text()
            except:
                pass
            
            try:
                profile["fans"] = page.locator(".fans").inner_text()
            except:
                pass
            
            try:
                profile["likes"] = page.locator(".likes").inner_text()
            except:
                pass
            
            browser.close()
            return profile
            
        except Exception as e:
            print(f"❌ 获取用户信息失败: {e}")
            browser.close()
            return None


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("""
honny-publisher v2.0 - 小红书发布器

用法:
    python3 honny_publisher.py login              # 登录（生成二维码）
    python3 honny_publisher.py check              # 检查登录状态
    python3 honny_publisher.py search <关键词>     # 搜索内容
    python3 honny_publisher.py feed               # 获取推荐
    python3 honny_publisher.py profile            # 获取用户信息
    python3 honny_publisher.py detail <URL>       # 获取笔记详情
        """)
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "login":
        login(headless=True)
    elif command == "check":
        if check_login():
            print("✅ 已登录")
        else:
            print("❌ 未登录")
    elif command == "search":
        keyword = sys.argv[2] if len(sys.argv) > 2 else "测试"
        results = search(keyword)
        if results:
            for i, r in enumerate(results, 1):
                print(f"{i}. {r['title'][:50]} - {r['author']}")
        else:
            print("未找到结果")
    elif command == "feed":
        results = get_feed()
        for i, r in enumerate(results, 1):
            print(f"{i}. {r['title'][:50]} - {r['author']}")
    elif command == "profile":
        profile = get_user_profile()
        if profile:
            for k, v in profile.items():
                print(f"{k}: {v}")
    elif command == "detail":
        url = sys.argv[2] if len(sys.argv) > 2 else ""
        if url:
            detail = get_note_detail(url)
            if detail:
                print(f"标题: {detail['title']}")
                print(f"作者: {detail['author']}")
                print(f"点赞: {detail['likes']}  收藏: {detail['collects']}")
                print(f"内容: {detail['content'][:200]}...")
        else:
            print("请提供笔记URL")
    else:
        print(f"未知命令: {command}")
