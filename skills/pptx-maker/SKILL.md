# pptx-maker - AI PPT 生成器

> 使用 python-pptx 创建和编辑 PowerPoint 演示文稿，支持模板功能

## 功能

- 📄 创建新 PPT（空白或基于模板）
- 📝 添加幻灯片（多种布局）
- 🖼️ 添加图片
- 📊 添加表格
- 📈 添加图表
- 💾 保存为 .pptx 文件

## 安装依赖

```bash
pip install python-pptx pillow
```

## 使用方法

### 1. 创建空白演示文稿

```python
from pptx import Presentation

prs = Presentation()
prs.save('blank.pptx')
```

### 2. 使用模板创建

```python
from pptx import Presentation

# 使用现有模板
prs = Presentation('template.pptx')
slide = prs.slides.add_slide(prs.slide_layouts[1])
prs.save('output.pptx')
```

### 3. 添加标题幻灯片

```python
from pptx import Presentation

prs = Presentation()
slide = prs.slides.add_slide(prs.slide_layouts[0])
title = slide.shapes.title
subtitle = slide.placeholders[1]
title.text = "主标题"
subtitle.text = "副标题"
prs.save('title_slide.pptx')
```

### 4. 添加图片

```python
from pptx import Presentation
from pptx.util import Inches

prs = Presentation()
slide = prs.slides.add_slide(prs.slide_layouts[5])  # 空白布局
img_path = 'photo.jpg'
slide.shapes.add_picture(img_path, Inches(1), Inches(1), width=Inches(4))
prs.save('with_image.pptx')
```

### 5. 添加表格

```python
from pptx import Presentation
from pptx.util import Inches, Pt

prs = Presentation()
slide = prs.slides.add_slide(prs.slide_layouts[5])
rows, cols = 3, 3
left, top, width, height = Inches(2), Inches(2), Inches(6), Inches(1.5)
table = slide.shapes.add_table(rows, cols, left, top, width, height).table

# 设置单元格内容
table.cell(0, 0).text = "姓名"
table.cell(0, 1).text = "年龄"
table.cell(0, 2).text = "城市"
prs.save('with_table.pptx')
```

### 6. 添加图表

```python
from pptx import Presentation
from pptx.chart.data import CategoryChartData
from pptx.enum.chart import XL_CHART_TYPE
from pptx.util import Inches

prs = Presentation()
slide = prs.slides.add_slide(prs.slide_layouts[5])

chart_data = CategoryChartData()
chart_data.categories = ['第一季度', '第二季度', '第三季度', '第四季度']
chart_data.add_series('销售额', (100, 150, 130, 180))

x, y, cx, cy = Inches(1), Inches(2), Inches(8), Inches(4.5)
chart = slide.shapes.add_chart(
    XL_CHART_TYPE.COLUMN_CLUSTERED, x, y, cx, cy, chart_data
).chart

prs.save('with_chart.pptx')
```

## 幻灯片布局

| 索引 | 布局名称 |
|------|----------|
| 0 | 标题幻灯片 |
| 1 | 标题和内容 |
| 2 | 标题居中 |
| 3 | 标题和两栏内容 |
| 4 | 标题和内容（带图片） |
| 5 | 空白 |
| 6 | 内容（带图片和标题） |
| 7 | 图片和标题 |
| 8 | 标题和图片 |
| 9 | 标题和图片（两张） |

## 布局索引参考

```
prs.slide_layouts[0]  # 标题页
prs.slide_layouts[1]  # 标题 + 正文
prs.slide_layouts[5]  # 空白页（最灵活）
```

## 输出路径

默认保存到当前目录，也可指定绝对路径：

```python
prs.save('/root/data/disk/workspace/output.pptx')
```
