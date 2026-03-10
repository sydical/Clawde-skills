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
const topics = values.topic || [];

if (!text && images.length === 0) {
  console.log("用法: bun dewu-publisher.ts <文字内容> [--image 图片路径] [--topic 话题] [--submit]");
  console.log("");
  console.log("示例:");
  console.log("  bun dewu-publisher.ts \"得物上新！\"");
  console.log("  bun dewu-publisher.ts \"好物分享！\" --image photo.png");
  console.log("  bun dewu-publisher.ts \"潮鞋分享！\" --image photo.png --topic 潮鞋 --submit");
  process.exit(1);
}

if (images.length === 0) {
  console.log("⚠️  得物推荐使用图片，图片能提高曝光率");
}

console.log("🚀 启动得物发布器...");
console.log(`📝 内容: ${text || "(无文字)"}`);
console.log(`🖼️  图片: ${images.length > 0 ? images.join(", ") : "(无图片)"}`);
console.log(`🏷️  话题: ${topics.length > 0 ? topics.map(t => '#' + t).join(" ") : "(无话题)"}`);
console.log(`✅ 实际发布: ${values.submit ? "是" : "否 (预览模式)"}`);
console.log("");

// 获取 skill 目录
const SKILL_DIR = path.dirname(path.dirname(path.dirname(Bun.argv[1] || "")));
const userDataDir = values.profile || path.join(SKILL_DIR, "dewu-profile");

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
  console.log("🌐 [得物] 访问得物首页...");
  await page.goto("https://www.dewu.com", { waitUntil: "networkidle", timeout: 60000 });

  // 检查是否需要登录
  const loginRequired = await page.locator("text=登录, text=立即登录").isVisible({ timeout: 5000 }).catch(() => true);
  
  if (loginRequired) {
    console.log("🔐 [得物] 请在浏览器中登录得物...");
    console.log("   登录完成后按回车键继续...");
    await new Promise(resolve => process.stdin.once("data", resolve));
  }

  console.log("✍️  [得物] 准备发布...");

  // 尝试访问社区发布页面
  try {
    console.log("🌐 [得物] 尝试进入社区发表页面...");
    await page.goto("https://www.dewu.com/community/publish", { waitUntil: "networkidle", timeout: 30000 });
    await page.waitForTimeout(2000);
  } catch (e) {
    console.log("⚠️  [得物] 社区发表页不可用，尝试首页发表...");
    await page.goto("https://www.dewu.com", { waitUntil: "networkidle" });
  }

  // 查找发布入口
  console.log("🔍 [得物] 寻找发布入口...");
  
  // 尝试多种发布按钮选择器
  const postSelectors = [
    "text=发笔记",
    "text=发帖子", 
    "text=发布",
    ".create-btn",
    "[class*='create']",
    "[class*='publish']"
  ];
  
  let foundPostBtn = false;
  for (const selector of postSelectors) {
    const btn = page.locator(selector).first();
    if (await btn.isVisible({ timeout: 2000 }).catch(() => false)) {
      console.log(`✅ [得物] 找到发布入口: ${selector}`);
      await btn.click();
      await page.waitForTimeout(2000);
      foundPostBtn = true;
      break;
    }
  }

  if (!foundPostBtn) {
    console.log("⚠️  [得物] 未找到发布按钮，请手动点击发布");
  }

  // 输入内容
  console.log("📝 [得物] 输入内容...");
  const contentSelectors = [
    "textarea[placeholder*='分享']",
    "textarea[placeholder*='心得']",
    "textarea[placeholder*='说']",
    "div[contenteditable='true']",
    "textarea"
  ];
  
  let filledContent = false;
  for (const selector of contentSelectors) {
    const contentBox = page.locator(selector).first();
    if (await contentBox.isVisible({ timeout: 2000 }).catch(() => false)) {
      await contentBox.click();
      
      let fullText = text;
      if (topics.length > 0) {
        fullText += "\n" + topics.map(t => `#${t}`).join(" ");
      }
      
      await contentBox.fill(fullText);
      console.log(`✅ [得物] 内容已输入`);
      filledContent = true;
      break;
    }
  }

  if (!filledContent) {
    console.log("⚠️  [得物] 未找到内容输入框，请手动输入");
  }

  // 上传图片
  if (images.length > 0) {
    console.log(`📤 [得物] 上传 ${images.length} 张图片...`);
    try {
      const fileInput = page.locator('input[type="file"]').first();
      await fileInput.setInputFiles(images);
      await page.waitForTimeout(3000);
      console.log("✅ [得物] 图片已上传");
    } catch (e) {
      console.log("⚠️  [得物] 自动上传失败，尝试手动...");
      // 尝试点击上传按钮
      const uploadBtn = page.locator("text=上传图片, text=添加图片").first();
      if (await uploadBtn.isVisible({ timeout: 2000 }).catch(() => false)) {
        await uploadBtn.click();
        await page.waitForTimeout(1000);
        const fileInput = page.locator('input[type="file"]').first();
        await fileInput.setInputFiles(images);
        await page.waitForTimeout(3000);
      }
    }
  }

  if (values.submit) {
    console.log("🚀 [得物] 发布中...");
    try {
      const submitSelectors = [
        "text=发布",
        "text=发表",
        ".submit-btn",
        "button[class*='primary']",
        "[class*='publish']"
      ];
      
      for (const selector of submitSelectors) {
        const submitBtn = page.locator(selector).last();
        if (await submitBtn.isVisible({ timeout: 2000 }).catch(() => false)) {
          await submitBtn.click();
          await page.waitForTimeout(3000);
          console.log("✅ [得物] 发布成功！");
          break;
        }
      }
    } catch (e) {
      console.log("⚠️  [得物] 发布按钮未找到，请手动点击发布");
    }
  } else {
    console.log("");
    console.log("👀 预览模式 - 请在浏览器中查看内容是否正确");
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
