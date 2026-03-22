---
title: vLLM 部署 Qwen3.5 满血&量化版，并发性能测试，附部署脚本
date: 2026-03-09
tags: [vLLM, Qwen3.5, 部署, 性能测试, AI]
author: 老章很忙
platform: 微信公众号
status: 已保存
---

# vLLM 部署 Qwen3.5 满血&量化版，并发性能测试，附部署脚本

> 作者：老章很忙  
> 来源：微信公众号「老章很忙」  
> 日期：2026年3月9日 09:28

---

## 前言

最近 OpenClaw 在国内火的有点离谱，主要是我个人一直玩的是自己折腾的一套，比较放心。我用 Opencode 做了一个 FakeClawBot，不过本周我会测试国产的两个 Claw，敬请期待。

本文继续折腾 Qwen3.5，不出意外是最后一篇了。

## Qwen3.5 系列选择建议

- **无脑选 Qwen3.5-27B**
- 小模型：0.8B 到 9B 毫无保留

## vLLM 部署

vLLM v0.17.0 来了，Qwen3.5 全系列完美支持，Anthropic API 兼容，趁着周末，玩一下。

### 升级 vLLM

唯一需要注意的是自己的硬件及 CUDA 版本。使用 Docker 正常拉取镜像即可：

```bash
docker pull vllm/vllm-openai:v0.17.0
```

### 模型权重

- **35B 权重文件**：37GB
- **27B 权重文件**：30GB

遭遇各种 OOM 之后，最终调整到了一版合适的参数。

## 部署脚本

```bash
#!/usr/bin/env bash
set -euo pipefail

MODEL_DIR="/data/models/Qwen3.5-35B-A3B-FP8"
CONTAINER_NAME="qwen35-35b-a3b-fp8"
PORT=8000

docker rm -f ${CONTAINER_NAME} 2>/dev/null || true

docker run -d \
  --name ${CONTAINER_NAME} \
  --gpus '"device=0,1,2,3"' \
  --ipc=host \
  --shm-size=16g \
  -p ${PORT}:8000 \
  -v ${MODEL_DIR}:/model:ro \
  -e NCCL_P2P_DISABLE=0 \
  -e NCCL_IB_DISABLE=1 \
  -e VLLM_USE_V1=1 \
  vllm/vllm-openai:v0.17.0 \
  --model /model \
  --served-model-name qwen3.5-35b-a3b-fp8 \
  --tensor-parallel-size 4 \
  --max-model-len 262144 \
  --kv-cache-dtype fp8 \
  --gpu-memory-utilization 0.9 \
  --max-num-seqs 4 \
  --max-num-batched-tokens 8192 \
  --language-model-only \
  --enable-prefix-caching \
  --default-chat-template-kwargs '{"enable_thinking": false}' \
  --host 0.0.0.0 \
  --port 8000
```

### 参数说明

| 参数 | 说明 |
|------|------|
| `--tensor-parallel-size 4` | 4 张 4090 显卡 |
| `--max-model-len 262144` | 长上下文需求 |
| `--kv-cache-dtype fp8` | 降低 KV cache 内存占用 |
| `--gpu-memory-utilization 0.9` | 给真实运行时留空间 |
| `--max-num-seqs 4` | 避免长上下文+高并发爆显存 |
| `--max-num-batched-tokens 8192` | 控制一次调度总 token 规模 |
| `--language-model-only` | 只要文本推理，不要多模态 |
| `--enable-prefix-caching` | 高效 KV 管理和吞吐优化 |
| `--enable_thinking: false` | 关闭思考模式 |

## 量化版部署

实际运行性能特别差：
- 27B 几乎没有并发能力
- 35B-A3B 还可以，但 RPS 很低，首 Token 延迟都奔 10s 了

于是上了 4bit 量化版本：

- `cyankiwi/Qwen3.5-35B-A3B-AWQ-4bit`
- `cyankiwi/Qwen3.5-27B-AWS-4bit`

量化版更省卡，2 张 4090 就能跑起来，可以同时跑 27B 和 35B。

## 性能测试结果

### 27B
- 70+ t/s
- 代码能力不太能看
- 性能方面依然相当差劲

### 35B
- 100+ t/s
- 比 FP8 提升多了，也比 27B 强多了

## 总结

以作者的需求，暂时不想替代 Qwen3-32B，还是 32B 稳。

而且 Qwen3.5 还整了骚操作，把开头的 `<think>` 从"动态生成"变成了"静态预置"，下游对接的系统苦了。

再加上它本身不支持思考与否的软关闭，这个级别能力提升也不见能弥补这些缺点，企业级应用感觉很多都不太乐意升 3.5。

---

*原文链接：微信公众号「老章很忙」*
