#!/usr/bin/env python3
"""
save_weekly_report.py — 周报复盘归档脚本

用法:
  python save_weekly_report.py \
    --image /path/to/screenshot.jpg \
    --week "2026-06-08~2026-06-14" \
    --data-json /path/to/data.json  # 可选, 没填则建空模板

行为:
  1. 建目录 review/weekly/{week}/
  2. 复制截图 → report.jpg
  3. 复制/初始化 data.json
  4. 创建空 diagnosis.md 模板
  5. 追加一行到 review/index.md
"""
import argparse
import json
import shutil
from datetime import datetime
from pathlib import Path

REVIEW_ROOT = Path("~/.openclaw/workspace/wechat_helper/review").expanduser()


def save(image: Path, week: str, data_json: Path | None) -> Path:
    week_dir = REVIEW_ROOT / "weekly" / week
    week_dir.mkdir(parents=True, exist_ok=True)

    # 1. 复制截图
    dst_img = week_dir / "report.jpg"
    shutil.copy2(image, dst_img)

    # 2. 复制或初始化 data.json
    dst_data = week_dir / "data.json"
    if data_json and data_json.exists():
        shutil.copy2(data_json, dst_data)
    else:
        dst_data.write_text(
            json.dumps(_empty_data_template(week), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    # 3. 创建诊断模板
    diagnosis_path = week_dir / "diagnosis.md"
    if not diagnosis_path.exists():
        diagnosis_path.write_text(_diagnosis_template(week), encoding="utf-8")

    # 4. 更新 index
    _append_index(week, dst_img, dst_data)

    return week_dir


def _empty_data_template(week: str) -> dict:
    return {
        "account": "",
        "week_range": week,
        "week_label": "",
        "report_source": "创作者周报",
        "extracted_at": datetime.now().isoformat(timespec="seconds"),
        "raw_image": "report.jpg",
        "output": {"total_posts": None, "original_articles": None, "image_posts": None},
        "traffic": {"total_views": None, "wow_change_views": None, "source_breakdown": {}},
        "top_articles": [],
        "shares": {"total": None, "top_article_shares": None},
        "followers": {"total": None, "net_change": None, "wow_change_pct": None, "top_interests": []},
        "comments": {"reserved_count": None, "hot_topics": []},
        "notes": "",
    }


def _diagnosis_template(week: str) -> str:
    return f"""# 周报诊断 — {week}

> 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}
> 数据文件: data.json

## 一、核心数据速览

| 指标 | 数值 |
|---|---|
| 总阅读 |  |
| 推荐占比 |  |
| 搜索占比 |  |
| 净增粉 |  |
| 头部文章 |  |

## 二、命中模式
<!-- 按 P1-P8 检查，列出命中的 -->

## 三、关键洞察
<!-- 2-3 条 -->

## 四、本周行动清单
- [ ] 
- [ ] 
"""


def _append_index(week: str, img: Path, data: Path) -> None:
    index_path = REVIEW_ROOT / "index.md"
    if not index_path.exists():
        index_path.write_text(
            "# 周报复盘总索引\n\n"
            "| 周次 | 截图 | 数据 | 诊断 | 备注 |\n"
            "|---|---|---|---|---|\n",
            encoding="utf-8",
        )

    # 读取现有内容
    text = index_path.read_text(encoding="utf-8")
    # 简化：直接追加一行；重复运行同一周不会去重（可手改）
    rel = lambda p: p.relative_to(REVIEW_ROOT)
    line = f"| {week} | [{rel(img).name}]({rel(img)}) | [{rel(data).name}]({rel(data)}) | [diagnosis.md](weekly/{week}/diagnosis.md) |  |\n"
    with index_path.open("a", encoding="utf-8") as f:
        f.write(line)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--image", required=True, type=Path)
    ap.add_argument("--week", required=True, help="如 2026-06-08~2026-06-14")
    ap.add_argument("--data-json", type=Path, default=None)
    args = ap.parse_args()

    out = save(args.image, args.week, args.data_json)
    print(f"✅ 已归档到: {out}")
    print(f"   - report.jpg (原图)")
    print(f"   - data.json (结构化数据)")
    print(f"   - diagnosis.md (诊断模板, 待填写)")
