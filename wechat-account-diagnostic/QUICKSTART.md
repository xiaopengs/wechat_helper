# 快速使用指南

## 🚀 30秒开始使用

### 方式1：有API权限（认证服务号/企业号）

```bash
# 1. 进入目录
cd wechat-account-diagnostic

# 2. 设置环境变量（或用命令行参数）
export WECHAT_APPID="你的AppID"
export WECHAT_APPSECRET="你的AppSecret"

# 3. 一键生成诊断报告
python scripts/account_analyzer.py full --output 我的公众号诊断报告.md
```

### 方式2：没有API权限（个人订阅号）

手动创建数据文件 `my_data.json`：

```json
{
  "fetch_time": "2024-06-05T00:00:00",
  "date_range": {
    "begin": "2024-05-05",
    "end": "2024-06-05"
  },
  "articles": [
    {
      "title": "文章标题1",
      "author": "作者名",
      "digest": "文章摘要",
      "publish_date": "2024-06-01"
    },
    {
      "title": "文章标题2",
      "author": "作者名",
      "digest": "文章摘要",
      "publish_date": "2024-05-28"
    }
    // ... 添加更多文章
  ],
  "article_stats": [
    {
      "ref_date": "2024-06-01",
      "title": "文章标题1",
      "int_page_read_count": 1500,
      "share_count": 80
    }
    // ... 添加更多统计
  ],
  "user_stats": []
}
```

然后运行：

```bash
python scripts/account_analyzer.py analyze \
  --data-file my_data.json \
  --output 诊断报告.md
```

---

## 📋 报告示例（节选）

```markdown
# 公众号账号诊断报告

> 生成时间：2024-06-05 00:00:00
> 数据范围：2024-05-05 ~ 2024-06-05

---

## 一、账号画像总评

### 综合评分：72.5/100

| 维度 | 得分/25 | 评估 |
|------|---------|------|
| 更新规律性 | 21.0 | 优秀 |
| 标题风格统一性 | 18.5 | 良好 |
| 主题集中度 | 17.5 | 比较聚焦 |
| 人味指数 | 15.5 | AI痕迹较重 |

---

## 二、基础数据指标

| 指标 | 数值 | 说明 |
|------|------|------|
| 分析文章数 | 12 篇 |  |
| 平均阅读量 | 1250.5 |  |
| 中位数阅读 | 1180 | 比平均值更能反映真实水平 |
| 分享率 | 2.8% | 行业基准 2-3% ✅ |
| 发布频率 | 0.4 篇/天 | 约 2.8 篇/周 |

---

## 五、后续行动清单

1. **本周**：分析3篇阅读最高和3篇阅读最低的文章，找出共性差异
2. **本月**：做2-3次标题A/B测试，验证不同风格的点击率
3. **长期**：建立「文章表现数据库」，每篇发布后24小时记录核心数据
```

---

## 🔧 常见问题排查

### 问题1：提示 "获取Token失败"

**可能原因**：
- AppID 或 AppSecret 错误
- IP 不在白名单里（微信后台 → 开发 → 基本配置 → IP白名单）
- 账号类型不对（个人订阅号无权限）

**解决方法**：
1. 登录微信公众平台 → 开发 → 基本配置
2. 确认 AppID 和 AppSecret 正确
3. 把运行脚本的服务器IP加入白名单

---

### 问题2：提示 "errcode: 48001, api unauthorized"

**原因**：当前公众号类型没有该API权限

**检查账号权限**：
微信公众平台 → 开发 → 接口权限 → 看看"数据统计"权限有没有开启

---

### 问题3：拉不到文章数据

**原因**：
- 文章是草稿，没有添加到永久素材
- 只拉到了最近N篇，需要调整 `count` 参数

---

## 📚 相关文档

- [微信公众平台技术文档](https://developers.weixin.qq.com/doc/offiaccount/Getting_Started/Overview.html)
- [数据统计接口说明](https://developers.weixin.qq.com/doc/offiaccount/Analytics/Analytics_API.html)
- [素材管理接口说明](https://developers.weixin.qq.com/doc/offiaccount/Asset_Management/Adding_Permanent_Assets.html)

---

## 💡 使用建议

1. **每周运行一次**：建立数据趋势，观察优化效果
2. **每次大改后运行**：换标题风格、调整主题后，对比数据变化
3. **保存历史报告**：建立 `reports/` 目录，存档每次的诊断结果
4. **配合A/B测试**：不要一次改太多变量，逐个验证优化效果

---

*有问题？提 Issue 或者直接改代码！PR Welcome！* 🎉
