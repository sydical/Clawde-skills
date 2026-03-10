#!/usr/bin/env bun

import { chromium } from "playwright";
import { parseArgs } from "util";
import * as path from "path";

const { values, positionals } = parseArgs({
  args: Bun.argv,
  options: {
    image: {
      type: "string",
      multiple: true,
    },
    video: {
      type: "string",
      multiple: true,
    },
    topic: {
      type: "string",
      multiple: true,
    },
    submit: {
      type: "boolean",
      default: false,
    },
    profile: {
      type: "string",
    },
  },
  strict: true,
  allowPositionals: true,
});

const text = positionals.slice(2).join(" ");
const images = values.image || [];
const videos = values.video || [];
const topics = values.topic || [];

if (!text && images.length === 0 && videos.length === 0) {
  console.log("用法: bun douyin-publisher.ts <文字内容> [--image 图片路径] [--video 视频路径] [--topic 话题] [--submit]");
  console.log("");
  console.log("示例:");
  console.log("  # 发布视频（推荐）");
  console.log("  bun douyin-publisher.ts \"精彩视频介绍\" --video ./video.mp4");
  console.log("  # 带话题");
  console.log("  bun douyin-publisher.ts \"新视频上线\" --video ./video.mp4 --topic 搞笑 --topic 宠物 --submit");
  console.log("  # 发布图文");
  console.log("  bun douyin-publisher.ts \"图文分享\" --image ./photo.png");
  console.log("  # 预览模式");
  console.log("  bun douyin-publisher.ts \"测试发布\" --video ./video.mp4");
  process.exit(1);
}

if (videos.length === 0 && images.length === 0) {
  console.log("⚠️  抖音建议上传视频，也可以发图片作品");
}

console.log("🚀 启动抖音发布器...");
console.log(`📝 内容: ${text || "(无文字)"}`);
console.log(`🖼️  图片: ${images.length > 0 ? images.join(", ") : "(无图片)"}`);
console.log(`🎬 视频: ${videos.length > 0 ? videos.join(", ") : "(无视频)"}`);
console.log(`🏷️  话题: ${topics.length > 0 ? topics.map(t => '#' + t).join(" ") : "(无话题)"}`);
console.log(`✅ 实际发布: ${values.submit ? "是" : "否 (预览模式)"}`);
console.log("");

// 获取 skill 目录
const SKILL_DIR = path.dirname(path.dirname(path.dirname(Bun.argv[1] || "")));
const userDataDir = values.profile || path.join(SKILL_DIR, "douyin-profile");

// 自动检测 Chrome 路径
let executablePath: string | undefined;
if (process.platform === "darwin") {
  executablePath = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome";
} else if (process.platform === "linux") {
  executablePath = "/usr/bin/google-chrome";
} else if (process.platform === "win32") {
  executablePath = "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe";
}

const browser = await chromium.launchPersistentContext(userDataDir, {
  headless: false,
  executablePath,
  channel: !executablePath ? "chrome" : undefined,
  viewport: { width: 1280, height: 800 },
});

const page = browser.pages()[0] || (await browser.newPage());

