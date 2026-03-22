"""
RunningHub Image Generation Skill (Python Version)

通过 RunningHub API 调用云端 ComfyUI 工作流生成 AI 图像

API 文档: https://www.runninghub.cn/call-api/api-detail/{workflow_id}?apiType=4
"""

import json
import time
from typing import Optional, Dict, Any, List

# Skill 元数据
SKILL_NAME = "runninghubskill"
SKILL_DESCRIPTION = "使用 RunningHub 云端 ComfyUI 生成 AI 图像"


def get_parameters() -> Dict[str, Any]:
    """返回 skill 参数定义"""
    return {
        "type": "object",
        "properties": {
            "nodeInfoList": {
                "type": "array",
                "description": "节点参数映射列表",
                "items": {
                    "type": "object",
                    "properties": {
                        "nodeId": {
                            "type": "string",
                            "description": "节点 ID",
                        },
                        "fieldName": {
                            "type": "string",
                            "description": "字段名称 (如 image, prompt)",
                        },
                        "fieldValue": {
                            "type": "string",
                            "description": "字段值",
                        },
                        "description": {
                            "type": "string",
                            "description": "参数描述",
                        },
                    },
                    "required": ["nodeId", "fieldName", "fieldValue"],
                },
            },
            "instanceType": {
                "type": "string",
                "description": "运行实例类型 (default/plus)",
                "default": "default",
            },
            "usePersonalQueue": {
                "type": "boolean",
                "description": "是否使用个人独占队列",
                "default": False,
            },
            "webhookUrl": {
                "type": "string",
                "description": "Webhook 回调地址",
            },
            "workflowId": {
                "type": "string",
                "description": "工作流 ID (默认使用配置的 ID)",
            },
            "poll_interval": {
                "type": "number",
                "description": "轮询间隔 (秒)",
                "default": 5,
            },
            "timeout": {
                "type": "number",
                "description": "超时时间 (秒)",
                "default": 300,
            },
        },
        "required": ["nodeInfoList"],
    }


def _get_config(
    config: Optional[Dict[str, Any]] = None,
    env: Optional[Dict[str, str]] = None,
) -> Dict[str, str]:
    """获取 API 配置"""
    return {
        "api_key": env.get("RUNNINGHUB_API_KEY") or config.get("apiKey") if config else None,
        "workflow_id": env.get("RUNNINGHUB_WORKFLOW_ID") or config.get("workflowId") if config else None,
        "api_base": env.get("RUNNINGHUB_API_BASE", "https://www.runninghub.cn/openapi/v2"),
    }


