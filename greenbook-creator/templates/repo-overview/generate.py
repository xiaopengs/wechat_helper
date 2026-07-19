#!/usr/bin/env python3
"""Repo-overview 模板 · 参数化生成器

Usage:
    python3 generate.py --data path/to/data.yaml --out path/to/output/

依赖: pip install pillow pyyaml
字体: /usr/share/fonts/opentype/noto/NotoSansCJK-{Bold,Regular}.ttc
      /usr/share/fonts/opentype/noto/NotoSansMonoCJK-Regular.ttc

If a field is missing, the generator falls back to the OpenWiki default
defined under DATA_DEFAULTS so the template still runs out of the box.
"""
from __future__ import annotations
import argparse, math, os, sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

try:
    import yaml  # type: ignore
except ImportError:
    yaml = None

# ---------- 颜色 / 字体 ----------
PALETTE = {
    "blue":   (79, 107, 255),
    "purple": (126, 80, 255),
    "cyan":   (59, 196, 220),
    "green":  (60, 207, 145),
    "orange": (255, 184, 77),
    "red":    (255, 107, 107),
}
PALE = {
    "blue":   (237, 241, 255),
    "purple": (244, 238, 255),
    "cyan":   (234, 249, 252),
    "green":  (234, 250, 243),
    "orange": (255, 247, 229),
    "red":    (255, 239, 239),
}
INK       = (28, 32, 46)
INK_2     = (86, 94, 118)
INK_3     = (139, 148, 172)
BORDER    = (225, 230, 244)
WHITE     = (255, 255, 255)
BG_TOP    = (255, 255, 255)
BG_BOTTOM = (244, 247, 255)
DARK_BG   = (24, 28, 43)
DARK_TXT  = (172, 187, 255)

W, H = 1080, 1440
FONT_B = "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"
FONT_R = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
FONT_M = FONT_R
FONT_MONO = "/usr/share/fonts/opentype/noto/NotoSansMonoCJK-Regular.ttc"

DATA_DEFAULTS = {
    "meta": {
        "name": "Repo", "kicker": "开源项目解读", "stars_text": "",
        "version": "", "license": "", "source": "github.com/owner/repo",
        "star_source_date": None,
    },
    "footer_label": "开源项目拆解",
}

# ---------- 文字 / 字体 ----------
def F(size, weight="regular"):
    path = FONT_B if weight == "bold" else FONT_M if weight == "medium" else FONT_R
    return ImageFont.truetype(path, size)


def text_size(draw, text, font):
    b = draw.textbbox((0, 0), text, font=font)
    return b[2] - b[0], b[3] - b[1]


def fit_font(draw, text, max_w, start, min_size=18, weight="bold"):
    size = start
    while size > min_size:
        f = F(size, weight)
        if text_size(draw, text, f)[0] <= max_w:
            return f
        size -= 1
    return F(min_size, weight)


def wrap_px(draw, text, font, max_w):
    lines, cur = [], ""
    for ch in text:
        test = cur + ch
        if cur and text_size(draw, test, font)[0] > max_w:
            lines.append(cur.rstrip())
            cur = ch.lstrip()
        else:
            cur = test
    if cur:
        lines.append(cur)
    return lines


def draw_wrapped(draw, xy, text, font, fill, max_w, gap=8, max_lines=None):
    x, y = xy
    all_lines = []
    for para in text.split("\n"):
        all_lines.extend(wrap_px(draw, para, font, max_w) or [""])
    if max_lines:
        all_lines = all_lines[:max_lines]
    h = text_size(draw, "国", font)[1]
    for line in all_lines:
        draw.text((x, y), line, font=font, fill=fill)
        y += h + gap
    return y


def linear_gradient(draw, box, c1, c2, horizontal=True):
    x0, y0, x1, y1 = box
    steps = max(1, (x1 - x0) if horizontal else (y1 - y0))
    for i in range(steps):
        t = i / max(1, steps - 1)
        c = tuple(int(c1[k] * (1 - t) + c2[k] * t) for k in range(3))
        if horizontal:
            draw.line((x0 + i, y0, x0 + i, y1), fill=c)
        else:
            draw.line((x0, y0 + i, x1, y0 + i), fill=c)