try {
  console.log("🌐 [抖音] 访问抖音创作者服务平台...");
  
  // 尝试访问创作者平台
  try {
    await page.goto("https://creator.douyin.com/", { waitUntil: "networkidle", timeout: 60000 });
  } catch (e) {
    console.log("⚠️  [抖音] 创作者平台不可用，尝试抖音官网...");
    await page.goto("https://www.douyin.com", { waitUntil: "networkidle", timeout: 60000 });
  }

  // 检查是否需要登录
  const loginRequired = await page.locator("text=登录, text=立即登录, text=登录/注册").isVisible({ timeout: 5000 }).catch(() => true);
  
  if (loginRequired) {
    console.log("🔐 [抖音] 请在浏览器中登录抖音...");
    console.log("   登录完成后按回车键继续...");
    await new Promise(resolve => process.stdin.once("data", resolve));
  }

  console.log("✍️  [抖音] 准备发布...");

  // 尝试进入发布页面
  try {
    console.log("🌐 [抖音] 尝试进入视频上传页面...");
    await page.goto("https://creator.douyin.com/videolive?from=create_video", { waitUntil: "networkidle", timeout: 30000 });
    await page.waitForTimeout(2000);
  } catch (e) {
    console.log("⚠️  [抖音] 创作者平台视频上传页不可用，尝试其他方式...");
  }

  // 查找上传入口
  console.log("🔍 [抖音] 寻找视频上传入口...");
  
  const uploadSelectors = [
    "text=上传视频",
    "text=发布作品", 
    "text=开始创作",
    "[class*='upload']",
    ".upload-btn",
    "text=点击上传",
    "a:has-text('上传视频')"
  ];
  
  let foundUpload = false;
  for (const selector of uploadSelectors) {
    const el = page.locator(selector).first();
    if (await el.isVisible({ timeout: 2000 }).catch(() => false)) {
      console.log(`✅ [抖音] 找到上传入口: ${selector}`);
      await el.click();
      await page.waitForTimeout(1500);
      
      // 查找并设置文件
      const fileInput = page.locator('input[type="file"]').first();
      if (videos.length > 0) {
        await fileInput.setInputFiles(videos);
      } else if (images.length > 0) {
        await fileInput.setInputFiles(images);
      }
      await page.waitForTimeout(3000);
      foundUpload = true;
      break;
    }
  }

  // 如果没找到上传入口，直接尝试设置文件
  if (!foundUpload) {
    console.log("🔍 [抖音] 尝试直接上传文件...");
    const fileInput = page.locator('input[type="file"]').first();
    if (videos.length > 0) {
      await fileInput.setInputFiles(videos);
      console.log("✅ [抖音] 视频文件已选择");
    } else if (images.length > 0) {
      await fileInput.setInputFiles(images);
      console.log("✅ [抖音] 图片文件已选择");
    }
    await page.waitForTimeout(3000);
    foundUpload = true;
  }

  // 等待上传处理
  if (foundUpload) {
    console.log("⏳ [抖音] 等待文件上传处理...");
    await page.waitForTimeout(5000);

    // 输入文案
    console.log("📝 [抖音] 输入视频描述...");
    const descSelectors = [
      "textarea[placeholder*='描述']",
      "textarea[placeholder*='文案']",
      "textarea[placeholder*='标题']",
      "textarea[placeholder*='来说点什么']",
      "div[contenteditable='true']",
      "input[placeholder*='添加标题']"
    ];
    
    for (const selector of descSelectors) {
      const descBox = page.locator(selector).first();
      if (await descBox.isVisible({ timeout: 2000 }).catch(() => false)) {
        await descBox.click();
        
        let fullText = text;
        if (topics.length > 0) {
          fullText += "\n" + topics.map(t => `#${t}`).join(" ");
        }
        
        await descBox.fill(fullText);
        console.log("✅ [抖音] 文案已输入");
        break;
      }
    }

    // 添加话题
    if (topics.length > 0) {
      console.log("🏷️  [抖音] 添加话题...");
      for (const topic of topics) {
        const topicInput = page.locator("input[placeholder*='话题'], textarea[placeholder*='话题']").first();
        if (await topicInput.isVisible({ timeout: 2000 }).catch(() => false)) {
          await topicInput.fill(`#${topic}`);
          await page.waitForTimeout(500);
          await page.keyboard.press("Enter");
          await page.waitForTimeout(500);
        }
      }
    }
  }

  if (values.submit) {
    console.log("🚀 [抖音] 发布中...");
    try {
      const submitSelectors = [
        "text=发布",
        "text=确认发布",
        "text=立即发布",
        "button:has-text('发布')",
        "[class*='publish']",
        ".submit-btn"
      ];
      
      for (const selector of submitSelectors) {
        const submitBtn = page.locator(selector).last();
        if (await submitBtn.isVisible({ timeout: 2000 }).catch(() => false)) {
          await submitBtn.click();
          await page.waitForTimeout(3000);
          console.log("✅ [抖音] 发布成功！");
          break;
        }
      }
    } catch (e) {
      console.log("⚠️  [抖音] 发布按钮未找到，请手动点击发布");
    }
  } else {
    console.log("");
    console.log("👀 预览模式 - 请在浏览器中确认内容是否正确");
    console.log("   确认无误后按 Ctrl+C 退出，或添加 --submit 参数正式发布");
    await new Promise(() => {});
  }

} catch (error) {
  console.error("❌ 出错:", error);
} finally {
  if (values.submit) {
    await browser.close();
  }
}