async def run(
    params: Dict[str, Any],
    config: Optional[Dict[str, Any]] = None,
    env: Optional[Dict[str, str]] = None,
) -> Dict[str, Any]:
    """
    主运行函数

    Args:
        params: 用户输入参数
        config: Skill 配置
        env: 环境变量

    Returns:
        生成结果
    """
    node_info_list = params.get("nodeInfoList", [])
    instance_type = params.get("instanceType", "default")
    use_personal_queue = params.get("usePersonalQueue", False)
    webhook_url = params.get("webhookUrl")
    workflow_id_param = params.get("workflowId")
    poll_interval = params.get("poll_interval", 5)
    timeout = params.get("timeout", 300)

    # 获取配置
    cfg = _get_config(config, env)
    api_key = cfg["api_key"]
    default_workflow_id = cfg["workflow_id"]
    api_base = cfg["api_base"]

    # 验证必需参数
    if not api_key:
        return {
            "success": False,
            "error": "缺少 RUNNINGHUB_API_KEY 配置",
            "message": "请在环境变量或 skill 配置中设置 apiKey",
        }

    if not node_info_list:
        return {
            "success": False,
            "error": "缺少必需的参数: nodeInfoList",
            "message": "请提供节点参数映射列表",
        }

    final_workflow_id = workflow_id_param or default_workflow_id
    if not final_workflow_id:
        return {
            "success": False,
            "error": "缺少工作流 ID",
            "message": "请设置 RUNNINGHUB_WORKFLOW_ID 或传入 workflowId 参数",
        }

    # 构建提交请求
    submit_url = f"{api_base}/run/ai-app/{final_workflow_id}"
    submit_body = {
        "nodeInfoList": node_info_list,
        "instanceType": instance_type,
        "usePersonalQueue": str(use_personal_queue),
    }

    if webhook_url:
        submit_body["webhookUrl"] = webhook_url

    try:
        # 1. 提交任务
        print(f"[RunningHub] 提交任务到工作流 {final_workflow_id}...")

        import aiohttp

        async with aiohttp.ClientSession() as session:
            async with session.post(
                submit_url,
                json=submit_body,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {api_key}",
                },
                timeout=aiohttp.ClientTimeout(total=60),
            ) as submit_response:

                submit_result = await submit_response.json()

                if not submit_response.ok:
                    error_msg = submit_result.get("errorMessage") or submit_result.get("message")
                    return {
                        "success": False,
                        "error": f"提交失败 ({submit_response.status})",
                        "message": error_msg or "未知错误",
                    }

                task_id = submit_result.get("taskId")
                status = submit_result.get("status")
                print(f"[RunningHub] 任务已提交. Task ID: {task_id}, 状态: {status}")

                # 如果不想等待，直接返回
                if poll_interval <= 0 or timeout <= 0:
                    return {
                        "success": True,
                        "message": "任务已提交",
                        "task_id": task_id,
                        "status": status,
                        "workflow_id": final_workflow_id,
                        "query_url": f"{api_base}/query",
                    }

                # 2. 轮询查询结果
                print(f"[RunningHub] 开始轮询查询结果...")

                query_url = f"{api_base}/query"
                start_time = time.time()
                attempts = 0
                max_attempts = timeout // poll_interval + 1

                while time.time() - start_time < timeout:
                    attempts += 1
                    await asyncio.sleep(poll_interval)

                    async with session.post(
                        query_url,
                        json={"taskId": task_id},
                        headers={
                            "Content-Type": "application/json",
                            "Authorization": f"Bearer {api_key}",
                        },
                    ) as query_response:

                        if not query_response.ok:
                            return {
                                "success": False,
                                "error": f"查询失败 ({query_response.status})",
                                "message": "查询任务状态失败",
                            }

                        query_result = await query_response.json()
                        status = query_result.get("status")
                        elapsed = int(time.time() - start_time)

                        print(f"[RunningHub] 尝试 {attempts}, 状态: {status}, 耗时: {elapsed}s")

                        if status == "SUCCESS":
                            # 成功
                            results = query_result.get("results", [])
                            images = [
                                {
                                    "url": r.get("url"),
                                    "type": r.get("outputType"),
                                    "text": r.get("text"),
                                }
                                for r in results
                                if r.get("outputType") in ["png", "jpg", "jpeg"]
                            ]

                            print(f"[RunningHub] 任务成功完成! 耗时: {elapsed}s, 生成 {len(images)} 张图像")

                            return {
                                "success": True,
                                "message": "图像生成成功",
                                "task_id": task_id,
                                "status": "completed",
                                "workflow_id": final_workflow_id,
                                "elapsed_seconds": elapsed,
                                "results": results,
                                "images": images,
                                "usage": query_result.get("usage"),
                            }

                        elif status == "FAILED":
                            # 失败
                            error_msg = query_result.get("errorMessage") or query_result.get("failedReason", {}).get("error")
                            print(f"[RunningHub] 任务失败: {error_msg}")

                            return {
                                "success": False,
                                "error": error_msg or "未知错误",
                                "message": "图像生成失败",
                                "task_id": task_id,
                                "status": "failed",
                                "failed_reason": query_result.get("failedReason"),
                            }

                        elif status in ["RUNNING", "QUEUED"]:
                            # 继续轮询
                            continue

                        else:
                            # 其他状态
                            if attempts >= max_attempts:
                                return {
                                    "success": False,
                                    "error": f"超时，任务状态: {status}",
                                    "message": "等待任务完成超时",
                                    "task_id": task_id,
                                    "status": status,
                                }

                # 超时
                return {
                    "success": False,
                    "error": "任务执行超时",
                    "message": f"等待超过 {timeout} 秒",
                    "task_id": task_id,
                    "status": "timeout",
                }

    except ImportError:
        # 如果 aiohttp 未安装，使用同步请求
        import requests

        # 1. 提交任务
        print(f"[RunningHub] 提交任务到工作流 {final_workflow_id}...")

        submit_response = requests.post(
            submit_url,
            json=submit_body,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}",
            },
            timeout=60,
        )

        submit_result = submit_response.json()

        if not submit_response.ok:
            error_msg = submit_result.get("errorMessage") or submit_result.get("message")
            return {
                "success": False,
                "error": f"提交失败 ({submit_response.status_code})",
                "message": error_msg or "未知错误",
            }

        task_id = submit_result.get("taskId")
        status = submit_result.get("status")
        print(f"[RunningHub] 任务已提交. Task ID: {task_id}, 状态: {status}")

        # 如果不想等待，直接返回
        if poll_interval <= 0 or timeout <= 0:
            return {
                "success": True,
                "message": "任务已提交",
                "task_id": task_id,
                "status": status,
                "workflow_id": final_workflow_id,
                "query_url": f"{api_base}/query",
            }

        # 2. 轮询查询结果
        print(f"[RunningHub] 开始轮询查询结果...")

        query_url = f"{api_base}/query"
        start_time = time.time()
        attempts = 0
        max_attempts = timeout // poll_interval + 1

        while time.time() - start_time < timeout:
            attempts += 1
            time.sleep(poll_interval)

            query_response = requests.post(
                query_url,
                json={"taskId": task_id},
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {api_key}",
                },
            )

            if not query_response.ok:
                return {
                    "success": False,
                    "error": f"查询失败 ({query_response.status_code})",
                    "message": "查询任务状态失败",
                }

            query_result = query_response.json()
            status = query_result.get("status")
            elapsed = int(time.time() - start_time)

            print(f"[RunningHub] 尝试 {attempts}, 状态: {status}, 耗时: {elapsed}s")

            if status == "SUCCESS":
                # 成功
                results = query_result.get("results", [])
                images = [
                    {
                        "url": r.get("url"),
                        "type": r.get("outputType"),
                        "text": r.get("text"),
                    }
                    for r in results
                    if r.get("outputType") in ["png", "jpg", "jpeg"]
                ]

                print(f"[RunningHub] 任务成功完成! 耗时: {elapsed}s, 生成 {len(images)} 张图像")

                return {
                    "success": True,
                    "message": "图像生成成功",
                    "task_id": task_id,
                    "status": "completed",
                    "workflow_id": final_workflow_id,
                    "elapsed_seconds": elapsed,
                    "results": results,
                    "images": images,
                    "usage": query_result.get("usage"),
                }

            elif status == "FAILED":
                # 失败
                error_msg = query_result.get("errorMessage") or query_result.get("failedReason", {}).get("error")
                print(f"[RunningHub] 任务失败: {error_msg}")

                return {
                    "success": False,
                    "error": error_msg or "未知错误",
                    "message": "图像生成失败",
                    "task_id": task_id,
                    "status": "failed",
                    "failed_reason": query_result.get("failedReason"),
                }

            elif status in ["RUNNING", "QUEUED"]:
                # 继续轮询
                continue

            else:
                # 其他状态
                if attempts >= max_attempts:
                    return {
                        "success": False,
                        "error": f"超时，任务状态: {status}",
                        "message": "等待任务完成超时",
                        "task_id": task_id,
                        "status": status,
                    }

        # 超时
        return {
            "success": False,
            "error": "任务执行超时",
            "message": f"等待超过 {timeout} 秒",
            "task_id": task_id,
            "status": "timeout",
        }

    except Exception as e:
        print(f"[RunningHub] 错误: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "message": "生成图像时发生错误",
        }


