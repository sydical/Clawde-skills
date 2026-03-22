---
tags:
  - OpenClaw
  - Superpowers
  - Agent
  - 技能库
date: 2026-03-23
---

# openclaw-superpowers 技能全解析

> 53 个即插即用技能，让 AI 自主、自愈、自改进

---

## 一、简介

**Stars:** ⭐ 26  
**定位：** 44+ 个即插即用技能，让 AI 自主、自愈、自改进  
**来源：** 基于 obra/superpowers 扩展

**核心理念：**
- Think before it acts
- Protect itself
- Run unattended
- Verify itself
- Recover from failures
- Never forget
- Improve itself

---

## 二、53 个技能分类

### 🧠 核心方法论（15个）

| 技能 | 功能 | 评估 |
|------|------|------|
| **using-superpowers** | 技能系统入门 | ⭐⭐⭐⭐⭐ 必装 |
| **brainstorming** | 结构化头脑风暴 | ⭐⭐⭐⭐⭐ 必装 |
| **writing-plans** | 清晰计划 | ⭐⭐⭐⭐⭐ 必装 |
| **executing-plans** | 逐步执行+验证 | ⭐⭐⭐⭐⭐ 必装 |
| **systematic-debugging** | 4阶段根因分析 | ⭐⭐⭐⭐⭐ 必装 |
| **verification-before-completion** | 完成验证 | ⭐⭐⭐⭐⭐ 必装 |
| **test-driven-development** | TDD 开发 | ⭐⭐⭐⭐ 开发必装 |
| **subagent-driven-development** | 子 Agent 并行开发 | ⭐⭐⭐⭐ 复杂任务 |
| **create-skill** | 自己写新技能 | ⭐⭐⭐⭐⭐ 核心亮点 |
| **skill-vetting** | 安全扫描 | ⭐⭐⭐⭐⭐ 安全必装 |
| **project-onboarding** | 代码库入门 | ⭐⭐⭐⭐ 新项目 |
| **fact-check-before-trust** | 事实核查 | ⭐⭐⭐⭐ 高要求场景 |
| **skill-trigger-tester** | 技能触发测试 | ⭐⭐⭐ 开发者 |
| **skill-conflict-detector** | 技能冲突检测 | ⭐⭐⭐ 开发者 |
| **skill-portability-checker** | 跨平台检查 | ⭐⭐⭐ 开发者 |

---

### ⚙️ OpenClaw 原生技能（37个）

#### 🏃 持久运行

| 技能 | 功能 | Cron | 评估 |
|------|------|------|------|
| **long-running-task-management** | 多小时任务分阶段 | 15分钟 | ⭐⭐⭐⭐⭐ 核心 |
| **task-handoff** | 任务交接 | - | ⭐⭐⭐⭐⭐ 持久必装 |
| **agent-self-recovery** | 循环检测+逃脱 | - | ⭐⭐⭐⭐⭐ 自愈 |
| **context-window-management** | 上下文溢出预防 | - | ⭐⭐⭐⭐⭐ 必装 |
| **persistent-memory-hygiene** | 内存清洁 | 23点 | ⭐⭐⭐⭐⭐ 必装 |

#### 📊 每日/周期任务

| 技能 | 功能 | Cron | 评估 |
|------|------|------|------|
| **morning-briefing** | 早间简报 | 7点 | ⭐⭐⭐⭐⭐ 推荐 |
| **daily-review** | 每日总结 | 18点 | ⭐⭐⭐⭐⭐ 推荐 |
| **secrets-hygiene** | 凭证审计 | 周一9点 | ⭐⭐⭐⭐ 安全 |
| **cron-hygiene** | Cron 效率审计 | 周一9点 | ⭐⭐⭐ 优化用 |
| **workspace-integrity-guardian** | 工作区完整性 | 周日3点 | ⭐⭐⭐⭐ 安全 |
| **community-skill-radar** | Reddit 扫描 | 3天 | ⭐⭐⭐⭐ 开发者 |

#### 🛡️ 安全防护

