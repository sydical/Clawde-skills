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

if (!text && images.length === 0 && videos.length === 0) {
  console.log("用法: bun douyin-publisher.ts <文字内容> [--image 图片] [--video 视频] [--submit]");
  console.log("");
  console.log("示例:");
  console.log("  bun douyin-publisher.ts \"抖音视频介绍\" --video video.mp4");
  console.log("  bun douyin-publisher.ts \"图文分享\" --image photo.png");
  console.log("  bun douyin-publisher.ts \"发布作品\" --video video.mp4 --submit");
  process.exit(1);
}

console.log("🚀 启动抖音发布器...");
console.log(`📝 内容: ${text || "(无文字)"}`);
console.log(`🎬 视频: ${videos.length > 0 ? videos.join(", ") : "(无)"}`);
console.log(`🖼️  图片: ${images.length > 0 ? images.join(", ") : "(无)"}`);
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
  console.log("🌐 访问抖音...");
  await page.goto("https://www.douyin.com", { waitUntil: "networkidle", timeout: 60000 });

  // 检查是否需要登录
  const loginRequired = await page.locator("text=登录").isVisible({ timeout: 5000 }).catch(() => true);
  
  if (loginRequired) {
    console.log("🔐 请在浏览器中登录抖音...");
    console.log("   登录完成后按回车键继续...");
    await new Promise(resolve => process.stdin.once("data", resolve));
  }

  console.log("✍️  准备发布...");

  // 点击发布按钮（首页右上角）
  console.log("🔍 寻找发布入口...");
  const publishBtn = page.locator("text=发布, a[href*='/upload']").first();
  
  if (await publishBtn.isVisible({ timeout: 5000 }).catch(() => false)) {
    await publishBtn.click();
    await page.waitForTimeout(2000);
  } else {
    // 尝试直接访问上传页面
    console.log("🔍 尝试直接访问上传页面...");
    await page.goto("https://www.douyin.com/upload", { waitUntil: "networkidle", timeout: 30000 });
  }

  // 等待上传区域出现
  await page.waitForSelector("input[type='file']", { timeout: 10000 });
  
  // 选择文件上传（视频优先，其次图片）
  const fileInput = page.locator('input[type="file"]').first();
  
  if (videos.length > 0) {
    console.log(`📤 上传视频: ${videos[0]}`);
    await fileInput.setInputFiles(videos);
  } else if (images.length > 0) {
    console.log(`📤 上传图片: ${images[0]}`);
    await fileInput.setInputFiles(images);
  }
  
  await page.waitForTimeout(3000);

  // 输入文案
  console.log("📝 输入文案...");
  const descBox = page.locator("textarea[placeholder*='来说点什么'], textarea[placeholder*='描述'], div[contenteditable='true']").first();
  
  if (await descBox.isVisible({ timeout: 5000 }).catch(() => false)) {
    await descBox.fill(text);
  }

  if (values.submit) {
    console.log("🚀 发布中...");
    const submitBtn = page.locator("button:has-text('发布'), button:has-text('确认')").first();
    await submitBtn.waitFor({ state: "visible", timeout: 10000 });
    await submitBtn.click();
    await page.waitForTimeout(3000);
    console.log("✅ 发布成功！");
  } else {
    console.log("👀 预览模式 - 请在浏览器中查看，按 Ctrl+C 退出");
    await new Promise(() => {});
  }

} catch (error) {
  console.error("❌ 出错:", error);
} finally {
  if (values.submit) {
    await browser.close();
  }
}
