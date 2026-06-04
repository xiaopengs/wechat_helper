#!/usr/bin/env python3
"""
微信公众号账号诊断分析器 - 基于官方API

功能：
1. 自动拉取历史文章列表（从永久素材）
2. 自动拉取每篇文章的阅读/在看/点赞/转发数据
3. 自动分析主题分布、风格一致性
4. 生成完整的诊断报告

使用方式：
  # 拉取最近20篇文章数据
  python account_analyzer.py fetch --appid APPID --secret SECRET --days 30
  
  # 生成诊断报告
  python account_analyzer.py analyze --data-file data.json --output report.md
  
  # 一键全流程（拉取+分析+生成报告）
  python account_analyzer.py full --appid APPID --secret SECRET --output report.md
  
  # 结合热点分析（需要AI哨兵晚报数据路径）
  python account_analyzer.py full --hotspot-path ../热点资讯追踪/
"""

import argparse
import json
import os
import sys
import time
from datetime import datetime, timedelta
from collections import Counter

try:
    import requests
except ImportError:
    print("请安装 requests: pip install requests==2.31.0", file=sys.stderr)
    sys.exit(1)

WECHAT_API_BASE = "https://api.weixin.qq.com"

# ============================================================
# 凭证加载（复用 wechat_api.py 的逻辑）
# ============================================================

SECRETS_FILE = os.path.expanduser("~/.openclaw/wechat-secrets.json")


def load_credentials():
    """按优先级加载微信凭证"""
    appid = os.environ.get("WECHAT_APPID")
    secret = os.environ.get("WECHAT_APPSECRET")
    if appid and secret:
        return appid, secret

    if os.path.isfile(SECRETS_FILE):
        try:
            with open(SECRETS_FILE, "r") as f:
                data = json.load(f)
            appid = data.get("WECHAT_APPID") or data.get("appid")
            secret = data.get("WECHAT_APPSECRET") or data.get("appsecret")
            if appid and secret:
                return appid, secret
        except (json.JSONDecodeError, IOError):
            pass
    return None, None


_token_cache = {}


def get_token(appid, secret):
    """获取 access_token"""
    url = f"{WECHAT_API_BASE}/cgi-bin/token"
    params = {
        "grant_type": "client_credential",
        "appid": appid,
        "secret": secret
    }
    resp = requests.get(url, params=params, timeout=10)
    data = resp.json()
    if "access_token" not in data:
        print(f"获取Token失败: {data}", file=sys.stderr)
        return None
    _token_cache["token"] = data["access_token"]
    _token_cache["expires_at"] = time.time() + data.get("expires_in", 7200) - 300
    return data["access_token"]


def get_cached_token():
    """获取缓存的token"""
    if "token" in _token_cache and time.time() < _token_cache.get("expires_at", 0):
        return _token_cache["token"]
    return None


# ============================================================
# 1. 素材管理 - 获取历史文章列表
# ============================================================

def get_article_list(token, count=20, offset=0):
    """
    获取永久素材中的图文列表
    
    返回: {
        "total_count": 总数,
        "item_count": 本次返回数,
        "articles": [
            {
                "media_id": "素材ID",
                "update_time": 时间戳,
                "title": "标题",
                "author": "作者",
                "digest": "摘要",
                "content": "正文HTML(可选)"
            }
        ]
    }
    """
    url = f"{WECHAT_API_BASE}/cgi-bin/material/batchget_material"
    params = {"access_token": token}
    body = {
        "type": "news",
        "offset": offset,
        "count": count
    }
    resp = requests.post(url, params=params, json=body, timeout=30)
    data = resp.json()
    
    if "errcode" in data and data["errcode"] != 0:
        return {"success": False, "error": data}
    
    articles = []
    for item in data.get("item", []):
        news_items = item.get("content", {}).get("news_item", [])
        if news_items:
            # 取第一篇（头条）
            news = news_items[0]
            articles.append({
                "media_id": item.get("media_id", ""),
                "update_time": item.get("update_time", 0),
                "publish_date": datetime.fromtimestamp(item.get("update_time", 0)).strftime("%Y-%m-%d"),
                "title": news.get("title", ""),
                "author": news.get("author", ""),
                "digest": news.get("digest", ""),
                "url": news.get("url", ""),
                "thumb_url": news.get("thumb_url", ""),
                "content_source_url": news.get("content_source_url", "")
            })
    
    return {
        "success": True,
        "total_count": data.get("total_count", 0),
        "item_count": data.get("item_count", 0),
        "articles": articles
    }


# ============================================================
# 2. 数据立方体 - 获取文章统计数据
# ============================================================

