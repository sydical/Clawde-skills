---
name: ingredient-recognition
description: 食材图像识别与对比工具。使用 SIFT/ORB 算法对比食材照片与素材库，识别食材名称。如果素材库中没有该食材，会要求用户输入食材名称并保存到素材库。触发场景：(1) 用户上传食材照片进行识别 (2) 需要对比食材库 (3) 添加新食材到素材库
---

# 食材识别 Skill

## 功能概述

1. **食材识别** - 上传照片，对比食材库，识别食材名称
2. **素材库管理** - 自动保存新食材到素材库
3. **相似度匹配** - 使用 ORB 算法进行图像特征匹配

## 工作流程

### Step 1: 接收用户上传的图片

用户会发送图片，使用 read 工具读取图片内容。

### Step 2: 调用识别脚本

运行识别脚本：
```bash
python3 ~/.openclaw/skills/ingredient-recognition/scripts/recognize.py --query <图片路径>
```

### Step 3: 处理识别结果

- **如果识别成功**：告诉用户识别的食材名称
- **如果识别失败（相似度低）**：告诉用户"未找到相似食材"，询问用户食材名称

### Step 4: 添加新食材（如果用户提供了名称）

运行添加脚本：
```bash
python3 ~/.openclaw/skills/ingredient-recognition/scripts/recognize.py --add <食材名称> <图片路径>
```

## 素材库位置

```
~/.openclaw/skills/ingredient-recognition/ingredients/
```

## 注意事项

- 首次使用需要先添加一些食材到素材库
- 识别结果取决于素材库的图片质量
- 支持 jpg/png 格式