| 技能 | 功能 | 评估 |
|------|------|------|
| **prompt-injection-guard** | 注入检测 | ⭐⭐⭐⭐⭐ 必装 |
| **dangerous-action-guard** | 危险操作确认 | ⭐⭐⭐⭐⭐ 必装 |
| **installed-skill-auditor** | 技能审计 | ⭐⭐⭐⭐⭐ 安全 |
| **skill-doctor** | 技能诊断 | ⭐⭐⭐⭐ 排错 |
| **config-encryption-auditor** | 凭证加密检查 | ⭐⭐⭐⭐ 安全 |

#### 💰 资源管理

| 技能 | 功能 | Cron | 评估 |
|------|------|------|------|
| **spend-circuit-breaker** | 预算追踪 | 4小时 | ⭐⭐⭐⭐ 必装 |
| **heartbeat-governor** | 执行预算 | 1小时 | ⭐⭐⭐⭐ 成本控制 |
| **context-budget-guard** | 上下文预算 | - | ⭐⭐⭐⭐ 必装 |

#### 🧠 记忆增强

| 技能 | 功能 | Cron | 评估 |
|------|------|------|------|
| **memory-graph-builder** | 记忆图谱 | 22点 | ⭐⭐⭐⭐⭐ 高级 |
| **memory-dag-compactor** | DAG 压缩 | 23点 | ⭐⭐⭐⭐⭐ 高级 |
| **session-persistence** | SQLite 持久化 | 15分钟 | ⭐⭐⭐⭐⭐ 长期 |
| **dag-recall** | DAG 召回 | - | ⭐⭐⭐⭐⭐ 高级 |
| **context-assembly-scorer** | 上下文评分 | 4小时 | ⭐⭐⭐⭐ 优化 |

---

## 三、评估总结

### ⭐⭐⭐⭐⭐ 必装技能（15个）

1. **using-superpowers** - 技能系统入门
2. **brainstorming** - 头脑风暴
3. **writing-plans** - 计划
4. **executing-plans** - 执行
5. **systematic-debugging** - 调试
6. **verification-before-completion** - 验证
7. **create-skill** - 自改进
8. **skill-vetting** - 安全扫描
9. **long-running-task-management** - 长程任务
10. **task-handoff** - 任务交接
11. **agent-self-recovery** - 自恢复
12. **context-window-management** - 上下文管理
13. **persistent-memory-hygiene** - 内存清洁
14. **prompt-injection-guard** - 注入防护
15. **dangerous-action-guard** - 危险操作确认

---

## 四、场景应用

| 场景 | 推荐技能组合 |
|------|-------------|
| **日常开发** | brainstorming + TDD + debugging + verification |
| **24/7 无人值守** | long-running + self-recovery + handoff + morning-briefing |
| **安全敏感** | skill-vetting + prompt-injection-guard + dangerous-action-guard + secrets-hygiene |
| **成本控制** | spend-circuit-breaker + heartbeat-governor + context-budget-guard |
| **长期记忆** | memory-graph-builder + dag-compactor + session-persistence |
| **多 Agent 协作** | multi-agent-coordinator + skill-loadout-manager |

---

## 五、对比总结

| 能力 | openclaw-superpowers | 其他方案 |
|------|---------------------|---------|
| 技能数 | **53** | - |
| 自改进 | ✅ 自己写技能 | ❌ |
| Cron 定时 | **20 个** | ❌ |
| 安全防护 | **6 层防御** | ❌ |
| 记忆增强 | DAG + 图谱 + SQLite | ❌ |
| MCP 监控 | ✅ | ❌ |
| 成本控制 | ✅ 预算追踪 | ❌ |

---

## 六、Superpowers 系列对比

| 版本 | 技能数 | 特点 |
|------|--------|------|
| obra/superpowers | 14 | 原始方法论，跨平台 |
| maloqab | 14 | 适配 OpenClaw，角色模板 |
| **ArchieIndian** | **44+** | **最全，Security + Cron + 自改进** |

---

## 七、安装

```bash
git clone https://github.com/ArchieIndian/openclaw-superpowers ~/.openclaw/src/openclaw-superpowers
cd ~/.openclaw/src/openclaw-superpowers && ./install.sh
openclaw gateway restart
```

---

## 八、相关笔记

- [[Proactive-Agent-技能对比与评估]]
- [[AI-Agent-创业策略与行业洞察]]
- [[OpenClaw-Scrapling-相关文章]]