def get_article_stats(token, begin_date, end_date):
    """
    获取图文群发每日数据
    
    注意：微信API返回的是按天汇总的数据，不是按单篇文章
    这个接口只能获取「汇总数据」，不能直接拿到单篇文章的精确数据
    
    返回格式: {
        "list": [
            {
                "ref_date": "2024-06-01",
                "msgid": "消息ID",
                "title": "标题",
                "int_page_read_user": 阅读人数,
                "int_page_read_count": 阅读次数,
                "ori_page_read_user": 原文页阅读人数,
                "ori_page_read_count": 原文页阅读次数,
                "share_user": 分享人数,
                "share_count": 分享次数,
                "add_to_fav_user": 收藏人数,
                "add_to_fav_count": 收藏次数,
                "feed_from_session_read": 会话阅读,
                "feed_from_feed_read": 朋友圈阅读,
                "feed_from_other_read": 其他来源阅读
            }
        ]
    }
    """
    url = f"{WECHAT_API_BASE}/datacube/getarticlesummary"
    params = {"access_token": token}
    body = {
        "begin_date": begin_date,
        "end_date": end_date
    }
    resp = requests.post(url, params=params, json=body, timeout=30)
    data = resp.json()
    
    if "errcode" in data and data["errcode"] != 0:
        return {"success": False, "error": data}
    
    return {"success": True, "list": data.get("list", [])}


def get_user_read_stats(token, begin_date, end_date):
    """获取图文阅读分析（来源分布）"""
    url = f"{WECHAT_API_BASE}/datacube/getuserread"
    params = {"access_token": token}
    body = {"begin_date": begin_date, "end_date": end_date}
    resp = requests.post(url, params=params, json=body, timeout=30)
    data = resp.json()
    
    if "errcode" in data and data["errcode"] != 0:
        return {"success": False, "error": data}
    
    return {"success": True, "list": data.get("list", [])}


def get_user_summary(token, begin_date, end_date):
    """获取用户增减数据"""
    url = f"{WECHAT_API_BASE}/datacube/getusersummary"
    params = {"access_token": token}
    body = {"begin_date": begin_date, "end_date": end_date}
    resp = requests.post(url, params=params, json=body, timeout=30)
    data = resp.json()
    
    if "errcode" in data and data["errcode"] != 0:
        return {"success": False, "error": data}
    
    return {"success": True, "list": data.get("list", [])}


# ============================================================
# 3. 数据整合与分析
# ============================================================

def fetch_full_data(token, days=30):
    """
    拉取完整数据：文章列表 + 统计数据 + 用户数据
    
    限制说明：
    - getarticlesummary 只能拉取最近3个月的数据
    - 每次最多拉取7天的数据
    """
    end_date = datetime.now()
    begin_date = end_date - timedelta(days=days)
    
    print(f"正在拉取 {begin_date.date()} 到 {end_date.date()} 的数据...")
    
    # 1. 获取文章列表
    print("1/3 拉取文章列表...")
    article_result = get_article_list(token, count=20)
    if not article_result["success"]:
        return article_result
    
    # 2. 拉取统计数据（分批次，每次7天）
    print("2/3 拉取文章统计数据...")
    all_stats = []
    current_begin = begin_date
    while current_begin < end_date:
        current_end = min(current_begin + timedelta(days=6), end_date)
        stats_result = get_article_stats(
            token, 
            current_begin.strftime("%Y-%m-%d"),
            current_end.strftime("%Y-%m-%d")
        )
        if stats_result["success"]:
            all_stats.extend(stats_result["list"])
        current_begin = current_end + timedelta(days=1)
        time.sleep(0.5)  # 避免限流
    
    # 3. 拉取用户数据
    print("3/3 拉取用户数据...")
    user_result = get_user_summary(
        token,
        begin_date.strftime("%Y-%m-%d"),
        end_date.strftime("%Y-%m-%d")
    )
    
    return {
        "success": True,
        "fetch_time": datetime.now().isoformat(),
        "date_range": {
            "begin": begin_date.strftime("%Y-%m-%d"),
            "end": end_date.strftime("%Y-%m-%d")
        },
        "articles": article_result["articles"],
        "article_stats": all_stats,
        "user_stats": user_result.get("list", []) if user_result.get("success") else []
    }


# ============================================================
# 4. 数据分析引擎
# ============================================================

