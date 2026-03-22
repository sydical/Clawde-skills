---
tags:
  - OpenClaw
  - Agent
  - Proactive
  - 主动智能体
  - 评估
date: 2026-03-23
---

# Proactive Agent 技能对比与评估

> 三个主动型 Agent 技能的详细对比与使用建议

---

## 一、技能介绍

### 1. claw-opus/proactive-self-improving-agent

**Stars:** ⭐ 9  
**定位:** 自改进 + 主动型

**核心理念：** 两条腿走路
- **记录** — 每次犯错、被纠正、发现最佳实践时立刻结构化记录
- **进化** — 反复出现的经验自动晋升为永久能力

**7 种触发条件：**

| # | 场景 | 记录到 |
|---|---|---|
| 1 | 命令/操作失败 | ERRORS.md |
| 2 | 用户纠正（"不对"/"应该是"） | LEARNINGS.md |
| 3 | 用户需要不存在的能力 | FEATURE_REQUESTS.md |
| 4 | 外部 API/工具出错 | ERRORS.md |
| 5 | 发现知识过时/错误 | LEARNINGS.md |
| 6 | 发现更好做法 | LEARNINGS.md |
| 7 | **任务完成时回顾** | LEARNINGS.md |

**经验进化路径：**
```
.learnings/*.md → AGENTS.md/TOOLS.md/SOUL.md → skills/<新技能>/
```

**安全护栏：**
- ADL 协议：防止漂移，不增加无意义复杂度
- VFM 协议：价值优先，打分 <50 不晋升

---

### 2. nkchivas/openclaw-skill-proactive-agent

**版本:** 3.0.0  
**作者:** halthelobster (Hal Labs)

**三大支柱：**

| 支柱 | 说明 |
|------|------|
| **Proactive** | 预测需求，主动创造价值 |
| **Persistent** | 上下文丢失后仍能恢复 |
| **Self-Improving** | 越用越聪明，安全进化 |

**v3.0.0 新特性：**

| 特性 | 说明 |
|------|------|
| **WAL Protocol** | 写前日志，记录关键细节再响应 |
| **Working Buffer** | 危险区（60%上下文后）捕获每个交换 |
| **Compaction Recovery** | 上下文压缩后逐步恢复 |
| **Unified Search** | 说"不知道"前搜索所有来源 |
| **Security Hardening** | 技能安装审查、上下文防泄漏 |

**WAL Protocol 触发条件：**
- ✏️ 纠正信号（"不是X是Y"）
- 📍 专有名词（名字、地点、公司）
- 🎨 偏好（颜色、风格）
- 📋 决策（"用X方案"）
- 📝 草稿修改
- 🔢 具体数值

**Memory 三层架构：**

| 文件 | 用途 |
|------|------|
| SESSION-STATE.md | 活跃工作内存 |
| memory/YYYY-MM-DD.md | 每日原始日志 |
| MEMORY.md | 长期记忆 |

---

### 3. jiyangnan/proactive-agent-skill

**定位:** 主动发现问题并汇报的标准化框架

**核心区别：**

| 传统 Agent | Proactive Agent |
|------------|----------------|
| 等命令 → 执行 → 报告 | 主动发现 → 实时监控 → 提前预警 |

**三层架构：**

| 层级 | 功能 | 文件/工具 |
|------|------|-----------|
| 1. 心跳机制 | 定期检查任务 | HEARTBEAT.md |
| 2. 异常检测 | 执行时监控指标 | heartbeat-helper.js |
| 3. 主动汇报 | 发现即通知 | message 工具 |

**监控异常类型：**

| 异常类型 | 检测条件 |
|----------|----------|
| 性能异常 | CPU > 90%、执行时间 > 预期 10x |
| 数据异常 | 文件过大、指数级增长 |
| 外部依赖 | API 配额不足、服务不可用 |
| 业务异常 | 任务连续失败 > 3 次 |

**汇报格式：**

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

---

## 二、评估对比

