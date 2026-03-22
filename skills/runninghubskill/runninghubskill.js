/**
 * RunningHub Image Generation Skill
 * 
 * 通过 RunningHub API 调用云端 ComfyUI 工作流生成 AI 图像
 * 
 * API 文档: https://www.runninghub.cn/call-api/api-detail/{workflow_id}?apiType=4
 */

export default {
  name: "runninghubskill",
  description: "使用 RunningHub 云端 ComfyUI 生成 AI 图像",
  parameters: {
    type: "object",
    properties: {
      nodeInfoList: {
        type: "array",
        description: "节点参数映射列表",
        items: {
          type: "object",
          properties: {
            nodeId: {
              type: "string",
              description: "节点 ID",
            },
            fieldName: {
              type: "string",
              description: "字段名称 (如 image, prompt)",
            },
            fieldValue: {
              type: "string",
              description: "字段值",
            },
            description: {
              type: "string",
              description: "参数描述",
            },
          },
          required: ["nodeId", "fieldName", "fieldValue"],
        },
      },
      instanceType: {
        type: "string",
        description: "运行实例类型 (default/plus)",
        default: "default",
      },
      usePersonalQueue: {
        type: "boolean",
        description: "是否使用个人独占队列",
        default: false,
      },
      webhookUrl: {
        type: "string",
        description: "Webhook 回调地址",
      },
      workflowId: {
        type: "string",
        description: "工作流 ID (默认使用配置的 ID)",
      },
      poll_interval: {
        type: "number",
        description: "轮询间隔 (秒)",
        default: 5,
      },
      timeout: {
        type: "number",
        description: "超时时间 (秒)",
        default: 300,
      },
    },
    required: ["nodeInfoList"],
  },

  async run(params) {
    const {
      nodeInfoList,
      instanceType = "default",
      usePersonalQueue = false,
      webhookUrl,
      workflowId,
      poll_interval = 5,
      timeout = 300,
    } = params;

    // 获取配置
    const apiKey = this.env?.RUNNINGHUB_API_KEY || this.config?.apiKey;
    const defaultWorkflowId = this.env?.RUNNINGHUB_WORKFLOW_ID || this.config?.workflowId;
    const apiBase = this.env?.RUNNINGHUB_API_BASE || "https://www.runninghub.cn/openapi/v2";

    // 验证必需参数
    if (!apiKey) {
      throw new Error("缺少 RUNNINGHUB_API_KEY 配置");
    }

    const finalWorkflowId = workflowId || defaultWorkflowId;
    if (!finalWorkflowId) {
      throw new Error("缺少工作流 ID，请设置 RUNNINGHUB_WORKFLOW_ID 或传入 workflowId 参数");
    }

    // 构建提交请求
    const submitUrl = `${apiBase}/run/ai-app/${finalWorkflowId}`;
    const submitBody = {
      nodeInfoList: nodeInfoList,
      instanceType: instanceType,
      usePersonalQueue: usePersonalQueue.toString(),
    };

    if (webhookUrl) {
      submitBody.webhookUrl = webhookUrl;
    }

    try {
      // 1. 提交任务
      console.log(`[RunningHub] 提交任务到工作流 ${finalWorkflowId}...`);
      
      const submitResponse = await fetch(submitUrl, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${apiKey}`,
        },
        body: JSON.stringify(submitBody),
      });

      const submitResult = await submitResponse.json();

      if (!submitResponse.ok) {
        throw new Error(`提交失败 (${submitResponse.status}): ${submitResult.errorMessage || submitResult.message}`);
      }

      const taskId = submitResult.taskId;
      console.log(`[RunningHub] 任务已提交. Task ID: ${taskId}, 状态: ${submitResult.status}`);

      // 如果不想等待，直接返回
      if (poll_interval <= 0 || timeout <= 0) {
        return {
          success: true,
          message: "任务已提交",
          task_id: taskId,
          status: submitResult.status,
          workflow_id: finalWorkflowId,
          query_url: `${apiBase}/query`,
        };
      }

      // 2. 轮询查询结果
      console.log(`[RunningHub] 开始轮询查询结果...`);
      
      const queryUrl = `${apiBase}/query`;
      const startTime = Date.now();
      let attempts = 0;
      const maxAttempts = Math.ceil(timeout / poll_interval);

      while (Date.now() - startTime < timeout * 1000) {
        attempts++;
        await new Promise(resolve => setTimeout(resolve, poll_interval * 1000));

        const queryResponse = await fetch(queryUrl, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "Authorization": `Bearer ${apiKey}`,
          },
          body: JSON.stringify({ taskId }),
        });

        if (!queryResponse.ok) {
          throw new Error(`查询失败 (${queryResponse.status})`);
        }

        const queryResult = await queryResponse.json();
        const status = queryResult.status;
        const elapsed = Math.round((Date.now() - startTime) / 1000);

        console.log(`[RunningHub] 尝试 ${attempts}/${maxAttempts}, 状态: ${status}, 耗时: ${elapsed}s`);

        if (status === "SUCCESS") {
          // 成功
          const results = queryResult.results || [];
          const images = results
            .filter(r => r.outputType === "png" || r.outputType === "jpg")
            .map(r => ({
              url: r.url,
              type: r.outputType,
              text: r.text,
            }));

          console.log(`[RunningHub] 任务成功完成! 耗时: ${elapsed}s, 生成 ${images.length} 张图像`);

          return {
            success: true,
            message: `图像生成成功`,
            task_id: taskId,
            status: "completed",
            workflow_id: finalWorkflowId,
            elapsed_seconds: elapsed,
            results: results,
            images: images,
          };
        } else if (status === "FAILED") {
          // 失败
          const errorMsg = queryResult.errorMessage || queryResult.failedReason?.error || "未知错误";
          console.log(`[RunningHub] 任务失败: ${errorMsg}`);
          
          return {
            success: false,
            error: errorMsg,
            message: "图像生成失败",
            task_id: taskId,
            status: "failed",
            failed_reason: queryResult.failedReason,
          };
        } else if (status === "RUNNING" || status === "QUEUED") {
          // 继续轮询
          continue;
        } else {
          // 其他状态
          console.log(`[RunningHub] 未知状态: ${status}`);
          if (attempts >= maxAttempts) {
            return {
              success: false,
              error: `超时，任务状态: ${status}`,
              message: "等待任务完成超时",
              task_id: taskId,
              status: status,
            };
          }
        }
      }

      // 超时
      return {
        success: false,
        error: "任务执行超时",
        message: `等待超过 ${timeout} 秒`,
        task_id: taskId,
        status: "timeout",
      };

    } catch (error) {
      console.error(`[RunningHub] 错误: ${error.message}`);
      return {
        success: false,
        error: error.message,
        message: "生成图像失败",
      };
    }
  },
};

/**
 * 辅助函数：仅提交任务，不等待结果
 * 
 * 使用示例:
 * const result = await submitTask({
 *   nodeInfoList: [{ nodeId: "77", fieldName: "image", fieldValue: "xxx.png" }],
 *   workflowId: "2009362441569832961"
 * });
 */
export async function submitTask(params, config = {}) {
  const {
    nodeInfoList,
    instanceType = "default",
    usePersonalQueue = false,
    webhookUrl,
    workflowId,
  } = params;

  const apiKey = config.apiKey || process.env.RUNNINGHUB_API_KEY;
  const apiBase = config.apiBase || "https://www.runninghub.cn/openapi/v2";
  const defaultWorkflowId = config.workflowId || process.env.RUNNINGHUB_WORKFLOW_ID;
  const finalWorkflowId = workflowId || defaultWorkflowId;

  const submitUrl = `${apiBase}/run/ai-app/${finalWorkflowId}`;
  const submitBody = {
    nodeInfoList: nodeInfoList,
    instanceType: instanceType,
    usePersonalQueue: usePersonalQueue.toString(),
  };

  if (webhookUrl) {
    submitBody.webhookUrl = webhookUrl;
  }

  const response = await fetch(submitUrl, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Authorization": `Bearer ${apiKey}`,
    },
    body: JSON.stringify(submitBody),
  });

  const result = await response.json();

  if (!response.ok) {
    throw new Error(`提交失败: ${result.errorMessage || result.message}`);
  }

  return {
    success: true,
    task_id: result.taskId,
    status: result.status,
    workflow_id: finalWorkflowId,
    client_id: result.clientId,
    prompt_tips: result.promptTips,
  };
}

/**
 * 辅助函数：查询任务状态
 * 
 * 使用示例:
 * const status = await queryTask({ taskId: "xxx" });
 */
export async function queryTask(params, config = {}) {
  const { taskId } = params;
  const apiKey = config.apiKey || process.env.RUNNINGHUB_API_KEY;
  const apiBase = config.apiBase || "https://www.runninghub.cn/openapi/v2";

  if (!taskId) {
    throw new Error("缺少 taskId 参数");
  }

  const response = await fetch(`${apiBase}/query`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Authorization": `Bearer ${apiKey}`,
    },
    body: JSON.stringify({ taskId }),
  });

  const result = await response.json();

  if (!response.ok) {
    throw new Error(`查询失败: ${result.message}`);
  }

  return {
    success: true,
    task_id: result.taskId,
    status: result.status,
    results: result.results,
    error_message: result.errorMessage,
    failed_reason: result.failedReason,
    usage: result.usage,
  };
}