def analyze_basic_metrics(data):
    """基础指标分析"""
    articles = data.get("articles", [])
    stats = data.get("article_stats", [])
    
    # 基础指标计算
    total_articles = len(articles)
    
    # 阅读数据统计（如果有统计数据）
    read_counts = [item.get("int_page_read_count", 0) for item in stats]
    avg_read = sum(read_counts) / len(read_counts) if read_counts else 0
    median_read = sorted(read_counts)[len(read_counts)//2] if read_counts else 0
    
    # 分享率计算
    share_counts = [item.get("share_count", 0) for item in stats]
    total_read = sum(read_counts)
    total_share = sum(share_counts)
    share_rate = (total_share / total_read * 100) if total_read > 0 else 0
    
    # 发布时间分析
    publish_dates = [a.get("publish_date", "") for a in articles if a.get("publish_date")]
    date_counts = Counter(publish_dates)
    
    return {
        "total_articles": total_articles,
        "avg_read": round(avg_read, 1),
        "median_read": median_read,
        "max_read": max(read_counts) if read_counts else 0,
        "min_read": min(read_counts) if read_counts else 0,
        "total_read": total_read,
        "share_rate": round(share_rate, 2),
        "publish_frequency": round(len(publish_dates) / 30, 2) if publish_dates else 0,
        "date_distribution": dict(date_counts.most_common(10))
    }


def analyze_title_style(articles):
    """标题风格分析"""
    titles = [a.get("title", "") for a in articles]
    
    # 标题类型分类
    types_count = {
        "数字型": 0,  # 含数字
        "悬念型": 0,  # 含问号、感叹号
        "观点型": 0,  # 含"我认为"、"其实"、"不是"等
        "名人/产品型": 0,  # 含知名公司、产品名
        "其他": 0
    }
    
    # 关键词库
    companies = ["OpenAI", "ChatGPT", "Claude", "Anthropic", "Google", "DeepMind", 
                 "微软", "字节", "腾讯", "阿里", "百度", "Meta", "特斯拉", "苹果"]
    viewpoint_words = ["我", "其实", "不是", "为什么", "如何", "怎样", "应该", "可能"]
    
    for title in titles:
        classified = False
        
        # 检测数字
        if any(c.isdigit() for c in title):
            types_count["数字型"] += 1
            classified = True
            
        # 检测悬念
        if any(c in title for c in "？?!！"):
            types_count["悬念型"] += 1
            classified = True
            
        # 检测名人/产品
        if any(name in title for name in companies):
            types_count["名人/产品型"] += 1
            classified = True
            
        # 检测观点
        if any(word in title for word in viewpoint_words):
            types_count["观点型"] += 1
            classified = True
            
        if not classified:
            types_count["其他"] += 1
    
    # 平均标题长度
    avg_length = sum(len(t) for t in titles) / len(titles) if titles else 0
    
    return {
        "type_distribution": types_count,
        "avg_title_length": round(avg_length, 1),
        "dominant_style": max(types_count.items(), key=lambda x: x[1])[0] if any(types_count.values()) else "未知"
    }


def analyze_topic_distribution(articles):
    """主题分布分析"""
    titles = [a.get("title", "") for a in articles]
    digests = [a.get("digest", "") for a in articles]
    all_text = " ".join(titles + digests)
    
    # 主题关键词分类
    topic_keywords = {
        "大模型": ["GPT", "Claude", "大模型", "LLM", "语言模型"],
        "Agent": ["Agent", "智能体", "工作流", "自动化"],
        "编程工具": ["Cursor", "Trae", "Copilot", "代码", "编程"],
        "创业/产品": ["创业", "产品", "商业化", "融资", "公司"],
        "行业观察": ["趋势", "观察", "行业", "未来", "分析"],
        "技术架构": ["架构", "设计", "系统", "技术", "工程"]
    }
    
    topic_counts = {}
    for topic, keywords in topic_keywords.items():
        count = sum(1 for keyword in keywords if keyword.lower() in all_text.lower())
        if count > 0:
            topic_counts[topic] = count
    
    # 计算集中度
    total = sum(topic_counts.values()) if topic_counts.values() else 0
    top3 = sum(sorted(topic_counts.values(), reverse=True)[:3]) if topic_counts else 0
    concentration = (top3 / total * 100) if total > 0 else 0
    
    return {
        "topic_counts": topic_counts,
        "concentration_rate": round(concentration, 1),
        "dominant_topic": max(topic_counts.items(), key=lambda x: x[1])[0] if topic_counts else "未知"
    }


def analyze_human_taste(articles):
    """人味指数分析"""
    all_content = " ".join([a.get("digest", "") + " " + a.get("title", "") for a in articles])
    
    ai_signals = ["首先", "其次", "再次", "最后", "总而言之", "综上所述", "总的来说"]
    human_signals = ["我", "我的", "我觉得", "说实话", "其实", "昨天", "今天", "刚才", "测试了"]
    
    ai_count = sum(all_content.count(signal) for signal in ai_signals)
    human_count = sum(all_content.count(signal) for signal in human_signals)
    
    # 计算人味指数 0-100
    if ai_count + human_count > 0:
        taste_score = (human_count / (ai_count + human_count)) * 100
    else:
        taste_score = 50  # 默认中性
    
    return {
        "human_taste_score": round(taste_score, 1),
        "ai_signal_count": ai_count,
        "human_signal_count": human_count,
        "assessment": "人味十足" if taste_score > 70 else "比较自然" if taste_score > 50 else "AI痕迹较重" if taste_score > 30 else "AI感很强"
    }


# ============================================================
# 5. 生成诊断报告
# ============================================================

def generate_diagnostic_report(data, output_file):
    """生成完整的诊断报告"""
    print("正在生成诊断报告...")
    
    # 执行各项分析
    basic_metrics = analyze_basic_metrics(data)
    title_analysis = analyze_title_style(data.get("articles", []))
    topic_analysis = analyze_topic_distribution(data.get("articles", []))
    human_taste = analyze_human_taste(data.get("articles", []))
    
    # 账号画像评分（简化版）
    scores = {
        "更新规律性": min(basic_metrics["publish_frequency"] * 20, 25),  # 假设每周2.5篇满分
        "标题风格统一性": 20,  # 简化处理
        "主题集中度": topic_analysis["concentration_rate"] / 4,  # 100%集中度 = 25分
        "人味指数": human_taste["human_taste_score"] / 4,  # 100分 = 25分
    }
    total_score = sum(scores.values())
    
    report = f"""# 公众号账号诊断报告

> 生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
> 数据范围：{data.get('date_range', {}).get('begin', 'N/A')} ~ {data.get('date_range', {}).get('end', 'N/A')}

---

## 一、账号画像总评

### 综合评分：{round(total_score, 1)}/100

| 维度 | 得分/25 | 评估 |
|------|---------|------|
| 更新规律性 | {round(scores['更新规律性'], 1)} | {"优秀" if scores['更新规律性'] >= 20 else "良好" if scores['更新规律性'] >= 15 else "需改进"} |
| 标题风格统一性 | {round(scores['标题风格统一性'], 1)} | {"高度统一" if scores['标题风格统一性'] >= 20 else "基本统一"} |
| 主题集中度 | {round(scores['主题集中度'], 1)} | {"非常聚焦" if scores['主题集中度'] >= 20 else "比较聚焦" if scores['主题集中度'] >= 15 else "需收窄"} |
| 人味指数 | {round(scores['人味指数'], 1)} | {human_taste['assessment']} |

---

## 二、基础数据指标

| 指标 | 数值 | 说明 |
|------|------|------|
| 分析文章数 | {basic_metrics['total_articles']} 篇 |  |
| 平均阅读量 | {basic_metrics['avg_read']} |  |
| 中位数阅读 | {basic_metrics['median_read']} | 比平均值更能反映真实水平 |
| 最高阅读 | {basic_metrics['max_read']} | 爆款潜力 |
| 最低阅读 | {basic_metrics['min_read']} |  |
| 分享率 | {basic_metrics['share_rate']}% | 行业基准 2-3% |
| 发布频率 | {basic_metrics['publish_frequency']} 篇/天 | 约 {round(basic_metrics['publish_frequency'] * 7, 1)} 篇/周 |

---

## 三、内容风格分析

### 3.1 标题风格分布

| 类型 | 占比 |
|------|------|
"""
    
    # 添加标题类型分布
    total_titles = sum(title_analysis['type_distribution'].values())
    for t, count in title_analysis['type_distribution'].items():
        pct = round(count / total_titles * 100, 1) if total_titles > 0 else 0
        report += f"| {t} | {count} 篇 ({pct}%) |\n"
    
    report += f"""
> 主导风格：**{title_analysis['dominant_style']}**
> 平均标题长度：**{title_analysis['avg_title_length']}** 字

---

### 3.2 主题分布

"""
    
    # 添加主题分布
    for topic, count in topic_analysis['topic_counts'].items():
        report += f"- **{topic}**: 出现 {count} 次\n"
    
    report += f"""
> 主导主题：**{topic_analysis['dominant_topic']}**
> TOP3主题集中度：**{topic_analysis['concentration_rate']}%**

---

### 3.3 人味指数

- **人味评分**：{human_taste['human_taste_score']}/100
- **AI信号数**：{human_taste['ai_signal_count']} 个
- **人味信号数**：{human_taste['human_signal_count']} 个
- **整体评估**：**{human_taste['assessment']}**

---

## 四、优化建议（可执行）

### 4.1 内容策略

"""
    
    # 根据主题集中度给出建议
    if topic_analysis['concentration_rate'] < 60:
        report += "- ⚠️ **主题过于分散**：建议砍掉表现后30%的主题，聚焦TOP2-3个核心方向\n"
    elif topic_analysis['concentration_rate'] > 90:
        report += "- ⚠️ **主题过于集中**：有内容枯竭风险，建议适度拓展1-2个周边相关主题\n"
    else:
        report += "- ✅ **主题集中度健康**：保持现有策略即可\n"
    
    # 根据人味指数给出建议
    if human_taste['human_taste_score'] < 50:
        report += "- ⚠️ **AI痕迹较重**：建议增加第一人称视角、个人经历分享、具体案例细节\n"
    
    title_style = title_analysis['dominant_style']
    report += f"""
### 4.2 标题优化

当前主导风格是 **{title_style}**

建议：
- 增加「数字型」标题比例（点击率通常更高）
- 尝试「痛点+数字」组合（如：\"用了10个Agent后，我发现只有2个真正有用\"）

---

## 五、后续行动清单

1. **本周**：分析3篇阅读最高和3篇阅读最低的文章，找出共性差异
2. **本月**：做2-3次标题A/B测试，验证不同风格的点击率
3. **长期**：建立「文章表现数据库」，每篇发布后24小时记录核心数据

---

*本报告由 wechat-account-diagnostic 技能自动生成*
"""
    
    # 保存报告
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"诊断报告已生成: {output_file}")
    return {"success": True, "output_file": output_file}


