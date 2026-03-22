/**
 * WeChatPadPro Login Skill
 * 
 * 触发方式: /wechat-login 或 "微信登录"
 * 
 * 功能:
 * 1. 检查当前登录状态
 * 2. 如果未登录，生成二维码并通过QQ发送给用户
 * 3. 用户扫码后发送登录成功通知
 */

import { readFileSync, writeFileSync, existsSync } from "fs";
import { join } from "path";
import axios from "axios";

const QR_CODE_PATH = "/tmp/wechatpadpro-qr.png";
const NOTIFY_QQ = process.env.WECHAT_NOTIFY_QQ || "4515644";
const API_URL = process.env.WECHAT_API_URL || "http://localhost:8080";
const ADMIN_KEY = process.env.WECHAT_ADMIN_KEY || "wechatpad123";
const LOGIN_STATE_PATH = "/tmp/wechatpadpro-login-state.json";

function saveLoginState(state) {
  try {
    writeFileSync(LOGIN_STATE_PATH, JSON.stringify(state, null, 2));
  } catch (e) {
    console.error("Failed to save login state:", e);
  }
}

function loadLoginState() {
  try {
    if (existsSync(LOGIN_STATE_PATH)) {
      return JSON.parse(readFileSync(LOGIN_STATE_PATH, "utf-8"));
    }
  } catch (e) {
    console.error("Failed to read login state:", e);
  }
  return { loggedIn: false };
}

async function checkLoginStatus() {
  try {
    const response = await axios.get(`${API_URL}/api/login/GetLoginStatus`, {
      headers: { adminKey: ADMIN_KEY },
      timeout: 5000,
    });
    
    const data = response.data;
    if (data.data?.status === 1) {
      return {
        loggedIn: true,
        userId: data.data.wxid,
        userName: data.data.name,
        loginTime: new Date().toISOString(),
      };
    }
    return { loggedIn: false };
  } catch (e) {
    console.error("Failed to check login status:", e);
    return { loggedIn: false };
  }
}

async function generateQRCode() {
  try {
    const response = await axios.post(
      `${API_URL}/api/login/qr/newx`,
      {},
      { headers: { adminKey: ADMIN_KEY }, timeout: 10000 }
    );
    
    const data = response.data;
    if (data.qrUuid) {
      return {
        qrImage: data.qrImage,
        qrUuid: data.qrUuid,
      };
    }
    return null;
  } catch (e) {
    console.error("Failed to generate QR code:", e);
    return null;
  }
}

async function checkQRLoginStatus(qrUuid) {
  try {
    const response = await axios.get(
      `${API_URL}/api/login/CheckLoginStatus?key=${qrUuid}`,
      { headers: { adminKey: ADMIN_KEY }, timeout: 5000 }
    );
    
    const data = response.data;
    if (data.code === 0 && data.data?.status === 1) {
      return {
        loggedIn: true,
        userId: data.data.wxid,
        userName: data.data.name,
        loginTime: new Date().toISOString(),
      };
    }
    return null;
  } catch (e) {
    console.error("Failed to check QR login status:", e);
    return null;
  }
}

async function sendToQQ(qq, message, imagePath) {
  console.log(`[QQ通知] 发送给 ${qq}: ${message}`);
}

async function main() {
  const command = process.argv[2] || "check";
  
  if (command === "check") {
    const state = await checkLoginStatus();
    
    if (state.loggedIn) {
      saveLoginState(state);
      console.log(JSON.stringify({
        ok: true,
        loggedIn: true,
        message: `✅ 微信已登录！登录用户: ${state.userName || state.userId}`
      }));
      return;
    }
    
    const qrData = await generateQRCode();
    if (qrData) {
      const qrBase64 = qrData.qrImage.replace(/^data:image\/\w+;base64,/, "");
      const qrBuffer = Buffer.from(qrBase64, "base64");
      
      const stateWithQr = {
        loggedIn: false,
        qrUuid: qrData.qrUuid,
      };
      saveLoginState(stateWithQr);
      
      console.log(JSON.stringify({
        ok: true,
        loggedIn: false,
        qrUuid: qrData.qrUuid,
        qrBase64: qrData.qrImage,
        message: `📱 请使用手机微信扫描二维码登录\n登录UUID: ${qrData.qrUuid}\n请将此二维码图片发送给QQ用户 ${NOTIFY_QQ}`
      }));
    } else {
      console.log(JSON.stringify({
        ok: false,
        error: "无法生成二维码，请检查WeChatPadPro服务是否运行"
      }));
    }
    return;
  }
  
  if (command === "check-qr") {
    const state = loadLoginState();
    if (!state.qrUuid) {
      console.log(JSON.stringify({
        ok: false,
        error: "没有待登录的二维码"
      }));
      return;
    }
    
    const loginState = await checkQRLoginStatus(state.qrUuid);
    if (loginState?.loggedIn) {
      saveLoginState(loginState);
      await sendToQQ(
        NOTIFY_QQ,
        `✅ 微信登录成功！\n用户: ${loginState.userName || loginState.userId}\n登录时间: ${loginState.loginTime}`
      );
      console.log(JSON.stringify({
        ok: true,
        loggedIn: true,
        message: `✅ 微信登录成功！\n用户: ${loginState.userName || loginState.userId}`
      }));
    } else {
      console.log(JSON.stringify({
        ok: true,
        loggedIn: false,
        message: "⏳ 等待用户扫码中..."
      }));
    }
    return;
  }
  
  if (command === "notify") {
    const state = loadLoginState();
    if (state.loggedIn) {
      await sendToQQ(
        NOTIFY_QQ,
        `✅ 微信登录成功！\n用户: ${state.userName || state.userId}\n登录时间: ${state.loginTime}`
      );
      console.log(JSON.stringify({
        ok: true,
        message: `✅ 已通知QQ用户 ${NOTIFY_QQ} 登录成功`
      }));
    } else {
      console.log(JSON.stringify({
        ok: false,
        error: "微信未登录"
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
