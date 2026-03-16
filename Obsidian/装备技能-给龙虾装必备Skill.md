---
created: 2026-03-11
tags:
  - openclaw
  - 技能安装
category: 教程
---

# 装备技能-给龙虾装必备Skill

到这里，龙虾、飞书、OB、Claude Code 全装好了。但龙虾现在还只有最基础的能力——缺几个关键 Skill，整个"输入→处理→输出"的循环就转不起来。

比如：
- 你在飞书转发一篇公众号文章给龙虾，它得能解析链接内容（x-reader）
- 你让它搜个话题，它得有搜索引擎（Multi Search Engine）
- 你让它把整理好的内容存进 OB，它得有Obsidian Skill
- 你以后想自己找更多能力，它得有find-skills

这四个 Skill 是地基，必装。龙虾自带了 Skill Creator（创建新 Skill 的能力），不用额外装。

---

## 在 Dashboard 或飞书里发给龙虾：

帮我安装以下 4 个必备 Skill，按顺序来：

### 1. Multi Search Engine（免费搜索引擎，17 个搜索引擎覆盖国内外）

npx clawhub@latest install multi-search-engine

### 2. x-reader（国内链接解析：微信公众号、小红书、B 站、X 等）

pip install git+https://github.com/runesleo/x-reader.git

### 3. Obsidian（让你能直接往我的 OB 知识库里存东西）

npx clawhub@latest install obsidian

### 4. find-skills（搜索和发现更多 Skill）

npx clawhub@latest install find-skills

每装完一个，帮我验证是否安装成功，再装下一个。

---

## 进阶：一个精选的开源 Skill 库

必备的装完了，想让龙虾更强？推荐这个开源 Skill 库：

https://github.com/cafe3310/public-agent-skills

这是一位重度 Agent 用户整理的个人 Skill 合集，全部开源免费，覆盖四大场景：

- **创作与知识管理** · 语音转写、研究报告、去AI味
- **在线平台** · 部署到 ModelScope，一键发布到社区
- **项目管理** · PMP 迭代、TDD、轻量管理
- **辅助工具** · 媒体库整理、表情包制作

---

## 使用方法

安装好龙虾、对接好飞书后，你就有了一个住在聊天窗口里的 AI 助理。

💡 Agent Skill 本质是提示词和代码的集合。装之前建议让龙虾帮你审核一下内容，养成好习惯。
