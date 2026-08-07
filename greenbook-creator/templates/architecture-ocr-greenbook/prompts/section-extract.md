# Stage 2 · 单区块结构化提取

> **目标**：每个区块独立调用，每段输出有界 100-300 tokens，**永远不会被截断**。

## 输入
一张架构图 + Stage 1 输出的第 N 个区块元数据：
- `index`: 区块编号（从 1 开始）
- `title_text`: 区块标题（如 "BOOTSTRAP" / "MAIN AGENT"）
- `color_label`: 颜色（green / blue / purple / orange / red / cyan / gray）
- `position`: 位置（顶部 / 4 内左上 / ...）
- `parent_index`: 父区块（null 表示顶层）

## 任务
**只针对这个区块**（不要描述其他区块），提取以下字段：

```json
{
  "title_en": "BOOTSTRAP",
  "title_zh": "装配运行环境",
  "bullets": [
    "解析模型端点",
    "加载模板和工具注册表",
    "应用系统规则"
  ],
  "details": "启动时一次性完成，无运行时副作用",
  "sub_blocks": [
    {"label": "templates", "desc": "提示词模板"},
    {"label": "tools", "desc": "工具注册表"}
  ]
}
```

## 字段语义

| 字段 | 类型 | 长度 | 说明 |
|------|------|------|------|
| `title_en` | str | - | 英文/标识（如有，原样保留） |
| `title_zh` | str | 4-12 字 | 中文一句话描述（图中如有副标） |
| `bullets` | list[str] | 3-5 条，每条 5-20 字 | 具体动作 / 可观察产物 |
| `details` | str | 10-30 字 | 1 句话总结（关键约束 / 适用范围） |
| `sub_blocks` | list[{label, desc}] | 0-6 个 | 区块内的子元素（标签+一句话） |

## 注意事项

1. **`bullets` 必须是「具体动作」或「可观察的产物」**——不要写"负责" / "用于" / "处理"之类空话
2. **数量限制**：bullets 3-5 条，sub_blocks 0-6 个——**超出会被 Stage 3 拒绝重跑**
3. **空字段也要输出**（如 `sub_blocks: []`）——便于 Stage 3 校验是否真为空
4. **子块可选**：如果图中此区块没有明显子元素，`sub_blocks: []`
5. **严格 JSON**——不要 markdown ```json ``` 包裹，不要前言/后记

## 为什么这样设计

- 每段独立调用 → 任何一段失败可以**单独重试**，不用重跑整张图
- 输出 token 上限 300 → 任意 8 段总和 ≤ 2400 tokens，远低于模型输出限制
- 字段严格 enum + 长度限制 → Stage 3 可以**机器校验**（脚本判断）
- 失败可观测（"section 4 的 bullets 只有 2 条，重跑"）vs 旧做法的**静默截断**

## Stage 3 校验脚本会做的

```python
for sec in sections:
    assert 3 <= len(sec.bullets) <= 5, f"section {sec.index} bullets={len(sec.bullets)}"
    assert 10 <= len(sec.details) <= 30, f"section {sec.index} details={len(sec.details)}字"
    assert sec.title_zh and 4 <= len(sec.title_zh) <= 12
    assert sec.sub_blocks is not None
```

校验失败 → 只重跑这一个 section（其他 section 保留结果）。