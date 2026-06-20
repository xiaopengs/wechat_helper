---
name: wechat-weekly-review
description: "微信公众号创作者周报截图复盘与流量诊断。触发：用户发送创作者周报截图(mp.weixin.qq.com 公众号助手发送的图片/JSON)；用户要求做周报复盘/流量诊断/周报对比/跨周趋势。自动提取阅读、分享、推荐占比、净增粉，对比历史周次识别模式(算法冷却、主题簇疲劳、爆款衰减)，归档截图与诊断到 review 目录。"
---

# 周报复盘与流量诊断

截图型复盘 skill。每次拿到一张「创作者周报」，按以下流程处理。

## 触发判定

| 输入 | 行为 |
|---|---|
| 单张周报截图 | 提取数据 + 单周诊断 + 归档 |
| 2+ 周截图（一次/分批） | 跨周对比 + 趋势报告 |
| 用户明确说"对比上周" | 强制走跨周模式 |
| 用户说"复盘上周那篇 X" | 单篇 deep-dive（用 wechat-explosive-analyzer） |

## 工作流（5 步）

### 1. 提取数据 → `data.json`
按 `references/weekly-data-schema.md` 把截图里的数字抽成结构化 JSON。**不放过任何数字**（包括次要来源占比）。

### 2. 选诊断模式
- 单张截图 → 走 `references/diagnostic-patterns.md` 的 condition 索引
- 2+ 张 → 先单周诊断，再走 `references/cross-week-trend.md` 做趋势分析

### 3. 写诊断 → `diagnosis.md`
用 `assets/templates/diagnosis-single.md` 或 `diagnosis-trend.md` 模板。

### 4. 归档（强制）
```
~/.openclaw/workspace/wechat_helper/review/
  index.md                           # 总索引（每条一行）
  weekly/YYYY-MM-DD~MM-DD/           # 周区间目录
    report.jpg                       # 原始截图
    data.json                        # 结构化数据
    diagnosis.md                     # 单周诊断
  trend/YYYY-MM~YYYY-MM-trend.md     # 跨周趋势（2+ 周才生成）
```

**归档脚本**：`scripts/save_weekly_report.py`（自动建目录 + 复制截图 + 初始化 JSON + 写 index）

### 5. 更新 `review/index.md`
每个新周报追加一行（用脚本追加，不手写）。

## 路径约定速查

| 用途 | 路径 |
|---|---|
| 截图原始归档 | `review/weekly/{range}/report.jpg` |
| 结构化数据 | `review/weekly/{range}/data.json` |
| 单周诊断 | `review/weekly/{range}/diagnosis.md` |
| 跨周趋势 | `review/trend/{start}~{end}-trend.md` |
| 总索引 | `review/index.md` |

## 知识加载策略（节省 token）

- **每次**：schema（数据提取）+ patterns（按 condition 取相关条目）
- **跨周时**：额外加载 trend 文档
- **不进 context**：历史 index.md（旧数据要查时用 grep，不用全读）

## 与其它 skill 的关系

| Skill | 何时用 |
|---|---|
| `wechat-account-diagnostic` | 有 AppID+AppSecret 走 API 全账号分析（不是周报截图） |
| `wechat-explosive-analyzer` | 单篇文章爆款审核（不是账号周报） |
| `wechat-weekly-review` (本 skill) | 周报截图复盘 + 跨周对比 |
