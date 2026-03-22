#!/usr/bin/env bun

import { chromium, type BrowserContext, type Page } from "playwright";
import { parseArgs } from "util";
import * as path from "path";

const { values, positionals } = parseArgs({
  args: Bun.argv,
  options: {
    weibo: {
      type: "string",
    },
    xhs: {
      type: "string",
    },
    dewu: {
      type: "string",
    },
    douyin: {
      type: "string",
    },
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

const weiboText = values.weibo;
const xhsText = values.xhs;
const dewuText = values.dewu;
const douyinText = values.douyin;
const images = values.image || [];
const videos = values.video || [];
const topics = values.topic || [];

if (!weiboText && !xhsText && !dewuText && !douyinText) {
  console.log("用法: bun social-publisher.ts [--weibo 微博] [--xhs 小红书] [--dewu 得物] [--douyin 抖音] [--image 图片] [--video 视频] [--submit]");
  console.log("");
  console.log("示例:");
  console.log("  # 只发微博");
  console.log("  bun social-publisher.ts --weibo \"你好，微博！\"");
  console.log("  # 只发小红书");
  console.log("  bun social-publisher.ts --xhs \"你好，小红书！\" --image photo.png");
  console.log("  # 只得物");
  console.log("  bun social-publisher.ts --dewu \"得物上新！\" --image photo.png");
  console.log("  # 只发抖音");
  console.log("  bun social-publisher.ts --douyin \"抖音视频介绍\" --video ./video.mp4");
  console.log("  # 同时发布多平台");
  console.log("  bun social-publisher.ts --weibo \"微博\" --xhs \"小红书\" --dewu \"得物\" --douyin \"抖音\" --image photo.png --submit");
  process.exit(1);
}

if (xhsText && images.length === 0 && !videos.length) {
  console.log("⚠️  小红书推荐使用图片，但也支持纯文字发布");
}

if (dewuText && images.length === 0 && !videos.length) {
  console.log("⚠️  得物推荐使用图片，图片能提高曝光率");
}

if (douyinText && videos.length === 0 && images.length === 0) {
  console.log("⚠️  抖音建议上传视频，也可以发图片作品");
}

console.log("🚀 启动社交平台发布器...");
if (weiboText) console.log(`📝 微博内容: ${weiboText}`);
if (xhsText) console.log(`📝 小红书内容: ${xhsText}`);
if (dewuText) console.log(`📝 得物内容: ${dewuText}`);
if (douyinText) console.log(`📝 抖音内容: ${douyinText}`);
console.log(`🖼️  图片: ${images.length > 0 ? images.join(", ") : "(无图片)"}`);
console.log(`🎬 视频: ${videos.length > 0 ? videos.join(", ") : "(无视频)"}`);
console.log(`✅ 实际发布: ${values.submit ? "是" : "否 (预览模式)"}`);
console.log("");

// 获取 skill 目录
const SKILL_DIR = path.dirname(path.dirname(path.dirname(Bun.argv[1] || "")));
const userDataDir = values.profile || path.join(SKILL_DIR, "social-profile");

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

async function publishWeibo(page: Page, text: string, images: string[], submit: boolean) {
  console.log("🌐 [微博] 访问微博...");
  await page.goto("https://weibo.com", { waitUntil: "networkidle", timeout: 60000 });

  // 检查是否需要登录
  const loginRequired = await page.locator("text=登录").isVisible({ timeout: 5000 }).catch(() => true);
  
  if (loginRequired) {
    console.log("🔐 [微博] 请在浏览器中登录微博...");
    console.log("   登录完成后按回车键继续...");
    await new Promise(resolve => process.stdin.once("data", resolve));
  }

  console.log("✍️  [微博] 准备发布...");

  // 点击发布框
  await page.waitForSelector("textarea[placeholder*='有什么新鲜事'], div[contenteditable='true']", { timeout: 10000 });
  
  const editBox = page.locator("textarea[placeholder*='有什么新鲜事'], div[contenteditable='true']").first();
  await editBox.click();
  
  // 输入文字
  if (text) {
    await editBox.fill(text);
  }

  // 上传图片
  if (images.length > 0) {
    console.log(`📤 [微博] 上传 ${images.length} 张图片...`);
    const fileInput = page.locator('input[type="file"]').first();
    await fileInput.setInputFiles(images);
    await page.waitForTimeout(2000);
  }

  if (submit) {
    console.log("🚀 [微博] 发布中...");
    const publishBtn = page.locator("button:has-text('发送'), button:has-text('发布'), a:has-text('发送'), a:has-text('发布'), [node-type='submit'], .W_btn_a").first();
    await publishBtn.waitFor({ state: "visible", timeout: 10000 });
    await publishBtn.click();
    await page.waitForTimeout(3000);
    console.log("✅ [微博] 发布成功！");
  }
}

async function publishXiaohongshu(page: Page, text: string, images: string[], submit: boolean) {
  console.log("🌐 [小红书] 访问小红书发布页面...");
  await page.goto("https://creator.xiaohongshu.com/publish/publish?from=menu&target=article", { waitUntil: "networkidle", timeout: 60000 });

  // 检查是否需要登录
  const loginRequired = await page.locator("text=登录, text=扫码登录").isVisible({ timeout: 5000 }).catch(() => true);
  
  if (loginRequired) {
    console.log("🔐 [小红书] 请在浏览器中登录小红书...");
    console.log("   登录完成后按回车键继续...");
    await new Promise(resolve => process.stdin.once("data", resolve));
  }

  console.log("✍️  [小红书] 准备发布...");

  // 点击"新的创作"
  const newCreateBtn = page.locator(".new-btn").first();
  if (await newCreateBtn.isVisible({ timeout: 5000 })) {
    await newCreateBtn.click();
    await page.waitForTimeout(2000);
  }

  // 输入标题
  if (text) {
    console.log("📝 [小红书] 输入标题...");
    const titleBox = page.locator("textarea[placeholder*='输入标题'], input[placeholder*='输入标题']").first();
    await titleBox.waitFor({ state: "visible", timeout: 10000 });
    await titleBox.click();
    await titleBox.fill(text.substring(0, 20));
  }

  // 输入正文（带话题）
  if (text) {
    console.log("📝 [小红书] 输入正文...");
    const contentBox = page.locator("div[contenteditable='true'], textarea[placeholder*='粘贴到这里或输入文字']").first();
    await contentBox.waitFor({ state: "visible", timeout: 10000 });
    await contentBox.click();
    
    let fullText = text;
    if (topics.length > 0) {
      fullText += " " + topics.map(t => `#${t}`).join(" ");
    }
    await contentBox.fill(fullText);
  }

  // 点击一键排版
  console.log("🎨 [小红书] 点击一键排版...");
  const formatBtn = page.locator(".next-btn").first();
  if (await formatBtn.isVisible({ timeout: 5000 })) {
    await formatBtn.click();
    await page.waitForTimeout(2000);
  }

  // 选择模板（简约基础、绿色或黄色）
  console.log("🎨 [小红书] 选择模板...");
  const templateBtn = page.locator(".color-item[style*='--item-color: #FFFEEA']").first();
  if (await templateBtn.isVisible({ timeout: 5000 })) {
    await templateBtn.click();
    await page.waitForTimeout(1000);
  }

  // 点击下一步
  console.log("➡️  [小红书] 点击下一步...");
  const nextBtn = page.locator(".submit").first();
  if (await nextBtn.isVisible({ timeout: 5000 })) {
    await nextBtn.click();
    await page.waitForTimeout(2000);
  }

  // 在最后页面输入正文描述（带话题）
  if (text) {
    console.log("📝 [小红书] 输入正文描述...");
    const finalContentBox = page.locator("div[contenteditable='true'], textarea[placeholder*='正文描述'], textarea[placeholder*='真诚有价值的分享予人温暖']").first();
    await finalContentBox.waitFor({ state: "visible", timeout: 10000 });
    await finalContentBox.click();
    
    let fullText = text;
    if (topics.length > 0) {
      fullText += " " + topics.map(t => `#${t}`).join(" ");
    }
    await finalContentBox.fill(fullText);
  }

  if (submit) {
    console.log("🚀 [小红书] 发布中...");
    const submitBtn = page.locator(".bg-red").last();
    await submitBtn.waitFor({ state: "visible", timeout: 10000 });
    await submitBtn.click();
    await page.waitForTimeout(3000);
    console.log("✅ [小红书] 发布成功！");
  }
}

async function publishDewu(page: Page, text: string, images: string[], submit: boolean) {
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

  // 尝试访问社区发表页面
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
  const postSelectors = ["text=发笔记", "text=发帖子", "text=发布", ".create-btn", "[class*='create']", "[class*='publish']"];
  
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
  const contentSelectors = ["textarea[placeholder*='分享']", "textarea[placeholder*='心得']", "textarea[placeholder*='说']", "div[contenteditable='true']", "textarea"];
  
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
      console.log("⚠️  [得物] 自动上传失败，请手动上传");
    }
  }

  if (submit) {
    console.log("🚀 [得物] 发布中...");
    try {
      const submitSelectors = ["text=发布", "text=发表", ".submit-btn", "button[class*='primary']", "[class*='publish']"];
      
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
    console.log("👀 [得物] 预览模式 - 请在浏览器中查看内容是否正确");
  }
}

async function publishDouyin(page: Page, text: string, videos: string[], images: string[], submit: boolean) {
  console.log("🌐 [抖音] 访问抖音创作者服务平台...");
  
  // 尝试访问抖音创作者服务平台
  try {
    await page.goto("https://creator.douyin.com/", { waitUntil: "networkidle", timeout: 60000 });
  } catch (e) {
    // 如果创作者平台不行，尝试主页
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
  // 方式1: 创作者服务平台 - 视频上传
  try {
    console.log("🌐 [抖音] 尝试进入视频上传页面...");
    await page.goto("https://creator.douyin.com/videolive?from=create_video", { waitUntil: "networkidle", timeout: 30000 });
    await page.waitForTimeout(2000);
  } catch (e) {
    console.log("⚠️  [抖音] 创作者平台视频上传页不可用");
  }

  // 查找上传入口
  console.log("🔍 [抖音] 寻找视频上传入口...");
  
  // 尝试多种上传选择器
  const uploadSelectors = [
    "text=上传视频",
    "text=发布作品", 
    "text=开始创作",
    "[class*='upload']",
    "input[type='file']",
    ".upload-btn",
    "text=点击上传"
  ];
  
  let foundUpload = false;
  for (const selector of uploadSelectors) {
    const el = page.locator(selector).first();
    if (await el.isVisible({ timeout: 2000 }).catch(() => false)) {
      console.log(`✅ [抖音] 找到上传入口: ${selector}`);
      
      // 如果是 input[type=file]，直接设置文件
      if (selector === "input[type='file']") {
        if (videos.length > 0) {
          await el.setInputFiles(videos);
        } else if (images.length > 0) {
          await el.setInputFiles(images);
        }
      } else {
        await el.click();
        await page.waitForTimeout(1000);
        // 查找隐藏的 file input
        const fileInput = page.locator('input[type="file"]').first();
        if (await fileInput.isVisible({ timeout: 2000 }).catch(() => false) || true) {
          if (videos.length > 0) {
            await fileInput.setInputFiles(videos);
          } else if (images.length > 0) {
            await fileInput.setInputFiles(images);
          }
        }
      }
      await page.waitForTimeout(3000);
      foundUpload = true;
      break;
    }
  }

  // 如果没找到上传入口，尝试直接用文件输入
  if (!foundUpload) {
    console.log("🔍 [抖音] 尝试直接上传文件...");
    const fileInput = page.locator('input[type="file"]').first();
    if (await fileInput.isVisible({ timeout: 3000 }).catch(() => false)) {
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
  }

  if (!foundUpload) {
    console.log("⚠️  [抖音] 未找到上传入口，请手动上传文件");
    console.log("   预览模式 - 请在浏览器中手动操作");
  } else {
    // 等待视频上传处理
    console.log("⏳ [抖音] 等待文件上传处理...");
    await page.waitForTimeout(5000);

    // 输入文案
    if (text) {
      console.log("📝 [抖音] 输入视频描述...");
      const descSelectors = [
        "textarea[placeholder*='描述']",
        "textarea[placeholder*='文案']",
        "textarea[placeholder*='标题']",
        "div[contenteditable='true']",
        "input[placeholder*='添加标题']"
      ];
      
      for (const selector of descSelectors) {
        const descBox = page.locator(selector).first();
        if (await descBox.isVisible({ timeout: 2000 }).catch(() => false)) {
          await descBox.click();
          
          let fullText = text;
          if (topics.length > 0) {
            fullText += " " + topics.map(t => `#${t}`).join(" ");
          }
          
          await descBox.fill(fullText);
          console.log("✅ [抖音] 文案已输入");
          break;
        }
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

    if (submit) {
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
      console.log("👀 [抖音] 预览模式 - 请在浏览器中确认内容后手动发布");
    }
  }
}

try {
  if (weiboText) {
    const weiboPage = browser.pages()[0] || (await browser.newPage());
    await publishWeibo(weiboPage, weiboText, images, values.submit);
    if (!values.submit) {
      console.log("👀 [微博] 预览模式 - 请在浏览器中查看");
    }
  }

  if (xhsText) {
    const xhsPage = await browser.newPage();
    await publishXiaohongshu(xhsPage, xhsText, images, values.submit);
    if (!values.submit) {
      console.log("👀 [小红书] 预览模式 - 请在浏览器中查看");
    }
  }

  if (dewuText) {
    const dewuPage = await browser.newPage();
    await publishDewu(dewuPage, dewuText, images, values.submit);
    if (!values.submit) {
      console.log("👀 [得物] 预览模式 - 请在浏览器中查看");
    }
  }

  if (douyinText) {
    const douyinPage = await browser.newPage();
    await publishDouyin(douyinPage, douyinText, videos, images, values.submit);
    if (!values.submit) {
      console.log("👀 [抖音] 预览模式 - 请在浏览器中查看");
    }
  }

  if (!values.submit) {
    console.log("");
    console.log("按 Ctrl+C 退出");
    await new Promise(() => {});
  }

} catch (error) {
  console.error("❌ 出错:", error);
} finally {
  if (values.submit) {
    await browser.close();
  }
}