async def submit_task(
    params: Dict[str, Any],
    config: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    仅提交任务，不等待结果

    Args:
        params: 任务参数
        config: 配置

    Returns:
        提交结果
    """
    node_info_list = params.get("nodeInfoList", [])
    instance_type = params.get("instanceType", "default")
    use_personal_queue = params.get("usePersonalQueue", False)
    webhook_url = params.get("webhookUrl")
    workflow_id = params.get("workflowId")

    cfg = _get_config(config)
    api_key = cfg["api_key"]
    default_workflow_id = cfg["workflow_id"]
    api_base = cfg["api_base"]

    final_workflow_id = workflow_id or default_workflow_id
    submit_url = f"{api_base}/run/ai-app/{final_workflow_id}"

    submit_body = {
        "nodeInfoList": node_info_list,
        "instanceType": instance_type,
        "usePersonalQueue": str(use_personal_queue),
    }

    if webhook_url:
        submit_body["webhookUrl"] = webhook_url

    import aiohttp

    async with aiohttp.ClientSession() as session:
        async with session.post(
            submit_url,
            json=submit_body,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}",
            },
        ) as response:

            result = await response.json()

            if not response.ok:
                raise Exception(f"提交失败: {result.get('errorMessage') or result.get('message')}")

            return {
                "success": True,
                "task_id": result.get("taskId"),
                "status": result.get("status"),
                "workflow_id": final_workflow_id,
                "client_id": result.get("clientId"),
                "prompt_tips": result.get("promptTips"),
            }


async def query_task(
    task_id: str,
    config: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    查询任务状态

    Args:
        task_id: 任务 ID
        config: 配置

    Returns:
        任务状态
    """
    if not task_id:
        raise ValueError("缺少 taskId 参数")

    cfg = _get_config(config)
    api_key = cfg["api_key"]
    api_base = cfg["api_base"]

    import aiohttp

    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"{api_base}/query",
            json={"taskId": task_id},
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}",
            },
        ) as response:

            result = await response.json()

            if not response.ok:
                raise Exception(f"查询失败: {result.get('message')}")

            return {
                "success": True,
                "task_id": result.get("taskId"),
                "status": result.get("status"),
                "results": result.get("results"),
                "error_message": result.get("errorMessage"),
                "failed_reason": result.get("failedReason"),
                "usage": result.get("usage"),
            }


# 为了支持 asyncio.sleep
import asyncio