def shadow_card(im, box, radius=24, fill=WHITE, outline=BORDER,
                shadow=(80, 92, 140, 32), blur=14, offset=(0, 6), width=2):
    x0, y0, x1, y1 = map(int, box)
    layer = Image.new("RGBA", im.size, (0, 0, 0, 0))
    ImageDraw.Draw(layer).rounded_rectangle(
        (x0 + offset[0], y0 + offset[1], x1 + offset[0], y1 + offset[1]),
        radius=radius, fill=shadow)
    layer = layer.filter(ImageFilter.GaussianBlur(blur))
    im.alpha_composite(layer)
    ImageDraw.Draw(im).rounded_rectangle(box, radius=radius, fill=fill,
                                        outline=outline, width=width)


def pill(draw, box, text, fill, color, font=None, outline=None):
    x0, y0, x1, y1 = box
    draw.rounded_rectangle(box, radius=(y1 - y0) // 2, fill=fill,
                           outline=outline, width=1 if outline else 0)
    font = font or F(22, "medium")
    draw.text(((x0 + x1) // 2, (y0 + y1) // 2 - 1), text,
              font=font, fill=color, anchor="mm")


def arrow(draw, start, end, color, width=5):
    draw.line((start[0], start[1], end[0], end[1]), fill=color, width=width)
    a = math.atan2(end[1] - start[1], end[0] - start[0])
    l = 14
    p1 = (end[0] - l * math.cos(a - math.pi / 6), end[1] - l * math.sin(a - math.pi / 6))
    p2 = (end[0] - l * math.cos(a + math.pi / 6), end[1] - l * math.sin(a + math.pi / 6))
    draw.polygon((end, p1, p2), fill=color)


# ---------- 视觉原子 ----------
def icon_code(draw, center, size, color, width=8):
    x, y = center
    s = size
    for sx, sy, ex, ey in (
        (x - s*0.45, y, x - s*0.12, y - s*0.34),
        (x - s*0.45, y, x - s*0.12, y + s*0.34),
        (x + s*0.45, y, x + s*0.12, y - s*0.34),
        (x + s*0.45, y, x + s*0.12, y + s*0.34),
        (x + s*0.08, y - s*0.42, x - s*0.08, y + s*0.42),
    ):
        draw.line((sx, sy, ex, ey), fill=color, width=width)


def icon_book(draw, box, c1, c2):
    x0, y0, x1, y1 = box
    xm = (x0 + x1) // 2
    draw.rounded_rectangle((x0, y0, xm - 4, y1), radius=16,
                           fill=(235, 240, 255), outline=c1, width=4)
    draw.rounded_rectangle((xm + 4, y0, x1, y1), radius=16,
                           fill=(244, 238, 255), outline=c2, width=4)
    draw.line((xm, y0 + 10, xm, y1 - 8), fill=(167, 174, 205), width=3)
    for yy in (y0 + 34, y0 + 62, y0 + 90):
        draw.line((x0 + 22, yy, xm - 24, yy), fill=(171, 183, 225), width=4)
        draw.line((xm + 24, yy, x1 - 22, yy), fill=(184, 164, 228), width=4)


def icon_brain(draw, center, radius_outer=92, radius_inner=48,
               color=PALETTE["purple"], pale=PALE["purple"]):
    cx, cy = center
    for a in range(0, 360, 60):
        rad = math.radians(a)
        nx, ny = cx + radius_outer * math.cos(rad), cy + (radius_outer - 20) * math.sin(rad)
        draw.line((cx, cy, nx, ny), fill=(205, 191, 241), width=5)
        draw.ellipse((nx - 15, ny - 15, nx + 15, ny + 15),
                     fill=pale, outline=color, width=4)
    draw.ellipse((cx - radius_inner, cy - radius_inner,
                  cx + radius_inner, cy + radius_inner),
                 fill=pale, outline=color, width=5)
    draw.text(center, "ME", font=F(25, "bold"), fill=color, anchor="mm")


# ---------- 工具 ----------
def gradient_bg():
    im = Image.new("RGB", (W, H), BG_TOP)
    px = im.load()
    for y in range(H):
        t = y / (H - 1)
        for x in range(W):
            glow1 = max(0.0, 1.0 - math.hypot(x - 930, y - 180) / 560)
            glow2 = max(0.0, 1.0 - math.hypot(x - 120, y - 1180) / 620)
            base = [int(BG_TOP[i] * (1 - t) + BG_BOTTOM[i] * t) for i in range(3)]
            base[0] = min(255, base[0] + int(4 * glow1 + 2 * glow2))
            base[1] = min(255, base[1] + int(1 * glow1 + 2 * glow2))
            base[2] = min(255, base[2] + int(7 * glow1 + 6 * glow2))
            px[x, y] = tuple(base)
    return im.convert("RGBA")


def header(im, page, total, kicker, title, subtitle=None, title_size=64):
    d = ImageDraw.Draw(im)
    linear_gradient(d, (0, 0, W, 10), PALETTE["blue"], PALETTE["purple"])
    pill(d, (60, 50, 410, 96), kicker,
         fill=PALE["blue"], color=PALETTE["blue"], font=F(21, "medium"))
    d.text((1015, 73), f"{page:02d}/{total:02d}",
           font=F(22, "bold"), fill=PALETTE["purple"], anchor="rm")
    ftitle = fit_font(d, title, 960, title_size, 44, "bold")
    d.text((60, 128), title, font=ftitle, fill=INK)
    y = 128 + text_size(d, title, ftitle)[1] + 22
    if subtitle:
        y = draw_wrapped(d, (62, y), subtitle, F(28, "regular"), INK_2,
                         940, gap=8, max_lines=2)
    return d, max(y + 28, 320)


def footer(im, source, label):
    d = ImageDraw.Draw(im)
    d.line((60, 1368, 1020, 1368), fill=BORDER, width=2)
    f = F(17, "regular")
    d.text((60, 1390), f"来源：{source}", font=f, fill=INK_3)
    d.text((1020, 1390), label, font=f, fill=INK_3, anchor="ra")


# ---------- 六页 ----------
def page_cover(data):
    im = gradient_bg(); d = ImageDraw.Draw(im)
    m, c = data["meta"], data["cover"]
    linear_gradient(d, (0, 0, W, 12), PALETTE["blue"], PALETTE["purple"])
    pill(d, (60, 54, 392, 104), m["kicker"],
         fill=PALE["blue"], color=PALETTE["blue"], font=F(22, "medium"))
    d.text((1020, 79), "01/06", font=F(22, "bold"),
           fill=PALETTE["purple"], anchor="rm")
    d.text((60, 150), m["name"], font=F(92, "bold"), fill=INK)
    d.text((62, 270), c["tagline_left"], font=F(56, "bold"), fill=INK)
    d.text((62, 340), c["tagline_right"],
           font=fit_font(d, c["tagline_right"], 950, 56, 46, "bold"),
           fill=PALETTE["blue"])
    d.text((64, 422), c["subline"], font=F(28, "regular"), fill=INK_2)

    # 主图卡
    shadow_card(im, (60, 505, 1020, 1115), radius=34, shadow=(71, 83, 135, 42))
    d = ImageDraw.Draw(im)
    d.line((266, 772, 470, 812), fill=(191, 202, 239), width=5)
    d.line((814, 740, 610, 812), fill=(205, 190, 241), width=5)
    d.line((300, 980, 470, 875), fill=(191, 225, 216), width=5)
    d.line((785, 983, 610, 875), fill=(235, 203, 163), width=5)
    d.rounded_rectangle((400, 700, 680, 930), radius=36,
                         fill=PALE["blue"], outline=PALETTE["blue"], width=4)
    icon_book(d, (458, 747, 622, 870), PALETTE["blue"], PALETTE["purple"])
    d.text((540, 895), f"{m['name'].lower()}/",
           font=F(26, "bold"), fill=INK, anchor="mm")
    # 4 个节点（取自 data.cover.central_nodes）
    nodes = c["central_nodes"][:4]
    positions = [
        (120, 650, 355, 790),
        (725, 620, 960, 760),
        (120, 930, 355, 1065),
        (725, 930, 960, 1065),
    ]
    for (box, n) in zip(positions, nodes):
        col = PALETTE.get(n["color"], PALETTE["blue"])
        pal = PALE.get(n["color"], PALE["blue"])
        d.rounded_rectangle(box, radius=26, fill=pal, outline=col, width=3)
        d.text(((box[0]+box[2])//2, box[1]+45), n["label"],
               font=F(26, "bold"), fill=col, anchor="mm")
        d.text(((box[0]+box[2])//2, box[1]+96), n["sub"],
               font=F(22, "regular"), fill=INK_2, anchor="mm")

    # 3 个数据徽章
    facts = [
        (f"{m['license']} 开源", PALETTE["blue"], PALE["blue"]),
        (m["version"], PALETTE["purple"], PALE["purple"]),
        (m["stars_text"], PALETTE["green"], PALE["green"]),
    ]
    x = 60
    for t, col, pal in facts:
        if not t or t.strip("0123456789,. *"):
            continue
        w = 285 if "Stars" in t else 205
        pill(d, (x, 1155, x + w, 1213), t,
             fill=pal, color=col, font=F(24, "bold"))
        x += w + 18

    d.text((60, 1260), f"它不是另一个漂亮文档站，而是 Agent 的项目内知识层。",
           font=F(32, "bold"), fill=INK)
    if m["stars_text"].endswith("*") and m.get("star_source_date"):
        d.text((60, 1312),
               f"* GitHub API 数据截于 {m['star_source_date']}",
               font=F(19, "regular"), fill=INK_3)
    footer(im, m["source"], data.get("footer_label", "开源项目拆解"))
    return im


def page_pain(data):
    im = gradient_bg(); d, y = header(im, 2, 6, "PAIN · 痛点",
        "它解决的，不是「没文档」",
        "真正的问题：Agent 每次进仓库，都像第一天入职。", 62)
    y = max(y + 28, 320)
    for i, p in enumerate(data["pains"][:3]):
        yy = y + i * 205
        col = PALETTE.get(p["color"], PALETTE["red"])
        pal = PALE.get(p["color"], PALE["red"])
        shadow_card(im, (60, yy, 1020, yy + 172), radius=26, shadow=(80, 92, 140, 25))
        d = ImageDraw.Draw(im)
        d.rounded_rectangle((88, yy + 32, 190, yy + 138), radius=24, fill=pal)
        d.text((139, yy + 85), p["num"],
               font=F(40, "bold"), fill=col, anchor="mm")
        d.text((225, yy + 38), p["title"], font=F(34, "bold"), fill=INK)
        d.text((225, yy + 96), p["desc"], font=F(25, "regular"), fill=INK_2)
    fy = y + 645
    d.text((60, fy), f"OpenWiki 把「重新读仓库」变成一条流水线",
           font=F(34, "bold"), fill=INK)
    items = [
        (120, PALETTE["blue"], "代码库"),
        (420, PALETTE["purple"], data["meta"]["name"]),
        (750, PALETTE["green"], "项目百科"),
    ]
    for x, c, label in items:
        d.rounded_rectangle((x, fy + 90, x + 210, fy + 240),
                            radius=28, fill=WHITE, outline=c, width=3)
        if label == "代码库":
            icon_code(d, (x + 105, fy + 135), 52, c, 6)
        elif label == data["meta"]["name"]:
            icon_book(d, (x + 60, fy + 105, x + 150, fy + 170),
                      PALETTE["blue"], PALETTE["purple"])
        else:
            d.ellipse((x + 72, fy + 102, x + 138, fy + 168),
                      fill=PALE["green"], outline=c, width=4)
            d.line((x + 89, fy + 136, x + 104, fy + 151, x + 129, fy + 119),
                   fill=c, width=6, joint="curve")
        d.text((x + 105, fy + 190), label,
               font=F(26, "bold"), fill=INK, anchor="mm")
        d.text((x + 105, fy + 222),
               ["Git 证据", "Agent 综合", "持续更新"][items.index((x, c, label))],
               font=F(20, "regular"), fill=INK_2, anchor="mm")
    arrow(d, (335, fy + 165), (400, fy + 165), PALETTE["blue"], 5)
    arrow(d, (635, fy + 165), (730, fy + 165), PALETTE["purple"], 5)
    d.rounded_rectangle((60, 1260, 1020, 1325), radius=22, fill=PALE["blue"])
    d.text((540, 1292), "一句话：把隐性项目知识，变成 Agent 可检索的显性文件。",
           font=F(27, "bold"), fill=PALETTE["blue"], anchor="mm")
    footer(im, f"{data['meta']['source']} · openwiki/architecture/overview.md",
           data.get("footer_label", "开源项目拆解"))
    return im


def page_advantage(data):
    im = gradient_bg(); d, y = header(im, 3, 6, "VALUE · 优势",
        "真正的护城河：不是生成，是维护",
        "一次性总结谁都能做；难的是跟着代码一起变。", 60)
    y = max(y + 30, 330)
    for i, st in enumerate(data["pipeline"][:4]):
        x = 60 + i * 247
        col = PALETTE.get(st["color"], PALETTE["blue"])
        pal = PALE.get(st["color"], PALE["blue"])
        shadow_card(im, (x, y, x + 220, y + 235), radius=24, shadow=(80, 92, 140, 22))
        d = ImageDraw.Draw(im)
        d.ellipse((x + 18, y + 18, x + 68, y + 68),
                  fill=pal, outline=col, width=2)
        d.text((x + 43, y + 43), st["num"],
               font=F(23, "bold"), fill=col, anchor="mm")
        d.text((x + 110, y + 105), st["name"],
               font=F(31, "bold"), fill=INK, anchor="mm")
        d.text((x + 110, y + 158), st["sub"],
               font=F(19, "regular"), fill=INK_2, anchor="mm")
        d.rounded_rectangle((x + 28, y + 190, x + 192, y + 200),
                            radius=5, fill=pal)
        d.rounded_rectangle((x + 28, y + 190,
                             x + 70 + (i * 28), y + 200), radius=5, fill=col)
        if i < 3:
            arrow(d, (x + 222, y + 117), (x + 242, y + 117), col, 4)
    d.text((60, y + 290), "四个难被替代的细节",
           font=F(36, "bold"), fill=INK)
    adv = data["advantages"][:4]
    for i, a in enumerate(adv):
        col, pal = PALETTE.get(a["color"], PALETTE["blue"]), PALE.get(a["color"], PALE["blue"])
        col_, row_ = i % 2, i // 2
        x = 60 + col_ * 490
        yy = y + 355 + row_ * 210
        shadow_card(im, (x, yy, x + 470, yy + 180), radius=24, shadow=(80, 92, 140, 18))
        d = ImageDraw.Draw(im)
        d.rounded_rectangle((x + 24, yy + 25, x + 76, yy + 77), radius=16, fill=pal)
        d.ellipse((x + 39, yy + 40, x + 61, yy + 62), fill=col)
        d.text((x + 95, yy + 28), a["title"], font=F(29, "bold"), fill=INK)
        draw_wrapped(d, (x + 28, yy + 95), a["desc"],
                     F(23, "regular"), INK_2, 414, gap=8, max_lines=2)
    d.rounded_rectangle((60, 1212, 1020, 1322), radius=25, fill=DARK_BG)
    d.text((90, 1238), "差异化结论",
           font=F(22, "bold"), fill=DARK_TXT)
    d.text((90, 1276),
           f"{data['meta']['name']} 把「AI 生成文档」接进了软件工程的审查链。",
           font=F(27, "bold"), fill=WHITE)
    footer(im, f"{data['meta']['source']} · examples/openwiki-update.yml",
           data.get("footer_label", "开源项目拆解"))
    return im


def page_modes(data):
    im = gradient_bg(); d, y = header(im, 4, 6, "SCOPE · 两种模式",
        "它不只懂代码，还想做「个人大脑」",
        "同一个 CLI，两条完全不同的知识生产线。", 56)
    y = max(y + 25, 325)
    cols = [(60, 520, data["modes"][0]), (560, 1020, data["modes"][1])]
    for x0, x1, mode in cols:
        col = PALETTE.get(mode["color"], PALETTE["blue"])
        pal = PALE.get(mode["color"], PALE["blue"])
        shadow_card(im, (x0, y, x1, y + 735), radius=30, shadow=(80, 92, 140, 26))
        d = ImageDraw.Draw(im)
        pill(d, (x0 + 28, y + 28, x0 + 250, y + 77),
             mode["label"], fill=pal, color=col, font=F(20, "bold"))
        d.text((x0 + 28, y + 112), mode["title"],
               font=F(38, "bold"), fill=INK)
        if mode.get("icon") == "brain":
            icon_brain(d, ((x0 + x1) // 2, y + 270), color=col, pale=pal)
        else:
            icon_code(d, ((x0 + x1) // 2, y + 272), 132, col, 12)
        d.line((x0 + 28, y + 382, x1 - 28, y + 382), fill=BORDER, width=2)
        yy = y + 420
        for b in mode["bullets"][:4]:
            d.ellipse((x0 + 32, yy + 9, x0 + 48, yy + 25), fill=col)
            draw_wrapped(d, (x0 + 62, yy), b, F(23, "regular"),
                         INK_2, x1 - x0 - 100, gap=7, max_lines=2)
            yy += 73
    sy = y + 785
    d.rounded_rectangle((60, sy, 1020, sy + 145), radius=28, fill=DARK_BG)
    d.text((90, sy + 34), "共同底座", font=F(23, "bold"), fill=DARK_TXT)
    d.text((90, sy + 82), data.get("modes_shared_footer", ""),
           font=fit_font(d, data.get("modes_shared_footer", ""), 860, 30, 24, "bold"),
           fill=WHITE)
    d.text((60, sy + 185),
           "凭证保存在 ~/.openwiki/.env；连接外部来源前，先核对权限与数据策略。",
           font=F(22, "regular"), fill=INK_2)
    footer(im, f"{data['meta']['source']}#personal-brain-mode",
           data.get("footer_label", "开源项目拆解"))
    return im


def page_compare(data):
    im = gradient_bg(); d, y = header(im, 5, 6, "COMPARE · 竞品",
        "别问谁最好，先看你要给谁写",
        "它们看似都叫「AI 文档」，其实服务的是四种任务。", 58)
    y = max(y + 20, 315)
    for i, c in enumerate(data["comparisons"][:4]):
        yy = y + i * 218
        col = PALETTE.get(c["color"], PALETTE["blue"])
        pal = PALE.get(c["color"], PALE["blue"])
        shadow_card(im, (60, yy, 1020, yy + 188), radius=26, shadow=(80, 92, 140, 22))
        d = ImageDraw.Draw(im)
        d.rounded_rectangle((82, yy + 26, 312, yy + 162), radius=23, fill=pal)
        name_font = fit_font(d, c["name"], 200, 30, 22, "bold")
        d.text((197, yy + 70), c["name"],
               font=name_font, fill=col, anchor="mm")
        d.text((197, yy + 122), "最佳角色",
               font=F(19, "medium"), fill=INK_2, anchor="mm")
        d.text((345, yy + 25), c["best_for"], font=F(30, "bold"), fill=INK)
        d.text((345, yy + 78), c["features"],
               font=F(22, "regular"), fill=INK_2)
        pill(d, (345, yy + 124, 990, yy + 164),
             f"适合：{c['best_for']}",
             fill=pal, color=col, font=F(20, "medium"))
    yy = y + 900
    d.rounded_rectangle((60, yy, 1020, yy + 115), radius=26, fill=DARK_BG)
    d.text((90, yy + 28),
           f"{data['meta']['name']} 的相对优势",
           font=F(22, "bold"), fill=DARK_TXT)
    d.text((90, yy + 69), data.get("comparisons_closing", data["meta"]["name"] + " 的相对优势"),
           font=F(30, "bold"), fill=WHITE)
    footer(im, data["meta"]["source"],
           data.get("footer_label", "开源项目拆解"))
    return im


def page_howto(data):
    im = gradient_bg(); d, y = header(im, 6, 6, "HOW TO · 使用",
        "4 条命令上手：先跑通，再接自动更新",
        "前置：Node.js 22+；首次运行会让你选择模型提供商并配置凭证。", 56)
    y = max(y + 25, 320)
    shadow_card(im, (60, y, 1020, y + 420), radius=30,
                fill=DARK_BG, outline=(51, 58, 82), shadow=(45, 50, 80, 42),
                blur=18, offset=(0, 8))
    d = ImageDraw.Draw(im)
    d.ellipse((92, y + 34, 110, y + 52), fill=PALETTE["red"])
    d.ellipse((122, y + 34, 140, y + 52), fill=PALETTE["orange"])
    d.ellipse((152, y + 34, 170, y + 52), fill=PALETTE["green"])
    d.text((540, y + 44), "Terminal", font=F(18, "medium"),
           fill=(153, 161, 187), anchor="mm")
    yy = y + 78
    try:
        mono = ImageFont.truetype(FONT_MONO, 25)
    except OSError:
        mono = F(25, "medium")  # fallback if Noto Mono CJK missing
    for it in data["quickstart"][:4]:
        d.text((92, yy), it["n"],
               font=F(21, "bold"), fill=(134, 153, 255))
        d.text((145, yy), it["cmd"], font=mono, fill=(239, 242, 255))
        d.text((145, yy + 35), it["desc"],
               font=F(18, "regular"), fill=(147, 157, 184))
        yy += 80
    d.text((60, y + 465), "三条使用建议", font=F(36, "bold"), fill=INK)
    for i, t in enumerate(data["tips"][:3]):
        yy = y + 525 + i * 125
        col, pal = PALETTE.get(t["color"], PALETTE["blue"]), PALE.get(t["color"], PALE["blue"])
        shadow_card(im, (60, yy, 1020, yy + 110), radius=23, shadow=(80, 92, 140, 18))
        d = ImageDraw.Draw(im)
        d.rounded_rectangle((84, yy + 20, 220, yy + 90), radius=18, fill=pal)
        d.text((152, yy + 55), t["title"],
               font=F(25, "bold"), fill=col, anchor="mm")
        d.text((248, yy + 33), t["desc"], font=F(22, "regular"), fill=INK_2)
    risk = data["risk"]
    yy = y + 910
    d.rounded_rectangle((60, yy, 1020, yy + 115), radius=25,
                         fill=PALE["red"], outline=(255, 205, 205), width=2)
    d.text((90, yy + 24), risk["banner"], font=F(25, "bold"), fill=PALETTE["red"])
    d.text((90, yy + 68), risk["detail"], font=F(21, "regular"), fill=INK_2)
    footer(im, f"{data['meta']['source']} · npmjs.com/package/{data['meta']['name'].lower()}",
           data.get("footer_label", "开源项目拆解"))
    return im


# ---------- 输出 / 入口 ----------
def build_contact_sheet(paths):
    thumbs = [Image.open(p).convert("RGB").resize((270, 360), Image.LANCZOS) for p in paths]
    sheet = Image.new("RGB", (270 * 3, 360 * 2), (232, 235, 244))
    for i, t in enumerate(thumbs):
        sheet.paste(t, ((i % 3) * 270, (i // 3) * 360))
    sheet.save(paths[0].parent / "contact-sheet.jpg", "JPEG",
               quality=90, optimize=True)


def render_intro_and_captions(data, out_path):
    m = data["meta"]
    intro = (
        f"你有没有发现，每次让 AI 编程助手改代码，它都得先花一半时间「重新认识」你的仓库。\n"
        f"README 写到去年，架构图藏在某个 Wiki 子页面，约定只在 PR 评论里出现过——人和 Agent 都在重复同一个动作：在脑子里重建这套代码。\n"
        f"\n"
        f"**{m['name']}** 最近开源 —— 一个会替你仓库「写并维护」文档的 CLI。"
        f"它读 git 变化、用 DeepAgents 写知识、按 OKF 规范组织，"
        f"最后通过 GitHub Actions 自动开 PR 把更新交回来审。\n"
        f"这意味着：同一份知识，Agent 能查到、人能 PR 审核、还能跟代码一起 diff。\n"
        f"\n"
        f"怎么开始？`npm i -g {m['name'].lower()}`、`{m['name'].lower()} --init`、"
        f"把官方 workflow 复制进 `.github/workflows/`，最快 5 分钟跑通。\n"
        f"\n"
        f"下面 6 张图把它的痛点、相对竞品的差异、两种用法都拆给你看。"
        f"⭐ {m['stars_text'].rstrip('*')}、{m['license']} 开源、{m['version']}，建议先拿非核心仓库试点。\n"
    )
    captions = (
        "## 总导语（公众号「图片·文字」首图说明）\n\n" + intro + "\n\n---\n\n"
        f"## P1 ｜封面\n> 给 AI 编程助手一份会自动更新的项目百科。"
        f"封面一句话：**{m['name']} = 持续维护的项目内 Wiki**，不是又一个文档站。"
        f"{m['license']} 开源、{m['version']}、{m['stars_text']}。\n\n"
        f"## P2 ｜痛点\n> AI 助手进陌生仓库的成本，不是调用 API，而是「重新认识这套代码」——上下文碎片、文档漂移、每次重复交接。"
        f"{m['name']} 把「重新读仓库」变成一条流水线：代码变化 → 自动综合 → 持续更新。\n\n"
        f"## P3 ｜优势\n> 真护城河不是「会生成文档」，而是「会跟着代码更新文档」。本地 Markdown、保护人工标记区、避免空转元数据、跨 Git 平台。\n\n"
        f"## P4 ｜双模式\n> 同一个 CLI，两条完全不同的知识生产线：**Code Mode** 写项目 Wiki，**Personal Mode** 写个人大脑。"
        f"共同底座是 Google Open Knowledge Format v0.1。\n\n"
        f"## P5 ｜竞品\n> 别问谁最好，先看你要给谁写。{m['name']} 的相对优势：知识留在项目里，能跟代码一起被审查与迭代。\n\n"
        f"## P6 ｜上手\n> 4 条命令 5 分钟跑通。三个建议：先写边界、PR 审核、看清成本。生成内容仍需人工审阅。\n"
    )
    Path(out_path).write_text(captions, encoding="utf-8")


def load_data(path):
    if yaml is None:
        sys.stderr.write("缺少 pyyaml: pip install pyyaml\n")
        sys.exit(1)
    data = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    # 兜底默认值
    merged = {"meta": {**DATA_DEFAULTS["meta"], **(data.get("meta") or {})}}
    for k in ("cover", "pains", "pipeline", "advantages",
              "modes", "comparisons", "quickstart", "tips", "risk"):
        if k in data:
            merged[k] = data[k]
    merged["footer_label"] = data.get("footer_label", DATA_DEFAULTS["footer_label"])
    return merged


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True, help="YAML 数据文件路径")
    ap.add_argument("--out", required=True, help="输出目录")
    args = ap.parse_args()
    data = load_data(args.data)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    pages = [
        page_cover, page_pain, page_advantage,
        page_modes, page_compare, page_howto,
    ]
    paths = []
    for i, make in enumerate(pages, 1):
        im = make(data).convert("RGB")
        p = out / f"p{i}-{'cover' if i == 1 else ['pain','advantage','modes','compare','howto'][i-2]}.jpg"
        im.save(p, "JPEG", quality=90, optimize=True, subsampling=0)
        paths.append(p)
        sz = Image.open(p).size
        print(f"{p.name}: {sz}, {p.stat().st_size:,} bytes")
    build_contact_sheet(paths)
    render_intro_and_captions(data, out / "intro-and-captions.md")
    print(f"接触页面:{out/'contact-sheet.jpg'}")
    print(f"总导语 + 单图配文:{out/'intro-and-captions.md'}")


if __name__ == "__main__":
    main()
