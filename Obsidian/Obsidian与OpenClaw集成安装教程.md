---
created: 2026-03-11
tags:
  - openclaw
  - obsidian
  - 集成教程
category: 配置教程
---

# Obsidian与OpenClaw集成安装教程

安装Obsidian软件后，要启用与OpenClaw的集成，主要需要完成以下步骤：

---

## 1. 确认Obsidian已正确安装

确保已从官网（obsidian.md）下载并安装Obsidian

创建或打开一个已有的Vault（知识库）

记下Vault的完整路径（如：C:\Users\你的用户名\Documents\My Obsidian Vault）

---

## 2. 安装OpenClaw的Obsidian技能

推荐安装 obsidian-direct 技能，这是最直接的集成方式：

skillhub install obsidian-direct 

或使用clawhub命令：

clawhub install obsidian-direct 

---

## 3. 配置Vault路径

安装完成后，需要告诉OpenClaw你的Obsidian Vault位置：

**Windows系统：**

openclaw config set obsidian.vaultPath "C:/Users/你的用户名/Obsidian/MyVault" --json 

**macOS系统：**

openclaw config set obsidian.vaultPath "/Users/你的用户名/Obsidian/MyVault" --json 

**Linux系统：**

openclaw config set obsidian.vaultPath "~/Obsidian/MyVault" --json 

---

## 4. 验证安装状态

检查技能是否安装成功：

openclaw skills list --status ready 

如果显示 obsidian-direct 状态为 ready，表示安装成功。

---

## 5. 开始使用

配置完成后，OpenClaw就可以：

- 搜索你的Obsidian笔记
- 读取、创建和编辑笔记
- 管理标签和Wiki链接
- 自动将AI生成的内容保存到知识库

---

## 注意事项

- 如果遇到权限问题，确保OpenClaw有访问该文件夹的权限
- 路径中避免使用中文和特殊字符
- 首次使用时，OpenClaw可能会要求确认访问权限

如果你已经安装了其他Obsidian技能（如obsidian-sync），启用步骤类似，但可能需要额外的配置，比如安装Obsidian插件和设置同步服务器。
