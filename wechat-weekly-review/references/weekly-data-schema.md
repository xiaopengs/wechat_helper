# 周报数据 Schema

把截图里的所有数字抽成 JSON。**不要省略**——次要来源占比在跨周对比时是关键信号。

## JSON 结构

```json
{
  "account": "AI知识体系礼记",
  "week_range": "2026-06-08~2026-06-14",
  "week_label": "2026-W23",                   // ISO 周，可选
  "report_source": "创作者周报",
  "extracted_at": "2026-06-20T08:09:40+08:00",
  "raw_image": "report.jpg",
  
  "output": {
    "total_posts": 7,
    "original_articles": 3,
    "image_posts": 1,
    "videos": 0                              // 视频/图文细分，可选
  },
  
  "traffic": {
    "total_views": 241,
    "wow_change_views": null,                // 周环比，原图没给就 null
    
    "source_breakdown": {                    // 必须全填，原图漏的标 "未披露"
      "recommend": { "views": null, "pct": 11.6 },
      "search": { "views": 89, "pct": 36.9 },
      "chat_session": { "views": null, "pct": 29.5 },
      "profile": { "views": null, "pct": null },       // 个人主页/名片
      "subscription_msg": { "views": null, "pct": 11.6 },  // 公众号消息
      "friend_share": { "views": null, "pct": null },
      "other": { "views": null, "pct": 14.1 }
    }
  },
  
  "top_articles": [
    {
      "rank": 1,
      "title": "Fable 5 三日封杀: AI史上最狠的一次政府叫停",
      "search_views": 46,
      "total_views": null,                    // 截图只给了搜索量就标 null
      "shares": 14,
      "shares_source": "搜索来源"               // 哪个数据来源的标题
    }
    // 至少前 3 篇；截图给多少写多少
  ],
  
  "shares": {
    "total": 27,
    "top_article_shares": 14
  },
  
  "followers": {
    "total": 345,
    "net_change": 4,
    "wow_change_pct": null,
    "top_interests": ["科技", "财经", "职场", "科学", "房产"]
  },
  
  "comments": {
    "reserved_count": null,                    // 预留/置顶评论数
    "hot_topics": []                          // 热评话题
  },
  
  "notes": "用户描述的额外信息，例：Fable 5 为 AI 圈热点"
}
```

## 提取 SOP

1. **先通读截图全文**（用 vision 一次性看完整图，不要一段段问）
2. **数字优先**：所有数字（阅读、占比、分享、净增粉）必须抓
3. **占比 vs 绝对值**：必须两个都记—— 占比看趋势，绝对值看绝对增长
4. **次要来源不能丢**：聊天会话、好友转发、主页这些"非主流量"在跨周对比时能看出推荐机制变化
5. **无法确定的字段**：`null` + 在 `notes` 里说明原因
6. **日期格式**：`week_range` 用 `YYYY-MM-DD~YYYY-MM-DD`，文件夹名也用这个

## 提取后的自检

- [ ] 所有占比加起来 ≈ 100%（容差 ±2%）
- [ ] 至少 1 篇 top_article 有完整数据
- [ ] followers.net_change 与上周对比可解释（涨/跌/平）
- [ ] 截图里任何百分比都已转成数字（不要保留 "36.9%" 字符串）

## 常见陷阱

| 陷阱 | 处理 |
|---|---|
| 截图模糊，数字看不清 | 在 `notes` 标"模糊"，相关字段填 null |
| 多个来源同占比（如 36.9% 和 36% 一起出现） | 取较精确那个，notes 标另一个 |
| "搜索来源 N" 出现在多个字段 | 区分清楚：是 search 来源的 views，还是某篇的 search_views |
| 净增粉显示为 ↑N 但数字未给出 | `net_change: N`，`wow_change_pct: null` |