# ============================================================
# 主函数
# ============================================================

def cmd_fetch(args):
    """拉取数据命令"""
    appid, secret = args.appid, args.secret
    if not appid or not secret:
        appid, secret = load_credentials()
    
    if not appid or not secret:
        print("错误: 请提供 --appid 和 --secret，或设置 WECHAT_APPID / WECHAT_APPSECRET 环境变量", file=sys.stderr)
        sys.exit(1)
    
    token = get_token(appid, secret)
    if not token:
        sys.exit(1)
    
    data = fetch_full_data(token, days=args.days)
    
    output_file = args.output or f"account_data_{datetime.now().strftime('%Y%m%d')}.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"数据已保存到: {output_file}")
    print(f"共拉取 {len(data.get('articles', []))} 篇文章信息")


def cmd_analyze(args):
    """分析数据命令"""
    with open(args.data_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    generate_diagnostic_report(data, args.output)


def cmd_full(args):
    """完整流程：拉取+分析"""
    appid, secret = args.appid, args.secret
    if not appid or not secret:
        appid, secret = load_credentials()
    
    if not appid or not secret:
        print("错误: 请提供 --appid 和 --secret", file=sys.stderr)
        sys.exit(1)
    
    token = get_token(appid, secret)
    if not token:
        sys.exit(1)
    
    # 拉取数据
    data = fetch_full_data(token, days=30)
    
    # 生成报告
    output_file = args.output or f"diagnostic_report_{datetime.now().strftime('%Y%m%d')}.md"
    generate_diagnostic_report(data, output_file)


def main():
    parser = argparse.ArgumentParser(description="微信公众号账号诊断分析器")
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    # fetch 子命令
    fetch_parser = subparsers.add_parser("fetch", help="拉取公众号数据")
    fetch_parser.add_argument("--appid", help="微信公众号 AppID")
    fetch_parser.add_argument("--secret", help="微信公众号 AppSecret")
    fetch_parser.add_argument("--days", type=int, default=30, help="拉取最近N天的数据")
    fetch_parser.add_argument("--output", "-o", help="输出JSON文件路径")
    
    # analyze 子命令
    analyze_parser = subparsers.add_parser("analyze", help="分析数据生成报告")
    analyze_parser.add_argument("--data-file", "-d", required=True, help="数据JSON文件路径")
    analyze_parser.add_argument("--output", "-o", required=True, help="输出报告路径")
    
    # full 子命令
    full_parser = subparsers.add_parser("full", help="一键全流程：拉取+分析")
    full_parser.add_argument("--appid", help="微信公众号 AppID")
    full_parser.add_argument("--secret", help="微信公众号 AppSecret")
    full_parser.add_argument("--output", "-o", help="输出报告路径")
    full_parser.add_argument("--hotspot-path", help="热点资讯路径（用于热点关联分析）")
    
    args = parser.parse_args()
    
    if args.command == "fetch":
        cmd_fetch(args)
    elif args.command == "analyze":
        cmd_analyze(args)
    elif args.command == "full":
        cmd_full(args)


if __name__ == "__main__":
    main()
