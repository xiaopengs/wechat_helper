#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""公众号封面固定版式生成器 —— 「左文右图 · 火柴人讽刺画」

版式规范（固定，2026-09-20 定版）
--------------------------------------------------------------------
画布        1400 × 596 px（微信封面 2.35:1），纯白底
右图        1:1 正方形插画，自动裁到内容边界后放大，铺满整个高度
            位置 x = 804..1400, y = 0..596
            题材固定：火柴人讽刺画，默认主题「AI 替代人」
标签        右图左下角橙底白字圆角签，默认「项目管理」
左文        x0 = 88
              y=132  蓝色 52×8 短块 + 橙色 28×8 短块（品牌色节拍器）
              y=166  主标题第一行（粗体 58）
              y=242  主标题第二行（粗体 58）
              y=344  副标题第一行（常规 26 灰）
              y=386  副标题第二行（常规 26 灰）
              y=468  橙色横线 220×4
              y=490  页脚小字（常规 23 极浅灰）
配色        ink #22262B / grey #787E88 / faint #969BA3
            blue #1a73e8 / orange #ff6b35

用法
--------------------------------------------------------------------
# 1) 已有底图（1:1 或任意方形/矩形），直接排版
python3 make_cover_satire.py --art cover_satire_raw.png \
    --label 项目管理 \
    --title "一个内核，" "两个前门。" \
    --sub "Copilot Agent Runtime" "43 万行 TypeScript → 83 万行 Rust" \
    --footer "14.5 周 · 128 个 PR · 原地换芯" \
    --out cover_v4.png

# 2) 还没有底图：自动调 MiniMax 生成讽刺画（--gen）
python3 make_cover_satire.py --gen --theme "AI 替代人" --out cover_v4.png

底图自动生成走 gen_cover_satire.sh（MiniMax image-01，1:1，浅色白底简笔画）。
"""
import argparse
import os
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont

BASE = os.path.dirname(os.path.abspath(__file__))

# ---------- 固定版式参数 ----------
W, H = 1400, 596
ART_X, ART_Y = W - H, 0          # 右图铺满高度，贴右边缘
LABEL_MARGIN = 28
INK = (34, 38, 43)               # #22262B
GREY = (120, 126, 136)           # #787E88
FAINT = (150, 155, 163)          # #969BA3
BLUE = (26, 115, 232)            # #1a73e8
ORANGE = (255, 107, 53)          # #ff6b35
FB = "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"
FR = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"

X0 = 88
Y_MARKS, Y_T1, Y_T2 = 132, 166, 242
Y_S1, Y_S2 = 344, 386
Y_RULE, Y_FOOT = 468, 490
F_TITLE, F_SUB, F_FOOT = 58, 26, 23
F_LABEL = 28


def font(path, size, index=2):
    return ImageFont.truetype(path, size, index=index)


def content_square(path, pad_ratio=0.06, dark=200, min_px=3):
    """裁到内容边界，并补成正方形（忽略纸面浅灰噪点）。"""
    im = Image.open(path).convert("RGB")
    a = np.asarray(im.convert("L")).astype(int)
    mask = a < dark
    nz_r = np.nonzero(mask.sum(axis=1) > min_px)[0]
    nz_c = np.nonzero(mask.sum(axis=0) > min_px)[0]
    if len(nz_r) == 0 or len(nz_c) == 0:
        return im
    y0, y1 = int(nz_r.min()), int(nz_r.max())
    x0, x1 = int(nz_c.min()), int(nz_c.max())
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    side = max(x1 - x0, y1 - y0) * (1 + pad_ratio * 2)
    side = min(side, min(im.width, im.height))
    left = max(0, min(im.width - side, cx - side / 2))
    top = max(0, min(im.height - side, cy - side / 2))
    print(f"  内容区 {x1-x0}×{y1-y0} → 正方形 {side:.0f}px")
    return im.crop((round(left), round(top), round(left + side), round(top + side)))


def build_cover(art_path, label, t1, t2, s1, s2, footer, out_png):
    canvas = Image.new("RGB", (W, H), (255, 255, 255))

    art = content_square(art_path).resize((H, H), Image.LANCZOS)
    canvas.paste(art, (ART_X, ART_Y))

    d = ImageDraw.Draw(canvas)

    # 右图左下角标签
    if label:
        f_label = font(FB, F_LABEL)
        tw = d.textlength(label, font=f_label)
        pad_x, pad_y = 20, 9
        bx = ART_X + LABEL_MARGIN
        by = H - LABEL_MARGIN - (F_LABEL + pad_y * 2)
        d.rounded_rectangle([bx, by, bx + tw + pad_x * 2, by + F_LABEL + pad_y * 2],
                            radius=10, fill=ORANGE)
        d.text((bx + pad_x, by + pad_y), label, font=f_label, fill=(255, 255, 255))

    # 左文区
    d.rectangle([X0, Y_MARKS, X0 + 52, Y_MARKS + 8], fill=BLUE)
    d.rectangle([X0 + 60, Y_MARKS, X0 + 88, Y_MARKS + 8], fill=ORANGE)

    ft = font(FB, F_TITLE)
    d.text((X0, Y_T1), t1, font=ft, fill=INK)
    d.text((X0, Y_T2), t2, font=ft, fill=INK)

    fs = font(FR, F_SUB)
    d.text((X0, Y_S1), s1, font=fs, fill=GREY)
    d.text((X0, Y_S2), s2, font=fs, fill=GREY)

    d.line([(X0, Y_RULE), (X0 + 220, Y_RULE)], fill=ORANGE, width=4)
    if footer:
        d.text((X0, Y_FOOT), footer, font=font(FR, F_FOOT), fill=FAINT)

    canvas.save(out_png)
    jpg = os.path.splitext(out_png)[0] + ".jpg"
    canvas.save(jpg, quality=95)
    print("saved", out_png, jpg, canvas.size)
    return out_png


def main():
    ap = argparse.ArgumentParser(description="公众号封面固定版式：左文右图（火柴人讽刺画）")
    ap.add_argument("--art", help="右侧底图路径（1:1 或方形）")
    ap.add_argument("--gen", action="store_true", help="没有底图时，调 MiniMax 自动生成")
    ap.add_argument("--theme", default="AI 替代人", help="讽刺主题（--gen 时使用）")
    ap.add_argument("--raw-out", default=os.path.join(BASE, "cover_satire_raw.png"))
    ap.add_argument("--label", default="项目管理")
    ap.add_argument("--title", nargs=2, default=["一个内核，", "两个前门。"])
    ap.add_argument("--sub", nargs=2, default=["Copilot Agent Runtime",
                                               "43 万行 TypeScript → 83 万行 Rust"])
    ap.add_argument("--footer", default="14.5 周 · 128 个 PR · 原地换芯")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    art = args.art
    if args.gen or not art:
        print(f"生成讽刺插画（主题：{args.theme}）...")
        subprocess.run(["bash", os.path.join(BASE, "gen_cover_satire.sh"), args.raw_out],
                       check=True)
        art = args.raw_out

    build_cover(art, args.label, args.title[0], args.title[1],
                args.sub[0], args.sub[1], args.footer,
                args.out if os.path.isabs(args.out) else os.path.join(BASE, args.out))


if __name__ == "__main__":
    main()
