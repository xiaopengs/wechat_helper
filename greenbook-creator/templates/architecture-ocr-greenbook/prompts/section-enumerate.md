# Stage 1 · 枚举架构图所有视觉区块

> **目标**：不描述内容，只列区块。**这是截断问题的根因解药**——后续按区块逐个提取，每段输出有界。

## 输入
一张架构图 / 流程图（PNG / JPG）。

## 任务
看这张图，列出你能看到的**所有视觉区块**（box / card / section / 显著 group）。**不要描述内容**，只列视觉属性。

## 输出格式（**严格 JSON 数组，无前言/后记**）

```json
[
  {"index": 1, "color_label": "green", "title_text": "BOOTSTRAP", "position": "顶部", "shape": "box"},
  {"index": 2, "color_label": "blue", "title_text": "DIFF PROVIDER", "position": "上部", "shape": "box"},
  {"index": 3, "color_label": "purple", "title_text": "FILTER & RULES", "position": "中部", "shape": "box"},
  {"index": 4, "color_label": "orange", "title_text": "逐文件并发子任务", "position": "中部", "shape": "container"},
  {"index": 5, "color_label": "sub-orange", "title_text": "PLAN (可选)", "position": "4 内左上", "shape": "sub-box", "parent_index": 4},
  {"index": 6, "color_label": "sub-purple", "title_text": "MAIN AGENT", "position": "4 内右上", "shape": "sub-box", "parent_index": 4},
  {"index": 7, "color_label": "purple-light", "title_text": "模型压缩", "position": "4 内底部", "shape": "sub-box", "parent_index": 4}
]
```

## 注意事项

1. **不要写描述性内容**——只列区块的视觉属性（颜色、标题、位置、形状）
2. **识别颜色标签**（小色块底色）：green / blue / purple / orange / red / cyan / gray / black
3. **父子关系**：大区块内的子块单独列，用 `parent_index` 指明归属
4. **数量上限 12 项**——超过说明你过度拆解，把子项合并到父区块的 `details` 里
5. **严格 JSON**——不要 markdown ```json ``` 包裹，不要前言"以下是..."，不要后记"以上是..."
6. **如果图模糊 / 文字看不清**：跳过该字段（如 `title_text: null`），不要瞎猜

## 为什么这样设计

| 旧做法（坏） | 新做法（好） |
|--------------|--------------|
| "Describe this architecture diagram in detail" | "List every visible block as JSON, no prose" |
| 单次长输出，超 token 限制后嘎断在 "≥50 lines" | 每次输出 ≤ 12 项 JSON 对象，token 充足 |
| 不知道丢了什么——截断是静默的 | 校验 `count == expected`，缺了就重跑 |
| 整张图必须重跑才能修 | 只重跑缺失区块 |

## 校验（Stage 3 会做）

- ✅ `count` 与图中可见区块数大致吻合（人工目测，差 1-2 可接受）
- ✅ 每项 `color_label` 是 enum 内
- ✅ 每项 `position` 是粗位置（顶部/中部/底部/...）
- ✅ 父区块在前，子区块在后，且 `parent_index` 引用合法