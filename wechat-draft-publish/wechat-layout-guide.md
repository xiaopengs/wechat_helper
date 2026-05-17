# 微信公众号排版兼容规范

## 核心原则
微信公众号编辑器会大量过滤CSS，排版必须遵循以下规则才能正常显示。

## ❌ 会被过滤/不支持的
- `<style>` 标签和 class 选择器
- 深色背景主题（`background-color: #0a0e17` 等深色）
- CSS3 高级特性：flex、grid、box-shadow、text-shadow、transform、position、opacity、backdrop-filter
- 外部图片URL（必须是 `mmbiz.qpic.cn` 域名）
- JavaScript 和 `<script>` 标签
- `<html><head><body>` 外层标签（只需输出body片段）

## ✅ 支持的样式
- **内联样式**：所有样式必须写在 `style="..."` 里
- **支持的CSS属性**：color, font-size, font-weight, text-align, line-height, margin, padding, border, background-color（浅色）, border-radius, letter-spacing
- **标签**：`<section>`, `<p>`, `<span>`, `<strong>`, `<em>`, `<br>`, `<img>`, `<a>`

## 推荐配色方案

```
品牌主色：#1a73e8（科技蓝）
辅助色：#ff6b35（活力橙，强调/判断用）
正文字色：#333333
次要文字：#666666 / #999999
背景色：白色为主
引用/摘要背景：#f7f8fa
分割线：#1a73e8（4px 品牌色块，不再用细灰线）
段落号：#1a73e8 13px letter-spacing:3px
```

## ⚠️ 花叔排版硬规则（推送前自检）

1. **正文不要标题** — 公众号自带标题，HTML里不从 `<h1>` / 大字标题开始
2. **正文不要作者署名** — 公众号自带作者字段
3. **段落间距统一 18px** — `margin-bottom:18px`，不要用 20px/24px 混搭
4. **插图位用简单一行** — `（插图：描述）`，不要用大框占位
5. **结尾不要互动引导框** — 花叔文章不收"你怎么看"/"欢迎评论"尾巴
6. **参考信息紧凑化** — 一行一个 `·`，小字灰色，不套引用框
7. **分隔线用品牌色块** — `36px×4px #1a73e8`，不用细灰线
8. **分隔处加段落号** — `01`-`06`，13px蓝色字在分隔栏下方
9. **优先色块引用框** — 金句/总结用 `#f7f8fa` 背景+左侧色条，不用纯文字
10. **关键词着色** — 术语/数据用 `#1a73e8`，强调/判断用 `#ff6b35`

## 排版模块模板

### 1. 标题区（⚠️ 花叔推文不要标题区）
```html
<!-- 公众号已有标题，正文直接从内容开始 -->
```

### 2. 小标题
```html
<section style="margin-top:30px;margin-bottom:16px;padding-left:12px;border-left:3px solid #1a73e8;">
  <span style="font-size:18px;font-weight:bold;color:#333333;line-height:1.6;">小标题文字</span>
</section>
```

### 3. 正文段落
```html
<section style="margin-bottom:20px;">
  <span style="font-size:16px;color:#333333;line-height:1.8;">正文内容</span>
</section>
```

### 4. 引用/金句
```html
<section style="margin:20px 0;padding:16px 18px;background-color:#f7f8fa;border-left:3px solid #1a73e8;border-radius:0 6px 6px 0;">
  <span style="font-size:15px;color:#333333;line-height:1.8;font-style:italic;">引用内容</span>
</section>
```

### 5. 强调文字
```html
<strong style="color:#ff6b35;">关键词</strong>
<strong style="color:#1a73e8;">数据/术语</strong>
```

### 6. 图片占位（未上传实图时）
```html
<section style="margin-bottom:18px;">
  <span style="font-size:16px;color:#333333;line-height:1.85;letter-spacing:0.3px;">（插图：描述）</span>
</section>
```

### 6b. 图片 + 图注（实图上传后）
```html
<section style="margin:25px 0;text-align:center;">
  <img src="微信图片URL" style="width:100%;border-radius:6px;"/>
  <p style="font-size:12px;color:#999999;margin-top:8px;text-align:center;">图注说明</p>
</section>
```

### 7. 互动引导框（⚠️ 花叔文章不用这个）
```html
<!-- 花叔文章不设互动引导区，直接收尾 -->
```

### 8. 卡片式链接
```html
<section style="margin-top:30px;padding-top:20px;border-top:1px solid #eeeeee;">
  <span style="font-size:15px;color:#1a73e8;font-weight:bold;">📎 延伸阅读</span>
</section>

<section style="margin-top:12px;padding:14px 16px;background-color:#f7f8fa;border-left:3px solid #1a73e8;border-radius:0 6px 6px 0;margin-bottom:8px;">
  <span style="font-size:14px;color:#333333;line-height:1.6;"><strong style="color:#1a73e8;">链接名称</strong></span><br/>
  <span style="font-size:12px;color:#999999;line-height:1.4;">简短描述</span><br/>
  <span style="font-size:12px;color:#1a73e8;line-height:1.4;">域名简写</span>
</section>
```

### 9. 参考信息（花叔结尾格式）
```html
<section style="margin-bottom:6px;">
  <span style="font-size:13px;color:#999999;line-height:1.8;">· 参考条目一</span>
</section>
<section style="margin-bottom:6px;">
  <span style="font-size:13px;color:#999999;line-height:1.8;">· 参考条目二</span>
</section>
```

### 10. 品牌色块分隔 + 段落号（左右结构）
```html
<section style="text-align:center;margin:24px 0;">
  <span style="display:inline-block;vertical-align:middle;font-size:12px;color:#1a73e8;letter-spacing:2px;margin-right:10px;">01</span>
  <span style="display:inline-block;vertical-align:middle;width:42px;height:3px;background-color:#1a73e8;border-radius:2px;"></span>
</section>
```

### 11. 章节小标题（无编号，编号已放在上方分隔线）
```html
<section style="margin-top:32px;margin-bottom:16px;padding-left:12px;border-left:3px solid #1a73e8;">
  <span style="font-size:18px;font-weight:bold;color:#333333;line-height:1.6;">小标题文字</span>
</section>
```

### 12. 数据卡片
```html
<section style="padding:16px;background-color:#f7f8fa;border-radius:6px;margin:15px 0;text-align:center;">
  <span style="font-size:28px;font-weight:bold;color:#1a73e8;">87%</span><br/>
  <span style="font-size:13px;color:#666666;">WebVoyager成功率</span>
</section>
```

## 重要提醒
1. **图片URL必须先用uploadimg接口上传**，获取 `mmbiz.qpic.cn` 域名URL
2. **中文不要Unicode转义**：API调用时用 `ensure_ascii=False`
3. **HTML只输出body片段**，不带外层标签
4. **微信会去除JS和外部链接**，`<a>` 标签只有微信支付权限的公众号才能用
5. **内容限制**：content < 2万字符、< 1MB
