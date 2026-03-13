/**
 * Wechaty Login Skill
 * 
 * 触发方式: /wechat-login 或 "微信登录"
 */

import { readFileSync, writeFileSync, existsSync } from "fs";

const QR_CODE_PATH = "/tmp/wechaty-qr.png";
const LOGIN_STATE_PATH = "/tmp/wechaty-login-state.json";

function getLoginState() {
  try {
    if (existsSync(LOGIN_STATE_PATH)) {
      return JSON.parse(readFileSync(LOGIN_STATE_PATH, "utf-8"));
    }
  } catch (e) {
    console.error("Failed to read login state:", e);
  }
  return { loggedIn: false };
}

function checkQrCodeExists() {
  return existsSync(QR_CODE_PATH);
}

async function main() {
  const command = process.argv[2] || "check";
  
  if (command === "check") {
    const state = getLoginState();
    
    if (state.loggedIn) {
      console.log(JSON.stringify({
        ok: true,
        loggedIn: true,
        message: `✅ 微信已登录！登录用户: ${state.userName || state.userId}`
      }));
      return;
    }
    
    const qrExists = checkQrCodeExists();
    if (qrExists) {
      console.log(JSON.stringify({
        ok: true,
        loggedIn: false,
        qrCodePath: QR_CODE_PATH,
        message: `📱 请使用手机微信扫描二维码登录\n二维码路径: ${QR_CODE_PATH}\n\n可通过 VNC (端口 5900) 查看二维码`
      }));
    } else {
      console.log(JSON.stringify({
        ok: true,
        loggedIn: false,
        message: `⏳ 正在生成二维码，请稍后再试\n或输入 /wechat-login 重试`
      }));
    }
    return;
  }
  
  console.log(JSON.stringify({
    ok: false,
    error: `Unknown command: ${command}`
  }));
}

main().catch(console.error);