| 版本 | 推荐指数 | 复杂度 | 特点 |
|------|---------|--------|------|
| **claw-opus** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | 自改进 + 7种触发 + 经验进化 |
| **nkchivas v3** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | WAL + Working Buffer + 安全加固 |
| **jiyangnan** | ⭐⭐⭐⭐ | ⭐⭐ | 心跳 + 异常检测 + 主动汇报 |

---

## 三、应用场景详细说明

### 场景一：日常 AI 助理 👤

**推荐技能：claw-opus**

**描述：**
你每天和 AI 讨论各种问题、学习新知识、完成任务。

**工作流程：**
- 纠正 AI 的错误 → 自动记入 LEARNINGS.md
- 发现更好的方法 → 沉淀到 TOOLS.md
- 任务完成回顾 → 形成最佳实践

**效果：**
越用越懂你，错误不重复犯，经验不断累积。

---

### 场景二：复杂项目开发 💻

**推荐技能：nkchivas v3**

**描述：**
开发大型项目，需要跨多会话协作。

**工作流程：**
- 第一天：设计架构，写入 SESSION-STATE.md
- 第二天：上下文压缩后，Working Buffer 自动恢复
- 第三天：继续开发，AI 记得之前的决策
- 遇到问题：WAL Protocol 记录所有关键变更

**效果：**
项目不中断，知识不丢失，上下文的连续性有保障。

---

### 场景三：系统监控运维 🖥️

**推荐技能：jiyangnan**

**描述：**
部署在服务器上跑定时任务，需要实时监控告警。

**工作流程：**
- 每小时检查服务状态
- CPU/内存异常 → 立即发消息通知
- 任务失败 > 3 次 → 主动预警
- API 配额不足 → 提前告知

**效果：**
人在睡觉，AI 帮忙盯着，出问题第一时间知道。

---

### 场景四：All-in-One 方案 🚀

**推荐组合：claw-opus + nkchivas v3**

**理由：**
- claw-opus 负责经验记录和进化
- nkchivas v3 负责上下文持久化和恢复
- 两者互补，形成完整的能力增强体系

---

## 四、选择建议

| 你的需求 | 推荐技能 |
|----------|----------|
| 日常对话助理 | claw-opus |
| 代码/项目开发 | nkchivas v3 |
| 服务器运维监控 | jiyangnan |
| 全面能力增强 | claw-opus + nkchivas v3 |

---

## 五、当前安装状态

- ✅ proactive-self-improving-agent (claw-opus) — 已安装
- ⬜ openclaw-skill-proactive-agent (nkchivas)
- ⬜ proactive-agent-skill (jiyangnan)

---

## 六、我的评价（作为 AI 助手的视角）

作为一线 AI 助手，这三个技能解决的核心问题是：

> **如何让 AI 不仅仅是被动响应，而是主动创造价值。**

### claw-opus 的优势

最符合"学习进化"的逻辑，7 种触发条件覆盖全面，有去重机制避免记录垃圾，经验晋升路径清晰。适合长期使用的个人助理。

### nkchivas v3 的优势

**WAL Protocol 太实用！** 纠正/偏好/决策自动落盘，Working Buffer 解决上下文丢失痛点。适合技术用户和复杂项目。

### jiyangnan 的优势

最"主动"的一个，真正会主动发消息，异常检测覆盖全面，汇报格式标准化。适合运维监控场景。

---

## 七、安装命令

```bash
# claw-opus
openclaw add https://github.com/yanhongxi-openclaw/proactive-self-improving-agent

# nkchivas v3
git clone https://github.com/nkchivas/openclaw-skill-proactive-agent.git ~/.openclaw/skills/openclaw-skill-proactive-agent

# jiyangnan
git clone https://github.com/jiyangnan/proactive-agent-skill.git ~/.openclaw/workspace/skills/proactive-agent-skill
```

---

## 相关笔记

- [[AI-Agent-创业策略与行业洞察]]
- [[OpenClaw-Scrapling-相关文章]]
- [[未来企业的变更：组织智能化]]
