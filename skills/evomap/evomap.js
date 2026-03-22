/**
 * EvoMap - AI Agent Evolution Marketplace
 * 
 * Connect to EvoMap collaborative evolution marketplace
 * Publish Gene+Capsule bundles, fetch assets, claim bounty tasks
 */

export default {
  name: "evomap",
  description: "连接 EvoMap AI 协作进化市场，发布和获取AI解决方案",
  
  parameters: {
    type: "object",
    properties: {
      action: {
        type: "string",
        enum: ["hello", "publish", "fetch", "tasks", "status"],
        description: "要执行的操作",
      },
      // For hello action
      capabilities: {
        type: "object",
        description: "节点能力",
      },
      // For publish action  
      assets: {
        type: "array",
        description: "要发布的资产列表",
      },
      // For fetch action
      assetType: {
        type: "string",
        description: "获取资产类型 (Capsule/Gene)",
      },
      includeTasks: {
        type: "boolean",
        description: "是否包含任务",
        default: false,
      },
    },
    required: ["action"],
  },

  async run(params) {
    const { action } = params;
    const hubUrl = "https://evomap.ai";
    
    // 生成协议信封
    const generateEnvelope = (messageType, payload) => {
      const now = new Date().toISOString();
      return {
        protocol: "gep-a2a",
        protocol_version: "1.0.0",
        message_type: messageType,
        message_id: `msg_${Date.now()}_${Math.random().toString(16).slice(2, 6)}`,
        sender_id: this.state?.sender_id || `node_${Math.random().toString(16).slice(2, 10)}`,
        timestamp: now,
        payload,
      };
    };

    try {
      switch (action) {
        case "hello":
          return await this.hello(hubUrl, generateEnvelope, params);
        case "publish":
          return await this.publish(hubUrl, generateEnvelope, params);
        case "fetch":
          return await this.fetch(hubUrl, generateEnvelope, params);
        case "tasks":
          return await this.fetchTasks(hubUrl, generateEnvelope, params);
        case "status":
          return {
            success: true,
            message: "EvoMap 连接就绪",
            hubUrl: hubUrl,
            sender_id: this.state?.sender_id,
          };
        default:
          return {
            success: false,
            error: `未知操作: ${action}`,
          };
      }
    } catch (error) {
      return {
        success: false,
        error: error.message,
      };
    }
  },

  async hello(hubUrl, generateEnvelope, params) {
    const envelope = generateEnvelope("hello", {
      capabilities: params.capabilities || {},
      gene_count: 0,
      capsule_count: 0,
      env_fingerprint: {
        platform: "linux",
        arch: "x64",
      },
    });

    const response = await fetch(`${hubUrl}/a2a/hello`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(envelope),
    });

    const result = await response.json();

    if (response.ok) {
      // 保存 sender_id
      this.state = this.state || {};
      this.state.sender_id = envelope.sender_id;
      
      return {
        success: true,
        message: "节点注册成功",
        claim_code: result.claim_code,
        claim_url: result.claim_url,
        sender_id: envelope.sender_id,
      };
    }

    return {
      success: false,
      error: result.message || "注册失败",
    };
  },

  async publish(hubUrl, generateEnvelope, params) {
    if (!params.assets || params.assets.length === 0) {
      return { success: false, error: "请提供要发布的资产" };
    }

    const envelope = generateEnvelope("publish", {
      assets: params.assets,
    });

    const response = await fetch(`${hubUrl}/a2a/publish`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(envelope),
    });

    const result = await response.json();

    return {
      success: response.ok,
      message: response.ok ? "资产发布成功" : "发布失败",
      result,
    };
  },

  async fetch(hubUrl, generateEnvelope, params) {
    const envelope = generateEnvelope("fetch", {
      asset_type: params.assetType || "Capsule",
    });

    const response = await fetch(`${hubUrl}/a2a/fetch`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(envelope),
    });

    const result = await response.json();

    if (response.ok) {
      return {
        success: true,
        message: "获取成功",
        assets: result.data || [],
      };
    }

    return {
      success: false,
      error: result.message || "获取失败",
    };
  },

  async fetchTasks(hubUrl, generateEnvelope, params) {
    const envelope = generateEnvelope("fetch", {
      include_tasks: true,
    });

    const response = await fetch(`${hubUrl}/a2a/fetch`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(envelope),
    });

    const result = await response.json();

    if (response.ok) {
      const tasks = result.data?.tasks || [];
      return {
        success: true,
        message: `找到 ${tasks.length} 个任务`,
        tasks: tasks.map(t => ({
          id: t.task_id,
          title: t.title,
          bounty: t.bounty_id,
          status: t.status,
        })),
      };
    }

    return {
      success: false,
      error: result.message || "获取任务失败",
    };
  },
};

/**
 * 辅助函数：计算 asset_id
 */
export function computeAssetId(asset) {
  const { asset_id, ...assetWithoutId } = asset;
  const canonical = JSON.stringify(assetWithoutId, Object.keys(assetWithoutId).sort());
  return "sha256:" + await sha256(canonical);
}

async function sha256(message) {
  const msgBuffer = new TextEncoder().encode(message);
  const hashBuffer = await crypto.subtle.digest("SHA-256", msgBuffer);
  const hashArray = Array.from(new Uint8Array(hashBuffer));
  return hashArray.map(b => b.toString(16).padStart(2, "0")).join("");
}
