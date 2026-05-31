# AI 技术科普海报风格参考（公众号轮播图 / 小绿书）

> **核心公式**：70% 信息设计 + 20% 排版 + 10% 插画
> 
> 本质是 **信息图**，不是插画集。插画是调味料，信息架构才是主菜。

## 风格融合来源

- **Apple** 风格留白
- **Notion / Linear** 风格信息架构
- **Stripe** 风格渐变蓝紫色系
- **飞书 / 腾讯云** 风格卡片布局
- **Midjourney** 常见 3D Clay + Glassmorphism 插画

---

## 一、配色体系

### 主色
```
Primary Blue:  #4F6BFF
Primary Purple: #7A4DFF
Primary Gradient: #4F6BFF → #8B5CFF
```

### 辅助色
```
浅灰背景: #F8F9FC
边框:     #E8EBF5
正文:     #222222
次级文字: #666666
```

### 功能色
```
成功: #3CCF91
警告: #FFB84D
错误: #FF6B6B
```

---

## 二、字体层级

```
48-72px  主标题（HarmonyOS Sans SC Heavy / OPPOSans Heavy / MiSans Heavy）
20-24px  副标题（Medium）
16-18px  正文（Regular）
14px     注释/脚注
```

---

## 三、插画风格关键词

```
3D Isometric（等距 3D）
Soft Shadow（柔和投影）
Floating（悬浮感）
Clay Render（黏土渲染）
Blue Purple Gradient（蓝紫渐变）
White Base（白色基底）
Minimal Detail（极简细节）
```

---

## 四、版式模板

### 封面（第一屏）
```
┌──────────────────────┐
│ [主标题]             │
│                      │
│     [核心概念]       │
│                      │
│ [价值主张副标题]     │
│                      │
│ [价值点卡片列表]     │  ← 左侧 60%
│                      │
│        [3D 插画]     │  ← 右侧 40%
└──────────────────────┘
```

### 概念解释（第二屏）
```
标题区 20%：大标题 + 一句定义
对比区 60%：左右对比（传统 vs 新范式）
总结区 20%：一句话总结
```

### 痛点解决（第三屏+）
```
左侧：痛点/问题（红色调标注）
右侧：方案/解法（绿色调标注）
底部：关键数据支撑
```

---

## 五、通用 AI 生图 Prompt

### 通用底版模板（只换主题即可复用）
```
Modern AI technology infographic,
Chinese tech education poster,
white minimalist background,
blue-purple gradient palette (#4F6BFF → #8B5CFF),
large bold Chinese headline,
3D isometric illustration,
glassmorphism UI cards,
multiple content blocks,
comparison section,
workflow diagram,
feature cards,
clean spacing,
high readability,
Apple keynote style,
Linear design language,
Stripe inspired gradients,
premium SaaS marketing design,
vector icons,
soft ambient shadow,
corporate presentation quality,
8k ultra detailed
```

### 封面专用 Prompt
```
[填入主题标题]

AI development paradigm poster,
large title "[填入英文缩写/核心概念]",
subtitle: "[填入中文副标题]",

left side text content cards,
right side 3D illustration,
[填入插画元素描述],

clean white background,
blue-purple gradient lighting,
Apple keynote style,
modern SaaS infographic,
glassmorphism,
soft shadow,
professional Chinese tech poster,
high-end startup branding,
Linear + Stripe + Notion aesthetic,
extremely detailed,
8k
```

### OpenClaw / Agent 架构专用 Prompt
```
OpenClaw Architecture Infographic,
AI Operating System Concept,
white background,
blue-purple futuristic gradient,
central AI Agent orchestration layer,
multiple connected nodes:
  Android Device,
  Browser Agent,
  Local LLM,
  Cloud LLM,
  Tool Gateway,
  Workflow Engine,
  Spec Driven Development,
glassmorphism architecture cards,
clean arrows and data flow,
Apple keynote style,
Linear style diagrams,
high-end enterprise SaaS visual design,
minimalist tech presentation,
Chinese labels,
professional architecture poster,
3D isometric illustration,
extremely detailed,
8k quality
```

---

## 六、适用场景

这套风格最适合：
- AI / SaaS / 开发者工具 赛道
- 技术科普类公众号轮播图
- 产品发布 / 功能更新海报
- 架构图 / 对比评测 信息图
- 技术方法论介绍

不适合：
- 生活/美食/穿搭类（换暖橘/森林绿色系）
- 纯情感/人文类（换薰衣草/极简黑白）
