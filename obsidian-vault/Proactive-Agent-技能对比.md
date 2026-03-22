---
tags:
  - OpenClaw
  - Agent
  - Proactive
  - 主动智能体
date: 2026-03-23
---

# Proactive Agent 技能对比

> 让 AI Agent 从"等命令"变成"主动发现问题并汇报"的三个技能

---

## 一、claw-opus/proactive-self-improving-agent

**Stars:** ⭐ 9  
**定位:** 自改进 + 主动型

### 核心理念

**两条腿走路：**
- **记录** — 每次犯错、被纠正、发现最佳实践时立刻结构化记录
- **进化** — 反复出现的经验自动晋升为永久能力

### 7 种触发条件

| # | 场景 | 记录到 |
|---|---|---|
| 1 | 命令/操作失败 | ERRORS.md |
| 2 | 用户纠正（"不对"/"应该是"） | LEARNINGS.md |
| 3 | 用户需要不存在的能力 | FEATURE_REQUESTS.md |
| 4 | 外部 API/工具出错 | ERRORS.md |
| 5 | 发现知识过时/错误 | LEARNINGS.md |
| 6 | 发现更好做法 | LEARNINGS.md |
| 7 | **任务完成时回顾** | LEARNINGS.md |

### 经验进化路径

```
.learnings/*.md → AGENTS.md/TOOLS.md/SOUL.md → skills/<新技能>/
```

### 安全护栏

- **ADL 协议**：防止漂移，不增加无意义复杂度
- **VFM 协议**：价值优先，打分 <50 不晋升

### 安装

```bash
openclaw add https://github.com/yanhongxi-openclaw/proactive-self-improving-agent
```

---

## 二、nkchivas/openclaw-skill-proactive-agent

**版本:** 3.0.0  
**作者:** halthelobster (Hal Labs)

### 三大支柱

| 支柱 | 说明 |
|------|------|
| **Proactive** | 预测需求，主动创造价值 |
| **Persistent** | 上下文丢失后仍能恢复 |
| **Self-Improving** | 越用越聪明，安全进化 |

### v3.0.0 新特性

| 特性 | 说明 |
|------|------|
| **WAL Protocol** | 写前日志，记录关键细节再响应 |
| **Working Buffer** | 危险区（60%上下文后）捕获每个交换 |
| **Compaction Recovery** | 上下文压缩后逐步恢复 |
| **Unified Search** | 说"不知道"前搜索所有来源 |
| **Security Hardening** | 技能安装审查、上下文防泄漏 |

### WAL Protocol 触发条件

- ✏️ 纠正信号（"不是X是Y"）
- 📍 专有名词（名字、地点、公司）
- 🎨 偏好（颜色、风格）
- 📋 决策（"用X方案"）
- 📝 草稿修改
- 🔢 具体数值

### Memory 三层架构

| 文件 | 用途 |
|------|------|
| SESSION-STATE.md | 活跃工作内存 |
| memory/YYYY-MM-DD.md | 每日原始日志 |
| MEMORY.md | 长期记忆 |

---

## 三、jiyangnan/proactive-agent-skill

**定位:** 主动发现问题并汇报的标准化框架

### 核心区别

| 传统 Agent | Proactive Agent |
|------------|----------------|
| 等命令 → 执行 → 报告 | 主动发现 → 实时监控 → 提前预警 |

### 三层架构

| 层级 | 功能 | 文件/工具 |
|------|------|-----------|
| 1. 心跳机制 | 定期检查任务 | HEARTBEAT.md |
| 2. 异常检测 | 执行时监控指标 | heartbeat-helper.js |
| 3. 主动汇报 | 发现即通知 | message 工具 |

### 监控异常类型

| 异常类型 | 检测条件 |
|----------|----------|
| 性能异常 | CPU > 90%、执行时间 > 预期 10x |
| 数据异常 | 文件过大、指数级增长 |
| 外部依赖 | API 配额不足、服务不可用 |
| 业务异常 | 任务连续失败 > 3 次 |

### 汇报格式

```json
{
  "severity": "critical",
  "title": "问题标题",
  "problem": "问题描述",
  "evidence": ["证据"],
  "impact": "影响",
  "recommendations": ["建议1", "建议2"]
}
```

### 安装

```bash
git clone https://github.com/jiyangnan/proactive-agent-skill.git \
 ~/.openclaw/workspace/skills/proactive-agent-skill
```

---

## 四、对比总结

| 版本 | 特点 | 复杂度 | 适合场景 |
|------|------|--------|---------|
| **claw-opus** | 自改进 + 7种触发 + 经验进化 | ⭐⭐⭐ | 想要自动记录经验并进化 |
| **nkchivas v3** | WAL + Working Buffer + 安全加固 | ⭐⭐⭐⭐ | 注重上下文持久化和恢复 |
| **jiyangnan** | 心跳 + 异常检测 + 主动汇报 | ⭐⭐ | 想要主动监控和预警 |

---

## 五、当前安装状态

- ✅ proactive-self-improving-agent (claw-opus)
- ⬜ openclaw-skill-proactive-agent (nkchivas)
- ⬜ proactive-agent-skill (jiyangnan)

---

## 相关笔记

- [[AI-Agent-创业策略与行业洞察]]
- [[OpenClaw-Scrapling-相关文章]]
- [[未来企业的变更：组织智能化]]
